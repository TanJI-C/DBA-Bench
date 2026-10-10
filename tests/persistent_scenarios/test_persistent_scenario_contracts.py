"""Backend port contracts, evidence invariants and trace export shape."""

from __future__ import annotations

import pytest

from src.persistent_scenarios.backend.contracts import (
    CapabilityDeclaration,
    EventActivationResult,
    EventAlertPayload,
    OwnershipMode,
    ResourceOwnership,
)
from src.persistent_scenarios.runtime.lifecycle import (
    AppliedEvidence,
    ArrivalFacts,
    EventArrivalStatus,
    EventAttemptEvidence,
    PreventionEvidence,
)
from src.persistent_scenarios.runtime.ports import (
    PersistentScenarioAgentProtocolError,
    PersistentScenarioAgentProviderError,
    PersistentScenarioEnvironmentInvalidError,
    PersistentScenarioProviderError,
)
from src.persistent_scenarios.runtime.trace import export_persistent_scenario_trace
from src.persistent_scenarios.runtime.state import EventRun, PersistentScenarioRun
from src.persistent_scenarios.runtime.clock import FakeClock
from tests.persistent_scenarios.fakes import FakeEvaluationProvider, make_spec


def attempt(at: float = 1.0) -> EventAttemptEvidence:
    return EventAttemptEvidence(attempted_at_monotonic=at, detail={"op": "inject"})


class TestEventActivationResult:
    def test_requires_exactly_one_of_applied_or_prevented(self):
        now = 1.0
        EventActivationResult(handle="h", attempt=attempt(now), applied=AppliedEvidence(now, {"i": 1}), prevented=None)
        EventActivationResult(
            handle="h",
            attempt=attempt(now),
            applied=None,
            prevented=PreventionEvidence(attempted=attempt(now), mechanism="m", protection_state={}, observed_at_monotonic=now),
        )
        with pytest.raises(ValueError, match="exactly one"):
            EventActivationResult(handle="h", attempt=attempt(now), applied=None, prevented=None)
        with pytest.raises(ValueError, match="exactly one"):
            EventActivationResult(
                handle="h",
                attempt=attempt(now),
                applied=AppliedEvidence(now, {}),
                prevented=PreventionEvidence(attempted=attempt(now), mechanism="m", protection_state={}, observed_at_monotonic=now),
            )


class TestArrivalFacts:
    def test_prevented_requires_both_attempt_and_protection(self):
        with pytest.raises(ValueError, match="prevented"):
            ArrivalFacts(
                status=EventArrivalStatus.PREVENTED,
                attempt=attempt(),
                applied=None,
                prevented=None,
                arrived_at_monotonic=1.0,
            )

    def test_applied_cannot_carry_prevention(self):
        with pytest.raises(ValueError, match="prevented arrival"):
            ArrivalFacts(
                status=EventArrivalStatus.PREVENTED,
                attempt=attempt(),
                applied=AppliedEvidence(1.0, {}),
                prevented=PreventionEvidence(attempted=attempt(), mechanism="m", protection_state={}, observed_at_monotonic=1.0),
                arrived_at_monotonic=1.0,
            )

    def test_failed_carries_only_attempt(self):
        ArrivalFacts(
            status=EventArrivalStatus.FAILED,
            attempt=attempt(),
            applied=None,
            prevented=None,
            arrived_at_monotonic=1.0,
        )
        with pytest.raises(ValueError, match="failed arrival"):
            ArrivalFacts(
                status=EventArrivalStatus.FAILED,
                attempt=attempt(),
                applied=AppliedEvidence(1.0, {}),
                prevented=None,
                arrived_at_monotonic=1.0,
            )


class TestCapabilityDeclaration:
    def test_resources_required(self):
        declaration = CapabilityDeclaration(
            capability_id="cap",
            resources=(ResourceOwnership("row:orders#1", "row", OwnershipMode.EXCLUSIVE),),
            max_activation_seconds=5,
        )
        assert declaration.resources[0].mode is OwnershipMode.EXCLUSIVE
        with pytest.raises(ValueError, match="declare resources"):
            CapabilityDeclaration(capability_id="cap", resources=(), max_activation_seconds=5)
        with pytest.raises(ValueError, match="positive integer"):
            CapabilityDeclaration(
                capability_id="cap",
                resources=(ResourceOwnership("row:orders#1", "row", OwnershipMode.SHARED),),
                max_activation_seconds=0,
            )


class TestEventAlertPayload:
    def test_alert_payload_exposes_symptoms_only(self):
        payload = EventAlertPayload(
            title="transaction throughput degraded",
            symptoms=("order commit latency above threshold",),
            severity="warning",
            category="database",
        )
        data = payload.title
        assert "statement_timeout" not in data  # no root cause in the title
        with pytest.raises(ValueError, match="symptoms"):
            EventAlertPayload(title="t", symptoms=(), severity="w", category="c")


class TestProviderErrorVocabulary:
    def test_environment_invalid_is_provider_error(self):
        assert issubclass(PersistentScenarioEnvironmentInvalidError, PersistentScenarioProviderError)

    def test_agent_errors_are_separate_from_provider_errors(self):
        assert not issubclass(PersistentScenarioAgentProtocolError, PersistentScenarioProviderError)
        assert not issubclass(PersistentScenarioAgentProviderError, PersistentScenarioProviderError)


class TestTraceExport:
    def test_trace_v2_document_shape(self, tmp_path):
        clock = FakeClock(1.0)
        spec = make_spec()
        run = PersistentScenarioRun("run-trace", spec, None, timeline_clock=clock.monotonic, started_monotonic=1.0)
        run.events.append(EventRun(
            event_id="event_one",
            capability_id="demo_capability",
            occurrence=1,
            entity="worker-1",
            planned_start_monotonic=3.0,
            arrival=ArrivalFacts(
                status=EventArrivalStatus.APPLIED,
                attempt=attempt(),
                applied=AppliedEvidence(1.5, {"impact": True}),
                prevented=None,
                arrived_at_monotonic=1.5,
            ),
        ))
        run.append_timeline(owner="test", kind="scoring_phase_started")
        evaluation = FakeEvaluationProvider()
        run.evaluation = dict(evaluation.result)
        path = export_persistent_scenario_trace(run, tmp_path)
        import json

        document = json.loads(open(path, encoding="utf-8").read())
        assert document["$schema"] == "persistent_scenario_trace_v2"
        assert document["metadata"]["run_id"] == "run-trace"
        assert document["persistent_scenario_spec"]["protocol_version"] == "persistent-scenario-v2"
        assert document["event_runs"][0]["arrival"]["status"] == "applied"
        assert "workload_request_summary" not in document
        assert document["artifacts"]["timeline"]

    def test_trace_v1_schema_rejected_for_new_runs(self, tmp_path, monkeypatch):
        import json

        clock = FakeClock(1.0)
        run = PersistentScenarioRun("run-trace-v1", make_spec(), None, timeline_clock=clock.monotonic)
        path = export_persistent_scenario_trace(run, tmp_path)
        document = json.loads(open(path, encoding="utf-8").read())
        assert document["$schema"] != "persistent_scenario_trace_v1"
