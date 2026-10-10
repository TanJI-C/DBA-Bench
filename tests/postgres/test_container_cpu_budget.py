import json
import math
import subprocess
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.scenarios.evaluation.diagnosis import ExactDiagnosisMatcher
from src.scenarios.evaluation.protocol import EvaluationContext
from src.execution.history.metrics import MetricFrame
from src.execution.history.records import HistoricalRecordSource
from src.scenarios import ALL_SCENARIOS
from src.scenarios.base import CaseRun
from src.scenarios.postgres.resource_governance.container_cpu_budget import (
    CPU_BUDGET_METRICS,
    CpuBudgetController,
    CpuBudgetMetricCatalog,
    CpuBudgetPGEnv,
    EXTERNAL_NEIGHBOR_JOB_ID,
    PgResourceGovernanceContainerCpuBudgetScenario,
    _parse_cpu_max,
    _parse_cpu_stat,
    _parse_psi,
)


def _scenario():
    return next(item for item in ALL_SCENARIOS if item.scenario_id == "pg_resource_governance_container_cpu_budget")


def test_update_container_serializes_cpu_quota_at_docker_nanocpu_precision():
    case = _scenario().cases[1]
    controller = CpuBudgetController(MagicMock(), case, "run-test")
    docker_calls = []
    controller._run_idempotent_docker = lambda command: docker_calls.append(command)
    controller._read_cgroup = lambda _container: {
        "cpu.max": "200000 100000",
        "cpu_max_cores": 0.2,
        "cpu.weight": 1024,
    }

    controller._update_container("postgres", quota=0.19999999999999998)

    assert docker_calls == [["docker", "update", "--cpus", "0.2", "postgres"]]


def _fake_controller(case, *, passed=True, post_fix_throttled_usec=0):
    external_neighbors = {
        job.job_id: {
            "managed": False,
            "running": True,
            "quota_cores": job.reserved_quota_cores,
            "reserved_quota_cores": job.reserved_quota_cores,
        }
        for job in case.external_neighbor_jobs
    }
    return SimpleNamespace(
        job_containers={job.job_id: f"run-{job.job_id}" for job in case.sibling_jobs},
        external_neighbor_containers={job.job_id: f"run-{job.job_id}" for job in case.external_neighbor_jobs},
        external_neighbor_container=f"run-{case.external_neighbor_job_id}",
        final_outcome=lambda: {
            "passed": passed,
            "db_cpu_max_cores": case.reference_db_quota_cores,
            "oltp_p99_ms": 12.0,
            "post_fix_throttled_usec": post_fix_throttled_usec,
            "total_quota_cores": case.host_cpu_budget_cores,
        },
        safety_state=lambda: {
            "db_cpu_max_cores": case.host_cpu_budget_cores - sum(job.minimum_quota_cores for job in case.sibling_jobs),
            "external_neighbors": external_neighbors,
            "jobs": {
                job.job_id: {
                    "running": True,
                    "quota_cores": job.minimum_quota_cores,
                    "minimum_quota_cores": job.minimum_quota_cores,
                }
                for job in case.sibling_jobs
            }
        },
    )


def _evaluate(case, actions):
    env = SimpleNamespace(_cpu_budget_controller=_fake_controller(case))
    scenario = _scenario()
    case_run = CaseRun(run_id="run-test", scenario=scenario, case=case, env=env)
    case_run.action_history.extend(actions)
    evaluator = case.evaluator(env)
    evaluator.capture_safety_baseline(case_run)
    return evaluator.evaluate(case_run)


def test_registration_identity_and_contiguous_case_numbers():
    scenario = _scenario()
    assert scenario.scenario_id == "pg_resource_governance_container_cpu_budget"
    assert [(case.case_no, case.case_id) for case in scenario.cases] == [
        (0, "db_quota_throttle"),
        (1, "db_quota_throttle_simple"),
    ]
    assert all(case.evaluator.scenario_id == scenario.scenario_id for case in scenario.cases)
    assert scenario.build_fault_plan(scenario.cases[0])[0].injector_type.__name__.endswith("Injector")
    assert scenario.cases[0].fault_image_name.startswith("aiopsbench-pg-fault-pg-resource-governance-container-cpu-budget-")


def test_simple_case_uses_public_frozen_history_and_fewer_neighbors():
    case = _scenario().cases[1]
    assert case.frozen_history is not None
    assert case.frozen_history.duration_seconds == 6 * 60 * 60
    assert case.frozen_history.overview_step_seconds == 20
    assert case.frozen_history.transition_seconds == 2
    assert case.frozen_history.duration_seconds // case.frozen_history.overview_step_seconds == 1_080
    assert case.frozen_history.max_points_per_series >= 1_080
    assert case.frozen_history.record_sources == (HistoricalRecordSource.OPERATION_EVENT,)
    assert set(case.frozen_history.required_metrics) == set(CPU_BUDGET_METRICS)
    assert {decoy.decoy_id for decoy in case.frozen_history.decoys} == {
        "post-target-host-busy",
        "pre-target-workload-burst",
        "post-target-db-process-burst",
        "pre-target-db-load-burst",
        "pre-target-planned-quota-window",
        "recent-workload-burst",
        "recent-db-process-burst",
        "db-load-burst",
        "pre-target-backup-load-burst",
        "pre-target-backup-throttle-burst",
        "pre-target-db-throttle-burst",
        "pre-target-sibling-quota-rebalance",
        "pre-target-neighbor-burst",
        "pre-target-host-busy-extended",
    }
    assert case.frozen_history.decoys_adjacent_to_target is True
    assert case.frozen_history.target_age_seconds_range == (10_800, 10_800)
    assert case.initial_db_quota_cores == 0.90
    assert case.fault_db_quota_cores == 0.45
    assert case.recovery_db_quota_cores == 0.90
    assert case.reference_db_quota_cores == 0.90
    assert case.sibling_jobs[0].initial_quota_cores == 0.60
    assert case.sibling_jobs[0].minimum_quota_cores == 0.18
    assert case.reference_sibling_quota_cores == (0.30,)
    assert case.initial_db_weight == 1024
    assert case.fault_db_weight == 256
    planned = next(
        decoy for decoy in case.frozen_history.decoys
        if decoy.decoy_id == "pre-target-planned-quota-window"
    )
    assert planned.metric == "cgroup_cpu_usage"
    assert planned.field == "quota_cores"
    assert planned.target == "entity_3"
    assert planned.direction.value == "dip"
    assert planned.after_target is False
    decoys = {decoy.decoy_id: decoy for decoy in case.frozen_history.decoys}
    assert decoys["post-target-host-busy"].kind.value == "captured_benign"
    assert decoys["pre-target-workload-burst"].metric == "service_slo"
    assert decoys["pre-target-workload-burst"].field == "throughput_per_sec"
    assert decoys["pre-target-workload-burst"].target is None
    assert decoys["pre-target-workload-burst"].after_target is False
    assert decoys["pre-target-workload-burst"].duration_seconds == 60
    assert decoys["pre-target-workload-burst"].minimum_deviation_mad == 0.5
    assert decoys["post-target-db-process-burst"].metric == "process_cpu"
    assert decoys["post-target-db-process-burst"].field == "cpu_percent"
    assert decoys["post-target-db-process-burst"].target == "entity_3"
    assert decoys["post-target-db-process-burst"].after_target is True
    assert decoys["post-target-db-process-burst"].duration_seconds == 20
    assert decoys["post-target-db-process-burst"].minimum_deviation_mad == 0.1
    assert decoys["pre-target-db-load-burst"].metric == "cgroup_cpu_usage"
    assert decoys["pre-target-db-load-burst"].field == "usage_cores"
    assert decoys["pre-target-db-load-burst"].target == "entity_3"
    assert decoys["pre-target-db-load-burst"].after_target is False
    assert decoys["pre-target-db-load-burst"].duration_seconds == 20
    assert decoys["pre-target-db-load-burst"].minimum_deviation_mad == 0.1
    assert decoys["recent-workload-burst"].kind.value == "captured_benign"
    assert decoys["recent-workload-burst"].metric == "service_slo"
    assert decoys["recent-workload-burst"].field == "throughput_per_sec"
    assert decoys["recent-workload-burst"].after_target is True
    assert decoys["recent-workload-burst"].duration_seconds == 60
    assert decoys["recent-workload-burst"].minimum_deviation_mad == 0.5
    assert decoys["recent-db-process-burst"].metric == "process_cpu"
    assert decoys["recent-db-process-burst"].field == "cpu_percent"
    assert decoys["recent-db-process-burst"].target == "entity_3"
    assert decoys["recent-db-process-burst"].after_target is True
    assert decoys["recent-db-process-burst"].duration_seconds == 60
    assert decoys["recent-db-process-burst"].minimum_deviation_mad == 0.1
    assert decoys["pre-target-backup-load-burst"].kind.value == "captured_benign"
    assert decoys["pre-target-backup-load-burst"].metric == "cgroup_cpu_usage"
    assert decoys["pre-target-backup-load-burst"].field == "usage_cores"
    assert decoys["pre-target-backup-load-burst"].target == "entity_1"
    assert decoys["pre-target-backup-load-burst"].after_target is False
    assert decoys["pre-target-backup-load-burst"].duration_seconds == 20
    assert decoys["pre-target-backup-load-burst"].minimum_deviation_mad == 0.1
    assert decoys["pre-target-backup-throttle-burst"].kind.value == "captured_benign"
    assert decoys["pre-target-backup-throttle-burst"].metric == "cgroup_cpu_throttle"
    assert decoys["pre-target-backup-throttle-burst"].field == "throttled_usec_delta"
    assert decoys["pre-target-backup-throttle-burst"].target == "entity_1"
    assert decoys["pre-target-backup-throttle-burst"].after_target is False
    assert decoys["pre-target-backup-throttle-burst"].duration_seconds == 40
    assert decoys["pre-target-backup-throttle-burst"].minimum_deviation_mad == 0.1
    assert decoys["pre-target-sibling-quota-rebalance"].metric == "cgroup_cpu_usage"
    assert decoys["pre-target-sibling-quota-rebalance"].field == "quota_cores"
    assert decoys["pre-target-sibling-quota-rebalance"].target == "entity_1"
    assert decoys["pre-target-sibling-quota-rebalance"].duration_seconds == 34
    assert decoys["pre-target-neighbor-burst"].metric == "cgroup_cpu_usage"
    assert decoys["pre-target-neighbor-burst"].field == "usage_cores"
    assert decoys["pre-target-neighbor-burst"].target == "entity_2"
    assert decoys["pre-target-neighbor-burst"].duration_seconds == 34
    assert decoys["pre-target-host-busy-extended"].metric == "host_cpu"
    assert decoys["pre-target-host-busy-extended"].field == "usage_percent"
    assert decoys["pre-target-host-busy-extended"].target is None
    assert decoys["pre-target-host-busy-extended"].duration_seconds == 34
    assert {job.job_id for job in case.external_neighbor_jobs} == {"backup_shadow"}
    assert case.evaluator.diagnosis_applicable is True


def test_simple_workload_can_reach_database_quota_before_fault_is_injected():
    case = _scenario().cases[1]
    checkout = next(profile for profile in case.background_workload.profiles if profile.name == "checkout_api")
    hard = _scenario().cases[0]
    hard_checkout = next(profile for profile in hard.background_workload.profiles if profile.name == "checkout_api")

    assert "generate_series(1, 480000)" in checkout.sql
    assert checkout.qps == 1.6
    report = next(profile for profile in case.background_workload.profiles if profile.name == "finance_report")
    assert report.qps == 0.18
    assert "generate_series(1, 40000)" in report.sql
    settlement = next(profile for profile in case.background_workload.profiles if profile.name == "settlement_probe")
    assert settlement.qps == 0.12
    assert "generate_series(1, 180000)" in settlement.sql
    settlement_shadow = next(profile for profile in case.background_workload.profiles if profile.name == "settlement_shadow")
    assert settlement_shadow.qps == 0.02
    assert "generate_series(1, 30000)" in settlement_shadow.sql
    assert "generate_series(1, 60000)" in hard_checkout.sql
    assert case.fault_db_quota_cores < case.initial_db_quota_cores
    assert case.validation_window_seconds == 12.0
    assert case.max_post_fix_db_psi_avg10 == 6.0


def test_hard_case_places_real_competitors_near_a_recent_target():
    case = _scenario().cases[0]
    history = case.frozen_history

    assert history is not None
    assert history.overview_step_seconds == 60
    assert history.target_age_seconds_range == (600, 600)
    assert history.decoys_adjacent_to_target is True
    assert history.record_sources == (
        HistoricalRecordSource.OPERATION_EVENT,
        HistoricalRecordSource.TOPSQL,
    )


def test_hard_case_alert_and_periodic_workload_noise_do_not_reveal_the_metric_path():
    case = _scenario().cases[0]
    profiles = {profile.name: profile for profile in case.background_workload.profiles}

    assert case.alert == "P1 alert: online request performance degraded."
    assert "latency" not in case.alert.casefold()
    assert case.background_workload.worker_count == 6
    assert profiles["checkout_campaign_burst"].activity_period_seconds == 90.0
    assert profiles["checkout_campaign_burst"].activity_active_seconds == 18.0
    assert profiles["inventory_reconciliation_burst"].activity_period_seconds == 120.0
    assert profiles["inventory_reconciliation_burst"].activity_active_seconds == 24.0


def test_hard_case_entity_contract_requires_cross_metric_role_mapping():
    case = _scenario().cases[0]
    controller = CpuBudgetController(MagicMock(), case, "run-hard-contract")
    contract = controller.agent_contract()
    database_alias = controller.agent_entity_aliases["database"]

    assert {item["role"] for item in contract["entity_scope"].values()} == {
        "managed_workload",
        "protected_neighbor",
    }
    # The recovery band, per-entity quota bounds and sibling deadlines are
    # private: the Agent derives entity, amplitude and protection constraints
    # from demand evidence, not from a published answer sheet.
    assert "recovery_db_quota_lower_exclusive_cores" not in contract["public_constraints"]
    assert "recovery_db_quota_upper_bound_cores" not in contract["public_constraints"]
    assert "managed_entity_quota_bounds_cores" not in contract["public_constraints"]
    assert all(
        item["minimum_quota_cores"] is None and item["deadline_seconds"] is None
        for item in contract["entity_scope"].values()
        if item["role"] == "managed_workload"
    )
    assert "statement_summary" in contract["records"]


def test_hard_case_records_only_a_successful_real_sql_competitor():
    case = _scenario().cases[0]
    env = MagicMock()
    env.execute_sql.return_value = json.dumps({
        "status": "success",
        "columns": ["sum", "avg"],
        "result": [[1, 2]],
    })
    controller = CpuBudgetController(env, case, "run-hard-topsql")

    controller._capture_target_sql_competitor()
    record = controller._target_sql_records[0]
    captured = controller.capture_history_records(
        (HistoricalRecordSource.TOPSQL,),
        record.start_ms,
        record.end_ms,
    )

    assert env.execute_sql.call_count == 1
    assert captured.interval_records == (record,)
    assert record.payload["exec_count"] == 1
    assert "generate_series(1, 120000)" in record.payload["sql_text"]


def test_cpu_budget_metric_catalog_exposes_only_raw_public_fields():
    catalog = CpuBudgetMetricCatalog()
    assert catalog.metric_names == CPU_BUDGET_METRICS
    assert catalog.definition("cgroup_cpu_throttle").value_fields == (
        "nr_throttled_delta", "throttled_usec_delta", "pressure_some_percent",
    )
    assert all("shortage" not in field and "recommended" not in field for metric in catalog.metric_names for field in catalog.definition(metric).value_fields)
    catalog.validate_target("process_cpu", "entity_3", MagicMock())
    with pytest.raises(ValueError, match="run-local entity alias"):
        catalog.validate_target("process_cpu", "database", MagicMock())


def test_cpu_budget_contract_publishes_entity_scope_and_outcome_thresholds():
    case = _scenario().cases[1]
    controller = CpuBudgetController(MagicMock(), case, "run-test")
    contract = controller.agent_contract()
    database_alias = controller.agent_entity_aliases["database"]
    sibling_alias = controller.agent_entity_aliases[case.sibling_jobs[0].job_id]
    neighbor_alias = controller.agent_entity_aliases[case.external_neighbor_job_id]

    assert contract["entity_scope"][database_alias] == {
        "role": "database",
        "managed": True,
        "actionable": True,
        "budget_scope": "managed",
        "minimum_quota_cores": None,
        "reserved_quota_cores": None,
        "deadline_seconds": None,
    }
    assert contract["entity_scope"][sibling_alias]["managed"] is True
    assert contract["entity_scope"][sibling_alias]["minimum_quota_cores"] == 0.18
    assert contract["entity_scope"][neighbor_alias]["actionable"] is False
    assert contract["entity_scope"][neighbor_alias]["reserved_quota_cores"] == 0.20
    assert contract["public_constraints"]["managed_budget_scope"] == [database_alias, sibling_alias]
    assert contract["public_constraints"]["excluded_neighbor_scope"] == [neighbor_alias]
    assert contract["public_constraints"]["recovery_db_quota_lower_exclusive_cores"] == 0.45
    assert contract["public_constraints"]["recovery_db_quota_upper_bound_cores"] == 0.90
    assert "healthy_database_scheduling_weight" not in contract["public_constraints"]
    assert contract["public_constraints"]["replay_sampling"] == {
        "sample_interval_seconds": 0.5,
        "summary_semantics": "trusted replay returns the final live sample at the end of the published validation window",
    }
    assert contract["public_constraints"]["outcome_thresholds"] == {
        "host_psi_some_avg10_max": 70.0,
        "db_psi_some_avg10_max": 6.0,
        "post_fix_throttled_usec_max": 1_000_000,
        "oltp_p99_ms_max": 2500.0,
        "oltp_success_ratio_min": 0.90,
        "report_qps_min": 0.08,
    }


def test_simple_case_uses_stable_public_entity_alias_order():
    case = _scenario().cases[1]
    controller = CpuBudgetController(MagicMock(), case, "run-test")

    assert controller.agent_entity_aliases[case.sibling_jobs[0].job_id] == "entity_1"
    assert controller.agent_entity_aliases[case.external_neighbor_job_id] == "entity_2"
    assert controller.agent_entity_aliases["database"] == "entity_3"


def test_operation_event_capture_exposes_gap_event_at_target_boundary():
    case = _scenario().cases[1]
    controller = CpuBudgetController(MagicMock(), case, "run-test")
    controller._started = True
    controller._operation_events.append({
        "timestamp_ms": 100,
        "event_type": "quota_revision",
        "entity": "entity_1",
        "old_quota_cores": 0.45,
        "new_quota_cores": 1.0,
        "old_weight": 1024,
        "new_weight": 1024,
        "policy_old_weight": 1024,
        "policy_new_weight": 1024,
        "actor": "fault_injector",
        "message": "bounded CPU policy revision applied",
    })
    captured = controller.capture_history_records((HistoricalRecordSource.OPERATION_EVENT,), 200, 300)
    assert captured.coverage[0].source is HistoricalRecordSource.OPERATION_EVENT
    assert len(captured.point_records) == 1
    assert captured.point_records[0].timestamp_ms == 200
    assert "apply_time_ms" not in captured.point_records[0].payload


def test_operation_event_capture_preserves_same_domain_scheduler_maintenance():
    case = _scenario().cases[1]
    controller = CpuBudgetController(MagicMock(), case, "run-test")
    controller._operation_events.extend([
        {
            "timestamp_ms": 110,
            "event_type": "quota_revision",
            "entity": "entity_3",
            "old_quota_cores": 2.0,
            "new_quota_cores": 1.8,
            "old_weight": 1024,
            "new_weight": 1024,
            "actor": "scheduler",
            "message": "routine bounded CPU policy maintenance started",
        },
        {
            "timestamp_ms": 120,
            "event_type": "quota_revision",
            "entity": "entity_3",
            "old_quota_cores": 1.8,
            "new_quota_cores": 2.0,
            "old_weight": 1024,
            "new_weight": 1024,
            "actor": "scheduler",
            "message": "routine bounded CPU policy maintenance completed",
        },
    ])
    captured = controller.capture_history_records((HistoricalRecordSource.OPERATION_EVENT,), 100, 130)
    assert all("actor" not in record.payload for record in captured.point_records)
    assert all("message" not in record.payload for record in captured.point_records)
    assert all("new_quota_cores" not in record.payload for record in captured.point_records)
    assert [record.payload["entity"] for record in captured.point_records] == ["entity_3", "entity_3"]


def test_recorded_operation_event_keeps_exact_quota_values_out_of_public_payload():
    case = _scenario().cases[1]
    controller = CpuBudgetController(MagicMock(), case, "run-test")
    controller._record_operation_event(
        event_type="quota_revision",
        entity="database",
        old_quota=2.0,
        new_quota=0.45,
        old_weight=1024,
        new_weight=1024,
        actor="fault_injector",
    )
    event = controller._operation_events[-1]
    assert "old_quota_cores" not in event
    assert "new_quota_cores" not in event
    assert event["_audit_old_quota_cores"] == 2.0
    assert event["_audit_new_quota_cores"] == 0.45


def test_operation_event_public_payload_has_no_provenance_shortcut():
    case = _scenario().cases[1]
    controller = CpuBudgetController(MagicMock(), case, "run-test")
    controller._operation_events.append({
        "timestamp_ms": 100,
        "event_type": "quota_revision",
        "entity": "entity_3",
        "old_weight": 1024,
        "new_weight": 1024,
        "_audit_actor": "fault_injector",
        "_audit_message": "bounded CPU policy revision applied",
        "_audit_old_quota_cores": 2.0,
        "_audit_new_quota_cores": 0.45,
    })
    captured = controller.capture_history_records((HistoricalRecordSource.OPERATION_EVENT,), 90, 110)
    assert captured.point_records[0].payload == {
        "event_type": "quota_revision",
        "entity": "entity_3",
        "old_weight": 1024,
        "new_weight": 1024,
    }


def test_operation_event_exposes_policy_and_effective_weight_units():
    case = _scenario().cases[1]
    controller = CpuBudgetController(MagicMock(), case, "run-test")
    controller._record_operation_event(
        event_type="quota_revision",
        entity="database",
        old_quota=case.initial_db_quota_cores,
        new_quota=case.fault_db_quota_cores,
        old_weight=39,
        new_weight=10,
        policy_old_weight=case.initial_db_weight,
        policy_new_weight=case.fault_db_weight,
        actor="fault_injector",
    )
    timestamp_ms = controller._operation_events[-1]["timestamp_ms"]

    captured = controller.capture_history_records(
        (HistoricalRecordSource.OPERATION_EVENT,), timestamp_ms, timestamp_ms + 1,
    )

    assert captured.point_records[0].payload == {
        "event_type": "quota_revision",
        "entity": "entity_3",
        "old_weight": 39,
        "new_weight": 10,
        "policy_old_weight": case.initial_db_weight,
        "policy_new_weight": case.fault_db_weight,
    }


def test_target_policy_maintenance_has_three_finite_reconciliation_delays(monkeypatch):
    case = _scenario().cases[0]
    controller = CpuBudgetController(MagicMock(), case, "run-test")
    waits = []
    cycles = []

    def fake_wait(delay):
        waits.append(delay)
        return False

    monkeypatch.setattr(controller._target_policy_stop, "wait", fake_wait)
    monkeypatch.setattr(controller, "_target_policy_maintenance_cycle", lambda: cycles.append(True))

    controller._target_policy_maintenance()

    assert waits == [8.0, 18.0, 18.0]
    assert len(cycles) == 3


def test_target_policy_maintenance_cycle_uses_short_weight_only_window(monkeypatch):
    case = _scenario().cases[1]
    controller = CpuBudgetController(MagicMock(), case, "run-test")
    controller.job_containers = {"backup_worker": "backup"}
    controller.external_neighbor_containers = {"backup_shadow": "shadow"}
    waits = []
    updates = []
    monkeypatch.setattr(controller, "_read_cgroup", lambda _: {"cpu.weight": 1024, "cpu_max_cores": 0.45})
    def fake_update(*args, **kwargs):
        updates.append(kwargs)
        return {"cpu.weight": 512, "cpu_max_cores": 0.45}
    monkeypatch.setattr(controller, "_update_container", fake_update)
    monkeypatch.setattr(controller._target_policy_stop, "wait", lambda delay: waits.append(delay) or False)
    controller._target_policy_maintenance_cycle()
    assert 0.5 in waits
    assert [item["weight"] for item in updates] == [1023, 1023, 512, 1024]


def test_target_policy_maintenance_never_writes_excluded_neighbor(monkeypatch):
    case = _scenario().cases[0]
    controller = CpuBudgetController(MagicMock(), case, "run-test")
    controller.job_containers = {"backup_worker": "backup"}
    controller.external_neighbor_containers = {"backup_shadow": "shadow"}
    reads = []
    updates = []
    monkeypatch.setattr(
        controller,
        "_read_cgroup",
        lambda target: reads.append(target) or {"cpu.weight": 1024, "cpu_max_cores": 0.45},
    )
    monkeypatch.setattr(
        controller,
        "_update_container",
        lambda target, **kwargs: updates.append((target, kwargs)) or {"cpu.weight": 512, "cpu_max_cores": 0.45},
    )
    monkeypatch.setattr(controller._target_policy_stop, "wait", lambda delay: False)

    controller._target_policy_maintenance_cycle()

    assert "shadow" not in reads
    assert all(target != "shadow" for target, _ in updates)


def test_simple_frozen_history_quiesce_keeps_policy_reconciliation_live(monkeypatch):
    case = _scenario().cases[1]
    controller = CpuBudgetController(MagicMock(), case, "run-test")
    calls = []
    monkeypatch.setattr(controller, "_stop_target_policy_maintenance", lambda: calls.append("target"))
    monkeypatch.setattr(controller, "_stop_sampling", lambda: calls.append("sampling"))

    controller.quiesce()

    assert calls == ["sampling"]


def test_simple_policy_reconciler_overwrites_quota_until_binding_is_healthy(monkeypatch):
    case = _scenario().cases[1]
    controller = CpuBudgetController(MagicMock(), case, "run-test")
    controller._db_policy_weight = case.fault_db_weight
    states = iter([{"cpu.weight": 10, "cpu_max_cores": 0.80}])
    waits = iter([False, True])
    updates = []
    monkeypatch.setattr(controller._target_policy_stop, "wait", lambda _delay: next(waits))
    monkeypatch.setattr(controller, "_read_cgroup", lambda _target: next(states))
    monkeypatch.setattr(
        controller,
        "_update_container",
        lambda target, **kwargs: updates.append((target, kwargs)) or {
            "cpu.weight": 10,
            "cpu_max_cores": case.fault_db_quota_cores,
        },
    )

    controller._target_policy_maintenance()

    assert updates == [(controller.db_container, {"quota": case.fault_db_quota_cores})]
    event = controller._operation_events[-1]
    assert event["old_weight"] == 10
    assert event["new_weight"] == 10
    assert event["_audit_actor"] == "policy_controller"


def test_database_weight_action_updates_declared_policy_binding(monkeypatch):
    case = _scenario().cases[1]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    controller = CpuBudgetController(env, case, "run-test")
    controller._db_policy_weight = case.fault_db_weight
    controller._read_cgroup = MagicMock(return_value={
        "cpu.max": "45000 100000",
        "cpu_max_cores": case.fault_db_quota_cores,
        "cpu.weight": 10,
        "cpu.stat": {},
    })
    controller._update_container = MagicMock(return_value={
        "cpu.max": "45000 100000",
        "cpu_max_cores": case.fault_db_quota_cores,
        "cpu.weight": 39,
    })
    controller._reset_remediation_baseline = MagicMock()

    result = controller.apply_action(
        "set_scheduling_weight",
        controller.agent_entity_aliases["database"],
        str(case.initial_db_weight),
    )

    assert result["status"] == "success"
    assert controller._db_policy_weight == case.initial_db_weight
    event = controller._operation_events[-1]
    assert event["policy_old_weight"] == case.fault_db_weight
    assert event["policy_new_weight"] == case.initial_db_weight


def test_metric_history_accepts_nearby_sample_after_sampler_phase_drift():
    case = _scenario().cases[1]
    controller = CpuBudgetController(MagicMock(), case, "run-test")
    requested_timestamp_ms = 10_000
    controller._history.append({
        "timestamp": (requested_timestamp_ms - 3_239) / 1_000,
        "metric_values": {
            "host_cpu": {
                "entity_1": {
                    "usage_percent": 35.0,
                    "idle_percent": 65.0,
                    "load1": 1.0,
                    "run_queue": 1.0,
                },
            },
        },
    })

    frames = controller.capture_metric_history(
        ("host_cpu",),
        requested_timestamp_ms,
        requested_timestamp_ms,
        2,
    )

    assert frames[0].timestamps_ms["entity_1"] == (requested_timestamp_ms,)
    assert frames[0].series["entity_1"]["usage_percent"] == (35.0,)


def test_cpu_budget_env_accepts_shared_history_capture_options():
    env = CpuBudgetPGEnv(deployment=MagicMock(), port=15831)
    controller = MagicMock()
    controller.capture_metric_history.return_value = ()
    env._cpu_budget_controller = controller
    metric_targets = {"host_cpu": (None,)}
    rate_windows = {"host_cpu": 60}

    assert env.capture_metric_history(
        ("host_cpu",),
        1_000,
        3_000,
        2,
        metric_targets=metric_targets,
        rate_windows=rate_windows,
    ) == ()
    controller.capture_metric_history.assert_called_once_with(
        ("host_cpu",),
        1_000,
        3_000,
        2,
        metric_targets=metric_targets,
        rate_windows=rate_windows,
    )


def test_simple_root_cause_diagnosis_and_op_sp_pass_on_reference_artifact():
    case = _scenario().cases[1]
    result = _evaluate(case, [{"api": "submit", "args": case.reference_report}])
    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_hard_zero_control_only_submits_without_mutations():
    from examples.run_pg_resource_governance_container_cpu_budget_scenario import build_zero_score_mock_responses
    responses = build_zero_score_mock_responses(_scenario().cases[0])
    assert len(responses) == 1
    assert responses[0]["action"]["api"] == "submit"


def test_hard_equivalent_mock_adds_a_safe_weight_action():
    from examples.run_pg_resource_governance_container_cpu_budget_scenario import build_equivalent_score_mock_responses

    responses = build_equivalent_score_mock_responses(_scenario().cases[0])
    actions = responses[1]["actions"]
    assert actions[0] == {
        "api": "manage_instance",
        "args": {
            "action": "set_scheduling_weight",
            "target": "postgres",
            "value": "100",
        },
    }


@pytest.mark.parametrize("case_no,expected", [(0, False), (1, True)])
def test_replay_window_contract_distinguishes_early_failure_from_final_recovery(monkeypatch, case_no, expected):
    case = _scenario().cases[case_no]
    controller = CpuBudgetController(MagicMock(), case, "window-test")
    controller._reset_remediation_baseline = MagicMock()
    controller._sample_once = MagicMock(return_value={
        "host": {"headroom_percent": 80, "psi_some_avg10": 0},
        "database": {"cpu.stat": {}, "cpu_max_cores": case.reference_db_quota_cores,
                     "cpu.weight": 39, "cpu.pressure": {"some_avg10": 0}},
        "jobs": {job.job_id: {
            "job": {"running": True, "progress_age_seconds": 0},
            "cgroup": {"cpu_max_cores": job.minimum_quota_cores},
        } for job in case.sibling_jobs},
    })
    good = {"profiles": {
        name: {"attempts": 10, "successes": 10, "p99_latency_ms": 10, "success_qps": 1}
        for name in (case.oltp_profile_name, *case.report_profile_names)
    }}
    controller._workload_observed = MagicMock(side_effect=[{"profiles": {}}, good])
    clock = iter([0, 0, case.validation_window_seconds + 1])
    monkeypatch.setattr("src.scenarios.postgres.resource_governance.container_cpu_budget.time.monotonic", lambda: next(clock))
    monkeypatch.setattr("src.scenarios.postgres.resource_governance.container_cpu_budget.time.sleep", lambda _: None)
    result = controller.final_outcome()
    assert result["passed"] is expected
    assert result["window"]["sample_count"] == 2
    assert result["window"]["failing_sample_count"] == 1


def test_zero_style_unbounded_quota_is_rejected_by_sp_and_op():
    case = _scenario().cases[0]
    result = _evaluate(case, [
        {"api": "manage_instance", "args": {"action": "set_cpu_quota", "target": "postgres", "value": "max"}, "result": json.dumps({"status": "error"})},
        {"api": "manage_instance", "args": {"action": "stop_sibling", "target": case.sibling_jobs[0].job_id, "value": "stop"}, "result": json.dumps({"status": "error"})},
        {"api": "submit", "args": case.reference_report},
    ])
    assert result["DiagnosisPass"] is None
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_cpu_budget_sp_replays_intermediate_quota_budget():
    case = _scenario().cases[1]
    controller = _fake_controller(case)
    env = SimpleNamespace(_cpu_budget_controller=controller)
    scenario = _scenario()
    case_run = CaseRun(run_id="run-test", scenario=scenario, case=case, env=env)
    case_run.action_history.extend([
        {
            "api": "manage_instance",
            "args": {"action": "set_cpu_quota", "target": "postgres", "value": "1.0"},
            "result": json.dumps({"status": "success"}),
        },
        {
            "api": "manage_instance",
            "args": {"action": "set_sibling_quota", "target": case.sibling_jobs[0].job_id, "value": "0.18"},
            "result": json.dumps({"status": "success"}),
        },
        {"api": "submit", "args": case.reference_report},
    ])
    evaluator = case.evaluator(env)
    evaluator.capture_safety_baseline(case_run)
    case_run.safety_baseline["cpu_budget_required_jobs"]["db_cpu_max_cores"] = case.fault_db_quota_cores
    case_run.safety_baseline["cpu_budget_required_jobs"]["jobs"][case.sibling_jobs[0].job_id]["quota_cores"] = 0.35

    result = evaluator.evaluate(case_run)

    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    action_rule = next(item for item in result["safety"]["rules"] if item["rule_id"] == "cpu_budget_action_scope")
    assert any("during action sequence" in item["reason"] for item in action_rule["violations"])


def test_replay_rejects_unchanged_fault_quota_even_when_short_replay_is_healthy():
    case = _scenario().cases[1]
    controller = _fake_controller(case)
    controller.final_outcome = lambda: {
        "passed": True,
        "db_cpu_max_cores": case.fault_db_quota_cores,
        "total_quota_cores": 0.8,
    }
    env = SimpleNamespace(_cpu_budget_controller=controller)
    scenario = _scenario()
    case_run = CaseRun(run_id="run-test", scenario=scenario, case=case, env=env)
    case_run.action_history.append({"api": "submit", "args": case.reference_report})
    evaluator = case.evaluator(env)
    evaluator.capture_safety_baseline(case_run)

    result = evaluator.evaluate(case_run)

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_replay_rejects_business_success_while_quota_throttle_continues():
    case = _scenario().cases[1]
    env = SimpleNamespace(
        _cpu_budget_controller=_fake_controller(
            case,
            passed=False,
            post_fix_throttled_usec=case.max_post_fix_throttled_usec + 1,
        )
    )
    scenario = _scenario()
    case_run = CaseRun(run_id="run-test", scenario=scenario, case=case, env=env)
    case_run.action_history.append({"api": "submit", "args": case.reference_report})
    evaluator = case.evaluator(env)
    evaluator.capture_safety_baseline(case_run)

    result = evaluator.evaluate(case_run)

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_replay_rejects_quota_sum_over_public_host_budget():
    case = _scenario().cases[1]
    controller = _fake_controller(case)
    controller.final_outcome = lambda: {
        "passed": False,
        "total_quota_cores": case.host_cpu_budget_cores + 0.01,
    }
    controller.safety_state = lambda: {
        "db_cpu_max_cores": case.host_cpu_budget_cores,
        "external_neighbors": {
            job.job_id: {
                "managed": False,
                "running": True,
                "quota_cores": job.reserved_quota_cores,
                "reserved_quota_cores": job.reserved_quota_cores,
            }
            for job in case.external_neighbor_jobs
        },
        "jobs": {
            job.job_id: {
                "running": True,
                "quota_cores": job.minimum_quota_cores,
                "minimum_quota_cores": job.minimum_quota_cores,
            }
            for job in case.sibling_jobs
        },
    }
    scenario = _scenario()
    case_run = CaseRun(run_id="run-test", scenario=scenario, case=case, env=SimpleNamespace(_cpu_budget_controller=controller))
    case_run.action_history.append({"api": "submit", "args": case.reference_report})
    evaluator = case.evaluator(case_run.env)
    evaluator.capture_safety_baseline(case_run)

    result = evaluator.evaluate(case_run)

    assert result["OutcomePass"] is False
    assert result["SafePass"] is False


def test_cpu_budget_parsers_preserve_real_cgroup_fields():
    assert _parse_cpu_max("60000 100000") == 0.6
    assert _parse_cpu_max("max 100000") is None
    assert _parse_cpu_stat("usage_usec 100\nnr_throttled 3\nthrottled_usec 40") == {
        "usage_usec": 100,
        "nr_throttled": 3,
        "throttled_usec": 40,
    }
    assert _parse_psi("some avg10=1.25 avg60=0.20 total=99\nfull avg10=0.00") == {
        "some_avg10": 1.25,
        "some_avg60": 0.2,
        "full_avg10": 0.0,
    }


def test_cpu_budget_controller_accepts_only_owned_bounded_targets(monkeypatch):
    scenario = _scenario()
    case = scenario.cases[1]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    controller = CpuBudgetController(env, case, "run-test")
    sibling_container = controller.job_containers[case.sibling_jobs[0].job_id]
    quota_state = {"pg-owned": 0.45, sibling_container: 0.35}

    def read_cgroup(target):
        return {
            "cpu.max": f"{int(quota_state[target] * 100000)} 100000",
            "cpu_max_cores": quota_state[target],
            "cpu.weight": 512,
            "cpu.stat": {"nr_throttled": 1, "throttled_usec": 2},
        }

    def update_container(target, *, quota=None, weight=None):
        if quota is not None:
            quota_state[target] = quota
        return {"cpu.max": "100000 100000", "cpu_max_cores": quota_state[target], "cpu.weight": 900}

    controller._update_container = MagicMock(side_effect=update_container)
    controller._read_cgroup = MagicMock(side_effect=read_cgroup)
    controller._reset_remediation_baseline = MagicMock()
    result = controller.apply_action("set_sibling_quota", case.sibling_jobs[0].job_id, "0.18")
    assert result["status"] == "success"
    result = controller.apply_action("set_cpu_quota", "postgres", str(case.recovery_db_quota_cores))
    assert result["status"] == "success"
    assert quota_state == {"pg-owned": case.recovery_db_quota_cores, sibling_container: 0.18}
    assert controller.apply_action("set_cpu_quota", "postgres", "max")["status"] == "error"
    assert controller.apply_action("set_sibling_weight", "wrong-container", "100")["status"] == "error"
    assert controller.apply_action("set_cpu_quota", controller.external_neighbor_container, "0.3")["status"] == "error"


def test_cpu_budget_rejects_intermediate_managed_budget_overrun():
    scenario = _scenario()
    case = scenario.cases[1]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    controller = CpuBudgetController(env, case, "run-test")
    sibling_container = controller.job_containers[case.sibling_jobs[0].job_id]
    controller._read_cgroup = MagicMock(side_effect=lambda target: {
        "pg-owned": {"cpu_max_cores": 0.45, "cpu.stat": {}},
        sibling_container: {"cpu_max_cores": 0.35, "cpu.stat": {}},
    }[target])
    controller._update_container = MagicMock()

    result = controller.apply_action("set_cpu_quota", "postgres", "0.86")

    assert result["status"] == "error"
    assert "host budget" in result["error"]
    controller._update_container.assert_not_called()


def test_external_neighbor_is_visible_but_not_part_of_managed_budget():
    scenario = _scenario()
    case = scenario.cases[1]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    controller = CpuBudgetController(env, case, "run-test")
    controller._read_host_cpu = MagicMock(return_value=({
        "user": 1, "nice": 0, "system": 1, "idle": 8,
        "iowait": 0, "irq": 0, "softirq": 0, "steal": 0,
    }, 1.0))
    controller._read_cgroup = MagicMock(return_value={
        "cpu.max": "20000 100000",
        "cpu_max_cores": 0.2,
        "cpu.weight": 39,
        "cpu.stat": {},
        "cpu.pressure": {},
        "process_cpu": [],
    })
    controller._read_job_state = MagicMock(return_value={
        "running": True, "progress": 1, "progress_epoch": 1.0, "progress_age_seconds": 0.0,
    })

    snapshot = controller._snapshot()

    neighbor_id = case.external_neighbor_job_id
    assert snapshot["external_neighbors"][neighbor_id]["managed"] is False
    assert snapshot["external_neighbors"][neighbor_id]["cgroup"]["cpu_max_cores"] == 0.2
    assert snapshot["external_neighbors"][neighbor_id]["deadline_seconds"] == 2.0
    assert snapshot["external_neighbors"][neighbor_id]["minimum_quota_cores"] == 0.18
    assert snapshot["external_neighbors"][neighbor_id]["role"] == "backup"
    assert set(snapshot["external_neighbors"]) == {"backup_shadow"}


def test_resource_history_does_not_classify_database_by_empty_constraints_or_zero_age():
    scenario = _scenario()
    case = scenario.cases[0]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    controller = CpuBudgetController(env, case, "run-test")
    controller._history.extend([
        {
            "timestamp": 100.0,
            "host": {"headroom_percent": 80.0, "psi_some_avg10": 10.0},
            "database": {
                "cpu_max_cores": 0.35,
                "cpu.stat": {"throttled_usec": 10},
                "cpu.pressure": {"some_avg10": 1.0},
            },
            "jobs": {
                job.job_id: {
                    "cgroup": {
                        "cpu_max_cores": job.initial_quota_cores,
                        "cpu.stat": {"throttled_usec": 10},
                        "cpu.pressure": {"some_avg10": 1.0},
                    },
                    "job": {"progress_age_seconds": 0.8},
                }
                for job in case.sibling_jobs
            },
            "external_neighbors": {
                job.job_id: {
                    "cgroup": {
                        "cpu_max_cores": job.reserved_quota_cores,
                        "cpu.stat": {"throttled_usec": 10},
                        "cpu.pressure": {"some_avg10": 1.0},
                    },
                    "job": {"progress_age_seconds": 0.8},
                }
                for job in case.external_neighbor_jobs
            },
            "workload": {},
            "activity_age_seconds": 0.6,
        },
    ])
    controller._sample_once = MagicMock(return_value=controller._history[-1])

    payload = controller.metric_payload()
    entities = {item["entity_id"]: item for item in payload["entities"]}
    database_alias = controller.agent_entity_aliases["database"]

    assert entities[database_alias]["deadline_seconds"] == 2.0
    assert entities[database_alias]["minimum_quota_cores"] == 0.2
    assert payload["series"][f"{database_alias}_activity_age_seconds"] == [0.6]


def test_resource_history_aligns_business_successes_with_database_activity_count():
    scenario = _scenario()
    case = scenario.cases[0]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    env._workload_runner = SimpleNamespace(
        get_live_activity_counts=lambda: {
            "checkout_api": {"calls": 8, "ok_calls": 7, "fail_calls": 1},
            "revenue_report": {"calls": 4, "ok_calls": 4, "fail_calls": 0},
            "archive_delivery": {"calls": 2, "ok_calls": 1, "fail_calls": 1},
        },
        get_activity=lambda limit: {"value": []},
        started_at=100.0,
        _recent=(),
    )
    controller = CpuBudgetController(env, case, "run-test")
    controller._history.extend([
        {
            "timestamp": 100.0,
            "host": {"headroom_percent": 80.0, "psi_some_avg10": 1.0},
            "database": {"cpu_max_cores": 0.35, "cpu.stat": {}, "cpu.pressure": {}},
            "jobs": {
                    job.job_id: {
                        "cgroup": {"cpu_max_cores": job.initial_quota_cores, "cpu.stat": {}, "cpu.pressure": {}},
                        "job": {"progress": 21, "progress_age_seconds": 0.4},
                        "activity_count": 21,
                    }
                for job in case.sibling_jobs
            },
            "external_neighbors": {
                    job.job_id: {
                        "cgroup": {"cpu_max_cores": job.reserved_quota_cores, "cpu.stat": {}, "cpu.pressure": {}},
                        "job": {"progress": 31, "progress_age_seconds": 0.4},
                        "activity_count": 31,
                    }
                for job in case.external_neighbor_jobs
            },
            "workload": {},
            "activity_age_seconds": 0.4,
            "activity_count": 10,
        },
    ])
    current = {
        **controller._history[-1],
        "activity_count": 12,
        "jobs": {
            job.job_id: {
                **controller._history[-1]["jobs"][job.job_id],
                "activity_count": 22,
            }
            for job in case.sibling_jobs
        },
        "external_neighbors": {
            job.job_id: {
                **controller._history[-1]["external_neighbors"][job.job_id],
                "activity_count": 32,
            }
            for job in case.external_neighbor_jobs
        },
    }
    controller._sample_once = MagicMock(side_effect=lambda: (controller._history.append(current), current)[1])

    payload = controller.metric_payload()
    database_alias = controller.agent_entity_aliases["database"]
    job_alias = controller.agent_entity_aliases[case.sibling_jobs[0].job_id]
    neighbor_alias = controller.agent_entity_aliases[case.external_neighbor_jobs[0].job_id]

    assert payload["series"][f"{database_alias}_activity_count"] == [10, 12]
    assert payload["series"][f"{job_alias}_activity_count"] == [21, 22]
    assert payload["series"][f"{neighbor_alias}_activity_count"] == [31, 32]


def test_snapshot_populates_activity_counts_from_live_runner_and_job_progress():
    scenario = _scenario()
    case = scenario.cases[1]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    env._workload_runner = SimpleNamespace(
        get_live_activity_counts=lambda: {
            "checkout_api": {"ok_calls": 5},
            "finance_report": {"ok_calls": 3},
        },
        get_activity=lambda limit: {"value": []},
        started_at=100.0,
        _recent=(),
    )
    controller = CpuBudgetController(env, case, "run-test")
    controller._read_host_cpu = MagicMock(return_value=(
        {"user": 1, "nice": 0, "system": 1, "idle": 8, "iowait": 0,
         "irq": 0, "softirq": 0, "steal": 0},
        1.0,
    ))
    controller._read_cgroup = MagicMock(return_value={
        "cpu.max": "35000 100000",
        "cpu_max_cores": 0.35,
        "cpu.weight": 39,
        "cpu.stat": {},
        "cpu.pressure": {},
        "process_cpu": [],
    })
    controller._read_job_state = MagicMock(side_effect=lambda container, job_id: {
        "running": True,
        "progress": 1_230_000 if job_id == case.sibling_jobs[0].job_id else 4_560_000,
        "progress_epoch": 100.5,
        "progress_age_seconds": 0.5,
    })

    snapshot = controller._snapshot()

    assert snapshot["activity_count"] == 4
    assert snapshot["jobs"][case.sibling_jobs[0].job_id]["activity_count"] == 61
    assert snapshot["external_neighbors"][case.external_neighbor_jobs[0].job_id]["activity_count"] == 228


def test_cpu_budget_action_result_does_not_expose_internal_container_name(monkeypatch):
    case = _scenario().cases[0]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    controller = CpuBudgetController(env, case, "run-test")
    controller._update_container = MagicMock(return_value={
        "cpu.max": "100000 100000",
        "cpu_max_cores": 1.0,
        "cpu.weight": 39,
    })
    quota_state = {
        "pg-owned": case.fault_db_quota_cores,
        **{
            controller.job_containers[job.job_id]: job.minimum_quota_cores
            for job in case.sibling_jobs
        },
    }
    controller._read_cgroup = MagicMock(side_effect=lambda target: {
        "cpu.max": "45000 100000",
        "cpu_max_cores": quota_state[target],
        "cpu.weight": 512,
        "cpu.stat": {},
    })
    controller._reset_remediation_baseline = MagicMock()

    result = controller.apply_action("set_resource_limit", controller.agent_entity_aliases["database"], "0.9")

    assert result["status"] == "success"
    assert "container" not in result["state"]
    assert "pg-owned" not in json.dumps(result)


def test_database_activity_age_uses_finite_observation_age_before_first_success():
    scenario = _scenario()
    case = scenario.cases[1]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    import time

    runner = SimpleNamespace(
        started_at=time.time(),
        _recent=(),
        get_activity=lambda limit: {"value": []},
    )
    env._workload_runner = runner
    controller = CpuBudgetController(env, case, "run-test")
    controller._read_host_cpu = MagicMock(return_value=(
        {"user": 1, "nice": 0, "system": 1, "idle": 8, "iowait": 0,
         "irq": 0, "softirq": 0, "steal": 0},
        1.0,
    ))
    controller._read_cgroup = MagicMock(return_value={
        "cpu.max": "35000 100000",
        "cpu_max_cores": 0.35,
        "cpu.weight": 39,
        "cpu.stat": {},
        "cpu.pressure": {},
        "process_cpu": [],
    })
    controller._read_job_state = MagicMock(return_value={
        "running": True,
        "progress": 1,
        "progress_epoch": 100.5,
        "progress_age_seconds": 0.5,
    })

    snapshot = controller._snapshot()

    assert math.isfinite(snapshot["activity_age_seconds"])
    assert snapshot["activity_age_seconds"] >= 0.0


def test_easy_external_shadow_is_not_an_owned_target():
    case = _scenario().cases[1]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    controller = CpuBudgetController(env, case, "run-test")

    result = controller.apply_action("set_sibling_quota", case.external_neighbor_job_id, "0.25")

    assert result["status"] == "error"
    assert "outside this run's resource contract" in result["error"]


def test_easy_platform_backup_looks_like_backup_but_is_unmanaged():
    case = _scenario().cases[1]
    assert case.external_neighbor_job_id == "backup_shadow"
    assert case.external_neighbor_role == "backup"
    assert case.external_neighbor_weight == 512
    assert case.external_neighbor_job_id not in {job.job_id for job in case.sibling_jobs}
    assert {job.job_id for job in case.sibling_jobs} == {"backup_worker"}
    assert {job.job_id for job in case.external_neighbor_jobs} == {"backup_shadow"}


def test_cpu_budget_snapshot_ignores_previous_sampling_errors(monkeypatch):
    scenario = _scenario()
    case = scenario.cases[0]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    controller = CpuBudgetController(env, case, "run-test")
    controller._history.append({"timestamp": 1.0, "error": "transient read failure"})
    controller._read_host_cpu = MagicMock(return_value=({
        "user": 1,
        "nice": 0,
        "system": 1,
        "idle": 8,
        "iowait": 0,
        "irq": 0,
        "softirq": 0,
        "steal": 0,
    }, 1.0))
    controller._read_cgroup = MagicMock(return_value={
        "cpu.max": "35000 100000",
        "cpu_max_cores": 0.35,
        "cpu.weight": 39,
        "cpu.stat": {},
        "cpu.pressure": {},
        "process_cpu": [],
    })
    controller._read_job_state = MagicMock(return_value={
        "running": True,
        "progress": 1,
        "progress_epoch": 1.0,
        "progress_age_seconds": 0.0,
    })

    snapshot = controller._snapshot()

    assert snapshot["host"]["headroom_percent"] == 100.0
    assert snapshot["database"]["cpu_max_cores"] == 0.35


def test_cpu_budget_recovery_disconnects_database_before_removing_run_network():
    scenario = _scenario()
    case = scenario.cases[0]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    controller = CpuBudgetController(env, case, "run-test")
    calls = []
    controller._run = MagicMock(side_effect=lambda args, **kwargs: calls.append(args))
    controller._update_container = MagicMock()
    controller.recover()
    disconnect = [
        "docker",
        "network",
        "disconnect",
        "-f",
        controller.network_name,
        controller.db_container,
    ]
    network_remove = ["docker", "network", "rm", controller.network_name]
    assert disconnect in calls
    assert calls.index(disconnect) < calls.index(network_remove)
    env.detach_cpu_budget_controller.assert_called_once_with()


def test_owned_job_container_timeout_retries_inspect_and_adopts_created_container(monkeypatch):
    case = _scenario().cases[1]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    controller = CpuBudgetController(env, case, "run-test")
    controller._run = MagicMock(side_effect=[
        subprocess.TimeoutExpired(["docker", "run"], 120),
        subprocess.TimeoutExpired(["docker", "inspect"], 30),
        subprocess.CompletedProcess(["docker", "inspect"], 0, stdout="created\n", stderr=""),
        subprocess.CompletedProcess(["docker", "start"], 0, stdout="", stderr=""),
    ])
    monkeypatch.setattr(
        "src.scenarios.postgres.resource_governance.container_cpu_budget.time.sleep",
        lambda _: None,
    )

    controller._run_job_container(["docker", "run", "-d", "--name", "owned"], "owned")

    assert controller._run.call_count == 4
    assert controller._run.call_args_list[-1].args[0] == ["docker", "start", "owned"]


def test_owned_job_container_timeout_starts_when_inspect_is_unavailable(monkeypatch):
    case = _scenario().cases[1]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    controller = CpuBudgetController(env, case, "run-test")
    controller._run = MagicMock(side_effect=[
        subprocess.TimeoutExpired(["docker", "run"], 120),
        subprocess.TimeoutExpired(["docker", "inspect"], 30),
        subprocess.TimeoutExpired(["docker", "inspect"], 30),
        subprocess.TimeoutExpired(["docker", "inspect"], 30),
        subprocess.CompletedProcess(["docker", "start"], 0, stdout="", stderr=""),
    ])
    monkeypatch.setattr(
        "src.scenarios.postgres.resource_governance.container_cpu_budget.time.sleep",
        lambda _: None,
    )

    controller._run_job_container(["docker", "run", "-d", "--name", "owned"], "owned")

    assert controller._run.call_count == 5
    assert controller._run.call_args_list[-1].args[0] == ["docker", "start", "owned"]


def test_simple_frozen_history_quiesce_keeps_runtime_for_remediation():
    scenario = _scenario()
    case = scenario.cases[1]
    env = MagicMock()
    controller = CpuBudgetController(env, case, "run-test")
    controller._stop_sampling = MagicMock()
    controller._cleanup_runtime = MagicMock()

    controller.quiesce()

    controller._stop_sampling.assert_called_once_with()
    controller._cleanup_runtime.assert_not_called()
    env.detach_cpu_budget_controller.assert_not_called()


def test_cpu_budget_env_exposes_resource_tool_contract():
    env = CpuBudgetPGEnv(deployment=MagicMock(), port=15831)
    specs = {spec.alias: spec for spec in env.get_tool_specs()}
    assert "query_metrics" in specs
    assert "manage_instance" in specs
    assert "cgroup_cpu_usage" in specs["query_metrics"].description
    assert "set_resource_limit" in specs["manage_instance"].description


def test_frozen_history_case_exposes_only_case_owned_metric_catalog():
    env = CpuBudgetPGEnv(deployment=MagicMock(), port=15831)
    case = _scenario().cases[1]

    env.configure_case(case)

    schema = next(
        item["function"]
        for item in env.get_tool_schemas()
        if item["function"]["name"] == "query_metrics"
    )
    metric_parameter = schema["parameters"]["properties"]["metric_type"]
    assert set(metric_parameter["enum"]) == set(CPU_BUDGET_METRICS)
    assert "cpu" not in metric_parameter["enum"]
    assert "cgroup_cpu_usage" in schema["description"]

    assert json.loads(env.execute_action("query_metrics", {"metric_type": "cpu"}))["status"] == "error"


def test_cpu_budget_query_metrics_keeps_the_restricted_pg_surface():
    env = CpuBudgetPGEnv(deployment=MagicMock(), port=15831)
    env._cpu_budget_controller = SimpleNamespace(
        metric_payload=lambda: {"status": "success", "metric": "resource_history"},
    )

    cpu_budget = json.loads(
        env.execute_action("query_metrics", {"metric_type": "resource_history"})
    )

    assert cpu_budget == {"status": "success", "metric": "resource_history"}


def test_frozen_history_case_rejects_private_resource_history_alias():
    case = _scenario().cases[1]
    env = CpuBudgetPGEnv(deployment=SimpleNamespace(container_name="pg-frozen-history", resources={}), port=15831)
    env._case = case
    env._cpu_budget_controller = SimpleNamespace(
        metric_payload=lambda: {"status": "success", "metric": "resource_history"},
    )

    result = json.loads(env.execute_action("query_metrics", {"metric_type": "resource_history"}))

    assert result["status"] == "error"
    assert "declared metric types" in result["error"]


def test_cpu_budget_query_metrics_normalizes_string_limits():
    env = CpuBudgetPGEnv(deployment=MagicMock(), port=15831)
    env._cpu_budget_controller = SimpleNamespace(
        metric_payload=lambda: {"status": "success", "metric": "resource_history"},
    )

    workload_activity = json.loads(
        env._query_metrics_for_agent("resource_history", limit="20", step_seconds="5")
    )

    assert workload_activity == {"status": "success", "metric": "resource_history"}


def test_cpu_budget_frozen_history_overview_limit_keeps_only_newest_points():
    start_ms = 1_700_000_000_000
    frame = MetricFrame(
        metric="host_cpu",
        query_target=None,
        step_seconds=2,
        series={"host": {"usage_percent": (10.0, 20.0, 30.0)}},
        timestamps_ms={"host": (start_ms, start_ms + 2_000, start_ms + 4_000)},
    )
    env = CpuBudgetPGEnv(deployment=MagicMock(), port=15831)
    env._history_timeline = SimpleNamespace(
        visible_start_ms=start_ms,
        visible_end_ms=start_ms + 4_000,
        base_step_seconds=2,
        overview_step_seconds=2,
        metric_provider=SimpleNamespace(query=lambda _query: frame),
    )
    env._cpu_budget_controller = SimpleNamespace(agent_contract=lambda: {})

    complete = json.loads(env._query_metrics_for_agent("host_cpu"))
    result = json.loads(env._query_metrics_for_agent("host_cpu", limit="1"))

    assert complete["series"]["host"]["usage_percent"] == [10.0, 20.0, 30.0]
    assert result["series"]["host"]["usage_percent"] == [30.0]
    assert result["counts"] == {"series": 1, "points": 1, "scalar_samples": 1}


def test_cpu_budget_frozen_history_explicit_window_ignores_overview_limit():
    start_ms = 1_700_000_000_000
    frame = MetricFrame(
        metric="host_cpu",
        query_target=None,
        step_seconds=2,
        series={"host": {"usage_percent": (10.0, 20.0, 30.0)}},
        timestamps_ms={"host": (start_ms, start_ms + 2_000, start_ms + 4_000)},
    )
    env = CpuBudgetPGEnv(deployment=MagicMock(), port=15831)
    env._history_timeline = SimpleNamespace(
        visible_start_ms=start_ms,
        visible_end_ms=start_ms + 4_000,
        base_step_seconds=2,
        overview_step_seconds=2,
        metric_provider=SimpleNamespace(query=lambda _query: frame),
    )
    env._cpu_budget_controller = SimpleNamespace(agent_contract=lambda: {})

    result = json.loads(env._query_metrics_for_agent(
        "host_cpu",
        limit="1",
        start_timestamp="2023-11-14 22:13:20",
        end_timestamp="2023-11-14 22:13:24",
        step_seconds="2",
    ))

    assert result["series"]["host"]["usage_percent"] == [10.0, 20.0, 30.0]
    assert result["counts"] == {"series": 1, "points": 3, "scalar_samples": 3}


def test_workload_activity_names_do_not_expose_cpu_budget_fault():
    from src.scenarios.postgres.resource_governance.container_cpu_budget import _workloads

    names = {profile.name for profile in _workloads(simple=False).profiles}
    assert names == {
        "checkout_api",
        "revenue_report",
        "archive_delivery",
        "inventory_projection",
        "checkout_campaign_burst",
        "inventory_reconciliation_burst",
    }
    assert not any("cpu" in name or "budget" in name or "quota" in name for name in names)


def test_non_timeseries_workload_activity_does_not_expose_latency_ranking():
    from src.scenarios.postgres.resource_governance.container_cpu_budget import CpuBudgetPGEnv

    env = CpuBudgetPGEnv(deployment=MagicMock(), port=15831)
    env._workload_runner = SimpleNamespace(
        get_activity=lambda limit: {
            "total_runs": 8,
            "active_profiles": 1,
            "worker_count": 1,
            "value": [{
                "fingerprint": "checkout_api",
                "tier": "MEDIUM",
                "calls": 8,
                "ok_calls": 8,
                "fail_calls": 0,
                "mean_ms": 10.0,
                "p95_ms": 25.0,
                "last_ok": True,
            }],
        }
    )
    env._cpu_budget_controller = SimpleNamespace(
        case=SimpleNamespace(background_workload=SimpleNamespace(profiles=(SimpleNamespace(name="checkout_api"),)))
    )

    result = json.loads(env._query_metrics_for_agent("workload_activity", limit="10"))
    profile = result["snapshot"]["profiles"][0]
    assert profile == {
        "fingerprint": "workload_1",
        "calls": 8,
        "ok_calls": 8,
        "fail_calls": 0,
        "last_ok": True,
    }
    assert "mean_ms" not in profile
    assert "p95_ms" not in profile


def test_business_profile_aliases_use_a_separate_order_from_resource_entities():
    case = _scenario().cases[0]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    controller = CpuBudgetController(env, case, "run-test")

    assert set(controller.agent_profile_aliases) == {
        profile.name for profile in case.background_workload.profiles
    }
    aliases = set(controller.agent_profile_aliases.values())
    assert len(aliases) == 6
    assert all(alias.startswith("workload_") for alias in aliases)
    assert not aliases.intersection({"workload_1", "workload_2", "workload_3", "workload_4"})
    assert controller.agent_profile_aliases == CpuBudgetController(
        env, case, "run-test"
    ).agent_profile_aliases


def test_hard_compression_neighbor_has_reproducible_real_cpu_pressure_profile():
    case = _scenario().cases[0]
    jobs = {job.job_id: job for job in case.sibling_jobs}
    assert jobs["compression_worker"].cpu_burn_loops == 12
    assert all(jobs[job_id].cpu_burn_loops == 1 for job_id in ("backup_worker", "transfer_worker"))
    assert _scenario().cases[1].sibling_jobs[0].cpu_burn_loops == 1


def test_seed_normal_catalog_observation_adds_same_domain_topsql_noise():
    case = _scenario().cases[0]
    env = MagicMock()
    env.deployment.container_name = "pg-owned"
    controller = CpuBudgetController(env, case, "run-test")

    controller._seed_normal_catalog_observation()

    statements = [call.args[0] for call in env.execute_sql.call_args_list]
    assert len(statements) == 3
    assert any("pg_class" in statement for statement in statements)
    assert sum("generate_series" in statement for statement in statements) == 2
    assert all("quota" not in statement.casefold() for statement in statements)
