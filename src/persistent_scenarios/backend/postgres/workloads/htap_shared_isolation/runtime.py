"""Instance driver for pg_htap_shared_resource_isolation.

Composes core shared executors with instance business SQL:
- OltpTransactionPool for the order and dashboard services;
- JobQueueRunner + instance JobQueueStore for analysis scans and the
  checkpointed export, both honoring the public htap_work_control table;
- a business calendar thread (external business inputs, identical on all
  three paths) and commit-watermark bookkeeping.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import threading
import time
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
from src.persistent_scenarios.runtime.ledger import JobAttemptOutcome, TrustedLedger

from dataclasses import dataclass

from ..htap_common.external_ledger import ExternalJsonlLedger
from ..htap_common.pool_retry import retry_failed_plans
from .calendar import HtapBusinessCalendar, PRODUCTION_CALENDAR, submission_payload
from .schema import (
    APP_ANALYSIS_WORKER,
    APP_DASHBOARD,
    APP_EXPORT_WORKER,
    APP_OLTP,
    ROLE_ANALYST,
    ROLE_DASHBOARD,
    ROLE_OLTP,
)

EXPORT_PAGE_SIZE = 20000
WATERMARK_INTERVAL_SECONDS = 5.0
MAX_PACING_SLEEP_SECONDS = 2.0
RETRY_SWEEP_SECONDS = 0.25
# Pre-scoring churn burst: lays down a realistic dead-tuple baseline on the
# order tables so an absolute bloat count looks unremarkable and the pinned-xmin
# signature is the growth trend (vacuum running while dead tuples keep rising),
# not the absolute count.
BASELINE_CHURN_ROWS = 2000


@dataclass(frozen=True, slots=True)
class WorkloadRates:
    """Business-input rates for the two transaction services (instance config)."""

    orders_qps: float = 6.0
    orders_timeout_ms: int = 1500
    dashboard_qps: float = 2.0
    dashboard_timeout_ms: int = 500

ROLE_BY_APP = {APP_OLTP: ROLE_OLTP, APP_DASHBOARD: ROLE_DASHBOARD}
DASHBOARD_WINDOW_SECONDS = 120


def _set_role(cursor, role: str) -> None:
    cursor.execute(f"SET ROLE {role};")


def _store_supplies_run(_job, _connection) -> str:
    raise AssertionError("JobQueueStore.claim supplies the real run callable; submission never executes")


# Claim gate: FIFO by job_id among tenants whose admitted running scan count is
# below their htap_tenant_quota.max_concurrency; a tenant without a quota row
# (or with a NULL quota) has no per-tenant admission yet and is governed only by
# the global analyst_max_concurrency budget.
ANALYSIS_CLAIM_SQL = (
    "UPDATE htap_analysis_jobs SET state = 'running' WHERE ref = ("
    "SELECT j.ref FROM htap_analysis_jobs j "
    "WHERE j.kind = 'scan' AND j.state = 'queued' "
    "AND ((SELECT q.max_concurrency FROM htap_tenant_quota q WHERE q.tenant = j.tenant) IS NULL "
    "OR (SELECT count(*) FROM htap_analysis_jobs r "
    "WHERE r.tenant = j.tenant AND r.kind = 'scan' AND r.state = 'running') "
    "< (SELECT q.max_concurrency FROM htap_tenant_quota q WHERE q.tenant = j.tenant)) "
    "ORDER BY j.job_id LIMIT 1 FOR UPDATE SKIP LOCKED) "
    "RETURNING ref, range_start, range_end, deadline_at;"
)


class _AnalysisJobStore(JobQueueStore):
    """Public htap_analysis_jobs queue for wide history scans.

    The queue receives driver submissions (planned by the runner) and external
    business arrivals injected by capability events (another tenant expanding
    its reporting). An external arrival is planned into the trusted ledger at
    first claim, with its public-queue deadline, so the ledger stays complete
    for every job a worker executes. Claims honor the per-tenant admission the
    agent allocates in htap_tenant_quota (business priority isolation).
    """

    def __init__(
        self,
        open_connection: Callable[[str, str], object],
        *,
        ledger: TrustedLedger,
        clock,
        is_driver_planned: Callable[[str], bool],
    ):
        self._open_connection = open_connection
        self._ledger = ledger
        self._clock = clock
        self._is_driver_planned = is_driver_planned
        self._external_planned: set[str] = set()
        self._lock = threading.Lock()

    def _connect(self, application: str):
        return self._open_connection(application, "primary")

    def enqueue(self, job: QueuedJob, connection: object) -> None:
        params = job.input_snapshot or {}
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO htap_analysis_jobs (ref, tenant, kind, range_start, range_end, deadline_at) "
                "VALUES (%s, %s, 'scan', %s, %s, %s);",
                (
                    job.job_id,
                    params["tenant"],
                    int(params["range_start"]),
                    int(params["range_end"]),
                    self._deadline_timestamp(job.deadline_at_monotonic),
                ),
            )

    def claim(self, worker_id: str, connection: object) -> QueuedJob | None:
        with connection.cursor() as cursor:
            cursor.execute(ANALYSIS_CLAIM_SQL)
            row = cursor.fetchone()
        if row is None:
            return None
        ref, range_start, range_end, deadline_at = str(row[0]), int(row[1]), int(row[2]), row[3]
        self._plan_external_arrival(ref, deadline_at)

        def run(job: QueuedJob, connection: object) -> str:
            with connection.cursor() as cursor:
                _set_role(cursor, ROLE_ANALYST)
                cursor.execute(
                    "SELECT count(*), COALESCE(sum(qty * price), 0.0) FROM htap_order_lines "
                    "WHERE line_id BETWEEN %s AND %s;",
                    (range_start, range_end),
                )
                count, total = cursor.fetchone()
            return hashlib.sha256(f"{count}|{total}".encode()).hexdigest()

        return QueuedJob(job_id=ref, job_kind="scan", submitted_at_monotonic=0.0, deadline_at_monotonic=0.0, run=run)

    def _plan_external_arrival(self, ref: str, deadline_at) -> None:
        if self._is_driver_planned(ref):
            return
        with self._lock:
            if ref in self._external_planned:
                return
            self._external_planned.add(ref)
        now = self._clock.monotonic()
        remaining = (deadline_at - _dt.datetime.now(_dt.timezone.utc)).total_seconds()
        self._ledger.append_job_planned(
            job_id=ref,
            service_id="htap3_analysis",
            job_kind="scan",
            batch_version=None,
            input_snapshot={"source": "external_arrival"},
            submitted_at_monotonic=now,
            deadline_at_monotonic=now + max(0.0, remaining),
        )

    def record_result(self, job_id: str, result_digest: str, connection: object) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE htap_analysis_jobs SET state = CASE WHEN clock_timestamp() > deadline_at "
                "THEN 'deadline_missed' ELSE 'done' END, finished_at = clock_timestamp() "
                "WHERE ref = %s;",
                (job_id,),
            )

    def read_control(self, connection: object) -> JobControl:
        with connection.cursor() as cursor:
            cursor.execute("SELECT control_value FROM htap_work_control WHERE control_key = 'analyst_max_concurrency';")
            row = cursor.fetchone()
        concurrency = int(str(row[0]))
        if concurrency < 0:
            raise ValueError(f"analyst_max_concurrency must be non-negative: value={concurrency}")
        return JobControl(max_concurrency=concurrency)

    def _deadline_timestamp(self, deadline_at_monotonic: float) -> _dt.datetime:
        wall_offset = time.time() - time.monotonic()
        return _dt.datetime.fromtimestamp(wall_offset + deadline_at_monotonic, tz=_dt.timezone.utc)


class _ExportJobStore(JobQueueStore):
    """Public export queue with deterministic content-bound export ids.

    The export binding is `htap-lines-export-w{watermark_seq}`; resubmitting
    the same binding resumes from the committed checkpoints.
    """

    def __init__(self, open_connection: Callable[[str, str], object], pages_ledger: ExternalJsonlLedger):
        self._open_connection = open_connection
        self._pages_ledger = pages_ledger

    def _connect(self, application: str):
        return self._open_connection(application, "primary")

    def enqueue(self, job: QueuedJob, connection: object) -> None:
        params = job.input_snapshot or {}
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO htap_analysis_jobs (ref, tenant, kind, range_end, binding, deadline_at) "
                "VALUES (%s, %s, 'export', %s, %s, %s);",
                (
                    job.job_id,
                    params["tenant"],
                    int(params["bound_line_id"]),
                    params["binding"],
                    self._deadline_timestamp(job.deadline_at_monotonic),
                ),
            )

    def claim(self, worker_id: str, connection: object) -> QueuedJob | None:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE htap_analysis_jobs SET state = 'running' WHERE ref = ("
                "SELECT ref FROM htap_analysis_jobs WHERE kind = 'export' AND state = 'queued' "
                "ORDER BY job_id LIMIT 1 FOR UPDATE SKIP LOCKED) "
                "RETURNING ref, range_end, binding;"
            )
            row = cursor.fetchone()
        if row is None:
            return None
        ref, bound_line_id, binding = str(row[0]), int(row[1]), str(row[2])

        def run(job: QueuedJob, connection: object) -> str:
            chain = hashlib.sha256()
            last_line_id = self._checkpoint(connection, binding)
            rows_per_second = self._rows_per_second(connection)
            while last_line_id < bound_line_id:
                with connection.cursor() as cursor:
                    _set_role(cursor, ROLE_ANALYST)
                    cursor.execute(
                        "SELECT line_id, order_id, sku, qty, price FROM htap_order_lines "
                        "WHERE line_id > %s AND line_id <= %s ORDER BY line_id LIMIT %s;",
                        (last_line_id, bound_line_id, EXPORT_PAGE_SIZE),
                    )
                    rows = cursor.fetchall()
                if not rows:
                    break
                page_digest = hashlib.sha256(
                    "\n".join("|".join(str(value) for value in row) for row in rows).encode("utf-8")
                ).hexdigest()
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO htap_export_checkpoints (export_id, watermark_seq, last_line_id, page_digest, page_rows) "
                        "VALUES (%s, %s, %s, %s, %s);",
                        (binding, int(binding.removeprefix("htap-lines-export-w")), int(rows[-1][0]), page_digest, len(rows)),
                    )
                connection.commit()
                chain.update(page_digest.encode())
                self._pages_ledger.append(
                    "export_page",
                    job_id=ref,
                    export_id=binding,
                    first_line_id=int(rows[0][0]),
                    last_line_id=int(rows[-1][0]),
                    page_rows=len(rows),
                    page_digest=page_digest,
                )
                last_line_id = int(rows[-1][0])
                time.sleep(min(MAX_PACING_SLEEP_SECONDS, len(rows) / rows_per_second))
            digest = chain.hexdigest()
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE htap_analysis_jobs SET state = 'done', finished_at = clock_timestamp() WHERE ref = %s;",
                    (ref,),
                )
            return digest

        return QueuedJob(job_id=ref, job_kind="export", submitted_at_monotonic=0.0, deadline_at_monotonic=0.0, run=run)

    def _checkpoint(self, connection: object, binding: str) -> int:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(max(last_line_id), 0) FROM htap_export_checkpoints WHERE export_id = %s;",
                (binding,),
            )
            return int(cursor.fetchone()[0])

    def _rows_per_second(self, connection: object) -> float:
        with connection.cursor() as cursor:
            cursor.execute("SELECT control_value FROM htap_work_control WHERE control_key = 'export_rows_per_second';")
            value = float(str(cursor.fetchone()[0]))
        if value <= 0:
            raise ValueError(f"export_rows_per_second must be positive: value={value!r}")
        return value

    def record_result(self, job_id: str, result_digest: str, connection: object) -> None:
        # The export run closes its own terminal state (deadline comparison is
        # handled by the caller-visible ledger and the checkpoint table).
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE htap_analysis_jobs SET state = CASE WHEN clock_timestamp() > deadline_at "
                "THEN 'deadline_missed' ELSE 'done' END, finished_at = clock_timestamp() "
                "WHERE ref = %s AND state = 'running';",
                (job_id,),
            )

    def read_control(self, connection: object) -> JobControl:
        return JobControl(max_concurrency=1)

    def _deadline_timestamp(self, deadline_at_monotonic: float) -> _dt.datetime:
        wall_offset = time.time() - time.monotonic()
        return _dt.datetime.fromtimestamp(wall_offset + deadline_at_monotonic, tz=_dt.timezone.utc)


class HtapSharedIsolationWorkloadRuntime:
    def __init__(
        self,
        *,
        environment,
        spec,
        run_id: str,
        clock,
        persistent_scenario_started: float,
        calendar: HtapBusinessCalendar = PRODUCTION_CALENDAR,
        ledger_dir: Path,
        rates: WorkloadRates | None = None,
    ):
        self.spec = spec
        self.run_id = run_id
        self.calendar = calendar
        self._rates = rates or WorkloadRates()
        self._clock = clock
        self._environment = environment
        self._scoring_origin: float | None = None
        self._trusted = TrustedLedger(f"{run_id}-htap3", Path(ledger_dir) / "trusted.jsonl")
        self._export_ledger = ExternalJsonlLedger(Path(ledger_dir) / "export_pages.jsonl")
        self._watermark_ledger = ExternalJsonlLedger(Path(ledger_dir) / "commit_watermarks.jsonl")
        self._open_connection = environment.open_workload_connection
        self._orders_pool = OltpTransactionPool(
            service_id="htap3_orders",
            ledger=self._trusted,
            clock=clock,
            concurrency=4,
            connection_factory=lambda app: self._open_connection(app, "primary"),
            request_timeout_ms=self._rates.orders_timeout_ms,
            application_name=APP_OLTP,
        )
        self._dashboard_pool = OltpTransactionPool(
            service_id="htap3_dashboard",
            ledger=self._trusted,
            clock=clock,
            concurrency=2,
            connection_factory=lambda app: self._open_connection(app, "primary"),
            request_timeout_ms=self._rates.dashboard_timeout_ms,
            application_name=APP_DASHBOARD,
        )
        self._driver_job_ids: set[str] = set()
        self._analysis_runner = JobQueueRunner(
            service_id="htap3_analysis",
            ledger=self._trusted,
            clock=clock,
            store=_AnalysisJobStore(
                self._open_connection,
                ledger=self._trusted,
                clock=clock,
                is_driver_planned=lambda job_id: job_id in self._driver_job_ids,
            ),
            connection_factory=lambda app: self._open_connection(app, "primary"),
            application_name=APP_ANALYSIS_WORKER,
            max_workers=8,
        )
        self._export_runner = JobQueueRunner(
            service_id="htap3_export",
            ledger=self._trusted,
            clock=clock,
            store=_ExportJobStore(self._open_connection, self._export_ledger),
            connection_factory=lambda app: self._open_connection(app, "primary"),
            application_name=APP_EXPORT_WORKER,
            max_workers=1,
        )
        self._services = [self._orders_pool, self._dashboard_pool, self._analysis_runner, self._export_runner]
        self._calendar_stop = threading.Event()
        self._watermark_stop = threading.Event()
        self._calendar_thread: threading.Thread | None = None
        self._watermark_thread: threading.Thread | None = None
        self._submitted_submissions: set[str] = set()
        self._service_failures: list[tuple[str, BaseException]] = []
        self._baseline_facts: dict[str, Any] = {}
        self._started = False

    # -- lifecycle ---------------------------------------------------------

    def start(self) -> None:
        if self._started:
            raise RuntimeError(f"HtapSharedIsolationWorkloadRuntime cannot start twice: run_id={self.run_id!r}")
        self._started = True
        self._prewarm()

    def _prewarm(self) -> None:
        facts: dict[str, Any] = {}
        started = self._clock.monotonic()
        for name, execute in (
            ("order_submit", self._order_execute),
            ("dashboard_agg", self._dashboard_execute),
        ):
            connection = self._open_connection(f"pg5r-htap3-warmup-{name}", "primary")
            try:
                digest = execute({"warmup": name}, connection)
            finally:
                connection.close()
            facts[name] = {"digest_prefix": digest[:12], "latency_ms": round((self._clock.monotonic() - started) * 1000, 3)}
        rows = self._open_connection("pg5r-htap3-warmup-control", "primary")
        rows.rollback()
        rows.close()
        facts["baseline_churn_rows"] = self._baseline_churn_burst()
        facts["htap_dead_tuples_baseline"] = self._dead_tuples_snapshot()
        self._baseline_facts = {"prewarm": facts, "healthy": True}

    def _baseline_churn_burst(self) -> int:
        connection = self._open_connection("pg5r-htap3-warmup-baseline", "primary")
        try:
            with connection.cursor() as cursor:
                _set_role(cursor, ROLE_OLTP)
                cursor.execute(
                    "WITH picked AS ("
                    "SELECT order_id FROM htap_orders WHERE status = 'paid' ORDER BY order_id LIMIT %s"
                    ") UPDATE htap_orders o SET status = 'shipped', updated_at = clock_timestamp() "
                    "FROM picked WHERE o.order_id = picked.order_id;",
                    (BASELINE_CHURN_ROWS,),
                )
                updated = cursor.rowcount
            connection.commit()
        finally:
            connection.close()
        return int(updated)

    def _dead_tuples_snapshot(self) -> int:
        connection = self._open_connection("pg5r-htap3-warmup-baseline", "primary")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COALESCE(sum(n_dead_tup), 0) FROM pg_stat_user_tables WHERE relname LIKE 'htap_%';"
                )
                return int(cursor.fetchone()[0])
        finally:
            connection.close()

    def _order_execute(self, params: Any, connection: object) -> str:
        with connection.cursor() as cursor:
            _set_role(cursor, ROLE_OLTP)
            cursor.execute("SELECT sku FROM htap_inventory ORDER BY (sku * 13) % 7 LIMIT 1;")
            sku = int(cursor.fetchone()[0])
            cursor.execute(
                "INSERT INTO htap_orders (region, status, amount, sku) "
                "VALUES (%s, 'paid', %s, %s) RETURNING order_id, amount;",
                (sku % 32, ((sku * 97) % 90000) / 100.0 + 5, sku),
            )
            order_id, amount = cursor.fetchone()
            cursor.execute("INSERT INTO htap_payments (order_id, amount) VALUES (%s, %s);", (order_id, amount))
            cursor.execute("UPDATE htap_inventory SET reserved = reserved + 1 WHERE sku = %s;", (sku,))
        return hashlib.sha256(f"{order_id}|{amount}".encode()).hexdigest()

    def _dashboard_execute(self, params: Any, connection: object) -> str:
        with connection.cursor() as cursor:
            _set_role(cursor, ROLE_DASHBOARD)
            cursor.execute(
                "SELECT count(*), COALESCE(sum(amount), 0.0) FROM htap_orders "
                "WHERE status = 'paid' AND created_at > clock_timestamp() - interval '120 seconds';"
            )
            row = cursor.fetchone()
        return hashlib.sha256(f"{row[0]}|{row[1]}".encode()).hexdigest()

    def wait_for_warmup(self) -> float:
        scoring_started = self._clock.monotonic()
        self._scoring_origin = scoring_started
        for service in self._services:
            service.start()
        self._calendar_thread = threading.Thread(
            target=self._guard(self._calendar_loop), name="pg5r-htap3-calendar", daemon=True
        )
        self._calendar_thread.start()
        self._watermark_thread = threading.Thread(
            target=self._guard(self._watermark_loop), name="pg5r-htap3-watermark", daemon=True
        )
        self._watermark_thread.start()
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
        if self._calendar_thread is not None:
            self._calendar_thread.join(timeout=15)
        if self._watermark_thread is not None:
            self._watermark_thread.join(timeout=15)
        # Every worker is drained and input is stopped, so each failed attempt
        # still open in either pool reaches exactly one terminal via submit_retry.
        retry_failed_plans(self._orders_pool)
        retry_failed_plans(self._dashboard_pool)
        for service in self._services:
            service.stop()
        if self._service_failures:
            name, failure = self._service_failures[0]
            raise RuntimeError(f"Htap workload service failed: thread={name!r}, error={failure!r}")

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
        if self._calendar_thread is not None:
            self._calendar_thread.join(timeout=15)
        if self._watermark_thread is not None:
            self._watermark_thread.join(timeout=15)
        for service in self._services:
            try:
                service.stop()
            except Exception as exc:  # noqa: BLE001 - release path; the caller's error wins
                self._service_failures.append((type(service).__name__, exc))

    def ledgers(self):
        return {
            "trusted": self._trusted,
            "export_pages": self._export_ledger,
            "commit_watermarks": self._watermark_ledger,
        }

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

    def _open_service_connection(self, application: str):
        return self._open_connection(application, "primary")

    def _watermark_loop(self) -> None:
        next_at = time.monotonic()
        while not self._watermark_stop.is_set():
            next_at += WATERMARK_INTERVAL_SECONDS
            if self._watermark_stop.wait(max(0.0, next_at - time.monotonic())):
                return
            connection = self._open_service_connection("pg5r-htap3-watermark")
            try:
                with connection.cursor() as cursor:
                    _set_role(cursor, ROLE_OLTP)
                    cursor.execute(
                        "INSERT INTO htap_commit_watermark (commit_lsn) VALUES (pg_current_wal_lsn()) "
                        "RETURNING watermark_seq, commit_lsn, committed_at;"
                    )
                    seq, lsn, committed_at = cursor.fetchone()
                connection.commit()
            finally:
                connection.close()
            self._watermark_ledger.append(
                "commit_watermark",
                watermark_seq=int(seq),
                commit_lsn=str(lsn),
                committed_at=str(committed_at),
                business_seconds=round(self.business_seconds_now(), 3),
            )

    def _calendar_loop(self) -> None:
        plan_interval = 1.0 / self._rates.orders_qps
        dashboard_interval = 1.0 / self._rates.dashboard_qps
        next_plan = self._clock.monotonic()
        next_dashboard = self._clock.monotonic()
        next_retry_sweep = self._clock.monotonic() + RETRY_SWEEP_SECONDS
        sequence = 0
        while not self._calendar_stop.is_set():
            now = self.business_seconds_now()
            if now >= self.calendar.input_stop_seconds:
                return
            for submission in self.calendar.submissions:
                if submission.tenant not in self._submitted_submissions and now >= submission.at_seconds:
                    self._submit_analysis(submission)
                    self._submitted_submissions.add(submission.tenant)
            if self._clock.monotonic() >= next_plan:
                sequence += 1
                self._submit_transaction(self._orders_pool, f"order-{sequence:08d}", "order_submit", plan_interval, self._order_execute)
                next_plan = self._clock.monotonic() + plan_interval
            if self._clock.monotonic() >= next_dashboard:
                sequence += 1
                self._submit_transaction(self._dashboard_pool, f"dashboard-{sequence:08d}", "dashboard_agg", dashboard_interval, self._dashboard_execute)
                next_dashboard = self._clock.monotonic() + dashboard_interval
            if self._clock.monotonic() >= next_retry_sweep:
                next_retry_sweep = self._clock.monotonic() + RETRY_SWEEP_SECONDS
                retry_failed_plans(self._orders_pool)
                retry_failed_plans(self._dashboard_pool)
            self._calendar_stop.wait(0.05)

    def _submit_transaction(self, pool: OltpTransactionPool, business_id: str, tx_kind: str, interval: float, execute) -> None:
        planned = self._clock.monotonic()
        deadline = planned + self._flow_deadline(tx_kind)
        pool.submit(
            LogicalTransactionPlan(
                business_id=business_id,
                tx_kind=tx_kind,
                planned_at_monotonic=planned,
                deadline_at_monotonic=deadline,
                execute=lambda plan, connection, _execute=execute: _execute(plan, connection),
            )
        )

    def _flow_deadline(self, tx_kind: str) -> float:
        if tx_kind == "order_submit":
            return self._rates.orders_timeout_ms / 1000.0
        return self._rates.dashboard_timeout_ms / 1000.0

    def _submit_analysis(self, submission) -> None:
        connection = self._open_service_connection("pg5r-htap3-calendar-jobs")
        try:
            with connection.cursor() as cursor:
                _set_role(cursor, ROLE_ANALYST)
                cursor.execute("SELECT COALESCE(max(watermark_seq), 0) FROM htap_commit_watermark;")
                watermark_seq = int(cursor.fetchone()[0])
                cursor.execute("SELECT COALESCE(max(line_id), 0) FROM htap_order_lines;")
                bound_line_id = int(cursor.fetchone()[0])
            connection.commit()
        finally:
            connection.close()
        payload = dict(submission_payload(submission))
        payload["binding"] = f"htap-lines-export-w{watermark_seq}"
        payload["bound_line_id"] = bound_line_id
        payload["business_seconds"] = round(self.business_seconds_now(), 3)
        deadline = self._clock.monotonic() + max(1, self.calendar.export_deadline_seconds - int(self.business_seconds_now()))
        for index in range(submission.scan_count):
            scan_deadline = self._clock.monotonic() + max(1, self.calendar.analysis_deadline_seconds - int(self.business_seconds_now()))
            self._driver_job_ids.add(f"{submission.tenant}:scan:{index}")
            self._analysis_runner.submit(
                QueuedJob(
                    job_id=f"{submission.tenant}:scan:{index}",
                    job_kind="scan",
                    submitted_at_monotonic=self._clock.monotonic(),
                    deadline_at_monotonic=scan_deadline,
                    run=_store_supplies_run,
                    input_snapshot={"tenant": submission.tenant, "range_start": 1, "range_end": bound_line_id},
                )
            )
        self._driver_job_ids.add(f"{submission.tenant}:export")
        self._export_runner.submit(
            QueuedJob(
                job_id=f"{submission.tenant}:export",
                job_kind="export",
                submitted_at_monotonic=self._clock.monotonic(),
                deadline_at_monotonic=deadline,
                run=_store_supplies_run,
                input_snapshot={"tenant": submission.tenant, "binding": payload["binding"], "bound_line_id": bound_line_id},
            )
        )

    # -- trusted facts -----------------------------------------------------

    def business_facts(self) -> dict[str, object]:
        if self._service_failures:
            name, failure = self._service_failures[0]
            raise RuntimeError(f"Htap workload service failed: thread={name!r}, error={failure!r}")
        connection = self._open_service_connection("pg5r-htap3-trusted")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle in transaction' "
                    "AND backend_xmin IS NOT NULL AND pid <> pg_backend_pid()), "
                    "(SELECT COALESCE(max(age(backend_xmin)), 0) FROM pg_stat_activity WHERE backend_xmin IS NOT NULL), "
                    "(SELECT count(*) FROM htap_analysis_jobs WHERE state IN ('queued', 'running')), "
                    "(SELECT count(*) FROM htap_analysis_jobs WHERE state = 'done'), "
                    "(SELECT count(*) FROM htap_analysis_jobs WHERE state = 'deadline_missed'), "
                    "(SELECT COALESCE(max(watermark_seq), 0) FROM htap_commit_watermark), "
                    "(SELECT COALESCE(sum(n_dead_tup), 0) FROM pg_stat_user_tables WHERE relname LIKE 'htap_%'), "
                    "(SELECT count(*) FROM pg_stat_activity WHERE backend_type = 'autovacuum worker');"
                )
                row = cursor.fetchone()
            connection.rollback()
        finally:
            connection.close()
        return {
            "stale_xmin_holder_count": int(row[0]),
            "oldest_xmin_age_transactions": int(row[1]),
            "open_job_count": int(row[2]),
            "done_job_count": int(row[3]),
            "deadline_missed_job_count": int(row[4]),
            "max_watermark_seq": int(row[5]),
            "htap_dead_tuples": int(row[6]),
            "autovacuum_worker_count": int(row[7]),
        }

    def export_ledger(self) -> ExternalJsonlLedger:
        return self._export_ledger

    def watermark_ledger(self) -> ExternalJsonlLedger:
        return self._watermark_ledger


class HtapSharedIsolationWorkloadProvider:
    """WorkloadProvider assembly for the shared-resource HTAP instance."""

    def __init__(self, *, calendar: HtapBusinessCalendar = PRODUCTION_CALENDAR, ledger_dir: Path | None = None):
        self.calendar = calendar
        self.ledger_dir = ledger_dir

    def create_runtime(self, environment, spec, run_id: str, clock, *, persistent_scenario_started: float):
        if self.ledger_dir is None:
            raise ValueError(
                "pg5 HTAP shared-isolation workload provider requires ledger_dir: "
                f"scenario_id={spec.scenario_id!r}, run_id={run_id!r}"
            )
        return HtapSharedIsolationWorkloadRuntime(
            environment=environment,
            spec=spec,
            run_id=run_id,
            clock=clock,
            persistent_scenario_started=persistent_scenario_started,
            calendar=self.calendar,
            ledger_dir=self.ledger_dir,
        )
