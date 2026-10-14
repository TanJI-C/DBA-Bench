from collections.abc import Mapping
from dataclasses import dataclass, replace

from src.execution.history.records import HistoricalRecordSource
from src.scenarios.evaluation.tidb.query_perf.statistics_drift_frozen_history import (
    TidbQueryPerfStatisticsDriftFrozenHistoryEvaluatorCase,
    TidbQueryPerfStatisticsDriftFrozenHistoryPartitionEvaluatorCase,
)
from src.scenarios.frozen_history import (
    DecoyDirection,
    DecoyKind,
    HistoryDecoySpec,
    FrozenHistorySpec,
)
from src.scenarios.tidb.common import validate_sql_identifier
from src.scenarios.faults import FaultLifecycleContext
from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase, WorkloadProfile

from ...base import (
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime
from .statistics_drift import TidbQueryPerfStatisticsDriftInjector


DB = "benchops_mf_qp04"
TARGET_TABLES = ("mf_qp04_order_events_a", "mf_qp04_order_events_b")
CONTROL_TABLES = (
    "mf_qp04_order_events_control_a",
    "mf_qp04_order_events_control_b",
)
NOISE_TABLES = ("mf_qp04_order_events_noise_a", "mf_qp04_order_events_noise_b")
BENIGN_COMPACTION_TABLE = "mf_qp04_compaction_buffer"
BENIGN_COMPACTION_ROWS = 20_000
INDEX_NAME = "idx_mf_qp04_routing_key"
STATUS_INDEX_NAME = "idx_mf_qp04_status"
TARGET_VALUE = "r29"
STATUS_VALUE = "pending"


def _aggregate_query(tables: tuple[str, str], alias: str) -> str:
    return (
        "SELECT COUNT(*) AS matched_rows, "
        "CAST(SUM(amount) AS DECIMAL(18,2)) AS total_amount "
        "FROM ("
        f"SELECT id, routing_key, status, amount FROM {DB}.{tables[0]} UNION ALL "
        f"SELECT id, routing_key, status, amount FROM {DB}.{tables[1]}"
        f") AS {alias} WHERE routing_key='{TARGET_VALUE}' OR status='{STATUS_VALUE}'"
    )


BUSINESS_QUERY = _aggregate_query(TARGET_TABLES, "target_shards")
CONTROL_QUERY = _aggregate_query(CONTROL_TABLES, "control_shards")
NOISE_QUERY = _aggregate_query(NOISE_TABLES, "noise_shards")


def _benign_compaction_rewrite_sql(start_id: int) -> str:
    end_id = start_id + 999
    return (
        f"REPLACE INTO {DB}.{BENIGN_COMPACTION_TABLE} "
        "(id, routing_key, status, amount, payload) "
        "SELECT id, routing_key, status, amount, "
        "RPAD(CONCAT('benign-compaction-', FLOOR(UNIX_TIMESTAMP() / 10)), 240, 'x') "
        f"FROM {DB}.{BENIGN_COMPACTION_TABLE} WHERE id BETWEEN {start_id} AND {end_id}"
    )


class TidbQueryPerfStatisticsDriftFrozenHistoryInjector(TidbQueryPerfStatisticsDriftInjector):
    """Reuse the real QP04 lifecycle with an independent frozen-history contract."""

    retain_workload_after_metric_history = True

    def __init__(self) -> None:
        self._frozen_history_environment_prepared = False

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Keep the fault state active through the Agent phase."""

    def _configure(self, config: Mapping[str, object]) -> None:
        super()._configure(config)
        self.benign_compaction_table = validate_sql_identifier(
            str(config["benign_compaction_table"]), "benign compaction table"
        )
        self.benign_compaction_rows = int(config["benign_compaction_buffer_rows"])

    def prepare_frozen_history_environment(self, context: FaultLifecycleContext) -> None:
        """Build the business fixture that frozen history capture samples from.

        Frozen-history history reads ``statistics_state`` from the six shards during
        warmup and normal capture, while the distribution-shift fault is only
        installed into the target window, so the baseline tables and the benign
        compaction buffer must already exist before capture starts. Statistics are
        collected here on the pre-shift distribution; the later shift against these
        stale statistics is exactly the fault evidence.
        """
        if self._frozen_history_environment_prepared:
            raise RuntimeError(
                "frozen-history QP04 environment was already prepared: "
                f"scenario={context.scenario_id!r}, case={context.case_id!r}"
            )
        self._configure(context.config)
        env = context.env
        with env.metrics_hidden():
            for table in (*self.target_tables, *self.control_tables, *self.noise_tables):
                self._create_table(env, table)
                self._load_rows(
                    env,
                    table,
                    self.initial_rows,
                    self.initial_target_rows,
                    0,
                    "baseline",
                )
                self._collect_statistics(env, table)
            self._create_compaction_buffer(env)
            self._load_compaction_buffer(env)
            self._collect_statistics(env, self.benign_compaction_table)
        self._frozen_history_environment_prepared = True

    def install(self, context: FaultLifecycleContext) -> None:
        """Shift the distribution after collection instead of rebuilding the fixture."""
        self._configure(context.config)
        if not self._frozen_history_environment_prepared:
            raise RuntimeError(
                "frozen-history QP04 install requires prepare_frozen_history_environment: "
                f"scenario={context.scenario_id!r}, case={context.case_id!r}"
            )
        self._capture_owned_state(context.env)
        self._disable_auto_analyze(context.env)
        for table in self.target_tables:
            self._load_distribution_shift(context.env, table, self.skew_rows)
        for table in self.noise_tables:
            self._load_distribution_shift(context.env, table, self.noise_skew_rows)
        self._verify_fault_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        super().activate(context)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        return super().prepare_observability(context)

    def quiesce(self, context: FaultLifecycleContext) -> None:
        super().quiesce(context)

    def recover(self, context: FaultLifecycleContext) -> None:
        super().recover(context)

    def _create_compaction_buffer(self, env) -> None:
        # The workload init.sql already creates and fills this buffer with its
        # own rows; the injector owns the table from here, so drop and rebuild
        # it instead of colliding with the bootstrap CREATE.
        self._require_success(
            env.execute_sql(
                f"DROP TABLE IF EXISTS {self.db}.{self.benign_compaction_table}"
            ),
            f"drop stale QP04 frozen-history benign compaction buffer {self.db}.{self.benign_compaction_table}",
        )
        self._require_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.benign_compaction_table} ("
                "id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                "routing_key VARCHAR(16) NOT NULL, "
                "status VARCHAR(16) NOT NULL, "
                "amount DECIMAL(12,2) NOT NULL, "
                "payload VARCHAR(240) NOT NULL, "
                "KEY idx_mf_qp04_compaction_routing (routing_key), "
                "KEY idx_mf_qp04_compaction_status (status), "
                "KEY idx_mf_qp04_compaction_payload (payload))"
            ),
            f"create QP04 frozen-history benign compaction buffer {self.db}.{self.benign_compaction_table}",
        )

    def _load_compaction_buffer(self, env) -> None:
        self._require_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.benign_compaction_table} "
                "(routing_key, status, amount, payload) "
                "SELECT IF(n % 2 = 0, 'r91', 'r92'), "
                "IF(n % 3 = 0, 'closed', 'open'), "
                "CAST(n AS DECIMAL(12,2)), RPAD('initial-compaction-', 240, 'x') "
                "FROM (SELECT ROW_NUMBER() OVER () AS n "
                "FROM INFORMATION_SCHEMA.COLUMNS first_source "
                "CROSS JOIN INFORMATION_SCHEMA.COLUMNS second_source "
                f"LIMIT {self.benign_compaction_rows}) source"
            ),
            f"load QP04 frozen-history benign compaction buffer rows={self.benign_compaction_rows}",
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfStatisticsDriftFrozenHistoryForHistoryInvestigationScenarioCase(TiDBScenarioCase):
    db: str
    table: str
    partner_table: str
    control_table: str
    control_partner_table: str
    noise_table: str
    noise_partner_table: str
    index_name: str
    status_index_name: str
    target_column: str
    target_value: str
    status_column: str
    status_value: str
    control_query: str
    initial_rows: int
    initial_target_rows: int
    skew_rows: int
    control_rows: int
    control_target_rows: int
    noise_skew_rows: int
    shift_target_rows: int
    shift_status_rows: int
    minimum_estimate_actual_ratio: float
    business_query: str


_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="mf_qp04_target_order_aggregate",
            sql=BUSINESS_QUERY,
            qps=0.8,
            tier="OLAP_BURST",
            application_name="order-report-target",
        ),
        WorkloadProfile(
            name="mf_qp04_control_order_aggregate",
            sql=CONTROL_QUERY,
            qps=0.8,
            tier="OLAP_BURST",
            application_name="order-report-control",
        ),
        WorkloadProfile(
            name="mf_qp04_noise_order_aggregate",
            sql=NOISE_QUERY,
            qps=0.25,
            tier="OLAP_BURST",
            application_name="order-report-noise",
        ),
        WorkloadProfile(
            name="mf_qp04_control_point_read",
            sql=(
                f"SELECT id, amount FROM {DB}.{CONTROL_TABLES[0]} "
                f"WHERE routing_key='{TARGET_VALUE}' ORDER BY id LIMIT 20"
            ),
            qps=1.0,
            tier="OLTP_CORE",
            application_name="order-control-api",
        ),
        WorkloadProfile(
            name="mf_qp04_history_probe_noise",
            sql=(
                "SELECT DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY "
                "FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY "
                "ORDER BY SUM_LATENCY DESC LIMIT 20"
            ),
            qps=0.5,
            tier="MONITORING",
            application_name="topsql-refresh",
        ),
        *tuple(
            WorkloadProfile(
                name=f"mf_qp04_benign_compaction_writer_{start_id}",
                sql=_benign_compaction_rewrite_sql(start_id),
                qps=0.15,
                tier="MAINTENANCE_IO",
                commit=True,
                application_name="benign-compaction-writer",
            )
            for start_id in (1, 5001, 10001, 15001)
        ),
    ),
    worker_count=4,
    seed=0x4D02,
    start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
    warmup_seconds=20,
)


_FROZEN_HISTORY_HISTORY = FrozenHistorySpec(
    schema_version=1,
    duration_seconds=12 * 60 * 60,
    normal_capture_seconds=180,
    fault_capture_seconds=150,
    base_step_seconds=10,
    overview_step_seconds=30,
    block_min_seconds=60,
    block_max_seconds=90,
    transition_seconds=30,
    target_age_seconds_range=(1800, 7200),
    required_metrics=(
        "statistics_state",
        "plan_cardinality",
        "query_latency",
        "qps",
        "cpu",
        "disk_io",
    ),
    record_sources=(
        HistoricalRecordSource.COMPONENT_LOG,
        HistoricalRecordSource.TOPSQL,
        HistoricalRecordSource.SLOW_QUERIES,
    ),
    decoys=(
        HistoryDecoySpec(
            decoy_id="benign-olap-burst",
            kind=DecoyKind.METRIC_ONLY,
            metric="query_latency",
            field="p99_ms",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=3,
            duration_seconds=120,
            amplitude_mad=2.5,
        ),
        HistoryDecoySpec(
            decoy_id="benign-compaction",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="disk_io",
            field="write_mb_per_second",
            target="tikv/tikv-0",
            direction=DecoyDirection.SPIKE,
            count=2,
            duration_seconds=60,
            minimum_deviation_mad=2.0,
        ),
        HistoryDecoySpec(
            decoy_id="noise-shard-shift",
            kind=DecoyKind.METRIC_ONLY,
            metric="query_latency",
            field="average_ms",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=2,
            duration_seconds=90,
            amplitude_mad=1.8,
        ),
        HistoryDecoySpec(
            decoy_id="session-toggle-decoy",
            kind=DecoyKind.METRIC_ONLY,
            metric="query_latency",
            field="p95_ms",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=2,
            duration_seconds=90,
            amplitude_mad=2.0,
        ),
    ),
    max_points_per_series=7200,
    max_scalar_samples_per_response=100000,
    max_history_records_per_response=400,
    metric_targets={
        "statistics_state": (None,),
        "plan_cardinality": (None,),
        "query_latency": (None,),
        "qps": (None,),
        "cpu": ("tidb/tidb-0", "tikv/tikv-0"),
        "disk_io": ("tikv/tikv-0",),
    },
    metric_rate_windows={
        "query_latency": 30,
        "qps": 30,
        "cpu": 30,
        "disk_io": 30,
    },
)


_CASE = TidbQueryPerfStatisticsDriftFrozenHistoryForHistoryInvestigationScenarioCase(
    case_id="statistics_drift_history_investigation",
    case_no=0,
    evaluator=TidbQueryPerfStatisticsDriftFrozenHistoryEvaluatorCase,
    title="历史统计分布漂移与 affected-session IndexMerge 共同造成订单聚合计划退化。",
    alert=(
        "[CRITICAL] [Grafana/TiDB-Query-Detail] 某订单聚合 SQL 指纹在过去一段业务窗口内 P95 "
        "从约 25ms 升到 2.8s，processed keys 同步上升；其它相似聚合和集群可用性没有同步异常。"
        "请从历史时序、历史记录和当前 SQL 观测还原先后关系，排除相邻 workload 和资源事件，"
        "在不改变业务结果的前提下恢复请求。题面授权必要的、可回滚且范围限定的 target 统计刷新和 affected session 设置；"
        "不授权全局策略、业务数据/schema/index 修改、停止业务或重启集群组件。"
    ),
    initial_state={
        "status": "degraded",
        "symptom": "historical_order_aggregate_regression",
        "current_locks": "none_required",
    },
    expected_target={
        "status": "recovered",
        "estimate_actual_ratio_at_most": 2.0,
        "business_result_consistent": True,
        "target_statistics_fresh": True,
        "target_plan_operator": "IndexMerge",
    },
    background_workload=_BACKGROUND_WORKLOAD,
    frozen_history=_FROZEN_HISTORY_HISTORY,
    metric_history_adapter_config={
        "database": DB,
        "tables": (*TARGET_TABLES, *CONTROL_TABLES, *NOISE_TABLES),
        "plan_queries": {
            "target": BUSINESS_QUERY,
            "control": CONTROL_QUERY,
        },
        "statement_matchers": {
            "target": TARGET_TABLES,
            "control": CONTROL_TABLES,
            "noise": NOISE_TABLES,
        },
    },
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        tikv_memory_mb=4096,
        tidb_memory_mb=2048,
        sql_timeout_seconds=300,
        image_group_key="qp04-frozen-history-statistics-drift",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.741419,
        reference_run_ids=(
            "tidb_query_perf_statistics_drift_frozen_history_smoke_r10_20260817__"
            "tidb_query_perf_statistics_drift_frozen_history__statistics_drift_history_investigation__mock__r001",
        ),
    ),
    db=DB,
    table=TARGET_TABLES[0],
    partner_table=TARGET_TABLES[1],
    control_table=CONTROL_TABLES[0],
    control_partner_table=CONTROL_TABLES[1],
    noise_table=NOISE_TABLES[0],
    noise_partner_table=NOISE_TABLES[1],
    index_name=INDEX_NAME,
    status_index_name=STATUS_INDEX_NAME,
    target_column="routing_key",
    target_value=TARGET_VALUE,
    status_column="status",
    status_value=STATUS_VALUE,
    control_query=CONTROL_QUERY,
    initial_rows=2000,
    initial_target_rows=100,
    skew_rows=30000,
    control_rows=2000,
    control_target_rows=100,
    noise_skew_rows=6000,
    shift_target_rows=3000,
    shift_status_rows=3000,
    minimum_estimate_actual_ratio=1.5,
    business_query=BUSINESS_QUERY,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "localized_history_window",
                    "entity": "statistics_drift_history_investigation",
                    "evidence": ["target fingerprint worsens while cluster-wide control remains stable"],
                },
                {
                    "type": "finding",
                    "factor": "distribution_shift_after_analyze",
                    "entity": "statistics_drift_history_investigation",
                    "evidence": ["target physical rows and modify count move after the prior analyze"],
                },
                {
                    "type": "finding",
                    "factor": "cardinality_plan_drift",
                    "entity": "statistics_drift_history_investigation",
                    "evidence": ["target estimate/actual and scanned rows diverge after the distribution change"],
                },
                {
                    "type": "finding",
                    "factor": "affected_index_merge_session",
                    "entity": "statistics_drift_history_investigation",
                    "evidence": ["the affected session has tidb_enable_index_merge=OFF"],
                },
                {
                    "type": "finding",
                    "factor": "benign_windows_excluded",
                    "entity": "statistics_drift_history_investigation",
                    "evidence": ["control/noise and maintenance windows do not explain both target branches"],
                },
                {
                    "type": "finding",
                    "factor": "causal_order",
                    "entity": "statistics_drift_history_investigation",
                    "evidence": ["distribution and cardinality drift precede plan, scan and latency degradation"],
                },
            ]
        },
        "outcome": {
            "changes": ["refresh target statistics and enable IndexMerge in the affected session"],
            "verification": ["recheck current plan, ratios, business truth and six-table integrity"],
        },
        "summary": "The structured reference path reconstructs the historical statistics-drift chain and repairs only the affected scope.",
    },
)

_PARTITION_WORKLOAD = replace(
    _BACKGROUND_WORKLOAD,
    profiles=tuple(
        replace(profile, qps=profile.qps * 0.75)
        for profile in _BACKGROUND_WORKLOAD.profiles
        if profile.name != "mf_qp04_history_probe_noise"
    ),
    worker_count=4,
    seed=20260902,
)
_PARTITION_CASE = replace(
    _CASE,
    case_id="statistics_drift_partition_history_investigation",
    case_no=1,
    evaluator=TidbQueryPerfStatisticsDriftFrozenHistoryPartitionEvaluatorCase,
    title="Investigate a two-partition statistics drift with a healthy paired aggregate.",
    background_workload=_PARTITION_WORKLOAD,
    frozen_history=replace(
        _CASE.frozen_history,
        duration_seconds=7_200,
        normal_capture_seconds=60,
        fault_capture_seconds=120,
        block_min_seconds=20,
        block_max_seconds=40,
        overview_step_seconds=60,
        target_age_seconds_range=(900, 2_700),
        decoys=tuple(
            replace(decoy, duration_seconds=30)
            for decoy in _CASE.frozen_history.decoys[:2]
            if decoy.decoy_id != "benign-compaction"
        ),
        install_before_normal_capture=True,
    ),
    runtime=replace(_CASE.runtime, image_group_key="qp04-frozen-history-statistics-partition"),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.473684,
        reference_run_ids=('reference-216__tidb_query_perf_statistics_drift_frozen_history__statistics_drift_history_investigation__mock__r001',),
        protocol_version='difficulty-v2',
    ),
    skew_rows=9_000,
    noise_skew_rows=1_500,
    shift_target_rows=900,
    shift_status_rows=900,
)


class TidbQueryPerfStatisticsDriftFrozenHistoryScenario(TiDBScenario):
    scenario_id = "tidb_query_perf_statistics_drift_frozen_history"
    description = "Frozen frozen-history history exposes a distribution shift, stale statistics, plan drift, and an affected-session IndexMerge toggle."
    cases = (_CASE, _PARTITION_CASE)

    def build_fault_plan(self, case: TidbQueryPerfStatisticsDriftFrozenHistoryForHistoryInvestigationScenarioCase) -> tuple[FaultPlan, ...]:
        for value, name in (
            (case.db, "database"),
            (case.table, "target table"),
            (case.partner_table, "target partner table"),
            (case.control_table, "control table"),
            (case.control_partner_table, "control partner table"),
            (case.noise_table, "noise table"),
            (case.noise_partner_table, "noise partner table"),
        ):
            validate_sql_identifier(value, name)
        return (
            FaultPlan(
                injector_type=TidbQueryPerfStatisticsDriftFrozenHistoryInjector,
                config={
                    "db": case.db,
                    "table": case.table,
                    "partner_table": case.partner_table,
                    "control_table": case.control_table,
                    "control_partner_table": case.control_partner_table,
                    "noise_table": case.noise_table,
                    "noise_partner_table": case.noise_partner_table,
                    "index_name": case.index_name,
                    "status_index_name": case.status_index_name,
                    "target_column": case.target_column,
                    "target_value": case.target_value,
                    "status_column": case.status_column,
                    "status_value": case.status_value,
                    "control_rows": case.control_rows,
                    "control_target_rows": case.control_target_rows,
                    "noise_skew_rows": case.noise_skew_rows,
                    "shift_target_rows": case.shift_target_rows,
                    "shift_status_rows": case.shift_status_rows,
                    "initial_rows": case.initial_rows,
                    "initial_target_rows": case.initial_target_rows,
                    "skew_rows": case.skew_rows,
                    "minimum_estimate_actual_ratio": case.minimum_estimate_actual_ratio,
                    "business_query": case.business_query,
                    "control_query": case.control_query,
                    "benign_compaction_table": BENIGN_COMPACTION_TABLE,
                    "benign_compaction_buffer_rows": BENIGN_COMPACTION_ROWS,
                },
            ),
        )


__all__ = (
    "TidbQueryPerfStatisticsDriftFrozenHistoryForHistoryInvestigationScenarioCase",
    "TidbQueryPerfStatisticsDriftFrozenHistoryInjector",
    "TidbQueryPerfStatisticsDriftFrozenHistoryScenario",
)
