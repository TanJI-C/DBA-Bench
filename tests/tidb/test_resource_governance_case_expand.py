import importlib
import json
import time

import pytest

from src.scenarios.tidb.resource_governance.br_slo import (
    TidbResourceGovernanceBrSloAdaptiveThrottlingScenario,
)
from src.scenarios.tidb.resource_governance.connection_balancing import (
    TidbResourceGovernanceConnectionBalancingScenario,
)
from src.scenarios.tidb.resource_governance.empty_region_merge_budget import (
    TidbResourceGovernanceEmptyRegionMergeBudgetScenario,
)
from src.scenarios.tidb.resource_governance.lightning_budget import (
    TidbResourceGovernanceLightningBudgetScenario,
)
from src.scenarios.tidb.resource_governance.pd_api_security import (
    TidbResourceGovernancePdApiSecurityScenario,
)
from src.scenarios.tidb.resource_governance.placement_policy import (
    TidbResourceGovernancePlacementPolicyScenario,
)
from src.scenarios.tidb.resource_governance.rg06_ticdc_checkpoint_lag import (
    TidbResourceGovernanceRg06Scenario,
)
from src.scenarios.tidb.resource_governance.ru_budget_calibration import (
    TidbResourceGovernanceRuBudgetCalibrationScenario,
)
from src.scenarios.tidb.resource_governance.runaway_query import (
    TidbResourceGovernanceRunawayQueryScenario,
)
from src.scenarios.tidb.resource_governance.sql_binding import (
    TidbResourceGovernanceSqlBindingScenario,
)


NEW_CASES = (
    ("tidb_resource_governance_br_slo_adaptive_throttling", "br_backup_storage_envelope"),
    ("tidb_resource_governance_ru_budget_calibration", "mixed_oltp_olap_ru_budget_rebalanced"),
    ("tidb_resource_governance_runaway_query", "runaway_query_protected_export"),
    ("tidb_resource_governance_connection_balancing", "multi_tidb_alternate_target_drain"),
    ("tidb_resource_governance_placement_policy", "compliance_table_neighbor_isolation"),
    ("tidb_resource_governance_lightning_budget", "lightning_import_conservative_rebalance"),
    ("tidb_resource_governance_rg06", "ticdc_reconcile_sink_budget"),
    ("tidb_resource_governance_empty_region_merge_budget", "empty_region_merge_reduced_inventory"),
    ("tidb_resource_governance_pd_api_security", "pd_api_staged_route_hardening"),
    ("tidb_resource_governance_sql_binding", "channel_window_binding_approval"),
)

SCENARIOS = (
    TidbResourceGovernanceBrSloAdaptiveThrottlingScenario(),
    TidbResourceGovernanceRuBudgetCalibrationScenario(),
    TidbResourceGovernanceRunawayQueryScenario(),
    TidbResourceGovernanceConnectionBalancingScenario(),
    TidbResourceGovernancePlacementPolicyScenario(),
    TidbResourceGovernanceLightningBudgetScenario(),
    TidbResourceGovernanceRg06Scenario(),
    TidbResourceGovernanceEmptyRegionMergeBudgetScenario(),
    TidbResourceGovernancePdApiSecurityScenario(),
    TidbResourceGovernanceSqlBindingScenario(),
)


def _new_cases():
    return [scenario.get_case(case_id) for scenario_id, case_id in NEW_CASES for scenario in SCENARIOS if scenario.scenario_id == scenario_id]


def test_all_expanded_cases_have_independent_hard_identity_and_contracts():
    cases = _new_cases()
    assert len(cases) == 10
    assert [(case.evaluator.scenario_id, case.evaluator.case_id) for case in cases] == list(NEW_CASES)
    assert all(case.case_no == 1 for case in cases)
    measured_labels = {
        "runaway_query_protected_export": "easy",
        "br_backup_storage_envelope": "easy",
        "ticdc_reconcile_sink_budget": "easy",
        "mixed_oltp_olap_ru_budget_rebalanced": "easy",
        "multi_tidb_alternate_target_drain": "easy",
        "empty_region_merge_reduced_inventory": "easy",
        "channel_window_binding_approval": "easy",
        "lightning_import_conservative_rebalance": "easy",
    }


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda item: item.scenario_id)
def test_each_resource_governance_scenario_has_contiguous_cases_and_case_specific_fault_plan(scenario):
    assert [case.case_no for case in scenario.cases] == [0, 1]
    original, expanded = scenario.cases
    assert expanded.case_id != original.case_id
    assert expanded.evaluator is not original.evaluator
    original_plan = scenario.build_fault_plan(original)
    expanded_plan = scenario.build_fault_plan(expanded)
    assert len(original_plan) == len(expanded_plan) == 1
    assert original_plan[0].injector_type is expanded_plan[0].injector_type
    assert original_plan[0].config != expanded_plan[0].config


def test_case_specific_targets_and_thresholds_are_not_old_case_aliases():
    cases = {case.case_id: case for case in _new_cases()}
    assert cases["br_backup_storage_envelope"].max_backup_bytes == 6 * 1024**3
    assert cases["mixed_oltp_olap_ru_budget_rebalanced"].maximum_total_ru_per_sec == 900
    assert cases["runaway_query_protected_export"].batch_id == "july-export"
    assert cases["multi_tidb_alternate_target_drain"].initial_target == "tidb/tidb-1"
    assert cases["compliance_table_neighbor_isolation"].table == "rg04_relation_01"
    assert cases["lightning_import_conservative_rebalance"].row_count == 400000
    assert cases["ticdc_reconcile_sink_budget"].changefeed_id == "reconcile-orders"
    assert cases["empty_region_merge_reduced_inventory"].empty_table_count == 16
    assert cases["empty_region_merge_reduced_inventory"].maximum_empty_regions == 8
    assert cases["empty_region_merge_reduced_inventory"].maximum_empty_ratio == 0.30
    assert cases["pd_api_staged_route_hardening"].consumer_route_rows == 20
    assert cases["channel_window_binding_approval"].expected_index == "idx_channel_time"
    assert cases["channel_window_binding_approval"].expected_result_count == 260


def test_rg08_alert_does_not_mark_managed_settlement_pool_as_protected():
    case = TidbResourceGovernanceConnectionBalancingScenario().get_case("multi_tidb_alternate_target_drain")
    assert "settlement pool within the application-pool rebalance scope" in case.alert
    assert "only the identity probe affinity is protected" in case.alert
    assert "settlement affinity are protected" not in case.alert



def test_rg05_case_fault_plan_carries_the_explicit_initial_budget():
    scenario = TidbResourceGovernanceLightningBudgetScenario()
    plan = scenario.build_fault_plan(scenario.get_case("lightning_import_conservative_rebalance"))[0]
    assert plan.config["phase1_region_concurrency"] == 1
    assert plan.config["phase1_disk_quota_mb"] == 1024
    assert plan.config["phase1_store_write_bwlimit_mib"] == 16
    assert plan.config["rebalance_after_rows"] == 300000


def test_rg10_target_table_index_definitions_are_unique():
    case = TidbResourceGovernanceSqlBindingScenario().get_case("channel_window_binding_approval")
    statement = case.evaluator
    assert statement.case_id == case.case_id
    assert case.expected_index not in {case.decoy_index}
    assert case.business_query.count("channel = 'batch'") == 1


def _response_action_lines(responses):
    lines = []
    for response in responses:
        if "actions" in response:
            actions = response["actions"]
        else:
            actions = [response["action"]]
        for action in actions:
            lines.append(json.dumps(action, ensure_ascii=False, sort_keys=True))
    return "\n".join(lines)


def _entry_module(module_name):
    return importlib.import_module(f"examples.{module_name}")


SIMPLIFIED_MOCK_CASES = (
    (
        "tidb_resource_governance_ru_budget_calibration",
        "mixed_oltp_olap_ru_budget_rebalanced",
        "run_tidb_resource_governance_ru_budget_calibration_scenario",
        "build_mock_responses",
        ("cluster_statements_summary", '"metric_type": "cpu"', "active_connections"),
        ("ALTER RESOURCE GROUP", "service_objectives", "resource_groups", '"api": "submit"'),
    ),
    (
        "tidb_resource_governance_sql_binding",
        "channel_window_binding_approval",
        "run_tidb_resource_governance_sql_binding_scenario",
        "full_pass_mock_responses",
        ("candidate_", "active_connections"),
        (
            "CREATE SESSION BINDING",
            "@@last_plan_from_binding",
            "SHOW INDEX",
            '"api": "submit"',
        ),
    ),
    (
        "tidb_resource_governance_connection_balancing",
        "multi_tidb_alternate_target_drain",
        "run_tidb_resource_governance_connection_balancing_scenario",
        "build_mock_responses",
        ('"metric_type": "cpu"', '"metric_type": "qps"', '"metric_type": "query_latency"'),
        ("active_connections", '"operation": "drain"', '"api": "submit"'),
    ),
    (
        "tidb_resource_governance_empty_region_merge_budget",
        "empty_region_merge_reduced_inventory",
        "run_tidb_resource_governance_empty_region_merge_budget_scenario",
        "build_mock_responses",
        ('"metric_type": "cpu"',),
        (
            "schedule.enable-cross-table-merge",
            "schedule.merge-schedule-limit",
            '"api": "submit"',
        ),
    ),
    (
        "tidb_resource_governance_rg06",
        "ticdc_reconcile_sink_budget",
        "run_tidb_resource_governance_rg06_scenario",
        "build_mock_responses",
        ("family = 'resource'", "active_connections"),
        ("UPDATE", "family = 'progress'", '"api": "submit"'),
    ),
)


@pytest.mark.parametrize(
    ("scenario_id", "case_id", "module_name", "function_name", "removed_markers", "kept_markers"),
    SIMPLIFIED_MOCK_CASES,
    ids=[item[1] for item in SIMPLIFIED_MOCK_CASES],
)
def test_simplified_case_mock_paths_are_compressed_to_two_hops(
    scenario_id, case_id, module_name, function_name, removed_markers, kept_markers
):
    scenario = next(item for item in SCENARIOS if item.scenario_id == scenario_id)
    case = scenario.get_case(case_id)
    responses = getattr(_entry_module(module_name), function_name)(case)
    text = _response_action_lines(responses)

    for marker in removed_markers:
        assert marker not in text
    for marker in kept_markers:
        assert marker in text
    assert responses[-1].get("actions", [responses[-1].get("action")])[-1]["api"] == "submit"


@pytest.mark.parametrize(
    ("scenario_id", "module_name", "function_name", "removed_markers"),
    [(item[0], item[2], item[3], item[4]) for item in SIMPLIFIED_MOCK_CASES],
    ids=[item[1] for item in SIMPLIFIED_MOCK_CASES],
)
def test_original_case_mock_paths_keep_the_removed_hops(
    scenario_id, module_name, function_name, removed_markers
):
    scenario = next(item for item in SCENARIOS if item.scenario_id == scenario_id)
    case = scenario.cases[0]
    responses = getattr(_entry_module(module_name), function_name)(case)
    text = _response_action_lines(responses)
    for marker in removed_markers:
        assert marker in text


def _agent_actions(agent, **stubbed_methods):
    executed = []

    def _execute(api, args, thinking=""):
        executed.append({"api": api, "args": args})
        return {"status": "success", "result": []}

    agent.execute = _execute
    for name, stub in stubbed_methods.items():
        setattr(agent, name, stub)
    return agent.solve(), executed


def test_runaway_export_mock_agent_uses_the_compressed_two_hop_path(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    module = _entry_module("run_tidb_resource_governance_runaway_query_scenario")
    scenario = TidbResourceGovernanceRunawayQueryScenario()
    case = scenario.get_case("runaway_query_protected_export")

    _, simplified = _agent_actions(module.RG02FullMockAgent(case))
    text = json.dumps(simplified, ensure_ascii=False)
    assert "PROCESSLIST" not in text
    for marker in (
        "cluster_statements_summary",
        "INFORMATION_SCHEMA.RESOURCE_GROUPS",
        "mysql.tidb_runaway_queries",
        "ALTER RESOURCE GROUP",
    ):
        assert marker in text

    _, original = _agent_actions(module.RG02FullMockAgent(scenario.cases[0]))
    original_text = json.dumps(original, ensure_ascii=False)
    assert "PROCESSLIST" in original_text


def test_br_slo_storage_envelope_mock_agent_uses_the_compressed_two_hop_path():
    module = _entry_module("run_tidb_resource_governance_br_slo_adaptive_throttling_scenario")
    scenario = TidbResourceGovernanceBrSloAdaptiveThrottlingScenario()
    case = scenario.get_case("br_backup_storage_envelope")
    noop = lambda: None

    _, simplified = _agent_actions(
        module.ResourceGovernanceFullMockAgent(case),
        _await_maintenance_completion=noop,
        _await_foreground_slo=noop,
    )
    text = json.dumps(simplified, ensure_ascii=False)
    assert "active_connections" not in text
    assert "disk_io" not in text
    for marker in ("query_latency", "SHOW CONFIG", "SET CONFIG", case.job_id):
        assert marker in text

    _, original = _agent_actions(
        module.ResourceGovernanceFullMockAgent(scenario.cases[0]),
        _await_maintenance_completion=noop,
        _await_foreground_slo=noop,
    )
    original_text = json.dumps(original, ensure_ascii=False)
    assert "active_connections" in original_text
    assert "disk_io" in original_text
