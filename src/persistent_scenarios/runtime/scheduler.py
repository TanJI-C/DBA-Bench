"""Fixed monotonic event arrival scheduler with no recovery dependencies."""

from __future__ import annotations

from concurrent.futures import Executor, ThreadPoolExecutor
import threading
from collections.abc import Callable, Iterable

from src.persistent_scenarios.model.spec import EventSpec

from .clock import Clock


class TimelineScheduler:
    def __init__(self, *, clock: Clock, activation_executor: Executor | None = None):
        self.clock = clock
        self._executor = activation_executor or ThreadPoolExecutor(thread_name_prefix="persistent_scenario-activation")
        self._owns_executor = activation_executor is None

    def run(
        self,
        persistent_scenario_started: float,
        events: Iterable[EventSpec],
        activate: Callable[[EventSpec], object],
        inspect: Callable[[], object],
        inspection_interval_seconds: int,
        inspection_start_seconds: int,
        stop: threading.Event,
    ) -> list[object]:
        if inspection_interval_seconds <= 0:
            raise ValueError(f"PersistentScenario inspection interval must be positive: value={inspection_interval_seconds!r}")
        if inspection_start_seconds <= 0:
            raise ValueError(f"PersistentScenario inspection start must be positive: value={inspection_start_seconds!r}")
        event_list = tuple(events)
        event_index = 0
        next_inspection = persistent_scenario_started + inspection_start_seconds
        futures = []
        while not stop.is_set():
            next_event = persistent_scenario_started + event_list[event_index].start_seconds if event_index < len(event_list) else None
            deadline = next_inspection if next_event is None else min(next_event, next_inspection)
            if not self.clock.wait_until(deadline, stop):
                break
            while event_index < len(event_list) and persistent_scenario_started + event_list[event_index].start_seconds <= self.clock.monotonic():
                futures.append(self._executor.submit(activate, event_list[event_index]))
                event_index += 1
            while next_inspection <= self.clock.monotonic():
                futures.append(self._executor.submit(inspect))
                next_inspection += inspection_interval_seconds
        results = []
        for future in futures:
            results.append(future.result())
        return results

    def close(self) -> None:
        if self._owns_executor:
            self._executor.shutdown(wait=True)
