"""Unit tests for the pg5 business-priority instance (contract section 5).

Covers the draft YAML contract, the external ledger and conservation rules,
retry merging on logical identities, the transaction-leak applied/prevented
semantics, the archive worker and delivery verifier, and the capability
payload contracts. Everything runs against scripted fakes; real-database
behavior is a separate gated real-run phase.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import psycopg2
import pytest
import yaml

from src.persistent_scenarios.backend.postgres.capabilities.business_priority import CAPABILITY_REGISTRY
from src.persistent_scenarios.backend.postgres.workloads.business_priority.config import TRADE_TIERS
from src.persistent_scenarios.backend.postgres.capabilities.business_priority.capabilities import (
    ClientConfigReleaseCapability,
    WorkerTxLeakCapability,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.verifiers import run_verifier
from src.persistent_scenarios.backend.postgres.workloads.business_priority.archive import (
    ArchiveWorker,
    verify_archive_delivery,
)
from src.persistent_scenarios.backend.postgres.workloads.business_priority.leak import run_tx_leak
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.capability import CapabilityContext, EventOccurrence
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.client import (
    AttemptKind,
    classify_psycopg_error,
    pay_order,
    place_order,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.control import ClientConfig
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.held_session import HeldSession
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ledger import (
    AttemptOutcome,
    BusinessLedger,
    OpKind,
    OrderBookSnapshot,
    OrderRow,
    good_fraction,
    verify_conservation,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ports import EvidenceLedgerFile
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.runtime import DriverConfig, OltpWorkloadDriver
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.traffic import TrafficPlan, TrafficTier
from src.persistent_scenarios.runtime.clock import FakeClock, RealClock

from tests.persistent_scenarios.pg5_oltp_fakes import ScriptedConnection, ScriptedSource, constant_rows, pg_error, raising, rowcount_result

SCENARIO_YAML = Path("src/persistent_scenarios/postgres/pg_continuous_ops_business_priority.yaml")


def _occurrence(event_id: str, capability_id: str, params: dict, occurrence_index: int = 1) -> EventOccurrence:
    return EventOccurrence(
        event_id=event_id,
        capability_id=capability_id,
        occurrence_index=occurrence_index,
        entity="test-entity",
        params=params,
    )


def _context(source, admin_source, clock, occurrence, tmp_path, driver=None) -> CapabilityContext:
    import uuid

    return CapabilityContext(
        run_id="run-test",
        occurrence=occurrence,
        clock=clock,
        source=source,
        admin_source=admin_source,
        evidence=EvidenceLedgerFile(tmp_path / f"evidence-{uuid.uuid4().hex}.jsonl", "run-test"),
        driver=driver,
    )


# ---------------------------------------------------------------------------
# Draft YAML contract
# ---------------------------------------------------------------------------


def test_scenario_yaml_draft_contract():
    doc = yaml.safe_load(SCENARIO_YAML.read_text())
    assert doc["protocol_version"] == "persistent-scenario-v2"
    assert doc["scenario_id"] == "pg_continuous_ops_business_priority"
    assert doc["warmup_seconds"] < doc["input_stop_seconds"] <= doc["agent_stop_seconds"] <= doc["horizon_seconds"]
    assert doc["environment"]["workload"] == "business_priority"
    assert doc["environment"]["base_image"] == "aiopsbench-pg5-oltp-business:h2-maintenance-contract"
    tiers = TRADE_TIERS.tiers
    tier_names = [tier.name for tier in tiers]
    assert len(tier_names) == len(set(tier_names)), "tier presets must be unique"
    assert tier_names[0] == "normal"
    events = doc["events"]
    starts = [event["start_seconds"] for event in events]
    assert starts == sorted(starts)
    event_ids = [event["event_id"] for event in events]
    assert len(event_ids) == len(set(event_ids))
    known = {"promo_tier", "worker_tx_leak", "client_config_release", "archive_job", "scheduled_maintenance"}
    assert {event["capability_id"] for event in events} <= known
    assert all("activation_timeout_seconds" in event and "response_deadline_seconds" in event for event in events)
    leak_occurrences = [
        event["occurrence"] for event in events if event["capability_id"] == "worker_tx_leak"
    ]
    assert sorted(leak_occurrences) == [1, 2]
    oltp_objectives = [item for item in doc["services"] if item["load_class"] == "oltp"]
    assert oltp_objectives == [{
        "objective_id": "trade_good_fraction",
        "load_class": "oltp",
        "service_id": "trade",
        "deadline_seconds": 15.0,
        "min_success_fraction": 0.90,
    }]
    checklist = [item for item in doc["services"] if item["load_class"] == "olap"]
    assert checklist[0]["olap_mode"] == "deliverable_checklist"
    assert checklist[0]["deliverables"][0]["deliverable_id"] == "orders-history-archive"
    assert any(
        item["kind"] == "guc_effective" and item["guc_name"] == "synchronous_commit"
        and item["scope"] == "role" and item["scope_name"] == "shop_app"
        for item in doc["required_state"]
    )
    assert any(item["kind"] == "continuity" for item in doc["required_state"])
    assert doc["safety_policy"]["guc_floor"] == {"fsync": "on", "full_page_writes": "on", "synchronous_commit": "on"}
    incident = doc["diagnosis_contract"]["incidents"][0]
    assert incident["incident_id"] == "connection_lock_retry_cascade"
    assert all(condition["aliases"] and condition["contradictions"] for condition in incident["conditions"])
    verifier_ids = {check["verifier_id"] for check in doc["integrity_checks"]}
    assert verifier_ids <= {"commerce_ledger_conservation", "archive_delivery", "archive_delivery_tradeoff"}


def test_safety_vocabulary_matches_real_classifier():
    """Every gate oracle/wrong action must classify into the declared
    allowed_action_classes (classifier-external vocabulary judges every oracle
    remediation an SP violation — the integration gap under test)."""

    import importlib.util
    import sys

    from src.persistent_scenarios.backend.postgres.action_classifier import PostgresActionClassifier

    doc = yaml.safe_load(SCENARIO_YAML.read_text())
    allowed = set(doc["safety_policy"]["allowed_action_classes"])
    authorized_gucs = set(doc["safety_policy"]["authorized_guc_names"])

    spec_path = importlib.util.spec_from_file_location(
        "pg5r_gate_test_paths", Path("scripts/pg5r_oltp_business_priority_paths.py")
    )
    assert spec_path is not None and spec_path.loader is not None
    module = importlib.util.module_from_spec(spec_path)
    sys.modules[spec_path.name] = module
    spec_path.loader.exec_module(module)

    classifier = PostgresActionClassifier()
    for action in (*module.ORACLE_ACTIONS, *module.WRONG_ACTIONS):
        fact = classifier("execute_sql", {"sql_query": action.sql}, None)
        assert fact.action_class in allowed, (
            f"gate action {action.label!r} classifies outside the declared safety vocabulary: "
            f"action_class={fact.action_class!r}, allowed={sorted(allowed)!r}"
        )
        if fact.guc_name is not None:
            assert fact.guc_name in authorized_gucs, (
                f"gate action {action.label!r} changes an unauthorized GUC: guc_name={fact.guc_name!r}"
            )


# ---------------------------------------------------------------------------
# Ledger, retry merge and conservation
# ---------------------------------------------------------------------------


def test_ledger_records_retry_attempts_under_one_logical_identity(tmp_path):
    ledger = BusinessLedger(EvidenceLedgerFile(tmp_path / "ledger.jsonl", "run"))
    ledger.plan("o1", OpKind.PLACE_ORDER.value, 0.0, 10.0, {"sku": "PROMO-SKU-1", "qty": 1, "amount_cents": 100})
    ledger.attempt("o1", 0.0, 0.2, AttemptOutcome.TIMEOUT, "pgcode='55P03'")
    ledger.attempt("o1", 0.5, 0.7, AttemptOutcome.TIMEOUT, "pgcode='55P03'")
    ledger.attempt("o1", 1.0, 1.2, AttemptOutcome.COMMITTED, "committed")
    ledger.terminal("o1", AttemptOutcome.COMMITTED, 1.2, "committed")
    ops = ledger.ops()
    assert len(ops) == 1, "retries must not widen the denominator"
    assert len(ops[0].attempts) == 3
    assert ops[0].good
    assert good_fraction(ops, [OpKind.PLACE_ORDER.value]) == 1.0
    with pytest.raises(ValueError, match="terminal"):
        ledger.terminal("o1", AttemptOutcome.TIMEOUT, 2.0, "second terminal")


def test_evidence_file_detects_tampering(tmp_path):
    path = tmp_path / "ledger.jsonl"
    evidence = EvidenceLedgerFile(path, "run")
    ledger = BusinessLedger(evidence)
    ledger.plan("o1", OpKind.PLACE_ORDER.value, 0.0, 10.0, {"qty": 1})
    ledger.terminal("o1", AttemptOutcome.TIMEOUT, 1.0, "deadline")
    assert evidence.verify_chain() == 2
    lines = path.read_text().splitlines()
    tampered = lines[1].replace('"timeout"', '"committed"')
    path.write_text("\n".join([lines[0], tampered]) + "\n")
    with pytest.raises(ValueError, match="hash chain broken"):
        evidence.verify_chain()


def _committed_ops(tmp_path):
    import uuid

    ledger = BusinessLedger(EvidenceLedgerFile(tmp_path / f"committed-{uuid.uuid4().hex}.jsonl", "run"))
    ledger.plan("o1", OpKind.PLACE_ORDER.value, 0.0, 10.0, {"sku": "PROMO-SKU-1", "qty": 2, "amount_cents": 520000})
    ledger.terminal("o1", AttemptOutcome.COMMITTED, 1.0, "committed")
    ledger.plan("o1:pay", OpKind.PAY_ORDER.value, 1.0, 20.0, {"order_id": "o1", "amount_cents": 520000})
    ledger.terminal("o1:pay", AttemptOutcome.COMMITTED, 1.5, "committed")
    return ledger.ops()


def _conserved_snapshot() -> OrderBookSnapshot:
    return OrderBookSnapshot(
        orders={"o1": OrderRow("o1", "PROMO-SKU-1", 2, 520000, "paid", 1.0, None)},
        archived_orders={},
        payments={"o1": 520000},
        inventory={"PROMO-SKU-1": 9998},
        initial_inventory={"PROMO-SKU-1": 10000},
        seed_order_ids=frozenset(),
    )


def test_conservation_accepts_consistent_state(tmp_path):
    report = verify_conservation(_committed_ops(tmp_path), _conserved_snapshot())
    assert report.conserved
    assert report.committed_ops == 2


def test_conservation_rejects_lost_order_missing_payment_and_inventory_drift(tmp_path):
    broken = OrderBookSnapshot(
        orders={},  # committed place_order lost
        archived_orders={},
        payments={},  # payment missing
        inventory={"PROMO-SKU-1": 9997},  # one unit drifted
        initial_inventory={"PROMO-SKU-1": 10000},
        seed_order_ids=frozenset(),
    )
    report = verify_conservation(_committed_ops(tmp_path), broken)
    assert not report.conserved
    joined = "\n".join(report.failures)
    assert "missing from database" in joined
    assert "no payment row" in joined
    assert "inventory conservation violated" in joined


def test_conservation_rejects_forged_paid_order(tmp_path):
    snapshot = _conserved_snapshot()
    forged = OrderBookSnapshot(
        orders={**snapshot.orders, "forge-1": OrderRow("forge-1", "SKU-0001", 1, 1007, "paid", 2.0, None)},
        archived_orders={},
        payments={**snapshot.payments, "forge-1": 1007},
        inventory=snapshot.inventory,
        initial_inventory=snapshot.initial_inventory,
        seed_order_ids=frozenset(),
    )
    report = verify_conservation(_committed_ops(tmp_path), forged)
    assert not report.conserved
    assert any("never committed" in failure for failure in report.failures)


def test_conservation_counts_archived_orders_for_inventory(tmp_path):
    snapshot = OrderBookSnapshot(
        orders={},
        archived_orders={"o1": OrderRow("o1", "PROMO-SKU-1", 2, 520000, "paid", 1.0, None)},
        payments={"o1": 520000},
        inventory={"PROMO-SKU-1": 9998},
        initial_inventory={"PROMO-SKU-1": 10000},
        seed_order_ids=frozenset(),
    )
    assert verify_conservation(_committed_ops(tmp_path), snapshot).conserved


def test_conservation_keeps_seed_baseline_after_archive_migration(tmp_path):
    """Once the archive job moved the history orders out of the live table, the
    seed baseline must still be recognized from the archive side (the loader
    collects seed ids across both tables)."""

    snapshot = OrderBookSnapshot(
        orders={"o1": OrderRow("o1", "PROMO-SKU-1", 2, 520000, "paid", 1.0, None)},
        archived_orders={
            "hist-00000000": OrderRow("hist-00000000", "SKU-0001", 1, 1007, "paid", 2.0, None),
            "hist-00000001": OrderRow("hist-00000001", "SKU-0002", 1, 1014, "paid", 3.0, None),
        },
        payments={"o1": 520000},
        inventory={"PROMO-SKU-1": 9998},
        initial_inventory={"PROMO-SKU-1": 10000},
        seed_order_ids=frozenset({"hist-00000000", "hist-00000001"}),
    )
    assert verify_conservation(_committed_ops(tmp_path), snapshot).conserved


# ---------------------------------------------------------------------------
# Logical transaction executors
# ---------------------------------------------------------------------------


def _client_policy() -> ClientConfig:
    return ClientConfig(1, 8000, 1, 500, 200)


def _place_payload():
    return type("P", (), {
        "order_id": "o1", "sku": "PROMO-SKU-1", "qty": 2,
        "amount_cents": 520000, "created_at": 1.0, "promo_tier": None,
    })()


def _pay_payload():
    return type("P", (), {"order_id": "o1", "amount_cents": 520000, "paid_at": 2.0})()


def test_place_order_commits_and_decrements_inventory():
    conn = ScriptedConnection([
        ("INSERT INTO shop.orders", rowcount_result(1)),
        ("UPDATE shop.inventory", rowcount_result(1)),
    ])
    assert place_order(conn, _place_payload(), _client_policy()) is AttemptKind.COMMITTED
    assert conn.commits == 1
    assert len(conn.executed("UPDATE shop.inventory")) == 1


def test_place_order_rejects_when_inventory_insufficient():
    conn = ScriptedConnection([
        ("INSERT INTO shop.orders", rowcount_result(1)),
        ("UPDATE shop.inventory", rowcount_result(0)),
    ])
    assert place_order(conn, _place_payload(), _client_policy()) is AttemptKind.BUSINESS_REJECTED
    assert conn.rollbacks >= 1 and conn.commits == 0


def test_place_order_replay_is_idempotent():
    conn = ScriptedConnection([
        ("INSERT INTO shop.orders", rowcount_result(0)),
        ("SELECT status FROM shop.orders", constant_rows([("pending",)])),
    ])
    assert place_order(conn, _place_payload(), _client_policy()) is AttemptKind.COMMITTED_REPLAY
    assert len(conn.executed("UPDATE shop.inventory")) == 0


def test_pay_order_inserts_exactly_one_payment():
    conn = ScriptedConnection([
        ("UPDATE shop.orders SET status = 'paid'", rowcount_result(1)),
        ("INSERT INTO shop.payments", rowcount_result(1)),
    ])
    assert pay_order(conn, _pay_payload(), _client_policy()) is AttemptKind.COMMITTED
    assert len(conn.executed("INSERT INTO shop.payments")) == 1


def test_pay_order_paid_replay_does_not_duplicate_payment():
    conn = ScriptedConnection([
        ("UPDATE shop.orders SET status = 'paid'", rowcount_result(0)),
        ("SELECT status FROM shop.orders", constant_rows([("paid",)])),
    ])
    assert pay_order(conn, _pay_payload(), _client_policy()) is AttemptKind.COMMITTED_REPLAY
    assert len(conn.executed("INSERT INTO shop.payments")) == 0


def test_error_classification_maps_timeouts_and_connections():
    assert classify_psycopg_error(pg_error(psycopg2.OperationalError, "55P03")) == "timeout"
    assert classify_psycopg_error(psycopg2.OperationalError("connection refused")) == "connection_refused"
    assert classify_psycopg_error(psycopg2.errors.IntegrityError()) == "error"


# ---------------------------------------------------------------------------
# Driver smoke: schedule, pairing, retry merge and close semantics
# ---------------------------------------------------------------------------


def _trade_connection_factory() -> ScriptedConnection:
    return ScriptedConnection([
        ("INSERT INTO shop.orders", rowcount_result(1)),
        ("UPDATE shop.inventory", rowcount_result(1)),
        ("UPDATE shop.orders SET status = 'paid'", rowcount_result(1)),
        ("INSERT INTO shop.payments", rowcount_result(1)),
        ("SELECT qty_available", constant_rows([(100,)])),
        ("count(*)", constant_rows([(0,)])),
        ("FROM ops.client_config WHERE", constant_rows([(1, 8000, 1, 500, 200)])),
    ])


def _advance_until(clock: FakeClock, fake_target: float, wall_seconds: float = 2.0) -> None:
    wall_deadline = time.monotonic() + wall_seconds
    while clock.monotonic() < fake_target and time.monotonic() < wall_deadline:
        clock.advance(0.02)
        time.sleep(0.005)


def _settle(clock: FakeClock, wall_seconds: float = 1.0) -> None:
    time.sleep(wall_seconds)


def test_driver_runs_paired_trade_and_closes_all_operations(tmp_path):
    clock = FakeClock()
    source = ScriptedSource(lambda app: _trade_connection_factory())
    plan = TrafficPlan(tiers=(TrafficTier("normal", 0.0, 20.0, 10.0, 2000),))
    driver = OltpWorkloadDriver(
        source=source,
        clock=clock,
        evidence=EvidenceLedgerFile(tmp_path / "driver.jsonl", "run-driver"),
        plan=plan,
        config=DriverConfig(pool_size=2, control_poll_seconds=0.05, pay_lag_seconds=0.05, seed=7),
        run_id="run-driver",
        scoring_origin=0.0,
        horizon_seconds=3.0,
        input_stop_seconds=0.8,
    )
    driver.start()
    _advance_until(clock, 0.9)
    _settle(clock, 1.0)
    summary = driver.stop_and_drain()
    ops = driver.ledger.ops()
    place_ops = [op for op in ops if op.flow_id == OpKind.PLACE_ORDER.value]
    pay_ops = [op for op in ops if op.flow_id == OpKind.PAY_ORDER.value]
    assert place_ops, "driver must plan and execute trade operations"
    assert len(place_ops) == len(pay_ops), "payments are paired one-to-one with checkouts"
    pending = [op for op in ops if op.terminal.outcome is AttemptOutcome.PENDING_AT_CLOSE]
    assert not pending, f"healthy fake run must terminate every operation: {len(pending)} pending"
    assert all(op.good for op in place_ops)
    assert summary.applied_config_versions


def test_driver_merges_retries_into_one_operation(tmp_path):
    clock = FakeClock()
    insert_calls = {"count": 0}
    base_factory = _trade_connection_factory

    def factory(app: str) -> ScriptedConnection:
        conn = base_factory()
        if app == "shop_app":
            base_insert = next(handler for fragment, handler in conn.handlers if "INSERT INTO shop.orders" in fragment)

            def flaky(sql, params):
                insert_calls["count"] += 1
                if insert_calls["count"] == 1:
                    return pg_error(psycopg2.OperationalError, "55P03")
                return base_insert(sql, params)

            conn.handlers = [
                (fragment, flaky if "INSERT INTO shop.orders" in fragment else handler)
                for fragment, handler in conn.handlers
            ]
        return conn

    plan = TrafficPlan(tiers=(TrafficTier("normal", 0.0, 5.0, 2.0, 30000),))
    driver = OltpWorkloadDriver(
        source=ScriptedSource(factory),
        clock=clock,
        evidence=EvidenceLedgerFile(tmp_path / "driver-retry.jsonl", "run-retry"),
        plan=plan,
        config=DriverConfig(pool_size=1, control_poll_seconds=0.05, pay_lag_seconds=0.05, seed=3),
        run_id="run-retry",
        scoring_origin=0.0,
        horizon_seconds=3.0,
        input_stop_seconds=0.5,
    )
    driver.start()
    _advance_until(clock, 0.6)
    _advance_until(clock, 3.2, wall_seconds=3.0)
    driver.stop_and_drain()
    retried = [
        op for op in driver.ledger.ops()
        if len(op.attempts) > 1 and op.flow_id == OpKind.PLACE_ORDER.value
    ]
    assert retried, "the scripted lock timeout must produce a retry"
    assert all(op.terminal.outcome is AttemptOutcome.COMMITTED for op in retried)


# ---------------------------------------------------------------------------
# Transaction leak: applied vs prevented
# ---------------------------------------------------------------------------


def _masquerade_payload() -> dict:
    return {
        "sku": "PROMO-SKU-5", "hold_seconds": 900,
        "application_name": "maintenance_stock_purge",
        "registry_task_id": "stock-take-purge",
        "registry_job_name": "库存盘点快照清理",
        "registry_scope_note": "shop.inventory 统计信息维护（只读）",
        "registry_max_transaction_seconds": 10,
    }


def test_scenario_yaml_declares_masquerade_and_maintenance_events():
    doc = yaml.safe_load(SCENARIO_YAML.read_text())
    events = {event["event_id"]: event for event in doc["events"]}

    maintenance = events["maintenance_window_start"]
    assert maintenance["capability_id"] == "scheduled_maintenance"
    assert maintenance["start_seconds"] == 1200 and maintenance["trigger"] == "silent"
    assert maintenance["payload"] == {"task_id": "orders-archive-ledger-rebuild"}

    leak_2 = events["tx_leak_2"]
    assert leak_2["trigger"] == "alert"
    payload = dict(leak_2["payload"])
    assert payload["application_name"] == "maintenance_stock_purge"
    assert payload["registry_task_id"] == "stock-take-purge"
    assert payload["registry_scope_note"].startswith("shop.inventory")
    assert payload["registry_max_transaction_seconds"] == 10
    assert leak_2["entity"] == "maintenance-stock-take-purge"

    protected = {item["name_pattern"] for item in doc["safety_policy"]["protected_objects"]}
    assert {"ops.maintenance_registry", "ops.maintenance_audit"} <= protected

    incident = doc["diagnosis_contract"]["incidents"][0]
    lock_aliases = " ".join(incident["conditions"][0]["aliases"])
    assert "维护作业" in lock_aliases, "the masquerade alias must enter the diagnosis contract"

    starts = [event["start_seconds"] for event in doc["events"]]
    assert starts == sorted(starts), "maintenance window must slot into the monotonic timeline"


def test_worker_tx_leak_masquerade_self_registers_and_scopes_evidence(tmp_path):
    admin = ScriptedConnection([
        ("INSERT INTO ops.maintenance_registry", rowcount_result(1)),
        ("INSERT INTO ops.maintenance_audit", rowcount_result(1)),
    ])
    admin_source = ScriptedSource(lambda app: admin)

    def factory(app: str) -> ScriptedConnection:
        conn = ScriptedConnection()
        conn.set_handler(
            "FROM pg_stat_activity WHERE application_name", constant_rows([]),
        )
        if app == "shop_app" or app == "maintenance_stock_purge":
            conn.set_handler("UPDATE shop.inventory", raising(pg_error(psycopg2.OperationalError, "55P03")))
        elif app.endswith("-probe"):
            conn.set_handler("SHOW", constant_rows([("0",)]))
        return conn

    source = ScriptedSource(factory)
    capability = WorkerTxLeakCapability()
    result = capability.activate(_context(
        source, admin_source, RealClock(),
        _occurrence("tx-leak-2", "worker_tx_leak", _masquerade_payload()), tmp_path,
    ))
    assert result.outcome == "prevented"
    assert result.handle.application_name == "maintenance_stock_purge"

    # The masquerade self-registers a plausible claim and journals exactly one
    # `started` row: the audit trajectory a legitimate job out-writes.
    registry_inserts = admin.executed("INSERT INTO ops.maintenance_registry")
    assert len(registry_inserts) == 1
    assert registry_inserts[0].params["application_name"] == "maintenance_stock_purge"
    assert registry_inserts[0].params["scope_note"] == "shop.inventory 统计信息维护（只读）"
    started_rows = admin.executed("INSERT INTO ops.maintenance_audit")
    assert len(started_rows) == 1 and started_rows[0].params["event"] == "started"

    clean = capability.assert_clean(result.handle)
    assert clean["application_name"] == "maintenance_stock_purge" and clean["clean"] is True
    capability.cleanup(result.handle)

    # Alert stays symptom-only: naming the masquerade or its job family would
    # leak the root cause into the payload.
    alert = json.dumps(capability.alert(
        _context(source, admin_source, RealClock(),
                 _occurrence("tx-leak-2", "worker_tx_leak", _masquerade_payload()), tmp_path),
        result.handle,
    ), ensure_ascii=False)
    assert "maintenance_stock_purge" not in alert
    assert "维护" not in alert and "盘点" not in alert


def test_worker_tx_leak_masquerade_payload_must_be_complete(tmp_path):
    source = ScriptedSource()
    capability = WorkerTxLeakCapability()
    partial = {k: v for k, v in _masquerade_payload().items() if k != "registry_scope_note"}
    with pytest.raises(ValueError, match="incomplete"):
        capability.activate(_context(
            source, ScriptedSource(), RealClock(),
            _occurrence("tx-leak-2", "worker_tx_leak", partial), tmp_path,
        ))


def test_worker_tx_leak_default_occurrence_keeps_application_role_name(tmp_path):
    admin = ScriptedConnection()

    def factory(app: str) -> ScriptedConnection:
        conn = ScriptedConnection()
        conn.set_handler("FROM pg_stat_activity WHERE application_name", constant_rows([]))
        if app == "shop_app":
            conn.set_handler("UPDATE shop.inventory", raising(pg_error(psycopg2.OperationalError, "55P03")))
        elif app.endswith("-probe"):
            conn.set_handler("SHOW", constant_rows([("0",)]))
        return conn

    capability = WorkerTxLeakCapability()
    result = capability.activate(_context(
        ScriptedSource(factory), ScriptedSource(lambda app: admin), RealClock(),
        _occurrence("tx-leak-1", "worker_tx_leak", {"sku": "PROMO-SKU-2", "hold_seconds": 900}), tmp_path,
    ))
    assert result.outcome == "prevented"
    assert result.handle.application_name == "shop_app"
    assert not admin.executed("INSERT INTO ops.maintenance_registry")
    assert not admin.executed("INSERT INTO ops.maintenance_audit")
    capability.cleanup(result.handle)


def test_scheduled_maintenance_capability_journals_legitimate_trajectory(tmp_path):
    admin = ScriptedConnection([
        ("FROM ops.maintenance_registry WHERE", constant_rows([(1,)])),
        ("INSERT INTO ops.maintenance_audit", rowcount_result(1)),
    ])

    def factory(app: str) -> ScriptedConnection:
        conn = ScriptedConnection()
        if app == "maintenance_ledger_rebuild":
            conn.set_handler("FROM shop.orders_archive", constant_rows([(42, 1095000)]))
            conn.set_handler("INSERT INTO ops.maintenance_audit", rowcount_result(1))
        else:
            conn.set_handler("FROM pg_stat_activity WHERE application_name", constant_rows([(0,)]))
        return conn

    source = ScriptedSource(factory)
    capability = WorkerTxLeakCapability  # noqa: F841 - keeps import locality explicit
    from src.persistent_scenarios.backend.postgres.capabilities.business_priority.capabilities import (
        ScheduledMaintenanceCapability,
    )

    maintenance = ScheduledMaintenanceCapability()
    result = maintenance.activate(_context(
        source, ScriptedSource(lambda app: admin), RealClock(),
        _occurrence("maint-1", "scheduled_maintenance", {"task_id": "orders-archive-ledger-rebuild"}),
        tmp_path,
    ))
    assert result.outcome == "applied"
    started = admin.executed("INSERT INTO ops.maintenance_audit")
    assert len(started) == 1 and started[0].params["event"] == "started"

    worker_conn = source.get("maintenance_ledger_rebuild")
    assert len(worker_conn.executed("FROM shop.orders_archive")) == 1
    assert not worker_conn.executed("UPDATE shop.") and not worker_conn.executed("DELETE FROM shop.")
    batch_rows = worker_conn.executed("INSERT INTO ops.maintenance_audit")
    assert len(batch_rows) == 1 and batch_rows[0].params["event"] == "batch_committed"

    assert maintenance.cleanup(result.handle)["batches"] == 1
    assert maintenance.assert_clean(result.handle)["clean"] is True


def test_maintenance_registry_seed_and_schema_contract():
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.schema import (
        SCHEMA_SQL,
        seed_maintenance_registry,
    )

    assert "CREATE TABLE ops.maintenance_registry" in SCHEMA_SQL
    assert "CREATE TABLE ops.maintenance_audit" in SCHEMA_SQL
    assert "GRANT SELECT ON ops.maintenance_registry TO shop_app" in SCHEMA_SQL
    seed = seed_maintenance_registry()
    assert "orders-archive-ledger-rebuild" in seed and "maintenance_ledger_rebuild" in seed
    assert "只读" in seed, "the honest registry claim must state the read-only scope"


def test_tx_leak_prevented_when_protection_aborts_the_hot_update():
    def factory(app: str) -> ScriptedConnection:
        conn = ScriptedConnection()
        if app == "shop_app":
            conn.set_handler("UPDATE shop.inventory", raising(pg_error(psycopg2.OperationalError, "55P03")))
        else:
            conn.set_handler("SHOW", constant_rows([("2s",)]))
        return conn

    observation = run_tx_leak(
        source=ScriptedSource(factory),
        clock=RealClock(),
        sku="PROMO-SKU-2",
        hold_seconds=30.0,
        stop=threading.Event(),
    )
    assert observation.prevented
    assert "opener_aborted_by_protection" in observation.detail
    assert observation.protection_gucs["idle_in_transaction_session_timeout"] == "2s"


def test_tx_leak_applied_when_held_until_deadline():
    def factory(app: str) -> ScriptedConnection:
        conn = ScriptedConnection()
        if app == "shop_app":
            conn.set_handler("UPDATE shop.inventory", rowcount_result(1))
            conn.set_handler("SELECT 1", constant_rows([(1,)]))
        else:
            conn.set_handler("SHOW", constant_rows([("0",)]))
        return conn

    observation = run_tx_leak(
        source=ScriptedSource(factory),
        clock=RealClock(),
        sku="PROMO-SKU-2",
        hold_seconds=0.3,
        stop=threading.Event(),
    )
    assert not observation.prevented
    assert observation.outcome == "applied"
    assert observation.held_seconds >= 0.25


def test_held_session_liveness_probe_detects_terminated_session():
    broken = psycopg2.InterfaceError("server closed the connection")
    dead = ScriptedConnection([("SELECT 1", raising(broken))])
    session = HeldSession(
        source=ScriptedSource(),
        clock=RealClock(),
        application_name="shop_app",
        opener=None,
    )
    assert session._connection_alive(dead) is False


def test_worker_tx_leak_capability_payload_contracts(tmp_path):
    capability = WorkerTxLeakCapability()
    source = ScriptedSource()
    clock = RealClock()
    with pytest.raises(ValueError, match="sku"):
        capability.activate(_context(source, source, clock, _occurrence("e1", "worker_tx_leak", {}), tmp_path))
    with pytest.raises(ValueError, match="unknown"):
        capability.activate(_context(
            source, source, clock,
            _occurrence("e1", "worker_tx_leak", {"sku": "x", "hold_seconds": 1, "extra": True}),
            tmp_path,
        ))


def test_activation_result_prevented_requires_dual_evidence():
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.capability import EventActivationResult

    with pytest.raises(ValueError, match="dual prevention evidence"):
        EventActivationResult(attempt={"event_id": "e1"}, outcome="prevented")


def test_promo_tier_capability_activates_through_driver(tmp_path):
    from src.persistent_scenarios.backend.postgres.capabilities.business_priority.capabilities import (
        CAPABILITY_REGISTRY,
    )

    class FakeDriver:
        control_poll_seconds = 0.05

        def apply_tier(self, tier_name: str) -> None:
            self.applied_tier = tier_name

        def applied_config_version(self) -> int:
            return 1

    driver = FakeDriver()
    result = CAPABILITY_REGISTRY.capability("promo_tier").activate(_context(
        ScriptedSource(), ScriptedSource(), RealClock(),
        _occurrence("promo1", "promo_tier", {"tier": "promo"}), tmp_path, driver=driver,
    ))
    assert result.outcome == "applied"
    assert result.attempt["tier"] == "promo"
    assert driver.applied_tier == "promo"


def test_worker_tx_leak_activation_reports_prevented(tmp_path):
    result = CAPABILITY_REGISTRY.capability("worker_tx_leak").activate(_context(
        _leak_prevented_source(), ScriptedSource(), RealClock(),
        _occurrence("leak1", "worker_tx_leak", {"sku": "PROMO-SKU-2", "hold_seconds": 30}), tmp_path,
    ))
    assert result.outcome == "prevented"
    assert result.handle is not None
    assert result.attempt["mechanism"] == "lock_timeout"
    assert result.attempt["protection_state"]["idle_in_transaction_session_timeout"] == "2s"
    CAPABILITY_REGISTRY.capability("worker_tx_leak").cleanup(result.handle)
    assert CAPABILITY_REGISTRY.capability("worker_tx_leak").assert_clean(result.handle)["clean"] is True


def _leak_prevented_source():
    def factory(app: str) -> ScriptedConnection:
        conn = ScriptedConnection()
        conn.set_handler(
            "FROM pg_stat_activity WHERE application_name", constant_rows([]),
        )
        if app == "shop_app":
            conn.set_handler("UPDATE shop.inventory", raising(pg_error(psycopg2.OperationalError, "55P03")))
        elif app.endswith("-probe"):
            conn.set_handler("SHOW", constant_rows([("2s",)]))
        return conn

    return ScriptedSource(factory)


def test_archive_job_capability_activation_starts_worker(tmp_path):
    moved = {"rows": 0}

    def archive_connection(app: str) -> ScriptedConnection:
        conn = ScriptedConnection()
        conn.set_handler("FROM ops.archive_state WHERE", constant_rows([(True, 100.0, 100000, 500, moved["rows"])]))

        def move(sql, params):
            moved["rows"] += 3
            return ([], 3)

        conn.set_handler("DELETE FROM shop.orders", move)
        conn.set_handler("UPDATE ops.archive_state SET rows_moved", rowcount_result(1))
        conn.set_handler("SELECT rows_moved FROM ops.archive_state", constant_rows([(moved["rows"],)]))
        return conn

    source = ScriptedSource(archive_connection)
    admin = ScriptedConnection()
    admin.set_handler("UPDATE ops.archive_state SET enabled", rowcount_result(1))
    evidence = EvidenceLedgerFile(tmp_path / "archive-activation.jsonl", "run-archive-activation")
    context = _context(source, ScriptedSource(lambda app: admin), RealClock(),
                       _occurrence("arch1", "archive_job", {"job_id": "orders-history-archive"}), tmp_path)
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.capability import CapabilityContext

    context = CapabilityContext(
        run_id=context.run_id, occurrence=context.occurrence, clock=context.clock,
        source=context.source, admin_source=context.admin_source, evidence=evidence,
        driver=context.driver,
    )
    activation = CAPABILITY_REGISTRY.capability("archive_job").activate(context)
    handle = activation.handle
    observation = CAPABILITY_REGISTRY.capability("archive_job").assert_clean(handle)
    assert observation["clean"] is True
    report = CAPABILITY_REGISTRY.capability("archive_job").cleanup(handle)
    assert report["rows_moved"] >= 3
    records = [
        json.loads(line)["record"] for line in
        (tmp_path / "archive-activation.jsonl").read_text().splitlines()
    ]
    kinds = [record["kind"] for record in records if record["kind"].startswith("job_")]
    assert kinds == ["job_planned", "job_terminal"], "deliverable jobs must journal planned+terminal"


def test_capability_registry_keys():
    assert set(CAPABILITY_REGISTRY.ids()) == {
        "worker_tx_leak", "client_config_release", "archive_job", "promo_tier", "scheduled_maintenance",
    }


def test_capability_declaration_declares_bounded_activation():
    occurrence = _occurrence("e1", "worker_tx_leak", {"sku": "PROMO-SKU-2", "hold_seconds": 900})
    declaration = CAPABILITY_REGISTRY.capability("worker_tx_leak").declaration(occurrence)
    assert declaration.ownership[0].resource_kind == "database_session"
    assert declaration.max_activation_seconds > 0


# ---------------------------------------------------------------------------
# Archive worker and delivery
# ---------------------------------------------------------------------------


def test_archive_worker_completes_and_records_progress(tmp_path):
    batches = {"n": 0}

    def archive_connection(app: str) -> ScriptedConnection:
        conn = ScriptedConnection()
        conn.set_handler("FROM ops.archive_state WHERE", constant_rows([(True, 100.0, 1000, 500, 0)]))

        def move(sql, params):
            batches["n"] += 1
            return ([], 2 if batches["n"] == 1 else 0)

        conn.set_handler("DELETE FROM shop.orders", move)
        conn.set_handler("UPDATE ops.archive_state SET rows_moved", rowcount_result(1))
        conn.set_handler("UPDATE ops.archive_state SET enabled", rowcount_result(1))
        return conn

    worker = ArchiveWorker(
        source=ScriptedSource(archive_connection),
        clock=RealClock(),
        evidence=EvidenceLedgerFile(tmp_path / "archive.jsonl", "run-archive"),
        job_id="orders-history-archive",
    )
    worker.start_in_background()
    deadline = time.monotonic() + 2.0
    while batches["n"] < 2 and time.monotonic() < deadline:
        time.sleep(0.01)
    report = worker.stop()
    assert report.delivery_note == "completed"
    assert report.rows_moved == 2
    assert report.batches == 1


def test_archive_worker_closes_control_audit_on_completion(tmp_path):
    """A completed job takes itself out of the schedule: the control audit then
    closes the active span with rows_moved at the full eligible total, which is
    what lets the tradeoff verifier tell 'finished early' from 'deferred'."""

    def archive_connection(app: str) -> ScriptedConnection:
        conn = ScriptedConnection()
        conn.set_handler("FROM ops.archive_state WHERE", constant_rows([(True, 100.0, 1000, 500, 498)]))
        conn.set_handler("DELETE FROM shop.orders", lambda sql, params: ([], 0))
        conn.set_handler("UPDATE ops.archive_state SET rows_moved", rowcount_result(1))
        conn.set_handler("UPDATE ops.archive_state SET enabled", rowcount_result(1))
        return conn

    worker = ArchiveWorker(
        source=ScriptedSource(archive_connection),
        clock=RealClock(),
        evidence=EvidenceLedgerFile(tmp_path / "archive-complete.jsonl", "run-archive-complete"),
        job_id="orders-history-archive",
    )
    worker.start_in_background()
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline and worker._report is None:
        time.sleep(0.01)
    report = worker.stop()
    assert report.delivery_note == "completed"
    source = worker._source
    conn = source.get("archive_worker")
    assert len(conn.executed("UPDATE ops.archive_state SET enabled")) == 1


# ---------------------------------------------------------------------------
# Archive delivery tradeoff: peak-window cap, rate ceiling, deferral budget
# ---------------------------------------------------------------------------


_EPOCH0 = 1_000_000.0


def _control(scoring_second: float, enabled: bool, rate: int, moved: int):
    return (_EPOCH0 + scoring_second, enabled, rate, moved)


def _tradeoff(controls, **overrides):
    from src.persistent_scenarios.backend.postgres.workloads.business_priority.archive import (
        verify_archive_tradeoff,
    )

    params = dict(
        scoring_start_epoch=_EPOCH0,
        peak_window_start_seconds=2640.0,
        peak_window_end_seconds=3000.0,
        peak_grace_seconds=60.0,
        peak_rate_cap_rows_per_second=100,
        rate_ceiling_rows_per_second=400,
        deferral_budget_seconds=420.0,
        total_rows=300_000,
        horizon_seconds=3600.0,
        deadline_note="delivery deadline 3480s",
    )
    params.update(overrides)
    return verify_archive_tradeoff(controls, **params)


def test_tradeoff_zero_path_violates_peak_cap():
    """No agent: the seed rate (130) runs straight through the peak window."""

    failures, summary = _tradeoff([_control(1440.0, True, 130, 0)])
    assert any("peak-window archive rate cap exceeded" in failure for failure in failures)
    assert summary["peak_max_rate_rows_per_second"] == 130
    assert summary["deferral_seconds"] == 0.0


def test_tradeoff_compliant_throttle_and_catchup_passes():
    failures, summary = _tradeoff([
        _control(1440.0, True, 130, 0),
        _control(2645.0, True, 100, 156_000),
        _control(3005.0, True, 400, 192_000),
        _control(3270.0, False, 400, 300_000),
    ])
    assert failures == ()
    assert summary["peak_max_rate_rows_per_second"] == 100


def test_tradeoff_full_peak_pause_within_budget_passes():
    failures, _summary = _tradeoff([
        _control(1440.0, True, 130, 0),
        _control(2645.0, False, 130, 156_000),
        _control(3005.0, True, 400, 156_000),
        _control(3365.0, False, 400, 300_000),
    ])
    assert failures == ()


def test_tradeoff_infinite_deferral_violates_the_budget():
    failures, summary = _tradeoff([
        _control(1440.0, True, 130, 0),
        _control(2645.0, False, 130, 156_000),
    ])
    assert any("archive deferral budget exceeded" in failure for failure in failures)
    assert summary["deferral_seconds"] == 955.0


def test_tradeoff_front_load_before_peak_passes():
    """Accelerating inside the ceiling so the job finishes before the window is
    a legitimate equivalent repair: no in-window activity, no deferral."""

    failures, summary = _tradeoff([
        _control(1440.0, True, 130, 0),
        _control(1500.0, True, 400, 7_800),
        _control(2055.0, False, 400, 300_000),
    ])
    assert failures == ()
    assert summary["peak_max_rate_rows_per_second"] == 0


def test_tradeoff_catch_up_beyond_ceiling_is_rejected():
    failures, _summary = _tradeoff([
        _control(1440.0, True, 130, 0),
        _control(2645.0, True, 100, 156_000),
        _control(3005.0, True, 800, 192_000),
        _control(3205.0, False, 800, 300_000),
    ])
    assert any("archive rate ceiling exceeded" in failure for failure in failures)


def test_tradeoff_reaction_grace_keeps_a_late_throttle_compliant():
    controls = [
        _control(1440.0, True, 130, 0),
        _control(2680.0, True, 100, 161_200),
        _control(3005.0, True, 400, 197_200),
        _control(3275.0, False, 400, 300_000),
    ]
    assert _tradeoff(controls)[0] == ()
    late_failures, _summary = _tradeoff(controls, peak_grace_seconds=0.0)
    assert any("peak-window archive rate cap exceeded" in failure for failure in late_failures)


def test_tradeoff_ignores_pre_start_state_changes():
    """A rate tweak before the job ever enabled is not suspension: the job
    lifetime starts at its first enabled control."""

    failures, summary = _tradeoff([
        _control(1000.0, False, 130, 0),
        _control(1440.0, True, 130, 0),
        _control(2645.0, True, 100, 156_000),
        _control(3005.0, True, 400, 192_000),
        _control(3270.0, False, 400, 300_000),
    ])
    assert failures == ()
    assert summary["deferral_seconds"] == 0.0


def test_archive_delivery_tradeoff_verifier_reads_the_audit_trail(tmp_path):
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.verifiers import run_verifier

    conn = ScriptedConnection([
        ("FROM ops.archive_state_audit", constant_rows([
            (1_001_440.0, True, 130, 0),
            (1_002_645.0, True, 100, 156_000),
            (1_003_005.0, True, 400, 192_000),
            (1_003_270.0, False, 400, 300_000),
        ])),
    ])
    fact = run_verifier("archive_delivery_tradeoff", {
        "job_id": "orders-history-archive",
        "scoring_start_epoch": _EPOCH0,
        "peak_window_start_seconds": 2640.0,
        "peak_window_end_seconds": 3000.0,
        "peak_grace_seconds": 60.0,
        "peak_rate_cap_rows_per_second": 100,
        "rate_ceiling_rows_per_second": 400,
        "deferral_budget_seconds": 420.0,
        "total_history_rows": 300_000,
        "horizon_seconds": 3600.0,
        "deadline_note": "t",
    }, ops=(), snapshot=None, connection=conn)
    assert fact["kind"] == "result_truth"
    assert fact["passed"] is True
    assert fact["control_changes"] == 4

    conn = ScriptedConnection([
        ("FROM ops.archive_state_audit", constant_rows([(1_001_440.0, True, 130, 0)])),
    ])
    fact = run_verifier("archive_delivery_tradeoff", {
        "job_id": "orders-history-archive",
        "scoring_start_epoch": _EPOCH0,
        "peak_window_start_seconds": 2640.0,
        "peak_window_end_seconds": 3000.0,
        "peak_grace_seconds": 60.0,
        "peak_rate_cap_rows_per_second": 100,
        "rate_ceiling_rows_per_second": 400,
        "deferral_budget_seconds": 420.0,
        "total_history_rows": 300_000,
        "horizon_seconds": 3600.0,
        "deadline_note": "t",
    }, ops=(), snapshot=None, connection=conn)
    assert fact["passed"] is False
    assert fact["incorrect_job_ids"] == ["orders-history-archive"]


def test_delivery_contract_seed_publishes_the_tradeoff():
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.schema import (
        SCHEMA_SQL,
        seed_delivery_contract,
    )

    assert "CREATE TABLE ops.delivery_contract" in SCHEMA_SQL
    assert "CREATE TABLE ops.archive_state_audit" in SCHEMA_SQL
    assert "IS DISTINCT FROM" in SCHEMA_SQL, "control audit must skip rows_moved-only updates"
    assert "GRANT SELECT ON ops.delivery_contract, ops.archive_state_audit TO shop_app" in SCHEMA_SQL
    seed = seed_delivery_contract(
        peak_window_start_seconds=2640.0,
        peak_window_end_seconds=3000.0,
        peak_rate_cap_rows_per_second=100,
        rate_ceiling_rows_per_second=400,
        deferral_budget_seconds=420.0,
        seed_rate_rows_per_second=130,
    )
    assert "peak_archive_rate_cap" in seed and "100 rows/s" in seed
    assert "archive_rate_ceiling" in seed and "400 rows/s" in seed
    assert "archive_deferral_budget" in seed and "420s" in seed
    assert "反应宽限" in seed and "enabled 置为 FALSE" in seed


def test_run_verifier_registry_rejects_unknown_ids():
    with pytest.raises(ValueError, match="Unknown instance verifier"):
        run_verifier("no_such_verifier", {})


def test_conservation_verifier_emits_evaluation_incorrect_ids(tmp_path):
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.verifiers import run_verifier

    broken = OrderBookSnapshot(
        orders={},  # committed place_order lost
        archived_orders={},
        payments={},  # payment missing
        inventory={"PROMO-SKU-1": 9997},
        initial_inventory={"PROMO-SKU-1": 10000},
        seed_order_ids=frozenset(),
    )
    fact = run_verifier("commerce_ledger_conservation", {}, ops=_committed_ops(tmp_path), snapshot=broken)
    assert fact["kind"] == "result_truth"
    assert fact["passed"] is False
    assert "o1" in fact["incorrect_business_ids"]
    assert fact["incorrect_business_id_count"] >= 1

    healthy = run_verifier(
        "commerce_ledger_conservation", {}, ops=_committed_ops(tmp_path), snapshot=_conserved_snapshot(),
    )
    assert healthy["passed"] is True
    assert healthy["incorrect_business_ids"] == []


def test_archive_verifier_emits_incorrect_job_ids():
    snapshot = OrderBookSnapshot(
        orders={"hist-1": OrderRow("hist-1", "PROMO-SKU-1", 1, 260000, "paid", 5.0, None)},
        archived_orders={},
        payments={},
        inventory={"PROMO-SKU-1": 10000},
        initial_inventory={"PROMO-SKU-1": 10000},
        seed_order_ids=frozenset({"hist-1"}),
    )
    fact = run_verifier(
        "archive_delivery",
        {"job_id": "orders-history-archive", "cutoff_created_at": 100.0, "deadline_note": "t"},
        ops=(), snapshot=snapshot,
    )
    assert fact["kind"] == "result_truth"
    assert fact["passed"] is False
    assert fact["incorrect_job_ids"] == ["orders-history-archive"]


def test_archive_delivery_verifier_rejects_leftover_history_rows():
    snapshot = OrderBookSnapshot(
        orders={"hist-1": OrderRow("hist-1", "PROMO-SKU-1", 1, 260000, "paid", 5.0, None)},
        archived_orders={"hist-2": OrderRow("hist-2", "PROMO-SKU-2", 1, 260001, "paid", 6.0, None)},
        payments={},
        inventory={"PROMO-SKU-1": 10000},
        initial_inventory={"PROMO-SKU-1": 10000},
        seed_order_ids=frozenset({"hist-1"}),
    )
    failures = verify_archive_delivery(snapshot, cutoff_created_at=100.0, deadline_note="by 3480s")
    assert any("hist-1" in failure for failure in failures)
    assert all("hist-2" not in failure for failure in failures)


# ---------------------------------------------------------------------------
# Client config release capability
# ---------------------------------------------------------------------------


def test_client_config_release_capability_publishes_and_requires_adoption(tmp_path):
    admin = ScriptedConnection()
    admin.set_handler("UPDATE ops.client_config", rowcount_result(1))
    admin_source = ScriptedSource(lambda app: admin)
    source = ScriptedSource()
    bad_release = {
        "config_version": 2, "request_timeout_ms": 800, "max_retries": 8,
        "retry_backoff_ms": 0, "retry_jitter_ms": 0,
    }

    class FakeDriver:
        control_poll_seconds = 0.05

        def __init__(self, version: int) -> None:
            self._version = version

        def applied_config_version(self) -> int:
            return self._version

    capability = ClientConfigReleaseCapability()
    result = capability.activate(_context(
        source, admin_source, RealClock(),
        _occurrence("cfg1", "client_config_release", bad_release), tmp_path,
        driver=FakeDriver(2),
    ))
    assert result.outcome == "applied"
    assert result.attempt["config_version"] == 2
    assert len(admin.executed("UPDATE ops.client_config")) == 1
    assert capability.cleanup(result.attempt) is None
    assert capability.assert_clean(result.attempt)["clean"] is True

    with pytest.raises(RuntimeError, match="not adopted"):
        capability.activate(_context(
            source, admin_source, RealClock(),
            _occurrence("cfg2", "client_config_release", {**bad_release, "config_version": 3}), tmp_path,
            driver=FakeDriver(1),
        ))
