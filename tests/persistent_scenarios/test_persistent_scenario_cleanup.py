"""Cleanup ownership: reverse order, per-handle scope, no repair undoing."""

from __future__ import annotations

import pytest

from src.persistent_scenarios.runtime.cleanup import cleanup_activated_events
from src.persistent_scenarios.runtime.lifecycle import ArrivalFacts, EventArrivalStatus, EventAttemptEvidence, AppliedEvidence
from src.persistent_scenarios.runtime.state import EventRun, PersistentScenarioRun
from src.persistent_scenarios.runtime.clock import FakeClock
from tests.persistent_scenarios.fakes import make_spec


class ScopedCleanupProvider:
    """A provider whose cleanup can only see the single handle it owns."""

    def __init__(self, *, fail_handles: set | None = None):
        self.calls: list[tuple[str, object]] = []
        self.fail_handles = fail_handles or set()
        self.environment_resets = 0

    def cleanup(self, handle) -> None:
        if handle in self.fail_handles:
            raise RuntimeError(f"cleanup failed for handle={handle!r}")
        self.calls.append(("cleanup", handle))

    def assert_clean(self, handle) -> dict:
        if handle in self.fail_handles:
            raise RuntimeError(f"handle={handle!r} not clean")
        self.calls.append(("assert_clean", handle))
        return {"clean": True, "handle": str(handle)}


def make_run_with_events(count: int):
    run = PersistentScenarioRun("run-cleanup", make_spec(), None, timeline_clock=FakeClock(1.0).monotonic)
    events = []
    for index in range(count):
        event = EventRun(
            event_id=f"event_{index}",
            capability_id="demo_capability",
            occurrence=index + 1,
            entity=f"worker-{index}",
            planned_start_monotonic=1.0 + index,
            arrival=ArrivalFacts(
                status=EventArrivalStatus.APPLIED,
                attempt=EventAttemptEvidence(attempted_at_monotonic=1.0, detail={}),
                applied=AppliedEvidence(observed_at_monotonic=1.5, facts={"impact": index}),
                prevented=None,
                arrived_at_monotonic=1.5,
            ),
        )
        run.events.append(event)
        events.append(event)
    return run, events


class TestReverseOrderCleanup:
    def test_cleanup_runs_in_reverse_activation_order(self):
        run, events = make_run_with_events(3)
        provider = ScopedCleanupProvider()
        order = list(events)
        errors = cleanup_activated_events(run, order, {e.event_id: f"h-{e.event_id}" for e in events}, provider)
        assert errors == []
        assert provider.calls == [
            ("cleanup", "h-event_2"),
            ("assert_clean", "h-event_2"),
            ("cleanup", "h-event_1"),
            ("assert_clean", "h-event_1"),
            ("cleanup", "h-event_0"),
            ("assert_clean", "h-event_0"),
        ]
        assert [item["event_id"] for item in run.cleanup if item["owner"] == "event"] == [
            "event_2", "event_1", "event_0",
        ]
        assert events[2].cleanup_facts == {"clean": True, "handle": "h-event_2"}

    def test_failure_is_deferred_and_retried_without_blocking_others(self):
        run, events = make_run_with_events(3)
        provider = ScopedCleanupProvider(fail_handles={"h-event_1"})
        order = list(events)
        errors = cleanup_activated_events(run, order, {e.event_id: f"h-{e.event_id}" for e in events}, provider)
        # One failed handle surfaces as a cleanup error; the others still clean.
        assert [error["event_id"] for error in errors] == ["event_1"]
        cleaned = [item["event_id"] for item in run.cleanup if item.get("status") == "cleaned"]
        assert set(cleaned) == {"event_0", "event_2"}

    def test_same_capability_twice_cleans_isolated_handles_only(self):
        """Two occurrences of one capability produce isolated handles; cleanup
        is scoped per handle and cannot undo an agent repair (no shared reset
        exists on the provider surface at all)."""
        run, events = make_run_with_events(2)
        provider = ScopedCleanupProvider()
        handles = {e.event_id: f"occurrence-{e.occurrence}" for e in events}
        order = [events[0], events[1]]
        errors = cleanup_activated_events(run, order, handles, provider)
        assert errors == []
        assert provider.calls == [
            ("cleanup", "occurrence-2"),
            ("assert_clean", "occurrence-2"),
            ("cleanup", "occurrence-1"),
            ("assert_clean", "occurrence-1"),
        ]
        cleanup_record = [item for item in run.cleanup if item["owner"] == "event"]
        assert all("facts" in item for item in cleanup_record)

    def test_timeline_records_cleanup_evidence(self):
        run, events = make_run_with_events(2)
        provider = ScopedCleanupProvider()
        cleanup_activated_events(run, list(events), {e.event_id: f"h-{e.event_id}" for e in events}, provider)
        completed = [entry for entry in run.canonical_timeline if entry["kind"] == "cleanup_completed"]
        assert [entry["event_id"] for entry in completed] == ["event_1", "event_0"]
