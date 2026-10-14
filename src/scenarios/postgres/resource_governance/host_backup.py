import time
from collections.abc import Mapping
from dataclasses import dataclass

from src.scenarios.evaluation.postgres.resource_governance import (
    PgResourceGovernanceHostBackupForNightlyBackupReadSaturationEvaluatorCase,
    PgResourceGovernanceHostBackupForSingleBackupReaderSimpleEvaluatorCase,
)
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.workloads.specs import WorkloadProfile

from src.scenarios.postgres.common import (
    _join_thread,
    _json_object,
    _require_sql_success,
    _run_cleanup_steps,
    _validate_sql_identifier,
)
from src.execution.specs import CaseResourceSpec, PostgresCaseRuntime
from src.scenarios.base import DifficultyCalibration, FaultPlan, PostgresScenario, PostgresScenarioCase
from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase


RESOURCE_GOVERNANCE_POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)


class PgResourceGovernanceHostBackupInjector(BaseFaultInjector):
    """Simulate a host/basebackup reader that makes unrelated reports I/O victims."""

    def __init__(self):
        self._stop_event = None
        self._backup_thread = None
        self._backup_conn = None

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.data_table = _validate_sql_identifier(config["data_table"], "data_table")
        self.control_table = _validate_sql_identifier(config["control_table"], "control_table")
        self.backup_app_name = str(config["backup_app_name"]).replace("'", "''")
        self.backup_job_name = str(config["backup_job_name"]).replace("'", "''")
        self.report_app_names = tuple(str(name).replace("'", "''") for name in config["report_app_names"])
        self.row_count = int(config["row_count"])
        self.payload_repeat = int(config["payload_repeat"])
        self.backup_sleep_seconds = float(config["backup_sleep_seconds"])

    def install(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        with self.env.metrics_hidden():
            self._cleanup()
            self._create_objects()
            self._verify_persistent_state()
        self._start_runtime()
        with self.env.metrics_hidden():
            self._wait_until_observable(timeout=30)
        self.env.reconnect()

    def _create_objects(self) -> None:
        self.env.execute_sql(f"""
            CREATE TABLE {self.data_table} (
                id integer PRIMARY KEY,
                bucket integer NOT NULL,
                region integer NOT NULL,
                amount numeric(12, 2) NOT NULL,
                payload text NOT NULL
            );
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.data_table} (id, bucket, region, amount, payload)
            SELECT g, g % 100, g % 12, ((g % 10000)::numeric / 100) + 1,
                   repeat(md5(g::text), {self.payload_repeat})
            FROM generate_series(1, {self.row_count}) AS g;
        """)
        self.env.execute_sql(f"CREATE INDEX idx_{self.data_table}_bucket_region ON {self.data_table}(bucket, region);")
        self.env.execute_sql(f"ANALYZE {self.data_table};")
        self.env.execute_sql(f"""
            CREATE TABLE {self.control_table} (
                job_name text PRIMARY KEY,
                status text NOT NULL,
                source text NOT NULL,
                scheduled_window text NOT NULL,
                governed_at timestamptz
            );
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.control_table} (job_name, status, source, scheduled_window)
            VALUES
                ('{self.backup_job_name}', 'running', 'host_basebackup', 'nightly'),
                ('reporting_snapshot_decoy', 'completed', 'logical_export', 'previous_window');
        """)

    def _start_runtime(self) -> None:
        import threading

        self._stop_event = threading.Event()
        self._backup_thread = threading.Thread(target=self._run_backup_reader, daemon=True)
        self._backup_thread.start()
        time.sleep(1.0)

    def _run_backup_reader(self) -> None:
        import psycopg2

        conn = None
        try:
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.env.user,
                password=self.env.password,
                dbname=self.env.dbname,
                application_name=self.backup_app_name,
                connect_timeout=5,
            )
            conn.autocommit = True
            self._backup_conn = conn
            with conn.cursor() as cursor:
                cursor.execute("SET statement_timeout = '0';")
                while self._stop_event is not None and not self._stop_event.is_set():
                    cursor.execute(
                        f"SELECT sum(length(payload)), pg_sleep({self.backup_sleep_seconds}) "
                        f"FROM {self.data_table};"
                    )
                    time.sleep(0.05)
        except Exception as exc:
            if self._stop_event is not None and not self._stop_event.is_set():
                print(f"[FaultInjector:PgResourceGovernanceHostBackupInjector] backup reader stopped: {exc}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            self._backup_conn = None

    def _wait_until_observable(self, timeout: float) -> None:
        deadline = time.time() + timeout
        last_count = None
        while time.time() < deadline:
            payload = _json_object(
                self.env.execute_sql(
                    "SELECT count(*) FROM pg_stat_activity "
                    f"WHERE application_name = '{self.backup_app_name}';"
                ),
                "wait for host backup reader",
            )
            last_count = int(payload["result"][0][0])
            if last_count >= 1:
                return
            time.sleep(0.5)
        raise RuntimeError(f"Host backup reader did not become observable: app={self.backup_app_name}, count={last_count}")

    def prepare_observability(self, context: FaultLifecycleContext):
        return {
            "disk_io": context.env.query_metrics("disk_io"),
            "slow_queries": context.env.query_metrics("slow_queries", threshold_ms=1000),
            "active_backup_reader": context.env.execute_sql(
                "SELECT pid, application_name, state, wait_event_type, left(query, 160) "
                "FROM pg_stat_activity "
                f"WHERE application_name = '{self.backup_app_name}' "
                f"OR application_name = ANY(ARRAY{list(self.report_app_names)!r}) "
                "ORDER BY application_name, query_start NULLS LAST;"
            ),
            "backup_job_catalog": context.env.execute_sql(
                f"SELECT job_name, status, source, scheduled_window FROM {self.control_table} ORDER BY job_name;"
            ),
        }

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT to_regclass('public.{self.data_table}')::text, "
                f"to_regclass('public.{self.control_table}')::text, "
                f"(SELECT count(*) FROM {self.data_table}), "
                f"(SELECT status FROM {self.control_table} WHERE job_name = '{self.backup_job_name}');"
            ),
            "verify host-backup persistent state",
        )
        expected = [[self.data_table, self.control_table, self.row_count, "running"]]
        if payload["result"] != expected:
            raise RuntimeError(f"Host-backup persistent state does not match the Case: expected={expected}, observed={payload['result']}")

    def _terminate_backup_reader(self) -> None:
        _require_sql_success(
            self.env.execute_sql(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                f"WHERE application_name = '{self.backup_app_name}' AND pid <> pg_backend_pid();"
            ),
            "terminate host-backup reader",
        )

    def _cleanup(self) -> None:
        self._terminate_backup_reader()
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.control_table} CASCADE;")
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.data_table} CASCADE;")

    def quiesce(self, context: FaultLifecycleContext):
        if self._stop_event:
            self._stop_event.set()
        steps = []
        if self._backup_conn is not None:
            steps.append(("close host-backup connection", self._backup_conn.close))
        if self._backup_thread is not None:
            steps.append(("join host-backup reader", lambda: _join_thread(self._backup_thread, 5, "host-backup reader")))
        _run_cleanup_steps(f"Host-backup cleanup for {context.scenario_id}/{context.case_id}", steps)
        self._backup_conn = None
        self._backup_thread = None
        self._stop_event = None
        self._terminate_backup_reader()

    def recover(self, context: FaultLifecycleContext):
        self.quiesce(context)
        self._cleanup()
        self.env.reconnect()

    def activate(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        with self.env.metrics_hidden():
            self._verify_persistent_state()
        self._start_runtime()
        with self.env.metrics_hidden():
            self._wait_until_observable(timeout=30)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceHostBackupCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    data_table: str
    control_table: str
    backup_app_name: str
    backup_job_name: str
    report_app_names: tuple[str, ...]
    row_count: int
    payload_repeat: int
    backup_sleep_seconds: float
    report_probe_query: str
    report_probe_latency_ms: int
    slow_queries: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceHostBackupForNightlyBackupReadSaturationScenarioCase(PgResourceGovernanceHostBackupCase):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceHostBackupForSingleBackupReaderSimpleScenarioCase(PgResourceGovernanceHostBackupCase):
    pass


_HOST_BACKUP_REPORT = {
    "diagnosis": {"conditions": [
        {"type": "finding", "factor": factor, "entity": "nightly_backup_read_saturation", "evidence": [factor]}
        for factor in (
            "host backup read saturation",
            "backup reader process is culprit",
            "no single report query is root cause",
            "pause limit or move backup window",
            "report latency recovers after backup governance",
        )
    ]},
    "outcome": {"changes": ["paused the backup reader"], "verification": ["report probe recovered"]},
    "summary": "Host backup governance restored report latency.",
}


_PGRESOURCEGOVERNANCEHOSTBACKUPSCENARIO_CASE = PgResourceGovernanceHostBackupForNightlyBackupReadSaturationScenarioCase(
    case_id='nightly_backup_read_saturation',
    case_no=0,
    evaluator=PgResourceGovernanceHostBackupForNightlyBackupReadSaturationEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Simulates a host backup reader saturating storage read bandwidth while multiple reports are victims.',
    alert='P1 reporting latency alert: several unrelated reports became slow at the same time while database CPU and individual SQL plans look normal. Host storage read latency and iowait are elevated during the backup window. Identify the external backup read stream, avoid per-query tuning, and pause, limit, or move the backup so reports recover.',
    initial_state={'status': 'degraded', 'disk_read_pressure': 'backup_stream', 'report_queries': 'victims'},
    expected_target={'status': 'recovered', 'backup_job': 'paused_or_throttled', 'report_latency': 'recovered'},
    background_workload=BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(name='report_latency_victim_customer', sql='SELECT region, count(*) FROM backup_report_probe WHERE bucket BETWEEN 10 AND 90 GROUP BY region', qps=0.25, tier='LIGHT', commit=False),
            WorkloadProfile(name='report_latency_victim_shipment', sql='SELECT bucket, avg(amount) FROM backup_report_probe WHERE region BETWEEN 2 AND 8 GROUP BY bucket', qps=0.2, tier='LIGHT', commit=False),
        ),
        worker_count=2,
        seed=0x5105,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=2,
    ),
    runtime=PostgresCaseRuntime(resources=RESOURCE_GOVERNANCE_POSTGRES_RESOURCES),
    data_table='backup_report_probe',
    control_table='backup_governance_jobs',
    backup_app_name='nightly-basebackup-reader',
    backup_job_name='nightly_basebackup_20260804',
    report_app_names=('ops-report-customer-aging', 'ops-report-shipment-status'),
    row_count=30000,
    payload_repeat=16,
    backup_sleep_seconds=0.35,
    report_probe_query='SELECT count(*) AS row_count FROM backup_report_probe WHERE bucket BETWEEN 10 AND 90;',
    report_probe_latency_ms=1000,
    slow_queries=('SELECT region, count(*) FROM backup_report_probe WHERE bucket BETWEEN 10 AND 90 GROUP BY region;', 'SELECT bucket, avg(amount) FROM backup_report_probe WHERE region BETWEEN 2 AND 8 GROUP BY bucket;'),
    reference_report=_HOST_BACKUP_REPORT,
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.333333,
        reference_run_ids=(
            "reference-51__pg_resource_governance_host_backup__"
            "nightly_backup_read_saturation__mock__r001",
        ),
    ),
)

_PGRESOURCEGOVERNANCEHOSTBACKUP_SIMPLE_CASE = PgResourceGovernanceHostBackupForSingleBackupReaderSimpleScenarioCase(
    case_id='single_backup_reader_simple',
    case_no=1,
    evaluator=PgResourceGovernanceHostBackupForSingleBackupReaderSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='A focused backup read-saturation case with one backup reader and one report-victim query.',
    alert='P2 storage governance alert: one operational report slowed down during a backup window, and disk read latency is elevated. The database does not show a single bad query plan. Find the backup read stream and govern it without restarting PostgreSQL or changing report SQL.',
    initial_state={'status': 'degraded', 'disk_read_pressure': 'backup_stream', 'report_queries': 'victims'},
    expected_target={'status': 'recovered', 'backup_job': 'paused_or_throttled', 'report_latency': 'recovered'},
    background_workload=BackgroundWorkloadSpec(
        profiles=(WorkloadProfile(name='simple_report_latency_victim', sql='SELECT region, count(*) FROM backup_report_probe_simple WHERE bucket BETWEEN 10 AND 90 GROUP BY region', qps=0.2, tier='LIGHT', commit=False),),
        worker_count=1,
        seed=0x5106,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=2,
    ),
    runtime=PostgresCaseRuntime(resources=RESOURCE_GOVERNANCE_POSTGRES_RESOURCES),
    data_table='backup_report_probe_simple',
    control_table='backup_governance_jobs_simple',
    backup_app_name='single-basebackup-reader',
    backup_job_name='single_basebackup_20260804',
    report_app_names=('ops-report-customer-aging-simple',),
    row_count=8000,
    payload_repeat=8,
    backup_sleep_seconds=0.2,
    report_probe_query='SELECT count(*) AS row_count FROM backup_report_probe_simple WHERE bucket BETWEEN 10 AND 90;',
    report_probe_latency_ms=1000,
    slow_queries=('SELECT region, count(*) FROM backup_report_probe_simple WHERE bucket BETWEEN 10 AND 90 GROUP BY region;',),
    reference_report=_HOST_BACKUP_REPORT,
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.333333,
        reference_run_ids=('run_pg_resource_governance_host_backup_single_backup_reader_simple_MockLLMAgent',),
    ),
)


class PgResourceGovernanceHostBackupScenario(PostgresScenario):
    scenario_id = 'pg_resource_governance_host_backup'
    description = 'Simulates a host backup reader saturating storage read bandwidth and making unrelated reports slow.'
    cases = (_PGRESOURCEGOVERNANCEHOSTBACKUPSCENARIO_CASE, _PGRESOURCEGOVERNANCEHOSTBACKUP_SIMPLE_CASE)

    def build_fault_plan(self, case: PgResourceGovernanceHostBackupCase) -> tuple[FaultPlan, ...]:
        return (FaultPlan(
            injector_type=PgResourceGovernanceHostBackupInjector,
            config={
                'data_table': case.data_table,
                'control_table': case.control_table,
                'backup_app_name': case.backup_app_name,
                'backup_job_name': case.backup_job_name,
                'report_app_names': case.report_app_names,
                'row_count': case.row_count,
                'payload_repeat': case.payload_repeat,
                'backup_sleep_seconds': case.backup_sleep_seconds,
            },
        ),)
