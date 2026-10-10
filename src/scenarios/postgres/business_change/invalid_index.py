import threading
import time
from dataclasses import dataclass
from typing import List, Mapping

from src.database.postgres import execution_time_seconds
from src.scenarios.evaluation.postgres.business_change import (
    PgBusinessChangeInvalidIndexForStoreSalesCicAbandonedIndexEvaluatorCase,
    PgBusinessChangeInvalidIndexForStoreSalesInvalidIndexSimpleEvaluatorCase,
)

from src.scenarios.workloads import WorkloadProfile

from ...base import (
    PostgresCaseRuntime,
    BackgroundWorkloadSpec,
    DifficultyCalibration,
    PostgresRuntimeSpec,
    PostgresScenario,
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

# 发布窗口部署基线（Hard）：默认 A 档参数 + 两阶段事务可用（孤儿 prepared
# transaction 干涉的前提）+ 失控语句确定性超时（Agent 自建的挂起并发 DDL 在
# 确定时长后报错返回，而不是运行框架永久阻塞；发布重试状态机自带 45s watchdog
# 取消，不受影响）。覆盖默认 GUC 串时必须全量复制默认项。
POSTGRES_RELEASE_WINDOW_RUNTIME = PostgresRuntimeSpec(
    parameters=(
        ("shared_buffers", "128MB"),
        ("work_mem", "16MB"),
        ("shared_preload_libraries", "pg_stat_statements"),
        ("logging_collector", "on"),
        ("log_destination", "stderr"),
        ("log_directory", "/var/log/postgresql"),
        ("log_filename", "postgresql-%Y-%m-%d_%H%M%S.log"),
        ("log_rotation_age", "1d"),
        ("log_rotation_size", "100MB"),
        ("max_prepared_transactions", "10"),
        ("statement_timeout", "120000"),
    ),
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeInvalidIndexCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    table: str
    peer_table: str
    pk_column: str
    store_column: str
    date_column: str
    item_column: str
    amount_column: str
    payload_column: str
    invalid_index_name: str
    invalid_index_predicate: str
    ddl_freeze_trigger_name: str
    decoy_index_name: str
    item_index_name: str
    release_log_table: str
    release_task_name: str
    noise_table: str
    noise_index_name: str
    noise_release_task_name: str
    noise_probe_query: str
    item_lookup_query: str
    controller_app_name: str
    export_prepare_gid: str
    export_ledger_table: str
    export_inbox_table: str
    export_batch_rows: int
    retry_app_name: str
    representative_query: str
    row_count: int
    seeded_rows: int
    peer_row_count: int
    noise_row_count: int
    cic_session_timeout_seconds: float
    cic_phase_timeout_seconds: float
    cic_max_attempts: int
    report_store_id: int
    report_window_days: int


def build_invalid_index_noise_profiles(
    table: str,
    peer_table: str,
    noise_table: str,
    representative_query: str,
    store_column: str,
    date_column: str,
    item_column: str,
    amount_column: str,
    payload_column: str,
    report_store_id: int,
    *,
    include_noise_report: bool,
    include_item_lookup: bool,
    item_lookup_query: str = "",
) -> List[WorkloadProfile]:
    """Business traffic for the invalid-index release scenario.

    The representative report query runs continuously so its latency baseline
    and recovery are observable through workload_activity/topsql. The peer
    report keeps the healthy-neighbor contrast visible, the ingest writer keeps
    online writes real, and the history rollup is an unrelated heavy report.
    """
    peer_query = (
        f"SELECT store_id, sold_date, sum(amount) AS store_daily_sales "
        f"FROM {peer_table} "
        f"WHERE store_id = {report_store_id} "
        f"AND sold_date >= CURRENT_DATE - INTERVAL '365 days' "
        f"GROUP BY store_id, sold_date ORDER BY sold_date"
    )
    profiles = [
        WorkloadProfile(
            name="store_sales_report_by_store",
            sql=representative_query,
            qps=0.3,
            tier="MEDIUM",
            application_name="store-sales-report-api",
        ),
        WorkloadProfile(
            name="store_sales_peer_report_baseline",
            sql=peer_query,
            qps=0.2,
            tier="LIGHT",
            application_name="peer-store-baseline-report",
        ),
        WorkloadProfile(
            name="store_sales_ingest_writer",
            sql=(
                f"INSERT INTO {table} ({store_column}, {date_column}, {item_column}, "
                f"{amount_column}, {payload_column}) "
                f"SELECT (g % 200) + 1, CURRENT_DATE, (g % 5000) + 1, "
                f"((g % 100000)::numeric / 100) + 1, repeat(md5(g::text || clock_timestamp()::text), 4) "
                f"FROM generate_series(1, 4) AS g;"
            ),
            qps=0.25,
            tier="DML_NOISE",
            commit=True,
            application_name="store-sales-ingest-writer",
        ),
    ]
    if include_item_lookup:
        profiles.append(
            WorkloadProfile(
                name="store_sales_item_lookup",
                sql=item_lookup_query,
                qps=0.2,
                tier="LIGHT",
                application_name="item-movement-lookup",
            ),
        )
    if include_noise_report:
        profiles.append(
            WorkloadProfile(
                name="returns_history_rollup_report",
                sql=(
                    f"SELECT extract(year from return_date)::int AS return_year, status, count(*) AS returns "
                    f"FROM {noise_table} "
                    f"GROUP BY return_year, status "
                    f"ORDER BY return_year DESC, status"
                ),
                qps=0.1,
                tier="HEAVY",
                application_name="returns-history-rollup",
            ),
        )
        profiles.append(
            WorkloadProfile(
                name="returns_pending_review_probe",
                sql=(
                    f"SELECT count(*) AS pending_reviews, coalesce(sum(amount), 0) AS held_amount "
                    f"FROM {noise_table} WHERE status = 'PENDING'"
                ),
                qps=0.2,
                tier="LIGHT",
                application_name="returns-pending-review",
            ),
        )
    return profiles


def _reference_report(case_id: str, factors: tuple[str, ...]) -> dict:
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": factor,
                    "entity": case_id,
                    "evidence": [f"scripted diagnostic actions observed {factor}"],
                }
                for factor in factors
            ]
        },
        "outcome": {
            "changes": ["dropped the leftover invalid index and rebuilt the report index concurrently"],
            "verification": [
                "catalog shows no invalid index on the target table",
                "representative report plan uses an index scan",
                "representative report latency recovered below the fault baseline",
            ],
        },
        "summary": "The interrupted concurrent index build left an invalid index; it was dropped and rebuilt online.",
    }


_HARD_REFERENCE_FACTORS = (
    "create index concurrently was interrupted and left an invalid index",
    "a hung long transaction blocks the concurrent index release from completing",
    "drop the invalid index and rebuild concurrently",
)

_EASY_REFERENCE_FACTORS = (
    "interrupted create index concurrently left an invalid index",
    "drop the invalid index and rebuild concurrently",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeInvalidIndexForStoreSalesCicAbandonedIndexScenarioCase(
    PgBusinessChangeInvalidIndexCase
):
    pass


_PGBUSINESSCHANGEINVALIDINDEXSCENARIO_HARD_CASE = (
    PgBusinessChangeInvalidIndexForStoreSalesCicAbandonedIndexScenarioCase(
        case_id="store_sales_cic_abandoned_index",
        reference_report=_reference_report(
            "store_sales_cic_abandoned_index", _HARD_REFERENCE_FACTORS
        ),
        difficulty=DifficultyCalibration(
            diagnostic_depth=8,
            environmental_complexity=0.714286,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_business_change_invalid_index_"
                "store_sales_cic_abandoned_index_MockLLMAgent.json",
            ),
            protocol_version="difficulty-v2",
        ),
        case_no=0,
        evaluator=PgBusinessChangeInvalidIndexForStoreSalesCicAbandonedIndexEvaluatorCase,
        base_image_name="aiopsbench-pg-default:latest",
        workload_tag="default",
        title=(
            "Report latency regression after an interrupted CREATE INDEX "
            "CONCURRENTLY left an invalid index behind."
        ),
        alert=(
            "变更发布告警：昨夜为 store_sales 上线门店销量报表新索引的发布任务一直显示失败重试，"
            "今晨门店销量报表查询延迟显著升高，另有若干不相关报表查询也偏慢。"
            "请找出性能退化的真实原因并恢复门店销量报表查询性能；"
            "发布窗口约束：不允许长时间阻塞 store_sales 的线上写入，也不允许重启实例。"
        ),
        initial_state={
            "status": "degraded",
            "alert": "release_retrying_and_report_latency_high",
            "table": "store_sales",
            "visible_symptom": "store_sales_report_slow_since_index_release",
        },
        expected_target={
            "status": "recovered",
            "table": "store_sales",
            "invalid_indexes": 0,
            "report_plan": "index_scan",
            "report_latency": "recovered_below_fault_baseline",
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=tuple(build_invalid_index_noise_profiles(
                table="store_sales",
                peer_table="store_sales_peer",
                noise_table="store_returns_hist",
                representative_query=(
                    "SELECT store_id, sold_date, sum(amount) AS store_daily_sales "
                    "FROM store_sales "
                    "WHERE store_id = 7 "
                    "GROUP BY store_id, sold_date ORDER BY sold_date"
                ),
                store_column="store_id",
                date_column="sold_date",
                item_column="item_id",
                amount_column="amount",
                payload_column="payload",
                report_store_id=7,
                include_noise_report=True,
                include_item_lookup=True,
                item_lookup_query=(
                    "SELECT count(*) AS movements, coalesce(sum(amount), 0) AS item_amount "
                    "FROM store_sales WHERE item_id = 4213"
                ),
            )),
            worker_count=4,
            seed=0,
            warmup_seconds=4,
        ),
        runtime=PostgresCaseRuntime(
            resources=POSTGRES_RESOURCES,
            parameters=POSTGRES_RELEASE_WINDOW_RUNTIME,
        ),
        table="store_sales",
        peer_table="store_sales_peer",
        pk_column="ss_id",
        store_column="store_id",
        date_column="sold_date",
        item_column="item_id",
        amount_column="amount",
        payload_column="payload",
        invalid_index_name="idx_store_sales_store_date_cic",
        invalid_index_predicate="",
        ddl_freeze_trigger_name="",
        decoy_index_name="idx_store_sales_date",
        item_index_name="idx_store_sales_item",
        release_log_table="ops_release_task_log",
        release_task_name="store_sales_report_index_release",
        noise_table="store_returns_hist",
        noise_index_name="idx_store_returns_hist_status",
        noise_release_task_name="returns_hist_pending_index_release",
        noise_probe_query=(
            "SELECT count(*) AS pending_reviews, coalesce(sum(amount), 0) AS held_amount "
            "FROM store_returns_hist WHERE status = 'PENDING'"
        ),
        item_lookup_query=(
            "SELECT count(*) AS movements, coalesce(sum(amount), 0) AS item_amount "
            "FROM store_sales WHERE item_id = 4213"
        ),
        controller_app_name="store-sales-release-controller",
        export_prepare_gid="store_sales_report_export_2pc_batch_1",
        export_ledger_table="ops_report_export_batches",
        export_inbox_table="store_sales_inbox",
        export_batch_rows=5000,
        retry_app_name="store-sales-release-retry",
        representative_query=(
            "SELECT store_id, sold_date, sum(amount) AS store_daily_sales "
            "FROM store_sales "
            "WHERE store_id = 7 "
            "GROUP BY store_id, sold_date ORDER BY sold_date"
        ),
        row_count=1200000,
        seeded_rows=1200000,
        peer_row_count=150000,
        noise_row_count=250000,
        cic_session_timeout_seconds=30.0,
        cic_phase_timeout_seconds=120.0,
        cic_max_attempts=3,
        report_store_id=7,
        report_window_days=365,
    )
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeInvalidIndexForStoreSalesInvalidIndexSimpleScenarioCase(
    PgBusinessChangeInvalidIndexCase
):
    pass


_PGBUSINESSCHANGEINVALIDINDEXSCENARIO_SIMPLE_CASE = (
    PgBusinessChangeInvalidIndexForStoreSalesInvalidIndexSimpleScenarioCase(
        case_id="store_sales_invalid_index_simple",
        reference_report=_reference_report(
            "store_sales_invalid_index_simple", _EASY_REFERENCE_FACTORS
        ),
        difficulty=DifficultyCalibration(
            diagnostic_depth=3,
            environmental_complexity=0.428571,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_business_change_invalid_index_"
                "store_sales_invalid_index_simple_MockLLMAgent.json",
            ),
            protocol_version="difficulty-v2",
        ),
        case_no=1,
        evaluator=PgBusinessChangeInvalidIndexForStoreSalesInvalidIndexSimpleEvaluatorCase,
        base_image_name="aiopsbench-pg-default:latest",
        workload_tag="default",
        title=(
            "An interrupted concurrent index release left an invalid partial "
            "index carrying a leftover template predicate; the store report "
            "stays on a sequential scan."
        ),
        alert=(
            "变更告警：昨夜 store_sales 的报表发布任务执行失败，今晨门店销量报表查询"
            "延迟明显升高。请找出性能退化的真实原因并恢复门店销量报表查询性能；"
            "发布窗口约束：不允许长时间阻塞 store_sales 的线上写入，也不允许重启实例。"
        ),
        initial_state={
            "status": "degraded",
            "alert": "release_retrying_and_report_latency_high",
            "table": "store_sales",
            "visible_symptom": "store_sales_report_slow_since_index_release",
        },
        expected_target={
            "status": "recovered",
            "table": "store_sales",
            "invalid_indexes": 0,
            "report_plan": "index_scan",
            "report_latency": "recovered_below_fault_baseline",
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=tuple(build_invalid_index_noise_profiles(
                table="store_sales",
                peer_table="store_sales_peer",
                noise_table="store_returns_hist",
                representative_query=(
                    "SELECT store_id, sold_date, sum(amount) AS store_daily_sales "
                    "FROM store_sales "
                    "WHERE store_id = 23 "
                    "AND sold_date >= CURRENT_DATE - INTERVAL '365 days' "
                    "GROUP BY store_id, sold_date ORDER BY sold_date"
                ),
                store_column="store_id",
                date_column="sold_date",
                item_column="item_id",
                amount_column="amount",
                payload_column="payload",
                report_store_id=23,
                include_noise_report=False,
                include_item_lookup=False,
            )),
            worker_count=2,
            seed=0x4104,
            warmup_seconds=2,
        ),
        runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
        table="store_sales",
        peer_table="store_sales_peer",
        pk_column="ss_id",
        store_column="store_id",
        date_column="sold_date",
        item_column="item_id",
        amount_column="amount",
        payload_column="payload",
        invalid_index_name="idx_store_sales_store_date_cic",
        # 发布脚本从"高频商品动销报表"复制索引模板时忘了删谓词：列序正确但
        # WHERE item_id < 1000 与门店报表的访问模式无蕴含关系，planner 永不使用。
        invalid_index_predicate="WHERE item_id < 1000",
        # 发布窗口的变更冻结：发布系统装了 DDL 守护 event trigger，把本库一切
        # 手工 CREATE INDEX 锁进发布管线；发布管线自身失败退出后冻结对象泄漏
        # （真实事故：变更管制未随发布失败回滚）。Agent 完成修复必须发现并
        # 解除该冻结。
        ddl_freeze_trigger_name="release_change_freeze_guard",
        decoy_index_name="idx_store_sales_sold_date",
        item_index_name="",
        release_log_table="ops_release_task_log",
        release_task_name="store_sales_report_index_release",
        noise_table="store_returns_hist",
        noise_index_name="",
        noise_release_task_name="",
        noise_probe_query="",
        item_lookup_query="",
        controller_app_name="",
        export_prepare_gid="",
        export_ledger_table="",
        export_inbox_table="",
        export_batch_rows=0,
        retry_app_name="",
        representative_query=(
            "SELECT store_id, sold_date, sum(amount) AS store_daily_sales "
            "FROM store_sales "
            "WHERE store_id = 23 "
            "AND sold_date >= CURRENT_DATE - INTERVAL '365 days' "
            "GROUP BY store_id, sold_date ORDER BY sold_date"
        ),
        row_count=800000,
        seeded_rows=800000,
        peer_row_count=120000,
        noise_row_count=0,
        cic_session_timeout_seconds=30.0,
        cic_phase_timeout_seconds=120.0,
        cic_max_attempts=3,
        report_store_id=23,
        report_window_days=365,
    )
)


from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.postgres.common import (
    _join_thread,
    _json_object,
    _require_sql_success,
    _run_cleanup_steps,
    _validate_sql_identifier,
)


class PgBusinessChangeInvalidIndexInjector(BaseFaultInjector):
    """
    复现"发布窗口内 CREATE INDEX CONCURRENTLY 被取消，遗留 indisvalid=false 索引"。

    install 在全新环境中真实地执行一次 CREATE INDEX CONCURRENTLY，并在其进入
    校验阶段（indisready=true, indisvalid=false）时用 pg_cancel_backend 取消，
    PostgreSQL 由此真实遗留 invalid 索引；planner 拒绝使用该索引，代表性报表
    查询退化为顺序扫描。
    """

    def __init__(self):
        self.env = None
        self.controller_app_name = "store-sales-release-controller"
        self.export_prepare_gid = ""
        self.export_ledger_table = ""
        self.export_inbox_table = ""
        self.export_batch_rows = 0
        self.retry_app_name = "store-sales-release-retry"
        self._controller_conn = None
        self._controller_thread = None
        self._retry_conn = None
        self._retry_thread = None
        self._stall_stop = threading.Event()
        self.table = "store_sales"
        self.peer_table = "store_sales_peer"
        self.noise_table = "store_returns_hist"
        self.pk_column = "ss_id"
        self.store_column = "store_id"
        self.date_column = "sold_date"
        self.amount_column = "amount"
        self.payload_column = "payload"
        self.invalid_index_name = "idx_store_sales_store_date_cic"
        self.invalid_index_predicate = ""
        self.ddl_freeze_trigger_name = ""
        self.decoy_index_name = ""
        self.item_index_name = ""
        self.release_log_table = ""
        self.release_task_name = ""
        self.noise_index_name = ""
        self.noise_release_task_name = ""
        self.row_count = 1200000
        self.seeded_rows = 1200000
        self.peer_row_count = 150000
        self.noise_row_count = 250000
        self.cic_session_timeout_seconds = 30.0
        self.cic_phase_timeout_seconds = 120.0
        self.cic_max_attempts = 3
        # 发布重试状态机：每轮并发 DDL 的等待阶段超过该时长即被取消并记一次失败重试。
        self.retry_ddl_timeout_seconds = 45.0
        self.retry_backoff_seconds = 10.0

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print(
            "[FaultInjector:PgBusinessChangeInvalidIndexInjector] "
            f"Seeding {self.table} ({self.row_count} rows) and releasing the report index..."
        )
        self.recover(context)
        # 部署期种子/建索引/ANALYZE 是部署操作，不受发布窗口 statement_timeout
        # 基线约束；会话级 SET 只影响部署连接，快照恢复后的 Agent 会话仍持
        # postgresql.conf 的发布窗口基线。
        self._exec_sql("SET statement_timeout = 0;")
        with env.metrics_hidden():
            self._setup_schema()
            self._create_abandoned_cic_index()
            self._finalize_schema()
            self._install_ddl_freeze()
        self._start_release_stall()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(config["table"], "table")
        self.peer_table = _validate_sql_identifier(config["peer_table"], "peer_table")
        self.noise_table = _validate_sql_identifier(config["noise_table"], "noise_table")
        self.pk_column = _validate_sql_identifier(config["pk_column"], "pk_column")
        self.store_column = _validate_sql_identifier(config["store_column"], "store_column")
        self.date_column = _validate_sql_identifier(config["date_column"], "date_column")
        self.item_column = _validate_sql_identifier(config["item_column"], "item_column")
        self.amount_column = _validate_sql_identifier(config["amount_column"], "amount_column")
        self.payload_column = _validate_sql_identifier(config["payload_column"], "payload_column")
        self.invalid_index_name = _validate_sql_identifier(
            config["invalid_index_name"], "invalid_index_name"
        )
        # 谓词文本由场景合同（作者侧静态字符串）定义，原样拼入建索引 DDL。
        self.invalid_index_predicate = str(config.get("invalid_index_predicate", ""))
        self.ddl_freeze_trigger_name = str(config.get("ddl_freeze_trigger_name", ""))
        self.decoy_index_name = str(config.get("decoy_index_name", ""))
        self.item_index_name = str(config.get("item_index_name", ""))
        self.release_log_table = str(config.get("release_log_table", ""))
        self.release_task_name = str(config.get("release_task_name", ""))
        self.noise_index_name = _validate_sql_identifier(
            config["noise_index_name"], "noise_index_name"
        ) if config.get("noise_index_name") else ""
        self.noise_release_task_name = str(config.get("noise_release_task_name", ""))
        self.row_count = int(config["row_count"])
        self.seeded_rows = int(config["seeded_rows"])
        self.peer_row_count = int(config["peer_row_count"])
        self.noise_row_count = int(config["noise_row_count"])
        self.cic_session_timeout_seconds = float(config["cic_session_timeout_seconds"])
        self.cic_phase_timeout_seconds = float(config["cic_phase_timeout_seconds"])
        self.cic_max_attempts = int(config["cic_max_attempts"])
        self.controller_app_name = str(config["controller_app_name"])
        self.export_prepare_gid = _validate_sql_identifier(
            config["export_prepare_gid"], "export_prepare_gid"
        ) if config.get("export_prepare_gid") else ""
        self.export_ledger_table = str(config.get("export_ledger_table", ""))
        self.export_inbox_table = str(config.get("export_inbox_table", ""))
        self.export_batch_rows = int(config.get("export_batch_rows", 0))
        self.retry_app_name = str(config["retry_app_name"])

    def _setup_schema(self):
        self._exec_sql(
            f"DROP TABLE IF EXISTS {self.table} CASCADE;"
        )
        self._exec_sql(
            f"""
            CREATE TABLE {self.table} (
                {self.pk_column} bigserial PRIMARY KEY,
                {self.store_column} integer NOT NULL,
                {self.date_column} date NOT NULL,
                {self.item_column} integer NOT NULL,
                {self.amount_column} numeric(12, 2) NOT NULL,
                {self.payload_column} text NOT NULL
            );
            """
        )
        self._exec_sql(
            f"""
            INSERT INTO {self.table} (
                {self.store_column}, {self.date_column}, {self.item_column}, {self.amount_column}, {self.payload_column}
            )
            SELECT
                (g % 200) + 1,
                CURRENT_DATE - ((g % 730) || ' days')::interval,
                (g % 5000) + 1,
                ((g % 100000)::numeric / 100) + 1,
                repeat(md5(g::text), 4)
            FROM generate_series(1, {self.row_count}) AS g;
            """
        )
        if self.decoy_index_name:
            self._exec_sql(
                f"CREATE INDEX {self.decoy_index_name} ON {self.table} ({self.date_column});"
            )
        if self.item_index_name:
            self._exec_sql(
                f"CREATE INDEX {self.item_index_name} ON {self.table} ({self.item_column});"
            )
        self._exec_sql(
            f"DROP TABLE IF EXISTS {self.peer_table} CASCADE;"
        )
        self._exec_sql(
            f"""
            CREATE TABLE {self.peer_table} (
                {self.pk_column} bigserial PRIMARY KEY,
                {self.store_column} integer NOT NULL,
                {self.date_column} date NOT NULL,
                {self.item_column} integer NOT NULL,
                {self.amount_column} numeric(12, 2) NOT NULL,
                {self.payload_column} text NOT NULL
            );
            """
        )
        self._exec_sql(
            f"""
            INSERT INTO {self.peer_table} (
                {self.store_column}, {self.date_column}, {self.item_column}, {self.amount_column}, {self.payload_column}
            )
            SELECT
                (g % 200) + 1,
                CURRENT_DATE - ((g % 730) || ' days')::interval,
                (g % 5000) + 1,
                ((g % 100000)::numeric / 100) + 1,
                repeat(md5(g::text), 4)
            FROM generate_series(1, {self.peer_row_count}) AS g;
            """
        )
        self._exec_sql(
            f"CREATE INDEX idx_{self.peer_table}_store_date "
            f"ON {self.peer_table} ({self.store_column}, {self.date_column});"
        )
        if self.noise_row_count:
            self._exec_sql(
                f"DROP TABLE IF EXISTS {self.noise_table} CASCADE;"
            )
            self._exec_sql(
                f"""
                CREATE TABLE {self.noise_table} (
                    return_id bigserial PRIMARY KEY,
                    store_id integer NOT NULL,
                    item_id integer NOT NULL,
                    return_date date NOT NULL,
                    status text NOT NULL,
                    amount numeric(12, 2) NOT NULL,
                    reason text NOT NULL
                );
                """
            )
            self._exec_sql(
                f"""
                INSERT INTO {self.noise_table} (
                    store_id, item_id, return_date, status, amount, reason
                )
                SELECT
                    (g % 200) + 1,
                    (g % 5000) + 1,
                    CURRENT_DATE - ((g % 900) || ' days')::interval,
                    (ARRAY['RESTOCKED','REFUNDED','PENDING'])[1 + g % 3],
                    ((g % 40000)::numeric / 100) + 1,
                    repeat(md5('return-' || g::text), 3)
                FROM generate_series(1, {self.noise_row_count}) AS g;
                """
            )
            if self.noise_index_name:
                self._exec_sql(
                    f"CREATE INDEX {self.noise_index_name} "
                    f"ON {self.noise_table} (status);"
                )
        if self.release_log_table:
            self._exec_sql(
                f"DROP TABLE IF EXISTS {self.release_log_table} CASCADE;"
            )
            self._exec_sql(
                f"""
                CREATE TABLE {self.release_log_table} (
                    task_name text PRIMARY KEY,
                    target_object text NOT NULL,
                    status text NOT NULL,
                    attempts integer NOT NULL,
                    last_error text,
                    updated_at timestamptz NOT NULL DEFAULT now()
                );
                """
            )
            if self.retry_app_name:
                # Hard：发布系统仍在退避重试，遗留 RETRYING 行与历史任务噪声。
                log_rows = [
                    (self.release_task_name, self.table, "RETRYING", 3,
                     "context deadline exceeded"),
                    (self.noise_release_task_name, self.noise_table, "COMPLETED", 2, None),
                    ("nightly_rollup_job_patch", "store_rollup_daily", "COMPLETED", 1, None),
                    ("archive_policy_refresh", self.noise_table, "COMPLETED", 1, None),
                ]
            else:
                # Easy：发布系统在多次失败后放弃，遗留一条 FAILED 记录；
                # target_object 记录发布目标 DDL（含模板谓词），是目标定义的书证。
                log_rows = [
                    (self.release_task_name,
                     f"{self.invalid_index_name} ON {self.table} "
                     f"({self.store_column}, {self.date_column}) "
                     f"{self.invalid_index_predicate}".strip(),
                     "FAILED", 3,
                     "cancel statement during index validation"),
                ]
            values = ", ".join(
                "(" + ", ".join(
                    "NULL" if value is None else f"'{value}'"
                    for value in row
                ) + ")"
                for row in log_rows
            )
            self._exec_sql(
                f"""
                INSERT INTO {self.release_log_table} (
                    task_name, target_object, status, attempts, last_error
                ) VALUES {values};
                """
            )
        if self.export_ledger_table:
            # 报表导出管线的交付台账与导入缓冲区：台账按批次记录交付状态与重发
            # 策略（CHECK 公开全部合法值）；缓冲区保存各批次落地行。历史批次
            # batch_0 已提交完成，batch_2 仍在导出中，为台账查询提供真实噪声。
            self._exec_sql(
                f"DROP TABLE IF EXISTS {self.export_inbox_table} CASCADE;"
            )
            self._exec_sql(
                f"""
                CREATE TABLE {self.export_inbox_table} (
                    batch_id text NOT NULL,
                    row_no integer NOT NULL,
                    store_id integer NOT NULL,
                    sold_date date NOT NULL,
                    item_id integer NOT NULL,
                    amount numeric(12, 2) NOT NULL,
                    payload text NOT NULL,
                    PRIMARY KEY (batch_id, row_no)
                );
                """
            )
            self._exec_sql(
                f"""
                INSERT INTO {self.export_inbox_table} (
                    batch_id, row_no, store_id, sold_date, item_id, amount, payload
                )
                SELECT 'store_sales_report_export_2pc_batch_0', g, (g % 200) + 1,
                       CURRENT_DATE - interval '2 days', (g % 5000) + 1,
                       ((g % 100000)::numeric / 100) + 1, repeat(md5('export0-' || g::text), 4)
                FROM generate_series(1, 3200) AS g;
                """
            )
            self._exec_sql(
                f"DROP TABLE IF EXISTS {self.export_ledger_table} CASCADE;"
            )
            self._exec_sql(
                f"""
                CREATE TABLE {self.export_ledger_table} (
                    batch_id text PRIMARY KEY,
                    target_table text NOT NULL,
                    row_count integer NOT NULL,
                    delivery_status text NOT NULL
                        CHECK (delivery_status IN ('EXPORTING', 'DELIVERED', 'DELIVERY_CONFIRMED')),
                    redelivery_policy text NOT NULL
                        CHECK (redelivery_policy IN ('AUTO_REDELIVER', 'MANUAL_REPLAY', 'NO_REDELIVERY')),
                    committed_at timestamptz,
                    updated_at timestamptz NOT NULL DEFAULT now()
                );
                """
            )
            self._exec_sql(
                f"""
                INSERT INTO {self.export_ledger_table} (
                    batch_id, target_table, row_count, delivery_status,
                    redelivery_policy, committed_at, updated_at
                ) VALUES
                    ('store_sales_report_export_2pc_batch_0', '{self.export_inbox_table}',
                     3200, 'DELIVERY_CONFIRMED', 'NO_REDELIVERY',
                     now() - interval '2 days', now() - interval '2 days'),
                    ('{self.export_prepare_gid}', '{self.export_inbox_table}',
                     {self.export_batch_rows}, 'DELIVERY_CONFIRMED', 'NO_REDELIVERY',
                     NULL, now() - interval '3 hours'),
                    ('store_sales_report_export_2pc_batch_2', '{self.export_inbox_table}',
                     1800, 'EXPORTING', 'AUTO_REDELIVER',
                     NULL, now() - interval '20 minutes');
                """
            )

    def _create_abandoned_cic_index(self):
        """真实执行 CREATE INDEX CONCURRENTLY 并在校验阶段取消，遗留 invalid 索引。"""
        for attempt in range(1, self.cic_max_attempts + 1):
            if self._cancel_cic_once():
                return
            print(
                "[FaultInjector:PgBusinessChangeInvalidIndexInjector] "
                f"CIC cancel attempt {attempt} did not leave an invalid index; retrying."
            )
            payload = _json_object(
                self.env.execute_sql(
                    f"SELECT to_regclass('{self.invalid_index_name}')::text;"
                ),
                "probe leftover CIC index",
            )
            if payload["result"][0][0] is not None:
                self._exec_sql(f"DROP INDEX IF EXISTS {self.invalid_index_name};")
        raise RuntimeError(
            "Could not produce the abandoned CIC invalid index: "
            f"table={self.table}, index={self.invalid_index_name}, "
            f"attempts={self.cic_max_attempts}"
        )

    def _cancel_cic_once(self) -> bool | None:
        build_error = []
        spawn_worker = self._env_supports_background_probe()

        def run_cic():
            import psycopg2

            conn = None
            try:
                conn = psycopg2.connect(
                    host=self.env.host,
                    port=self.env.port,
                    user=self.env.user,
                    password=self.env.password,
                    dbname=self.env.dbname,
                    connect_timeout=5,
                    application_name="aiopsbench_cic_release_worker",
                )
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute("SET statement_timeout = 0;")
                    cur.execute(
                        f"CREATE INDEX CONCURRENTLY {self.invalid_index_name} "
                        f"ON {self.table} ({self.store_column}, {self.date_column}) "
                        f"{self.invalid_index_predicate};"
                    )
            except Exception as exc:
                build_error.append(str(exc))
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass

        worker = None
        if spawn_worker:
            worker = threading.Thread(target=run_cic, daemon=True)
            worker.start()

        deadline = time.monotonic() + self.cic_session_timeout_seconds
        cic_pid = None
        while time.monotonic() < deadline:
            payload = _json_object(
                self.env.execute_sql(
                    "SELECT pid FROM pg_stat_activity "
                    "WHERE application_name = 'aiopsbench_cic_release_worker' "
                    "AND state = 'active' AND pid <> pg_backend_pid();"
                ),
                "observe CIC release session",
            )
            rows = payload["result"]
            if rows:
                cic_pid = int(rows[0][0])
                break
            time.sleep(0.05)
        if cic_pid is None:
            # 轮询窗口内没有观测到建索引会话：等 CIC 自然结束，再按遗留状态分类。
            if worker is not None:
                worker.join(timeout=self.cic_phase_timeout_seconds)
                if worker.is_alive():
                    raise RuntimeError(
                        "CREATE INDEX CONCURRENTLY worker did not finish: "
                        f"table={self.table}, index={self.invalid_index_name}, "
                        f"timeout_seconds={self.cic_phase_timeout_seconds}, "
                        f"build_error={build_error}"
                    )
            return self._leftover_is_invalid()

        # 等待 CIC 进入校验阶段：indisready=true 且 indisvalid=false。此时取消
        # 会精确遗留一个被 DML 维护但 planner 不可用的 invalid 索引。
        deadline = time.monotonic() + self.cic_phase_timeout_seconds
        in_validation = False
        while time.monotonic() < deadline:
            # CIC 第一阶段提交前索引目录行尚不存在；to_regclass 缺失时返回 NULL
            # 而不是像 regclass 强转那样直接报错。
            payload = _json_object(
                self.env.execute_sql(
                    "SELECT i.indisready, i.indisvalid "
                    "FROM pg_class c JOIN pg_index i ON i.indexrelid = c.oid "
                    f"WHERE c.oid = (SELECT to_regclass('{self.invalid_index_name}'));"
                ),
                "poll CIC index readiness",
            )
            rows = payload["result"]
            if rows:
                indisready, indisvalid = bool(rows[0][0]), bool(rows[0][1])
                if indisready and not indisvalid:
                    in_validation = True
                    break
                if indisvalid:
                    break
            time.sleep(0.05)
        if in_validation:
            self._exec_sql(f"SELECT pg_cancel_backend({cic_pid});")
        if worker is not None:
            worker.join(timeout=60)
            if worker.is_alive():
                raise RuntimeError(
                    "CREATE INDEX CONCURRENTLY worker did not finish after cancellation: "
                    f"index={self.invalid_index_name}"
                )
        return self._leftover_is_invalid()

    def _env_supports_background_probe(self) -> bool:
        # 单元测试里 env 是协议 fake；只有真实 PGEnv 具备这些连接字段时才启动
        # 真实的 CIC 后台会话（与 PgQueryPerfFaultFingerprintProbe 同一模式）。
        return (
            isinstance(getattr(self.env, "host", None), str)
            and isinstance(getattr(self.env, "port", None), int)
            and isinstance(getattr(self.env, "user", None), str)
            and isinstance(getattr(self.env, "password", None), str)
            and isinstance(getattr(self.env, "dbname", None), str)
        )

    def _leftover_is_invalid(self) -> bool:
        payload = _json_object(
            self.env.execute_sql(
                "SELECT i.indisvalid "
                "FROM pg_class c JOIN pg_index i ON i.indexrelid = c.oid "
                f"WHERE c.oid = (SELECT to_regclass('{self.invalid_index_name}'));"
            ),
            "check cancelled CIC leftover state",
        )
        rows = payload["result"]
        return bool(rows) and not bool(rows[0][0])

    def _finalize_schema(self):
        self._exec_sql(f"ANALYZE {self.table};")
        self._exec_sql(f"ANALYZE {self.peer_table};")
        if self.noise_row_count:
            self._exec_sql(f"ANALYZE {self.noise_table};")

    def _install_ddl_freeze(self):
        """发布窗口的 DDL 变更冻结：发布系统把本库一切手工 CREATE INDEX 锁进
        发布管线（变更单 CFG-2291）。发布管线失败退出后冻结对象未随发布回滚，
        形成"索引修复必须先解除冻结"的真实堵点。PG 的 event trigger tag 过滤
        只接受 'CREATE INDEX'，实测它同时拦截普通与 CONCURRENTLY 变体；不触碰
        写入、查询、EXPLAIN 与其它 DDL。"""
        if not self.ddl_freeze_trigger_name:
            return
        self._exec_sql(
            """
            CREATE OR REPLACE FUNCTION aiopsbench_release_ddl_guard()
            RETURNS event_trigger AS $$
            BEGIN
                RAISE EXCEPTION 'index DDL is frozen by release change CFG-2291: '
                                'the change window routes all index DDL through '
                                'the release pipeline; manual index DDL is rejected';
            END;
            $$ LANGUAGE plpgsql;
            """
        )
        self._exec_sql(
            f"""
            CREATE EVENT TRIGGER {self.ddl_freeze_trigger_name}
            ON ddl_command_start
            WHEN TAG IN ('CREATE INDEX')
            EXECUTE FUNCTION aiopsbench_release_ddl_guard();
            """
        )

    def _start_release_stall(self):
        if not self.controller_app_name or not self.retry_app_name:
            return
        """重建发布卡点的运行期症状：

        - 发布控制器会话以 idle in transaction 持有 store_sales 的 SHARE UPDATE
          EXCLUSIVE 锁；发布重试的 DROP INDEX CONCURRENTLY 因拿不到 SUE 而阻塞在
          锁获取阶段。
        - 报表导出工具崩溃遗留的孤儿 prepared transaction 持有旧快照与目标表的
          AccessShareLock：它是"pre-existing transaction"，使一切并发索引 DDL
          （DIC）在拿到锁之后的"等待旧事务结束"阶段永不完成——发布任务超时取消
          自己、记一次失败重试、退避后再来。prepared transaction 没有 PID，
          pg_terminate_backend 无法解除，Agent 必须发现 pg_prepared_xacts 并处置。
        Agent 必须识别并解除两类卡点，修复 DDL 才能执行。
        """
        self._stop_release_stall()
        self._stall_stop = threading.Event()
        if self._env_supports_background_probe():
            self._controller_conn = self._connect(self.controller_app_name)
            self._controller_thread = threading.Thread(
                target=self._run_controller_session, daemon=True
            )
            self._controller_thread.start()
            if self.export_prepare_gid:
                self._create_orphan_prepared_transaction()
            self._retry_conn = self._connect(self.retry_app_name)
            self._retry_thread = threading.Thread(
                target=self._run_retry_release_session, daemon=True
            )
            self._retry_thread.start()
        self._wait_for_release_stall()

    def _connect(self, application_name: str):
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
        conn.autocommit = True
        return conn

    def _run_controller_session(self):
        try:
            with self._controller_conn.cursor() as cur:
                cur.execute("SET idle_in_transaction_session_timeout = 0;")
                cur.execute("SET statement_timeout = 0;")
                cur.execute("BEGIN;")
                cur.execute(
                    f"LOCK TABLE {self.table} IN SHARE UPDATE EXCLUSIVE MODE;"
                )
                cur.execute("SELECT 1;")
            while not self._stall_stop.is_set():
                # 事务保持打开即可持锁；线程只等待停止信号。
                self._stall_stop.wait(1)
        except Exception as exc:
            print(
                "[FaultInjector:PgBusinessChangeInvalidIndexInjector] "
                f"Release controller session stopped: {exc}"
            )

    def _create_orphan_prepared_transaction(self):
        """报表导出工具的两阶段提交遗留：短连接在事务内向导入缓冲表写入本批次
        销量补录数据后 PREPARE，COMMIT PREPARED 前工具崩溃——孤儿 in-doubt
        transaction 持有目标表快照与 AccessShareLock（阻塞一切并发索引 DDL 的
        等待阶段），且携带 5,000 行"下游已确认收到、不会重发"的业务数据：
        pg_terminate_backend 无法解除，ROLLBACK PREPARED 会不可逆丢弃该批次，
        处置方向必须依据交付台账裁决。没有活动会话持有它。"""
        import psycopg2

        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=5,
            application_name="store-sales-report-export",
        )
        try:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("SET idle_in_transaction_session_timeout = 0;")
                cur.execute("BEGIN;")
                cur.execute(
                    f"""
                    INSERT INTO {self.export_inbox_table} (
                        batch_id, row_no, store_id, sold_date, item_id, amount, payload
                    )
                    SELECT '{self.export_prepare_gid}', g, (g % 200) + 1, CURRENT_DATE,
                           (g % 5000) + 1, ((g % 100000)::numeric / 100) + 1,
                           repeat(md5('export1-' || g::text), 4)
                    FROM generate_series(1, {self.export_batch_rows}) AS g;
                    """
                )
                cur.execute(
                    f"SELECT count(*), COALESCE(sum({self.amount_column}), 0) "
                    f"FROM {self.table};"
                )
                cur.fetchone()
                cur.execute(f"PREPARE TRANSACTION '{self.export_prepare_gid}';")
        finally:
            conn.close()

    def _run_retry_release_session(self):
        """发布重试状态机：DROP INDEX CONCURRENTLY → CREATE INDEX CONCURRENTLY。

        每一步并发 DDL 若在等待阶段超过 retry_ddl_timeout_seconds 未完成，发布任务
        通过 pg_cancel_backend 取消自己并记一次失败重试（attempts/last_error 更新到
        发布日志），退避后重试；会话被终止则发布任务停止。
        """
        try:
            with self._retry_conn.cursor() as cur:
                cur.execute("SET lock_timeout = 0;")
                cur.execute("SET statement_timeout = 0;")
                while not self._stall_stop.is_set():
                    drop_sql = (
                        f"DROP INDEX CONCURRENTLY IF EXISTS {self.invalid_index_name};"
                    )
                    if not self._run_concurrent_ddl(cur, drop_sql, "drop"):
                        self._update_release_log(
                            cur, "RETRYING", "context deadline exceeded at drop phase"
                        )
                        self._stall_stop.wait(self.retry_backoff_seconds)
                        continue
                    create_sql = (
                        f"CREATE INDEX CONCURRENTLY {self.invalid_index_name} "
                        f"ON {self.table} ({self.store_column}, {self.date_column}) "
                        f"{self.invalid_index_predicate};"
                    )
                    if not self._run_concurrent_ddl(cur, create_sql, "create"):
                        self._update_release_log(
                            cur, "RETRYING", "context deadline exceeded at create phase"
                        )
                        self._stall_stop.wait(self.retry_backoff_seconds)
                        continue
                    self._update_release_log(cur, "COMPLETED", None)
                    break
        except Exception as exc:
            print(
                "[FaultInjector:PgBusinessChangeInvalidIndexInjector] "
                f"Release retry task stopped: {exc}"
            )

    def _run_concurrent_ddl(self, cur, ddl_sql: str, phase: str) -> bool:
        """执行一条并发 DDL；等待阶段超时则取消自己并返回 False。"""
        import psycopg2

        with cur.connection.cursor() as pid_cur:
            pid_cur.execute("SELECT pg_backend_pid();")
            retry_pid = int(pid_cur.fetchone()[0])
        cancel_timer = threading.Timer(
            self.retry_ddl_timeout_seconds,
            self._cancel_retry_backend,
            args=(retry_pid,),
        )
        cancel_timer.daemon = True
        cancel_timer.start()
        try:
            cur.execute(ddl_sql)
            return True
        except psycopg2.errors.QueryCanceled as exc:
            print(
                "[FaultInjector:PgBusinessChangeInvalidIndexInjector] "
                f"Release retry {phase} cancelled after "
                f"{self.retry_ddl_timeout_seconds}s: {exc}"
            )
            return False
        finally:
            cancel_timer.cancel()

    def _cancel_retry_backend(self, pid: int):
        """独立短连接取消发布重试会话正在等待的 DDL。"""
        import psycopg2

        conn = None
        try:
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.env.user,
                password=self.env.password,
                dbname=self.env.dbname,
                connect_timeout=5,
                application_name="aiopsbench_release_retry_watchdog",
            )
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT pg_cancel_backend(pid) FROM pg_stat_activity "
                    f"WHERE pid = {int(pid)} "
                    f"AND application_name = '{self.retry_app_name}';"
                )
        except Exception as exc:
            print(
                "[FaultInjector:PgBusinessChangeInvalidIndexInjector] "
                f"Release retry watchdog failed to cancel pid {pid}: {exc}"
            )
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _update_release_log(self, cur, status: str, last_error: str | None):
        if not self.release_log_table or not self.release_task_name:
            return
        with cur.connection.cursor() as log_cur:
            log_cur.execute(
                f"UPDATE {self.release_log_table} "
                "SET status = %s, attempts = attempts + 1, "
                "last_error = %s, updated_at = now() "
                "WHERE task_name = %s;",
                (status, last_error, self.release_task_name),
            )

    def _wait_for_release_stall(self):
        deadline = time.monotonic() + 30.0
        while time.monotonic() < deadline:
            escaped_controller = self.controller_app_name.replace("'", "''")
            escaped_retry = self.retry_app_name.replace("'", "''")
            escaped_gid = self.export_prepare_gid.replace("'", "''")
            payload = _json_object(
                self.env.execute_sql(
                    "SELECT count(*) FILTER ("
                    f"WHERE application_name = '{escaped_controller}' "
                    "AND state = 'idle in transaction'), "
                    f"(SELECT count(*) FROM pg_prepared_xacts "
                    f"WHERE gid = '{escaped_gid}'), "
                    "count(*) FILTER ("
                    f"WHERE application_name = '{escaped_retry}' "
                    "AND state = 'active' AND wait_event_type = 'Lock') "
                    "FROM pg_stat_activity "
                    "WHERE datname = current_database() "
                    "AND pid <> pg_backend_pid();"
                ),
                "verify release-stall runtime sessions",
            )
            idle_controllers, prepared_transactions, locked_retries = payload["result"][0]
            if (
                int(idle_controllers) >= 1
                and int(prepared_transactions) >= 1
                and int(locked_retries) >= 1
            ):
                return
            time.sleep(0.2)
        raise RuntimeError(
            "Release-stall runtime sessions did not become observable: "
            f"controller_app={self.controller_app_name}, "
            f"prepared_gid={self.export_prepare_gid}, retry_app={self.retry_app_name}, "
            f"observed={payload['result'][0]}"
        )

    def _stop_release_stall(self):
        if not self.controller_app_name and not self.retry_app_name:
            return
        self._stall_stop.set()
        steps = []
        for label, app_name in (
            ("release retry session", self.retry_app_name),
            ("release controller session", self.controller_app_name),
        ):
            if not app_name:
                continue
            escaped = app_name.replace("'", "''")
            steps.append((
                f"terminate {label}",
                lambda escaped=escaped: _require_sql_success(
                    self.env.execute_sql(
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        f"WHERE application_name = '{escaped}' "
                        "AND pid <> pg_backend_pid();"
                    ),
                    f"terminate {escaped}",
                ),
            ))
        if self.export_prepare_gid:
            # 先终止会话再回滚孤儿 prepared transaction：重试会话可能在等待阶段
            # 持有并发 DDL，解除干涉后它会在清理前瞬间推进，破坏持久目录状态。
            # 必须在 DROP 对象之前完成（prepared xact 的 AccessShareLock 会卡死
            # AccessExclusive 的 DROP TABLE）。
            steps.append((
                "rollback orphan prepared transaction",
                self._rollback_orphan_prepared_transaction,
            ))
        if self._controller_conn is not None:
            steps.append(("close controller connection", self._controller_conn.close))
        if self._retry_conn is not None:
            steps.append(("close retry connection", self._retry_conn.close))
        if self._controller_thread is not None:
            steps.append((
                "join controller thread",
                lambda: _join_thread(self._controller_thread, 5, "release controller thread"),
            ))
        if self._retry_thread is not None:
            steps.append((
                "join retry thread",
                lambda: _join_thread(self._retry_thread, 5, "release retry thread"),
            ))
        _run_cleanup_steps(
            "Release-stall session cleanup",
            steps,
        )
        self._controller_conn = None
        self._controller_thread = None
        self._retry_conn = None
        self._retry_thread = None

    def _rollback_orphan_prepared_transaction(self):
        gid_exists = _json_object(
            self.env.execute_sql(
                "SELECT count(*) FROM pg_prepared_xacts "
                f"WHERE gid = '{self.export_prepare_gid}';"
            ),
            "check orphan prepared transaction before rollback",
        )["result"][0][0]
        if int(gid_exists):
            self._exec_sql(f"ROLLBACK PREPARED '{self.export_prepare_gid}';")

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                "SELECT i.indisready, i.indisvalid "
                "FROM pg_index i "
                "JOIN pg_class t ON t.oid = i.indrelid "
                f"WHERE t.relname = '{self.table}' AND i.indisvalid = false;"
            ),
            "verify invalid-index fault image",
        )
        rows = payload["result"]
        if len(rows) != 1 or rows[0][0] is not True:
            raise RuntimeError(
                "Invalid-index fault image does not match the Case: expected exactly "
                f"one indisvalid=false index on {self.table}, observed={rows}"
            )
        peer_payload = _json_object(
            self.env.execute_sql(
                "SELECT count(*) FROM pg_index i "
                "JOIN pg_class t ON t.oid = i.indrelid "
                f"WHERE t.relname = '{self.peer_table}' AND i.indisvalid = false;"
            ),
            "verify peer table index health",
        )
        if int(peer_payload["result"][0][0]) != 0:
            raise RuntimeError(
                f"Healthy peer table {self.peer_table} must not carry invalid indexes"
            )
        if self.ddl_freeze_trigger_name:
            guard_payload = _json_object(
                self.env.execute_sql(
                    "SELECT count(*) FROM pg_event_trigger "
                    f"WHERE evtname = '{self.ddl_freeze_trigger_name}';"
                ),
                "verify release DDL freeze trigger",
            )
            if int(guard_payload["result"][0][0]) != 1:
                raise RuntimeError(
                    "Release DDL freeze trigger is missing from the fault image: "
                    f"trigger={self.ddl_freeze_trigger_name}"
                )

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._verify_persistent_state()
        self._start_release_stall()
        print(
            "[FaultInjector:PgBusinessChangeInvalidIndexInjector] "
            f"Persistent invalid index verified on {self.table}; "
            "release stall rebuilt."
        )

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        case = context.case
        baseline = _json_object(
            env.execute_sql(
                f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {case.representative_query}"
            ),
            "measure fault-time representative query baseline",
        )
        baseline_plan = baseline["result"]
        baseline_seconds = execution_time_seconds(baseline_plan)
        if baseline_seconds is None or baseline_seconds <= 0:
            raise RuntimeError(
                "Fault-time representative query baseline is not measurable: "
                f"query={case.representative_query!r}, plan={baseline_plan!r}"
            )
        truth = _json_object(
            env.execute_sql(
                "SELECT count(*), COALESCE(sum(amount), 0) "
                f"FROM {self.table} WHERE {self.pk_column} <= {self.seeded_rows};"
            ),
            "snapshot seeded business truth",
        )
        seeded_truth = truth["result"][0]
        evidence = {
            "fault_plan": baseline_plan,
            "fault_query_seconds": baseline_seconds,
            "seeded_truth": seeded_truth,
            "invalid_index_state": env.execute_sql(
                "SELECT t.relname, c.relname, i.indisready, i.indisvalid "
                "FROM pg_index i "
                "JOIN pg_class c ON c.oid = i.indexrelid "
                "JOIN pg_class t ON t.oid = i.indrelid "
                f"WHERE t.relname IN ('{self.table}', '{self.peer_table}') "
                "ORDER BY t.relname, c.relname;"
            ),
        }
        if self.export_prepare_gid and self.export_inbox_table:
            evidence["export_batch_truth"] = {
                "batch_id": self.export_prepare_gid,
                "batch_rows": self.export_batch_rows,
            }
        if self.noise_row_count:
            noise_truth = _json_object(
                env.execute_sql(
                    "SELECT count(*), COALESCE(sum(amount), 0) "
                    f"FROM {self.noise_table} WHERE return_id <= {self.noise_row_count};"
                ),
                "snapshot noise table seeded truth",
            )
            evidence["noise_truth"] = noise_truth["result"][0]
        return evidence

    def quiesce(self, context: FaultLifecycleContext):
        # 快照保存前停止运行期卡点会话；持久故障只保留目录状态。
        self._configure(context.config, context.env)
        self._stop_release_stall()
        print(
            "[FaultInjector:PgBusinessChangeInvalidIndexInjector] quiesce: "
            "release stall sessions stopped."
        )

    def recover(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        print(
            "[FaultInjector:PgBusinessChangeInvalidIndexInjector] "
            "Recovering invalid-index scenario objects..."
        )
        self._stop_release_stall()
        steps = [
            (
                f"terminate leftover release worker sessions",
                lambda: _require_sql_success(
                    self.env.execute_sql(
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        "WHERE application_name = 'aiopsbench_cic_release_worker' "
                        "AND pid <> pg_backend_pid();"
                    ),
                    "terminate leftover CIC release sessions",
                ),
            ),
        ]
        if self.ddl_freeze_trigger_name:
            escaped_trigger = self.ddl_freeze_trigger_name.replace("'", "''")
            steps.append((
                f"drop release DDL freeze {escaped_trigger}",
                lambda: self._exec_sql(
                    f"DROP EVENT TRIGGER IF EXISTS {escaped_trigger};"
                ),
            ))
            steps.append((
                "drop release ddl guard function",
                lambda: self._exec_sql(
                    "DROP FUNCTION IF EXISTS aiopsbench_release_ddl_guard();"
                ),
            ))
        steps += [
            (f"drop {self.table}", lambda: self._exec_sql(
                f"DROP TABLE IF EXISTS {self.table} CASCADE;")),
            (f"drop {self.peer_table}", lambda: self._exec_sql(
                f"DROP TABLE IF EXISTS {self.peer_table} CASCADE;")),
        ]
        if self.noise_row_count:
            steps.append((f"drop {self.noise_table}", lambda: self._exec_sql(
                f"DROP TABLE IF EXISTS {self.noise_table} CASCADE;")))
        if self.release_log_table:
            steps.append((f"drop {self.release_log_table}", lambda: self._exec_sql(
                f"DROP TABLE IF EXISTS {self.release_log_table} CASCADE;")))
        if self.export_ledger_table:
            steps.append((f"drop {self.export_ledger_table}", lambda: self._exec_sql(
                f"DROP TABLE IF EXISTS {self.export_ledger_table} CASCADE;")))
        if self.export_inbox_table:
            steps.append((f"drop {self.export_inbox_table}", lambda: self._exec_sql(
                f"DROP TABLE IF EXISTS {self.export_inbox_table} CASCADE;")))
        _run_cleanup_steps(
            f"Invalid-index cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )

    def _exec_sql(self, sql: str):
        return _require_sql_success(
            self.env.execute_sql(sql),
            f"invalid-index injector SQL: {sql[:120]}",
        )


class PgBusinessChangeInvalidIndexScenario(PostgresScenario):
    scenario_id = "pg_business_change_invalid_index"
    description = (
        "Report latency regression caused by an invalid index left behind by an "
        "interrupted CREATE INDEX CONCURRENTLY."
    )
    cases = (
        _PGBUSINESSCHANGEINVALIDINDEXSCENARIO_HARD_CASE,
        _PGBUSINESSCHANGEINVALIDINDEXSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgBusinessChangeInvalidIndexCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgBusinessChangeInvalidIndexInjector,
                config={
                    "table": case.table,
                    "peer_table": case.peer_table,
                    "noise_table": case.noise_table,
                    "pk_column": case.pk_column,
                    "store_column": case.store_column,
                    "date_column": case.date_column,
                    "item_column": case.item_column,
                    "amount_column": case.amount_column,
                    "payload_column": case.payload_column,
                    "invalid_index_name": case.invalid_index_name,
                    "invalid_index_predicate": case.invalid_index_predicate,
                    "ddl_freeze_trigger_name": case.ddl_freeze_trigger_name,
                    "decoy_index_name": case.decoy_index_name,
                    "item_index_name": case.item_index_name,
                    "release_log_table": case.release_log_table,
                    "release_task_name": case.release_task_name,
                    "noise_index_name": case.noise_index_name,
                    "noise_release_task_name": case.noise_release_task_name,
                    "controller_app_name": case.controller_app_name,
                    "export_prepare_gid": case.export_prepare_gid,
                    "export_ledger_table": case.export_ledger_table,
                    "export_inbox_table": case.export_inbox_table,
                    "export_batch_rows": case.export_batch_rows,
                    "retry_app_name": case.retry_app_name,
                    "row_count": case.row_count,
                    "seeded_rows": case.seeded_rows,
                    "peer_row_count": case.peer_row_count,
                    "noise_row_count": case.noise_row_count,
                    "cic_session_timeout_seconds": case.cic_session_timeout_seconds,
                    "cic_phase_timeout_seconds": case.cic_phase_timeout_seconds,
                    "cic_max_attempts": case.cic_max_attempts,
                },
            ),
        )
