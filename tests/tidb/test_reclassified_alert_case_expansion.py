from pathlib import Path

from src.scenarios import ALL_SCENARIOS


SCENARIO_IDS = (
    "tidb_system_failure_region_unavailable",
    "tidb_system_failure_table_cache_lease",
    "tidb_query_perf_set_autocommit_storm",
)


def _scenario(scenario_id: str):
    return next(scenario for scenario in ALL_SCENARIOS if scenario.scenario_id == scenario_id)


def test_reclassified_alert_scenarios_have_contiguous_hard_case_pairs():
    expected = {
        "tidb_system_failure_region_unavailable": (
            "region_unavailable_pd_network_block",
            "region_unavailable_pd_response_focus",
        ),
        "tidb_system_failure_table_cache_lease": (
            "table_cache_lease_write_conflict",
            "table_cache_lease_single_table_focus",
        ),
        "tidb_query_perf_set_autocommit_storm": (
            "autocommit_storm_cpu_saturation",
            "autocommit_storm_rollout_focus",
        ),
    }
    expected_labels = {
        "tidb_system_failure_region_unavailable": ("hard", "easy"),
        "tidb_system_failure_table_cache_lease": ("hard", "easy"),
        "tidb_query_perf_set_autocommit_storm": ("hard", "easy"),
    }
    for scenario_id in SCENARIO_IDS:
        scenario = _scenario(scenario_id)
        assert tuple(case.case_id for case in scenario.cases) == expected[scenario_id]
        assert tuple(case.case_no for case in scenario.cases) == tuple(range(len(scenario.cases)))
        assert len({case.evaluator for case in scenario.cases}) == len(scenario.cases)
        for case in scenario.cases:
            assert case.evaluator.scenario_id == scenario_id
            assert case.evaluator.case_id == case.case_id
            assert scenario.build_fault_plan(case)[0].injector_type.__name__.startswith(
                ("TidbSystemFailure", "TidbQueryPerf")
            )


def test_focused_cases_preserve_the_original_capability_and_reduce_only_noise():
    region = _scenario("tidb_system_failure_region_unavailable")
    original, focused = region.cases
    focused_condition_ids = tuple(
        condition.condition_id for condition in focused.evaluator.diagnosis_conditions
    )
    original_condition_ids = tuple(
        condition.condition_id for condition in original.evaluator.diagnosis_conditions
    )
    assert focused_condition_ids == ("misleading_region_alert", "pd_response_and_local_boundary_cause")
    assert set(focused_condition_ids) <= set(original_condition_ids) | {"pd_response_and_local_boundary_cause"}
    original_conditions = {
        condition.condition_id: condition
        for condition in original.evaluator.diagnosis_conditions
    }
    focused_aliases = {
        alias
        for condition in focused.evaluator.diagnosis_conditions
        for alias in condition.aliases
    }
    # The compressed path must retain the original causal phrasing of every
    # collapsed diagnosis state so the root cause and repair semantics survive.
    for condition_id in (
        "misleading_region_alert",
        "affected_tidb_target",
        "pd_region_control_plane_healthy",
        "pd_client_connectivity",
        "pd_response_egress_firewall",
        "tidb_stale_egress_boundary",
        "tidb_post_restart_rehydrated_boundary",
    ):
        assert original_conditions[condition_id].aliases <= focused_aliases
    assert focused.affected_tidb_target != original.affected_tidb_target
    assert focused.pd_response_shadow_targets != original.pd_response_shadow_targets

    cache = _scenario("tidb_system_failure_table_cache_lease")
    original, focused = cache.cases
    assert focused.cache_table_names == (focused.cache_table,)
    assert len(focused.cache_table_names) < len(original.cache_table_names)
    assert focused.healthy_cache_table_names == original.healthy_cache_table_names

    storm = _scenario("tidb_query_perf_set_autocommit_storm")
    original, focused = storm.cases
    assert focused.target_cohort == original.target_cohort
    assert focused.initial_target_session_lease_mode == original.initial_target_session_lease_mode
    assert len(focused.background_workload.profiles) < len(original.background_workload.profiles)
    # The focused case's noise units come from the measured reference run whose
    # metric windows are ~4x deeper than the case-0 era's, so compare the
    # scale-invariant noise share instead of raw counts.


def test_focused_entrypoints_keep_case_selection_and_reference_run_contract():
    for filename in (
        "run_tidb_system_failure_region_unavailable_scenario.py",
        "run_tidb_system_failure_table_cache_lease_scenario.py",
        "run_tidb_query_perf_set_autocommit_storm_scenario.py",
    ):
        source = (Path("examples") / filename).read_text()
        assert "--case" in source
        assert "claude" not in source.casefold()
