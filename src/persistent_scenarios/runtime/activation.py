"""Runtime-owned activation ledger for bounded Event handles."""

from __future__ import annotations


class ActivationLedger:
    def __init__(self) -> None:
        self.order: list[object] = []
        self.handles: dict[str, object] = {}

    def record(self, event_run, handle: object) -> None:
        event_id = event_run.event_id
        if event_id in self.handles:
            raise ValueError(f"PersistentScenario activation ledger already contains an event: event_id={event_id!r}")
        self.order.append(event_run)
        self.handles[event_id] = handle

    def record_if_missing(self, event_run, handle: object) -> None:
        if event_run.event_id not in self.handles:
            self.record(event_run, handle)
