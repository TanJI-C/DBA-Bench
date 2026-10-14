import math

from collections.abc import Mapping

from src.database.query_results import capture_query_result_truth

from src.database.sql import parse_json_object, require_success_payload

from src.database.sql import sequence_row_source
from src.scenarios.tidb.common import BaseFaultInjector, FaultLifecycleContext, validate_sql_identifier

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.query_perf.statistics_drift import (
    TidbQueryPerfStatisticsDriftForDistributionShiftEvaluatorCase,
    TidbQueryPerfStatisticsDriftReducedEvaluatorCase,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfStatisticsDriftForDistributionShiftScenarioCase(TiDBScenarioCase):
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


_BUSINESS_QUERY = (
    "SELECT COUNT(*) AS matched_rows, "
    "CAST(SUM(amount) AS DECIMAL(18,2)) AS total_amount "
    "FROM ("
    "SELECT id, routing_key, status, amount FROM test.qp04_order_events "
    "UNION ALL "
    "SELECT id, routing_key, status, amount FROM test.qp04_order_event_ledger"
    ") AS order_shards WHERE routing_key='r17' OR status='pending'"
)

_CONTROL_QUERY = (
    "SELECT COUNT(*) AS matched_rows, "
    "CAST(SUM(amount) AS DECIMAL(18,2)) AS total_amount "
    "FROM ("
    "SELECT id, routing_key, status, amount FROM test.qp04_order_events_control "
    "UNION ALL "
    "SELECT id, routing_key, status, amount FROM test.qp04_order_event_ledger_control"
    ") AS control_shards WHERE routing_key='r17' OR status='pending'"
)

_NOISE_QUERY = (
    "SELECT COUNT(*) AS matched_rows, "
    "CAST(SUM(amount) AS DECIMAL(18,2)) AS total_amount "
    "FROM ("
    "SELECT id, routing_key, status, amount FROM test.qp04_order_events_noise "
    "UNION ALL "
    "SELECT id, routing_key, status, amount FROM test.qp04_order_event_ledger_noise"
    ") AS archive_shards WHERE routing_key='r17' OR status='pending'"
)


_CASE = TidbQueryPerfStatisticsDriftForDistributionShiftScenarioCase(
    case_id="distribution_shift_stale_statistics",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "the regression is isolated to the distributed r17 aggregate over qp04_order_events and qp04_order_event_ledger while both control shards remain healthy, so a cluster-wide TiDB failure is not the cause",
                    "entity": "distribution_shift_stale_statistics",
                    "evidence": [
                        "scripted diagnostic actions observed the regression is isolated to the distributed r17 aggregate over qp04_order_events and qp04_order_event_ledger while both control shards remain healthy, so a cluster-wide TiDB failure is not the cause"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "a large r17 data change happened after the last successful statistics collection on both target shards qp04_order_events and qp04_order_event_ledger",
                    "entity": "distribution_shift_stale_statistics",
                    "evidence": [
                        "scripted diagnostic actions observed a large r17 data change happened after the last successful statistics collection on both target shards qp04_order_events and qp04_order_event_ledger"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "both target shard statistics still estimate roughly 1035 matching OR-predicate rows even though each distributed shard contributes 10000 rows, while both control shard statistics match their actual cardinality",
                    "entity": "distribution_shift_stale_statistics",
                    "evidence": [
                        "scripted diagnostic actions observed both target shard statistics still estimate roughly 1035 matching OR-predicate rows even though each distributed shard contributes 10000 rows, while both control shard statistics match their actual cardinality"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the stale cardinality estimates on both target shards caused the optimizer to choose unsuitable index access paths and scan far more rows than estimated",
                    "entity": "distribution_shift_stale_statistics",
                    "evidence": [
                        "scripted diagnostic actions observed the stale cardinality estimates on both target shards caused the optimizer to choose unsuitable index access paths and scan far more rows than estimated"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "tidb_enable_index_merge is disabled in the affected diagnostic session, so refreshing statistics alone still leaves the distributed OR aggregate on a full table scan",
                    "entity": "distribution_shift_stale_statistics",
                    "evidence": [
                        "scripted diagnostic actions observed tidb_enable_index_merge is disabled in the affected diagnostic session, so refreshing statistics alone still leaves the distributed OR aggregate on a full table scan"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "run ANALYZE TABLE on both affected target shards and enable tidb_enable_index_merge for the diagnostic session"
            ],
            "verification": [
                "both target-shard estimates, IndexMerge plan, comparison estimates, and business result were rechecked"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=TidbQueryPerfStatisticsDriftForDistributionShiftEvaluatorCase,
    title="A distributed order aggregate spans two physical shards whose post-collection distribution shifts leave both sides with stale statistics while control shards remain healthy.",
    alert=(
        "[CRITICAL] [Grafana/TiDB-Query-Detail] 某订单聚合 SQL 指纹的 P95 从 25ms 升到 2.8s，"
        "同一指纹的处理行数明显增加，但其它相似聚合和集群可用性没有同步异常。"
        "请从 SQL 指纹、执行计划、估算/实际行数、统计新鲜度和数据分布中定位真正影响该请求的原因，"
        "排除无关 workload、索引定义和集群级故障，并在不改变业务结果的前提下恢复性能。"
    ),
    initial_state={
        "status": "degraded",
        "symptom": "one_query_fingerprint_regressed",
        "control_workload": "healthy",
    },
    expected_target={
        "status": "recovered",
        "estimated_rows": 20000,
        "estimate_actual_ratio_at_most": 2.0,
        "business_result_consistent": True,
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="qp04_target_order_report",
                sql=_BUSINESS_QUERY,
                qps=0.8,
                tier="OLAP_BURST",
            ),
            WorkloadProfile(
                name="qp04_control_order_report",
                sql=_CONTROL_QUERY,
                qps=0.8,
                tier="OLAP_BURST",
            ),
            WorkloadProfile(
                name="qp04_statistics_inventory",
                sql=(
                    "SHOW STATS_META WHERE Db_name='test' "
                    "AND Table_name LIKE 'qp04_order_event%'"
                ),
                qps=0.4,
                tier="DDL_MAINTENANCE_OBSERVABILITY",
            ),
            WorkloadProfile(
                name="qp04_control_point_read",
                sql=(
                    "SELECT id, amount FROM test.qp04_order_events_control "
                    "WHERE routing_key='r17' ORDER BY id LIMIT 20"
                ),
                qps=1.0,
                tier="OLTP_CORE",
            ),
            WorkloadProfile(
                name="qp04_noise_archive_report",
                sql=(
                    _NOISE_QUERY,
                ),
                qps=0.15,
                tier="OLAP_BURST",
            ),
        ),
        worker_count=4,
        seed=20260731,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=5,
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=300,
        image_group_key="qp04-statistics-drift",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.8125,
        reference_run_ids=("reference-272__tidb_query_perf_statistics_drift",),
    ),
    db="test",
    table="qp04_order_events",
    partner_table="qp04_order_event_ledger",
    control_table="qp04_order_events_control",
    control_partner_table="qp04_order_event_ledger_control",
    noise_table="qp04_order_events_noise",
    noise_partner_table="qp04_order_event_ledger_noise",
    index_name="idx_routing_key",
    status_index_name="idx_status",
    target_column="routing_key",
    target_value="r17",
    status_column="status",
    status_value="pending",
    control_query=_CONTROL_QUERY,
    initial_rows=1000,
    initial_target_rows=10,
    skew_rows=49990,
    control_rows=1000,
    control_target_rows=10,
    noise_skew_rows=4000,
    shift_target_rows=4990,
    shift_status_rows=4990,
    minimum_estimate_actual_ratio=5.0,
    business_query=_BUSINESS_QUERY,
)

_CASE_REDUCED = replace(
    _CASE,
    case_id="distribution_shift_stale_statistics_simple",
    case_no=1,
    evaluator=TidbQueryPerfStatisticsDriftReducedEvaluatorCase,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": (
                        "the regression is isolated to the distributed r17 aggregate over qp04_order_events and "
                        "qp04_order_event_ledger while both control shards remain healthy, so a cluster-wide TiDB "
                        "failure is not the cause"
                    ),
                    "entity": "distribution_shift_stale_statistics_simple",
                    "evidence": [
                        (
                            "a large r17 data change happened after the last successful statistics collection on "
                            "both target shards qp04_order_events and qp04_order_event_ledger"
                        ),
                        (
                            "both target shard statistics still estimate roughly 1035 matching OR-predicate rows "
                            "even though each distributed shard contributes 10000 rows, while both control shard "
                            "statistics match their actual cardinality"
                        ),
                    ],
                },
                {
                    "type": "root_cause",
                    "factor": (
                        "the stale cardinality estimates on both target shards caused the optimizer to choose "
                        "unsuitable index access paths and scan far more rows than estimated"
                    ),
                    "entity": "distribution_shift_stale_statistics_simple",
                    "evidence": [
                        (
                            "tidb_enable_index_merge is disabled in the affected diagnostic session, so refreshing "
                            "statistics alone still leaves the distributed OR aggregate on a full table scan"
                        ),
                    ],
                },
            ]
        },
        "outcome": {
            "changes": [
                "run ANALYZE TABLE on both affected target shards and enable tidb_enable_index_merge for the diagnostic session"
            ],
            "verification": [
                "both target-shard estimates, IndexMerge plan, comparison estimates, and business result were rechecked"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification.",
    },
    title=(
        "A distributed order aggregate spans two physical shards whose post-collection "
        "distribution shifts leave both sides with stale statistics while control shards remain healthy."
    ),
    alert=(
        "[CRITICAL] [Grafana/TiDB-Query-Detail] 某订单聚合 SQL 指纹的 P95 从 25ms 升到 2.8s，"
        "同一指纹的处理行数明显增加，但其它相似聚合和集群可用性没有同步异常。"
        "请从 SQL 指纹、执行计划、估算/实际行数、统计新鲜度和数据分布中定位真正影响该请求的原因，"
        "排除无关 workload、索引定义和集群级故障，并在不改变业务结果的前提下恢复性能。"
    ),
    noise_skew_rows=2_000,
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.506884,
        reference_run_ids=(
            "tidb-reference-4__tidb_query_perf_statistics_drift__"
            "distribution_shift_stale_statistics_simple__mock__r001",
        ),
    ),
)


class TidbQueryPerfStatisticsDriftInjector(BaseFaultInjector):
    """Create a two-shard stale-statistics workload beside control and noise shards."""

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._capture_owned_state(context.env)
        self._disable_auto_analyze(context.env)
        for table in self.target_tables:
            self._create_table(context.env, table)
            self._load_rows(
                context.env,
                table,
                self.initial_rows,
                self.initial_target_rows,
                0,
                "baseline",
            )
            self._collect_statistics(context.env, table)
        for table in self.target_tables:
            self._load_distribution_shift(context.env, table, self.skew_rows)
        for table in self.control_tables:
            self._create_table(context.env, table)
            self._load_rows(
                context.env,
                table,
                self.control_rows,
                self.control_target_rows,
                0,
                "control",
            )
            self._collect_statistics(context.env, table)
        for table in self.noise_tables:
            self._create_table(context.env, table)
            self._load_rows(
                context.env,
                table,
                self.initial_rows,
                self.initial_target_rows,
                0,
                "noise-baseline",
            )
            self._collect_statistics(context.env, table)
        for table in self.noise_tables:
            self._load_distribution_shift(context.env, table, self.noise_skew_rows)
        self._verify_fault_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._disable_auto_analyze(context.env)
        self._verify_fault_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._verify_fault_state(context.env)
        fault_stats = self._stats_meta_for_tables(context.env, self.target_tables)
        control_stats = self._stats_meta_for_tables(context.env, self.control_tables)
        noise_stats = self._stats_meta_for_tables(context.env, self.noise_tables)
        fault_plan = self._payload(
            context.env,
            f"EXPLAIN {self.business_query}",
            "capture QP04 target plan",
        )
        fault_plan_analyze = self._payload(
            context.env,
            f"EXPLAIN ANALYZE {self.business_query}",
            "capture QP04 target estimate and actual rows",
        )
        control_plan_analyze = self._payload(
            context.env,
            f"EXPLAIN ANALYZE {self.control_query}",
            "capture QP04 control estimate and actual rows",
        )
        noise_plan_analyze = self._payload(
            context.env,
            f"EXPLAIN ANALYZE {self._noise_query()}",
            "capture QP04 noise estimate and actual rows",
        )
        business_result = self._payload(
            context.env,
            self.business_query,
            "capture QP04 target business result truth",
        )
        control_result = self._payload(
            context.env,
            self.control_query,
            "capture QP04 control business result",
        )
        topsql = parse_json_object(
            context.env.observe_metric("topsql", None),
            "capture QP04 TopSQL evidence",
        )
        query_latency = parse_json_object(
            context.env.query_metrics("query_latency", None),
            "capture QP04 query-latency evidence",
        )
        self._assert_fault_statistics(fault_stats)
        self._assert_control_statistics(control_stats)
        fault_scan = self._assert_fault_plan(fault_plan_analyze)
        return {
            "original_auto_analyze_state": {
                "ratio": self.original_auto_analyze_ratio,
                "start_time": self.original_auto_analyze_start_time,
                "end_time": self.original_auto_analyze_end_time,
            },
            "original_index_merge": self.original_index_merge,
            "fault_stats_meta": fault_stats,
            "control_stats_meta": control_stats,
            "noise_stats_meta": noise_stats,
            "fault_plan": fault_plan,
            "fault_plan_analyze": fault_plan_analyze,
            "control_plan_analyze": control_plan_analyze,
            "noise_plan_analyze": noise_plan_analyze,
            "fault_scan": fault_scan,
            "business_result_truth": capture_query_result_truth(
                business_result,
                ordered=True,
            ),
            "control_result_truth": capture_query_result_truth(
                control_result,
                ordered=True,
            ),
            "topsql": topsql,
            "query_latency": query_latency,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._assert_auto_analyze_disabled(context.env)
        self._verify_fault_state(context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        for table in self.all_tables:
            self._require_success(
                context.env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{table}"),
                f"drop QP04 table {self.db}.{table}",
            )
        self._require_success(
            context.env.execute_sql(
                f"SET GLOBAL tidb_auto_analyze_ratio={self.original_auto_analyze_ratio}"
            ),
            "restore QP04 auto-analyze ratio",
        )
        self._require_success(
            context.env.execute_sql(
                "SET GLOBAL tidb_auto_analyze_start_time="
                f"'{self.original_auto_analyze_start_time}'"
            ),
            "restore QP04 auto-analyze start time",
        )
        self._require_success(
            context.env.execute_sql(
                "SET GLOBAL tidb_auto_analyze_end_time="
                f"'{self.original_auto_analyze_end_time}'"
            ),
            "restore QP04 auto-analyze end time",
        )
        self._require_success(
            context.env.execute_sql(
                f"SET SESSION tidb_enable_index_merge={self.original_index_merge}"
            ),
            "restore QP04 index merge session state",
        )
        self._assert_owned_state_restored(context.env)

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.partner_table = validate_sql_identifier(
            str(config["partner_table"]), "partner table"
        )
        self.control_table = validate_sql_identifier(
            str(config["control_table"]), "control table"
        )
        self.control_partner_table = validate_sql_identifier(
            str(config["control_partner_table"]), "control partner table"
        )
        self.noise_table = validate_sql_identifier(str(config["noise_table"]), "noise table")
        self.noise_partner_table = validate_sql_identifier(
            str(config["noise_partner_table"]), "noise partner table"
        )
        self.index_name = validate_sql_identifier(str(config["index_name"]), "index")
        self.status_index_name = validate_sql_identifier(
            str(config["status_index_name"]), "status index"
        )
        self.target_column = validate_sql_identifier(
            str(config["target_column"]), "target column"
        )
        self.target_value = str(config["target_value"])
        self.status_column = validate_sql_identifier(
            str(config["status_column"]), "status column"
        )
        self.status_value = str(config["status_value"])
        self.initial_rows = int(config["initial_rows"])
        self.initial_target_rows = int(config["initial_target_rows"])
        self.skew_rows = int(config["skew_rows"])
        self.control_rows = int(config["control_rows"])
        self.control_target_rows = int(config["control_target_rows"])
        self.noise_skew_rows = int(config["noise_skew_rows"])
        self.shift_target_rows = int(config["shift_target_rows"])
        self.shift_status_rows = int(config["shift_status_rows"])
        self.minimum_estimate_actual_ratio = float(config["minimum_estimate_actual_ratio"])
        self.business_query = str(config["business_query"])
        self.control_query = str(config["control_query"])
        self.target_tables = (self.table, self.partner_table)
        self.control_tables = (self.control_table, self.control_partner_table)
        self.noise_tables = (self.noise_table, self.noise_partner_table)
        self.all_tables = self.target_tables + self.control_tables + self.noise_tables

    def _payload(self, env, sql: str, description: str) -> dict:
        return require_success_payload(env.execute_sql(sql), f"{description}: sql={sql!r}")

    def _require_success(self, raw, description: str) -> dict:
        return require_success_payload(raw, description)

    def _capture_owned_state(self, env) -> None:
        payload = self._payload(
            env,
            "SELECT @@GLOBAL.tidb_auto_analyze_ratio, "
            "@@GLOBAL.tidb_auto_analyze_start_time, "
            "@@GLOBAL.tidb_auto_analyze_end_time",
            "capture QP04 auto-analyze state",
        )
        row = payload["result"][0]
        self.original_auto_analyze_ratio = str(row[0])
        self.original_auto_analyze_start_time = str(row[1])
        self.original_auto_analyze_end_time = str(row[2])
        self.original_index_merge = str(
            self._payload(
                env,
                "SHOW VARIABLES LIKE 'tidb_enable_index_merge'",
                "capture QP04 index merge session state",
            )["result"][0][1]
        )

    def _disable_auto_analyze(self, env) -> None:
        self._require_success(
            env.execute_sql("SET GLOBAL tidb_auto_analyze_ratio=0.000010"),
            "disable QP04 auto-analyze",
        )
        window = self._payload(
            env,
            "SELECT DATE_FORMAT(DATE_SUB(UTC_TIMESTAMP(), INTERVAL 30 MINUTE), '%H:%i +0000'), "
            "DATE_FORMAT(DATE_SUB(UTC_TIMESTAMP(), INTERVAL 29 MINUTE), '%H:%i +0000')",
            "choose QP04 closed auto-analyze window",
        )["result"][0]
        self.disabled_auto_analyze_start_time = str(window[0])
        self.disabled_auto_analyze_end_time = str(window[1])
        self._require_success(
            env.execute_sql(
                "SET GLOBAL tidb_auto_analyze_start_time="
                f"'{self.disabled_auto_analyze_start_time}'"
            ),
            "close QP04 auto-analyze start time",
        )
        self._require_success(
            env.execute_sql(
                "SET GLOBAL tidb_auto_analyze_end_time="
                f"'{self.disabled_auto_analyze_end_time}'"
            ),
            "close QP04 auto-analyze end time",
        )
        self._assert_auto_analyze_disabled(env)
        self._require_success(
            env.execute_sql("SET SESSION tidb_enable_index_merge=OFF"),
            "disable QP04 index merge for the fault session",
        )

    def _assert_auto_analyze_disabled(self, env) -> None:
        payload = self._payload(
            env,
            "SELECT @@GLOBAL.tidb_auto_analyze_ratio, "
            "@@GLOBAL.tidb_auto_analyze_start_time, "
            "@@GLOBAL.tidb_auto_analyze_end_time",
            "verify QP04 auto-analyze is disabled",
        )
        observed = [str(value) for value in payload["result"][0]]
        expected = [
            "0.000010",
            self.disabled_auto_analyze_start_time,
            self.disabled_auto_analyze_end_time,
        ]
        if float(observed[0]) != 0.000010 or observed[1:] != expected[1:]:
            raise RuntimeError(
                "QP04 requires auto-analyze to stay outside its active window: "
                f"expected={expected!r}, observed={observed!r}"
            )

    def _assert_index_merge_disabled(self, env) -> None:
        payload = self._payload(
            env,
            "SHOW VARIABLES LIKE 'tidb_enable_index_merge'",
            "verify QP04 index merge is disabled",
        )
        observed = str(payload["result"][0][1]).casefold()
        if observed not in {"off", "0"}:
            raise RuntimeError(
                "QP04 requires index merge to remain disabled until the agent repairs the session: "
                f"observed={payload['result']!r}"
            )

    def _create_table(self, env, table: str) -> None:
        self._require_success(
            env.execute_sql(f"CREATE DATABASE IF NOT EXISTS {self.db}"),
            f"create QP04 database {self.db}",
        )
        self._require_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{table}"),
            f"clear QP04 table {self.db}.{table}",
        )
        self._require_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{table} ("
                "id BIGINT NOT NULL PRIMARY KEY, "
                "routing_key VARCHAR(16) NOT NULL, "
                "status VARCHAR(16) NOT NULL, "
                "amount DECIMAL(12,2) NOT NULL, "
                "payload VARCHAR(64) NOT NULL, "
                f"KEY {self.index_name} (routing_key), "
                f"KEY {self.status_index_name} (status))"
            ),
            f"create QP04 table {self.db}.{table}",
        )

    def _load_rows(
        self,
        env,
        table: str,
        rows: int,
        target_rows: int,
        id_offset: int,
        payload_prefix: str,
    ) -> None:
        inserted = 0
        while inserted < rows:
            batch_size = min(1000, rows - inserted)
            start = id_offset + inserted
            self._require_success(
                env.execute_sql(
                    f"INSERT INTO {self.db}.{table} "
                    "(id, routing_key, status, amount, payload) "
                    f"SELECT {start}+n, IF({inserted}+n <= {target_rows}, '{self.target_value}', 'r03'), "
                    f"IF({inserted}+n <= {target_rows}, 'closed', "
                    f"IF({inserted}+n <= {target_rows * 2}, '{self.status_value}', 'closed')), "
                    f"CAST({start}+n AS DECIMAL(12,2)), CONCAT('{payload_prefix}-', {start}+n) "
                    f"FROM ({sequence_row_source(batch_size)}) source"
                ),
                f"load QP04 {table} batch offset={inserted}",
            )
            inserted += batch_size

    def _collect_statistics(self, env, table: str) -> None:
        self._require_success(
            env.execute_sql(f"ANALYZE TABLE {self.db}.{table}"),
            f"collect QP04 baseline statistics for {self.db}.{table}",
        )
        # TiDB publishes SHOW STATS_META asynchronously after ANALYZE completes.
        # Ensure the frozen-history sampler never observes a missing baseline row.
        for _ in range(12):
            payload = self._payload(
                env,
                f"SHOW STATS_META WHERE Db_name='{self.db}' AND Table_name='{table}'",
                f"verify QP04 baseline statistics for {self.db}.{table}",
            )
            rows = payload.get("result")
            columns = [str(column).casefold() for column in payload["columns"]]
            analyze_index = columns.index("last_analyze_time")
            if rows and isinstance(rows, list) and rows[0][analyze_index] is not None:
                return
            import time
            time.sleep(1)
        raise RuntimeError(
            f"QP04 baseline statistics were not published: database={self.db!r}, table={table!r}"
        )

    def _load_distribution_shift(self, env, table: str, skew_rows: int) -> None:
        start = self.initial_rows
        self._require_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{table} "
                "(id, routing_key, status, amount, payload) "
                f"SELECT {start}+n, "
                f"IF(n <= {self.shift_target_rows}, '{self.target_value}', 'r03'), "
                f"IF(n <= {self.shift_target_rows}, 'closed', "
                f"IF(n <= {self.shift_target_rows + self.shift_status_rows}, '{self.status_value}', 'closed')), "
                f"1.00, CONCAT('distribution-shift-', {start}+n) "
                f"FROM ({sequence_row_source(skew_rows)}) source"
            ),
            f"load QP04 post-ANALYZE shift table={table} rows={skew_rows}",
        )

    def _noise_query(self) -> str:
        return (
            "SELECT COUNT(*) AS matched_rows, "
            "CAST(SUM(amount) AS DECIMAL(18,2)) AS total_amount "
            "FROM ("
            f"SELECT id, {self.target_column}, {self.status_column}, amount FROM {self.db}.{self.noise_table} "
            "UNION ALL "
            f"SELECT id, {self.target_column}, {self.status_column}, amount FROM {self.db}.{self.noise_partner_table}"
            f") AS archive_shards WHERE {self.target_column}='{self.target_value}' "
            f"OR {self.status_column}='{self.status_value}'"
        )

    def _stats_meta(self, env, table: str) -> dict:
        return self._payload(
            env,
            f"SHOW STATS_META WHERE Db_name='{self.db}' AND Table_name='{table}'",
            f"inspect QP04 statistics metadata for {table}",
        )

    def _stats_meta_for_tables(self, env, tables: tuple[str, ...]) -> dict[str, dict]:
        return {table: self._stats_meta(env, table) for table in tables}

    def _stats_row(self, payload: dict, table: str) -> dict:
        columns = [str(column).casefold() for column in payload["columns"]]
        rows = [dict(zip(columns, row)) for row in payload["result"]]
        matches = [row for row in rows if str(row.get("table_name")) == table]
        if len(matches) != 1:
            raise RuntimeError(
                "QP04 expected one table statistics row: "
                f"table={table!r}, rows={rows!r}"
            )
        return matches[0]

    def _assert_fault_statistics(self, payloads: dict[str, dict]) -> None:
        for table in self.target_tables:
            row = self._stats_row(payloads[table], table)
            if not str(row["last_analyze_time"]).strip():
                raise RuntimeError(
                    "QP04 target shard stats-meta has no analyze timestamp: "
                    f"table={table!r}, stats={row!r}"
                )

    def _assert_control_statistics(self, payloads: dict[str, dict]) -> None:
        for table in self.control_tables:
            row = self._stats_row(payloads[table], table)
            if not str(row["last_analyze_time"]).strip():
                raise RuntimeError(
                    "QP04 control shard stats-meta has no analyze timestamp: "
                    f"table={table!r}, stats={row!r}"
                )

    def _plan_scan_candidates(self, payload: dict) -> list[tuple[float, float, list]]:
        columns = [str(column).casefold() for column in payload["columns"]]
        est_index = columns.index("estrows")
        act_index = columns.index("actrows")
        candidates = []
        for row in payload["result"]:
            operator = str(row[0]).casefold()
            if not any(
                name in operator
                for name in ("selection", "tablefullscan", "indexlookup", "indexrangescan")
            ):
                continue
            estimate = float(row[est_index])
            actual = float(row[act_index])
            if actual > 0:
                candidates.append((estimate, actual, row))
        return candidates

    def _target_table_scans(self, payload: dict) -> dict[str, tuple[float, list]]:
        scans = {}
        for row in payload["result"]:
            if "tablefullscan" not in str(row[0]).casefold():
                continue
            rendered = " ".join(str(value) for value in row).casefold()
            matches = [
                table
                for table in self.target_tables
                if f"table:{table.casefold()}" in rendered
            ]
            if len(matches) != 1:
                raise RuntimeError(
                    "QP04 target TableFullScan row is not attributable to one target shard: "
                    f"target_tables={self.target_tables!r}, row={row!r}"
                )
            if matches[0] in scans:
                raise RuntimeError(
                    "QP04 plan exposes duplicate TableFullScan rows for one target shard: "
                    f"table={matches[0]!r}, row={row!r}"
                )
            columns = [str(column).casefold() for column in payload["columns"]]
            actual = float(row[columns.index("actrows")])
            scans[matches[0]] = (actual, row)
        if set(scans) != set(self.target_tables):
            raise RuntimeError(
                "QP04 target plan must expose one TableFullScan for every target shard: "
                f"expected={self.target_tables!r}, observed={scans!r}, plan={payload['result']!r}"
            )
        return scans

    def _assert_fault_plan(self, payload: dict) -> dict:
        candidates = self._plan_scan_candidates(payload)
        severe = []
        for estimate, actual, row in candidates:
            ratio = actual / estimate if estimate > 0 else math.inf
            if ratio >= self.minimum_estimate_actual_ratio:
                severe.append((estimate, actual, row, ratio))
        if len(candidates) < len(self.target_tables) or len(severe) < len(self.target_tables):
            raise RuntimeError(
                "QP04 fault plan must expose stale scans for every target shard: "
                f"index={self.index_name!r}, target_shards={self.target_tables!r}, "
                f"candidates={candidates!r}, severe={severe!r}, plan={payload['result']!r}"
            )
        scans = self._target_table_scans(payload)
        expected_actual = self.initial_rows + self.skew_rows
        insufficient = {
            table: actual
            for table, (actual, _row) in scans.items()
            if int(actual) < expected_actual
        }
        if insufficient:
            raise RuntimeError(
                "QP04 target TableFullScan does not cover a complete shifted shard: "
                f"minimum_expected={expected_actual}, observed={insufficient!r}, plan={payload['result']!r}"
            )
        estimate, actual, row, ratio = severe[0]
        return {
            "operator": str(row[0]),
            "index": self.index_name,
            "estimate": estimate,
            "actual": actual,
            "scan_coverage": {
                table: actual for table, (actual, _row) in scans.items()
            },
            "ratio": ratio,
            "severe_shards": [
                {
                    "operator": str(item[2][0]),
                    "estimate": item[0],
                    "actual": item[1],
                    "ratio": item[3],
                }
                for item in severe
            ],
        }

    def _verify_fault_state(self, env) -> None:
        expected_actual = self.initial_rows + self.skew_rows
        for table in self.target_tables:
            target_count = self._payload(
                env,
                f"SELECT COUNT(*) FROM {self.db}.{table}",
                f"verify QP04 target shard row count table={table}",
            )
            observed_actual = int(target_count["result"][0][0])
            if observed_actual != expected_actual:
                raise RuntimeError(
                    "QP04 target shard row count mismatch: "
                    f"table={table!r}, expected={expected_actual}, observed={observed_actual}"
                )
        for table in self.control_tables:
            control_count = self._payload(
                env,
                f"SELECT COUNT(*) FROM {self.db}.{table}",
                f"verify QP04 control shard row count table={table}",
            )
            observed_control = int(control_count["result"][0][0])
            if observed_control != self.control_rows:
                raise RuntimeError(
                    "QP04 control shard row count mismatch: "
                    f"table={table!r}, expected={self.control_rows}, observed={observed_control}"
                )
        fault_stats = self._stats_meta_for_tables(env, self.target_tables)
        control_stats = self._stats_meta_for_tables(env, self.control_tables)
        noise_stats = self._stats_meta_for_tables(env, self.noise_tables)
        self._assert_fault_statistics(fault_stats)
        self._assert_control_statistics(control_stats)
        expected_noise_rows = self.initial_rows + self.noise_skew_rows
        for table in self.noise_tables:
            noise_row = self._stats_row(noise_stats[table], table)
            if not str(noise_row["last_analyze_time"]).strip():
                raise RuntimeError(
                    "QP04 noise shard stats-meta has no analyze timestamp: "
                    f"table={table!r}, stats={noise_row!r}, expected_physical_rows={expected_noise_rows}"
                )
            noise_count = self._payload(
                env,
                f"SELECT COUNT(*) FROM {self.db}.{table}",
                f"verify QP04 noise row count table={table}",
            )
            if int(noise_count["result"][0][0]) != self.initial_rows + self.noise_skew_rows:
                raise RuntimeError(
                    "QP04 noise row count mismatch: "
                    f"table={table!r}, expected={self.initial_rows + self.noise_skew_rows}, "
                    f"observed={noise_count['result'][0][0]}"
                )
        plan = self._payload(
            env,
            f"EXPLAIN ANALYZE {self.business_query}",
            "verify QP04 stale estimate and actual rows",
        )
        self._assert_fault_plan(plan)
        self._assert_auto_analyze_disabled(env)
        self._assert_index_merge_disabled(env)

    def _assert_owned_state_restored(self, env) -> None:
        payload = self._payload(
            env,
            "SELECT @@GLOBAL.tidb_auto_analyze_ratio, "
            "@@GLOBAL.tidb_auto_analyze_start_time, "
            "@@GLOBAL.tidb_auto_analyze_end_time",
            "verify QP04 auto-analyze restoration",
        )
        observed = [str(value) for value in payload["result"][0]]
        expected = [
            self.original_auto_analyze_ratio,
            self.original_auto_analyze_start_time,
            self.original_auto_analyze_end_time,
        ]
        if [float(observed[0]), *observed[1:]] != [float(expected[0]), *expected[1:]]:
            raise RuntimeError(
                "QP04 auto-analyze state was not restored: "
                f"expected={expected!r}, observed={observed!r}"
            )


class TidbQueryPerfStatisticsDriftScenario(TiDBScenario):
    scenario_id = "tidb_query_perf_statistics_drift"
    description = "Deterministic data skew leaves stale TiDB statistics and causes query-plan drift."
    cases = (_CASE, _CASE_REDUCED)

    def build_fault_plan(
        self,
        case: TidbQueryPerfStatisticsDriftForDistributionShiftScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbQueryPerfStatisticsDriftInjector,
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
                },
            ),
        )
