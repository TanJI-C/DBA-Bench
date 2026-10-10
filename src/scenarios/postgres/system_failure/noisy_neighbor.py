from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.postgres.system_failure import (
    PgSystemFailureAutoAnalyzeStormForSalesTablesAutoAnalyzeStormEvaluatorCase,
    PgSystemFailureAutoAnalyzeStormForStoreSalesAutoAnalyzeStormSimpleEvaluatorCase,
    PgSystemFailureConnectionStormForCheckoutPoolIdleTransactionStormEvaluatorCase,
    PgSystemFailureConnectionStormForCheckoutPoolLeakSimpleEvaluatorCase,
    PgSystemFailureDeadlockForCheckoutOrderDeadlockEvaluatorCase,
    PgSystemFailureDeadlockForSingleOrderPairDeadlockSimpleEvaluatorCase,
    PgSystemFailureFdExhaustionForNightlyReportingNofileExhaustionEvaluatorCase,
    PgSystemFailureFdExhaustionForReportExportFdExhaustionSimpleEvaluatorCase,
    PgSystemFailureIoCheckpointSpikesForCheckoutCheckpointSpikesEvaluatorCase,
    PgSystemFailureIoCheckpointSpikesForSingleCheckoutCheckpointSpikeSimpleEvaluatorCase,
    PgSystemFailureNoisyNeighborForWalArchiveCpuNeighborEvaluatorCase,
    PgSystemFailureNoisyNeighborForSingleArchiveCpuNeighborSimpleEvaluatorCase,
    PgSystemFailureOomForRestartMemoryConfigOomEvaluatorCase,
    PgSystemFailureOomForRestartSharedBuffersOomSimpleEvaluatorCase,
    PgSystemFailurePageCorruptionForOrderLineAuditPageCorruptionEvaluatorCase,
    PgSystemFailurePageCorruptionForInvoicePageCorruptionTriageSimpleEvaluatorCase,
    PgSystemFailureTempFileExplosionForNightlyMarginTempExhaustionEvaluatorCase,
    PgSystemFailureTempFileExplosionForDailySalesTempExhaustionSimpleEvaluatorCase,
    PgSystemFailureWalAccumulationForAnalyticsSlotWalRetentionEvaluatorCase,
    PgSystemFailureWalAccumulationForAbandonedReportSlotWalRetentionSimpleEvaluatorCase,
    PgSystemFailureXidWraparoundForPaymentLedgerXidWraparoundEvaluatorCase,
    PgSystemFailureXidWraparoundForBillingFreezeBlockedSimpleEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    PostgresCaseRuntime,
    PostgresScenario,
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    EMPTY_BACKGROUND_WORKLOAD,
    FaultPlan,
    CaseResourceSpec,
    PostgresRuntimeSpec,
    PostgresScenarioCase,
)

_DEFAULT_SYSTEM_FAILURE_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)

_OOM_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=256,
    container_cpu_limit=0.5,
    container_memory_mb=256,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureNoisyNeighborCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    table: str
    external_process_name: str
    safe_cpu_threshold: float
    probe_sql: str
    slow_queries: tuple[str, ...]
    worker_count: int
    noise_connections: int
    minimum_external_cpu_percent: float
    startup_timeout_seconds: float
    production_noise: bool
    # Extended candidates for single_archive_cpu_neighbor_simple. The
    # wal_archive_cpu_neighbor case keeps these disabled (None/0) so its
    # environment, injector behavior, and evaluator stay unchanged.
    protected_process_name: str | None = None
    protected_process_cycle_seconds: float = 0.0
    transient_process_name: str | None = None
    transient_start_delay_seconds: float = 0.0
    transient_runtime_seconds: float = 0.0
    job_registry_table: str = 'ops_maintenance_jobs'
    job_runs_table: str = 'ops_maintenance_job_runs'

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureNoisyNeighborForWalArchiveCpuNeighborScenarioCase(PgSystemFailureNoisyNeighborCase):
    pass

_PGSYSTEMFAILURENOISYNEIGHBORSCENARIO_CASE = PgSystemFailureNoisyNeighborForWalArchiveCpuNeighborScenarioCase(
    case_id='wal_archive_cpu_neighbor',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "postgres container cpu pressure",
                    "entity": "wal_archive_cpu_neighbor",
                    "evidence": [
                        "scripted diagnostic actions observed postgres container cpu pressure"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "database internal workload is normal",
                    "entity": "wal_archive_cpu_neighbor",
                    "evidence": [
                        "scripted diagnostic actions observed database internal workload is normal"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "wal archive external cpu neighbor",
                    "entity": "wal_archive_cpu_neighbor",
                    "evidence": [
                        "scripted diagnostic actions observed wal archive external cpu neighbor"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "terminate or isolate external process",
                    "entity": "wal_archive_cpu_neighbor",
                    "evidence": [
                        "scripted diagnostic actions observed terminate or isolate external process"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "applied the case-specific remediation"
            ],
            "verification": [
                "verified the case-specific final state"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgSystemFailureNoisyNeighborForWalArchiveCpuNeighborEvaluatorCase,
    runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Simulates CPU contention from an overrun WAL archive compression job.',
    alert='Alert: Checkout and order APIs are reporting a sustained throughput drop while PostgreSQL remains reachable. Dashboards show mixed signals: a few historical reporting queries, normal business connections, routine maintenance probes, and elevated host-level resource pressure. Identify the active cause and restore throughput without disrupting normal database work.',
    initial_state={'status': 'degraded',
 'symptom': 'throughput_drop',
 'database_internal_indicators': 'normal',
 'resource_layer': 'os_cpu_contention'},
    expected_target={'status': 'recovered',
 'external_process': 'terminated_or_isolated',
 'database_internal_indicators': 'normal',
 'cpu_pressure': 'reduced'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    table='orders_probe',
    external_process_name='wal_archive_compressor',
    safe_cpu_threshold=70.0,
    probe_sql="SET statement_timeout = '5s'; SELECT sum(amount) FROM orders_probe WHERE id BETWEEN 1 AND 1000;",
    slow_queries=("SET statement_timeout = '5s'; SELECT sum(amount) FROM orders_probe WHERE id BETWEEN 1 AND 1000;",),
    worker_count=2,
    noise_connections=14,
    minimum_external_cpu_percent=50.0,
    startup_timeout_seconds=15.0,
    production_noise=True,
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.5,
        reference_run_ids=(
            "reference-47__pg_system_failure_noisy_neighbor__"
            "wal_archive_cpu_neighbor__mock__r001",
        ),
    ),
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureNoisyNeighborForSingleArchiveCpuNeighborSimpleScenarioCase(PgSystemFailureNoisyNeighborCase):
    pass

_PGSYSTEMFAILURENOISYNEIGHBORSCENARIO_SIMPLE_CASE = (
    PgSystemFailureNoisyNeighborForSingleArchiveCpuNeighborSimpleScenarioCase(
        case_id='single_archive_cpu_neighbor_simple',
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "postgres container cpu pressure",
                        "entity": "single_archive_cpu_neighbor_simple",
                        "evidence": [
                            "scripted diagnostic actions observed postgres container cpu pressure"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "database internal workload is normal",
                        "entity": "single_archive_cpu_neighbor_simple",
                        "evidence": [
                            "scripted diagnostic actions observed database internal workload is normal"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "wal archive external cpu neighbor",
                        "entity": "single_archive_cpu_neighbor_simple",
                        "evidence": [
                            "scripted diagnostic actions observed wal archive external cpu neighbor"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "terminate or isolate external process",
                        "entity": "single_archive_cpu_neighbor_simple",
                        "evidence": [
                            "scripted diagnostic actions observed terminate or isolate external process"
                        ]
                    }
                ]
            },
            "outcome": {
                "changes": [
                    "applied the case-specific remediation"
                ],
                "verification": [
                    "verified the case-specific final state"
                ]
            },
            "summary": "The scripted mock completed its case-specific diagnosis and verification."
        },
        case_no=1,
        evaluator=PgSystemFailureNoisyNeighborForSingleArchiveCpuNeighborSimpleEvaluatorCase,
        runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
        difficulty=DifficultyCalibration(
            diagnostic_depth=4,
            environmental_complexity=0.565,
            reference_run_ids=(
                "reference-283__pg_system_failure_noisy_neighbor__single_archive_cpu_neighbor_simple__mock__r001",
            ),
        ),
        base_image_name='aiopsbench-pg-initialized:latest',
        workload_tag='initialized',
        title='A runaway WAL archive compression worker contends with PostgreSQL while scheduled maintenance jobs run.',
        alert=(
            'Alert: Order lookup throughput is persistently below baseline while PostgreSQL '
            'remains reachable. A low-rate database health probe is succeeding. Identify the '
            'active resource consumer and restore throughput without disrupting database work.'
        ),
        initial_state={
            'status': 'degraded',
            'symptom': 'order_lookup_throughput_drop',
            'database': 'reachable',
        },
        expected_target={
            'status': 'recovered',
            'external_process': 'terminated_or_isolated',
            'database_probe': 'healthy',
            'protected_maintenance': 'preserved',
            'scheduled_jobs': 'intact',
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=(
                WorkloadProfile(
                    name='order_lookup_health_probe',
                    sql='SELECT count(*) FROM orders_probe WHERE id BETWEEN 1 AND 100;',
                    qps=0.1,
                    tier='LIGHT',
                    application_name='order_lookup_health_probe',
                ),
            ),
            worker_count=1,
            seed=0x2F05,
            start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
            warmup_seconds=11,
        ),
        table='orders_probe',
        external_process_name='wal_archive_compressor',
        safe_cpu_threshold=70.0,
        probe_sql="SET statement_timeout = '5s'; SELECT count(*) FROM orders_probe WHERE id BETWEEN 1 AND 100;",
        slow_queries=(),
        worker_count=1,
        noise_connections=0,
        minimum_external_cpu_percent=30.0,
        startup_timeout_seconds=15.0,
        production_noise=False,
        protected_process_name='metrics_rollup_maintenance',
        protected_process_cycle_seconds=2.0,
        transient_process_name='backup_manifest_verifier',
        transient_start_delay_seconds=8.0,
        transient_runtime_seconds=100.0,
    )
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

class PgSystemFailureNoisyNeighborInjector(BaseFaultInjector):
    """
    Simulate OS-level CPU contention from a non-database process in the same
    container. The process is intentionally neutral-looking and does not use a
    scenario identifier in its command line.
    """
    def __init__(self):
        self.env = None
        self.table = "orders_probe"
        self.noise_table = "reporting_rollup_noise"
        self.marker_table = "maintenance_lock_marker"
        self.external_process_name = "wal_archive_compressor"
        self.protected_process_name = None
        self.protected_process_cycle_seconds = 0.0
        self.transient_process_name = None
        self.transient_start_delay_seconds = 0.0
        self.transient_runtime_seconds = 0.0
        self.job_registry_table = "ops_maintenance_jobs"
        self.job_runs_table = "ops_maintenance_job_runs"
        self._hog_pids = []
        self._noise_pids = []
        self._protected_pids = []
        self._transient_pids = []
        self._connections = []

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print("[FaultInjector:NoisyNeighbor] Preparing OLTP probe and production noise...")
        with env.metrics_hidden():
            self._prepare_probe_table()
        self._start_runtime()
        self._verify_runtime_pressure()
        print(f"[FaultInjector:NoisyNeighbor] Started WAL archive compression workers: {self._hog_pids}")

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(config['table'], "table")
        self.external_process_name = config['external_process_name']
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,64}", self.external_process_name):
            raise ValueError("external_process_name must be a simple process name")
        self.worker_count = int(config['worker_count'])
        self.noise_connections = int(config['noise_connections'])
        self.probe_sql = config['probe_sql']
        self.minimum_external_cpu_percent = float(config['minimum_external_cpu_percent'])
        self.startup_timeout_seconds = float(config['startup_timeout_seconds'])
        self.production_noise = bool(config['production_noise'])
        # Extended-candidate config; absent/None for wal_archive_cpu_neighbor.
        self.protected_process_name = config.get('protected_process_name') or None
        self.protected_process_cycle_seconds = float(config.get('protected_process_cycle_seconds') or 0.0)
        self.transient_process_name = config.get('transient_process_name') or None
        self.transient_start_delay_seconds = float(config.get('transient_start_delay_seconds') or 0.0)
        self.transient_runtime_seconds = float(config.get('transient_runtime_seconds') or 0.0)
        self.job_registry_table = _validate_sql_identifier(
            config.get('job_registry_table') or 'ops_maintenance_jobs', "job_registry_table")
        self.job_runs_table = _validate_sql_identifier(
            config.get('job_runs_table') or 'ops_maintenance_job_runs', "job_runs_table")
        self._hog_pids = []
        self._noise_pids = []
        self._protected_pids = []
        self._transient_pids = []
        self._connections = []

    def _verify_persistent_state(self) -> None:
        has_registry = bool(self.protected_process_name or self.transient_process_name)
        registry_select = (
            f", (SELECT count(*) FROM {self.job_registry_table})" if has_registry else ""
        )
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT (SELECT count(*) FROM {self.table}), "
                f"(SELECT count(*) FROM {self.noise_table}), "
                f"(SELECT count(*) FROM {self.marker_table})"
                f"{registry_select};"
            ),
            "verify noisy-neighbor fault image tables",
        )
        expected = [[20000, 180000, 1] + ([2] if has_registry else [])]
        if payload["result"] != expected:
            raise RuntimeError(
                f"Noisy-neighbor fault image does not match the Case: "
                f"expected={expected}, observed={payload['result']}"
            )

    def _start_runtime(self) -> None:
        import time

        if self.production_noise:
            self._prepare_observability_noise(self.noise_connections)
        else:
            self.env.execute_sql("SELECT pg_stat_statements_reset();")
            self.env._snapshot_pgss_baseline()
        container = self.env.deployment.container_name
        for _ in range(self.worker_count):
            self._hog_pids.append(self._start_container_process(
                container,
                self.external_process_name,
                "while :; do dd if=/dev/zero bs=1M count=64 2>/dev/null | gzip -9 > /tmp/wal_archive_compressor.gz; done",
                "/tmp/wal_archive_compressor.out",
            ))
        if self.protected_process_name:
            self._protected_pids.append(self._start_container_process(
                container,
                self.protected_process_name,
                self._protected_process_body(),
                f"/tmp/{self.protected_process_name}.out",
            ))
        if self.transient_process_name:
            self._transient_pids.append(self._start_container_process(
                container,
                self.transient_process_name,
                self._transient_process_body(),
                f"/tmp/{self.transient_process_name}.out",
            ))
        if self.production_noise:
            self._noise_pids.append(self._start_container_process(
                container,
                "metrics_shipper",
                "while :; do dd if=/dev/zero of=/tmp/metrics_shipper.tmp bs=32K count=1 conv=notrunc 2>/dev/null; sleep 0.4; done",
                "/tmp/metrics_shipper.out",
            ))
        time.sleep(4.0)

    def _protected_process_body(self) -> str:
        """Legitimate duty-cycled maintenance/statistics loop. It compresses a
        real metrics export, appends one visible progress row per cycle, then
        sleeps; killing it interrupts sanctioned nightly maintenance."""
        cycle = max(float(self.protected_process_cycle_seconds or 2.0), 0.5)
        return (
            "dd if=/dev/urandom of=/tmp/metrics_rollup_window.bin bs=1M count=8 2>/dev/null; "
            "while :; do "
            "gzip -9 -c /tmp/metrics_rollup_window.bin > /dev/null 2>&1; "
            f"PGPASSWORD=password psql -U postgres -d testdb -q -c \"INSERT INTO {self.job_runs_table} "
            f"(job_name, progress_note) VALUES ('{self.protected_process_name}', 'rolled one metrics window');\" "
            "2>/dev/null; "
            f"sleep {cycle}; "
            "done"
        )

    def _transient_process_body(self) -> str:
        """Legitimate one-shot verification job: after a short delay it burns
        CPU verifying manifests for a bounded time, records completion in the
        run log, then exits by itself."""
        delay = max(float(self.transient_start_delay_seconds or 0.0), 0.0)
        runtime = max(int(float(self.transient_runtime_seconds or 100.0)), 5)
        return (
            f"sleep {delay}; "
            "dd if=/dev/urandom of=/tmp/backup_manifest_bundle.bin bs=1M count=16 2>/dev/null; "
            f"end=$((SECONDS + {runtime})); "
            "while [ $SECONDS -lt $end ]; do "
            "gzip -9 -c /tmp/backup_manifest_bundle.bin > /dev/null 2>&1; "
            "done; "
            f"PGPASSWORD=password psql -U postgres -d testdb -q -c \"UPDATE {self.job_runs_table} "
            f"SET finished_at = now(), progress_note = 'manifest checksums verified' "
            f"WHERE job_name = '{self.transient_process_name}' AND finished_at IS NULL;\" "
            "2>/dev/null"
        )

    def _verify_runtime_pressure(self) -> None:
        import subprocess
        import time

        container = self.env.deployment.container_name
        candidate_pids = [*self._hog_pids, *self._protected_pids, *self._transient_pids]
        pid_args = [str(pid) for pid in candidate_pids]
        liveness = subprocess.run(
            ["docker", "exec", container, "kill", "-0", *pid_args],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if liveness.returncode != 0:
            raise RuntimeError(
                f"Noisy-neighbor CPU workers exited during startup: "
                f"container={container}, pids={candidate_pids}, stderr={liveness.stderr.strip()!r}"
            )

        deadline = time.monotonic() + self.startup_timeout_seconds
        latest = None
        external_cpu = None
        while time.monotonic() < deadline:
            cpu_metric = _json_object(
                self.env.query_metrics("cpu", target="top_processes"),
                "verify noisy-neighbor CPU pressure",
            )
            latest = float(cpu_metric["series"]["postgres"]["percent"][-1])
            external_cpu = float(cpu_metric["current"]["external_cpu_percent"])
            if external_cpu >= self.minimum_external_cpu_percent:
                return
            time.sleep(1.0)
        raise RuntimeError(
            f"Noisy-neighbor CPU pressure did not reach the Case threshold: "
            f"container={container}, pids={self._hog_pids}, latest={latest}, "
            f"external_cpu={external_cpu}, required_external={self.minimum_external_cpu_percent}, "
            f"timeout_seconds={self.startup_timeout_seconds}"
        )

    def _start_container_process(self, container: str, process_name: str, shell_body: str, outfile: str) -> int:
        import shlex
        import subprocess

        if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,64}", process_name):
            raise ValueError(f"process_name must be a simple process name: {process_name!r}")
        script_path = f"/tmp/{process_name}.sh"
        command = (
            f"printf %s {shlex.quote(shell_body)} > {shlex.quote(script_path)}; "
            f"chmod +x {shlex.quote(script_path)}; "
            f"nohup bash -lc 'exec -a {process_name} bash {script_path}' "
            f">{shlex.quote(outfile)} 2>&1 & echo $!"
        )
        result = subprocess.run(
            ["docker", "exec", container, "bash", "-lc", command],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to start {process_name}: {result.stderr.strip()}")
        pid_line = result.stdout.strip().splitlines()[-1]
        try:
            return int(pid_line)
        except ValueError as exc:
            raise RuntimeError(f"Could not parse {process_name} pid from: {result.stdout!r}") from exc

    def _prepare_probe_table(self):
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table}, {self.noise_table}, {self.marker_table} CASCADE;")
        self.env.execute_sql(f"""
            CREATE TABLE {self.table} (
                id integer PRIMARY KEY,
                customer_id integer NOT NULL,
                amount numeric(12,2) NOT NULL,
                status text NOT NULL
            );
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.table} (id, customer_id, amount, status)
            SELECT g, (g % 1000) + 1, ((g % 10000)::numeric / 100) + 1, 'PAID'
            FROM generate_series(1, 20000) AS g;
        """)
        self.env.execute_sql(f"CREATE INDEX idx_{self.table}_customer ON {self.table}(customer_id);")
        self.env.execute_sql(f"""
            CREATE TABLE {self.noise_table} AS
            SELECT g AS id, (g % 500) + 1 AS account_id, ((g % 7000)::numeric / 10) AS revenue
            FROM generate_series(1, 180000) AS g;
        """)
        self.env.execute_sql(f"CREATE TABLE {self.marker_table} (id integer PRIMARY KEY, note text);")
        self.env.execute_sql(f"INSERT INTO {self.marker_table} VALUES (1, 'routine maintenance marker');")
        if self.protected_process_name or self.transient_process_name:
            self._prepare_job_registry()
        self.env.execute_sql(f"ANALYZE {self.table};")
        self.env.execute_sql(f"ANALYZE {self.noise_table};")
        self.env.reconnect()

    def _prepare_job_registry(self):
        """Agent-visible registry of sanctioned scheduled operations plus their
        run/progress log. The runaway culprit is intentionally NOT registered:
        registered jobs are legitimate business, everything else burning CPU in
        this container is not sanctioned maintenance."""
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.job_runs_table}, {self.job_registry_table} CASCADE;")
        self.env.execute_sql(f"""
            CREATE TABLE {self.job_registry_table} (
                job_name text PRIMARY KEY,
                schedule text NOT NULL,
                purpose text NOT NULL,
                protection text NOT NULL CHECK (protection IN ('protected', 'one_shot')),
                owner text NOT NULL
            );
        """)
        self.env.execute_sql(f"""
            COMMENT ON TABLE {self.job_registry_table} IS
            'Sanctioned scheduled operations registered by the ops team; '
            'any other process doing heavy work inside this container is not sanctioned maintenance.';
        """)
        registry_rows = []
        if self.protected_process_name:
            registry_rows.append(
                f"('{self.protected_process_name}', "
                f"'nightly 01:00-05:00 window, continuous rollup loop', "
                f"'roll up and compress daily metrics exports', 'protected', 'dba-ops')"
            )
        if self.transient_process_name:
            registry_rows.append(
                f"('{self.transient_process_name}', "
                f"'one-shot after the nightly backup completes', "
                f"'verify backup manifest checksums, then exit', 'one_shot', 'dba-ops')"
            )
        self.env.execute_sql(
            f"INSERT INTO {self.job_registry_table} (job_name, schedule, purpose, protection, owner) "
            f"VALUES {', '.join(registry_rows)};"
        )
        self.env.execute_sql(f"""
            CREATE TABLE {self.job_runs_table} (
                run_id serial PRIMARY KEY,
                job_name text NOT NULL,
                started_at timestamptz NOT NULL DEFAULT now(),
                finished_at timestamptz,
                progress_note text,
                logged_at timestamptz NOT NULL DEFAULT now()
            );
        """)
        if self.protected_process_name:
            self.env.execute_sql(
                f"INSERT INTO {self.job_runs_table} (job_name, progress_note) "
                f"VALUES ('{self.protected_process_name}', 'maintenance window opened');"
            )
        if self.transient_process_name:
            self.env.execute_sql(
                f"INSERT INTO {self.job_runs_table} (job_name, progress_note) "
                f"VALUES ('{self.transient_process_name}', 'verification started');"
            )

    def _prepare_observability_noise(self, noise_connections: int):
        import psycopg2

        self.env.execute_sql("SELECT pg_stat_statements_reset();")
        self.env._snapshot_pgss_baseline()
        self.env.execute_sql(f"""
            SET application_name = 'bi_month_end_rollup';
            SET statement_timeout = '5s';
            SELECT account_id, count(*) AS orders, sum(revenue) AS revenue
            FROM {self.noise_table}
            GROUP BY account_id
            ORDER BY revenue DESC
            LIMIT 20;
            SELECT pg_sleep(1.15);
            RESET application_name;
        """)
        self.env.execute_sql(f"""
            SET application_name = 'finance_daily_margin';
            SET statement_timeout = '5s';
            SELECT account_id, avg(revenue), max(revenue)
            FROM {self.noise_table}
            WHERE account_id BETWEEN 40 AND 420
            GROUP BY account_id
            ORDER BY avg(revenue) DESC
            LIMIT 30;
            SELECT pg_sleep(1.05);
            RESET application_name;
        """)
        self.env.execute_sql(f"""
            SET application_name = 'retention_cohort_backfill';
            SET statement_timeout = '5s';
            SELECT count(*), sum(revenue)
            FROM {self.noise_table}
            WHERE id % 17 = 0;
            SELECT pg_sleep(1.10);
            RESET application_name;
        """)
        app_names = [
            "order_gateway_pool",
            "checkout_worker_pool",
            "payment_callback_pool",
            "inventory_reserve_pool",
            "shipping_quote_pool",
            "web_session_pool",
            "read_only_api_pool",
            "prometheus_pg_exporter",
            "grafana_healthcheck",
            "synthetic_checkout_probe",
            "autovacuum_observer",
            "reporting_scheduler_idle",
            "etl_coordinator_idle",
            "maintenance_lock_holder",
        ][:noise_connections]
        for idx, app_name in enumerate(app_names):
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.env.user,
                password=self.env.password,
                dbname=self.env.dbname,
                connect_timeout=3,
                application_name=app_name,
            )
            conn.autocommit = False
            cur = conn.cursor()
            if app_name == "maintenance_lock_holder":
                cur.execute(f"LOCK TABLE {self.marker_table} IN SHARE MODE;")
            else:
                cur.execute("SELECT 1;")
                conn.commit()
            self._connections.append(conn)
        self._start_running_report_noise()
        self._emit_business_noise_logs()

    def _start_running_report_noise(self):
        container = self.env.deployment.container_name
        self._noise_pids.append(self._start_container_process(
            container,
            "bi_dashboard_refresh",
            "PGPASSWORD=password psql -U postgres -d testdb -v ON_ERROR_STOP=1 "
            "-c \"SET application_name='bi_dashboard_refresh'; "
            "SET statement_timeout='10min'; SELECT pg_sleep(600);\"",
            "/tmp/bi_dashboard_refresh.out",
        ))

    def _emit_business_noise_logs(self):
        import shlex
        import subprocess

        lines = [
            "duration: 1288.114 ms  execute <unnamed>: SELECT nightly_revenue_rollup($1)",
            "duration: 1120.882 ms  statement: SELECT refresh_finance_margin_window($1, $2)",
            "duration: 1187.406 ms  execute <unnamed>: SELECT rebuild_retention_cohort($1)",
            "checkpoint starting: time",
            "checkpoint complete: wrote 812 buffers (5.1%); sync files=21, longest=141.992 ms",
            "temporary file: path \"base/pgsql_tmp/pgsql_tmp311.0\", size 29360128",
            "temporary file: path \"base/pgsql_tmp/pgsql_tmp344.1\", size 18874368",
            "automatic analyze of table \"public.reporting_rollup_noise\" system usage: CPU 0.18s/0.73u sec elapsed 3.44 sec",
            "connection authorized: user=postgres database=testdb application_name=prometheus_pg_exporter",
            "connection authorized: user=postgres database=testdb application_name=grafana_healthcheck",
            "connection received: host=10.42.7.18 port=55214",
            "duration: 642.551 ms  statement: SELECT count(*) FROM reporting_rollup_noise",
            "duration: 734.992 ms  statement: SELECT percentile_disc(0.95) WITHIN GROUP (ORDER BY revenue) FROM reporting_rollup_noise",
            "background worker \"logical replication launcher\" checked subscriptions",
        ]
        payload = "\n".join(f"2026-07-06 00:00:00.000 UTC [511] LOG:  {line}" for line in lines) + "\n"
        subprocess.run(
            [
                "docker", "exec", self.env.deployment.container_name, "sh", "-c",
                f"printf %s {shlex.quote(payload)} >> /var/log/postgresql/postgresql.log",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def _stop_connections(self):
        for conn in self._connections:
            conn.close()
        self._connections = []

    def _stop_report_noise(self):
        _require_sql_success(
            self.env.execute_sql("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE application_name = 'bi_dashboard_refresh'
                  AND pid <> pg_backend_pid();
            """),
            "terminate noisy-neighbor report sessions",
        )

    def _stop_container_processes(self, context: FaultLifecycleContext) -> None:
        import subprocess

        pids = [*self._hog_pids, *self._noise_pids, *self._protected_pids, *self._transient_pids]
        if not pids:
            return
        pid_args = " ".join(str(pid) for pid in pids)
        script = (
            f"kill -TERM {pid_args}; "
            "for attempt in $(seq 1 50); do "
            "alive=0; "
            f"for pid in {pid_args}; do if kill -0 $pid 2>/dev/null; then alive=1; fi; done; "
            "if [ $alive -eq 0 ]; then exit 0; fi; "
            "sleep 0.1; "
            "done; exit 1"
        )
        result = subprocess.run(
            [
                "docker",
                "exec",
                context.env.deployment.container_name,
                "bash",
                "-lc",
                script,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Noisy-neighbor processes did not stop: pids={pids}, "
                f"container={context.env.deployment.container_name}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        self._hog_pids = []
        self._noise_pids = []
        self._protected_pids = []
        self._transient_pids = []

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {}

    def quiesce(self, context: FaultLifecycleContext):
        """Kill noisy-neighbor processes for teardown."""
        self.env = context.env
        self._stop_report_noise()
        self._stop_connections()
        self._stop_container_processes(context)

    def recover(self, context: FaultLifecycleContext):
        self.env = context.env
        self._stop_report_noise()
        self._stop_connections()
        self._stop_container_processes(context)
        drop_targets = [self.table, self.noise_table, self.marker_table]
        if self.protected_process_name or self.transient_process_name:
            drop_targets.extend([self.job_runs_table, self.job_registry_table])
        _require_sql_success(
            self.env.execute_sql(
                f"DROP TABLE IF EXISTS {', '.join(drop_targets)} CASCADE;"
            ),
            "drop noisy-neighbor scenario tables",
        )
        if not self.env.reconnect():
            raise RuntimeError(
                f"Noisy-neighbor recovery could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._verify_persistent_state()
        self._start_runtime()
        self._verify_runtime_pressure()
        print(f"[FaultInjector:NoisyNeighbor] Re-activated WAL archive compression workers: {self._hog_pids}")


class PgSystemFailureNoisyNeighborScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_noisy_neighbor'
    description = 'Simulates CPU contention from an overrun WAL archive compression job.'
    cases = (
        _PGSYSTEMFAILURENOISYNEIGHBORSCENARIO_CASE,
        _PGSYSTEMFAILURENOISYNEIGHBORSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgSystemFailureNoisyNeighborCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailureNoisyNeighborInjector,
                config={
                    'table': case.table,
                    'external_process_name': case.external_process_name,
                    'worker_count': case.worker_count,
                    'noise_connections': case.noise_connections,
                    'probe_sql': case.probe_sql,
                    'minimum_external_cpu_percent': case.minimum_external_cpu_percent,
                    'startup_timeout_seconds': case.startup_timeout_seconds,
                    'production_noise': case.production_noise,
                    'protected_process_name': case.protected_process_name,
                    'protected_process_cycle_seconds': case.protected_process_cycle_seconds,
                    'transient_process_name': case.transient_process_name,
                    'transient_start_delay_seconds': case.transient_start_delay_seconds,
                    'transient_runtime_seconds': case.transient_runtime_seconds,
                    'job_registry_table': case.job_registry_table,
                    'job_runs_table': case.job_runs_table,
                },
            ),
        )
