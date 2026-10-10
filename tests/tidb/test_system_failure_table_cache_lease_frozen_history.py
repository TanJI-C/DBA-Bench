import inspect
from pathlib import Path

from src.scenarios.evaluation.protocol import EvaluationContext, StructuredReport
from src.scenarios.base import CaseRun
from src.scenarios.tidb import SCENARIO_REGISTRY
from src.scenarios.tidb.system_failure.table_cache_lease_frozen_history import (
    _REFERENCE_REPORT,
    _ORDERS_PHASE_PROBE_COUNT,
    TidbSystemFailureTableCacheLeaseFrozenHistoryInjector,
    TidbSystemFailureTableCacheLeaseFrozenHistoryScenario,
)


SCENARIO_ID = "tidb_system_failure_table_cache_lease_frozen_history"
CASE_ID = "table_cache_lease_history_investigation"
SCENARIO = TidbSystemFailureTableCacheLeaseFrozenHistoryScenario()
CASE = SCENARIO.get_case(CASE_ID)


def test_case_identity_registry_history_contract_and_provisional_hard_target():
    registration = next(item for item in SCENARIO_REGISTRY if item.scenario_id == SCENARIO_ID)
    plan = SCENARIO.build_fault_plan(CASE)[0]

    assert registration.entrypoint == "run_tidb_system_failure_table_cache_lease_frozen_history_scenario.py"
    assert CASE.evaluator.scenario_id == SCENARIO_ID
    assert CASE.evaluator.case_id == CASE_ID
    assert CASE.case_no == 0
    assert CASE.frozen_history.duration_seconds == 12 * 60 * 60
    assert CASE.frozen_history.base_step_seconds == 60
    assert CASE.frozen_history.required_metrics == (
        "cpu",
        "disk_io",
        "qps",
        "query_latency",
        "active_connections",
    )
    assert dict(CASE.frozen_history.metric_targets) == {
        "cpu": (
            "tidb/tidb-0",
            "tidb/tidb-1",
            "tikv/tikv-0",
            "tikv/tikv-1",
            "tikv/tikv-2",
        ),
        "disk_io": ("tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"),
        "qps": (None,),
        "query_latency": (None,),
        "active_connections": (None,),
    }
    assert CASE.background_workload.warmup_seconds == 180
    assert _ORDERS_PHASE_PROBE_COUNT == 420
    assert CASE.runtime.readiness_timeout_seconds == 3600
    assert "cache-policy" not in CASE.alert
    assert "table-cache-lease" not in CASE.alert
    auxiliary_profiles = {
        profile.name: profile
        for profile in CASE.background_workload.profiles
        if profile.name.startswith("aux_catalog_")
    }
    assert set(auxiliary_profiles) == {
        "aux_catalog_lookup",
        "aux_catalog_rollup",
        "aux_catalog_point_probe",
    }
    assert all(profile.target == "tidb/tidb-0" for profile in auxiliary_profiles.values())
    assert CASE.frozen_history.record_sources
    decoys = {decoy.decoy_id: decoy for decoy in CASE.frozen_history.decoys}
    assert decoys["orders-9007-window"].kind.value == "metric_only"
    assert decoys["orders-9007-window"].metric == "query_latency"
    assert decoys["orders-9007-window"].field == "p95_ms"
    assert decoys["single-endpoint-cache-window"].kind.value == "captured_benign"
    assert decoys["single-endpoint-cache-window"].metric == "query_latency"
    assert decoys["single-endpoint-cache-window"].field == "p95_ms"
    assert decoys["single-endpoint-cache-window"].target is None
    assert decoys["cluster-load-window"].metric == "query_latency"
    assert decoys["cluster-load-window"].field == "p95_ms"
    assert decoys["cluster-load-window"].target is None
    assert decoys["missing-catalog-window"].metric == "query_latency"
    assert decoys["missing-catalog-window"].field == "p95_ms"
    assert decoys["missing-catalog-window"].target is None
    assert plan.config["cache_table_names"] == CASE.cache_table_names
    assert plan.config["healthy_aux_table"] == CASE.healthy_cache_table_names[0]


def test_injector_uses_only_the_current_five_phase_protocol():
    for name in ("install", "activate", "prepare_observability", "quiesce", "recover"):
        assert tuple(inspect.signature(getattr(TidbSystemFailureTableCacheLeaseFrozenHistoryInjector, name)).parameters) == (
            "self",
            "context",
        )


def test_reference_report_contains_the_history_plan_without_changing_structured_protocol():
    StructuredReport.from_mapping(_REFERENCE_REPORT)
    assert _REFERENCE_REPORT["outcome"]["plan"]["incident_window"]
    assert "orders conflict" in _REFERENCE_REPORT["outcome"]["plan"]["timeline"]
    assert _REFERENCE_REPORT["outcome"]["plan"]["repair_family"] == "causal NOCACHE or global tidb_table_cache_lease in 6..30"


def test_exact_dp_accepts_reference_conditions_without_touching_an_environment():
    run = CaseRun(run_id="table-cache-lease-static-dp", scenario=SCENARIO, case=CASE, env=None)
    run.action_history.append({"api": "submit", "args": _REFERENCE_REPORT})
    report = StructuredReport.from_mapping(_REFERENCE_REPORT)
    result = CASE.evaluator(None).DiagnosisPassFunc(EvaluationContext(run, report))

    assert result["DiagnosisPass"] is True
    assert result["missing_conditions"] == []


def test_missing_root_cause_does_not_pass_diagnosis():
    report = {
        "diagnosis": {
            "conditions": [{
                "type": "symptom",
                "factor": "historical 2PC failures",
                "entity": "commerce traffic",
                "evidence": ["the alert mentions Prewrite"],
            }]
        },
        "outcome": {"changes": [], "verification": []},
        "summary": "The failure was not localized.",
    }
    run = CaseRun(run_id="table-cache-lease-static-missing-dp", scenario=SCENARIO, case=CASE, env=None)
    run.action_history.append({"api": "submit", "args": report})
    result = CASE.evaluator(None).DiagnosisPassFunc(EvaluationContext(run, StructuredReport.from_mapping(report)))

    assert result["DiagnosisPass"] is False
    assert "cache_lease_metadata_conflict" in result["critical_missing"]


def test_entrypoint_requires_model_without_version_default():
    source = Path("examples/run_tidb_system_failure_table_cache_lease_frozen_history_scenario.py").read_text()
    assert 'parser.add_argument("--model", required=True, help="LLM model name")' in source
