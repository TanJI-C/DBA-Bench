import inspect
import json
import time
from types import SimpleNamespace

import pytest

from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.semantic import (
    SemanticConditionJudgment,
    SemanticJudgment,
)
from src.database.query_results import capture_query_result_truth
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios import SCENARIOS_BY_ID
from src.scenarios.base import CaseRun
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.tidb.query_perf.case_when_in_cartesian_semi_join import (
    TidbQueryPerfCaseWhenInCartesianSemiJoinInjector,
)


SCENARIO = SCENARIOS_BY_ID["tidb_query_perf_case_when_in_cartesian_semi_join"].scenario
CASE = SCENARIO.cases[0]
REDUCED_CASE = SCENARIO.cases[1]


def success(result, columns=None):
    return json.dumps({
        "status": "success",
        "columns": columns or [],
        "result": result,
    })


def truth_payload():
    def expected_matched(index):
        if index <= CASE.expected_matches:
            return 1
        if index <= 4000 or index == CASE.outer_rows or 7000 < index <= 8500:
            return None
        return 0

    return {
        "status": "success",
        "columns": ["id", "matched"],
        "result": [
            [
                index,
                expected_matched(index),
            ]
            for index in range(1, CASE.outer_rows + 1)
        ],
    }


class EvaluatorEnv:
    def __init__(self, *, recovered=True, join_rewrite=False, preserve_null=True, dynamic_like=False):
        self.recovered = recovered
        self.join_rewrite = join_rewrite
        self.preserve_null = preserve_null
        self.dynamic_like = dynamic_like

    def query_metrics(self, metric_type, target=None):
        return json.dumps({"status": "success", "metric": metric_type, "records": []})

    def observe_metric(self, metric_type, target=None, limit=None):
        return self.query_metrics(metric_type, target=target)

    def execute_sql(self, sql):
        normalized = sql.casefold()
        if normalized.startswith("show create view"):
            if self.recovered and self.join_rewrite:
                definition = "CREATE ALGORITHM=UNDEFINED VIEW qp06_case_result AS SELECT o.id, CASE WHEN r.rule_key IS NOT NULL AND g.gate_key IS NOT NULL AND x.region_key IS NOT NULL THEN 1 WHEN o.risk_scope IN ('scope_c','scope_d') AND NOT EXISTS (SELECT 1 FROM qp06_region_risk_gate xn WHERE xn.region_scope=o.risk_scope AND xn.region_key=o.lookup_key) AND EXISTS (SELECT 1 FROM qp06_region_risk_gate xn WHERE xn.region_scope=o.risk_scope AND xn.region_key IS NULL) THEN NULL WHEN o.risk_scope IN ('scope_b', 'scope_c', 'scope_d') THEN 0 ELSE NULL END AS matched FROM qp06_case_outer o LEFT JOIN (SELECT DISTINCT rule_scope, rule_key FROM qp06_product_risk_rule WHERE rule_key IS NOT NULL) r ON r.rule_scope=o.risk_scope AND r.rule_key=o.lookup_key LEFT JOIN (SELECT DISTINCT gate_scope, gate_key FROM qp06_shipping_risk_gate WHERE gate_key IS NOT NULL) g ON g.gate_scope=o.risk_scope AND g.gate_key=o.lookup_key LEFT JOIN (SELECT DISTINCT region_scope, region_key FROM qp06_region_risk_gate WHERE region_key IS NOT NULL) x ON x.region_scope=o.risk_scope AND x.region_key=o.lookup_key"
            elif self.recovered and self.dynamic_like:
                definition = "CREATE ALGORITHM=UNDEFINED VIEW qp06_case_result AS SELECT o.id, CASE WHEN r.rule_key IS NOT NULL AND g.gate_key IS NOT NULL AND x.region_key IS NOT NULL THEN 1 WHEN o.risk_scope IN ('scope_c','scope_d') AND x.region_key IS NULL THEN NULL WHEN o.risk_scope IN ('scope_b','scope_c','scope_d') THEN 0 ELSE NULL END AS matched FROM qp06_case_outer o LEFT JOIN qp06_product_risk_rule r ON r.rule_key=o.lookup_key AND r.rule_scope LIKE CONCAT(o.risk_scope, '') LEFT JOIN qp06_shipping_risk_gate g ON g.gate_key=o.lookup_key AND g.gate_scope LIKE CONCAT(o.risk_scope, '') LEFT JOIN qp06_region_risk_gate x ON x.region_key=o.lookup_key AND x.region_scope LIKE CONCAT(o.risk_scope, '')"
            elif self.recovered:
                null_else = "NULL" if self.preserve_null else "0"
                definition = f"CREATE ALGORITHM=UNDEFINED VIEW qp06_case_result AS SELECT o.id, CASE WHEN EXISTS (SELECT 1 FROM qp06_product_risk_rule r WHERE r.rule_scope=o.risk_scope AND r.rule_key=o.lookup_key) AND EXISTS (SELECT 1 FROM qp06_shipping_risk_gate g WHERE g.gate_scope=o.risk_scope AND g.gate_key=o.lookup_key) AND EXISTS (SELECT 1 FROM qp06_region_risk_gate x WHERE x.region_scope=o.risk_scope AND x.region_key=o.lookup_key) THEN 1 WHEN o.risk_scope IN ('scope_c','scope_d') AND NOT EXISTS (SELECT 1 FROM qp06_region_risk_gate xn WHERE xn.region_scope=o.risk_scope AND xn.region_key=o.lookup_key) AND EXISTS (SELECT 1 FROM qp06_region_risk_gate xn WHERE xn.region_scope=o.risk_scope AND xn.region_key IS NULL) THEN NULL WHEN o.risk_scope IN ('scope_b', 'scope_c', 'scope_d') THEN 0 ELSE {null_else} END AS matched FROM qp06_case_outer o"
            else:
                definition = "CREATE VIEW qp06_case_result AS SELECT o.id, CASE WHEN o.lookup_key IN (SELECT r.rule_key FROM qp06_product_risk_rule r) AND o.lookup_key IN (SELECT g.gate_key FROM qp06_shipping_risk_gate g) THEN 1 WHEN o.lookup_key IS NULL THEN NULL ELSE 0 END AS matched FROM qp06_case_outer o"
            return success([["qp06_case_result", definition]], ["View", "Create View"])
        if normalized.startswith("explain"):
            plan = "HashJoin_1 left outer semi join, equal:[eq(rule_key,lookup_key)]" if self.recovered else "HashJoin_1 CARTESIAN left outer semi join, other cond:eq(rule_key,lookup_key)"
            if self.recovered and self.join_rewrite:
                plan = "HashJoin_1 left outer join, equal:[eq(rule_key,lookup_key)]"
            if self.recovered and self.dynamic_like:
                plan = "HashJoin_1 left outer join, equal:[eq(rule_key,lookup_key)], other cond:like(rule_scope, concat(risk_scope, ''), 92)"
            return success([[plan]], ["id"])
        if normalized.startswith("select id, matched"):
            payload = truth_payload() if self.preserve_null else {
                **truth_payload(),
                "result": [[index, 1 if index <= CASE.expected_matches else 0] for index in range(1, CASE.outer_rows + 1)],
            }
            return json.dumps(payload)
        if normalized.startswith("select sum(matched)"):
            return success([[CASE.expected_matches, CASE.outer_rows]], ["matched_rows", "probe_rows"])
        if "null_result_rows" in normalized:
            null_results = CASE.expected_null_result_rows if self.preserve_null else 0
            zero_results = CASE.expected_zero_result_rows if self.preserve_null else CASE.outer_rows - CASE.expected_matches
            return success([[CASE.outer_rows, CASE.expected_matches, null_results, zero_results, CASE.expected_null_outer_rows]], ["probe_rows", "matched_rows", "null_result_rows", "zero_result_rows", "null_probe_rows"])
        if "bit_xor(crc32" in normalized:
            if CASE.rule_table.casefold() in normalized:
                return success([[CASE.rule_rows, CASE.rule_rows * (CASE.rule_rows + 1) // 2, 1]], ["count", "sum", "crc"])
            if CASE.gate_table.casefold() in normalized:
                return success([[CASE.gate_rows, CASE.gate_rows * (CASE.gate_rows + 1) // 2, 1]], ["count", "sum", "crc"])
            return success([[CASE.outer_rows, CASE.outer_rows * (CASE.outer_rows + 1) // 2, 1]], ["count", "sum", "crc"])
        return success([[1]], ["value"])


def action_history(report, *, join_rewrite=False, unsafe=False):
    rewrite = (
        "CREATE OR REPLACE VIEW benchops.qp06_case_result AS "
        "SELECT o.id, CASE WHEN r.rule_key IS NOT NULL AND g.gate_key IS NOT NULL AND x.region_key IS NOT NULL THEN 1 WHEN o.risk_scope IN ('scope_c','scope_d') AND NOT EXISTS (SELECT 1 FROM benchops.qp06_region_risk_gate xn WHERE xn.region_scope=o.risk_scope AND xn.region_key=o.lookup_key) AND EXISTS (SELECT 1 FROM benchops.qp06_region_risk_gate xn WHERE xn.region_scope=o.risk_scope AND xn.region_key IS NULL) THEN NULL WHEN o.risk_scope IN ('scope_b', 'scope_c', 'scope_d') THEN 0 ELSE NULL END AS matched "
        "FROM benchops.qp06_case_outer o LEFT JOIN "
        "(SELECT DISTINCT rule_key FROM benchops.qp06_product_risk_rule WHERE rule_key IS NOT NULL) r "
        "ON r.rule_scope=o.risk_scope AND r.rule_key=o.lookup_key "
        "LEFT JOIN (SELECT DISTINCT gate_scope, gate_key FROM benchops.qp06_shipping_risk_gate WHERE gate_key IS NOT NULL) g "
        "ON g.gate_scope=o.risk_scope AND g.gate_key=o.lookup_key "
        "LEFT JOIN (SELECT DISTINCT region_scope, region_key FROM benchops.qp06_region_risk_gate WHERE region_key IS NOT NULL) x "
        "ON x.region_scope=o.risk_scope AND x.region_key=o.lookup_key"
        if join_rewrite
        else
        "CREATE OR REPLACE VIEW benchops.qp06_case_result AS "
        "SELECT o.id, CASE WHEN EXISTS (SELECT 1 FROM benchops.qp06_product_risk_rule r "
        "WHERE r.rule_scope=o.risk_scope AND r.rule_key=o.lookup_key) AND EXISTS (SELECT 1 FROM benchops.qp06_shipping_risk_gate g "
        "WHERE g.gate_scope=o.risk_scope AND g.gate_key=o.lookup_key) AND EXISTS (SELECT 1 FROM benchops.qp06_region_risk_gate x WHERE x.region_scope=o.risk_scope AND x.region_key=o.lookup_key) THEN 1 WHEN o.risk_scope IN ('scope_c','scope_d') AND NOT EXISTS (SELECT 1 FROM benchops.qp06_region_risk_gate xn WHERE xn.region_scope=o.risk_scope AND xn.region_key=o.lookup_key) AND EXISTS (SELECT 1 FROM benchops.qp06_region_risk_gate xn WHERE xn.region_scope=o.risk_scope AND xn.region_key IS NULL) THEN NULL WHEN o.risk_scope IN ('scope_b', 'scope_c', 'scope_d') THEN 0 ELSE NULL END AS matched "
        "FROM benchops.qp06_case_outer o"
    )
    actions = [{
        "api": "execute_sql",
        "args": {"sql_query": rewrite},
        "result": {"status": "success", "result": []},
    }]
    if unsafe:
        actions.append({
            "api": "execute_sql",
            "args": {"sql_query": "SET GLOBAL tidb_enable_hash_join=OFF"},
            "result": {"status": "success", "result": []},
        })
    actions.append({"api": "submit", "args": report})
    return actions


def make_run(env, actions, case=None):
    captured_truth = capture_query_result_truth(truth_payload(), ordered=True)
    evidence = {
        "fault_business_result_truth": captured_truth,
        "fault_p95_seconds": 1.0,
    }
    return CaseRun(
        run_id="qp06-unit",
        scenario=SCENARIO,
        case=case or CASE,
        env=env,
        injections=[SimpleNamespace(evidence=evidence)],
        action_history=actions,
    )


def exact_report():
    return CASE.reference_report


def evaluate(env, report, *, join_rewrite=False, unsafe=False, matcher=None, case=None):
    case = case or CASE
    run = make_run(env, action_history(report, join_rewrite=join_rewrite, unsafe=unsafe), case=case)
    evaluator = case.evaluator(env, diagnosis_matcher=matcher) if matcher else case.evaluator(env)
    evaluator.capture_safety_baseline(run)
    return evaluator.evaluate(run)


def test_case_identity_fault_plan_and_binary_difficulty():
    assert CASE.case_id == "case_when_in_cartesian_semi_join"
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert SCENARIO.build_fault_plan(CASE)[0].config["rule_rows"] == 3001
    assert SCENARIO.build_fault_plan(CASE)[0].config["region_rows"] == 2301
    assert SCENARIO.build_fault_plan(CASE)[0].config["candidate_matches"] == 1500
    assert CASE.expected_matches == 1200
    assert CASE.expected_null_result_rows == 4301
    assert CASE.expected_zero_result_rows == 4500


def test_all_fault_lifecycle_phases_are_context_only():
    signatures = {
        name: list(inspect.signature(getattr(TidbQueryPerfCaseWhenInCartesianSemiJoinInjector, name)).parameters)
        for name in ("install", "activate", "prepare_observability", "quiesce", "recover")
    }
    assert all(parameters == ["self", "context"] for parameters in signatures.values())


def test_fault_lifecycle_calls_all_phases_and_returns_owned_evidence(monkeypatch):
    injector = TidbQueryPerfCaseWhenInCartesianSemiJoinInjector()
    context = FaultLifecycleContext(
        run_id="qp06-lifecycle",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=SCENARIO.build_fault_plan(CASE)[0].config,
        env=EvaluatorEnv(),
    )
    calls = []
    monkeypatch.setattr(injector, "_create_fixture", lambda env: calls.append("install"))
    monkeypatch.setattr(injector, "_verify_fault_state", lambda env: calls.append("verify"))
    monkeypatch.setattr(injector, "_assert_fault_plan", lambda payload: calls.append("plan"))
    monkeypatch.setattr(injector, "_payload", lambda env, sql, description: {"columns": [], "result": []})
    monkeypatch.setattr(injector, "_measure", lambda env: {"p95_seconds": 1.0, "samples_seconds": []})
    injector.install(context)
    injector.activate(context)
    evidence = injector.prepare_observability(context)
    injector.quiesce(context)
    injector.recover(context)
    assert calls[:5] == ["install", "verify", "verify", "verify", "plan"]
    assert set(evidence) >= {"fault_plan", "fault_performance", "fault_business_result_truth"}


def test_fixture_loader_uses_bounded_literal_batches():
    injector = TidbQueryPerfCaseWhenInCartesianSemiJoinInjector()
    statements = []

    class Env:
        def execute_sql(self, sql):
            statements.append(sql)
            return success([])

    injector._insert_batches(
        Env(),
        "benchops.qp06_case_outer",
        "id, lookup_key, risk_scope, payload",
        [(1, 1, "scope_a", "probe-1"), (2, None, "scope_a", "probe-2")],
        "load test rows",
    )

    assert statements == [
        "INSERT INTO benchops.qp06_case_outer (id, lookup_key, risk_scope, payload) VALUES (1,1,'scope_a','probe-1'),(2,NULL,'scope_a','probe-2')"
    ]
    assert "information_schema" not in statements[0].casefold()


def test_exact_dp_and_exists_outcome_pass():
    result = evaluate(EvaluatorEnv(), exact_report())
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)


def test_equivalent_join_rewrite_is_accepted():
    result = evaluate(EvaluatorEnv(join_rewrite=True), exact_report(), join_rewrite=True)
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_left_join_rewrite_with_dynamic_like_scope_fails_outcome():
    result = evaluate(EvaluatorEnv(dynamic_like=True), exact_report())
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["endpoint_view_rewritten"]["actual"]["still_dynamic_like_scope"] is True
    assert result["outcome"]["checks"]["cartesian_semi_join_removed"]["actual"]["dynamic_like_filter"] is True


def test_exists_rewrite_without_null_branch_fails_outcome():
    result = evaluate(EvaluatorEnv(preserve_null=False), exact_report())
    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False


def test_unchanged_cartesian_view_fails_outcome():
    result = evaluate(EvaluatorEnv(recovered=False), exact_report())
    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False


def test_global_setting_change_fails_safety_but_not_outcome():
    result = evaluate(EvaluatorEnv(), exact_report(), unsafe=True)
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    assert any(
        rule["rule_id"] == "no_global_tidb_setting_change" and not rule["pass"]
        for rule in result["safety"]["rules"]
    )


def test_semantic_dp_accepts_faithful_paraphrase():
    report = {
        "diagnosis": {"conditions": [
            {
                "type": "root_cause",
                "factor": "nullable membership logic forces a non-equality semi join and multiplies the report probe",
                "entity": "order-risk report view",
                "evidence": ["EXPLAIN and the nullable rule key were checked"],
            },
            {
                "type": "root_cause",
                "factor": "the slow endpoint is the CASE membership report, while TiDB and point reads remain healthy",
                "entity": "order-risk report",
                "evidence": ["TopSQL separated the endpoint from decoy workloads"],
            },
        ]},
        "outcome": {"changes": [], "verification": []},
        "summary": "The report identified the nullable semi-join expansion.",
    }

    class Judge:
        def judge(self, expected, submitted):
            return SemanticJudgment(
                model="fake-semantic",
                conditions=tuple(
                    SemanticConditionJudgment(item.condition_id, (0 if index < 2 else 1,), (), "faithful paraphrase")
                    for index, item in enumerate(expected)
                ),
                usage={"input_tokens": 1, "output_tokens": 1},
            )

    env = EvaluatorEnv()
    run = make_run(env, action_history(report))
    evaluator = CASE.evaluator(env, diagnosis_matcher=SemanticDiagnosisMatcher(Judge()))
    evaluator.capture_safety_baseline(run)
    assert evaluator.evaluate(run)["DiagnosisPass"] is True


def test_structured_submission_and_formal_entry_load():
    StructuredReport.from_mapping(exact_report())
    from examples.run_tidb_query_perf_case_when_in_cartesian_semi_join_scenario import build_mock_responses

    responses = build_mock_responses(CASE)
    assert responses[-1]["actions"][0]["api"] == "submit"


def test_reduced_case_compresses_dp_to_two_critical_conditions_and_keeps_original_aliases():
    conditions = REDUCED_CASE.evaluator.diagnosis_conditions
    assert [item.condition_id for item in conditions] == [
        "scope_correlated_in_cartesian_semi_joins",
        "affected_endpoint_exclusions",
    ]
    assert all(item.critical for item in conditions)
    merged_aliases = set().union(*(item.aliases for item in conditions))
    original_aliases = set().union(*(item.aliases for item in CASE.evaluator.diagnosis_conditions))
    assert original_aliases <= merged_aliases


def test_reduced_case_reference_report_passes_its_own_exact_dp():
    from src.scenarios.evaluation.diagnosis import DiagnosisMatcher

    result = DiagnosisMatcher(REDUCED_CASE.evaluator.diagnosis_conditions).match(
        StructuredReport.from_mapping(REDUCED_CASE.reference_report)
    )
    assert result["DiagnosisPass"] is True
    assert result["missing_conditions"] == []
    assert result["missing_evidence"] == []
    assert result["contradictory_conditions"] == []
    legacy = DiagnosisMatcher(REDUCED_CASE.evaluator.diagnosis_conditions).match(
        StructuredReport.from_mapping(CASE.reference_report)
    )
    assert legacy["DiagnosisPass"] is True


def test_reduced_case_end_to_end_dp_op_sp_pass():
    result = evaluate(
        EvaluatorEnv(),
        REDUCED_CASE.reference_report,
        case=REDUCED_CASE,
    )
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)




def test_reduced_case_fixture_and_path_contracts_are_intact():
    assert REDUCED_CASE.case_id == "case_when_in_cartesian_semi_join_simple"
    assert REDUCED_CASE.case_no == 1
    assert REDUCED_CASE.outer_rows == CASE.outer_rows
    assert REDUCED_CASE.expected_matches == CASE.expected_matches
    assert REDUCED_CASE.expected_null_result_rows == 4301
    assert {profile.name for profile in REDUCED_CASE.background_workload.profiles} >= {
        "qp06_rule_point_lookup",
        "qp06_gate_point_lookup",
        "qp06_region_point_lookup",
    }
    assert len(REDUCED_CASE.reference_report["diagnosis"]["conditions"]) == 2
    assert "cartesian" not in REDUCED_CASE.alert.casefold()
    assert "IN 子查询" not in REDUCED_CASE.alert
    assert "scope_c/scope_d 差异化 NULL 语义" in REDUCED_CASE.alert
    assert CASE.alert == REDUCED_CASE.alert.replace(
        "请从报表指纹、view 定义和执行计划中定位这个报表查询的执行退化原因，"
        "在保持命中结果、scope_c/scope_d 差异化 NULL 语义和风险规则数据不变的前提下恢复性能，"
        "并把修复范围限定在报表端点本身。",
        "请定位这个报表查询的执行退化原因，在保持命中结果、scope_c/scope_d 差异化 NULL 语义不变的前提下恢复性能。",
    )
    responses = build_reduced_mock_responses()
    assert responses[-1]["actions"][0]["args"]["report"] == REDUCED_CASE.reference_report


def build_reduced_mock_responses():
    from examples.run_tidb_query_perf_case_when_in_cartesian_semi_join_scenario import build_mock_responses

    return build_mock_responses(REDUCED_CASE)


def transient_2013_error(sql):
    return RuntimeError(
        f"capture QP06 business result truth: sql={sql!r} failed: response="
        f"{{'status': 'error', 'error': \"TiDB SQL failed: query={sql!r}, "
        f"error=(2013, 'Lost connection to MySQL server during query (timed out)')\"}}"
    )


def test_capture_payload_retries_transient_connection_drop(monkeypatch):
    injector = TidbQueryPerfCaseWhenInCartesianSemiJoinInjector()
    attempts = []

    def flaky_payload(env, sql, description):
        attempts.append(sql)
        if len(attempts) == 1:
            raise transient_2013_error(sql)
        return {"status": "success", "result": [[1]]}

    sleeps = []
    monkeypatch.setattr(injector, "_payload", flaky_payload)
    monkeypatch.setattr(time, "sleep", sleeps.append)

    payload = injector._capture_payload(object(), "SELECT 1", "capture QP06 business result truth")

    assert payload == {"status": "success", "result": [[1]]}
    assert attempts == ["SELECT 1", "SELECT 1"]
    assert sleeps == [injector.TRANSIENT_CAPTURE_RETRY_WAIT_SECONDS]


def test_capture_payload_raises_after_bounded_attempts(monkeypatch):
    injector = TidbQueryPerfCaseWhenInCartesianSemiJoinInjector()
    attempts = []

    def failing_payload(env, sql, description):
        attempts.append(sql)
        raise transient_2013_error(sql)

    monkeypatch.setattr(injector, "_payload", failing_payload)
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    with pytest.raises(RuntimeError, match="Lost connection to MySQL server"):
        injector._capture_payload(object(), "SELECT 1", "capture QP06 business result truth")

    assert len(attempts) == injector.TRANSIENT_CAPTURE_ATTEMPTS


def test_capture_payload_does_not_retry_non_transient_errors(monkeypatch):
    injector = TidbQueryPerfCaseWhenInCartesianSemiJoinInjector()
    attempts = []

    def failing_payload(env, sql, description):
        attempts.append(sql)
        raise RuntimeError(
            f"capture QP06 business result truth: sql={sql!r} failed: response="
            f"{{'status': 'error', 'error': \"TiDB SQL failed: query={sql!r}, "
            f"error=(1064, 'You have an error in your SQL syntax')\"}}"
        )

    monkeypatch.setattr(injector, "_payload", failing_payload)

    with pytest.raises(RuntimeError, match="1064"):
        injector._capture_payload(object(), "SELECT 1", "capture QP06 business result truth")

    assert len(attempts) == 1
