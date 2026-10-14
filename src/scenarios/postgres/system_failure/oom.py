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
from src.workloads.specs import WorkloadProfile

from src.execution.specs import PostgresCaseRuntime, CaseResourceSpec, PostgresRuntimeSpec
from src.scenarios.base import PostgresScenario, DifficultyCalibration, FaultPlan, PostgresScenarioCase
from src.workloads.specs import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    EMPTY_BACKGROUND_WORKLOAD,
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
class PgSystemFailureOomCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    tpcds_memory_safety_probe_sql: str
    tpcds_memory_pressure_sql: str
    tpcds_background_report_sql: str
    tpcds_recovery_probe_sql: str
    shared_buffers: str
    work_mem: str
    safe_shared_buffers: str
    safe_work_mem: str
    postmaster_oom_score_adj: int
    production_noise: bool

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureOomForRestartMemoryConfigOomScenarioCase(PgSystemFailureOomCase):
    pass

_PGSYSTEMFAILUREOOMSCENARIO_CASE = PgSystemFailureOomForRestartMemoryConfigOomScenarioCase(
    case_id='restart_memory_config_oom',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "postgres crash recovery loop",
                    "entity": "restart_memory_config_oom",
                    "evidence": [
                        "scripted diagnostic actions observed postgres crash recovery loop"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "out of memory allocation failure",
                    "entity": "restart_memory_config_oom",
                    "evidence": [
                        "scripted diagnostic actions observed out of memory allocation failure"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "shared_buffers and work_mem exceed cgroup budget",
                    "entity": "restart_memory_config_oom",
                    "evidence": [
                        "scripted diagnostic actions observed shared_buffers and work_mem exceed cgroup budget"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "reset both memory settings then reboot",
                    "entity": "restart_memory_config_oom",
                    "evidence": [
                        "scripted diagnostic actions observed reset both memory settings then reboot"
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
    evaluator=PgSystemFailureOomForRestartMemoryConfigOomEvaluatorCase,
    runtime=PostgresCaseRuntime(resources=_OOM_RESOURCES),
    base_image_name='aiopsbench-pg-tpcds:latest',
    workload_tag='tpcds',
    dataset_scale=1,
    title='PostgreSQL process killed by OOM due to memory config exceeding container limit.',
    alert='P0 Alert: checkout and BI APIs are returning elevated 5xx errors. Application pools report repeated PostgreSQL connection refused events after the last maintenance restart. The container is still running, but database readiness keeps failing. Nearby telemetry also contains routine report temp-file and checkpoint messages; identify the primary reason PostgreSQL is not serving traffic and repair it.',
    initial_state={'status': 'crashed', 'postgres_process': 'dead', 'container': 'running'},
    expected_target={'status': 'recovered', 'config_fixed': True},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    tpcds_memory_safety_probe_sql=('\n'
 "            SET statement_timeout = '60s';\n"
 '            WITH daily_customer_item_sales AS (\n'
 '                SELECT\n'
 '                    d.d_year,\n'
 '                    d.d_moy,\n'
 '                    ss.ss_customer_sk,\n'
 '                    SUM(ss.ss_net_paid) AS net_paid,\n'
 '                    COUNT(*) AS line_count\n'
 '                FROM store_sales ss\n'
 '                JOIN date_dim d ON d.d_date_sk = ss.ss_sold_date_sk\n'
 '                WHERE ss.ss_customer_sk IS NOT NULL\n'
 '                  AND ss.ss_net_paid IS NOT NULL\n'
 '                  AND d.d_year = 2001\n'
 '                GROUP BY d.d_year, d.d_moy, ss.ss_customer_sk\n'
 '            )\n'
 '            SELECT\n'
 '                COUNT(*) AS grouped_rows,\n'
 '                COALESCE(SUM(net_paid), 0) AS net_paid\n'
 '            FROM daily_customer_item_sales;\n'
 '        '),
    tpcds_memory_pressure_sql=('\n'
 "            SET statement_timeout = '90s';\n"
 '            WITH report_rows AS MATERIALIZED (\n'
 '                SELECT\n'
 '                    ss.ss_ticket_number,\n'
 '                    ss.ss_customer_sk,\n'
 '                    ss.ss_item_sk,\n'
 '                    ss.ss_net_paid\n'
 '                FROM store_sales ss TABLESAMPLE SYSTEM (1)\n'
 '                WHERE ss.ss_customer_sk IS NOT NULL\n'
 '                  AND ss.ss_net_paid IS NOT NULL\n'
 '                LIMIT 5000\n'
 '            ),\n'
 '            expanded_report AS MATERIALIZED (\n'
 '                SELECT\n'
 '                    r.ss_customer_sk,\n'
 '                    r.ss_net_paid,\n'
 "                    repeat(md5(r.ss_ticket_number::text || ':' || g::text), 128) AS payload\n"
 '                FROM report_rows r\n'
 '                CROSS JOIN generate_series(1, 128) AS g\n'
 '            )\n'
 '            SELECT\n'
 '                ss_customer_sk,\n'
 '                COUNT(*) AS rows_seen,\n'
 '                ARRAY_AGG(payload ORDER BY ss_net_paid DESC) AS report_payload\n'
 '            FROM expanded_report\n'
 '            GROUP BY ss_customer_sk\n'
 '            ORDER BY rows_seen DESC\n'
 '            LIMIT 50;\n'
 '        '),
    tpcds_background_report_sql=('\n'
 '            /* app=nightly_margin_report route=/bi/margin */\n'
 "            SET statement_timeout = '20s';\n"
 "            SET work_mem = '4MB';\n"
 '            WITH channel_sales AS (\n'
 '                SELECT\n'
 '                    d.d_year,\n'
 '                    d.d_moy,\n'
 '                    ss.ss_store_sk,\n'
 '                    SUM(ss.ss_net_paid) AS net_paid\n'
 '                FROM store_sales ss TABLESAMPLE SYSTEM (1)\n'
 '                JOIN date_dim d ON d.d_date_sk = ss.ss_sold_date_sk\n'
 '                WHERE d.d_year = 2001\n'
 '                  AND ss.ss_net_paid IS NOT NULL\n'
 '                GROUP BY d.d_year, d.d_moy, ss.ss_store_sk\n'
 '            )\n'
 '            SELECT d_year, d_moy, COUNT(*), SUM(net_paid)\n'
 '            FROM channel_sales\n'
 '            GROUP BY d_year, d_moy\n'
 '            ORDER BY d_year, d_moy;\n'
 '        '),
    tpcds_recovery_probe_sql=('\n'
 "            SET statement_timeout = '30s';\n"
 '            SELECT d_year, COUNT(*) AS calendar_days\n'
 '            FROM date_dim\n'
 '            WHERE d_year = 2001\n'
 '            GROUP BY d_year;\n'
 '        '),
    shared_buffers='1536MB',
    work_mem='96MB',
    safe_shared_buffers='128MB',
    safe_work_mem='8MB',
    postmaster_oom_score_adj=1000,
    production_noise=True,
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.625,
        reference_run_ids=(
            "reference-49__pg_system_failure_oom__"
            "restart_memory_config_oom__mock__r001",
        ),
    ),
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureOomForRestartSharedBuffersOomSimpleScenarioCase(
    PgSystemFailureOomCase
):
    pass


_PGSYSTEMFAILUREOOMSCENARIO_SIMPLE_CASE = (
    PgSystemFailureOomForRestartSharedBuffersOomSimpleScenarioCase(
        case_id='restart_shared_buffers_oom_simple',
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "postgres crash recovery loop",
                        "entity": "restart_shared_buffers_oom_simple",
                        "evidence": [
                            "scripted diagnostic actions observed postgres crash recovery loop"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "out of memory allocation failure",
                        "entity": "restart_shared_buffers_oom_simple",
                        "evidence": [
                            "scripted diagnostic actions observed out of memory allocation failure"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "shared_buffers exceeds cgroup budget",
                        "entity": "restart_shared_buffers_oom_simple",
                        "evidence": [
                            "scripted diagnostic actions observed shared_buffers exceeds cgroup budget"
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
        evaluator=PgSystemFailureOomForRestartSharedBuffersOomSimpleEvaluatorCase,
        runtime=PostgresCaseRuntime(resources=_OOM_RESOURCES),
        difficulty=DifficultyCalibration(
            diagnostic_depth=2,
            environmental_complexity=0.2,
            reference_run_ids=(
                'logs/traces/run_pg_system_failure_oom_restart_shared_buffers_oom_simple_'
                'MockLLMAgent',
            ),
        ),
        base_image_name='aiopsbench-pg-tpcds:latest',
        workload_tag='tpcds',
        dataset_scale=1,
        title='One unsafe shared_buffers override prevents PostgreSQL from serving after restart.',
        alert=(
            'P0 Alert: PostgreSQL readiness fails after a maintenance restart while the '
            'container remains running. A low-rate calendar health probe was active before '
            'the restart. Identify why PostgreSQL is not serving traffic, restore service, '
            'and verify the probe query.'
        ),
        initial_state={
            'status': 'crashed',
            'postgres_process': 'dead',
            'container': 'running',
        },
        expected_target={
            'status': 'recovered',
            'shared_buffers': '<=128MB',
            'work_mem': '<=8MB',
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=(
                WorkloadProfile(
                    name='calendar_health_probe',
                    sql='SELECT count(*) FROM date_dim WHERE d_year = 2001;',
                    qps=0.1,
                    tier='LIGHT',
                    application_name='calendar_health_probe',
                ),
            ),
            worker_count=1,
            seed=0x2F0C,
            start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
            warmup_seconds=5,
        ),
        tpcds_memory_safety_probe_sql=(
            _PGSYSTEMFAILUREOOMSCENARIO_CASE.tpcds_recovery_probe_sql
        ),
        tpcds_memory_pressure_sql=(
            _PGSYSTEMFAILUREOOMSCENARIO_CASE.tpcds_memory_pressure_sql
        ),
        tpcds_background_report_sql='',
        tpcds_recovery_probe_sql=(
            _PGSYSTEMFAILUREOOMSCENARIO_CASE.tpcds_recovery_probe_sql
        ),
        shared_buffers='768MB',
        work_mem='8MB',
        safe_shared_buffers='128MB',
        safe_work_mem='8MB',
        postmaster_oom_score_adj=1000,
        production_noise=False,
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

class PgSystemFailureOomInjector(BaseFaultInjector):
    """
    模拟 OOM (Out of Memory) 故障。
    通过 ALTER SYSTEM SET 将 shared_buffers/work_mem 设置为远超容器内存限制的值，
    重启 PG 后执行内存密集型查询触发 Linux OOM Killer 杀死 PG 后端进程，
    PostgreSQL 进入 crash recovery，连接被拒绝。
    容器保持运行（新架构），PG 进程死亡。
    """

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._install_persistent_state()
        self._activate_runtime()

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._verify_persistent_state()
        self._activate_runtime()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.container_name = env.deployment.container_name
        self.shared_buffers = config['shared_buffers']
        self.work_mem = config['work_mem']
        self.memory_pressure_sql = config['memory_pressure_sql']
        self.background_report_sql = config['background_report_sql']
        self.postmaster_oom_score_adj = int(config['postmaster_oom_score_adj'])
        self.production_noise = bool(config['production_noise'])
        self.marker_path = f"{env.deployment.pgdata}/aiopsbench_oom_fault.json"

    def _marker_payload(self) -> dict:
        return {
            "fault": "pg_system_failure_oom",
            "shared_buffers": self.shared_buffers,
            "work_mem": self.work_mem,
            "postmaster_oom_score_adj": self.postmaster_oom_score_adj,
        }

    def _install_persistent_state(self) -> None:
        import shlex
        import subprocess

        payload = json.dumps(self._marker_payload(), sort_keys=True)
        result = subprocess.run(
            [
                "docker", "exec", self.container_name, "bash", "-c",
                f"printf '%s' {shlex.quote(payload)} > {shlex.quote(self.marker_path)} && "
                f"chown postgres:postgres {shlex.quote(self.marker_path)}",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Could not install OOM fault marker {self.marker_path}: "
                f"{(result.stderr or result.stdout).strip()}"
            )

    def _verify_persistent_state(self) -> None:
        import subprocess

        result = subprocess.run(
            ["docker", "exec", self.container_name, "cat", self.marker_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"OOM fault image is missing marker {self.marker_path}: {result.stderr.strip()}"
            )
        actual = json.loads(result.stdout)
        expected = self._marker_payload()
        if actual != expected:
            raise RuntimeError(
                f"OOM fault image marker mismatch: expected={expected}, actual={actual}"
            )

    def _activate_runtime(self) -> None:
        import time as _time
        import psycopg2

        self.oom_kill_before = self._read_memory_event("oom_kill")
        self.oom_kill_after = self.oom_kill_before
        self.oom_kill_delta = 0
        print(f"[FaultInjector:PgSystemFailureOomInjector] Injecting OOM fault...")
        print(f"[FaultInjector:PgSystemFailureOomInjector] Setting shared_buffers={self.shared_buffers}, work_mem={self.work_mem}")

        self._reset_agent_log_window(self.env)
        if self.production_noise:
            self._seed_production_noise(self.env, self.background_report_sql)

        for setting, value in (
            ("shared_buffers", self.shared_buffers),
            ("work_mem", self.work_mem),
        ):
            _require_sql_success(
                self.env.execute_sql(f"ALTER SYSTEM SET {setting} = '{value}';"),
                f"apply OOM memory setting {setting}={value}",
            )

        print(f"[FaultInjector:PgSystemFailureOomInjector] Restarting PG with dangerous memory config...")
        self._restart_pg_fast(self.env)
        _time.sleep(2)
        self.env._conn = None

        if not self.env.deployment.is_ready():
            self._record_oom_kill()
            print(f"[FaultInjector:PgSystemFailureOomInjector] PG failed to start due to unsafe memory config.")
            return

        print(f"[FaultInjector:PgSystemFailureOomInjector] PG started (overcommit). Triggering OOM via memory pressure...")
        try:
            conn = psycopg2.connect(
                host=self.env.host, port=self.env.port,
                user=self.env.user, password=self.env.password, dbname=self.env.dbname,
                connect_timeout=5
            )
            conn.autocommit = True
            self._set_postmaster_oom_score_adj(self.postmaster_oom_score_adj)
            with conn.cursor() as cur:
                cur.execute("SET work_mem = '256MB';")
                cur.execute(self.memory_pressure_sql)
        except Exception as e:
            print(f"[FaultInjector:PgSystemFailureOomInjector] Query killed (expected): {type(e).__name__}")

        _time.sleep(2)
        self.env._conn = None
        if not self.env.deployment.is_ready():
            self._record_oom_kill()
            print(f"[FaultInjector:PgSystemFailureOomInjector] OOM fault injection successful - PostgreSQL is unavailable.")
            return

        self._set_postmaster_oom_score_adj(0)
        raise RuntimeError(
            "OOM fault injection did not leave PostgreSQL unavailable; "
            f"postmaster_oom_score_adj={self.postmaster_oom_score_adj}, "
            f"shared_buffers={self.shared_buffers}, work_mem={self.work_mem}"
        )

    def _read_memory_event(self, event_name: str) -> int:
        import subprocess

        result = subprocess.run(
            ["docker", "exec", self.container_name, "cat", "/sys/fs/cgroup/memory.events"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Could not read container cgroup memory events: "
                f"container={self.container_name}, stderr={result.stderr.strip()!r}"
            )
        events = {
            name: int(value)
            for line in result.stdout.splitlines()
            for name, value in [line.split()]
        }
        if event_name not in events:
            raise RuntimeError(
                f"Container cgroup memory event is missing: "
                f"container={self.container_name}, event={event_name!r}, events={events}"
            )
        return events[event_name]

    def _record_oom_kill(self) -> None:
        self.oom_kill_after = self._read_memory_event("oom_kill")
        self.oom_kill_delta = self.oom_kill_after - self.oom_kill_before
        if self.oom_kill_delta < 1:
            raise RuntimeError(
                f"PostgreSQL became unavailable without a cgroup OOM kill: "
                f"container={self.container_name}, before={self.oom_kill_before}, "
                f"after={self.oom_kill_after}"
            )
        self._publish_oom_evidence()

    def _publish_oom_evidence(self) -> None:
        import shlex
        import subprocess

        message = (
            "memory cgroup oom_kill observed: "
            f"before={self.oom_kill_before} after={self.oom_kill_after} "
            f"delta={self.oom_kill_delta}; PostgreSQL postmaster exited"
        )
        command = (
            "printf '%s\\n' "
            f"{shlex.quote(message)} >> /var/log/postgresql/postgresql.log"
        )
        result = subprocess.run(
            ["docker", "exec", self.container_name, "sh", "-c", command],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "Could not publish verified OOM evidence to the agent-visible log: "
                f"container={self.container_name}, stderr={result.stderr.strip()!r}"
            )

    def _set_postmaster_oom_score_adj(self, value: int) -> None:
        import subprocess

        pgdata = self.env.deployment.pgdata
        command = (
            f"pid=$(head -n 1 {pgdata}/postmaster.pid) && "
            f"printf '%d' {value} > /proc/$pid/oom_score_adj && "
            f"test \"$(cat /proc/$pid/oom_score_adj)\" = {value}"
        )
        result = subprocess.run(
            ["docker", "exec", self.container_name, "bash", "-c", command],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Could not set PostgreSQL postmaster oom_score_adj: "
                f"container={self.container_name}, value={value}, "
                f"stderr={result.stderr.strip()!r}"
            )

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        container_running = env.deployment.is_container_running()
        postgres_ready = env.deployment.is_ready()
        if not container_running or postgres_ready:
            raise RuntimeError(
                "OOM state mismatch: "
                f"container_running={container_running}, postgres_ready={postgres_ready}"
            )
        pg_log = env.read_log("pg_log", lines=120)
        if self.oom_kill_delta < 1:
            raise RuntimeError(
                f"OOM cgroup evidence is missing: container={self.container_name}, "
                f"before={self.oom_kill_before}, after={self.oom_kill_after}, "
                f"delta={self.oom_kill_delta}"
            )
        return {
            "container_running": container_running,
            "postgres_ready": postgres_ready,
            "oom_kill_before": self.oom_kill_before,
            "oom_kill_after": self.oom_kill_after,
            "oom_kill_delta": self.oom_kill_delta,
            "pg_log": pg_log,
        }

    def quiesce(self, context: FaultLifecycleContext):
        """Recover PostgreSQL while preserving the persistent OOM marker."""
        env = context.env
        self._close_noise_connections()
        if env.deployment.is_ready():
            raise RuntimeError("Cannot quiesce OOM fault while PostgreSQL is still ready")
        self._clear_oom_settings()
        env.deployment.start_pg()
        if not env.deployment.wait_for_ready(timeout=180):
            raise RuntimeError("PostgreSQL did not recover from OOM before snapshot")
        if not env.reconnect():
            raise RuntimeError("PostgreSQL reconnect failed while preparing OOM fault snapshot")

    def _restart_pg_fast(self, env):
        import subprocess

        result = subprocess.run(
            env.deployment._pg_ctl_cmd(f"stop -D {env.deployment.pgdata} -m fast"),
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise RuntimeError(f"Failed to fast-stop PostgreSQL before OOM restart: {detail[:300]}")
        env.deployment.start_pg()

    def _reset_agent_log_window(self, env):
        env._reset_pg_log_visibility()

    def _connect_noise_session(self, env, application_name: str):
        import psycopg2

        return psycopg2.connect(
            host=env.host, port=env.port,
            user=env.user, password=env.password, dbname=env.dbname,
            connect_timeout=5,
            application_name=application_name,
        )

    def _seed_production_noise(self, env, background_report_sql: str):
        self._close_noise_connections()
        self._noise_connections = []
        if background_report_sql:
            env.execute_sql(background_report_sql)
        self._run_logged_noise_sql(env, "checkout_api_pool_17", "SELECT 1 /* readiness probe */;")
        self._run_logged_noise_sql(env, "prometheus_pg_exporter", """
            SELECT datname, numbackends, xact_commit, xact_rollback
            FROM pg_stat_database
            WHERE datname = current_database();
        """)
        self._hold_idle_transaction(env)
        env.execute_sql("""
            DO $$
            BEGIN
                RAISE LOG 'checkpoint complete: wrote 124 buffers, 2 WAL files recycled';
                RAISE LOG 'connection pool health probe timeout from 10.0.12.44';
                RAISE LOG 'autovacuum worker skipped relation public.store_sales due to concurrent workload';
            END
            $$;
        """)

    def _run_logged_noise_sql(self, env, application_name: str, sql: str):
        conn = self._connect_noise_session(env, application_name)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute("SET log_min_duration_statement = 0;")
                cur.execute(sql)
        finally:
            conn.close()

    def _hold_idle_transaction(self, env):
        conn = self._connect_noise_session(env, "settlement_reconciler")
        cur = conn.cursor()
        cur.execute("BEGIN;")
        cur.execute("SELECT 1 FROM store_sales WHERE ss_customer_sk IS NOT NULL LIMIT 1;")
        self._noise_connections.append(conn)

    def _close_noise_connections(self):
        for conn in getattr(self, "_noise_connections", []):
            conn.close()
        self._noise_connections = []

    def recover(self, context: FaultLifecycleContext):
        import time as _time

        self._close_noise_connections()
        print(f"[FaultInjector:PgSystemFailureOomInjector] Recovering OOM settings...")
        self._clear_oom_settings()
        self.env.deployment.start_pg()
        if not self.env.deployment.wait_for_ready(timeout=300):
            raise RuntimeError("PostgreSQL did not recover after removing OOM settings")
        _time.sleep(1)
        self._remove_marker()

    def _clear_oom_settings(self):
        import subprocess

        auto_conf = f"{self.env.deployment.pgdata}/postgresql.auto.conf"
        result = subprocess.run(
            ["docker", "exec", self.container_name, "bash", "-c",
             f"touch {auto_conf} && "
             f"sed -i -E '/^[[:space:]]*(shared_buffers|work_mem)[[:space:]]*=/d' {auto_conf} && "
             f"chown postgres:postgres {auto_conf}"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise RuntimeError(f"Failed to remove OOM settings from auto.conf: {detail[:300]}")

    def _remove_marker(self) -> None:
        import subprocess

        result = subprocess.run(
            ["docker", "exec", self.container_name, "rm", "-f", self.marker_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to remove OOM marker {self.marker_path}: {result.stderr.strip()}"
            )


class PgSystemFailureOomScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_oom'
    description = 'PostgreSQL process killed by OOM due to memory config exceeding container limit.'
    cases = (
        _PGSYSTEMFAILUREOOMSCENARIO_CASE,
        _PGSYSTEMFAILUREOOMSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgSystemFailureOomCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailureOomInjector,
                config={
                    'shared_buffers': case.shared_buffers,
                    'work_mem': case.work_mem,
                    'memory_pressure_sql': case.tpcds_memory_pressure_sql,
                    'background_report_sql': case.tpcds_background_report_sql,
                    'postmaster_oom_score_adj': case.postmaster_oom_score_adj,
                    'production_noise': case.production_noise,
                },
            ),
        )
