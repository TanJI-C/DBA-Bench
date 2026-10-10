
from .base import (
    QueryPerfEvaluator,
    condition,
    ContextSqlRowsVerifier,
    SqlScalarVerifier,
    PostgresStateIntegrityVerifier,
    plan_nodes,
    plan_runtime_improved,
)

_PARAMETER_DP = (
    condition(
        "target_localized",
        "customer 360 hot year query",
        "hot and rare year report",
        "hot and rare year cardinality skew",
        critical=True,
    ),
    condition(
        "root_cause",
        "generic prepared plan reused under parameter skew",
        "generic prepared plan reused",
        "parameter sensitive generic plan",
        critical=True,
    ),
    condition("causal_mechanism", "hot year uses unsuitable cached plan", "parameter sniffing plan mismatch", critical=True),
)

_CUSTOM_PLAN_MODE = SqlScalarVerifier(
    "custom_plan_mode",
    lambda case: "SELECT current_setting('plan_cache_mode')",
    "force_custom_plan",
    lambda actual, case: str(actual) == "force_custom_plan",
)

_HOT_BIND_PLAN = ContextSqlRowsVerifier(
    "hot_bind_plan_recovered",
    lambda case: (
        f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
        f"EXECUTE {case.stmt_name}({case.hot_year})"
    ),
    "the original hot bind uses a custom plan and runs at least 25% faster",
    lambda rows, case, context: (
        bool(plan_nodes(rows))
        and plan_runtime_improved(rows, context, "fault_query_seconds")
    ),
)

_PREPARED_CUSTOM = SqlScalarVerifier(
    "prepared_statement_uses_custom_plan",
    lambda case: (
        "SELECT count(*) FROM pg_prepared_statements "
        f"WHERE name = '{case.stmt_name}' AND custom_plans > 0 AND generic_plans = 0"
    ),
    1,
    lambda actual, case: int(actual) == 1,
)


class PgQueryPerfParameterSniffingForBranchOrderYearSkewEvaluatorCase(QueryPerfEvaluator):
    scenario_id = "pg_query_perf_parameter_sniffing"
    case_id = "branch_order_year_skew"
    diagnosis_conditions = _PARAMETER_DP
    outcome_verifiers = (_CUSTOM_PLAN_MODE, _HOT_BIND_PLAN, _PREPARED_CUSTOM)
    final_state_safety_verifiers = (PostgresStateIntegrityVerifier(),)


class PgQueryPerfParameterSniffingForBranchOrderYearSkewSimpleEvaluatorCase(
    PgQueryPerfParameterSniffingForBranchOrderYearSkewEvaluatorCase
):
    case_id = "branch_order_year_skew_simple"
