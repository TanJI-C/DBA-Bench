"""Action boundary tests: what the agent surface may and may not do."""

from __future__ import annotations

import threading
import time

import pytest

from src.persistent_scenarios.runtime.clock import FakeClock
from src.persistent_scenarios.runtime.mailbox import PersistentScenarioMailbox
from src.persistent_scenarios.runtime.sessions import PersistentScenarioAgentControl
from src.persistent_scenarios.runtime.state import PersistentScenarioRun
from tests.persistent_scenarios.fakes import FakeActionClassifier, FakeEnvironment, make_spec


def make_control(*, activation_gate: threading.Event | None = None):
    stop = threading.Event()
    mailbox = PersistentScenarioMailbox(stop)
    clock = FakeClock(1.0)
    run = PersistentScenarioRun("run-boundary", make_spec(), None, timeline_clock=clock.monotonic)
    environment = FakeEnvironment()
    control = PersistentScenarioAgentControl(
        run,
        environment,
        mailbox,
        clock=clock,
        activation_gate=activation_gate,
        action_classifier=FakeActionClassifier(),
    )
    control.register_session("session-0001")
    return run, mailbox, control, clock, environment


class TestAgentSqlBounds:
    def test_execute_sql_is_bounded_like_a_real_client(self):
        run, _, control, clock, environment = make_control()
        result = control.execute("execute_sql", {"sql_query": "SELECT 1;"}, session_id="session-0001")
        assert result["status"] == "success"
        assert environment.operations[0] == ("set_sql_timeouts", "60s", "10s")
        assert environment.operations[-1] == ("reset_sql_timeouts", None, None)

    def test_non_sql_actions_are_not_bounded(self):
        _, _, control, _, environment = make_control()
        control.execute("query_metrics", {"metric_type": "cpu"}, session_id="session-0001")
        assert environment.sql_timeouts is None
        assert not any(op[0] == "set_sql_timeouts" for op in environment.operations)


class TestActionHistory:
    def test_actions_and_turns_are_recorded_append_only(self):
        run, _, control, _, _ = make_control()
        control.execute("execute_sql", {"sql_query": "SELECT 1;"}, session_id="session-0001")
        control.execute("execute_sql", {"sql_query": "SELECT 2;"}, session_id="session-0001")
        assert [entry["turn"] for entry in run.action_history] == [1, 2]
        assert all(entry["surface"] == "environment" for entry in run.action_history)
        assert [entry["api"] for entry in run.action_history] == ["execute_sql", "execute_sql"]
        environment_entries = [
            entry for entry in run.canonical_timeline if entry["kind"] == "environment_action"
        ]
        assert len(environment_entries) == 2
        # Backend classifier produced one typed safety fact per action.
        assert [fact.action_class for fact in run.action_facts] == ["read_only", "read_only"]
        assert [fact.sequence for fact in run.action_facts] == [0, 1]

    def test_environment_failure_recorded_then_raised(self):
        run, _, control, _, environment = make_control()
        environment.execute_action = lambda api, args: (_ for _ in ()).throw(RuntimeError("connection down"))
        with pytest.raises(RuntimeError, match="environment action failed"):
            control.execute("execute_sql", {"sql_query": "SELECT 1;"}, session_id="session-0001")
        failed = run.action_history[-1]
        assert "connection down" in failed["error"]
        assert failed["timestamp_end_monotonic"] >= failed["timestamp_start_monotonic"]
        assert run.action_facts == []


class TestActivationGate:
    def test_agent_sql_waits_for_inflight_activation(self):
        gate = threading.Event()
        run, _, control, _, environment = make_control(activation_gate=gate)
        finished = []
        thread = threading.Thread(
            target=lambda: finished.append(
                control.execute("execute_sql", {"sql_query": "SELECT 1;"}, session_id="session-0001")
            ),
            daemon=True,
        )
        thread.start()
        time.sleep(0.1)
        assert not finished, "agent SQL must wait while an activation is in flight"
        gate.set()
        thread.join(timeout=5)
        assert finished

    def test_mailbox_operations_do_not_wait_on_the_gate(self):
        gate = threading.Event()
        _, mailbox, control, _, _ = make_control(activation_gate=gate)
        mailbox.publish(task_type="incident", created_at_monotonic=1.0, title="t", description="d")
        result = control.mailbox("read", session_id="session-0001")
        assert result["pending"]


class TestSessionBoundary:
    def test_execute_from_other_session_rejected(self):
        _, _, control, _, environment = make_control()
        with pytest.raises(ValueError, match="another mailbox session"):
            control.execute("execute_sql", {"sql_query": "SELECT 1;"}, session_id="session-0002")
        assert environment.operations == []

    def test_execute_before_registration_rejected(self):
        stop = threading.Event()
        mailbox = PersistentScenarioMailbox(stop)
        run = PersistentScenarioRun("run-boundary", make_spec(), None, timeline_clock=FakeClock(1.0).monotonic)
        control = PersistentScenarioAgentControl(run, FakeEnvironment(), mailbox, clock=FakeClock(1.0))
        with pytest.raises(ValueError, match="not initialized"):
            control.execute("execute_sql", {"sql_query": "SELECT 1;"}, session_id="session-0001")
