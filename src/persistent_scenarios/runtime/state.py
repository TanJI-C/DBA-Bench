"""Mutable Persistent Scenario run records with append-only evidence history."""

from __future__ import annotations

import time
import threading
from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType
from collections.abc import Mapping as MappingABC
from typing import Callable, Mapping

from ..model.spec import PersistentScenarioSpec, JSONValue
from .encoding import jsonable
from .lifecycle import (
    ActionFact,
    ArrivalFacts,
    CheckpointReason,
    FailureClassification,
    InputVersions,
    IntegrityFact,
    RequiredStateEvidence,
    RunValidityFact,
    ScoringWindow,
)


def _frozen_jsonable(value: Mapping[str, object]) -> Mapping[str, object]:
    if not isinstance(value, MappingABC):
        raise TypeError(f"run evidence field must be a mapping: value={value!r}")
    return MappingProxyType(dict(jsonable(dict(value))))


@dataclass(frozen=True, slots=True)
class EventCheckpoint:
    """Trusted structured state sample at a run boundary; never agent self-report."""

    checkpoint_id: str
    event_id: str | None
    reason: CheckpointReason
    evaluated_at_monotonic: float
    safety: Mapping[str, JSONValue]
    trusted_state: Mapping[str, JSONValue]
    action_indices: tuple[int, ...]
    ledger_positions: Mapping[str, int]
    telemetry_indices: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.checkpoint_id.strip():
            raise ValueError(f"checkpoint_id must be non-empty: value={self.checkpoint_id!r}")
        if not isinstance(self.reason, CheckpointReason):
            raise TypeError(f"checkpoint reason must be CheckpointReason: value={self.reason!r}")
        object.__setattr__(self, "safety", _frozen_jsonable(self.safety))
        object.__setattr__(self, "trusted_state", _frozen_jsonable(self.trusted_state))
        if self.ledger_positions and not all(
            isinstance(key, str) and isinstance(value, int) for key, value in self.ledger_positions.items()
        ):
            raise TypeError(f"checkpoint ledger_positions must map ledger ids to ints: value={self.ledger_positions!r}")
        object.__setattr__(self, "ledger_positions", MappingProxyType(dict(self.ledger_positions)))


@dataclass(slots=True)
class EventRun:
    """Execution facts for one Event occurrence. No incident-state machinery."""

    event_id: str
    capability_id: str
    occurrence: int
    entity: str
    planned_start_monotonic: float
    arrival: ArrivalFacts | None = None
    provider_handle: object | None = None
    alert_task_id: str | None = None
    cleanup_facts: Mapping[str, JSONValue] | None = None


@dataclass(slots=True)
class PersistentScenarioRun:
    run_id: str
    spec: PersistentScenarioSpec
    env: object
    source_spec: PersistentScenarioSpec | None = None
    timeline_clock: Callable[[], float] = time.monotonic
    events: list[EventRun] = field(default_factory=list)
    canonical_timeline: list[dict[str, object]] = field(default_factory=list)
    action_history: list[dict[str, object]] = field(default_factory=list)
    # Trusted checkpoints must observe a complete agent action, never a half-written result.
    action_lock: threading.RLock = field(default_factory=threading.RLock, repr=False)
    turn_history: list[dict[str, object]] = field(default_factory=list)
    agent_conversation_raw: list[dict[str, object]] = field(default_factory=list)
    agent_conversation_phases: list[dict[str, object]] = field(default_factory=list)
    agent_sessions: list[dict[str, object]] = field(default_factory=list)
    agent_llm_usage: list[dict[str, object]] = field(default_factory=list)
    learning_events: list[dict[str, object]] = field(default_factory=list)
    learning_memory: dict[str, object] | None = None
    mailbox_history: list[dict[str, object]] = field(default_factory=list)
    mailbox_state: dict[str, object] = field(default_factory=dict)
    alert_truth_map: dict[str, str] = field(default_factory=dict)
    checkpoints: list[EventCheckpoint] = field(default_factory=list)
    safety_checkpoints: list[dict[str, object]] = field(default_factory=list)
    ledgers: dict[str, object] = field(default_factory=dict)
    trusted_telemetry: list[object] = field(default_factory=list)
    business_window: ScoringWindow | None = None
    action_facts: list[ActionFact] = field(default_factory=list)
    integrity_facts: list[IntegrityFact] = field(default_factory=list)
    required_state_evidence: list[RequiredStateEvidence] = field(default_factory=list)
    validity: RunValidityFact | None = None
    input_versions: InputVersions | None = None
    evaluation: dict[str, object] | None = None
    cleanup: list[dict[str, object]] = field(default_factory=list)
    failure_certificate: dict[str, object] | None = None
    failure_classification: FailureClassification | None = None
    started_monotonic: float | None = None
    ended_monotonic: float | None = None
    started_wall: float | None = None
    ended_wall: float | None = None
    pre_cleanup_evaluation: dict[str, object] | None = None
    _timeline_lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    run_mode: str = "development"
    time_scale: float = 1.0
    formal_eligible: bool = False
    calibration_evidence_hash: str | None = None
    early_stop_reason: str | None = None
    evaluation_mode: str = "persistent_scenario"
    runtime_evidence: dict[str, object] = field(default_factory=dict)
    gate_result: dict[str, object] | None = None

    @property
    def event_by_id(self) -> dict[str, EventRun]:
        return {event.event_id: event for event in self.events}

    def append_timeline(
        self,
        *,
        owner: str,
        kind: str,
        timestamp_monotonic: float | None = None,
        payload: Mapping[str, object] | None = None,
        event_id: str | None = None,
    ) -> dict[str, object]:
        with self._timeline_lock:
            recorded_timestamp = self.timeline_clock() if timestamp_monotonic is None else timestamp_monotonic
            if self.canonical_timeline and recorded_timestamp < self.canonical_timeline[-1]["timestamp_monotonic"]:
                raise ValueError(
                    "Persistent Scenario canonical timeline timestamp moved backwards: "
                    f"run_id={self.run_id!r}, owner={owner!r}, kind={kind!r}, "
                    f"timestamp_monotonic={recorded_timestamp!r}, "
                    f"previous_timestamp_monotonic={self.canonical_timeline[-1]['timestamp_monotonic']!r}"
                )
            entry = {
                "sequence": len(self.canonical_timeline) + 1,
                "timestamp_monotonic": recorded_timestamp,
                "timestamp_wall": time.time(),
                "owner": owner,
                "kind": kind,
                "event_id": event_id,
                "payload": dict(payload or {}),
            }
            self.canonical_timeline.append(entry)
        return entry

    def append_checkpoint(self, checkpoint: EventCheckpoint) -> None:
        if any(item.checkpoint_id == checkpoint.checkpoint_id for item in self.checkpoints):
            raise ValueError(
                "Persistent Scenario checkpoint ID already exists: "
                f"checkpoint_id={checkpoint.checkpoint_id!r}"
            )
        if self.checkpoints and checkpoint.evaluated_at_monotonic < self.checkpoints[-1].evaluated_at_monotonic:
            raise ValueError(
                "Persistent Scenario checkpoints must be append-only by monotonic time: "
                f"previous={self.checkpoints[-1].evaluated_at_monotonic}, current={checkpoint.evaluated_at_monotonic}"
            )
        self.checkpoints.append(checkpoint)

    def append_agent_conversation(
        self,
        raw_messages: list[Mapping[str, object]],
        phases: list[Mapping[str, object]],
    ) -> None:
        """Record the latest conversation snapshot (latest wins).

        Evidence integrity does not depend on this store: every snapshot also
        lands in the run timeline and the sidecar files, so the full history
        stays on disk regardless of what the agent reports here.
        """
        self.agent_conversation_raw = [deepcopy(dict(message)) for message in raw_messages]
        self.agent_conversation_phases = [deepcopy(dict(phase)) for phase in phases]
