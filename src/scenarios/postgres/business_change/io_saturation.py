from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.postgres.business_change import (
    PgBusinessChangeIoSaturationForArchiveBacklogIoPressureEvaluatorCase,
    PgBusinessChangeIoSaturationForReportingMaintenanceIoSaturationEvaluatorCase,
    PgBusinessChangeIoSaturationForVacuumReportIoVictimSimpleEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from src.scenarios.postgres.common import (
    build_io_saturation_noise_profiles,
)

from src.execution.specs import PostgresCaseRuntime, CaseResourceSpec
from src.scenarios.base import PostgresScenario, DifficultyCalibration, FaultPlan, PostgresScenarioCase
from src.workloads.specs import BackgroundWorkloadSpec, EMPTY_BACKGROUND_WORKLOAD


IO_SATURATION_POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeIoSaturationCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    fault_variant: str
    table: str
    slow_queries: tuple[str, ...]
    row_count: int
    slow_queries_2: tuple[str, ...]
    slow_query_seconds: int
    maintenance_seconds: int
    maintenance_worker_count: int
    startup_timeout_seconds: float
    io_observability_timeout_seconds: float
    minimum_io_mb_per_sec: float
    maintenance_app_name: str
    slow_query_app_prefix: str
    wal_slot_name: str
    healthy_slot_name: str
    scheduler_app_name: str = ""
    schedule_table: str = ""
    job_run_table: str = ""
    healthy_job_name: str = ""
    culprit_job_name: str = ""
    disabled_job_name: str = ""
    report_role_name: str = ""
    report_role_work_mem: str = ""
    report_work_mem_floor: str = "8MB"
    bi_role_name: str = ""
    bi_role_work_mem: str = ""
    bi_work_mem_floor: str = "16MB"
    database_work_mem: str = ""
    database_work_mem_floor: str = "32MB"
    twin_app_name: str = ""
    twin_table: str = ""
    maintenance_function: str = "refresh_report_rollup_state"
    worker_entry_function: str = ""
    worker_task_name: str = ""
    decoy_workers: tuple[tuple[str, str], ...] = ()
    preserved_job_names: tuple[str, ...] = ()
    worker_tick_table: str = ""

@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeIoSaturationForReportingMaintenanceIoSaturationScenarioCase(PgBusinessChangeIoSaturationCase):
    pass

_PGBUSINESSCHANGEIOSATURATIONSCENARIO_CASE = PgBusinessChangeIoSaturationForReportingMaintenanceIoSaturationScenarioCase(
    case_id='reporting_maintenance_io_saturation',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "multiple unrelated slow queries",
                    "entity": "etl-worker-11",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed multiple unrelated slow queries"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "disk io saturation",
                    "entity": "etl-worker-11",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed disk io saturation"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "background maintenance io pressure",
                    "entity": "etl-worker-11",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed background maintenance io pressure"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "reports are io victims",
                    "entity": "etl-worker-11",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed reports are io victims"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "terminate only maintenance session",
                    "entity": "etl-worker-11",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed terminate only maintenance session"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "removed only the root-cause target etl-worker-11"
            ],
            "verification": [
                "target state, protected state, I/O, and victim queries were rechecked"
            ]
        },
        "summary": "The slow queries were victims of shared I/O pressure, not individual SQL regressions."
    },
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.578947,
        reference_run_ids=(
            'logs/traces/'
            'run_pg_business_change_io_saturation_'
            'reporting_maintenance_io_saturation_MockLLMAgent.json',
        ),
        protocol_version='difficulty-v2',
    ),
    case_no=0,
    evaluator=PgBusinessChangeIoSaturationForReportingMaintenanceIoSaturationEvaluatorCase,
    base_image_name='aiopsbench-pg-default:latest',
    workload_tag='default',
    fault_variant='maintenance_io_saturation',
    title='Slow-query alert caused by background maintenance saturating database I/O.',
    alert='[FIRING: WARNING] alertname=PostgresReportQueryLatencyHigh service=tpcds-reporting instance=postgresql-primary severity=warning\nsummary=Multiple TPC-DS report query fingerprints exceeded the slow-query threshold\ndescription=In the last 5m, customer revenue, regional sales, and inventory trend reports all exceeded 5s latency; p95 report latency is 18.4s. Please diagnose the shared cause of the concurrent query slowdown and restore latency.',
    initial_state={'status': 'degraded',
 'alert': 'multiple_slow_queries',
 'table': 'reporting_order_fact',
 'visible_symptom': 'unrelated_tpcds_queries_slow_together'},
    expected_target={'status': 'recovered',
 'table': 'reporting_order_fact',
 'maintenance_sessions': 0,
 'root_cause': 'background_maintenance_io_saturation'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_io_saturation_noise_profiles('reporting_order_fact')),
        worker_count=6,
        seed=0,
    ),
    runtime=PostgresCaseRuntime(resources=IO_SATURATION_POSTGRES_RESOURCES),
    table='reporting_order_fact',
    slow_queries=('/* customer revenue dashboard */ SELECT run_report_latency_probe(64);',
 '/* regional sales dashboard */ SELECT run_report_latency_probe(27);',
 '/* inventory trend dashboard */ SELECT run_report_latency_probe(43);'),
    row_count=60000,
    slow_queries_2=('/* customer revenue dashboard */ SELECT run_report_latency_probe(64);',
 '/* regional sales dashboard */ SELECT run_report_latency_probe(27);',
 '/* inventory trend dashboard */ SELECT run_report_latency_probe(43);'),
    slow_query_seconds=240,
    maintenance_seconds=600,
    maintenance_worker_count=1,
    startup_timeout_seconds=10.0,
    io_observability_timeout_seconds=120.0,
    minimum_io_mb_per_sec=20.0,
    maintenance_app_name='etl-worker-11',
    slow_query_app_prefix='report-dashboard-slow-',
    wal_slot_name='',
    healthy_slot_name='',
    scheduler_app_name='report-batch-scheduler-03',
    schedule_table='ops_batch_job_schedule',
    job_run_table='ops_batch_job_run',
    healthy_job_name='nightly_archive_check',
    culprit_job_name='metric_flush_worker',
    disabled_job_name='report_rollup_legacy_v1',
    maintenance_function='run_batch_cycle',
    worker_entry_function='run_batch_cycle',
    worker_task_name='metric_flush',
    decoy_workers=(('etl-worker-12', 'inventory_sync'),
                   ('etl-worker-13', 'archive_tick')),
    preserved_job_names=('nightly_archive_check', 'inventory_sync_worker', 'archive_tick_worker'),
    worker_tick_table='ops_batch_job_ticks',
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeIoSaturationForVacuumReportIoVictimSimpleScenarioCase(PgBusinessChangeIoSaturationCase):
    pass

_PGBUSINESSCHANGEIOSATURATIONSCENARIO_VACUUM_REPORT_CASE = PgBusinessChangeIoSaturationForVacuumReportIoVictimSimpleScenarioCase(
    case_id='vacuum_report_io_victim_simple',
    runtime=PostgresCaseRuntime(resources=IO_SATURATION_POSTGRES_RESOURCES),
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "multiple unrelated slow queries",
                    "entity": "ops-maintenance-refresh-05",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed multiple unrelated slow queries"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "disk io saturation",
                    "entity": "ops-maintenance-refresh-05",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed disk io saturation"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "background maintenance io pressure",
                    "entity": "ops-maintenance-refresh-05",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed background maintenance io pressure"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "reports are io victims",
                    "entity": "ops-maintenance-refresh-05",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed reports are io victims"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "role level work_mem regression",
                    "entity": "ops-maintenance-refresh-05",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed role in database work_mem regression for report_reader"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "terminate only maintenance session",
                    "entity": "ops-maintenance-refresh-05",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed terminate only maintenance session"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "disabled only the culprit scheduled job and removed only the root-cause target ops-maintenance-refresh-05",
                "reset only the report_reader in-database work_mem override and preserved healthy database and role tunings"
            ],
            "verification": [
                "target state, protected state, I/O, schedule heartbeat, and victim queries were rechecked"
            ]
        },
        "summary": "The slow queries were victims of shared I/O pressure and a change-window role-in-database work_mem regression, not individual SQL regressions."
    },
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.565,
        reference_run_ids=(
            'logs/traces/'
            'run_pg_business_change_io_saturation_'
            'vacuum_report_io_victim_simple_MockLLMAgent.json',
        ),
        protocol_version='difficulty-v2',
    ),
    case_no=1,
    evaluator=PgBusinessChangeIoSaturationForVacuumReportIoVictimSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-default:latest',
    workload_tag='simple-io-victim',
    fault_variant='maintenance_io_saturation',
    title='Slow report alerts caused by a maintenance refresh saturating I/O.',
    alert='[FIRING: WARNING] alertname=PostgresReportQueryLatencyHigh service=ops-reporting instance=postgresql-primary severity=warning\nsummary=Two operational reports crossed the slow-query threshold together\ndescription=Recent slow-query samples point at customer aging and shipment status reports, while host storage latency is elevated. A change window earlier today adjusted scheduled maintenance jobs. Restore report latency and keep other production workloads running unaffected.',
    initial_state={'status': 'degraded',
 'alert': 'multiple_slow_queries',
 'table': 'ops_report_fact',
 'visible_symptom': 'two_reports_slow_during_storage_latency'},
    expected_target={'status': 'recovered',
 'table': 'ops_report_fact',
 'maintenance_sessions': 0,
 'root_cause': 'maintenance_refresh_io_and_role_work_mem_regression'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_io_saturation_noise_profiles('ops_report_fact')[:2]),
        worker_count=2,
        seed=17,
    ),
    table='ops_report_fact',
    slow_queries=('/* customer aging report */ SELECT run_report_latency_probe(12);',
 '/* shipment status report */ SELECT run_report_latency_probe(31);'),
    row_count=36000,
    slow_queries_2=('/* customer aging report */ SELECT run_report_latency_probe(12);',
 '/* shipment status report */ SELECT run_report_latency_probe(31);'),
    slow_query_seconds=1500,
    maintenance_seconds=420,
    maintenance_worker_count=1,
    startup_timeout_seconds=10.0,
    io_observability_timeout_seconds=30.0,
    minimum_io_mb_per_sec=8.0,
    maintenance_app_name='ops-maintenance-refresh-05',
    slow_query_app_prefix='ops-report-slow-',
    wal_slot_name='',
    healthy_slot_name='',
    scheduler_app_name='ops-batch-scheduler-02',
    schedule_table='ops_batch_job_schedule',
    job_run_table='ops_batch_job_run',
    healthy_job_name='nightly_archive_check',
    culprit_job_name='ops_maintenance_vacuum',
    worker_task_name='ops_maintenance_vacuum',
    disabled_job_name='old_vacuum_refresh_v1',
    report_role_name='report_reader',
    report_role_work_mem='64kB',
    bi_role_name='bi_viewer',
    bi_role_work_mem='32MB',
    database_work_mem='64MB',
    twin_app_name='ops-analytics-keeper-08',
    twin_table='ops_shipping_log',
    maintenance_function='ops_maintenance_vacuum_cycle',
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeIoSaturationForArchiveBacklogIoPressureScenarioCase(PgBusinessChangeIoSaturationCase):
    pass

_PGBUSINESSCHANGEIOSATURATIONSCENARIO_ARCHIVE_BACKLOG_CASE = PgBusinessChangeIoSaturationForArchiveBacklogIoPressureScenarioCase(
    case_id='archive_backlog_io_pressure',
    runtime=PostgresCaseRuntime(resources=IO_SATURATION_POSTGRES_RESOURCES),
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "disk io and query latency",
                    "entity": "billing_archive_stalled",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed disk io and query latency"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "wal retained by stalled slot",
                    "entity": "billing_archive_stalled",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed wal retained by stalled slot"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "stalled archive replication slot",
                    "entity": "billing_archive_stalled",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed stalled archive replication slot"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "wal backlog causes checkpoint write amplification",
                    "entity": "billing_archive_stalled",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed wal backlog causes checkpoint write amplification"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "drop only stalled archive slot",
                    "entity": "billing_archive_stalled",
                    "evidence": [
                        "metrics and PostgreSQL state confirmed drop only stalled archive slot"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "removed only the root-cause target billing_archive_stalled"
            ],
            "verification": [
                "target state, protected state, I/O, and victim queries were rechecked"
            ]
        },
        "summary": "The slow queries were victims of shared I/O pressure, not individual SQL regressions."
    },
    case_no=2,
    evaluator=PgBusinessChangeIoSaturationForArchiveBacklogIoPressureEvaluatorCase,
    base_image_name='aiopsbench-pg-default:latest',
    workload_tag='wal-archive-backlog',
    fault_variant='wal_archive_backlog',
    title='I/O saturation alert caused by a stalled WAL archive slot rather than report SQL regressions.',
    alert='[FIRING: WARNING] alertname=PostgresDiskIOLatencyHigh service=checkout-writes instance=postgresql-primary severity=warning\nsummary=Database write latency and report latency rose while disk I/O stayed elevated\ndescription=Recent dashboards show several report samples and checkout writes slower than normal, but the WAL/archive panel also shows unusual backlog growth. Determine whether the visible slow SQL is the root cause or a victim of WAL retention/archive pressure, then clear the backlog safely without changing report SQL.',
    initial_state={'status': 'degraded',
 'alert': 'disk_io_high',
 'table': 'archive_backlog_order_events',
 'visible_symptom': 'slow_reports_and_write_latency_during_wal_backlog',
 'fault_mechanism': 'stalled_wal_archive_slot_retains_wal'},
    expected_target={'status': 'recovered',
 'table': 'archive_backlog_order_events',
 'maintenance_sessions': 0,
 'root_cause': 'stalled_wal_archive_slot_io_pressure'},
    background_workload=BackgroundWorkloadSpec(
        profiles=(),
        worker_count=0,
        seed=23,
    ),
    table='archive_backlog_order_events',
    slow_queries=('/* finance backlog report */ SELECT run_wal_backlog_victim_probe(180, 7);',
 '/* checkout write latency report */ SELECT run_wal_backlog_victim_probe(180, 19);'),
    row_count=24000,
    slow_queries_2=('/* finance backlog report */ SELECT run_wal_backlog_victim_probe(180, 7);',
 '/* checkout write latency report */ SELECT run_wal_backlog_victim_probe(180, 19);'),
    slow_query_seconds=180,
    maintenance_seconds=420,
    maintenance_worker_count=1,
    startup_timeout_seconds=10.0,
    io_observability_timeout_seconds=30.0,
    minimum_io_mb_per_sec=1.0,
    maintenance_app_name='wal-archive-backlog-writer-04',
    slow_query_app_prefix='wal-backlog-victim-report-',
    wal_slot_name='billing_archive_stalled',
    healthy_slot_name='orders_reporting_healthy',
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.45,
        reference_run_ids=(
            "reference-63__pg_io_saturation__"
            "archive_backlog_io_pressure__mock__r001",
        ),
    ),
)


import json
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.postgres.common import (
    PgQueryPerfFaultFingerprintProbe,
    _cancel_open_connection,
    _join_thread,
    _json_object,
    _json_response,
    _require_sql_success,
    _run_cleanup_steps,
    _validate_sql_identifier,
)

class PgBusinessChangeIoSaturationInjector(BaseFaultInjector):
    """
    Simulate multiple slow-query alerts whose shared root cause is a background
    maintenance task saturating database I/O.
    """
    def __init__(self):
        self.env = None
        self.fault_variant = "maintenance_io_saturation"
        self.table = "reporting_order_fact"
        self.row_count = 60000
        self.maintenance_seconds = 600
        self.maintenance_worker_count = 1
        self.startup_timeout_seconds = 10.0
        self.io_observability_timeout_seconds = 30.0
        self.minimum_io_mb_per_sec = 20.0
        self.slow_query_seconds = 240
        self.slow_queries = []
        self.maintenance_app_name = "etl-worker-11"
        self.slow_query_app_prefix = "report-dashboard-slow-"
        self.wal_slot_name = ""
        self.healthy_slot_name = ""
        self._wal_writer_stop_event = None
        self._runtime_stop_event = None
        self._relaunch_not_before_ts = 0.0
        self._maintenance_threads = []
        self._slow_query_threads = []
        self._slow_query_connections = []
        self._connections = []

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self.quiesce(context)
        self._verify_persistent_state()
        self._start_runtime()

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print("[FaultInjector:PgBusinessChangeIoSaturationInjector] Preparing I/O saturation scenario...")
        self.recover(context)
        self.env = env
        with env.metrics_hidden():
            self._setup_schema()
        self._start_runtime()

    def _configure(self, config, env):
        self.env = env
        self.fault_variant = str(config["fault_variant"])
        self.table = config["table"]
        self.row_count = int(config["row_count"])
        self.maintenance_seconds = int(config["maintenance_seconds"])
        self.maintenance_worker_count = int(config["maintenance_worker_count"])
        self.startup_timeout_seconds = float(config["startup_timeout_seconds"])
        self.io_observability_timeout_seconds = float(config["io_observability_timeout_seconds"])
        self.minimum_io_mb_per_sec = float(config["minimum_io_mb_per_sec"])
        self.slow_query_seconds = int(config["slow_query_seconds"])
        self.slow_queries = config["slow_queries"]
        self.maintenance_app_name = config["maintenance_app_name"]
        self.slow_query_app_prefix = config["slow_query_app_prefix"]
        self.wal_slot_name = str(config["wal_slot_name"])
        self.healthy_slot_name = str(config["healthy_slot_name"])
        self.scheduler_app_name = str(config.get("scheduler_app_name", ""))
        self.schedule_table = str(config.get("schedule_table", ""))
        self.job_run_table = str(config.get("job_run_table", ""))
        self.healthy_job_name = str(config.get("healthy_job_name", ""))
        self.culprit_job_name = str(config.get("culprit_job_name", ""))
        self.disabled_job_name = str(config.get("disabled_job_name", ""))
        self.report_role_name = str(config.get("report_role_name", ""))
        self.report_role_work_mem = str(config.get("report_role_work_mem", ""))
        self.report_work_mem_floor = str(config.get("report_work_mem_floor", "8MB"))
        self.bi_role_name = str(config.get("bi_role_name", ""))
        self.bi_role_work_mem = str(config.get("bi_role_work_mem", ""))
        self.bi_work_mem_floor = str(config.get("bi_work_mem_floor", "16MB"))
        self.database_work_mem = str(config.get("database_work_mem", ""))
        self.database_work_mem_floor = str(config.get("database_work_mem_floor", "32MB"))
        self.twin_app_name = str(config.get("twin_app_name", ""))
        self.twin_table = str(config.get("twin_table", ""))
        self.maintenance_function = str(config.get("maintenance_function", "refresh_report_rollup_state"))
        self.worker_entry_function = str(config.get("worker_entry_function", ""))
        self.worker_task_name = str(config.get("worker_task_name", ""))
        self.decoy_workers = tuple(
            (str(app), str(task))
            for app, task in config.get("decoy_workers", ())
        )
        self.worker_tick_table = str(config.get("worker_tick_table", ""))

        if not self.table.isidentifier():
            raise ValueError(f"Invalid I/O saturation table name: {self.table!r}")
        if self.report_role_name and not self.env.dbname.isidentifier():
            raise ValueError(
                f"Invalid I/O saturation database name for role-in-database settings: "
                f"dbname={self.env.dbname!r}"
            )
        for role_name in (self.report_role_name, self.bi_role_name):
            if role_name and not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", role_name):
                raise ValueError(f"Invalid I/O saturation role name: {role_name!r}")
        for slot_name in (self.wal_slot_name, self.healthy_slot_name):
            if slot_name and not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", slot_name):
                raise ValueError(f"Invalid WAL backlog slot name: {slot_name!r}")

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT to_regclass('public.{self.table}')::text, "
                f"(SELECT count(*) FROM {self.table});"
            ),
            "verify I/O-saturation fault image",
        )
        table_name, row_count = payload["result"][0]
        if table_name != self.table or int(row_count) < self.row_count:
            raise RuntimeError(
                f"I/O-saturation fault image does not match the Case: table={table_name}, "
                f"row_count={row_count}, required_rows={self.row_count}"
            )

    def _start_runtime(self):
        import threading
        import time

        self._maintenance_threads = []
        self._wal_writer_stop_event = threading.Event()
        for worker_id in range(self.maintenance_worker_count):
            if self.fault_variant == "wal_archive_backlog":
                thread = threading.Thread(
                    target=self._run_wal_backlog_writer,
                    args=(worker_id,),
                    daemon=True,
                )
            else:
                thread = threading.Thread(
                    target=self._run_worker,
                    args=(self.maintenance_app_name,),
                    daemon=True,
                )
            thread.start()
            self._maintenance_threads.append(thread)
        time.sleep(1.0)

        self._slow_query_threads = []
        maintenance_variant = self.fault_variant != "wal_archive_backlog"
        if maintenance_variant:
            self._runtime_stop_event = threading.Event()
        slow_query_target = self._run_slow_query if not maintenance_variant else self._run_maintenance_slow_query
        for idx, sql in enumerate(self.slow_queries):
            thread = threading.Thread(target=slow_query_target, args=(idx, sql), daemon=True)
            thread.start()
            self._slow_query_threads.append(thread)

        if maintenance_variant:
            if self.scheduler_app_name:
                self._relaunch_not_before_ts = time.time() + 12.0
                scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
                scheduler_thread.start()
                self._maintenance_threads.append(scheduler_thread)
            for decoy_app, _decoy_task in self.decoy_workers:
                decoy_thread = threading.Thread(
                    target=self._run_worker,
                    args=(decoy_app,),
                    daemon=True,
                )
                decoy_thread.start()
                self._maintenance_threads.append(decoy_thread)
            if self.twin_app_name:
                twin_thread = threading.Thread(target=self._run_twin_maintenance, daemon=True)
                twin_thread.start()
                self._maintenance_threads.append(twin_thread)

        self._wait_for_runtime_ready()
        self._wait_for_io_saturation()
        self.env.reconnect()
        print(
            "[FaultInjector:PgBusinessChangeIoSaturationInjector] "
            f"Background maintenance and {len(self._slow_query_threads)} slow query sessions are active."
        )

    def _wait_for_runtime_ready(self) -> None:
        import time

        expected_worker_sessions = {
            self.maintenance_app_name: self.maintenance_worker_count,
        }
        expected_worker_sessions.update(
            {decoy_app: 1 for decoy_app, _task in self.decoy_workers}
        )
        deadline = time.monotonic() + self.startup_timeout_seconds
        while True:
            worker_filters = ", ".join(
                f"count(*) FILTER (WHERE application_name = '{app}' "
                "AND state = 'active' AND backend_type = 'client backend')"
                for app in expected_worker_sessions
            )
            payload = _json_object(
                self.env.execute_sql(
                    "SELECT "
                    + worker_filters
                    + f", count(*) FILTER (WHERE application_name LIKE '{self.slow_query_app_prefix}%' "
                    "AND backend_type = 'client backend') "
                    "FROM pg_stat_activity WHERE datname = current_database();"
                ),
                "verify I/O-saturation runtime sessions",
            )
            counts = [int(value) for value in payload["result"][0]]
            *worker_counts, slow_query_count = counts
            observed = dict(zip(expected_worker_sessions, worker_counts))
            if (
                observed == expected_worker_sessions
                and slow_query_count == len(self.slow_queries)
            ):
                return
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "I/O-saturation runtime sessions did not become observable: "
                    f"expected_workers={expected_worker_sessions}, "
                    f"observed_workers={observed}, "
                    f"expected_slow_queries={len(self.slow_queries)}, "
                    f"observed_slow_queries={slow_query_count}, "
                    f"timeout_seconds={self.startup_timeout_seconds}"
                )
            time.sleep(0.5)

    def _observe_temp_bytes(self) -> int | None:
        payload = _json_response(
            self.env.execute_sql(
                "SELECT coalesce(max(temp_bytes), 0) FROM pg_stat_database "
                "WHERE datname = current_database();"
            ),
            "observe I/O-saturation temp spill counter",
        )
        if payload.get("status") != "success":
            return None
        return int(payload["result"][0][0])

    def _wait_for_io_saturation(self) -> None:
        import time

        # cgroup 设备写在低内存压力宿主上会被页缓存长期吸收（脏页老化前
        # 不产生设备流量），因此 maintenance 变体额外接受 pg_stat_database
        # 的 temp 溢写增长作为激活证据：溢写是本故障的直接机制，且不受
        # 设备回写时机影响。
        use_temp_signal = self.fault_variant == "maintenance_io_saturation"
        baseline_temp_bytes = self._observe_temp_bytes() if use_temp_signal else None
        deadline = time.monotonic() + self.io_observability_timeout_seconds
        last_observed = None
        while time.monotonic() < deadline:
            payload = _json_response(
                self.env.query_metrics("disk_io"),
                "verify I/O-saturation metrics",
            )
            if payload.get("status") == "error":
                if "Sampler has no data yet" not in str(payload.get("error")):
                    raise RuntimeError(
                        f"Failed to observe I/O-saturation metrics: result={payload}"
                    )
                time.sleep(0.5)
                continue

            series = payload["series"]["postgres"]
            latest_read = float(series["read_mb_per_second"][-1])
            latest_write = float(series["write_mb_per_second"][-1])
            last_observed = {"read": latest_read, "write": latest_write}
            if max(latest_read, latest_write) >= self.minimum_io_mb_per_sec:
                return
            if use_temp_signal and baseline_temp_bytes is not None:
                temp_bytes = self._observe_temp_bytes()
                spilled_mb = (temp_bytes - baseline_temp_bytes) / (1024 * 1024)
                if spilled_mb >= self.minimum_io_mb_per_sec:
                    return
            time.sleep(0.5)

        spilled_mb = (
            (self._observe_temp_bytes() - baseline_temp_bytes) / (1024 * 1024)
            if use_temp_signal and baseline_temp_bytes is not None
            else None
        )
        raise RuntimeError(
            "I/O-saturation throughput did not become observable: "
            f"required_mb_per_sec={self.minimum_io_mb_per_sec}, "
            f"last_observed={last_observed}, "
            f"temp_spilled_mb={spilled_mb}, "
            f"timeout_seconds={self.io_observability_timeout_seconds}"
        )

    def _connect(self, application_name: str, user: str = ""):
        import psycopg2

        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=user or self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=5,
            application_name=application_name,
        )
        conn.autocommit = True
        self._connections.append(conn)
        return conn

    def _setup_schema(self):
        self._terminate_leftover_sessions()
        self.env.execute_sql("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
        if self.fault_variant == "wal_archive_backlog":
            self._setup_wal_backlog_schema()
            return
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table} CASCADE;")
        self.env.execute_sql(f"""
            CREATE TABLE {self.table} (
                id integer PRIMARY KEY,
                customer_id integer NOT NULL,
                region_id integer NOT NULL,
                item_id integer NOT NULL,
                amount numeric(12, 2) NOT NULL,
                status text NOT NULL,
                order_ts timestamptz NOT NULL,
                payload text NOT NULL
            );
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.table} (id, customer_id, region_id, item_id, amount, status, order_ts, payload)
            SELECT
                g,
                (g % 5000) + 1,
                (g % 32) + 1,
                (g % 10000) + 1,
                ((g % 100000)::numeric / 100) + 1,
                CASE WHEN g % 11 = 0 THEN 'RETURNED' WHEN g % 7 = 0 THEN 'PENDING' ELSE 'SOLD' END,
                NOW() - (g % 365) * INTERVAL '1 day',
                repeat(md5(g::text), 8)
            FROM generate_series(1, {self.row_count}) AS g;
        """)
        self.env.execute_sql(f"CREATE INDEX idx_{self.table}_customer_ts ON {self.table}(customer_id, order_ts);")
        self.env.execute_sql(f"CREATE INDEX idx_{self.table}_region_status ON {self.table}(region_id, status);")
        self.env.execute_sql(f"CREATE INDEX idx_{self.table}_payload ON {self.table}(payload);")
        self.env.execute_sql(f"ANALYZE {self.table};")
        self.env.execute_sql("DROP TABLE IF EXISTS aiopsbench_io_runtime_gate;")
        self.env.execute_sql("""
            CREATE TABLE aiopsbench_io_runtime_gate (
                gate_key text PRIMARY KEY,
                gate_value text NOT NULL
            );
        """)
        escaped_maintenance = self.maintenance_app_name.replace("'", "''")
        self.env.execute_sql(
            "INSERT INTO aiopsbench_io_runtime_gate(gate_key, gate_value) "
            f"VALUES ('maintenance_app', '{escaped_maintenance}');"
        )
        if self.schedule_table:
            self.env.execute_sql(f"""
                CREATE TABLE {self.schedule_table} (
                    job_name text PRIMARY KEY,
                    worker_application text NOT NULL,
                    worker_task text NOT NULL,
                    enabled boolean NOT NULL,
                    restart_delay_seconds integer NOT NULL,
                    last_heartbeat_at timestamptz
                );
            """)
            worker_job_rows = [
                (self.culprit_job_name, self.maintenance_app_name, self.worker_task_name, True, 8),
                *(
                    (f"{decoy_task}_worker", decoy_app, decoy_task, True, 8)
                    for decoy_app, decoy_task in self.decoy_workers
                ),
                (self.healthy_job_name, self.scheduler_app_name, self.healthy_job_name, True, 8),
                (self.disabled_job_name, "report-rollup-refresh-legacy", "report_rollup_v1", False, 30),
            ]
            rows_sql = ", ".join(
                f"('{job_name}', '{worker_application}', '{worker_task}', {enabled}, {delay}, now())"
                if enabled
                else
                f"('{job_name}', '{worker_application}', '{worker_task}', {enabled}, {delay}, now() - interval '3 days')"
                for job_name, worker_application, worker_task, enabled, delay in worker_job_rows
            )
            self.env.execute_sql(
                f"INSERT INTO {self.schedule_table}(job_name, worker_application, worker_task, enabled, restart_delay_seconds, last_heartbeat_at) "
                f"VALUES {rows_sql};"
            )
            self.env.execute_sql(f"""
                CREATE TABLE {self.job_run_table} (
                    run_id bigserial PRIMARY KEY,
                    job_name text NOT NULL,
                    started_at timestamptz NOT NULL DEFAULT now(),
                    source text NOT NULL
                );
            """)
            bootstrap_jobs = [self.culprit_job_name] + [
                f"{decoy_task}_worker"
                for _app, decoy_task in self.decoy_workers
            ]
            bootstrap_sql = ", ".join(
                f"('{job_name}', 'bootstrap')" for job_name in bootstrap_jobs
            )
            self.env.execute_sql(
                f"INSERT INTO {self.job_run_table}(job_name, source) VALUES {bootstrap_sql};"
            )
        if self.twin_table:
            self.env.execute_sql(f"DROP TABLE IF EXISTS {self.twin_table};")
            self.env.execute_sql(f"""
                CREATE TABLE {self.twin_table} (
                    id integer PRIMARY KEY,
                    shipment_no text NOT NULL,
                    carrier text NOT NULL,
                    weight_kg numeric(8, 2) NOT NULL
                );
            """)
            self.env.execute_sql(f"""
                INSERT INTO {self.twin_table} (id, shipment_no, carrier, weight_kg)
                SELECT g, 'SHP-' || lpad(g::text, 8, '0'),
                       (ARRAY['express','freight','postal','air'])[1 + g % 4],
                       ((g % 4000)::numeric / 100) + 1
                FROM generate_series(1, 9000) AS g;
            """)
            self.env.execute_sql(f"CREATE INDEX idx_{self.twin_table}_carrier ON {self.twin_table}(carrier);")
        if self.report_role_name:
            self.env.execute_sql(
                f"DROP ROLE IF EXISTS {self.report_role_name};"
            )
            self.env.execute_sql(
                f"CREATE ROLE {self.report_role_name} LOGIN PASSWORD '{self.env.password}';"
            )
            self.env.execute_sql(
                f"GRANT SELECT ON {self.table} TO {self.report_role_name};"
            )
            self.env.execute_sql(
                f"ALTER ROLE {self.report_role_name} IN DATABASE {self.env.dbname} "
                f"SET work_mem = '{self.report_role_work_mem}';"
            )
        if self.bi_role_name:
            self.env.execute_sql(
                f"DROP ROLE IF EXISTS {self.bi_role_name};"
            )
            self.env.execute_sql(
                f"CREATE ROLE {self.bi_role_name} NOLOGIN;"
            )
            self.env.execute_sql(
                f"ALTER ROLE {self.bi_role_name} "
                f"SET work_mem = '{self.bi_role_work_mem}';"
            )
        if self.database_work_mem:
            self.env.execute_sql(
                f"ALTER DATABASE {self.env.dbname} "
                f"SET work_mem = '{self.database_work_mem}';"
            )
        if self.worker_entry_function:
            self.env.execute_sql(f"""
                CREATE TABLE {self.worker_tick_table} (
                    worker_application text NOT NULL,
                    ticked_at timestamptz NOT NULL
                );
            """)
            self.env.execute_sql(f"""
                CREATE OR REPLACE FUNCTION {self.worker_entry_function}()
                RETURNS void AS $$
                DECLARE
                    worker_name text := current_setting('application_name');
                BEGIN
                    RAISE LOG 'worker task cycle commit: %', worker_name;
                    DROP TABLE IF EXISTS worker_stage_tmp;
                    IF worker_name = '{self.maintenance_app_name}' THEN
                        CREATE TEMP TABLE worker_stage_tmp ON COMMIT DROP AS
                        SELECT
                            id,
                            customer_id,
                            region_id,
                            item_id,
                            amount,
                            payload
                        FROM {self.table}
                        ORDER BY payload;
                    ELSE
                        CREATE TEMP TABLE worker_stage_tmp ON COMMIT DROP AS
                        SELECT
                            id,
                            customer_id,
                            region_id,
                            item_id,
                            amount,
                            payload
                        FROM {self.table}
                        WHERE id % 997 = 1
                        ORDER BY payload;
                    END IF;
                    CREATE INDEX worker_stage_tmp_payload_idx ON worker_stage_tmp(payload);
                    PERFORM count(*) FROM worker_stage_tmp WHERE payload IS NOT NULL;
                    INSERT INTO {self.worker_tick_table}(worker_application, ticked_at)
                        VALUES (worker_name, clock_timestamp());
                    PERFORM pg_sleep(2);
                END;
                $$ LANGUAGE plpgsql;
            """)
        else:
            self.env.execute_sql(f"""
                CREATE OR REPLACE FUNCTION {self.maintenance_function}(max_seconds integer)
                RETURNS void AS $$
                DECLARE
                    deadline timestamptz := clock_timestamp() + (max_seconds::text || ' seconds')::interval;
                BEGIN
                    WHILE clock_timestamp() < deadline LOOP
                        RAISE LOG 'maintenance cycle start';
                        DROP TABLE IF EXISTS aiopsbench_io_tmp;
                        CREATE TEMP TABLE aiopsbench_io_tmp ON COMMIT DROP AS
                        SELECT
                            id,
                            customer_id,
                            region_id,
                            item_id,
                            amount,
                            payload
                        FROM {self.table}
                        ORDER BY payload;
                        CREATE INDEX aiopsbench_io_tmp_payload_idx ON aiopsbench_io_tmp(payload);
                        PERFORM count(*) FROM aiopsbench_io_tmp WHERE payload IS NOT NULL;
                    END LOOP;
                END;
                $$ LANGUAGE plpgsql;
            """)
        self.env.execute_sql(f"""
            CREATE OR REPLACE FUNCTION run_report_latency_probe(query_id integer)
            RETURNS bigint AS $$
            DECLARE
                total bigint := 0;
            BEGIN
                SELECT count(*)
                INTO total
                FROM (
                    SELECT id
                    FROM {self.table}
                    WHERE id BETWEEN ((query_id % 10) * 1000 + 1)
                                 AND ((query_id % 10) * 1000 + 500)
                    ORDER BY payload
                ) report_rows;
                RETURN total;
            END;
            $$ LANGUAGE plpgsql;
        """)

    def _setup_wal_backlog_schema(self):
        if self.wal_slot_name:
            self._drop_slot_if_exists(self.wal_slot_name)
        if self.healthy_slot_name:
            self._drop_slot_if_exists(self.healthy_slot_name)
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table} CASCADE;")
        self.env.execute_sql(f"""
            CREATE TABLE {self.table} (
                id bigserial PRIMARY KEY,
                customer_id integer NOT NULL,
                status text NOT NULL,
                amount numeric(12, 2) NOT NULL,
                payload text NOT NULL,
                created_at timestamptz NOT NULL DEFAULT now()
            );
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.table} (customer_id, status, amount, payload)
            SELECT
                (g % 5000) + 1,
                CASE WHEN g % 9 = 0 THEN 'RETRY' ELSE 'COMMITTED' END,
                ((g % 10000)::numeric / 100) + 1,
                repeat(md5('wal-backlog-' || g::text), 8)
            FROM generate_series(1, {self.row_count}) AS g;
        """)
        self.env.execute_sql(f"CREATE INDEX idx_{self.table}_customer ON {self.table}(customer_id);")
        self.env.execute_sql(f"ANALYZE {self.table};")
        self.env.execute_sql(f"SELECT pg_create_physical_replication_slot('{self.wal_slot_name}', true);")
        if self.healthy_slot_name:
            self.env.execute_sql(f"SELECT pg_create_physical_replication_slot('{self.healthy_slot_name}', false);")
        self.env.execute_sql(f"""
            CREATE OR REPLACE FUNCTION run_wal_backlog_victim_probe(max_seconds integer, query_id integer)
            RETURNS bigint AS $$
            DECLARE
                deadline timestamptz := clock_timestamp() + (max_seconds::text || ' seconds')::interval;
                minimum_end timestamptz := clock_timestamp() + INTERVAL '5 seconds';
                backlog_active boolean := true;
                total bigint := 0;
            BEGIN
                WHILE clock_timestamp() < deadline LOOP
                    SELECT count(*)
                    INTO total
                    FROM (
                        SELECT id
                        FROM {self.table}
                        WHERE customer_id BETWEEN ((query_id % 20) * 100 + 1)
                                             AND ((query_id % 20) * 100 + 600)
                        ORDER BY payload
                    ) report_rows;

                    SELECT EXISTS (
                        SELECT 1
                        FROM pg_replication_slots
                        WHERE slot_name = '{self.wal_slot_name}'
                    )
                    INTO backlog_active;

                    IF NOT backlog_active AND clock_timestamp() >= minimum_end THEN
                        RETURN total;
                    END IF;
                END LOOP;
                RETURN total;
            END;
            $$ LANGUAGE plpgsql;
        """)

    def _run_worker(self, app_name: str):
        conn = None
        try:
            conn = self._connect(app_name)
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                cur.execute("SET work_mem = '1MB';")
                if self.worker_entry_function:
                    import time

                    deadline = time.time() + self.maintenance_seconds
                    while time.time() < deadline and not (
                        self._runtime_stop_event is not None
                        and self._runtime_stop_event.is_set()
                    ):
                        cur.execute(f"SELECT {self.worker_entry_function}();")
                else:
                    cur.execute(
                        f"SELECT {self.maintenance_function}(%s);",
                        (self.maintenance_seconds,),
                    )
        except Exception as exc:
            print(
                "[FaultInjector:PgBusinessChangeIoSaturationInjector] "
                f"Worker session {app_name} stopped: {exc}"
            )
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _run_scheduler(self):
        import threading
        import time

        conn = None
        try:
            conn = self._connect(self.scheduler_app_name)
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                relaunch_gates = {}
                while (
                    self._runtime_stop_event is not None
                    and not self._runtime_stop_event.is_set()
                ):
                    cur.execute(
                        f"UPDATE {self.schedule_table} "
                        "SET last_heartbeat_at = now() "
                        "WHERE enabled;"
                    )
                    cur.execute(
                        f"SELECT job_name, worker_application, restart_delay_seconds "
                        f"FROM {self.schedule_table} "
                        "WHERE enabled AND worker_application <> %s;",
                        (self.scheduler_app_name,),
                    )
                    for job_name, worker_app, delay in cur.fetchall():
                        cur.execute(
                            "SELECT count(*) FROM pg_stat_activity "
                            "WHERE datname = current_database() "
                            "AND application_name = %s;",
                            (worker_app,),
                        )
                        worker_sessions = int(cur.fetchone()[0])
                        if worker_sessions == 0 and time.time() >= relaunch_gates.get(job_name, self._relaunch_not_before_ts):
                            cur.execute(
                                f"INSERT INTO {self.job_run_table}(job_name, source) "
                                "VALUES (%s, 'scheduler');",
                                (job_name,),
                            )
                            relaunch_gates[job_name] = time.time() + float(delay)
                            thread = threading.Thread(
                                target=self._run_worker,
                                args=(worker_app,),
                                daemon=True,
                            )
                            thread.start()
                            self._maintenance_threads.append(thread)
                    self._runtime_stop_event.wait(4)
        except Exception as exc:
            print(
                "[FaultInjector:PgBusinessChangeIoSaturationInjector] "
                f"Batch scheduler stopped: {exc}"
            )
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _run_twin_maintenance(self):
        import time

        conn = None
        try:
            conn = self._connect(self.twin_app_name)
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                while (
                    self._runtime_stop_event is not None
                    and not self._runtime_stop_event.is_set()
                ):
                    cur.execute(f"VACUUM (ANALYZE) {self.twin_table};")
                    self._runtime_stop_event.wait(20)
        except Exception as exc:
            print(
                "[FaultInjector:PgBusinessChangeIoSaturationInjector] "
                f"Twin maintenance session stopped: {exc}"
            )
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _run_wal_backlog_writer(self, worker_id: int):
        import time

        conn = None
        deadline = time.time() + self.maintenance_seconds
        try:
            conn = self._connect(self.maintenance_app_name)
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                batch = 0
                while (
                    time.time() < deadline
                    and self._wal_writer_stop_event is not None
                    and not self._wal_writer_stop_event.is_set()
                ):
                    cur.execute(
                        "SELECT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = %s);",
                        (self.wal_slot_name,),
                    )
                    row = cur.fetchone()
                    if not row or not bool(row[0]):
                        break
                    cur.execute(
                        f"""
                        INSERT INTO {self.table} (customer_id, status, amount, payload)
                        SELECT
                            (g % 5000) + 1,
                            'WAL_BACKLOG',
                            ((g % 10000)::numeric / 100) + 1,
                            repeat(md5('writer-{worker_id}-{batch}-' || g::text), 16)
                        FROM generate_series(1, 1200) AS g;
                        """
                    )
                    batch += 1
                    if batch % 4 == 0:
                        cur.execute("CHECKPOINT;")
                    time.sleep(0.08)
        except Exception as exc:
            print(
                "[FaultInjector:PgBusinessChangeIoSaturationInjector] "
                f"WAL backlog writer {worker_id} stopped: {exc}"
            )
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            self._terminate_slow_query_sessions()
            self._close_slow_query_connections()

    def _run_slow_query(self, worker_id: int, sql: str):
        conn = None
        try:
            conn = self._connect(f"{self.slow_query_app_prefix}{worker_id}")
            self._slow_query_connections.append(conn)
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                cur.execute(sql)
        except Exception as exc:
            print(f"[FaultInjector:PgBusinessChangeIoSaturationInjector] Slow query {worker_id} stopped: {exc}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _maintenance_pressure_active(self, cur) -> bool:
        escaped_maintenance = self.maintenance_app_name.replace("'", "''")
        work_mem_clause = ""
        if self.report_role_name:
            escaped_role = self.report_role_name.replace("'", "''")
            work_mem_clause = (
                " OR EXISTS ("
                "SELECT 1 FROM pg_db_role_setting s, unnest(s.setconfig) AS cfg "
                f"WHERE s.setrole = (SELECT oid FROM pg_roles WHERE rolname = '{escaped_role}') "
                "AND cfg LIKE 'work_mem=%' "
                f"AND pg_size_bytes(split_part(cfg, '=', 2)) < pg_size_bytes('{self.report_work_mem_floor}')"
                ")"
            )
        cur.execute(
            "SELECT EXISTS ("
            "SELECT 1 FROM pg_stat_activity AS a "
            f"WHERE a.application_name = '{escaped_maintenance}' AND a.state = 'active')"
            + work_mem_clause + ";"
        )
        return bool(cur.fetchone()[0])

    def _run_maintenance_slow_query(self, worker_id: int, sql: str):
        """Victim probe loop: each iteration issues fresh statements so the
        maintenance-pressure gate reads a current pg_stat_activity snapshot."""
        import time

        conn = None
        try:
            conn = self._connect(
                f"{self.slow_query_app_prefix}{worker_id}",
                user=self.report_role_name or None,
            )
            self._slow_query_connections.append(conn)
            minimum_end = time.time() + 2.0
            deadline = time.time() + self.slow_query_seconds
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                while time.time() < deadline:
                    if self._runtime_stop_event is not None and self._runtime_stop_event.is_set():
                        break
                    cur.execute(sql)
                    if time.time() >= minimum_end and not self._maintenance_pressure_active(cur):
                        break
                    time.sleep(0.05)
        except Exception as exc:
            print(f"[FaultInjector:PgBusinessChangeIoSaturationInjector] Slow query {worker_id} stopped: {exc}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _close_slow_query_connections(self):
        for conn in list(self._slow_query_connections):
            try:
                conn.close()
            except Exception:
                pass
        self._slow_query_connections = []

    def _terminate_slow_query_sessions(self):
        conn = None
        try:
            escaped_prefix = self.slow_query_app_prefix.replace("'", "''")
            conn = self._connect("aiopsbench_io_controller")
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE (
                            application_name LIKE 'report-dashboard-slow-%'
                         OR application_name LIKE 'aiopsbench_io_slow_query_%'
                         OR application_name LIKE '{escaped_prefix}%'
                    )
                      AND pid <> pg_backend_pid();
                """)
        except Exception as exc:
            print(f"[FaultInjector:PgBusinessChangeIoSaturationInjector] Slow query cleanup skipped: {exc}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _terminate_report_role_sessions(self):
        if not self.report_role_name:
            return
        escaped_role = self.report_role_name.replace("'", "''")
        try:
            conn = self._connect("aiopsbench_io_controller")
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE usename = %s AND pid <> pg_backend_pid();",
                    (escaped_role,),
                )
        except Exception as exc:
            print(
                "[FaultInjector:PgBusinessChangeIoSaturationInjector] "
                f"Report role session cleanup skipped: {exc}"
            )
        finally:
            pass

    def _terminate_leftover_sessions(self):
        escaped_maintenance = self.maintenance_app_name.replace("'", "''")
        escaped_prefix = self.slow_query_app_prefix.replace("'", "''")
        escaped_scheduler = self.scheduler_app_name.replace("'", "''")
        escaped_twin = self.twin_app_name.replace("'", "''")
        escaped_decoys = "".join(
            f" OR application_name = '{decoy_app.replace(chr(39), chr(39) * 2)}'"
            for decoy_app, _task in self.decoy_workers
        )
        _require_sql_success(
            self.env.execute_sql(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE (
                        application_name LIKE 'report-dashboard-slow-%'
                     OR application_name LIKE 'aiopsbench_io_%'
                     OR application_name LIKE 'wal-backlog-victim-report-%'
                     OR application_name = 'wal-archive-backlog-writer-04'
                     OR application_name = '{escaped_maintenance}'
                     OR application_name LIKE '{escaped_prefix}%'
                     OR application_name = '{escaped_scheduler}'
                     OR application_name = '{escaped_twin}'
                     {escaped_decoys}
                )
                  AND pid <> pg_backend_pid();
            """),
            "terminate I/O-saturation sessions",
        )

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        if self.fault_variant != "wal_archive_backlog":
            return {}
        return {
            "disk_io": env.query_metrics("disk_io"),
            "slow_queries": env.query_metrics("slow_queries", threshold_ms=1000),
            "replication_slots": env.execute_sql(
                "SELECT slot_name, active, restart_lsn, wal_status, "
                "pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS retained_bytes "
                "FROM pg_replication_slots "
                f"WHERE slot_name IN ('{self.wal_slot_name}', '{self.healthy_slot_name}') "
                "ORDER BY retained_bytes DESC NULLS LAST;"
            ),
            "archiver": env.execute_sql(
                "SELECT archived_count, failed_count, last_failed_wal, last_failed_time "
                "FROM pg_stat_archiver;"
            ),
        }

    def quiesce(self, context: FaultLifecycleContext):
        self._stop_runtime(context)

    def _stop_runtime(self, context: FaultLifecycleContext) -> None:
        self.env = context.env
        if self._wal_writer_stop_event is not None:
            self._wal_writer_stop_event.set()
        if self._runtime_stop_event is not None:
            self._runtime_stop_event.set()
        self._terminate_leftover_sessions()
        threads = [*self._maintenance_threads, *self._slow_query_threads]
        connections = [*self._connections, *self._slow_query_connections]
        steps = [
            (
                f"join I/O worker thread {index}",
                lambda thread=thread, index=index: _join_thread(
                    thread,
                    5,
                    f"I/O-saturation thread {index}",
                ),
            )
            for index, thread in enumerate(threads)
        ]
        steps.extend(
            (f"close I/O connection {index}", conn.close)
            for index, conn in enumerate(connections)
            if not conn.closed
        )
        _run_cleanup_steps(
            f"I/O-saturation cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._connections = []
        self._slow_query_connections = []
        self._maintenance_threads = []
        self._slow_query_threads = []
        self._wal_writer_stop_event = None
        self._runtime_stop_event = None

    def recover(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        print("[FaultInjector:PgBusinessChangeIoSaturationInjector] Recovering I/O saturation fault...")
        self._stop_runtime(context)
        if not self.env.reconnect():
            raise RuntimeError(
                f"I/O-saturation recovery could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        _require_sql_success(
            self.env.execute_sql(
                "DROP FUNCTION IF EXISTS run_report_latency_probe(integer); "
                "DROP FUNCTION IF EXISTS run_wal_backlog_victim_probe(integer, integer); "
                "DROP FUNCTION IF EXISTS refresh_report_rollup_state(integer); "
                f"DROP FUNCTION IF EXISTS {self.maintenance_function}(integer); "
                f"DROP FUNCTION IF EXISTS {self.maintenance_function}(text, integer); "
                f"DROP FUNCTION IF EXISTS {self.maintenance_function}(); "
                "DROP FUNCTION IF EXISTS aiopsbench_io_slow_report(integer, integer); "
                "DROP FUNCTION IF EXISTS aiopsbench_io_workload_driver(integer); "
                "DROP FUNCTION IF EXISTS aiopsbench_io_maintenance_burn(integer); "
                "DROP TABLE IF EXISTS aiopsbench_io_runtime_gate; "
                "DROP TABLE IF EXISTS aiopsbench_io_tmp; "
                "DROP TABLE IF EXISTS worker_stage_tmp; "
                f"DROP TABLE IF EXISTS {self.table} CASCADE;"
                + (
                    f" DROP TABLE IF EXISTS {self.job_run_table};"
                    f" DROP TABLE IF EXISTS {self.schedule_table};"
                    if self.schedule_table
                    else ""
                )
                + (
                    f" DROP TABLE IF EXISTS {self.twin_table};"
                    if self.twin_table
                    else ""
                )
                + (
                    f" DROP TABLE IF EXISTS {self.worker_tick_table};"
                    if self.worker_tick_table
                    else ""
                ),
            ),
            "recover I/O-saturation functions and tables",
        )
        if self.database_work_mem and self.env.dbname.isidentifier():
            _require_sql_success(
                self.env.execute_sql(
                    f"ALTER DATABASE {self.env.dbname} RESET work_mem;"
                ),
                "recover I/O-saturation database work_mem override",
            )
        if self.bi_role_name:
            _require_sql_success(
                self.env.execute_sql(
                    f"DROP ROLE IF EXISTS {self.bi_role_name};"
                ),
                "recover I/O-saturation bi role",
            )
        if self.report_role_name:
            self._terminate_report_role_sessions()
            _require_sql_success(
                self.env.execute_sql(
                    f"DROP ROLE IF EXISTS {self.report_role_name};"
                ),
                "recover I/O-saturation report role",
            )
        if self.wal_slot_name:
            self._drop_slot_if_exists(self.wal_slot_name)
        if self.healthy_slot_name:
            self._drop_slot_if_exists(self.healthy_slot_name)

    def _drop_slot_if_exists(self, slot_name: str) -> None:
        _require_sql_success(
            self.env.execute_sql(
                f"SELECT pg_drop_replication_slot(slot_name) "
                f"FROM pg_replication_slots WHERE slot_name = '{slot_name}';"
            ),
            f"drop WAL-backlog replication slot {slot_name}",
        )


class PgBusinessChangeIoSaturationScenario(PostgresScenario):
    scenario_id = 'pg_business_change_io_saturation'
    description = 'Slow-query alert caused by background maintenance saturating database I/O.'
    cases = (
        _PGBUSINESSCHANGEIOSATURATIONSCENARIO_CASE,
        _PGBUSINESSCHANGEIOSATURATIONSCENARIO_VACUUM_REPORT_CASE,
        _PGBUSINESSCHANGEIOSATURATIONSCENARIO_ARCHIVE_BACKLOG_CASE,
    )

    def build_fault_plan(self, case: PgBusinessChangeIoSaturationCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgBusinessChangeIoSaturationInjector,
                config={
                    'table': case.table,
                    'fault_variant': case.fault_variant,
                    'row_count': case.row_count,
                    'slow_queries': case.slow_queries_2,
                    'slow_query_seconds': case.slow_query_seconds,
                    'maintenance_seconds': case.maintenance_seconds,
                    'maintenance_worker_count': case.maintenance_worker_count,
                    'startup_timeout_seconds': case.startup_timeout_seconds,
                    'io_observability_timeout_seconds': case.io_observability_timeout_seconds,
                    'minimum_io_mb_per_sec': case.minimum_io_mb_per_sec,
                    'maintenance_app_name': case.maintenance_app_name,
                    'slow_query_app_prefix': case.slow_query_app_prefix,
                    'wal_slot_name': case.wal_slot_name,
                    'healthy_slot_name': case.healthy_slot_name,
                    'scheduler_app_name': case.scheduler_app_name,
                    'schedule_table': case.schedule_table,
                    'job_run_table': case.job_run_table,
                    'healthy_job_name': case.healthy_job_name,
                    'culprit_job_name': case.culprit_job_name,
                    'disabled_job_name': case.disabled_job_name,
                    'report_role_name': case.report_role_name,
                    'report_role_work_mem': case.report_role_work_mem,
                    'report_work_mem_floor': case.report_work_mem_floor,
                    'bi_role_name': case.bi_role_name,
                    'bi_role_work_mem': case.bi_role_work_mem,
                    'bi_work_mem_floor': case.bi_work_mem_floor,
                    'database_work_mem': case.database_work_mem,
                    'database_work_mem_floor': case.database_work_mem_floor,
                    'twin_app_name': case.twin_app_name,
                    'twin_table': case.twin_table,
                    'maintenance_function': case.maintenance_function,
                    'worker_entry_function': case.worker_entry_function,
                    'worker_task_name': case.worker_task_name,
                    'decoy_workers': case.decoy_workers,
                    'worker_tick_table': case.worker_tick_table,
                },
            ),
        )
