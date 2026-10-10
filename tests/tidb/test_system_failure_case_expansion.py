from pathlib import Path

from src.benchmark.manifest import load_manifest
from src.benchmark.planner import plan_runs
from src.scenarios.tidb.system_failure import (
    TidbSystemFailureBrPermissionScenario,
    TidbSystemFailureDeadlockScenario,
    TidbSystemFailureLockContentionScenario,
    TidbSystemFailureMdlBlockingScenario,
    TidbSystemFailurePendingOfflineScenario,
    TidbSystemFailureSf01Scenario,
    TidbSystemFailureSf02Scenario,
)


SCENARIOS = (
    TidbSystemFailureLockContentionScenario(),
    TidbSystemFailurePendingOfflineScenario(),
    TidbSystemFailureMdlBlockingScenario(),
    TidbSystemFailureDeadlockScenario(),
    TidbSystemFailureSf01Scenario(),
    TidbSystemFailureSf02Scenario(),
    TidbSystemFailureBrPermissionScenario(),
)

NEW_CASES = (
    ("tidb_system_failure_lock_contention", "checkout_row_lock_simple"),
    ("tidb_system_failure_mdl_blocking", "mdl_release_chain_simple"),
    ("tidb_system_failure_deadlock", "wallet_pair_deadlock_simple"),
    ("tidb_system_failure_sf01", "pd_mixed_disk_eviction_simple"),
    ("tidb_system_failure_sf02", "slow_store_lock_ttl_simple"),
    ("tidb_system_failure_br_permission", "br_s3_binding_focus"),
)

EXPECTED_CALIBRATION = {
    "checkout_row_lock_simple": (2, 7, 62, "reference-234__"),
    "mdl_release_chain_simple": (2, 7, 15, "reference-240__"),
    "wallet_pair_deadlock_simple": (2, 12, 167, "reference-236__"),
    "pd_mixed_disk_eviction_simple": (2, 109, 147, "reference-235__"),
    "slow_store_lock_ttl_simple": (2, 24, 373, "reference-234__"),
    "br_s3_binding_focus": (4, 119, 405, "reference-233__"),
}

EXPECTED_FOCUSED_LABEL = {
    "checkout_row_lock_simple": "easy",
    "mdl_release_chain_simple": "easy",
    "wallet_pair_deadlock_simple": "easy",
    "pd_mixed_disk_eviction_simple": "easy",
    "slow_store_lock_ttl_simple": "easy",
    "br_s3_binding_focus": "easy",
}


def _new_cases():
    return [
        scenario.get_case(case_id)
        for scenario_id, case_id in NEW_CASES
        for scenario in SCENARIOS
        if scenario.scenario_id == scenario_id
    ]


def test_calibrated_system_failure_scenarios_have_one_contiguous_focused_case():
    assert len(_new_cases()) == 6
    for scenario in SCENARIOS:
        if scenario.scenario_id == "tidb_system_failure_pending_offline":
            continue
        assert [case.case_no for case in scenario.cases] == [0, 1]
        original, focused = scenario.cases
        assert focused.case_id != original.case_id
        assert focused.evaluator is not original.evaluator
        assert focused.evaluator.scenario_id == scenario.scenario_id
        assert focused.evaluator.case_id == focused.case_id
        assert focused.background_workload != original.background_workload
        original_plan = scenario.build_fault_plan(original)
        focused_plan = scenario.build_fault_plan(focused)
        assert len(original_plan) == len(focused_plan) == 1
        assert original_plan[0].injector_type is focused_plan[0].injector_type
        assert original_plan[0].config != focused_plan[0].config


def test_focused_cases_use_live_reference_calibration_without_placeholders():
    for case in _new_cases():
        depth, causal, noise, reference_prefix = EXPECTED_CALIBRATION[case.case_id]


def test_focused_cases_preserve_the_scenario_capability_and_change_real_scope():
    cases = {case.case_id: case for case in _new_cases()}
    assert cases["checkout_row_lock_simple"].same_table_decoy_routes == (
        (17, "app=checkout-api route=reconciliation"),
        (23, "app=checkout-api route=retry"),
        (42, "app=settlement-worker route=repair"),
    )
    assert cases["mdl_release_chain_simple"].fourth_added_column == "focused_release_trace_id"
    assert len(cases["wallet_pair_deadlock_simple"].deadlock_decoy_specs) == 4
    assert cases["pd_mixed_disk_eviction_simple"].insert_row_id == 1002
    assert cases["slow_store_lock_ttl_simple"].target_order_id == 43
    assert cases["slow_store_lock_ttl_simple"].target_delta == 29
    assert cases["br_s3_binding_focus"].effective_binding_id == 1900
    assert cases["br_s3_binding_focus"].candidate_binding_id == 1901


def test_focused_sf01_publishes_its_authorized_business_contract():
    case = next(
        case
        for scenario in SCENARIOS
        if scenario.scenario_id == "tidb_system_failure_sf01"
        for case in scenario.cases
        if case.case_id == "pd_mixed_disk_eviction_simple"
    )

    for value in (
        "event_id=1002",
        "event_amount=24500",
        "event_state='paid'",
        "record_crc=525252",
        "region_code='north'",
        "settlement_day='2026-08-01'",
        "event_id <= 1000",
        "count, amount, and checksum deltas are zero",
    ):
        assert value in case.alert


def test_sf07_online_unsafe_case_uses_r05_maintenance_scope_calibration():
    scenario = next(item for item in SCENARIOS if item.scenario_id == "tidb_system_failure_pending_offline")
    assert [case.case_id for case in scenario.cases] == [
        "online_unsafe_recovery_failed_stores",
        "store_migration_pending_offline",
    ]
    case = scenario.cases[0]
    plan_config = scenario.build_fault_plan(scenario.cases[0])[0].config
    assert "failed_nodes" in plan_config
    assert "maintenance_nodes" in plan_config


def test_tidb_experiment_ports_reserve_non_overlapping_deployment_blocks(tmp_path):
    manifest_path = tmp_path / "tidb-port-blocks.yaml"
    manifest_path.write_text(
        """
experiment_id: tidb-port-blocks
benchmark:
  systems: [tidb]
  categories: [system_failure]
  scenarios:
    - tidb_system_failure_lock_contention
    - tidb_system_failure_pending_offline
    - tidb_system_failure_mdl_blocking
    - tidb_system_failure_deadlock
    - tidb_system_failure_sf01
    - tidb_system_failure_sf02
    - tidb_system_failure_br_permission
agents: [{id: mock, mode: mock}]
exclude_cells:
  - {scenario: tidb_system_failure_lock_contention, case: admission_events_row_lock_deadlock, agent: mock}
  - {scenario: tidb_system_failure_mdl_blocking, case: long_transaction_mdl_blocks_online_ddl, agent: mock}
  - {scenario: tidb_system_failure_deadlock, case: wallet_pair_reverse_order_deadlock, agent: mock}
  - {scenario: tidb_system_failure_sf01, case: pd_mixed_disk_eviction, agent: mock}
  - {scenario: tidb_system_failure_sf02, case: slow_store_lock_ttl_commit_failure, agent: mock}
  - {scenario: tidb_system_failure_br_permission, case: br_s3_credentials_denied, agent: mock}
  - {scenario: tidb_system_failure_pending_offline, case: store_migration_pending_offline, agent: mock}
repetitions: 1
seeds: [20260814]
runtime: {port_base: 50000}
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    ports = [spec.port for spec in plan_runs(manifest)]
    assert ports == [50000, 50032, 50064, 50096, 50128, 50160, 50192]


def test_formal_entrypoints_keep_case_selection():
    root = Path(__file__).parents[2]
    for entrypoint in (
        "run_tidb_system_failure_lock_contention_scenario.py",
        "run_tidb_system_failure_pending_offline_scenario.py",
        "run_tidb_system_failure_mdl_blocking_scenario.py",
        "run_tidb_system_failure_deadlock_scenario.py",
        "run_tidb_system_failure_sf01_scenario.py",
        "run_tidb_system_failure_sf02_scenario.py",
        "run_tidb_system_failure_br_permission_scenario.py",
    ):
        assert 'add_argument("--case"' in (root / "examples" / entrypoint).read_text()
