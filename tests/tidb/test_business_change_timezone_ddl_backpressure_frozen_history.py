import inspect

from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios import TIDB_SCENARIO_REGISTRY
from src.scenarios.tidb import (
    TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryInjector,
    TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryScenario,
)
from src.scenarios.tidb.business_change.timezone_ddl_backpressure_frozen_history import (
    _FROZEN_HISTORY_HISTORY,
)
from src.execution.environment import TiDBEnv


SCENARIO = TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryScenario()
CASE = SCENARIO.get_case("timezone_ddl_backpressure_history_investigation")


def test_identity_registry_and_case_contract():
    registration = next(
        item for item in TIDB_SCENARIO_REGISTRY if item.scenario_id == SCENARIO.scenario_id
    )
    assert registration.category.value == "business_change"
    assert registration.entrypoint == (
        "run_tidb_business_change_timezone_ddl_backpressure_frozen_history_scenario.py"
    )
    assert CASE.case_no == 0
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert CASE.evaluator.case_id == CASE.case_id
    StructuredReport.from_mapping(CASE.reference_report)


def test_frozen_history_and_difficulty_contract_are_static_and_reproducible():
    CASE.frozen_history.validate(CASE.background_workload)
    assert CASE.frozen_history is _FROZEN_HISTORY_HISTORY
    assert CASE.frozen_history.required_metrics == ("qps", "query_latency")
    assert CASE.frozen_history.target_age_seconds_range == (2400, 7200)
    assert CASE.frozen_history.normal_capture_seconds == 600
    assert CASE.frozen_history.fault_capture_seconds == 600
    assert CASE.frozen_history.base_step_seconds == 120
    assert CASE.frozen_history.transition_seconds == 120
    assert CASE.schema_rollout_tables == (
        "mf_cf01_cutover_shadow",
        "mf_cf01_archive_rollup",
    )


def test_fault_plan_contains_only_case_owned_configuration():
    plan = SCENARIO.build_fault_plan(CASE)[0]
    assert plan.injector_type is TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryInjector
    assert set(plan.config) == {
        "source_db",
        "source_table",
        "ddl_table",
        "decoy_table",
        "schema_rollout_tables",
        "changefeed_id",
        "business_trigger",
        "archive_trigger",
        "seeded_rows",
        "post_fault_rows",
        "ddl_delay_seconds",
    }
    assert plan.config["ddl_delay_seconds"] == 180.0


def test_injector_uses_the_current_five_phase_protocol():
    for phase in ("install", "activate", "prepare_observability", "quiesce", "recover"):
        assert tuple(inspect.signature(getattr(TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryInjector, phase)).parameters) == (
            "self",
            "context",
        )


def test_diagnosis_contract_keeps_all_causal_and_scope_conditions_critical():
    condition_ids = tuple(condition.condition_id for condition in CASE.evaluator.diagnosis_conditions)
    assert condition_ids == (
        "historical_target_window",
        "pre_ddl_sink_backpressure",
        "timezone_sensitive_ddl",
        "ddl_checkpoint_block",
        "temporal_cascade",
        "scope_exclusion",
        "post_ddl_dml_preservation",
    )
    assert all(condition.critical for condition in CASE.evaluator.diagnosis_conditions)


def test_frozen_history_public_tools_are_existing_tools_only():
    assert TiDBEnv.FROZEN_HISTORY_PUBLIC_TOOLS == (
        "query_metrics",
        "execute_sql",
        "manage_cluster",
        "read_log",
        "search_knowledge",
        "help",
        "submit",
        "exit",
    )
