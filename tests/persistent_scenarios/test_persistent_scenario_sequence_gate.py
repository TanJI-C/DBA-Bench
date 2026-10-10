"""Development gate evidence computed from arrival facts and run records."""

from __future__ import annotations

from types import SimpleNamespace

from src.persistent_scenarios.runtime.lifecycle import (
    ArrivalFacts,
    EventArrivalStatus,
    EventAttemptEvidence,
    AppliedEvidence,
    PreventionEvidence,
)
from src.persistent_scenarios.runtime.sequence_gate import build_gate_result
from src.persistent_scenarios.runtime.state import EventRun, PersistentScenarioRun
from src.persistent_scenarios.runtime.clock import FakeClock
from tests.persistent_scenarios.fakes import make_spec


def applied_arrival(at: float = 1.0) -> ArrivalFacts:
    return ArrivalFacts(
        status=EventArrivalStatus.APPLIED,
        attempt=EventAttemptEvidence(attempted_at_monotonic=at, detail={}),
        applied=AppliedEvidence(observed_at_monotonic=at, facts={"impact": True}),
        prevented=None,
        arrived_at_monotonic=at,
    )


def prevented_arrival(at: float = 1.0) -> ArrivalFacts:
    attempt = EventAttemptEvidence(attempted_at_monotonic=at, detail={})
    return ArrivalFacts(
        status=EventArrivalStatus.PREVENTED,
        attempt=attempt,
        applied=None,
        prevented=PreventionEvidence(
            attempted=attempt,
            mechanism="statement_timeout",
            protection_state={"value": "2s"},
            observed_at_monotonic=at,
        ),
        arrived_at_monotonic=at,
    )


def make_run(arrivals: dict[str, ArrivalFacts | None]):
    spec = make_spec()
    run = PersistentScenarioRun("run-gate", spec, None, timeline_clock=FakeClock(1.0).monotonic)
    for index, event in enumerate(spec.events):
        run.events.append(EventRun(
            event_id=event.event_id,
            capability_id=event.capability_id,
            occurrence=event.occurrence,
            entity=event.entity,
            planned_start_monotonic=1.0 + index,
            arrival=arrivals.get(event.event_id),
        ))
    run.ledgers = {"orders": SimpleNamespace(event_count=lambda kind: 3)}
    return run


def full_runtime_evidence(**overrides):
    evidence = {
        "environment_deployed": True,
        "ledger_event_count": 10,
        "ledgers_sealed": True,
        "telemetry_sample_count": 5,
    }
    evidence.update(overrides)
    return evidence


def base_mailbox_actions(run):
    session = {"session_id": "session-0001"}
    run.action_history.extend([
        {"api": "mailbox", "surface": "control", "session_id": "session-0001",
         "args": {"operation": "read"}, "result": {"pending": [], "completed": []}},
        {"api": "mailbox", "surface": "control", "session_id": "session-0001",
         "args": {"operation": "write", "task_ids": ["task-0001"],
                  "report": {"diagnosis": {"conditions": []}, "outcome": {"changes": [], "verification": []}, "summary": "s"}},
         "result": {"completed_task_ids": ["task-0001"]}},
        {"api": "mailbox", "surface": "control", "session_id": "session-0001",
         "args": {"operation": "wait"}, "result": {"waited": True}},
    ])
    run.mailbox_state = {"completed": [{"task_id": "task-0001"}]}
    timeline_payloads = [
        {"kind": "agent_session_started", "payload": {"session_id": "session-0001"}},
        {"kind": "agent_mailbox_state", "payload": {"state": "active"}},
        {"kind": "agent_mailbox_state", "payload": {"state": "idle"}},
        {"kind": "mailbox_wait_started", "payload": {"session_id": "session-0001"}},
        {"kind": "mailbox_document_changed", "payload": {"operation": "published"}},
        {"kind": "mailbox_wait_completed", "payload": {"session_id": "session-0001"}},
        {"kind": "agent_mailbox_state", "payload": {"state": "woken"}},
        {"kind": "alert_published", "event_id": "event_one"},
        {"kind": "alert_published", "event_id": "event_two"},
        {"kind": "event_arrival_recorded", "event_id": "event_two",
         "payload": {"prefix_event_statuses": {"event_one": "applied"}}},
    ]
    for entry in timeline_payloads:
        run.append_timeline(owner="test", **entry)
    run.agent_sessions.append({"session_id": "session-0001", "status": "running", "state": "active"})
    run.agent_conversation_phases.append({"phase_index": 0, "session_id": "session-0001", "messages": []})
    for event in run.spec.events:
        run.cleanup.append({"owner": "event", "event_id": event.event_id, "status": "cleaned", "facts": {}})


class TestGateResults:
    def test_all_applied_passes(self):
        run = make_run({"event_one": applied_arrival(), "event_two": applied_arrival()})
        base_mailbox_actions(run)
        result = build_gate_result(
            "unresolved-prefix", run,
            event_activation=True,
            runtime_evidence=full_runtime_evidence(),
            cleanup_errors=(),
        )
        assert result["sequence_pass"] is True
        assert result["prefix_state_preserved"] is True
        assert result["ledger_seal_pass"] is True

    def test_missing_arrival_fails_activation(self):
        run = make_run({"event_one": applied_arrival(), "event_two": None})
        base_mailbox_actions(run)
        result = build_gate_result(
            "unresolved-prefix", run,
            event_activation=True,
            runtime_evidence=full_runtime_evidence(),
            cleanup_errors=(),
        )
        assert result["event_activation_pass"] is False
        assert result["sequence_pass"] is False

    def test_failed_arrival_fails_activation(self):
        failed = ArrivalFacts(
            status=EventArrivalStatus.FAILED,
            attempt=EventAttemptEvidence(attempted_at_monotonic=1.0, detail={}),
            applied=None,
            prevented=None,
            arrived_at_monotonic=1.0,
        )
        run = make_run({"event_one": failed, "event_two": applied_arrival()})
        base_mailbox_actions(run)
        result = build_gate_result(
            "unresolved-prefix", run,
            event_activation=True,
            runtime_evidence=full_runtime_evidence(),
            cleanup_errors=(),
        )
        assert result["event_activation_pass"] is False

    def test_prevented_prefix_requires_prevented_prefix_status(self):
        run = make_run({"event_one": applied_arrival(), "event_two": applied_arrival()})
        base_mailbox_actions(run)
        result = build_gate_result(
            "prevented-prefix", run,
            event_activation=True,
            runtime_evidence=full_runtime_evidence(),
            cleanup_errors=(),
        )
        assert result["prefix_state_preserved"] is False

    def test_prevented_prefix_passes_when_first_event_prevented(self):
        run = make_run({"event_one": prevented_arrival(), "event_two": applied_arrival()})
        base_mailbox_actions(run)
        follower = next(
            entry for entry in run.canonical_timeline
            if entry["kind"] == "event_arrival_recorded"
        )
        follower["payload"]["prefix_event_statuses"] = {"event_one": "prevented"}
        result = build_gate_result(
            "prevented-prefix", run,
            event_activation=True,
            runtime_evidence=full_runtime_evidence(),
            cleanup_errors=(),
        )
        assert result["prefix_state_preserved"] is True
        assert result["sequence_pass"] is True

    def test_cleanup_error_fails_teardown(self):
        run = make_run({"event_one": applied_arrival(), "event_two": applied_arrival()})
        base_mailbox_actions(run)
        result = build_gate_result(
            "unresolved-prefix", run,
            event_activation=True,
            runtime_evidence=full_runtime_evidence(),
            cleanup_errors=({"event_id": "event_one", "status": "failed", "error": "x"},),
        )
        assert result["final_teardown_pass"] is False
        assert result["sequence_pass"] is False

    def test_unsealed_ledger_fails_seal_gate(self):
        run = make_run({"event_one": applied_arrival(), "event_two": applied_arrival()})
        base_mailbox_actions(run)
        result = build_gate_result(
            "unresolved-prefix", run,
            event_activation=True,
            runtime_evidence=full_runtime_evidence(ledgers_sealed=False),
            cleanup_errors=(),
        )
        assert result["ledger_seal_pass"] is False

    def test_no_agent_gate_skips_agent_checks(self):
        run = make_run({})
        result = build_gate_result(
            "no-agent", run,
            event_activation=False,
            runtime_evidence=full_runtime_evidence(),
            cleanup_errors=(),
        )
        assert result["mailbox_contract_pass"] is True
        assert result["single_mailbox_session_pass"] is True
        assert result["event_activation_pass"] is True
