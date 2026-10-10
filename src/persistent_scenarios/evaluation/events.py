"""Observational event records built from core ``EventRun.arrival`` facts.

Events are external disturbances and business changes, not questions to answer.
These records preserve applied/prevented/failed evidence for review; they never
enter a conjunction, so one action mitigating several events, a symptom
cancelled by a third event, or a repair preventing a recurrence all remain
purely business-result decisions.
"""

from __future__ import annotations

from ..runtime.lifecycle import ArrivalFacts, EventArrivalStatus

from .contracts import LedgerIncompleteError


_ARRIVAL_STATES = {
    EventArrivalStatus.APPLIED: "applied",
    EventArrivalStatus.PREVENTED: "attempted_prevented",
    EventArrivalStatus.FAILED: "injection_failed",
}


def _arrival_evidence(arrival: ArrivalFacts) -> dict[str, object]:
    evidence: dict[str, object] = {"attempt": dict(arrival.attempt.detail)}
    if arrival.applied is not None:
        evidence["applied_facts"] = dict(arrival.applied.facts)
    if arrival.prevented is not None:
        evidence["prevention_mechanism"] = arrival.prevented.mechanism
        evidence["protection_state"] = dict(arrival.prevented.protection_state)
    return evidence


def build_event_observations(events) -> list[dict[str, object]]:
    observations = []
    for event in events:
        arrival: ArrivalFacts | None = event.arrival
        if arrival is None:
            raise LedgerIncompleteError(
                f"An Event reached final evaluation without materialized arrival facts: "
                f"event_id={event.event_id!r}"
            )
        observations.append(
            {
                "event_id": event.event_id,
                "capability_id": event.capability_id,
                "occurrence": event.occurrence,
                "entity": event.entity,
                "planned_start_monotonic": event.planned_start_monotonic,
                "arrival_status": _ARRIVAL_STATES[arrival.status],
                "arrival_monotonic": arrival.arrived_at_monotonic,
                "evidence": _arrival_evidence(arrival),
            }
        )
    return observations
