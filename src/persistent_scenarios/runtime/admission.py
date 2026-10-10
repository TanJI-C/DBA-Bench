"""Persistent Scenario admission boundary.

Static admission happens before environment creation: every Event's
capability must be registered, declarations must match the event timing, and
exclusive resource ownership must not conflict between overlapping event
activation windows.
"""

from __future__ import annotations

from ..model.spec import EventSpec, PersistentScenarioSpec
from .ports import PersistentScenarioProviderError


def admit_persistent_scenario(spec: PersistentScenarioSpec, backend, registry) -> None:
    """Validate static/backend/capability admission before environment creation."""
    backend.validate_spec(spec)
    declarations = {}
    for event in spec.events:
        capability = registry.capability(event.capability_id)
        declaration = capability.declaration(event)
        if declaration.capability_id != event.capability_id:
            raise PersistentScenarioProviderError(
                "capability declaration identity mismatch: "
                f"event_id={event.event_id!r}, expected_capability={event.capability_id!r}, "
                f"declared={declaration.capability_id!r}"
            )
        if declaration.max_activation_seconds > event.activation_timeout_seconds:
            raise PersistentScenarioProviderError(
                "capability activation bound exceeds the event activation timeout: "
                f"event_id={event.event_id!r}, capability_id={event.capability_id!r}, "
                f"max_activation_seconds={declaration.max_activation_seconds}, "
                f"activation_timeout_seconds={event.activation_timeout_seconds}"
            )
        declarations[event.event_id] = declaration
    _admit_resource_conflicts(spec, declarations)


def _overlaps(first: EventSpec, second: EventSpec) -> bool:
    first_end = first.start_seconds + first.activation_timeout_seconds
    second_end = second.start_seconds + second.activation_timeout_seconds
    return first.start_seconds < second_end and second.start_seconds < first_end


def _admit_resource_conflicts(spec: PersistentScenarioSpec, declarations: dict[str, object]) -> None:
    events = spec.events
    for index, first in enumerate(events):
        for second in events[index + 1:]:
            if not _overlaps(first, second):
                continue
            first_keys = {
                ownership.resource_key
                for ownership in declarations[first.event_id].resources
                if ownership.mode.value == "exclusive"
            }
            if not first_keys:
                continue
            second_keys = {
                ownership.resource_key
                for ownership in declarations[second.event_id].resources
                if ownership.mode.value == "exclusive"
            }
            conflict = first_keys & second_keys
            if conflict:
                raise PersistentScenarioProviderError(
                    "overlapping events claim exclusive ownership of the same resources: "
                    f"first_event_id={first.event_id!r}, second_event_id={second.event_id!r}, "
                    f"conflict_resource_keys={sorted(conflict)!r}"
                )
