from dataclasses import dataclass
from typing import List, Mapping

from src.scenarios.evaluation.postgres.system_failure import (
    PgSystemFailureConnectionBloatForCheckoutConnectionAndBloatEvaluatorCase,
    PgSystemFailureConnectionBloatForCheckoutBloatSingleBlockerSimpleEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    PostgresCaseRuntime,
    PostgresScenario,
    BackgroundWorkloadSpec,
    DifficultyCalibration,
    EMPTY_BACKGROUND_WORKLOAD,
    FaultPlan,
    CaseResourceSpec,
    PostgresScenarioCase,
)


POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureConnectionBloatCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    table: str
    app_role: str
    app_password: str
    worker_app_prefix: str
    blocker_app_name: str
    distractor_app_names: tuple[str, ...]
    max_connections: int
    superuser_reserved_connections: int
    worker_connections: int
    row_count: int
    dead_tuple_threshold: int
    diagnostic_query: str
    slow_queries: tuple[str, ...]
    distractor_app_names_2: tuple[str, ...]
    elder_decoy_app_name: str = ""
    decoy_table: str = ""
    decoy_row_count: int = 0
    orphan_prepared_gid: str = ""
    blocker_probe_tables: tuple[str, ...] = ()
    # easy only：常驻监控连接保留（SP 双层保护），健康业务表不注入；
    # hard case 保持默认空值，行为不变。
    monitor_app_name: str = ""
    healthy_tables: tuple[str, ...] = ()
    healthy_table_rows: tuple[int, ...] = ()

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureConnectionBloatForCheckoutConnectionAndBloatScenarioCase(PgSystemFailureConnectionBloatCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureConnectionBloatForCheckoutBloatSingleBlockerSimpleScenarioCase(PgSystemFailureConnectionBloatCase):
    pass

def build_connection_bloat_noise_profiles(table: str = "order_history") -> List[WorkloadProfile]:
    """Business-shaped SQL noise for the connection exhaustion and bloat scenario.

    The queries intentionally look like plausible report/index-tuning candidates,
    but they do not remediate the old-snapshot blocker. They run after the
    scenario table exists, so no TPC-DS workload is required.
    """
    return [
        WorkloadProfile(
            name="order_capacity_dashboard_rollup",
            sql=(
                "SELECT district_id, order_status, count(*) AS orders, "
                "coalesce(sum(amount), 0) AS gross_amount "
                f"FROM {table} "
                "WHERE updated_at > now() - interval '7 days' "
                "GROUP BY district_id, order_status "
                "ORDER BY gross_amount DESC, district_id "
                "LIMIT 20"
            ),
            qps=0.35,
            tier="MEDIUM",
        ),
        WorkloadProfile(
            name="payload_audit_rollup",
            sql=(
                "SELECT district_id, sum(length(payload)) AS payload_bytes "
                f"FROM {table} "
                "GROUP BY district_id "
                "ORDER BY payload_bytes DESC"
            ),
            qps=0.25,
            tier="MEDIUM",
        ),
        WorkloadProfile(
            name="billing_retry_visibility_probe",
            sql=(
                "SELECT pg_sleep(2.4), count(*) AS retry_candidates "
                f"FROM {table} "
                "WHERE order_status = 'OPEN'"
            ),
            qps=0.18,
            tier="SLOW_NOISE",
        ),
        WorkloadProfile(
            name="missing_settlement_rollup_log_noise",
            sql="SELECT count(*) FROM settlement_rollup_cache_missing;",
            qps=0.12,
            tier="LOG_NOISE",
        ),
    ]

def build_connection_bloat_decoy_profiles(decoy_table: str) -> List[WorkloadProfile]:
    """Same-domain SELECT churn look for the decoy bloated table (hard case).

    Keeps the decoy table visible as an actively used business table so the
    "biggest dead-tuple table is the culprit" hypothesis is plausible but
    excluded by the blocker's own evidence chain.
    """
    if not decoy_table:
        return []
    return [
        WorkloadProfile(
            name="fulfillment_backlog_probe",
            sql=(
                "SELECT district_id, count(*) AS backlog, "
                "sum(length(payload)) AS payload_bytes "
                f"FROM {decoy_table} "
                "GROUP BY district_id "
                "ORDER BY backlog DESC"
            ),
            qps=0.2,
            tier="MEDIUM",
        ),
    ]

_PGSYSTEMFAILURECONNECTIONBLOATSCENARIO_CASE = PgSystemFailureConnectionBloatForCheckoutConnectionAndBloatScenarioCase(
    case_id='checkout_connection_and_bloat',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "connection pool exhaustion",
                    "entity": "order_history",
                    "evidence": [
                        "observed connection pool exhaustion"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "dead tuple table bloat",
                    "entity": "order_history",
                    "evidence": [
                        "observed dead tuple table bloat"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "idle transaction holds old snapshot",
                    "entity": "order_history",
                    "evidence": [
                        "observed idle transaction holds old snapshot"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "orphaned prepared transaction also pins the vacuum horizon",
                    "entity": "order_history",
                    "evidence": [
                        "observed orphaned prepared transaction also pins the vacuum horizon"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "old snapshot causes bloat and connection exhaustion",
                    "entity": "order_history",
                    "evidence": [
                        "observed old snapshot causes bloat and connection exhaustion"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "terminate blocker then vacuum",
                    "entity": "order_history",
                    "evidence": [
                        "observed terminate blocker then vacuum"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "terminated the old-snapshot blocker, released the orphan prepared transaction, and vacuumed the bloated order table"
            ],
            "verification": [
                "old transaction, prepared xact, dead tuples, and worker connections cleared"
            ]
        },
        "summary": "An old snapshot and an orphan prepared transaction caused bloat, slow queries, and connection exhaustion."
    },
    case_no=0,
    evaluator=PgSystemFailureConnectionBloatForCheckoutConnectionAndBloatEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='default',
    title='Simulates connection saturation caused by slow scans over a bloated table whose cleanup is blocked by an old transaction.',
    alert='[CRITICAL] [PostgreSQL/Primary] The order service is intermittently failing to acquire new database sessions while existing requests are much slower than baseline. Investigate the saturation and restore normal service.',
    initial_state={'status': 'degraded',
 'new_connections': 'rejected',
 'existing_requests': 'slow',
 'table_cleanup': 'blocked'},
    expected_target={'status': 'recovered',
 'old_transaction': 'terminated',
 'vacuum': 'completed',
 'dead_tuples': 'low',
 'connection_slots': 'released'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_connection_bloat_noise_profiles('order_history')),
        # 单一 runner 池是 easy 的正常业务足迹，校准落在稳定侧。
        worker_count=1,
        seed=0xA10B,
    ),
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    table='order_history',
    app_role='order_app',
    app_password='order_app_pwd',
    worker_app_prefix='order_api_worker',
    blocker_app_name='finance_rollup_cursor',
    distractor_app_names=('finance_rollup_auditor', 'finance_stream_exporter', 'order_report_cursor', 'finance_close_probe', 'finance_reconciliation_cursor'),
    # 常驻 idle 邻居与常驻监控连接参与溢出拒绝算术：常驻后端全集
    # （12 worker + 5 邻居 + monitor + blocker + env 主连接 + sampler = 21）
    # 恰好占满 max_connections - superuser_reserved_connections，保持 worker
    # 全部连入、普通客户端溢出被拒；邻居会话与 blocker/elder 同属财务月结
    # 批会话家族。背景 runner
    # （AFTER_FAULTS 启动，1 池化连接）在溢出探针之后出现、agent 窗口内仍有余量。
    max_connections=25,
    superuser_reserved_connections=4,
    worker_connections=12,
    row_count=24000,
    dead_tuple_threshold=100,
    diagnostic_query=('SELECT district_id, order_status, sum(length(payload)) AS payload_bytes FROM order_history WHERE '
     "updated_at > now() - interval '7 days' GROUP BY district_id, order_status ORDER BY payload_bytes "
     'DESC;'),
    slow_queries=('SELECT district_id, order_status, sum(length(payload)) AS payload_bytes FROM order_history WHERE '
     "updated_at > now() - interval '7 days' GROUP BY district_id, order_status ORDER BY payload_bytes "
     'DESC;',),
    distractor_app_names_2=('finance_rollup_auditor', 'finance_stream_exporter', 'order_report_cursor', 'finance_close_probe', 'finance_reconciliation_cursor'),
    elder_decoy_app_name='finance_rollup_auditor',
    decoy_table='',
    decoy_row_count=0,
    orphan_prepared_gid='finance_rollup_batch_close_2026w37',
    blocker_probe_tables=('order_history',),
    # easy：监控连接保留（SP 双层保护），健康业务表不注入（单目标表膨胀绑定形态）。
    monitor_app_name='order_capacity_monitor',
    healthy_tables=(),
    healthy_table_rows=(),
    # 校准（稳定口径：结构性预算只建立在 pga/pgst/prepared 的稳定行计数上）：
    # D_s=4，pga 13/8、pgst 1/0、prepared 1/0
    # → m=15/n=8，rho=15/23≈0.652，C_s≈0.348 <0.5 → 标签 easy。
    # query_metrics.active_connections 的点计数随 install/bootstrap 时长波动
    # （负载下实测 16/4、3/14、5/15，Qm 口径 C_s 0.279-0.55），不作为
    # 结构性预算。结构性计数在不同 run 间逐字节一致。
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.348,
        reference_run_ids=(
            'reference-255__pg_system_failure_connection_bloat__checkout_connection_and_bloat__mock__r001',
            'reference-256__pg_system_failure_connection_bloat__checkout_connection_and_bloat__mock__r001',
            'reference-257__pg_system_failure_connection_bloat__checkout_connection_and_bloat__mock__r001',
        ),
    ),
)

_PGSYSTEMFAILURECONNECTIONBLOAT_SIMPLE_CASE = PgSystemFailureConnectionBloatForCheckoutBloatSingleBlockerSimpleScenarioCase(
    case_id='checkout_bloat_single_blocker_simple',
    case_no=1,
    evaluator=PgSystemFailureConnectionBloatForCheckoutBloatSingleBlockerSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='A focused connection exhaustion case with one old snapshot blocker and one reporting decoy.',
    alert='[SEV2] [PostgreSQL/Primary] Checkout requests intermittently fail to get database sessions, and existing requests are slower than baseline. Storage growth on one order-history table is above trend. Restore service without terminating unrelated report sessions.',
    initial_state={'status': 'degraded', 'new_connections': 'rejected', 'existing_requests': 'slow', 'table_cleanup': 'blocked'},
    expected_target={'status': 'recovered', 'old_transaction': 'terminated', 'vacuum': 'completed', 'dead_tuples': 'low', 'connection_slots': 'released'},
    background_workload=BackgroundWorkloadSpec(
        profiles=(
            tuple(build_connection_bloat_noise_profiles('order_history_simple')[:1])
            + tuple(build_connection_bloat_decoy_profiles('fulfillment_events_simple'))
        ),
        worker_count=1,
        seed=0x6101,
    ),
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    table='order_history_simple',
    app_role='order_app_simple',
    app_password='order_app_pwd',
    worker_app_prefix='order_api_simple_worker',
    blocker_app_name='settlement_simple_reporter',
    distractor_app_names=('settlement_simple_audit_reader', 'settlement_simple_report_cursor', 'settlement_simple_batch_consumer'),
    # elder decoy 与 batch consumer 各占一个常驻会话，计入 max_connections 算术，
    # 保持“常规槽位被故障会话与 worker 恰好占满、普通客户端溢出被拒”的算术。
    max_connections=16,
    superuser_reserved_connections=4,
    worker_connections=6,
    row_count=6000,
    dead_tuple_threshold=80,
    diagnostic_query="SELECT district_id, order_status, sum(length(payload)) AS payload_bytes FROM order_history_simple WHERE updated_at > now() - interval '7 days' GROUP BY district_id, order_status ORDER BY payload_bytes DESC;",
    slow_queries=("SELECT district_id, order_status, sum(length(payload)) AS payload_bytes FROM order_history_simple WHERE updated_at > now() - interval '7 days' GROUP BY district_id, order_status ORDER BY payload_bytes DESC;",),
    distractor_app_names_2=('settlement_simple_audit_reader', 'settlement_simple_report_cursor', 'settlement_simple_batch_consumer'),
    elder_decoy_app_name='settlement_simple_report_cursor',
    decoy_table='fulfillment_events_simple',
    decoy_row_count=9000,
    orphan_prepared_gid='settlement_batch_close_2026w37',
    # blocker 事务先后扫过两张表、最后停在干扰表上，切断“last_query=受影响表”的捷径。
    blocker_probe_tables=('order_history_simple', 'fulfillment_events_simple'),
    reference_report=_PGSYSTEMFAILURECONNECTIONBLOATSCENARIO_CASE.reference_report,
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.657,
        reference_run_ids=('run_pg_conn_bloat_mock_r02c__pg_system_failure_connection_bloat__checkout_bloat_single_blocker_simple__mock__r001',),
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

class PgSystemFailureConnectionBloatInjector(BaseFaultInjector):
    """
    模拟连接槽耗尽 -> 慢业务扫描 -> 表膨胀 -> 旧事务阻塞 VACUUM 的因果链。
    所有可见对象使用中性业务命名；根因通过 pg_stat_activity 的状态、
    backend_xmin/xact_start 和 pg_stat_user_tables 的 dead tuples 暴露。
    同一窗口内的非因果观测：同形 idle 事务邻居与 autocommit 空闲的常驻监控
    连接（健康业务表不注入）——全部可由 backend_xmin/
    事务状态与死元组规模排除。
    """

    def __init__(self):
        self.env = None
        self._stop_event = None
        self._threads = []
        self._connections = []
        self._blocker_conn = None
        self._elder_decoy_conn = None
        self._monitor_conn = None
        self._distractor_connections = []
        self._overflow_error = ""

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        import threading
        import time
        self.env = env
        self._apply_config(config)
        self.baseline_active_connections = env.query_metrics("active_connections")

        print("[FaultInjector:ConnectionBloat] Preparing connection/bloat fault...")
        self._stop_runtime_sessions(context)
        _require_sql_success(
            env.execute_sql(
                f"DROP TABLE IF EXISTS {self.table}; "
                f"DROP ROLE IF EXISTS {self.app_role};"
            ),
            "reset connection-bloat persistent objects before install",
        )

        with env.metrics_hidden(allow_pgss_reset=True):
            self._start_elder_decoy()
            self._prepare_objects()
            self._prepare_orphan_xact()
            self._start_blocking_snapshot()
            self._start_idle_distractors()
            self._start_monitor_session()
            self._prime_elder_decoy_snapshot()
            self._generate_dead_tuples()
            self._scrub_pg_stat_statements()

        self._start_worker_threads()

        deadline = time.time() + 20
        while time.time() < deadline:
            if self._fault_observable():
                break
            time.sleep(0.5)
        if not self._fault_observable():
            raise RuntimeError("Connection/bloat fault did not become observable")

        self._overflow_error = self._try_overflow_connection()
        if not self._overflow_error:
            raise RuntimeError("Normal client connection was not rejected; max_connections may be too high")

        print(f"[FaultInjector:ConnectionBloat] Overflow error observed: {self._overflow_error}")
        print("[FaultInjector:ConnectionBloat] Fault injection complete.")

    def _apply_config(self, config: dict):
        self.table = _validate_sql_identifier(config['table'], "table")
        self.app_role = _validate_sql_identifier(config['app_role'], "app_role")
        self.app_password = config['app_password']
        self.worker_app_prefix = _validate_sql_identifier(
            config['worker_app_prefix'],
            "worker_app_prefix",
        )
        self.blocker_app_name = _validate_sql_identifier(
            config['blocker_app_name'],
            "blocker_app_name",
        )
        self.distractor_app_names = [
            _validate_sql_identifier(name, "distractor_app_name")
            for name in config['distractor_app_names']
        ]
        self.elder_decoy_app_name = (
            _validate_sql_identifier(config['elder_decoy_app_name'], "elder_decoy_app_name")
            if config.get('elder_decoy_app_name')
            else ''
        )
        self.decoy_table = (
            _validate_sql_identifier(config['decoy_table'], "decoy_table")
            if config.get('decoy_table')
            else ''
        )
        self.decoy_row_count = int(config.get('decoy_row_count', 0) or 0)
        self.orphan_prepared_gid = str(config.get('orphan_prepared_gid', '') or '')
        self.blocker_probe_tables = tuple(
            _validate_sql_identifier(name, "blocker_probe_table")
            for name in (config.get('blocker_probe_tables') or ())
        )
        # easy only：健康业务表与常驻监控连接；缺省为空，hard case 行为不变。
        self.monitor_app_name = (
            _validate_sql_identifier(config['monitor_app_name'], "monitor_app_name")
            if config.get('monitor_app_name')
            else ''
        )
        self.healthy_tables = tuple(
            _validate_sql_identifier(name, "healthy_table")
            for name in (config.get('healthy_tables') or ())
        )
        self.healthy_table_rows = tuple(
            int(rows) for rows in (config.get('healthy_table_rows') or ())
        )
        if len(self.healthy_table_rows) != len(self.healthy_tables):
            raise ValueError(
                "healthy_table_rows must align with healthy_tables: "
                f"tables={self.healthy_tables}, rows={self.healthy_table_rows}"
            )
        self.worker_connections = int(config['worker_connections'])
        self.row_count = int(config['row_count'])
        self.dead_tuple_threshold = int(config['dead_tuple_threshold'])
        self.diagnostic_query = config['diagnostic_query']

    def _start_worker_threads(self):
        import threading

        self._stop_event = threading.Event()
        self._threads = []
        for idx in range(self.worker_connections):
            ready = threading.Event()
            thread = threading.Thread(
                target=self._run_order_worker,
                args=(idx, ready),
                daemon=True,
            )
            thread.start()
            self._threads.append(thread)
            if not ready.wait(timeout=10):
                raise RuntimeError(f"Order worker {idx} did not start within 10s")

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        active = env.query_metrics("active_connections")
        dead_tuples = env.query_metrics("dead_tuples", tables=self.table)
        if not self._overflow_error:
            raise RuntimeError("Connection-bloat overflow rejection evidence is missing")
        return {
            "baseline_active_connections": self.baseline_active_connections,
            "active_connections": active,
            "dead_tuples": dead_tuples,
            "backend_states": env.execute_sql(
                "SET statement_timeout = '5s'; "
                "SELECT application_name, state, count(*) FROM pg_stat_activity "
                f"WHERE application_name LIKE '{self.worker_app_prefix}%' "
                f"OR application_name = '{self.blocker_app_name}' "
                "GROUP BY application_name, state ORDER BY application_name, state;"
            ),
            "overflow_error": self._overflow_error,
        }

    def quiesce(self, context: FaultLifecycleContext):
        self._stop_runtime_sessions(context)
        # 快照流（save/auto）中 prepared xact 不能进入镜像：activate 会重建它，
        # 残留的旧 gid 会让 PREPARE TRANSACTION 因 gid 冲突失败。
        self._rollback_orphan_xact("quiesce")

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        import time

        self.env = env
        self._apply_config(config)
        self.baseline_active_connections = env.query_metrics("active_connections")
        with env.metrics_hidden(allow_pgss_reset=True):
            self._verify_persistent_state()
            self._stop_runtime_sessions(context)
            self._start_elder_decoy()
            self._prepare_orphan_xact()
            self._start_blocking_snapshot()
            self._start_idle_distractors()
            self._start_monitor_session()
            self._prime_elder_decoy_snapshot()
            self._generate_dead_tuples()
            self._scrub_pg_stat_statements()

        self._start_worker_threads()
        deadline = time.time() + 20
        while time.time() < deadline:
            if self._fault_observable():
                break
            time.sleep(0.5)
        if not self._fault_observable():
            raise RuntimeError("Connection/bloat fault did not become observable from fault image")

        self._overflow_error = self._try_overflow_connection()
        if not self._overflow_error:
            raise RuntimeError("Normal client connection was not rejected after fault image activation")

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT to_regclass('public.{self.table}')::text, "
                f"(SELECT count(*) FROM {self.table}), "
                f"EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{self.app_role}');"
            ),
            "verify connection/bloat fault image",
        )
        table_name, row_count, role_exists = payload["result"][0]
        if (
            table_name != self.table
            or int(row_count) != self.row_count
            or role_exists is not True
        ):
            raise RuntimeError(
                f"Connection/bloat fault image does not match the Case: table={table_name}, "
                f"row_count={row_count}, expected_rows={self.row_count}, role_exists={role_exists}"
            )

    def _prepare_objects(self):
        self._cleanup_sessions(include_elder=False)
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table};")
        self.env.execute_sql(f"DROP ROLE IF EXISTS {self.app_role};")
        app_password_sql = str(self.app_password).replace("'", "''")
        self.env.execute_sql(f"CREATE ROLE {self.app_role} LOGIN PASSWORD '{app_password_sql}';")
        self.env.execute_sql(
            f"""
            CREATE TABLE {self.table} (
                order_id integer PRIMARY KEY,
                district_id integer NOT NULL,
                order_status text NOT NULL,
                amount numeric(12,2) NOT NULL,
                payload text NOT NULL,
                updated_at timestamptz NOT NULL DEFAULT now()
            );
            """
        )
        self.env.execute_sql(
            f"""
            INSERT INTO {self.table} (order_id, district_id, order_status, amount, payload)
            SELECT g,
                   (g % 10) + 1,
                   CASE WHEN g % 3 = 0 THEN 'OPEN' ELSE 'PAID' END,
                   (g % 1000)::numeric / 10.0,
                   repeat(md5(g::text), 16)
            FROM generate_series(1, {self.row_count}) AS g;
            """
        )
        self.env.execute_sql(f"GRANT SELECT ON {self.table} TO {self.app_role};")
        self.env.execute_sql(f"ANALYZE {self.table};")
        if self.decoy_table:
            self.env.execute_sql(
                f"""
                CREATE TABLE {self.decoy_table} (
                    event_id integer PRIMARY KEY,
                    district_id integer NOT NULL,
                    channel text NOT NULL,
                    payload text NOT NULL,
                    updated_at timestamptz NOT NULL DEFAULT now()
                );
                """
            )
            self.env.execute_sql(
                f"""
                INSERT INTO {self.decoy_table} (event_id, district_id, channel, payload)
                SELECT g,
                       (g % 8) + 1,
                       CASE WHEN g % 4 = 0 THEN 'RETRY' ELSE 'NORMAL' END,
                       repeat(md5((g * 7)::text), 12)
                FROM generate_series(1, {self.decoy_row_count}) AS g;
                """
            )
            self.env.execute_sql(f"GRANT SELECT ON {self.decoy_table} TO {self.app_role};")
            self.env.execute_sql(f"ANALYZE {self.decoy_table};")
        self._create_healthy_tables()

    def _create_healthy_tables(self):
        """创建配置注入的同域健康业务表（配置驱动能力，当前 Case 配置为空不再使用）。

        业务语义：订单库同时存在结算缓存、退款暂存、汇率快照等多张业务表，
        填充 pg_stat_user_tables 的同窗口竞争观测。healthy_tables 为空时
        无操作，hard case 行为始终不变。
        """
        for table, rows in zip(self.healthy_tables, self.healthy_table_rows):
            self.env.execute_sql(f"DROP TABLE IF EXISTS {table};")
            self.env.execute_sql(
                f"""
                CREATE TABLE {table} (
                    item_id integer PRIMARY KEY,
                    district_id integer NOT NULL,
                    status text NOT NULL,
                    amount numeric(12,2) NOT NULL,
                    updated_at timestamptz NOT NULL DEFAULT now()
                );
                """
            )
            self.env.execute_sql(
                f"""
                INSERT INTO {table} (item_id, district_id, status, amount)
                SELECT g,
                       (g % 10) + 1,
                       CASE WHEN g % 4 = 0 THEN 'DONE' ELSE 'POSTED' END,
                       (g % 500)::numeric / 10.0
                FROM generate_series(1, {rows}) AS g;
                """
            )
            self.env.execute_sql(f"GRANT SELECT ON {table} TO {self.app_role};")
            self.env.execute_sql(f"VACUUM {table};")
            self.env.execute_sql(f"ANALYZE {table};")

    def _start_monitor_session(self):
        """easy only：常驻订单容量监控连接，autocommit 空闲（非 idle in transaction）。

        业务语义：监控 poller 两次轮询之间持有的池化连接。它不处于事务中，
        xact_start/backend_xmin 均为 NULL，不持有任何快照，不阻塞 VACUUM；
        与 idle in transaction 邻居构成不同排除路径的噪声形态（state='idle'）。
        误杀它属于真实运维事故（观测能力丢失），由 SP 保护清单兜底。
        """
        if not self.monitor_app_name:
            return
        import psycopg2

        self._monitor_conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.app_role,
            password=self.app_password,
            dbname=self.env.dbname,
            connect_timeout=5,
            application_name=self.monitor_app_name,
        )
        self._monitor_conn.autocommit = True
        cur = self._monitor_conn.cursor()
        cur.execute(
            f"SELECT count(*) FROM {self.table} WHERE updated_at > now() - interval '5 minutes';"
        )
        cur.fetchall()
        cur.close()

    def _start_blocking_snapshot(self):
        import psycopg2

        self._blocker_conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=5,
            application_name=self.blocker_app_name,
        )
        self._blocker_conn.autocommit = False
        cur = self._blocker_conn.cursor()
        cur.execute("BEGIN ISOLATION LEVEL REPEATABLE READ;")
        # 报表事务先后扫描多张表，last_query 停在最后一张上；
        # 受影响表的绑定证据必须来自 worker 慢查询/业务症状，而不是 last_query。
        for probe_table in (self.blocker_probe_tables or (self.table,)):
            cur.execute(f"SELECT count(*) FROM {probe_table};")
            cur.fetchall()
        cur.close()

    def _prepare_orphan_xact(self):
        """遗留一个孤儿 prepared transaction，作为第二个 horizon 持有者。

        业务语义：两阶段提交的批处理在提交前崩溃，PREPARE TRANSACTION 之后连接断开，
        事务的快照与锁被集群永久持有。它在 pg_stat_activity 中不可见，只能通过
        pg_prepared_xacts 发现，用 ROLLBACK PREPARED/COMMIT PREPARED 释放。
        """
        if not self.orphan_prepared_gid:
            return
        import psycopg2

        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=5,
        )
        conn.autocommit = False
        try:
            cur = conn.cursor()
            cur.execute("BEGIN;")
            cur.execute(f"SELECT count(*) FROM {self.table};")
            cur.fetchall()
            gid = self.orphan_prepared_gid.replace("'", "''")
            cur.execute(f"PREPARE TRANSACTION '{gid}';")
            cur.close()
        finally:
            # PREPARE TRANSACTION 之后连接必须关闭：事务所有权已移交给集群。
            conn.close()

    def _prepared_xact_present(self) -> bool:
        if not self.orphan_prepared_gid:
            return False
        gid = self.orphan_prepared_gid.replace("'", "''")
        payload = _json_object(
            self.env.execute_sql(
                "SELECT count(*) FROM pg_prepared_xacts "
                f"WHERE gid = '{gid}';"
            ),
            "check orphan prepared xact",
        )
        return int(payload["result"][0][0] or 0) >= 1

    def _rollback_orphan_xact(self, context_label: str):
        if not self.orphan_prepared_gid:
            return
        if not self._prepared_xact_present():
            return
        # ROLLBACK PREPARED 不能在事务块内执行，必须作为顶层语句单独下发。
        gid = self.orphan_prepared_gid.replace("'", "''")
        _require_sql_success(
            self.env.execute_sql(f"ROLLBACK PREPARED '{gid}';"),
            f"rollback orphan prepared xact during {context_label}",
        )

    def _start_elder_decoy(self):
        """Open the elder decoy session before any other fault state exists.

        业务语义：一个常驻的批处理游标会话比肇事会话更早开启事务，因此 xact_start
        更老、看起来最可疑；但它使用默认 READ COMMITTED，空闲期不持有快照，
        backend_xmin 为空，不阻塞 VACUUM。真正的判别证据是 backend_xmin，而不是
        会话/事务时长。
        """
        if not self.elder_decoy_app_name:
            return
        import psycopg2

        self._elder_decoy_conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=5,
            application_name=self.elder_decoy_app_name,
        )
        self._elder_decoy_conn.autocommit = False
        cur = self._elder_decoy_conn.cursor()
        cur.execute("BEGIN;")
        cur.close()

    def _prime_elder_decoy_snapshot(self):
        """Give the elder decoy its last business query against the target table.

        READ COMMITTED 下该语句只在执行期持有快照，语句结束后释放；事务保持
        idle in transaction，因此它在 pg_stat_activity 里与 blocker 形态一致，
        只有 backend_xmin 列能区分两者。
        """
        if self._elder_decoy_conn is None:
            return
        cur = self._elder_decoy_conn.cursor()
        cur.execute(
            f"SELECT count(*) FROM {self.table} WHERE order_status = 'PAID';"
        )
        cur.fetchall()
        cur.close()

    def _start_idle_distractors(self):
        """Create idle transactions that look related but do not block VACUUM."""
        import psycopg2

        self._distractor_connections = []
        queries = [
            f"SELECT count(*) FROM {self.table} WHERE order_status = 'OPEN';",
            f"SELECT district_id, count(*) FROM {self.table} GROUP BY district_id;",
            f"SELECT max(updated_at) FROM {self.table};",
        ]
        # healthy_tables 配置注入时追加以各业务表为最后查询目标的同形 idle 邻居；
        # 邻居 last_query 随配置变化，判别证据仍是 backend_xmin，而不是查询文本。
        for idx, healthy_table in enumerate(self.healthy_tables):
            if idx % 2 == 0:
                queries.append(f"SELECT count(*) FROM {healthy_table};")
            else:
                queries.append(f"SELECT max(updated_at) FROM {healthy_table};")
        live_distractors = [
            name for name in getattr(self, "distractor_app_names", [])
            if name != self.elder_decoy_app_name
        ]
        for idx, app_name in enumerate(live_distractors):
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.app_role,
                password=self.app_password,
                dbname=self.env.dbname,
                connect_timeout=5,
                application_name=app_name,
            )
            conn.autocommit = False
            cur = conn.cursor()
            cur.execute("BEGIN;")
            cur.execute(queries[idx % len(queries)])
            cur.close()
            self._distractor_connections.append(conn)

    def _generate_dead_tuples(self):
        self.env.execute_sql(
            f"""
            UPDATE {self.table}
            SET order_status = CASE WHEN order_status = 'OPEN' THEN 'PAID' ELSE 'OPEN' END,
                updated_at = now()
            WHERE order_id <= {self.row_count};
            """
        )
        if self.decoy_table:
            # 两轮翻转让干扰表的死元组数与 dead_ratio 都高于目标表，形成
            # “死元组最多的表才是元凶”的位移假设；其真实成因是持续 UPDATE 搅动。
            self.env.execute_sql(
                f"""
                UPDATE {self.decoy_table}
                SET channel = CASE WHEN channel = 'RETRY' THEN 'NORMAL' ELSE 'RETRY' END,
                    updated_at = now()
                WHERE event_id <= {self.decoy_row_count};
                """
            )
            self.env.execute_sql(
                f"""
                UPDATE {self.decoy_table}
                SET payload = repeat(md5((event_id * 13)::text), 14)
                WHERE event_id <= {self.decoy_row_count};
                """
            )
        self.env.execute_sql(f"VACUUM {self.table};")
        self.env.execute_sql(f"ANALYZE {self.table};")
        if self.decoy_table:
            self.env.execute_sql(f"VACUUM {self.decoy_table};")
            self.env.execute_sql(f"ANALYZE {self.decoy_table};")
        self._generate_healthy_table_churn()

    def _generate_healthy_table_churn(self):
        """健康表遗留死元组的搅动步（配置驱动能力，healthy_tables 为空时无操作）。

        业务语义：退款暂存表遗留一小批已完成批量的死元组（horizon 被钉住期间
        同样不可回收），构成"健康但局部异常"的近邻观测。
        """
        if len(self.healthy_tables) < 2:
            return
        churn_table = self.healthy_tables[1]
        self.env.execute_sql(
            f"""
            UPDATE {churn_table}
            SET status = CASE WHEN status = 'DONE' THEN 'POSTED' ELSE 'DONE' END,
                updated_at = now()
            WHERE item_id <= 40;
            """
        )

    def _connect_app(self, application_name: str):
        import psycopg2

        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.app_role,
            password=self.app_password,
            dbname=self.env.dbname,
            connect_timeout=3,
            application_name=application_name,
        )
        conn.autocommit = True
        return conn

    def _run_order_worker(self, idx: int, ready_event):
        import time

        conn = None
        try:
            conn = self._connect_app(f"{self.worker_app_prefix}_{idx:02d}")
            self._connections.append(conn)
            ready_event.set()
            with conn.cursor() as cur:
                # 语句超时为 2s。孤儿 prepared xact 存在期间所有新快照
                # 都会被污染（xmin 停在其回收线）；过长的在途查询会把污染带进修复后的
                # VACUUM 窗口，使 OP 对任何正确修复都不确定。2s 保证污染查询在修复后
                # 最多 2s 内自然结束，dead_tuples_low 的 Eventually 验收窗口（8x1s）
                # 可以覆盖。
                cur.execute("SET statement_timeout = '2s';")
                while self._stop_event is not None and not self._stop_event.is_set():
                    dead_tuples = self._dead_tuples_from_cursor(cur)
                    if dead_tuples <= self.dead_tuple_threshold:
                        break
                    try:
                        cur.execute(self.diagnostic_query)
                        cur.fetchall()
                    except Exception:
                        try:
                            conn.rollback()
                        except Exception:
                            pass
                    time.sleep(0.2)
        except Exception as exc:
            print(f"[FaultInjector:ConnectionBloat] Worker {idx} stopped: {exc}")
            ready_event.set()
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _dead_tuples_from_cursor(self, cur) -> int:
        cur.execute(
            "SELECT COALESCE(n_dead_tup, 0) "
            "FROM pg_stat_user_tables "
            f"WHERE relname = '{self.table}';"
        )
        row = cur.fetchone()
        return int(row[0] or 0) if row else 0

    def _fault_observable(self) -> bool:
        payload = _json_object(self.env.execute_sql(
            f"""
            SET statement_timeout = '5s';
            SELECT
                (SELECT count(*) FROM pg_stat_activity
                 WHERE application_name = '{self.blocker_app_name}'
                   AND state = 'idle in transaction'
                   AND backend_xmin IS NOT NULL
                   AND pid <> pg_backend_pid()) AS blockers,
                (SELECT COALESCE(n_dead_tup, 0)
                 FROM pg_stat_user_tables
                 WHERE relname = '{self.table}') AS dead_tuples,
                (SELECT count(*) FROM pg_stat_activity
                 WHERE application_name LIKE '{self.worker_app_prefix}%') AS workers;
            """
        ), "read connection-bloat observability")
        row = payload["result"][0]
        blockers = int(row[0] or 0)
        dead_tuples = int(row[1] or 0)
        workers = int(row[2] or 0)
        observable = (
            blockers >= 1
            and dead_tuples > self.dead_tuple_threshold
            and workers >= self.worker_connections
        )
        if observable and self.orphan_prepared_gid:
            # 第二 horizon 持有者就位才算注入完整。
            observable = self._prepared_xact_present()
        return observable

    def _try_overflow_connection(self) -> str:
        try:
            conn = self._connect_app(f"{self.worker_app_prefix}_overflow_probe")
            conn.close()
            return ""
        except Exception as exc:
            return str(exc)

    def _cleanup_sessions(self, include_elder: bool = True):
        names = list(self.distractor_app_names)
        if not include_elder and getattr(self, "elder_decoy_app_name", ""):
            # elder decoy 在 install 中先于建表开启长事务，_prepare_objects 的
            # 重置清理不能把它一并终止。
            names = [name for name in names if name != self.elder_decoy_app_name]
        monitor_app = getattr(self, "monitor_app_name", "")
        if monitor_app and monitor_app not in names:
            # 常驻监控连接同属 Case 注入状态，恢复/重置时必须一并清理，
            # 不能泄漏进 fault snapshot 或后续运行。
            names.append(monitor_app)
        array_sql = (
            f"ARRAY[{self._distractor_app_sql_literals(names)}]"
            if names
            else "ARRAY[]::text[]"
        )
        _require_sql_success(
            self.env.execute_sql(
                f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE pid <> pg_backend_pid()
                  AND (
                    application_name LIKE '{getattr(self, "worker_app_prefix", "order_api_worker")}%'
                    OR application_name = '{getattr(self, "blocker_app_name", "settlement_reporter")}'
                    OR application_name = ANY({array_sql})
                  );
                """
            ),
            "terminate connection-bloat sessions",
        )

    def _distractor_app_sql_literals(self, names=None) -> str:
        names = self.distractor_app_names if names is None else names
        if not names:
            return ""
        return ", ".join(
            "'" + str(name).replace("'", "''") + "'"
            for name in names
        )

    def _scrub_pg_stat_statements(self):
        _require_sql_success(
            self.env.execute_sql(
                "SET pg_stat_statements.track = 'none'; "
                "SELECT pg_stat_statements_reset(); "
                "RESET pg_stat_statements.track;"
            ),
            "reset pg_stat_statements for connection-bloat scenario",
        )
        self.env._snapshot_pgss_baseline()

    def recover(self, context: FaultLifecycleContext):
        self.env = context.env
        self._apply_config(context.config)
        print("[FaultInjector:ConnectionBloat] Recovering...")
        self._stop_runtime_sessions(context)
        if not self.env.reconnect():
            raise RuntimeError(
                f"Connection-bloat recovery could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        # 孤儿 prepared xact 持有目标表的 AccessShare 锁与快照，必须先释放，
        # 否则后续 VACUUM/DROP 会被无限期阻塞。
        self._rollback_orphan_xact("recovery")
        _require_sql_success(
            self.env.execute_sql(f"VACUUM {self.table};"),
            f"vacuum recovered connection-bloat table {self.table}",
        )
        _require_sql_success(
            self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table};"),
            f"drop connection-bloat table {self.table}",
        )
        if self.decoy_table:
            _require_sql_success(
                self.env.execute_sql(f"DROP TABLE IF EXISTS {self.decoy_table};"),
                f"drop connection-bloat decoy table {self.decoy_table}",
            )
        for healthy_table in getattr(self, "healthy_tables", ()):
            _require_sql_success(
                self.env.execute_sql(f"DROP TABLE IF EXISTS {healthy_table};"),
                f"drop connection-bloat healthy table {healthy_table}",
            )
        _require_sql_success(
            self.env.execute_sql(f"DROP ROLE IF EXISTS {self.app_role};"),
            f"drop connection-bloat role {self.app_role}",
        )
        print("[FaultInjector:ConnectionBloat] Recovery complete.")

    def _stop_runtime_sessions(self, context: FaultLifecycleContext):
        if self._stop_event is not None:
            self._stop_event.set()
        steps = []
        if self._blocker_conn is not None:
            steps.append(("close blocker connection", self._blocker_conn.close))
        if self._elder_decoy_conn is not None:
            steps.append(("close elder decoy connection", self._elder_decoy_conn.close))
        for index, conn in enumerate(self._distractor_connections):
            steps.append((f"close distractor connection {index}", conn.close))
        if getattr(self, "_monitor_conn", None) is not None:
            steps.append(("close monitor connection", self._monitor_conn.close))
        steps.append(("terminate residual connection-bloat sessions", self._cleanup_sessions))
        steps.extend(
            (
                f"join worker thread {index}",
                lambda thread=thread, index=index: _join_thread(
                    thread,
                    2,
                    f"connection-bloat worker thread {index}",
                ),
            )
            for index, thread in enumerate(self._threads)
        )
        steps.extend(
            (f"close worker connection {index}", conn.close)
            for index, conn in enumerate(self._connections)
        )
        _run_cleanup_steps(
            f"Connection-bloat cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._connections = []
        self._blocker_conn = None
        self._elder_decoy_conn = None
        self._monitor_conn = None
        self._distractor_connections = []
        self._threads = []
        self._stop_event = None
class PgSystemFailureConnectionBloatScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_connection_bloat'
    description = 'Simulates connection saturation caused by slow scans over a bloated table whose cleanup is blocked by an old transaction.'
    cases = (_PGSYSTEMFAILURECONNECTIONBLOATSCENARIO_CASE, _PGSYSTEMFAILURECONNECTIONBLOAT_SIMPLE_CASE)

    def build_fault_plan(self, case: PgSystemFailureConnectionBloatCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailureConnectionBloatInjector,
                config={
                    'table': case.table,
                    'app_role': case.app_role,
                    'app_password': case.app_password,
                    'worker_app_prefix': case.worker_app_prefix,
                    'blocker_app_name': case.blocker_app_name,
                    'distractor_app_names': case.distractor_app_names_2,
                    'elder_decoy_app_name': case.elder_decoy_app_name,
                    'decoy_table': case.decoy_table,
                    'decoy_row_count': case.decoy_row_count,
                    'worker_connections': case.worker_connections,
                    'row_count': case.row_count,
                    'dead_tuple_threshold': case.dead_tuple_threshold,
                    'diagnostic_query': case.diagnostic_query,
                    'orphan_prepared_gid': case.orphan_prepared_gid,
                    'blocker_probe_tables': list(case.blocker_probe_tables),
                    'monitor_app_name': case.monitor_app_name,
                    'healthy_tables': list(case.healthy_tables),
                    'healthy_table_rows': list(case.healthy_table_rows),
                },
            ),
        )
