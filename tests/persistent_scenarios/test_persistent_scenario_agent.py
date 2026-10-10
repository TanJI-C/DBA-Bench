"""Mailbox protocol and persistent session tests at the control-plane level."""

from __future__ import annotations

import threading
import time

import pytest

from src.persistent_scenarios.runtime.clock import FakeClock
from src.persistent_scenarios.runtime.mailbox import PersistentScenarioMailbox
from src.persistent_scenarios.runtime.sessions import PersistentScenarioAgentControl
from src.persistent_scenarios.runtime.state import PersistentScenarioRun
from tests.persistent_scenarios.fakes import FakeEnvironment, make_event, make_spec


def make_control():
    stop = threading.Event()
    mailbox = PersistentScenarioMailbox(stop)
    clock = FakeClock(1.0)
    run = PersistentScenarioRun("run-agent", make_spec(), None, timeline_clock=clock.monotonic)
    run.agent_sessions.append({
        "session_id": "session-0001",
        "kind": "mailbox",
        "started_at_monotonic": 1.0,
        "ended_at_monotonic": None,
        "status": "running",
        "state": "active",
        "error": None,
        "result": None,
    })
    control = PersistentScenarioAgentControl(run, FakeEnvironment(), mailbox, clock=clock)
    control.register_session("session-0001")
    return run, mailbox, control, clock, stop


def report():
    return {
        "diagnosis": {"conditions": [{
            "type": "lock_wait",
            "factor": "long transaction",
            "entity": "orders",
            "evidence": ["lock queue"],
        }]},
        "outcome": {"changes": ["raised timeout"], "verification": ["queue drained"]},
        "summary": "done",
    }


class TestSessionUniqueness:
    def test_second_session_rejected(self):
        _, _, control, _, _ = make_control()
        with pytest.raises(ValueError, match="already registered"):
            control.register_session("session-0002")

    def test_actions_from_unregistered_session_rejected(self):
        _, mailbox, control, _, _ = make_control()
        mailbox.publish(task_type="incident", created_at_monotonic=1.0, title="t", description="d")
        with pytest.raises(ValueError, match="another mailbox session"):
            control.mailbox("read", session_id="session-0002")


class TestMailboxContract:
    def test_read_write_wait_flow_records_states(self):
        run, mailbox, control, clock, stop = make_control()
        mailbox.publish(task_type="incident", created_at_monotonic=1.0, title="alert", description="symptom")
        control.record_agent_state("active", session_id="session-0001")
        status = control.mailbox("read", session_id="session-0001")
        assert [item["task_id"] for item in status["pending"]] == ["task-0001"]
        result = control.mailbox("write", task_ids=["task-0001"], report=report(), session_id="session-0001")
        assert result["completed_task_ids"] == ["task-0001"]
        wait_result_holder = {}

        def do_wait():
            wait_result_holder["value"] = control.mailbox("wait", session_id="session-0001")

        thread = threading.Thread(target=do_wait, daemon=True)
        thread.start()
        deadline = time.monotonic() + 5
        while "mailbox_wait_started" not in [entry["kind"] for entry in run.canonical_timeline]:
            assert time.monotonic() < deadline, "wait never started"
            time.sleep(0.005)
        clock.advance(1.0)
        # A wake is driven by newly appended work (or the end signal).
        mailbox.publish(task_type="periodic_inspection", created_at_monotonic=clock.monotonic(), title="check", description="inspect")
        thread.join(timeout=5)
        assert wait_result_holder["value"]["waited"] is True
        states = [
            entry["payload"]["state"]
            for entry in run.canonical_timeline
            if entry["kind"] == "agent_mailbox_state"
        ]
        assert "idle" in states and "woken" in states

    def test_write_requires_structured_report(self):
        _, mailbox, control, _, _ = make_control()
        mailbox.publish(task_type="incident", created_at_monotonic=1.0, title="alert", description="symptom")
        with pytest.raises(ValueError, match="report"):
            control.mailbox("write", task_ids=["task-0001"], report=None, session_id="session-0001")
        with pytest.raises(Exception):
            control.mailbox("write", task_ids=["task-0001"], report={"summary": "incomplete"}, session_id="session-0001")

    def test_unknown_and_duplicate_task_ids_rejected(self):
        _, mailbox, control, _, _ = make_control()
        mailbox.publish(task_type="incident", created_at_monotonic=1.0, title="alert", description="symptom")
        with pytest.raises(ValueError, match="Unknown mailbox task_id"):
            control.mailbox("write", task_ids=["task-9999"], report=report(), session_id="session-0001")
        control.mailbox("write", task_ids=["task-0001"], report=report(), session_id="session-0001")
        with pytest.raises(ValueError, match="already completed"):
            control.mailbox("write", task_ids=["task-0001"], report=report(), session_id="session-0001")

    def test_wait_with_stale_pending_rejected(self):
        _, mailbox, control, _, _ = make_control()
        mailbox.publish(task_type="incident", created_at_monotonic=1.0, title="alert", description="symptom")
        control.mailbox("read", session_id="session-0001")
        with pytest.raises(ValueError, match="requires no pending tasks"):
            control.mailbox("wait", session_id="session-0001")

    def test_read_rejects_write_arguments(self):
        _, _, control, _, _ = make_control()
        with pytest.raises(ValueError, match="does not accept"):
            control.mailbox("read", task_ids=["task-0001"], session_id="session-0001")

    def test_mailbox_history_is_append_only_with_monotonic_revision(self):
        run, mailbox, control, _, _ = make_control()
        mailbox.publish(task_type="incident", created_at_monotonic=1.0, title="alert", description="symptom")
        control.mailbox("read", session_id="session-0001")
        control.mailbox("write", task_ids=["task-0001"], report=report(), session_id="session-0001")
        revisions = [change["revision"] for change in run.mailbox_history]
        assert revisions == sorted(revisions) and len(set(revisions)) == len(revisions)


class TestProtocolFailureEvidence:
    def test_protocol_error_recorded_on_action(self):
        run, mailbox, control, _, _ = make_control()
        mailbox.publish(task_type="incident", created_at_monotonic=1.0, title="alert", description="symptom")
        with pytest.raises(ValueError):
            control.mailbox("write", task_ids=["task-0001"], report={"summary": "bad"}, session_id="session-0001")
        failed = [entry for entry in run.action_history if entry.get("error")]
        assert failed and "fields mismatch" in failed[-1]["error"]


class TestConversationHistory:
    def test_conversation_snapshot_latest_wins(self):
        """The run stores the latest conversation snapshot; history lives in
        the timeline/sidecar evidence, so the store itself imposes no shape."""
        _, _, control, _, _ = make_control()
        control.record_agent_conversation(
            [{"role": "user", "content": "a"}],
            [{"phase_index": 0, "messages": [{"role": "user", "content": "a"}], "compaction": None}],
            session_id="session-0001",
        )
        control.record_agent_conversation(
            [
                {"role": "user", "content": "a"},
                {"role": "assistant", "content": "b"},
            ],
            [
                {"phase_index": 0, "messages": [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}], "compaction": None},
            ],
            session_id="session-0001",
        )
        control.record_agent_conversation(
            [
                {"role": "user", "content": "a"},
                {"role": "assistant", "content": "b"},
                {"role": "user", "content": [{"type": "tool_result", "content": "r1"}, {"type": "tool_result", "content": "r2"}]},
            ],
            [
                {"phase_index": 0, "messages": [
                    {"role": "user", "content": "a"},
                    {"role": "assistant", "content": "b"},
                    {"role": "user", "content": [{"type": "tool_result", "content": "r1"}, {"type": "tool_result", "content": "r2"}]}],
                    "compaction": None},
            ],
            session_id="session-0001",
        )
        assert [m["role"] for m in control.run.agent_conversation_raw] == ["user", "assistant", "user"]
        assert control.run.agent_conversation_phases[0]["session_id"] == "session-0001"


class TestAgentFailureSession:
    def test_failed_agent_session_keeps_run_valid_as_model_failure(self, tmp_path):
        """Agent crash is a valid run: business facts stay, model failure recorded."""
        from src.persistent_scenarios.runtime.engine import PersistentScenarioEngine
        from src.persistent_scenarios.runtime.ledger import LedgerTerminal, TrustedLedger
        from tests.persistent_scenarios.fakes import FakeBackend, FakeEvaluationProvider

        spec = make_spec(events=(make_event("event_one", start_seconds=2),))
        ledger = TrustedLedger("orders", tmp_path / "orders.jsonl")
        ledger.append_planned_transaction(
            business_id="tx-pre", service_id="orders", tx_kind="order",
            planned_at_monotonic=1.0, deadline_at_monotonic=8.0,
        )
        ledger.append_transaction_terminal(
            business_id="tx-pre", terminal=LedgerTerminal.COMPLETED,
            completed_at_monotonic=2.0, result_digest="seed",
        )
        backend = FakeBackend(ledgers={"orders": ledger})
        clock = FakeClock(0.0)
        engine = PersistentScenarioEngine(
            spec,
            backend,
            lambda ctx: (_ for _ in ()).throw(RuntimeError("model exploded")),
            evaluation_provider=FakeEvaluationProvider(),
            run_id="run-agent-fail", port=25001, clock=clock, run_mode="development",
        )
        holder = {}

        def run():
            holder["value"] = engine.run()

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        for _ in range(600):
            if "value" in holder:
                break
            clock.advance(0.5)
            time.sleep(0.005)
        thread.join(timeout=10)
        result = holder["value"]
        assert result["valid"] is True
        assert result["model_failure"] is True
        session = engine.persistent_scenario_run.agent_sessions[0]
        assert session["status"] == "failed"
