"""TiCDC checkpoint sampler and freshness recorder tests."""

import json
import threading
import time

import pytest

from src.persistent_scenarios.backend.tidb.freshness import (
    CdcChangefeedCheckpointSampler,
    TiDBFreshnessRecorder,
    tso_lag_seconds,
    tso_to_unix_ms,
)
from src.persistent_scenarios.runtime.clock import FakeClock, RealClock
from src.persistent_scenarios.runtime.ledger import LedgerView, TrustedLedger


def test_tso_arithmetic():
    # TSO = physical_ms << 18 | counter
    tso = (1_700_000_000_000 << 18) | 7
    assert tso_to_unix_ms(tso) == 1_700_000_000_000
    replica = (1_699_999_999_000 << 18) | 3
    assert tso_lag_seconds(tso, replica) == pytest.approx(1.0)
    # lag never goes negative even when the sink reports a newer checkpoint
    assert tso_lag_seconds(replica, tso) == 0.0
    with pytest.raises(ValueError):
        tso_to_unix_ms(-1)


# v8.1 full changefeed query payload (live-verified snake_case keys)
_CLI_PAYLOAD = {
    "checkpoint_tso": (1_700_000_000_000 << 18) | 1,
    "resolved_ts": (1_700_000_000_500 << 18) | 2,
    "state": "normal",
}


def test_changefeed_checkpoint_sampler():
    calls: list[list[str]] = []

    def cli_runner(args: list[str]) -> str:
        calls.append(args)
        return json.dumps(_CLI_PAYLOAD)

    sampler = CdcChangefeedCheckpointSampler(service_id="cdc-orders", changefeed_id="orders-feed", cli_runner=cli_runner)
    sample = sampler.sample(1)
    assert sampler.checkpoint() == _CLI_PAYLOAD
    assert calls[0][:4] == ["/cdc", "cli", "changefeed", "query"]
    assert "--changefeed-id" in calls[0] and "orders-feed" in calls[0]
    assert "--simple" not in calls[0]
    assert sample.primary_watermark == str((1_700_000_000_500 << 18) | 2)
    assert sample.replica_watermark == str((1_700_000_000_000 << 18) | 1)
    assert sample.lag_seconds == pytest.approx(0.5)
    assert sample.detail["state"] == "normal"


def test_freshness_recorder_stamps_clock_and_appends(tmp_path):
    ledger = TrustedLedger("fresh-test", tmp_path / "fresh-ledger.jsonl")
    clock = FakeClock(start=42.0)

    def sample(sequence: int):
        return CdcChangefeedCheckpointSampler(
            service_id="cdc-orders",
            changefeed_id="orders-feed",
            cli_runner=lambda args: json.dumps(_CLI_PAYLOAD),
        ).sample(sequence)

    recorder = TiDBFreshnessRecorder(service_id="cdc-orders", ledger=ledger, clock=clock, sample=sample, interval_seconds=1.0)
    recorded = recorder.record_once()
    assert recorded.sampled_at_monotonic == 42.0
    assert recorded.sample_id.endswith("-1")
    ledger.seal()
    samples = LedgerView(ledger).freshness_samples()
    assert len(samples) == 1
    assert samples[0].lag_seconds == pytest.approx(0.5)


def test_freshness_recorder_loop_and_stop(tmp_path):
    ledger = TrustedLedger("fresh-loop", tmp_path / "fresh-loop-ledger.jsonl")
    clock = RealClock()
    sequence_seen: list[int] = []
    done = threading.Event()

    def sample(sequence: int):
        sequence_seen.append(sequence)
        done.set()
        return CdcChangefeedCheckpointSampler(
            service_id="cdc-orders",
            changefeed_id="orders-feed",
            cli_runner=lambda args: json.dumps(_CLI_PAYLOAD),
        ).sample(sequence)

    recorder = TiDBFreshnessRecorder(service_id="cdc-orders", ledger=ledger, clock=clock, sample=sample, interval_seconds=0.05)
    recorder.start()
    with pytest.raises(RuntimeError, match="already started"):
        recorder.start()
    assert done.wait(5), "recorder loop did not sample"
    recorder.stop()
    # stopping twice is idempotent
    recorder.stop()
    assert sequence_seen  # the loop recorded at least one sample


def test_freshness_recorder_surfaces_sampling_error(tmp_path):
    ledger = TrustedLedger("fresh-error", tmp_path / "fresh-error-ledger.jsonl")
    clock = RealClock()

    def sample(sequence: int):
        raise RuntimeError("cdc cli failed: connection refused")

    recorder = TiDBFreshnessRecorder(service_id="cdc-orders", ledger=ledger, clock=clock, sample=sample, interval_seconds=0.05)
    recorder.start()
    deadline = time.monotonic() + 5
    while recorder._thread.is_alive():
        if time.monotonic() > deadline:
            raise AssertionError("recorder thread did not stop after error")
        time.sleep(0.01)
    with pytest.raises(RuntimeError, match="cdc cli failed"):
        recorder.stop()
