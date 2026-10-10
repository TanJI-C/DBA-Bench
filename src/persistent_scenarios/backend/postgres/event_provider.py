"""PostgreSQL event services: registry dispatch plus handle-bound services.

The engine resolves capabilities through this provider, activates them
directly, and then calls ``agent_alert``/``cleanup``/``assert_clean`` with the
returned handle. The provider keeps the handle -> (capability, activation
context) binding recorded at activate time so those calls dispatch to the
capability that owns the handle; PostgreSQL capabilities are plain objects
that do not self-identify from a handle.
"""

from __future__ import annotations

from src.persistent_scenarios.backend.contracts import (
    EventActivationContext,
    EventActivationResult,
    EventAlertPayload,
    PersistentScenarioEventCapability,
)
from src.persistent_scenarios.model.spec import EventSpec

from .registry import PostgresEventCapabilityRegistry


class _BoundCapability:
    """Records the provider binding when the engine activates through it."""

    def __init__(self, provider: "PostgresEventProvider", capability: PersistentScenarioEventCapability):
        self._provider = provider
        self._capability = capability
        self.capability_id = capability.capability_id

    def declaration(self, event: EventSpec):
        return self._capability.declaration(event)

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        result = self._capability.activate(context)
        self._provider._record_binding(result.handle, self._capability, context)
        return result

    def alert(self, context: EventActivationContext, handle: object) -> EventAlertPayload:
        return self._capability.alert(context, handle)

    def cleanup(self, handle: object) -> None:
        self._capability.cleanup(handle)

    def assert_clean(self, handle: object):
        return self._capability.assert_clean(handle)


class PostgresEventProvider:
    def __init__(self, registry: PostgresEventCapabilityRegistry):
        self._registry = registry
        self._bindings: dict[int, tuple[PersistentScenarioEventCapability, EventActivationContext, object]] = {}

    def _record_binding(
        self,
        handle: object,
        capability: PersistentScenarioEventCapability,
        context: EventActivationContext,
    ) -> None:
        binding = (capability, context, handle)
        existing = self._bindings.get(id(handle))
        if existing is not None and existing[2] is not handle:
            raise ValueError(
                "PostgreSQL event provider already holds a different handle at the same id: "
                f"capability_id={capability.capability_id!r}, event_id={context.event.event_id!r}"
            )
        self._bindings[id(handle)] = binding

    def _binding(self, handle: object) -> tuple[PersistentScenarioEventCapability, EventActivationContext]:
        try:
            capability, context, _registered = self._bindings[id(handle)]
        except KeyError:
            raise ValueError(
                "PostgreSQL event handle was not activated through this provider: "
                f"handle={handle!r}, registered_handles={len(self._bindings)}"
            ) from None
        return capability, context

    def capability(self, capability_id: str) -> _BoundCapability:
        return _BoundCapability(self, self._registry.capability(capability_id))

    def agent_alert(self, handle: object) -> EventAlertPayload:
        capability, context = self._binding(handle)
        return capability.alert(context, handle)

    def cleanup(self, handle: object) -> None:
        capability, _context = self._binding(handle)
        capability.cleanup(handle)

    def assert_clean(self, handle: object):
        capability, _context = self._binding(handle)
        return capability.assert_clean(handle)
