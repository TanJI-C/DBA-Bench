"""PostgreSQL FK validation lock-queue cascade scenario.

真实机制（已在 PostgreSQL 16 上探针验证）：
- 数据治理发布先加 NOT VALID 外键（瞬时完成），再由校验作业执行真实的
  ``ALTER TABLE ... VALIDATE CONSTRAINT``；
- Hard：流水线第 3 步 ``ALTER TABLE order_items ADD COLUMN ...`` 请求
  AccessExclusiveLock，被空闲报表长事务持有的 AccessShareLock 挡住而排队；
  排队的 AEL 让随后的全部业务弱锁请求进入锁队列，形成全表停摆。治理校验作业
  另被只读会话配置钉死，每次 VALIDATE 尝试都必然失败，停摆解除也无法自愈。
- VALIDATE 一旦获授就对真实大表做单遍扫描并真实地把外键置为 validated。
"""

import threading
import time
from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.postgres.business_change import (
    PgBusinessChangeFkValidationForOrderItemsFkValidateStormEvaluatorCase,
)
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.workloads.specs import WorkloadProfile

from src.scenarios.base import DifficultyCalibration, FaultPlan, PostgresScenario, PostgresScenarioCase
from src.workloads.specs import BackgroundWorkloadSpec
from src.execution.specs import CaseResourceSpec, PostgresCaseRuntime

SCENARIO_ID = "pg_business_change_fk_validation"

POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=2048,
    container_cpu_limit=1.0,
    container_memory_mb=1024,
)


def build_fk_validation_workload_profiles() -> tuple[WorkloadProfile, ...]:
    """订单业务流 + 同域噪声：peer 报表、客户资料、发布流水线监控。"""
    return (
        WorkloadProfile(
            name="order_entry_query_stream",
            sql=(
                "SELECT id, amount FROM order_items "
                "WHERE customer_id = 42 ORDER BY id DESC LIMIT 20"
            ),
            qps=0.6,
            tier="LIGHT",
            application_name="order-entry-api",
        ),
        WorkloadProfile(
            name="order_status_writer_stream",
            sql=(
                "UPDATE order_items SET payload = payload WHERE id IN "
                "(SELECT id FROM order_items ORDER BY id LIMIT 15)"
            ),
            qps=0.3,
            tier="WRITE",
            commit=True,
            application_name="order-status-writer",
        ),
        WorkloadProfile(
            name="peer_dashboard_refresh",
            sql=(
                "SELECT status, count(*) AS orders FROM order_items_peer "
                "GROUP BY status ORDER BY status"
            ),
            qps=0.25,
            tier="LIGHT",
            application_name="bi-dashboard-refresh-04",
        ),
        WorkloadProfile(
            name="customer_profile_lookup",
            sql="SELECT id, name FROM customers WHERE id % 100 = 0",
            qps=0.2,
            tier="LIGHT",
            application_name="customer-profile-api",
        ),
        WorkloadProfile(
            name="release_pipeline_monitor",
            sql=(
                "SELECT step_no, step_name, status FROM fk_release_pipeline "
                "ORDER BY step_no"
            ),
            qps=0.15,
            tier="LIGHT",
            application_name="release-pipeline-monitor",
        ),
    )


_STORM_ALERT = (
    "变更发布告警：数据治理外键发布正在订单库执行，发布开始后订单相关接口超时激增，"
    "发布流水线第 3 步（表结构调整）已卡住超过 10 分钟，监控显示大量会话堆积。"
    "请尽快恢复业务，并确认本次数据治理目标最终达成。"
)
_STORM_ALERT_EN = (
    "Change release alert: a data governance foreign key release is running on the orders database. Since the "
    "release started, timeouts on order-related APIs have surged, step 3 of the release pipeline (table structure "
    "adjustment) has been stuck for more than 10 minutes, and monitoring shows a large pile-up of sessions. "
    "Restore the business as soon as possible and confirm that the data governance goal of this release is "
    "ultimately achieved."
)

_STORM_REFERENCE_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "finding",
                "factor": "the queued access exclusive alter request makes every later lock request on order_items queue behind it",
                "entity": "fk_release_pipeline.step3",
                "evidence": [
                    "pg_locks shows the pending AccessExclusiveLock request ahead of every later waiter",
                ],
            },
            {
                "type": "finding",
                "factor": "the fk validate job session is pinned to a read-only transaction so every validation attempt fails",
                "entity": "fkrollout-fk-validate-job-2",
                "evidence": [
                    "the pipeline records repeated failed VALIDATE CONSTRAINT attempts with read-only transaction errors and convalidated stays false",
                ],
            },
            {
                "type": "finding",
                "factor": "an orphaned prepared transaction holds the weak lock that blocks the pipeline ddl",
                "entity": "bi-report-daily-close-20260910",
                "evidence": [
                    "pg_locks shows a granted AccessShareLock on order_items whose pid is NULL",
                    "pg_prepared_xacts maps the lock to the orphaned two-phase transaction bi-report-daily-close-20260910",
                ],
            },
            {
                "type": "finding",
                "factor": "all queries and writes on order_items queue behind the lock chain",
                "entity": "order_items",
                "evidence": [
                    "business sessions fail with lock timeout while the queue head waits",
                ],
            },
            {
                "type": "finding",
                "factor": "a dba must take over and rerun validate constraint until convalidated becomes true",
                "entity": "fk_order_items_customer",
                "evidence": [
                    "the failing job cannot heal itself, so the validation must be replayed manually",
                ],
            },
            {
                "type": "finding",
                "factor": "the same governance rollout also left the order_items_peer foreign key not valid and pending validation",
                "entity": "fk_order_items_peer_customer",
                "evidence": [
                    "pg_constraint shows a second NOT VALID foreign key from the same rollout on order_items_peer",
                ],
            },
            {
                "type": "finding",
                "factor": "legacy orphan order rows violate the foreign key so replaying validate constraint fails until the orphan data is remediated",
                "entity": "order_items",
                "evidence": [
                    "replaying VALIDATE CONSTRAINT fails with a foreign key violation because legacy order rows reference customers absent from the customer master",
                ],
            },
        ]
    },
    "outcome": {
        "changes": [
            "resolved the orphaned prepared transaction with ROLLBACK PREPARED, cancelled the queued pipeline DDL request, stopped the failing validation job, removed the legacy orphan order rows that failed validation, and reran VALIDATE CONSTRAINT for both rollout foreign keys",
        ],
        "verification": [
            "lock queue drained, business reads restored, and both fk_order_items_customer and fk_order_items_peer_customer are convalidated=true",
        ],
    },
    "summary": (
        "The rollout DDL queued behind an orphaned prepared transaction (no live session "
        "holds the lock; only pg_locks with a NULL pid plus pg_prepared_xacts reveal it) and "
        "blocked every later lock while the FK validation job was pinned to a read-only "
        "session and kept failing; resolving the two-phase transaction, unblocking the queue, "
        "removing the legacy orphan order rows that made the replayed validation fail, and "
        "replaying both rollout validations restored service and closed the governance goal."
    ),
}

@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeFkValidationCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    fault_variant: str
    table: str
    customers_table: str
    peer_table: str
    pipeline_table: str
    fk_name: str
    peer_fk_name: str
    ddl_column: str
    order_rows: int
    orphan_rows: int
    customer_rows: int
    peer_rows: int
    validate_app_name: str
    alter_app_name: str
    prepared_tx_gid: str
    noise_vacuum_app_name: str
    noise_advisory_holder_app_name: str
    noise_advisory_waiter_app_name: str
    advisory_lock_key: int
    incident_hold_seconds: int
    startup_timeout_seconds: float

    @property
    def incident_app_names(self) -> tuple[str, ...]:
        return (self.validate_app_name, self.alter_app_name)

    @property
    def protected_app_names(self) -> tuple[str, ...]:
        workload_apps = tuple(
            profile.application_name
            for profile in self.background_workload.profiles
            if profile.application_name
        )
        return workload_apps + (
            self.noise_vacuum_app_name,
            self.noise_advisory_holder_app_name,
            self.noise_advisory_waiter_app_name,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeFkValidationForOrderItemsFkValidateStormScenarioCase(
    PgBusinessChangeFkValidationCase
):
    pass


def _storm_case() -> PgBusinessChangeFkValidationForOrderItemsFkValidateStormScenarioCase:
    return PgBusinessChangeFkValidationForOrderItemsFkValidateStormScenarioCase(
        case_id="order_items_fk_validate_storm",
        case_no=0,
        evaluator=PgBusinessChangeFkValidationForOrderItemsFkValidateStormEvaluatorCase,
        base_image_name="aiopsbench-pg-default:latest",
        workload_tag="default",
        title="FK rollout DDL lock-queue cascade stalls every query on order_items.",
        alert=_STORM_ALERT,
        alert_en=_STORM_ALERT_EN,
        initial_state={
            "status": "incident_active",
            "change": "fk_governance_rollout",
            "pipeline_step": "step3_add_release_note_column",
            "visible_symptom": "order_items_queries_and_writes_queued",
        },
        expected_target={
            "status": "recovered",
            "table": "order_items",
            "fk_state": "validated",
            "peer_fk_state": "validated",
            "incident_sessions": 0,
        },
        reference_report=_STORM_REFERENCE_REPORT,
        background_workload=BackgroundWorkloadSpec(
            profiles=build_fk_validation_workload_profiles(),
            worker_count=3,
            seed=0x0F1,
            warmup_seconds=3,
        ),
        runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
        fault_variant="storm",
        table="order_items",
        customers_table="customers",
        peer_table="order_items_peer",
        pipeline_table="fk_release_pipeline",
        fk_name="fk_order_items_customer",
        peer_fk_name="fk_order_items_peer_customer",
        ddl_column="release_note",
        order_rows=800_000,
        orphan_rows=5,
        customer_rows=2000,
        peer_rows=50_000,
        validate_app_name="fkrollout-fk-validate-job-2",
        alter_app_name="fkrollout-ddl-pipeline-step3",
        prepared_tx_gid="bi-report-daily-close-20260910",
        noise_vacuum_app_name="maintenance-peer-vacuum-03",
        noise_advisory_holder_app_name="etl-sync-holder-07",
        noise_advisory_waiter_app_name="etl-sync-waiter-08",
        advisory_lock_key=836472211,
        incident_hold_seconds=2700,
        startup_timeout_seconds=20.0,
        difficulty=DifficultyCalibration(
            diagnostic_depth=5,
            environmental_complexity=0.533333,
            reference_run_ids=(
                "logs/traces/run_pg_business_change_fk_validation_order_items_fk_validate_storm_MockLLMAgent.json",
            ),
        ),
    )


class PgBusinessChangeFkValidationInjector(BaseFaultInjector):
    """Five-phase injector for the FK validation lock-queue scenarios."""

    def __init__(self):
        self.env = None
        self.fault_variant = "storm"
        self.table = "order_items"
        self.customers_table = "customers"
        self.peer_table = "order_items_peer"
        self.pipeline_table = "fk_release_pipeline"
        self.fk_name = "fk_order_items_customer"
        self.peer_fk_name = ""
        self.ddl_column = "release_note"
        self.order_rows = 800_000
        self.orphan_rows = 0
        self.customer_rows = 2000
        self.peer_rows = 50_000
        self.validate_app_name = ""
        self.alter_app_name = ""
        self.prepared_tx_gid = ""
        self.noise_vacuum_app_name = ""
        self.noise_advisory_holder_app_name = ""
        self.noise_advisory_waiter_app_name = ""
        self.advisory_lock_key = 0
        self.incident_hold_seconds = 2700
        self.startup_timeout_seconds = 20.0
        self._baseline: dict[str, int] | None = None
        self._stop_event = None
        self._threads = []
        self._connections = []
        self.validate_retry_interval_seconds = 3.0

    # ------------------------------------------------------------------
    # configuration helpers
    # ------------------------------------------------------------------
    def _configure(self, config: Mapping[str, object], env) -> None:
        from src.scenarios.postgres.common import _validate_sql_identifier

        self.env = env
        self.fault_variant = str(config["fault_variant"])
        if self.fault_variant not in {"storm"}:
            raise ValueError(
                f"Unknown fk-validation fault variant: {self.fault_variant!r}"
            )
        self.table = _validate_sql_identifier(str(config["table"]), "table")
        self.customers_table = _validate_sql_identifier(str(config["customers_table"]), "customers_table")
        self.peer_table = _validate_sql_identifier(str(config["peer_table"]), "peer_table")
        self.pipeline_table = _validate_sql_identifier(str(config["pipeline_table"]), "pipeline_table")
        self.fk_name = _validate_sql_identifier(str(config["fk_name"]), "fk_name")
        self.peer_fk_name = str(config.get("peer_fk_name", ""))
        if self.peer_fk_name:
            _validate_sql_identifier(self.peer_fk_name, "peer_fk_name")
        self.ddl_column = _validate_sql_identifier(str(config["ddl_column"]), "ddl_column")
        self.order_rows = int(config["order_rows"])
        self.orphan_rows = int(config["orphan_rows"])
        self.customer_rows = int(config["customer_rows"])
        self.peer_rows = int(config["peer_rows"])
        self.validate_app_name = str(config["validate_app_name"])
        self.alter_app_name = str(config["alter_app_name"])
        self.prepared_tx_gid = str(config["prepared_tx_gid"])
        self.noise_vacuum_app_name = str(config["noise_vacuum_app_name"])
        self.noise_advisory_holder_app_name = str(config["noise_advisory_holder_app_name"])
        self.noise_advisory_waiter_app_name = str(config["noise_advisory_waiter_app_name"])
        self.advisory_lock_key = int(config["advisory_lock_key"])
        self.incident_hold_seconds = int(config["incident_hold_seconds"])
        self.startup_timeout_seconds = float(config["startup_timeout_seconds"])
        if self.fault_variant == "storm" and not (
            self.alter_app_name and self.prepared_tx_gid
        ):
            raise ValueError(
                "storm variant requires alter application name and prepared_tx_gid: "
                f"alter_app_name={self.alter_app_name!r}, prepared_tx_gid={self.prepared_tx_gid!r}"
            )
        if self.prepared_tx_gid and ("'" in self.prepared_tx_gid or ";" in self.prepared_tx_gid):
            raise ValueError(
                f"prepared_tx_gid must be a plain literal: {self.prepared_tx_gid!r}"
            )

    def _incident_app_names(self) -> tuple[str, ...]:
        return (self.validate_app_name, self.alter_app_name)

    def _all_case_app_names(self) -> tuple[str, ...]:
        return self._incident_app_names() + (
            self.noise_vacuum_app_name,
            self.noise_advisory_holder_app_name,
            self.noise_advisory_waiter_app_name,
        )

    def _sql_array(self, values) -> str:
        return "ARRAY[" + ",".join("'" + str(v).replace("'", "''") + "'" for v in values) + "]"

    # ------------------------------------------------------------------
    # connection and session helpers
    # ------------------------------------------------------------------
    def _connect(self, application_name: str, autocommit: bool = True):
        import psycopg2

        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=5,
            application_name=application_name,
        )
        conn.autocommit = autocommit
        self._connections.append(conn)
        return conn

    def _terminate_sessions(self, app_names) -> None:
        if not app_names:
            return
        from src.scenarios.postgres.common import _require_sql_success

        statement = (
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            f"WHERE application_name = ANY({self._sql_array(app_names)}) "
            "AND pid <> pg_backend_pid();"
        )
        _require_sql_success(
            self.env.execute_sql(statement),
            f"terminate fk-validation sessions {tuple(app_names)}",
        )

    def _count_locks(self, app_name: str, mode: str, granted: bool) -> int:
        from src.scenarios.postgres.common import _json_object

        payload = _json_object(
            self.env.execute_sql(
                "SELECT count(*) FROM pg_stat_activity a "
                f"JOIN pg_locks l ON l.pid = a.pid AND l.granted = {str(granted).upper()} "
                f"WHERE a.application_name = '{app_name}' "
                f"AND l.mode = '{mode}' "
                f"AND l.relation = '{self.table}'::regclass;"
            ),
            f"count {'' if granted else 'waiting '}locks for {app_name}",
        )
        return int(payload["result"][0][0])

    def _wait_for_waiting_lock(self, app_name: str, mode: str) -> None:
        deadline = time.monotonic() + self.startup_timeout_seconds
        while True:
            if self._count_locks(app_name, mode, granted=False) == 1:
                return
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "fk-validation lock request did not appear in the lock queue: "
                    f"app={app_name!r}, mode={mode}, "
                    f"timeout_seconds={self.startup_timeout_seconds}"
                )
            time.sleep(0.3)

    def _business_probe(self) -> str:
        """'success' 或错误文本：停摆时业务读取会超时。"""
        from src.scenarios.postgres.common import _json_response

        payload = _json_response(
            self.env.execute_sql(
                "SET LOCAL statement_timeout = '800ms'; "
                f"SELECT 1 FROM {self.table} LIMIT 1;"
            ),
            "fk-validation business probe",
        )
        if payload.get("status") == "success":
            return "success"
        return str(payload.get("error"))[:200]

    # ------------------------------------------------------------------
    # five-phase lifecycle
    # ------------------------------------------------------------------
    def install(self, context: FaultLifecycleContext) -> None:
        from src.scenarios.postgres.common import _json_object

        self._configure(context.config, context.env)
        print(f"[FaultInjector:{type(self).__name__}] Installing fault image for {self.fault_variant}...")
        self._enable_prepared_transactions()
        self._terminate_sessions(self._all_case_app_names())
        with self.env.metrics_hidden():
            self._drop_case_objects()
            self._setup_schema()
        payload = _json_object(
            self.env.execute_sql(
                "SELECT convalidated FROM pg_constraint "
                f"WHERE conname = '{self.fk_name}' "
                f"AND conrelid = '{self.table}'::regclass;"
            ),
            "verify installed NOT VALID foreign key",
        )
        if payload["result"][0][0] is not False:
            raise RuntimeError(
                f"fk-validation install did not leave {self.fk_name} NOT VALID: "
                f"convalidated={payload['result'][0][0]!r}"
            )
        print(f"[FaultInjector:{type(self).__name__}] Fault image installed.")
        self.activate(context)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self.quiesce(context)
        self._verify_persistent_state()
        # 基线必须在停摆建立前捕获：停摆后 order_items 上的 count(*) 会被锁队列阻塞。
        self._baseline = self._capture_baseline()
        self._start_incident()
        print(
            f"[FaultInjector:{type(self).__name__}] Incident sessions are live "
            f"({self.fault_variant} variant)."
        )

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        from src.scenarios.postgres.common import _json_object

        if self._baseline is None:
            raise RuntimeError(
                "fk-validation prepare_observability requires activate to have captured "
                f"the baseline: scenario={context.scenario_id}, case={context.case_id}"
            )
        pipeline = _json_object(
            self.env.execute_sql(
                f"SELECT step_no, step_name, status FROM {self.pipeline_table} ORDER BY step_no;"
            ),
            "capture fk-validation pipeline snapshot",
        )
        return {
            "baseline": dict(self._baseline),
            "pipeline_steps": pipeline["result"],
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        from src.scenarios.postgres.common import _join_thread, _run_cleanup_steps

        if self._stop_event is not None:
            self._stop_event.set()
        # Agent 可能终止了环境连接的后端：先恢复主连接，避免清理 SQL 挂在
        # 半开 socket 上；同时打断 injector 自有连接上阻塞中的查询，让线程
        # 立即带着异常退出，而不是在网络等待上耗尽 cleanup 预算。
        if not self.env.reconnect():
            raise RuntimeError(
                f"fk-validation quiesce could not reconnect the environment: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        for conn in self._connections:
            if not conn.closed:
                conn.cancel()
        # 先终止排队的锁请求（validate/alter），再终止锁持有者，避免持有者退出
        # 让 AEL 短暂获授而改变持久状态。
        self._terminate_sessions((self.validate_app_name, self.alter_app_name))
        # prepared 阻塞源无会话可终止，只能用两阶段提交语义解除。
        self._resolve_prepared_holder_tx()
        self._terminate_sessions(
            (
                self.noise_vacuum_app_name,
                self.noise_advisory_holder_app_name,
                self.noise_advisory_waiter_app_name,
            )
        )
        threads = list(self._threads)
        connections = [conn for conn in self._connections if not conn.closed]
        steps = [
            (
                f"join fk-validation thread {index}",
                lambda thread=thread, index=index: _join_thread(thread, 2, f"fk-validation thread {index}"),
            )
            for index, thread in enumerate(threads)
        ]
        steps.extend(
            (f"close fk-validation connection {index}", conn.close)
            for index, conn in enumerate(connections)
        )
        _run_cleanup_steps(
            f"fk-validation cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._threads = []
        self._connections = []
        self._stop_event = None

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        print(f"[FaultInjector:{type(self).__name__}] Recovering fk-validation fault...")
        self.quiesce(context)
        if not self.env.reconnect():
            raise RuntimeError(
                f"fk-validation recovery could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        self._terminate_sessions(self._all_case_app_names())
        self._drop_case_objects()
        print(f"[FaultInjector:{type(self).__name__}] Recovery complete.")

    # ------------------------------------------------------------------
    # persistent state
    # ------------------------------------------------------------------
    def _drop_case_objects(self) -> None:
        from src.scenarios.postgres.common import _require_sql_success

        statements = [
            f"DROP TABLE IF EXISTS {self.table} CASCADE;",
            f"DROP TABLE IF EXISTS {self.peer_table} CASCADE;",
            f"DROP TABLE IF EXISTS {self.customers_table} CASCADE;",
            f"DROP TABLE IF EXISTS {self.pipeline_table} CASCADE;",
        ]
        for statement in statements:
            _require_sql_success(
                self.env.execute_sql(statement),
                f"drop fk-validation object with {statement}",
            )

    def _setup_schema(self) -> None:
        from src.scenarios.postgres.common import _require_sql_success

        statements = [
            f"""
            CREATE TABLE {self.customers_table} (
                id integer PRIMARY KEY,
                name text NOT NULL,
                region integer NOT NULL
            );
            """,
            f"""
            INSERT INTO {self.customers_table} (id, name, region)
            SELECT g, 'customer-' || g, g % 32
            FROM generate_series(1, {self.customer_rows}) AS g;
            """,
            f"""
            CREATE TABLE {self.table} (
                id bigserial PRIMARY KEY,
                customer_id integer NOT NULL,
                amount numeric(10, 2) NOT NULL,
                status text NOT NULL,
                payload text NOT NULL,
                created_at timestamptz NOT NULL DEFAULT now()
            );
            """,
            f"""
            INSERT INTO {self.table} (customer_id, amount, status, payload)
            SELECT
                (g % {self.customer_rows}) + 1,
                ((g % 10000)::numeric / 100),
                CASE WHEN g % 13 = 0 THEN 'PENDING' ELSE 'SETTLED' END,
                repeat(md5(g::text), 4)
            FROM generate_series(1, {self.order_rows}) AS g;
            """,
        ]
        if self.orphan_rows > 0:
            # 治理发布前的 ETL 把已下线渠道（客户段 5000+，未同步进客户主数据）
            # 的订单导入了主表。必须在 FK 创建之前插入：NOT VALID 只豁免存量行，
            # 约束存在后的 INSERT 会被即时检查并拒绝。
            statements.append(
                f"""
                INSERT INTO {self.table} (customer_id, amount, status, payload)
                SELECT {self.customer_rows} + 5000 + g,
                       ((g % 10000)::numeric / 100),
                       'SETTLED',
                       repeat(md5('orphan-channel-' || g::text), 4)
                FROM generate_series(1, {self.orphan_rows}) AS g;
                """
            )
        statements.extend(
            [
                f"""
                CREATE TABLE {self.peer_table} (
                id bigserial PRIMARY KEY,
                customer_id integer NOT NULL,
                amount numeric(10, 2) NOT NULL,
                status text NOT NULL,
                payload text NOT NULL,
                created_at timestamptz NOT NULL DEFAULT now()
            );
            """,
            f"""
            INSERT INTO {self.peer_table} (customer_id, amount, status, payload)
            SELECT
                (g % {self.customer_rows}) + 1,
                ((g % 10000)::numeric / 100),
                CASE WHEN g % 11 = 0 THEN 'PENDING' ELSE 'SETTLED' END,
                repeat(md5('peer-' || g::text), 4)
            FROM generate_series(1, {self.peer_rows}) AS g;
            """,
            f"""
            ALTER TABLE {self.table} ADD CONSTRAINT {self.fk_name}
            FOREIGN KEY (customer_id) REFERENCES {self.customers_table}(id) NOT VALID;
            """,
            f"""
            CREATE TABLE {self.pipeline_table} (
                step_no integer PRIMARY KEY,
                step_name text NOT NULL,
                status text NOT NULL,
                started_at timestamptz,
                finished_at timestamptz,
                attempts integer NOT NULL DEFAULT 0,
                last_error text
            );
            """,
            ]
        )
        if self.fault_variant == "storm":
            statements.append(
                f"""
                ALTER TABLE {self.peer_table} ADD CONSTRAINT {self.peer_fk_name}
                FOREIGN KEY (customer_id) REFERENCES {self.customers_table}(id) NOT VALID;
                """
            )
            statements.append(
                f"""
                INSERT INTO {self.pipeline_table} (step_no, step_name, status, started_at, finished_at)
                VALUES
                    (1, 'add_fk_not_valid', 'done', now() - interval '35 minutes', now() - interval '35 minutes'),
                    (2, 'validate_fk', 'running', now() - interval '12 minutes', NULL),
                    (3, 'add_release_note_column', 'queued', NULL, NULL);
                """
            )
        statements.extend(
            [
                f"ANALYZE {self.customers_table};",
                f"ANALYZE {self.table};",
                f"ANALYZE {self.peer_table};",
                f"ANALYZE {self.pipeline_table};",
            ]
        )
        for statement in statements:
            _require_sql_success(
                self.env.execute_sql(statement),
                f"install fk-validation schema with {statement[:80]!r}",
            )

    def _verify_persistent_state(self) -> None:
        from src.scenarios.postgres.common import _json_object

        orphan_probe = (
            f"(SELECT count(*) FROM {self.table} o "
            f"LEFT JOIN {self.customers_table} c ON o.customer_id = c.id "
            "WHERE c.id IS NULL), "
        ) if self.orphan_rows > 0 else ""
        payload = _json_object(
            self.env.execute_sql(
                "SELECT c.convalidated, "
                f"(SELECT count(*) FROM {self.table}), "
                f"{orphan_probe}"
                f"(SELECT count(*) FROM {self.pipeline_table}) "
                "FROM pg_constraint c "
                f"WHERE c.conname = '{self.fk_name}' "
                f"AND c.conrelid = '{self.table}'::regclass;"
            ),
            "verify fk-validation fault image",
        )
        rows = payload["result"]
        if len(rows) != 1 or rows[0][0] is not False or int(rows[0][1]) < self.order_rows:
            raise RuntimeError(
                f"fk-validation fault image does not match the Case: rows={rows!r}, "
                f"expected_order_rows>={self.order_rows}"
            )
        if self.orphan_rows > 0 and int(rows[0][2]) != self.orphan_rows:
            raise RuntimeError(
                "fk-validation fault image orphan row count does not match the Case: "
                f"orphan_rows={rows[0][2]!r}, expected={self.orphan_rows}"
            )
        if self.peer_fk_name:
            peer_payload = _json_object(
                self.env.execute_sql(
                    "SELECT convalidated FROM pg_constraint "
                    f"WHERE conname = '{self.peer_fk_name}' "
                    f"AND conrelid = '{self.peer_table}'::regclass;"
                ),
                "verify fk-validation peer fault image",
            )
            if peer_payload["result"][0][0] is not False:
                raise RuntimeError(
                    f"fk-validation install did not leave {self.peer_fk_name} NOT VALID: "
                    f"convalidated={peer_payload['result'][0][0]!r}"
                )

    def _capture_baseline(self) -> dict[str, int]:
        from src.scenarios.postgres.common import _json_object

        rows = _json_object(
            self.env.execute_sql(
                f"SELECT (SELECT count(*) FROM {self.table}), "
                f"(SELECT count(*) FROM {self.customers_table}), "
                f"(SELECT count(*) FROM {self.peer_table}), "
                f"(SELECT count(*) FROM {self.table} o "
                f"LEFT JOIN {self.customers_table} c ON o.customer_id = c.id "
                "WHERE c.id IS NULL);"
            ),
            "capture fk-validation baseline row counts",
        )
        order_items_rows, customers_rows, peer_rows, orphan_rows = (int(v) for v in rows["result"][0])
        return {
            "order_items_rows": order_items_rows,
            "customers_rows": customers_rows,
            "peer_rows": peer_rows,
            "orphan_rows": orphan_rows,
        }

    # ------------------------------------------------------------------
    # runtime incident sessions
    # ------------------------------------------------------------------
    def _start_incident(self) -> None:
        self._stop_event = threading.Event()
        deadline = time.time() + self.incident_hold_seconds
        self._start_noise_sessions(deadline)
        self._start_storm_chain(deadline)
        self._wait_for_incident_ready()

    def _spawn(self, target, name: str, *args) -> None:
        thread = threading.Thread(target=target, args=args, daemon=True, name=name)
        thread.start()
        self._threads.append(thread)

    def _start_noise_sessions(self, deadline: float) -> None:
        self._spawn(self._run_advisory_holder, "fkval-noise-advisory-holder", deadline)
        # 先确认 holder 已持有 advisory 锁，再启动 waiter，避免启动竞态让
        # waiter 反而先拿到锁后立即退出（噪声必须可复现）。
        self._wait_for_granted_advisory_lock()
        self._spawn(self._run_advisory_waiter, "fkval-noise-advisory-waiter", deadline)
        self._spawn(self._run_peer_vacuum_loop, "fkval-noise-vacuum", deadline)

    def _wait_for_granted_advisory_lock(self) -> None:
        from src.scenarios.postgres.common import _json_object

        deadline = time.monotonic() + self.startup_timeout_seconds
        while True:
            payload = _json_object(
                self.env.execute_sql(
                    "SELECT count(*) FROM pg_locks "
                    "WHERE locktype = 'advisory' AND granted "
                    f"AND objid = {self.advisory_lock_key};"
                ),
                "wait for advisory noise holder",
            )
            if int(payload["result"][0][0]) == 1:
                return
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "fk-validation advisory noise holder did not acquire its lock: "
                    f"key={self.advisory_lock_key}, "
                    f"timeout_seconds={self.startup_timeout_seconds}"
                )
            time.sleep(0.3)

    def _start_storm_chain(self, deadline: float) -> None:
        self._prepare_holder_prepared_tx()
        self._spawn(self._run_pipeline_ddl, "fkval-alter", self.alter_app_name)
        self._wait_for_waiting_lock(self.alter_app_name, "AccessExclusiveLock")
        self._spawn(self._run_fk_validate_job, "fkval-validate", self.validate_app_name, deadline)
        self._wait_for_validate_job_attempts()

    def _wait_for_incident_ready(self) -> None:
        deadline = time.monotonic() + self.startup_timeout_seconds
        while True:
            stall = self._business_probe()
            if "timeout" in stall or "canceling statement" in stall:
                return
            detail = f"business probe not blocked yet: {stall!r}"
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    f"fk-validation incident did not reach the expected state: {detail}, "
                    f"timeout_seconds={self.startup_timeout_seconds}"
                )
            time.sleep(0.5)

    # ------------------------------------------------------------------
    # session runners
    # ------------------------------------------------------------------
    def _enable_prepared_transactions(self) -> None:
        """Storm 前置：打开 max_prepared_transactions 并重启 PG（写入 fault image）。"""
        from src.scenarios.postgres.common import _json_object, _require_sql_success

        _require_sql_success(
            self.env.execute_sql("ALTER SYSTEM SET max_prepared_transactions = '10';"),
            "enable max_prepared_transactions for fk-validation storm",
        )
        if not self.env.deployment.restart_pg():
            raise RuntimeError(
                "fk-validation storm install could not restart PG after enabling "
                "max_prepared_transactions"
            )
        if not self.env.reconnect():
            raise RuntimeError(
                "fk-validation storm install could not reconnect after PG restart"
            )
        payload = _json_object(
            self.env.execute_sql("SHOW max_prepared_transactions;"),
            "verify max_prepared_transactions after restart",
        )
        if int(payload["result"][0][0]) <= 0:
            raise RuntimeError(
                "max_prepared_transactions is still disabled after restart: "
                f"value={payload['result'][0][0]!r}"
            )

    def _prepare_holder_prepared_tx(self) -> None:
        """Storm 阻塞源头：孤儿 prepared transaction 持有 order_items 的 AccessShareLock。

        会话在 PREPARE 后关闭：pg_stat_activity 里没有持有者，pg_blocking_pids 对它
        返回空，只有 pg_locks（pid 为 NULL 的 granted ASE）+ pg_prepared_xacts 能定位。
        """
        from src.scenarios.postgres.common import _json_object

        _json_object(
            self.env.execute_sql(
                "BEGIN; "
                f"SELECT count(*) FROM {self.table}; "
                f"PREPARE TRANSACTION '{self.prepared_tx_gid}';"
            ),
            "prepare the orphan report holder transaction",
        )
        payload = _json_object(
            self.env.execute_sql(
                "SELECT count(*) FROM pg_prepared_xacts WHERE gid = "
                f"'{self.prepared_tx_gid}';"
            ),
            "verify the orphan prepared transaction exists",
        )
        if int(payload["result"][0][0]) != 1:
            raise RuntimeError(
                "fk-validation storm did not leave the orphan prepared transaction: "
                f"gid={self.prepared_tx_gid!r}, count={payload['result'][0][0]!r}"
            )

    def _resolve_prepared_holder_tx(self) -> None:
        """解除 prepared 阻塞源（幂等：agent 可能已用 COMMIT/ROLLBACK PREPARED 处置）。"""
        from src.scenarios.postgres.common import _json_object, _require_sql_success

        payload = _json_object(
            self.env.execute_sql(
                "SELECT count(*) FROM pg_prepared_xacts WHERE gid = "
                f"'{self.prepared_tx_gid}';"
            ),
            "check the orphan prepared transaction before resolution",
        )
        if int(payload["result"][0][0]) == 0:
            return
        _require_sql_success(
            self.env.execute_sql(f"ROLLBACK PREPARED '{self.prepared_tx_gid}';"),
            f"roll back the orphan prepared transaction {self.prepared_tx_gid!r}",
        )

    def _run_pipeline_ddl(self, app_name: str) -> None:
        """流水线第 3 步：请求 AccessExclusiveLock 的轻量 DDL（元数据级）。"""
        conn = None
        try:
            conn = self._connect(app_name)
            with conn.cursor() as cur:
                cur.execute(f"ALTER TABLE {self.table} ADD COLUMN {self.ddl_column} text;")
            self._finish_pipeline_step(conn, 3)
        except Exception as exc:
            print(f"[FaultInjector:{type(self).__name__}] pipeline ddl stopped: {exc}")
        finally:
            if conn is not None and not conn.closed:
                try:
                    conn.close()
                except Exception:
                    pass

    def _run_fk_validate_job(self, app_name: str, deadline: float) -> None:
        """Storm 校验作业：被只读配置钉死的真实 VALIDATE CONSTRAINT 重试作业。

        发布流水线把校验步骤绑到了只读会话（角色残留 default_transaction_read_only），
        每次尝试都在 `BEGIN TRANSACTION READ ONLY` 里执行真实 VALIDATE，必然以
        "cannot execute ALTER TABLE in a read-only transaction" 失败；作业自身永远
        无法完成，只有 Agent 接手（终止作业并重放 VALIDATE）后才能闭环治理目标。
        """
        conn = None
        try:
            conn = self._connect(app_name)
            attempt = 0
            while not self._stop_event.is_set() and time.time() < deadline:
                if self._fk_already_validated(conn):
                    break
                attempt += 1
                error = self._attempt_validate(conn)
                self._record_validate_attempt(conn, attempt, error)
                if error is None:
                    self._finish_pipeline_step(conn, 2)
                    print(f"[FaultInjector:{type(self).__name__}] FK validation job completed.")
                    return
                self._stop_event.wait(self.validate_retry_interval_seconds)
        except Exception as exc:
            print(f"[FaultInjector:{type(self).__name__}] fk validate job stopped: {exc}")
        finally:
            if conn is not None and not conn.closed:
                try:
                    conn.close()
                except Exception:
                    pass

    def _fk_already_validated(self, conn) -> bool:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT convalidated FROM pg_constraint "
                "WHERE conname = %s AND conrelid = %s::regclass;",
                (self.fk_name, self.table),
            )
            return bool(cur.fetchone()[0])

    def _attempt_validate(self, conn) -> str | None:
        try:
            with conn.cursor() as cur:
                cur.execute("BEGIN TRANSACTION READ ONLY;")
                cur.execute(
                    f"ALTER TABLE {self.table} VALIDATE CONSTRAINT {self.fk_name};"
                )
                cur.execute("COMMIT;")
            return None
        except Exception as exc:
            try:
                with conn.cursor() as cur:
                    cur.execute("ROLLBACK;")
            except Exception as rollback_exc:
                print(
                    f"[FaultInjector:{type(self).__name__}] validate attempt rollback "
                    f"failed: {rollback_exc}"
                )
            return str(exc)[:160]

    def _record_validate_attempt(self, conn, attempt: int, error: str | None) -> None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE {self.pipeline_table} "
                    "SET attempts = %s, last_error = %s, status = CASE WHEN %s IS NULL THEN 'done' ELSE 'retrying' END "
                    "WHERE step_no = 2;",
                    (attempt, error, error),
                )
        except Exception as exc:
            print(
                f"[FaultInjector:{type(self).__name__}] validate attempt bookkeeping failed: {exc}"
            )

    def _wait_for_validate_job_attempts(self) -> None:
        from src.scenarios.postgres.common import _json_object

        deadline = time.monotonic() + self.startup_timeout_seconds
        while True:
            payload = _json_object(
                self.env.execute_sql(
                    f"SELECT attempts, last_error FROM {self.pipeline_table} "
                    "WHERE step_no = 2;"
                ),
                "wait for fk validate job attempts",
            )
            attempts = int(payload["result"][0][0] or 0)
            if attempts >= 1 and payload["result"][0][1]:
                return
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "fk-validation validate job did not record a failed attempt: "
                    f"attempts={attempts}, timeout_seconds={self.startup_timeout_seconds}"
                )
            time.sleep(0.3)

    def _run_advisory_holder(self, deadline: float) -> None:
        conn = None
        try:
            conn = self._connect(self.noise_advisory_holder_app_name)
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_lock(%s);", (self.advisory_lock_key,))
            while not self._stop_event.is_set() and time.time() < deadline:
                time.sleep(0.5)
        except Exception as exc:
            print(f"[FaultInjector:{type(self).__name__}] advisory holder stopped: {exc}")
        finally:
            if conn is not None and not conn.closed:
                try:
                    conn.close()
                except Exception:
                    pass

    def _run_advisory_waiter(self, deadline: float) -> None:
        conn = None
        try:
            conn = self._connect(self.noise_advisory_waiter_app_name)
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_lock(%s);", (self.advisory_lock_key,))
        except Exception as exc:
            print(f"[FaultInjector:{type(self).__name__}] advisory waiter stopped: {exc}")
        finally:
            if conn is not None and not conn.closed:
                try:
                    conn.close()
                except Exception:
                    pass

    def _run_peer_vacuum_loop(self, deadline: float) -> None:
        conn = None
        try:
            conn = self._connect(self.noise_vacuum_app_name)
            while not self._stop_event.is_set() and time.time() < deadline:
                with conn.cursor() as cur:
                    cur.execute(f"VACUUM (ANALYZE) {self.peer_table};")
                self._stop_event.wait(30)
        except Exception as exc:
            print(f"[FaultInjector:{type(self).__name__}] peer vacuum stopped: {exc}")
        finally:
            if conn is not None and not conn.closed:
                try:
                    conn.close()
                except Exception:
                    pass

    def _finish_pipeline_step(self, conn, step_no: int) -> None:
        """在线程自有连接上记录流水线步骤完成，避免并发使用 env 主连接。"""
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE {self.pipeline_table} SET status = 'done', finished_at = now() "
                    f"WHERE step_no = {step_no};"
                )
        except Exception as exc:
            print(
                f"[FaultInjector:{type(self).__name__}] pipeline step {step_no} "
                f"bookkeeping failed: {exc}"
            )


class PgBusinessChangeFkValidationScenario(PostgresScenario):
    scenario_id = SCENARIO_ID
    description = (
        "FK rollout VALIDATE CONSTRAINT and a queued AccessExclusive DDL cascade into a "
        "lock-queue stall on order_items."
    )
    cases = (
        _storm_case(),
    )

    def build_fault_plan(self, case: PgBusinessChangeFkValidationCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgBusinessChangeFkValidationInjector,
                config={
                    "fault_variant": case.fault_variant,
                    "table": case.table,
                    "customers_table": case.customers_table,
                    "peer_table": case.peer_table,
                    "pipeline_table": case.pipeline_table,
                    "fk_name": case.fk_name,
                    "peer_fk_name": case.peer_fk_name,
                    "ddl_column": case.ddl_column,
                    "order_rows": case.order_rows,
                    "orphan_rows": case.orphan_rows,
                    "customer_rows": case.customer_rows,
                    "peer_rows": case.peer_rows,
                    "validate_app_name": case.validate_app_name,
                    "alter_app_name": case.alter_app_name,
                    "prepared_tx_gid": case.prepared_tx_gid,
                    "noise_vacuum_app_name": case.noise_vacuum_app_name,
                    "noise_advisory_holder_app_name": case.noise_advisory_holder_app_name,
                    "noise_advisory_waiter_app_name": case.noise_advisory_waiter_app_name,
                    "advisory_lock_key": case.advisory_lock_key,
                    "incident_hold_seconds": case.incident_hold_seconds,
                    "startup_timeout_seconds": case.startup_timeout_seconds,
                },
            ),
        )
