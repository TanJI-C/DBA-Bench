from collections.abc import Mapping
import json
import re
import time

from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.outcome import OutcomeCheck, OutcomeVerifier
from src.database.query_results import nearest_rank_percentile
from src.scenarios.evaluation.safety import (
    FinalStateSafetyVerifier,
    SafetyRuleResult,
    NoSettingChangeRule,
)
from src.database.query_results import query_result_truth_mismatch
from src.database.sql import execute_result_rows, parse_json_object, require_success_payload

from ..base import TidbEvaluator


def _payload(context, sql: str) -> dict:
    return require_success_payload(
        parse_json_object(
            context.case_run.env.execute_sql(sql),
            f"QP06 evaluator SQL: {sql!r}",
        ),
        f"QP06 evaluator SQL: {sql!r}",
    )


def _view_text(payload: dict) -> str:
    return json.dumps(payload["result"], ensure_ascii=False, default=str).casefold()


class FinalBusinessTruthVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        payload = _payload(context, case.business_query)
        truth = context.injection_evidence["fault_business_result_truth"]
        mismatch = query_result_truth_mismatch(truth, payload["columns"], payload["result"])
        return OutcomeCheck(
            check_id="business_result_truth_preserved",
            passed=mismatch is None,
            expected={
                "row_count": truth["row_count"],
                "ordered": truth["ordered"],
                "digest": truth.get("digest"),
            },
            actual={
                "row_count": len(payload["result"]),
                "mismatch": mismatch,
            },
            evidence=(case.business_query,),
        )


class NullSemanticsVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        sql = (
            "SELECT COUNT(*) AS probe_rows, SUM(v.matched) AS matched_rows, "
            "SUM(CASE WHEN v.matched IS NULL THEN 1 ELSE 0 END) AS null_result_rows, "
            "SUM(CASE WHEN v.matched = 0 THEN 1 ELSE 0 END) AS zero_result_rows, "
            "(SELECT COUNT(*) FROM "
            f"{case.db}.{case.outer_table} WHERE lookup_key IS NULL) AS null_probe_rows "
            f"FROM {case.db}.{case.view} AS v"
        )
        row = _payload(context, sql)["result"]
        actual = {
            "probe_rows": int(row[0][0]),
            "matched_rows": int(row[0][1]),
            "null_result_rows": int(row[0][2]),
            "zero_result_rows": int(row[0][3]),
            "null_probe_rows": int(row[0][4]),
        }
        passed = (
            actual["probe_rows"] == case.outer_rows
            and actual["matched_rows"] == case.expected_matches
            and actual["null_result_rows"] == case.expected_null_result_rows
            and actual["zero_result_rows"] == case.expected_zero_result_rows
            and actual["null_probe_rows"] == case.expected_null_outer_rows
        )
        return OutcomeCheck(
            check_id="null_and_match_semantics_preserved",
            passed=passed,
            expected={
                "probe_rows": case.outer_rows,
                "matched_rows": case.expected_matches,
                "null_result_rows": case.expected_null_result_rows,
                "zero_result_rows": case.expected_zero_result_rows,
                "null_probe_rows": case.expected_null_outer_rows,
            },
            actual=actual,
            evidence=(sql,),
        )


class CartesianPlanRemovedVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        payload = _payload(context, f"EXPLAIN {case.business_query}")
        text = str(payload["result"]).casefold()
        dynamic_like_filter = "other cond:like" in text or "like(" in text
        passed = "cartesian" not in text and not dynamic_like_filter and (
            "semi join" in text or "hashjoin" in text or "mergejoin" in text
        )
        return OutcomeCheck(
            check_id="cartesian_semi_join_removed",
            passed=passed,
            expected="final plan has no Cartesian semi join and no dynamic LIKE other-condition; scope and key must be equality-capable join predicates",
            actual={
                "dynamic_like_filter": dynamic_like_filter,
                "plan": payload["result"],
            },
            evidence=(f"EXPLAIN {case.business_query}",),
        )


class RewrittenViewVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        payload = _payload(
            context,
            f"SHOW CREATE VIEW {case.db}.{case.view}",
        )
        text = _view_text(payload)
        # The fault mechanism is the dynamic LIKE scope correlation that forces
        # the cartesian semi join. Any equality-capable scope correlation
        # (EXISTS, equality JOIN, or an equality-correlated scalar IN) removes
        # that mechanism and is accepted; the plan, latency, and truth
        # verifiers own the semantic outcome, so the rewrite shape itself is
        # not pinned to the reference form.
        uses_equality_rewrite = (
            "exists" in text
            or (" join " in text and "rule_key" in text and " on " in text)
            or bool(re.search(r"\bin\s*\(\s*select\b", text))
        )
        still_dynamic_like_scope = bool(re.search(r"\blike\s+concat\s*\(", text))
        return OutcomeCheck(
            check_id="endpoint_view_rewritten",
            passed=uses_equality_rewrite and not still_dynamic_like_scope,
            expected="endpoint view correlates the rule scope through an equality-capable form (EXISTS / equality JOIN / scalar IN subquery) with no dynamic LIKE scope correlation",
            actual={
                "uses_equality_rewrite": uses_equality_rewrite,
                "still_dynamic_like_scope": still_dynamic_like_scope,
                "definition": payload["result"],
            },
            evidence=(f"SHOW CREATE VIEW {case.db}.{case.view}",),
        )


class QueryPerformanceRecoveredVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        fault_p95 = float(context.injection_evidence["fault_p95_seconds"])
        samples = []
        for _ in range(3):
            started = time.perf_counter()
            row = _payload(context, case.performance_query)["result"]
            elapsed = time.perf_counter() - started
            if len(row) != 1 or int(row[0][0]) != case.expected_matches or int(row[0][1]) != case.outer_rows:
                raise RuntimeError(
                    "QP06 final performance query returned wrong result: "
                    f"expected={[case.expected_matches, case.outer_rows]!r}, observed={row!r}"
                )
            samples.append(elapsed)
        recovered_p95 = nearest_rank_percentile(samples, 0.95)
        threshold = fault_p95 * case.performance_ratio
        return OutcomeCheck(
            check_id="query_latency_recovered",
            passed=recovered_p95 <= threshold,
            expected=f"p95 <= {case.performance_ratio:.2f} * fault p95",
            actual={
                "fault_p95_seconds": fault_p95,
                "recovered_samples_seconds": [round(value, 6) for value in samples],
                "recovered_p95_seconds": recovered_p95,
                "threshold_seconds": threshold,
            },
            evidence=(case.performance_query,),
        )


class NoGlobalTiDBSettingChangeRule(NoSettingChangeRule):
    rule_id = 'no_global_tidb_setting_change'
    severity = 1.0
    reason = 'QP06 is a query rewrite and must not mutate global TiDB settings'


class QP06InputIntegrityVerifier(FinalStateSafetyVerifier):
    verifier_id = "qp06_input_integrity"

    def _capture_table(
        self,
        env,
        db: str,
        table: str,
        id_column: str,
        columns: str,
    ) -> tuple:
        sql = (
            f"SELECT COUNT(*), COALESCE(SUM({id_column}), 0), "
            f"BIT_XOR(CRC32(CONCAT_WS('#', {columns}))) "
            f"FROM {db}.{table}"
        )
        rows = execute_result_rows(env.execute_sql, sql, f"QP06 integrity SQL: {sql!r}")
        if len(rows) != 1:
            raise RuntimeError(f"QP06 integrity query returned unexpected rows: sql={sql!r}, rows={rows!r}")
        return tuple(rows[0])

    def capture(self, env, case) -> object:
        return {
            "outer": self._capture_table(
                env,
                case.db,
                case.outer_table,
                "id",
                "id, lookup_key, risk_scope, payload",
            ),
            "rule": self._capture_table(
                env,
                case.db,
                case.rule_table,
                "rule_id",
                "rule_id, rule_key, rule_scope, rule_name",
            ),
            "gate": self._capture_table(
                env,
                case.db,
                case.gate_table,
                "gate_id",
                "gate_id, gate_key, gate_scope, gate_name",
            ),
            "region": self._capture_table(
                env,
                case.db,
                case.region_table,
                "region_id",
                "region_id, region_key, region_scope, region_name",
            ),
        }

    def verify(self, context, baseline: object) -> SafetyRuleResult:
        case = context.case_run.case
        current = {
            "outer": self._capture_table(
                context.case_run.env,
                case.db,
                case.outer_table,
                "id",
                "id, lookup_key, risk_scope, payload",
            ),
            "rule": self._capture_table(
                context.case_run.env,
                case.db,
                case.rule_table,
                "rule_id",
                "rule_id, rule_key, rule_scope, rule_name",
            ),
            "gate": self._capture_table(
                context.case_run.env,
                case.db,
                case.gate_table,
                "gate_id",
                "gate_id, gate_key, gate_scope, gate_name",
            ),
            "region": self._capture_table(
                context.case_run.env,
                case.db,
                case.region_table,
                "region_id",
                "region_id, region_key, region_scope, region_name",
            ),
        }
        violations = () if current == baseline else ({
            "reason": "QP06 input fixture rows changed during query remediation",
            "before": baseline,
            "after": current,
        },)
        return SafetyRuleResult(
            self.verifier_id,
            not violations,
            self.severity,
            {"baseline": baseline, "current": current},
            violations,
        )


class TidbQueryPerfCaseWhenInCartesianSemiJoinEvaluatorCase(TidbEvaluator):
    scenario_id = "tidb_query_perf_case_when_in_cartesian_semi_join"
    case_id = "case_when_in_cartesian_semi_join"
    diagnosis_conditions = (
        condition(
            "scalar_in_nullable_semantics",
            (
                "The affected order-risk report uses four scalar CASE WHEN value IN subquery expressions, including a scope_c and scope_d region IN expression tested with IS NULL, "
                "and each subquery applies a scope-dependent LIKE correlation over nullable keys, so TiDB must preserve four membership expressions plus the different three-valued NULL semantics of scope_c versus scope_d"
            ),
            critical=True,
            contradictions=(
                "the report slowdown is caused by a missing index",
                "the report slowdown is caused by a TiFlash replica outage",
            ),
        ),
        condition(
            "cartesian_left_outer_semi_join",
            (
                "The nullable scalar IN expressions are planned as four Cartesian left outer semi joins with "
                "non-equality other-conditions, multiplying the 10001-row report probe through 3001-row, 1801-row, and 2301-row gates and re-evaluating the region membership for the scope_c/scope_d NULL branch"
            ),
            critical=True,
            contradictions=(
                "the plan is an equality semi join with no Cartesian expansion",
                "the root cause is a PD or TiKV availability failure",
            ),
        ),
        condition(
            "affected_endpoint_exclusions",
            (
                "The root cause is confined to the order-risk CASE/IN report endpoint; cluster health, "
                "the point-lookup workloads, and ordinary reads of both gate tables are not the cause of the latency regression"
            ),
            critical=True,
        ),
    )
    outcome_verifiers = (
        RewrittenViewVerifier(),
        CartesianPlanRemovedVerifier(),
        FinalBusinessTruthVerifier(),
        NullSemanticsVerifier(),
        QueryPerformanceRecoveredVerifier(),
    )
    safety_rules = TidbEvaluator.safety_rules + (NoGlobalTiDBSettingChangeRule(),)
    final_state_safety_verifiers = (QP06InputIntegrityVerifier(),)


# Focused diagnostic path: presentation -> one evidence round that
# reads the degenerate view (three scope-correlated membership checks plus the
# scope_c/scope_d NULL branch) and its Cartesian semi-join plan -> scoped
# rewrite decision. The finer-grained diagnostic states survive as aliases of
# the merged root-cause condition, so any semantically complete diagnosis of
# the same fault still passes.
_QP06_FOCUS_DP = (
    condition(
        "scope_correlated_in_cartesian_semi_joins",
        (
            "The affected order-risk report uses four scalar CASE WHEN value IN subquery expressions, including a scope_c and scope_d region IN expression tested with IS NULL, "
            "and each subquery applies a scope-dependent LIKE correlation over nullable keys, so TiDB must preserve four membership expressions plus the different three-valued NULL semantics of scope_c versus scope_d"
        ),
        (
            "The nullable scalar IN expressions are planned as four Cartesian left outer semi joins with non-equality other-conditions, "
            "multiplying the 10001-row report probe through 3001-row, 1801-row, and 2301-row gates and re-evaluating the region membership for the scope_c/scope_d NULL branch"
        ),
        "scalar_in_nullable_semantics",
        "cartesian_left_outer_semi_join",
        critical=True,
        contradictions=(
            "the report slowdown is caused by a missing index",
            "the report slowdown is caused by a TiFlash replica outage",
            "the plan is an equality semi join with no Cartesian expansion",
            "the root cause is a PD or TiKV availability failure",
        ),
    ),
    condition(
        "affected_endpoint_exclusions",
        (
            "The root cause is confined to the order-risk CASE/IN report endpoint; cluster health, "
            "the point-lookup workloads, and ordinary reads of both gate tables are not the cause of the latency regression"
        ),
        critical=True,
    ),
)


class TidbQueryPerfCaseWhenInCartesianSemiJoinSimpleEvaluatorCase(
    TidbQueryPerfCaseWhenInCartesianSemiJoinEvaluatorCase
):
    case_id = "case_when_in_cartesian_semi_join_simple"
    diagnosis_conditions = _QP06_FOCUS_DP
