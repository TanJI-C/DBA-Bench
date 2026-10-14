"""Shared in-memory fakes for Persistent Scenario core tests. No real DB."""

from __future__ import annotations

import threading
from types import SimpleNamespace

from src.persistent_scenarios.backend.contracts import (
    CapabilityDeclaration,
    EventActivationContext,
    EventActivationResult,
    EventAlertPayload,
    OwnershipMode,
    ResourceOwnership,
)
from src.persistent_scenarios.model.enums import CalibrationStatus, EventTrigger
from src.database.system import DatabaseSystem
from src.persistent_scenarios.model.spec import (
    CalibrationSpec,
    DiagnosisContract,
    EventSpec,
    NodeSpec,
    OltpObjective,
    PersistentScenarioEnvironmentSpec,
    PersistentScenarioResourceSpec,
    PersistentScenarioSpec,
    SafetyPolicyContract,
)
from src.persistent_scenarios.runtime.ledger import TrustedLedger
from src.persistent_scenarios.runtime.lifecycle import (
    ActionClassification,
    EventAttemptEvidence,
    AppliedEvidence,
    EvidenceStatus,
    IntegrityFact,
    IntegrityStatus,
    PreventionEvidence,
    RequiredStateEvidence,
)


def applied_result(handle: str, clock, *, facts: dict | None = None) -> EventActivationResult:
    now = clock.monotonic()
    return EventActivationResult(
        handle=handle,
        attempt=EventAttemptEvidence(attempted_at_monotonic=now, detail={"op": "inject"}),
        applied=AppliedEvidence(observed_at_monotonic=now, facts=facts or {"impact": handle}),
        prevented=None,
    )


def prevented_result(handle: str, clock, *, mechanism: str = "statement_timeout") -> EventActivationResult:
    now = clock.monotonic()
    return EventActivationResult(
        handle=handle,
        attempt=EventAttemptEvidence(attempted_at_monotonic=now, detail={"op": "inject"}),
        applied=None,
        prevented=PreventionEvidence(
            attempted=EventAttemptEvidence(attempted_at_monotonic=now, detail={"op": "inject"}),
            mechanism=mechanism,
            protection_state={"setting": mechanism, "value": "2s"},
            observed_at_monotonic=now,
        ),
    )


def make_event(
    event_id: str,
    *,
    capability_id: str = "demo_capability",
    occurrence: int = 1,
    entity: str = "worker-1",
    start_seconds: int = 2,
    trigger: EventTrigger = EventTrigger.ALERT,
    payload: dict | None = None,
) -> EventSpec:
    return EventSpec(
        event_id=event_id,
        capability_id=capability_id,
        occurrence=occurrence,
        entity=entity,
        payload=payload or {"worker": entity},
        start_seconds=start_seconds,
        activation_timeout_seconds=5,
        response_deadline_seconds=8,
        trigger=trigger,
    )


def make_spec(
    *,
    scenario_id: str = "fake_persistent_scenario",
    citation_tag: str = "PG-PS-01",
    events: tuple[EventSpec, ...] | None = None,
    horizon_seconds: int = 12,
    warmup_seconds: int = 1,
    nodes: int = 1,
) -> PersistentScenarioSpec:
    if events is None:
        events = (
            make_event("event_one", start_seconds=2),
            make_event("event_two", occurrence=2, entity="worker-2", start_seconds=4),
        )
    return PersistentScenarioSpec(
        protocol_version="persistent-scenario-v2",
        scenario_id=scenario_id,
        family_id="fake_family",
        citation_tag=citation_tag,
        system=DatabaseSystem.POSTGRESQL,
        mode="timeline",
        warmup_seconds=warmup_seconds,
        input_stop_seconds=horizon_seconds - 2,
        agent_stop_seconds=horizon_seconds - 1,
        horizon_seconds=horizon_seconds,
        calibration=CalibrationSpec(CalibrationStatus.DEVELOPMENT_PROVISIONAL, "fake-dev"),
        environment=PersistentScenarioEnvironmentSpec(
            workload="fake_profile",
            scale=1,
            base_image="fake:image",
            nodes=tuple(
                NodeSpec(
                    node_id="primary" if index == 0 else f"node-{index}",
                    role="primary" if index == 0 else "standby",
                    resources=PersistentScenarioResourceSpec(1, 128, 1.0, 128),
                )
                for index in range(nodes)
            ),
        ),
        services=(
            OltpObjective(
                "oltp_good_fraction",
                service_id="orders",
                deadline_seconds=8.0,
                min_success_fraction=0.9,
            ),
        ),
        safety_policy=SafetyPolicyContract(
            allowed_action_classes=("read_only", "terminate_single_backend", "alter_guc"),
        ),
        integrity_checks=(),
        required_state=(),
        diagnosis_contract=DiagnosisContract(incidents=()),
        events=events,
        inspection_interval_seconds=3,
    )


class FakeEnvironment:
    def __init__(self):
        self.operations: list[tuple] = []
        self.sql_timeouts: tuple[str, str] | None = None

    def get_tool_schemas(self):
        return ()

    def set_agent_sql_timeouts(self, statement_timeout: str, lock_timeout: str) -> None:
        self.sql_timeouts = (statement_timeout, lock_timeout)
        self.operations.append(("set_sql_timeouts", statement_timeout, lock_timeout))

    def reset_agent_sql_timeouts(self) -> None:
        self.sql_timeouts = None
        self.operations.append(("reset_sql_timeouts", None, None))

    def execute_action(self, api: str, args: dict):
        self.operations.append(("agent_action", api))
        return {"status": "success", "api": api}


class FakeEnvironmentProvider:
    def host_ports(self, spec):
        from src.execution.specs import HostPortLayout
        return HostPortLayout(offsets=tuple(range(len(spec.environment.nodes))))

    def __init__(self, environment: FakeEnvironment | None = None):
        self.environment = environment or FakeEnvironment()
        self.teardowns = 0

    def create(self, spec, run_id, port, *, time_scale=1.0):
        return self.environment

    def deploy(self, environment):
        self.environment.operations.append(("deploy", None))

    def teardown(self, environment):
        self.teardowns += 1
        self.environment.operations.append(("environment_teardown", None))


class FakeCapability:
    """Scripted capability: per event_id activation behavior.

    ``behaviors`` maps event_id -> EventActivationResult | BaseException.
    Missing keys produce a default applied result.
    """

    def __init__(self, capability_id: str, *, behaviors: dict | None = None, exclusive: bool = False):
        self.capability_id = capability_id
        self.behaviors = behaviors or {}
        self.exclusive = exclusive
        self.contexts: dict[str, EventActivationContext] = {}
        self.alert_calls: list[str] = []
        cleanup_owner = self

        class _CleanupTarget:
            def __init__(self, handle):
                self.handle = handle

        self._cleanup_target = _CleanupTarget
        self.cleanup_calls: list[object] = []
        self._cleanups = cleanup_owner

    def declaration(self, event: EventSpec) -> CapabilityDeclaration:
        mode = OwnershipMode.EXCLUSIVE if self.exclusive else OwnershipMode.SHARED
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(ResourceOwnership(f"row:{event.entity}", "row", mode),),
            max_activation_seconds=4,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        event_id = context.event.event_id
        self.contexts[event_id] = context
        behavior = self.behaviors.get(event_id)
        if isinstance(behavior, BaseException):
            raise behavior
        if behavior is not None:
            return behavior
        return applied_result(f"handle-{event_id}", context.clock)

    def alert(self, context: EventActivationContext, handle: object) -> EventAlertPayload:
        self.alert_calls.append(handle)
        return EventAlertPayload(
            title=f"opaque alert for {context.event.entity}",
            symptoms=("database symptom",),
            severity="warning",
            category="database",
        )

    def cleanup(self, handle: object) -> None:
        self.cleanup_calls.append(handle)

    def assert_clean(self, handle: object) -> dict:
        # Live semantics: the injected impact exists until this capability's
        # cleanup reclaimed it. Prefix gates read this during the run.
        return {"clean": handle in self.cleanup_calls, "handle": str(handle)}


class FakeEventProvider:
    """Registry + handle services backed by FakeCapability instances."""

    def __init__(self, capabilities: list[FakeCapability]):
        self.capabilities = {capability.capability_id: capability for capability in capabilities}

    def capability(self, capability_id: str):
        if capability_id not in self.capabilities:
            raise KeyError(f"unknown capability_id={capability_id!r}")
        return self.capabilities[capability_id]

    def agent_alert(self, handle: str) -> EventAlertPayload:
        # Engine registered the alert context on the capability during activate.
        for capability in self.capabilities.values():
            if handle in {f"handle-{event_id}" for event_id in capability.contexts}:
                event_id = handle.removeprefix("handle-")
                return capability.alert(capability.contexts[event_id], handle)
        raise KeyError(f"no capability owns handle={handle!r}")

    def cleanup(self, handle: object) -> None:
        for capability in self.capabilities.values():
            if handle in {f"handle-{event_id}" for event_id in capability.contexts} or handle in capability.cleanup_calls:
                capability.cleanup(handle)
                return
        raise KeyError(f"no capability owns handle={handle!r}")

    def assert_clean(self, handle: object) -> dict:
        for capability in self.capabilities.values():
            if handle in {f"handle-{event_id}" for event_id in capability.contexts} or handle in capability.cleanup_calls:
                return capability.assert_clean(handle)
        raise KeyError(f"no capability owns handle={handle!r}")


class FakeWorkloadRuntime:
    def __init__(self, spec, clock, persistent_scenario_started, *, ledgers: dict | None = None):
        self.spec = spec
        self.clock = clock
        self._origin = persistent_scenario_started
        self.stopped_new_requests = False
        self.stopped = False
        self.drained = False
        self._ledgers = ledgers or {}

    def start(self):
        pass

    def wait_for_warmup(self) -> float:
        if not self.clock.wait_until(self._origin + self.spec.warmup_seconds, threading.Event()):
            raise RuntimeError("fake workload stopped during warmup")
        return self.clock.monotonic()

    def stop_new_requests(self):
        self.stopped_new_requests = True

    def drain(self):
        self.drained = True

    def stop(self):
        self.stopped = True

    def ledgers(self):
        return dict(self._ledgers)

    def baseline_facts(self):
        return {"warmup": "healthy"}


class FakeWorkloadProvider:
    def __init__(self, ledgers: dict | None = None):
        self.runtimes: list[FakeWorkloadRuntime] = []
        self._ledgers = ledgers

    def create_runtime(self, environment, spec, run_id, clock, *, persistent_scenario_started):
        runtime = FakeWorkloadRuntime(spec, clock, persistent_scenario_started, ledgers=self._ledgers)
        self.runtimes.append(runtime)
        return runtime


class FakeTelemetryRuntime:
    def __init__(self, samples):
        self._samples = samples
        self.stopped = False

    def start(self):
        pass

    def stop(self):
        self.stopped = True
        return tuple(self._samples)


class FakeTelemetryProvider:
    def __init__(self, samples=()):
        self.samples = list(samples)

    def create_runtime(self, environment, spec, run_id, clock, *, persistent_scenario_started):
        return FakeTelemetryRuntime(self.samples)


class FakeSafetyProvider:
    def __init__(self):
        self.calls: list[str] = []

    def capture_baseline(self, environment, spec):
        return {"baseline": True}

    def evaluate(self, environment, baseline, action_history, checkpoint):
        self.calls.append(checkpoint)
        return {"safe": True, "checkpoint": checkpoint}


class FakeActionClassifier:
    """Semantically classes agent actions; the real one lives in integration."""

    def __init__(self):
        self.calls: list[tuple] = []

    def __call__(self, api: str, args, result) -> ActionClassification:
        self.calls.append((api, dict(args)))
        if api == "execute_sql":
            sql = str(args.get("sql_query", ""))
            if sql.strip().lower().startswith("select"):
                return ActionClassification(
                    action_class="read_only",
                    details={"sql_digest": f"sha:{abs(hash(sql)) % 10**8:08d}"},
                )
            return ActionClassification(action_class="mutating_dml", objects=("public.orders",))
        return ActionClassification(action_class="other_tool")


class FakeStateFactProvider:
    """Final trusted sampling; the real one executes instance verifiers."""

    def __init__(self, *, integrity=None, required_state=None):
        self.integrity = tuple(integrity or ())
        self.required_state = tuple(required_state or ())
        self.calls = 0

    def capture_integrity_facts(self, environment, spec, *, scoring_start_epoch=None):
        self.calls += 1
        return self.integrity

    def capture_required_state_evidence(self, environment, spec, *, scoring_start_epoch=None):
        self.calls += 1
        return self.required_state


def make_integrity_fact(check_id="ledger_conservation") -> IntegrityFact:
    return IntegrityFact(
        check_id=check_id,
        kind="ledger_conservation",
        status=IntegrityStatus.PASSED,
        details={"delta": 0},
    )


def make_required_state_evidence(check_id="durable_commit") -> RequiredStateEvidence:
    return RequiredStateEvidence(
        check_id=check_id,
        status=EvidenceStatus.CAPTURED,
        facts={"value": "on", "pending_restart": False, "fresh_connection": True},
        captured_at_monotonic=1.0,
    )


class FakeEvaluationProvider:
    def __init__(self, result: dict | None = None):
        self.result = result or {
            "valid": True,
            "DiagnosisPass": None,
            "OutcomePass": True,
            "SafePass": True,
        }
        self.evaluated_runs: list = []
        self.invalid_calls: list = []

    def evaluate(self, persistent_scenario_run):
        self.evaluated_runs.append(persistent_scenario_run)
        return dict(self.result)

    def evaluate_baseline(self, persistent_scenario_run, safety):
        self.evaluated_runs.append(persistent_scenario_run)
        return dict(self.result)

    def invalid_run(self, persistent_scenario_run, classification, reason):
        self.invalid_calls.append((classification, reason))
        return {
            "valid": False,
            "DiagnosisPass": None,
            "OutcomePass": None,
            "SafePass": None,
            "failure": reason,
        }


class FakeBackend:
    def __init__(self, *, capabilities: list[FakeCapability] | None = None, ledgers: dict | None = None,
                 state_facts: FakeStateFactProvider | None = None):
        self.system = DatabaseSystem.POSTGRESQL
        self.operations: list[tuple] = []
        self.environment = FakeEnvironmentProvider()
        self.events = FakeEventProvider(capabilities or [FakeCapability("demo_capability")])
        self.workload = FakeWorkloadProvider(ledgers=ledgers)
        self.telemetry = FakeTelemetryProvider(samples=[{"cpu": 0.1}])
        self.safety = FakeSafetyProvider()
        self.action_classifier = FakeActionClassifier()
        self.state_facts = state_facts or FakeStateFactProvider()

    def validate_spec(self, spec):
        self.operations.append(("validate_spec", spec.scenario_id))


def make_service_ledger(tmp_path, service_id: str = "orders") -> TrustedLedger:
    return TrustedLedger(service_id, tmp_path / f"{service_id}.jsonl")


class ScriptedAgent:
    """Deterministic mailbox agent: read -> (optional action) -> write -> wait."""

    def __init__(
        self,
        *,
        task_ids: list[str] | None = None,
        fail: Exception | None = None,
        execute_first: bool = False,
    ):
        self.task_ids = task_ids
        self.fail = fail
        self.execute_first = execute_first
        self.context = None
        self.reads = 0

    def start(self, context):
        self.context = context

    def run_until_stop(self):
        gateway = self.context.gateway
        while not self.context.stop_signal.is_set():
            status = gateway.mailbox("read")
            self.reads += 1
            if self.execute_first:
                gateway.execute("execute_sql", {"sql_query": "SELECT 1;"}, thinking="probe")
                self.execute_first = False
            pending = [item["task_id"] for item in status["pending"]]
            if pending:
                report = {
                    "diagnosis": {"conditions": [{
                        "type": "lock_wait",
                        "factor": "long transaction holding hot row lock",
                        "entity": "orders",
                        "evidence": ["pg_locks wait queue", "aged transaction"],
                    }]},
                    "outcome": {"changes": ["adjusted timeout"], "verification": ["queue drained"]},
                    "summary": "scripted remediation",
                }
                gateway.mailbox("write", task_ids=pending, report=report)
            gateway.mailbox("wait")
        if self.fail is not None:
            raise self.fail
        return {"status": "horizon_reached"}
