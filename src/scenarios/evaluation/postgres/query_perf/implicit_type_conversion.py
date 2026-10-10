from .base import BusinessQueryPerformanceVerifier, QueryPerfEvaluator, condition


_CAST_DP = (
    condition(
        "target_localized",
        "order exception triage query",
        "receipt watchlist report",
        "receipt number implicit type conversion",
        "branch order line bol receipt number",
        critical=True,
    ),
    condition(
        "root_cause",
        "request values have wrong type",
        "numeric receipt watchlist compared with integer key",
        "类型不匹配导致索引失效",
        critical=True,
    ),
    condition(
        "causal_mechanism",
        "implicit cast bypasses integer index",
        "numeric coercion forces sequential scan",
        "receipt watchlist 包含小数元素无法直接转 integer",
        critical=True,
    ),
)


class PgQueryPerfImplicitTypeConversionForBranchOrderImplicitCastEvaluatorCase(QueryPerfEvaluator):
    scenario_id = "pg_query_perf_implicit_type_conversion"
    case_id = "branch_order_implicit_cast"
    diagnosis_conditions = _CAST_DP
    outcome_verifiers = (BusinessQueryPerformanceVerifier(
        "business_query_result_and_performance_recovered",
        "a successful read-only branch_order_line query returns the captured ordered business "
        "result and independently runs at least 25% faster",
    ),)


class PgQueryPerfImplicitTypeConversionForBranchOrderImplicitCastSimpleEvaluatorCase(
    PgQueryPerfImplicitTypeConversionForBranchOrderImplicitCastEvaluatorCase
):
    case_id = "branch_order_implicit_cast_simple"
