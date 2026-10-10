"""Trusted run checkpoints for the Persistent Scenario timeline.

Checkpoints are structured state samples at fixed boundaries - warmup
baseline, each event arrival and the horizon final. They are evidence for the
trace and for the evaluator; they never drive per-event outcome decisions.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Mapping

from ..model.spec import EventSpec
from .clock import Clock
from .lifecycle import CheckpointReason, EventArrivalStatus
from .state import EventCheckpoint, EventRun, PersistentScenarioRun


class CheckpointCoordinator:
    def __init__(
        self,
        run: PersistentScenarioRun,
        *,
        clock: Clock,
        safety_provider,
        safety_baseline: object,
        ledger_positions: Callable[[], Mapping[str, int]],
        telemetry_index_count: Callable[[], int],
        on_error: Callable[[str, Exception], None] | None = None,
        on_checkpoint: Callable[[EventCheckpoint, PersistentScenarioRun], None] | None = None,
    ):
        self.run = run
        self.clock = clock
        self.safety_provider = safety_provider
        self.safety_baseline = safety_baseline
        self._ledger_positions = ledger_positions
        self._telemetry_index_count = telemetry_index_count
        self.on_error = on_error
        self.on_checkpoint = on_checkpoint
        self._lock = threading.RLock()
        self._per_reason_counts: dict[tuple[str, str], int] = {}

    def _safety(self, reason: CheckpointReason) -> Mapping[str, object]:
        with self.run.action_lock:
            result = self.safety_provider.evaluate(
                self.run.env,
                self.safety_baseline,
                tuple(self.run.action_history),
                reason.value,
            )
        if not isinstance(result, Mapping):
            raise TypeError(
                f"Persistent Scenario safety provider must return a mapping: reason={reason.value!r}, result={result!r}"
            )
        safety = dict(result)
        safety["checkpoint_reason"] = reason.value
        return safety

    def _append(
        self,
        reason: CheckpointReason,
        *,
        event_id: str | None,
        trusted_state: Mapping[str, object],
    ) -> EventCheckpoint:
        now = self.clock.monotonic()
        key = (event_id or "run", reason.value)
        with self._lock:
            self._per_reason_counts[key] = self._per_reason_counts.get(key, 0) + 1
            count = self._per_reason_counts[key]
        checkpoint = EventCheckpoint(
            checkpoint_id=f"{event_id or 'run'}:{reason.value}:{count:04d}",
            event_id=event_id,
            reason=reason,
            evaluated_at_monotonic=now,
            safety=self._safety(reason),
            trusted_state=dict(trusted_state),
            action_indices=tuple(range(len(self.run.action_history))),
            ledger_positions=dict(self._ledger_positions()),
            telemetry_indices=tuple(range(self._telemetry_index_count())),
        )
        self.run.append_checkpoint(checkpoint)
        self.run.append_timeline(
            owner="engine",
            kind="trusted_checkpoint",
            event_id=event_id,
            payload={"checkpoint_id": checkpoint.checkpoint_id, "reason": reason.value},
        )
        if self.on_checkpoint is not None:
            self.on_checkpoint(checkpoint, self.run)
        return checkpoint

    def on_warmup_baseline(self) -> EventCheckpoint:
        return self._append(CheckpointReason.WARMUP_BASELINE, event_id=None, trusted_state={})

    def on_arrival(self, event: EventSpec, event_run: EventRun) -> EventCheckpoint:
        if event_run.arrival is None:
            raise RuntimeError(
                f"arrival checkpoint requires recorded arrival facts: event_id={event.event_id!r}"
            )
        arrival = event_run.arrival
        status = arrival.status.value
        applied_facts = dict(arrival.applied.facts) if arrival.applied is not None else {}
        prevention = (
            {
                "mechanism": arrival.prevented.mechanism,
                "protection_state": dict(arrival.prevented.protection_state),
            }
            if arrival.prevented is not None
            else {}
        )
        return self._append(
            CheckpointReason.EVENT_ARRIVAL,
            event_id=event.event_id,
            trusted_state={
                "arrival_status": status,
                "applied_facts": applied_facts,
                **({"prevention": prevention} if prevention else {}),
            },
        )

    def on_horizon_final(self) -> EventCheckpoint:
        applied_event_ids = tuple(
            event_run.event_id
            for event_run in self.run.events
            if event_run.arrival is not None and event_run.arrival.status is EventArrivalStatus.APPLIED
        )
        return self._append(
            CheckpointReason.HORIZON_FINAL,
            event_id=None,
            trusted_state={"applied_event_ids": list(applied_event_ids)},
        )

    def capture_baseline_safety(self) -> Mapping[str, object]:
        """Safety snapshot recorded together with the warmup baseline."""
        safety = dict(self._safety(CheckpointReason.WARMUP_BASELINE))
        self.run.safety_checkpoints.append({"event_id": None, **safety})
        return safety
