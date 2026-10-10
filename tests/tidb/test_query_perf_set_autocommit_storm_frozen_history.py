"""Offline contract tests for the frozen-history set-autocommit Case.

These tests intentionally do not construct TiDBEnv, run an entrypoint, use the
reference agent, or exercise a mock path. Runtime lifecycle and recovery checks
are covered by the TiDB runtime validation tests.
"""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
from pathlib import Path
from types import SimpleNamespace

from src.execution.tidb_metrics import TIDB_METRIC_CATALOG
from src.scenarios.evaluation.diagnosis import ExactDiagnosisMatcher
from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.semantic import SemanticConditionJudgment, SemanticJudgment
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios.tidb import (
    TidbQueryPerfSetAutocommitStormFrozenHistoryScenario,
)
from src.scenarios.tidb.query_perf.set_autocommit_storm_frozen_history import (
    _COHORT_LEASE_MODES,
    _COHORT_STATES,
    _REFERENCE_REPORT,
    _RESOURCE_GROUPS,
    _session_setup_statement_count,
    TidbQueryPerfSetAutocommitStormFrozenHistoryInjector,
)
from src.scenarios.evaluation.tidb.query_perf.set_autocommit_storm_frozen_history import (
    MfSetAutocommitClusterHealthVerifier,
    _is_target_catalog_insert,
    _is_target_rollout_update,
)


ROOT = Path(__file__).resolve().parents[2]
SCENARIO = TidbQueryPerfSetAutocommitStormFrozenHistoryScenario()
CASE = SCENARIO.cases[0]
EVALUATOR = CASE.evaluator


def test_identity_registry_and_fault_plan_are_new_frozen_history_contracts():
    assert SCENARIO.scenario_id == "tidb_query_perf_set_autocommit_storm_frozen_history"
    assert CASE.case_id == "autocommit_storm_history_investigation"
    assert CASE.case_no == 0
    assert EVALUATOR.scenario_id == SCENARIO.scenario_id
    assert EVALUATOR.case_id == CASE.case_id

    plans = SCENARIO.build_fault_plan(CASE)
    assert len(plans) == 1
    assert plans[0].injector_type is TidbQueryPerfSetAutocommitStormFrozenHistoryInjector
    assert plans[0].config["target_cohort"] == "cohort-d"
    assert plans[0].config["db"] == "benchops_mf_ma03"
    assert plans[0].config["events_table"] == "mf_ma03_events"


def test_frozen_history_is_bounded_and_uses_only_existing_tidb_metrics():
    history = CASE.frozen_history
    assert history is not None
    history.validate(CASE.background_workload)
    assert history.duration_seconds == 12 * 60 * 60
    assert history.normal_capture_seconds == 240
    assert history.fault_capture_seconds == 150
    assert history.base_step_seconds == 30
    assert history.overview_step_seconds == 60
    assert history.target_age_seconds_range == (1800, 3600)
    assert history.required_metrics == ("cpu", "qps", "query_latency", "active_connections")
    assert set(history.required_metrics) <= set(TIDB_METRIC_CATALOG.metric_names)
    assert "session_lifecycle" not in TIDB_METRIC_CATALOG.metric_names
    assert "statement_execution" not in TIDB_METRIC_CATALOG.metric_names
    assert "workload_profile" in TIDB_METRIC_CATALOG.metric_names
    assert {item.decoy_id for item in history.decoys} == {
        "business-peak",
        "historical-rollout-b",
        "reporting-cpu",
        "rebind-stable",
    }


def test_four_online_cohorts_encode_the_required_counterfactuals():
    assert _COHORT_STATES == {
        "cohort-a": ("stable", "steady"),
        "cohort-b": ("canary", "steady"),
        "cohort-c": ("stable", "rebind"),
        "cohort-d": ("canary", "rebind"),
    }
    assert _COHORT_LEASE_MODES == {
        "cohort-a": "fixed",
        "cohort-b": "fixed",
        "cohort-c": "renew_on_checkout",
        "cohort-d": "renew_on_checkout",
    }
    assert CASE.cohort_ids == ("cohort-a", "cohort-b", "cohort-c", "cohort-d")
    assert set(_RESOURCE_GROUPS) == set(CASE.cohort_ids)
    assert len({profile.name for profile in CASE.background_workload.profiles}) == len(CASE.background_workload.profiles)
    assert len(CASE.background_workload.profiles) == 12

    fixed_lane = (True, False, "transition", 1, "stable", "steady", "fixed")
    lane_only = (False, False, "transition", 1, "canary", "steady", "fixed")
    lease_only = (False, False, "per_checkout", 512, "stable", "rebind", "renew_on_checkout")
    target = (False, False, "per_checkout", 512, "canary", "rebind", "renew_on_checkout")
    assert _session_setup_statement_count(fixed_lane, 1) == 1
    assert _session_setup_statement_count(lane_only, 1) == 1
    assert _session_setup_statement_count(lease_only, 1) == 0
    assert _session_setup_statement_count(target, 1) == 512


def test_reference_report_matches_every_critical_diagnosis_condition():
    report = StructuredReport.from_mapping(_REFERENCE_REPORT)
    result = ExactDiagnosisMatcher().match(EVALUATOR.diagnosis_conditions, report)
    assert result["DiagnosisPass"] is True
    assert result["missing_conditions"] == []
    assert result["critical_missing"] == []
    assert result["contradictory_conditions"] == []
    assert len(result["matched_conditions"]) == len(EVALUATOR.diagnosis_conditions)


def test_cutting_the_history_or_interaction_chain_fails_diagnosis_without_rewriting_op():
    report = deepcopy(_REFERENCE_REPORT)
    report["diagnosis"]["conditions"] = [
        item
        for item in report["diagnosis"]["conditions"]
        if item["type"] not in {"timeline", "counterfactual", "root_cause"}
    ]
    for item in report["diagnosis"]["conditions"]:
        if item["type"] == "exclusion":
            item["factor"] = item["factor"].replace("causal time order", "episode timing")
    result = ExactDiagnosisMatcher().match(
        EVALUATOR.diagnosis_conditions,
        StructuredReport.from_mapping(report),
    )
    assert result["DiagnosisPass"] is False
    assert {"causal_time_order", "online_counterfactuals", "deployment_state_interaction"} <= set(result["critical_missing"])


def test_contradictory_historical_noise_claim_cannot_pass_diagnosis():
    report = deepcopy(_REFERENCE_REPORT)
    report["diagnosis"]["conditions"].append(
        {
            "type": "root_cause",
            "factor": "the historical cohort-b rollout is the current target root cause",
            "entity": "cohort-b",
            "evidence": ["same SET fingerprint"],
        }
    )
    result = ExactDiagnosisMatcher().match(
        EVALUATOR.diagnosis_conditions,
        StructuredReport.from_mapping(report),
    )
    assert result["DiagnosisPass"] is False
    assert "historical_and_benign_exclusions" in result["contradictory_conditions"]


class _FaithfulSemanticJudge:
    def judge(self, expected, submitted):
        return SemanticJudgment(
            model="offline-faithful-judge",
            conditions=tuple(
                SemanticConditionJudgment(item.condition_id, (index,), (), "same causal meaning")
                for index, item in enumerate(expected)
            ),
            usage={"input_tokens": 1, "output_tokens": 1},
        )


def test_semantic_matcher_uses_the_same_complete_expected_conditions():
    result = SemanticDiagnosisMatcher(_FaithfulSemanticJudge()).match(
        EVALUATOR.diagnosis_conditions,
        StructuredReport.from_mapping(_REFERENCE_REPORT),
    )
    assert result["DiagnosisPass"] is True
    assert result["matching_mode"] == "semantic"
    assert result["missing_conditions"] == []


def test_diagnosis_without_causal_chain_or_evidence_fails():
    report = deepcopy(_REFERENCE_REPORT)
    report["diagnosis"]["conditions"] = [{
        "type": "symptom",
        "factor": "CPU and latency are high",
        "entity": "the database",
        "evidence": [],
    }]
    result = ExactDiagnosisMatcher().match(
        EVALUATOR.diagnosis_conditions,
        StructuredReport.from_mapping(report),
    )
    assert result["DiagnosisPass"] is False
    assert set(result["critical_missing"]) == {item.condition_id for item in EVALUATOR.diagnosis_conditions}


def test_target_only_rollout_boundary_and_target_owned_revision_boundary_are_explicit():
    rollout_table = "benchops_mf_ma03.mf_ma03_runtime_rollouts"
    catalog_table = "benchops_mf_ma03.mf_ma03_runtime_revision_catalog"
    assert _is_target_rollout_update(
        f"update {rollout_table} set desired_session_lease_mode='fixed', generation=generation+1, rollout_state='pending' where cohort_id='cohort-d'",
        rollout_table,
        "cohort-d",
    )
    assert not _is_target_rollout_update(
        f"update {rollout_table} set desired_session_lease_mode='fixed' where cohort_id='cohort-b'",
        rollout_table,
        "cohort-d",
    )
    assert _is_target_catalog_insert(
        f"insert into {catalog_table} values ('lease-target', 'session_lease', 'target', 'cohort-d', null)",
        catalog_table,
        "cohort-d",
    )
    assert not _is_target_catalog_insert(
        f"insert into {catalog_table} values ('lease-shared', 'session_lease', 'shared', null)",
        catalog_table,
        "cohort-d",
    )


def test_cluster_health_verifier_rejects_node_set_drift_without_starting_tidb():
    baseline_nodes = {
        "pd/pd-0": {"running": True, "paused": False, "oom_killed": False},
        "tikv/tikv-0": {"running": True, "paused": False, "oom_killed": False},
    }

    class Env:
        def manage_cluster(self, resource, operation):
            assert (resource, operation) == ("service", "list")
            return json.dumps({
                "status": "success",
                "result": {"nodes": {**baseline_nodes, "tikv/tikv-1": {"running": True, "paused": False, "oom_killed": False}}},
            })

    context = SimpleNamespace(
        case_run=SimpleNamespace(env=Env()),
        injection_evidence={"mf-set-autocommit_node_health": {"result": {"nodes": baseline_nodes}}},
    )
    result = MfSetAutocommitClusterHealthVerifier().verify(context)
    assert result.passed is False
    assert result.actual["added_nodes"] == ["tikv/tikv-1"]


def test_target_rollout_boundary_accepts_only_target_desired_state():
    from src.scenarios.evaluation.tidb.query_perf.set_autocommit_storm_frozen_history import (
        _is_target_rollout_update,
    )

    table = "benchops_mf_ma03.mf_ma03_runtime_rollouts"
    assert _is_target_rollout_update(
        f"update {table} set desired_session_lease_mode='fixed', generation=generation+1, rollout_state='pending' where cohort_id='cohort-d'",
        table,
        "cohort-d",
    )
    assert not _is_target_rollout_update(
        f"update {table} set desired_session_lease_mode='fixed' where cohort_id='cohort-b'",
        table,
        "cohort-d",
    )
    assert not _is_target_rollout_update(
        f"update {table} set desired_session_lease_mode='fixed' where cohort_id='cohort-d' or cohort_id='cohort-b'",
        table,
        "cohort-d",
    )


def test_injector_implements_the_five_phase_lifecycle_without_legacy_methods():
    for method_name in ("install", "activate", "prepare_observability", "quiesce", "recover"):
        signature = inspect.signature(getattr(TidbQueryPerfSetAutocommitStormFrozenHistoryInjector, method_name))
        assert tuple(signature.parameters) == ("self", "context")
    assert not hasattr(TidbQueryPerfSetAutocommitStormFrozenHistoryInjector, "inject")
    assert not hasattr(TidbQueryPerfSetAutocommitStormFrozenHistoryInjector, "get_name")


def test_frozen_history_fixture_preparation_is_internal_and_context_bound():
    signature = inspect.signature(
        getattr(TidbQueryPerfSetAutocommitStormFrozenHistoryInjector, "prepare_frozen_history_environment")
    )
    assert tuple(signature.parameters) == ("self", "context")
    orchestrator = (ROOT / "src/scenarios/runtime/orchestrator.py").read_text(encoding="utf-8")
    assert "_prepare_frozen_history_workload_environment()" not in orchestrator
    assert "_prepare_observability()" in orchestrator


def test_entrypoint_is_seeded_and_gpt_only_without_new_tidb_tool_path():
    entry = ROOT / "examples/run_tidb_query_perf_set_autocommit_storm_frozen_history_scenario.py"
    source = entry.read_text(encoding="utf-8")
    assert 'parser.add_argument("--seed", required=True, type=int)' in source
    assert 'parser.add_argument("--model", required=True, help="LLM model name")' in source
    assert 'model=args.model' in source
    assert "MockLLMAgent" not in source
    assert "claude" not in source.casefold()
    assert "session_lifecycle" not in source
    assert "statement_execution" not in source
    assert "workload_profile" not in source


def test_original_ma03_scenario_identity_remains_untouched():
    from src.scenarios.tidb.query_perf.set_autocommit_storm import (
        TidbQueryPerfSetAutocommitStormScenario,
    )

    assert TidbQueryPerfSetAutocommitStormScenario.scenario_id == "tidb_query_perf_set_autocommit_storm"
