"""Replica freshness sampling into the trusted watermark ledger."""

from __future__ import annotations

from collections.abc import Callable
import threading

from src.persistent_scenarios.runtime.clock import Clock
from src.persistent_scenarios.runtime.ledger import FreshnessSample, TrustedLedger


class FreshnessRecorder:
    """Periodically records primary commit watermarks and replica visibility."""

    def __init__(
        self,
        *,
        service_id: str,
        ledger: TrustedLedger,
        clock: Clock,
        sample: Callable[[int], FreshnessSample],
        interval_seconds: float,
    ):
        if interval_seconds <= 0:
            raise ValueError(f"freshness interval must be positive: service_id={service_id!r}, value={interval_seconds!r}")
        self.service_id = service_id
        self.ledger = ledger
        self.clock = clock
        self._sample = sample
        self._interval_seconds = interval_seconds
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._sequence = 0
        self._lock = threading.Lock()
        self._error: Exception | None = None

    def start(self) -> None:
        if self._thread is not None:
            raise RuntimeError(f"freshness recorder already started: service_id={self.service_id!r}")
        self._thread = threading.Thread(
            target=self._loop, name=f"persistent_scenario-freshness-{self.service_id}", daemon=True
        )
        self._thread.start()

    def _loop(self) -> None:
        next_sample = self.clock.monotonic()
        while not self._stop.is_set():
            if not self.clock.wait_until(next_sample, self._stop):
                return
            try:
                self.record_once()
            except Exception as exc:
                self._error = exc
                self._stop.set()
                return
            next_sample += self._interval_seconds

    def record_once(self) -> FreshnessSample:
        with self._lock:
            self._sequence += 1
            sequence = self._sequence
        sample = self._sample(sequence)
        self.ledger.append_freshness_sample(sample)
        return sample

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=10)
            if self._thread.is_alive():
                raise RuntimeError(f"freshness recorder thread did not stop: service_id={self.service_id!r}")
        if self._error is not None:
            raise RuntimeError(
                f"freshness recorder failed: service_id={self.service_id!r}, error={self._error!r}"
            ) from self._error
