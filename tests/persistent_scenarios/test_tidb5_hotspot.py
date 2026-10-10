"""Focused tests for the tidb_oltp_hotspot_resilience instance package."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import time

import pytest

from src.persistent_scenarios.backend.contracts import EventActivationContext, OwnershipMode
from src.persistent_scenarios.backend.tidb.capabilities.hotspot import CAPABILITIES, VERIFIERS
from src.persistent_scenarios.backend.tidb.capabilities.hotspot.capabilities import (
    LegacyClientReleaseCapability,
    PromoHotspotCapability,
    SettlementLongTxCapability,
    TikvCatchUpBurstCapability,
    TikvSlowThrottleCapability,
    released_config_version,
)
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.persistent_scenarios.model.spec import PersistentScenarioSpec
from src.persistent_scenarios.runtime.admission import admit_persistent_scenario
from src.persistent_scenarios.runtime.clock import RealClock
from src.persistent_scenarios.runtime.ledger import (
    AttemptOutcome,
    LedgerTerminal,
    LedgerView,
    TransactionAttempt,
    TrustedLedger,
)
from src.persistent_scenarios.tidb.hotspot.business import (
    BusinessRejected,
    DECREMENT_INVENTORY_SQL,
    INSERT_PAYMENT_SQL,
    PAY_ORDER_SQL,
    PLACE_ORDER_SQL,
    RECONCILE_ORDER_SQL,
    STOCK_READ_SQL,
    classify_pymysql_error,
)
from src.persistent_scenarios.tidb.hotspot.control import READ_CLIENT_POLICY_SQL
from src.persistent_scenarios.tidb.hotspot.schema import CLIENT_CONFIG_DDL, initial_client_config_statement
from src.persistent_scenarios.tidb.hotspot.driver import (
    DriverConfig,
    HotspotWorkloadDriver,
    TrafficPlan,
    TrafficTier,
    _NEGATIVE_INVENTORY_SQL,
    order_identifier,
    PAID_WITHOUT_PAYMENT_PROBE_SQL,
)
from src.persistent_scenarios.tidb.hotspot.control import ClientPolicy, validate_policy_transition
from src.persistent_scenarios.tidb.hotspot.verifiers import (
    commerce_ledger_conservation,
    orders_idempotency_uniqueness,
    unknown_commit_dedup,
)

from .tidb5_fakes import (
    FakeConnectionSource,
    FakeTiDBPort,
    FakeWorkloadDriver,
    Registry,
    ScriptedConnection,
    exact_responder,
)

WORKTREE = Path(__file__).resolve().parents[2]
HOTSPOT_YAML = WORKTREE / "src" / "persistent_scenarios" / "tidb" / "tidb_oltp_hotspot_resilience.yaml"


def _registry() -> "Registry":
    from .tidb5_fakes import Registry

    return Registry({capability.capability_id: capability for capability in CAPABILITIES})


def _event(spec: PersistentScenarioSpec, event_id: str):
    return [item for item in spec.events if item.event_id == event_id][0]


class _SqlConn:
    """A read-only trusted connection fake running over a scripted responder."""

    def __init__(self, responder) -> None:
        self._connection = ScriptedConnection(responder, "verifier")

    def cursor(self):
        return self._connection.cursor()

    def commit(self):
        return None


def _class_backend():
    class Backend:
        def validate_spec(self, spec) -> None:
            return None

    return Backend()


def test_hotspot_spec_passes_static_and_capability_admission() -> None:
    spec = load_persistent_scenario(HOTSPOT_YAML)
    admit_persistent_scenario(spec, _class_backend(), _registry())


def test_hotspot_whole_window_budget_stays_at_calibrated_freeze() -> None:
    """The honest complete repair cannot reach 0.90 through the designed
    throttle+burst window — three reference samples span 0.565 / 0.575 /
    0.5783 whole-window trade SLA. 0.54 = worst reference minus a 2.5pp
    margin; post-recovery health is enforced by trade_continuity and
    commerce conservation, which stay at their contract values."""
    spec = load_persistent_scenario(HOTSPOT_YAML)
    by_id = {objective.objective_id: objective for objective in spec.services}
    assert by_id["trade_good_fraction"].min_success_fraction == 0.54
    continuity = {check.check_id: check for check in spec.required_state}
    assert continuity["trade_continuity"].min_success_fraction == 0.90


def test_admission_rejects_overlapping_exclusive_store_throttles() -> None:
    spec = load_persistent_scenario(HOTSPOT_YAML)
    # A second throttle occurrence on the same store with an overlapping
    # activation window, keeping the non-decreasing start_seconds invariant.
    duplicate = replace(_event(spec, "tikv_slow_throttle_1"), event_id="tikv_slow_throttle_conflict",
                        start_seconds=1085)
    rebuilt_events = tuple(sorted(
        tuple(event for event in spec.events if event.event_id not in {"settlement_long_tx_1", "tikv_throttle_release_1"})
        + (duplicate,),
        key=lambda item: item.start_seconds,
    ))
    rebuilt = replace(spec, events=rebuilt_events)
    with pytest.raises(Exception, match="exclusive ownership"):
        admit_persistent_scenario(rebuilt, _class_backend(), _registry())


def test_slow_throttle_applies_reversibly_with_hot_region_proof() -> None:
    port = FakeTiDBPort(leader_distribution={"tikv/tikv-1": 4, "tikv/tikv-0": 2, "tikv/tikv-2": 2})
    spec = load_persistent_scenario(HOTSPOT_YAML)
    event = _event(spec, "tikv_slow_throttle_1")
    capability = TikvSlowThrottleCapability()

    declaration = capability.declaration(event)
    assert declaration.capability_id == "tikv_slow_throttle"
    assert declaration.resources[0].mode is OwnershipMode.EXCLUSIVE
    assert declaration.max_activation_seconds <= event.activation_timeout_seconds

    result = capability.activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert result.applied is not None and result.prevented is None
    assert result.applied.facts["throttled_to_max_bytes_per_sec"] == 1048576
    assert result.applied.facts["baseline_max_bytes_per_sec"] == 262144000
    assert result.applied.facts["leader_distribution"]["tikv/tikv-1"] == 4

    capability.cleanup(result.handle)
    assert port.io_limits["tikv/tikv-1"] == 262144000
    assert capability.assert_clean(result.handle)["clean"] is True


def test_slow_throttle_rejects_store_not_carrying_the_hot_table() -> None:
    port = FakeTiDBPort(leader_distribution={"tikv/tikv-0": 8})
    spec = load_persistent_scenario(HOTSPOT_YAML)
    event = _event(spec, "tikv_slow_throttle_1")
    with pytest.raises(RuntimeError, match="does not carry any leader region"):
        TikvSlowThrottleCapability().activate(EventActivationContext(
            run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
        ))


def test_long_tx_session_is_observable_and_killed_on_cleanup() -> None:
    statements: list[str] = []

    def control_responder(sql: str, _args):
        statements.append(sql)
        if "CONNECTION_ID()" in sql:
            return (((77,),), 1)
        if "settlement_paused" in sql:
            return (((0,),), 1)
        if "TIDB_TRX" in sql:
            killed = any(str(statement).startswith("KILL 77") for statement in statements)
            return ((), 0) if killed else (((77,),), 1)
        if "FOR UPDATE" in sql:
            return (((2000,),), 1)
        return ((), 0)

    port = FakeTiDBPort(control_responder=control_responder)
    spec = load_persistent_scenario(HOTSPOT_YAML)
    event = _event(spec, "settlement_long_tx_1")
    capability = SettlementLongTxCapability()

    result = capability.activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert result.applied is not None
    assert result.applied.facts["connection_id"] == 77
    assert result.applied.facts["holding_sku"] == "SKU-0000"
    assert result.applied.facts["batch_legs"] == 4

    capability.cleanup(result.handle)
    assert any(str(sql).startswith("KILL 77") for sql, _args in [(s, None) for s in statements])
    assert capability.assert_clean(result.handle)["clean"] is True


def test_settlement_batch_honors_the_pause_and_stops_after_the_current_leg() -> None:
    """The documented ops.client_config.settlement_paused lever is the batch's
    resolution mechanism: the current leg finishes its business attempt, and
    no further leg starts. This is the complete-path check for the wave-2
    coupling ("resolve settlement residual before/early in wave 2")."""
    reads = {"pause": 0}
    statements: list[str] = []

    def control_responder(sql: str, _args):
        statements.append(sql)
        if "CONNECTION_ID()" in sql:
            return (((77,),), 1)
        if "settlement_paused" in sql:
            reads["pause"] += 1
            # unpaused at the first leg start, published pause afterwards
            return (((0,),), 1) if reads["pause"] == 1 else (((1,),), 1)
        if "TIDB_TRX" in sql:
            killed = any(str(statement).startswith("KILL") for statement in statements)
            return ((), 0) if killed else (((77,),), 1)
        if "FOR UPDATE" in sql:
            return (((2000,),), 1)
        return ((), 0)

    port = FakeTiDBPort(control_responder=control_responder)
    spec = load_persistent_scenario(HOTSPOT_YAML)
    event = _event(spec, "settlement_long_tx_1")
    event = replace(event, payload={
        "queue": ["SKU-0000", "SKU-0012"], "hold_seconds": 0.2, "leg_gap_seconds": 0.05,
    })
    capability = SettlementLongTxCapability()

    result = capability.activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert result.applied is not None

    deadline = time.monotonic() + 5.0
    handle = result.handle
    while time.monotonic() < deadline and handle.paused_at_leg is None:
        time.sleep(0.01)
    assert handle.paused_at_leg == 1, (handle.leg_index, handle.leg_failures)
    assert handle.batch_exhausted is False
    assert handle.leg_failures == ()
    # Only leg 1 opened a session: the paused batch never touches the wave-2 row.
    assert handle.connection_ids == (77,)

    capability.cleanup(handle)
    assert capability.assert_clean(handle)["clean"] is True


def test_preventive_pause_publication_is_reported_as_prevented_evidence() -> None:
    """A preventive pause published before the settlement event arrives is a
    legitimate agent action (prevention is not an arrival failure): the batch
    never opens a session and the activation reports prevented evidence via
    the settlement_batch_paused mechanism."""
    statements: list[str] = []

    def control_responder(sql: str, _args):
        statements.append(sql)
        if "settlement_paused" in sql:
            return (((1,),), 1)
        return ((), 0)

    port = FakeTiDBPort(control_responder=control_responder)
    spec = load_persistent_scenario(HOTSPOT_YAML)
    event = _event(spec, "settlement_long_tx_1")
    result = SettlementLongTxCapability().activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert result.applied is None and result.prevented is not None
    assert result.prevented.mechanism == "settlement_batch_paused"
    assert result.handle.connection_ids == ()


def test_settlement_batch_survives_session_kills_without_the_pause() -> None:
    """Killing the current settlement session does not resolve the residual:
    the batch client reconnects and continues its queue, so the wave-2 hot row
    is still held when the second wave arrives (the violated check: the
    settlement residual stays unresolved through wave 2)."""
    connection_counter = {"next": 77}
    leg_index = {"touch": 0}
    statements: list[str] = []

    def control_responder(sql: str, _args):
        statements.append(sql)
        if "CONNECTION_ID()" in sql:
            issued = connection_counter["next"]
            connection_counter["next"] += 1
            return (((issued,),), 1)
        if "settlement_paused" in sql:
            return (((0,),), 1)
        if "TIDB_TRX" in sql:
            killed = any(str(statement).startswith("KILL") for statement in statements)
            return ((), 0) if killed else (((connection_counter["next"] - 1,),), 1)
        if "FOR UPDATE" in sql:
            import pymysql

            leg_index["touch"] += 1
            if leg_index["touch"] == 2:
                # the agent's KILL landed on the second leg's session
                raise pymysql.err.OperationalError(2013, "lost connection")
            return (((2000,),), 1)
        return ((), 0)

    port = FakeTiDBPort(control_responder=control_responder)
    spec = load_persistent_scenario(HOTSPOT_YAML)
    event = _event(spec, "settlement_long_tx_1")
    event = replace(event, payload={
        "queue": ["SKU-0000", "SKU-0012", "SKU-0012"], "hold_seconds": 0.1, "leg_gap_seconds": 0.02,
    })
    capability = SettlementLongTxCapability()

    result = capability.activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))

    handle = result.handle
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and len(handle.connection_ids) < 3:
        time.sleep(0.01)
    assert len(handle.connection_ids) == 3, (handle.connection_ids, handle.leg_failures)
    assert handle.connection_ids == (77, 78, 79)
    assert len(handle.leg_failures) == 1
    assert handle.leg_failures[0]["leg_index"] == 1
    assert handle.paused_at_leg is None

    capability.cleanup(handle)
    assert capability.assert_clean(handle)["clean"] is True


def test_settlement_queue_overlaps_wave_2_hot_rows_when_unresolved() -> None:
    """The coupling exists mechanically: the unpaused batch's leg schedule
    holds a promo wave-2 hot row (SKU-0012 is in promo group B) well into the
    second wave, so wave-2 trades hit the lock chain through the residual."""
    from src.persistent_scenarios.tidb.hotspot.schema import PROMO_GROUP_B

    spec = load_persistent_scenario(HOTSPOT_YAML)
    settlement = _event(spec, "settlement_long_tx_1")
    wave_2 = _event(spec, "promo_wave_2")
    legs = [str(sku) for sku in settlement.payload["queue"]]
    hold = float(settlement.payload["hold_seconds"])
    gap = float(settlement.payload["leg_gap_seconds"])
    start = float(settlement.start_seconds)
    windows = [(legs[i], start + i * (hold + gap), start + i * (hold + gap) + hold) for i in range(len(legs))]

    overlapping = [
        (sku, leg_start, leg_end)
        for sku, leg_start, leg_end in windows
        if sku in PROMO_GROUP_B and leg_start < wave_2.start_seconds + 600 and leg_end > wave_2.start_seconds
    ]
    assert overlapping, f"settlement queue does not couple with promo wave 2: windows={windows!r}"
    assert any(leg_end - wave_2.start_seconds >= 300 for _sku, _leg_start, leg_end in overlapping)


def test_promo_capability_switches_tier_per_entity() -> None:
    port = FakeTiDBPort(workload_driver=FakeWorkloadDriver())
    spec = load_persistent_scenario(HOTSPOT_YAML)
    capability = PromoHotspotCapability()
    for event_id in ("promo_wave_1", "promo_wave_2"):
        event = _event(spec, event_id)
        result = capability.activate(EventActivationContext(
            run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
        ))
        assert result.applied is not None
        assert result.applied.facts["tier"] == event.payload["tier"]
    assert port.workload().tiers == ["promo_a", "promo_b"]


def test_legacy_client_release_is_prevented_by_client_validation() -> None:
    rejected = ({"published_version": "2", "reason": "unsafe policy"},)
    port = FakeTiDBPort(workload_driver=FakeWorkloadDriver(applied_version=1, rejected=rejected))
    spec = load_persistent_scenario(HOTSPOT_YAML)
    event = _event(spec, "legacy_client_release_1")
    result = LegacyClientReleaseCapability().activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert result.applied is None and result.prevented is not None
    assert result.prevented.mechanism == "client_config_validation"
    assert result.prevented.protection_state["rejections"][0]["published_version"] == "2"


def test_client_policy_validation_rejects_stale_versions() -> None:
    previous = ClientPolicy(2, 3000, 3, 100, 50, 60, None, 8, None, 0)
    stale = ClientPolicy(1, 3000, 3, 100, 50, 60, None, 8, None, 0)
    with pytest.raises(ValueError, match="strictly increase"):
        validate_policy_transition(previous, stale)


_ORDERS_SQL = "SELECT order_id, sku, qty, amount_cents, status, idempotency_key FROM shop.orders"
_PAYMENTS_SQL = "SELECT order_id, amount_cents FROM shop.payments"
_INVENTORY_SQL = "SELECT sku, qty_available FROM shop.inventory"


def test_commerce_conservation_verifier_cross_checks_ledger_and_db(tmp_path: Path) -> None:
    ledger = TrustedLedger("trade", tmp_path / "trade.jsonl")
    ledger.append_planned_transaction(
        business_id="o1", service_id="trade", tx_kind="place_order",
        planned_at_monotonic=0.0, deadline_at_monotonic=10.0,
    )
    ledger.append_transaction_attempt(
        business_id="o1",
        attempt=TransactionAttempt(0, 0.1, 0.5, AttemptOutcome.COMMITTED, {
            "order_id": "o1", "sku": "SKU-0000", "qty": 2, "amount_cents": 2000,
        }),
    )
    ledger.append_transaction_terminal(
        business_id="o1", terminal=LedgerTerminal.COMPLETED,
        completed_at_monotonic=0.5, result_digest="order:o1:SKU-0000:2:2000",
    )
    view = LedgerView(ledger)

    inventory_rows = tuple((f"SKU-{index:04d}", 2000) for index in range(20))
    inventory_rows = (("SKU-0000", 1998),) + inventory_rows[1:]
    responder = exact_responder({
        _ORDERS_SQL: (("o1", "SKU-0000", 2, 2000, "placed", "o1"),),
        _PAYMENTS_SQL: (),
        _INVENTORY_SQL: inventory_rows,
    })
    result = commerce_ledger_conservation(None, _SqlConn(responder), view, {})
    assert result["passed"] is True, result["failures"]

    broken_inventory = (("SKU-0000", 1990),) + inventory_rows[1:]
    broken_responder = exact_responder({
        _ORDERS_SQL: (("o1", "SKU-0000", 2, 2000, "placed", "o1"),),
        _PAYMENTS_SQL: (),
        _INVENTORY_SQL: broken_inventory,
    })
    broken = commerce_ledger_conservation(None, _SqlConn(broken_responder), view, {})
    assert broken["passed"] is False
    assert any("inventory conservation" in failure for failure in broken["failures"])


def test_unknown_commit_dedup_flags_rows_without_completion(tmp_path: Path) -> None:
    ledger = TrustedLedger("trade", tmp_path / "trade.jsonl")
    ledger.append_planned_transaction(
        business_id="o9", service_id="trade", tx_kind="place_order",
        planned_at_monotonic=0.0, deadline_at_monotonic=10.0,
    )
    ledger.append_transaction_attempt(
        business_id="o9",
        attempt=TransactionAttempt(0, 0.1, 0.5, AttemptOutcome.TIMED_OUT, {"uncertain_commit": True}),
    )
    ledger.append_transaction_terminal(
        business_id="o9", terminal=LedgerTerminal.INCOMPLETE_OUTSTANDING,
        completed_at_monotonic=None, result_digest=None,
    )
    view = LedgerView(ledger)
    responder = exact_responder({
        _ORDERS_SQL: (("o9", "SKU-0000", 1, 1000, "placed", "o9"),),
    })
    result = unknown_commit_dedup(None, _SqlConn(responder), view, {})
    assert result["passed"] is False
    assert any("did not complete" in failure for failure in result["failures"])


def test_idempotency_uniqueness_detects_duplicate_keys(tmp_path: Path) -> None:
    ledger = TrustedLedger("trade", tmp_path / "trade.jsonl")
    ledger.append_planned_transaction(
        business_id="o1", service_id="trade", tx_kind="place_order",
        planned_at_monotonic=0.0, deadline_at_monotonic=10.0,
    )
    ledger.append_transaction_terminal(
        business_id="o1", terminal=LedgerTerminal.INCOMPLETE_ERROR,
        completed_at_monotonic=None, result_digest=None,
    )
    view = LedgerView(ledger)
    responder = exact_responder({
        "SELECT idempotency_key, COUNT(*) FROM shop.orders GROUP BY idempotency_key HAVING COUNT(*) > 1": (
            ("o1", 2),
        ),
        _ORDERS_SQL: (
            ("o1", "SKU-0000", 1, 1000, "placed", "o1"),
            ("o1-dup", "SKU-0000", 1, 1000, "placed", "o1"),
        ),
    })
    result = orders_idempotency_uniqueness(None, _SqlConn(responder), view, {})
    assert result["passed"] is False
    assert result["duplicate_keys"] == 1


def test_verifier_registry_matches_implemented_verifier_ids() -> None:
    ids = [verifier_id for verifier_id, _callable in VERIFIERS]
    assert set(ids) == {"commerce_ledger_conservation", "orders_idempotency_uniqueness", "unknown_commit_dedup"}


def test_business_rejection_is_not_retryable() -> None:
    outcome, retryable = classify_pymysql_error(BusinessRejected("insufficient inventory"))
    assert outcome.value == "aborted" and retryable is False


def test_driver_stop_finalizes_only_ledger_transactions(tmp_path: Path) -> None:
    """Stock reads are observations: drain must not wait on them and stop must
    never finalize them as ledger terminals."""
    control = exact_responder({
        READ_CLIENT_POLICY_SQL: ((1, 500, 3, 100, 50, 900, None, 8, None, 0),),
        PAID_WITHOUT_PAYMENT_PROBE_SQL: ((0,),),
        _NEGATIVE_INVENTORY_SQL: ((0,),),
    })

    class Source(FakeConnectionSource):
        def connect(self, policy):
            return ScriptedConnection(exact_responder({
                PLACE_ORDER_SQL: ((1,),),
                DECREMENT_INVENTORY_SQL: ((1,),),
                PAY_ORDER_SQL: ((1,),),
                INSERT_PAYMENT_SQL: ((1,),),
                STOCK_READ_SQL: ((7,),),
            }), f"conn-v{policy.config_version}")

    ledger = TrustedLedger("trade", tmp_path / "trade.jsonl")
    driver = HotspotWorkloadDriver(
        service_id="trade",
        ledger=ledger,
        clock=RealClock(),
        connection_source=Source(control),
        plan=TrafficPlan(tiers=(TrafficTier("normal", 4.0, 6.0, ("SKU-0001", "SKU-0002")),)),
        config=DriverConfig(pool_size=2, deadline_seconds=5.0, control_poll_seconds=0.05,
                            pay_lag_seconds=0.05, integrity_probe_interval_seconds=0.2),
        run_id="drvtest",
        scoring_origin=time.monotonic() + 0.2,
        input_stop_seconds=0.8,
        normal_sku_count=20,
    )
    driver.start()
    driver.wait_for_warmup()
    time.sleep(1.6)
    summary = driver.stop()

    ledger.seal()
    ledger.verify()
    records = LedgerView(ledger).logical_transactions()
    assert records
    assert all(record.tx_kind in {"place_order", "pay_order"} for record in records)
    assert all(record.terminal is not None for record in records)
    assert any(record.terminal is LedgerTerminal.COMPLETED for record in records)
    assert summary["stock_reads"]


def test_driver_incomplete_trade_reaches_ledger_terminal(tmp_path: Path) -> None:
    """An uncertain-commit trade that exhausts its deadline must land an
    incomplete_timeout terminal in the ledger and keep the worker alive
    (reason strings passed as result_digest kill workers)."""
    import pymysql

    control = exact_responder({
        READ_CLIENT_POLICY_SQL: ((1, 500, 3, 100, 50, 900, None, 8, None, 0),),
        PAID_WITHOUT_PAYMENT_PROBE_SQL: ((0,),),
        _NEGATIVE_INVENTORY_SQL: ((0,),),
        RECONCILE_ORDER_SQL: ((0,),),
    })

    def respond(sql: str, args):
        if sql == PLACE_ORDER_SQL and args[1] == "SKU-0002":
            raise pymysql.err.OperationalError(2013, "lost connection")
        rows = {
            PLACE_ORDER_SQL: ((1,),),
            DECREMENT_INVENTORY_SQL: ((1,),),
            PAY_ORDER_SQL: ((1,),),
            INSERT_PAYMENT_SQL: ((1,),),
            STOCK_READ_SQL: ((7,),),
        }.get(sql, ())
        return rows, len(rows)

    class Source(FakeConnectionSource):
        def connect(self, policy):
            return ScriptedConnection(respond, f"conn-v{policy.config_version}")

    ledger = TrustedLedger("trade", tmp_path / "trade.jsonl")
    driver = HotspotWorkloadDriver(
        service_id="trade",
        ledger=ledger,
        clock=RealClock(),
        connection_source=Source(control),
        plan=TrafficPlan(tiers=(TrafficTier("normal", 4.0, 6.0, ("SKU-0001", "SKU-0002")),)),
        config=DriverConfig(pool_size=2, deadline_seconds=2.0, control_poll_seconds=0.05,
                            pay_lag_seconds=0.05, integrity_probe_interval_seconds=0.2),
        run_id="drvtest2",
        scoring_origin=time.monotonic() + 0.2,
        input_stop_seconds=1.2,
        normal_sku_count=20,
    )
    driver.start()
    driver.wait_for_warmup()
    time.sleep(2.4)
    driver.stop()

    ledger.seal()
    ledger.verify()
    records = LedgerView(ledger).logical_transactions()
    incomplete = [record for record in records if record.terminal is not LedgerTerminal.COMPLETED]
    assert incomplete
    assert all(record.terminal in {LedgerTerminal.INCOMPLETE_TIMEOUT, LedgerTerminal.INCOMPLETE_ERROR}
               for record in incomplete)
    failed_orders = {record.business_id for record in incomplete if record.tx_kind == "place_order"}
    assert {f"{order}:pay" for order in failed_orders} <= {
        record.business_id for record in incomplete if record.tx_kind == "pay_order"
    }
    assert any(record.terminal is LedgerTerminal.COMPLETED for record in records)


def test_commerce_verifier_scopes_declared_trusted_probe_orders(tmp_path: Path) -> None:
    """Mechanism-evidence probes write business rows outside the workload
    ledger. Declaring their id prefix keeps them DB-verified (they still
    consume inventory and stay checked for paid/uniqueness consistency)
    while unexplained rows keep failing."""
    ledger = TrustedLedger("trade", tmp_path / "trade.jsonl")
    ledger.append_planned_transaction(
        business_id="o1", service_id="trade", tx_kind="place_order",
        planned_at_monotonic=0.0, deadline_at_monotonic=10.0,
    )
    ledger.append_transaction_attempt(
        business_id="o1",
        attempt=TransactionAttempt(0, 0.1, 0.5, AttemptOutcome.COMMITTED, {
            "order_id": "o1", "sku": "SKU-0000", "qty": 2, "amount_cents": 2000,
        }),
    )
    ledger.append_transaction_terminal(
        business_id="o1", terminal=LedgerTerminal.COMPLETED,
        completed_at_monotonic=0.5, result_digest="order:o1:SKU-0000:2:2000",
    )
    view = LedgerView(ledger)

    inventory_rows = tuple((f"SKU-{index:04d}", 2000) for index in range(20))
    inventory_rows = (("SKU-0000", 1997),) + inventory_rows[1:]
    responder = exact_responder({
        _ORDERS_SQL: (
            ("o1", "SKU-0000", 2, 2000, "placed", "o1"),
            ("probe-1", "SKU-0000", 1, 1000, "placed", "probe-1"),
        ),
        _PAYMENTS_SQL: (),
        _INVENTORY_SQL: inventory_rows,
    })
    scoped = commerce_ledger_conservation(None, _SqlConn(responder), view, {"trusted_order_id_prefixes": ["probe-"]})
    assert scoped["passed"] is True, scoped["failures"]
    unscoped = commerce_ledger_conservation(None, _SqlConn(responder), view, {})
    assert unscoped["passed"] is False
    assert any("ledger never committed" in failure for failure in unscoped["failures"])


def test_catch_up_burst_applies_bounded_squeeze_and_cleanup_restores() -> None:
    port = FakeTiDBPort(leader_distribution={"tikv/tikv-1": 4, "tikv/tikv-0": 2, "tikv/tikv-2": 2})
    spec = load_persistent_scenario(HOTSPOT_YAML)
    event = _event(spec, "tikv_catch_up_burst_1")
    capability = TikvCatchUpBurstCapability()

    declaration = capability.declaration(event)
    assert declaration.capability_id == "tikv_catch_up_burst"
    assert declaration.resources[0].resource_key == "container:tikv/tikv-1:cpu"
    assert declaration.resources[0].mode is OwnershipMode.EXCLUSIVE
    assert declaration.max_activation_seconds <= event.activation_timeout_seconds

    result = capability.activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert result.applied is not None and result.prevented is None
    assert port.cpu_limits["tikv/tikv-1"] == 0.45
    assert result.applied.facts["baseline_cpus"] == 1.0
    assert result.applied.facts["burst_cpu_limit"] == 0.45
    assert result.applied.facts["burst_seconds"] == 420
    # The applied facts carry the coupling condition: the burst store still
    # carries hot-region leaders at burst time.
    assert result.applied.facts["hot_leaders_on_target"] == 4

    capability.cleanup(result.handle)
    assert port.cpu_limits["tikv/tikv-1"] == 1.0
    assert capability.assert_clean(result.handle)["clean"] is True


def test_catch_up_burst_auto_restores_after_the_bounded_window() -> None:
    port = FakeTiDBPort()
    spec = load_persistent_scenario(HOTSPOT_YAML)
    event = _event(spec, "tikv_catch_up_burst_1")
    event = replace(event, payload={"target": "tikv/tikv-1", "cpu_limit": 0.45, "burst_seconds": 0.1})
    capability = TikvCatchUpBurstCapability()

    result = capability.activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert port.cpu_limits["tikv/tikv-1"] == 0.45
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and port.cpu_limits["tikv/tikv-1"] != 1.0:
        time.sleep(0.01)
    assert port.cpu_limits["tikv/tikv-1"] == 1.0
    capability.cleanup(result.handle)  # idempotent after the auto-restore
    assert capability.assert_clean(result.handle)["clean"] is True


def test_catch_up_burst_re_degrades_only_while_hot_leaders_stay_on_target() -> None:
    """The burst is store-physical: it hits the previously throttled store.
    The hot region suffers only while its leaders remain concentrated there —
    a release without leader/load rebalancing keeps the coupling condition
    true, a completed rebalance breaks it."""
    spec = load_persistent_scenario(HOTSPOT_YAML)
    event = _event(spec, "tikv_catch_up_burst_1")
    capability = TikvCatchUpBurstCapability()

    concentrated = FakeTiDBPort(leader_distribution={"tikv/tikv-1": 6, "tikv/tikv-0": 1, "tikv/tikv-2": 1})
    result_concentrated = capability.activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=concentrated, clock=RealClock(),
    ))
    capability.cleanup(result_concentrated.handle)

    rebalanced = FakeTiDBPort(leader_distribution={"tikv/tikv-0": 4, "tikv/tikv-2": 4})
    result_rebalanced = capability.activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=rebalanced, clock=RealClock(),
    ))
    capability.cleanup(result_rebalanced.handle)

    assert result_concentrated.applied.facts["hot_leaders_on_target"] == 6
    assert result_rebalanced.applied.facts["hot_leaders_on_target"] == 0


def test_release_version_is_a_floor_above_agent_publications() -> None:
    """The planned release version is a floor, not a static identity: agent
    publications of the documented levers (order_id_prefix, settlement_paused)
    raise the applied version, and the release must still land — without
    rolling an agent publication back (the UPDATE only rewrites retry
    columns)."""
    assert released_config_version(2, 1) == 2
    assert released_config_version(2, 5) == 6
    assert released_config_version(3, 3) == 4

    published: list[tuple] = []
    state = {"applied": 5}

    class AdoptingDriver(FakeWorkloadDriver):
        def applied_config_version(self) -> int:
            return state["applied"]

    def control_responder(sql: str, args):
        if sql.startswith("UPDATE ops.client_config"):
            published.append(args)
            state["applied"] = int(args[0])
            return ((), 1)
        return ((), 0)

    port = FakeTiDBPort(
        workload_driver=AdoptingDriver(applied_version=5),
        control_responder=control_responder,
    )
    spec = load_persistent_scenario(HOTSPOT_YAML)
    event = _event(spec, "legacy_client_release_1")
    result = LegacyClientReleaseCapability().activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert result.applied is not None
    assert result.applied.facts["config_version"] == 6
    assert published and int(published[0][0]) == 6


def test_client_config_declares_the_documented_lever_columns() -> None:
    """The documented application-config surface: order_id_prefix is the
    column-width compatible identifier lever (the legitimate repair path),
    settlement_paused is the settlement batch's resolution lever. Both are
    discoverable through the control-table schema and enforced by the
    driver-side publication validation."""
    from src.persistent_scenarios.tidb.hotspot.control import (
        ORDER_ID_COLUMN_LENGTH,
        ORDER_ID_PREFIX_MAX_LENGTH,
    )

    assert "order_id_prefix VARCHAR(16)" in CLIENT_CONFIG_DDL
    assert "settlement_paused TINYINT NOT NULL DEFAULT 0" in CLIENT_CONFIG_DDL
    assert "COMMENT" in CLIENT_CONFIG_DDL
    initial = initial_client_config_statement()
    assert "order_id_prefix" in initial and "settlement_paused" in initial
    assert (ORDER_ID_PREFIX_MAX_LENGTH, ORDER_ID_COLUMN_LENGTH) == (16, 64)

    previous = ClientPolicy(2, 3000, 3, 100, 50, 60, None, 8, None, 0)
    validate_policy_transition(previous, ClientPolicy(3, 3000, 3, 100, 50, 60, None, 8, "shop9", 1))
    with pytest.raises(ValueError, match="order_id_prefix must be 1..16"):
        validate_policy_transition(previous, ClientPolicy(3, 3000, 3, 100, 50, 60, None, 8, "x" * 17, 0))
    with pytest.raises(ValueError, match="order_id_prefix must be 1..16"):
        validate_policy_transition(previous, ClientPolicy(3, 3000, 3, 100, 50, 60, None, 8, "bad prefix!", 0))
    with pytest.raises(ValueError, match="settlement_paused must be 0 or 1"):
        validate_policy_transition(previous, ClientPolicy(3, 3000, 3, 100, 50, 60, None, 8, None, 2))


def test_order_identifier_honors_the_published_prefix() -> None:
    """A published prefix bounds generated order ids to the column width; the
    fallback deployment identifier is truncated to the same bound."""
    published = ClientPolicy(2, 3000, 3, 100, 50, 60, None, 8, "shop9", 0)
    legacy = ClientPolicy(1, 3000, 3, 100, 50, 60, None, 8, None, 0)

    order_id = order_identifier(published, "r", 42)
    assert order_id == "shop9-o00000042"
    assert len(order_id) <= 64

    long_run_id = "experiment-with-a-very-long-deployment-identifier-exceeding-the-column-width"
    truncated_id = order_identifier(legacy, long_run_id, 42)
    assert truncated_id == f"{long_run_id[:54]}-o00000042"
    assert len(truncated_id) <= 64
    # Ids stay unique across the run's sequence space under the same prefix.
    assert order_identifier(legacy, long_run_id, 43) != truncated_id
    # A short run id passes through untruncated.
    assert order_identifier(legacy, "short-run", 7) == "short-run-o00000007"
