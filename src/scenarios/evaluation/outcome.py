from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import re
import time
from typing import Any, Callable

from src.scenarios.evaluation.protocol import EvaluationContext
from src.database.sql import (
    execute_result_rows,
    parse_json_object,
    require_success_payload,
)


@dataclass(frozen=True, slots=True)
class OutcomeCheck:
    check_id: str
    passed: bool
    expected: Any
    actual: Any
    evidence: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "pass": self.passed,
            "expected": self.expected,
            "actual": self.actual,
            "evidence": list(self.evidence),
        }


class OutcomeVerifier(ABC):
    @abstractmethod
    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        raise NotImplementedError


class CompositeOutcomeVerifier(OutcomeVerifier):
    def __init__(self, verifiers: tuple[OutcomeVerifier, ...]):
        self.verifiers = verifiers

    def verify_all(self, context: EvaluationContext) -> dict[str, Any]:
        checks = tuple(verifier.verify(context) for verifier in self.verifiers)
        return build_outcome_result(checks)

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        raise TypeError("CompositeOutcomeVerifier must be evaluated with verify_all()")


def execute_sql_rows(context: EvaluationContext, sql: str) -> list:
    return execute_result_rows(context.case_run.env.execute_sql, sql, "outcome query")


def execute_trusted_sql_rows(context: EvaluationContext, sql: str) -> list:
    executor = getattr(context.case_run.env, "execute_sql_trusted", None)
    if not callable(executor):
        # Lightweight evaluator fakes may only implement the public executor;
        # production PGEnv always exposes the trusted current-state boundary.
        executor = context.case_run.env.execute_sql
    return execute_result_rows(executor, sql, "trusted live outcome query")


def execute_sql_scalar(context: EvaluationContext, sql: str) -> object:
    rows = execute_sql_rows(context, sql)
    if len(rows) != 1 or not isinstance(rows[0], (list, tuple)) or len(rows[0]) != 1:
        raise ValueError(f"outcome scalar query expected one row and one column: sql={sql!r}, rows={rows!r}")
    return rows[0][0]


def eventually_sql_rows(
    context: EvaluationContext,
    sql: str,
    *,
    max_attempts: int,
    interval_seconds: float,
    predicate: Callable[[list], bool],
) -> tuple[list, int, bool]:
    rows = []
    for attempt in range(1, max_attempts + 1):
        rows = execute_sql_rows(context, sql)
        if predicate(rows):
            return rows, attempt, True
        if attempt < max_attempts:
            time.sleep(interval_seconds)
    return rows, max_attempts, False


def plan_text(rows: list) -> str:
    """Render an EXPLAIN result for structural assertions without trusting report text."""
    if len(rows) != 1 or not isinstance(rows[0], (list, tuple)) or not rows[0]:
        raise ValueError(f"EXPLAIN result must contain one non-empty row: rows={rows!r}")
    return json.dumps(rows[0][0], ensure_ascii=False, sort_keys=True, default=str).casefold()


def plan_nodes(rows: list) -> tuple[dict, ...]:
    if len(rows) != 1 or not isinstance(rows[0], (list, tuple)) or len(rows[0]) != 1:
        raise ValueError(f"EXPLAIN result must contain one row and one column: rows={rows!r}")

    nodes = []

    def visit(value):
        if isinstance(value, dict):
            if "Node Type" in value:
                nodes.append(value)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(rows[0][0])
    return tuple(nodes)


def relation_plan_nodes(rows: list, relation: str) -> tuple[dict, ...]:
    expected = relation.casefold().split(".")[-1]
    return tuple(
        node
        for node in plan_nodes(rows)
        if str(node.get("Relation Name", "")).casefold().split(".")[-1] == expected
    )


def _descendant_plan_nodes(node: dict) -> tuple[dict, ...]:
    descendants = []

    def visit(value):
        if isinstance(value, dict):
            if "Node Type" in value:
                descendants.append(value)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    for child in node.get("Plans", ()):
        visit(child)
    return tuple(descendants)


def relation_uses_index(rows: list, relation: str, index_name: str | None = None) -> bool:
    nodes = relation_plan_nodes(rows, relation)
    if not nodes or not all(
        str(node["Node Type"]).casefold() in {"index scan", "index only scan", "bitmap heap scan"}
        for node in nodes
    ):
        return False
    if index_name is None:
        return True
    expected = index_name.casefold().split(".")[-1]
    observed = {
        str(node.get("Index Name", "")).casefold().split(".")[-1]
        for node in (*nodes, *(descendant for node in nodes for descendant in _descendant_plan_nodes(node)))
        if node.get("Index Name")
    }
    return observed == {expected}


def explain_subject_sql(sql: str) -> str:
    match = re.match(r"\s*EXPLAIN(?:\s*\([^)]*\))?\s+", sql, re.I | re.S)
    return sql[match.end():] if match else sql


@dataclass(frozen=True, slots=True)
class SqlScalarVerifier(OutcomeVerifier):
    check_id: str
    sql: Callable[[object], str]
    expected: object
    predicate: Callable[[object, object], bool]

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        statement = self.sql(context.case_run.case)
        actual = execute_sql_scalar(context, statement)
        return OutcomeCheck(
            check_id=self.check_id,
            passed=self.predicate(actual, context.case_run.case),
            expected=self.expected,
            actual=actual,
            evidence=(statement,),
        )


@dataclass(frozen=True, slots=True)
class EventuallySqlScalarVerifier(OutcomeVerifier):
    check_id: str
    sql: Callable[[object], str]
    expected: object
    predicate: Callable[[object, object], bool]
    max_attempts: int
    interval_seconds: float

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        statement = self.sql(context.case_run.case)
        expected = (
            self.expected(context.case_run.case)
            if callable(self.expected)
            else self.expected
        )
        actual = None
        for attempt in range(1, self.max_attempts + 1):
            actual = execute_sql_scalar(context, statement)
            if self.predicate(actual, context.case_run.case):
                return OutcomeCheck(
                    check_id=self.check_id,
                    passed=True,
                    expected=expected,
                    actual=actual,
                    evidence=(statement, f"attempts={attempt}"),
                )
            if attempt < self.max_attempts:
                time.sleep(self.interval_seconds)
        return OutcomeCheck(
            check_id=self.check_id,
            passed=False,
            expected=expected,
            actual=actual,
            evidence=(statement, f"attempts={self.max_attempts}"),
        )


@dataclass(frozen=True, slots=True)
class SqlRowsVerifier(OutcomeVerifier):
    check_id: str
    sql: Callable[[object], str]
    expected: object
    predicate: Callable[[list, object], bool]

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        statement = self.sql(context.case_run.case)
        rows = execute_sql_rows(context, statement)
        return OutcomeCheck(
            check_id=self.check_id,
            passed=self.predicate(rows, context.case_run.case),
            expected=self.expected,
            actual=rows,
            evidence=(statement,),
        )


@dataclass(frozen=True, slots=True)
class EventuallySqlRowsVerifier(OutcomeVerifier):
    check_id: str
    sql: Callable[[object], str]
    expected: object
    predicate: Callable[[list, object], bool]
    max_attempts: int
    interval_seconds: float

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        statement = self.sql(context.case_run.case)
        rows, attempts, passed = eventually_sql_rows(
            context,
            statement,
            max_attempts=self.max_attempts,
            interval_seconds=self.interval_seconds,
            predicate=lambda values: self.predicate(values, context.case_run.case),
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=passed,
            expected=self.expected,
            actual=rows,
            evidence=(statement, f"attempts={attempts}"),
        )


@dataclass(frozen=True, slots=True)
class ContextSqlRowsVerifier(OutcomeVerifier):
    check_id: str
    sql: Callable[[object], str]
    expected: object
    predicate: Callable[[list, object, EvaluationContext], bool]

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        statement = self.sql(context.case_run.case)
        rows = execute_sql_rows(context, statement)
        return OutcomeCheck(
            check_id=self.check_id,
            passed=self.predicate(rows, context.case_run.case, context),
            expected=self.expected,
            actual=rows,
            evidence=(statement,),
        )


@dataclass(frozen=True, slots=True)
class TrustedSqlRowsVerifier(OutcomeVerifier):
    check_id: str
    sql: Callable[[object], str]
    expected: object
    predicate: Callable[[list, object], bool]

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        statement = self.sql(context.case_run.case)
        rows = execute_result_rows(
            context.case_run.env.execute_sql_trusted,
            statement,
            "trusted outcome query",
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=self.predicate(rows, context.case_run.case),
            expected=self.expected,
            actual=rows,
            evidence=(statement,),
        )


@dataclass(frozen=True, slots=True)
class TrustedContextSqlRowsVerifier(OutcomeVerifier):
    check_id: str
    sql: Callable[[object], str]
    expected: object
    predicate: Callable[[list, object, EvaluationContext], bool]

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        statement = self.sql(context.case_run.case)
        rows = execute_result_rows(
            context.case_run.env.execute_sql_trusted,
            statement,
            "trusted outcome query",
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=self.predicate(rows, context.case_run.case, context),
            expected=self.expected,
            actual=rows,
            evidence=(statement,),
        )


@dataclass(frozen=True, slots=True)
class SqlResponseVerifier(OutcomeVerifier):
    check_id: str
    sql: Callable[[object], str]
    expected: object
    predicate: Callable[[dict, object], bool]

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        statement = self.sql(context.case_run.case)
        payload = parse_json_object(
            context.case_run.env.execute_sql(statement),
            f"outcome response: sql={statement!r}",
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=self.predicate(payload, context.case_run.case),
            expected=self.expected,
            actual=payload,
            evidence=(statement,),
        )


@dataclass(frozen=True, slots=True)
class TrustedSqlResponseVerifier(OutcomeVerifier):
    check_id: str
    sql: Callable[[object], str]
    expected: object
    predicate: Callable[[dict, object], bool]

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        statement = self.sql(context.case_run.case)
        payload = parse_json_object(
            context.case_run.env.execute_sql_trusted(statement),
            f"trusted outcome response: sql={statement!r}",
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=self.predicate(payload, context.case_run.case),
            expected=self.expected,
            actual=payload,
            evidence=(statement,),
        )


@dataclass(frozen=True, slots=True)
class ActionResultVerifier(OutcomeVerifier):
    check_id: str
    expected: object
    predicate: Callable[[dict, object], bool]

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        matches = tuple(
            action
            for action in context.action_history
            if "result" in action
            and isinstance(action["result"], dict)
            and action["result"].get("status") == "success"
            and _has_result_payload(action["result"])
            and self.predicate(action, context.case_run.case)
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=bool(matches),
            expected=self.expected,
            actual={"matching_action_count": len(matches)},
            evidence=tuple(
                f"{action['api']}({json.dumps(action['args'], sort_keys=True, default=str)})"
                for action in matches
            ),
        )


@dataclass(frozen=True, slots=True)
class SuccessfulSqlPlanVerifier(OutcomeVerifier):
    check_id: str
    expected: object
    action_predicate: Callable[[dict, object], bool]
    plan_predicate: Callable[[list, object, EvaluationContext], bool]

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        matches = tuple(
            action
            for action in context.action_history
            if action.get("api") == "execute_sql"
            and isinstance(action.get("result"), dict)
            and action["result"].get("status") == "success"
            and _has_result_payload(action["result"])
            and self.action_predicate(action, context.case_run.case)
        )
        if not matches:
            return OutcomeCheck(self.check_id, False, self.expected, {"matching_action_count": 0}, ())

        action = matches[-1]
        statement = action["args"]["sql_query"]
        subject = explain_subject_sql(statement)
        if subject == statement:
            plan = execute_sql_rows(context, f"EXPLAIN (ANALYZE, FORMAT JSON) {statement}")
        else:
            plan = action["result"].get("result")
            if not isinstance(plan, list):
                raise TypeError(
                    f"successful EXPLAIN action must contain result rows: action={action!r}"
                )
        return OutcomeCheck(
            self.check_id,
            self.plan_predicate(plan, context.case_run.case, context),
            self.expected,
            {"matching_action_count": len(matches), "plan": plan},
            (subject,),
        )


@dataclass(frozen=True, slots=True)
class ActionOrderVerifier(OutcomeVerifier):
    """Require two remediation events to occur in the declared order."""

    check_id: str
    first: Callable[[dict, object, tuple[dict, ...]], bool]
    second: Callable[[dict, object, tuple[dict, ...]], bool]
    expected: object

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        first_index = None
        second_index = None
        second_before_first = False
        for index, action in enumerate(context.action_history):
            if action.get("api") == "submit":
                continue
            result = action.get("result")
            if not isinstance(result, dict) or result.get("status") != "success":
                continue
            if self.second(action, context.case_run.case, context.action_history):
                if first_index is None:
                    second_before_first = True
                elif second_index is None:
                    second_index = index
                continue
            if first_index is None and self.first(action, context.case_run.case, context.action_history):
                first_index = index
        passed = first_index is not None and second_index is not None and not second_before_first
        return OutcomeCheck(
            self.check_id,
            passed,
            self.expected,
            {"first_index": first_index, "second_index": second_index},
            (f"first={first_index}", f"second={second_index}"),
        )


def _has_result_payload(result: dict) -> bool:
    if "data" in result:
        return result["data"] not in (None, {}, [], "")
    if "result" in result:
        return bool(result["result"])
    if "value" in result:
        return result["value"] not in (None, {}, [], "")
    for key in ("series", "records", "snapshot"):
        if key in result:
            return result[key] not in (None, {}, [], "")
    return any(
        key in result
        for key in ("action", "metric", "param", "rows_affected", "content", "error")
    )


def action_result_text(action: dict) -> str:
    return json.dumps(action.get("result"), ensure_ascii=False, sort_keys=True, default=str).casefold()


REPORT_TERM_SEPARATOR = re.compile(r"[-_]+")
REPORT_OUTCOME_FIELDS = ("changes", "verification", "plan", "summary")


def normalize_report_term(term: str) -> str:
    """Fold separator variants so 'maintenance-window' matches 'maintenance window'."""
    return REPORT_TERM_SEPARATOR.sub(" ", term).casefold()


def report_outcome_text(context: EvaluationContext) -> str:
    """The full agent-reported outcome: changes, verification, plan, and summary.

    Report-term checks match equivalent wording anywhere in the report, not a
    specific field or exact spelling."""
    outcome = context.report.outcome
    parts = [*outcome.changes, *outcome.verification, context.report.summary]
    if outcome.plan:
        parts.append(json.dumps(outcome.plan, ensure_ascii=False, default=str))
    return normalize_report_term("\n".join(parts))


@dataclass(frozen=True, slots=True)
class ReportTermsVerifier(OutcomeVerifier):
    check_id: str
    required_terms: tuple[str, ...]

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        text = report_outcome_text(context)
        missing = tuple(term for term in self.required_terms if normalize_report_term(term) not in text)
        return OutcomeCheck(
            check_id=self.check_id,
            passed=not missing,
            expected={"required_terms": list(self.required_terms)},
            actual={"missing_terms": list(missing)},
            evidence=(*context.report.outcome.changes, *context.report.outcome.verification, context.report.summary),
        )


@dataclass(frozen=True, slots=True)
class InstanceConfigVerifier(OutcomeVerifier):
    check_id: str
    target: str
    expected: object
    predicate: Callable[[dict, object], bool]

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        payload = require_success_payload(
            context.case_run.env.manage_instance("get_config", self.target),
            f"outcome config query: target={self.target!r}",
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=self.predicate(payload, context.case_run.case),
            expected=self.expected,
            actual=payload,
            evidence=(f"manage_instance(get_config, {self.target})",),
        )


@dataclass(frozen=True, slots=True)
class MetricVerifier(OutcomeVerifier):
    check_id: str
    metric_type: str
    expected: object
    predicate: Callable[[dict, object], bool]

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        payload = require_success_payload(
            context.case_run.env.query_metrics(metric_type=self.metric_type),
            f"outcome metric query: metric_type={self.metric_type!r}",
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=self.predicate(payload, context.case_run.case),
            expected=self.expected,
            actual=payload,
            evidence=(f"query_metrics({self.metric_type})",),
        )


@dataclass(frozen=True, slots=True)
class InstanceActionVerifier(OutcomeVerifier):
    check_id: str
    action: str
    target: Callable[[object], str]
    expected: object
    predicate: Callable[[dict, object], bool]

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        target = self.target(context.case_run.case)
        payload = require_success_payload(
            context.case_run.env.manage_instance(self.action, target),
            f"outcome instance query: action={self.action!r}, target={target!r}",
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=self.predicate(payload, context.case_run.case),
            expected=self.expected,
            actual=payload,
            evidence=(f"manage_instance({self.action}, {target})",),
        )


def build_outcome_result(
    checks: tuple[OutcomeCheck, ...],
    report_fields_used: tuple[str, ...] = (),
    trusted_artifacts_used: tuple[str, ...] = (),
) -> dict[str, Any]:
    if not checks:
        raise ValueError("outcome verification requires at least one check")
    passed = all(check.passed for check in checks)
    return {
        "OutcomePass": passed,
        "checks": {check.check_id: check.as_dict() for check in checks},
        "report_fields_used": list(report_fields_used),
        "trusted_artifacts_used": list(trusted_artifacts_used),
    }
