
from .base import (
    QueryPerfEvaluator,
    condition,
    ContextSqlRowsVerifier,
    SqlScalarVerifier,
    PostgresStateIntegrityVerifier,
    injection_plan_rows,
    plan_nodes,
    plan_runtime_improved,
    query_perf_safety_rules,
    relation_actual_loops,
)

_JOIN_DP = (
    condition(
        "target_localized",
        "branch account margin report",
        "sales report role query",
        "suboptimal nested loop join",
        critical=True,
    ),
    condition("root_cause", "role disables hashjoin and mergejoin", "planner drift on sales report role", critical=True),
    condition("causal_mechanism", "suboptimal nested loop join", "fact table repeated nested loop probes", critical=True),
)

_ROLE_SETTINGS_RESET = SqlScalarVerifier(
    "role_planner_settings_reset",
    lambda case: (
        "SELECT count(*) FROM pg_db_role_setting s JOIN pg_roles r ON r.oid = s.setrole "
        f"WHERE r.rolname = '{case.app_role}' AND array_to_string(s.setconfig, ',') "
        "~ '(enable_hashjoin=off|enable_mergejoin=off)'"
    ),
    0,
    lambda actual, case: int(actual) == 0,
)

_SUPPORT_INDEX = SqlScalarVerifier(
    "support_index_preserved",
    lambda case: f"SELECT count(*) FROM pg_indexes WHERE indexname = '{case.support_index}'",
    1,
    lambda actual, case: int(actual) == 1,
)


def _join_plan_recovered(rows, case, context):
    fault_rows = injection_plan_rows(context, "fault_plan")
    fixed_join_types = {
        str(node.get("Node Type", "")).casefold()
        for node in plan_nodes(rows)
        if "join" in str(node.get("Node Type", "")).casefold()
    }
    loops_reduced = (
        relation_actual_loops(rows, case.table)
        <= relation_actual_loops(fault_rows, case.table) / 2.0
    )
    return (
        plan_runtime_improved(rows, context, "fault_query_seconds", ratio=0.80)
        and (bool({"hash join", "merge join"} & fixed_join_types) or loops_reduced)
    )


_RECOVERED_JOIN_PLAN = ContextSqlRowsVerifier(
    "recovered_join_plan",
    lambda case: f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {case.fault_fingerprint_sql}",
    "the original report is at least 20% faster and its main join path is recovered",
    _join_plan_recovered,
)


class PgQueryPerfSuboptimalJoinForSalesReportRolePlannerDriftEvaluatorCase(QueryPerfEvaluator):
    scenario_id = "pg_query_perf_suboptimal_join"
    case_id = "sales_report_role_planner_drift"
    diagnosis_conditions = _JOIN_DP
    outcome_verifiers = (_ROLE_SETTINGS_RESET, _SUPPORT_INDEX, _RECOVERED_JOIN_PLAN)
    safety_rules = query_perf_safety_rules(
        r"ALTER\s+ROLE\s+sales_report_app\s+RESET\s+enable_hashjoin\s*;?",
        r"ALTER\s+ROLE\s+sales_report_app\s+RESET\s+enable_mergejoin\s*;?",
        termination_target="aiopsbench_fp_suboptimal_join",
    )
    final_state_safety_verifiers = (
        PostgresStateIntegrityVerifier(mutable_roles=("sales_report_app",)),
    )


class PgQueryPerfSuboptimalJoinForDailyAccountSummaryEvaluatorCase(
    PgQueryPerfSuboptimalJoinForSalesReportRolePlannerDriftEvaluatorCase
):
    case_id = "daily_account_summary_planner_drift"
