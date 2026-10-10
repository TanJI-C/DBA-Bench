"""Core-protocol capability base for pg5 HTAP instance capabilities.

Implements the frozen `PersistentScenarioEventCapability` protocol:
declaration / activate (applied|prevented evidence) / alert / cleanup /
assert_clean. Subclasses own mechanics and honest evidence only.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Mapping

from src.persistent_scenarios.backend.contracts import (
    AppliedEvidence,
    CapabilityDeclaration,
    EventActivationContext,
    EventActivationResult,
    EventAlertPayload,
    OwnershipMode,
    PreventionEvidence,
    ResourceOwnership,
)
from src.persistent_scenarios.runtime.lifecycle import EventAttemptEvidence


class PreventedActivation(Exception):
    """The external intent really started but a trusted protection blocked it."""

    def __init__(self, mechanism: str, protection_state: Mapping[str, Any]):
        self.mechanism = mechanism
        self.protection_state = dict(protection_state)
        super().__init__(f"activation prevented by {mechanism}: protection={self.protection_state!r}")


@dataclass(slots=True)
class HtapCapabilityHandle:
    event_id: str
    capability_id: str
    entity: str
    payload: Mapping[str, Any]
    facts: dict[str, Any] = field(default_factory=dict)
    runtime_state: dict[str, Any] = field(default_factory=dict)
    stop: threading.Event = field(default_factory=threading.Event)
    sessions: list[threading.Thread] = field(default_factory=list)
    state: str = "activated"

    def join_sessions(self, timeout: float = 20.0) -> None:
        for thread in self.sessions:
            thread.join(timeout=timeout)
            if thread.is_alive():
                raise RuntimeError(
                    "Htap capability session did not stop: "
                    f"capability_id={self.capability_id!r}, event_id={self.event_id!r}, thread={thread.name!r}"
                )


def injection_failed(handle: HtapCapabilityHandle, reason: str) -> RuntimeError:
    return RuntimeError(
        "pg5 HTAP capability injection failed: "
        f"capability_id={handle.capability_id!r}, event_id={handle.event_id!r}, "
        f"state={handle.state!r}, reason={reason}"
    )


class CoreProtocolCapability:
    """Template-method base; subclasses provide mechanics and evidence."""

    capability_id: str = ""
    max_activation_seconds: int = 120

    # -- subclass hooks ------------------------------------------------------

    def _resources(self, entity: str) -> tuple[ResourceOwnership, ...]:
        raise NotImplementedError

    def _open_connection(self, context: EventActivationContext, application: str, target: str = "primary"):
        return context.environment.open_workload_connection(application, target)

    def _start(self, context: EventActivationContext) -> HtapCapabilityHandle:
        raise NotImplementedError

    def _await_impact(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> Mapping[str, Any]:
        raise NotImplementedError

    def _alert(self, handle: HtapCapabilityHandle) -> EventAlertPayload:
        raise NotImplementedError

    def cleanup(self, handle: HtapCapabilityHandle) -> None:
        handle.stop.set()
        handle.join_sessions()

    def assert_clean(self, handle: HtapCapabilityHandle) -> Mapping[str, object]:
        raise NotImplementedError

    # -- core protocol -------------------------------------------------------

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=self._resources(event.entity),
            max_activation_seconds=self.max_activation_seconds,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        clock = context.clock
        attempt = EventAttemptEvidence(
            attempted_at_monotonic=clock.monotonic(),
            detail={
                "capability_id": self.capability_id,
                "event_id": context.event.event_id,
                "entity": context.event.entity,
                "payload": dict(context.event.payload),
            },
        )
        handle = self._start(context)
        try:
            facts = self._await_impact(context, handle)
        except PreventedActivation as prevented:
            return EventActivationResult(
                handle=handle,
                attempt=attempt,
                applied=None,
                prevented=PreventionEvidence(
                    attempted=attempt,
                    mechanism=prevented.mechanism,
                    protection_state=prevented.protection_state,
                    observed_at_monotonic=clock.monotonic(),
                ),
            )
        return EventActivationResult(
            handle=handle,
            attempt=attempt,
            applied=AppliedEvidence(observed_at_monotonic=clock.monotonic(), facts=dict(facts)),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> EventAlertPayload:
        return self._alert(handle)


def exclusive(key: str, kind: str) -> ResourceOwnership:
    return ResourceOwnership(resource_key=key, resource_kind=kind, mode=OwnershipMode.EXCLUSIVE)


def shared(key: str, kind: str) -> ResourceOwnership:
    return ResourceOwnership(resource_key=key, resource_kind=kind, mode=OwnershipMode.SHARED)
