"""Provider bundle contract for the shared Persistent Scenario engine."""

from __future__ import annotations

from dataclasses import dataclass

from src.persistent_scenarios.model.enums import DatabaseSystem
from src.persistent_scenarios.backend.contracts import (
    EnvironmentProvider,
    EventCapabilityRegistry,
    SafetyProvider,
    TelemetryProvider,
    WorkloadProvider,
)


@dataclass(frozen=True, slots=True)
class PersistentScenarioProviderBundle:
    system: DatabaseSystem
    environment: EnvironmentProvider
    events: EventCapabilityRegistry
    workload: WorkloadProvider
    telemetry: TelemetryProvider
    safety: SafetyProvider
