"""PostgreSQL capability registry and handle-bound event provider tests."""

from __future__ import annotations

import pytest

from src.persistent_scenarios.backend.contracts import EventActivationContext
from src.persistent_scenarios.backend.postgres.event_provider import PostgresEventProvider
from src.persistent_scenarios.backend.postgres.registry import PostgresEventCapabilityRegistry
from src.persistent_scenarios.runtime.admission import admit_persistent_scenario
from src.persistent_scenarios.runtime.clock import FakeClock
from src.persistent_scenarios.runtime.ports import PersistentScenarioProviderError

from tests.persistent_scenarios.fakes import FakeCapability, make_event, make_spec


def _registry(*capabilities: FakeCapability) -> PostgresEventCapabilityRegistry:
    return PostgresEventCapabilityRegistry(tuple(capabilities))


class _StubBackend:
    def validate_spec(self, spec) -> None:
        return None


def test_duplicate_capability_registration_is_rejected_with_both_objects():
    with pytest.raises(ValueError, match="Duplicate PostgreSQL capability registration"):
        _registry(FakeCapability("demo_capability"), FakeCapability("demo_capability"))


def test_blank_capability_id_is_rejected():
    capability = FakeCapability("demo_capability")
    capability.capability_id = "  "
    with pytest.raises(ValueError, match="non-empty capability_id"):
        _registry(capability)


def test_unknown_capability_lookup_reports_registered_ids():
    registry = _registry(FakeCapability("registered_one"), FakeCapability("registered_two"))
    with pytest.raises(ValueError, match="registered_"):
        registry.capability("missing_capability")


def test_capability_lookup_returns_the_registered_object():
    capability = FakeCapability("demo_capability")
    registry = _registry(capability)
    assert registry.capability("demo_capability") is capability
    assert registry.capability_ids() == ("demo_capability",)


def test_provider_binds_handles_activated_through_it():
    clock = FakeClock()
    capability = FakeCapability("demo_capability")
    provider = PostgresEventProvider(_registry(capability))
    spec = make_spec()
    event = spec.events[0]
    context = EventActivationContext("run-1", spec, event, environment=None, clock=clock)

    bound = provider.capability("demo_capability")
    assert bound.declaration(event) == capability.declaration(event)
    result = bound.activate(context)
    assert result.applied is not None
    assert capability.contexts[event.event_id] is context

    alert = provider.agent_alert(result.handle)
    assert alert.title.startswith("opaque alert")
    provider.cleanup(result.handle)
    assert capability.cleanup_calls == [result.handle]
    assert provider.assert_clean(result.handle) == capability.assert_clean(result.handle)


def test_provider_rejects_handles_activated_elsewhere():
    provider = PostgresEventProvider(_registry(FakeCapability("demo_capability")))
    with pytest.raises(ValueError, match="not activated through this provider"):
        provider.agent_alert("unregistered-handle")


def test_admission_rejects_overlapping_exclusive_same_entity_events():
    events = (
        make_event("event_one", start_seconds=2),
        make_event("event_two", occurrence=2, entity="worker-1", start_seconds=4),
    )
    spec = make_spec(events=events)
    capability = FakeCapability("demo_capability", exclusive=True)
    with pytest.raises(PersistentScenarioProviderError, match="exclusive ownership of the same resources"):
        admit_persistent_scenario(spec, _StubBackend(), _registry(capability))


def test_admission_allows_same_capability_occurrences_on_distinct_entities():
    events = (
        make_event("event_one", start_seconds=2),
        make_event("event_two", occurrence=2, entity="worker-2", start_seconds=4),
    )
    spec = make_spec(events=events)
    capability = FakeCapability("demo_capability", exclusive=True)
    admit_persistent_scenario(spec, _StubBackend(), _registry(capability))


def test_admission_allows_shared_overlapping_claims():
    events = (
        make_event("event_one", start_seconds=2),
        make_event("event_two", occurrence=2, entity="worker-1", start_seconds=4),
    )
    spec = make_spec(events=events)
    capability = FakeCapability("demo_capability", exclusive=False)
    admit_persistent_scenario(spec, _StubBackend(), _registry(capability))


def test_non_overlapping_exclusive_events_do_not_conflict():
    events = (
        make_event("event_one", start_seconds=2),
        make_event("event_two", occurrence=2, entity="worker-1", start_seconds=10),
    )
    spec = make_spec(events=events, horizon_seconds=20)
    capability = FakeCapability("demo_capability", exclusive=True)
    admit_persistent_scenario(spec, _StubBackend(), _registry(capability))
