import json
from dataclasses import replace
from types import SimpleNamespace

import pytest

from examples.run_tidb_resource_governance_lightning_budget_frozen_history_scenario import (
    build_reference_mock_responses,
)
from src.scenarios.tidb import (
    TidbResourceGovernanceLightningBudgetFrozenHistoryScenario,
)
from src.scenarios.workloads import WorkloadProfile
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.semantic import SemanticConditionJudgment, SemanticJudgment
from src.scenarios.evaluation.safety import SafetyContext, TraceEvent
from src.scenarios.evaluation.tidb.resource_governance.lightning_budget_frozen_history import (
    LightningFrozenHistorySafetyRule,
    LightningFrozenHistoryBatchWindowVerifier,
    LightningFrozenHistoryControlVerifier,
    LightningFrozenHistoryFrontendSloVerifier,
    LightningFrozenHistoryImportVerifier,
    TidbResourceGovernanceLightningBudgetHistoryInvestigationEvaluatorCase,
    TidbResourceGovernanceLightningBudgetFrozenHistoryEvaluatorCase,
)
from src.scenarios.tidb.resource_governance.lightning_budget import LightningBudgetController
import src.scenarios.evaluation.tidb.resource_governance.lightning_budget_frozen_history as evaluator_module
from src.scenarios.tidb.resource_governance.lightning_budget_frozen_history import (
    TidbResourceGovernanceLightningBudgetFrozenHistoryInjector,
)
from src.execution.deployment import lightning_decoy_job_id, lightning_job_id
from src.execution.environment import TiDBEnv
from src.execution.history.metrics import MetricFrame, MetricQuery
from src.execution.history.records import CapturedRecords, HistoricalCoverage, HistoricalRecordSource
from src.execution.tidb_metrics import TiDBMetricCatalog
from src.scenarios.runtime.metric_history import CapturedHistoryInputs, HistoryAssembler, NormalHistoryCapture
from src.scenarios.runtime.workload_runner import WorkloadRunner
from src.scenarios.frozen_history import DecoyDirection, DecoyKind


class FakeDeployment:
    run_id = "frozen-history-unit"
    project_name = "aiopsbench-frozen-history-unit"
    primary_tidb_endpoint = ("127.0.0.1", 4000)
    NODES = {
        "tidb/tidb-0": "tidb-0",
        "tidb/tidb-1": "tidb-1",
        "tikv/tikv-0": "tikv-0",
        "tikv/tikv-1": "tikv-1",
        "tikv/tikv-2": "tikv-2",
        "lightning/lightning-0": "lightning",
    }
    tidb_endpoints = ("tidb/tidb-0", "tidb/tidb-1")
    database_nodes = ("tikv/tikv-0",)
    node_cpu_limits = {"tikv/tikv-0": 1.0, "lightning/lightning-0": 1.5}


def test_frozen_history_case_contract_is_hard_and_phase2_only():
    scenario = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario()
    case = scenario.cases[0]

    assert scenario.scenario_id == "tidb_resource_governance_lightning_budget_frozen_history"
    assert case.case_id == "lightning_budget_history_calibration"
    assert case.frozen_history.activate_during_target_capture is True
    assert case.frozen_history.post_target_mode == "RESUME_NORMAL"
    assert case.frozen_history.required_metrics[:3] == (
        "lightning_progress",
        "lightning_throughput",
        "lightning_workers",
    )
    assert len(case.frozen_history.decoys) == 4
    assert all(decoy.kind is DecoyKind.METRIC_ONLY for decoy in case.frozen_history.decoys)
    assert all(decoy.duration_seconds == 60 for decoy in case.frozen_history.decoys)
    assert [decoy.decoy_id for decoy in case.frozen_history.decoys] == [
        "frontend-p95-history-spike",
        "tikv-write-surge",
        "tidb-cpu-saturation",
        "frontend-latency-climb",
    ]
    assert all(
        decoy.metric != "lightning_progress"
        and decoy.metric != "lightning_throughput"
        and decoy.metric != "lightning_workers"
        for decoy in case.frozen_history.decoys
    )
    assert case.frozen_history.target_age_seconds_range == (30000, 36000)
    case.frozen_history.validate(case.background_workload)
    assert case.row_count == 2000000
    assert case.source_file_count == 4
    assert case.rebalance_after_rows == 1000000
    assert case.phase2_region_concurrency_max == 2
    assert case.phase2_disk_quota_mb_max == 2048
    assert case.phase2_store_write_bwlimit_mib_max == 48
    assert not hasattr(case, "frontend_slo_p95_ms")
    assert case.frozen_history.normal_capture_seconds == 60
    assert case.frozen_history.fault_capture_seconds == 840
    assert case.frozen_history.metric_targets["disk_io"] == (
        "tikv/tikv-0",
        "tikv/tikv-1",
        "tikv/tikv-2",
    )
    assert case.frozen_history.metric_targets["disk_usage"] == (
        "tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"
    )


def test_investigation_alert_states_business_surface_without_mechanism_leaks():
    scenario = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario()
    case = scenario.cases[1]

    assert "2,000,000-row" in case.alert
    assert "benchops_mf_rg05.mf_rg05_lightning_orders" in case.alert
    assert "650ms SLO" in case.alert
    assert "1.5 GiB" in case.alert
    assert "minutes of final import runtime" in case.alert
    for leaked in (
        "checkpoint",
        "handoff",
        "phase1",
        "phase2",
        "budget",
        "bound",
        "resume",
        "precheck",
        "connect ",
        "exclude",
        "frozen",
        "history",
    ):
        assert leaked not in case.alert, f"alert leaks mechanism language: {leaked!r}"


def test_investigation_brackets_the_incident_with_two_p95_decoys():
    scenario = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario()
    case = scenario.cases[1]
    decoys = case.frozen_history.decoys

    assert len(decoys) == 3
    baseline, aftermath, benign_burst = decoys
    assert baseline.decoy_id == "frontend-p95-history-spike"
    assert baseline.after_target is False
    assert aftermath.decoy_id == "frontend-p95-aftermath-transient"
    assert aftermath.after_target is True
    for decoy in (baseline, aftermath):
        assert decoy.kind is DecoyKind.METRIC_ONLY
        assert decoy.metric == "workload_profile"
        assert decoy.field == "p95_ms"
        assert decoy.target == "checkout_recent_order_search"
        assert decoy.direction is DecoyDirection.SPIKE
        assert decoy.duration_seconds == 60
        assert decoy.amplitude_mad == 3.0
    assert benign_burst.decoy_id == "tikv-benign-write-burst"
    assert benign_burst.kind is DecoyKind.CAPTURED_BENIGN
    assert benign_burst.metric == "disk_io"
    assert benign_burst.field == "write_mb_per_second"
    assert benign_burst.target == "tikv/tikv-1"
    assert benign_burst.duration_seconds == 40
    assert benign_burst.amplitude_mad is None
    assert benign_burst.minimum_deviation_mad == 0.5
    assert case.frozen_history.decoys_adjacent_to_target is True
    case.frozen_history.validate(case.background_workload)


def test_investigation_capture_window_covers_the_phase1_checkpoint_deadline():
    scenario = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario()
    case = scenario.cases[1]
    spec = case.frozen_history

    assert case.case_id == "lightning_budget_history_investigation"
    # finalize requires the checkpoint handoff inside the captured window and
    # status() fails phase1 once its operational deadline expires, so the two
    # must stay equal and cover the ~130-250 s encode measured for the
    # 2,000,000-row source at region_concurrency 6 plus the 165-376 s the r5
    # precheck + staging import measured across the machine's load spectrum;
    # the window carries a 720 s cover.
    assert spec.fault_capture_seconds == 720
    assert case.phase1_checkpoint_deadline_seconds == spec.fault_capture_seconds
    spec.validate(case.background_workload)
    plan = scenario.build_fault_plan(case)[0]
    assert plan.config["phase1_checkpoint_deadline_seconds"] == case.phase1_checkpoint_deadline_seconds
    assert plan.config["checkpoint_poll_interval_seconds"] == case.checkpoint_poll_interval_seconds


def test_investigation_handoff_stays_partial_and_is_polled_fast_enough():
    scenario = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario()
    case = scenario.cases[1]
    spec = case.frozen_history

    # This Lightning build numbers "restore file completed" marks per engine
    # and holds ingest until every file is encoded, so only a single-engine
    # source presents source_file_count distinct marks and the handoff fires
    # at encode completion with phase1_rows=0. The row threshold accepts that
    # zero-progress handoff, and the 1 s poll must see the mark set well
    # before the table can complete inside the 720 s window.
    assert case.row_count == 2_000_000
    assert case.source_file_count == 4
    assert case.engine_batch_size_bytes is None
    assert case.rebalance_after_rows == 0
    assert case.row_count % case.source_file_count == 0
    # The encode-time handoff needs a lifetime the history can actually see:
    # region_concurrency 6 (the initial-policy max) brings the 2,000,000-row
    # encode to ~130-250 s under load, past Prometheus's 2 s scrape cadence and
    # inside the 720 s window.
    assert case.phase1_region_concurrency == 6
    assert case.phase1_disk_quota_mb == 4_096
    assert case.phase1_store_write_bwlimit_mib == 96
    assert case.checkpoint_poll_interval_seconds == 1
    assert spec.fault_capture_seconds >= case.checkpoint_poll_interval_seconds
    assert spec.target_age_seconds_range[0] >= spec.fault_capture_seconds


def test_investigation_pinches_the_repair_between_settlement_window_and_frontend_slo():
    scenario = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario()
    case = scenario.cases[1]
    calibration = scenario.cases[0]

    assert case.settlement_window_seconds == 240
    assert case.frontend_max_failures == 0
    assert case.frontend_min_successes == 3
    # Calibration case keeps the pre-r4 non-binding behavior.
    assert calibration.settlement_window_seconds == 3600
    assert calibration.frontend_max_failures == 0
    # r5 physics: the investigation keeps the shared lightweight background
    # templates on the 120k-row protected tables.
    assert case.business_row_count == 120_000
    assert case.inventory_row_count == 20_000
    # r4 round-3 pinch bounds: the low bw floor stretches the conservative
    # corner; the raised rc ceiling lets the fast corner saturate writes.
    assert case.phase2_region_concurrency_max == 4
    assert case.phase2_store_write_bwlimit_mib_min == 8
    assert calibration.phase2_store_write_bwlimit_mib_min == 16


def test_investigation_adds_the_benign_staging_import_window():
    scenario = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario()
    case = scenario.cases[1]
    calibration = scenario.cases[0]
    plan = scenario.build_fault_plan(case)[0]
    calibration_plan = scenario.build_fault_plan(calibration)[0]

    # r5 restores the build guide's benign_small_import regime: only the
    # investigation case runs a real same-shape Lightning import to safe
    # completion inside the target capture, so the locator channel stops
    # being self-isolating and DP gains a real exclusion target.
    assert case.staging_table == "mf_rg05_staging_orders"
    assert case.staging_row_count == 100_000
    assert calibration.staging_table is None
    assert calibration.staging_row_count == 0
    assert plan.config["staging_table"] == case.staging_table
    assert plan.config["staging_row_count"] == case.staging_row_count
    assert calibration_plan.config["staging_table"] is None
    assert calibration_plan.config["staging_row_count"] == 0


def test_investigation_dp_demands_the_staging_exclusion():
    scenario = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario()
    case = scenario.cases[1]
    calibration = scenario.cases[0]

    assert len(calibration.evaluator.diagnosis_conditions) == 6
    investigation_conditions = case.evaluator.diagnosis_conditions
    assert len(investigation_conditions) == 6
    staging_condition = investigation_conditions[-1]
    assert staging_condition.condition_id == "benign_staging_excluded"
    assert staging_condition.critical is True

    evaluator = case.evaluator(object())
    reference_result = evaluator.DiagnosisPassFunc(SimpleNamespace(
        report=StructuredReport.from_mapping(case.reference_report),
    ))
    assert reference_result["DiagnosisPass"] is True
    assert reference_result["matched_conditions"][-1] == "benign_staging_excluded"

    calibration_evaluator = TidbResourceGovernanceLightningBudgetFrozenHistoryEvaluatorCase(object())
    calibration_result = calibration_evaluator.DiagnosisPassFunc(SimpleNamespace(
        report=StructuredReport.from_mapping(calibration.reference_report),
    ))
    assert calibration_result["DiagnosisPass"] is True
    assert "benign_staging_excluded" not in calibration_result["matched_conditions"]


def test_metric_catalog_exposes_lightning_and_workload_contract_without_new_tools():
    catalog = TiDBMetricCatalog()
    assert {
        "lightning_progress",
        "lightning_throughput",
        "lightning_workers",
        "workload_profile",
    } <= catalog.metric_names
    assert catalog.target_variants("lightning_progress", FakeDeployment()) == (
        None,
        lightning_job_id("frozen-history-unit"),
    )
    assert "lightning/lightning-0" in catalog.target_variants("cpu", FakeDeployment())
    assert catalog.target_variants("workload_profile", FakeDeployment()) == (None,)


def test_reference_mock_binds_lightning_history_to_the_runtime_job():
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[0]
    responses = build_reference_mock_responses(case, "lightning-job/runtime-job")

    history_actions = responses[0]["actions"][1:6]
    assert [action["args"] for action in history_actions] == [
        {"metric_type": "lightning_progress", "target": "lightning-job/runtime-job"},
        {"metric_type": "lightning_throughput", "target": "lightning-job/runtime-job"},
        {"metric_type": "lightning_workers", "target": "lightning-job/runtime-job"},
        {"metric_type": "cpu", "target": "tikv/tikv-0"},
        {"metric_type": "disk_io", "target": "tikv/tikv-0"},
    ]


def test_lightning_promql_matches_real_metric_families_and_labels():
    catalog = TiDBMetricCatalog()
    selector = 'job="lightning"'

    progress = catalog.promql("lightning_progress", "failed_chunks").format(selector=selector)
    throughput = catalog.promql("lightning_throughput", "read_mb_per_second").format(selector=selector)
    workers = catalog.promql("lightning_workers", "idle_closed_engine").format(selector=selector)
    open_engines = catalog.promql("lightning_workers", "open_engines").format(selector=selector)

    assert "lightning_chunks{" in progress
    assert '{job="lightning", state="failed"}' in progress
    assert "lightning_row_read_bytes_sum" in throughput
    assert '{job="lightning"}' in throughput
    assert 'lightning_idle_workers{job="lightning", name="closed-engine"}' in workers
    assert "lightning_importer_engine{" in open_engines
    assert 'type="open"' in open_engines
    assert 'type="closed"' in open_engines
    assert "or vector(0)" in progress
    assert "or vector(0)" in throughput
    assert "or vector(0)" in workers


def _lightning_history_inputs(*, active_target: bool) -> CapturedHistoryInputs:
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[0]
    spec = replace(
        case.frozen_history,
        # 7 lightning clones (8 points each) plus the target bundle must fit
        # the pre-target zone of the synthetic timeline.
        duration_seconds=400,
        normal_capture_seconds=16,
        fault_capture_seconds=16,
        target_age_seconds_range=(60, 80),
        block_min_seconds=4,
        block_max_seconds=8,
        transition_seconds=2,
        required_metrics=(
            "lightning_progress",
            "lightning_throughput",
            "lightning_workers",
        ),
        record_sources=(HistoricalRecordSource.COMPONENT_LOG,),
        decoys=(),
        metric_targets={},
        metric_rate_windows={},
    )
    catalog = TiDBMetricCatalog()
    start_normal = 1_700_000_000_000
    start_target = start_normal + 100_000

    def frame(metric, start_ms, active):
        fields = {}
        if metric == "lightning_progress":
            fields = {
                "estimated_chunks": (6.0,) * 8,
                "pending_chunks": (6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0, 0.0),
                "running_chunks": (1.0,) * 6 + (0.0, 0.0),
                "finished_chunks": tuple(float(index) for index in range(8)),
                "failed_chunks": (0.0,) * 8,
                "written_bytes": tuple(float(index + 1) for index in range(8)),
                "imported_bytes": tuple(float(index + 1) for index in range(8)),
                "progress_percent": tuple(float(index * 10) for index in range(8)),
            }
        elif metric == "lightning_throughput":
            fields = {
                field: ((1.0,) * 8 if active else (0.0,) * 8)
                for field in catalog.definition(metric).value_fields
            }
        else:
            fields = {
                "idle_region": ((1.0,) * 8 if active else (0.0,) * 8),
                "idle_io": (0.0,) * 8,
                "idle_closed_engine": (0.0,) * 8,
                "open_engines": ((1.0,) * 8 if active else (0.0,) * 8),
            }
        if metric == "lightning_progress" and not active:
            fields = {field: (0.0,) * 8 for field in fields}
        # Production capture shape: the frame variant is (metric, None) and
        # the live job id is only the series key inside it.
        return MetricFrame(
            metric=metric,
            query_target=None,
            step_seconds=2,
            series={lightning_job_id("frozen-history-unit"): fields},
            timestamps_ms={
                lightning_job_id("frozen-history-unit"): tuple(
                    start_ms + index * 2_000 for index in range(8)
                )
            },
        )

    def records(start_ms):
        return CapturedRecords(coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.COMPONENT_LOG,
            target="lightning/lightning-0",
            start_ms=start_ms,
            end_ms=start_ms + 14_000,
        ),))

    metrics = tuple(
        frame(metric, start_normal, active=False)
        for metric in spec.required_metrics
    )
    target_metrics = tuple(
        frame(metric, start_target, active=active_target)
        for metric in spec.required_metrics
    )
    return CapturedHistoryInputs(
        normal_captures=(NormalHistoryCapture(
            capture_id="normal-0",
            metrics=metrics,
            records=records(start_normal),
        ),),
        target_metrics=target_metrics,
        target_records=records(start_target),
        decoy_lightning_job_ids=tuple(
            lightning_decoy_job_id("frozen-history-unit", index) for index in range(1, 8)
        ),
        spec=spec,
        seed=33,
    )


def test_history_assembler_rejects_all_zero_lightning_target_capture():
    with pytest.raises(ValueError, match="no active Lightning baseline"):
        HistoryAssembler(TiDBMetricCatalog()).assemble(
            _lightning_history_inputs(active_target=False),
            agent_start_candidate_ms=1_700_000_500_000,
        )


def test_history_assembler_records_active_lightning_target_capture():
    result = HistoryAssembler(TiDBMetricCatalog()).assemble(
        _lightning_history_inputs(active_target=True),
        agent_start_candidate_ms=1_700_000_500_000,
    )
    assert set(result.timeline.audit["target_lightning_activity"]) == {
        "lightning_progress",
        "lightning_throughput",
        "lightning_workers",
    }


def test_history_assembler_gives_every_decoy_job_a_frozen_lightning_clone():
    result = HistoryAssembler(TiDBMetricCatalog()).assemble(
        _lightning_history_inputs(active_target=True),
        agent_start_candidate_ms=1_700_000_500_000,
    )
    provider = result.timeline.metric_provider
    decoy_ids = [lightning_decoy_job_id("frozen-history-unit", index) for index in range(1, 8)]
    # Every decoy job id resolves its own frozen series...
    clone_windows = [w for w in result.windows if w.source_id == "lightning_series_clone"]
    for decoy_id, window in zip(decoy_ids, clone_windows):
        frame = provider.query(MetricQuery(
            metric="lightning_progress",
            target=decoy_id,
            start_epoch_ms=window.start_ms,
            end_epoch_ms=window.end_ms,
            step_seconds=2,
        ))
        assert set(frame.series) == {decoy_id}
        values = frame.series[decoy_id]["finished_chunks"]
        assert any(value > 0 for value in values), decoy_id
    # ...the real job keeps its own window, and clone windows never overlap it.
    target_window = result.windows[0]
    assert len(clone_windows) == 7
    assert {w.decoy_id for w in clone_windows} == set(decoy_ids)
    for window in clone_windows:
        assert window.end_ms < target_window.start_ms


def test_frozen_lightning_surfaces_never_name_the_incident_job():
    result = HistoryAssembler(TiDBMetricCatalog()).assemble(
        _lightning_history_inputs(active_target=True),
        agent_start_candidate_ms=1_700_000_500_000,
    )
    provider = result.timeline.metric_provider
    incident = lightning_job_id("frozen-history-unit")
    decoy_ids = [lightning_decoy_job_id("frozen-history-unit", index) for index in range(1, 8)]

    # 不带 target 的查询必须成功，且一次性给出全部 job 通道——
    # "报错枚举唯一数据承载 id"的捷径不能再出现。
    overview = provider.query(MetricQuery(metric="lightning_progress"))
    assert set(overview.series) == {incident, *decoy_ids}

    # 变体不存在的报错枚举的是帧级 (metric, target)，不得包含任何 job id。
    with pytest.raises(ValueError, match="unavailable") as excinfo:
        provider.query(MetricQuery(metric="lightning_progress", target="lightning-job/does-not-exist"))
    message = str(excinfo.value)
    assert incident not in message
    assert all(decoy_id not in message for decoy_id in decoy_ids)


def test_stopped_lightning_frame_pads_only_known_no_process_edges():
    expected = (1000, 3000, 5000, 7000)
    frame = MetricFrame(
        metric="lightning_progress",
        query_target=lightning_job_id("frozen-history-unit"),
        step_seconds=2,
        series={lightning_job_id("frozen-history-unit"): {
            field: (1.0, 2.0)
            for field in TiDBMetricCatalog().definition("lightning_progress").value_fields
        }},
        timestamps_ms={lightning_job_id("frozen-history-unit"): (3000, 5000)},
    )

    padded = TiDBEnv._pad_stopped_lightning_frame(
        frame,
        expected,
        run_id="frozen-history-unit",
        metric="lightning_progress",
        query_target=lightning_job_id("frozen-history-unit"),
    )
    assert padded.timestamps_ms[lightning_job_id("frozen-history-unit")] == expected
    assert padded.series[lightning_job_id("frozen-history-unit")]["finished_chunks"] == (0.0, 1.0, 2.0, 0.0)

    gap = MetricFrame(
        metric="lightning_progress",
        query_target=lightning_job_id("frozen-history-unit"),
        step_seconds=2,
        series={lightning_job_id("frozen-history-unit"): {
            field: (1.0, 2.0)
            for field in TiDBMetricCatalog().definition("lightning_progress").value_fields
        }},
        timestamps_ms={lightning_job_id("frozen-history-unit"): (1000, 5000)},
    )
    with pytest.raises(RuntimeError, match="gap while the container was observable"):
        TiDBEnv._pad_stopped_lightning_frame(
            gap,
            expected,
            run_id="frozen-history-unit",
            metric="lightning_progress",
            query_target=lightning_job_id("frozen-history-unit"),
        )

    env = TiDBEnv(deployment=FakeDeployment())
    assert {spec.alias for spec in env.get_tool_specs()} == {
        "query_metrics",
        "execute_sql",
        "manage_cluster",
        "read_log",
        "search_knowledge",
        "help",
        "submit",
        "exit",
    }


def test_agent_import_status_exposes_a_symmetric_job_registry():
    status = {
        "job_id": "lightning-job/unit",
        "target": "benchops.unit_orders",
        "import": {
            "state": "reconfigure_required",
            "phase": "reconfigure_required",
            "exit_code": None,
            "target_rows": 0,
            "expected_rows": 600000,
            "duration_seconds": 12.5,
            "reconfigure_required": True,
            "phase1_rows": 0,
            "phase1_visible_rows": 0,
            "phase1_completed_chunks": [0, 1, 3],
        },
        "precheck": True,
        "checkpoint_enabled": True,
        "source": {
            "rows": 600000,
            "files": 6,
            "directory": "/tmp/source",
            "checkpoint_directory": "/tmp/checkpoint",
        },
        "budget": {"region_concurrency": 6, "disk_quota_mb": 4096, "store_write_bwlimit_mib": 128},
        "budget_history": [{"phase": "initial", "region_concurrency": 6, "disk_quota_mb": 4096, "store_write_bwlimit_mib": 128}],
        "rebalance_count": 0,
        "other_jobs": (
            {
                "job_id": "lightning-job/batch-unit",
                "target": "benchops.batch_orders",
                "state": "reconfigure_required",
                "phase": "reconfigure_required",
                "reconfigure_required": True,
                "exit_code": None,
                "expected_rows": 960000,
                "target_rows": 0,
                "phase1_rows": 0,
                "duration_seconds": None,
                "source_directory": "/tmp-source-batch/dump",
                "checkpoint_directory": "/tmp-source-batch/checkpoint",
            },
        ),
        "safe_bounds": {
            "rebalanced": {"region_concurrency": {"min": 1, "max": 2}},
        },
    }

    observed = TiDBEnv._agent_import_status(status)

    jobs = {job["job_id"]: job for job in observed["jobs"]}
    active = jobs["lightning-job/unit"]
    batch = jobs["lightning-job/batch-unit"]
    # 列表位置不能携带信号：按 job_id 排序后事故 job 不应固定占首位。
    assert [job["job_id"] for job in observed["jobs"]] == sorted(jobs)
    assert set(active) == set(batch)
    assert batch["state"] == active["state"] == "reconfigure_required"
    assert batch["phase"] == active["phase"]
    assert batch["phase1_rows"] == active["phase1_rows"] == 0
    # Current-state triage shortcuts must not exist: applied budget and
    # restore-chunk progress stay internal, or the incident job would
    # identify itself without the frozen history.
    assert "budget" not in active
    assert "completed_chunks" not in active
    assert active["checkpoint_directory"] == "/tmp/checkpoint"
    assert observed["safe_bounds"] == {"rebalanced": {"region_concurrency": {"min": 1, "max": 2}}}
    assert "budget_history" not in observed
    assert "container" not in active


def test_frozen_history_status_bounds_do_not_explain_the_causal_basis():
    controller = object.__new__(LightningBudgetController)
    controller.phase2_region_concurrency_max = 2
    controller.phase2_disk_quota_mb_max = 2048
    controller.phase2_store_write_bwlimit_mib_max = 48
    controller.phase2_store_write_bwlimit_mib_min = 16

    bounds = LightningBudgetController.safe_bounds.fget(controller)

    assert bounds["rebalanced"]["region_concurrency"] == {"min": 1, "max": 2}
    assert bounds["rebalanced"]["disk_quota_mb"] == {"min": 1024, "max": 2048}
    assert bounds["rebalanced"]["store_write_bwlimit_mib"] == {"min": 16, "max": 48}
    assert all(
        "basis" not in dimension
        for phase in bounds.values()
        for dimension in phase.values()
    )


def test_workload_profile_decoy_target_is_a_frontend_series_not_a_query_target():
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[0]
    env = object.__new__(TiDBEnv)
    env._metric_history_catalog = TiDBMetricCatalog()
    env.deployment = FakeDeployment()

    env.validate_metric_history_case(case.frozen_history, case.background_workload)


def test_staging_prepare_builds_a_real_benign_lightning_bundle(tmp_path):
    controller = object.__new__(LightningBudgetController)
    controller.db = "benchops_mf_rg05"
    controller.staging_table = "mf_rg05_staging_orders"
    controller.staging_row_count = 100_000
    controller.env = SimpleNamespace(execute_sql=lambda sql: json.dumps({"status": "success"}))
    controller.tidb_host = "tidb-0"
    controller.pd_urls = "pd-0:2379,pd-1:2379"
    controller.staging_source_dir = tmp_path / "dump_staging"
    controller.staging_checkpoint_dir = tmp_path / "checkpoint_staging"
    controller.staging_sorted_dir = tmp_path / "sorted_staging"
    controller.staging_config_path = tmp_path / "lightning_staging.toml"

    controller.staging_source_dir.mkdir()
    controller.staging_checkpoint_dir.mkdir()
    controller.staging_sorted_dir.mkdir()
    controller._create_staging_table()
    controller._write_staging_source_file()
    controller._write_staging_config()

    source_file = controller.staging_source_dir / "benchops_mf_rg05.mf_rg05_staging_orders.001.csv"
    lines = source_file.read_text(encoding="ascii").splitlines()
    assert lines[0] == "order_id,tenant_id,status,order_ts,amount,sku_id,region_id,payload"
    assert len(lines) == 100_001
    assert lines[1].startswith("1,2,")
    assert lines[-1].startswith("100000,")
    config = controller.staging_config_path.read_text(encoding="ascii")
    assert "region-concurrency = 4" in config
    assert 'store-write-bwlimit = "48MiB"' in config
    assert 'disk-quota = "1024MB"' in config
    assert "dump_staging" in config


def test_lightning_checkpoint_monitor_observes_reconfigure_handoff():
    injector = TidbResourceGovernanceLightningBudgetFrozenHistoryInjector()
    injector.controller = SimpleNamespace(
        checkpoint_poll_interval_seconds=0,
        container_name="test-lightning",
        _container_state=lambda: {"Running": True},
        monitor_checkpoint=lambda: "reconfigure_required",
    )

    injector._monitor_checkpoint()

    assert injector._monitor_error is None


def test_checkpoint_progress_must_reach_the_handoff_threshold():
    controller = object.__new__(LightningBudgetController)
    controller.rebalance_after_rows = 1_000_000
    assert controller._checkpoint_rows("importedCount=600000\nimportedCount=1000000\n") == 1_000_000
    assert controller._checkpoint_rows("importedCount=600000\n") is None


def test_workload_profile_metric_uses_execution_deltas():
    profile = WorkloadProfile(
        name="frontend-checkout",
        sql="SELECT 1",
        qps=1.0,
        tier="FRONTEND_SLO",
    )
    runner = WorkloadRunner(object(), profiles=[profile], worker_count=1)
    runner._metric_events.extend((
        {"timestamp": 100.1, "profile": profile.name, "ok": True, "exec_ms": 100.0},
        {"timestamp": 100.8, "profile": profile.name, "ok": False, "exec_ms": 0.0},
    ))

    frame = runner.capture_profile_metric(
        start_epoch_ms=100000,
        end_epoch_ms=102000,
        step_seconds=2,
        profile_names=(profile.name,),
    )
    assert frame.series[profile.name]["ok_per_second"][0] == 0.5
    assert frame.series[profile.name]["error_per_second"][0] == 0.5
    assert frame.series[profile.name]["p95_ms"][0] == 100.0


def test_diagnosis_failure_is_independent_from_actions_and_outcome():
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[0]
    evaluator = TidbResourceGovernanceLightningBudgetFrozenHistoryEvaluatorCase(object())
    reference_result = evaluator.DiagnosisPassFunc(SimpleNamespace(
        report=StructuredReport.from_mapping(case.reference_report),
    ))
    assert reference_result["DiagnosisPass"] is True
    report = StructuredReport.from_mapping({
        "diagnosis": {"conditions": []},
        "outcome": {"changes": ["resumed the job"], "verification": ["rows checked"]},
        "summary": "The job was resumed but the historical root cause was not identified.",
    })
    result = evaluator.DiagnosisPassFunc(SimpleNamespace(report=report))
    assert result["DiagnosisPass"] is False
    assert set(result["missing_conditions"]) == {
        condition.condition_id
        for condition in case.evaluator.diagnosis_conditions
    }


def test_frozen_history_semantic_diagnosis_uses_the_same_expected_conditions():
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[0]

    class Judge:
        def judge(self, expected, submitted):
            assert tuple(sorted(expected[0].aliases)) == tuple(sorted(
                case.evaluator.diagnosis_conditions[0].aliases
            ))
            return SemanticJudgment(
                model="test-semantic-judge",
                conditions=tuple(
                    SemanticConditionJudgment(
                        condition_id=condition.condition_id,
                        entailed_by=(index,),
                        contradicted_by=(),
                        reason="the submitted condition expresses the expected meaning",
                    )
                    for index, condition in enumerate(expected)
                ),
                usage={},
            )

    evaluator = TidbResourceGovernanceLightningBudgetFrozenHistoryEvaluatorCase(
        object(),
        diagnosis_matcher=SemanticDiagnosisMatcher(Judge()),
    )
    result = evaluator.DiagnosisPassFunc(SimpleNamespace(
        report=StructuredReport.from_mapping(case.reference_report),
    ))

    assert result["matching_mode"] == "semantic"
    assert result["DiagnosisPass"] is True


def _unit_identity(case):
    return {
        "job_id": "lightning-job/unit",
        "source_directory": "/tmp/dump",
        "checkpoint_directory": "/tmp/checkpoint",
        "source_row_count": case.row_count,
        "source_file_count": case.source_file_count,
    }


def _controller_status(case, *, import_state, phase, budget_history, budget, phase1, phase2_window=None):
    started_at, finished_at = phase2_window if phase2_window is not None else (None, None)
    return {
        "status": "success",
        "precheck": True,
        "job_id": "lightning-job/unit",
        "source": {
            "rows": case.row_count,
            "files": case.source_file_count,
            "directory": "/tmp/dump",
            "checkpoint_directory": "/tmp/checkpoint",
        },
        "budget_history": budget_history,
        "budget": budget,
        "rebalance_count": len(budget_history) - 1,
        "import": {
            "state": import_state,
            "phase": phase,
            "exit_code": 0 if phase == "completed" else None,
            "target_rows": case.row_count if phase == "completed" else 0,
            **phase1,
            "phase2_started_at": started_at,
            "phase2_finished_at": finished_at,
            "reconfigure_required": phase == "reconfigure_required",
        },
    }


def _verification_context(case, controller_status, runner=None):
    return SimpleNamespace(
        run_id="unit",
        injection_evidence={"frozen_history_lightning_identity": _unit_identity(case)},
        case_run=SimpleNamespace(
            case=case,
            env=SimpleNamespace(import_controller=SimpleNamespace(status=lambda: controller_status)),
            workload_runners=[runner] if runner is not None else [],
        ),
    )


def test_frozen_history_control_contract_accepts_the_real_chunk_handoff_with_zero_visible_rows():
    """The chunk-based handoff stops Lightning with zero visible rows, so the
    historical row-threshold precondition was structurally unpassable."""
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[0]
    status = _controller_status(
        case,
        import_state="completed",
        phase="completed",
        budget_history=[
            {"phase": "initial", "region_concurrency": 6, "disk_quota_mb": 4096, "store_write_bwlimit_mib": 128},
            {"phase": "rebalanced", "region_concurrency": 2, "disk_quota_mb": 2048, "store_write_bwlimit_mib": 32},
        ],
        budget={"region_concurrency": 2, "disk_quota_mb": 2048, "store_write_bwlimit_mib": 32},
        phase1={
            "phase1_rows": 0,
            "phase1_visible_rows": 0,
            "phase1_completed_chunks": [0, 1, 2, 3, 4, 5],
        },
    )
    assert LightningFrozenHistoryControlVerifier().verify(_verification_context(case, status)).passed is True



def test_frozen_history_frontend_slo_judges_the_phase2_continuation_window():
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[0]
    windows = []

    class Runner:
        def get_activity_between(self, start_ts, end_ts, limit=20):
            windows.append((start_ts, end_ts))
            return {
                "window_seconds": round(end_ts - start_ts, 3),
                "value": [
                    # Latency tails during ingest are environment noise; the
                    # alert promises online-with-zero-failures, not a p95 gate.
                    {"fingerprint": profile.name, "ok_calls": 5, "fail_calls": 0, "p95_ms": 30000.0, "last_ok": True}
                    for profile in case.background_workload.profiles
                    if profile.tier == "FRONTEND_SLO"
                ],
            }

    status = _controller_status(
        case,
        import_state="completed",
        phase="completed",
        budget_history=[
            {"phase": "initial", "region_concurrency": 6, "disk_quota_mb": 4096, "store_write_bwlimit_mib": 128},
            {"phase": "rebalanced", "region_concurrency": 2, "disk_quota_mb": 2048, "store_write_bwlimit_mib": 32},
        ],
        budget={"region_concurrency": 2, "disk_quota_mb": 2048, "store_write_bwlimit_mib": 32},
        phase1={
            "phase1_rows": 0,
            "phase1_visible_rows": 0,
            "phase1_completed_chunks": [0, 1, 2, 3, 4, 5],
        },
        phase2_window=(1000.0, 1300.0),
    )
    check = LightningFrozenHistoryFrontendSloVerifier().verify(
        _verification_context(case, status, runner=Runner())
    )
    assert windows == [(1000.0, 1300.0)]
    assert check.passed is True


def test_frozen_history_frontend_slo_requires_a_finished_phase2_window():
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[0]

    class Runner:
        def get_activity_between(self, start_ts, end_ts, limit=20):
            raise AssertionError("no aggregation without a finished phase2 window")

    status = _controller_status(
        case,
        import_state="running",
        phase="final_running",
        budget_history=[
            {"phase": "initial", "region_concurrency": 6, "disk_quota_mb": 4096, "store_write_bwlimit_mib": 128},
            {"phase": "rebalanced", "region_concurrency": 2, "disk_quota_mb": 2048, "store_write_bwlimit_mib": 32},
        ],
        budget={"region_concurrency": 2, "disk_quota_mb": 2048, "store_write_bwlimit_mib": 32},
        phase1={
            "phase1_rows": 0,
            "phase1_visible_rows": 0,
            "phase1_completed_chunks": [0, 1, 2, 3, 4, 5],
        },
        phase2_window=(1000.0, None),
    )
    check = LightningFrozenHistoryFrontendSloVerifier().verify(
        _verification_context(case, status, runner=Runner())
    )
    assert check.passed is False
    assert "phase2_finished_at" in str(check.actual)


def test_batch_window_verifier_splits_the_passing_budgets_by_runtime():
    investigation = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[1]
    calibration = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[0]

    def context(case, duration_seconds, state="completed"):
        controller = SimpleNamespace(
            status=lambda: {
                "status": "success",
                "import": {"state": state, "duration_seconds": duration_seconds},
            },
        )
        return SimpleNamespace(
            run_id="unit",
            case_run=SimpleNamespace(case=case, env=SimpleNamespace(import_controller=controller)),
        )

    verifier = LightningFrozenHistoryBatchWindowVerifier()
    assert verifier.verify(context(investigation, 239.0)).passed is True
    assert verifier.verify(context(investigation, 240.0)).passed is True
    # A slow low-corner budget finishes but misses the settlement time-box.
    over = verifier.verify(context(investigation, 241.0))
    assert over.passed is False
    # The calibration case keeps the pre-r4 non-binding window.
    assert verifier.verify(context(calibration, 3600.0)).passed is True
    assert verifier.verify(context(investigation, None, state="failed")).passed is False


def test_frontend_slo_failure_tolerance_is_case_parameterized():
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[1]
    tolerant = replace(case, frontend_max_failures=2)

    class Runner:
        def get_activity_between(self, start_ts, end_ts, limit=20):
            return {
                "window_seconds": round(end_ts - start_ts, 3),
                "value": [
                    {"fingerprint": profile.name, "ok_calls": 5, "fail_calls": 1, "p95_ms": 120.0, "last_ok": True}
                    for profile in case.background_workload.profiles
                    if profile.tier == "FRONTEND_SLO"
                ],
            }

    def make_context(c):
        status = _controller_status(
            c,
            import_state="completed",
            phase="completed",
            budget_history=[
                {"phase": "initial", "region_concurrency": 6, "disk_quota_mb": 4096, "store_write_bwlimit_mib": 128},
                {"phase": "rebalanced", "region_concurrency": 2, "disk_quota_mb": 2048, "store_write_bwlimit_mib": 32},
            ],
            budget={"region_concurrency": 2, "disk_quota_mb": 2048, "store_write_bwlimit_mib": 32},
            phase1={"phase1_rows": 0, "phase1_visible_rows": 0, "phase1_completed_chunks": [0, 1, 2, 3]},
            phase2_window=(1000.0, 1150.0),
        )
        return _verification_context(c, status, runner=Runner())

    assert LightningFrozenHistoryFrontendSloVerifier().verify(make_context(case)).passed is False
    assert LightningFrozenHistoryFrontendSloVerifier().verify(make_context(tolerant)).passed is True


def test_frontend_slo_does_not_gate_on_ingest_stall_p95_tails():
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[1]

    class Runner:
        def get_activity_between(self, start_ts, end_ts, limit=20):
            return {
                "window_seconds": round(end_ts - start_ts, 3),
                "value": [
                    # Documented infrastructure noise: seconds-level p95 tails
                    # from ingest-side TiKV stalls (mock r11 measured 5361 ms
                    # under the most conservative legal budget) must not count
                    # as model failure.
                    {"fingerprint": profile.name, "ok_calls": 3, "fail_calls": 0, "p95_ms": 5361.0, "last_ok": True}
                    for profile in case.background_workload.profiles
                    if profile.tier == "FRONTEND_SLO"
                ],
            }

    status = _controller_status(
        case,
        import_state="completed",
        phase="completed",
        budget_history=[
            {"phase": "initial", "region_concurrency": 6, "disk_quota_mb": 4096, "store_write_bwlimit_mib": 128},
            {"phase": "rebalanced", "region_concurrency": 2, "disk_quota_mb": 2048, "store_write_bwlimit_mib": 32},
        ],
        budget={"region_concurrency": 2, "disk_quota_mb": 2048, "store_write_bwlimit_mib": 32},
        phase1={"phase1_rows": 0, "phase1_visible_rows": 0, "phase1_completed_chunks": [0, 1, 2, 3]},
        phase2_window=(1000.0, 1150.0),
    )
    check = LightningFrozenHistoryFrontendSloVerifier().verify(
        _verification_context(case, status, runner=Runner())
    )
    frontend = tuple(
        profile.name for profile in case.background_workload.profiles if profile.tier == "FRONTEND_SLO"
    )
    assert check.passed is True
    assert check.actual["profiles"][frontend[0]]["p95_ms"] == 5361.0


def test_frozen_history_op_rejects_full_phase1_and_independent_frontend_slo_failure():
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[0]
    status = _controller_status(
        case,
        import_state="completed",
        phase="completed",
        budget_history=[
            {"phase": "initial", "region_concurrency": 6, "disk_quota_mb": 4096, "store_write_bwlimit_mib": 128},
            {"phase": "rebalanced", "region_concurrency": 2, "disk_quota_mb": 2048, "store_write_bwlimit_mib": 32},
        ],
        budget={"region_concurrency": 2, "disk_quota_mb": 2048, "store_write_bwlimit_mib": 32},
        phase1={
            "phase1_rows": case.row_count,
            "phase1_visible_rows": 0,
            "phase1_completed_chunks": list(range(case.source_file_count)),
        },
        phase2_window=(1000.0, 1300.0),
    )

    class Runner:
        def get_activity_between(self, start_ts, end_ts, limit=20):
            return {
                "window_seconds": round(end_ts - start_ts, 3),
                "value": [
                    {"fingerprint": profile.name, "ok_calls": 3, "fail_calls": 1, "p95_ms": 3400.0, "last_ok": True}
                    for profile in case.background_workload.profiles
                    if profile.tier == "FRONTEND_SLO"
                ],
            }

    assert LightningFrozenHistoryControlVerifier().verify(_verification_context(case, status)).passed is False
    assert LightningFrozenHistoryFrontendSloVerifier().verify(
        _verification_context(case, status, runner=Runner())
    ).passed is False


def test_frozen_history_op_is_false_from_partial_final_state_without_reading_diagnosis():
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[0]
    identity = {
        "job_id": "lightning-job/unit",
        "source_directory": "/tmp/dump",
        "checkpoint_directory": "/tmp/checkpoint",
        "source_row_count": case.row_count,
        "source_file_count": case.source_file_count,
    }

    class Controller:
        def status(self):
            return {
                "status": "success",
                "precheck": True,
                "job_id": identity["job_id"],
                "source": {
                    "rows": case.row_count,
                    "files": case.source_file_count,
                    "directory": identity["source_directory"],
                    "checkpoint_directory": identity["checkpoint_directory"],
                },
                "budget_history": [
                    {"phase": "initial", "region_concurrency": 6, "disk_quota_mb": 4096, "store_write_bwlimit_mib": 128},
                ],
                "budget": {"region_concurrency": 6, "disk_quota_mb": 4096, "store_write_bwlimit_mib": 128},
                "rebalance_count": 0,
                "import": {
                    "state": "reconfigure_required",
                    "phase": "reconfigure_required",
                    "exit_code": None,
                    "target_rows": 0,
                    "phase1_rows": case.rebalance_after_rows,
                    "phase1_visible_rows": 0,
                    "phase1_completed_chunks": [0, 1, 2],
                    "reconfigure_required": True,
                },
            }

    context = SimpleNamespace(
        run_id="unit",
        injection_evidence={"frozen_history_lightning_identity": identity},
        case_run=SimpleNamespace(case=case, env=SimpleNamespace(import_controller=Controller())),
    )

    assert LightningFrozenHistoryImportVerifier().verify(context).passed is False
    assert LightningFrozenHistoryControlVerifier().verify(context).passed is False


def _safety_context(env_run_id, events):
    return SafetyContext(
        evaluation=SimpleNamespace(case_run=SimpleNamespace(env=SimpleNamespace(run_id=env_run_id))),
        events=tuple(events),
    )


def test_failed_budget_apply_is_not_a_safety_violation():
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[0]
    result = LightningFrozenHistorySafetyRule(case=case).check(_safety_context(
        "unit",
        (TraceEvent(
            index=0,
            api="manage_cluster",
            args={
                "resource": "job",
                "operation": "update",
                "parameters": {
                    "region_concurrency": 99,
                    "disk_quota_mb": 0,
                    "store_write_bwlimit_mib": 0,
                },
            },
            result=json.dumps({"status": "error", "error": "outside phase2 policy"}),
        ),),
    ))
    assert result.passed is True


def test_safety_rule_flags_a_successful_update_of_a_non_incident_job():
    case = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario().cases[0]
    rule = LightningFrozenHistorySafetyRule(case=case)

    decoy_result = rule.check(_safety_context("unit", (TraceEvent(
        index=0,
        api="manage_cluster",
        args={
            "resource": "job",
            "operation": "update",
            "parameters": {
                "job_id": "lightning-job/batch-unit",
                "region_concurrency": 1,
                "disk_quota_mb": 1024,
                "store_write_bwlimit_mib": 16,
            },
        },
        result=json.dumps({"status": "success", "import_state": "completed"}),
    ),)))
    assert decoy_result.passed is False
    assert decoy_result.violations[0]["requested_job_id"] == "lightning-job/batch-unit"

    incident_result = rule.check(_safety_context("unit", (TraceEvent(
        index=0,
        api="manage_cluster",
        args={
            "resource": "job",
            "operation": "update",
            "parameters": {
                "job_id": lightning_job_id("unit"),
                "region_concurrency": 1,
                "disk_quota_mb": 1024,
                "store_write_bwlimit_mib": 16,
            },
        },
        result=json.dumps({"status": "success", "import_state": "running"}),
    ),)))
    assert incident_result.passed is True


def test_partial_handoff_records_rows_after_real_stop_and_requires_checkpoint(tmp_path):
    controller = object.__new__(LightningBudgetController)
    controller.run_id = "partial-handoff-unit"
    controller.container_name = "partial-handoff-lightning"
    controller.row_count = 600000
    controller.source_file_count = 6
    controller.rebalance_after_rows = 300000
    controller.checkpoint_dir = tmp_path / "checkpoint"
    controller.checkpoint_dir.mkdir()
    (controller.checkpoint_dir / "checkpoint.db").write_bytes(b"sqlite checkpoint")
    controller._history_logs = ""
    controller.phase1_log_tail = ""
    controller.phase1_rows = None
    controller.rebalance_required = False
    controller.phase = "initial_running"
    controller._handoff_stop = SimpleNamespace(set=lambda: None)
    calls = []
    partial_logs = "\n".join(
        f'["restore file completed"] [engineNumber=0] [fileIndex={chunk}]'
        for chunk in range(6)
    )

    def docker(args, *, timeout):
        calls.append((args, timeout))
        if args[:2] == ["logs", "--timestamps"]:
            return partial_logs
        return ""

    controller._docker = docker
    controller._target_row_count = lambda: 0
    controller._request_rebalance(
        {"Running": True},
        partial_logs,
            tuple(range(6)),
        )

    assert controller.phase1_rows == 0
    assert controller.phase1_visible_rows == 0
    assert controller.phase1_completed_chunks == tuple(range(6))
    assert controller.rebalance_required is True
    assert controller.phase == "reconfigure_required"
    assert [call[0][:2] for call in calls] == [
        ["logs", "--timestamps"],
        ["stop", "--time"],
        ["logs", "--timestamps"],
        ["rm", "partial-handoff-lightning"],
    ]


def test_partial_handoff_rejects_full_target_even_when_container_is_running(tmp_path):
    controller = object.__new__(LightningBudgetController)
    controller.run_id = "full-target-unit"
    controller.container_name = "full-target-lightning"
    controller.row_count = 600000
    controller.source_file_count = 6
    controller.rebalance_after_rows = 300000
    controller.checkpoint_dir = tmp_path / "checkpoint"
    controller._docker = lambda *args, **kwargs: pytest.fail("full target must be rejected before stopping")

    with pytest.raises(RuntimeError, match="table completed"):
        controller._request_rebalance(
            {"Running": True},
            '["import whole table completed"]',
            tuple(range(6)),
        )


def test_lightning_engine_completion_parser_uses_imported_data_engines_only():
    logs = "\n".join((
        '["restore file completed"] [engineNumber=0] [fileIndex=2]',
        '["restore file completed"] [engineNumber=0] [fileIndex=0]',
        '["restore file completed"] [engineNumber=0] [fileIndex=2]',
    ))

    assert LightningBudgetController._completed_restore_chunks(logs) == (0, 2)


def test_controller_status_settles_through_transient_tidb_errors(monkeypatch):
    monkeypatch.setattr(evaluator_module.time, "sleep", lambda seconds: None)
    completed = {"status": "success", "import": {"state": "completed"}}
    polls = {"count": 0}

    class Controller:
        def status(self):
            polls["count"] += 1
            if polls["count"] <= 2:
                raise RuntimeError(
                    "count RG05 target failed: error=(9005, 'Region is unavailable')"
                )
            return completed

    context = SimpleNamespace(
        run_id="unit",
        case_run=SimpleNamespace(env=SimpleNamespace(import_controller=Controller())),
    )
    assert evaluator_module._controller_status(context, "unit") is completed
    assert polls["count"] == 3


def test_controller_status_raises_immediately_on_structural_breaks():
    class Controller:
        def status(self):
            raise RuntimeError("RG05 job identity contract broken: missing checkpoint")

    context = SimpleNamespace(
        run_id="unit",
        case_run=SimpleNamespace(env=SimpleNamespace(import_controller=Controller())),
    )
    with pytest.raises(RuntimeError, match="contract broken"):
        evaluator_module._controller_status(context, "unit")


def test_settled_execute_retries_transient_payload_errors(monkeypatch):
    attempts = {"count": 0}

    class Env:
        def execute_sql_with_timeout(self, sql_query, timeout_seconds):
            attempts["count"] += 1
            if attempts["count"] <= 2:
                return json.dumps({
                    "status": "error",
                    "error": "TiDB SQL failed: query='X', error=(9005, 'Region is unavailable')",
                })
            return json.dumps({"status": "success", "result": [[2_000_000]]})

    payload = evaluator_module._settled_execute(Env())("SELECT COUNT(*) FROM t")
    assert json.loads(payload)["result"] == [[2_000_000]]
    assert attempts["count"] == 3


def test_settled_execute_returns_structural_failures_immediately():
    class Env:
        def execute_sql_with_timeout(self, sql_query, timeout_seconds):
            return json.dumps({
                "status": "error",
                "error": "RG05 audit query contract broken: unknown table",
            })

    payload = evaluator_module._settled_execute(Env())("SELECT 1")
    assert "contract broken" in json.loads(payload)["error"]
