"""Contracts implemented by Persistent Scenario database backends.

Provider methods return structured facts (never natural language for the
core to guess). Prevention must be returned as evidence, never synthesized
from unknown exceptions: a capability that cannot complete its job raises.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol, Sequence, runtime_checkable

from src.execution.specs import HostPortLayout
from src.database.system import DatabaseSystem
from src.persistent_scenarios.model.spec import PersistentScenarioSpec, EventSpec
from src.persistent_scenarios.runtime.ledger import TrustedLedger
from src.persistent_scenarios.runtime.lifecycle import (
    ActionClassification,
    AppliedEvidence,
    EventAttemptEvidence,
    IntegrityFact,
    PreventionEvidence,
    RequiredStateEvidence,
)


class OwnershipMode(str, Enum):
    EXCLUSIVE = "exclusive"
    SHARED = "shared"


@dataclass(frozen=True, slots=True)
class ResourceOwnership:
    """A named resource a capability owns during its bounded activation."""

    resource_key: str
    resource_kind: str
    mode: OwnershipMode

    def __post_init__(self) -> None:
        for name, value in (("resource_key", self.resource_key), ("resource_kind", self.resource_kind)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Resource ownership {name} must be non-empty: value={value!r}")
        if not isinstance(self.mode, OwnershipMode):
            raise TypeError(f"Resource ownership mode must be OwnershipMode: value={self.mode!r}")


@dataclass(frozen=True, slots=True)
class CapabilityDeclaration:
    capability_id: str
    resources: tuple[ResourceOwnership, ...]
    max_activation_seconds: int

    def __post_init__(self) -> None:
        if not isinstance(self.capability_id, str) or not self.capability_id.strip():
            raise ValueError(f"Capability declaration identity must be non-empty: value={self.capability_id!r}")
        if not self.resources:
            raise ValueError(f"Capability must declare resources: capability_id={self.capability_id!r}")
        if isinstance(self.max_activation_seconds, bool) or not isinstance(self.max_activation_seconds, int) or self.max_activation_seconds <= 0:
            raise ValueError(
                f"Capability max_activation_seconds must be a positive integer: "
                f"capability_id={self.capability_id!r}, value={self.max_activation_seconds!r}"
            )


@dataclass(frozen=True, slots=True)
class EventActivationContext:
    run_id: str
    spec: PersistentScenarioSpec
    event: EventSpec
    environment: object
    clock: object


@dataclass(frozen=True, slots=True)
class EventActivationResult:
    """Arrival facts plus the provider handle that owns the activation.

    Exactly one of applied/prevented must carry evidence. Infrastructure and
    environment failures are raised, never returned.
    """

    handle: object
    attempt: EventAttemptEvidence
    applied: AppliedEvidence | None
    prevented: PreventionEvidence | None

    def __post_init__(self) -> None:
        if (self.applied is None) == (self.prevented is None):
            raise ValueError(
                "Event activation result requires exactly one of applied or prevented evidence: "
                f"applied={self.applied!r}, prevented={self.prevented!r}"
            )


@dataclass(frozen=True, slots=True)
class EventAlertPayload:
    """Production-plausible symptoms. No root cause, blocker identity or fix SQL."""

    title: str
    symptoms: tuple[str, ...]
    severity: str
    category: str

    def __post_init__(self) -> None:
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError(f"Event alert title must be non-empty: value={self.title!r}")
        if not self.symptoms or any(not isinstance(symptom, str) or not symptom.strip() for symptom in self.symptoms):
            raise ValueError(f"Event alert symptoms must be non-empty strings: value={self.symptoms!r}")
        if not isinstance(self.severity, str) or not self.severity.strip():
            raise ValueError(f"Event alert severity must be non-empty: value={self.severity!r}")
        if not isinstance(self.category, str) or not self.category.strip():
            raise ValueError(f"Event alert category must be non-empty: value={self.category!r}")


@runtime_checkable
class PersistentScenarioEventCapability(Protocol):
    """The complete capability surface used by the core runtime."""

    capability_id: str

    def declaration(self, event: EventSpec) -> CapabilityDeclaration: ...

    def activate(self, context: EventActivationContext) -> EventActivationResult: ...

    def alert(self, context: EventActivationContext, handle: object) -> EventAlertPayload: ...

    def cleanup(self, handle: object) -> None: ...

    def assert_clean(self, handle: object) -> Mapping[str, object]: ...


@runtime_checkable
class EventCapabilityRegistry(Protocol):
    """Registration entry; assembly is owned by the integration package."""

    def capability(self, capability_id: str) -> PersistentScenarioEventCapability: ...


@runtime_checkable
class EnvironmentProvider(Protocol):
    def host_ports(self, spec: PersistentScenarioSpec) -> HostPortLayout: ...

    def create(self, spec: PersistentScenarioSpec, run_id: str, port: int) -> object: ...

    def deploy(self, environment: object) -> None: ...

    def teardown(self, environment: object) -> None: ...


@runtime_checkable
class PersistentWorkloadRuntime(Protocol):
    def start(self) -> None: ...

    def wait_for_warmup(self) -> float: ...

    def stop_new_requests(self) -> None: ...

    def drain(self) -> None: ...

    def stop(self) -> None: ...

    def ledgers(self) -> Mapping[str, TrustedLedger]: ...

    def baseline_facts(self) -> Mapping[str, object]: ...


@runtime_checkable
class WorkloadProvider(Protocol):
    def create_runtime(
        self,
        environment: object,
        spec: PersistentScenarioSpec,
        run_id: str,
        clock: object,
        *,
        persistent_scenario_started: float,
    ) -> PersistentWorkloadRuntime: ...


@runtime_checkable
class TelemetryProvider(Protocol):
    def create_runtime(
        self,
        environment: object,
        spec: PersistentScenarioSpec,
        run_id: str,
        clock: object,
        *,
        persistent_scenario_started: float,
    ) -> object: ...


@runtime_checkable
class SafetyProvider(Protocol):
    def capture_baseline(self, environment: object, spec: PersistentScenarioSpec) -> object: ...

    def evaluate(
        self,
        environment: object,
        baseline: object,
        action_history: Sequence[Mapping[str, object]],
        checkpoint: str,
    ) -> Mapping[str, object]: ...


@runtime_checkable
class EventProvider(Protocol):
    """Backend-side registry and handle services for the engine."""

    def capability(self, capability_id: str) -> PersistentScenarioEventCapability: ...

    def agent_alert(self, handle: object) -> EventAlertPayload: ...

    def cleanup(self, handle: object) -> None: ...

    def assert_clean(self, handle: object) -> Mapping[str, object]: ...


@runtime_checkable
class StateFactProvider(Protocol):
    """Final-horizon trusted sampling port.

    Implementations belong to the backend/integration side: they execute the
    instance-registered integrity and required-state verifiers and return
    typed facts. Core stores them on the run; evaluation only consumes.
    """

    def capture_integrity_facts(self, environment: object, spec: PersistentScenarioSpec) -> tuple[IntegrityFact, ...]: ...

    def capture_required_state_evidence(self, environment: object, spec: PersistentScenarioSpec) -> tuple[RequiredStateEvidence, ...]: ...


class ActionClassifier(Protocol):
    """Semantic classifier for agent environment actions.

    Implemented by integration (PG SQL -> action_class); core owns the
    ``ActionClassification`` return type and stamps identity/time into the
    stored ``ActionFact``.
    """

    def __call__(self, api: str, args: Mapping[str, object], result: object) -> ActionClassification: ...


@runtime_checkable
class PersistentScenarioBackend(Protocol):
    system: DatabaseSystem
    environment: EnvironmentProvider
    events: EventCapabilityRegistry
    workload: WorkloadProvider
    telemetry: TelemetryProvider
    safety: SafetyProvider
    state_facts: StateFactProvider
    action_classifier: ActionClassifier

    def validate_spec(self, spec: PersistentScenarioSpec) -> None: ...
