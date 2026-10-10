"""Engine integration tests over the arrival-facts contract (fake backend)."""

from __future__ import annotations

import threading
import time

import pytest

from src.persistent_scenarios.runtime.clock import FakeClock
from src.persistent_scenarios.runtime.engine import PersistentScenarioEngine
from src.persistent_scenarios.runtime.lifecycle import (
    AppliedEvidence,
    EventArrivalStatus,
    EventAttemptEvidence,
    FailureClassification,
)
from src.persistent_scenarios.runtime.ledger import LedgerTerminal, TrustedLedger
from src.persistent_scenarios.runtime.ports import (
    PersistentScenarioEnvironmentInvalidError,
)
from src.agents.persistent_scenario_agent import PersistentScenarioAgentContext

from tests.persistent_scenarios.fakes import (
    FakeBackend,
    FakeCapability,
    FakeEvaluationProvider,
    FakeStateFactProvider,
    ScriptedAgent,
    applied_result,
    make_event,
    make_integrity_fact,
    make_required_state_evidence,
    make_spec,
    prevented_result,
)


def run_engine(spec, backend, agent_factory, *, evaluation, clock, gate_name=None, event_activation=True, evaluation_mode="persistent_scenario"):
    engine = PersistentScenarioEngine(
        spec,
        backend,
        agent_factory,
        evaluation_provider=evaluation,
        run_id="run-test",
        port=25001,
        clock=clock,
        run_mode="development",
        event_activation=event_activation,
        evaluation_mode=evaluation_mode,
        gate_name=gate_name,
    )
    result = {}

    def run():
        result["value"] = engine.run()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    for _ in range(600):
        if "value" in result:
            break
        clock.advance(0.5)
        time.sleep(0.005)
    thread.join(timeout=10)
    assert "value" in result, "engine did not finish within the advance loop"
    return engine, result["value"]


def make_ready_ledger(tmp_path, ledger_id="orders") -> TrustedLedger:
    ledger = TrustedLedger(ledger_id, tmp_path / f"{ledger_id}.jsonl")
    ledger.append_planned_transaction(
        business_id="tx-pre", service_id=ledger_id, tx_kind="order",
        planned_at_monotonic=1.0, deadline_at_monotonic=8.0,
    )
    ledger.append_transaction_terminal(
        business_id="tx-pre", terminal=LedgerTerminal.COMPLETED,
        completed_at_monotonic=2.0, result_digest="seed",
    )
    return ledger


class TestEngineHappyPath:
    def test_two_occurrences_arrive_without_waiting_and_cleanup_reverses(self, tmp_path):
        spec = make_spec()
        capability = FakeCapability("demo_capability")
        backend = FakeBackend(capabilities=[capability], ledgers={"orders": make_ready_ledger(tmp_path)})
        evaluation = FakeEvaluationProvider()
        clock = FakeClock(0.0)
        agent_factory = lambda context: ScriptedAgent()
        engine, result = run_engine(spec, backend, agent_factory, evaluation=evaluation, clock=clock, gate_name="unresolved-prefix")

        run = engine.persistent_scenario_run
        assert result["valid"] is True
        assert [event.event_id for event in run.events] == ["event_one", "event_two"]
        assert all(event.arrival.status is EventArrivalStatus.APPLIED for event in run.events)
        # Occurrence isolation: separate handles per occurrence.
        assert run.events[0].provider_handle == "handle-event_one"
        assert run.events[1].provider_handle == "handle-event_two"
        # Arrival order: second event arrival did not wait for any resolution.
        arrival_times = {
            entry["event_id"]: entry["timestamp_monotonic"]
            for entry in run.canonical_timeline
            if entry["kind"] == "event_arrival_recorded"
        }
        assert arrival_times["event_one"] < arrival_times["event_two"]
        # Alerts published in spec order.
        alert_order = [entry["event_id"] for entry in run.canonical_timeline if entry["kind"] == "alert_published"]
        assert alert_order == ["event_one", "event_two"]
        assert set(run.alert_truth_map.values()) == {"event_one", "event_two"}
        # Single mailbox session worked the mailbox contract.
        assert len(run.agent_sessions) == 1
        assert run.agent_sessions[0]["status"] == "completed"
        # Evaluation ran before any event cleanup.
        assert len(evaluation.evaluated_runs) == 1
        assert capability.cleanup_calls == ["handle-event_two", "handle-event_one"]
        assert result["cleanup"][-1]["owner"] == "environment"
        # Ledger sealed and verified before evaluation.
        assert engine._ledgers_sealed is True
        assert run.runtime_evidence["ledgers_sealed"] is True
        gate = result["gate_result"]
        assert gate["sequence_pass"] is True
        assert gate["prefix_state_preserved"] is True
        assert gate["prefix_status"] == "applied"

    def test_prevented_arrival_keeps_run_valid(self, tmp_path):
        spec = make_spec(events=(make_event("event_one", start_seconds=2),))
        capability = FakeCapability(
            "demo_capability",
            behaviors={"event_one": prevented_result("handle-event_one", FakeClock(3.0))},
        )
        backend = FakeBackend(capabilities=[capability], ledgers={"orders": make_ready_ledger(tmp_path)})
        evaluation = FakeEvaluationProvider()
        clock = FakeClock(0.0)
        engine, result = run_engine(spec, backend, lambda context: ScriptedAgent(), evaluation=evaluation, clock=clock)

        run = engine.persistent_scenario_run
        assert result["valid"] is True
        assert run.events[0].arrival.status is EventArrivalStatus.PREVENTED
        assert run.events[0].arrival.prevented.mechanism == "statement_timeout"
        assert run.events[0].arrival.attempt is not None
        assert run.events[0].alert_task_id is not None

    def test_silent_event_arrives_without_alert(self, tmp_path):
        from src.persistent_scenarios.model.enums import EventTrigger

        spec = make_spec(events=(make_event("event_one", start_seconds=2, trigger=EventTrigger.SILENT),))
        backend = FakeBackend(ledgers={"orders": make_ready_ledger(tmp_path)})
        clock = FakeClock(0.0)
        engine, result = run_engine(spec, backend, lambda context: ScriptedAgent(), evaluation=FakeEvaluationProvider(), clock=clock)
        run = engine.persistent_scenario_run
        assert run.events[0].arrival.status is EventArrivalStatus.APPLIED
        assert run.events[0].alert_task_id is None
        assert not [entry for entry in run.canonical_timeline if entry["kind"] == "alert_published"]

    def test_engine_materializes_validity_before_the_real_evaluator_consumes_it(self, tmp_path):
        """Regression: the v2 evaluator refuses runs whose validity facts are
        unmaterialized (the refusal names the missing scoring window, run
        validity or input versions)."""

        from src.persistent_scenarios.evaluation import PersistentScenarioEvaluator

        spec = make_spec(events=(make_event("event_one", start_seconds=2),))
        backend = FakeBackend(
            capabilities=[FakeCapability("demo_capability")],
            ledgers={"orders": make_ready_ledger(tmp_path)},
        )
        clock = FakeClock(0.0)
        engine, result = run_engine(
            spec,
            backend,
            lambda context: ScriptedAgent(),
            evaluation=PersistentScenarioEvaluator(),
            clock=clock,
        )

        assert result["valid"] is True
        assert "did not materialize" not in str(result.get("failure"))
        assert engine.persistent_scenario_run.validity.valid is True
        assert engine.persistent_scenario_run.validity.ledger_complete is True


class TestEngineFailureClassification:
    def test_capability_exception_invalidates_run(self, tmp_path):
        spec = make_spec(events=(make_event("event_one", start_seconds=2),))
        capability = FakeCapability(
            "demo_capability",
            behaviors={"event_one": RuntimeError("fault script crashed")},
        )
        backend = FakeBackend(capabilities=[capability], ledgers={"orders": make_ready_ledger(tmp_path)})
        evaluation = FakeEvaluationProvider()
        clock = FakeClock(0.0)
        engine, result = run_engine(spec, backend, lambda context: ScriptedAgent(), evaluation=evaluation, clock=clock)

        run = engine.persistent_scenario_run
        assert result["valid"] is False
        assert result["OutcomePass"] is None and result["SafePass"] is None
        assert run.failure_classification is FailureClassification.INFRASTRUCTURE_FAILURE
        assert run.events[0].arrival.status is EventArrivalStatus.FAILED

    def test_environment_invalid_error_classified_as_invalid_environment(self, tmp_path):
        spec = make_spec(events=(make_event("event_one", start_seconds=2),))
        capability = FakeCapability(
            "demo_capability",
            behaviors={"event_one": PersistentScenarioEnvironmentInvalidError("contract broken")},
        )
        backend = FakeBackend(capabilities=[capability], ledgers={"orders": make_ready_ledger(tmp_path)})
        clock = FakeClock(0.0)
        engine, result = run_engine(
            spec, backend, lambda context: ScriptedAgent(),
            evaluation=FakeEvaluationProvider(), clock=clock,
        )
        assert engine.persistent_scenario_run.failure_classification is FailureClassification.INVALID_ENVIRONMENT

    def test_agent_failure_keeps_run_valid_as_model_failure(self, tmp_path):
        spec = make_spec(events=(make_event("event_one", start_seconds=2),))
        backend = FakeBackend(ledgers={"orders": make_ready_ledger(tmp_path)})
        evaluation = FakeEvaluationProvider()
        clock = FakeClock(0.0)
        engine, result = run_engine(
            spec, backend,
            lambda context: ScriptedAgent(fail=RuntimeError("model exploded")),
            evaluation=evaluation, clock=clock,
        )
        assert result["valid"] is True
        assert result["model_failure"] is True
        assert result["failure_classification"] == "agent_failure"
        # Evaluation still consumed the collected business facts.
        assert len(evaluation.evaluated_runs) == 1


class TestNoAgentBaseline:
    def test_baseline_mode_skips_agent_and_events(self, tmp_path):
        spec = make_spec()
        backend = FakeBackend(ledgers={"orders": make_ready_ledger(tmp_path)})
        evaluation = FakeEvaluationProvider()
        clock = FakeClock(0.0)
        engine, result = run_engine(
            spec, backend,
            lambda context: pytest.fail("no agent must be created in baseline mode"),
            evaluation=evaluation, clock=clock,
            event_activation=False, evaluation_mode="baseline",
        )
        assert result["valid"] is True
        assert engine.persistent_scenario_run.events == []
        assert engine.persistent_scenario_run.agent_sessions == []


class TestPrefixGates:
    @pytest.mark.parametrize("gate", ["resolved-prefix", "unresolved-prefix"])
    def test_prefix_status_preserved_for_applied_prefix(self, tmp_path, gate):
        spec = make_spec()
        backend = FakeBackend(ledgers={"orders": make_ready_ledger(tmp_path)})
        clock = FakeClock(0.0)
        engine, result = run_engine(
            spec, backend, lambda context: ScriptedAgent(),
            evaluation=FakeEvaluationProvider(), clock=clock, gate_name=gate,
        )
        gate_result = result["gate_result"]
        assert gate_result["prefix_status"] == "applied"
        # Prefix status is read at follower arrival; the first event stays
        # applied - no incident state machine resets or undoes it.
        follower_arrival = next(
            entry
            for entry in engine.persistent_scenario_run.canonical_timeline
            if entry["kind"] == "event_arrival_recorded" and entry["event_id"] == "event_two"
        )
        assert follower_arrival["payload"]["prefix_event_statuses"] == {"event_one": "applied"}

    def test_prevented_prefix_gate_passes_with_prevented_prefix(self, tmp_path):
        spec = make_spec()
        behaviors = {
            "event_one": prevented_result("handle-event_one", FakeClock(3.0)),
        }
        backend = FakeBackend(
            capabilities=[FakeCapability("demo_capability", behaviors=behaviors)],
            ledgers={"orders": make_ready_ledger(tmp_path)},
        )
        clock = FakeClock(0.0)
        engine, result = run_engine(
            spec, backend, lambda context: ScriptedAgent(),
            evaluation=FakeEvaluationProvider(), clock=clock,
            gate_name="prevented-prefix",
        )
        gate_result = result["gate_result"]
        assert gate_result["sequence_pass"] is True
        follower_arrival = next(
            entry
            for entry in engine.persistent_scenario_run.canonical_timeline
            if entry["kind"] == "event_arrival_recorded" and entry["event_id"] == "event_two"
        )
        assert follower_arrival["payload"]["prefix_event_statuses"] == {"event_one": "prevented"}


class TestCleanupOwnership:
    def test_cleanup_owns_only_its_handles_across_repeated_capability(self, tmp_path):
        spec = make_spec(events=(
            make_event("event_one", start_seconds=2),
            make_event("event_two", occurrence=2, entity="worker-2", start_seconds=4),
            make_event("event_three", occurrence=3, entity="worker-3", start_seconds=5, trigger=make_event("x").trigger),
        ))
        capability = FakeCapability("demo_capability")
        backend = FakeBackend(capabilities=[capability], ledgers={"orders": make_ready_ledger(tmp_path)})
        clock = FakeClock(0.0)
        engine, result = run_engine(
            spec, backend, lambda context: ScriptedAgent(),
            evaluation=FakeEvaluationProvider(), clock=clock,
        )
        run = engine.persistent_scenario_run
        handles = [event.provider_handle for event in run.events]
        assert len(set(handles)) == 3
        # Reverse activation order, one handle per occurrence, no global reset.
        assert capability.cleanup_calls == list(reversed(handles))
        assert all(event.cleanup_facts == {"clean": True, "handle": handle} for event, handle in zip(run.events, handles))


class TestMailboxEvidence:
    def test_reports_recorded_and_truth_map_scoped_to_trace(self, tmp_path):
        spec = make_spec()
        backend = FakeBackend(ledgers={"orders": make_ready_ledger(tmp_path)})
        clock = FakeClock(0.0)
        engine, result = run_engine(spec, backend, lambda context: ScriptedAgent(execute_first=True), evaluation=FakeEvaluationProvider(), clock=clock)
        run = engine.persistent_scenario_run
        completed = run.mailbox_state["completed"]
        completed_ids = {item["task_id"] for item in completed}
        assert completed_ids
        # Every alert task got exactly one report; inspections ride the same path.
        assert set(run.alert_truth_map.values()) == {"event_one", "event_two"}
        assert set(run.alert_truth_map) <= completed_ids
        for item in completed:
            assert item["report"]["summary"]


class TestInterfaceV1RuntimeFacts:
    def test_scoring_window_validity_input_versions_and_facts(self, tmp_path):
        from src.persistent_scenarios.runtime.lifecycle import EVALUATION_SCHEMA, TRACE_SCHEMA, ScoringWindow

        spec = make_spec()
        state_facts = FakeStateFactProvider(
            integrity=(make_integrity_fact(),),
            required_state=(make_required_state_evidence(),),
        )
        backend = FakeBackend(ledgers={"orders": make_ready_ledger(tmp_path)}, state_facts=state_facts)
        clock = FakeClock(0.0)
        engine, result = run_engine(
            spec, backend, lambda context: ScriptedAgent(execute_first=True),
            evaluation=FakeEvaluationProvider(), clock=clock,
        )
        run = engine.persistent_scenario_run
        window = run.business_window
        assert isinstance(window, ScoringWindow)
        assert window.scoring_start_monotonic == pytest.approx(1.0)  # warmup ended
        assert window.scoring_end_monotonic == pytest.approx(1.0 + spec.horizon_seconds)
        assert window.input_stop_monotonic == pytest.approx(1.0 + spec.input_stop_seconds)
        # Input versions bind spec/protocol/trace/evaluation/lease/calibration/code.
        versions = run.input_versions
        assert versions.protocol_version == "persistent-scenario-v2"
        assert versions.trace_schema == TRACE_SCHEMA
        assert versions.evaluation_schema == EVALUATION_SCHEMA
        assert versions.resource_lease_id == "run-test"
        assert versions.calibration_evidence_id == "fake-dev"
        assert len(versions.spec_digest) == 64
        # Final sampling captured backend-executed verifier facts.
        assert state_facts.calls == 2
        assert run.integrity_facts[0].check_id == "ledger_conservation"
        assert run.required_state_evidence[0].status.value == "captured"
        # Validity conclusion materialized from run outcome + ledger seal.
        assert run.validity.valid is True
        assert run.validity.classification is None
        assert run.validity.ledger_complete is True

    def test_invalid_run_validity_carries_classification(self, tmp_path):
        spec = make_spec(events=(make_event("event_one", start_seconds=2),))
        capability = FakeCapability(
            "demo_capability",
            behaviors={"event_one": RuntimeError("fault script crashed")},
        )
        backend = FakeBackend(capabilities=[capability], ledgers={"orders": make_ready_ledger(tmp_path)})
        clock = FakeClock(0.0)
        engine, result = run_engine(spec, backend, lambda context: ScriptedAgent(), evaluation=FakeEvaluationProvider(), clock=clock)
        validity = engine.persistent_scenario_run.validity
        assert result["valid"] is False
        assert validity.valid is False
        assert validity.classification == "infrastructure_failure"
        assert validity.reason
        assert validity.ledger_complete is True
