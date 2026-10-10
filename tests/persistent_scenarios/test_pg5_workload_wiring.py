"""Workload assembly wiring tests: the create_runtime paths must resolve all
names and produce the right runtime/driver/ledger wiring without a database.

They cover cross-module wiring that static analysis alone does not reach.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.persistent_scenarios.api import build_postgres_backend
from src.persistent_scenarios.backend.postgres import backend as backend_module
from src.persistent_scenarios.backend.postgres.instance_adapter import InstanceWorkloadRuntime
from src.persistent_scenarios.model.loader import load_persistent_scenario


SCENARIO_ROOT = Path("src/persistent_scenarios/postgres")


class _FakeEnv:
    host = "localhost"
    port = 25399
    user = "postgres"
    password = "password"
    dbname = "testdb"


class _RecordingSource:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class _RecordingDriver:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def start(self):
        return None

    def wait_for_warmup(self):
        return 100.0

    def stop_new_requests(self):
        return None

    def drain(self):
        return None

    def stop(self):
        return None

    def ledgers(self):
        return {}

    def baseline_facts(self):
        return {}


@pytest.fixture()
def smoke_setup(tmp_path: Path, monkeypatch):
    spec = load_persistent_scenario(SCENARIO_ROOT / "pg_continuous_ops_smoke.yaml")
    backend = build_postgres_backend(spec, evidence_root=tmp_path)
    recorded: list[dict] = []

    def record_driver(**kwargs):
        recorded.append(kwargs)
        return _RecordingDriver(**kwargs)

    monkeypatch.setattr(backend_module, "TcpConnectionSource", lambda **kwargs: _RecordingSource(**kwargs))
    monkeypatch.setattr(
        "src.persistent_scenarios.backend.postgres.bindings.OltpWorkloadDriver", record_driver
    )
    return spec, backend, recorded


def test_smoke_create_runtime_wires_sources_driver_and_ledgers(smoke_setup):
    spec, backend, recorded = smoke_setup
    runtime = backend.workload.create_runtime(
        _FakeEnv(), spec, "run-wiring", clock=None, persistent_scenario_started=1000.0
    )

    assert isinstance(runtime, InstanceWorkloadRuntime)
    assert len(recorded) == 1
    driver_kwargs = recorded[0]
    assert driver_kwargs["run_id"] == "run-wiring"
    assert driver_kwargs["scoring_origin"] == 1000.0
    assert driver_kwargs["horizon_seconds"] == spec.horizon_seconds
    assert driver_kwargs["input_stop_seconds"] == spec.input_stop_seconds
    assert isinstance(driver_kwargs["source"], _RecordingSource)
    assert driver_kwargs["source"].kwargs["port"] == 25399

    ledgers = runtime.ledgers()
    assert set(ledgers) == {"commerce"}
    assert ledgers["commerce"].path.name == "ledger-commerce.jsonl"
    assert backend.state_facts._workload_runtime is runtime


def test_smoke_create_runtime_is_repeatable_per_run_id(smoke_setup):
    spec, backend, _ = smoke_setup
    first = backend.workload.create_runtime(
        _FakeEnv(), spec, "run-a", clock=None, persistent_scenario_started=0.0
    )
    second = backend.workload.create_runtime(
        _FakeEnv(), spec, "run-b", clock=None, persistent_scenario_started=0.0
    )

    assert first is not second
    assert first.trusted_ledger.path != second.trusted_ledger.path
    assert backend.state_facts._workload_runtime is second


def test_warehouse_create_runtime_wires_four_service_ledgers(tmp_path, monkeypatch):
    from src.persistent_scenarios.backend.postgres.workloads.warehouse_reporting.runtime import (
        SERVICE_IDS,
        WarehouseReportingRuntime,
    )

    spec = load_persistent_scenario(SCENARIO_ROOT / "pg_warehouse_batch_reporting.yaml")
    backend = build_postgres_backend(spec, evidence_root=tmp_path)
    recorded: list[dict] = []

    def record_runtime(**kwargs):
        recorded.append(kwargs)

        class _FakeRuntime:
            def start(self):
                return None

            def wait_for_warmup(self):
                return 100.0

            def stop_new_requests(self):
                return None

            def drain(self):
                return None

            def stop(self):
                return None

            def ledgers(self):
                return kwargs["ledgers"]

            def baseline_facts(self):
                return {}

        return _FakeRuntime()

    monkeypatch.setattr(
        "src.persistent_scenarios.backend.postgres.bindings.WarehouseReportingRuntime", record_runtime
    )
    runtime = backend.workload.create_runtime(
        _FakeEnv(), spec, "run-wh", clock=None, persistent_scenario_started=500.0
    )

    assert len(recorded) == 1
    kwargs = recorded[0]
    assert set(kwargs["ledgers"]) == set(SERVICE_IDS)
    assert kwargs["input_end_monotonic"] == 500.0 + spec.input_stop_seconds
    assert isinstance(runtime, WarehouseReportingRuntime) or type(runtime).__name__ == "_FakeRuntime"
    # the capability runtime provider resolves the assembled runtime
    capability = backend.capabilities.capability("pg5r_olap_batch_arrival")
    assert capability._runtime_provider() is runtime


def test_oltp_driver_wait_for_warmup_consumes_the_warmup_phase(tmp_path):
    """Regression: the driver must return the post-warmup instant, not its
    construction-time origin (otherwise the canonical timeline moves
    backwards)."""

    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ports import EvidenceLedgerFile
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.runtime import (
        DriverConfig,
        OltpWorkloadDriver,
    )
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.traffic import TrafficPlan, TrafficTier
    from src.persistent_scenarios.runtime.clock import FakeClock

    clock = FakeClock(start=1000.0 + 30.0)  # the real-time instant after warmup
    driver = OltpWorkloadDriver(
        source=None,
        clock=clock,
        evidence=EvidenceLedgerFile(tmp_path / "evidence.jsonl", "run-warmup"),
        plan=TrafficPlan(tiers=(TrafficTier("normal", 0.0, 1.0, 1.0, 10000),)),
        config=DriverConfig(pool_size=1),
        run_id="run-warmup",
        scoring_origin=1000.0,
        horizon_seconds=900.0,
        input_stop_seconds=800.0,
        warmup_seconds=30.0,
    )
    scoring_start = driver.wait_for_warmup()
    assert scoring_start == 1030.0


def test_instance_workload_runtime_translates_the_business_ledger_exactly_once(tmp_path):
    """Regression: cleanup calls stop() after the pre-evaluation drain already
    ran; the second drain must not replay the business ledger into the core
    trusted ledger (a double plan fails with 'is already planned in
    ledger')."""

    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ledger import (
        AttemptOutcome,
        BusinessLedger,
        OpKind,
    )
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ports import EvidenceLedgerFile
    from src.persistent_scenarios.runtime.ledger import TrustedLedger

    evidence = EvidenceLedgerFile(tmp_path / "evidence.jsonl", "run-once")
    business = BusinessLedger(evidence)
    business.plan("tx-1", OpKind.PLACE_ORDER.value, 1.0, 9.0, {"sku": "SKU-0001"})
    business.attempt("tx-1", 1.0, 2.0, AttemptOutcome.COMMITTED, "ok")
    business.terminal("tx-1", AttemptOutcome.COMMITTED, 2.0, "ok")

    class _Driver:
        def __init__(self):
            self.ledger = business
            self.stop_and_drain_calls = 0

        def stop_and_drain(self):
            self.stop_and_drain_calls += 1

    driver = _Driver()
    trusted = TrustedLedger("commerce", tmp_path / "trusted-commerce.jsonl")
    runtime = InstanceWorkloadRuntime(
        driver,
        trusted,
        evidence,
        transaction_service_id="orders",
        horizon_seconds=10.0,
        input_stop_seconds=8.0,
    )

    runtime.drain()  # engine _stop_before_evaluation
    runtime.stop()  # engine _cleanup

    assert driver.stop_and_drain_calls == 1
    assert trusted.event_count("planned_transaction") == 1
    assert trusted.event_count("transaction_attempt") == 1
    assert trusted.event_count("transaction_terminal") == 1


def test_oltp_driver_schedules_arrivals_inside_the_scoring_window(tmp_path):
    """Regression: the schedulers must anchor arrivals at the post-warmup
    origin; anchoring at the pre-warmup origin lands the compressed business
    window inside warmup and leaves the scoring window without traffic."""

    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ledger import OpKind
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ports import EvidenceLedgerFile
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.runtime import (
        DriverConfig,
        OltpWorkloadDriver,
    )
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.traffic import TrafficPlan, TrafficTier
    from src.persistent_scenarios.runtime.clock import FakeClock
    from tests.persistent_scenarios.pg5_oltp_fakes import ScriptedSource
    from tests.persistent_scenarios.test_pg5_business_priority import _trade_connection_factory

    clock = FakeClock(start=1000.0)
    driver = OltpWorkloadDriver(
        source=ScriptedSource(lambda app: _trade_connection_factory()),
        clock=clock,
        evidence=EvidenceLedgerFile(tmp_path / "evidence.jsonl", "run-anchor"),
        plan=TrafficPlan(tiers=(TrafficTier("normal", 0.0, 0.5, 0.1, 10000),)),
        config=DriverConfig(pool_size=1, control_poll_seconds=0.05, pay_lag_seconds=0.0),
        run_id="run-anchor",
        scoring_origin=1000.0,
        horizon_seconds=900.0,
        input_stop_seconds=28.0,
        warmup_seconds=30.0,
    )
    driver.start()
    import time

    while clock.monotonic() < 1059.0:
        clock.advance(1.0)
        time.sleep(0.005)
    driver.stop_new_requests()
    summary = driver.stop_and_drain()

    ops = driver.ledger.ops()
    place = [op for op in ops if op.flow_id == OpKind.PLACE_ORDER.value]
    assert place, "the business window must produce trade arrivals"
    assert all(op.scheduled_at >= 1030.0 for op in ops), "no arrival may land inside warmup"
    assert all(op.scheduled_at < 1058.0 for op in ops), "arrivals stop at the compressed input stop"
    assert summary.applied_config_versions
