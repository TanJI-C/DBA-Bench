from collections.abc import Mapping

from src.database.query_results import capture_query_result_truth

from src.database.sql import parse_json_object, require_success_payload

from src.scenarios.tidb.common import BaseFaultInjector, FaultLifecycleContext, validate_sql_identifier

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.query_perf.index_merge_selection_failure import (
    TidbQueryPerfIndexMergeSelectionFailureForDualSingleColumnIndexOrPredicateEvaluatorCase,
    TidbQueryPerfIndexMergeSelectionFailureForSingleWindowOrEvaluatorCase,
)
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfIndexMergeSelectionFailureCase(TiDBScenarioCase):
    db: str
    table: str
    row_count: int
    expected_result_count: int
    expected_result_summary: tuple[int, int, int]
    expected_integrity: tuple[int, int, int]
    fault_fingerprint_sql: str
    business_query: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfIndexMergeSelectionFailureForDualSingleColumnIndexOrPredicateScenarioCase(
    TidbQueryPerfIndexMergeSelectionFailureCase
):
    pass


_QP03_TIME_WINDOW = (
    "event_ts >= '2026-01-01 08:00:00' AND "
    "event_ts < '2026-01-02 00:00:00'"
)
_QP03_TARGET_WHERE = (
    "WHERE ((tenant_id = 7 AND "
    f"{_QP03_TIME_WINDOW}) OR (event_type = 'refund' AND "
    f"{_QP03_TIME_WINDOW}))"
)
_QP03_QUERY = (
    "SELECT DISTINCT event_id FROM ("
    "SELECT event_id FROM test.qp03_admission_events "
    f"{_QP03_TARGET_WHERE}"
    ") AS matched_events "
    "ORDER BY event_id LIMIT 512"
)
_QP03_TARGET_SUMMARY = (
    "SELECT COUNT(*), COALESCE(SUM(event_id), 0), "
    "COALESCE(BIT_XOR(CRC32(CAST(event_id AS CHAR))), 0) "
    f"FROM ({_QP03_QUERY}) AS qp03_target"
)
_QP03_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="qp03_target_fingerprint_summary",
            sql=_QP03_TARGET_SUMMARY,
            qps=0.25,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_tenant_charge_summary",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                f"WHERE ((tenant_id = 42 AND {_QP03_TIME_WINDOW}) "
                f"OR (event_type = 'charge' AND {_QP03_TIME_WINDOW})) "
                "AND amount BETWEEN 0.00 AND 999.99"
            ),
            qps=0.25,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_tenant7_charge_decoy",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                f"WHERE ((tenant_id = 7 AND {_QP03_TIME_WINDOW}) "
                f"OR (event_type = 'charge' AND {_QP03_TIME_WINDOW})) "
                "AND payload LIKE 'event-%'"
            ),
            qps=0.25,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_tenant_create_summary",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                f"WHERE ((tenant_id = 21 AND {_QP03_TIME_WINDOW}) "
                f"OR (event_type = 'create' AND {_QP03_TIME_WINDOW})) "
                "AND payload LIKE 'event-%'"
            ),
            qps=0.25,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_refund_window_probe",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0), MIN(event_ts), MAX(event_ts) "
                "FROM test.qp03_admission_events "
                f"WHERE event_type = 'refund' AND {_QP03_TIME_WINDOW}"
            ),
            qps=0.25,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_tenant7_no_residual_probe",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                f"WHERE tenant_id = 7 AND {_QP03_TIME_WINDOW}"
            ),
            qps=0.25,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_amount_range_probe",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                f"WHERE amount BETWEEN 100.00 AND 200.00 AND {_QP03_TIME_WINDOW}"
            ),
            qps=0.35,
            tier="OLTP_CORE",
            application_name="risk-scoring-worker",
        ),
        WorkloadProfile(
            name="qp03_event_window_probe",
            sql=(
                "SELECT COUNT(*), MIN(event_id), MAX(event_id) "
                "FROM test.qp03_admission_events "
                f"WHERE {_QP03_TIME_WINDOW}"
            ),
            qps=0.35,
            tier="DDL_MAINTENANCE_OBSERVABILITY",
            application_name="event-retention-monitor",
        ),
        WorkloadProfile(
            name="qp03_table_status_probe",
            sql="SHOW TABLE STATUS FROM test LIKE 'qp03_admission_events'",
            qps=0.25,
            tier="DDL_MAINTENANCE_OBSERVABILITY",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="qp03_index_catalog_probe",
            sql="SHOW INDEX FROM test.qp03_admission_events",
            qps=0.35,
            tier="DDL_MAINTENANCE_OBSERVABILITY",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="qp03_optimizer_variable_probe",
            sql="SHOW VARIABLES LIKE 'tidb_enable_%'",
            qps=0.25,
            tier="DDL_MAINTENANCE_OBSERVABILITY",
            application_name="session-inspector",
        ),
        WorkloadProfile(
            name="qp03_missing_search_cache_probe",
            sql="SELECT COUNT(*) FROM test.qp03_event_search_cache_missing",
            qps=0.15,
            tier="LOG_NOISE",
            application_name="search-cache-refresher",
        ),
        WorkloadProfile(
            name="qp03_exact_target_row_probe",
            sql=(
                "SELECT event_id FROM test.qp03_admission_events "
                f"WHERE ((tenant_id = 7 AND {_QP03_TIME_WINDOW}) "
                f"OR (event_type = 'refund' AND {_QP03_TIME_WINDOW})) "
                "ORDER BY event_id LIMIT 500"
            ),
            qps=0.15,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_refund_full_day_decoy",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                "WHERE event_type = 'refund' "
                "AND event_ts >= '2026-01-01 00:00:00' "
                "AND event_ts < '2026-01-03 00:00:00'"
            ),
            qps=0.15,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_tenant7_unbounded_decoy",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                "WHERE tenant_id = 7 AND event_type = 'refund'"
            ),
            qps=0.15,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_shifted_window_decoy",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                "WHERE ((tenant_id = 42 AND event_ts >= '2026-01-02 08:00:00' "
                "AND event_ts < '2026-01-03 00:00:00') "
                "OR (event_type = 'charge' AND event_ts >= '2026-01-02 08:00:00' "
                "AND event_ts < '2026-01-03 00:00:00'))"
            ),
            qps=0.15,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_schema_definition_probe",
            sql="SHOW CREATE TABLE test.qp03_admission_events",
            qps=0.15,
            tier="DDL_MAINTENANCE_OBSERVABILITY",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="qp03_statistics_catalog_probe",
            sql=(
                "SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME, CARDINALITY "
                "FROM information_schema.statistics "
                "WHERE TABLE_SCHEMA = 'test' AND TABLE_NAME = 'qp03_admission_events'"
            ),
            qps=0.15,
            tier="DDL_MAINTENANCE_OBSERVABILITY",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="qp03_missing_index_catalog_probe",
            sql="SHOW INDEX FROM test.qp03_event_search_cache_missing",
            qps=0.10,
            tier="LOG_NOISE",
            application_name="search-cache-refresher",
        ),
        WorkloadProfile(
            name="qp03_missing_search_view_probe",
            sql="SELECT COUNT(*) FROM test.qp03_event_search_view_missing",
            qps=0.10,
            tier="LOG_NOISE",
            application_name="search-cache-refresher",
        ),
        WorkloadProfile(
            name="qp03_target_ordered_fingerprint",
            sql=_QP03_QUERY,
            qps=0.12,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_target_page_450_decoy",
            sql=(
                "SELECT DISTINCT event_id FROM ("
                "SELECT event_id FROM test.qp03_admission_events "
                f"{_QP03_TARGET_WHERE}"
                ") AS matched_events ORDER BY event_id LIMIT 450"
            ),
            qps=0.08,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_target_offset_1_decoy",
            sql=(
                "SELECT DISTINCT event_id FROM ("
                "SELECT event_id FROM test.qp03_admission_events "
                f"{_QP03_TARGET_WHERE}"
                ") AS matched_events ORDER BY event_id LIMIT 512 OFFSET 1"
            ),
            qps=0.08,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_target_desc_order_decoy",
            sql=(
                "SELECT DISTINCT event_id FROM ("
                "SELECT event_id FROM test.qp03_admission_events "
                f"{_QP03_TARGET_WHERE}"
                ") AS matched_events ORDER BY event_id DESC LIMIT 512"
            ),
            qps=0.08,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_target_no_distinct_decoy",
            sql=(
                "SELECT event_id FROM test.qp03_admission_events "
                f"{_QP03_TARGET_WHERE} ORDER BY event_id LIMIT 512"
            ),
            qps=0.08,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_target_timestamp_order_decoy",
            sql=(
                "SELECT event_id FROM test.qp03_admission_events "
                f"{_QP03_TARGET_WHERE} ORDER BY event_ts, event_id LIMIT 512"
            ),
            qps=0.08,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_tenant_branch_ordered_decoy",
            sql=(
                "SELECT DISTINCT event_id FROM test.qp03_admission_events "
                f"WHERE tenant_id = 7 AND {_QP03_TIME_WINDOW} "
                "ORDER BY event_id LIMIT 512"
            ),
            qps=0.08,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_refund_branch_ordered_decoy",
            sql=(
                "SELECT DISTINCT event_id FROM test.qp03_admission_events "
                f"WHERE event_type = 'refund' AND {_QP03_TIME_WINDOW} "
                "ORDER BY event_id LIMIT 512"
            ),
            qps=0.08,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_target_payload_residual_decoy",
            sql=(
                "SELECT DISTINCT event_id FROM ("
                "SELECT event_id FROM test.qp03_admission_events "
                f"{_QP03_TARGET_WHERE} AND payload LIKE 'event-%'"
                ") AS matched_events ORDER BY event_id LIMIT 512"
            ),
            qps=0.08,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_overlap_branch_decoy",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                f"WHERE tenant_id = 7 AND event_type = 'refund' AND {_QP03_TIME_WINDOW}"
            ),
            qps=0.12,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_event_type_set_decoy",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                f"WHERE event_type IN ('refund', 'charge') AND {_QP03_TIME_WINDOW}"
            ),
            qps=0.12,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_tenant_set_decoy",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                f"WHERE tenant_id IN (7, 8) AND {_QP03_TIME_WINDOW}"
            ),
            qps=0.12,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_boundary_window_decoy",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                "WHERE event_type = 'refund' "
                "AND event_ts >= '2026-01-01 00:00:00' "
                "AND event_ts < '2026-01-01 08:00:00'"
            ),
            qps=0.10,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_next_day_window_decoy",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                "WHERE event_type = 'refund' "
                "AND event_ts >= '2026-01-02 08:00:00' "
                "AND event_ts < '2026-01-03 00:00:00'"
            ),
            qps=0.10,
            tier="TARGET_LIKE",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="qp03_event_id_range_decoy",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0) "
                "FROM test.qp03_admission_events "
                "WHERE event_id BETWEEN 32000 AND 68000 "
                f"AND {_QP03_TIME_WINDOW}"
            ),
            qps=0.10,
            tier="OLTP_CORE",
            application_name="event-replay-worker",
        ),
        WorkloadProfile(
            name="qp03_missing_event_rollup_probe",
            sql="SELECT COUNT(*) FROM test.qp03_event_rollup_cache_missing",
            qps=0.10,
            tier="LOG_NOISE",
            application_name="event-replay-worker",
        ),
    ),
    worker_count=6,
    seed=20260731,
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=12,
)

_QP03_REDUCED_PROFILE_NAMES = {
    "qp03_target_fingerprint_summary",
    "qp03_target_ordered_fingerprint",
    "qp03_tenant_charge_summary",
    "qp03_tenant7_charge_decoy",
    "qp03_refund_window_probe",
    "qp03_table_status_probe",
    "qp03_index_catalog_probe",
    "qp03_optimizer_variable_probe",
}

_QP03_REDUCED_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=tuple(
        profile
        for profile in _QP03_BACKGROUND_WORKLOAD.profiles
        if profile.name in _QP03_REDUCED_PROFILE_NAMES
    ),
    worker_count=3,
    seed=20260731,
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=12,
)


_TIDBQUERYPERFINDEXMERGESELECTIONFAILURESCENARIO_CASE = TidbQueryPerfIndexMergeSelectionFailureForDualSingleColumnIndexOrPredicateScenarioCase(
    case_id="dual_single_column_index_or_predicate",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "or predicate uses a full table scan",
                    "entity": "dual_single_column_index_or_predicate",
                    "evidence": [
                        "scripted diagnostic actions observed or predicate uses a full table scan"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "two single column indexes can serve the or predicate",
                    "entity": "dual_single_column_index_or_predicate",
                    "evidence": [
                        "scripted diagnostic actions observed two single column indexes can serve the or predicate"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "tidb enable index merge is off",
                    "entity": "dual_single_column_index_or_predicate",
                    "evidence": [
                        "scripted diagnostic actions observed tidb enable index merge is off"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "enable index merge for this session",
                    "entity": "dual_single_column_index_or_predicate",
                    "evidence": [
                        "scripted diagnostic actions observed enable index merge for this session"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "enabled tidb_enable_index_merge for the current session"
            ],
            "verification": [
                "verified the OR predicate uses IndexMerge again"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=TidbQueryPerfIndexMergeSelectionFailureForDualSingleColumnIndexOrPredicateEvaluatorCase,
    title="Simulates TiDB skipping Index Merge for a time-bounded OR event search while the optimizer setting is disabled.",
    alert=(
        "[CRITICAL] [Grafana/TiDB-Query-Detail] 事件检索接口 P99 延迟从 18ms 上升到 4.6s。"
        "慢 SQL 集中在 test.qp03_admission_events 的带时间窗口 OR 事件检索，目标表 CPU 读放大明显；"
        "同一业务路径还有多个租户/事件类型相似 fingerprint 和统计探针；"
        "请从可观测的 SQL fingerprint 和执行计划中定位退化原因，恢复性能，同时保持结果集和整表真值不变。"
    ),
    initial_state={
        "status": "degraded",
        "plan": "TableFullScan",
        "index_merge": "OFF",
        "global_index_merge": "ON",
        "result_count": 450,
        "result_summary": (450, 25894350, 1153822208),
        "table_truth": (100000, 5000050000, 3676395719),
    },
    expected_target={
        "status": "recovered",
        "plan": "IndexMerge",
        "index_merge": "ON",
        "global_index_merge": "ON",
        "result_count": 450,
        "result_summary": (450, 25894350, 1153822208),
        "table_truth": (100000, 5000050000, 3676395719),
    },
    background_workload=_QP03_BACKGROUND_WORKLOAD,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=180,
        image_group_key="qp03-index-merge-selection-failure",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.793103,
        reference_run_ids=(
            "reference-105__tidb_query_perf_index_merge_selection_failure__dual_single_column_index_or_predicate__mock__r001",
        ),
    ),
    db="test",
    table="qp03_admission_events",
    row_count=100000,
    expected_result_count=450,
    expected_result_summary=(450, 25894350, 1153822208),
    expected_integrity=(100000, 5000050000, 3676395719),
    fault_fingerprint_sql=_QP03_QUERY,
    business_query=_QP03_QUERY,
)

_TIDBQUERYPERFINDEXMERGESELECTIONFAILURE_REDUCED_CASE = replace(
    _TIDBQUERYPERFINDEXMERGESELECTIONFAILURESCENARIO_CASE,
    case_id="single_window_or_index_merge_disabled",
    case_no=1,
    evaluator=TidbQueryPerfIndexMergeSelectionFailureForSingleWindowOrEvaluatorCase,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": (
                        "the OR predicate on test.qp03_admission_events falls back to TableFullScan because the "
                        "current TiDB session has tidb_enable_index_merge disabled while the global setting is ON, "
                        "despite usable index branches for the time-bounded event search"
                    ),
                    "entity": "single_window_or_index_merge_disabled",
                    "evidence": [
                        "reference path observed the OR predicate on TableFullScan while the session "
                        "tidb_enable_index_merge is OFF and the global setting is ON"
                    ]
                },
                {
                    "type": "necessary_exclusion",
                    "factor": (
                        "the leading tenant_id branch of idx_tenant_time and the event_type branch of idx_type "
                        "are the two existing index paths needed to union the time-bounded OR branches with IndexMerge"
                    ),
                    "entity": "single_window_or_index_merge_disabled",
                    "evidence": [
                        "reference path observed both existing branch indexes in the index catalog"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "enabled tidb_enable_index_merge for the current session"
            ],
            "verification": [
                "verified the OR predicate uses IndexMerge again"
            ]
        },
        "summary": "The session optimizer setting caused the OR predicate full scan; enabling it for the session restores IndexMerge."
    },
    title=(
        "Simulates TiDB skipping Index Merge for a time-bounded OR event search while the optimizer setting is disabled."
    ),
    alert=(
        "[CRITICAL] [Grafana/TiDB-Query-Detail] 事件检索接口 P99 延迟从 18ms 上升到 4.6s。"
        "慢 SQL 集中在 test.qp03_admission_events 的带时间窗口 OR 事件检索，目标表 CPU 读放大明显；"
        "请从可观测的 SQL fingerprint 和执行计划中定位退化原因，恢复性能，同时保持结果集和整表真值不变。"
    ),
    background_workload=_QP03_REDUCED_BACKGROUND_WORKLOAD,
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.75,
        reference_run_ids=(
            "tidb-reference-3__tidb_query_perf_index_merge_selection_failure__"
            "single_window_or_index_merge_disabled__mock__r001",
        ),
    ),
)


class TidbQueryPerfIndexMergeSelectionFailureInjector(BaseFaultInjector):
    """Create the fixed ALT-QP01 data contract with Index Merge disabled."""

    def install(self, context: FaultLifecycleContext):
        self._configure(context.config)
        self._create_table(context.env)
        self._load_rows(context.env)
        self._execute(context.env, f"ANALYZE TABLE {self.db}.{self.table}", "analyze QP03 table")
        self._enable_global_index_merge(context.env)
        self._disable_index_merge(context.env)
        self._verify_fault_state(context.env)

    def activate(self, context: FaultLifecycleContext):
        self._configure(context.config)
        self._enable_global_index_merge(context.env)
        self._disable_index_merge(context.env)
        self._verify_fault_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext):
        self._configure(context.config)
        self._verify_fault_state(context.env)
        setting_sql = "SHOW VARIABLES LIKE 'tidb_enable_index_merge'"
        plan_sql = f"EXPLAIN {self.fault_fingerprint_sql}"
        result_summary = self._payload(
            context.env,
            self._business_result_summary_sql(),
            "capture QP03 business result summary",
        )
        return {
            "index_merge_setting": self._payload(context.env, setting_sql, "capture QP03 Index Merge setting"),
            "global_index_merge_setting": self._payload(
                context.env,
                "SHOW GLOBAL VARIABLES LIKE 'tidb_enable_index_merge'",
                "capture QP03 global Index Merge setting",
            ),
            "fault_plan": self._payload(context.env, plan_sql, "capture QP03 full-scan plan"),
            "business_result_truth": capture_query_result_truth(result_summary, ordered=True),
            "business_result_count": int(result_summary["result"][0][0]),
            "table_integrity": self._table_integrity(context.env),
            "index_catalog": self._payload(
                context.env,
                f"SHOW INDEX FROM {self.db}.{self.table}",
                "capture QP03 index catalog",
            ),
        }

    def quiesce(self, context: FaultLifecycleContext):
        return None

    def recover(self, context: FaultLifecycleContext):
        self._configure(context.config)
        self._execute(
            context.env,
            "SET SESSION tidb_enable_index_merge = ON",
            "restore QP03 Index Merge session setting",
        )
        self._enable_global_index_merge(context.env)
        self._execute(
            context.env,
            f"DROP TABLE IF EXISTS {self.db}.{self.table}",
            f"drop QP03 table {self.db}.{self.table}",
        )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.row_count = int(config["row_count"])
        self.expected_result_count = int(config["expected_result_count"])
        self.expected_result_summary = tuple(int(value) for value in config["expected_result_summary"])
        self.expected_integrity = tuple(int(value) for value in config["expected_integrity"])
        self.fault_fingerprint_sql = str(config["fault_fingerprint_sql"])
        self.business_query = str(config["business_query"])

    @staticmethod
    def _execute(env, sql: str, context: str) -> dict:
        return require_success_payload(env.execute_sql(sql), f"{context}: sql={sql!r}")

    @staticmethod
    def _payload(env, sql: str, context: str) -> dict:
        return require_success_payload(parse_json_object(env.execute_sql(sql), f"{context}: sql={sql!r}"), context)

    def _create_table(self, env) -> None:
        self._execute(env, f"DROP TABLE IF EXISTS {self.db}.{self.table}", f"clear QP03 table {self.db}.{self.table}")
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.table} ("
            "event_id BIGINT NOT NULL, "
            "tenant_id INT NOT NULL, "
            "event_ts DATETIME NOT NULL, "
            "event_type VARCHAR(16) NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, "
            "payload VARCHAR(128) NOT NULL, "
            "PRIMARY KEY (event_id), "
            "KEY idx_tenant_time (tenant_id, event_ts), "
            "KEY idx_type (event_type), "
            "KEY idx_amount_event (amount, event_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create QP03 table {self.db}.{self.table}",
        )

    def _load_rows(self, env) -> None:
        batch_size = 1000
        inserted = 0
        while inserted < self.row_count:
            size = min(batch_size, self.row_count - inserted)
            start = inserted
            self._execute(
                env,
                f"INSERT INTO {self.db}.{self.table} "
                "(event_id, tenant_id, event_ts, event_type, amount, payload) "
                "SELECT "
                f"{start} + n, MOD({start} + n, 128), "
                f"TIMESTAMPADD(SECOND, {start} + n, TIMESTAMP'2026-01-01 00:00:00'), "
                f"CASE WHEN MOD({start} + n, 128) = 7 THEN 'refund' "
                f"ELSE ELT(MOD({start} + n, 4) + 1, 'create', 'update', 'charge', 'close') END, "
                f"CAST(MOD(({start} + n) * 7919, 100000) / 100 AS DECIMAL(12,2)), "
                f"CASE WHEN MOD({start} + n, 2) = 0 THEN CONCAT('redacted:', {start} + n) "
                f"ELSE RPAD(CONCAT('event-', {start} + n), 64, 'x') END "
                "FROM ("
                "SELECT ROW_NUMBER() OVER ("
                "ORDER BY table_schema, table_name, column_name"
                ") AS n "
                "FROM information_schema.columns "
                f"LIMIT {size}"
                ") AS source",
                f"load QP03 rows starting at {start}",
            )
            inserted += size

    def _disable_index_merge(self, env) -> None:
        self._execute(env, "SET SESSION tidb_enable_index_merge = OFF", "disable QP03 Index Merge")

    def _enable_global_index_merge(self, env) -> None:
        self._execute(env, "SET GLOBAL tidb_enable_index_merge = ON", "set QP03 global Index Merge baseline")

    def _verify_fault_state(self, env) -> None:
        count = self._table_integrity(env)
        if count != self.expected_integrity:
            raise RuntimeError(
                "QP03 table integrity mismatch before agent handoff: "
                f"table={self.db}.{self.table}, expected={self.expected_integrity!r}, observed={count!r}"
            )
        setting = self._payload(env, "SHOW VARIABLES LIKE 'tidb_enable_index_merge'", "verify QP03 setting")["result"]
        if setting != [["tidb_enable_index_merge", "OFF"]]:
            raise RuntimeError(f"QP03 Index Merge setting must be OFF: observed={setting!r}")
        global_setting = self._payload(
            env,
            "SHOW GLOBAL VARIABLES LIKE 'tidb_enable_index_merge'",
            "verify QP03 global setting",
        )["result"]
        if global_setting != [["tidb_enable_index_merge", "ON"]]:
            raise RuntimeError(f"QP03 global Index Merge setting must be ON: observed={global_setting!r}")
        result_summary = self._payload(
            env,
            self._business_result_summary_sql(),
            "verify QP03 business result summary",
        )["result"][0]
        if tuple(int(value) for value in result_summary) != self.expected_result_summary:
            raise RuntimeError(
                "QP03 business result summary mismatch before agent handoff: "
                f"expected={self.expected_result_summary!r}, observed={result_summary!r}"
            )
        plan = self._payload(env, f"EXPLAIN {self.fault_fingerprint_sql}", "verify QP03 fault plan")["result"]
        rendered = "\n".join(" | ".join(str(value) for value in row) for row in plan).casefold()
        if "tablefullscan" not in rendered or "indexmerge" in rendered:
            raise RuntimeError(
                "QP03 fault plan must be TableFullScan without IndexMerge: "
                f"table={self.db}.{self.table}, plan={plan!r}"
            )

    def _table_integrity(self, env) -> tuple[int, int, int]:
        sql = (
            f"SELECT COUNT(*), COALESCE(SUM(event_id), 0), "
            "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_type, amount, payload))), 0) "
            f"FROM {self.db}.{self.table}"
        )
        row = self._payload(env, sql, f"verify QP03 table integrity: sql={sql!r}")["result"][0]
        return int(row[0]), int(row[1]), int(row[2])

    def _business_result_summary_sql(self) -> str:
        return (
            "SELECT COUNT(*), COALESCE(SUM(event_id), 0), "
            "COALESCE(BIT_XOR(CRC32(CAST(event_id AS CHAR))), 0) "
            f"FROM ({self.business_query}) AS qp03_result"
        )


class TidbQueryPerfIndexMergeSelectionFailureScenario(TiDBScenario):
    scenario_id = "tidb_query_perf_index_merge_selection_failure"
    description = "Simulates Index Merge selection failure for a TiDB OR predicate."
    cases = (
        _TIDBQUERYPERFINDEXMERGESELECTIONFAILURESCENARIO_CASE,
        _TIDBQUERYPERFINDEXMERGESELECTIONFAILURE_REDUCED_CASE,
    )

    def build_fault_plan(
        self,
        case: TidbQueryPerfIndexMergeSelectionFailureCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbQueryPerfIndexMergeSelectionFailureInjector,
                config={
                    "db": case.db,
                    "table": case.table,
                    "row_count": case.row_count,
                    "expected_result_count": case.expected_result_count,
                    "expected_result_summary": case.expected_result_summary,
                    "expected_integrity": case.expected_integrity,
                    "fault_fingerprint_sql": case.fault_fingerprint_sql,
                    "business_query": case.business_query,
                },
            ),
        )
