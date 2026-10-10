from .base import (
    BusinessQueryPerformanceVerifier,
    QueryPerfEvaluator,
    condition,
)

_OFFSET_DP = (
    condition(
        "target_localized",
        "audit export deep batch query",
        "high rank pagination query",
        "deep offset pagination",
        "branch order line",
        critical=True,
    ),
    condition(
        "root_cause",
        "deep offset pagination",
        "million row row_number pagination",
        "pagination cost",
        critical=True,
    ),
    condition(
        "causal_mechanism",
        "offset scans and discards preceding rows",
        "pagination cost grows linearly",
        "missed keyset pagination opportunity",
        critical=True,
    ),
)

# shallow reference path 的诊断合同：alert 不再给出 SQL 与修复方向，
# Agent 必须在语句历史（topsql/pg_stat_statements）中定位晚页导出语句，再用
# 计划分析把代价归因到 row_number 深分页机制。别名覆盖正确诊断的自然表述
# （含单复数变体），三个 critical 条件同时命中才通过。
_SHALLOW_OFFSET_DP = (
    condition(
        "target_localized",
        "branch order line",
        "branch order export",
        "late page",
        "late-page export query",
        "export endpoint",
        critical=True,
    ),
    condition(
        "root_cause",
        "row_number pagination",
        "row number pagination",
        "row_number window",
        "row number window",
        "row_number",
        "row number",
        "deep pagination",
        "deep offset pagination",
        "high rank pagination",
        "offset pagination",
        "pagination cost",
        critical=True,
    ),
    condition(
        "causal_mechanism",
        "scans and discards",
        "scan and discard",
        "discards preceding rows",
        "discard preceding rows",
        "discarding preceding rows",
        "skips preceding rows",
        "skip preceding rows",
        "skipping preceding rows",
        "numbering all preceding rows",
        "numbering all prior rows",
        "numbering preceding rows",
        "numbering and discarding",
        "scanning and numbering",
        "ordered prefix",
        "prefix scan",
        "cost grows with page depth",
        "cost grow with page depth",
        "grows with page depth",
        "grows with requested page depth",
        "grows with depth",
        "cost grows linearly",
        "cost grow linearly",
        "missed keyset",
        "keyset pagination opportunity",
        "keyset seek",
        "seek pagination",
        "offset scans and discards preceding rows",
        critical=True,
    ),
)


class PgQueryPerfHeavyOffsetPaginationForBranchOrderDeepOffsetEvaluatorCase(QueryPerfEvaluator):
    scenario_id = "pg_query_perf_heavy_offset_pagination"
    case_id = "branch_order_deep_offset"
    diagnosis_conditions = _OFFSET_DP
    outcome_verifiers = (BusinessQueryPerformanceVerifier(
        "business_query_result_and_performance_recovered",
        "a successful read-only branch_order_line query returns the captured ordered ten-row "
        "business result and independently runs at least 25% faster",
        expected_row_count=10,
    ),)


class PgQueryPerfHeavyOffsetPaginationForBranchOrderShallowOffsetEvaluatorCase(
    PgQueryPerfHeavyOffsetPaginationForBranchOrderDeepOffsetEvaluatorCase
):
    case_id = "branch_order_shallow_offset"
    diagnosis_conditions = _SHALLOW_OFFSET_DP
