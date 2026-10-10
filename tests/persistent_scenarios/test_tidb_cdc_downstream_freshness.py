"""Focused tests for tidb_cdc_downstream_freshness (tidb5-portfolio, instance 4).

Covers: the CDC spec shape (two oltp objectives, verifier-kind required state,
provisional calibration), business marker construction, version-aware pairing
(including replay tolerance), the fulfilment visibility driver (resolution,
expiry, batching, poll counts), the downstream batch worker (locked chunked
transaction with staging churn), instance verifiers over fakes, and the
capability activation surfaces.
"""

from __future__ import annotations

import re
import threading
from pathlib import Path

import pytest

from src.persistent_scenarios.backend.contracts import OwnershipMode
from src.persistent_scenarios.backend.tidb.capabilities.cdc import CAPABILITIES, VERIFIERS
from src.persistent_scenarios.backend.tidb.capabilities.cdc.capabilities import (
    CdcDownstreamBatchCapability,
    CdcOrderPeakCapability,
    CdcSchemaReleaseCapability,
)
from src.persistent_scenarios.backend.tidb.capabilities.cdc.driver import (
    DownstreamBatchWorker,
    _FulfilmentService,
    _OrderWriter,
)
from src.persistent_scenarios.backend.tidb.capabilities.cdc.markers import (
    UpstreamCommittedOrder,
    pair_orders,
)
from src.persistent_scenarios.backend.tidb.capabilities.cdc.schema import (
    DOWNSTREAM_DATABASE,
    UPSTREAM_DATABASE,
    marker_for,
    schema_statements,
)
from src.persistent_scenarios.backend.tidb.capabilities.cdc.verifiers import (
    CdcDownstreamCaughtUpVerifier,
    CdcMarkerPairingVerifier,
    CdcUpstreamLedgerConservationVerifier,
    CdcVisibilityDeadlineVerifier,
)
from src.persistent_scenarios.model.enums import DatabaseSystem, LoadClass
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.persistent_scenarios.runtime.clock import FakeClock, RealClock
from src.persistent_scenarios.runtime.ledger import (
    AttemptOutcome,
    LedgerTerminal,
    LedgerView,
    TransactionAttempt,
    TrustedLedger,
)

YAML_PATH = Path("src/persistent_scenarios/tidb/tidb_cdc_downstream_freshness.yaml")


# ---------------------------------------------------------------------------
# fakes


class ScriptedCursor:
    """Answers SELECTs from substring-keyed row sources; records every statement."""

    def __init__(self):
        self.executed: list[str] = []
        self._sources: list[tuple[str, object]] = []
        self._last = ""

    def on(self, substring: str, rows):
        self._sources.append((substring, rows))
        return self

    def execute(self, sql, args=()):
        self.executed.append(sql)
        self._last = sql

    def fetchall(self):
        for substring, rows in self._sources:
            if substring in self._last:
                return rows() if callable(rows) else rows
        raise AssertionError(f"no scripted rows for SQL: {self._last!r}")

    def close(self):
        pass


class ReadModelCursor:
    """Stands in for the downstream read-model table: stateful rows by order id."""

    def __init__(self, rows: dict[int, tuple[int, str, str]]):
        self.rows = dict(rows)
        self.executed: list[str] = []

    def execute(self, sql, args=()):
        self.executed.append(sql)
        self._last = sql

    def fetchall(self):
        # rows[oid] is (version, state, marker); each query gets its own projection
        if "SELECT order_id, version, state, marker" in self._last:
            ids = [int(x) for x in re.search(r"IN \(([^)]*)\)", self._last).group(1).split(",")]
            return [tuple((oid, *self.rows[oid])) for oid in ids if oid in self.rows]
        if "SELECT order_id, version, marker" in self._last:
            ids = [int(x) for x in re.search(r"IN \(([^)]*)\)", self._last).group(1).split(",")]
            return [(oid, self.rows[oid][0], self.rows[oid][2]) for oid in ids if oid in self.rows]
        if "SELECT order_id FROM" in self._last and "FOR UPDATE" in self._last:
            return [(oid,) for oid in sorted(self.rows, reverse=True)]
        raise AssertionError(f"no read-model answer for SQL: {self._last!r}")

    def close(self):
        pass


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor

    def close(self):
        pass


def _nolog(message: str) -> None:
    raise AssertionError(f"driver logged unexpectedly: {message}")


def append_commit(ledger: TrustedLedger, business_id: str, planned: float, completed: float,
                  deadline: float, digest: str | None) -> None:
    ledger.append_planned_transaction(
        business_id=business_id, service_id="fulfilment_visibility", tx_kind="order_visibility",
        planned_at_monotonic=planned, deadline_at_monotonic=deadline)
    ledger.append_transaction_attempt(
        business_id=business_id,
        attempt=TransactionAttempt(attempt_index=1, started_at_monotonic=planned,
                                   ended_at_monotonic=completed,
                                   outcome=AttemptOutcome.COMMITTED if digest else AttemptOutcome.TIMED_OUT,
                                   detail={}))
    ledger.append_transaction_terminal(
        business_id=business_id,
        terminal=LedgerTerminal.COMPLETED if digest else LedgerTerminal.INCOMPLETE_TIMEOUT,
        completed_at_monotonic=completed if digest else None, result_digest=digest)


# ---------------------------------------------------------------------------
# spec shape


def test_cdc_spec_loads_with_two_oltp_objectives() -> None:
    s = load_persistent_scenario(YAML_PATH)
    assert s.system is DatabaseSystem.TIDB
    oltp = [service for service in s.services if service.load_class is LoadClass.OLTP]
    assert {service.service_id for service in oltp} == {"orders", "fulfilment_visibility"}
    orders = next(service for service in oltp if service.service_id == "orders")
    visibility = next(service for service in oltp if service.service_id == "fulfilment_visibility")
    assert orders.min_success_fraction == 0.999
    assert visibility.deadline_seconds > orders.deadline_seconds


def test_cdc_required_state_uses_verifier_kind_until_scope_vocabulary_lands() -> None:
    """TIDB-REQ-001 is unresolved: TiDB scopes are expressed through verifiers."""
    s = load_persistent_scenario(YAML_PATH)
    verifier_items = [item for item in s.required_state if item.kind == "verifier"]
    assert [item.verifier_id for item in verifier_items] == ["cdc_downstream_caught_up"]
    assert s.calibration.status == "development_provisional"


def test_cdc_schema_sides_share_the_business_shape() -> None:
    statements = schema_statements()
    assert UPSTREAM_DATABASE == DOWNSTREAM_DATABASE == "fulfil"
    assert any("orders" in sql for sql in statements.upstream)
    assert any("batch_control" in sql for sql in statements.downstream)


# ---------------------------------------------------------------------------
# business markers and pairing


def test_marker_for_is_deterministic_and_version_decodable() -> None:
    first = marker_for(1000001, 2, 900.5)
    assert first == marker_for(1000001, 2, 900.5)
    assert first != marker_for(1000001, 2, 900.6)
    # the driver recovers the version from the marker alone
    assert int(first.split("-v")[1].split("-")[0]) == 2


def _upstream(order_id: int, version: int, marker: str) -> UpstreamCommittedOrder:
    return UpstreamCommittedOrder(order_id=order_id, version=version, state="paid",
                                  amount="1.00", marker=marker)


def test_pair_orders_passes_on_matching_version_and_marker() -> None:
    upstream = {7: _upstream(7, 1, "m7-v1")}
    cursor = ReadModelCursor({7: (1, "paid", "m7-v1")})
    report = pair_orders(cursor, upstream)
    assert report.complete and report.checked == 1


def test_pair_orders_reports_missing_and_stale_rows() -> None:
    upstream = {7: _upstream(7, 2, "m7-v2"), 8: _upstream(8, 1, "m8-v1")}
    cursor = ReadModelCursor({7: (1, "paid", "m7-v1")})  # order 8 entirely missing
    report = pair_orders(cursor, upstream)
    assert not report.complete
    assert report.missing == (8,)
    assert report.version_mismatch == ((7, 2, 1),)


def test_pair_orders_requires_marker_equality_only_for_latest_version() -> None:
    upstream = {9: _upstream(9, 1, "m9-v1-early")}
    # the read model already serves version 2: the v1 commit must have been
    # applied and overwritten, so the historical marker cannot be observed
    cursor = ReadModelCursor({9: (2, "shipped", "m9-v2-later")})
    report = pair_orders(cursor, upstream)
    assert report.complete


def test_pair_orders_flags_corrupted_marker_at_same_version() -> None:
    upstream = {9: _upstream(9, 1, "m9-v1-early")}
    cursor = ReadModelCursor({9: (1, "paid", "different")})
    report = pair_orders(cursor, upstream)
    assert not report.complete
    assert report.marker_mismatch == (9,)


def test_pair_orders_tolerates_replayed_apply_at_same_version() -> None:
    """At-least-once sink replay re-delivers the identical (key, version, marker);
    idempotency is decided by business identity, not transport dedup."""
    upstream = {11: _upstream(11, 1, "m11-v1")}
    cursor = ReadModelCursor({11: (1, "paid", "m11-v1")})
    for _ in range(3):  # replay the same downstream state any number of times
        assert pair_orders(cursor, upstream).complete


# ---------------------------------------------------------------------------
# fulfilment visibility driver


def _fulfilment(tmp_path, clock, downstream_cursor, deadline=10.0):
    ledger = TrustedLedger("cdc_visibility", tmp_path / "visibility.jsonl")
    service = _FulfilmentService(
        factories=type("F", (), {"downstream": lambda self: FakeConnection(downstream_cursor)})(),
        ledger=ledger, clock=clock, visibility_deadline_seconds=deadline, log=_nolog)
    return service, ledger


def test_visibility_resolves_visible_marker_and_records_latency(tmp_path) -> None:
    clock = FakeClock()
    cursor = ReadModelCursor({})
    service, ledger = _fulfilment(tmp_path, clock, cursor)
    service.record_commit(1001, "m001001-v001-00001", committed_at=0.0)
    cursor.rows[1001] = (1, "paid", "m001001-v001-00001")
    clock.advance(2.0)
    service._resolve_due(cursor)
    assert service.outstanding() == 0
    assert service.resolved == [2.0]
    records = LedgerView(ledger).logical_transactions()
    assert records[0].terminal is LedgerTerminal.COMPLETED
    assert records[0].good  # 2.0s <= 10.0s deadline
    assert records[0].attempts[0].detail["downstream_version"] == 1


def test_visibility_resolves_when_newer_version_served(tmp_path) -> None:
    """The v1 marker was overwritten by the confirm update; serving v2 proves v1 applied."""
    clock = FakeClock()
    cursor = ReadModelCursor({1002: (2, "shipped", "m001002-v002-00002")})
    service, ledger = _fulfilment(tmp_path, clock, cursor)
    service.record_commit(1002, "m001002-v001-00001", committed_at=0.0)
    clock.advance(3.0)
    service._resolve_due(cursor)
    assert service.resolved == [3.0]
    assert LedgerView(ledger).logical_transactions()[0].terminal is LedgerTerminal.COMPLETED


def test_visibility_expires_past_deadline_without_row(tmp_path) -> None:
    clock = FakeClock()
    cursor = ReadModelCursor({})
    service, ledger = _fulfilment(tmp_path, clock, cursor, deadline=10.0)
    service.record_commit(1003, "m001003-v001-00001", committed_at=0.0)
    clock.advance(5.0)
    service._resolve_due(cursor)  # before deadline: stays pending
    assert service.outstanding() == 1
    assert service.expired == 0
    clock.advance(5.0)  # now == deadline
    service._resolve_due(cursor)
    assert service.outstanding() == 0
    assert service.expired == 1
    record = LedgerView(ledger).logical_transactions()[0]
    assert record.terminal is LedgerTerminal.INCOMPLETE_TIMEOUT
    assert not record.good
    assert record.result_digest is None


def test_visibility_polls_all_pending_in_one_batched_statement(tmp_path) -> None:
    clock = FakeClock()
    cursor = ReadModelCursor({})
    service, _ledger = _fulfilment(tmp_path, clock, cursor)
    for order_id in (2001, 2002, 2003):
        service.record_commit(order_id, f"m{order_id:09d}-v001-00001", committed_at=0.0)
    clock.advance(1.0)
    service._resolve_due(cursor)
    polls = [sql for sql in cursor.executed if "SELECT order_id, version, marker" in sql]
    assert len(polls) == 1
    assert all(str(oid) in polls[0] for oid in (2001, 2002, 2003))


def test_visibility_poll_count_grows_while_pending(tmp_path) -> None:
    clock = FakeClock()
    cursor = ReadModelCursor({})
    service, ledger = _fulfilment(tmp_path, clock, cursor, deadline=100.0)
    service.record_commit(3001, "m003001-v001-00001", committed_at=0.0)
    for _ in range(4):
        clock.advance(1.0)
        service._resolve_due(cursor)
    clock.advance(1.0)
    cursor.rows[3001] = (1, "paid", "m003001-v001-00001")
    service._resolve_due(cursor)
    attempt = LedgerView(ledger).logical_transactions()[0].attempts[0]
    assert attempt.detail["poll_count"] == 5


def test_visibility_facts_report_counts_and_percentiles(tmp_path) -> None:
    clock = FakeClock()
    cursor = ReadModelCursor({})
    service, _ledger = _fulfilment(tmp_path, clock, cursor)
    service.record_commit(4001, "m004001-v001-00001", committed_at=0.0)
    cursor.rows[4001] = (1, "paid", "m004001-v001-00001")
    clock.advance(1.5)
    service._resolve_due(cursor)
    facts = service.facts()
    assert facts["resolved_count"] == 1
    assert facts["visibility_p50_seconds"] == 1.5
    assert facts["visibility_max_seconds"] == 1.5
    assert facts["expired_count"] == 0


def test_visibility_backlog_accumulates_then_drains_in_one_poll(tmp_path) -> None:
    """Sink backpressure leaves obligations queued (outstanding grows); once the
    read model catches up a single batched poll drains the whole backlog."""
    clock = FakeClock()
    cursor = ReadModelCursor({})
    service, ledger = _fulfilment(tmp_path, clock, cursor, deadline=100.0)
    for oid in (5001, 5002, 5003):
        service.record_commit(oid, f"m{oid:09d}-v001-00001", committed_at=0.0)
    clock.advance(1.0)
    service._resolve_due(cursor)  # nothing visible yet: full backlog
    assert service.outstanding() == 3
    assert service.facts()["outstanding"] == 3
    for oid in (5001, 5002, 5003):
        cursor.rows[oid] = (1, "paid", f"m{oid:09d}-v001-00001")
    clock.advance(1.0)
    service._resolve_due(cursor)
    assert service.outstanding() == 0
    polls = [sql for sql in cursor.executed if "SELECT order_id, version, marker" in sql]
    assert len(polls) == 2  # backlog poll + drain poll, never one poll per order
    facts = service.facts()
    assert facts["resolved_count"] == 3 and facts["expired_count"] == 0
    latencies = [record.completed_at_monotonic - record.planned_at_monotonic
                 for record in LedgerView(ledger).logical_transactions()]
    assert len(latencies) == 3 and all(1.0 <= latency <= 2.0 for latency in latencies)


def test_capabilities_never_fabricate_prevented_evidence() -> None:
    """These capabilities inject external business facts; no trusted protection
    state legitimately blocks them, so every activation either applies with
    evidence or raises - infrastructure and not-reproduced failures propagate."""
    import inspect

    from src.persistent_scenarios.backend.tidb.capabilities.cdc import capabilities as caps_mod
    source = inspect.getsource(caps_mod)
    assert "prevented=PreventionEvidence" not in source
    assert "prevented=None" in source  # the applied path always declares no prevention


# ---------------------------------------------------------------------------
# order writer: source commit creates the downstream visibility obligation


def test_order_writer_commit_feeds_visibility_sink(tmp_path) -> None:
    ledger = TrustedLedger("cdc_orders", tmp_path / "orders.jsonl")
    cursor = ScriptedCursor()
    clock = FakeClock()
    sink_calls = []
    writer = _OrderWriter(
        factories=type("F", (), {"upstream": lambda self: FakeConnection(cursor)})(),
        ledger=ledger, clock=clock, orders_deadline_seconds=5.0,
        confirm_fraction=0.0, first_order_id=1_000_000, log=_nolog)
    writer.attach_visibility_sink(lambda oid, marker, at: sink_calls.append((oid, marker, at)))
    writer._submit_one(cursor)
    assert sink_calls, "every upstream commit must open a visibility obligation"
    order_id, marker, _at = sink_calls[0]
    assert order_id == 1_000_000
    assert int(marker.split("-v")[1].split("-")[0]) == 1
    record = LedgerView(ledger).logical_transactions()[0]
    assert record.terminal is LedgerTerminal.COMPLETED
    assert record.result_digest == f"1000000:1:paid:{marker}"


# ---------------------------------------------------------------------------
# downstream batch worker: locked chunked transaction with staging churn


def _batch_worker(cursor) -> DownstreamBatchWorker:
    # every batch transaction locks recent read-model rows; script that SELECT
    cursor.on("FOR UPDATE", [(6_000_000,)])
    return DownstreamBatchWorker(
        factories=type("F", (), {"downstream": lambda self: FakeConnection(cursor)})(),
        clock=FakeClock(), log=_nolog)


def test_batch_worker_locks_reads_then_inserts_in_chunks_and_drops_previous() -> None:
    cursor = ScriptedCursor()
    worker = _batch_worker(cursor)
    worker.batches_run = 1
    worker.rows_written = 2000
    worker._run_batch(cursor, 2500, "xx")
    inserts = [sql for sql in cursor.executed if sql.startswith("INSERT IGNORE")]
    assert len(inserts) == 3  # 1000 + 1000 + 500
    assert "ORDER BY order_id DESC LIMIT 200 FOR UPDATE" in cursor.executed[1]
    assert cursor.executed[0] == "BEGIN" and cursor.executed[-1] == "COMMIT"
    assert any(sql.startswith("DELETE FROM") and "batch_no = 0" in sql for sql in cursor.executed)
    assert worker.rows_written == 4500 and worker.batches_run == 2


def test_batch_worker_first_run_has_no_previous_batch_to_drop() -> None:
    cursor = ScriptedCursor()
    worker = _batch_worker(cursor)
    worker._run_batch(cursor, 1000, "xx")
    assert not any(sql.startswith("DELETE FROM") for sql in cursor.executed)


def test_batch_worker_read_model_locks_enable_sink_backpressure() -> None:
    """The batch transaction must hold row locks on the read model so the sink
    apply queues behind a real downstream lock (contract 7.2), not an artificial delay."""
    cursor = ScriptedCursor()
    worker = _batch_worker(cursor)
    worker._run_batch(cursor, 1, "xx")
    lock_sql = cursor.executed[1]
    assert f"FROM {DOWNSTREAM_DATABASE}.orders" in lock_sql and "FOR UPDATE" in lock_sql


# ---------------------------------------------------------------------------
# verifiers


def test_verifier_registry_exposes_all_instance_verifiers() -> None:
    assert [v.verifier_id for v in VERIFIERS] == [
        "cdc_marker_pairing", "cdc_upstream_ledger_conservation",
        "cdc_downstream_caught_up", "cdc_visibility_deadline"]


def test_marker_pairing_verifier_passes_on_complete_watermark() -> None:
    upstream = ScriptedCursor().on("SELECT order_id, version, marker", [(1000000, 1, "m1"), (1000001, 1, "m2")])
    downstream = ScriptedCursor().on("SELECT order_id, version, state, marker",
                                     [(1000000, 1, "paid", "m1"), (1000001, 1, "paid", "m2")])
    detail = CdcMarkerPairingVerifier()(
        {"from_order_id": 1000000, "through_order_id": 1000001},
        upstream=FakeConnection(upstream), downstream=FakeConnection(downstream), ledger_view=None)
    assert detail["passed"] and detail["checked"] == 2


def test_marker_pairing_verifier_fails_on_downstream_hole() -> None:
    upstream = ScriptedCursor().on("SELECT order_id, version, marker",
                                   [(1000000, 1, "m1"), (1000001, 1, "m2")])
    downstream = ScriptedCursor().on("SELECT order_id, version, state, marker",
                                     [(1000000, 1, "paid", "m1")])  # hole: 1000001 missing
    detail = CdcMarkerPairingVerifier()(
        {"from_order_id": 1000000, "through_order_id": 1000001},
        upstream=FakeConnection(upstream), downstream=FakeConnection(downstream), ledger_view=None)
    assert not detail["passed"]
    assert detail["missing_order_ids"] == [1000001]


def test_upstream_ledger_conservation_agrees_when_rows_match_ledger(tmp_path) -> None:
    ledger = TrustedLedger("cdc_orders", tmp_path / "orders.jsonl")
    ledger.append_planned_transaction(
        business_id="order-1000000", service_id="orders", tx_kind="submit_order",
        planned_at_monotonic=0.0, deadline_at_monotonic=5.0)
    ledger.append_transaction_attempt(
        business_id="order-1000000",
        attempt=TransactionAttempt(1, 0.0, 0.1, AttemptOutcome.COMMITTED, {}))
    ledger.append_transaction_terminal(
        business_id="order-1000000", terminal=LedgerTerminal.COMPLETED,
        completed_at_monotonic=0.1, result_digest="1000000:1:paid:m1")
    upstream = ScriptedCursor().on("SELECT order_id, version, marker", [(1000000, 1, "m1")])
    detail = CdcUpstreamLedgerConservationVerifier()(
        {"from_order_id": 1000000}, upstream=FakeConnection(upstream), downstream=None,
        ledger_view=LedgerView(ledger))
    assert detail["passed"]
    assert detail["ledger_orders"] == detail["workload_db_rows"] == 1


def test_upstream_ledger_conservation_folds_in_place_updates(tmp_path) -> None:
    """The orders table keeps one row per business key: a row already at the
    confirm commit (v2) proves the v1 commit applied - it is not a loss."""
    ledger = TrustedLedger("cdc_orders", tmp_path / "orders.jsonl")
    for business_id, digest in (("order-1", "1:1:paid:m1"), ("order-1-confirm", "1:2:shipped:m2")):
        ledger.append_planned_transaction(
            business_id=business_id, service_id="orders", tx_kind="submit_order",
            planned_at_monotonic=0.0, deadline_at_monotonic=5.0)
        ledger.append_transaction_attempt(
            business_id=business_id,
            attempt=TransactionAttempt(1, 0.0, 0.1, AttemptOutcome.COMMITTED, {}))
        ledger.append_transaction_terminal(
            business_id=business_id, terminal=LedgerTerminal.COMPLETED,
            completed_at_monotonic=0.1, result_digest=digest)
    upstream = ScriptedCursor().on("SELECT order_id, version, marker", [(1, 2, "m2")])
    detail = CdcUpstreamLedgerConservationVerifier()(
        {"from_order_id": 1}, upstream=FakeConnection(upstream), downstream=None,
        ledger_view=LedgerView(ledger))
    assert detail["passed"]
    assert detail["ledger_orders"] == 1  # two commits, one business row


def test_upstream_ledger_conservation_flags_fabricated_and_lost_rows(tmp_path) -> None:
    ledger = TrustedLedger("cdc_orders", tmp_path / "orders.jsonl")
    ledger.append_planned_transaction(
        business_id="order-1000000", service_id="orders", tx_kind="submit_order",
        planned_at_monotonic=0.0, deadline_at_monotonic=5.0)
    ledger.append_transaction_attempt(
        business_id="order-1000000",
        attempt=TransactionAttempt(1, 0.0, 0.1, AttemptOutcome.COMMITTED, {}))
    ledger.append_transaction_terminal(
        business_id="order-1000000", terminal=LedgerTerminal.COMPLETED,
        completed_at_monotonic=0.1, result_digest="1000000:1:paid:m1")
    # the DB lost the ledger commit and fabricated an unknown row
    upstream = ScriptedCursor().on("SELECT order_id, version, marker", [(1000005, 1, "mx")])
    detail = CdcUpstreamLedgerConservationVerifier()(
        {"from_order_id": 1000000}, upstream=FakeConnection(upstream), downstream=None,
        ledger_view=LedgerView(ledger))
    assert not detail["passed"]
    assert detail["ledger_missing_in_db"] == [
        {"order_id": 1000000, "ledger_version": 1, "db_version": None}]
    assert detail["db_missing_in_ledger"] == [{"order_id": 1000005, "db_version": 1}]


def test_upstream_ledger_conservation_excludes_declared_non_ledger_rows(tmp_path) -> None:
    """Fault-injection probe orders are source commits authored by the
    capability, not trading obligations: declared ids leave the pairing
    universe on both sides instead of counting as fabricated rows."""
    ledger = TrustedLedger("cdc_orders", tmp_path / "orders.jsonl")
    ledger.append_planned_transaction(
        business_id="order-1000000", service_id="orders", tx_kind="submit_order",
        planned_at_monotonic=0.0, deadline_at_monotonic=5.0)
    ledger.append_transaction_attempt(
        business_id="order-1000000",
        attempt=TransactionAttempt(1, 0.0, 0.1, AttemptOutcome.COMMITTED, {}))
    ledger.append_transaction_terminal(
        business_id="order-1000000", terminal=LedgerTerminal.COMPLETED,
        completed_at_monotonic=0.1, result_digest="1000000:1:paid:m1")
    upstream = ScriptedCursor().on("SELECT order_id, version, marker",
                                   [(1000000, 1, "m1"), (8800000, 1, "probe-8800000")])
    detail = CdcUpstreamLedgerConservationVerifier()(
        {"from_order_id": 1000000, "exclude_order_ids": [8800000]},
        upstream=FakeConnection(upstream), downstream=None,
        ledger_view=LedgerView(ledger))
    assert detail["passed"]
    assert detail["workload_db_rows"] == 1
    assert detail["db_missing_in_ledger_count"] == 0


def test_upstream_ledger_conservation_flags_stale_row_behind_latest_commit(tmp_path) -> None:
    """A row still serving v1 while the ledger completed the v2 confirm is a
    lost update, not a pass."""
    ledger = TrustedLedger("cdc_orders", tmp_path / "orders.jsonl")
    for business_id, digest in (("order-1", "1:1:paid:m1"), ("order-1-confirm", "1:2:shipped:m2")):
        ledger.append_planned_transaction(
            business_id=business_id, service_id="orders", tx_kind="submit_order",
            planned_at_monotonic=0.0, deadline_at_monotonic=5.0)
        ledger.append_transaction_attempt(
            business_id=business_id,
            attempt=TransactionAttempt(1, 0.0, 0.1, AttemptOutcome.COMMITTED, {}))
        ledger.append_transaction_terminal(
            business_id=business_id, terminal=LedgerTerminal.COMPLETED,
            completed_at_monotonic=0.1, result_digest=digest)
    upstream = ScriptedCursor().on("SELECT order_id, version, marker", [(1, 1, "m1")])
    detail = CdcUpstreamLedgerConservationVerifier()(
        {"from_order_id": 1}, upstream=FakeConnection(upstream), downstream=None,
        ledger_view=LedgerView(ledger))
    assert not detail["passed"]
    assert detail["ledger_missing_in_db"] == [
        {"order_id": 1, "ledger_version": 2, "db_version": 1}]


def test_visibility_deadline_verifier_enforces_success_fraction(tmp_path) -> None:
    ledger = TrustedLedger("cdc_visibility", tmp_path / "visibility.jsonl")
    append_commit(ledger, "order-1:v1", 0.0, 1.0, 10.0, "1:1:paid:m1")
    append_commit(ledger, "order-2:v1", 0.0, 20.0, 10.0, None)  # past deadline -> bad
    view = LedgerView(ledger)
    verifier = CdcVisibilityDeadlineVerifier()
    failed = verifier({"min_success_fraction": 0.99}, upstream=None, downstream=None, ledger_view=view)
    assert not failed["passed"] and failed["success_fraction"] == 0.5
    assert failed["worst_visible_seconds"] == 1.0
    passed = verifier({"min_success_fraction": 0.4}, upstream=None, downstream=None, ledger_view=view)
    assert passed["passed"]


def test_downstream_caught_up_verifier_checks_only_the_final_window(tmp_path) -> None:
    ledger = TrustedLedger("cdc_visibility", tmp_path / "visibility.jsonl")
    append_commit(ledger, "order-4:v1", 50.0, 51.0, 60.0, "4:1:paid:m4")
    append_commit(ledger, "order-5:v1", 100.0, 101.0, 110.0, "5:1:paid:m5")
    upstream = ScriptedCursor().on("SELECT order_id, version, state, amount, marker",
                                   [(5, 1, "paid", "5.25", "m5")])
    downstream = ScriptedCursor().on("SELECT order_id, version, state, marker",
                                     [(5, 1, "paid", "m5")])
    detail = CdcDownstreamCaughtUpVerifier()(
        {"window_seconds": 10}, upstream=FakeConnection(upstream),
        downstream=FakeConnection(downstream), ledger_view=LedgerView(ledger))
    assert detail["passed"] and detail["window_order_count"] == 1


def test_downstream_caught_up_verifier_fails_on_window_hole(tmp_path) -> None:
    ledger = TrustedLedger("cdc_visibility", tmp_path / "visibility.jsonl")
    append_commit(ledger, "order-5:v1", 100.0, 101.0, 110.0, "5:1:paid:m5")
    upstream = ScriptedCursor().on("SELECT order_id, version, state, amount, marker",
                                   [(5, 1, "paid", "5.25", "m5")])
    downstream = ScriptedCursor().on("SELECT order_id, version, state, marker", [])
    detail = CdcDownstreamCaughtUpVerifier()(
        {"window_seconds": 10}, upstream=FakeConnection(upstream),
        downstream=FakeConnection(downstream), ledger_view=LedgerView(ledger))
    assert not detail["passed"] and detail["missing_order_ids"] == [5]


# ---------------------------------------------------------------------------
# capabilities


class SequenceCountCursor:
    """Answers the batch-staging marker query (MAX(batch_no)) and row counts
    with a scripted sequence (baseline, then advancement)."""

    def __init__(self, counts: list[int], control_rows: list[tuple]):
        self._counts = list(counts)
        self._control_rows = list(control_rows)
        self.executed: list[str] = []
        self._last = ""

    def execute(self, sql, args=()):
        self.executed.append(sql)
        self._last = sql

    def fetchall(self):
        if "COUNT(*)" in self._last or "MAX(batch_no)" in self._last:
            value = self._counts.pop(0) if len(self._counts) > 1 else self._counts[0]
            return [(value,)]
        return [self._control_rows.pop(0)]


class FakeEnvironment:
    def __init__(self, cursor):
        self._cursor = cursor

    def upstream(self):
        return FakeConnection(self._cursor)

    def downstream(self):
        return FakeConnection(self._cursor)


class FakeEvent:
    def __init__(self, event_id, entity, payload):
        self.event_id = event_id
        self.entity = entity
        self.payload = payload


class FakeContext:
    def __init__(self, event, cursor, clock=None):
        self.event = event
        self.environment = FakeEnvironment(cursor)
        self.clock = clock or RealClock()


def test_batch_capability_opens_window_and_keeps_operator_tuning() -> None:
    # control row previously retuned by the operator: note carries no campaign prefix
    cursor = SequenceCountCursor(counts=[10, 15], control_rows=[(1, 777, 9.0, "operator nightly tune")])
    capability = CdcDownstreamBatchCapability()
    result = capability.activate(FakeContext(
        FakeEvent("cdc_batch_window_1", "window-1",
                  {"batch_rows": 5000, "batch_pause_seconds": 0.2,
                   "window_seconds": 1, "campaign": "nightly-1"}),
        cursor))
    update = next(sql for sql in cursor.executed if sql.startswith("UPDATE"))
    assert "enabled = 1" in update and "batch_rows = 777" in update
    assert "batch_pause_seconds = 9.0" in update
    assert result.applied.facts["effective_schedule"] == {"batch_rows": 777, "batch_pause_seconds": 9.0}
    assert result.applied.facts["batches_advanced_during_activation"] == 5
    assert result.prevented is None
    declaration = capability.declaration(result.handle and FakeEvent("e", "window-1", {}))
    assert declaration.resources[0].mode is OwnershipMode.EXCLUSIVE


def test_batch_capability_campaign_window_uses_requested_schedule() -> None:
    cursor = SequenceCountCursor(counts=[0, 3], control_rows=[(0, 5000, 0.2, "campaign:nightly-0")])
    capability = CdcDownstreamBatchCapability()
    result = capability.activate(FakeContext(
        FakeEvent("cdc_batch_window_2", "window-2",
                  {"batch_rows": 4000, "batch_pause_seconds": 0.5,
                   "window_seconds": 1, "campaign": "nightly-1"}),
        cursor))
    update = next(sql for sql in cursor.executed if sql.startswith("UPDATE"))
    assert "batch_rows = 4000" in update and "batch_pause_seconds = 0.5" in update
    assert result.attempt.detail["operator_tuned_schedule"] is False


def test_batch_capability_cleanup_closes_only_campaign_windows() -> None:
    cursor = SequenceCountCursor(counts=[0, 1], control_rows=[(0, 10, 0.1, "campaign:nightly-1")])
    capability = CdcDownstreamBatchCapability()
    result = capability.activate(FakeContext(
        FakeEvent("e", "window-1",
                  {"batch_rows": 10, "batch_pause_seconds": 0.1, "window_seconds": 1,
                   "campaign": "nightly-1"}),
        cursor))
    capability.cleanup(result.handle)
    close = [sql for sql in cursor.executed if "enabled = 0" in sql]
    assert close and "LIKE 'campaign:%'" in close[0]


def test_batch_capability_rejects_unknown_payload_fields() -> None:
    cursor = SequenceCountCursor(counts=[0], control_rows=[(0, 1, 0.1, "x")])
    capability = CdcDownstreamBatchCapability()
    with pytest.raises(ValueError, match="unknown payload fields"):
        capability.activate(FakeContext(
            FakeEvent("e", "window-1", {"batch_rows": 1, "batch_pause_seconds": 0.1,
                                        "window_seconds": 1, "campaign": "c", "evil": 1}),
            cursor))


def test_batch_capability_alert_is_symptom_only() -> None:
    alert = CdcDownstreamBatchCapability().alert(context=None, handle=None)
    joined = " ".join(alert.symptoms).lower() + alert.title.lower()
    assert alert.severity == "notice" and alert.category == "downstream_batch"
    for forbidden in ("cdc_downstream_batch", "changefeed", "batch_control", "update "):
        assert forbidden not in joined, f"alert leaks mechanism detail: {forbidden!r}"


class StagingDownstreamState:
    """Stateful downstream stand-in for the batch-window observation: models the
    real batch transaction shape (INSERT new batch + DELETE previous batch in
    one commit) so the staging row count returns to rest between runs while
    batch_no keeps advancing. Cursor views are per-connection; shared state is
    lock-guarded."""

    def __init__(self, control_row: tuple):
        self._lock = threading.Lock()
        self.enabled, self.batch_rows, self.batch_pause_seconds, self.note = control_row
        self._staging: dict[int, int] = {}  # batch_id -> batch_no
        self.marker_query = threading.Event()  # armed by the test per window

    @property
    def staging_row_count(self) -> int:
        with self._lock:
            return len(self._staging)

    @property
    def latest_batch_no(self) -> int:
        with self._lock:
            return max(self._staging.values(), default=-1)

    def execute(self, sql: str) -> list[tuple]:
        with self._lock:
            if "MAX(batch_no)" in sql:
                self.marker_query.set()
                return [(max(self._staging.values(), default=-1),)]
            if "SELECT enabled, batch_rows" in sql:
                return [(self.enabled, self.batch_rows, self.batch_pause_seconds, self.note)]
            if "FOR UPDATE" in sql:
                return [(order_id,) for order_id in range(200)]
            if sql.startswith("UPDATE"):
                self._apply_update(sql)
                return []
            if "INSERT IGNORE" in sql:
                for batch_id, batch_no in re.findall(r"\((\d+), (\d+), '", sql):
                    self._staging.setdefault(int(batch_id), int(batch_no))
                return []
            if sql.startswith("DELETE"):
                target = int(re.search(r"batch_no = (\d+)", sql).group(1))
                self._staging = {bid: no for bid, no in self._staging.items() if no != target}
                return []
            if sql in ("BEGIN", "COMMIT"):
                return []
            raise AssertionError(f"staging fake has no answer for SQL: {sql!r}")

    def _apply_update(self, sql: str) -> None:
        enabled = re.search(r"enabled = (\d+)", sql)
        rows = re.search(r"batch_rows = (\d+)", sql)
        pause = re.search(r"batch_pause_seconds = ([\d.]+)", sql)
        note = re.search(r"note = '([^']*)'", sql)
        if enabled:
            self.enabled = int(enabled.group(1))
        if rows:
            self.batch_rows = int(rows.group(1))
        if pause:
            self.batch_pause_seconds = float(pause.group(1))
        if note:
            self.note = note.group(1)


class _StagingCursor:
    """Per-connection cursor view over StagingDownstreamState."""

    def __init__(self, state: StagingDownstreamState):
        self._state = state
        self._result: list[tuple] = []

    def execute(self, sql, args=()):
        self._result = self._state.execute(sql)

    def fetchall(self):
        return self._result

    def close(self):
        pass


class _StagingEnvironment:
    def __init__(self, state: StagingDownstreamState):
        self._state = state

    def downstream(self):
        return FakeConnection(_StagingCursor(self._state))


class _StagingContext:
    """Activation context over the stateful staging environment."""

    def __init__(self, event, environment):
        self.event = event
        self.environment = environment
        self.clock = RealClock()


def _run_one_batch_after(trigger: threading.Event, worker: DownstreamBatchWorker,
                         state: StagingDownstreamState, batch_rows: int) -> None:
    """Stand-in for the always-on batch worker: run one real batch transaction
    as soon as the window's baseline marker is taken."""
    assert trigger.wait(10), "batch window never read the batch_no marker"
    worker._run_batch(_StagingCursor(state), batch_rows, "x" * 512)


def test_batch_window_two_observed_through_batch_no_marker_when_row_count_stays_flat() -> None:
    """Regression: each batch transaction writes the new batch and drops the
    previous one in one commit, so after the first run the staging row count
    never leaves its resting value; a count-baseline observation predicate
    made the t=65 rerun of window 2 unobservable. The window must be observed
    through the batch_no marker stream instead."""
    state = StagingDownstreamState((0, 5000, 0.2, "batch window closed"))
    capability = CdcDownstreamBatchCapability()
    worker = DownstreamBatchWorker(
        factories=type("F", (), {"downstream": lambda self: FakeConnection(_StagingCursor(state))})(),
        clock=FakeClock(), log=_nolog)

    # window 1: the worker runs one real batch transaction once the window's
    # baseline marker is taken; the marker advances -1 -> 0
    state.marker_query = threading.Event()
    helper = threading.Thread(
        target=_run_one_batch_after, args=(state.marker_query, worker, state, 5000), daemon=True)
    helper.start()
    result1 = capability.activate(_StagingContext(
        FakeEvent("cdc_batch_window_1", "window-1",
                  {"batch_rows": 5000, "batch_pause_seconds": 0.2,
                   "window_seconds": 1, "campaign": "nightly-1"}),
        _StagingEnvironment(state)))
    helper.join(10)
    capability.cleanup(result1.handle)
    assert result1.applied.facts["batches_advanced_during_activation"] == 1
    assert state.staging_row_count == 5000  # one batch at rest

    # window 2: the batch transaction keeps the row count flat (insert new +
    # drop previous in one commit); only batch_no advances - the window must
    # still be observed
    count_before = state.staging_row_count
    state.marker_query = threading.Event()
    helper = threading.Thread(
        target=_run_one_batch_after, args=(state.marker_query, worker, state, 5000), daemon=True)
    helper.start()
    result2 = capability.activate(_StagingContext(
        FakeEvent("cdc_batch_window_2", "window-2",
                  {"batch_rows": 5000, "batch_pause_seconds": 0.2,
                   "window_seconds": 1, "campaign": "nightly-2"}),
        _StagingEnvironment(state)))
    helper.join(10)
    capability.cleanup(result2.handle)
    assert state.staging_row_count == count_before  # the count signal is flat
    assert state.latest_batch_no == 1               # only the marker advanced
    assert result2.applied.facts["batches_advanced_during_activation"] == 1


def test_order_peak_capability_raises_rate_and_reports_growth() -> None:
    # SequenceCountCursor serves the baseline COUNT then the grown COUNT; the
    # control-row read answers the previous traffic rate
    cursor = SequenceCountCursor(counts=[30, 32], control_rows=[(4.0,)])
    capability = CdcOrderPeakCapability()
    result = capability.activate(FakeContext(
        FakeEvent("cdc_order_peak_1", "peak-1",
                  {"target_orders_per_sec": 12.0, "note": "order peak"}),
        cursor))
    update = next(sql for sql in cursor.executed if sql.startswith("UPDATE"))
    assert "target_orders_per_sec = 12.0" in update
    assert result.applied.facts["rows_added_during_activation"] == 2
    assert result.applied.facts["target_orders_per_sec"] == 12.0
    assert result.prevented is None


def test_schema_release_capability_applies_drift_then_releases_schema() -> None:
    # upstream: nothing scripted needed for DDL/probe (they execute blind);
    # downstream: processlist lists two sink sessions, probe stays invisible
    # (empty tuple = the real fetchall shape of "no such row"); upstream also
    # answers the real GC surfaces (retention GUC + tikv_gc_safe_point)
    cursor = ScriptedCursor().on("SELECT id FROM information_schema.processlist", [(7,), (8,)]).on(
        "SELECT marker", ()).on(
        "SHOW VARIABLES LIKE 'tidb_gc_life_time'", [("tidb_gc_life_time", "30m0s")]).on(
        "SELECT VARIABLE_VALUE FROM mysql.tidb", [("2026-09-21 00:29:00.000",)])
    capability = CdcSchemaReleaseCapability()
    result = capability.activate(FakeContext(
        FakeEvent("cdc_schema_release_1", "release-1",
                  {"column_name": "gift_note", "column_type": "VARCHAR(128)",
                   "release_note": "gift note", "probe_order_id": 8800000,
                   "gc_pin_release_seconds": 600, "upstream_gc_life_time": "30m0s"}),
        cursor))
    assert "REVOKE ALTER ON *.* FROM 'cdc_sink'@'%'" in cursor.executed
    assert "KILL 7" in cursor.executed and "KILL 8" in cursor.executed
    assert any(sql.startswith("ALTER TABLE fulfil.orders ADD COLUMN gift_note") for sql in cursor.executed)
    assert result.applied.facts["probe_missing_seconds"] == 20.0
    assert result.applied.facts["invalidated_sink_sessions"] == 2
    assert result.applied.facts["probe_order_id"] == 8800000
    stall = result.applied.facts["stall"]
    assert stall["pin_release_after_seconds"] == 600.0
    assert stall["upstream_gc_life_time"] == "30m0s"
    assert stall["gc_life_time_seconds"] == 1800.0
    assert stall["tikv_gc_safe_point"] == "2026-09-21 00:29:00.000"
    assert result.prevented is None


def test_schema_release_capability_fails_closed_when_drift_does_not_stall() -> None:
    """If the probe order becomes visible downstream the mechanism did not reproduce;
    activation must raise, never fabricate applied evidence."""
    cursor = ScriptedCursor().on("SELECT id FROM information_schema.processlist", [(7,)]).on(
        "SELECT marker", [("probe-row",)])
    clock = FakeClock()
    capability = CdcSchemaReleaseCapability()
    context = FakeContext(
        FakeEvent("e", "release-1",
                  {"column_name": "gift_note", "column_type": "VARCHAR(128)",
                   "release_note": "note", "probe_order_id": 8800001,
                   "gc_pin_release_seconds": 600, "upstream_gc_life_time": "30m0s"}),
        cursor, clock=clock)
    # advance the clock from inside the probe so the 20s budget elapses without real waiting
    original_execute = cursor.execute

    def advancing_execute(sql, args=()):
        original_execute(sql, args)
        if "SELECT marker" in sql:
            clock.advance(25.0)

    cursor.execute = advancing_execute
    with pytest.raises(RuntimeError, match="did not stall downstream visibility"):
        capability.activate(context)


def test_schema_release_capability_alert_hides_mechanism() -> None:
    alert = CdcSchemaReleaseCapability().alert(context=None, handle=None)
    joined = " ".join(alert.symptoms) + alert.title
    assert alert.severity == "high" and alert.category == "downstream_visibility"
    for forbidden in ("cdc_sink", "REVOKE", "ALTER", "changefeed", "schema release"):
        assert forbidden not in joined, f"alert leaks root cause: {forbidden!r}"


def test_capability_registration_surface_is_complete() -> None:
    ids = {capability.capability_id for capability in CAPABILITIES}
    assert ids == {"cdc_downstream_batch", "cdc_schema_release", "cdc_order_peak"}


# ---------------------------------------------------------------------------
# runtime assembly


def test_driver_threads_join_without_shadowing_thread_internals(tmp_path) -> None:
    """Driver threads are Thread subclasses; an instance attribute named
    ``_stop`` shadows Thread._stop and breaks join() with
    'Event object is not callable'. Every driver thread must start and join
    cleanly (regression)."""
    from src.persistent_scenarios.backend.tidb.capabilities.cdc.driver import (
        _FulfilmentService,
        _OrderWriter,
    )
    ledger = TrustedLedger("cdc_join", tmp_path / "join.jsonl")
    writer = _OrderWriter(
        factories=type("F", (), {"upstream": lambda self: FakeConnection(ScriptedCursor())})(),
        ledger=ledger, clock=FakeClock(), orders_deadline_seconds=5.0,
        confirm_fraction=0.0, first_order_id=1, log=_nolog)
    fulfilment = _FulfilmentService(
        factories=type("F", (), {"downstream": lambda self: FakeConnection(ReadModelCursor({}))})(),
        ledger=ledger, clock=FakeClock(), visibility_deadline_seconds=5.0, log=_nolog)
    batch = _batch_worker(ScriptedCursor())
    for thread in (writer, fulfilment, batch):
        thread.shutdown()  # stop signal before start: run() exits immediately
        thread.start()
        thread.join(timeout=5)
        assert not thread.is_alive(), f"{thread.name} did not exit"


def test_cdc_runtime_requires_objectives_for_both_services(tmp_path) -> None:
    from dataclasses import replace

    from src.persistent_scenarios.backend.tidb.capabilities.cdc.driver import (
        CdcFreshnessWorkloadRuntime,
    )
    spec = load_persistent_scenario(YAML_PATH)
    spec = replace(
        spec,
        services=[s for s in spec.services if s.service_id != "fulfilment_visibility"])
    with pytest.raises(ValueError, match="fulfilment_visibility"):
        CdcFreshnessWorkloadRuntime(
            environment=None, spec=spec, run_id="r", clock=FakeClock(), factories=None,
            ledger_dir=tmp_path, log=_nolog)


def test_schema_release_closer_thread_targets_are_bounded() -> None:
    """Activation must not leave unbounded threads: every handle owns its closer."""
    import inspect
    source = inspect.getsource(CdcDownstreamBatchCapability.activate)
    assert "close_window_later" in source
    closer = inspect.getsource(CdcDownstreamBatchCapability.activate)
    assert "handle.closer.join(timeout=30)" in inspect.getsource(
        CdcDownstreamBatchCapability.cleanup)
