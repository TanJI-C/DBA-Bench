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
class PgSystemFailureConnectionStormCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    app_role: str
    app_password: str
    app_name_prefix: str
    pooler_app_prefix: str
    max_connections: int
    superuser_reserved_connections: int
    idle_connections: int
    idle_in_xact_connections: int
    noise_idle_connections: int
    mixed_business_idle_apps: tuple[str, ...]
    short_idle_in_xact_apps: tuple[str, ...]
    reporting_idle_connections: int
    monitoring_connections: int
    # checkout_pool_leak_simple：同源健康读池与 OP 受保护健康旁观会话。
    # 空元组时（case 0）注入器与验收行为与未启用该扩展时一致。
    healthy_pool_apps: tuple[str, ...] = ()
    preserved_bystander_apps: tuple[str, ...] = ()
    # checkout_pool_leak_simple：同域其他微服务的健康 idle 旁观连接。
    # 计入 OP preserved 名单的业务会话（非 SP 按名保护，误伤由 OP 修复范围拦截）。
    domain_idle_apps: tuple[str, ...] = ()
    # 计划会话安装后用同名池空闲连接补满普通槽，吸收管理面连接数浮动，保证溢出确定性。
    fill_to_exhaustion: bool = False

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureConnectionStormForCheckoutPoolIdleTransactionStormScenarioCase(PgSystemFailureConnectionStormCase):
    pass

_PGSYSTEMFAILURECONNECTIONSTORMSCENARIO_CASE = PgSystemFailureConnectionStormForCheckoutPoolIdleTransactionStormScenarioCase(
    case_id='checkout_pool_idle_transaction_storm',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "connection pool saturation",
                    "entity": "checkout_pool_idle_transaction_storm",
                    "evidence": [
                        "scripted diagnostic actions observed connection pool saturation"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "checkout pool idle transactions",
                    "entity": "checkout_pool_idle_transaction_storm",
                    "evidence": [
                        "scripted diagnostic actions observed checkout pool idle transactions"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "reporting and monitoring sessions are not root cause",
                    "entity": "checkout_pool_idle_transaction_storm",
                    "evidence": [
                        "scripted diagnostic actions observed reporting and monitoring sessions are not root cause"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "terminate leaked checkout pool sessions",
                    "entity": "checkout_pool_idle_transaction_storm",
                    "evidence": [
                        "scripted diagnostic actions observed terminate leaked checkout pool sessions"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "fix pool transaction lifecycle and timeouts",
                    "entity": "checkout_pool_idle_transaction_storm",
                    "evidence": [
                        "scripted diagnostic actions observed fix pool transaction lifecycle and timeouts"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "fix checkout pool lifecycle and configure session timeout"
            ],
            "verification": [
                "connection headroom was verified"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgSystemFailureConnectionStormForCheckoutPoolIdleTransactionStormEvaluatorCase,
    runtime=PostgresCaseRuntime(
        resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES,
        parameters=PostgresRuntimeSpec(
            parameters=(
                ('max_connections', '44'),
                ('superuser_reserved_connections', '4'),
                ('shared_preload_libraries', 'pg_stat_statements'),
            ),
        ),
    ),
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Simulates checkout web session pool transaction leakage hidden inside mixed retry traffic.',
    alert='Alert: Checkout p95 latency and 5xx are elevated. Payment callbacks, inventory reservation, and health checks are retrying intermittently; a subset of new database sessions fail while the PostgreSQL admin channel remains reachable. Diagnose the database-side contributor and restore checkout availability without restarting the instance.',
    initial_state={'status': 'unavailable_for_new_clients',
 'connection_slots': 'exhausted',
 'admin_channel': 'available'},
    expected_target={'status': 'recovered',
 'connection_slots': 'checkout_web_session_pool_idle_transactions_released',
 'long_term_plan': 'fix checkout web session pool transaction leak and set pool/session timeouts'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    app_role='checkout_app',
    app_password='checkout_app_pwd',
    app_name_prefix='checkout',
    pooler_app_prefix='checkout-web-rw',
    max_connections=44,
    superuser_reserved_connections=4,
    idle_connections=6,
    idle_in_xact_connections=11,
    noise_idle_connections=10,
    mixed_business_idle_apps=('inventory-reservation-worker-01',
 'payment-callback-dispatcher-02',
 'fraud-score-cache-refresh-01',
 'shipping-quote-prefetch-01'),
    short_idle_in_xact_apps=('inventory-reconcile-preview-01', 'payment-webhook-ack-sampler-01'),
    reporting_idle_connections=4,
    monitoring_connections=1,
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.45,
        reference_run_ids=(
            "reference-65__pg_system_failure_connection_storm__"
            "checkout_pool_idle_transaction_storm__mock__r001",
        ),
    ),
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureConnectionStormForCheckoutPoolLeakSimpleScenarioCase(
    PgSystemFailureConnectionStormCase
):
    pass


_PGSYSTEMFAILURECONNECTIONSTORMSCENARIO_SIMPLE_CASE = (
    PgSystemFailureConnectionStormForCheckoutPoolLeakSimpleScenarioCase(
        case_id='checkout_pool_leak_simple',
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "connection pool saturation",
                        "entity": "checkout_pool_leak_simple",
                        "evidence": [
                            "scripted diagnostic actions observed connection pool saturation"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "checkout pool idle transactions",
                        "entity": "checkout_pool_leak_simple",
                        "evidence": [
                            "scripted diagnostic actions observed checkout pool idle transactions"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "reporting and monitoring sessions are not root cause",
                        "entity": "checkout_pool_leak_simple",
                        "evidence": [
                            "scripted diagnostic actions observed reporting and monitoring sessions are not root cause"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "terminate leaked checkout pool sessions",
                        "entity": "checkout_pool_leak_simple",
                        "evidence": [
                            "scripted diagnostic actions observed terminate leaked checkout pool sessions"
                        ]
                    }
                ]
            },
            "outcome": {
                "changes": [
                    "fix checkout pool lifecycle and configure session timeout"
                ],
                "verification": [
                    "connection headroom was verified"
                ]
            },
            "summary": "The scripted mock completed its case-specific diagnosis and verification."
        },
        case_no=1,
        evaluator=PgSystemFailureConnectionStormForCheckoutPoolLeakSimpleEvaluatorCase,
        runtime=PostgresCaseRuntime(
            resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES,
            parameters=PostgresRuntimeSpec(
                parameters=(
                    # 普通槽 21（max_connections 25）。计划会话 18 后，
                    # filler 以 0..1 个会话吸收管理面超管会话（2..3）浮动并确认槽耗尽；峰值口径
                    # n = 普通槽 − 10 泄漏行 − 管理面连接数 ≤ 9，不受 filler 抬高；故障时算术为
                    # 21/25。autovacuum 继续关闭配合 fill_to_exhaustion。
                    ('max_connections', '25'),
                    ('superuser_reserved_connections', '4'),
                    ('shared_preload_libraries', 'pg_stat_statements'),
                    # 关闭 autovacuum：worker 不再浮动抢占普通槽，配合 fill_to_exhaustion
                    # 令注入后的连接槽耗尽状态确定可复现。
                    ('autovacuum', 'off'),
                ),
            ),
        ),
        difficulty=DifficultyCalibration(
            diagnostic_depth=3,
            environmental_complexity=0.421,
            reference_run_ids=(
                "reference-273__pg_system_failure_connection_storm__checkout_pool_leak_simple__mock__r001/attempts/001/trace.json",
            ),
        ),
        base_image_name='aiopsbench-pg-initialized:latest',
        workload_tag='initialized',
        title='A small checkout pool leaks idle transactions until ordinary connection slots fill.',
        alert=(
            'Alert: a single checkout API pool is rejecting new database sessions while the '
            'PostgreSQL admin channel remains reachable. Checkout web read traffic is currently '
            'healthy and must stay that way while the pool problem is fixed. A low-rate checkout '
            'status probe and a few unrelated payment/reporting sessions are also present. '
            'Identify the database-side contributor and restore new-session availability without '
            'restarting the instance.'
        ),
        initial_state={
            'status': 'degraded_for_new_clients',
            'connection_slots': 'ordinary_slots_exhausted',
            'admin_channel': 'available',
        },
        expected_target={
            'status': 'recovered',
            'connection_slots': 'checkout_pool_idle_transactions_released',
            'long_term_plan': 'fix pool transaction lifecycle and configure timeouts',
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=(
                WorkloadProfile(
                    name='checkout_status_health_probe',
                    sql='SELECT 1;',
                    qps=0.1,
                    tier='LIGHT',
                    application_name='checkout_status_probe',
                ),
            ),
            worker_count=1,
            seed=0x2F03,
            start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        ),
        app_role='checkout_app',
        app_password='checkout_app_pwd',
        app_name_prefix='checkout',
        pooler_app_prefix='checkout-web-rw',
        max_connections=25,
        superuser_reserved_connections=4,
        idle_connections=1,
        idle_in_xact_connections=10,
        # 支付侧竞争假设由 payment-callback-dispatcher-02 与
        # webhook-ack-sampler-01 承担。
        noise_idle_connections=0,
        mixed_business_idle_apps=('payment-callback-dispatcher-02',),
        # 支付侧 webhook ack 采样器（部分实例配置回滚）以短事务
        # decoy 在同窗保持 idle in transaction——同 state、数量 1、xact 年龄秒级、非 checkout
        # 前缀，构成可与成批泄漏池竞争的近邻假设；复用 case 0 的 decoy 线程机制。
        short_idle_in_xact_apps=('payment-webhook-ack-sampler-01',),
        reporting_idle_connections=1,
        monitoring_connections=1,
        healthy_pool_apps=('checkout-web-ro-00', 'checkout-web-ro-01', 'checkout-web-ro-02'),
        domain_idle_apps=(),
        preserved_bystander_apps=(
            'payment-callback-dispatcher-02',
            'reporting-dashboard-refresh-00',
            'synthetic-checkout-probe-00',
            'checkout-web-ro-00',
            'checkout-web-ro-01',
            'checkout-web-ro-02',
        ),
        fill_to_exhaustion=True,
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

class PgSystemFailureConnectionStormInjector(BaseFaultInjector):
    """
    模拟混合业务重试里的 checkout pooler idle-in-transaction 泄漏。
    注入器只制造真实 PostgreSQL 客户端连接，不修改共享环境工具。
    """

    def __init__(self):
        self._connections = []
        self._short_xact_stop_event = None
        self._short_xact_threads = []

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
        self.app_role = _validate_sql_identifier(config["app_role"], "app_role")
        self.app_password = config["app_password"]
        self.app_name_prefix = config["app_name_prefix"]
        self.pooler_app_prefix = config["pooler_app_prefix"]
        self.max_connections = int(config["max_connections"])
        self.superuser_reserved_connections = int(config["superuser_reserved_connections"])
        self.idle_connections = int(config["idle_connections"])
        self.idle_in_xact_connections = int(config["idle_in_xact_connections"])
        self.noise_idle_connections = int(config["noise_idle_connections"])
        self.mixed_business_idle_apps = tuple(config["mixed_business_idle_apps"])
        self.short_idle_in_xact_apps = tuple(config["short_idle_in_xact_apps"])
        self.healthy_pool_apps = tuple(config.get("healthy_pool_apps", ()))
        self.domain_idle_apps = tuple(config.get("domain_idle_apps", ()))
        self.fill_to_exhaustion = bool(config.get("fill_to_exhaustion", False))
        self.reporting_idle_connections = int(config["reporting_idle_connections"])
        self.monitoring_connections = int(config["monitoring_connections"])

    def _install_persistent_state(self) -> None:
        escaped_password = self.app_password.replace("'", "''")
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE ROLE {self.app_role} LOGIN PASSWORD '{escaped_password}';"
            ),
            "install connection-storm application role",
        )

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                "SELECT rolname, rolcanlogin FROM pg_roles "
                f"WHERE rolname = '{self.app_role}';"
            ),
            "verify connection-storm application role",
        )
        if payload["result"] != [[self.app_role, True]]:
            raise RuntimeError(
                f"Connection-storm fault image role mismatch: role={self.app_role}, "
                f"rows={payload['result']}"
            )

    def _activate_runtime(self) -> None:
        import threading
        import time

        self._connections = []
        self._short_xact_stop_event = threading.Event()
        self._short_xact_threads = []
        self._overflow_error = None

        print("[FaultInjector:ConnectionStorm] Clearing runtime leftovers...")
        self._cleanup_leftovers()
        self._seed_slow_query_noise()
        self._write_log_noise()

        target = (
            self.idle_connections
            + self.idle_in_xact_connections
            + self.noise_idle_connections
            + len(self.mixed_business_idle_apps)
            + len(self.short_idle_in_xact_apps)
            + len(self.healthy_pool_apps)
            + len(self.domain_idle_apps)
            + self.reporting_idle_connections
            + self.monitoring_connections
        )
        print(
            "[FaultInjector:ConnectionStorm] Opening "
            f"{target} mixed checkout connections against max_connections={self.max_connections}..."
        )

        for idx in range(self.idle_connections):
            conn = self._connect_app(f"{self.app_name_prefix}-api-{idx:02d}")
            conn.autocommit = True
            self._connections.append(conn)

        for idx in range(self.idle_in_xact_connections):
            conn = self._connect_app(f"{self.pooler_app_prefix}-{idx:02d}")
            conn.autocommit = False
            cur = conn.cursor()
            cur.execute("SELECT pg_backend_pid(), now();")
            cur.close()
            self._connections.append(conn)

        for idx in range(self.noise_idle_connections):
            conn = self._connect_app(f"{self.app_name_prefix}-payment-retry-{idx:02d}")
            conn.autocommit = True
            self._connections.append(conn)

        for app_name in self.mixed_business_idle_apps:
            conn = self._connect_app(app_name)
            conn.autocommit = True
            self._connections.append(conn)

        for app_name in self.short_idle_in_xact_apps:
            thread = threading.Thread(target=self._run_short_idle_xact_decoy, args=(app_name,), daemon=True)
            thread.start()
            self._short_xact_threads.append(thread)

        for app_name in self.healthy_pool_apps:
            conn = self._connect_app(app_name)
            conn.autocommit = True
            self._connections.append(conn)

        for app_name in self.domain_idle_apps:
            conn = self._connect_app(app_name)
            conn.autocommit = True
            self._connections.append(conn)

        for idx in range(self.reporting_idle_connections):
            conn = self._connect_app(f"reporting-dashboard-refresh-{idx:02d}")
            conn.autocommit = True
            self._connections.append(conn)

        for idx in range(self.monitoring_connections):
            conn = self._connect_app(f"synthetic-checkout-probe-{idx:02d}")
            conn.autocommit = True
            self._connections.append(conn)

        deadline = time.time() + 20
        while time.time() < deadline:
            if self._storm_observable():
                break
            time.sleep(0.5)
        if not self._storm_observable():
            raise RuntimeError("Connection storm did not become visible in pg_stat_activity")

        if self.fill_to_exhaustion:
            self._fill_to_exhaustion()

        self._overflow_error = self._try_overflow_connection()
        if not self._overflow_error:
            raise RuntimeError(
                "Connection storm did not trigger a normal-client connection failure; "
                "max_connections may not be low enough for this environment."
            )

        print(f"[FaultInjector:ConnectionStorm] Overflow error observed: {self._overflow_error}")
        print("[FaultInjector:ConnectionStorm] Fault injection complete.")

    def _connect_app(self, application_name: str):
        import psycopg2

        return psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.app_role,
            password=self.app_password,
            dbname=self.env.dbname,
            connect_timeout=3,
            application_name=application_name,
        )

    def _seed_slow_query_noise(self):
        noise_queries = {
            "nightly_revenue_rollup": """
                WITH revenue_bucket AS (
                  SELECT substring(md5(g::text || 'revenue'), 1, 2) AS bucket,
                         (g % 97)::numeric AS cents
                  FROM generate_series(1, 500000) AS g
                )
                SELECT bucket, count(*), sum(cents)
                FROM revenue_bucket
                GROUP BY bucket
                ORDER BY sum(cents) DESC
                LIMIT 20;
            """,
            "inventory_reservation_recount": """
                WITH reservation_scan AS (
                  SELECT substring(md5(g::text || 'inventory'), 1, 3) AS sku_bucket,
                         (g % 41) AS reserved_units
                  FROM generate_series(1, 500000) AS g
                )
                SELECT sku_bucket, count(*), sum(reserved_units)
                FROM reservation_scan
                GROUP BY sku_bucket
                ORDER BY count(*) DESC
                LIMIT 20;
            """,
            "settlement_callback_reconcile": """
                WITH callback_window AS (
                  SELECT substring(md5(g::text || 'settlement'), 1, 2) AS provider_bucket,
                         (g % 113)::numeric AS retry_cents
                  FROM generate_series(1, 500000) AS g
                )
                SELECT provider_bucket, count(*), sum(retry_cents)
                FROM callback_window
                GROUP BY provider_bucket
                ORDER BY sum(retry_cents) DESC
                LIMIT 20;
            """,
        }
        for label, sql in noise_queries.items():
            conn = self._connect_app(f"{label}-history")
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.close()

    def _write_log_noise(self):
        self.env.execute_sql(
            """
            DO $$
            BEGIN
              RAISE WARNING 'checkout synthetic probe timeout after 1500 ms';
              RAISE WARNING 'daily revenue dashboard refresh exceeded soft latency budget';
              RAISE WARNING 'payment callback retry queue depth above normal range';
            END $$;
            """
        )

    def _storm_observable(self) -> bool:
        payload = _json_object(
            self.env.execute_sql(
                f"""
                SELECT state, count(*)
                FROM pg_stat_activity
                WHERE usename = '{self.app_role}'
                GROUP BY state;
                """
            ),
            "read connection-storm session states",
        )
        if payload.get("status") == "error":
            raise RuntimeError(f"Could not read connection-storm session states: {payload}")
        counts = {row[0] or "null": int(row[1]) for row in payload["result"]}
        total = sum(counts.values())
        pooler_payload = _json_object(
            self.env.execute_sql(
                f"""
                SELECT count(*)
                FROM pg_stat_activity
                WHERE application_name LIKE '{self.pooler_app_prefix}%'
                  AND state = 'idle in transaction';
                """
            ),
            "read connection-storm pooler sessions",
        )
        if pooler_payload.get("status") == "error":
            raise RuntimeError(f"Could not read connection-storm pooler sessions: {pooler_payload}")
        pooler_idle_xact = int(pooler_payload["result"][0][0])
        return (
            total >= (
                self.idle_connections
                + self.idle_in_xact_connections
                + self.noise_idle_connections
                + len(self.mixed_business_idle_apps)
                + len(self.short_idle_in_xact_apps)
                + len(self.healthy_pool_apps)
                + len(self.domain_idle_apps)
                + self.reporting_idle_connections
                + self.monitoring_connections
            )
            and counts.get("idle", 0) >= self.idle_connections
            and pooler_idle_xact >= self.idle_in_xact_connections
        )

    def _fill_to_exhaustion(self) -> None:
        """计划会话安装后按同一业务池命名补满普通槽。

        管理面（env 管理、workload 探针、指标采样器）为超管会话且优先占用普通槽，其数量
        存在 ±1 浮动；补满后普通槽必然全满，溢出探测因此确定失败。补满连接全部为
        idle 的 checkout-api 池成员，属于可被合法回收的旁观会话，不进入 OP 保护名单。
        """
        expected = ("remaining connection slots", "too many clients", "too many connections")
        for index in range(self.idle_connections + 1, self.idle_connections + 10):
            try:
                conn = self._connect_app(f"{self.app_name_prefix}-api-{index:02d}")
            except Exception as exc:
                message = str(exc)
                if not any(fragment in message.lower() for fragment in expected):
                    raise
                print(
                    "[FaultInjector:ConnectionStorm] Slot exhaustion confirmed by filler "
                    f"connect failure after {index - self.idle_connections - 1} filler sessions."
                )
                return
            conn.autocommit = True
            self._connections.append(conn)
        raise RuntimeError(
            "Connection-storm filler top-up did not reach slot exhaustion; "
            "max_connections may leave too much ordinary-slot headroom."
        )

    def _try_overflow_connection(self) -> str:
        import psycopg2

        try:
            conn = self._connect_app(f"{self.app_name_prefix}_overflow_probe")
            conn.close()
            return ""
        except psycopg2.OperationalError as exc:
            message = str(exc)
            expected = ("remaining connection slots", "too many clients", "too many connections")
            if not any(fragment in message.lower() for fragment in expected):
                raise RuntimeError(
                    f"Connection overflow probe failed for an unrelated reason: {message}"
                ) from exc
            return message

    def _run_short_idle_xact_decoy(self, application_name: str):
        import psycopg2

        conn = self._connect_app(application_name)
        conn.autocommit = False
        self._connections.append(conn)
        try:
            while not self._short_xact_stop_event.is_set():
                cur = conn.cursor()
                cur.execute("SELECT pg_backend_pid(), 'short_business_callback_checkpoint', now();")
                cur.close()
                self._short_xact_stop_event.wait(2.0)
                conn.rollback()
        except psycopg2.OperationalError as exc:
            print(f"[FaultInjector:ConnectionStorm] Short idle transaction decoy ended: {exc}")

    def _cleanup_leftovers(self):
        _require_sql_success(
            self.env.execute_sql(
                f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE pid <> pg_backend_pid()
                  AND usename = '{self.app_role}';
                """
            ),
            "terminate connection-storm application sessions",
        )

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {
            "overflow_error": self._overflow_error,
            "session_states": env.execute_sql(
                "SELECT state, count(*) FROM pg_stat_activity "
                f"WHERE usename = '{self.app_role}' GROUP BY state ORDER BY state;"
            ),
        }

    def _stop_runtime(self, context: FaultLifecycleContext) -> None:
        if self._short_xact_stop_event is not None:
            self._short_xact_stop_event.set()
        steps = []
        for index, thread in enumerate(self._short_xact_threads):
            steps.append((
                f"join short transaction thread {index}",
                lambda thread=thread, index=index: _join_thread(
                    thread,
                    3,
                    f"connection-storm short transaction thread {index}",
                ),
            ))
        for index, conn in enumerate(self._connections):
            steps.append((f"close connection {index}", conn.close))
        steps.append(("terminate leftover server sessions", self._cleanup_leftovers))
        _run_cleanup_steps(
            f"Connection-storm runtime cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._connections = []
        self._short_xact_threads = []
        self._short_xact_stop_event = None

    def quiesce(self, context: FaultLifecycleContext):
        """Clean up background connections and threads for teardown."""
        print("[FaultInjector:ConnectionStorm] quiesce...")
        self._stop_runtime(context)

    def recover(self, context: FaultLifecycleContext):
        print("[FaultInjector:ConnectionStorm] Recovering...")
        self._stop_runtime(context)
        _require_sql_success(
            context.env.execute_sql(f"DROP ROLE IF EXISTS {self.app_role};"),
            "recover connection-storm application role",
        )
        print("[FaultInjector:ConnectionStorm] Recovery complete.")


class PgSystemFailureConnectionStormScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_connection_storm'
    description = 'Simulates checkout web session pool transaction leakage hidden inside mixed retry traffic.'
    cases = (
        _PGSYSTEMFAILURECONNECTIONSTORMSCENARIO_CASE,
        _PGSYSTEMFAILURECONNECTIONSTORMSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgSystemFailureConnectionStormCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailureConnectionStormInjector,
                config={
                    'app_role': case.app_role,
                    'app_password': case.app_password,
                    'app_name_prefix': case.app_name_prefix,
                    'pooler_app_prefix': case.pooler_app_prefix,
                    'max_connections': case.max_connections,
                    'superuser_reserved_connections': case.superuser_reserved_connections,
                    'idle_connections': case.idle_connections,
                    'idle_in_xact_connections': case.idle_in_xact_connections,
                    'noise_idle_connections': case.noise_idle_connections,
                    'mixed_business_idle_apps': case.mixed_business_idle_apps,
                    'short_idle_in_xact_apps': case.short_idle_in_xact_apps,
                    'healthy_pool_apps': case.healthy_pool_apps,
                    'domain_idle_apps': case.domain_idle_apps,
                    'fill_to_exhaustion': case.fill_to_exhaustion,
                    'reporting_idle_connections': case.reporting_idle_connections,
                    'monitoring_connections': case.monitoring_connections,
                },
            ),
        )
