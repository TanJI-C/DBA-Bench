"""Instance driver for pg_htap_replica_freshness.

Composes core shared executors with instance business SQL:
- OltpTransactionPool for primary order submissions;
- JobQueueRunner + FreshnessReportJobStore for standby report deliveries
  (freshness wait, recovery-conflict retry, honest visible-watermark
  recording into frs_report_jobs and the external ledger);
- FreshnessRecorder sampling primary commit watermarks and replica replay
  visibility at a rate that covers every delivery moment.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import psycopg2

from src.persistent_scenarios.backend.postgres.workloads import (
    JobControl,
    JobQueueRunner,
    JobQueueStore,
    LogicalTransactionPlan,
    OltpTransactionPool,
    QueuedJob,
)
from src.persistent_scenarios.runtime.ledger import FreshnessSample, TrustedLedger

from ..htap_common.external_ledger import ExternalJsonlLedger
from ..htap_common.pool_retry import retry_failed_plans
from .calendar import FreshnessBusinessCalendar, PRODUCTION_CALENDAR
from .schema import APP_OLTP, ROLE_OLTP, ROLE_REPORT

REPORT_POLL_SECONDS = 1.0
WATERMARK_INTERVAL_SECONDS = 5.0
RETRY_SWEEP_SECONDS = 0.25
LINK_POLICY_POLL_SECONDS = 2.0
LINK_POLICY_CONTROL_KEY = "replication_link_rate_kbit"

REPORT_QUERIES = {
    "default": (
        "SELECT count(*), COALESCE(sum(amount), 0.0) FROM frs_orders "
        "WHERE updated_at > clock_timestamp() - interval '15 minutes';"
    ),
    "events": (
        "SELECT count(*), COALESCE(sum(event_id % 97), 0) FROM frs_order_events "
        "WHERE created_at > clock_timestamp() - interval '30 minutes';"
    ),
}


@dataclass(frozen=True, slots=True)
class WorkloadRates:
    orders_qps: float = 4.0
    orders_timeout_ms: int = 1500
    report_statement_timeout_ms: int = 30000


def lsn_to_int(lsn: str) -> int:
    high, low = str(lsn).split("/")
    return int(high, 16) * (1 << 32) + int(low, 16)


def _set_role(cursor, role: str) -> None:
    cursor.execute(f"SET ROLE {role};")


class FreshnessReportJobStore(JobQueueStore):
    """Public frs_report_jobs queue executed against the standby.

    The run callable waits until the replica replay covers a fresh-enough
    watermark (contract freshness budget), executes the report under the
    standby snapshot policy and retries real recovery-conflict cancellations
    until the business deadline. A missed deadline ends as an explicit
    deadline_missed row in the external ledger plus a trusted terminal whose
    delivered_at is past the deadline (delivered_on_time=False); it is never a
    stale delivery. Raising here would kill the shared job worker thread and
    leave the planned job without any terminal, so the miss is a return value.
    """

    def __init__(
        self,
        open_connection: Callable[[str, str], object],
        watermark_view: "WatermarkView",
        reports_ledger: ExternalJsonlLedger,
        runtime,
    ):
        self._open_connection = open_connection
        self._watermarks = watermark_view
        self._reports_ledger = reports_ledger
        self._runtime = runtime

    def enqueue(self, job: QueuedJob, connection: object) -> None:
        params = job.input_snapshot or {}
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO frs_report_jobs (ref, report_kind, freshness_budget_seconds, deadline_at) "
                "VALUES (%s, %s, %s, %s);",
                (
                    job.job_id,
                    params["report_kind"],
                    int(params["freshness_budget_seconds"]),
                    self._deadline_timestamp(job.deadline_at_monotonic),
                ),
            )

    def claim(self, worker_id: str, connection: object) -> QueuedJob | None:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE frs_report_jobs SET state = 'running' WHERE ref = ("
                "SELECT ref FROM frs_report_jobs WHERE state = 'queued' "
                "ORDER BY job_id LIMIT 1 FOR UPDATE SKIP LOCKED) "
                "RETURNING ref, report_kind, freshness_budget_seconds, deadline_at, "
                "(SELECT control_value FROM frs_work_control "
                "WHERE control_key = 'report_statement_timeout_ms');"
            )
            row = cursor.fetchone()
        if row is None:
            return None
        ref, report_kind, budget, deadline_at, statement_timeout_ms = (
            str(row[0]), str(row[1]), int(row[2]), row[3], int(row[4]),
        )
        deadline_wall = deadline_at if isinstance(deadline_at, _dt.datetime) else _dt.datetime.fromisoformat(str(deadline_at))
        if deadline_wall.tzinfo is None:
            deadline_wall = deadline_wall.replace(tzinfo=_dt.timezone.utc)

        def run(job: QueuedJob, connection: object) -> str:
            return self._execute_with_freshness_and_retry(ref, report_kind, budget, deadline_wall, statement_timeout_ms)

        return QueuedJob(job_id=ref, job_kind="report", submitted_at_monotonic=0.0, deadline_at_monotonic=0.0, run=run)

    def _execute_with_freshness_and_retry(
        self, ref: str, report_kind: str, budget: int, deadline_wall: _dt.datetime, statement_timeout_ms: int
    ) -> str:
        wall_offset = time.time() - time.monotonic()
        deadline_monotonic = deadline_wall.timestamp() - wall_offset
        attempts = 0
        while True:
            attempts += 1
            if time.monotonic() >= deadline_monotonic:
                self._miss_deadline(ref, report_kind, "deadline passed before a fresh snapshot was available")
                return self._miss_digest(ref, report_kind)
            replay_int = lsn_to_int(self._runtime._standby_replay_lsn())
            visible = self._watermarks.visible_watermark(replay_int)
            if visible is not None:
                watermark_lag = self._runtime.business_seconds_now() - visible[1]
                if watermark_lag > budget:
                    time.sleep(REPORT_POLL_SECONDS)
                    continue
            delivery = self._run_report_query(report_kind, statement_timeout_ms)
            if delivery["status"] == "delivered":
                return self._record_delivery(ref, report_kind, delivery, visible)
            if delivery["status"] == "recovery_conflict":
                self._reports_ledger.append(
                    "report_attempt_cancelled",
                    job_id=ref,
                    report_kind=report_kind,
                    attempt=attempts,
                    replay_lsn=delivery["replay_lsn"],
                    visible_watermark_seq=None if visible is None else visible[0],
                    business_seconds=round(self._runtime.business_seconds_now(), 3),
                )
                time.sleep(min(10.0, 2.0 * attempts))
                continue
            raise RuntimeError(f"Report query failed without a retryable terminal: ref={ref!r}, delivery={delivery!r}")

    def _run_report_query(self, report_kind: str, statement_timeout_ms: int) -> dict[str, Any]:
        connection = self._open_connection("pg5r-htap4-report-exec", "standby")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_last_wal_replay_lsn();")
                replay_lsn = str(cursor.fetchone()[0])
                cursor.execute(f"SET statement_timeout = {statement_timeout_ms};")
                cursor.execute(REPORT_QUERIES["default" if report_kind.startswith("routine") else "events"])
                rows = cursor.fetchall()
            connection.rollback()
        except psycopg2.Error as exc:
            status = "recovery_conflict" if "conflict with recovery" in str(exc) else "query_error"
            return {"status": status, "error": str(exc).strip(), "replay_lsn": None}
        finally:
            connection.close()
        digest = hashlib.sha256(
            "\n".join("|".join(str(value) for value in row) for row in rows).encode("utf-8")
        ).hexdigest()
        return {"status": "delivered", "rows": len(rows), "digest": digest, "replay_lsn": replay_lsn}

    def _record_delivery(self, ref: str, report_kind: str, delivery: dict[str, Any], visible) -> str:
        connection = self._open_connection("pg5r-htap4-report-record", "primary")
        try:
            with connection.cursor() as cursor:
                _set_role(cursor, ROLE_REPORT)
                cursor.execute(
                    "UPDATE frs_report_jobs SET state = 'delivered', delivered_at = clock_timestamp(), "
                    "visible_watermark_seq = %s, replay_lsn = %s, result_digest = %s WHERE ref = %s;",
                    (None if visible is None else visible[0], delivery["replay_lsn"], delivery["digest"], ref),
                )
            connection.commit()
        finally:
            connection.close()
        self._reports_ledger.append(
            "report_delivered",
            job_id=ref,
            report_kind=report_kind,
            visible_watermark_seq=None if visible is None else visible[0],
            replay_lsn=delivery["replay_lsn"],
            result_digest=delivery["digest"],
            business_seconds=round(self._runtime.business_seconds_now(), 3),
        )
        return delivery["digest"]

    def _miss_digest(self, ref: str, report_kind: str) -> str:
        """Deterministic result digest standing for the deadline-miss outcome.

        The trusted terminal the job runner records for this digest lands after
        the business deadline, so delivered_on_time stays False; the external
        deadline_missed row carries the reason.
        """
        payload = "|".join(("report_deadline_missed", ref, report_kind))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _miss_deadline(self, ref: str, report_kind: str, reason: str) -> None:
        connection = self._open_connection("pg5r-htap4-report-miss", "primary")
        try:
            with connection.cursor() as cursor:
                _set_role(cursor, ROLE_REPORT)
                cursor.execute("UPDATE frs_report_jobs SET state = 'deadline_missed' WHERE ref = %s;", (ref,))
            connection.commit()
        finally:
            connection.close()
        self._reports_ledger.append(
            "report_deadline_missed",
            job_id=ref,
            report_kind=report_kind,
            reason=reason,
            business_seconds=round(self._runtime.business_seconds_now(), 3),
        )

    def record_result(self, job_id: str, result_digest: str, connection: object) -> None:
        # Delivery state is recorded by the run callable itself; nothing to do.
        return None

    def read_control(self, connection: object) -> JobControl:
        return JobControl(max_concurrency=3)

    def _deadline_timestamp(self, deadline_at_monotonic: float) -> _dt.datetime:
        wall_offset = time.time() - time.monotonic()
        return _dt.datetime.fromtimestamp(wall_offset + deadline_at_monotonic, tz=_dt.timezone.utc)


class WatermarkView:
    """In-memory mirror of the primary watermark ledger for LSN alignment."""

    def __init__(self):
        self._lock = threading.Lock()
        self._entries: list[tuple[int, int, float]] = []

    def record(self, seq: int, lsn_int: int, business_seconds: float) -> None:
        with self._lock:
            self._entries.append((seq, lsn_int, business_seconds))

    def visible_watermark(self, replay_lsn_int: int) -> tuple[int, float] | None:
        with self._lock:
            visible = [entry for entry in self._entries if entry[1] <= replay_lsn_int]
        if not visible:
            return None
        return (visible[-1][0], visible[-1][2])

    def latest(self) -> tuple[int, float] | None:
        with self._lock:
            if not self._entries:
                return None
            seq, _lsn, business_seconds = self._entries[-1]
        return (seq, business_seconds)


def _is_transient_db_error(exc: BaseException) -> bool:
    """Connection-class failures are observations, not service failures.

    The agent may legitimately restart either instance mid-run (remediation)
    and replication outages are scenario content: an unobservable tick is a
    measurement gap graded by the evaluation, never a reason to poison the
    whole run through _service_failures.
    """
    import psycopg2

    return isinstance(exc, (psycopg2.OperationalError, psycopg2.InterfaceError))


class LinkPolicyGovernor:
    """Consumes frs_work_control.replication_link_rate_kbit.

    The public control row is the sanctioned DBA lever for the replication link
    QoS (0 = full rate, >0 = tc tbf kbit); this governor is its real consumer.
    On every observed change it applies or releases the shaping qdisc through
    the environment. A rejected value (non-integer, negative) raises: a corrupt
    governance row is a failed governance action, not something to ignore.
    """

    def __init__(self, *, open_connection: Callable[[str, str], object], environment, poll_seconds: float = LINK_POLICY_POLL_SECONDS):
        self._open_connection = open_connection
        self._environment = environment
        self._poll_seconds = poll_seconds
        self._stop = threading.Event()
        self._applied_rate: int | None = None

    def read_policy(self) -> int:
        connection = self._open_connection("pg5r-htap4-link-policy", "primary")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT control_value FROM frs_work_control WHERE control_key = %s;",
                    (LINK_POLICY_CONTROL_KEY,),
                )
                row = cursor.fetchone()
            connection.rollback()
        finally:
            connection.close()
        if row is None:
            raise RuntimeError(
                f"Link policy control row is missing: control_key={LINK_POLICY_CONTROL_KEY!r}"
            )
        rate = int(str(row[0]))
        if rate < 0:
            raise RuntimeError(f"Link policy rate must be >= 0: control_value={row[0]!r}")
        return rate

    def _reconcile(self, rate: int) -> None:
        if rate == self._applied_rate:
            return
        if rate == 0:
            self._environment.release_bandwidth_limit()
        else:
            self._environment.apply_bandwidth_limit(rate)
        self._applied_rate = rate

    def poll_once(self) -> int:
        rate = self.read_policy()
        self._reconcile(rate)
        return rate

    def loop(self) -> None:
        next_at = time.monotonic()
        while not self._stop.is_set():
            next_at += self._poll_seconds
            if self._stop.wait(max(0.0, next_at - time.monotonic())):
                return
            try:
                self.poll_once()
            except BaseException as exc:
                if _is_transient_db_error(exc):
                    continue
                raise

    def stop(self) -> None:
        self._stop.set()


def _report_batch_binding(spec) -> str | None:
    """The deliverable input batch declared by the spec (single source)."""
    bindings = set()
    for service in spec.services:
        for deliverable in getattr(service, "deliverables", ()):
            bindings.add(deliverable.input_batch_binding)
    if len(bindings) > 1:
        raise ValueError(f"Report deliverables declare inconsistent input batch bindings: {sorted(bindings)!r}")
    return next(iter(bindings)) if bindings else None


class HtapReplicaFreshnessWorkloadRuntime:
    def __init__(
        self,
        *,
        environment,
        spec,
        run_id: str,
        clock,
        persistent_scenario_started: float,
        calendar: FreshnessBusinessCalendar = PRODUCTION_CALENDAR,
        ledger_dir: Path,
        rates: WorkloadRates | None = None,
    ):
        self.spec = spec
        self.run_id = run_id
        self.calendar = calendar
        self._report_batch_binding = _report_batch_binding(spec)
        self._clock = clock
        self._environment = environment
        self._scoring_origin: float | None = None
        self._rates = rates or WorkloadRates()
        self._trusted = TrustedLedger(f"{run_id}-htap4", Path(ledger_dir) / "trusted.jsonl")
        self._reports_ledger = ExternalJsonlLedger(Path(ledger_dir) / "report_deliveries.jsonl")
        self._watermark_view = WatermarkView()
        self._open_connection = environment.open_workload_connection
        self._orders_pool = OltpTransactionPool(
            service_id="htap4_orders",
            ledger=self._trusted,
            clock=clock,
            concurrency=3,
            connection_factory=lambda app: self._open_connection(app, "primary"),
            request_timeout_ms=self._rates.orders_timeout_ms,
            application_name=APP_OLTP,
        )
        self._report_runner = JobQueueRunner(
            service_id="htap4_reports",
            ledger=self._trusted,
            clock=clock,
            store=FreshnessReportJobStore(self._open_connection, self._watermark_view, self._reports_ledger, self),
            connection_factory=self._open_connection,
            application_name="pg5r-htap4-report-worker",
            max_workers=3,
            poll_interval_seconds=REPORT_POLL_SECONDS,
        )
        self._services = [self._orders_pool, self._report_runner]
        self._calendar_stop = threading.Event()
        self._watermark_stop = threading.Event()
        self._link_policy_governor = LinkPolicyGovernor(
            open_connection=self._open_connection, environment=environment
        )
        self._governor_thread: threading.Thread | None = None
        self._calendar_thread: threading.Thread | None = None
        self._watermark_thread: threading.Thread | None = None
        self._submitted_kinds: set[str] = set()
        self._service_failures: list[tuple[str, BaseException]] = []
        self._baseline_facts: dict[str, Any] = {}
        self._started = False

    # -- lifecycle ---------------------------------------------------------

    def start(self) -> None:
        if self._started:
            raise RuntimeError(f"HtapReplicaFreshnessWorkloadRuntime cannot start twice: run_id={self.run_id!r}")
        self._started = True
        self._prewarm()

    def _prewarm(self) -> None:
        started = self._clock.monotonic()
        connection = self._open_connection("pg5r-htap4-warmup-orders", "primary")
        try:
            digest = self._order_execute({}, connection)
        finally:
            connection.close()
        standby = self._open_connection("pg5r-htap4-warmup-standby", "standby")
        try:
            with standby.cursor() as cursor:
                cursor.execute("SELECT pg_is_in_recovery();")
                in_recovery = str(cursor.fetchone()[0])
            standby.rollback()
        finally:
            standby.close()
        if str(in_recovery).lower() not in {"true", "t"}:
            raise RuntimeError(f"Standby probe prewarm found a non-recovery node: pg_is_in_recovery={in_recovery!r}")
        self._baseline_facts = {
            "prewarm": {"order_digest_prefix": digest[:12], "standby_in_recovery": True},
            "healthy": True,
            "latency_ms": round((self._clock.monotonic() - started) * 1000, 3),
        }

    def _order_execute(self, params: Any, connection: object) -> str:
        with connection.cursor() as cursor:
            _set_role(cursor, ROLE_OLTP)
            cursor.execute(
                "INSERT INTO frs_orders (status, amount) VALUES ('paid', %s) RETURNING order_id, amount;",
                (((int(time.time() * 1000) % 80000) / 100.0) + 4,),
            )
            order_id, amount = cursor.fetchone()
            cursor.execute("INSERT INTO frs_payments (order_id, amount) VALUES (%s, %s);", (order_id, amount))
        return hashlib.sha256(f"{order_id}|{amount}".encode()).hexdigest()

    def wait_for_warmup(self) -> float:
        scoring_started = self._clock.monotonic()
        self._scoring_origin = scoring_started
        for service in self._services:
            service.start()
        self._calendar_thread = threading.Thread(target=self._guard(self._calendar_loop), name="pg5r-htap4-calendar", daemon=True)
        self._calendar_thread.start()
        self._watermark_thread = threading.Thread(target=self._guard(self._watermark_loop), name="pg5r-htap4-watermark", daemon=True)
        self._watermark_thread.start()
        self._governor_thread = threading.Thread(
            target=self._guard(self._link_policy_governor.loop), name="pg5r-htap4-link-policy", daemon=True
        )
        self._governor_thread.start()
        return scoring_started

    def stop_new_requests(self) -> None:
        self._calendar_stop.set()
        for service in self._services:
            service.stop_new_requests()

    def drain(self) -> None:
        for service in self._services:
            service.drain()

    def stop(self) -> None:
        self.stop_new_requests()
        self.drain()
        self._calendar_stop.set()
        self._watermark_stop.set()
        self._link_policy_governor.stop()
        if self._calendar_thread is not None:
            self._calendar_thread.join(timeout=15)
        if self._watermark_thread is not None:
            self._watermark_thread.join(timeout=15)
        if self._governor_thread is not None:
            self._governor_thread.join(timeout=15)
        # Input is stopped and every worker drained: the final sweep lands
        # each remaining failed plan on exactly one incomplete terminal.
        retry_failed_plans(self._orders_pool)
        for service in self._services:
            service.stop()
        if self._service_failures:
            name, failure = self._service_failures[0]
            raise RuntimeError(f"Freshness workload service failed: thread={name!r}, error={failure!r}")

    def stop_forced(self) -> None:
        """Release every worker thread on the driver's failure path.

        Unlike stop() this records but tolerates per-service errors (the
        triggering failure propagates to the caller), and it appends no ledger
        records: the run is already invalid. The executor shutdown still
        happens, so the process can exit instead of hanging on non-daemon
        worker threads.
        """
        self.stop_new_requests()
        self._calendar_stop.set()
        self._watermark_stop.set()
        self._link_policy_governor.stop()
        if self._calendar_thread is not None:
            self._calendar_thread.join(timeout=15)
        if self._watermark_thread is not None:
            self._watermark_thread.join(timeout=15)
        if self._governor_thread is not None:
            self._governor_thread.join(timeout=15)
        for service in self._services:
            try:
                service.stop()
            except Exception as exc:  # noqa: BLE001 - release path; the caller's error wins
                self._service_failures.append((type(service).__name__, exc))

    def ledgers(self):
        return {"trusted": self._trusted, "report_deliveries": self._reports_ledger}

    def baseline_facts(self):
        return dict(self._baseline_facts)

    def business_seconds_now(self) -> float:
        if self._scoring_origin is None:
            raise RuntimeError(f"Business clock unavailable before scoring: run_id={self.run_id!r}")
        return self._clock.monotonic() - self._scoring_origin

    # -- services ----------------------------------------------------------

    def _guard(self, target):
        def wrapper(*args, **kwargs):
            try:
                target(*args, **kwargs)
            except BaseException as exc:
                self._service_failures.append((threading.current_thread().name, exc))
                raise

        return wrapper

    def _watermark_loop(self) -> None:
        sequence = 0
        next_at = time.monotonic()
        while not self._watermark_stop.is_set():
            next_at += WATERMARK_INTERVAL_SECONDS
            if self._watermark_stop.wait(max(0.0, next_at - time.monotonic())):
                return
            sequence += 1
            try:
                connection = self._open_connection("pg5r-htap4-watermark", "primary")
                try:
                    with connection.cursor() as cursor:
                        _set_role(cursor, ROLE_OLTP)
                        cursor.execute(
                            "INSERT INTO frs_commit_watermark (commit_lsn) VALUES (pg_current_wal_lsn()) "
                            "RETURNING watermark_seq, commit_lsn;"
                        )
                        seq, lsn = cursor.fetchone()
                    connection.commit()
                finally:
                    connection.close()
                business_seconds = self.business_seconds_now()
                self._watermark_view.record(int(seq), lsn_to_int(str(lsn)), business_seconds)
                replay = self._standby_replay_lsn()
                visible = self._watermark_view.visible_watermark(lsn_to_int(replay))
                lag = None if visible is None else round(max(0.0, business_seconds - visible[1]), 3)
                self._trusted.append_freshness_sample(
                    FreshnessSample(
                        sample_id=f"frs-sample-{sequence:08d}",
                        sampled_at_monotonic=self._clock.monotonic(),
                        primary_watermark=f"{int(seq)}@{lsn}",
                        replica_watermark="-" if visible is None else f"{visible[0]}@{replay}",
                        lag_seconds=lag,
                        detail={"business_seconds": round(business_seconds, 3)},
                    )
                )
            except BaseException as exc:
                if _is_transient_db_error(exc):
                    continue
                raise

    def _standby_replay_lsn(self) -> str:
        connection = self._open_connection("pg5r-htap4-watermark-standby", "standby")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_last_wal_replay_lsn();")
                row = cursor.fetchone()
            connection.rollback()
        finally:
            connection.close()
        return str(row[0])

    def _calendar_loop(self) -> None:
        plan_interval = 1.0 / self._rates.orders_qps
        next_plan = self._clock.monotonic()
        next_retry_sweep = self._clock.monotonic() + RETRY_SWEEP_SECONDS
        sequence = 0
        while not self._calendar_stop.is_set():
            now = self.business_seconds_now()
            if now >= self.calendar.input_stop_seconds:
                return
            for submission in self.calendar.submissions:
                if submission.report_kind not in self._submitted_kinds and now >= submission.at_seconds:
                    self._submit_report(submission)
                    self._submitted_kinds.add(submission.report_kind)
            if self._clock.monotonic() >= next_plan:
                sequence += 1
                planned = self._clock.monotonic()
                self._orders_pool.submit(
                    LogicalTransactionPlan(
                        business_id=f"order-{sequence:08d}",
                        tx_kind="order_submit",
                        planned_at_monotonic=planned,
                        deadline_at_monotonic=planned + self._rates.orders_timeout_ms / 1000.0,
                        execute=lambda plan, connection: self._order_execute(plan, connection),
                    )
                )
                next_plan = self._clock.monotonic() + plan_interval
            if self._clock.monotonic() >= next_retry_sweep:
                next_retry_sweep = self._clock.monotonic() + RETRY_SWEEP_SECONDS
                retry_failed_plans(self._orders_pool)
            self._calendar_stop.wait(0.05)

    def _submit_report(self, submission) -> None:
        deadline_monotonic = self._clock.monotonic() + max(1.0, submission.deadline_seconds - submission.at_seconds)
        self._report_runner.submit(
            QueuedJob(
                job_id=submission.report_kind,
                job_kind="report",
                submitted_at_monotonic=self._clock.monotonic(),
                deadline_at_monotonic=deadline_monotonic,
                batch_version=self._report_batch_binding,
                run=lambda job, connection: (_ for _ in ()).throw(AssertionError("store claim supplies the run callable")),
                input_snapshot={
                    "report_kind": submission.report_kind,
                    "freshness_budget_seconds": submission.freshness_budget_seconds,
                },
            )
        )

    # -- trusted facts -----------------------------------------------------

    def business_facts(self) -> dict[str, Any]:
        if self._service_failures:
            name, failure = self._service_failures[0]
            raise RuntimeError(f"Freshness workload service failed: thread={name!r}, error={failure!r}")
        primary = self._open_connection("pg5r-htap4-trusted", "primary")
        try:
            with primary.cursor() as cursor:
                cursor.execute(
                    "SELECT COALESCE(max(watermark_seq), 0) FROM frs_commit_watermark;"
                )
                max_watermark_seq = int(cursor.fetchone()[0])
                cursor.execute(
                    "SELECT "
                    "(SELECT count(*) FROM frs_report_jobs WHERE state IN ('queued', 'running')), "
                    "(SELECT count(*) FROM frs_report_jobs WHERE state = 'delivered'), "
                    "(SELECT count(*) FROM frs_report_jobs WHERE state = 'deadline_missed'), "
                    "(SELECT count(*) FROM frs_orders o LEFT JOIN frs_payments p ON p.order_id = o.order_id "
                    "WHERE o.status = 'paid' AND p.payment_id IS NULL);"
                )
                row = cursor.fetchone()
            primary.rollback()
        finally:
            primary.close()
        return {
            "max_watermark_seq": max_watermark_seq,
            "open_report_jobs": int(row[0]),
            "delivered_report_jobs": int(row[1]),
            "deadline_missed_report_jobs": int(row[2]),
            "missing_payment_count": int(row[3]),
            "report_ledger_entries": self._reports_ledger.entry_count(),
        }

    def reports_ledger(self) -> ExternalJsonlLedger:
        return self._reports_ledger


class HtapReplicaFreshnessWorkloadProvider:
    """WorkloadProvider assembly for the replica-freshness instance."""

    def __init__(self, *, calendar: FreshnessBusinessCalendar = PRODUCTION_CALENDAR, ledger_dir: Path | None = None, rates: WorkloadRates | None = None):
        self.calendar = calendar
        self.ledger_dir = ledger_dir
        self.rates = rates

    def create_runtime(self, environment, spec, run_id: str, clock, *, persistent_scenario_started: float):
        if self.ledger_dir is None:
            raise ValueError(
                "pg5 HTAP replica-freshness workload provider requires ledger_dir: "
                f"scenario_id={spec.scenario_id!r}, run_id={run_id!r}"
            )
        return HtapReplicaFreshnessWorkloadRuntime(
            environment=environment,
            spec=spec,
            run_id=run_id,
            clock=clock,
            persistent_scenario_started=persistent_scenario_started,
            calendar=self.calendar,
            ledger_dir=self.ledger_dir,
            rates=self.rates,
        )
