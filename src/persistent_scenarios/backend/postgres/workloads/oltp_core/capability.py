"""Capability protocol for the pg5 OLTP instances.

`PersistentScenarioEventCapability` = declaration(event) -> CapabilityDeclaration,
activate(ctx) -> EventActivationResult(attempt + applied|prevented),
alert(ctx, handle) -> EventAlertPayload, cleanup(handle), assert_clean(handle).
Registration goes through `EventCapabilityRegistry.capability(capability_id)`
(owned by integration); these types mirror the frozen core shapes so the
adaptation stays mechanical.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol, runtime_checkable

from .ports import Clock, ConnectionSource, EvidenceLedgerFile


@dataclass(frozen=True, slots=True)
class EventOccurrence:
    event_id: str
    capability_id: str
    occurrence_index: int
    entity: str
    params: Mapping[str, object]

    def require_str(self, key: str) -> str:
        value = self.params.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Occurrence payload requires a non-empty string param: "
                f"event_id={self.event_id!r}, capability_id={self.capability_id!r}, param={key!r}"
            )
        return value

    def require_number(self, key: str) -> float:
        value = self.params.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(
                f"Occurrence payload requires a numeric param: "
                f"event_id={self.event_id!r}, capability_id={self.capability_id!r}, param={key!r}, value={value!r}"
            )
        return float(value)

    def reject_unknown_params(self, known: frozenset[str]) -> None:
        unknown = set(self.params) - known
        if unknown:
            raise ValueError(
                f"Occurrence payload has unknown params: event_id={self.event_id!r}, "
                f"capability_id={self.capability_id!r}, unknown={sorted(unknown)!r}"
            )


@dataclass(frozen=True, slots=True)
class ResourceOwnership:
    """One owned resource; `resource_key` carries the entity/occurrence template
    so repeated occurrences on different entities never conflict."""

    resource_key: str
    resource_kind: str
    mode: str = "exclusive"


@dataclass(frozen=True, slots=True)
class CapabilityDeclaration:
    ownership: tuple[ResourceOwnership, ...]
    max_activation_seconds: float


@dataclass(frozen=True, slots=True)
class EventActivationResult:
    """`attempt` carries the injection/execution evidence; the outcome is
    applied (fault/live business input present) or prevented (protection or a
    lawful earlier resolution terminated it). Prevented attempts carry the
    dual prevention evidence: `mechanism` (which protection fired) and
    `protection_state` (the effective protection values at termination).
    `handle` is the capability's internal handle for cleanup/assert_clean.
    Technical failures raise."""

    attempt: Mapping[str, object]
    outcome: str
    handle: object = None

    def __post_init__(self) -> None:
        if self.outcome not in {"applied", "prevented"}:
            raise ValueError(
                f"EventActivationResult outcome must be applied or prevented: "
                f"outcome={self.outcome!r}, attempt={dict(self.attempt)!r}"
            )
        if self.outcome == "prevented":
            missing = {"mechanism", "protection_state"} - set(self.attempt)
            if missing:
                raise ValueError(
                    f"Prevented activation requires dual prevention evidence: "
                    f"event_id={self.attempt.get('event_id')!r}, missing={sorted(missing)!r}"
                )


@dataclass(frozen=True, slots=True)
class CapabilityContext:
    run_id: str
    occurrence: EventOccurrence
    clock: Clock
    source: ConnectionSource
    admin_source: ConnectionSource
    evidence: EvidenceLedgerFile
    driver: object | None = None


@runtime_checkable
class EventCapability(Protocol):
    """Module-local mirror of the frozen core capability protocol."""

    capability_id: str

    def declaration(self, occurrence: EventOccurrence) -> CapabilityDeclaration: ...

    def activate(self, context: CapabilityContext) -> EventActivationResult: ...

    def alert(self, context: CapabilityContext, handle: object) -> Mapping[str, object]: ...

    def cleanup(self, handle: object) -> None: ...

    def assert_clean(self, handle: object) -> Mapping[str, object]: ...


class CapabilityRegistry:
    """Module-local registration entry; integration replaces this with the
    core `EventCapabilityRegistry` and the same capability_id keys."""

    def __init__(self, capabilities: tuple) -> None:
        self._capabilities: dict[str, object] = {}
        for capability in capabilities:
            if capability.capability_id in self._capabilities:
                raise ValueError(
                    f"Capability registered twice: capability_id={capability.capability_id!r}"
                )
            self._capabilities[capability.capability_id] = capability

    def capability(self, capability_id: str) -> object:
        capability = self._capabilities.get(capability_id)
        if capability is None:
            raise ValueError(
                f"Unknown capability: capability_id={capability_id!r}, known={sorted(self._capabilities)!r}"
            )
        return capability

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._capabilities))


def require_driver(context: CapabilityContext, capability_id: str):
    if context.driver is None:
        raise ValueError(
            f"Capability requires the workload driver in its activation context: "
            f"capability_id={capability_id!r}, event_id={context.occurrence.event_id!r}"
        )
    return context.driver


class PromoTierCapability:
    """Switches the driver traffic tier; a versioned business event, never a fault."""

    capability_id = "promo_tier"
    _PARAMS = frozenset({"tier"})

    def declaration(self, occurrence: EventOccurrence) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            ownership=(ResourceOwnership(
                resource_key=f"driver:traffic-tier:{occurrence.entity}",
                resource_kind="workload_plan",
            ),),
            max_activation_seconds=10.0,
        )

    def activate(self, context: CapabilityContext) -> EventActivationResult:
        context.occurrence.reject_unknown_params(self._PARAMS)
        tier = context.occurrence.require_str("tier")
        driver = require_driver(context, self.capability_id)
        driver.apply_tier(tier)
        handle = {"tier": tier, "applied_at": context.clock.monotonic()}
        return EventActivationResult(attempt=dict(handle), outcome="applied", handle=handle)

    def alert(self, context: CapabilityContext, handle: object) -> Mapping[str, object]:
        return {
            "title": "业务流量档位切换",
            "symptoms": [f"流量进入 {handle['tier']} 档位，交易与池水位同步上升"],
            "severity": "info",
            "category": "planned_traffic_change",
        }

    def cleanup(self, handle: object) -> None:
        return None

    def assert_clean(self, handle: object) -> Mapping[str, object]:
        return {"capability_id": self.capability_id, "clean": True}
