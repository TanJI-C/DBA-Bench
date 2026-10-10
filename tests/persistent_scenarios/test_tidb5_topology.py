"""Focused tests for the tidb_oltp_online_topology_change instance package."""

from __future__ import annotations

from pathlib import Path
import time

import pytest

from src.persistent_scenarios.backend.contracts import EventActivationContext
from src.persistent_scenarios.backend.tidb.capabilities.topology import CAPABILITIES, VERIFIERS
from src.persistent_scenarios.backend.tidb.capabilities.topology.capabilities import (
    ConnectionPoolBiasCapability,
    MaintenanceWorkOrderCapability,
    MigrationLinkDelayCapability,
    ReserveStoreArrivalCapability,
)
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.persistent_scenarios.runtime.admission import admit_persistent_scenario
from src.persistent_scenarios.runtime.clock import RealClock
from src.persistent_scenarios.runtime.ledger import LedgerTerminal, LedgerView, TrustedLedger
from src.persistent_scenarios.tidb.topology.delivery import (
    placement_satisfied,
    store_retired_satisfied,
    store_scaleout_satisfied,
    tidb_drain_satisfied,
)
from src.persistent_scenarios.tidb.hotspot.control import READ_CLIENT_POLICY_SQL
from src.persistent_scenarios.tidb.hotspot.driver import DriverConfig, TrafficPlan, TrafficTier
from src.persistent_scenarios.tidb.hotspot.schema import PROMO_GROUP_A
from src.persistent_scenarios.tidb.port_adapter import parse_bytes_per_sec
from src.persistent_scenarios.tidb.topology.driver import MaintenanceOrderRow, TopologyWorkloadDriver
from src.persistent_scenarios.tidb.topology.schema import (
    READ_MAINTENANCE_ORDERS_SQL,
    SHOW_PLACEMENT_SQL,
)
from src.persistent_scenarios.tidb.topology.verifiers import (
    maintenance_final_state,
    maintenance_jobs_delivered,
    replica_safety_after_change,
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
TOPOLOGY_YAML = WORKTREE / "src" / "persistent_scenarios" / "tidb" / "tidb_oltp_online_topology_change.yaml"


def _registry() -> Registry:
    return Registry({capability.capability_id: capability for capability in CAPABILITIES})


def _event(spec, event_id: str):
    return [item for item in spec.events if item.event_id == event_id][0]


class _Backend:
    def validate_spec(self, spec) -> None:
        return None


class _SqlConn:
    def __init__(self, rows: tuple[tuple, ...]) -> None:
        self._rows = rows

    def cursor(self):
        conn = ScriptedConnection(lambda sql, args: (self._rows, len(self._rows)), "verifier")
        return conn.cursor()

    def commit(self):
        return None


def _work_order_payload() -> dict:
    spec = load_persistent_scenario(TOPOLOGY_YAML)
    return dict(_event(spec, "maintenance_order_1").payload)


def _topology_driver(
    tmp_path: Path,
    *,
    maintenance_poll_seconds: float = 2.0,
    control_responder=None,
    environment_port: FakeTiDBPort | None = None,
) -> TopologyWorkloadDriver:
    clock = RealClock()
    # A scoring origin in the future keeps the trade schedulers parked on the
    # warmup wait, so a started driver plans no trade traffic in these tests.
    return TopologyWorkloadDriver(
        maintenance_ledger=TrustedLedger("maintenance", tmp_path / "maintenance.jsonl"),
        maintenance_service_id="maintenance",
        environment_port=environment_port if environment_port is not None else FakeTiDBPort(),
        maintenance_poll_seconds=maintenance_poll_seconds,
        service_id="trade",
        ledger=TrustedLedger("trade", tmp_path / "trade.jsonl"),
        clock=clock,
        connection_source=FakeConnectionSource(control_responder or exact_responder({})),
        plan=TrafficPlan(tiers=(TrafficTier("normal", 2.0, 3.0, PROMO_GROUP_A),)),
        config=DriverConfig(pool_size=2, deadline_seconds=10.0),
        run_id="r-test",
        scoring_origin=clock.monotonic() + 3600.0,
        input_stop_seconds=60.0,
        normal_sku_count=20,
    )


def _work_order_rows(clock: RealClock) -> tuple[MaintenanceOrderRow, ...]:
    payload = _work_order_payload()
    published_at_ms = int(clock.monotonic() * 1000)
    targets = {
        "store_scaleout": payload["reserve_tikv"],
        "placement_satisfied": "ops.maintenance_tracking",
        "tidb_drain": payload["drain_backend"],
        "store_retired": payload["retire_tikv"],
    }
    return tuple(
        MaintenanceOrderRow(
            order_id=payload["order_id"],
            deliverable_id=payload["deliverable_ids"][kind],
            kind=kind,
            target=targets[kind],
            deadline_seconds=int(payload["deadlines"][kind]),
            published_at_ms=published_at_ms,
        )
        for kind in ("store_scaleout", "placement_satisfied", "tidb_drain", "store_retired")
    )


def test_topology_spec_passes_static_and_capability_admission() -> None:
    spec = load_persistent_scenario(TOPOLOGY_YAML)
    admit_persistent_scenario(spec, _Backend(), _registry())


def test_work_order_deliverable_ids_match_the_olap_checklist() -> None:
    spec = load_persistent_scenario(TOPOLOGY_YAML)
    payload = _work_order_payload()
    objective = [service for service in spec.services if service.service_id == "maintenance"][0]
    checklist_ids = {deliverable.deliverable_id for deliverable in objective.deliverables}
    payload_ids = set(payload["deliverable_ids"].values())
    assert checklist_ids == payload_ids


def test_work_order_activation_publishes_rows_and_driver_plans_jobs() -> None:
    inserts: list[tuple] = []

    def control_responder(sql: str, args):
        if sql.startswith("INSERT INTO ops.maintenance_orders"):
            inserts.append(args)
        return ((), 1)

    port = FakeTiDBPort(
        workload_driver=FakeWorkloadDriver(),
        control_responder=control_responder,
    )
    port.workload_driver._planned = {"mo_store_scaleout", "mo_placement_satisfied", "mo_tidb_drain", "mo_store_retired"}
    spec = load_persistent_scenario(TOPOLOGY_YAML)
    event = _event(spec, "maintenance_order_1")
    result = MaintenanceWorkOrderCapability().activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert result.applied is not None
    assert result.applied.facts["adopted_deliverables"] == 4
    assert len(inserts) == 4
    assert {row[1] for row in inserts} == {"mo_store_scaleout", "mo_placement_satisfied", "mo_tidb_drain", "mo_store_retired"}


def test_work_order_adoption_accepts_decided_and_removed_deliverables(tmp_path: Path) -> None:
    """The driver decides a terminal and removes the job from its planned set
    in the same step (decide-then-remove). A work order whose deliverables
    were decided before the adoption poll must still be adopted: the decided
    ids are the real terminal evidence, and rejecting them fails a legitimate
    decision path."""
    driver = _topology_driver(tmp_path)
    rows = _work_order_rows(driver.clock)
    for row in rows[:2]:
        driver._plan_job(row)
    for row in rows[2:]:
        driver._plan_job(row)
        driver._deliver(row, LedgerTerminal.COMPLETED, {"satisfied": True, "target": row.target})
    # rows[0]/rows[1] are planned-not-decided, rows[2]/rows[3] decided-and-removed.
    capability = MaintenanceWorkOrderCapability()
    deliverable_ids = {row.kind: row.deliverable_id for row in rows}
    assert capability._adopted_count(driver, deliverable_ids) == 4
    assert capability._adopted_count(driver, {**deliverable_ids, "extra": "mo_missing"}) is None

    spec = load_persistent_scenario(TOPOLOGY_YAML)
    port = FakeTiDBPort(workload_driver=driver, control_responder=lambda sql, args: ((), 1))
    result = capability.activate(EventActivationContext(
        run_id="r", spec=spec, event=_event(spec, "maintenance_order_1"), environment=port, clock=RealClock(),
    ))
    assert result.applied is not None
    assert result.applied.facts["adopted_deliverables"] == 4


def test_work_order_activation_adopts_pre_bias_and_drain_delivers_only_post_bias(tmp_path: Path) -> None:
    """The real e2e conflict: tidb-1 carries no connections at work-order
    publication - the connection-pool bias concentrates connections much
    later. The driver must plan ALL FOUR deliverables at publication so
    activation adoption succeeds inside the 30s budget, while the drain
    deliverable's terminal evidence comes only from the real post-bias drain:
    pre-bias zero connections stays planned-pending and is never a COMPLETED
    delivery."""
    published_rows: list[tuple] = []

    def control_responder(sql: str, args):
        if sql.startswith("INSERT INTO ops.maintenance_orders"):
            published_rows.append(args)
            return ((), 1)
        if sql == READ_MAINTENANCE_ORDERS_SQL:
            return (tuple(published_rows), len(published_rows))
        if sql == READ_CLIENT_POLICY_SQL:
            return (((1, 3000, 3, 200, 100, 600, "tidb/tidb-0", 50, None, 0),), 1)
        if sql.startswith("SELECT COUNT(*)"):
            return (((0,),), 1)
        return ((), 0)

    port = FakeTiDBPort(
        stores=[{"store": {"id": 3, "address": "tikv-2:20160", "state_name": "Up", "labels": []}}],
        connection_counts={"tidb/tidb-0": 6, "tidb/tidb-1": 0},
        control_responder=control_responder,
    )
    driver = _topology_driver(tmp_path, maintenance_poll_seconds=0.02, control_responder=control_responder,
                              environment_port=port)
    port.workload_driver = driver
    driver.start()
    try:
        spec = load_persistent_scenario(TOPOLOGY_YAML)
        result = MaintenanceWorkOrderCapability().activate(EventActivationContext(
            run_id="r", spec=spec, event=_event(spec, "maintenance_order_1"), environment=port, clock=RealClock(),
        ))
        assert result.applied is not None
        assert result.applied.facts["adopted_deliverables"] == 4
        # Pre-bias: all four deliverables planned at publication, none decided.
        all_ids = {"mo_store_scaleout", "mo_placement_satisfied", "mo_tidb_drain", "mo_store_retired"}
        assert driver.planned_deliverable_ids() == all_ids
        assert driver.decided_deliverable_ids() == set()

        # The bias event concentrates real connections on tidb-1 ...
        port.connection_counts = {"tidb/tidb-0": 6, "tidb/tidb-1": 4}
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline and "tidb/tidb-1" not in driver._busy_backends:
            time.sleep(0.01)
        assert "tidb/tidb-1" in driver._busy_backends
        # ... the drain becomes evaluable but is not satisfied: real
        # connections remain, so the deliverable is still planned-pending.
        assert "mo_tidb_drain" in driver.planned_deliverable_ids()
        assert "mo_tidb_drain" not in driver.decided_deliverable_ids()

        # The agent's real drain (connection lifecycle governance) empties
        # tidb-1; only now does the deliverable carry a COMPLETED terminal.
        port.connection_counts = {"tidb/tidb-0": 6, "tidb/tidb-1": 0}
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline and "mo_tidb_drain" not in driver.decided_deliverable_ids():
            time.sleep(0.01)
        assert "mo_tidb_drain" in driver.decided_deliverable_ids()
        published_at_ms = int(result.applied.facts["published_at_ms"])
    finally:
        driver.stop_new_requests()
        driver.drain()
        driver.stop()

    driver.maintenance_ledger.seal()
    driver.maintenance_ledger.verify()
    assert driver._maintenance_errors == ()
    records = {job.job_id: job for job in LedgerView(driver.maintenance_ledger).jobs()}
    drain = records["mo_tidb_drain"]
    assert drain.terminal is LedgerTerminal.COMPLETED
    assert drain.delivered_on_time is True
    assert drain.job_kind == "tidb_drain"
    assert drain.input_snapshot == {"target": "tidb/tidb-1", "order_id": "MO-2026-001"}
    # The delivery deadline is anchored at work-order publication, not at the
    # post-bias planning moment.
    assert drain.submitted_at_monotonic == pytest.approx(published_at_ms / 1000.0)
    assert drain.deadline_at_monotonic == pytest.approx(published_at_ms / 1000.0 + 3300)
    assert drain.attempts[0].detail["remaining_connections"] == 0
    assert drain.attempts[0].detail["connection_counts"]["tidb/tidb-1"] == 0


def test_reserve_store_arrival_attaches_the_policy_after_the_store_is_up() -> None:
    statements: list[str] = []
    store_up_before_create: list[bool] = []

    def control_responder(sql: str, args):
        statements.append(sql)
        if sql.startswith("SHOW PLACEMENT"):
            state = "SCHEDULED" if len(statements) == 1 else "PENDING"
            return ((("ops.maintenance_tracking", "maintenance_learner", state),), 1)
        return ((), 0)

    def store_observer(sql: str, args):
        if sql.startswith("CREATE PLACEMENT POLICY"):
            store_up_before_create.append(len(port.started_tikv) == 1)
        return control_responder(sql, args)

    port = FakeTiDBPort(control_responder=None)
    port.control_responder = store_observer
    spec = load_persistent_scenario(TOPOLOGY_YAML)
    event = _event(spec, "reserve_store_arrival_1")
    result = ReserveStoreArrivalCapability().activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert result.applied is not None
    assert result.applied.facts["store_state"] == "Up"
    assert result.applied.facts["placement_state_before_policy"] == "SCHEDULED"
    assert result.applied.facts["placement_state"] == "PENDING"
    assert any("FOLLOWERS=2" in sql for sql in statements)
    assert any("CONSTRAINTS=\"[+zone=zone4]\"" in sql for sql in statements)
    assert any("ALTER TABLE ops.maintenance_tracking" in sql for sql in statements)
    assert store_up_before_create == [True]
    assert port.started_tikv == ["tikv/tikv-3"]


def test_reserve_store_arrival_records_default_layout_before_policy_on_v8_1() -> None:
    """Measured TiDB v8.1 semantics: a table without an explicit placement
    policy has NO SHOW PLACEMENT row at all, so the fresh tracked table's
    before-policy state is the default layout. The activation records that
    fact instead of failing with "SHOW PLACEMENT returned no row"."""
    placement_reads = {"count": 0}

    def control_responder(sql: str, args):
        if sql.startswith("SHOW PLACEMENT"):
            placement_reads["count"] += 1
            if placement_reads["count"] == 1:
                return ((), 0)
            return (((
                "TABLE ops.maintenance_tracking",
                'CONSTRAINTS="[+zone=zone4]" FOLLOWERS=2',
                "PENDING",
            ),), 1)
        return ((), 0)

    port = FakeTiDBPort(control_responder=control_responder)
    spec = load_persistent_scenario(TOPOLOGY_YAML)
    event = _event(spec, "reserve_store_arrival_1")
    result = ReserveStoreArrivalCapability().activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert result.applied is not None
    assert result.applied.facts["placement_state_before_policy"] == "NO-EXPLICIT-PLACEMENT"
    assert result.applied.facts["placement_state"] == "PENDING"
    assert port.started_tikv == ["tikv/tikv-3"]


def test_delivery_predicates_read_trusted_state() -> None:
    port = FakeTiDBPort(stores=[
        {"store": {"id": 4, "address": "tikv-3:20160", "state_name": "Up", "labels": []}},
        {"store": {"id": 3, "address": "tikv-2:20160", "state_name": "Tombstone", "labels": []}},
    ])
    assert store_scaleout_satisfied(port, None, "tikv/tikv-3")["satisfied"] is True
    assert store_retired_satisfied(port, None, "tikv/tikv-2")["satisfied"] is True
    offline = FakeTiDBPort(stores=[
        {"store": {"id": 3, "address": "tikv-2:20160", "state_name": "Offline", "labels": []}},
    ])
    assert store_retired_satisfied(offline, None, "tikv/tikv-2")["satisfied"] is False
    assert tidb_drain_satisfied(port, None, "tidb/tidb-1")["satisfied"] is False

    pending = _SqlConn((("ops.maintenance_tracking", "maintenance_learner", "PENDING"),))
    scheduled = _SqlConn((("ops.maintenance_tracking", "maintenance_learner", "SCHEDULED"),))
    assert placement_satisfied(port, pending, "ops.maintenance_tracking")["satisfied"] is False
    assert placement_satisfied(port, scheduled, "ops.maintenance_tracking")["satisfied"] is True


def test_connection_pool_bias_prevented_on_stale_version() -> None:
    rejected = ({"published_version": "2", "reason": "client config version must strictly increase"},)
    port = FakeTiDBPort(workload_driver=FakeWorkloadDriver(applied_version=1, rejected=rejected))
    spec = load_persistent_scenario(TOPOLOGY_YAML)
    event = _event(spec, "connection_pool_bias_1")
    result = ConnectionPoolBiasCapability().activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert result.applied is None and result.prevented is not None
    assert result.prevented.mechanism == "client_config_validation"


def test_migration_link_delay_cleanup_restores_the_baseline() -> None:
    port = FakeTiDBPort()
    spec = load_persistent_scenario(TOPOLOGY_YAML)
    event = _event(spec, "migration_link_delay_1")
    capability = MigrationLinkDelayCapability()
    result = capability.activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert result.applied is not None
    assert port.io_limits["tikv/tikv-3"] == 524288
    capability.cleanup(result.handle)
    assert port.io_limits["tikv/tikv-3"] == 262144000
    assert capability.assert_clean(result.handle)["clean"] is True


def test_maintenance_final_state_verifier_aggregates_delivery_facts() -> None:
    port = FakeTiDBPort(
        stores=[
            {"store": {"id": 4, "address": "tikv-3:20160", "state_name": "Up", "labels": []}},
            {"store": {"id": 3, "address": "tikv-2:20160", "state_name": "Tombstone", "labels": []}},
        ],
        connection_counts={"tidb/tidb-0": 6, "tidb/tidb-1": 0},
        control_script={
            "SHOW PLACEMENT FOR TABLE ops.maintenance_tracking": (
                ("TABLE ops.maintenance_tracking", 'LEARNERS=1 LEARNER_CONSTRAINTS="[+zone=zone4]"', "SCHEDULED"),
            ),
        },
    )
    params = {
        "reserve_tikv": "tikv/tikv-3",
        "retire_tikv": "tikv/tikv-2",
        "drain_backend": "tidb/tidb-1",
        "placement_table": "ops.maintenance_tracking",
        "placement_expected_constraint": "[+zone=zone4]",
    }
    result = maintenance_final_state(port, port.control_connection(), None, params)
    assert result["passed"] is True
    assert result["facts"]["placement_satisfied"]["satisfied"] is True


def test_maintenance_final_state_exposes_default_placement_fake() -> None:
    """Contract 8.3 error path: dropping the placement to fake migration
    completion leaves NO-ROW (default placement has no SHOW PLACEMENT row)."""
    port = FakeTiDBPort(
        stores=[
            {"store": {"id": 4, "address": "tikv-3:20160", "state_name": "Up", "labels": []}},
            {"store": {"id": 3, "address": "tikv-2:20160", "state_name": "Up", "labels": []}},
        ],
        connection_counts={"tidb/tidb-0": 6, "tidb/tidb-1": 2},
        control_script={},
    )
    params = {
        "reserve_tikv": "tikv/tikv-3",
        "retire_tikv": "tikv/tikv-2",
        "drain_backend": "tidb/tidb-1",
        "placement_table": "ops.maintenance_tracking",
        "placement_expected_constraint": "[+zone=zone4]",
    }
    result = maintenance_final_state(port, port.control_connection(), None, params)
    assert result["passed"] is False
    assert result["facts"]["placement_satisfied"]["state"] == "NO-ROW"
    assert result["facts"]["store_retired"]["satisfied"] is False
    assert result["facts"]["tidb_drain"]["satisfied"] is False


def test_placement_satisfied_requires_expected_constraint_text() -> None:
    port = FakeTiDBPort()
    converged_wrong_constraint = _SqlConn((
        ("TABLE ops.maintenance_tracking", 'CONSTRAINTS="[+zone=zone1]" FOLLOWERS=2', "SCHEDULED"),
    ))
    pending_pin = _SqlConn((
        ("TABLE ops.maintenance_tracking", 'CONSTRAINTS="[+zone=zone4]" FOLLOWERS=2', "PENDING"),
    ))
    assert placement_satisfied(
        port, converged_wrong_constraint, "ops.maintenance_tracking", expected_constraint="[+zone=zone4]",
    )["satisfied"] is False
    assert placement_satisfied(
        port, pending_pin, "ops.maintenance_tracking", expected_constraint="[+zone=zone4]",
    )["satisfied"] is False


def test_replica_safety_verifier_enforces_region_bounds() -> None:
    port = FakeTiDBPort(region_checks={
        "miss-peer": [{"id": 17}],
        "down-peer": [],
    })
    result = replica_safety_after_change(port, None, None, {"max_missing_peer_regions": 0, "max_down_peer_regions": 0})
    assert result["passed"] is False
    assert result["missing_peer_regions"] == 1

    ok = replica_safety_after_change(port, None, None, {"max_missing_peer_regions": 1, "max_down_peer_regions": 0})
    assert ok["passed"] is True


def test_maintenance_jobs_delivered_checks_ledger_terminals(tmp_path: Path) -> None:
    ledger = TrustedLedger("maintenance", tmp_path / "maintenance.jsonl")
    ledger.append_job_planned(
        job_id="mo_store_scaleout", service_id="maintenance", job_kind="store_scaleout",
        batch_version="MO-2026-001", input_snapshot={"target": "tikv/tikv-3"},
        submitted_at_monotonic=100.0, deadline_at_monotonic=200.0,
    )
    ledger.append_job_terminal(
        job_id="mo_store_scaleout", terminal=LedgerTerminal.INCOMPLETE_TIMEOUT,
        delivered_at_monotonic=None, result_digest=None,
    )
    view = LedgerView(ledger)
    result = maintenance_jobs_delivered(None, None, view, {})
    assert result["passed"] is False
    assert any("not delivered" in failure for failure in result["failures"])


def test_topology_driver_plans_and_delivers_jobs_through_the_core_ledger(tmp_path: Path) -> None:
    driver = _topology_driver(tmp_path)
    row = _work_order_rows(driver.clock)[0]
    driver._plan_job(row)
    assert driver.planned_deliverable_ids() == {row.deliverable_id}
    driver._deliver(row, LedgerTerminal.COMPLETED, {"satisfied": True, "target": row.target})
    assert driver.planned_deliverable_ids() == set()
    view = LedgerView(driver.maintenance_ledger)
    job = view.jobs()[0]
    assert job.job_id == row.deliverable_id
    assert job.terminal is LedgerTerminal.COMPLETED
    assert job.delivered_on_time is True

    # A decided job is never re-planned from a still-published row.
    driver._plan_job(row)
    assert len(LedgerView(driver.maintenance_ledger).jobs()) == 1


def test_driver_finalize_repeats_cleanly_after_ledger_finalize_outstanding(tmp_path: Path) -> None:
    """Repeated finalize: the runtime's ledger seal closes every open job
    (TrustedLedger.finalize_outstanding) while the driver still holds the key
    in its planned set; the driver's own stop-time finalize must skip the
    already-decided job instead of raising "terminal decided twice"."""
    driver = _topology_driver(tmp_path)
    row = _work_order_rows(driver.clock)[0]
    driver._plan_job(row)
    driver.maintenance_ledger.finalize_outstanding(driver.clock.monotonic())
    driver._finalize_outstanding_maintenance()
    driver.maintenance_ledger.seal()
    driver.maintenance_ledger.verify()
    job = LedgerView(driver.maintenance_ledger).jobs()[0]
    assert job.terminal is LedgerTerminal.INCOMPLETE_OUTSTANDING
    assert driver.planned_deliverable_ids() == set()
    # The key is terminal-decided whether this driver wrote the terminal or
    # the ledger seal decided it first; a surviving tick must never re-plan.
    assert driver.decided_deliverable_ids() == {row.deliverable_id}


def test_maintenance_poller_stops_before_the_runtime_seals_ledgers(tmp_path: Path) -> None:
    """The runtime stops arrivals, drains, then seals the trusted ledgers
    (engine._stop_before_evaluation) while the driver is still alive. The
    maintenance poller appends to the maintenance ledger, so it must stop in
    stop_new_requests/drain; keeping it alive past the seal deterministically
    produces "terminal decided twice" when it delivers against a job the
    ledger finalize already closed."""
    row = _work_order_rows(RealClock())[1]
    placement_shown = {"visible": False}

    def control_responder(sql: str, args):
        if sql == READ_CLIENT_POLICY_SQL:
            return (((1, 3000, 3, 200, 100, 600, "tidb/tidb-0", 50, None, 0),), 1)
        if sql == READ_MAINTENANCE_ORDERS_SQL:
            return ((
                (row.order_id, row.deliverable_id, row.kind, row.target,
                 row.deadline_seconds, row.published_at_ms),
            ), 1)
        if sql == SHOW_PLACEMENT_SQL:
            if not placement_shown["visible"]:
                return ((), 0)
            return (((
                f"TABLE {row.target}",
                'LEARNERS=1 LEARNER_CONSTRAINTS="[+zone=zone4]"',
                "SCHEDULED",
            ),), 1)
        if sql.startswith("SELECT COUNT(*)"):
            return (((0,),), 1)
        return ((), 0)

    driver = _topology_driver(tmp_path, maintenance_poll_seconds=0.02, control_responder=control_responder)
    driver.start()
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and row.deliverable_id not in driver.planned_deliverable_ids():
        time.sleep(0.01)
    assert row.deliverable_id in driver.planned_deliverable_ids()

    # Engine shutdown sequence: stop arrivals, drain, then seal the ledgers.
    driver.stop_new_requests()
    driver.drain()
    driver.maintenance_ledger.finalize_outstanding(driver.clock.monotonic())
    driver.maintenance_ledger.seal()
    # The ledger no longer accepts events; the poller must never write again.
    placement_shown["visible"] = True
    driver.stop()

    assert driver._maintenance_errors == ()
    driver.maintenance_ledger.verify()
    job = LedgerView(driver.maintenance_ledger).jobs()[0]
    assert job.terminal is LedgerTerminal.INCOMPLETE_OUTSTANDING
    assert driver.planned_deliverable_ids() == set()


def test_verifier_registry_matches_implemented_verifier_ids() -> None:
    ids = [verifier_id for verifier_id, _callable in VERIFIERS]
    assert set(ids) == {"maintenance_final_state", "replica_safety_after_change", "maintenance_jobs_delivered"}


def test_tikv_byte_rate_report_is_normalized_to_bytes() -> None:
    parse = parse_bytes_per_sec
    assert parse("0KiB") == 0
    assert parse("1MiB") == 1024 * 1024
    assert parse("1.5MiB") == 1_572_864
    assert parse("512KiB") == 512 * 1024
    assert parse("2GiB") == 2 * 1024 ** 3
    assert parse(262144) == 262144
    with pytest.raises(ValueError, match="unparseable TiKV byte-rate value"):
        parse("fast")


def test_topology_declares_the_decoy_near_neighbor_store() -> None:
    """The decoy store is a regular node, Up from deployment start, with the
    same resources signature as the retire target — but the work order names
    only tikv/tikv-2. The work-order identity is the discriminator between the
    two same-signature stores."""
    spec = load_persistent_scenario(TOPOLOGY_YAML)
    node_ids = [node.node_id for node in spec.environment.nodes]
    assert "tikv-4" in node_ids
    roles = {node.node_id: node.role for node in spec.environment.nodes}
    assert roles["tikv-4"] == "tikv"  # a regular store, not the reserved node
    resources = {node.node_id: node.resources for node in spec.environment.nodes}
    assert resources["tikv-4"] == resources["tikv-2"]

    payload = _work_order_payload()
    assert payload["retire_tikv"] == "tikv/tikv-2"
    assert "tikv/tikv-4" not in str(payload)


def test_migration_link_delay_overlaps_the_drain_window_not_the_placement_deadline() -> None:
    """Coupled-event coupling, conservative form: the bounded link delay starts inside
    the drain delivery window (bias at 2700 concentrates connections on the
    drain backend; the drain deliverable falls due at publication+3300) while
    the placement deliverable deadline (publication+3000) stays untouched.
    Strength is unchanged; no deliverable deadline moved."""
    spec = load_persistent_scenario(TOPOLOGY_YAML)
    order_start = _event(spec, "maintenance_order_1").start_seconds
    delay_start = _event(spec, "migration_link_delay_1").start_seconds
    bias_start = _event(spec, "connection_pool_bias_1").start_seconds
    objective = [service for service in spec.services if service.service_id == "maintenance"][0]
    deadlines = {deliverable.deliverable_id: deliverable.deadline_seconds
                 for deliverable in objective.deliverables}

    placement_due = order_start + deadlines["mo_placement_satisfied"]
    drain_due = order_start + deadlines["mo_tidb_drain"]
    assert delay_start > placement_due, "the link delay must not overlap the placement delivery deadline"
    assert bias_start < delay_start < drain_due, (
        f"the link delay must overlap the drain delivery window: "
        f"delay_start={delay_start}, bias_start={bias_start}, drain_due={drain_due}"
    )
    payload = _event(spec, "migration_link_delay_1").payload
    assert int(payload["max_bytes_per_sec"]) == 524288  # strength unchanged


def test_drain_with_the_biased_pool_untouched_fails_honestly() -> None:
    """The pool bias concentrates real client connections on the drain backend
    (tidb/tidb-1); with the bias untouched the drain predicate is honestly
    unsatisfied and the final-state verifier names the violated deliverable."""
    port = FakeTiDBPort(
        stores=[
            {"store": {"id": 4, "address": "tikv-3:20160", "state_name": "Up", "labels": []}},
            {"store": {"id": 3, "address": "tikv-2:20160", "state_name": "Tombstone", "labels": []}},
        ],
        connection_counts={"tidb/tidb-0": 6, "tidb/tidb-1": 5},
        control_script={
            "SHOW PLACEMENT FOR TABLE ops.maintenance_tracking": (
                ("TABLE ops.maintenance_tracking", 'LEARNERS=1 LEARNER_CONSTRAINTS="[+zone=zone4]"', "SCHEDULED"),
            ),
        },
    )
    params = {
        "reserve_tikv": "tikv/tikv-3",
        "retire_tikv": "tikv/tikv-2",
        "drain_backend": "tidb/tidb-1",
        "placement_table": "ops.maintenance_tracking",
        "placement_expected_constraint": "[+zone=zone4]",
    }
    result = maintenance_final_state(port, port.control_connection(), None, params)
    assert result["passed"] is False
    assert any("tidb_drain not satisfied for 'tidb/tidb-1'" in failure for failure in result["failures"])
    assert result["facts"]["tidb_drain"]["remaining_connections"] == 5


def test_draining_the_decoy_store_does_not_satisfy_the_retire_deliverable() -> None:
    """Retiring the same-signature near-neighbor (tikv-4) "succeeds" locally —
    the decoy really is Tombstone — but the work-order deliverable is bound to
    tikv/tikv-2, so the final-state verifier rejects the wrong repair target."""
    decoy_retired = FakeTiDBPort(stores=[
        {"store": {"id": 4, "address": "tikv-3:20160", "state_name": "Up", "labels": []}},
        {"store": {"id": 3, "address": "tikv-2:20160", "state_name": "Up", "labels": []}},
        {"store": {"id": 5, "address": "tikv-4:20160", "state_name": "Tombstone", "labels": []}},
    ])
    # The decoy is genuinely retired: the predicate passes against it.
    assert store_retired_satisfied(decoy_retired, None, "tikv/tikv-4")["satisfied"] is True
    # ... yet the work-order target is untouched, so delivery fails honestly.
    assert store_retired_satisfied(decoy_retired, None, "tikv/tikv-2")["satisfied"] is False

    port = FakeTiDBPort(
        stores=[
            {"store": {"id": 4, "address": "tikv-3:20160", "state_name": "Up", "labels": []}},
            {"store": {"id": 3, "address": "tikv-2:20160", "state_name": "Up", "labels": []}},
            {"store": {"id": 5, "address": "tikv-4:20160", "state_name": "Tombstone", "labels": []}},
        ],
        connection_counts={"tidb/tidb-0": 6, "tidb/tidb-1": 0},
        control_script={
            "SHOW PLACEMENT FOR TABLE ops.maintenance_tracking": (
                ("TABLE ops.maintenance_tracking", 'LEARNERS=1 LEARNER_CONSTRAINTS="[+zone=zone4]"', "SCHEDULED"),
            ),
        },
    )
    params = {
        "reserve_tikv": "tikv/tikv-3",
        "retire_tikv": "tikv/tikv-2",
        "drain_backend": "tidb/tidb-1",
        "placement_table": "ops.maintenance_tracking",
        "placement_expected_constraint": "[+zone=zone4]",
    }
    result = maintenance_final_state(port, port.control_connection(), None, params)
    assert result["passed"] is False
    assert any("store_retired not satisfied for 'tikv/tikv-2'" in failure for failure in result["failures"])


def test_pool_bias_event_publishes_above_agent_publications() -> None:
    """The planned bias version is a floor: an agent publication of the shared
    client-config row before the bias event cannot defuse it, and the bias
    UPDATE only rewrites the connection columns."""
    published: list[tuple] = []
    state = {"applied": 4}

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
        workload_driver=AdoptingDriver(applied_version=4),
        control_responder=control_responder,
    )
    spec = load_persistent_scenario(TOPOLOGY_YAML)
    event = _event(spec, "connection_pool_bias_1")
    result = ConnectionPoolBiasCapability().activate(EventActivationContext(
        run_id="r", spec=spec, event=event, environment=port, clock=RealClock(),
    ))
    assert result.applied is not None
    assert result.applied.facts["config_version"] == 5
    assert result.applied.facts["connect_bias"] == "tidb/tidb-1"
    assert published and int(published[0][0]) == 5
    assert str(published[0][6]) == "tidb/tidb-1"
