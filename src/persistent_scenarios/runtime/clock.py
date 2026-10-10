"""Monotonic clocks used by production and deterministic tests."""

from __future__ import annotations

import threading
import time
from typing import Protocol


class Clock(Protocol):
    def monotonic(self) -> float: ...
    def wait_until(self, deadline: float, stop: threading.Event) -> bool: ...


class RealClock:
    def monotonic(self) -> float:
        return time.monotonic()

    def wait_until(self, deadline: float, stop: threading.Event) -> bool:
        while True:
            remaining = deadline - self.monotonic()
            if remaining <= 0:
                return True
            if stop.wait(min(remaining, 0.25)):
                return False


class FakeClock:
    def __init__(self, start: float = 0.0):
        self._now = float(start)
        self._condition = threading.Condition()

    def monotonic(self) -> float:
        with self._condition:
            return self._now

    def advance(self, seconds: float) -> float:
        if seconds < 0:
            raise ValueError(f"FakeClock cannot move backwards: seconds={seconds}")
        with self._condition:
            self._now += seconds
            self._condition.notify_all()
            return self._now

    def wait_until(self, deadline: float, stop: threading.Event) -> bool:
        with self._condition:
            while self._now < deadline and not stop.is_set():
                self._condition.wait(timeout=0.05)
            return not stop.is_set()
