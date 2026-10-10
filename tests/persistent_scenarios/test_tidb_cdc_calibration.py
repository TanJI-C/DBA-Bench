"""Focused tests for the tidb_cdc three-path calibration verdicts.

The verdict functions are pure; these tests pin the three-path decision
semantics: per-order ledger deadlines, violation sets that
survive a late recovery, watermark hole localization, and the full/zero/error
path compositions.
"""

from __future__ import annotations

import pytest

from src.persistent_scenarios.backend.tidb.capabilities.cdc.calibration import (
    expect_localized_hole,
    full_path_verdict,
    hole_check_report,
    visibility_violation_set,
    zero_path_verdict,
)
from src.persistent_scenarios.runtime.ledger import (
    AttemptOutcome,
    LedgerTerminal,
    LogicalTransactionRecord,
    TransactionAttempt,
)


def _record(business_id: str, planned_at: float, deadline_seconds: float,
            terminal: LedgerTerminal, completed_at: float | None = None) -> LogicalTransactionRecord:
    attempts = ()
    if completed_at is not None:
        attempts = (TransactionAttempt(
            attempt_index=1, started_at_monotonic=planned_at,
            ended_at_monotonic=completed_at, outcome=AttemptOutcome.COMMITTED, detail={},
        ),)
    return LogicalTransactionRecord(
        business_id=business_id, service_id="fulfilment_visibility", tx_kind="order_visibility",
        planned_at_monotonic=planned_at,
        deadline_at_monotonic=planned_at + deadline_seconds,
        attempts=attempts, terminal=terminal,
        completed_at_monotonic=completed_at,
        result_digest="1:1:paid:m" if terminal is LedgerTerminal.COMPLETED else None,
    )


def _good(business_id: str, planned_at: float, latency: float = 0.9) -> LogicalTransactionRecord:
    return _record(business_id, planned_at, 10.0, LedgerTerminal.COMPLETED, planned_at + latency)


# ---------------------------------------------------------------------------
# hole check + localization
# ---------------------------------------------------------------------------


def test_hole_check_report_complete_when_both_sides_match() -> None:
    report = hole_check_report({1: 2, 2: 1}, {1: 2, 2: 1})
    assert report.complete
    assert report.checked == 2
    assert report.as_details() == {
        "checked": 2, "missing_count": 0, "missing_head": [],
        "stale_count": 0, "stale_head": [], "complete": True,
    }


def test_hole_check_report_flags_missing_and_stale_rows() -> None:
    report = hole_check_report({1: 2, 2: 1, 3: 1}, {1: 1, 3: 1})
    assert not report.complete
    assert report.missing == (2,)
    assert report.stale == (1,)


def test_expect_localized_hole_requires_exact_set_equality() -> None:
    report = hole_check_report({10: 1, 11: 1, 12: 1}, {12: 1})
    detail = expect_localized_hole(report, [10, 11])
    assert detail["missing_matches_expectation"]
    assert detail["unexpected_missing"] == []
    assert detail["unexpectedly_present"] == []
    extra = expect_localized_hole(report, [10])
    assert not extra["missing_matches_expectation"]
    assert extra["unexpected_missing"] == [11]
    partial = expect_localized_hole(report, [10, 11, 99])
    assert not partial["missing_matches_expectation"]
    assert partial["unexpectedly_present"] == [99]


# ---------------------------------------------------------------------------
# visibility violation set
# ---------------------------------------------------------------------------


def test_visibility_violation_set_counts_only_breaches() -> None:
    records = [
        _good("order-1:v1", 0.0, 0.9),
        _record("order-2:v1", 1.0, 10.0, LedgerTerminal.INCOMPLETE_TIMEOUT),
        _record("order-3:v1", 2.0, 10.0, LedgerTerminal.COMPLETED, 2.0 + 14.0),
    ]
    report = visibility_violation_set(records)
    assert report["total_obligations"] == 3
    assert report["good_obligations"] == 1
    assert report["breached_count"] == 2
    assert report["timed_out_count"] == 1
    assert report["late_visible_count"] == 1
    assert report["breached_business_ids"] == ["order-2:v1", "order-3:v1"]
    assert report["success_fraction"] == round(1 / 3, 6)
    assert report["good_max_seconds"] == 0.9


def test_visibility_violation_set_uses_each_record_own_deadline() -> None:
    # identical wall-clock latency: inside the deadline for one record, a
    # breach for a record with a tighter deadline
    records = [
        _record("order-1:v1", 0.0, 10.0, LedgerTerminal.COMPLETED, 8.0),
        _record("order-2:v1", 100.0, 5.0, LedgerTerminal.COMPLETED, 108.0),
    ]
    report = visibility_violation_set(records)
    assert report["breached_business_ids"] == ["order-2:v1"]
    assert report["good_obligations"] == 1


def test_visibility_violation_set_on_empty_ledger_is_all_zero() -> None:
    report = visibility_violation_set([])
    assert report["total_obligations"] == 0
    assert report["breached_count"] == 0
    assert report["success_fraction"] == 0.0


# ---------------------------------------------------------------------------
# full path verdict
# ---------------------------------------------------------------------------


def _orders_report(fraction: float = 1.0, total: int = 100) -> dict:
    return {"total_obligations": total, "good_obligations": total,
            "success_fraction": fraction, "breached_count": 0, "breach_planned_at": []}


def test_full_path_verdict_passes_with_bounded_breaches_and_complete_watermark() -> None:
    visibility = visibility_violation_set([
        _good("order-1:v1", 0.0),
        _record("order-2:v1", 50.0, 10.0, LedgerTerminal.COMPLETED, 50.0 + 30.0),
    ])
    verdict = full_path_verdict(
        _orders_report(), visibility, hole_check_report({1: 1}, {1: 1}), True,
        min_orders_success_fraction=0.999, min_visibility_success_fraction=0.99,
        fault_started_at=40.0, recovery_completed_at=70.0,
    )
    assert verdict["full_path_pass"]
    assert verdict["breaches_bounded_to_fault_window"]
    assert verdict["watermark_integrity_pass"]


def test_full_path_verdict_fails_when_breach_is_planned_after_recovery() -> None:
    visibility = visibility_violation_set([
        _record("order-1:v1", 200.0, 10.0, LedgerTerminal.INCOMPLETE_TIMEOUT),
    ])
    verdict = full_path_verdict(
        _orders_report(), visibility, hole_check_report({1: 1}, {1: 1}), True,
        min_orders_success_fraction=0.999, min_visibility_success_fraction=0.99,
        fault_started_at=40.0, recovery_completed_at=70.0,
    )
    assert not verdict["breaches_bounded_to_fault_window"]
    assert not verdict["full_path_pass"]


def test_full_path_verdict_fails_on_watermark_hole_or_upstream_loss() -> None:
    visibility = visibility_violation_set([_good("order-1:v1", 0.0)])
    holed = hole_check_report({1: 1, 2: 1}, {1: 1})
    verdict = full_path_verdict(
        _orders_report(), visibility, holed, True,
        min_orders_success_fraction=0.999, min_visibility_success_fraction=0.99,
        fault_started_at=0.0, recovery_completed_at=1.0,
    )
    assert not verdict["full_path_pass"]
    upstream_lost = full_path_verdict(
        _orders_report(fraction=0.99), visibility, hole_check_report({1: 1}, {1: 1}), True,
        min_orders_success_fraction=0.999, min_visibility_success_fraction=0.99,
        fault_started_at=0.0, recovery_completed_at=1.0,
    )
    assert not upstream_lost["full_path_pass"]
    not_caught_up = full_path_verdict(
        _orders_report(), visibility, hole_check_report({1: 1}, {1: 1}), False,
        min_orders_success_fraction=0.999, min_visibility_success_fraction=0.99,
        fault_started_at=0.0, recovery_completed_at=1.0,
    )
    assert not not_caught_up["full_path_pass"]


# ---------------------------------------------------------------------------
# zero path verdict
# ---------------------------------------------------------------------------


def test_zero_path_verdict_preserves_violations_after_end_of_run_recovery() -> None:
    visibility = visibility_violation_set([
        _good("order-1:v1", 0.0),
        _record("order-2:v1", 5.0, 10.0, LedgerTerminal.INCOMPLETE_TIMEOUT),
        _record("order-3:v1", 6.0, 10.0, LedgerTerminal.INCOMPLETE_TIMEOUT),
    ])
    verdict = zero_path_verdict(
        visibility, end_state_complete=True, caught_up_pass=True, recovered_at_end=True,
    )
    assert not verdict["zero_path_pass"]
    assert verdict["intervention_necessary"]
    assert verdict["historical_breach_count"] == 2
    assert verdict["recovery_preserves_violations"]
    assert verdict["end_state_complete"]


def test_zero_path_verdict_flags_healthy_config_when_no_fault_breaches() -> None:
    visibility = visibility_violation_set([_good("order-1:v1", 0.0)])
    verdict = zero_path_verdict(
        visibility, end_state_complete=True, caught_up_pass=True, recovered_at_end=False,
    )
    # no violation without intervention: the combination proved nothing and
    # must be re-reviewed instead of counting as a passed zero path
    assert verdict["zero_path_pass"]
    assert not verdict["intervention_necessary"]
    assert not verdict["recovery_preserves_violations"]


def test_zero_path_verdict_counts_late_visible_as_breach_even_when_recovered() -> None:
    visibility = visibility_violation_set([
        _record("order-1:v1", 0.0, 10.0, LedgerTerminal.COMPLETED, 0.0 + 45.0),
    ])
    verdict = zero_path_verdict(
        visibility, end_state_complete=True, caught_up_pass=True, recovered_at_end=True,
    )
    assert verdict["historical_breach_count"] == 1
    assert verdict["late_visible_count"] == 1
    assert verdict["recovery_preserves_violations"]


# ---------------------------------------------------------------------------
# guard against silently widening the contracts
# ---------------------------------------------------------------------------


def test_hole_check_treats_equal_version_as_caught_up() -> None:
    report = hole_check_report({5: 3}, {5: 3})
    assert report.complete


@pytest.mark.parametrize("down_version,complete", [(2, True), (1, False)])
def test_hole_check_staleness_follows_upstream_version(down_version: int, complete: bool) -> None:
    report = hole_check_report({7: 2}, {7: down_version})
    assert report.complete is complete
