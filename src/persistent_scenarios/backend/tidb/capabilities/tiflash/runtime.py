"""HTAP isolation driver: trading pool + analysis job runner + dashboard rhythm.

Implements the frozen `PersistentWorkloadRuntime` protocol for
`tidb_htap_tiflash_isolation`. Trading runs as independent logical transactions on a
bounded connection pool; analysis jobs are claimed from the public `htap.analytics_jobs`
queue and each worker applies the engine preference published in `htap.analytics_config`
at claim time — so GLOBAL-scope releases reach new connections while existing sessions
keep theirs, which is exactly the t=58 tenant-repeat mechanism.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
import subprocess
import threading
import time

from src.persistent_scenarios.backend.tidb.capabilities.warehouse.errors import classify_job_outcome
from src.persistent_scenarios.backend.tidb.capabilities.warehouse.reports import streaming_result_digest
from src.persistent_scenarios.backend.tidb.capabilities.warehouse.runtime import (
    CancelMonitor,
    JobControl,
    JobStore,
    QueuedJob,
    TiDBJobRunner,
)
from src.persistent_scenarios.runtime.clock import Clock
from src.persistent_scenarios.runtime.ledger import (
    AttemptOutcome,
    JobAttempt,
    JobAttemptOutcome,
    LedgerTerminal,
    LogicalTransactionRecord,
    TransactionAttempt,
    TrustedLedger,
)

from .schema import (
    ANALYSIS_REPORT_SQL,
    CONFIG_TABLE,
    DASHBOARD_SQL_TEMPLATE,
    ENGINE_PREFERENCES,
    ORDERS_TABLE,
    QUEUE_TABLE,
    RESULT_TABLE,
    TENANT_SLICE_MODULUS,
    TENANT_TABLE,
    TENANT_TEMPLATE_CONFIG_KEY,
    TRADE_AUDIT,
    analysis_report_sql,
    tenant_analysis_sql,
)

DEFAULT_TRADE_RATE_PER_SECOND = 2.0
DEFAULT_TRADE_DEADLINE_SECONDS = 5.0
DEFAULT_DASHBOARD_INTERVAL_SECONDS = 30.0
DEFAULT_DASHBOARD_BUDGET_SECONDS = 20.0
DEFAULT_ANALYSIS_ATTEMPT_TIMEOUT_SECONDS = 600.0
TENANT_RETRY_BACKOFF_SECONDS = 180.0
QUEUE_APP_PREFIX = "tidb5-htap"

SERVICE_TRADE = "htap_trade_service"
SERVICE_ANALYSIS = "htap_analysis_service"
SERVICE_DASHBOARD = "htap_dashboard_service"
SERVICE_TENANT = "htap_tenant_service"
SERVICE_IDS = (SERVICE_TRADE, SERVICE_ANALYSIS, SERVICE_DASHBOARD, SERVICE_TENANT)

PRIORITY_REQUIRED_ANALYSIS = 50
PRIORITY_DASHBOARD = 100


class AnalysisQueueStore(JobStore):
    """Analysis service store: engine preference is applied per claim from the config table."""

    job_kind = "analysis"

    def __init__(self, tables: "AnalyticsTables", *, attempt_timeout_seconds: float):
        self.tables = tables
        self._attempt_timeout_seconds = attempt_timeout_seconds

    def enqueue(self, job: QueuedJob, connection) -> None:
        snapshot = dict(job.input_snapshot or {})
        self.tables.enqueue_row(
            connection, job.job_id, job.job_kind, str(snapshot.get("report_id") or job.job_id),
            snapshot.get("snapshot_marker"), str(snapshot["sql"]),
            job.submitted_at_monotonic, job.deadline_at_monotonic, int(snapshot.get("priority", PRIORITY_REQUIRED_ANALYSIS)),
        )

    def claim(self, worker_id: str, connection) -> QueuedJob | None:
        row = self.tables.claim_row(connection, worker_id, self.job_kind)
        if row is None:
            return None
        job_id, job_kind, report_id, marker, sql_text, submit_at, deadline = row
        # The published engine preference reaches every new claim through the session
        # this connection runs its analysis with.
        self.tables.apply_engine_preference(connection)
        return QueuedJob(
            job_id=str(job_id),
            job_kind=str(job_kind),
            submitted_at_monotonic=float(submit_at),
            deadline_at_monotonic=float(deadline),
            run=self._make_run(str(job_id), str(report_id), int(marker) if marker is not None else None),
            input_snapshot={"report_id": str(report_id), "sql": str(sql_text)},
        )

    def record_result(self, job_id: str, result_digest: str, connection) -> None:
        return

    def read_control(self, connection) -> JobControl:
        enabled = self.tables.analysis_enabled(connection)
        return JobControl(max_concurrency=self.tables.max_analysis_workers, paused=not enabled)

    def job_state(self, job_id: str, connection) -> tuple[str, bool, int]:
        return self.tables.job_state(connection, job_id)

    def _make_run(self, job_id: str, report_id: str, marker: int | None):
        def run(job: QueuedJob, connection) -> str:
            _sql_text, _cancel, _attempts = self.tables.job_state(connection, job.job_id)
            # The delivered digest is the truth of the job's declared snapshot:
            # trading keeps inserting, so an unbound full-dataset
            # digest could never match a recomputation after input stop.
            bound_sql = analysis_report_sql(marker if marker is not None else 0)
            with connection.cursor() as cursor:
                cursor.execute(f"SET SESSION max_execution_time = {int(self._attempt_timeout_seconds * 1000)};")
                cursor.execute(bound_sql)
                digest, row_count = streaming_result_digest(cursor, ordered=True)
                cursor.execute("SELECT @@SESSION.tidb_isolation_read_engines;")
                engines = str(cursor.fetchone()[0])
            connection.rollback()
            self.tables.record_result(connection, job.job_id, report_id, marker or 0, _now(), row_count, engines, digest)
            return digest

        return run


class TenantQueueStore(AnalysisQueueStore):
    """Tenant analysis service: the tenant's own connection template pins the
    column-store replica (published as `tenant_engine_preference`), independent of
    the shared analytics pool preference, and failed tenant loads requeue with a
    real retry backoff (the tenant BI scheduler's retry policy).
    """

    job_kind = "tenant_analysis"
    retry_backoff_seconds = TENANT_RETRY_BACKOFF_SECONDS

    def claim(self, worker_id: str, connection) -> QueuedJob | None:
        row = self.tables.claim_row(connection, worker_id, self.job_kind)
        if row is None:
            return None
        job_id, job_kind, report_id, marker, sql_text, submit_at, deadline = row
        # The tenant template reaches every tenant claim as its SESSION engine pin;
        # a placement gap on the tenant tables surfaces as recurring routing errors.
        self.tables.apply_tenant_template(connection)
        return QueuedJob(
            job_id=str(job_id),
            job_kind=str(job_kind),
            submitted_at_monotonic=float(submit_at),
            deadline_at_monotonic=float(deadline),
            run=self._make_run(str(job_id), str(report_id), int(marker) if marker is not None else None),
            input_snapshot={"report_id": str(report_id), "sql": str(sql_text)},
        )

    def retry_on_failure(self, job: QueuedJob, attempts: int) -> bool:
        return attempts < self.max_attempts

    def requeue_row(self, connection, job_id: str) -> None:
        self.tables.requeue_row(connection, job_id, not_before=_now() + self.retry_backoff_seconds)

    def _make_run(self, job_id: str, report_id: str, marker: int | None):
        def run(job: QueuedJob, connection) -> str:
            # The BI scheduler's control reads do not force column-store; the
            # signed tiflash pin applies to the analysis itself. The queue
            # table lives on the row store only, so a pinned control read
            # would fail with planner error 1815 regardless of placement and
            # the requeue policy could never reach its designed routing
            # failures on the tenant table.
            with connection.cursor() as cursor:
                cursor.execute("SET SESSION tidb_isolation_read_engines = 'tikv,tiflash,tidb';")
            _sql_text, _cancel, _attempts = self.tables.job_state(connection, job.job_id)
            # The delivered digest is the truth of the job's declared tenant snapshot;
            # the tenant table only grows through onboarding loads.
            bound_sql = tenant_analysis_sql(marker if marker is not None else 0)
            with connection.cursor() as cursor:
                cursor.execute(f"SET SESSION max_execution_time = {int(self._attempt_timeout_seconds * 1000)};")
            self.tables.apply_tenant_template(connection)
            with connection.cursor() as cursor:
                cursor.execute(bound_sql)
                digest, row_count = streaming_result_digest(cursor, ordered=True)
                cursor.execute("SELECT @@SESSION.tidb_isolation_read_engines;")
                engines = str(cursor.fetchone()[0])
            connection.rollback()
            # The completion writes ride the row store too: a tiflash-pinned
            # session cannot execute non-readonly statements (planner error
            # 1815 fires on the UPDATE even with the replica present), and
            # the delivered digest only exists once the queue row flips.
            with connection.cursor() as cursor:
                cursor.execute("SET SESSION tidb_isolation_read_engines = 'tikv,tiflash,tidb';")
            self.tables.record_result(connection, job.job_id, report_id, marker or 0, _now(), row_count, engines, digest)
            return digest

        return run


def _now() -> float:
    return time.monotonic()


def _unused_job_run(job, connection) -> str:
    """Submission-side placeholder: the store's claim() builds the real run body."""
    raise RuntimeError("submission-side QueuedJob.run must never execute; the store builds the real body")


class AnalyticsTables:
    """Raw SQL over the htap control tables."""

    max_analysis_workers = 2

    def config_value(self, connection, key: str) -> str:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT config_value FROM {CONFIG_TABLE} WHERE config_key = %s;", (key,))
            row = cursor.fetchone()
        connection.rollback()
        if row is None:
            raise RuntimeError(f"{CONFIG_TABLE} lost its {key!r} row")
        return str(row[0])

    def release_config(self, connection, at: float, key: str, value: str) -> dict:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT config_value FROM {CONFIG_TABLE} WHERE config_key = %s;", (key,))
            old = cursor.fetchone()
            if old is None:
                raise RuntimeError(f"{CONFIG_TABLE} lost its {key!r} row")
            cursor.execute(f"UPDATE {CONFIG_TABLE} SET config_value = %s WHERE config_key = %s;", (value, key))
            cursor.execute(
                f"INSERT INTO {TRADE_AUDIT} (at_monotonic, config_key, old_value, new_value) VALUES (%s, %s, %s, %s);",
                (at, key, str(old[0]), value),
            )
        connection.commit()
        return {"config_key": key, "old_value": str(old[0]), "new_value": value}

    def publish_config_key(self, connection, at: float, key: str, value: str) -> dict:
        """Insert-or-update publication for keys whose owner introduces them (the
        tenant template does not exist before its onboarding publishes it)."""
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT config_value FROM {CONFIG_TABLE} WHERE config_key = %s;", (key,))
            old = cursor.fetchone()
            if old is None:
                cursor.execute(
                    f"INSERT INTO {CONFIG_TABLE} (config_key, config_value) VALUES (%s, %s);", (key, value)
                )
                old_value = None
            else:
                cursor.execute(f"UPDATE {CONFIG_TABLE} SET config_value = %s WHERE config_key = %s;", (value, key))
                old_value = str(old[0])
            cursor.execute(
                f"INSERT INTO {TRADE_AUDIT} (at_monotonic, config_key, old_value, new_value) VALUES (%s, %s, %s, %s);",
                (at, key, str(old_value), value),
            )
        connection.commit()
        return {"config_key": key, "old_value": old_value, "new_value": value}

    def apply_engine_preference(self, connection) -> None:
        preference = self.config_value(connection, "engine_preference")
        with connection.cursor() as cursor:
            if preference == "tikv_only":
                cursor.execute("SET SESSION tidb_isolation_read_engines = 'tikv';")
            elif preference == "tiflash_preferred":
                cursor.execute("SET SESSION tidb_isolation_read_engines = 'tiflash';")
            else:
                cursor.execute("SET SESSION tidb_isolation_read_engines = 'tikv,tiflash,tidb';")
        connection.rollback()

    def apply_tenant_template(self, connection) -> None:
        """The tenant's own connection template: the tenant signed for
        column-store isolation, so its claims pin the engine regardless of the shared
        pool preference. The template is published by the onboarding capability before
        any tenant job exists; a missing row is a contract break and raises."""
        preference = self.config_value(connection, TENANT_TEMPLATE_CONFIG_KEY)
        if preference not in ENGINE_PREFERENCES:
            raise ValueError(
                f"published tenant template is not a valid engine preference: "
                f"tenant_engine_preference={preference!r}, valid={ENGINE_PREFERENCES!r}"
            )
        with connection.cursor() as cursor:
            if preference == "tikv_only":
                cursor.execute("SET SESSION tidb_isolation_read_engines = 'tikv';")
            elif preference == "tiflash_preferred":
                cursor.execute("SET SESSION tidb_isolation_read_engines = 'tiflash';")
            else:
                cursor.execute("SET SESSION tidb_isolation_read_engines = 'tikv,tiflash,tidb';")
        connection.rollback()

    def analysis_enabled(self, connection) -> bool:
        return self.config_value(connection, "analysis_enabled").lower() == "true"

    def dashboard_enabled(self, connection) -> bool:
        return self.config_value(connection, "dashboard_enabled").lower() == "true"

    def enqueue_row(self, connection, job_id: str, job_kind: str, report_id: str, marker: int | None,
                    sql_text: str, submit_at: float, deadline: float, priority: int) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {QUEUE_TABLE} (job_id, job_kind, report_id, snapshot_marker, sql_text, "
                f"submit_at, deadline, status, attempts, cancel_requested, priority) "
                f"VALUES (%s, %s, %s, %s, %s, %s, %s, 'queued', 0, FALSE, %s);",
                (job_id, job_kind, report_id, marker, sql_text, submit_at, deadline, priority),
            )
        connection.commit()

    def claim_row(self, connection, worker_id: str, job_kind: str) -> tuple | None:
        with connection.cursor() as cursor:
            cursor.execute("BEGIN PESSIMISTIC;")
            cursor.execute(
                f"SELECT job_id FROM {QUEUE_TABLE} WHERE job_kind = %s AND status = 'queued' "
                f"AND (not_before IS NULL OR not_before <= %s) "
                f"ORDER BY priority, job_id LIMIT 1 FOR UPDATE SKIP LOCKED;",
                (job_kind, _now()),
            )
            picked = cursor.fetchone()
            if picked is None:
                cursor.execute("ROLLBACK;")
                return None
            cursor.execute(
                f"UPDATE {QUEUE_TABLE} SET status = 'running', claimed_by = %s, claim_conn_id = CONNECTION_ID() "
                f"WHERE job_id = %s AND status = 'queued';",
                (worker_id, picked[0]),
            )
            if cursor.rowcount != 1:
                # Same TiDB v8.1 SKIP LOCKED pending-lock semantics measured on the
                # warehouse queue: collapse duplicate
                # claims to the single winner; the losers re-poll.
                cursor.execute("ROLLBACK;")
                return None
            cursor.execute(
                f"SELECT job_id, job_kind, report_id, snapshot_marker, sql_text, submit_at, deadline "
                f"FROM {QUEUE_TABLE} WHERE job_id = %s;",
                (picked[0],),
            )
            row = cursor.fetchone()
            cursor.execute("COMMIT;")
        return row

    def cancel_requested_running(self, connection) -> tuple[tuple[str, int], ...]:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT job_id, claim_conn_id FROM {QUEUE_TABLE} "
                f"WHERE status = 'running' AND cancel_requested = TRUE AND claim_conn_id IS NOT NULL;"
            )
            rows = cursor.fetchall()
        connection.rollback()
        return tuple((str(row[0]), int(row[1])) for row in rows)

    def kill_connection(self, connection, conn_id: int) -> None:
        with connection.cursor() as cursor:
            cursor.execute(f"KILL TIDB {int(conn_id)};")
        connection.commit()

    def job_state(self, connection, job_id: str) -> tuple[str, bool, int]:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT sql_text, cancel_requested, attempts FROM {QUEUE_TABLE} WHERE job_id = %s;", (job_id,)
            )
            row = cursor.fetchone()
        connection.rollback()
        if row is None:
            raise RuntimeError(f"claimed analytics row disappeared during execution: job_id={job_id!r}")
        return str(row[0]), bool(row[1]), int(row[2])

    def requeue_row(self, connection, job_id: str, not_before: float | None = None) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {QUEUE_TABLE} SET status = 'queued', claimed_by = NULL, claim_conn_id = NULL, "
                f"cancel_requested = FALSE, not_before = %s WHERE job_id = %s;",
                (not_before, job_id),
            )
        connection.commit()

    def fail_row(self, connection, job_id: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE {QUEUE_TABLE} SET status = 'failed' WHERE job_id = %s;", (job_id,))
        connection.commit()

    def record_result(self, connection, job_id: str, report_id: str, marker: int, delivered_at: float,
                      row_count: int, engines: str, digest: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {QUEUE_TABLE} SET status = 'delivered', result_digest = %s WHERE job_id = %s;",
                (digest, job_id),
            )
            cursor.execute(
                f"INSERT INTO {RESULT_TABLE} (job_id, report_id, snapshot_marker, delivered_at, row_count, "
                f"engine_used, result_digest) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                (job_id, report_id, marker, delivered_at, row_count, engines, digest),
            )
        connection.commit()


class HtapIsolationRuntime:
    """Owns the HTAP trade/analysis system for one persistent scenario run."""

    def __init__(
        self,
        connection_factory: Callable[[str], object],
        clock: Clock,
        run_id: str,
        *,
        ledgers: Mapping[str, TrustedLedger],
        input_end_monotonic: float,
        trade_rate_per_second: float = DEFAULT_TRADE_RATE_PER_SECOND,
        trade_deadline_seconds: float = DEFAULT_TRADE_DEADLINE_SECONDS,
        dashboard_interval_seconds: float = DEFAULT_DASHBOARD_INTERVAL_SECONDS,
        dashboard_budget_seconds: float = DEFAULT_DASHBOARD_BUDGET_SECONDS,
        poll_interval_seconds: float = 0.2,
        tiflash_container: str | None = None,
    ) -> None:
        missing = set(SERVICE_IDS) - set(ledgers)
        if missing:
            raise ValueError(
                "per-service trusted ledgers are required (one service, one ledger): "
                f"missing={sorted(missing)!r}, provided={sorted(ledgers)!r}"
            )
        self.connection_factory = connection_factory
        self.clock = clock
        self.run_id = run_id
        self._ledgers = {service_id: ledgers[service_id] for service_id in SERVICE_IDS}
        self.input_end_monotonic = input_end_monotonic
        self._trade_rate = trade_rate_per_second
        self._trade_deadline_seconds = trade_deadline_seconds
        self._dashboard_interval_seconds = dashboard_interval_seconds
        self._dashboard_budget_seconds = dashboard_budget_seconds
        self._lock = threading.Lock()
        self._trade_sequence = 0
        self._trade_multiplier = 1
        self._tiflash_container = tiflash_container
        self._tiflash_cpus_default: float | None = None
        # Node maintenance window: set by the degradation
        # capability, cleared by the recovery. The tenant onboarding pipeline defers
        # replica attachments while it is held; the recovery does NOT flush the
        # deferred queue (the pipeline does not watch node events) - that residue is
        # the repair surface.
        self._node_under_maintenance = False
        self._stop_input = threading.Event()
        self._monitor_threads: list[threading.Thread] = []

        self.tables = AnalyticsTables()
        self._analysis_runner = TiDBJobRunner(
            service_id=SERVICE_ANALYSIS,
            ledger=self._ledgers[SERVICE_ANALYSIS],
            clock=clock,
            store=AnalysisQueueStore(self.tables, attempt_timeout_seconds=DEFAULT_ANALYSIS_ATTEMPT_TIMEOUT_SECONDS),
            connection_factory=connection_factory,
            application_name=f"{QUEUE_APP_PREFIX}-analysis",
            max_workers=2,
            poll_interval_seconds=poll_interval_seconds,
        )
        self._dashboard_runner = TiDBJobRunner(
            service_id=SERVICE_DASHBOARD,
            ledger=self._ledgers[SERVICE_DASHBOARD],
            clock=clock,
            store=DashboardQueueStore(self.tables, attempt_timeout_seconds=60.0),
            connection_factory=connection_factory,
            application_name=f"{QUEUE_APP_PREFIX}-dashboard",
            max_workers=1,
            poll_interval_seconds=poll_interval_seconds,
        )
        # The tenant service runner is created up front but started only by the
        # onboarding capability (t=58): before that no tenant job exists.
        self._tenant_runner = TiDBJobRunner(
            service_id=SERVICE_TENANT,
            ledger=self._ledgers[SERVICE_TENANT],
            clock=clock,
            store=TenantQueueStore(self.tables, attempt_timeout_seconds=DEFAULT_ANALYSIS_ATTEMPT_TIMEOUT_SECONDS),
            connection_factory=connection_factory,
            application_name=f"{QUEUE_APP_PREFIX}-tenant",
            max_workers=2,
            poll_interval_seconds=poll_interval_seconds,
        )
        self._runners = [self._analysis_runner, self._dashboard_runner]
        self._cancel_monitor = CancelMonitor(tables=self.tables, connection_factory=connection_factory)
        self._started = False
        self._stopped = False

    # -- submission API used by capabilities and the timeline ------------------

    def release_engine_preference(self, at: float, engine_preference: str) -> dict:
        connection = self.connection_factory(f"{QUEUE_APP_PREFIX}-config-release")
        try:
            return self.tables.release_config(connection, at, "engine_preference", engine_preference)
        finally:
            connection.close()

    def set_trade_multiplier(self, multiplier: int) -> dict:
        with self._lock:
            self._trade_multiplier = multiplier
        return {"trade_multiplier": multiplier}

    def set_node_maintenance(self, under_maintenance: bool) -> dict:
        with self._lock:
            self._node_under_maintenance = under_maintenance
        return {"tiflash_node_under_maintenance": under_maintenance}

    @property
    def node_under_maintenance(self) -> bool:
        with self._lock:
            return self._node_under_maintenance

    def restart_tiflash_node(self) -> dict:
        """Node recovery (t=70): the node rejoins and its replicas
        rebuild - real catch-up lag observable through information_schema.tiflash_replica."""
        container = self._tiflash_container
        if container is None:
            raise RuntimeError("tiflash container name is required for the node recovery restart")
        subprocess.run(["docker", "restart", container], check=True, capture_output=True)
        return {"container": container, "restarted": True}

    def create_tenant_tables(self, at: float) -> dict:
        """Tenant onboarding (t=58): the tenant's table is created
        with CREATE TABLE LIKE and loaded with a real slice of the shared orders.
        While the node is under maintenance the onboarding pipeline strips the
        (inherited) replica — placement ops stay frozen for the window — and
        audits the deferral; the recovery event does not flush it - the residue
        must be repaired."""
        connection = self.connection_factory(f"{QUEUE_APP_PREFIX}-tenant-onboarding")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS {TENANT_TABLE} LIKE {ORDERS_TABLE};"
                )
                cursor.execute(
                    f"INSERT INTO {TENANT_TABLE} (order_id, user_id, item_id, region_id, amount, status, created_at) "
                    f"SELECT order_id, user_id, item_id, region_id, amount, status, created_at FROM {ORDERS_TABLE} "
                    f"WHERE order_id % {TENANT_SLICE_MODULUS} = 0;"
                )
                tenant_rows = int(cursor.rowcount)
                attachment_deferred = self.node_under_maintenance
                if attachment_deferred:
                    # On this v8.1.0 build CREATE TABLE LIKE DOES inherit the
                    # source table's TiFlash replica, so the frozen placement pipeline must
                    # explicitly strip the inherited replica — the designed
                    # placement residue only exists once the tenant table
                    # carries none.
                    cursor.execute(f"ALTER TABLE {TENANT_TABLE} SET TIFLASH REPLICA 0;")
                    cursor.execute(
                        f"INSERT INTO {TRADE_AUDIT} (at_monotonic, config_key, old_value, new_value) "
                        f"VALUES (%s, %s, %s, %s);",
                        (at, "tenant_replica_attachment", TENANT_TABLE,
                         "deferred: replica target node under maintenance"),
                    )
                else:
                    cursor.execute(f"ALTER TABLE {TENANT_TABLE} SET TIFLASH REPLICA 1;")
                    cursor.execute(
                        f"INSERT INTO {TRADE_AUDIT} (at_monotonic, config_key, old_value, new_value) "
                        f"VALUES (%s, %s, %s, %s);",
                        (at, "tenant_replica_attachment", TENANT_TABLE, "attached"),
                    )
            connection.commit()
        finally:
            connection.close()
        return {"tenant_table": TENANT_TABLE, "tenant_rows": tenant_rows, "attachment_deferred": attachment_deferred}

    def release_tenant_template(self, at: float, preference: str = "tiflash_preferred") -> dict:
        """Publish the tenant connection template (column-store isolation SLA)."""
        connection = self.connection_factory(f"{QUEUE_APP_PREFIX}-tenant-template")
        try:
            return self.tables.publish_config_key(connection, at, TENANT_TEMPLATE_CONFIG_KEY, preference)
        finally:
            connection.close()

    def apply_tiflash_cpu_limit(self, cpus: float | None) -> dict:
        """Reversible TiFlash node throttle.

        The shared TiDB deployment offers no public CPU-limit primitive, so the
        throttle goes through `docker update --cpus` on the TiFlash container and is
        recorded here; passing None restores the recorded default.
        """
        container = self._tiflash_container
        if container is None:
            raise RuntimeError("tiflash container name is required for the throttle primitive")
        if cpus is None:
            target = self._tiflash_cpus_default
            if target is None:
                raise RuntimeError("no recorded default TiFlash cpu limit to restore")
        else:
            if self._tiflash_cpus_default is None:
                self._tiflash_cpus_default = self._read_nanocpus(container) / 1e9
            target = cpus
        subprocess.run(
            ["docker", "update", "--cpus", str(target), container],
            check=True, capture_output=True,
        )
        return {"container": container, "cpus": target}

    @staticmethod
    def _read_nanocpus(container: str) -> int:
        out = subprocess.run(
            ["docker", "inspect", "--format", "{{.HostConfig.NanoCpus}}", container],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        return int(out)

    def submit_required_analysis(self, report_id: str, deadline_at_monotonic: float) -> str:
        # Deliverable identity: deliverable_id == job_id. The report id IS the deliverable
        # identity; cancel/retry merge into the same job through ledger attempts,
        # never through a suffixed name.
        job_id = report_id
        at = self.clock.monotonic()
        self._analysis_runner.submit(
            QueuedJob(
                job_id=job_id,
                job_kind="analysis",
                submitted_at_monotonic=at,
                deadline_at_monotonic=deadline_at_monotonic,
                run=_unused_job_run,
                input_snapshot={
                    "report_id": report_id,
                    "sql": ANALYSIS_REPORT_SQL,
                    "snapshot_marker": self._current_order_count(),
                    "priority": PRIORITY_REQUIRED_ANALYSIS,
                },
            )
        )
        return job_id

    def submit_tenant_analysis(self, report_id: str, deadline_at_monotonic: float) -> str:
        """The new tenant's heavy analysis rides the peak window overlapping the
        recovery: it reads the tenant table under the tenant's
        column-store template, so a placement gap resurfaces here."""
        job_id = report_id
        at = self.clock.monotonic()
        self._tenant_runner.submit(
            QueuedJob(
                job_id=job_id,
                job_kind="tenant_analysis",
                submitted_at_monotonic=at,
                deadline_at_monotonic=deadline_at_monotonic,
                run=_unused_job_run,
                input_snapshot={
                    "report_id": report_id,
                    "sql": tenant_analysis_sql(0),  # the claim path rebuilds the snapshot-bound body
                    "snapshot_marker": self._current_tenant_snapshot_marker(),
                    "priority": PRIORITY_REQUIRED_ANALYSIS,
                },
            )
        )
        return job_id

    def _current_tenant_snapshot_marker(self) -> int:
        """The tenant table's largest order id (ids ride the shared sequence, so the
        row count is not a valid order_id bound for the snapshot)."""
        connection = self.connection_factory(f"{QUEUE_APP_PREFIX}-tenant-marker")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COALESCE(MAX(order_id), 0) FROM {TENANT_TABLE};")
                return int(cursor.fetchone()[0])
        finally:
            connection.close()

    def start_tenant_workers(self, worker_count: int = 2) -> dict:
        """t=58: new tenants arrive with the current published config.

        Tenant claims read the tenant template (column-store SLA) and claim only
        `tenant_analysis` rows from the tenant service queue, so a fix that covers
        the tenant placement protects them; a fix that only touches old sessions or
        the shared pool does not.
        """
        self._tenant_runner.start()
        return {"tenant_workers_started": worker_count}

    # -- PersistentWorkloadRuntime protocol ------------------------------------

    def start(self) -> None:
        if self._started:
            raise RuntimeError(f"htap isolation runtime cannot start twice: run_id={self.run_id!r}")
        self._started = True
        for runner in self._runners:
            runner.start()
        self._cancel_monitor.start()
        self._spawn_monitor("trade-loop", self._trade_loop)
        self._spawn_monitor("dashboard-loop", self._dashboard_loop)

    def _spawn_monitor(self, name: str, target) -> None:
        thread = threading.Thread(target=target, name=f"tidb5-htap-{self.run_id}-{name}", daemon=True)
        self._monitor_threads.append(thread)
        thread.start()

    def wait_for_warmup(self) -> float:
        return self.clock.monotonic()

    def stop_new_requests(self) -> None:
        self._stop_input.set()
        for runner in (*self._runners, self._tenant_runner):
            runner.stop_new_requests()

    def drain(self) -> None:
        for runner in (*self._runners, self._tenant_runner):
            runner.drain()

    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self.stop_new_requests()
        self._cancel_monitor.stop()
        for runner in (*self._runners, self._tenant_runner):
            runner.stop()

    def ledgers(self) -> Mapping[str, TrustedLedger]:
        return dict(self._ledgers)

    def baseline_facts(self) -> Mapping[str, object]:
        connection = self.connection_factory(f"{QUEUE_APP_PREFIX}-baseline")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {ORDERS_TABLE};")
                orders = int(cursor.fetchone()[0])
                cursor.execute(f"SELECT config_key, config_value FROM {CONFIG_TABLE} ORDER BY config_key;")
                config = {str(key): str(value) for key, value in cursor.fetchall()}
            connection.rollback()
            return {"orders": orders, "config": config}
        finally:
            connection.close()

    # -- monitors ---------------------------------------------------------------

    def _trade_loop(self) -> None:
        ledger = self._ledgers[SERVICE_TRADE]
        interval = 1.0 / self._trade_rate
        connection = self.connection_factory(f"{QUEUE_APP_PREFIX}-trade")
        while not self._stop_input.is_set():
            with self._lock:
                multiplier = self._trade_multiplier
                self._trade_sequence += 1
                sequence = self._trade_sequence
            business_id = f"trade-{sequence:07d}"
            planned_at = self.clock.monotonic()
            deadline_at = planned_at + self._trade_deadline_seconds
            ledger.append_planned_transaction(
                business_id=business_id,
                service_id=SERVICE_TRADE,
                tx_kind="order_submit",
                planned_at_monotonic=planned_at,
                deadline_at_monotonic=deadline_at,
            )
            started = self.clock.monotonic()
            outcome = AttemptOutcome.COMMITTED
            detail: dict = {}
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"INSERT INTO {ORDERS_TABLE} (order_id, user_id, item_id, region_id, amount, status, created_at) "
                        f"SELECT COALESCE(MAX(order_id), 0) + 1, %s, %s, %s, %s, 'created', NOW() FROM {ORDERS_TABLE};",
                        (sequence % 5000, 1 + (sequence * 13 % 400), 1 + (sequence * 7 % 12),
                         round(10 + (sequence * 31 % 5000) / 100.0, 2)),
                    )
                connection.commit()
            except Exception as exc:
                connection.rollback()
                outcome, detail = classify_job_outcome(exc)
                detail = dict(detail)
            ended = self.clock.monotonic()
            ledger.append_transaction_attempt(
                business_id=business_id,
                attempt=TransactionAttempt(
                    attempt_index=1,
                    started_at_monotonic=started,
                    ended_at_monotonic=ended,
                    outcome=outcome,
                    detail=detail,
                ),
            )
            if outcome is AttemptOutcome.COMMITTED:
                ledger.append_transaction_terminal(
                    business_id=business_id,
                    terminal=LedgerTerminal.COMPLETED,
                    completed_at_monotonic=ended,
                    result_digest=None,
                )
            else:
                ledger.append_transaction_terminal(
                    business_id=business_id,
                    terminal=LedgerTerminal.INCOMPLETE_ERROR,
                    completed_at_monotonic=None,
                    result_digest=None,
                )
            self._stop_input.wait(interval / multiplier)
        connection.close()

    def _dashboard_loop(self) -> None:
        runner = self._dashboard_runner
        while not self._stop_input.is_set():
            now = self.clock.monotonic()
            if now >= self.input_end_monotonic:
                return
            connection = self.connection_factory(f"{QUEUE_APP_PREFIX}-dash-submit")
            try:
                enabled = self.tables.dashboard_enabled(connection)
            finally:
                connection.close()
            if enabled:
                with self._lock:
                    self._dashboard_sequence = getattr(self, "_dashboard_sequence", 0) + 1
                    sequence = self._dashboard_sequence
                job_id = f"dashboard_{sequence:05d}"
                since_ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(now - 300))
                runner.submit(
                    QueuedJob(
                        job_id=job_id,
                        job_kind="dashboard",
                        submitted_at_monotonic=now,
                        deadline_at_monotonic=now + self._dashboard_budget_seconds,
                        run=_unused_job_run,
                        input_snapshot={
                            "report_id": "dashboard_refresh",
                            "sql": DASHBOARD_SQL_TEMPLATE.format(since_ts=since_ts),
                            "priority": PRIORITY_DASHBOARD,
                        },
                    )
                )
            self._stop_input.wait(self._dashboard_interval_seconds)

    def _current_order_count(self) -> int:
        connection = self.connection_factory(f"{QUEUE_APP_PREFIX}-marker")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {ORDERS_TABLE};")
                return int(cursor.fetchone()[0])
        finally:
            connection.close()


class DashboardQueueStore(JobStore):
    """Dashboard refresh store: single worker, paused via the config table."""

    job_kind = "dashboard"

    def __init__(self, tables: AnalyticsTables, *, attempt_timeout_seconds: float):
        self.tables = tables
        self._attempt_timeout_seconds = attempt_timeout_seconds

    def enqueue(self, job: QueuedJob, connection) -> None:
        snapshot = dict(job.input_snapshot or {})
        self.tables.enqueue_row(
            connection, job.job_id, "dashboard", str(snapshot.get("report_id") or job.job_id),
            None, str(snapshot["sql"]), job.submitted_at_monotonic, job.deadline_at_monotonic,
            int(snapshot.get("priority", PRIORITY_DASHBOARD)),
        )

    def claim(self, worker_id: str, connection) -> QueuedJob | None:
        row = self.tables.claim_row(connection, worker_id, self.job_kind)
        if row is None:
            return None
        job_id, _job_kind, report_id, marker, sql_text, submit_at, deadline = row
        self.tables.apply_engine_preference(connection)
        return QueuedJob(
            job_id=str(job_id),
            job_kind="dashboard",
            submitted_at_monotonic=float(submit_at),
            deadline_at_monotonic=float(deadline),
            run=self._make_run(str(report_id)),
            input_snapshot={"report_id": str(report_id), "sql": str(sql_text)},
        )

    def record_result(self, job_id: str, result_digest: str, connection) -> None:
        return

    def read_control(self, connection) -> JobControl:
        enabled = self.tables.dashboard_enabled(connection)
        return JobControl(max_concurrency=1, paused=not enabled)

    def job_state(self, job_id: str, connection) -> tuple[str, bool, int]:
        return self.tables.job_state(connection, job_id)

    def _make_run(self, report_id: str):
        def run(job: QueuedJob, connection) -> str:
            sql_text, _cancel, _attempts = self.tables.job_state(connection, job.job_id)
            with connection.cursor() as cursor:
                cursor.execute(sql_text)
                digest, _rows = streaming_result_digest(cursor, ordered=True)
                cursor.execute("SELECT @@SESSION.tidb_isolation_read_engines;")
                engines = str(cursor.fetchone()[0])
            connection.rollback()
            self.tables.record_result(connection, job.job_id, report_id, 0, _now(), 0, engines, digest)
            return digest

        return run
