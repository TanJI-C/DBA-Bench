"""Warehouse reporting driver: composes core job runners over the public control tables.

The driver implements the frozen `PersistentWorkloadRuntime` protocol
by combining three `JobQueueRunner` services — report/heartbeat, batch ingest, backup —
with a cancellation monitor and the heartbeat submission rhythm. All trusted facts land
in the shared `TrustedLedger`; the public `wh.*` tables are the real scheduling surface.
"""

from __future__ import annotations

import json
import threading
from collections.abc import Mapping

from src.persistent_scenarios.backend.postgres.workloads.olap import JobQueueRunner, QueuedJob
from src.persistent_scenarios.backend.postgres.workloads.watermark import FreshnessRecorder
from src.persistent_scenarios.runtime.ledger import FreshnessSample, TrustedLedger

from .reports import REQUIRED_REPORT_IDS, canonical_report_sql, deliverable_job_id, report_contract
from .schema import STAGE_BATCHES
from .store import (
    BackupQueueStore,
    HeartbeatQueueStore,
    IngestQueueStore,
    MAINTENANCE_INVALIDATION_NOTE,
    QueueTables,
    ReportQueueStore,
    heartbeat_job_id,
    heartbeat_query_ids,
    heartbeat_sql,
    ingest_stage_spec,
)

_STAGE_BY_BATCH = {spec.batch_id: spec for spec in STAGE_BATCHES}

DEFAULT_HEARTBEAT_INTERVAL_SECONDS = 90.0
DEFAULT_HEARTBEAT_BUDGET_SECONDS = 30.0
DEFAULT_REPORT_WORKER_CEILING = 6
DEFAULT_BACKUP_PASS_COUNT = 4
DEFAULT_ATTEMPT_TIMEOUT_SECONDS = 900.0
DEFAULT_WATERMARK_SAMPLE_INTERVAL_SECONDS = 30.0
DRAIN_GRACE_SECONDS = 60.0
# The premature completion lie must stay observable across
# inspection cycles for the whole trap window [marker publish, real ingest
# completion]. The upstream publisher re-asserts its registry marker on this
# cadence — shorter than the 300s inspection interval, so every inspection cycle
# landing inside the window observes a fresh lie — until the real ingest
# completion overwrites the row (the guarded re-assert can never touch truth).
PREMATURE_MARKER_REPEAT_INTERVAL_SECONDS = 60.0
# The maintenance attempt-invalidation monitor: the upstream
# maintenance pipeline polls the public queue on this cadence while its
# "statistics rebuild window" is open. Its invalidation budget is self-limiting
# (the queue retry budget, MAX_ATTEMPTS) and the whole loop is wall-clock bounded.
MAINTENANCE_INVALIDATION_POLL_SECONDS = 1.0
MAINTENANCE_INVALIDATION_MAX_POLL_SECONDS = 900.0
# The last planned submission may sit exactly on input_stop; a real clock read can
# overshoot the boundary by scheduling jitter (sub-millisecond to low milliseconds).
# Submissions within this slack of input_stop are still the planned input; anything
# later is a genuine contract violation.
INPUT_END_TOLERANCE_SECONDS = 1.0

SERVICE_REPORT = "wh_report_service"
SERVICE_HEARTBEAT = "wh_heartbeat_service"
SERVICE_INGEST = "wh_ingest_service"
SERVICE_BACKUP = "wh_backup_service"
SERVICE_IDS = (SERVICE_REPORT, SERVICE_HEARTBEAT, SERVICE_INGEST, SERVICE_BACKUP)


class WarehouseReportingRuntime:
    """Owns the warehouse job system for one persistent scenario run."""

    def __init__(
        self,
        env,
        clock,
        run_id: str,
        *,
        ledgers: Mapping[str, TrustedLedger],
        input_end_monotonic: float,
        heartbeat_interval_seconds: float = DEFAULT_HEARTBEAT_INTERVAL_SECONDS,
        heartbeat_budget_seconds: float = DEFAULT_HEARTBEAT_BUDGET_SECONDS,
        report_worker_ceiling: int = DEFAULT_REPORT_WORKER_CEILING,
        backup_pass_count: int = DEFAULT_BACKUP_PASS_COUNT,
        attempt_timeout_seconds: float = DEFAULT_ATTEMPT_TIMEOUT_SECONDS,
        watermark_sample_interval_seconds: float = DEFAULT_WATERMARK_SAMPLE_INTERVAL_SECONDS,
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
            raise ValueError(f"ledgers carry unknown service ids: unknown={sorted(unknown)!r}")
        self.env = env
        self.clock = clock
        self.run_id = run_id
        self._ledgers = {service_id: ledgers[service_id] for service_id in SERVICE_IDS}
        self.input_end_monotonic = input_end_monotonic
        self.heartbeat_interval_seconds = heartbeat_interval_seconds
        self.heartbeat_budget_seconds = heartbeat_budget_seconds
        self.tables = QueueTables(env)
        self.backup_pass_count = backup_pass_count

        def connection_factory(application_name: str):
            return self.tables.connect(application_name)

        self.report_runner = JobQueueRunner(
            service_id="wh_report_service",
            ledger=ledgers["wh_report_service"],
            clock=clock,
            store=ReportQueueStore(self.tables, attempt_timeout_seconds=attempt_timeout_seconds),
            connection_factory=connection_factory,
            application_name=f"{run_id}-report",
            max_workers=report_worker_ceiling,
            poll_interval_seconds=poll_interval_seconds,
            drain_grace_seconds=DRAIN_GRACE_SECONDS,
        )
        self.ingest_runner = JobQueueRunner(
            service_id="wh_ingest_service",
            ledger=ledgers["wh_ingest_service"],
            clock=clock,
            store=IngestQueueStore(self.tables, attempt_timeout_seconds=attempt_timeout_seconds),
            connection_factory=connection_factory,
            application_name=f"{run_id}-ingest",
            max_workers=1,
            poll_interval_seconds=poll_interval_seconds,
            drain_grace_seconds=DRAIN_GRACE_SECONDS,
        )
        self.backup_runner = JobQueueRunner(
            service_id="wh_backup_service",
            ledger=ledgers["wh_backup_service"],
            clock=clock,
            store=BackupQueueStore(self.tables, backup_pass_count=backup_pass_count,
                                   attempt_timeout_seconds=attempt_timeout_seconds),
            connection_factory=connection_factory,
            application_name=f"{run_id}-backup",
            max_workers=1,
            poll_interval_seconds=poll_interval_seconds,
            drain_grace_seconds=DRAIN_GRACE_SECONDS,
        )
        self.heartbeat_runner = JobQueueRunner(
            service_id="wh_heartbeat_service",
            ledger=ledgers["wh_heartbeat_service"],
            clock=clock,
            store=HeartbeatQueueStore(self.tables, attempt_timeout_seconds=attempt_timeout_seconds),
            connection_factory=connection_factory,
            application_name=f"{run_id}-heartbeat",
            max_workers=1,
            poll_interval_seconds=poll_interval_seconds,
            drain_grace_seconds=DRAIN_GRACE_SECONDS,
        )
        self._runners = (self.report_runner, self.ingest_runner, self.backup_runner, self.heartbeat_runner)
        self.freshness_recorder = FreshnessRecorder(
            service_id="wh_warehouse_watermark",
            ledger=self.report_ledger,
            clock=clock,
            sample=self._sample_watermark,
            interval_seconds=watermark_sample_interval_seconds,
        )
        self._stop_input = threading.Event()
        self._stop_monitor = threading.Event()
        self._monitor_threads: list[threading.Thread] = []
        self._heartbeat_sequence = 0
        self.premature_marker_reasserts: list[float] = []
        self.maintenance_invalidation_writes: list[float] = []
        self._started = False
        self._stopped = False

    @property
    def report_ledger(self) -> TrustedLedger:
        return self._ledgers[SERVICE_REPORT]

    @property
    def heartbeat_ledger(self) -> TrustedLedger:
        return self._ledgers[SERVICE_HEARTBEAT]

    @property
    def ingest_ledger(self) -> TrustedLedger:
        return self._ledgers[SERVICE_INGEST]

    @property
    def backup_ledger(self) -> TrustedLedger:
        return self._ledgers[SERVICE_BACKUP]

    # ------------------------------------------------------------------ submissions

    def _check_accepting(self, now: float, deadline: float) -> None:
        if self._stop_input.is_set():
            raise ValueError(f"warehouse input is frozen: run_id={self.run_id!r}")
        if now > self.input_end_monotonic + INPUT_END_TOLERANCE_SECONDS:
            raise ValueError(
                "job submission arrived after the frozen input end: "
                f"run_id={self.run_id!r}, now={now}, input_end={self.input_end_monotonic}, "
                f"tolerance={INPUT_END_TOLERANCE_SECONDS}"
            )
        if deadline <= now:
            raise ValueError(
                f"job deadline does not follow submission: report now={now}, deadline={deadline}"
            )

    def submit_required_report(self, report_id: str, batch_id: int, deadline: float,
                               *, definition_sql: str | None = None) -> str:
        if report_id not in REQUIRED_REPORT_IDS:
            raise KeyError(
                f"report is not on the required delivery list: report_id={report_id!r}, "
                f"required={sorted(REQUIRED_REPORT_IDS)!r}"
            )
        contract = report_contract(report_id)
        now = self.clock.monotonic()
        self._check_accepting(now, deadline)
        job_id = deliverable_job_id(report_id, batch_id)
        self.report_runner.submit(QueuedJob(
            job_id=job_id,
            job_kind="required_report",
            submitted_at_monotonic=now,
            deadline_at_monotonic=deadline,
            run=_never_executed(job_id),
            batch_version=str(batch_id),
            input_snapshot={
                # The deployed definition is what the release pipeline published into
                # the queue; the binding snapshot keeps declaring the contract, so a
                # definition that drifts from it is visible by row inspection.
                "sql": definition_sql if definition_sql is not None else canonical_report_sql(report_id, batch_id),
                "ordered": contract.ordered,
                "cutoff": batch_id,
                "binding": f"exact_batch_{batch_id}" if contract.binds_exact_batch else f"through_batch_{batch_id}",
            },
        ))
        return job_id

    def submit_ingest(self, batch_id: int, deadline: float) -> str:
        now = self.clock.monotonic()
        self._check_accepting(now, deadline)
        spec = ingest_stage_spec(batch_id)
        job_id = f"ingest_batch_{batch_id}"
        self.ingest_runner.submit(QueuedJob(
            job_id=job_id,
            job_kind="ingest",
            submitted_at_monotonic=now,
            deadline_at_monotonic=deadline,
            run=_never_executed(job_id),
            batch_version=str(batch_id),
            input_snapshot={"stage_table": spec.stage_table, "expected_rows": spec.row_count},
        ))
        return job_id

    def submit_backup(self, deadline: float) -> str:
        now = self.clock.monotonic()
        self._check_accepting(now, deadline)
        job_id = "routine_backup_read"
        self.backup_runner.submit(QueuedJob(
            job_id=job_id,
            job_kind="backup",
            submitted_at_monotonic=now,
            deadline_at_monotonic=deadline,
            run=_never_executed(job_id),
            batch_version=None,
            input_snapshot={"passes": self.backup_pass_count},
        ))
        return job_id

    def submit_heartbeat(self, query_id: str, deadline: float) -> str:
        now = self.clock.monotonic()
        self._check_accepting(now, deadline)
        self._heartbeat_sequence += 1
        job_id = heartbeat_job_id(f"{self.run_id}-{query_id}", self._heartbeat_sequence)
        self.heartbeat_runner.submit(QueuedJob(
            job_id=job_id,
            job_kind="heartbeat",
            submitted_at_monotonic=now,
            deadline_at_monotonic=deadline,
            run=_never_executed(job_id),
            batch_version=None,
            input_snapshot={"sql": heartbeat_sql(query_id), "ordered": True},
        ))
        return job_id

    # ---------------------------------------------------- external config releases

    def apply_queue_config_release(self, at: float, **changes: object) -> dict[str, object]:
        connection = self.tables.connect("config-release")
        try:
            return self.tables.update_config(connection, at, **changes)
        finally:
            connection.close()

    def apply_ingest_control_release(self, batch_id: int, analyze_after_ingest: bool, at: float) -> dict[str, object]:
        connection = self.tables.connect("ingest-control-release")
        try:
            new_state = self.tables.update_ingest_control(connection, batch_id, analyze_after_ingest, at)
        finally:
            connection.close()
        return new_state

    def apply_database_release(self, sql: str, audit_table: str, at: float) -> None:
        connection = self.tables.connect("database-release")
        try:
            self.tables.execute_release_sql(connection, sql, audit_table, at)
        finally:
            connection.close()

    def effective_database_guc(self, guc_name: str) -> str:
        """GUC value on a fresh session — the only view that inherits
        database/role-scoped settings (existing sessions keep startup values)."""
        connection = self.tables.connect("guc-probe")
        try:
            return self.tables.database_guc_value(connection, guc_name)
        finally:
            connection.close()

    def audit_report_definition_release(self, batch_id: int, definitions: Mapping[str, str], at: float) -> dict[str, object]:
        """Audit the published report definitions of one release into wh.config_audit."""
        if not definitions:
            raise ValueError(
                f"a definition release must deploy at least one definition: batch_id={batch_id}"
            )
        payload = json.dumps(
            {"batch_id": batch_id, "definitions": dict(sorted(definitions.items()))},
            sort_keys=True,
        )
        connection = self.tables.connect("definition-release")
        try:
            row = self.tables.audit_release(connection, at, "wh.report_queue", "", payload)
        finally:
            connection.close()
        return row

    def batch_ingest_completion_state(self, batch_id: int) -> dict[str, object]:
        """Authoritative batch ingest progress fact (queue row + registry truth)."""
        connection = self.tables.connect("ingest-state")
        try:
            return self.tables.batch_ingest_state(connection, batch_id, f"ingest_batch_{batch_id}")
        finally:
            connection.close()

    def read_batch_registry_state(self, batch_id: int) -> dict[str, object]:
        connection = self.tables.connect("registry-state")
        try:
            return self.tables.batch_registry_state(connection, batch_id)
        finally:
            connection.close()

    def publish_premature_batch_marker(self, batch_id: int, marker_at: float) -> dict[str, object] | None:
        connection = self.tables.connect("premature-marker")
        try:
            return self.tables.publish_premature_registry_marker(connection, batch_id, marker_at)
        finally:
            connection.close()

    def start_premature_marker_repeat(self, batch_id: int, first_marker_at: float) -> None:
        """Keep the premature completion lie observable across inspection cycles.

        Spawns the re-assert monitor: every repeat cadence step the guarded
        re-assert re-stamps the lie (auditing each step) until the real ingest
        completion lands and makes the guard refuse — the lie stays transient by
        construction. ``first_marker_at`` only feeds the run evidence; the loop
        itself stamps the current instant on every re-assert.
        """
        self._spawn_monitor("premature-marker-repeat", lambda: repeat_premature_registry_marker(
            self.tables, self.clock, batch_id=batch_id,
            interval_seconds=PREMATURE_MARKER_REPEAT_INTERVAL_SECONDS,
            stop_event=self._stop_monitor, journal=self.premature_marker_reasserts,
        ))

    def audit_maintenance_invalidation_release(self, job_id: str, at: float) -> dict[str, object]:
        """Audit the maintenance pipeline's attempt-invalidation policy release."""
        connection = self.tables.connect("maintenance-release")
        try:
            return self.tables.audit_release(
                connection, at, "wh.report_queue", "",
                json.dumps({"note": MAINTENANCE_INVALIDATION_NOTE, "job_id": job_id,
                            "release": "statistics rebuild window opened"}, sort_keys=True),
            )
        finally:
            connection.close()

    def start_maintenance_invalidation_monitor(self, job_id: str, max_invalidations: int) -> None:
        """Spawn the maintenance pipeline's attempt-invalidation monitor."""
        self._spawn_monitor("maintenance-invalidation", lambda: invalidate_running_report_attempts(
            self.tables, self.clock, job_id=job_id, max_invalidations=max_invalidations,
            poll_seconds=MAINTENANCE_INVALIDATION_POLL_SECONDS,
            max_poll_seconds=MAINTENANCE_INVALIDATION_MAX_POLL_SECONDS,
            stop_event=self._stop_monitor, journal=self.maintenance_invalidation_writes,
        ))

    # ------------------------------------------------------------------ protocol

    def start(self) -> None:
        if self._started:
            raise RuntimeError(f"warehouse reporting runtime cannot start twice: run_id={self.run_id!r}")
        self._started = True
        for runner in self._runners:
            runner.start()
        self.freshness_recorder.start()
        self._spawn_monitor("heartbeat-submitter", self._heartbeat_loop)
        self._spawn_monitor("cancel-monitor", self._cancel_loop)

    def _spawn_monitor(self, name: str, target) -> None:
        thread = threading.Thread(target=target, name=f"pg5r-olap-{self.run_id}-{name}", daemon=True)
        self._monitor_threads.append(thread)
        thread.start()

    def wait_for_warmup(self) -> float:
        """No internal warmup phase; provisioning happens at deploy time."""
        return self.clock.monotonic()

    def stop_new_requests(self) -> None:
        self._stop_input.set()
        for runner in self._runners:
            runner.stop_new_requests()

    def drain(self) -> None:
        for runner in self._runners:
            runner.drain()

    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self.stop_new_requests()
        self._stop_monitor.set()
        self.freshness_recorder.stop()
        for runner in self._runners:
            runner.stop()
        for thread in self._monitor_threads:
            thread.join(timeout=30)
            if thread.is_alive():
                raise RuntimeError(
                    f"warehouse reporting monitor thread did not stop: run_id={self.run_id!r}, thread={thread.name!r}"
                )

    def ledgers(self) -> dict[str, TrustedLedger]:
        return dict(self._ledgers)

    def baseline_facts(self) -> dict[str, object]:
        connection = self.tables.connect("baseline")
        try:
            max_workers, work_mb, analytics_enabled, backup_enabled = self.tables.config_row(connection)
            with connection.cursor() as cursor:
                cursor.execute("SELECT batch_id, row_count, ingest_finished_at IS NOT NULL FROM wh.batch_registry ORDER BY batch_id;")
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
                "work_mb": work_mb,
                "analytics_enabled": analytics_enabled,
                "backup_enabled": backup_enabled,
            },
            "batch_registry": batches,
        }

    # ------------------------------------------------------------------ monitors

    def _heartbeat_loop(self) -> None:
        rotation = 0
        while not self._stop_input.is_set():
            now = self.clock.monotonic()
            if now >= self.input_end_monotonic:
                return
            query_id = heartbeat_query_ids()[rotation % len(heartbeat_query_ids())]
            rotation += 1
            self.submit_heartbeat(query_id, now + self.heartbeat_budget_seconds)
            self.clock.wait_until(now + self.heartbeat_interval_seconds, self._stop_input)

    def _sample_watermark(self, sequence: int) -> FreshnessSample:
        """Batch watermark: the highest fully ingested batch, sampled for freshness."""
        connection = self.tables.connect("watermark")
        try:
            row = QueueTables._fetchone(
                connection,
                "SELECT COALESCE(max(batch_id), 0) FROM wh.batch_registry WHERE ingest_finished_at IS NOT NULL;",
            )
        finally:
            connection.close()
        watermark_batch = int(row[0])
        return FreshnessSample(
            sample_id=f"wh-watermark-{sequence:05d}",
            sampled_at_monotonic=self.clock.monotonic(),
            primary_watermark=f"batch-{watermark_batch}",
            replica_watermark=f"batch-{watermark_batch}",
            lag_seconds=None,
            detail={"watermark_batch": watermark_batch, "sampler": "batch_registry"},
        )

    def _cancel_loop(self) -> None:
        while not self._stop_monitor.is_set():
            connection = self.tables.connect("cancel-monitor")
            try:
                for _job_id, pid in self.tables.cancel_requested_running(connection):
                    self.tables.cancel_backend(connection, pid)
            finally:
                connection.close()
            self._stop_monitor.wait(0.25)


def repeat_premature_registry_marker(tables, clock, *, batch_id: int, interval_seconds: float,
                                     stop_event: threading.Event, journal: list) -> int:
    """Re-assert the premature completion lie until the real ingest completes.

    Every cadence step re-stamps the lie and audits it (the trap-window evidence
    trail); the guarded UPDATE inside the store makes a re-assert over the true
    completion impossible, so the loop ends the moment truth lands. Returns the
    number of re-asserts written into ``journal``.
    """
    reasserts = 0
    while not stop_event.is_set():
        if not clock.wait_until(clock.monotonic() + interval_seconds, stop_event):
            break
        connection = tables.connect("premature-marker-repeat")
        try:
            if not tables.reassert_premature_registry_marker(connection, batch_id, clock.monotonic()):
                break
        finally:
            connection.close()
        reasserts += 1
        journal.append(clock.monotonic())
    return reasserts


def invalidate_running_report_attempts(tables, clock, *, job_id: str, max_invalidations: int,
                                       poll_seconds: float, max_poll_seconds: float,
                                       stop_event: threading.Event, journal: list) -> int:
    """Maintenance-pipeline attempt invalidations within its rebuild window.

    Polls the public queue row and requests cancellation of every attempt found
    running, until the invalidation budget (the queue retry budget) is spent, the
    row reaches a terminal state, or the window bound expires. The guard inside
    ``invalidate_running_attempt`` keeps each write single-counted; the loop is
    what turns the pipeline's policy into a retry-budget burn. Returns the number
    of invalidations written into ``journal``.
    """
    invalidations = 0
    window_deadline = clock.monotonic() + max_poll_seconds
    while (not stop_event.is_set() and invalidations < max_invalidations
           and clock.monotonic() < window_deadline):
        if not clock.wait_until(clock.monotonic() + poll_seconds, stop_event):
            break
        connection = tables.connect("maintenance-invalidation")
        try:
            state = tables.maintenance_attempt_state(connection, job_id)
            if state is not None and state["status"] in ("failed", "delivered", "canceled"):
                break  # terminal: the retry budget is spent or the delivery landed
            if (state is not None and state["status"] == "running"
                    and not state["cancel_requested"]
                    and tables.invalidate_running_attempt(connection, job_id, clock.monotonic())):
                invalidations += 1
                journal.append(clock.monotonic())
        finally:
            connection.close()
    return invalidations


def _never_executed(job_id: str):
    def run(job, connection) -> str:
        raise RuntimeError(
            "submission-time job body must never execute; the queue store rebuilds the "
            f"authoritative body at claim time: job_id={job_id!r}"
        )
    return run
