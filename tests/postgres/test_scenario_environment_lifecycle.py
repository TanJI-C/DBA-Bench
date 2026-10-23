import ast
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.workloads.specs import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    EMPTY_BACKGROUND_WORKLOAD,
)
from src.scenarios.base import FaultPlan, InjectionState
from src.scenarios.runtime import orchestrator as orchestrator_module
from src.scenarios.faults import (
    BaseFaultInjector,
    FaultLifecycleContext,
)
from src.scenarios import POSTGRES_SCENARIO_REGISTRY
from src.scenarios.postgres.system_failure.fd_exhaustion import PgSystemFailureFdExhaustionInjector
from src.scenarios.postgres.system_failure.lock_contention import PgSystemFailureLockContentionInjector
from src.scenarios.postgres.system_failure.noisy_neighbor import PgSystemFailureNoisyNeighborInjector
from src.scenarios.postgres.system_failure.oom import PgSystemFailureOomInjector
from src.scenarios.postgres.system_failure.page_corruption import PgSystemFailurePageCorruptionInjector
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.visualization import exporter as exporter_module


EVENTS = []
CONTEXTS = []


class FakeEvaluator:
    def __init__(self, env, *, diagnosis_matcher):
        self.env = env

    def capture_safety_baseline(self, case_run):
        return None


class FakeInjector(BaseFaultInjector):
    def install(self, context):
        CONTEXTS.append(context)
        EVENTS.append(("install", context.config["value"]))

    def activate(self, context):
        CONTEXTS.append(context)
        EVENTS.append(("activate", context.config["value"]))

    def prepare_observability(self, context):
        CONTEXTS.append(context)
        EVENTS.append(("observe", context.config["value"]))
        return {"baseline": context.config["value"]}

    def quiesce(self, context):
        CONTEXTS.append(context)
        EVENTS.append("quiesce")

    def recover(self, context):
        CONTEXTS.append(context)
        EVENTS.append("recover")


class InvalidEvidenceInjector(FakeInjector):
    def prepare_observability(self, context):
        return []


class DuplicateEvidenceInjector(FakeInjector):
    def prepare_observability(self, context):
        return {"baseline": 8}

CASE = SimpleNamespace(
    case_id="checkout_case",
    case_no=0,
    evaluator=FakeEvaluator,
    alert="checkout alert",
    base_image_name="aiopsbench-pg-tpcds:latest",
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    postgres_runtime=None,
)


class FakeScenario:
    scenario_id = "pg_checkout_fault"
    description = "checkout fault"

    def build_fault_plan(self, case):
        assert case is CASE
        return (FaultPlan(injector_type=FakeInjector, config={"value": 7}),)


class FakeDeployment:
    image_name = CASE.base_image_name
    container_name = "pg-test"

    def is_container_running(self):
        return True

    def stop_pg(self):
        EVENTS.append("stop_pg")
        return True

    def start_pg(self):
        EVENTS.append("start_pg")
        return True

    def wait_for_ready(self, timeout):
        EVENTS.append(("wait_ready", timeout))
        return True


class FakeEnv:
    def __init__(self):
        self.deployment = FakeDeployment()
        self.baseline_image_name = CASE.base_image_name
        self.snapshots = set()

    def configure_case(self, case):
        assert case is CASE

    def base_snapshot_name(self, case):
        assert case is CASE
        return case.base_image_name

    def snapshot_name(self, scenario_id, case):
        assert scenario_id == FakeScenario.scenario_id
        assert case is CASE
        return "aiopsbench-pg-fault-pg-checkout-fault-checkout-case:tpcds"

    def snapshot_exists(self, snapshot_name):
        return snapshot_name in self.snapshots

    def select_snapshot(self, snapshot_name, base_snapshot_name):
        assert snapshot_name in self.snapshots
        self.deployment.image_name = snapshot_name
        self.baseline_image_name = base_snapshot_name

    def save_snapshot(self, snapshot_name, labels):
        EVENTS.append(("save_snapshot", snapshot_name, labels))
        self.snapshots.add(snapshot_name)

    def deploy(self):
        EVENTS.append(("deploy", self.deployment.image_name))

    def execute_sql(self, sql):
        EVENTS.append(("sql", sql))
        return {"status": "success"}

    def reconnect(self):
        EVENTS.append("reconnect")
        return True

    def refresh_pgss_baseline(self):
        EVENTS.append("refresh_pgss_baseline")

    def teardown(self):
        EVENTS.append("teardown")


@pytest.fixture(autouse=True)
def reset_events():
    EVENTS.clear()
    CONTEXTS.clear()


def build_orchestrator(mode="off", image_name=None):
    return Orchestrator(
        env=FakeEnv(),
        scenario=FakeScenario(),
        case=CASE,
        agent=None,
        pretty_print=False,
        run_config=OrchestratorRunConfig(mode, image_name),
    )


def test_fault_image_identity_includes_case():
    env = FakeEnv()
    assert env.snapshot_name(FakeScenario.scenario_id, CASE) == (
        "aiopsbench-pg-fault-pg-checkout-fault-checkout-case:tpcds"
    )


def test_off_mode_uses_orchestrator_owned_injector():
    orchestrator = build_orchestrator()
    orchestrator.setup()
    orchestrator.teardown()

    assert EVENTS == [
        ("deploy", CASE.base_image_name),
        ("install", 7),
        ("observe", 7),
        "recover",
        "teardown",
    ]
    assert len(orchestrator.case_run.injections) == 1
    assert orchestrator.case_run.injections[0].evidence == {"baseline": 7}
    assert orchestrator.case_run.injections[0].state is InjectionState.RECOVERED
    assert all(context is CONTEXTS[0] for context in CONTEXTS)
    assert CONTEXTS[0] == FaultLifecycleContext(
        run_id=orchestrator.case_run.run_id,
        scenario_id=FakeScenario.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config={"value": 7},
        env=orchestrator.env,
    )


def test_save_mode_quiesces_commits_and_reactivates_same_injector(monkeypatch):
    orchestrator = build_orchestrator("save", "fault:latest")

    orchestrator.setup()

    assert EVENTS[:3] == [
        ("deploy", CASE.base_image_name),
        ("install", 7),
        "quiesce",
    ]
    assert ("activate", 7) in EVENTS
    assert ("observe", 7) in EVENTS
    saved = next(event for event in EVENTS if event[0] == "save_snapshot")
    assert saved[1] == "fault:latest"
    assert saved[2]["aiopsbench.case_id"] == "checkout_case"
    assert orchestrator.run_config.fault_snapshot_mode == "use"


def test_use_mode_deploys_image_then_activates(monkeypatch):
    orchestrator = build_orchestrator("use", "fault:latest")
    orchestrator.env.snapshots.add("fault:latest")

    orchestrator.setup()

    assert EVENTS == [
        ("deploy", "fault:latest"),
        ("activate", 7),
        ("observe", 7),
    ]
    assert orchestrator.env.baseline_image_name == CASE.base_image_name


def test_auto_mode_saves_when_fault_image_is_missing(monkeypatch):
    orchestrator = build_orchestrator("auto", "fault:latest")

    orchestrator.setup()

    assert any(event[0] == "save_snapshot" for event in EVENTS)
    assert orchestrator.run_config.fault_snapshot_mode == "use"


def test_auto_mode_uses_existing_fault_image(monkeypatch):
    orchestrator = build_orchestrator("auto", "fault:latest")
    orchestrator.env.snapshots.add("fault:latest")

    orchestrator.setup()

    assert EVENTS[0] == ("deploy", "fault:latest")
    assert ("activate", 7) in EVENTS


def test_workload_and_warmup_precede_observability(monkeypatch):
    orchestrator = build_orchestrator()
    orchestrator.run_config.runtime_warmup_seconds = 2
    monkeypatch.setattr(
        orchestrator,
        "_start_workload_runner",
        lambda: EVENTS.append("start_workload"),
    )
    monkeypatch.setattr(
        orchestrator_module.time,
        "sleep",
        lambda seconds: EVENTS.append(("warmup", seconds)),
    )

    orchestrator.setup()

    assert EVENTS == [
        ("deploy", CASE.base_image_name),
        ("install", 7),
        "start_workload",
        ("warmup", 2),
        ("observe", 7),
    ]


def test_case_can_start_workload_after_observability(monkeypatch):
    monkeypatch.setattr(
        CASE,
        "background_workload",
        BackgroundWorkloadSpec(
            profiles=(),
            worker_count=0,
            seed=0,
            start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
            warmup_seconds=3,
        ),
    )
    orchestrator = build_orchestrator()
    monkeypatch.setattr(
        orchestrator,
        "_start_workload_runner",
        lambda: EVENTS.append("start_workload"),
    )
    monkeypatch.setattr(
        orchestrator_module.time,
        "sleep",
        lambda seconds: EVENTS.append(("warmup", seconds)),
    )

    orchestrator.setup()

    assert EVENTS == [
        ("deploy", CASE.base_image_name),
        ("install", 7),
        ("observe", 7),
        "start_workload",
        ("warmup", 3),
    ]


def test_case_can_start_workload_before_faults(monkeypatch):
    monkeypatch.setattr(
        CASE,
        "background_workload",
        BackgroundWorkloadSpec(
            profiles=(),
            worker_count=0,
            seed=0,
            start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        ),
    )
    orchestrator = build_orchestrator()
    monkeypatch.setattr(
        orchestrator,
        "_start_workload_runner",
        lambda: EVENTS.append("start_workload"),
    )

    orchestrator.setup()

    assert EVENTS == [
        ("deploy", CASE.base_image_name),
        "start_workload",
        ("install", 7),
        ("observe", 7),
    ]


def test_noisy_neighbor_runtime_pressure_waits_for_case_threshold(monkeypatch):
    injector = PgSystemFailureNoisyNeighborInjector()
    injector.env = SimpleNamespace(
        deployment=SimpleNamespace(container_name="pg-noisy"),
        query_metrics=lambda *_args, **_kwargs: next(metrics),
    )
    injector._hog_pids = [101, 102]
    injector.minimum_external_cpu_percent = 50.0
    injector.startup_timeout_seconds = 3.0
    metrics = iter(
        [
            {
                "status": "success", "metric": "cpu", "kind": "series",
                "series": {"postgres": {"timestamps": ["2026-07-28 10:00:00"], "percent": [62.0]}},
                "current": {"external_cpu_percent": 37.0},
            },
            {
                "status": "success", "metric": "cpu", "kind": "series",
                "series": {"postgres": {"timestamps": ["2026-07-28 10:00:01"], "percent": [74.0]}},
                "current": {"external_cpu_percent": 53.0},
            },
        ]
    )
    monkeypatch.setattr(
        "subprocess.run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )
    monkeypatch.setattr("time.sleep", lambda _seconds: None)

    injector._verify_runtime_pressure()


def test_noisy_neighbor_runtime_pressure_fails_with_compact_context(monkeypatch):
    injector = PgSystemFailureNoisyNeighborInjector()
    injector.env = SimpleNamespace(
        deployment=SimpleNamespace(container_name="pg-noisy"),
        query_metrics=lambda *_args, **_kwargs: {
            "status": "success", "metric": "cpu", "kind": "series",
            "series": {"postgres": {"timestamps": ["2026-07-28 10:00:00"], "percent": [41.0]}},
            "current": {"external_cpu_percent": 23.0},
        },
    )
    injector._hog_pids = [101, 102]
    injector.minimum_external_cpu_percent = 50.0
    injector.startup_timeout_seconds = 0.001
    monkeypatch.setattr(
        "subprocess.run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )
    monkeypatch.setattr("time.sleep", lambda _seconds: None)

    with pytest.raises(
        RuntimeError,
        match=r"latest=41.0, external_cpu=23.0, required_external=50.0",
    ):
        injector._verify_runtime_pressure()


def test_lock_contention_observability_requires_complete_topology():
    injector = PgSystemFailureLockContentionInjector()
    active_connections = json.dumps({
        "idle in transaction": 3,
        "lock_waiting_sessions": 14,
    })
    waiting_locks = json.dumps({
        "result": [[
            "checkout_api_tx_17",
            "checkout_api_wait_01",
            "nightly_reporting_wait_01",
            "profile_read_wait_01",
        ]]
    })
    noise_context = json.dumps({
        "result": [[
            "checkout_api_pool_01",
            "profile_read_api_01",
            "nightly_reporting_snapshot",
            "profile_read_tx_legacy",
            "nightly_reporting_wait_01",
            "profile_read_wait_01",
            "dashboard_profile_rollup",
        ]]
    })

    injector._assert_lock_topology(active_connections, waiting_locks, noise_context)

    with pytest.raises(RuntimeError, match="profile_read_wait_01"):
        injector._assert_lock_topology(
            active_connections,
            waiting_locks.replace("profile_read_wait_01", "missing_decoy"),
            noise_context,
        )


def test_lock_contention_counts_only_background_report_noise():
    injector = PgSystemFailureLockContentionInjector()
    slow_queries = {
        "status": "success",
        "metric": "slow_queries",
        "kind": "records",
        "records": [
            {"query": "SELECT FROM store_sales ss JOIN date_dim d ON true"},
            {"query": "UPDATE customer SET c_salutation = 'Mr.'"},
        ],
    }

    assert injector._background_slow_query_count(slow_queries) == 1


def test_oom_injector_requires_cgroup_oom_kill_increment(monkeypatch):
    injector = PgSystemFailureOomInjector()
    injector.container_name = "pg-oom"
    injector.oom_kill_before = 4
    responses = iter(
        [
            SimpleNamespace(
                returncode=0,
                stdout="low 0\nhigh 0\nmax 8\noom 5\noom_kill 5\n",
                stderr="",
            ),
            SimpleNamespace(returncode=0, stdout="", stderr=""),
            SimpleNamespace(
                returncode=0,
                stdout="low 0\nhigh 0\nmax 8\noom 5\noom_kill 4\n",
                stderr="",
            ),
        ]
    )
    monkeypatch.setattr("subprocess.run", lambda *_args, **_kwargs: next(responses))

    injector._record_oom_kill()
    assert injector.oom_kill_delta == 1

    injector.oom_kill_before = 4
    with pytest.raises(RuntimeError, match="without a cgroup OOM kill"):
        injector._record_oom_kill()


def test_setup_cannot_run_twice():
    orchestrator = build_orchestrator()
    orchestrator.setup()
    assert orchestrator.phase_timings["container_start_seconds"] >= 0
    with pytest.raises(RuntimeError, match="single-use"):
        orchestrator.setup()


def test_orchestrator_cannot_be_reused_after_teardown():
    orchestrator = build_orchestrator()
    orchestrator.setup()
    orchestrator.teardown()

    with pytest.raises(RuntimeError, match="single-use"):
        orchestrator.setup()


def test_run_reports_trace_failure_without_skipping_teardown(monkeypatch):
    orchestrator = build_orchestrator()

    def fail_setup():
        raise RuntimeError("run boom")

    def fail_trace(*args, **kwargs):
        raise RuntimeError("trace boom")

    orchestrator.setup = fail_setup
    orchestrator.teardown = lambda: EVENTS.append("teardown")
    monkeypatch.setattr(exporter_module, "export_run_trace", fail_trace)

    with pytest.raises(RuntimeError, match="Scenario finalization failed") as exc_info:
        orchestrator.run()

    assert "run boom" in str(exc_info.value)
    assert "trace boom" in str(exc_info.value)
    assert EVENTS == ["teardown"]


def test_run_exports_trace_after_teardown_observes_workload(monkeypatch):
    orchestrator = build_orchestrator()
    orchestrator.setup = lambda: orchestrator.phase_timings.update(
        {"container_start_seconds": 0.0}
    )
    orchestrator.agent = SimpleNamespace(
        solve=lambda: {},
        init_env_gateway=lambda _gateway: None,
        model_usage_history=[],
    )
    orchestrator._run_evaluation = lambda _submission: None

    def teardown():
        orchestrator.case_run.background_workload_observed = {
            "profiles": {"qp03_target": {"attempts": 3}}
        }
        EVENTS.append("teardown")

    def export(_orchestrator, output_dir):
        EVENTS.append(("export", _orchestrator.case_run.background_workload_observed))
        return output_dir

    orchestrator.teardown = teardown
    monkeypatch.setattr(exporter_module, "export_run_trace", export)

    orchestrator.run()

    assert set(orchestrator.phase_timings) == {
        "container_start_seconds",
        "preparation_seconds",
        "agent_interaction_seconds",
        "evaluation_seconds",
        "cleanup_seconds",
        "total_seconds",
    }

    assert EVENTS == [
        "teardown",
        ("export", {"profiles": {"qp03_target": {"attempts": 3}}}),
    ]


def test_teardown_captures_runner_attached_by_trusted_replay():
    class ReplayRunner:
        def stop(self):
            EVENTS.append("stop_replay")

        def get_observed(self):
            return {"profiles": {"replay": {"attempts": 5}}}

    orchestrator = build_orchestrator()
    orchestrator.setup()
    runner = ReplayRunner()
    orchestrator.env._workload_runner = runner

    orchestrator.teardown()

    assert orchestrator.case_run.background_workload_observed == {
        "profiles": {"replay": {"attempts": 5}}
    }
    assert orchestrator.env._workload_runner is None
    assert EVENTS.index("stop_replay") < EVENTS.index("recover")


def test_teardown_recovers_only_injectors_that_entered_the_lifecycle():
    class FailingInjector(FakeInjector):
        def install(self, context):
            EVENTS.append(("failing_install", context.config["value"]))
            raise RuntimeError("injection failed")

        def recover(self, context):
            EVENTS.append("recover_failing")

    class NeverStartedInjector(FakeInjector):
        def recover(self, context):
            EVENTS.append("recover_never_started")

    class Scenario(FakeScenario):
        def build_fault_plan(self, case):
            return (
                FaultPlan(injector_type=FakeInjector, config={"value": 1}),
                FaultPlan(injector_type=FailingInjector, config={"value": 2}),
                FaultPlan(injector_type=NeverStartedInjector, config={"value": 3}),
            )

    orchestrator = build_orchestrator()
    orchestrator.scenario = Scenario()

    with pytest.raises(RuntimeError, match="injection failed"):
        orchestrator.setup()
    orchestrator.teardown()

    assert EVENTS == [
        ("deploy", CASE.base_image_name),
        ("install", 1),
        ("failing_install", 2),
        "recover_failing",
        "recover",
        "teardown",
    ]
    assert [record.state for record in orchestrator.case_run.injections] == [
        InjectionState.RECOVERED,
        InjectionState.RECOVERED,
        InjectionState.PLANNED,
    ]


def test_observability_must_return_mapping():
    class Scenario(FakeScenario):
        def build_fault_plan(self, case):
            return (FaultPlan(injector_type=InvalidEvidenceInjector, config={"value": 7}),)

    orchestrator = build_orchestrator()
    orchestrator.scenario = Scenario()
    with pytest.raises(TypeError, match="must return a Mapping"):
        orchestrator.setup()


def test_observability_rejects_duplicate_evidence_keys():
    class Scenario(FakeScenario):
        def build_fault_plan(self, case):
            return (
                FaultPlan(injector_type=FakeInjector, config={"value": 7}),
                FaultPlan(injector_type=DuplicateEvidenceInjector, config={"value": 8}),
            )

    orchestrator = build_orchestrator()
    orchestrator.scenario = Scenario()
    with pytest.raises(ValueError, match="Duplicate injection evidence key 'baseline'"):
        orchestrator.setup()


def test_fd_exhaustion_probe_preserves_expected_sql_error():
    injector = PgSystemFailureFdExhaustionInjector()
    injector.validation_sql = "SELECT * FROM relation_fanout;"
    injector.failure_probe_timeout_seconds = 8
    executed_sql = []
    injector.env = SimpleNamespace(
        execute_sql=lambda sql: (
            executed_sql.append(sql)
            or json.dumps({
                "status": "error",
                "error": "parallel worker failed: Too many open files",
            })
        )
    )

    assert injector._run_failure_probe() == (
        "parallel worker failed: Too many open files"
    )
    assert executed_sql == [
        "SET statement_timeout = '8s'; SELECT * FROM relation_fanout;"
    ]


def test_fd_exhaustion_recovery_starts_postgres_when_restart_cannot():
    injector = PgSystemFailureFdExhaustionInjector()
    injector.safe_nofile_limit = 4096
    actions = []
    injector.env = SimpleNamespace(
        manage_instance=lambda action, target=None, value=None: (
            actions.append((action, target, value))
            or json.dumps({
                "status": (
                    "error" if action == "restart" else "success"
                )
            })
        ),
        reconnect=lambda: actions.append(("reconnect", None, None)),
    )

    injector._restore_safe_limit()

    assert actions == [
        ("set_config", "nofile", "4096"),
        ("restart", "postgres", None),
        ("start", "postgres", None),
        ("reconnect", None, None),
    ]


def test_page_corruption_probe_requires_expected_database_error():
    injector = PgSystemFailurePageCorruptionInjector()
    injector.env = SimpleNamespace(
        execute_sql=lambda sql: json.dumps({
            "status": "error",
            "error": "invalid page in block 1 of relation base/16384/16416",
        }),
        read_log=lambda log_type, lines: "invalid page in block 1",
    )

    injector._verify_runtime_fault()

    assert "invalid page" in injector.fault_query_result
    assert injector.log_excerpt == "invalid page in block 1"


def test_formal_pg_entries_use_only_orchestrator_run_path():
    paths = sorted(Path("examples").glob("run_pg_*_scenario.py"))
    assert len(paths) == sum(
        registration.entrypoint is not None
        for registration in POSTGRES_SCENARIO_REGISTRY
    )
    for path in paths:
        source = path.read_text()
        tree = ast.parse(source, filename=str(path))
        assert "PGFaultSnapshotManager" not in source
        assert ".run_snapshot(" not in source
        assert "--fault-snapshot-mode" in source
        assert any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "run"
            for node in ast.walk(tree)
        ), path

        env_builders = {
            node.name: node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name in {"build_env", "_build_env"}
        }
        for builder in env_builders.values():
            assert "case" in {arg.arg for arg in builder.args.args}, path
            assert "case.base_image_name" in ast.unparse(builder), path
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in env_builders
            ):
                continue
            passes_case = (
                bool(node.args)
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id == "case"
            ) or any(keyword.arg == "case" for keyword in node.keywords)
            assert passes_case, f"{path}:{node.lineno} must pass case to {node.func.id}()"
