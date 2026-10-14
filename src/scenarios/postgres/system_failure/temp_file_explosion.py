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
class PgSystemFailureTempFileExplosionCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    culprit_role: str
    culprit_application: str
    culprit_job: str
    required_temp_file_limit: str
    pgdata: str
    tmpfs_size_mb: int
    target_temp_mb: int
    sort_rows: int
    failure_probe_rows: int
    production_noise: bool

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureTempFileExplosionForNightlyMarginTempExhaustionScenarioCase(PgSystemFailureTempFileExplosionCase):
    pass

_PGSYSTEMFAILURETEMPFILEEXPLOSIONSCENARIO_CASE = PgSystemFailureTempFileExplosionForNightlyMarginTempExhaustionScenarioCase(
    case_id='nightly_margin_temp_exhaustion',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "temporary file explosion",
                    "entity": "nightly_margin_temp_exhaustion",
                    "evidence": [
                        "scripted diagnostic actions observed temporary file explosion"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "nightly margin rollup spills",
                    "entity": "nightly_margin_temp_exhaustion",
                    "evidence": [
                        "scripted diagnostic actions observed nightly margin rollup spills"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "report batch role is culprit",
                    "entity": "nightly_margin_temp_exhaustion",
                    "evidence": [
                        "scripted diagnostic actions observed report batch role is culprit"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "limit culprit temp files to 64mb",
                    "entity": "nightly_margin_temp_exhaustion",
                    "evidence": [
                        "scripted diagnostic actions observed limit culprit temp files to 64mb"
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
    evaluator=PgSystemFailureTempFileExplosionForNightlyMarginTempExhaustionEvaluatorCase,
    runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
    base_image_name='aiopsbench-pg-tpcds:latest',
    workload_tag='tpcds',
    dataset_scale=1,
    title='Simulates write failures caused by one reporting batch spilling temp files amid normal production noise.',
    alert='Alert: PostgreSQLWriteFailuresHigh. Order writes and several scheduled jobs are intermittently failing with storage-related errors, while OLTP reads and monitoring probes still connect normally. Several BI/reporting queries and routine collectors are active on the primary. Identify the production source of the write failures, restore write availability, and prevent the same batch from immediately exhausting scratch space again.',
    initial_state={'status': 'degraded',
 'symptom': 'storage-related write failures',
 'noise': 'normal client sessions, monitoring probes, BI history, and completed slow SQL'},
    expected_target={'status': 'recovered',
 'culprit_role': 'report_batch',
 'culprit_application': 'batch_rollup_scheduler',
 'culprit_job': 'nightly_margin_rollup',
 'required_temp_file_limit': '64MB'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    culprit_role='report_batch',
    culprit_application='batch_rollup_scheduler',
    culprit_job='nightly_margin_rollup',
    required_temp_file_limit='64MB',
    pgdata='/var/lib/postgresql/data_fat',
    tmpfs_size_mb=192,
    target_temp_mb=80,
    sort_rows=180000,
    failure_probe_rows=220000,
    production_noise=True,
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.5,
        reference_run_ids=(
            "reference-65__pg_system_failure_temp_file_explosion__"
            "nightly_margin_temp_exhaustion__mock__r001",
        ),
    ),
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureTempFileExplosionForDailySalesTempExhaustionSimpleScenarioCase(PgSystemFailureTempFileExplosionCase):
    pass

_PGSYSTEMFAILURETEMPFILEEXPLOSIONSCENARIO_SIMPLE_CASE = (
    PgSystemFailureTempFileExplosionForDailySalesTempExhaustionSimpleScenarioCase(
        case_id='daily_sales_temp_exhaustion_simple',
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "temporary file explosion",
                        "entity": "daily_sales_temp_exhaustion_simple",
                        "evidence": [
                            "scripted diagnostic actions observed temporary file explosion"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "nightly margin rollup spills",
                        "entity": "daily_sales_temp_exhaustion_simple",
                        "evidence": [
                            "scripted diagnostic actions observed nightly margin rollup spills"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "report batch role is culprit",
                        "entity": "daily_sales_temp_exhaustion_simple",
                        "evidence": [
                            "scripted diagnostic actions observed report batch role is culprit"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "limit culprit temp files to 64mb",
                        "entity": "daily_sales_temp_exhaustion_simple",
                        "evidence": [
                            "scripted diagnostic actions observed limit culprit temp files to 64mb"
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
        evaluator=PgSystemFailureTempFileExplosionForDailySalesTempExhaustionSimpleEvaluatorCase,
        runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
        difficulty=DifficultyCalibration(
            diagnostic_depth=3,
            environmental_complexity=0.5,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_system_failure_temp_file_explosion_"
                "daily_sales_temp_exhaustion_simple_"
                "MockLLMAgent.json",
            ),
        ),
        base_image_name='aiopsbench-pg-tpcds:latest',
        workload_tag='tpcds',
        dataset_scale=1,
        title='One daily sales rollup fills PostgreSQL scratch space beside a same-role retry batch.',
        alert=(
            'Alert: Scheduled writes fail with a storage-related error while PostgreSQL remains '
            'reachable and a low-rate date probe succeeds. A cancelled retry batch uses the same '
            'report role and application identity. Identify the active scratch-space consumer by '
            'job, restore writes, and prevent that batch from exhausting temp storage again.'
        ),
        initial_state={'status': 'degraded', 'symptom': 'scratch_write_failures'},
        expected_target={
            'status': 'recovered',
            'culprit_role': 'report_batch',
            'culprit_application': 'batch_rollup_scheduler',
            'required_temp_file_limit': '32-64MB role-scoped',
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=(
                WorkloadProfile(
                    name='date_health_probe',
                    sql='SELECT count(*) FROM date_dim WHERE d_year = 2001;',
                    qps=0.1,
                    tier='LIGHT',
                    application_name='date_health_probe',
                ),
            ),
            worker_count=1,
            seed=0x2F08,
            start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
            warmup_seconds=11,
        ),
        culprit_role='report_batch',
        culprit_application='batch_rollup_scheduler',
        culprit_job='daily_sales_rollup',
        required_temp_file_limit='64MB',
        pgdata='/var/lib/postgresql/data_fat',
        tmpfs_size_mb=128,
        target_temp_mb=48,
        sort_rows=110000,
        failure_probe_rows=160000,
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

class PgSystemFailureTempFileExplosionInjector(BaseFaultInjector):
    """
    模拟"临时文件爆炸与磁盘耗尽"故障。
    依赖运行环境在启动容器时挂载 tmpfs 限制 pgsql_tmp 目录大小，
    然后启动会物化大结果集并长期持有临时文件的查询，模拟临时文件快速膨胀。

    注意：运行环境需要在 deploy 前为 pgsql_tmp 配置 tmpfs mount。
    """

    def __init__(self):
        self._stop_event = None
        self._bg_conn = None
        self._bg_pid = None
        self._thread = None
        self._noise_conns = []
        self._noise_threads = []

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._verify_tmpfs()
        self._install_persistent_state()
        self._activate_runtime()

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._verify_tmpfs()
        self._verify_persistent_state()
        self._activate_runtime()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.container_name = env.deployment.container_name
        self.pgdata = config['pgdata']
        self.tmpfs_size_mb = int(config['tmpfs_size_mb'])
        self.target_temp_mb = int(config['target_temp_mb'])
        self.sort_rows = int(config['sort_rows'])
        self.failure_probe_rows = int(config['failure_probe_rows'])
        self.pgsql_tmp_dir = f"{self.pgdata}/base/pgsql_tmp"
        self.culprit_role = _validate_sql_identifier(config['culprit_role'], "culprit_role")
        self.culprit_password = config['culprit_password']
        self.culprit_application = config['culprit_application']
        self.culprit_job = config['culprit_job']
        self.required_temp_file_limit = config['required_temp_file_limit']
        self.production_noise = bool(config['production_noise'])

    def _verify_tmpfs(self) -> None:
        print(f"[FaultInjector:TempFileExplosion] Verifying tmpfs ({self.tmpfs_size_mb}MB) for pgsql_tmp...")
        self._assert_pgsql_tmp_tmpfs()
        self._ensure_pgsql_tmp_writable()

    def _install_persistent_state(self) -> None:
        escaped_password = self.culprit_password.replace("'", "''")
        _require_sql_success(
            self.env.execute_sql(
                f"""
                CREATE ROLE {self.culprit_role} LOGIN PASSWORD '{escaped_password}';
                ALTER ROLE {self.culprit_role} CONNECTION LIMIT -1;
                """
            ),
            "install temp-file culprit role",
        )

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                "SELECT rolname, rolcanlogin FROM pg_roles "
                f"WHERE rolname = '{self.culprit_role}';"
            ),
            "verify temp-file culprit role",
        )
        if payload["result"] != [[self.culprit_role, True]]:
            raise RuntimeError(
                f"Temp-file fault image role mismatch: role={self.culprit_role}, "
                f"rows={payload['result']}"
            )

    def _activate_runtime(self) -> None:
        import subprocess
        import threading
        import psycopg2
        import time

        self._noise_conns = []
        self._noise_threads = []
        self._stop_event = threading.Event()
        if self.production_noise:
            self._start_production_context()

        self._pid_ready = threading.Event()
        self._bg_conn = None
        self._bg_pid = None
        self._background_error = None

        def run_cartesian():
            try:
                conn = psycopg2.connect(
                    host=self.env.host, port=self.env.port,
                    user=self.culprit_role, password=self.culprit_password, dbname=self.env.dbname,
                    application_name=self.culprit_application
                )
                conn.autocommit = True
                self._bg_conn = conn
                with conn.cursor() as cur:
                    cur.execute("SELECT pg_backend_pid();")
                    self._bg_pid = cur.fetchone()[0]
                    self._pid_ready.set()
                    print(f"[FaultInjector:TempFileExplosion] Background query PID: {self._bg_pid}")
                    try:
                        # 保持默认 work_mem，让大体量物化结果自然超过内存后写入 pgsql_tmp。
                        # 这样故障根因是报表查询临时文件膨胀，而不是异常会话参数。
                        cur.execute(
                            f"""
                            /* service=finance_reporting job={self.culprit_job} ticket=finops-7742 */
                            WITH daily_margin_rollup AS MATERIALIZED (
                                SELECT g AS store_sk,
                                       (g % 96) AS quarter_hour,
                                       repeat(md5(('margin:' || g)::text), 32) AS payload
                                FROM generate_series(1, {self.sort_rows}) AS g
                            )
                            SELECT pg_sleep(3600)
                            FROM (SELECT count(*) FROM daily_margin_rollup) AS counted;
                            """
                        )
                    except Exception as e:
                        print(f"[FaultInjector:TempFileExplosion] Query ended: {e}")
                self._stop_event.wait()
            except Exception as e:
                self._background_error = e
                print(f"[FaultInjector:TempFileExplosion] Background thread error: {e}")
                self._pid_ready.set()
                self._stop_event.wait()

        self._thread = threading.Thread(target=run_cartesian, daemon=True) # 后台连接，持续施加真实SQL压力
        self._thread.start()

        # This cancelled retry shares the application identity; its distinct
        # job marker makes target selection observable.
        self._start_culprit_context_query(
            "/* service=finance_reporting job=daily_sales_rollup_retry status=cancelled */ "
            "SELECT pg_sleep(3600) FROM (SELECT count(*) FROM generate_series(1, 5000)) s;"
        )

        if not self._pid_ready.wait(timeout=15):
            raise RuntimeError("Background query failed to start within 15s")
        if self._bg_pid is None:
            raise RuntimeError(
                f"Background temp-file query failed before obtaining a backend PID: "
                f"{self._background_error!r}"
            ) from self._background_error

        print(f"[FaultInjector:TempFileExplosion] Waiting for PostgreSQL temp files from PID={self._bg_pid}...")
        observed_mb = 0.0
        deadline = time.time() + 60
        backend_holding_temp = False
        while time.time() < deadline: # 注入器轮询 pg_ls_tmpdir()，知道文件总量达到 target_temp_mb
            if self._bg_pid and not self._is_backend_active(self._bg_pid):
                raise RuntimeError("Background temp-file query exited before the fault became observable")
            observed_mb = self._current_pg_temp_mb()
            backend_holding_temp = self._is_backend_sleeping(self._bg_pid)
            if observed_mb >= self.target_temp_mb and backend_holding_temp:
                break
            time.sleep(1)
        if observed_mb < self.target_temp_mb:
            raise RuntimeError(
                f"PostgreSQL temp files reached only {observed_mb:.1f}MB; "
                f"expected at least {self.target_temp_mb}MB"
            )
        if not backend_holding_temp:
            raise RuntimeError("Background query did not reach pg_sleep while holding temp files")

        # 真实产生并有了大量 pg tmpfs 之后，启动 analytical_probe 执行额外物化查询
        self._run_no_space_probe(self.env)

        res = subprocess.run([
            "docker", "exec", self.container_name, "df", "-h", self.pgsql_tmp_dir
        ], capture_output=True, text=True)
        print(f"[FaultInjector:TempFileExplosion] Disk status:\n  {res.stdout.strip()}")
        print(f"[FaultInjector:TempFileExplosion] Fault injection complete.")

    def _start_culprit_context_query(self, sql: str):
        import psycopg2
        import threading
        conn = psycopg2.connect(
            host=self.env.host, port=self.env.port,
            user=self.culprit_role, password=self.culprit_password,
            dbname=self.env.dbname, application_name=self.culprit_application,
        )
        conn.autocommit = True
        self._noise_conns.append(conn)
        started = threading.Event()
        def run():
            try:
                with conn.cursor() as cur:
                    started.set()
                    cur.execute(sql)
            except psycopg2.Error as exc:
                print(f"[FaultInjector:TempFileExplosion] Context query ended: {exc}")
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        if not started.wait(timeout=5):
            raise RuntimeError("Same-role retry context query did not start")
        self._noise_threads.append(thread)

    def _start_production_context(self):
        import psycopg2

        for app_name, sql in [
            (
                "bi_dashboard_api",
                """
                /* dashboard=exec_kpi refresh=hourly */
                WITH dashboard_rollup AS MATERIALIZED (
                    SELECT g, g % 24 AS hour_bucket
                    FROM generate_series(1, 1800) AS g
                )
                SELECT pg_sleep(3600) FROM (SELECT count(*) FROM dashboard_rollup) s;
                """,
            ),
            (
                "inventory_snapshot_job",
                """
                /* job=inventory_snapshot warehouse=all */
                WITH snapshot_delta AS MATERIALIZED (
                    SELECT g AS item_sk, g % 7 AS warehouse_sk
                    FROM generate_series(1, 2400) AS g
                    WHERE g % 11 = 0
                )
                SELECT pg_sleep(3600)
                FROM (SELECT count(*) FROM snapshot_delta) s;
                """,
            ),
            (
                "prometheus_pg_exporter",
                """
                /* monitor=prometheus collector=activity */
                SELECT pg_sleep(3600) FROM (SELECT count(*) FROM pg_stat_activity) s;
                """,
            ),
            (
                "etl_revenue_reconcile",
                """
                /* job=hourly_revenue_reconcile source=billing */
                WITH revenue_rollup AS MATERIALIZED (
                    SELECT g AS account_id, g % 31 AS billing_day
                    FROM generate_series(1, 3200) AS g
                )
                SELECT pg_sleep(3600)
                FROM (SELECT count(*) FROM revenue_rollup) s;
                """,
            ),
        ]:
            self._start_noise_query(app_name, sql)

        idle_conn = psycopg2.connect(
            host=self.env.host, port=self.env.port,
            user=self.env.user, password=self.env.password, dbname=self.env.dbname,
            application_name="orders_api_pooler",
        )
        idle_conn.autocommit = False
        with idle_conn.cursor() as cur:
            cur.execute("SELECT 'checkout latency probe' AS probe;")
        self._noise_conns.append(idle_conn)

    def _start_noise_query(self, app_name: str, sql: str):
        import psycopg2
        import threading

        conn = psycopg2.connect(
            host=self.env.host, port=self.env.port,
            user=self.env.user, password=self.env.password, dbname=self.env.dbname,
            application_name=app_name,
        )
        conn.autocommit = True
        self._noise_conns.append(conn)
        started = threading.Event()

        def run_noise():
            try:
                with conn.cursor() as cur:
                    started.set()
                    cur.execute(sql)
            except psycopg2.Error as exc:
                print(f"[FaultInjector:TempFileExplosion] Noise query ended for application_name={app_name}: {exc}")

        thread = threading.Thread(target=run_noise, daemon=True)
        thread.start()
        if not started.wait(timeout=5):
            raise RuntimeError(f"Noise query did not start for application_name={app_name}")
        self._noise_threads.append(thread)

    def _run_no_space_probe(self, env):
        import psycopg2

        print("[FaultInjector:TempFileExplosion] Running No space left on device probe...")
        try:
            conn = psycopg2.connect(
                host=env.host, port=env.port,
                user=env.user, password=env.password, dbname=env.dbname,
                application_name="api_write_probe"
            )
            conn.autocommit = True
            try:
                with conn.cursor() as cur:
                    cur.execute("SET statement_timeout = '45s';")
                    cur.execute(
                        f"""
                        WITH probe_spill AS MATERIALIZED (
                            SELECT g, repeat(md5((g + 9000000)::text), 32) AS payload
                            FROM generate_series(1, {self.failure_probe_rows}) AS g
                        )
                        SELECT count(*) FROM probe_spill;
                        """
                    )
            finally:
                conn.close()
        except Exception as e:
            message = str(e)
            # 只有探针 SQL 报错，且异常文本包含 No space left on device，则继续
            if "No space left on device" in message:
                print("[FaultInjector:TempFileExplosion] No-space probe failed as expected.")
                self.no_space_error = message
                return
            raise RuntimeError(
                "Temp-file failure probe failed, but not with No space left on device: "
                f"{type(e).__name__}: {message}"
            )

        raise RuntimeError(
            "Temp-file failure probe unexpectedly completed; "
            "No space left on device was not reproduced."
        )

    def _assert_pgsql_tmp_tmpfs(self):
        import subprocess

        res = subprocess.run([
            "docker", "exec", self.container_name,
            "df", "-PT", self.pgsql_tmp_dir
        ], capture_output=True, text=True, timeout=10)
        output = res.stdout.strip()
        if res.returncode != 0 or "tmpfs" not in output:
            raise RuntimeError(
                "Temp-file explosion scenario requires pgsql_tmp to be mounted "
                "as tmpfs before fault injection. Configure deployment resources "
                f"with tmpfs_mounts=['{self.pgsql_tmp_dir}:size={self.tmpfs_size_mb}m']."
            )

    def _ensure_pgsql_tmp_writable(self):
        import subprocess

        res = subprocess.run(
            [
                "docker", "exec", self.container_name,
                "bash", "-c",
                f"chown postgres:postgres {self.pgsql_tmp_dir} && chmod 700 {self.pgsql_tmp_dir}",
            ],
            capture_output=True, text=True, timeout=10,
        )
        if res.returncode != 0:
            raise RuntimeError(
                "Could not make pgsql_tmp writable by postgres: "
                f"{(res.stderr or res.stdout).strip()[:300]}"
            )

    def _current_pg_temp_mb(self) -> float:
        payload = _json_object(
            self.env.execute_sql("SELECT COALESCE(SUM(size), 0) FROM pg_ls_tmpdir();"),
            "read temp-file usage",
        )
        if payload.get("status") == "error":
            raise RuntimeError(f"Could not read PostgreSQL temp-file usage: {payload}")
        return float(payload["result"][0][0]) / 1024 / 1024

    def _is_backend_active(self, pid: int) -> bool:
        payload = _json_object(
            self.env.execute_sql(
                f"""
                SELECT count(*)
                FROM pg_stat_activity
                WHERE pid = {int(pid)}
                  AND state = 'active'
                  AND usename = '{self.culprit_role}'
                  AND application_name = '{self.culprit_application}';
                """
            ),
            f"check temp-file backend activity for pid={pid}",
        )
        if payload.get("status") == "error":
            raise RuntimeError(f"Could not check temp-file backend activity: pid={pid}, payload={payload}")
        return int(payload["result"][0][0]) > 0

    def _is_backend_sleeping(self, pid: int) -> bool:
        payload = _json_object(
            self.env.execute_sql(
                f"""
                SELECT count(*)
                FROM pg_stat_activity
                WHERE pid = {int(pid)}
                  AND state = 'active'
                  AND usename = '{self.culprit_role}'
                  AND application_name = '{self.culprit_application}'
                  AND wait_event = 'PgSleep';
                """
            ),
            f"check temp-file backend wait event for pid={pid}",
        )
        if payload.get("status") == "error":
            raise RuntimeError(f"Could not check temp-file backend wait event: pid={pid}, payload={payload}")
        return int(payload["result"][0][0]) > 0

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        temp_mb = self._current_pg_temp_mb()
        if temp_mb < 10:
            raise RuntimeError(f"Temp-file fault is below 10MB: observed_mb={temp_mb}")
        if self._bg_pid is None or not self._is_backend_active(self._bg_pid):
            raise RuntimeError(
                f"Temp-file culprit backend is not active: pid={self._bg_pid}"
            )
        return {
            "temp_file_mb": temp_mb,
            "culprit_pid": self._bg_pid,
            "disk_usage": env.query_metrics("disk_usage"),
        }

    def _stop_runtime(self, context: FaultLifecycleContext) -> None:
        if self._stop_event is not None:
            self._stop_event.set()
        steps = []
        if self._bg_conn is not None:
            steps.append((
                "cancel culprit connection",
                lambda: _cancel_open_connection(self._bg_conn),
            ))
        for index, conn in enumerate(self._noise_conns):
            steps.append((
                f"cancel noise connection {index}",
                lambda conn=conn: _cancel_open_connection(conn),
            ))
        for index, thread in enumerate(self._noise_threads):
            steps.append((
                f"join noise thread {index}",
                lambda thread=thread, index=index: _join_thread(
                    thread,
                    2,
                    f"temp-file noise thread {index}",
                ),
            ))
        if self._thread is not None:
            steps.append((
                "join culprit thread",
                lambda: _join_thread(self._thread, 5, "temp-file culprit thread"),
            ))
        if self._bg_conn is not None:
            steps.append(("close culprit connection", self._bg_conn.close))
        steps.extend(
            (f"close noise connection {index}", conn.close)
            for index, conn in enumerate(self._noise_conns)
        )
        _run_cleanup_steps(
            f"Temp-file runtime cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._bg_conn = None
        self._thread = None
        self._noise_conns = []
        self._noise_threads = []

    def quiesce(self, context: FaultLifecycleContext):
        """Stop runtime sessions and remove non-persistable temp files."""
        import subprocess

        print(f"[FaultInjector:TempFileExplosion] quiesce...")
        self._stop_runtime(context)
        env = context.env
        pgdata = env.deployment.pgdata
        result = subprocess.run(
            [
                "docker", "exec", env.deployment.container_name, "bash", "-c",
                f"rm -f {pgdata}/base/pgsql_tmp/*",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to clean PostgreSQL temp files before snapshot: {result.stderr.strip()}"
            )

    def recover(self, context: FaultLifecycleContext):
        env = context.env
        print(f"[FaultInjector:TempFileExplosion] Recovering...")
        self._stop_runtime(context)
        if self._bg_pid is not None:
            _require_sql_success(
                env.execute_sql(
                    f"SELECT pg_terminate_backend({int(self._bg_pid)});"
                ),
                f"terminate temp-file culprit backend {self._bg_pid}",
            )
        _require_sql_success(
            env.execute_sql(f"DROP ROLE IF EXISTS {self.culprit_role};"),
            "recover temp-file culprit role",
        )
        self._bg_pid = None
        self._stop_event = None
        print(f"[FaultInjector:TempFileExplosion] Recovery complete.")


class PgSystemFailureTempFileExplosionScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_temp_file_explosion'
    description = 'Simulates write failures caused by one reporting batch spilling temp files amid normal production noise.'
    cases = (
        _PGSYSTEMFAILURETEMPFILEEXPLOSIONSCENARIO_CASE,
        _PGSYSTEMFAILURETEMPFILEEXPLOSIONSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgSystemFailureTempFileExplosionCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailureTempFileExplosionInjector,
                config={
                    'pgdata': case.pgdata,
                    'tmpfs_size_mb': case.tmpfs_size_mb,
                    'target_temp_mb': case.target_temp_mb,
                    'sort_rows': case.sort_rows,
                    'failure_probe_rows': case.failure_probe_rows,
                    'culprit_role': case.culprit_role,
                    'culprit_password': case.culprit_role,
                    'culprit_application': case.culprit_application,
                    'culprit_job': case.culprit_job,
                    'required_temp_file_limit': case.required_temp_file_limit,
                    'production_noise': case.production_noise,
                },
            ),
        )
