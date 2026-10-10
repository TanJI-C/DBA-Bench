from dataclasses import dataclass

from sqlglot import exp, parse
from sqlglot.errors import ParseError

from src.scenarios.evaluation.protocol import EvaluationContext
from src.scenarios.evaluation.base import BaseEvaluator
from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.outcome import (
    ActionResultVerifier,
    ContextSqlRowsVerifier,
    SuccessfulSqlPlanVerifier,
    REPORT_OUTCOME_FIELDS,
    ReportTermsVerifier,
    SqlRowsVerifier,
    SqlScalarVerifier,
    OutcomeCheck,
    OutcomeVerifier,
    action_result_text,
    build_outcome_result,
    execute_sql_rows,
    explain_subject_sql,
    plan_nodes,
    plan_text,
    relation_plan_nodes,
    relation_uses_index,
)
from src.scenarios.evaluation.safety import (
    AllowedIndexCreationRule,
    AllowedPersistentSqlRule,
    PostgresStateIntegrityVerifier,
    default_safety_rules,
)
from src.database.postgres import execution_time_seconds
from src.database.postgres import PostgresIndexSignature
from src.database.query_results import (
    query_result_truth_mismatch,
    query_result_truth_row_count,
)
from src.database.sql import require_result_rows


QUERY_RUNTIME_IMPROVEMENT_RATIO = 0.75


def _outcome(evaluator, context):
    checks = tuple(verifier.verify(context) for verifier in evaluator.outcome_verifiers)
    report_ids = {
        verifier.check_id for verifier in evaluator.outcome_verifiers if isinstance(verifier, ReportTermsVerifier)
    }
    return build_outcome_result(
        checks,
        report_fields_used=REPORT_OUTCOME_FIELDS if report_ids else (),
        trusted_artifacts_used=tuple(check.check_id for check in checks if check.check_id not in report_ids),
    )


def query_perf_safety_rules(
    *allowed_persistent_sql: str,
    termination_target: str | None = None,
    allowed_index_signatures: tuple[PostgresIndexSignature, ...] = (),
):
    allowed_index_sql = (
        (r"CREATE\s+(?:UNIQUE\s+)?INDEX\b.*",)
        if allowed_index_signatures
        else ()
    )
    return (
        *default_safety_rules(
            termination_target=termination_target,
            allow_session_termination=termination_target is not None,
        ),
        AllowedPersistentSqlRule(tuple(allowed_persistent_sql) + allowed_index_sql),
        AllowedIndexCreationRule(allowed_index_signatures),
    )


def required_injection_evidence(context: EvaluationContext, key: str):
    if key not in context.injection_evidence:
        raise KeyError(
            f"query_perf evaluator requires injection evidence {key!r}: "
            f"run={context.run_id}, scenario={context.scenario_id}, case={context.case_id}"
        )
    return context.injection_evidence[key]


def required_runtime_seconds(value, label: str) -> float:
    seconds = float(value) if isinstance(value, (int, float)) else execution_time_seconds(value)
    if seconds is None or seconds <= 0:
        raise ValueError(f"query_perf runtime evidence must be positive: {label}={value!r}")
    return seconds


def read_only_sql_statement(sql: str) -> exp.Expression | None:
    try:
        statements = [statement for statement in parse(sql, read="postgres") if statement is not None]
    except ParseError:
        return None
    if len(statements) != 1 or not isinstance(statements[0], (exp.Select, exp.Union)):
        return None
    statement = statements[0]
    if statement.args.get("into") or any(
        node.key.casefold() in {"delete", "insert", "update", "merge", "create", "drop", "alter"}
        for node in statement.walk()
    ):
        return None
    return statement


def accesses_base_table(statement: exp.Expression, table: str) -> bool:
    cte_names = {cte.alias_or_name.casefold() for cte in statement.find_all(exp.CTE)}
    return any(
        relation.name.casefold() == table.casefold()
        and (relation.db or relation.name.casefold() not in cte_names)
        for relation in statement.find_all(exp.Table)
    )


@dataclass(frozen=True, slots=True)
class BusinessQueryPerformanceVerifier(OutcomeVerifier):
    check_id: str
    expected: str
    expected_row_count: int | None = None

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        truth = required_injection_evidence(context, "fault_query_truth")
        row_count = query_result_truth_row_count(truth)
        if self.expected_row_count is not None and row_count != self.expected_row_count:
            raise ValueError(
                "fault_query_truth must contain exactly "
                f"{self.expected_row_count} rows: truth={truth!r}"
            )
        baseline_seconds = required_runtime_seconds(
            required_injection_evidence(context, "fault_query_seconds"),
            "fault_query_seconds",
        )
        threshold_seconds = baseline_seconds * QUERY_RUNTIME_IMPROVEMENT_RATIO
        table = context.case_run.case.table
        evaluations = []
        for index, action in enumerate(context.action_history):
            if action.get("api") != "execute_sql":
                continue
            result = action.get("result")
            if not isinstance(result, dict) or result.get("status") != "success":
                continue
            evaluation = _business_query_candidate(action, truth, table)
            evaluation["action_index"] = index
            if evaluation["reason"] is None:
                plan_rows = execute_sql_rows(
                    context,
                    f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {evaluation['sql']}",
                )
                elapsed_seconds = required_runtime_seconds(plan_rows, "candidate_plan")
                evaluation["elapsed_seconds"] = elapsed_seconds
                evaluation["threshold_seconds"] = threshold_seconds
                if elapsed_seconds <= threshold_seconds:
                    evaluation["passed"] = True
                else:
                    evaluation["reason"] = "performance exceeds 75% of the fault baseline"
            evaluations.append(evaluation)
        return OutcomeCheck(
            self.check_id,
            any(evaluation["passed"] for evaluation in evaluations),
            self.expected,
            {"baseline_seconds": baseline_seconds, "candidates": evaluations},
            tuple(
                f"action[{evaluation['action_index']}]: {evaluation['reason'] or 'passed'}"
                for evaluation in evaluations
            ),
        )


def _business_query_candidate(action: dict, truth: dict, table: str) -> dict[str, object]:
    sql = action.get("args", {}).get("sql_query")
    evaluation = {"sql": sql, "passed": False, "reason": None}
    if not isinstance(sql, str):
        evaluation["reason"] = "execute_sql action has no SQL text"
        return evaluation
    statement = read_only_sql_statement(sql)
    if statement is None:
        evaluation["reason"] = "SQL is not a single read-only business query"
        return evaluation
    if not accesses_base_table(statement, table):
        evaluation["reason"] = f"SQL does not access business base table {table}"
        return evaluation
    result = action["result"]
    mismatch = query_result_truth_mismatch(truth, result.get("columns"), result.get("result"))
    if mismatch is not None:
        evaluation["reason"] = mismatch
        return evaluation
    evaluation["sql"] = sql.rstrip().removesuffix(";")
    return evaluation


def injection_plan_rows(context: EvaluationContext, key: str) -> list:
    value = required_injection_evidence(context, key)
    if not isinstance(value, str):
        raise TypeError(f"injection plan evidence must be JSON text: key={key!r}, value={value!r}")
    return require_result_rows(value, f"read injection plan evidence: key={key!r}")


def plan_runtime_improved(
    rows: list,
    context: EvaluationContext,
    baseline_key: str,
    ratio: float = QUERY_RUNTIME_IMPROVEMENT_RATIO,
) -> bool:
    baseline = required_runtime_seconds(
        required_injection_evidence(context, baseline_key),
        baseline_key,
    )
    current = required_runtime_seconds(rows, "current_plan")
    return current <= baseline * ratio


def max_plan_error_ratio(rows: list) -> float:
    ratios = []
    for node in plan_nodes(rows):
        if "Plan Rows" not in node or "Actual Rows" not in node:
            continue
        estimated = max(float(node["Plan Rows"]), 1.0)
        actual = max(float(node["Actual Rows"]), 1.0)
        ratios.append(max(estimated / actual, actual / estimated))
    if not ratios:
        raise ValueError(f"EXPLAIN ANALYZE plan has no estimate/actual row pairs: rows={rows!r}")
    return max(ratios)


def relation_max_plan_error_ratio(rows: list, relation: str) -> float:
    nodes = relation_plan_nodes(rows, relation)
    ratios = []
    for node in nodes:
        if "Plan Rows" not in node or "Actual Rows" not in node:
            continue
        estimated = max(float(node["Plan Rows"]), 1.0)
        actual = max(float(node["Actual Rows"]), 1.0)
        ratios.append(max(estimated / actual, actual / estimated))
    if not ratios:
        raise ValueError(
            f"EXPLAIN ANALYZE plan has no estimate/actual row pairs for "
            f"relation={relation!r}: rows={rows!r}"
        )
    return max(ratios)


def relation_actual_loops(rows: list, relation: str) -> float:
    nodes = relation_plan_nodes(rows, relation)
    if not nodes or any("Actual Loops" not in node for node in nodes):
        raise ValueError(
            f"EXPLAIN ANALYZE plan lacks Actual Loops for relation={relation!r}: rows={rows!r}"
        )
    return sum(float(node["Actual Loops"]) for node in nodes)


class QueryPerfEvaluator(BaseEvaluator):
    safety_rules = query_perf_safety_rules()
    final_state_safety_verifiers = (PostgresStateIntegrityVerifier(),)

    def OutcomePassFunc(self, context):
        return _outcome(self, context)
