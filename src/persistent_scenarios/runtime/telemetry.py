"""Trusted telemetry loop shared by PersistentScenario backends."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable, Mapping
import threading

from .clock import Clock


@dataclass(frozen=True, slots=True)
class TrustedTelemetrySample:
    timestamp_monotonic: float
    values: Mapping[str, object]


class TelemetryRuntime:
    def __init__(self, sample: Callable[[], Mapping[str, object]], *, interval_seconds: float, clock: Clock):
        if interval_seconds <= 0:
            raise ValueError(f"Telemetry interval must be positive: interval_seconds={interval_seconds}")
        self._sample = sample
        self._interval_seconds = interval_seconds
        self._clock = clock
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._samples: list[TrustedTelemetrySample] = []
        self._error: Exception | None = None

    def start(self) -> None:
        if self._thread is not None:
            raise RuntimeError("TelemetryRuntime cannot start twice")
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="persistent_scenario-trusted-telemetry", daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        next_sample = self._clock.monotonic()
        try:
            while not self._stop.is_set():
                if not self._clock.wait_until(next_sample, self._stop):
                    return
                values = self._sample()
                if not isinstance(values, Mapping):
                    raise TypeError(f"Trusted telemetry provider must return a mapping: value={values!r}")
                self._samples.append(TrustedTelemetrySample(self._clock.monotonic(), dict(values)))
                next_sample += self._interval_seconds
        except Exception as exc:
            self._error = exc
            self._stop.set()

    def stop(self) -> tuple[TrustedTelemetrySample, ...]:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=10)
            if self._thread.is_alive():
                raise RuntimeError("TelemetryRuntime thread did not stop")
        if self._error is not None:
            raise RuntimeError(f"Trusted telemetry runtime failed: error={self._error!r}") from self._error
        return tuple(self._samples)

    @property
    def samples(self) -> tuple[TrustedTelemetrySample, ...]:
        if self._error is not None:
            raise RuntimeError(f"Trusted telemetry runtime failed: error={self._error!r}") from self._error
        return tuple(self._samples)
