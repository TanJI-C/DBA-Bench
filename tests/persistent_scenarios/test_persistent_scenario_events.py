"""Event observations carry evidence only, never gates."""

from __future__ import annotations

import pytest

from src.persistent_scenarios.evaluation.contracts import LedgerIncompleteError
from src.persistent_scenarios.evaluation.events import build_event_observations

from tests.persistent_scenarios._evaluation_factories import (
    applied_arrival,
    event_run,
    failed_arrival,
    prevented_arrival,
)


def test_event_observations_preserve_state_and_evidence_without_pass_fields():
    observations = build_event_observations(
        [
            event_run("event-1", applied_arrival(arrival=10.0, facts={"lock_queue": 3})),
            event_run(
                "event-2",
                prevented_arrival(arrival=34.0, mechanism="scoped_statement_timeout"),
                occurrence=2,
                entity="order-2",
            ),
            event_run(
                "event-3",
                failed_arrival(arrival=50.0, error="activation precondition missing"),
                capability_id="capability.io_spike",
                entity="volume",
            ),
        ]
    )

    assert [item["arrival_status"] for item in observations] == [
        "applied",
        "attempted_prevented",
        "injection_failed",
    ]
    assert observations[1]["evidence"]["prevention_mechanism"] == "scoped_statement_timeout"
    assert observations[2]["evidence"]["attempt"] == {"error": "activation precondition missing"}
    for item in observations:
        assert not any("pass" in key or "gate" in key or "coverage" in key for key in item)


def test_repeated_capability_occurrences_stay_observational_records():
    observations = build_event_observations(
        [
            event_run("event-1", applied_arrival(), occurrence=1),
            event_run("event-2", applied_arrival(arrival=30.0), occurrence=2, entity="order-2"),
        ]
    )

    assert observations[0]["capability_id"] == observations[1]["capability_id"]
    assert observations[1]["occurrence"] == 2
    assert observations[1]["entity"] == "order-2"


def test_event_without_materialized_arrival_facts_is_a_facility_gap():
    with pytest.raises(LedgerIncompleteError, match="arrival facts"):
        build_event_observations([event_run("event-1", None)])
