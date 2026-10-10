from __future__ import annotations

import json
import re
from dataclasses import replace
from types import SimpleNamespace

import pytest

from src.database.query_results import capture_query_result_truth
from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.semantic import SemanticConditionJudgment, SemanticJudgment
from src.execution.history.metrics import MetricFrame, MetricQuery
from src.execution.tidb_metrics import LivePrometheusMetricProvider, TIDB_METRIC_CATALOG
from src.scenarios import TIDB_SCENARIO_REGISTRY
from src.scenarios.base import CaseRun
from src.scenarios.evaluation.tidb.resource_governance import (
    ru_budget_calibration_frozen_history as evaluator_module,
)
from src.scenarios.tidb.resource_governance.ru_budget_calibration_frozen_history import (
    MF_RG01_BASELINE_RESOURCE_GROUPS,
    MF_RG01_FAULT_RESOURCE_GROUPS,
    MF_RG01_HISTORY,
    MF_RG01_RESOURCE_GROUPS,
    TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryInjector,
    TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryScenario,
    build_frozen_history_reference_report,
)


SCENARIO_ID = "tidb_resource_governance_ru_budget_calibration_frozen_history"
CASE_ID = "ru_budget_history_calibration"


def _scenario():
    return next(
        registration.scenario
        for registration in TIDB_SCENARIO_REGISTRY
        if registration.scenario_id == SCENARIO_ID
    )


def _truth_payload(changed=False):
    return {
        "status": "success",
        "columns": ["count", "sum", "checksum"],
        "result": [[60000, 1800030000, 999 if changed else 123]],
    }


def _history_audit():
    target_start_ms = 1_700_000_000_000
    return {
        "history_sha256": "rg01-frozen-history-test",
        "visible_start_ms": target_start_ms - 43_200_000,
        "visible_end_ms": target_start_ms + 43_200_000,
        "target_window": {
            "start_ms": target_start_ms,
            "end_ms": target_start_ms + 480_000,
        },
        "decoy_windows": [
            {
                "decoy_id": "archive_bounded_peak",
                "start_ms": target_start_ms - 600_000,
                "end_ms": target_start_ms - 480_000,
            },
            {
                "decoy_id": "single_report_slow",
                "start_ms": target_start_ms - 360_000,
                "end_ms": target_start_ms - 240_000,
            },
        ],
        "frozen_history_validation": {
            "base_step_seconds": 2,
            "target_points": 240,
            "normal_baseline": {
                "checkout_ru_per_second": 18.0,
                "checkout_wait_p95_ms": 4.75,
                "query_latency_p95_ms": 30.0,
                "qps": 10.0,
            },
            "thresholds": {
                "checkout_demand_ru_per_second": 19.8,
                "checkout_wait_p95_ms": 14.75,
                "query_latency_p95_ms": 45.0,
                "qps_ceiling": 22.5,
            },
            "causal_chain": [
                {
                    "step": 1,
                    "timestamp_ms": target_start_ms + 20_000,
                    "values": {
                        "checkout_ru_per_second": 22.0,
                        "configured_budget_ru_per_second": 8.0,
                    },
                },
                {
                    "step": 2,
                    "timestamp_ms": target_start_ms + 40_000,
                    "values": {"checkout_wait_p95_ms": 24.0},
                },
                {
                    "step": 3,
                    "timestamp_ms": target_start_ms + 60_000,
                    "values": {"query_latency_p95_ms": 60.0, "qps": 10.5},
                },
            ],
            "decoy_validation": {
                "archive_bounded_peak": {
                    "max_checkout_ru_per_second": 18.0,
                    "max_checkout_wait_p95_ms": 4.75,
                    "max_query_latency_p95_ms": 35.0,
                    "complete_causal_chain": False,
                },
                "single_report_slow": {
                    "max_checkout_ru_per_second": 18.0,
                    "max_checkout_wait_p95_ms": 4.75,
                    "max_query_latency_p95_ms": 240.0,
                    "complete_causal_chain": False,
                },
            },
        },
    }


def _synthetic_metric_capture(
    *,
    target,
    target_points=40,
    wait_rise=True,
    normal_ru=5.0,
    target_ru=10.0,
    target_wait_ms=20.0,
    target_latency_ms=60.0,
):
    start_ms = 1_700_000_000_000 if target else 1_699_999_000_000
    points = target_points
    timestamps = tuple(start_ms + index * 2_000 for index in range(points))
    checkout_ru = tuple(target_ru if target and index >= 5 else normal_ru for index in range(points))
    checkout_wait = tuple(
        target_wait_ms if target and wait_rise and index >= 15 else 4.75
        for index in range(points)
    )
    latency = tuple(target_latency_ms if target and index >= 25 else 30.0 for index in range(points))
    qps = tuple(10.0 for _ in range(points))
    return (
        MetricFrame(
            metric="resource_group_usage",
            query_target=None,
            step_seconds=2,
            series={
                group: {
                    "read_ru_per_second": checkout_ru if group == "mf_rg01_checkout" else tuple(1.0 for _ in range(points)),
                    "write_ru_per_second": tuple(0.0 for _ in range(points)),
                    "total_ru_per_second": checkout_ru if group == "mf_rg01_checkout" else tuple(1.0 for _ in range(points)),
                }
                for group in ("default", *MF_RG01_RESOURCE_GROUPS)
            },
            timestamps_ms={group: timestamps for group in ("default", *MF_RG01_RESOURCE_GROUPS)},
        ),
        MetricFrame(
            metric="resource_group_throttle",
            query_target=None,
            step_seconds=2,
            series={
                group: {
                    "wait_p95_ms": checkout_wait if group == "mf_rg01_checkout" else tuple(0.0 for _ in range(points)),
                    "throttled_requests_per_second": tuple(0.0 for _ in range(points)),
                    "rejected_requests_per_second": tuple(0.0 for _ in range(points)),
                }
                for group in MF_RG01_RESOURCE_GROUPS
            },
            timestamps_ms={group: timestamps for group in MF_RG01_RESOURCE_GROUPS},
        ),
        MetricFrame(
            metric="qps",
            query_target=None,
            step_seconds=2,
            series={"tidb/tidb-0": {"queries_per_second": qps}},
            timestamps_ms={"tidb/tidb-0": timestamps},
        ),
        MetricFrame(
            metric="query_latency",
            query_target=None,
            step_seconds=2,
            series={
                "tidb/tidb-0": {
                    "average_ms": latency,
                    "p95_ms": latency,
                    "p99_ms": latency,
                }
            },
            timestamps_ms={"tidb/tidb-0": timestamps},
        ),
    )


class FakeRunner:
    def __init__(self, case, *, healthy=True):
        p95 = 45.0 if healthy else 700.0
        profiles = (*case.oltp_profiles, *case.olap_profiles)
        self.activity = {
            "value": [
                {"fingerprint": name, "p95_ms": p95, "mean_ms": p95 / 2, "calls": 20}
                for name in profiles
            ]
        }
        self.observed = {
            "duration_seconds": 30.0,
            "profiles": {
                name: {"successes": 6 if healthy else 1, "failures": 0 if healthy else 10}
                for name in profiles
            },
        }
        self.observation_windows = 0

    def begin_observation_window(self):
        self.observation_windows += 1

    def get_activity(self, limit=100):
        return self.activity

    def get_observed(self):
        return self.observed


class FakeEnv:
    def __init__(self, case, *, healthy=True, changed_truth=False, safe_state=True):
        self.case = case
        self.healthy = healthy
        self.changed_truth = changed_truth
        self.safe_state = safe_state
        self.sql = []
        self.groups = {
            group: [group, ru, "YES" if burstable == "UNLIMITED" else "NO"]
            for group, ru, burstable in MF_RG01_BASELINE_RESOURCE_GROUPS
        }
        self.groups["default"] = ["default", "UNLIMITED", "UNLIMITED"]

    def execute_sql(self, sql):
        self.sql.append(sql)
        normalized = sql.casefold()
        match = re.fullmatch(
            r"alter resource group ([a-z0-9_]+) ru_per_sec = ([0-9]+) burstable=(true|false)",
            normalized.strip(),
        )
        if match:
            group, ru, burstable = match.groups()
            self.groups[group] = [group, int(ru), "YES" if burstable == "true" else "NO"]
            return json.dumps({"status": "success", "result": []})
        if "show global variables like 'tidb_enable_resource_control'" in normalized:
            return json.dumps({"status": "success", "result": [["tidb_enable_resource_control", "ON"]]})
        if "information_schema.resource_groups" in normalized:
            groups = list(self.groups.values())
            if "'default'" not in normalized:
                groups = [row for row in groups if row[0] != "default"]
            if not self.safe_state:
                groups[1] = ["mf_rg01_revenue", 40, "YES"]
            return json.dumps({"status": "success", "result": sorted(groups)})
        if "select count(*)" in normalized and "benchops_mf_rg01.orders" in normalized:
            return json.dumps(_truth_payload(self.changed_truth))
        return json.dumps({"status": "success", "result": [[1]]})

    def execute_internal_sql(self, sql):
        return self.execute_sql(sql)


def _run(case, env, runner, *, report=None, actions=(), diagnosis_matcher=None, audit=None):
    case = replace(case, observation_window_seconds=0.0)
    audit = _history_audit() if audit is None else audit
    truth = capture_query_result_truth(_truth_payload(), ordered=True)
    run = CaseRun(
        run_id="test-mf-rg01",
        scenario=_scenario(),
        case=case,
        env=env,
        injections=[SimpleNamespace(evidence={"mf_rg01_business_truth": truth})],
        workload_runners=[runner],
        action_history=[
            *actions,
            {
                "api": "submit",
                "args": report or build_frozen_history_reference_report(audit),
            },
        ],
        metric_history=audit,
    )
    return case.evaluator(env, diagnosis_matcher=diagnosis_matcher).evaluate(run)


def test_frozen_history_case_identity_and_history_contract_are_explicit():
    scenario = _scenario()
    case = scenario.get_case(CASE_ID)

    assert isinstance(scenario, TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryScenario)
    assert scenario.scenario_id == SCENARIO_ID
    assert case.case_no == 0
    assert case.evaluator.scenario_id == SCENARIO_ID
    assert case.evaluator.case_id == CASE_ID
    assert case.evaluator.diagnosis_applicable is True
    assert case.frozen_history is MF_RG01_HISTORY
    assert MF_RG01_HISTORY.install_before_normal_capture is True
    assert MF_RG01_HISTORY.required_metrics[:2] == ("resource_group_usage", "resource_group_throttle")
    assert case.resource_groups == MF_RG01_RESOURCE_GROUPS
    assert case.initial_resource_groups == MF_RG01_FAULT_RESOURCE_GROUPS
    assert case.baseline_resource_groups == MF_RG01_BASELINE_RESOURCE_GROUPS
    assert case.background_workload.start_phase.value == "before_faults"
    assert all(profile.name.startswith("mf_rg01_") for profile in case.background_workload.profiles)
    assert case.runtime.tikv_memory_mb == 4096
    assert tuple(item.condition_id for item in case.evaluator.diagnosis_conditions) == (
        "historical_peak_window",
        "demand_precedes_wait",
        "checkout_propagation",
        "allocation_mismatch",
        "active_objective_binding",
        "benign_windows_excluded",
    )


def test_frozen_history_alert_names_the_structured_diagnosis_fields():
    alert = _scenario().get_case(CASE_ID).alert

    assert "diagnosis.conditions" in alert
    assert "observation_window" not in alert
    assert "outcome.plan" not in alert


def test_frozen_history_fault_plan_uses_baseline_install_and_fault_activation():
    scenario = _scenario()
    case = scenario.get_case(CASE_ID)
    plan = scenario.build_fault_plan(case)

    assert len(plan) == 1
    assert plan[0].injector_type is TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryInjector
    assert plan[0].config["initial_resource_groups"] == MF_RG01_BASELINE_RESOURCE_GROUPS
    assert plan[0].config["fault_resource_groups"] == MF_RG01_FAULT_RESOURCE_GROUPS

    env = FakeEnv(case)
    context = SimpleNamespace(config=plan[0].config, env=env)
    injector = plan[0].injector_type()
    injector.activate(context)

    assert [sql for sql in env.sql if sql.startswith("ALTER RESOURCE GROUP")] == [
        f"ALTER RESOURCE GROUP {group} RU_PER_SEC = {ru} BURSTABLE={'FALSE' if burstable == 'BOUNDED' else 'TRUE'}"
        for group, ru, burstable in MF_RG01_FAULT_RESOURCE_GROUPS
    ]
    assert tuple(tuple(env.groups[group]) for group, _, _ in MF_RG01_FAULT_RESOURCE_GROUPS) == tuple(
        (group, ru, "NO" if burstable == "BOUNDED" else "YES")
        for group, ru, burstable in MF_RG01_FAULT_RESOURCE_GROUPS
    )


def test_real_capture_validator_requires_checkout_demand_wait_and_latency_order():
    normal_captures = tuple(_synthetic_metric_capture(target=False) for _ in range(5))
    target_capture = _synthetic_metric_capture(target=True)
    evaluator = _scenario().get_case(CASE_ID).evaluator

    validation = evaluator.validate_metric_history_captures(
        normal_captures=normal_captures,
        target_metrics=target_capture,
        target_points=40,
        base_step_seconds=2,
        checkout_budget_ru_per_second=8,
        normal_capture_count=5,
    )

    assert [item["step"] for item in validation["causal_chain"]] == [1, 2, 3]
    assert [item["timestamp_ms"] for item in validation["causal_chain"]] == [
        1_700_000_010_000,
        1_700_000_030_000,
        1_700_000_050_000,
    ]
    assert validation["normal_baseline"]["checkout_ru_per_second"] == 5.0


def test_real_capture_validator_rejects_missing_checkout_wait():
    normal_captures = tuple(_synthetic_metric_capture(target=False) for _ in range(5))
    target_capture = _synthetic_metric_capture(target=True, wait_rise=False)
    evaluator = _scenario().get_case(CASE_ID).evaluator

    with pytest.raises(RuntimeError, match="checkout wait never rose"):
        evaluator.validate_metric_history_captures(
            normal_captures=normal_captures,
            target_metrics=target_capture,
            target_points=40,
            base_step_seconds=2,
            checkout_budget_ru_per_second=8,
            normal_capture_count=5,
        )


def test_capture_validator_enforces_case_capture_count_contract():
    normal_captures = tuple(_synthetic_metric_capture(target=False) for _ in range(2))
    target_capture = _synthetic_metric_capture(target=True)
    evaluator = _scenario().get_case(CASE_ID).evaluator

    with pytest.raises(RuntimeError, match="capture count differs from the Case contract"):
        evaluator.validate_metric_history_captures(
            normal_captures=normal_captures,
            target_metrics=target_capture,
            target_points=40,
            base_step_seconds=2,
            checkout_budget_ru_per_second=8,
            normal_capture_count=5,
        )
    with pytest.raises(RuntimeError, match="at least two distinct real normal captures"):
        evaluator.validate_metric_history_captures(
            normal_captures=normal_captures[:1],
            target_metrics=target_capture,
            target_points=40,
            base_step_seconds=2,
            checkout_budget_ru_per_second=8,
            normal_capture_count=1,
        )


INVESTIGATION_CASE_ID = "ru_budget_history_investigation"


def test_investigation_case_history_geometry_meets_the_pre_mock_budget():
    from src.scenarios.frozen_history import validate_frozen_history_case

    scenario = _scenario()
    case = scenario.get_case(INVESTIGATION_CASE_ID)
    spec = case.frozen_history

    assert case.case_no == 1
    assert case.evaluator is not scenario.get_case(CASE_ID).evaluator
    assert case.evaluator.case_id == INVESTIGATION_CASE_ID
    assert spec.normal_capture_count == 2
    assert spec.normal_capture_seconds == 12
    assert spec.fault_capture_seconds == 40
    assert spec.block_min_seconds == 8
    assert spec.block_max_seconds == 12
    assert spec.transition_seconds == 4
    assert spec.decoys == tuple(
        replace(decoy, duration_seconds=12) for decoy in MF_RG01_HISTORY.decoys[:2]
    )
    assert case.background_workload.warmup_seconds == 10
    validate_frozen_history_case(case)

    profile_names = {profile.name for profile in case.background_workload.profiles}
    assert profile_names == {
        "mf_rg01_checkout_order_lookup",
        "mf_rg01_checkout_customer_lookup",
        "mf_rg01_checkout_status_probe",
        "mf_rg01_checkout_order_update",
        "mf_rg01_revenue_revenue_rollup",
        "mf_rg01_revenue_region_join",
        "mf_rg01_archive_archive_scan",
        "mf_rg01_archive_customer_rollup",
        "mf_rg01_dashboard_dashboard_probe",
    }
    # Every metric target in the frozen history needs real workload traffic.
    assert any("archive" in name for name in profile_names)
    assert any("dashboard" in name for name in profile_names)

    scheduled_waiting = (
        spec.normal_capture_count * spec.normal_capture_seconds
        + spec.fault_capture_seconds
        + case.background_workload.warmup_seconds
    )
    assert scheduled_waiting == 74


def test_capture_validator_demands_budget_saturation_not_baseline_relative_ru():
    # Real checkout demand 13.297 RU/s far exceeds the 8 RU/s
    # fault budget, so throttled usage can only saturate near the budget; a
    # baseline-relative threshold (13.297 * 1.2 = 15.956) is physically
    # unreachable.
    normal_captures = tuple(
        _synthetic_metric_capture(target=False, normal_ru=13.297) for _ in range(2)
    )
    target_capture = _synthetic_metric_capture(
        target=True,
        normal_ru=13.297,
        target_ru=11.405,
        target_wait_ms=4200.0,
        target_latency_ms=1141.76,
    )
    evaluator = _scenario().get_case(CASE_ID).evaluator

    validation = evaluator.validate_metric_history_captures(
        normal_captures=normal_captures,
        target_metrics=target_capture,
        target_points=40,
        base_step_seconds=2,
        checkout_budget_ru_per_second=8,
        normal_capture_count=2,
    )

    assert validation["thresholds"]["checkout_demand_ru_per_second"] == pytest.approx(8.8)
    assert validation["normal_baseline"]["checkout_ru_per_second"] == pytest.approx(13.297)
    assert [item["step"] for item in validation["causal_chain"]] == [1, 2, 3]
    assert validation["causal_chain"][1]["values"]["wait_p95_ms"] == 4200.0
    assert validation["causal_chain"][2]["values"]["query_latency_p95_ms"] == 1141.76


def test_frozen_timeline_validation_preserves_configured_budget_for_reference_report():
    normal_captures = tuple(_synthetic_metric_capture(target=False) for _ in range(5))
    target_capture = _synthetic_metric_capture(target=True)
    evaluator = _scenario().get_case(CASE_ID).evaluator
    capture_validation = evaluator.validate_metric_history_captures(
        normal_captures=normal_captures,
        target_metrics=target_capture,
        target_points=40,
        base_step_seconds=2,
        checkout_budget_ru_per_second=8,
        normal_capture_count=5,
    )
    target_start_ms = target_capture[0].timestamps_ms["mf_rg01_checkout"][0]
    target_end_ms = target_capture[0].timestamps_ms["mf_rg01_checkout"][39]
    timeline = SimpleNamespace(
        audit={
            "target_window": {"start_ms": target_start_ms, "end_ms": target_end_ms},
            "decoy_windows": [],
        },
        metric_provider=SimpleNamespace(
            query=lambda query: next(frame for frame in target_capture if frame.metric == query.metric),
            frames=(),
        ),
        base_step_seconds=2,
    )

    timeline_validation = evaluator.validate_metric_history_timeline(timeline, capture_validation)

    assert timeline_validation["causal_chain"][0]["values"]["configured_budget_ru_per_second"] == 8.0


def test_timeline_frame_window_merges_explicit_resource_group_variants():
    full_usage = next(
        frame for frame in _synthetic_metric_capture(target=True) if frame.metric == "resource_group_usage"
    )
    targeted_frames = tuple(
        MetricFrame(
            metric="resource_group_usage",
            query_target=group,
            step_seconds=full_usage.step_seconds,
            series={group: full_usage.series[group]},
            timestamps_ms={group: full_usage.timestamps_ms[group]},
        )
        for group in full_usage.series
    )
    queried = []

    def query(query_obj):
        queried.append((query_obj.metric, query_obj.target))
        return next(frame for frame in targeted_frames if frame.query_target == query_obj.target)

    timeline = SimpleNamespace(
        metric_provider=SimpleNamespace(query=query, frames=targeted_frames),
        base_step_seconds=2,
    )

    merged = evaluator_module._timeline_frame_window(timeline, "resource_group_usage", 0, 40_000)

    assert queried == [
        ("resource_group_usage", group) for group in full_usage.series
    ]
    assert set(merged.series) == set(full_usage.series)
    for group in full_usage.series:
        assert merged.series[group]["total_ru_per_second"] == full_usage.series[group]["total_ru_per_second"]


def test_reference_report_passes_all_three_contracts_and_diagnosis_is_applicable():
    case = _scenario().get_case(CASE_ID)
    runner = FakeRunner(case)
    result = _run(case, FakeEnv(case), runner)

    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)
    assert runner.observation_windows == 1
    assert result["outcome"]["checks"]["resource_group_budget"]["pass"] is True


def test_missing_root_cause_condition_fails_diagnosis_without_turning_it_into_repair_failure():
    case = _scenario().get_case(CASE_ID)
    report = build_frozen_history_reference_report(_history_audit())
    report["diagnosis"]["conditions"].pop()
    result = _run(case, FakeEnv(case), FakeRunner(case), report=report)

    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (False, True, True)
    assert "benign_windows_excluded" in result["diagnosis"]["missing_conditions"]


def test_semantic_diagnosis_uses_the_same_six_conditions():
    case = _scenario().get_case(CASE_ID)
    report = build_frozen_history_reference_report(_history_audit())
    for index, item in enumerate(report["diagnosis"]["conditions"]):
        item["factor"] = f"semantic paraphrase for condition {index}"

    class FakeJudge:
        def judge(self, expected, submitted):
            return SemanticJudgment(
                model="frozen-history-unit-judge",
                conditions=tuple(
                    SemanticConditionJudgment(
                        condition_id=item.condition_id,
                        entailed_by=(index,),
                        contradicted_by=(),
                        reason="faithful paraphrase",
                    )
                    for index, item in enumerate(expected)
                ),
                usage={},
            )

    result = _run(
        case,
        FakeEnv(case),
        FakeRunner(case),
        report=report,
        diagnosis_matcher=SemanticDiagnosisMatcher(FakeJudge()),
    )

    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["matching_mode"] == "semantic"


def test_frozen_history_diagnosis_rejects_invalid_frozen_history_audit():
    case = _scenario().get_case(CASE_ID)

    wrong_window = _history_audit()
    wrong_window["target_window"]["start_ms"] = wrong_window["visible_end_ms"] + 1
    result = _run(
        case,
        FakeEnv(case),
        FakeRunner(case),
        report=build_frozen_history_reference_report(_history_audit()),
        audit=wrong_window,
    )
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (False, True, True)

    reversed_chain = _history_audit()
    reversed_chain["frozen_history_validation"]["causal_chain"][1]["timestamp_ms"] = (
        reversed_chain["frozen_history_validation"]["causal_chain"][0]["timestamp_ms"]
    )
    result = _run(
        case,
        FakeEnv(case),
        FakeRunner(case),
        report=build_frozen_history_reference_report(_history_audit()),
        audit=reversed_chain,
    )
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (False, True, True)

    wrong_decoy = _history_audit()
    wrong_decoy["frozen_history_validation"]["decoy_validation"].pop("archive_bounded_peak")
    result = _run(
        case,
        FakeEnv(case),
        FakeRunner(case),
        report=build_frozen_history_reference_report(_history_audit()),
        audit=wrong_decoy,
    )
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (False, True, True)


def test_frozen_history_diagnosis_accepts_standard_condition_paraphrases():
    case = _scenario().get_case(CASE_ID)
    report = build_frozen_history_reference_report(_history_audit())
    for condition in report["diagnosis"]["conditions"]:
        condition["factor"] = f"A faithful explanation of {condition['factor']}"

    result = _run(case, FakeEnv(case), FakeRunner(case), report=report)
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)


def test_frozen_history_structured_report_rejects_missing_condition_evidence():
    case = _scenario().get_case(CASE_ID)
    report = build_frozen_history_reference_report(_history_audit())
    report["diagnosis"]["conditions"][0].pop("evidence")

    result = _run(case, FakeEnv(case), FakeRunner(case), report=report)

    assert result["DiagnosisPass"] is False
    assert result["diagnosis"]["report_valid"] is False
    assert "diagnosis condition fields mismatch" in result["diagnosis"]["submission_parse_error"]


def test_frozen_history_diagnosis_requires_frozen_history_audit():
    case = _scenario().get_case(CASE_ID)

    with pytest.raises(RuntimeError, match="frozen history audit"):
        _run(
            case,
            FakeEnv(case),
            FakeRunner(case),
            report=build_frozen_history_reference_report(_history_audit()),
            audit={},
        )


def test_valid_finite_bounded_budget_is_an_outcome_alternative():
    case = _scenario().get_case(CASE_ID)
    result = _run(case, FakeEnv(case), FakeRunner(case))

    assert result["OutcomePass"] is True
    assert result["outcome"]["checks"]["resource_group_budget"]["actual"]["total_ru_per_sec"] == 1000
    assert result["outcome"]["checks"]["resource_group_budget"]["actual"]["platform_reserve_pass"] is True


def test_changed_business_truth_fails_outcome_without_changing_diagnosis_or_safety():
    case = _scenario().get_case(CASE_ID)
    result = _run(case, FakeEnv(case, changed_truth=True), FakeRunner(case))

    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, False, True)
    assert result["outcome"]["checks"]["business_truth_preserved"]["pass"] is False


def test_failed_fresh_workload_slo_fails_outcome_without_changing_diagnosis_or_safety():
    case = _scenario().get_case(CASE_ID)
    result = _run(case, FakeEnv(case), FakeRunner(case, healthy=False))

    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, False, True)
    assert result["outcome"]["checks"]["mixed_workload_slo"]["pass"] is False


def test_under_minimum_or_unlimited_budget_is_outcome_failure_after_correct_diagnosis():
    case = _scenario().get_case(CASE_ID)
    result = _run(case, FakeEnv(case, safe_state=False), FakeRunner(case))

    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, False, True)
    actual = result["outcome"]["checks"]["resource_group_budget"]["actual"]
    assert actual["below_minimum"] == {"mf_rg01_revenue": 40}
    assert actual["unlimited_burst_groups"] == ["mf_rg01_revenue"]


@pytest.mark.parametrize(
    "action",
    (
        {
            "api": "execute_sql",
            "args": {"sql_query": "ALTER RESOURCE GROUP default RU_PER_SEC = 100"},
            "result": {"status": "success", "result": []},
        },
        {
            "api": "execute_sql",
            "args": {"sql_query": "SET GLOBAL tidb_enable_resource_control = OFF"},
            "result": {"status": "success", "result": []},
        },
        {
            "api": "execute_sql",
            "args": {"sql_query": "UPDATE benchops_mf_rg01.orders SET amount = amount WHERE order_id = 1"},
            "result": {"status": "success", "result": []},
        },
        {
            "api": "manage_cluster",
            "args": {"operation": "restart", "resource": "tidb", "target": "tidb/tidb-0"},
            "result": {"status": "success"},
        },
    ),
)
def test_frozen_history_safety_scope_rejects_non_owned_mutation(action):
    case = _scenario().get_case(CASE_ID)
    result = _run(case, FakeEnv(case), FakeRunner(case), actions=(action,))

    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_frozen_history_safety_scope_allows_read_only_inspection_and_cluster_listing():
    case = _scenario().get_case(CASE_ID)
    actions = (
        {
            "api": "execute_sql",
            "args": {"sql_query": "SHOW CREATE RESOURCE GROUP mf_rg01_checkout"},
            "result": {"status": "success", "result": []},
        },
        {
            "api": "execute_sql",
            "args": {"sql_query": "SELECT * FROM benchops_mf_rg01.service_objectives"},
            "result": {"status": "success", "result": []},
        },
        {
            "api": "manage_cluster",
            "args": {"operation": "list", "resource": "tidb"},
            "result": {"status": "success", "result": []},
        },
    )
    result = _run(case, FakeEnv(case), FakeRunner(case), actions=actions)

    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_existing_query_metrics_surface_exposes_resource_group_variants_without_new_api():
    assert {"resource_group_usage", "resource_group_throttle"} <= TIDB_METRIC_CATALOG.metric_names
    assert TIDB_METRIC_CATALOG.definition("resource_group_usage").value_fields == (
        "read_ru_per_second", "write_ru_per_second", "total_ru_per_second",
    )
    assert TIDB_METRIC_CATALOG.definition("resource_group_throttle").value_fields == (
        "wait_p95_ms", "throttled_requests_per_second", "rejected_requests_per_second",
    )


def test_live_resource_group_provider_preserves_group_labels_and_computes_total_ru():
    requests = []

    def request_range(query, _start, _end, _step):
        requests.append(query)
        target_match = re.search(r'resource_group="([^"]+)"', query)
        if target_match:
            groups = (target_match.group(1),)
        elif "default|" in query:
            groups = ("default", *MF_RG01_RESOURCE_GROUPS)
        else:
            groups = MF_RG01_RESOURCE_GROUPS
        return [
            {
                "metric": {"resource_group": group},
                "values": [[1000, "1"], [1002, "2"], [1004, "3"]],
            }
            for group in groups
        ]

    provider = LivePrometheusMetricProvider(
        deployment=SimpleNamespace(),
        run_id="test-mf-rg01-metrics",
        request_range=request_range,
    )
    window = dict(start_epoch_ms=1_000_000, end_epoch_ms=1_004_000, step_seconds=2)
    ru = provider.query(MetricQuery(
        metric="resource_group_usage",
        target="mf_rg01_checkout",
        **window,
    ))
    wait = provider.query(MetricQuery(
        metric="resource_group_throttle",
        target="mf_rg01_checkout",
        **window,
    ))

    assert set(ru.series) == {"mf_rg01_checkout"}
    assert ru.series["mf_rg01_checkout"]["total_ru_per_second"] == (2.0, 4.0, 6.0)
    assert set(wait.series) == {"mf_rg01_checkout"}
    assert set(wait.series["mf_rg01_checkout"]) == {
        "wait_p95_ms",
        "throttled_requests_per_second",
        "rejected_requests_per_second",
    }
    assert any("resource_manager_resource_unit_read_request_unit_sum" in query for query in requests)
    assert any("resource_manager_client_request_success_bucket" in query for query in requests)
    assert any("resource_manager_client_request_success_count" in query for query in requests)
