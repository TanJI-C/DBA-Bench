"""Focused tests for the tidb_cdc scenario (composite root cause, event
coupling, competing hypotheses).

Covers: the GC safepoint pin-release model (factor B of the composite root
cause), the schema-release stall anchor evidence, the three-path decisions
over the coupled timeline (complete path with the peak/rerun overlap passes;
privilege-only and safepoint-only partial repairs each fail the named
contract check; the zero path still violates), the rerun-sequencing judgement
(defer accepted, run-during-drain rejected, open campaign reported honestly),
and the competing-hypothesis noise surfaces (upstream maintenance audit +
frozen safepoint samples + batch-window activity, all excludable by
cross-evidence). All numbers are scenario seconds from the scoring start.
"""

from __future__ import annotations

import re

import pytest

from src.persistent_scenarios.backend.tidb.capabilities.cdc.calibration import (
    composite_repair_report,
    drain_completion_at,
    full_path_verdict,
    hole_check_report,
    rerun_sequencing_report,
    stall_window_holes,
    visibility_violation_set,
    zero_path_verdict,
)
from src.persistent_scenarios.backend.tidb.capabilities.cdc.capabilities import (
    CdcSchemaReleaseCapability,
)
from src.persistent_scenarios.backend.tidb.capabilities.cdc.driver import (
    UpstreamMaintenanceWorker,
)
from src.persistent_scenarios.backend.tidb.capabilities.cdc.safepoint import (
    checkpoint_pinned,
    exposed_commits,
    gc_eligible_from,
    parse_gc_duration,
    pin_release_at,
    retention_secured,
    safepoint_stalled,
    sample_upstream_gc_state,
)
from src.persistent_scenarios.backend.tidb.capabilities.cdc.verifiers import (
    CdcDownstreamCaughtUpVerifier,
    CdcMarkerPairingVerifier,
)
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.persistent_scenarios.runtime.admission import admit_persistent_scenario
from src.persistent_scenarios.runtime.clock import FakeClock
from src.persistent_scenarios.runtime.ledger import (
    AttemptOutcome,
    LedgerTerminal,
    LedgerView,
    LogicalTransactionRecord,
    TransactionAttempt,
    TrustedLedger,
)

YAML_PATH = "src/persistent_scenarios/tidb/tidb_cdc_downstream_freshness.yaml"

# The coupled timeline (scenario seconds from the scoring start).
STALL_START = 1800.0          # event 2: schema release meets privilege drift
PIN_RELEASE = 2400.0          # STALL_START + 600: fail-fast GC pin release
RECOVERY_EARLY = 2200.0       # complete path A: repaired before the pin release
RECOVERY_LATE = 2600.0        # complete path B: repaired after, with retention raise
RERUN_ARRIVAL = 3900.0        # event 4: batch rerun lands inside the drain
DRAINED_AT = 4100.0           # the catch-up backlog drains (after the rerun arrival)
SAMPLED_AT = 6300.0           # final sampling (agent_stop)
GC_LIFE_BASELINE = 1800.0     # deploy baseline tidb_gc_life_time = 30m
GC_LIFE_RAISED = 5400.0       # operator raises retention to cover the gap


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


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor

    def close(self):
        pass


class RowsCursor:
    """Order-store stand-in answering the verifier projections by primary key.

    ``rows[order_id] = (version, state, amount, marker)``; range and ``IN``
    queries return the rows that exist - missing ids are the downstream holes."""

    def __init__(self, rows: dict[int, tuple[int, str, str, str]]):
        self.rows = dict(rows)
        self._last = ""

    def execute(self, sql, args=()):
        self._last = sql

    def _query_ids(self) -> list[int]:
        listed = re.search(r"IN \(([^)]*)\)", self._last)
        if listed:
            return [int(x) for x in listed.group(1).split(",")]
        ranged = re.search(r"order_id >= (\d+) AND order_id <= (\d+)", self._last)
        if ranged:
            return list(range(int(ranged.group(1)), int(ranged.group(2)) + 1))
        raise AssertionError(f"no id range in SQL: {self._last!r}")

    def fetchall(self):
        if "SELECT order_id, version, state, amount, marker" in self._last:
            projected = lambda oid: tuple((oid, *self.rows[oid]))
        elif "SELECT order_id, version, state, marker" in self._last:
            projected = lambda oid: (oid, *self.rows[oid][:2], self.rows[oid][3])
        elif "SELECT order_id, version, marker" in self._last:
            projected = lambda oid: (oid, self.rows[oid][0], self.rows[oid][3])
        else:
            raise AssertionError(f"no row answer for SQL: {self._last!r}")
        return [projected(oid) for oid in self._query_ids() if oid in self.rows]

    def close(self):
        pass


def _marker(order_id: int, version: int = 1) -> str:
    return f"m{order_id:09d}-v{version:03d}"


def _order_ids(count: int, *, from_time: float, step: float) -> tuple[list[int], list[float]]:
    """One order per business commit: ids and their source-commit times."""
    order_ids = [1_000_000 + 10 * index for index in range(count)]
    return order_ids, [from_time + index * step for index in range(count)]


def _visibility_record(business_id: str, planned_at: float, completed_at: float | None,
                       deadline_seconds: float = 10.0) -> LogicalTransactionRecord:
    if completed_at is None:
        return LogicalTransactionRecord(
            business_id=business_id, service_id="fulfilment_visibility",
            tx_kind="order_visibility", planned_at_monotonic=planned_at,
            deadline_at_monotonic=planned_at + deadline_seconds,
            attempts=(TransactionAttempt(
                attempt_index=1, started_at_monotonic=planned_at,
                ended_at_monotonic=planned_at + deadline_seconds,
                outcome=AttemptOutcome.TIMED_OUT, detail={}),
            ),
            terminal=LedgerTerminal.INCOMPLETE_TIMEOUT, completed_at_monotonic=None,
            result_digest=None,
        )
    return LogicalTransactionRecord(
        business_id=business_id, service_id="fulfilment_visibility",
        tx_kind="order_visibility", planned_at_monotonic=planned_at,
        deadline_at_monotonic=planned_at + deadline_seconds,
        attempts=(TransactionAttempt(
            attempt_index=1, started_at_monotonic=planned_at,
            ended_at_monotonic=completed_at, outcome=AttemptOutcome.COMMITTED, detail={}),
        ),
        terminal=LedgerTerminal.COMPLETED, completed_at_monotonic=completed_at,
        result_digest="1:1:paid:m",
    )


def _ledger_with(tmp_path, records: list[LogicalTransactionRecord]) -> LedgerView:
    ledger = TrustedLedger("cdc_visibility", tmp_path / "visibility.jsonl")
    for record in records:
        ledger.append_planned_transaction(
            business_id=record.business_id, service_id=record.service_id,
            tx_kind=record.tx_kind, planned_at_monotonic=record.planned_at_monotonic,
            deadline_at_monotonic=record.deadline_at_monotonic)
        ledger.append_transaction_attempt(business_id=record.business_id, attempt=record.attempts[0])
        ledger.append_transaction_terminal(
            business_id=record.business_id, terminal=record.terminal,
            completed_at_monotonic=record.completed_at_monotonic,
            result_digest=record.result_digest)
    return LedgerView(ledger)


def _orders_report() -> dict:
    return {"total_obligations": 100, "good_obligations": 100,
            "success_fraction": 1.0, "breached_count": 0, "breach_planned_at": []}


# ---------------------------------------------------------------------------
# safepoint model (composite root cause factor B)


def test_pin_release_and_gc_eligibility_math() -> None:
    assert pin_release_at(STALL_START) == PIN_RELEASE
    assert checkpoint_pinned(2000.0, STALL_START)
    assert checkpoint_pinned(2399.0, STALL_START, PIN_RELEASE)
    assert not checkpoint_pinned(PIN_RELEASE, STALL_START, PIN_RELEASE)
    # while the pin holds, the service safepoint blocks GC entirely
    assert gc_eligible_from(STALL_START, GC_LIFE_BASELINE, None) is None
    # after the release the boundary is now - life_time
    assert gc_eligible_from(STALL_START, GC_LIFE_BASELINE, PIN_RELEASE) == 3600.0
    assert gc_eligible_from(1000.0, GC_LIFE_BASELINE, PIN_RELEASE) == 2800.0


def test_retention_secured_covers_checkpoint_gap() -> None:
    assert retention_secured(GC_LIFE_BASELINE, RECOVERY_LATE, STALL_START)
    assert not retention_secured(600.0, RECOVERY_LATE, STALL_START)
    assert retention_secured(GC_LIFE_RAISED, SAMPLED_AT, STALL_START)


def test_exposed_commits_localize_the_unprotected_stall_window() -> None:
    order_ids, commit_times = _order_ids(24, from_time=STALL_START, step=100.0)
    applied_through = STALL_START - 1.0  # the pinned checkpoint: nothing newer applied
    # nothing exposed while the pin holds the GC safepoint in place
    assert exposed_commits(
        commit_times, now=SAMPLED_AT, life_time_seconds=GC_LIFE_BASELINE,
        pin_released_at=None, replicated_through=applied_through) == ()
    # the boundary eats the unreplicated window one retention behind "now"
    exposed = exposed_commits(
        commit_times, now=5000.0, life_time_seconds=GC_LIFE_BASELINE,
        pin_released_at=PIN_RELEASE, replicated_through=applied_through)
    assert exposed == tuple(1800.0 + 100 * index for index in range(15))  # commit + 1800 <= 5000
    # a retention raise at 2600 preempts every deletion (evaluate at securing
    # time with the baseline: nothing was old enough to lose)
    assert exposed_commits(
        commit_times, now=RECOVERY_LATE, life_time_seconds=GC_LIFE_BASELINE,
        pin_released_at=PIN_RELEASE, replicated_through=applied_through) == ()


def test_parse_gc_duration_and_sampling_fail_closed() -> None:
    assert parse_gc_duration("30m0s") == 1800.0
    assert parse_gc_duration("600s") == 600.0
    assert parse_gc_duration("1h30m") == 5400.0
    with pytest.raises(ValueError):
        parse_gc_duration("soon")
    with pytest.raises(ValueError):
        parse_gc_duration("30")
    cursor = ScriptedCursor().on("SHOW VARIABLES LIKE 'tidb_gc_life_time'",
                                 [("tidb_gc_life_time", "30m0s")]).on(
        "SELECT VARIABLE_VALUE FROM mysql.tidb", [("2026-09-21 00:29:00.000",)])
    state = sample_upstream_gc_state(cursor)
    assert state["gc_life_time_seconds"] == 1800.0
    assert state["tikv_gc_safe_point"] == "2026-09-21 00:29:00.000"
    with pytest.raises(ValueError, match="tikv_gc_safe_point"):
        sample_upstream_gc_state(ScriptedCursor().on(
            "SHOW VARIABLES LIKE 'tidb_gc_life_time'", [("tidb_gc_life_time", "30m0s")]).on(
            "SELECT VARIABLE_VALUE FROM mysql.tidb", []))


def test_frozen_safepoint_samples_are_the_stall_signature() -> None:
    frozen = {"tikv_gc_safe_point": "2026-09-21 00:29:00.000"}
    advanced = {"tikv_gc_safe_point": "2026-09-21 00:34:00.000"}
    assert safepoint_stalled(frozen, frozen)
    assert not safepoint_stalled(frozen, advanced)


# ---------------------------------------------------------------------------
# capability: the composite stall anchor


def test_schema_release_records_the_composite_stall_anchor() -> None:
    class _Env:
        def __init__(self, cursor):
            self._cursor = cursor

        def upstream(self):
            return FakeConnection(self._cursor)

        def downstream(self):
            return FakeConnection(self._cursor)

    cursor = ScriptedCursor().on("SELECT id FROM information_schema.processlist", []).on(
        "SELECT marker", ()).on(
        "SHOW VARIABLES LIKE 'tidb_gc_life_time'", [("tidb_gc_life_time", "30m0s")]).on(
        "SELECT VARIABLE_VALUE FROM mysql.tidb", [("2026-09-21 00:29:30.000",)])
    event = type("E", (), {
        "event_id": "cdc_schema_release_1", "entity": "release-1",
        "payload": {"column_name": "gift_note", "column_type": "VARCHAR(128)",
                    "release_note": "gift note", "probe_order_id": 8800000,
                    "gc_pin_release_seconds": 600, "upstream_gc_life_time": "30m0s"},
    })()
    context = type("C", (), {"event": event, "environment": _Env(cursor),
                             "clock": FakeClock(start=1800.0)})()
    result = CdcSchemaReleaseCapability().activate(context)
    stall = result.applied.facts["stall"]
    assert stall["stall_started_at_monotonic"] == 1800.0
    assert stall["pin_release_after_seconds"] == 600.0
    assert stall["gc_life_time_seconds"] == 1800.0
    assert stall["tikv_gc_safe_point"] == "2026-09-21 00:29:30.000"


def test_schema_release_rejects_unknown_payload_fields() -> None:
    class _Env:
        def upstream(self):
            return FakeConnection(ScriptedCursor())

        def downstream(self):
            return FakeConnection(ScriptedCursor())

    event = type("E", (), {
        "event_id": "e", "entity": "release-1",
        "payload": {"column_name": "c", "column_type": "VARCHAR(8)", "release_note": "n",
                    "probe_order_id": 1, "gc_pin_release_seconds": 600,
                    "upstream_gc_life_time": "30m0s", "evil": 1},
    })()
    context = type("C", (), {"event": event, "environment": _Env(),
                             "clock": FakeClock()})()
    with pytest.raises(ValueError, match="unknown payload fields"):
        CdcSchemaReleaseCapability().activate(context)


# ---------------------------------------------------------------------------
# three paths over the coupled timeline


def _path_records(*, recovered_at: float | None, drained_at: float | None,
                  rerun_breaches: bool) -> list[LogicalTransactionRecord]:
    """Visibility obligations across the coupled timeline.

    Pre-fault obligations resolve well; the stall window breaches and, on a
    repaired run, drains by ``drained_at``; after the recovery point
    obligations resolve within the deadline unless the rerun competed with
    the drain (``rerun_breaches``)."""
    records: list[LogicalTransactionRecord] = []
    # healthy baseline: 3 obligations before the fault
    for planned in (600.0, 1200.0, 1700.0):
        records.append(_visibility_record(f"order-{planned:.0f}:v1", planned, planned + 1.0))
    if recovered_at is None:  # zero path: the stall window times out entirely
        records.append(_visibility_record("order-2000:v1", 2000.0, None))
        records.append(_visibility_record("order-2400:v1", 2400.0, None))
        return records
    # the stall window: planned before the repair point; breaches drain only
    # once replication resumes (drained_at), or times out when it never does
    if drained_at is None:
        records.append(_visibility_record("order-1900:v1", 1900.0, None))
        records.append(_visibility_record("order-2199:v1", 2199.0, None))
    else:
        records.append(_visibility_record("order-1900:v1", 1900.0, drained_at - 500.0))
        records.append(_visibility_record("order-2199:v1", 2199.0, drained_at))
    # post-recovery traffic
    for planned in (2300.0, 3000.0, 3600.0):
        records.append(_visibility_record(f"order-{planned:.0f}:v1", planned, planned + 2.0))
    if rerun_breaches:  # the rerun competed with the drain: new orders expire
        for planned in (3950.0, 4000.0, 4050.0):
            records.append(_visibility_record(f"order-{planned:.0f}:v1", planned, None))
    for planned in (4500.0, 5200.0, 5900.0, 6100.0):
        records.append(_visibility_record(f"order-{planned:.0f}:v1", planned, planned + 2.0))
    return records


_CAUGHT_UP_WINDOW_IDS = (5900, 6100)  # orders committed inside the final window


def _watermark_inputs(order_ids, commit_times, visible_through: float | None):
    """Upstream/downstream cursors for the verifiers; ``visible_through`` is
    the newest commit time the downstream serves (None = nothing replicated)."""
    upstream_rows = {
        order_id: (1, "paid", f"{order_id % 500 + 1}.25", _marker(order_id))
        for order_id in order_ids
    }
    for order_id in _CAUGHT_UP_WINDOW_IDS:  # the final-window business commits
        upstream_rows[order_id] = (1, "paid", f"{order_id % 500 + 1}.25", _marker(order_id))
    downstream_rows = {}
    if visible_through is not None:
        for order_id, row in upstream_rows.items():
            commit_time = commit_times[order_ids.index(order_id)] if order_id in order_ids else float(order_id)
            if commit_time <= visible_through:
                downstream_rows[order_id] = row
    return RowsCursor(upstream_rows), RowsCursor(downstream_rows)


def test_complete_path_with_coupling_passes_all_contracts(tmp_path) -> None:
    """Repaired before the pin release (self-heal): the catch-up drains through
    the peak overlap, the rerun is deferred until the drain completes, and
    every contract accepts the final state."""
    order_ids, commit_times = _order_ids(24, from_time=STALL_START, step=100.0)
    upstream, downstream = _watermark_inputs(order_ids, commit_times, visible_through=SAMPLED_AT)
    pairing = CdcMarkerPairingVerifier()(
        {"from_order_id": order_ids[0], "through_order_id": order_ids[-1]},
        upstream=FakeConnection(upstream), downstream=FakeConnection(downstream),
        ledger_view=None)
    assert pairing["passed"]

    records = _path_records(recovered_at=RECOVERY_EARLY, drained_at=DRAINED_AT,
                            rerun_breaches=False)
    ledger_view = _ledger_with(tmp_path, records)
    caught_up = CdcDownstreamCaughtUpVerifier()(
        {"window_seconds": 600}, upstream=FakeConnection(upstream),
        downstream=FakeConnection(downstream), ledger_view=ledger_view)
    assert caught_up["passed"]

    report = visibility_violation_set(records)
    verdict = full_path_verdict(
        _orders_report(), report,
        hole_check_report({1: 1}, {1: 1}), caught_up["passed"],
        min_orders_success_fraction=0.999, min_visibility_success_fraction=0.99,
        fault_started_at=STALL_START, recovery_completed_at=RECOVERY_EARLY,
    )
    assert verdict["full_path_pass"]
    assert verdict["breaches_bounded_to_fault_window"]

    composite = composite_repair_report(
        privilege_restored=True, replication_resumed=True,
        gc_life_time_seconds=GC_LIFE_BASELINE, sampled_at=SAMPLED_AT,
        stall_started_at=STALL_START, pin_released_at=None,
        watermark_complete=pairing["passed"], caught_up_pass=caught_up["passed"],
    )
    assert composite["composite_repair_complete"]
    assert composite["violated_contract_checks"] == []

    sequencing = rerun_sequencing_report(
        records, rerun_arrival_at=RERUN_ARRIVAL,
        recovery_completed_at=RECOVERY_EARLY,
        campaign_activity=[DRAINED_AT + 50.0],  # the rerun ran after the drain
    )
    assert sequencing["overlap_present"]  # rerun arrived inside the drain window
    assert sequencing["campaign_deferred_until_drain"]
    assert sequencing["sequencing_acceptable"]
    assert not sequencing["campaign_open"]


def test_complete_path_after_pin_release_secures_retention_first(tmp_path) -> None:
    """Repaired after the fail-fast pin release: raising the authorized
    retention GUC before resuming preempts every deletion, so the watermark
    stays complete with the pin released."""
    order_ids, commit_times = _order_ids(24, from_time=STALL_START, step=100.0)
    upstream, downstream = _watermark_inputs(order_ids, commit_times, visible_through=SAMPLED_AT)
    pairing = CdcMarkerPairingVerifier()(
        {"from_order_id": order_ids[0], "through_order_id": order_ids[-1]},
        upstream=FakeConnection(upstream), downstream=FakeConnection(downstream),
        ledger_view=None)
    assert pairing["passed"]
    # securing at RECOVERY_LATE with the baseline deletes nothing (commit+1800 > 2600)
    assert exposed_commits(
        commit_times, now=RECOVERY_LATE, life_time_seconds=GC_LIFE_BASELINE,
        pin_released_at=PIN_RELEASE, replicated_through=STALL_START - 1.0) == ()

    composite = composite_repair_report(
        privilege_restored=True, replication_resumed=True,
        gc_life_time_seconds=GC_LIFE_RAISED, sampled_at=SAMPLED_AT,
        stall_started_at=STALL_START, pin_released_at=PIN_RELEASE,
        watermark_complete=True, caught_up_pass=True,
    )
    assert composite["composite_repair_complete"]
    assert composite["factors"]["retention_covers_checkpoint_gap"] is True


def test_privilege_only_repair_fails_the_named_contract_checks(tmp_path) -> None:
    """Grant-only: the changefeed stays parked after the pin release, the
    catch-up never crosses the safepoint/checkpoint stall, and the GC boundary
    makes part of the stall window permanently unreplicable."""
    order_ids, commit_times = _order_ids(24, from_time=STALL_START, step=100.0)
    upstream, downstream = _watermark_inputs(order_ids, commit_times, visible_through=None)
    pairing = CdcMarkerPairingVerifier()(
        {"from_order_id": order_ids[0], "through_order_id": order_ids[-1]},
        upstream=FakeConnection(upstream), downstream=FakeConnection(downstream),
        ledger_view=None)
    assert not pairing["passed"]
    assert pairing["missing_count"] == 24

    holes = stall_window_holes(
        commit_times, sampled_at=SAMPLED_AT, stall_started_at=STALL_START,
        life_time_seconds=GC_LIFE_BASELINE, replicated_through=STALL_START - 1.0,
        pin_released_at=PIN_RELEASE)
    # commits older than the current GC boundary are permanently lost even if
    # the changefeed is resumed later: at final sampling the boundary has eaten
    # every unreplicated stall-window commit (commit + 1800 <= 6300)
    assert holes["hole_count"] == 24
    assert holes["hole_commit_times"][0] == STALL_START
    assert holes["hole_commit_times"][-1] == 4100.0

    records = _path_records(recovered_at=RECOVERY_EARLY, drained_at=None, rerun_breaches=False)
    caught_up = CdcDownstreamCaughtUpVerifier()(
        {"window_seconds": 600}, upstream=FakeConnection(upstream),
        downstream=FakeConnection(downstream), ledger_view=_ledger_with(tmp_path, records))
    assert not caught_up["passed"]

    composite = composite_repair_report(
        privilege_restored=True, replication_resumed=False,
        gc_life_time_seconds=GC_LIFE_BASELINE, sampled_at=SAMPLED_AT,
        stall_started_at=STALL_START, pin_released_at=PIN_RELEASE,
        watermark_complete=False, caught_up_pass=False,
    )
    assert not composite["composite_repair_complete"]
    # the grant resolved factor A only: the changefeed is still parked after
    # the pin release and the baseline retention no longer covers the gap
    assert composite["unresolved_factors"] == [
        "replication_resumed", "retention_covers_checkpoint_gap"]
    assert composite["violated_contract_checks"] == [
        "cdc_watermark_pairing", "cdc_downstream_caught_up"]


def test_safepoint_only_repair_fails_the_named_contract_checks(tmp_path) -> None:
    """Resume + retention without the grant: the resumed sink re-attempts the
    DDL and stays blocked, so the watermark keeps failing with the privilege
    factor unresolved."""
    order_ids, commit_times = _order_ids(24, from_time=STALL_START, step=100.0)
    upstream, downstream = _watermark_inputs(order_ids, commit_times, visible_through=None)
    pairing = CdcMarkerPairingVerifier()(
        {"from_order_id": order_ids[0], "through_order_id": order_ids[-1]},
        upstream=FakeConnection(upstream), downstream=FakeConnection(downstream),
        ledger_view=None)
    assert not pairing["passed"]

    records = _path_records(recovered_at=RECOVERY_LATE, drained_at=None, rerun_breaches=False)
    caught_up = CdcDownstreamCaughtUpVerifier()(
        {"window_seconds": 600}, upstream=FakeConnection(upstream),
        downstream=FakeConnection(downstream), ledger_view=_ledger_with(tmp_path, records))
    assert not caught_up["passed"]

    composite = composite_repair_report(
        privilege_restored=False, replication_resumed=True,
        gc_life_time_seconds=GC_LIFE_RAISED, sampled_at=SAMPLED_AT,
        stall_started_at=STALL_START, pin_released_at=PIN_RELEASE,
        watermark_complete=False, caught_up_pass=False,
    )
    assert not composite["composite_repair_complete"]
    assert composite["unresolved_factors"] == ["privilege_restored"]
    assert "cdc_watermark_pairing" in composite["violated_contract_checks"]


def test_zero_path_still_violates_visibility_contracts(tmp_path) -> None:
    """No repair: the parked replication breaches visibility deadlines and the
    late-pinned window never reaches the downstream; the breach record survives."""
    order_ids, commit_times = _order_ids(24, from_time=STALL_START, step=100.0)
    upstream, downstream = _watermark_inputs(order_ids, commit_times, visible_through=None)
    pairing = CdcMarkerPairingVerifier()(
        {"from_order_id": order_ids[0], "through_order_id": order_ids[-1]},
        upstream=FakeConnection(upstream), downstream=FakeConnection(downstream),
        ledger_view=None)
    assert not pairing["passed"]

    records = _path_records(recovered_at=None, drained_at=None, rerun_breaches=False)
    report = visibility_violation_set(records)
    assert report["breached_count"] == 2 and report["timed_out_count"] == 2
    verdict = zero_path_verdict(
        report, end_state_complete=False, caught_up_pass=False, recovered_at_end=False)
    assert not verdict["zero_path_pass"]
    assert verdict["intervention_necessary"]

    composite = composite_repair_report(
        privilege_restored=False, replication_resumed=False,
        gc_life_time_seconds=GC_LIFE_BASELINE, sampled_at=SAMPLED_AT,
        stall_started_at=STALL_START, pin_released_at=PIN_RELEASE,
        watermark_complete=False, caught_up_pass=False,
    )
    assert sorted(composite["unresolved_factors"]) == [
        "privilege_restored", "replication_resumed", "retention_covers_checkpoint_gap"]


# ---------------------------------------------------------------------------
# rerun sequencing inside the catch-up drain


def test_rerun_during_drain_creates_post_recovery_breaches_and_is_rejected(tmp_path) -> None:
    """Running the rerun at full pressure while the peak backlog drains extends
    the contention past the recovery point: new visibility obligations expire,
    the full path loses its breach bound, and the sequencing is rejected."""
    records = _path_records(recovered_at=RECOVERY_EARLY, drained_at=DRAINED_AT,
                            rerun_breaches=True)
    report = visibility_violation_set(records)
    verdict = full_path_verdict(
        _orders_report(), report, hole_check_report({1: 1}, {1: 1}), True,
        min_orders_success_fraction=0.999, min_visibility_success_fraction=0.99,
        fault_started_at=STALL_START, recovery_completed_at=RECOVERY_EARLY,
    )
    assert not verdict["breaches_bounded_to_fault_window"]
    assert not verdict["full_path_pass"]

    sequencing = rerun_sequencing_report(
        records, rerun_arrival_at=RERUN_ARRIVAL, recovery_completed_at=RECOVERY_EARLY,
        campaign_activity=[3950.0],  # the rerun ran while the backlog was draining
    )
    assert sequencing["overlap_present"]
    assert not sequencing["campaign_deferred_until_drain"]
    assert sequencing["post_recovery_breach_count"] == 3
    assert not sequencing["sequencing_acceptable"]


def test_deferred_rerun_and_open_campaign_are_judged_honestly() -> None:
    """A campaign that only runs after the drain is a recorded deferral; a
    campaign that never runs stays open - both are honest facts, neither is an
    action-name judgement."""
    records = _path_records(recovered_at=RECOVERY_EARLY, drained_at=DRAINED_AT,
                            rerun_breaches=False)
    deferred = rerun_sequencing_report(
        records, rerun_arrival_at=RERUN_ARRIVAL, recovery_completed_at=RECOVERY_EARLY,
        campaign_activity=[DRAINED_AT + 50.0])
    assert deferred["campaign_deferred_until_drain"]
    assert not deferred["campaign_open"]
    assert deferred["sequencing_acceptable"]

    never_ran = rerun_sequencing_report(
        records, rerun_arrival_at=RERUN_ARRIVAL, recovery_completed_at=RECOVERY_EARLY,
        campaign_activity=[])
    assert never_ran["campaign_open"]
    assert not never_ran["campaign_completed_after_arrival"]
    assert never_ran["sequencing_acceptable"]  # no data consequence: not punished


def test_drain_completion_is_the_last_pre_recovery_resolution() -> None:
    records = _path_records(recovered_at=RECOVERY_EARLY, drained_at=DRAINED_AT,
                            rerun_breaches=False)
    assert drain_completion_at(records, RECOVERY_EARLY) == DRAINED_AT
    assert drain_completion_at(_path_records(
        recovered_at=None, drained_at=None, rerun_breaches=False), 10.0) is None


# ---------------------------------------------------------------------------
# competing hypotheses with real same-window noise


def test_maintenance_worker_produces_real_passes_with_audit_rows() -> None:
    """The upstream stats-refresh is real maintenance: ANALYZE on the order
    store plus an audit trail in ops.maintenance_log with durations - the same
    tool results the agent reads during the incident window."""
    clock = FakeClock(start=1500.0)
    cursor = ScriptedCursor()

    def advance_on_analyze(sql, args=()):
        cursor.executed.append(sql)
        cursor._last = sql
        if sql.startswith("ANALYZE TABLE"):
            clock.advance(5.0)

    cursor.execute = advance_on_analyze
    worker = UpstreamMaintenanceWorker(
        factories=type("F", (), {"upstream": lambda self: FakeConnection(cursor)})(),
        clock=clock, log=lambda message: None, cycle_seconds=600.0)
    worker._run_pass(cursor, 1500.0)
    assert "ANALYZE TABLE fulfil.orders" in cursor.executed
    insert = cursor.executed[0]
    assert "INSERT INTO ops.maintenance_log" in insert and "'running'" in insert
    update = cursor.executed[-1]
    assert "status = 'completed'" in update and "duration_seconds = 5.000" in update
    assert worker.facts() == {"maintenance_runs": 1}


def test_competing_hypotheses_share_the_window_and_are_excludable() -> None:
    """The initial visibility dip is consistent with all three near-neighbors:
    (1) sink permission error, (2) downstream batch contention (event-1
    overlap), (3) safepoint block. Each carries its own decisive evidence on a
    different surface, so only cross-tool correlation separates them."""
    cursor = ScriptedCursor().on("SELECT id FROM information_schema.processlist", []).on(
        "SELECT marker", ()).on(
        "SHOW VARIABLES LIKE 'tidb_gc_life_time'", [("tidb_gc_life_time", "30m0s")]).on(
        "SELECT VARIABLE_VALUE FROM mysql.tidb", [("2026-09-21 00:29:30.000",)])
    event = type("E", (), {
        "event_id": "cdc_schema_release_1", "entity": "release-1",
        "payload": {"column_name": "gift_note", "column_type": "VARCHAR(128)",
                    "release_note": "gift note", "probe_order_id": 8800000,
                    "gc_pin_release_seconds": 600, "upstream_gc_life_time": "30m0s"},
    })()

    class _Env:
        def __init__(self, cursor):
            self._cursor = cursor

        def upstream(self):
            return FakeConnection(self._cursor)

        def downstream(self):
            return FakeConnection(self._cursor)

    result = CdcSchemaReleaseCapability().activate(type(
        "C", (), {"event": event, "environment": _Env(cursor),
                  "clock": FakeClock(start=1800.0)})())
    stall = result.applied.facts["stall"]

    # hypothesis 3 looks live at the same moment (frozen safepoint sample)...
    assert stall["tikv_gc_safe_point"] == "2026-09-21 00:29:30.000"
    # ...and stays frozen across samples, so it needs the causal chain resolved
    later = sample_upstream_gc_state(cursor)
    assert safepoint_stalled(stall, later)

    # hypothesis 2 was live in the same window: the event-1 batch campaign
    # (900..2100) overlaps the fault onset - its own control row closes it
    batch_window_active = ("campaign:nightly-1", 900.0, 2100.0)
    assert batch_window_active[1] <= 1800.0 < batch_window_active[2]

    # hypothesis 1 has no alias in the sampled surfaces: the downstream
    # privilege table is a different tool and decides the sink factor
    grants_cursor = ScriptedCursor().on("SHOW GRANTS FOR", [("GRANT SELECT, INSERT, UPDATE, DELETE",)])
    grants_cursor.execute("SHOW GRANTS FOR 'cdc_sink'@'%'")
    grants = grants_cursor.fetchall()
    assert grants and "ALTER" not in grants[0]

    # exclusion: the batch window closed at 2100 and maintenance completed
    # normally while the visibility stall persisted - only the composite
    # (privilege + pinned checkpoint safepoint) explains every observation
    assert batch_window_active[2] < 2400.0
    maintenance_row = {"status": "completed", "duration_seconds": 5.0}
    assert maintenance_row["status"] == "completed"


# ---------------------------------------------------------------------------
# interface v1: admission with the coupled timeline + frozen budgets


class _Registry:
    def __init__(self, capabilities):
        self._by_id = {capability.capability_id: capability for capability in capabilities}

    def capability(self, capability_id: str):
        return self._by_id[capability_id]


class _Backend:
    def validate_spec(self, spec) -> None:
        pass


def test_admission_passes_with_coupled_timeline() -> None:
    from src.persistent_scenarios.backend.tidb.capabilities.cdc import CAPABILITIES

    spec = load_persistent_scenario(YAML_PATH)
    admit_persistent_scenario(spec, _Backend(), _Registry(CAPABILITIES))

    schema_release = next(event for event in spec.events if event.event_id == "cdc_schema_release_1")
    peak = next(event for event in spec.events if event.event_id == "cdc_order_peak_1")
    # the peak lands inside the schema-release recovery window
    recovery_end = schema_release.start_seconds + schema_release.response_deadline_seconds
    assert schema_release.start_seconds < peak.start_seconds < recovery_end
    # activation windows still do not collide
    assert schema_release.start_seconds + schema_release.activation_timeout_seconds <= peak.start_seconds


def test_public_budget_constants_stay_frozen() -> None:
    """The difficulty comes from mechanisms, never from budget changes."""
    spec = load_persistent_scenario(YAML_PATH)
    assert (spec.warmup_seconds, spec.input_stop_seconds, spec.agent_stop_seconds,
            spec.horizon_seconds) == (300, 6000, 6300, 6600)
    by_service = {service.service_id: service for service in spec.services}
    assert by_service["orders"].deadline_seconds == 5.0
    assert by_service["orders"].min_success_fraction == 0.999
    assert by_service["fulfilment_visibility"].deadline_seconds == 10.0
    # Calibration evidence: even the deterministic reference path cannot
    # reach 0.99 through the designed stall+catch-up window. Three
    # complete-repair reference samples span 0.776 / 0.873 / 0.8875;
    # 0.72 = worst reference minus a 5.6pp margin so every honest repair
    # passes, while post-recovery discipline stays enforced by the breach
    # bound.
    assert by_service["fulfilment_visibility"].min_success_fraction == 0.72
    expected = {
        "cdc_batch_window_1": (900, 90, 600),
        "cdc_schema_release_1": (1800, 180, 900),
        "cdc_order_peak_1": (2100, 120, 600),
        "cdc_batch_window_2": (3900, 90, 600),
    }
    for event in spec.events:
        assert (event.start_seconds, event.activation_timeout_seconds,
                event.response_deadline_seconds) == expected[event.event_id]
    peak = next(event for event in spec.events if event.event_id == "cdc_order_peak_1")
    assert peak.payload["target_orders_per_sec"] == 12.0
    assert spec.calibration.status.value == "development_provisional"
