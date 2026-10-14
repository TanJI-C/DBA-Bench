import json
from types import SimpleNamespace

from src.scenarios import ALL_SCENARIOS
from src.scenarios.base import CaseRun
from src.scenarios.evaluation.diagnosis import DiagnosisMatcher
from src.protocols.report import StructuredReport
from src.scenarios.evaluation.tidb.system_failure.mdl_blocking import (
    MdlBlockingOutcomeVerifier,
)
from src.scenarios.tidb.system_failure.mdl_blocking import (
    TidbSystemFailureMdlBlockingInjector,
)


SIMPLIFIED_CASES = {
    "tidb_system_failure_br_permission": (
        "br_s3_credentials_denied",
        "br_s3_binding_focus",
    ),
    "tidb_system_failure_sf01": (
        "pd_mixed_disk_eviction",
        "pd_mixed_disk_eviction_simple",
    ),
    "tidb_system_failure_table_cache_lease": (
        "table_cache_lease_write_conflict",
        "table_cache_lease_single_table_focus",
    ),
    "tidb_system_failure_sf02": (
        "slow_store_lock_ttl_commit_failure",
        "slow_store_lock_ttl_simple",
    ),
    "tidb_system_failure_lock_contention": (
        "admission_events_row_lock_deadlock",
        "checkout_row_lock_simple",
    ),
    "tidb_system_failure_deadlock": (
        "wallet_pair_reverse_order_deadlock",
        "wallet_pair_deadlock_simple",
    ),
    "tidb_system_failure_region_unavailable": (
        "region_unavailable_pd_network_block",
        "region_unavailable_pd_response_focus",
    ),
    "tidb_system_failure_mdl_blocking": (
        "long_transaction_mdl_blocks_online_ddl",
        "mdl_release_chain_simple",
    ),
}

BASELINE_ORIGINAL_CONDITION_COUNTS = {
    "tidb_system_failure_br_permission": 19,
    "tidb_system_failure_sf01": 4,
    "tidb_system_failure_table_cache_lease": 5,
    "tidb_system_failure_sf02": 6,
    "tidb_system_failure_lock_contention": 4,
    "tidb_system_failure_deadlock": 8,
    "tidb_system_failure_region_unavailable": 9,
    "tidb_system_failure_mdl_blocking": 3,
}

# Labels follow the difficulty calibration rule; Easy holds whenever the
# compressed path reaches D_s<=2 even in noisy environments (D and C are
# independent dimensions).
MEASURED_FOCUSED_LABELS = {
    "tidb_system_failure_br_permission": "easy",
    "tidb_system_failure_sf01": "easy",
    "tidb_system_failure_sf02": "easy",
    "tidb_system_failure_lock_contention": "easy",
    "tidb_system_failure_deadlock": "easy",
    "tidb_system_failure_region_unavailable": "easy",
    "tidb_system_failure_table_cache_lease": "easy",
    "tidb_system_failure_mdl_blocking": "easy",
}


def _scenario(scenario_id):
    return next(item for item in ALL_SCENARIOS if item.scenario_id == scenario_id)


def _pair(scenario_id):
    scenario = _scenario(scenario_id)
    original_id, focused_id = SIMPLIFIED_CASES[scenario_id]
    return scenario, scenario.get_case(original_id), scenario.get_case(focused_id)


def test_simplified_cases_compress_the_focused_diagnosis_to_two_hops():
    for scenario_id in SIMPLIFIED_CASES:
        scenario, original, focused = _pair(scenario_id)
        assert focused.case_no == 1
        assert focused.evaluator is not original.evaluator
        assert len(focused.evaluator.diagnosis_conditions) == 2
        assert len(original.evaluator.diagnosis_conditions) == (
            BASELINE_ORIGINAL_CONDITION_COUNTS[scenario_id]
        )

        focused_match = DiagnosisMatcher(
            focused.evaluator.diagnosis_conditions
        ).match(StructuredReport.from_mapping(focused.reference_report))
        assert focused_match["DiagnosisPass"] is True, (
            scenario_id,
            focused_match["missing_conditions"],
            focused_match["contradictory_conditions"],
        )


def test_simplified_cases_keep_case_zero_contracts_intact():
    alias_complete_case_zero_reports = {
        "tidb_system_failure_br_permission",
        "tidb_system_failure_sf01",
        "tidb_system_failure_deadlock",
        "tidb_system_failure_mdl_blocking",
    }
    for scenario_id in SIMPLIFIED_CASES:
        scenario, original, focused = _pair(scenario_id)
        if scenario_id in alias_complete_case_zero_reports:
            original_match = DiagnosisMatcher(
                original.evaluator.diagnosis_conditions
            ).match(StructuredReport.from_mapping(original.reference_report))
            assert original_match["DiagnosisPass"] is True, (
                scenario_id,
                original_match["missing_conditions"],
            )
        assert focused.reference_report != original.reference_report
        assert scenario.build_fault_plan(original)[0].config != (
            scenario.build_fault_plan(focused)[0].config
        )


def test_lock_contention_focus_keeps_decoy_scope_and_op_invariants():
    _, original, focused = _pair("tidb_system_failure_lock_contention")
    assert focused.same_table_decoy_routes == (
        (17, "app=checkout-api route=reconciliation"),
        (23, "app=checkout-api route=retry"),
        (42, "app=settlement-worker route=repair"),
    )
    assert focused.minimum_other_lock_waits == 18
    assert focused.lock_row_id == original.lock_row_id
    assert focused.expected_amount == original.expected_amount


def test_deadlock_focus_keeps_decoy_batches_and_op_invariants():
    _, original, focused = _pair("tidb_system_failure_deadlock")
    assert len(focused.deadlock_decoy_specs) == 4
    assert focused.batch_id == original.batch_id
    assert focused.from_expected_balance == original.from_expected_balance
    assert focused.to_expected_balance == original.to_expected_balance


def test_mdl_focus_uses_a_single_release_stage_and_case_zero_keeps_four():
    scenario, original, focused = _pair("tidb_system_failure_mdl_blocking")
    assert original.release_stage_count == 4
    assert focused.release_stage_count == 1
    original_plan = scenario.build_fault_plan(original)[0].config
    focused_plan = scenario.build_fault_plan(focused)[0].config
    assert original_plan["release_stage_count"] == 4
    assert focused_plan["release_stage_count"] == 1
    assert focused.fourth_added_column == "focused_release_trace_id"


def test_mdl_single_stage_chain_thread_returns_before_the_first_ddl_completes():
    import threading

    injector = object.__new__(TidbSystemFailureMdlBlockingInjector)
    injector.release_stage_count = 1
    stop_event = threading.Event()
    injector._runtime_stop = stop_event
    ddl_done = threading.Event()
    injector._ddl_done = ddl_done
    injector._advance_release_chain(None)
    assert not ddl_done.is_set()
    stop_event.set()


def _focused_mdl_run(env, *, released):
    focused = _scenario("tidb_system_failure_mdl_blocking").get_case(
        "mdl_release_chain_simple"
    )
    evidence = {
        "table": focused.table,
        "guard_table": focused.guard_table,
        "table_id": 812,
        "ddl_job_id": 901,
        "ddl_job_ids": [901],
        "ddl_session_id": 1201,
        "holder_session_ids": [1200, 1203, 1204, 1205, 1206, 1207],
        "late_holder_session_ids": [],
        "third_holder_session_ids": [],
        "fourth_holder_session_ids": [],
        "guard_session_ids": [1202, 1208],
        "protected_target_session_ids": [1209, 1212],
        "added_column": focused.added_column,
        "second_added_column": focused.second_added_column,
        "third_added_column": focused.third_added_column,
        "fourth_added_column": focused.fourth_added_column,
        "ddl_sql": focused.ddl_sql,
        "second_ddl_sql": focused.second_ddl_sql,
        "third_ddl_sql": focused.third_ddl_sql,
        "fourth_ddl_sql": focused.fourth_ddl_sql,
        "row_count": 128,
        "id_sum": 8256,
        "payload_crc": 12345,
        "mdl_rows": [],
    }

    def execute_sql(sql):
        normalized = sql.casefold()
        if "information_schema.ddl_jobs" in normalized:
            schema_state, job_state = (
                ("public", "synced") if released else ("none", "running")
            )
            rows = [[
                901, "test", focused.table, "add column", schema_state, job_state,
                focused.ddl_sql,
            ]]
        elif "information_schema.columns" in normalized:
            rows = [[focused.added_column]] if released else []
        elif "session_id in (1200, 1203, 1204, 1205, 1206, 1207)" in normalized:
            rows = [] if released else [[1200]]
        elif "session_id in (1202, 1208)" in normalized:
            rows = [[2]]
        elif "bit_xor(crc32" in normalized:
            rows = [[128, 8256, 12345]]
        else:
            rows = [[1]]
        return json.dumps({"status": "success", "result": rows})

    env.execute_sql = execute_sql
    context = SimpleNamespace(
        case_run=CaseRun(
            run_id="mdl-focused-test-run",
            scenario=_scenario("tidb_system_failure_mdl_blocking"),
            case=focused,
            env=env,
            injections=[SimpleNamespace(evidence=evidence)],
            action_history=[{"api": "submit", "args": focused.reference_report}],
        )
    )
    return context


def test_mdl_focus_outcome_verifier_accepts_a_single_stage_chain():
    verifier = MdlBlockingOutcomeVerifier(max_attempts=1, interval_seconds=0)
    check = verifier.verify(_focused_mdl_run(SimpleNamespace(), released=True))
    assert check.passed is True
    assert check.actual["release_chain_synced"]


def test_mdl_focus_outcome_verifier_fails_while_the_blocker_is_live():
    verifier = MdlBlockingOutcomeVerifier(max_attempts=1, interval_seconds=0)
    check = verifier.verify(_focused_mdl_run(SimpleNamespace(), released=False))
    assert check.passed is False
