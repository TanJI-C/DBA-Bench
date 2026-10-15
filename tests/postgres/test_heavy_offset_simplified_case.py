from src.scenarios.postgres.query_perf import PgQueryPerfHeavyOffsetPaginationScenario
from src.scenarios.evaluation.postgres.query_perf import (
    PgQueryPerfHeavyOffsetPaginationForBranchOrderShallowOffsetEvaluatorCase,
)


def test_shallow_offset_case_contract_and_identity():
    scenario = PgQueryPerfHeavyOffsetPaginationScenario()
    assert [case.case_no for case in scenario.cases] == list(range(len(scenario.cases)))
    case = scenario.get_case("branch_order_shallow_offset")
    assert case.evaluator is PgQueryPerfHeavyOffsetPaginationForBranchOrderShallowOffsetEvaluatorCase
    assert case.offset_value == 10000
    assert "ROW_NUMBER()" in case.fault_fingerprint_sql


def test_shallow_offset_alert_does_not_leak_fault_or_repair():
    scenario = PgQueryPerfHeavyOffsetPaginationScenario()
    case = scenario.get_case("branch_order_shallow_offset")
    alert = case.alert
    assert "ROW_NUMBER" not in alert
    assert "row_number" not in alert
    assert "rn BETWEEN" not in alert
    assert "OFFSET" not in alert
    assert "keyset" not in alert.lower()
    assert "seek" not in alert.lower()
    assert "SELECT" not in alert
    assert "branch_order_line" not in alert


def test_shallow_offset_fault_plan_uses_case_specific_offset():
    scenario = PgQueryPerfHeavyOffsetPaginationScenario()
    case = scenario.get_case("branch_order_shallow_offset")
    plan = scenario.build_fault_plan(case)[0]
    assert plan.config["offset_value"] == 10000
    assert plan.config["table"] == "branch_order_line"


def test_shallow_offset_evaluator_owns_distinct_diagnosis_conditions():
    scenario = PgQueryPerfHeavyOffsetPaginationScenario()
    shallow = scenario.get_case("branch_order_shallow_offset")
    deep = scenario.get_case("branch_order_deep_offset")
    assert (
        shallow.evaluator.diagnosis_conditions
        is not deep.evaluator.diagnosis_conditions
    )
    shallow_aliases = {
        alias
        for expected in shallow.evaluator.diagnosis_conditions
        for alias in expected.aliases
    }
    assert "row number window" in shallow_aliases
    assert "cost grows with page depth" in shallow_aliases
    assert "late page" in shallow_aliases
