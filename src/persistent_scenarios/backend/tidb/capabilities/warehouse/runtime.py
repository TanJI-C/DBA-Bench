"""Warehouse delivery driver: composes job runners over the public wh.* control tables.

The driver implements the frozen `PersistentWorkloadRuntime` protocol
by combining three job services — required reports (concurrency governed by the public
control table), BI heartbeat, and batch ingest — with a cancellation monitor and the
heartbeat submission rhythm. All trusted facts land in per-service `TrustedLedger`s;
the public `wh.*` tables are the real scheduling surface.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import threading
import time

from src.persistent_scenarios.model.spec import JSONValue
from src.persistent_scenarios.runtime.clock import Clock
from src.persistent_scenarios.runtime.ledger import (
    FreshnessSample,
    JobAttempt,
    JobAttemptOutcome,
    LedgerTerminal,
    TrustedLedger,
)

from .errors import classify_job_outcome
from .reports import (
    REPORT_CONTRACTS_BY_ID,
    report_sql,
)
from .schema import (
    BATCH_A_ID,
    BATCH_B_ID,
    BATCH_REGISTRY,
    CONFIG_TABLE,
    FACT_TABLE,
    QUEUE_TABLE,
    REPORT_RESULT,
    stage_spec,
)
from .store import (
    DEFAULT_ATTEMPT_TIMEOUT_SECONDS,
    HEARTBEAT_JOB_PREFIX,
    HEARTBEAT_PRIORITY,
    INGEST_PRIORITY,
    MAX_ATTEMPTS,
    REQUIRED_REPORT_PRIORITY,
    QueueTables,
    fetchone,
    heartbeat_job_id,
    heartbeat_query_ids,
    heartbeat_sql,
    make_ingest_run,
    make_report_run,
)

DEFAULT_HEARTBEAT_INTERVAL_SECONDS = 60.0
DEFAULT_HEARTBEAT_BUDGET_SECONDS = 30.0
DEFAULT_REPORT_WORKER_CEILING = 6
DRAIN_GRACE_SECONDS = 60.0

SERVICE_REPORT = "wh_report_service"
SERVICE_HEARTBEAT = "wh_heartbeat_service"
SERVICE_INGEST = "wh_ingest_service"
SERVICE_IDS = (SERVICE_REPORT, SERVICE_HEARTBEAT, SERVICE_INGEST)


@dataclass(frozen=True, slots=True)
class QueuedJob:
    job_id: str
    job_kind: str
    submitted_at_monotonic: float
    deadline_at_monotonic: float
    run: Callable[[QueuedJob, object], str]
    batch_version: str | None = None
    input_snapshot: Mapping[str, JSONValue] | None = None


@dataclass(frozen=True, slots=True)
class JobControl:
    """Authorized queue control read from the public control table."""

    max_concurrency: int
    paused: bool = False


class TiDBJobRunner:
    """Job queue runner over `wh.warehouse_jobs`: claim, ledger, execute, deliver.

    The pool size is fixed (`max_workers`); the effective concurrency is read live
    from the public control table through the service store, so external configuration
    releases and agent governance act through the database, not driver internals.
    """

    def __init__(
        self,
        *,
        service_id: str,
        ledger: TrustedLedger,
        clock: Clock,
        store: "JobStore",
        connection_factory: Callable[[str], object],
        application_name: str,
        max_workers: int,
        poll_interval_seconds: float = 0.2,
        drain_grace_seconds: float = DRAIN_GRACE_SECONDS,
    ):
        if max_workers < 1:
            raise ValueError(f"job runner max_workers must be at least 1: service_id={service_id!r}, value={max_workers}")
        self.service_id = service_id
        self.ledger = ledger
        self.clock = clock
        self.store = store
        self._connection_factory = connection_factory
        self._application_name = application_name
        self._max_workers = max_workers
        self._poll_interval_seconds = poll_interval_seconds
        self._drain_grace_seconds = drain_grace_seconds
        self._planned: set[str] = set()
        self._attempt_counts: dict[str, int] = {}
        self._lock = threading.Lock()
        self._accepting = threading.Event()
        self._accepting.set()
        self._stop_workers = threading.Event()
        self._active_count = 0
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix=f"persistent_scenario-jobs-{service_id}"
        )
        self._started = False
        self._stopped = False

    # -- submission -----------------------------------------------------------

    def submit(self, job: QueuedJob) -> None:
        """Submit a delivery obligation: ledger first, then the public queue."""
        with self._lock:
            if job.job_id in self._planned:
                raise ValueError(f"job {job.job_id!r} submitted twice in service {self.service_id!r}")
            self._planned.add(job.job_id)
        self.ledger.append_job_planned(
            job_id=job.job_id,
            service_id=self.service_id,
            job_kind=job.job_kind,
            batch_version=job.batch_version,
            input_snapshot=job.input_snapshot,
            submitted_at_monotonic=job.submitted_at_monotonic,
            deadline_at_monotonic=job.deadline_at_monotonic,
        )
        connection = self._connection_factory(f"{self._application_name}-submit")
        try:
            self.store.enqueue(job, connection)
        finally:
            connection.close()

    # -- lifecycle ------------------------------------------------------------

    def start(self) -> None:
        if self._started:
            raise RuntimeError(f"job runner {self.service_id!r} already started")
        self._started = True
        for index in range(self._max_workers):
            self._executor.submit(self._worker_loop, index)

    def stop_new_requests(self) -> None:
        self._accepting.clear()

    def drain(self) -> None:
        deadline = time.monotonic() + self._drain_grace_seconds
        while time.monotonic() < deadline:
            with self._lock:
                if self._active_count == 0:
                    return
            time.sleep(0.1)
        raise RuntimeError(
            f"job runner {self.service_id!r} did not drain within grace: "
            f"active={self._active_count}, grace_seconds={self._drain_grace_seconds}"
        )

    def stop(self) -> None:
        if self._stopped:
            return
        self._stop_workers.set()
        self._executor.shutdown(wait=True)
        self._stopped = True

    # -- worker loop ----------------------------------------------------------

    def _worker_loop(self, index: int) -> None:
        worker_id = f"{self._application_name}-w{index}"
        connection = self._connection_factory(worker_id)
        while not self._stop_workers.is_set():
            if not self._accepting.is_set():
                break
            control = self.store.read_control(connection)
            if control.paused:
                self._stop_workers.wait(self._poll_interval_seconds)
                continue
            with self._lock:
                at_concurrency_limit = self._active_count >= control.max_concurrency
                if not at_concurrency_limit:
                    self._active_count += 1
            if at_concurrency_limit:
                # Waiting must happen outside the runner lock: holding it here starves
                # submit() whenever the released concurrency is below the pool ceiling.
                self._stop_workers.wait(self._poll_interval_seconds)
                continue
            try:
                claimed = self.store.claim(worker_id, connection)
                if claimed is None:
                    self._stop_workers.wait(self._poll_interval_seconds)
                    continue
                self._execute(claimed, connection)
            finally:
                with self._lock:
                    self._active_count -= 1
        connection.close()

    def _execute(self, job: QueuedJob, connection) -> None:
        with self._lock:
            attempt_index = self._attempt_counts.get(job.job_id, 0) + 1
            self._attempt_counts[job.job_id] = attempt_index
        started = self.clock.monotonic()
        outcome = None
        detail: Mapping[str, JSONValue] = {}
        result_digest: str | None = None
        try:
            result_digest = job.run(job, connection)
            outcome = JobAttemptOutcome.SUCCEEDED
        except Exception as exc:
            outcome, detail = classify_job_outcome(exc)
        ended = self.clock.monotonic()
        self.ledger.append_job_attempt(
            job_id=job.job_id,
            attempt=JobAttempt(
                attempt_index=attempt_index,
                queued_at_monotonic=job.submitted_at_monotonic,
                started_at_monotonic=started,
                ended_at_monotonic=ended,
                outcome=outcome,
                detail=dict(detail),
            ),
        )
        if outcome is JobAttemptOutcome.SUCCEEDED:
            self.store.record_result(job.job_id, result_digest, connection)
            self.ledger.append_job_terminal(
                job_id=job.job_id,
                terminal=LedgerTerminal.COMPLETED,
                delivered_at_monotonic=self.clock.monotonic(),
                result_digest=result_digest,
            )
            return
        # A requested cancellation does not delete the delivery duty: while attempts
        # remain the job is requeued; otherwise it ends as an explicit loss.
        if (
            outcome is JobAttemptOutcome.CANCELLED
            and self._cancel_requested(job.job_id, connection)
            and self._attempt_counts[job.job_id] < MAX_ATTEMPTS
        ):
            self.store.requeue_row(connection, job.job_id)
            return
        # Service-owned retry policies (e.g. the tenant BI scheduler):
        # a failed load requeues while attempts remain, so a repair that lands between
        # attempts is honored instead of silently ending the duty.
        if self.store.retry_on_failure(job, self._attempt_counts[job.job_id]):
            self.store.requeue_row(connection, job.job_id)
            return
        self.store.fail_row(connection, job.job_id)
        self.ledger.append_job_terminal(
            job_id=job.job_id,
            terminal=LedgerTerminal.INCOMPLETE_ERROR,
            delivered_at_monotonic=None,
            result_digest=None,
        )

    def _cancel_requested(self, job_id: str, connection) -> bool:
        _sql_text, cancel_requested, _attempts = self.store.job_state(job_id, connection)
        return cancel_requested


class JobStore:
    """SQL adapter surface the runner needs per service."""

    max_attempts: int = MAX_ATTEMPTS

    def enqueue(self, job: QueuedJob, connection) -> None: ...

    def claim(self, worker_id: str, connection) -> QueuedJob | None: ...

    def record_result(self, job_id: str, result_digest: str, connection) -> None: ...

    def read_control(self, connection) -> JobControl: ...

    def job_state(self, job_id: str, connection) -> tuple[str, bool, int]: ...

    def requeue_row(self, connection, job_id: str) -> None:
        """Re-queue a cancelled or retryable attempt (delegates to the queue adapter)."""
        self.tables.requeue_row(connection, job_id)

    def fail_row(self, connection, job_id: str) -> None:
        """End the queue row after the final failed attempt (delegates to the adapter)."""
        self.tables.fail_row(connection, job_id)

    def retry_on_failure(self, job: QueuedJob, attempts: int) -> bool:
        """Service-owned retry policy: whether a failed attempt requeues the duty."""
        return False


class ReportQueueStore(JobStore):
    """Required-report service: concurrency and memory quota come from the control table."""

    def __init__(self, tables: QueueTables, *, attempt_timeout_seconds: float = DEFAULT_ATTEMPT_TIMEOUT_SECONDS):
        self.tables = tables
        self._attempt_timeout_seconds = attempt_timeout_seconds

    def enqueue(self, job: QueuedJob, connection) -> None:
        snapshot = dict(job.input_snapshot or {})
        self.tables.enqueue_row(
            connection, job.job_id, "report", str(snapshot["report_id"]), int(snapshot["batch_cutoff"]),
            str(snapshot["sql"]), job.submitted_at_monotonic, job.deadline_at_monotonic, REQUIRED_REPORT_PRIORITY,
        )

    def claim(self, worker_id: str, connection) -> QueuedJob | None:
        row = self.tables.claim_row(connection, "report", worker_id, report_id_prefix=f"!{HEARTBEAT_JOB_PREFIX}",
                                    respect_report_hold=True)
        if row is None:
            return None
        job_id, _report_id, _cutoff, _sql, submit_at, deadline, _attempts = row
        snapshot = self._snapshot(connection, str(job_id))
        return QueuedJob(
            job_id=str(job_id),
            job_kind="report",
            submitted_at_monotonic=float(submit_at),
            deadline_at_monotonic=float(deadline),
            run=make_report_run(self.tables, attempt_timeout_seconds=self._attempt_timeout_seconds),
            input_snapshot=snapshot,
        )

    def record_result(self, job_id: str, result_digest: str, connection) -> None:
        # The report body already wrote wh.report_result and marked the row delivered.
        return

    def read_control(self, connection) -> JobControl:
        max_workers, _quota_mb, analytics_enabled, _ingest = self.tables.config_row(connection)
        return JobControl(max_concurrency=max_workers, paused=not analytics_enabled)

    def job_state(self, job_id: str, connection) -> tuple[str, bool, int]:
        return self.tables.job_state(connection, job_id)

    def _snapshot(self, connection, job_id: str) -> dict:
        row = fetchone(
            connection, f"SELECT report_id, batch_cutoff FROM {QUEUE_TABLE} WHERE job_id = %s;", (job_id,)
        )
        if row is None:
            raise RuntimeError(f"claimed report row lost its report_id/batch_cutoff: job_id={job_id!r}")
        contract = REPORT_CONTRACTS_BY_ID[str(row[0])]
        cutoff = int(row[1])
        return {
            "report_id": str(row[0]),
            "batch_cutoff": cutoff,
            "sql": report_sql(contract.report_id, cutoff),
            "ordered": contract.ordered,
        }


class HeartbeatQueueStore(JobStore):
    """BI heartbeat service: only the `bi_heartbeat_*` rows; paused with analytics."""

    def __init__(self, tables: QueueTables, *, attempt_timeout_seconds: float = DEFAULT_ATTEMPT_TIMEOUT_SECONDS):
        self.tables = tables
        self._attempt_timeout_seconds = attempt_timeout_seconds

    def enqueue(self, job: QueuedJob, connection) -> None:
        snapshot = dict(job.input_snapshot or {})
        self.tables.enqueue_row(
            connection, job.job_id, "report", job.job_id, None,
            str(snapshot["sql"]), job.submitted_at_monotonic, job.deadline_at_monotonic, HEARTBEAT_PRIORITY,
        )

    def claim(self, worker_id: str, connection) -> QueuedJob | None:
        row = self.tables.claim_row(connection, "report", worker_id, report_id_prefix=HEARTBEAT_JOB_PREFIX)
        if row is None:
            return None
        job_id, _report_id, _cutoff, _sql, submit_at, deadline, _attempts = row
        return QueuedJob(
            job_id=str(job_id),
            job_kind="heartbeat",
            submitted_at_monotonic=float(submit_at),
            deadline_at_monotonic=float(deadline),
            run=make_report_run(self.tables, attempt_timeout_seconds=self._attempt_timeout_seconds),
            input_snapshot={"ordered": True},
        )

    def record_result(self, job_id: str, result_digest: str, connection) -> None:
        return

    def read_control(self, connection) -> JobControl:
        _max_workers, _quota_mb, analytics_enabled, _ingest = self.tables.config_row(connection)
        return JobControl(max_concurrency=1, paused=not analytics_enabled)

    def job_state(self, job_id: str, connection) -> tuple[str, bool, int]:
        return self.tables.job_state(connection, job_id)


class IngestQueueStore(JobStore):
    """Batch ingest service: one worker; paused only through ingest_enabled."""

    def __init__(self, tables: QueueTables, *, attempt_timeout_seconds: float = DEFAULT_ATTEMPT_TIMEOUT_SECONDS):
        self.tables = tables
        self._attempt_timeout_seconds = attempt_timeout_seconds

    def enqueue(self, job: QueuedJob, connection) -> None:
        self.tables.enqueue_row(
            connection, job.job_id, "ingest", f"ingest_batch_{job.batch_version}", int(job.batch_version),
            "staged_batch_publish", job.submitted_at_monotonic, job.deadline_at_monotonic, INGEST_PRIORITY,
        )

    def claim(self, worker_id: str, connection) -> QueuedJob | None:
        row = self.tables.claim_row(connection, "ingest", worker_id)
        if row is None:
            return None
        job_id, _report_id, batch_cutoff, _sql, submit_at, deadline, _attempts = row
        batch_id = int(batch_cutoff)
        spec = stage_spec(batch_id)
        return QueuedJob(
            job_id=str(job_id),
            job_kind="ingest",
            submitted_at_monotonic=float(submit_at),
            deadline_at_monotonic=float(deadline),
            run=make_ingest_run(self.tables, str(job_id), batch_id,
                                attempt_timeout_seconds=self._attempt_timeout_seconds),
            batch_version=str(batch_id),
            input_snapshot={"stage_table": spec.stage_table, "expected_rows": spec.row_count},
        )

    def record_result(self, job_id: str, result_digest: str, connection) -> None:
        # The ingest body already updated the registry and marked the row delivered.
        return

    def read_control(self, connection) -> JobControl:
        _max_workers, _quota_mb, _analytics, ingest_enabled = self.tables.config_row(connection)
        return JobControl(max_concurrency=1, paused=not ingest_enabled)

    def job_state(self, job_id: str, connection) -> tuple[str, bool, int]:
        return self.tables.job_state(connection, job_id)


class CancelMonitor:
    """Applies public cancel_requested flags by killing the claim connection (KILL TIDB)."""

    def __init__(self, *, tables: QueueTables, connection_factory: Callable[[str], object], poll_interval_seconds: float = 0.5):
        self._tables = tables
        self._connection_factory = connection_factory
        self._poll_interval_seconds = poll_interval_seconds
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._loop, name="tidb5-olap-cancel-monitor", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=30)
            if self._thread.is_alive():
                raise RuntimeError("cancel monitor thread did not stop within 30s")

    def _loop(self) -> None:
        connection = self._connection_factory("tidb5-olap-cancel-monitor")
        while not self._stop.is_set():
            for job_id, conn_id in self._tables.cancel_requested_running(connection):
                self._tables.kill_connection(connection, conn_id)
            self._stop.wait(self._poll_interval_seconds)
        connection.close()


class WarehouseDeliveryRuntime:
    """Owns the warehouse job system for one persistent scenario run."""

    def __init__(
        self,
        connection_factory: Callable[[str], object],
        clock: Clock,
        run_id: str,
        *,
        ledgers: Mapping[str, TrustedLedger],
        input_end_monotonic: float,
        heartbeat_interval_seconds: float = DEFAULT_HEARTBEAT_INTERVAL_SECONDS,
        heartbeat_budget_seconds: float = DEFAULT_HEARTBEAT_BUDGET_SECONDS,
        report_worker_ceiling: int = DEFAULT_REPORT_WORKER_CEILING,
        attempt_timeout_seconds: float = DEFAULT_ATTEMPT_TIMEOUT_SECONDS,
        poll_interval_seconds: float = 0.2,
    ) -> None:
        missing = set(SERVICE_IDS) - set(ledgers)
        if missing:
            raise ValueError(
                "per-service trusted ledgers are required (one service, one ledger): "
                f"missing={sorted(missing)!r}, provided={sorted(ledgers)!r}"
            )
        unknown = set(ledgers) - set(SERVICE_IDS)
        if unknown:
            raise ValueError(f"ledgers carry unknown service ids: unknown={sorted(ledgers)!r}")
        self.connection_factory = connection_factory
        self.clock = clock
        self.run_id = run_id
        self._ledgers = {service_id: ledgers[service_id] for service_id in SERVICE_IDS}
        self.input_end_monotonic = input_end_monotonic
        self._heartbeat_interval_seconds = heartbeat_interval_seconds
        self._heartbeat_budget_seconds = heartbeat_budget_seconds
        self._heartbeat_sequence = 0
        self._lock = threading.Lock()
        self._runtime_started_wall = time.time()

        self.tables = QueueTables()
        self._report_store = ReportQueueStore(self.tables, attempt_timeout_seconds=attempt_timeout_seconds)
        self._heartbeat_store = HeartbeatQueueStore(self.tables, attempt_timeout_seconds=attempt_timeout_seconds)
        self._ingest_store = IngestQueueStore(self.tables, attempt_timeout_seconds=attempt_timeout_seconds)
        self._runners = {
            SERVICE_REPORT: TiDBJobRunner(
                service_id=SERVICE_REPORT,
                ledger=self._ledgers[SERVICE_REPORT],
                clock=clock,
                store=self._report_store,
                connection_factory=connection_factory,
                application_name="tidb5-olap-report",
                max_workers=report_worker_ceiling,
                poll_interval_seconds=poll_interval_seconds,
            ),
            SERVICE_HEARTBEAT: TiDBJobRunner(
                service_id=SERVICE_HEARTBEAT,
                ledger=self._ledgers[SERVICE_HEARTBEAT],
                clock=clock,
                store=self._heartbeat_store,
                connection_factory=connection_factory,
                application_name="tidb5-olap-heartbeat",
                max_workers=1,
                poll_interval_seconds=poll_interval_seconds,
            ),
            SERVICE_INGEST: TiDBJobRunner(
                service_id=SERVICE_INGEST,
                ledger=self._ledgers[SERVICE_INGEST],
                clock=clock,
                store=self._ingest_store,
                connection_factory=connection_factory,
                application_name="tidb5-olap-ingest",
                max_workers=1,
                poll_interval_seconds=poll_interval_seconds,
            ),
        }
        self._cancel_monitor = CancelMonitor(tables=self.tables, connection_factory=connection_factory)
        self._stop_input = threading.Event()
        self._monitor_threads: list[threading.Thread] = []
        self._started = False
        self._stopped = False

    # -- submission API used by capabilities and the timeline ------------------

    def start_correction_wave(self, batch_id: int, at: float) -> threading.Thread:
        """Upstream correction wave: rewrite both stage tables
        with the corrected re-delivery, then atomically re-publish the batch.

        The wave runs on its own connection as a real background ingest; its
        progress is registry-visible (republished_at) and audited. Returns the
        wave thread so tests can join it deterministically.
        """
        if batch_id != BATCH_A_ID:
            raise ValueError(f"the correction wave re-publishes batch A only: batch_id={batch_id}")

        def run_wave() -> None:
            connection = self.connection_factory("tidb5-olap-correction-wave")
            try:
                for stage_table in (stage_spec(BATCH_A_ID).stage_table, stage_spec(BATCH_B_ID).stage_table):
                    self.tables.rewrite_stage_with_correction(connection, stage_table, at, batch_id)
                self.tables.republish_batch(connection, batch_id, at)
            finally:
                connection.close()

        wave = threading.Thread(target=run_wave, name=f"tidb5-olap-{self.run_id}-correction-wave", daemon=True)
        self._monitor_threads.append(wave)
        wave.start()
        return wave

    def start_maintenance_analyze(self, at: float) -> threading.Thread:
        """Scheduler maintenance pass (release window): a real
        maintenance session rebuilding stage-table statistics (FULL ANALYZE on the
        non-target staging tables rewritten by the correction wave), audited per
        phase. Returns the session thread so tests can join it deterministically.
        """

        def run_maintenance() -> None:
            connection = self.connection_factory("tidb5-olap-maintenance")
            try:
                for stage_table in (stage_spec(BATCH_A_ID).stage_table, stage_spec(BATCH_B_ID).stage_table):
                    self.tables.record_maintenance_analyze(connection, at, stage_table, "started")
                    with connection.cursor() as cursor:
                        cursor.execute(f"ANALYZE TABLE {stage_table};")
                    connection.commit()
                    self.tables.record_maintenance_analyze(connection, at, stage_table, "finished")
            finally:
                connection.close()

        maintenance = threading.Thread(target=run_maintenance, name=f"tidb5-olap-{self.run_id}-maintenance-analyze", daemon=True)
        self._monitor_threads.append(maintenance)
        maintenance.start()
        return maintenance

    def set_analyze_after_ingest(self, batch_id: int, analyze_after_ingest: bool, at: float) -> dict:
        connection = self.connection_factory("tidb5-olap-registry-release")
        try:
            return self.tables.set_analyze_after_ingest(connection, batch_id, analyze_after_ingest, at)
        finally:
            connection.close()

    def apply_queue_config_release(self, at: float, **config_changes: object) -> dict:
        connection = self.connection_factory("tidb5-olap-config-release")
        try:
            return self.tables.update_config(connection, at, **config_changes)
        finally:
            connection.close()

    def submit_ingest(self, batch_id: int, deadline_at_monotonic: float) -> str:
        spec = stage_spec(batch_id)
        job_id = f"ingest_batch_{batch_id}"
        at = self.clock.monotonic()
        self._runners[SERVICE_INGEST].submit(
            QueuedJob(
                job_id=job_id,
                job_kind="ingest",
                submitted_at_monotonic=at,
                deadline_at_monotonic=deadline_at_monotonic,
                run=make_ingest_run(self.tables, job_id, batch_id,
                                    attempt_timeout_seconds=DEFAULT_ATTEMPT_TIMEOUT_SECONDS),
                batch_version=str(batch_id),
                input_snapshot={"stage_table": spec.stage_table, "expected_rows": spec.row_count},
            )
        )
        return job_id

    def submit_required_report(self, report_id: str, batch_number: int, deadline_at_monotonic: float) -> str:
        deliverable_id = f"{report_id}_batch{batch_number}"
        at = self.clock.monotonic()
        self._runners[SERVICE_REPORT].submit(
            QueuedJob(
                job_id=deliverable_id,
                job_kind="report",
                submitted_at_monotonic=at,
                deadline_at_monotonic=deadline_at_monotonic,
                run=make_report_run(self.tables, attempt_timeout_seconds=DEFAULT_ATTEMPT_TIMEOUT_SECONDS),
                # The deliverable contract binds the report through `through_batch_N`:
                # the checklist evaluation compares the ledger
                # batch_version to `input_batch_binding` literally, so the binding
                # must travel with the job from submission.
                batch_version=f"through_batch_{batch_number}",
                input_snapshot={
                    "report_id": report_id,
                    "batch_cutoff": batch_number,
                    "sql": report_sql(report_id, batch_number),
                    "ordered": REPORT_CONTRACTS_BY_ID[report_id].ordered,
                },
            )
        )
        return deliverable_id

    def submit_heartbeat(self, deadline_at_monotonic: float) -> str:
        with self._lock:
            self._heartbeat_sequence += 1
            sequence = self._heartbeat_sequence
        query_id = heartbeat_query_ids()[sequence % len(heartbeat_query_ids())]
        job_id = heartbeat_job_id(query_id, sequence)
        at = self.clock.monotonic()
        since_ts = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.gmtime(self._runtime_started_wall + self.clock.monotonic() - 3600)
        )
        self._runners[SERVICE_HEARTBEAT].submit(
            QueuedJob(
                job_id=job_id,
                job_kind="heartbeat",
                submitted_at_monotonic=at,
                deadline_at_monotonic=deadline_at_monotonic,
                run=make_report_run(self.tables, attempt_timeout_seconds=DEFAULT_ATTEMPT_TIMEOUT_SECONDS),
                input_snapshot={
                    "report_id": f"heartbeat_{query_id}",
                    "batch_cutoff": 2,
                    "sql": heartbeat_sql(query_id, 2, since_ts),
                    "ordered": True,
                },
            )
        )
        return job_id

    # -- PersistentWorkloadRuntime protocol ------------------------------------

    def start(self) -> None:
        if self._started:
            raise RuntimeError(f"warehouse delivery runtime cannot start twice: run_id={self.run_id!r}")
        self._started = True
        for runner in self._runners.values():
            runner.start()
        self._cancel_monitor.start()
        self._spawn_monitor("heartbeat-submitter", self._heartbeat_loop)

    def _spawn_monitor(self, name: str, target) -> None:
        thread = threading.Thread(target=target, name=f"tidb5-olap-{self.run_id}-{name}", daemon=True)
        self._monitor_threads.append(thread)
        thread.start()

    def wait_for_warmup(self) -> float:
        """No internal warmup phase; provisioning happens at deploy time."""
        return self.clock.monotonic()

    def stop_new_requests(self) -> None:
        self._stop_input.set()
        for runner in self._runners.values():
            runner.stop_new_requests()

    def drain(self) -> None:
        for runner in self._runners.values():
            runner.drain()

    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self.stop_new_requests()
        self._cancel_monitor.stop()
        for runner in self._runners.values():
            runner.stop()
        for thread in self._monitor_threads:
            thread.join(timeout=30)
            if thread.is_alive():
                raise RuntimeError(
                    f"warehouse delivery monitor thread did not stop: run_id={self.run_id!r}, thread={thread.name!r}"
                )

    def ledgers(self) -> Mapping[str, TrustedLedger]:
        return dict(self._ledgers)

    def baseline_facts(self) -> Mapping[str, object]:
        connection = self.connection_factory("tidb5-olap-baseline")
        try:
            max_workers, quota_mb, analytics_enabled, ingest_enabled = self.tables.config_row(connection)
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT batch_id, row_count, ingest_finished_at IS NOT NULL FROM {BATCH_REGISTRY} ORDER BY batch_id;"
                )
                batches = [
                    {"batch_id": int(row[0]), "row_count": int(row[1]), "ingested": bool(row[2])}
                    for row in cursor.fetchall()
                ]
            connection.rollback()
        finally:
            connection.close()
        return {
            "queue_config": {
                "max_workers": max_workers,
                "report_memory_quota_mb": quota_mb,
                "analytics_enabled": analytics_enabled,
                "ingest_enabled": ingest_enabled,
            },
            "batch_registry": batches,
        }

    # -- monitors ---------------------------------------------------------------

    def _heartbeat_loop(self) -> None:
        while not self._stop_input.is_set():
            now = self.clock.monotonic()
            if now >= self.input_end_monotonic:
                return
            self.submit_heartbeat(now + self._heartbeat_budget_seconds)
            self.clock.wait_until(now + self._heartbeat_interval_seconds, self._stop_input)
