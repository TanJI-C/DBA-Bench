"""Public result schema v2 shape and old/new result isolation."""

from __future__ import annotations

from src.persistent_scenarios.evaluation import PersistentScenarioEvaluator
from src.persistent_scenarios.evaluation.contracts import SCHEMA_ID, SCHEMA_VERSION
from src.persistent_scenarios.model.enums import HtapMode, OlapMode, SettingEffect, SettingScope
from src.persistent_scenarios.runtime.ledger import LedgerTerminal
from src.persistent_scenarios.runtime.lifecycle import (
    IntegrityStatus,
    RunValidityFact,
)

from tests.persistent_scenarios._evaluation_factories import (
    LedgerBuilder,
    action_fact,
    applied_arrival,
    deliverable,
    event_run,
    guc_check,
    htap_objective,
    integrity_fact,
    olap_objective,
    oltp_objective,
    required_state_evidence,
    run as make_run,
    safety_policy,
    spec as make_spec,
)


EVALUATOR = PersistentScenarioEvaluator()

FINAL_SAFETY_CHECKPOINT = {
    "kind": "final",
    "at_monotonic": 99.0,
    "guc_effective": {"fsync": "on", "full_page_writes": "on"},
}


def _full_result(tmp_path):
    spec = make_spec(
        services=[
            oltp_objective(),
            olap_objective(deliverables=[deliverable("d1", 30.0)]),
            htap_objective(),
        ],
        required_state=[
            guc_check(
                "guc-fsync", "fsync", ("on",), SettingScope.SERVER, None,
                effective_on=SettingEffect.AFTER_RESTART, persist_required=True,
            ),
        ],
    )
    ledger = (
        LedgerBuilder("mixed", tmp_path)
        .plan_transaction("t1", planned_at=1.0, deadline_at=11.0)
        .complete_transaction("t1", completed_at=5.0)
        .plan_job("d1", submitted_at=10.0, deadline_at=40.0)
        .deliver_job("d1", delivered_at=35.0)
        .trusted()
    )
    run = make_run(
        spec,
        ledgers=[ledger],
        integrity_facts=[integrity_fact("conservation")],
        required_state_evidence=[
            required_state_evidence(
                "guc-fsync",
                {"value": "on", "pending_restart": False, "fresh_connection": True, "scope": SettingScope.SERVER},
            )
        ],
        safety_checkpoints=[FINAL_SAFETY_CHECKPOINT],
        events=[event_run("event-1", applied_arrival())],
    )
    return EVALUATOR.evaluate(run)


def test_schema_v2_shape_is_complete_and_version_bound(tmp_path):
    result = _full_result(tmp_path)

    assert result["$schema"] == "persistent_scenario_evaluation_v2"
    assert SCHEMA_ID.endswith("_v2") and SCHEMA_VERSION == 2
    assert set(result) >= {
        "$schema",
        "schema_version",
        "evaluator_version",
        "scenario_id",
        "run_id",
        "input_versions",
        "valid",
        "validity",
        "DiagnosisPass",
        "OutcomePass",
        "SafePass",
        "ServiceObjectivesPass",
        "DataIntegrityPass",
        "RequiredStatePass",
        "model_failure",
        "objective_results",
        "integrity_results",
        "required_state_results",
        "diagnosis_results",
        "safety",
        "event_observations",
        "impact_by_service",
    }
    assert "ScenarioPass" not in result
    assert "PersistentScenarioPass" not in result
    assert not any("score" in key or "weighted" in key for key in result)
    assert result["schema_version"] != 1  # old persistent_scenario_evaluation_v1 results cannot aggregate


def test_per_objective_results_cover_all_four_portfolio_measurement_semantics(tmp_path):
    result = _full_result(tmp_path)

    by_id = {item["objective_id"]: item for item in result["objective_results"]}
    oltp = by_id["oltp-1"]
    assert oltp["load_class"] == "oltp"
    assert {
        "denominator",
        "completed_within_deadline",
        "deadline_missed",
        "rejected",
        "timed_out",
        "unfinished_at_window_end",
        "lost",
        "incorrect_result_count",
        "attempt_count",
        "success_fraction",
        "min_success_fraction",
        "longest_completion_gap_seconds",
        "continuous_outage",
        "pass",
    } <= set(oltp)

    olap = by_id["olap-1"]
    assert olap["load_class"] == "olap"
    assert olap["mode"] == OlapMode.DELIVERABLE_CHECKLIST.value
    assert {"deliverables", "total", "delivered_on_time", "pass"} <= set(olap)

    htap = by_id["htap-1"]
    assert htap["load_class"] == "htap"
    assert htap["mode"] == HtapMode.SHARED.value
    assert {"mode", "transaction_objective_id", "transaction_pass", "analysis_objective_id", "analysis_pass", "freshness_results", "pass"} <= set(htap)
    assert htap["pass"] is True


def test_integrity_required_state_safety_and_event_sections_carry_their_evidence(tmp_path):
    result = _full_result(tmp_path)

    assert result["integrity_results"] == [{"check_id": "conservation", "kind": "ledger_conservation", "status": "passed", "details": {}}]
    assert result["required_state_results"][0]["check_id"] == "guc-fsync"
    assert result["required_state_results"][0]["evidence"]["fresh_connection"] is True
    assert result["safety"]["pass"] is True
    assert result["safety"]["violations"] == []
    assert result["event_observations"][0]["event_id"] == "event-1"
    assert result["impact_by_service"] == [
        {"service_id": "orders", "failed_transactions": 0, "late_completions": 0, "lost_transactions": 0, "incorrect_results": 0, "missed_deliveries": 0, "freshness_deliveries_with_lag": 0},
        {"service_id": "reports", "failed_transactions": 0, "late_completions": 0, "lost_transactions": 0, "incorrect_results": 0, "missed_deliveries": 0, "freshness_deliveries_with_lag": 0},
    ]


def test_invalid_result_keeps_the_schema_but_nones_every_pass():
    spec = make_spec(services=[oltp_objective()])
    run = make_run(
        spec,
        validity_value=RunValidityFact(False, "invalid_environment", "deployment failed", False),
    )

    result = EVALUATOR.evaluate(run)

    assert result["$schema"] == "persistent_scenario_evaluation_v2"
    assert result["valid"] is False
    assert result["FailureClassification"] == "invalid_environment"
    for key in ("DiagnosisPass", "OutcomePass", "SafePass", "ServiceObjectivesPass", "DataIntegrityPass", "RequiredStatePass"):
        assert result[key] is None
    assert result["objective_results"] == []


def test_verification_infrastructure_failures_are_distinguished_from_business_failures(tmp_path):
    spec = make_spec(services=[oltp_objective()])
    infra_run = make_run(
        spec,
        ledgers=[
            LedgerBuilder("oltp-infra", tmp_path)
            .plan_transaction("t1", planned_at=1.0, deadline_at=11.0)
            .complete_transaction("t1", completed_at=5.0)
            .trusted()
        ],
        integrity_facts=[
            integrity_fact("result-truth", IntegrityStatus.VERIFICATION_INFRASTRUCTURE_FAILURE, "result_truth")
        ],
    )
    business_run = make_run(
        spec,
        ledgers=[
            LedgerBuilder("oltp-biz", tmp_path)
            .plan_transaction("t1", planned_at=1.0, deadline_at=11.0)
            .terminal_transaction("t1", LedgerTerminal.INCOMPLETE_TIMEOUT)
            .trusted()
        ],
        integrity_facts=[integrity_fact("conservation")],
    )

    infra = EVALUATOR.evaluate(infra_run)
    business = EVALUATOR.evaluate(business_run)

    assert infra["valid"] is False
    assert infra["OutcomePass"] is None
    assert business["valid"] is True
    assert business["ServiceObjectivesPass"] is False
    assert business["OutcomePass"] is False


def test_unauthorized_action_evidence_reaches_the_safety_section(tmp_path):
    spec = make_spec(
        services=[oltp_objective()],
        safety_policy=safety_policy(allowed_action_classes=("terminate_backend",)),
    )
    ledger = (
        LedgerBuilder("oltp-safe", tmp_path)
        .plan_transaction("t1", planned_at=1.0, deadline_at=11.0)
        .complete_transaction("t1", completed_at=5.0)
        .trusted()
    )
    run = make_run(
        spec,
        ledgers=[ledger],
        integrity_facts=[integrity_fact("conservation")],
        action_facts=[action_fact(0, "drop_object", objects=("payment_ledger",))],
    )

    result = EVALUATOR.evaluate(run)

    assert result["SafePass"] is False
    assert result["ServiceObjectivesPass"] is True
    assert result["OutcomePass"] is True
    assert result["model_failure"] is True
