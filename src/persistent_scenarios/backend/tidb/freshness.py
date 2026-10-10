"""TiCDC checkpoint watermark sampling and freshness recording.

Freshness for the CDC scenario is a business contract: "when can the
downstream correctly see a committed upstream transaction". Checkpoint/resolved
TSO from TiCDC and the downstream received watermark are auxiliary facts; the
business truth is produced by comparing markers through instance-owned SQL.
This module provides the shared plumbing:

- ``tso_to_unix_ms`` / ``tso_lag_seconds``: TSO arithmetic (TSO physical part
  is milliseconds since the epoch);
- ``CdcChangefeedCheckpointSampler``: reads changefeed checkpoint/resolved TSO
  through ``cdc cli`` in a capture container and turns them into
  ``FreshnessSample`` facts;
- ``TiDBFreshnessRecorder``: periodic sampling into the trusted ledger.
"""

from __future__ import annotations

from collections.abc import Callable
import json
import threading

from src.persistent_scenarios.runtime.clock import Clock
from src.persistent_scenarios.runtime.ledger import FreshnessSample, TrustedLedger

_TSO_PHYSICAL_SHIFT = 18


def tso_to_unix_ms(tso: int) -> int:
    """Physical milliseconds encoded in a TSO (low 18 bits are the counter)."""
    if isinstance(tso, bool) or not isinstance(tso, int) or tso < 0:
        raise ValueError(f"TSO must be a non-negative integer: value={tso!r}")
    return tso >> _TSO_PHYSICAL_SHIFT


def tso_lag_seconds(upstream_tso: int, replica_tso: int) -> float:
    """Replication lag in seconds derived from two TSOs (floored at 0)."""
    lag_ms = tso_to_unix_ms(upstream_tso) - tso_to_unix_ms(replica_tso)
    return max(0.0, lag_ms / 1000.0)


class CdcChangefeedCheckpointSampler:
    """Read one changefeed's checkpoint/resolved TSO via ``cdc cli changefeed query``.

    ``cli_runner`` receives the full argument vector (after ``docker exec``),
    e.g. ``["/cdc", "cli", "changefeed", "query", "--changefeed-id", ...]`` and
    returns the captured stdout. The pinned pingcap/ticdc image keeps the
    binary at ``/cdc`` (it is not on PATH). The instance driver wires the
    runner to its environment
    (``PersistentTiDBEnvironment.changefeed_cli_runner``).

    v8.1 output facts verified live (pingcap/ticdc:v8.1.0): the
    full query payload carries ``state`` / ``checkpoint_tso`` / ``resolved_ts``
    (snake_case); the ``--simple`` subset carries state/checkpoint_tso/error
    but no resolved_ts, so the sampler uses the full query.
    """

    def __init__(
        self,
        *,
        service_id: str,
        changefeed_id: str,
        cli_runner: Callable[[list[str]], str],
    ):
        if not changefeed_id.strip():
            raise ValueError(f"changefeed_id must be non-empty: service_id={service_id!r}")
        self.service_id = service_id
        self.changefeed_id = changefeed_id
        self._cli_runner = cli_runner

    def _query(self) -> dict:
        stdout = self._cli_runner([
            "/cdc", "cli", "changefeed", "query",
            "--changefeed-id", self.changefeed_id,
        ])
        payload = json.loads(stdout)
        if not isinstance(payload, dict):
            raise TypeError(f"cdc cli changefeed query returned non-mapping output: payload={payload!r}")
        return payload

    def checkpoint(self) -> dict:
        """Return the raw query payload (state, checkpoint_tso, resolved_ts, ...)."""
        return self._query()

    def sample(self, sequence: int) -> FreshnessSample:
        """Produce one FreshnessSample from the changefeed checkpoint state.

        ``primary_watermark`` carries the resolved TSO of the upstream capture
        and ``replica_watermark`` the sink checkpoint TSO; both are auxiliary
        facts, never business truth on their own.
        """
        payload = self._query()
        checkpoint_tso = int(payload["checkpoint_tso"])
        resolved_tso = int(payload["resolved_ts"])
        state = str(payload["state"])
        return FreshnessSample(
            sample_id=f"{self.service_id}-changefeed-{self.changefeed_id}-{sequence}",
            sampled_at_monotonic=0.0,  # stamped by the recorder
            primary_watermark=str(resolved_tso),
            replica_watermark=str(checkpoint_tso),
            lag_seconds=tso_lag_seconds(resolved_tso, checkpoint_tso),
            detail={"state": state, "changefeed_id": self.changefeed_id},
        )


class TiDBFreshnessRecorder:
    """Periodically records freshness samples into the trusted ledger.

    The first sample is stamped with the recorder's sampling clock: the
    ``sample`` callable returns a template with ``sampled_at_monotonic=0.0``
    and the recorder replaces it with ``clock.monotonic()`` before appending.
    """

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
            target=self._loop, name=f"persistent_scenario-tidb-freshness-{self.service_id}", daemon=True
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
        template = self._sample(sequence)
        sample = FreshnessSample(
            sample_id=template.sample_id,
            sampled_at_monotonic=self.clock.monotonic(),
            primary_watermark=template.primary_watermark,
            replica_watermark=template.replica_watermark,
            lag_seconds=template.lag_seconds,
            detail=template.detail,
        )
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
