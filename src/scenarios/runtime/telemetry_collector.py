"""Canonical Scenario telemetry collection."""

from __future__ import annotations

import threading
import time


class TelemetryCollector:
    def __init__(self, capture, interval_seconds: float = 2.0, operation_lock=None):
        if interval_seconds <= 0:
            raise ValueError(f"Telemetry interval must be positive: interval_seconds={interval_seconds}")
        self.capture = capture
        self.interval_seconds = interval_seconds
        self.samples: list[object] = []
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._error: Exception | None = None
        self._operation_lock = operation_lock

    def set_operation_lock(self, operation_lock) -> None:
        if self._thread is not None:
            raise RuntimeError("TelemetryCollector operation lock must be set before start()")
        self._operation_lock = operation_lock

    def _capture(self):
        if self._operation_lock is None:
            return self.capture()
        with self._operation_lock:
            return self.capture()

    def start(self) -> None:
        if self._thread is not None:
            raise RuntimeError("TelemetryCollector cannot start twice")
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="scenario-telemetry", daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.samples.append(self._capture())
            except Exception as exc:
                self._error = exc
                self._stop.set()
                return
            self._stop.wait(self.interval_seconds)

    def sample_now(self):
        if self._error is not None:
            raise RuntimeError(f"Scenario telemetry collector failed: error={self._error!r}") from self._error
        sample = self._capture()
        self.samples.append(sample)
        return sample

    def stop(self) -> list[object]:
        if self._thread is None:
            raise RuntimeError("TelemetryCollector.stop requires start()")
        self._stop.set()
        self._thread.join(timeout=max(5.0, self.interval_seconds * 3))
        if self._thread.is_alive():
            raise RuntimeError("Scenario telemetry collector thread did not stop")
        if self._error is not None:
            raise RuntimeError(f"Scenario telemetry collector failed: error={self._error!r}") from self._error
        self._thread = None
        return list(self.samples)
