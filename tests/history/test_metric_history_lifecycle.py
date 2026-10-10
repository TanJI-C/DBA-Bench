from types import SimpleNamespace

import pytest

from src.execution.history.metrics import MetricDefinition, MetricFrame
from src.execution.history.records import CapturedRecords, HistoricalCoverage, HistoricalRecordSource
from src.scenarios.runtime import orchestrator as orchestrator_module
from src.scenarios.runtime.orchestrator import InjectionState, Orchestrator, OrchestratorRunConfig
from src.scenarios.frozen_history import FrozenHistorySpec
from src.scenarios.workloads import BackgroundWorkloadStartPhase, WorkloadProfile


BASE_MS = 1_700_000_000_000


class StubMetricCatalog:
    system = "stub"

    @property
    def metric_names(self):
        return frozenset({"qps"})

    def definition(self, metric):
        if metric != "qps":
            raise ValueError(metric)
        return MetricDefinition(name="qps", value_fields=("queries_per_second",), lookback_seconds=0, source_step_seconds=2, lower_bound=0.0, upper_bound=None)

    def target_variants(self, metric, deployment):
        self.definition(metric)
        return (None,)

    def validate_target(self, metric, target, deployment):
        if target is not None:
            raise ValueError(target)

    def fingerprint(self):
        return "stub-catalog-v1"


class FakeHistoryEnv:
    sample_interval_sec = 2

    def __init__(self, events):
        self.events = events
        self.deployment = object()
        self.bound = None
        self.disable_generic_sampler = None
        self.sampler_flags = []

    def configure_case(self, case):
        self.events.append("configure_case")

    def metric_history_catalog(self):
        return StubMetricCatalog()

    def validate_metric_history_case(self, spec, background_workload):
        self.events.append("validate_metric_history_case")

    def metric_history_warmup_seconds(self, required_metrics):
        return 2.0

    def deploy(self):
        self.events.append("deploy")
        self.sampler_flags.append(("deploy", self.disable_generic_sampler))

    def configure_history_observability(self, spec):
        self.events.append("configure_history_observability")
        self.sampler_flags.append(("configure", self.disable_generic_sampler))

    def capture_metric_history(self, metrics, start_ms, end_ms, step_seconds, *, metric_targets=None, rate_windows=None):
        self.events.append("capture_metrics")
        start = BASE_MS if self.events.count("capture_metrics") == 1 else BASE_MS + 100_000
        values = (10.0, 11.0, 10.5, 11.5, 10.8)
        return (MetricFrame(
            metric="qps",
            query_target=None,
            step_seconds=2,
            series={"postgres": {"queries_per_second": values}},
            timestamps_ms={"postgres": tuple(start + index * 2_000 for index in range(len(values)))},
        ),)

    def capture_history_records(self, sources, start_ms, end_ms):
        self.events.append("capture_records")
        return CapturedRecords(coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.COMPONENT_LOG,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 8_000,
        ),))

    def bind_metric_history(self, timeline):
        self.events.append("bind_metric_history")
        self.bound = timeline


class RetainedRunner:
    def __init__(self, events):
        self.events = events
        self.stopped = False

    def begin_observation_window(self):
        self.events.append("begin_observation_window")

    def stop(self):
        self.stopped = True
        self.events.append("stop_runner")


class RetainedHistoryEnv(FakeHistoryEnv):
    def __init__(self, events, runner):
        super().__init__(events)
        self._workload_runner = runner


class FakeEvaluator:
    def __init__(self, events):
        self.events = events

    def capture_safety_baseline(self, case_run):
        self.events.append("capture_safety_baseline")


def _case():
    workload = SimpleNamespace(
        profiles=(WorkloadProfile(name="history", sql="SELECT 1", qps=1.0),),
        worker_count=1,
        warmup_seconds=0,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
    )
    spec = FrozenHistorySpec(
        schema_version=1,
        duration_seconds=40,
        normal_capture_seconds=8,
        fault_capture_seconds=8,
        base_step_seconds=2,
        overview_step_seconds=4,
        block_min_seconds=4,
        block_max_seconds=4,
        transition_seconds=2,
        target_age_seconds_range=(8, 12),
        required_metrics=("qps",),
        record_sources=(HistoricalRecordSource.COMPONENT_LOG,),
        decoys=(),
        max_points_per_series=100,
        max_scalar_samples_per_response=100,
        max_history_records_per_response=20,
    )
    return SimpleNamespace(case_id="history-case", frozen_history=spec, background_workload=workload)


def _orchestrator(events, *, snapshot_mode="off"):
    scenario = SimpleNamespace(
        scenario_id="history-scenario",
        description="history test",
        system=SimpleNamespace(value="postgresql"),
        build_fault_plan=lambda _case: (),
    )
    orchestrator = Orchestrator.__new__(Orchestrator)
    orchestrator.env = FakeHistoryEnv(events)
    orchestrator.scenario = scenario
    orchestrator.case = _case()
    orchestrator.run_config = OrchestratorRunConfig(fault_snapshot_mode=snapshot_mode, history_seed=7)
    orchestrator.agent = SimpleNamespace()
    orchestrator.case_run = SimpleNamespace(run_id="history-run", injections=[], workload_runners=[], metric_history={}, background_workload_planned={}, background_workload_observed={})
    orchestrator.action_history = []
    orchestrator.turn_history = []
    orchestrator.evaluator = FakeEvaluator(events)
    orchestrator.case.evaluator = orchestrator.evaluator
    orchestrator._setup_started = False
    return orchestrator


def test_frozen_history_setup_binds_history_after_real_capture_phases(monkeypatch):
    events = []
    orchestrator = _orchestrator(events)
    orchestrator.case_run.injections = [SimpleNamespace(
        injector=SimpleNamespace(
            prepare_metric_history=lambda context: events.append("prepare_metric_history"),
            quiesce=lambda context: events.append("quiesce"),
        ),
        context=object(),
        state=InjectionState.READY,
    )]
    monkeypatch.setattr(orchestrator_module.time, "sleep", lambda seconds: events.append(("sleep", seconds)))
    orchestrator._start_workload_runner = lambda: events.append("start_workload")
    orchestrator._stop_workload_runners_for_snapshot = lambda: events.append("stop_workload")
    orchestrator._install_faults = lambda: events.append("install_faults")
    orchestrator._prepare_observability = lambda: events.append("prepare_observability")
    orchestrator._sleep_until_ms = lambda deadline: events.append(("sleep_until", deadline))
    orchestrator.setup()
    names = [event if isinstance(event, str) else event[0] for event in events]
    assert names == ["configure_case", "validate_metric_history_case", "deploy", "prepare_metric_history", "start_workload", "configure_history_observability", "sleep", "sleep_until", "capture_metrics", "capture_records", "install_faults", "prepare_observability", "sleep_until", "sleep_until", "capture_metrics", "capture_records", "quiesce", "bind_metric_history", "capture_safety_baseline"]
    assert orchestrator.env.disable_generic_sampler is False
    assert orchestrator.env.sampler_flags == [("deploy", True), ("configure", False)]
    assert orchestrator.env.bound.history_sha256
    assert orchestrator.case_run.metric_history["seed"] == 7


def test_frozen_history_setup_rejects_fault_snapshot_before_deploy():
    events = []
    orchestrator = _orchestrator(events, snapshot_mode="auto")
    with pytest.raises(RuntimeError, match="fault_snapshot_mode='off'"):
        orchestrator._setup_frozen_history_case()
    assert events == []


def test_frozen_history_capture_waits_for_sampler_endpoint_tick(monkeypatch):
    orchestrator = Orchestrator.__new__(Orchestrator)
    deadlines = []
    monkeypatch.setattr(orchestrator, "_sleep_until_ms", lambda deadline: deadlines.append(deadline))

    orchestrator._sleep_until_history_capture(10_000, 2)

    assert deadlines == [12_000]


def test_frozen_history_setup_retains_declared_workload_runner_after_target_capture(monkeypatch):
    events = []
    runner = RetainedRunner(events)
    orchestrator = _orchestrator(events)
    orchestrator.env = RetainedHistoryEnv(events, runner)
    orchestrator.case_run.injections = [SimpleNamespace(
        injector=SimpleNamespace(
            retain_workload_after_metric_history=True,
            prepare_metric_history=lambda context: events.append("prepare_metric_history"),
            quiesce=lambda context: events.append("quiesce"),
        ),
        context=object(),
        state=InjectionState.READY,
    )]

    def start_runner():
        events.append("start_workload")
        orchestrator.case_run.workload_runners.append(runner)

    monkeypatch.setattr(orchestrator_module.time, "sleep", lambda seconds: events.append(("sleep", seconds)))
    orchestrator._start_workload_runner = start_runner
    orchestrator._install_faults = lambda: events.append("install_faults")
    orchestrator._prepare_observability = lambda: events.append("prepare_observability")
    orchestrator._sleep_until_ms = lambda deadline: events.append(("sleep_until", deadline))

    orchestrator._setup_frozen_history_case()

    assert runner.stopped is False
    assert orchestrator.case_run.workload_runners == [runner]
    assert orchestrator.env._workload_runner is runner
    assert "stop_runner" not in events
    assert "begin_observation_window" in events
    assert orchestrator.case_run.metric_history["agent_handoff"]["diagnostic_workload"] == "retained_after_target_capture"
