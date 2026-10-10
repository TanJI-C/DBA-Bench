"""PG-RG-IO01: distinguish I/O context from the batch workload that caused the SLO miss.

The injector deliberately keeps the observation path honest.  ``pg_stat_io`` is
sampled as a cluster/backend/context aggregate.  Query and application buckets
come from the independent sampler's active-session/query_id join and
``pg_stat_statements`` deltas; they are never presented as native per-query
``pg_stat_io.read_time`` values.
"""

from __future__ import annotations

import hashlib
import json
import re
import socket
import subprocess
import threading
import time
import traceback
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Mapping

from src.scenarios.evaluation.postgres.resource_governance.io_context_workload import (
    PgResourceGovernanceIoContextWorkloadForReportIsPressureEvaluatorCase,
    PgResourceGovernanceIoContextWorkloadForReportIsPressureSimpleEvaluatorCase,
)
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.postgres.common import _json_object, _require_sql_success, _run_cleanup_steps
from src.scenarios.base import (
    BackgroundWorkloadSpec,
    CaseResourceSpec,
    DifficultyCalibration,
    FaultPlan,
    PostgresCaseRuntime,
    PostgresRuntimeSpec,
    PostgresScenario,
    PostgresScenarioCase,
)
from src.workloads.tpcds import get_tpcds_query


SCENARIO_ID = "pg_resource_governance_io_context_workload"
BASE_IMAGE = "aiopsbench-pg-pg-io-context-tpcds:latest"
DEFAULT_POSTGRES_PORT = 15871
MONITOR_PORT_MIN = 15872
MONITOR_PORT_MAX = 15879
REPORT_SQL = get_tpcds_query("q77").rstrip().rstrip(";").rstrip()
REPORT_ROUTINE = "ops_run_batch"
# Every report-like source uses the same prepared statement. Its parameters
# select a business slice, while PostgreSQL normalizes all calls into one
# queryid. The routine remains a real, inspectable TPC-DS workload.
REPORT_SQL_TEMPLATE = (
    REPORT_SQL
    .replace("(cast('2001-08-11' as date) + interval '30 days')", "($1 + make_interval(days => $2))")
    .replace("cast('2001-08-11' as date)", "$1")
)
# Values are carried in ordinary PostgreSQL session context.  This keeps the
# active statement identical across sources while the call ledger records the
# actual business slice after completion.
REPORT_ROUTINE_CALL_SQL = (
    f"SELECT * FROM public.{REPORT_ROUTINE}("
    "current_setting('ops.report_anchor')::date, "
    "current_setting('ops.report_window_days')::integer)"
)
REPORT_CALL_PROFILES: dict[str, tuple[str, int]] = {
    "worker-1": ("1999-01-15", 45),
    "worker-2": ("2001-08-11", 30),
    "worker-3": ("2000-06-01", 30),
    "worker-4": ("2002-02-01", 60),
    "worker-5": ("2001-01-15", 45),
    "worker-6": ("2003-01-15", 30),
    "worker-7": ("1998-07-15", 30),
    "worker-8": ("2002-07-15", 45),
    # These scheduler replicas intentionally use the same business slice as
    # the target.  Their job and checksum records therefore remain valid
    # evidence of a shared report family, rather than an identity marker.
    "worker-9": ("2001-08-11", 30),
    "worker-10": ("2001-08-11", 30),
    "warehouse-refresh": ("2001-08-11", 30),
    "finance-rollup": ("2001-08-11", 30),
}
IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")
APPLICATION_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,62}$")
CONTROL_MODES = frozenset({
    "pause",
    "stop",
    "throttle",
    "reschedule",
    "io_limit",
    "cgroup_io_limit",
    "role_limit",
    "role_concurrency",
    "query_rewrite",
    "replica",
    "maintenance_budget",
    "job_reschedule",
    "controlled",
})
CONTROL_NAME = "workload_policy"

IO_CONTEXT_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)

IO_CONTEXT_RUNTIME = PostgresCaseRuntime(
    resources=IO_CONTEXT_RESOURCES,
    parameters=PostgresRuntimeSpec(
        parameters=(
            ("shared_buffers", "64MB"),
            ("work_mem", "4MB"),
            ("track_io_timing", "on"),
            ("track_activity_query_size", "4096"),
            ("shared_preload_libraries", "pg_stat_statements"),
            ("max_wal_senders", "4"),
            ("autovacuum", "on"),
            ("autovacuum_naptime", "1s"),
        ),
    ),
)


def _reference_report(case_id: str, report_app: str) -> dict[str, object]:
    report = {
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "bulkread context pressure",
                    "entity": report_app,
                    "evidence": ["PG16 pg_stat_io bulkread deltas and device queue formed the pressure window"],
                },
                {
                    "type": "finding",
                    "factor": "report workload causes the OLTP SLO violation",
                    "entity": report_app,
                    "evidence": ["the report query bucket preceded the OLTP p99 violation"],
                },
                {
                    "type": "finding",
                    "factor": "read count alone is a decoy",
                    "entity": "batch windows",
                    "evidence": ["another window had more reads without an OLTP SLO miss"],
                },
                {
                    "type": "finding",
                    "factor": "OLTP p99 violation follows report I/O pressure",
                    "entity": "pgbench-oltp",
                    "evidence": ["the independent bucket history preserves the pressure-before-impact order"],
                },
                {
                    "type": "finding",
                    "factor": "control the report workload while preserving required jobs",
                    "entity": report_app,
                    "evidence": ["the report was throttled or rescheduled and required jobs remained eligible"],
                },
            ]
        },
        "outcome": {
            "changes": ["controlled the causal report workload without cancelling required jobs"],
            "verification": ["OLTP SLO, target workload, deadlines and result checksums were rechecked"],
        },
    "summary": "The workload's I/O context caused the business impact; cache-hit and read count were only symptoms or decoys.",
    }
    return report


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceIoContextWorkloadCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    report_app_name: str
    report_relation: str
    report_sql: str
    report_working_set_bytes: int
    report_window_count: int
    decoy_app_names: tuple[str, ...]
    decoy_types: tuple[str, ...]
    decoy_job_names: tuple[str, ...]
    interference_app_names: tuple[str, ...]
    interference_job_names: tuple[str, ...]
    required_job_names: tuple[str, ...]
    target_job_name: str
    deadline_seconds: int
    oltp_slo_p99_ms: float
    monitoring_port: int
    fault_variant: str
    synchronize_required_cohort: bool = False
    interference_call_modes: tuple[str, ...] = ()
    control_table: str = "ops_run_policy"
    observations_table: str = "ops_batch_history"
    context_observations_table: str = "ops_context_history"
    phase_observations_table: str = "ops_phase_history"
    call_history_table: str = "ops_batch_calls"
    jobs_table: str = "ops_job_registry"
    outcome_table: str = "ops_replay_status"


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceIoContextWorkloadForReportIsPressureScenarioCase(PgResourceGovernanceIoContextWorkloadCase):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceIoContextWorkloadForReportIsPressureSimpleScenarioCase(PgResourceGovernanceIoContextWorkloadCase):
    pass


_HARD_CASE = PgResourceGovernanceIoContextWorkloadForReportIsPressureScenarioCase(
    case_id="report_is_pressure",
    case_no=0,
    evaluator=PgResourceGovernanceIoContextWorkloadForReportIsPressureEvaluatorCase,
    title="PG16 I/O context identifies a workload window that violates the OLTP SLO.",
    alert=(
        "[FIRING: WARNING] alertname=PostgresCacheHitAndReadPressure "
        "service=checkout-oltp instance=postgresql-primary severity=warning\n"
        "summary=Several I/O windows show lower cache hit and higher reads while one transaction window misses SLO\n"
        "description=Compare the historical I/O context, device queue, workload buckets and transaction p99. "
        "Keep all required jobs within their deadlines while controlling the actual source of impact."
    ),
    initial_state={
        "status": "degraded",
        "alert": "cache_hit_and_read_pressure",
        "visible_symptom": "multiple_same_domain_windows_and_one_oltp_slo_miss",
        "required_observation": "pg16_context_device_bucket_timeline",
    },
    expected_target={
        "status": "recovered",
        "target_workload": "bounded_workload_control",
        "required_jobs": "completed_with_checksums_before_deadline",
        "oltp_slo": "p99_within_budget",
    },
    background_workload=BackgroundWorkloadSpec(profiles=(), worker_count=0, seed=701),
    reference_report=_reference_report("report_is_pressure", "worker-2"),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.529412,
        reference_run_ids=("pg-rg-io01-hard-proposed",),
    ),
    runtime=IO_CONTEXT_RUNTIME,
    base_image_name=BASE_IMAGE,
    workload_tag="tpcds",
    report_app_name="worker-2",
    report_relation="store_sales",
    report_sql=REPORT_SQL,
    report_working_set_bytes=64 * 1024 * 1024,
    report_window_count=3,
    decoy_app_names=(
        "worker-1",
        "worker-3",
        "worker-4",
        "worker-5",
        "worker-6",
    ),
    target_job_name="job-2",
    deadline_seconds=600,
    oltp_slo_p99_ms=1000.0,
    monitoring_port=15872,
    fault_variant="report_is_pressure",
    decoy_types=("read_decoy", "backup", "autovacuum", "read_decoy", "scan_decoy"),
    decoy_job_names=("", "", "", "", ""),
    interference_app_names=("worker-7", "worker-8", "worker-9", "worker-10"),
    interference_job_names=("job-9", "job-10", "job-11", "job-12"),
    required_job_names=("job-2", "job-9", "job-10", "job-11", "job-12"),
)

_EASY_CASE = PgResourceGovernanceIoContextWorkloadForReportIsPressureSimpleScenarioCase(
    case_id="report_is_pressure_simple",
    case_no=1,
    evaluator=PgResourceGovernanceIoContextWorkloadForReportIsPressureSimpleEvaluatorCase,
    title="A reduced I/O-context case separates a causal workload from read-count noise.",
    alert=(
        "[FIRING: WARNING] alertname=PostgresCacheHitAndReadPressure "
        "service=checkout-oltp instance=postgresql-primary severity=warning\n"
        "summary=Two I/O windows raised reads while OLTP p99 missed SLO\n"
        "description=Use I/O time, queue and the application bucket to control the causal workload, "
        "then verify the OLTP SLO and every required job without changing their results."
    ),
    initial_state={
        "status": "degraded",
        "alert": "cache_hit_and_read_pressure",
        "visible_symptom": "two_same_domain_windows_and_one_oltp_slo_miss",
        "required_observation": "count_time_queue_business_impact",
    },
    expected_target={
        "status": "recovered",
        "target_workload": "bounded_workload_control",
        "required_jobs": "completed_with_checksum_before_deadline",
        "oltp_slo": "p99_within_budget",
    },
    background_workload=BackgroundWorkloadSpec(profiles=(), worker_count=0, seed=702),
    reference_report=_reference_report("report_is_pressure_simple", "worker-2"),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.333333,
        reference_run_ids=("pg-rg-io01-easy-round1-cohort",),
    ),
    runtime=IO_CONTEXT_RUNTIME,
    base_image_name=BASE_IMAGE,
    workload_tag="tpcds",
    report_app_name="worker-2",
    report_relation="store_sales",
    report_sql=REPORT_SQL,
    report_working_set_bytes=64 * 1024 * 1024,
    report_window_count=1,
    decoy_app_names=("worker-1", "worker-3", "worker-5"),
    # Easy keeps the same bounded cohort shape as a production scheduler:
    # replicas 9/10 use the target's real business slice and remain required
    # jobs, so queryid, parameters and checksum cannot identify worker-2.
    interference_app_names=("warehouse-refresh", "finance-rollup"),
    interference_job_names=("job-9", "job-10"),
    required_job_names=("job-11", "job-9", "job-10"),
    target_job_name="job-11",
    deadline_seconds=300,
    oltp_slo_p99_ms=1000.0,
    monitoring_port=15873,
    fault_variant="report_is_pressure_simple",
    decoy_types=("scan_decoy", "read_decoy", "read_decoy"),
    decoy_job_names=("", "", ""),
    synchronize_required_cohort=True,
    interference_call_modes=("direct_sql", "direct_sql"),
)


class _IoContextMonitor:
    """Small local HTTP endpoint exposing the sampler's latest real observation."""

    def __init__(self, port: int):
        self.port = port
        self._latest: dict[str, object] = {"status": "starting", "port": port}
        self._lock = threading.Lock()
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def publish(self, payload: Mapping[str, object]) -> None:
        with self._lock:
            self._latest = dict(payload)

    def latest(self) -> dict[str, object]:
        with self._lock:
            return dict(self._latest)

    def start(self) -> None:
        if self._server is not None:
            return
        monitor = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                if self.path not in {"/health", "/metrics"}:
                    self.send_response(404)
                    self.end_headers()
                    return
                payload = json.dumps(monitor.latest(), default=str).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *_args):
                return

        self._server = ThreadingHTTPServer(("127.0.0.1", self.port), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True, name=f"pg-io-context-monitor-{self.port}")
        self._thread.start()

    def stop(self) -> None:
        server, thread = self._server, self._thread
        self._server = None
        self._thread = None
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout=3)


class PgResourceGovernanceIoContextWorkloadInjector(BaseFaultInjector):
    """Create real PG16 context pressure and keep the runtime lifecycle repeatable."""

    def __init__(self):
        self.env = None
        self.run_id = ""
        self.case: PgResourceGovernanceIoContextWorkloadCase | None = None
        self.report_app_name = ""
        self.report_sql = ""
        self.report_relation = ""
        self.report_routine = REPORT_ROUTINE
        self.report_working_set_bytes = 0
        self.report_window_count = 0
        self.decoy_app_names: tuple[str, ...] = ()
        self.decoy_types: tuple[str, ...] = ()
        self.decoy_job_names: tuple[str, ...] = ()
        self.interference_app_names: tuple[str, ...] = ()
        self.interference_job_names: tuple[str, ...] = ()
        self.required_job_names: tuple[str, ...] = ()
        self.target_job_name = ""
        self.deadline_seconds = 0
        self.oltp_slo_p99_ms = 0.0
        self.monitoring_port = 0
        self.synchronize_required_cohort = False
        self.interference_call_modes: tuple[str, ...] = ()
        self.control_table = "ops_run_policy"
        self.observations_table = "ops_batch_history"
        self.context_observations_table = "ops_context_history"
        self.phase_observations_table = "ops_phase_history"
        self.call_history_table = "ops_batch_calls"
        self.jobs_table = "ops_job_registry"
        self.outcome_table = "ops_replay_status"
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []
        self._pgbench_process: subprocess.Popen | None = None
        self._backup_processes: list[subprocess.Popen] = []
        self._connections: list[object] = []
        self._monitor: _IoContextMonitor | None = None
        self._state_lock = threading.Lock()
        self._current_window = "bootstrap"
        self._oltp_latencies: list[float] = []
        self._oltp_violations = 0
        self._observer_error: str | None = None
        self._report_controlled = False
        self._job_checksums: dict[str, str] = {}
        self._bucket_snapshots: dict[tuple[str, int | None], tuple[int, int, float]] = {}
        self._scan_decoy_ready = threading.Event()
        self._scan_decoy_error: str | None = None
        self._required_cohort_barrier: threading.Barrier | None = None

    def _configure(self, context: FaultLifecycleContext) -> None:
        config = context.config
        self.env = context.env
        self.run_id = context.run_id
        self.case = context.case
        self.report_app_name = self._application_name(config["report_app_name"], "report_app_name")
        self.report_sql = str(config["report_sql"])
        self.report_relation = self._identifier(config["report_relation"], "report_relation")
        self.report_working_set_bytes = int(config["report_working_set_bytes"])
        self.report_window_count = int(config["report_window_count"])
        self.decoy_app_names = tuple(self._application_name(item, "decoy_app_name") for item in config["decoy_app_names"])
        self.decoy_types = tuple(str(item).casefold() for item in config["decoy_types"])
        self.decoy_job_names = tuple(str(item) for item in config["decoy_job_names"])
        self.interference_app_names = tuple(
            self._application_name(item, "interference_app_name") for item in config.get("interference_app_names", ())
        )
        self.interference_job_names = tuple(
            self._application_name(item, "interference_job_name") for item in config.get("interference_job_names", ())
        )
        self.required_job_names = tuple(self._application_name(item, "required_job_name") for item in config["required_job_names"])
        self.target_job_name = self._application_name(config["target_job_name"], "target_job_name")
        self.deadline_seconds = int(config["deadline_seconds"])
        self.oltp_slo_p99_ms = float(config["oltp_slo_p99_ms"])
        self.monitoring_port = int(config["monitoring_port"])
        self.synchronize_required_cohort = bool(config.get("synchronize_required_cohort", False))
        self.interference_call_modes = tuple(
            str(item).casefold() for item in config.get("interference_call_modes", ())
        ) or ("routine",) * len(self.interference_app_names)
        self.control_table = self._identifier(config["control_table"], "control_table")
        self.observations_table = self._identifier(config["observations_table"], "observations_table")
        self.context_observations_table = self._identifier(
            config["context_observations_table"], "context_observations_table"
        )
        self.phase_observations_table = self._identifier(
            config["phase_observations_table"], "phase_observations_table"
        )
        self.call_history_table = self._identifier(config["call_history_table"], "call_history_table")
        self.jobs_table = self._identifier(config["jobs_table"], "jobs_table")
        self.outcome_table = self._identifier(config["outcome_table"], "outcome_table")
        if not 1 <= self.monitoring_port <= 65535:
            raise ValueError(f"monitoring_port must be a valid TCP port, got {self.monitoring_port}")
        if self.report_window_count <= 0 or not self.required_job_names:
            raise ValueError("I/O context case requires report windows and required jobs")
        if len(self.decoy_app_names) != len(self.decoy_types) or len(self.decoy_app_names) != len(self.decoy_job_names):
            raise ValueError("decoy_app_names, decoy_types and decoy_job_names must have the same length")
        if len(self.interference_app_names) != len(self.interference_job_names):
            raise ValueError("interference_app_names and interference_job_names must have the same length")
        if len(self.interference_app_names) != len(self.interference_call_modes):
            raise ValueError("interference_app_names and interference_call_modes must have the same length")
        if any(item not in {"routine", "direct_sql"} for item in self.interference_call_modes):
            raise ValueError(f"Unsupported PG-RG-IO01 interference call mode: {self.interference_call_modes!r}")
        all_apps = (*self.decoy_app_names, self.report_app_name, *self.interference_app_names)
        if len(set(all_apps)) != len(all_apps):
            raise ValueError(f"PG-RG-IO01 application names must be unique: {all_apps!r}")
        if len(set(self.interference_job_names)) != len(self.interference_job_names):
            raise ValueError(f"PG-RG-IO01 interference job names must be unique: {self.interference_job_names!r}")
        if any(item not in {"backup", "vacuum", "autovacuum", "read_decoy", "scan_decoy"} for item in self.decoy_types):
            raise ValueError(f"Unsupported PG-RG-IO01 decoy type: {self.decoy_types!r}")
        if self.target_job_name not in self.required_job_names:
            raise ValueError(f"target_job_name must be required: {self.target_job_name!r}")

    @staticmethod
    def _identifier(value: object, field: str) -> str:
        text = str(value)
        if not IDENTIFIER.fullmatch(text):
            raise ValueError(f"Invalid {field}: {text!r}")
        return text

    @staticmethod
    def _application_name(value: object, field: str) -> str:
        text = str(value)
        if not APPLICATION_NAME.fullmatch(text):
            raise ValueError(f"Invalid {field}: {text!r}")
        return text

    @staticmethod
    def _literal(value: object) -> str:
        return "'" + str(value).replace("'", "''") + "'"

    @property
    def _container_name(self) -> str:
        return str(getattr(getattr(self.env, "deployment", None), "container_name", ""))

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self.recover(context)
        self._assert_monitor_port_available()
        self._ensure_pgbench()
        with self.env.metrics_hidden():
            self._setup_schema()
        self._start_runtime()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self.quiesce(context)
        self._verify_persistent_state()
        self._reset_run_state()
        self._assert_monitor_port_available()
        self._start_runtime()

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        payload = _json_object(self.env.execute_sql(
            "SELECT current_setting('track_io_timing'), "
            "(SELECT count(*) FROM pg_stat_io), "
            f"(SELECT count(*) FROM {self.observations_table}), "
            f"(SELECT count(*) FROM {self.phase_observations_table}), "
            f"(SELECT count(*) FROM {self.call_history_table}), "
            f"(SELECT count(*) FROM {self.jobs_table} WHERE run_id = {self._literal(self.run_id)});"
        ), "prepare PG-RG-IO01 observability")
        row = payload["result"][0]
        if str(row[0]).lower() != "on" or int(row[1]) <= 0:
            raise RuntimeError(f"PG16 pg_stat_io/track_io_timing is not ready: row={row!r}")
        if int(row[2]) <= 0 or int(row[3]) <= 0 or int(row[4]) <= 0:
            raise RuntimeError(
                "PG-RG-IO01 independent sampler did not produce baseline call/phase rows: "
                f"error={self._observer_error!r}"
            )
        latest = self._monitor.latest() if self._monitor else {}
        protected_checksum_sql = self._checksum_sql(self.target_job_name)
        protected_checksum = self._checksum_for_job(self.target_job_name)
        return {
            "io_context_source": "pg_stat_io backend_type/object/context='bulkread' aggregate",
            "query_bucket_source": "pg_stat_statements delta plus pg_stat_activity query_id/application_name",
            "device_queue_source": "/proc/diskstats io_in_progress and weighted_io_time deltas",
            "phase_observations_table": self.phase_observations_table,
            "phase_observations_query": (
                f"SELECT phase_started_at, phase_finished_at, window_name, bucket_application, "
                f"bucket_queryid, scan_count, query_calls_delta, query_shared_blks_read_delta, "
                f"query_exec_ms_delta, context_reads_delta, context_read_time_ms_delta, "
                f"context_hits_delta, device_io_in_progress, device_weighted_io_ms_delta "
                f"FROM {self.phase_observations_table} ORDER BY phase_started_at;"
            ),
            "query_bucket_monitor_url": f"http://127.0.0.1:{self.monitoring_port}/metrics",
            "query_bucket_monitor_port": self.monitoring_port,
            "track_io_timing": row[0],
            "pg_stat_io_rows": int(row[1]),
            "observation_rows": int(row[2]),
            "phase_observation_rows": int(row[3]),
            "call_history_rows": int(row[4]),
            "job_rows": int(row[5]),
            "latest_observation": latest,
            "protected_report_checksum": protected_checksum,
            "protected_report_checksum_sql": protected_checksum_sql,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self._stop_runtime()

    def recover(self, context: FaultLifecycleContext) -> None:
        if self.env is None:
            self._configure(context)
        else:
            self._configure(context)
        self._stop_runtime()
        if not hasattr(self.env, "execute_sql"):
            return
        statements = [
            f"DROP FUNCTION IF EXISTS public.{self.report_routine}(date, integer)",
            f"DROP TABLE IF EXISTS {self.outcome_table} CASCADE",
            f"DROP TABLE IF EXISTS {self.observations_table} CASCADE",
            f"DROP TABLE IF EXISTS {self.context_observations_table} CASCADE",
            f"DROP TABLE IF EXISTS {self.phase_observations_table} CASCADE",
            f"DROP TABLE IF EXISTS {self.call_history_table} CASCADE",
            f"DROP TABLE IF EXISTS {self.jobs_table} CASCADE",
            f"DROP TABLE IF EXISTS {self.control_table} CASCADE",
        ]
        try:
            _require_sql_success(self.env.execute_sql("; ".join(statements) + ";"), "recover PG-RG-IO01 tables")
        except Exception as exc:
            if "does not exist" not in str(exc).lower() and "connection" not in str(exc).lower():
                raise

    def cleanup(self, context: FaultLifecycleContext) -> None:
        self.recover(context)

    def _assert_monitor_port_available(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", self.monitoring_port))
            except OSError as exc:
                raise RuntimeError(f"PG-RG-IO01 monitoring port is unavailable: {self.monitoring_port}") from exc

    def _ensure_pgbench(self) -> None:
        if not self._container_name:
            raise RuntimeError("PG-RG-IO01 requires PGDockerDeployment.container_name for pgbench")
        command = [
            "docker", "exec", "-e", f"PGPASSWORD={self.env.password}", self._container_name,
            "pgbench", "-h", "127.0.0.1", "-p", "5432", "-U", self.env.user,
            "-d", self.env.dbname, "-i", "-s", "1",
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=180)
        if result.returncode != 0 and "already exists" not in (result.stderr + result.stdout).lower():
            raise RuntimeError(f"pgbench initialization failed: {result.stderr.strip()}")

    def _setup_schema(self) -> None:
        self._verify_tpcds_working_set()
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.outcome_table} CASCADE; DROP TABLE IF EXISTS {self.observations_table} CASCADE; DROP TABLE IF EXISTS {self.context_observations_table} CASCADE; DROP TABLE IF EXISTS {self.phase_observations_table} CASCADE; DROP TABLE IF EXISTS {self.call_history_table} CASCADE; DROP TABLE IF EXISTS {self.jobs_table} CASCADE; DROP TABLE IF EXISTS {self.control_table} CASCADE; DROP TABLE IF EXISTS ops_vacuum_noise CASCADE;")
        self.env.execute_sql(f"""
            CREATE TABLE {self.control_table} (
                control_name text PRIMARY KEY,
                requested_mode text NOT NULL CHECK (requested_mode IN ({', '.join(self._literal(mode) for mode in sorted(CONTROL_MODES | {'observe'}))})),
                target_application text NOT NULL DEFAULT 'unspecified',
                target_queryid bigint,
                requested_at timestamptz NOT NULL DEFAULT clock_timestamp(),
                CHECK (target_application = 'unspecified' OR target_application ~ '^[a-z][a-z0-9_-]{{0,62}}$')
            );
            CREATE TABLE {self.jobs_table} (
                run_id text NOT NULL,
                job_name text NOT NULL,
                required boolean NOT NULL,
                status text NOT NULL DEFAULT 'planned',
                deadline_at timestamptz NOT NULL,
                started_at timestamptz,
                completed_at timestamptz,
                result_checksum text,
                expected_checksum text NOT NULL,
                error text,
                PRIMARY KEY (run_id, job_name)
            );
            CREATE TABLE {self.observations_table} (
                observed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
                window_name text NOT NULL,
                bucket_application text NOT NULL,
                bucket_queryid bigint,
                query_calls_delta bigint NOT NULL,
                query_shared_blks_read_delta bigint NOT NULL,
                query_exec_ms_delta double precision NOT NULL,
                oltp_p99_ms double precision,
                oltp_slo_violations bigint NOT NULL
            );
            CREATE TABLE {self.context_observations_table} (
                observed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
                window_name text NOT NULL,
                context_reads_delta bigint NOT NULL,
                context_read_time_ms_delta double precision NOT NULL,
                context_hits_delta bigint NOT NULL,
                device_io_in_progress bigint NOT NULL,
                device_weighted_io_ms_delta bigint NOT NULL
            );
            CREATE TABLE {self.phase_observations_table} (
                phase_started_at timestamptz NOT NULL,
                phase_finished_at timestamptz NOT NULL,
                window_name text NOT NULL,
                bucket_application text NOT NULL,
                bucket_queryid bigint,
                scan_count bigint NOT NULL,
                query_calls_delta bigint NOT NULL,
                query_shared_blks_read_delta bigint NOT NULL,
                query_exec_ms_delta double precision NOT NULL,
                context_reads_delta bigint NOT NULL,
                context_read_time_ms_delta double precision NOT NULL,
                context_hits_delta bigint NOT NULL,
                device_io_in_progress bigint NOT NULL,
                device_weighted_io_ms_delta bigint NOT NULL
            );
            CREATE TABLE {self.call_history_table} (
                call_id bigserial PRIMARY KEY,
                phase_started_at timestamptz NOT NULL,
                phase_finished_at timestamptz NOT NULL,
                window_name text NOT NULL,
                application_name text NOT NULL,
                queryid bigint,
                anchor_date date NOT NULL,
                window_days integer NOT NULL CHECK (window_days > 0),
                duration_ms double precision NOT NULL,
                call_role text NOT NULL CHECK (call_role IN ('baseline', 'batch'))
            );
            CREATE TABLE {self.outcome_table} (
                run_id text PRIMARY KEY,
                target_workload_controlled boolean NOT NULL DEFAULT false,
                report_pressure_recovered boolean NOT NULL DEFAULT false,
                oltp_slo_pass boolean NOT NULL DEFAULT false,
                required_jobs_completed boolean NOT NULL DEFAULT false,
                required_jobs_checksum_ok boolean NOT NULL DEFAULT false,
                required_jobs_deadline_ok boolean NOT NULL DEFAULT false,
                target_job_status text NOT NULL DEFAULT 'planned',
                worst_oltp_p99_ms double precision,
                updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
            );
            CREATE TABLE ops_vacuum_noise (
                id bigint PRIMARY KEY,
                payload text NOT NULL
            ) WITH (
                autovacuum_enabled = true,
                autovacuum_vacuum_scale_factor = 0,
                autovacuum_vacuum_threshold = 50
            );
            INSERT INTO ops_vacuum_noise(id, payload)
            SELECT id, repeat('v', 64) FROM generate_series(1, 5000) AS id;
        """)
        self._ensure_report_routine()
        self._seed_run_state()

    def _ensure_report_routine(self) -> None:
        """Expose parameterized report slices through a shared routine boundary."""
        routine_body = self._parameterized_report_sql(self.report_sql).replace("$routine$", "$$routine$$")
        sql = f"""
            DROP FUNCTION IF EXISTS public.{self.report_routine}(date, integer);
            CREATE FUNCTION public.{self.report_routine}(anchor_date date, window_days integer)
            RETURNS TABLE(channel text, id integer, sales numeric, returns numeric, profit numeric)
            LANGUAGE SQL
            AS $routine${routine_body}$routine$;
        """
        _require_sql_success(self.env.execute_sql(sql), "create PG-RG-IO01 report routine")

    @staticmethod
    def _parameterized_report_sql(report_sql: str) -> str:
        return (
            report_sql
            .replace("(cast('2001-08-11' as date) + interval '30 days')", "($1 + make_interval(days => $2))")
            .replace("cast('2001-08-11' as date)", "$1")
        )

    def _seed_run_state(self) -> None:
        deadline = f"clock_timestamp() + interval '{self.deadline_seconds} seconds'"
        job_rows = []
        self._job_checksums = {}
        for job_name in self.required_job_names:
            checksum = self._checksum_for_job(job_name)
            self._job_checksums[job_name] = checksum
            job_rows.append(
                f"({self._literal(self.run_id)}, {self._literal(job_name)}, true, {deadline}, {self._literal(checksum)})"
            )
        self.env.execute_sql(
            f"INSERT INTO {self.jobs_table}(run_id, job_name, required, deadline_at, expected_checksum) VALUES "
            + ",".join(job_rows)
            + f"; INSERT INTO {self.outcome_table}(run_id) VALUES ({self._literal(self.run_id)}); "
            + f"INSERT INTO {self.control_table}(control_name, requested_mode) VALUES ({self._literal(CONTROL_NAME)}, 'observe');"
        )

    def _verify_tpcds_working_set(self) -> None:
        payload = _json_object(self.env.execute_sql(
            f"SELECT to_regclass('public.{self.report_relation}')::text, pg_relation_size('{self.report_relation}');"
        ), "verify PG-RG-IO01 TPC-DS report relation")
        relation, size = payload["result"][0]
        if relation != self.report_relation or int(size) <= self.report_working_set_bytes:
            raise RuntimeError(
                f"TPC-DS report relation is not larger than effective working set: "
                f"relation={relation!r}, bytes={size}, required_gt={self.report_working_set_bytes}"
            )

    def _verify_persistent_state(self) -> None:
        payload = _json_object(self.env.execute_sql(
            "SELECT count(*) FROM pg_class c "
            "JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE n.nspname = 'public' AND c.relkind IN ('r', 'p') "
            f"AND c.relname IN ({', '.join(self._literal(name) for name in (self.control_table, self.jobs_table, self.observations_table, self.context_observations_table, self.phase_observations_table, self.call_history_table, self.outcome_table, 'ops_vacuum_noise'))});"
        ), "verify PG-RG-IO01 fault image")
        if int(payload["result"][0][0]) != 8:
            raise RuntimeError("PG-RG-IO01 fault image does not contain the persistent scenario tables")
        self._verify_tpcds_working_set()
        self._ensure_report_routine()

    def _reset_run_state(self) -> None:
        """Replace snapshot-local rows so a reused image gets a fresh CaseRun contract."""
        _require_sql_success(
            self.env.execute_sql(
                f"DELETE FROM {self.outcome_table}; "
                f"DELETE FROM {self.observations_table}; "
                f"DELETE FROM {self.context_observations_table}; "
                f"DELETE FROM {self.phase_observations_table}; "
                f"DELETE FROM {self.call_history_table}; "
                f"DELETE FROM {self.jobs_table}; "
                f"DELETE FROM {self.control_table}; "
                "UPDATE ops_vacuum_noise SET payload = repeat('v', 64);"
            ),
            "reset PG-RG-IO01 run state",
        )
        self._seed_run_state()

    def _checksum_for_job(self, job_name: str) -> str:
        cached = self._job_checksums.get(job_name)
        if cached is not None:
            return cached
        rows = self._direct_rows(self._checksum_sql(job_name))
        if len(rows) != 1 or len(rows[0]) != 1:
            raise RuntimeError(f"checksum {job_name} did not return one scalar: rows={rows!r}")
        return str(rows[0][0])

    def _checksum_sql(self, job_name: str) -> str:
        # Required jobs are all replicas of the same reporting contract.  A
        # backup/autovacuum/read decoy is real runtime activity, but it is not
        # inserted into this business-job ledger.  Keeping the checksum
        # identical across report replicas prevents the ledger from naming
        # the causal source through job type or result shape.
        return (
            "SELECT md5(count(*)::text || ':' || "
            "coalesce(sum(pg_column_size(row_to_json(r))), 0)::text) "
            f"FROM (SELECT * FROM public.{self.report_routine}(DATE '2001-08-11', 30)) AS r;"
        )

    def _report_call_sql(self) -> str:
        return REPORT_ROUTINE_CALL_SQL

    def _direct_report_call_sql(self) -> str:
        """Run the routine's real SQL body from another business owner.

        The direct caller uses the same PostgreSQL parameterized query family as
        the routine body. Its application identity is therefore observable but
        cannot be recovered from a queryid alone.
        """
        return (
            self._parameterized_report_sql(self.report_sql)
            .replace("$1", "%(anchor_date)s::date")
            .replace("$2", "%(window_days)s::integer")
        )

    def _report_call_params(self, application_name: str) -> tuple[str, int]:
        return REPORT_CALL_PROFILES.get(application_name, REPORT_CALL_PROFILES["worker-2"])

    def _record_report_call(
        self,
        application_name: str,
        started_at: object,
        finished_at: object,
        duration_ms: float,
    ) -> None:
        queryid = self._queryid_for_application(application_name)
        anchor_date, window_days = self._report_call_params(application_name)
        # The ledger records execution stage, not the injector's hidden causal
        # label. Every source in the shared query family is a normal batch call.
        role = "baseline" if self._current_window == "window_0" else "batch"
        self._direct_execute(
            f"INSERT INTO {self.call_history_table}(phase_started_at, phase_finished_at, window_name, application_name, queryid, anchor_date, window_days, duration_ms, call_role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                started_at,
                finished_at,
                self._current_window,
                application_name,
                queryid,
                anchor_date,
                window_days,
                duration_ms,
                role,
            ),
        )

    def _execute_report_call(self, cursor, application_name: str, call_mode: str = "routine") -> None:
        anchor_date, window_days = self._report_call_params(application_name)
        cursor.execute(
            "SELECT set_config('ops.report_anchor', %s, false), "
            "set_config('ops.report_window_days', %s, false)",
            (anchor_date, str(window_days)),
        )
        started_at = self._direct_rows("SELECT clock_timestamp();")[0][0]
        started = time.monotonic()
        if call_mode == "direct_sql":
            cursor.execute(
                self._direct_report_call_sql(),
                {"anchor_date": anchor_date, "window_days": window_days},
            )
        else:
            cursor.execute(self._report_call_sql(), self._report_call_params(application_name))
        cursor.fetchall()
        finished_at = self._direct_rows("SELECT clock_timestamp();")[0][0]
        self._record_report_call(application_name, started_at, finished_at, (time.monotonic() - started) * 1000)

    def _start_runtime(self) -> None:
        self._stop.clear()
        # Keep the pre-impact comparison in its own visible phase.  The
        # causal report/OLTP phase starts only after all bounded scans finish.
        self._current_window = "window_0"
        self._observer_error = None
        self._report_controlled = False
        self._bucket_snapshots = {}
        self._scan_decoy_ready.clear()
        self._scan_decoy_error = None
        cohort_size = 1 + len(self.interference_app_names)
        self._required_cohort_barrier = (
            threading.Barrier(cohort_size) if self.synchronize_required_cohort and cohort_size > 1 else None
        )
        self._monitor = _IoContextMonitor(self.monitoring_port)
        self._monitor.start()
        observer = threading.Thread(target=self._observation_loop, daemon=True, name="pg-io-context-observer")
        report = threading.Thread(target=self._report_loop, daemon=True, name="pg-io-context-report")
        oltp = threading.Thread(target=self._oltp_loop, daemon=True, name="pg-io-context-oltp")
        scan_threads = []
        workload_threads = [report, oltp]
        prework_threads = []
        prework_job_names = []
        for index, (app_name, decoy_type, job_name) in enumerate(zip(self.decoy_app_names, self.decoy_types, self.decoy_job_names)):
            target = {
                "backup": self._backup_loop,
                "read_decoy": self._read_decoy_loop,
                "scan_decoy": self._scan_decoy_loop,
            }.get(decoy_type, self._vacuum_loop)
            thread = threading.Thread(target=target, args=(app_name, index, decoy_type, job_name), daemon=True, name=f"pg-io-context-decoy-{index}")
            if decoy_type == "scan_decoy":
                scan_threads.append(thread)
            elif decoy_type == "backup":
                # The base archive is a real, required read workload, but it is
                # a pre-impact decoy. Complete it before the causal batch and
                # OLTP probe start so it cannot become a second root cause.
                prework_threads.append(thread)
                if job_name:
                    prework_job_names.append(job_name)
            else:
                workload_threads.append(thread)
        for index, (app_name, job_name, call_mode) in enumerate(
            zip(self.interference_app_names, self.interference_job_names, self.interference_call_modes),
            start=len(self.decoy_app_names),
        ):
            thread = threading.Thread(
                target=self._read_decoy_loop,
                args=(app_name, index, call_mode, job_name),
                daemon=True,
                name=f"pg-io-context-interference-{index}",
            )
            workload_threads.append(thread)
        self._threads = [observer, *scan_threads, *prework_threads, *workload_threads]
        observer.start()
        for thread in scan_threads:
            thread.start()
        if scan_threads and not self._scan_decoy_ready.wait(timeout=max(120, self.deadline_seconds - 30)):
            raise RuntimeError("PG-RG-IO01 bounded scan decoy did not finish before workload start")
        if self._scan_decoy_error is not None:
            raise RuntimeError(f"PG-RG-IO01 bounded scan decoy failed before workload start: {self._scan_decoy_error}")
        for thread in prework_threads:
            thread.start()
        prework_timeout = max(60, self.deadline_seconds - 60)
        for thread in prework_threads:
            thread.join(timeout=prework_timeout)
            if thread.is_alive():
                raise RuntimeError("PG-RG-IO01 required pre-impact archive did not finish before workload start")
        if prework_threads:
            for job_name in prework_job_names:
                rows = self._direct_rows(
                    f"SELECT status FROM {self.jobs_table} WHERE run_id = {self._literal(self.run_id)} AND job_name = {self._literal(job_name)};"
                )
                if not rows or str(rows[0][0]) != "completed":
                    raise RuntimeError(f"PG-RG-IO01 required pre-impact job did not complete: job={job_name!r}, rows={rows!r}")
        self._current_window = "report_window_1"
        for thread in workload_threads:
            thread.start()
        self._start_pgbench()
        self._wait_fault_ready()

    def _start_pgbench(self) -> None:
        if not self._container_name:
            return
        command = [
            "docker", "exec", "-e", f"PGPASSWORD={self.env.password}", self._container_name,
            "pgbench", "-h", "127.0.0.1", "-p", "5432", "-U", self.env.user,
            "-d", self.env.dbname, "-c", "1", "-j", "1", "-N", "-T", str(max(self.deadline_seconds, 60)),
            "-P", "5", "--latency-limit", str(int(self.oltp_slo_p99_ms)),
        ]
        self._pgbench_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    def _wait_fault_ready(self) -> None:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if self.fault_ready(None):
                return
            time.sleep(0.25)
        latest = self._monitor.latest() if self._monitor else {}
        raise RuntimeError(
            "PG-RG-IO01 report workload did not become observable: "
            f"observer_error={self._observer_error!r}, monitor={latest!r}"
        )

    def fault_ready(self, _context: FaultLifecycleContext | None) -> bool:
        """Return whether the causal report and independent monitor are live."""
        try:
            payload = _json_object(self.env.execute_sql(
                f"SELECT (SELECT count(*) FROM pg_stat_activity WHERE application_name = {self._literal(self.report_app_name)} AND state = 'active'), "
                f"(SELECT count(*) FROM {self.observations_table} WHERE bucket_application = {self._literal(self.report_app_name)});"
            ), "check PG-RG-IO01 readiness")
            latest = self._monitor.latest() if self._monitor else {}
            active_count, observed_count = payload["result"][0]
            return (int(active_count) > 0 or int(observed_count) > 0) and latest.get("status") == "success"
        except Exception:
            return False

    def _connect(self, application_name: str):
        import psycopg2

        connection = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=5,
            application_name=application_name,
        )
        connection.autocommit = True
        self._connections.append(connection)
        return connection

    def _control_mode(self) -> str | None:
        rows = self._direct_rows(
            f"SELECT requested_mode FROM {self.control_table} WHERE control_name = {self._literal(CONTROL_NAME)};"
        )
        return str(rows[0][0]).lower() if rows else None

    def _control_applies(self, application_name: str) -> bool:
        """A shared queryid is a family hint, not a sufficient target selector."""
        rows = self._direct_rows(
            f"SELECT requested_mode, target_application FROM {self.control_table} "
            f"WHERE control_name = {self._literal(CONTROL_NAME)};"
        )
        if not rows or str(rows[0][0]).lower() not in CONTROL_MODES:
            return False
        target_application = str(rows[0][1] or "unspecified").lower()
        return target_application == application_name.casefold()

    def _direct_rows(self, sql: str, params: tuple[object, ...] = ()) -> list:
        connection = self._connect("pg-io-context-control")
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall() if cursor.description else []
        finally:
            connection.close()

    def _direct_execute(self, sql: str, params: tuple[object, ...] = ()) -> None:
        connection = self._connect("pg-io-context-control")
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
            connection.commit()
        finally:
            connection.close()

    def _report_loop(self) -> None:
        connection = None
        report_executed = False
        cohort_waited = False
        try:
            connection = self._connect(self.report_app_name)
            with connection.cursor() as cursor:
                cursor.execute("SET statement_timeout = '0'")
                self._mark_job_started(self.target_job_name)
                for window in range(1, self.report_window_count + 1):
                    self._current_window = f"report_window_{window}"
                    if self._control_applies(self.report_app_name):
                        self._report_controlled = True
                        self._reset_oltp_slo_window()
                        if not report_executed:
                            cursor.execute("SELECT pg_sleep(0.25)")
                            self._execute_report_call(cursor, self.report_app_name)
                            report_executed = True
                        if not cohort_waited:
                            self._wait_for_required_cohort()
                            cohort_waited = True
                        self._mark_job_completed(self.target_job_name, self._checksum_for_job(self.target_job_name))
                        return
                    self._execute_report_call(cursor, self.report_app_name)
                    report_executed = True
                    if not cohort_waited:
                        self._wait_for_required_cohort()
                        cohort_waited = True
                    if self._stop.is_set():
                        return
                    # Keep the report windows bounded and repeatable.
                    self._stop.wait(0.25)
                if self.synchronize_required_cohort:
                    # A finite scheduler submission is a real completed job;
                    # workload control is a separate business policy state.
                    control_deadline = time.monotonic() + self.deadline_seconds
                    while not self._stop.is_set() and time.monotonic() < control_deadline:
                        if self._control_applies(self.report_app_name):
                            self._report_controlled = True
                            self._reset_oltp_slo_window()
                            if not cohort_waited:
                                self._wait_for_required_cohort()
                                cohort_waited = True
                            self._mark_job_completed(self.target_job_name, self._checksum_for_job(self.target_job_name))
                            return
                        self._stop.wait(0.25)
                    if not self._stop.is_set():
                        self._mark_job_failed(
                            self.target_job_name,
                            "target workload control was not observed before the published deadline",
                        )
                    return
            while not self._stop.is_set():
                if self._control_applies(self.report_app_name):
                    self._report_controlled = True
                    with self._state_lock:
                        self._oltp_latencies.clear()
                        self._oltp_violations = 0
                    if not report_executed:
                        cursor.execute("SELECT pg_sleep(0.25)")
                        self._execute_report_call(cursor, self.report_app_name)
                        report_executed = True
                    if not cohort_waited:
                        self._wait_for_required_cohort()
                        cohort_waited = True
                    self._mark_job_completed(self.target_job_name, self._checksum_for_job(self.target_job_name))
                    return
                self._stop.wait(0.25)
        except Exception as exc:
            if not self._stop.is_set():
                self._mark_job_failed(self.target_job_name, str(exc))
        finally:
            if connection is not None:
                connection.close()

    def _oltp_loop(self) -> None:
        connection = None
        try:
            connection = self._connect("pgbench-oltp-probe")
            with connection.cursor() as cursor:
                while not self._stop.is_set():
                    started = time.monotonic()
                    aid = int(time.time() * 1000) % 100000 + 1
                    cursor.execute("SELECT abalance FROM pgbench_accounts WHERE aid = %s", (aid,))
                    cursor.execute("UPDATE pgbench_accounts SET abalance = abalance + 1 WHERE aid = %s", (aid,))
                    elapsed = (time.monotonic() - started) * 1000
                    with self._state_lock:
                        self._oltp_latencies.append(elapsed)
                        # Keep a recent, bounded SLO window.  A shorter window is
                        # still large enough for a p99 sample while allowing the
                        # post-control state to converge after a required decoy
                        # has finished.
                        self._oltp_latencies = self._oltp_latencies[-40:]
                        if elapsed > self.oltp_slo_p99_ms:
                            self._oltp_violations += 1
                    time.sleep(0.05)
        except Exception as exc:
            return
        finally:
            if connection is not None:
                connection.close()

    def _backup_loop(self, application_name: str, _index: int, _decoy_type: str, job_name: str) -> None:
        if not job_name:
            # The backup is a real infrastructure workload, but the
            # required ledger is intentionally homogeneous report jobs. Do
            # not borrow a report job row for an unrelated backup.
            job_name = ""
        if job_name:
            self._mark_job_started(job_name)
        connection = None
        try:
            connection = self._connect(application_name)
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_current_wal_lsn()::text, count(*) "
                    "FROM pg_class WHERE relkind IN ('r', 'p', 'i')"
                )
                cursor.fetchone()
                cursor.execute("SELECT pg_sleep(0.25)")
            if job_name:
                self._mark_job_completed(job_name, self._checksum_for_job(job_name))
        except Exception as exc:
            if job_name and not self._stop.is_set():
                self._mark_job_failed(job_name, str(exc))
        finally:
            if connection is not None:
                connection.close()

    def _vacuum_loop(self, application_name: str, _index: int, decoy_type: str, job_name: str) -> None:
        if not job_name:
            # Autovacuum/VACUUM remains observable runtime interference; it is
            # not a required report replica and must not claim one else's row.
            job_name = ""
        if job_name:
            self._mark_job_started(job_name)
        connection = None
        try:
            if decoy_type == "autovacuum":
                started_at = time.time()
                self._direct_execute(
                    "UPDATE ops_vacuum_noise "
                    "SET payload = payload || 'x' WHERE id %% 2 = 0"
                )
                deadline = time.monotonic() + min(self.deadline_seconds, 120)
                while not self._stop.is_set() and time.monotonic() < deadline:
                    rows = self._direct_rows(
                        "SELECT last_autovacuum, autovacuum_count "
                        "FROM pg_stat_user_tables "
                        "WHERE relname = 'ops_vacuum_noise'"
                    )
                    if rows and rows[0][0] is not None and rows[0][0].timestamp() >= started_at and int(rows[0][1]) > 0:
                        if job_name:
                            self._mark_job_completed(job_name, self._checksum_for_job(job_name))
                        return
                    self._stop.wait(1.0)
                if not self._stop.is_set():
                    if job_name:
                        self._mark_job_failed(job_name, "autovacuum worker did not complete before the decoy deadline")
                return
            connection = self._connect(application_name)
            with connection.cursor() as cursor:
                cursor.execute("VACUUM (ANALYZE) ops_vacuum_noise")
            if job_name:
                self._mark_job_completed(job_name, self._checksum_for_job(job_name))
        except Exception as exc:
            if job_name and not self._stop.is_set():
                self._mark_job_failed(job_name, str(exc))
        finally:
            if connection is not None:
                connection.close()

    def _read_decoy_loop(self, application_name: str, _index: int, call_mode: str, job_name: str) -> None:
        """Run finite, real slices from the same query family as candidate history."""
        connection = None
        try:
            connection = self._connect(application_name)
            with connection.cursor() as cursor:
                if job_name:
                    self._mark_job_started(job_name)
                # Keep several real candidate sources active with the target
                # during the first causal window. They share the normalized
                # call but use distinct session-context slices.
                for _ in range(self.report_window_count):
                    if self._stop.is_set():
                        return
                    self._execute_report_call(cursor, application_name, call_mode)
                    # Scheduler replicas keep the same bounded cadence as the
                    # causal report.  This makes their active/job intervals a
                    # genuine concurrent workload cohort, not a short-lived
                    # synthetic read spike.
                    if not self._stop.wait(0.25):
                        continue
                if job_name:
                    self._wait_for_required_cohort()
                    self._mark_job_completed(job_name, self._checksum_for_job(job_name))
        except Exception as exc:
            if job_name and not self._stop.is_set():
                self._mark_job_failed(job_name, str(exc))
            return
        finally:
            if connection is not None:
                connection.close()

    def _wait_for_required_cohort(self) -> None:
        barrier = self._required_cohort_barrier
        if barrier is None:
            return
        try:
            barrier.wait(timeout=max(60, self.deadline_seconds - 60))
        except threading.BrokenBarrierError as exc:
            raise RuntimeError("PG-RG-IO01 required report cohort did not converge") from exc

    def _scan_decoy_loop(self, application_name: str, _index: int, _decoy_type: str, job_name: str) -> None:
        """Run bounded, report-shaped scans before OLTP and causal pressure start."""
        connection = None
        try:
            connection = self._connect(application_name)
            if job_name:
                self._mark_job_started(job_name)
            phase_started_at = self._direct_rows("SELECT clock_timestamp();")[0][0]
            statement_before = self._report_statement_snapshot()
            context_before = self._context_snapshot()
            observed_queryid = None
            with connection.cursor() as cursor:
                # This is intentionally the same report query shape as the
                # causal worker.  It is a healthy pre-impact comparison: it
                # creates real read evidence but runs before OLTP starts and
                # does not create a second business-SLO failure.
                scan_count = 1
                for _ in range(scan_count):
                    query_done = threading.Event()
                    query_error: list[BaseException] = []

                    def execute_scan() -> None:
                        try:
                            self._execute_report_call(cursor, application_name)
                        except BaseException as exc:  # propagate the real worker error
                            query_error.append(exc)
                        finally:
                            query_done.set()

                    query_thread = threading.Thread(target=execute_scan, daemon=True)
                    query_thread.start()
                    while not query_done.wait(0.25):
                        if observed_queryid is None:
                            observed_queryid = self._queryid_for_application(application_name)
                    query_thread.join()
                    if query_error:
                        raise query_error[0]
                    if self._stop.is_set():
                        return
            phase_finished_at = self._direct_rows("SELECT clock_timestamp();")[0][0]
            if observed_queryid is None:
                observed_queryid = self._queryid_for_application(application_name)
            statement_after = self._report_statement_snapshot(observed_queryid)
            context_after = self._context_snapshot()
            disk_after = self._read_diskstats()
            statement_delta = self._bucket_delta(statement_before, statement_after)
            context_delta = self._delta(context_before, context_after)
            if not context_before:
                context_delta = (0, 0.0, 0, (0, 0))
            disk_delta = tuple(max(0, disk_after[index] - context_before[3][index]) for index in range(2))
            self._direct_execute(
                f"INSERT INTO {self.phase_observations_table}(phase_started_at, phase_finished_at, window_name, bucket_application, bucket_queryid, scan_count, query_calls_delta, query_shared_blks_read_delta, query_exec_ms_delta, context_reads_delta, context_read_time_ms_delta, context_hits_delta, device_io_in_progress, device_weighted_io_ms_delta) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (phase_started_at, phase_finished_at, "window_0", application_name, observed_queryid, scan_count,
                 statement_delta[0], statement_delta[1], statement_delta[2], context_delta[0], context_delta[1],
                 context_delta[2], disk_after[0], disk_delta[1]),
            )
            if job_name:
                self._mark_job_completed(job_name, self._checksum_for_job(job_name))
        except Exception as exc:
            self._scan_decoy_error = (
                f"{type(exc).__name__}: {exc}; "
                f"traceback={traceback.format_exc(limit=6)}"
            )
            if job_name and not self._stop.is_set():
                self._mark_job_failed(job_name, str(exc))
        finally:
            self._scan_decoy_ready.set()
            if connection is not None:
                connection.close()

    def _queryid_for_application(self, application_name: str) -> int | None:
        rows = self._direct_rows(
            "SELECT query_id FROM pg_stat_activity "
            "WHERE application_name = %s AND state = 'active' AND query_id IS NOT NULL "
            "ORDER BY query_start DESC LIMIT 1",
            (application_name,),
        )
        if rows and rows[0][0] is not None:
            return int(rows[0][0])
        rows = self._direct_rows(
            "SELECT queryid FROM pg_stat_statements "
            "WHERE query LIKE %s "
            "ORDER BY calls DESC LIMIT 1",
            (f"SELECT * FROM public.{self.report_routine}(%",),
        )
        return None if not rows or rows[0][0] is None else int(rows[0][0])

    def _report_statement_snapshot(self, queryid: int | None = None) -> tuple[int, int, float]:
        if queryid is not None:
            sql = (
                "SELECT coalesce(sum(calls), 0), coalesce(sum(shared_blks_read), 0), "
                "coalesce(sum(total_exec_time), 0) FROM pg_stat_statements WHERE queryid = %s"
            )
            params = (queryid,)
        else:
            sql = (
                "SELECT coalesce(sum(calls), 0), coalesce(sum(shared_blks_read), 0), "
                "coalesce(sum(total_exec_time), 0) FROM pg_stat_statements "
                "WHERE query LIKE %s"
            )
            params = (f"SELECT * FROM public.{self.report_routine}(%",)
        rows = self._direct_rows(
            sql,
            params,
        )
        return tuple(rows[0]) if rows else (0, 0, 0.0)

    def _context_snapshot(self) -> tuple[int, float, int, tuple[int, int]]:
        rows = self._direct_rows(
            "SELECT coalesce(sum(reads), 0), coalesce(sum(read_time), 0), coalesce(sum(hits), 0) "
            "FROM pg_stat_io WHERE object = 'relation' AND context = 'bulkread'"
        )
        values = tuple(rows[0]) if rows else (0, 0.0, 0)
        return int(values[0]), float(values[1]), int(values[2]), self._read_diskstats()

    def _observation_loop(self) -> None:
        connection = None
        previous = None
        try:
            connection = self._connect("pg-io-context-observer")
            application_filter = ", ".join(
                self._literal(name)
                for name in (*self.decoy_app_names, *self.interference_app_names, self.report_app_name, "pgbench-oltp-probe")
            )
            while not self._stop.is_set():
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT coalesce(sum(reads), 0), coalesce(sum(read_time), 0),
                               coalesce(sum(hits), 0)
                        FROM pg_stat_io
                        WHERE object = 'relation' AND context = 'bulkread'
                    """)
                    io_reads, io_read_time, io_hits = cursor.fetchone()
                    cursor.execute(f"""
                        SELECT a.application_name, a.query_id,
                               coalesce(sum(s.calls), 0),
                               coalesce(sum(s.shared_blks_read), 0),
                               coalesce(sum(s.total_exec_time), 0)
                        FROM pg_stat_activity AS a
                        LEFT JOIN pg_stat_statements AS s ON s.queryid = a.query_id
                        WHERE a.application_name IN ({application_filter})
                        GROUP BY a.application_name, a.query_id
                    """)
                    bucket_rows = cursor.fetchall()
                disk = self._read_diskstats()
                current = (int(io_reads or 0), float(io_read_time or 0), int(io_hits or 0), disk)
                delta = self._delta(previous, current)
                previous = current
                with self._state_lock:
                    latencies = sorted(self._oltp_latencies)
                    p99 = latencies[min(len(latencies) - 1, int(len(latencies) * 0.99))] if latencies else None
                    violations = self._oltp_violations
                bucket_deltas = []
                for app_name, queryid, calls, shared_reads, exec_ms in bucket_rows:
                    key = (str(app_name), int(queryid) if queryid is not None else None)
                    bucket_current = (int(calls or 0), int(shared_reads or 0), float(exec_ms or 0))
                    bucket_previous = self._bucket_snapshots.get(key)
                    self._bucket_snapshots[key] = bucket_current
                    bucket_delta = self._bucket_delta(bucket_previous, bucket_current)
                    bucket_deltas.append((key[0], key[1], bucket_delta))
                if not bucket_deltas:
                    bucket_deltas.append(("pg-io-context-aggregate", None, (0, 0, 0.0)))
                bucket_aggregate = tuple(
                    sum(item[2][index] for item in bucket_deltas)
                    for index in range(3)
                )
                for app_name, queryid, bucket_delta in bucket_deltas:
                    insert_cursor = connection.cursor()
                    insert_cursor.execute(
                        f"INSERT INTO {self.observations_table}(window_name, bucket_application, bucket_queryid, query_calls_delta, query_shared_blks_read_delta, query_exec_ms_delta, oltp_p99_ms, oltp_slo_violations) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (self._current_window, app_name, queryid, bucket_delta[0], bucket_delta[1], bucket_delta[2], p99, violations),
                    )
                    insert_cursor.close()
                context_cursor = connection.cursor()
                context_cursor.execute(
                    f"INSERT INTO {self.context_observations_table}(window_name, context_reads_delta, context_read_time_ms_delta, context_hits_delta, device_io_in_progress, device_weighted_io_ms_delta) VALUES (%s, %s, %s, %s, %s, %s)",
                    (self._current_window, delta[0], delta[1], delta[2], disk[0], delta[3][1]),
                )
                context_cursor.close()
                connection.commit()
                if self._monitor:
                    self._monitor.publish({
                        "status": "success",
                        "observed_at": time.time(),
                        "window": self._current_window,
                        "pg_stat_io_context": {"context": "bulkread", "reads_delta": delta[0], "read_time_ms_delta": delta[1], "hits_delta": delta[2]},
                        "query_bucket": {"calls_delta": bucket_aggregate[0], "shared_blks_read_delta": bucket_aggregate[1], "exec_ms_delta": bucket_aggregate[2]},
                        "device": {"io_in_progress": disk[0], "weighted_io_ms_delta": delta[3][1]},
                        "oltp_p99_ms": p99,
                        "oltp_slo_violations": violations,
                    })
                self._refresh_outcome()
                self._stop.wait(1.0)
        except Exception as exc:
            self._observer_error = f"{type(exc).__name__}: {exc}"
            if self._monitor:
                self._monitor.publish({"status": "observer_error", "error": self._observer_error})
            return
        finally:
            if connection is not None:
                connection.close()

    @staticmethod
    def _delta(previous, current):
        if previous is None:
            return (0, 0.0, 0, (0, 0))
        return (
            *(max(0, current[index] - previous[index]) for index in range(3)),
            tuple(max(0, current[3][index] - previous[3][index]) for index in range(2)),
        )

    @staticmethod
    def _bucket_delta(previous, current):
        if previous is None:
            return (0, 0, 0.0)
        return tuple(max(0, current[index] - previous[index]) for index in range(3))

    @staticmethod
    def _read_diskstats() -> tuple[int, int]:
        in_progress = 0
        weighted_ms = 0
        try:
            with open("/proc/diskstats", encoding="utf-8") as stream:
                for line in stream:
                    fields = line.split()
                    if len(fields) < 14:
                        continue
                    in_progress += int(fields[11])
                    # Linux diskstats field 13 is weighted time in I/O. Field 12
                    # is only the time spent doing I/O and does not include queue
                    # wait accumulated across outstanding requests.
                    weighted_ms += int(fields[13])
        except (OSError, ValueError):
            pass
        return in_progress, weighted_ms

    def _mark_job_started(self, job_name: str) -> None:
        self._direct_execute(
            f"UPDATE {self.jobs_table} SET status = 'running', started_at = coalesce(started_at, clock_timestamp()) WHERE run_id = {self._literal(self.run_id)} AND job_name = {self._literal(job_name)} AND status = 'planned';"
        )

    def _mark_job_completed(self, job_name: str, checksum: str) -> None:
        self._direct_execute(
            f"UPDATE {self.jobs_table} SET status = 'completed', completed_at = clock_timestamp(), result_checksum = {self._literal(checksum)} WHERE run_id = {self._literal(self.run_id)} AND job_name = {self._literal(job_name)};"
        )
        if job_name != self.target_job_name:
            # Required decoys are allowed to create the initial pressure.  Once
            # one has finished, start a fresh bounded SLO window so the final
            # state measures steady service after that required job, while the
            # observation history still retains the violation timeline.
            self._reset_oltp_slo_window()
        else:
            # Start the final business window after the target report has
            # completed, so OP measures settled service rather than its I/O tail.
            self._reset_oltp_slo_window()
        self._refresh_outcome()

    def _mark_job_failed(self, job_name: str, error: str) -> None:
        self._direct_execute(
            f"UPDATE {self.jobs_table} SET status = 'failed', error = {self._literal(error[-500:])} WHERE run_id = {self._literal(self.run_id)} AND job_name = {self._literal(job_name)};"
        )

    def _refresh_outcome(self) -> None:
        try:
            mode = self._control_mode()
            with self._state_lock:
                latencies = sorted(self._oltp_latencies)
                p99 = latencies[min(len(latencies) - 1, int(len(latencies) * 0.99))] if latencies else None
                oltp_pass = (
                    len(latencies) >= 20
                    and p99 is not None
                    and p99 <= self.oltp_slo_p99_ms
                )
            rows = self._direct_rows(
                f"SELECT status, completed_at <= deadline_at, result_checksum = expected_checksum FROM {self.jobs_table} WHERE run_id = {self._literal(self.run_id)};"
            )
            complete = bool(rows) and all(str(row[0]) == "completed" for row in rows)
            deadlines = bool(rows) and all(bool(row[1]) for row in rows)
            checksums = bool(rows) and all(bool(row[2]) for row in rows)
            worst_oltp_p99_sql = "NULL" if p99 is None else str(float(p99))
            self._direct_execute(
                f"UPDATE {self.outcome_table} SET target_workload_controlled = {str(mode in CONTROL_MODES).lower()}, report_pressure_recovered = {str(self._report_controlled).lower()}, oltp_slo_pass = {str(oltp_pass).lower()}, required_jobs_completed = {str(complete).lower()}, required_jobs_checksum_ok = {str(checksums).lower()}, required_jobs_deadline_ok = {str(deadlines).lower()}, target_job_status = (SELECT status FROM {self.jobs_table} WHERE run_id = {self._literal(self.run_id)} AND job_name = {self._literal(self.target_job_name)}), worst_oltp_p99_ms = {worst_oltp_p99_sql}, updated_at = clock_timestamp() WHERE run_id = {self._literal(self.run_id)};"
            )
        except Exception:
            return

    def _reset_oltp_slo_window(self) -> None:
        with self._state_lock:
            self._oltp_latencies.clear()
            self._oltp_violations = 0

    def _stop_runtime(self) -> None:
        self._stop.set()
        for connection in list(self._connections):
            try:
                if not connection.closed:
                    connection.cancel()
            except Exception:
                pass
        if self._pgbench_process is not None:
            self._pgbench_process.terminate()
            try:
                self._pgbench_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._pgbench_process.kill()
            self._pgbench_process = None
        for process in list(self._backup_processes):
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        self._backup_processes = []
        started_threads = [thread for thread in self._threads if thread.ident is not None]
        for thread in started_threads:
            thread.join(timeout=8)
        alive = [thread.name for thread in started_threads if thread.is_alive()]
        if alive:
            # A backend in a filesystem wait may not observe cancel promptly. Closing the
            # owning client connection is the bounded second-stage shutdown path.
            for connection in list(self._connections):
                try:
                    if not connection.closed:
                        connection.close()
                except Exception:
                    pass
            for thread in started_threads:
                thread.join(timeout=8)
            alive = [thread.name for thread in started_threads if thread.is_alive()]
        self._threads = []
        if self._monitor is not None:
            self._monitor.stop()
            self._monitor = None
        for connection in list(self._connections):
            try:
                if not connection.closed:
                    connection.close()
            except Exception:
                pass
        self._connections = []
        self._stop.clear()
        if alive:
            raise RuntimeError(f"PG-RG-IO01 runtime threads did not stop: {alive}")


class PgResourceGovernanceIoContextWorkloadScenario(PostgresScenario):
    scenario_id = SCENARIO_ID
    description = "PG16 I/O context and workload buckets distinguish a causal batch worker from read-count noise."
    cases = (_HARD_CASE, _EASY_CASE)

    def build_fault_plan(self, case: PgResourceGovernanceIoContextWorkloadCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgResourceGovernanceIoContextWorkloadInjector,
                config={
                    "report_app_name": case.report_app_name,
                    "report_relation": case.report_relation,
                    "report_sql": case.report_sql,
                    "report_working_set_bytes": case.report_working_set_bytes,
                    "report_window_count": case.report_window_count,
                    "decoy_app_names": case.decoy_app_names,
                    "decoy_types": case.decoy_types,
                    "decoy_job_names": case.decoy_job_names,
                    "interference_app_names": case.interference_app_names,
                    "interference_job_names": case.interference_job_names,
                    "required_job_names": case.required_job_names,
                    "target_job_name": case.target_job_name,
                    "deadline_seconds": case.deadline_seconds,
                    "oltp_slo_p99_ms": case.oltp_slo_p99_ms,
                    "monitoring_port": case.monitoring_port,
                    "synchronize_required_cohort": case.synchronize_required_cohort,
                    "interference_call_modes": case.interference_call_modes or ("routine",) * len(case.interference_app_names),
                    "control_table": case.control_table,
                    "observations_table": case.observations_table,
                    "context_observations_table": case.context_observations_table,
                    "phase_observations_table": case.phase_observations_table,
                    "call_history_table": case.call_history_table,
                    "jobs_table": case.jobs_table,
                    "outcome_table": case.outcome_table,
                },
            ),
        )


__all__ = (
    "PgResourceGovernanceIoContextWorkloadCase",
    "PgResourceGovernanceIoContextWorkloadForReportIsPressureScenarioCase",
    "PgResourceGovernanceIoContextWorkloadForReportIsPressureSimpleScenarioCase",
    "PgResourceGovernanceIoContextWorkloadScenario",
    "PgResourceGovernanceIoContextWorkloadInjector",
)
