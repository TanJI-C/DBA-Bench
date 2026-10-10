"""Three-path calibration verdicts for tidb_cdc_downstream_freshness.

The full path repairs the reversible downstream blockage and
must keep the promised watermark complete with breaches bounded to the
unrepaired fault window; the zero path shows the un-repaired apply failure
breaches per-order fulfilment visibility deadlines and that a late end-of-run
recovery does not erase the recorded violations; the error paths are judged by
real data consequences (localized hole checks), never by action names.

Every function here is pure: the calibration scripts in ``scripts/`` execute
them over live database rows and trusted-ledger records, while focused tests
pin the decision semantics. Every judgement input is business data (order
pairs, ledger obligations) - changefeed state and checkpoint TSO are
auxiliary evidence only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from src.persistent_scenarios.runtime.ledger import LedgerTerminal, LogicalTransactionRecord

from .safepoint import exposed_commits, retention_secured


# ---------------------------------------------------------------------------
# Watermark integrity: pairing the upstream order store against the read model
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class HoleCheckReport:
    """order_id -> version maps for both sides of the replication."""

    checked: int
    missing: tuple[int, ...] = ()
    stale: tuple[int, ...] = ()

    @property
    def complete(self) -> bool:
        return not self.missing and not self.stale

    def as_details(self) -> dict:
        return {
            "checked": self.checked,
            "missing_count": len(self.missing),
            "missing_head": list(self.missing)[:50],
            "stale_count": len(self.stale),
            "stale_head": list(self.stale)[:50],
            "complete": self.complete,
        }


def hole_check_report(
    upstream_versions: Mapping[int, int],
    downstream_versions: Mapping[int, int],
) -> HoleCheckReport:
    missing = tuple(sorted(oid for oid in upstream_versions if oid not in downstream_versions))
    stale = tuple(sorted(
        oid for oid, version in upstream_versions.items()
        if oid in downstream_versions and downstream_versions[oid] < version
    ))
    return HoleCheckReport(checked=len(upstream_versions), missing=missing, stale=stale)


def expect_localized_hole(report: HoleCheckReport, expected_missing: Iterable[int]) -> dict:
    """Data-consequence judgement for the error paths: the hole must be exactly
    the expected set. Extra missing rows and rows that should be missing but
    are present both falsify the expectation."""

    expected = set(expected_missing)
    observed = set(report.missing)
    return {
        "expected_count": len(expected),
        "missing_matches_expectation": observed == expected,
        "unexpected_missing": sorted(observed - expected)[:50],
        "unexpectedly_present": sorted(expected - observed)[:50],
    }


def expect_hole_covers(report: HoleCheckReport, minimum_missing: Iterable[int]) -> dict:
    """Weaker data-consequence judgement for the fake-progress shortcut: the
    pre-TSO commits must all be missing; the skipped DDL may cost the read
    model additional rows (the sink can no longer apply the new upstream
    shape), and those extra holes are recorded, not excused."""

    minimum = set(minimum_missing)
    observed = set(report.missing)
    return {
        "minimum_expected_count": len(minimum),
        "covers_expected_hole": minimum <= observed,
        "extra_missing": sorted(observed - minimum)[:50],
        "extra_missing_count": len(observed - minimum),
    }


# ---------------------------------------------------------------------------
# Per-order visibility deadline accounting over the trusted ledger
# ---------------------------------------------------------------------------


def visibility_violation_set(records: Sequence[LogicalTransactionRecord]) -> dict:
    """Decide every obligation against its own ledger deadline
    (``deadline_at_monotonic``), so a late end-of-run recovery cannot rewrite
    history: a commit visible after its deadline stays a violation, and a
    timed-out obligation stays violated even once the row finally arrives."""

    total = len(records)
    breached: list[LogicalTransactionRecord] = []
    timed_out: list[LogicalTransactionRecord] = []
    late_visible: list[LogicalTransactionRecord] = []
    good_latencies: list[float] = []
    for record in records:
        if record.good:
            good_latencies.append(record.completed_at_monotonic - record.planned_at_monotonic)
            continue
        breached.append(record)
        if record.terminal is LedgerTerminal.INCOMPLETE_TIMEOUT:
            timed_out.append(record)
        elif record.completed_at_monotonic is not None:
            late_visible.append(record)
    ordered_breached = sorted(breached, key=lambda record: record.planned_at_monotonic)
    good_latencies.sort()
    return {
        "total_obligations": total,
        "good_obligations": total - len(breached),
        "success_fraction": round((total - len(breached)) / total, 6) if total else 0.0,
        "breached_count": len(breached),
        "breached_business_ids": sorted(record.business_id for record in breached)[:500],
        "timed_out_count": len(timed_out),
        "late_visible_count": len(late_visible),
        "breach_planned_at": [round(record.planned_at_monotonic, 3) for record in ordered_breached],
        "good_p50_seconds": round(good_latencies[len(good_latencies) // 2], 3) if good_latencies else None,
        "good_max_seconds": round(good_latencies[-1], 3) if good_latencies else None,
    }


# ---------------------------------------------------------------------------
# Path verdicts
# ---------------------------------------------------------------------------


def full_path_verdict(
    orders_report: Mapping,
    visibility_report: Mapping,
    watermark: HoleCheckReport,
    caught_up_pass: bool,
    *,
    min_orders_success_fraction: float,
    min_visibility_success_fraction: float,
    fault_started_at: float,
    recovery_completed_at: float,
) -> dict:
    """OP composition for the repaired run: upstream trading
    budget, downstream visibility deadline, completeness before the promised
    watermark, and post-repair catch-up. The visibility fraction is reported
    against its minimum but does not gate a compressed-window calibration run:
    a bounded fault window is over-represented when the 100-minute timeline is
    compressed, so the freeze decision belongs to the full-timeline run."""

    breaches_bounded = all(
        planned_at <= recovery_completed_at
        for planned_at in visibility_report["breach_planned_at"]
    )
    upstream_pass = (
        orders_report["total_obligations"] > 0
        and orders_report["success_fraction"] >= min_orders_success_fraction
    )
    passed = (
        upstream_pass
        and watermark.complete
        and caught_up_pass
        and breaches_bounded
    )
    return {
        "full_path_pass": passed,
        "upstream_budget_pass": upstream_pass,
        "watermark_integrity_pass": watermark.complete,
        "downstream_caught_up_pass": caught_up_pass,
        "breaches_bounded_to_fault_window": breaches_bounded,
        "fault_started_at": round(fault_started_at, 3),
        "recovery_completed_at": round(recovery_completed_at, 3),
        "orders": dict(orders_report),
        "visibility": {**dict(visibility_report), "min_success_fraction": min_visibility_success_fraction},
        "watermark": watermark.as_details(),
    }


def zero_path_verdict(
    visibility_report: Mapping,
    *,
    end_state_complete: bool,
    caught_up_pass: bool,
    recovered_at_end: bool,
) -> dict:
    """Zero-path accounting: the violation set recorded at each order's own
    deadline survives an end-of-run recovery, so restoring state=normal at the
    tail never erases the historical breaches. ``zero_path_pass`` is only true
    when even the un-handled fault produced no violation - which means the
    load/mechanism combination failed to prove the need for
    intervention and must be re-reviewed."""

    breached_count = int(visibility_report["breached_count"])
    return {
        "zero_path_pass": breached_count == 0,
        "intervention_necessary": breached_count > 0,
        "historical_breach_count": breached_count,
        "timed_out_count": int(visibility_report["timed_out_count"]),
        "late_visible_count": int(visibility_report["late_visible_count"]),
        "recovered_at_end": recovered_at_end,
        "end_state_complete": end_state_complete,
        "downstream_caught_up_pass": caught_up_pass,
        "recovery_preserves_violations": (
            recovered_at_end and end_state_complete and breached_count > 0
        ),
        "visibility": dict(visibility_report),
    }


# ---------------------------------------------------------------------------
# Composite root cause: privilege drift + GC safepoint checkpoint stall
# ---------------------------------------------------------------------------


_WATERMARK_CHECK = "cdc_watermark_pairing"
_CATCH_UP_CHECK = "cdc_downstream_caught_up"


def stall_window_holes(commit_times: Sequence[float], *, sampled_at: float,
                       stall_started_at: float, life_time_seconds: float,
                       replicated_through: float,
                       pin_released_at: float | None) -> dict:
    """Localize the permanent downstream holes the composite factor B leaves.

    ``pin_released_at=None`` means the changefeed still holds its GC pin (the
    stall is unresolved but nothing is lost yet); a timestamp means the pin
    was given up and the GC boundary ate every unreplicated commit older than
    its retention. The hole set is a data consequence, not an action judgement.
    """
    holes = exposed_commits(
        commit_times, now=sampled_at, life_time_seconds=life_time_seconds,
        pin_released_at=pin_released_at, replicated_through=replicated_through,
    )
    return {
        "stall_started_at": round(stall_started_at, 3),
        "pin_released_at": round(pin_released_at, 3) if pin_released_at is not None else None,
        "replicated_through": round(replicated_through, 3),
        "hole_count": len(holes),
        "hole_commit_times": [round(value, 3) for value in holes[:50]],
    }


def composite_repair_report(
    *,
    privilege_restored: bool,
    replication_resumed: bool,
    gc_life_time_seconds: float,
    sampled_at: float,
    stall_started_at: float,
    pin_released_at: float | None,
    watermark_complete: bool,
    caught_up_pass: bool,
) -> dict:
    """Factor-resolution accounting for the composite root cause.

    Two factors form one causal chain: the privilege drift blocks the DDL
    apply (factor A) and the retrying changefeed pins its checkpoint, holding
    the upstream GC safepoint (factor B). Every factor resolution is a final
    environment fact; the violated contract checks are named from the data
    consequences, never from repair actions:

    - only-privilege: the changefeed stays parked after the pin release, the
      catch-up never crosses the safepoint/checkpoint stall -> the watermark
      pairing and the final catch-up window stay unmet;
    - only-safepoint (resume/retention without the grant): the resumed sink
      re-attempts the DDL and stays blocked -> the watermark pairing stays
      unmet;
    - a resumed catch-up without secured retention collides with the GC
      boundary -> permanent holes keep the watermark unmet.
    """
    retention_covers_gap = (
        retention_secured(gc_life_time_seconds, sampled_at, stall_started_at)
        if pin_released_at is not None else True
    )  # a pin that never released held GC back by itself: nothing to secure
    violated: list[str] = []
    if not watermark_complete:
        violated.append(_WATERMARK_CHECK)
    if not caught_up_pass:
        violated.append(_CATCH_UP_CHECK)
    factors = {
        "privilege_restored": privilege_restored,
        "replication_resumed": replication_resumed,
        "retention_covers_checkpoint_gap": retention_covers_gap,
    }
    unresolved = sorted(name for name, resolved in factors.items() if resolved is not True)
    return {
        "composite_repair_complete": not violated and not unresolved,
        "unresolved_factors": unresolved,
        "violated_contract_checks": violated,
        "factors": factors,
        "stall_window": {
            "stall_started_at": round(stall_started_at, 3),
            "pin_released_at": round(pin_released_at, 3) if pin_released_at is not None else None,
            "sampled_at": round(sampled_at, 3),
        },
    }


# ---------------------------------------------------------------------------
# Event coupling: order peak / batch rerun overlapping the catch-up drain
# ---------------------------------------------------------------------------


def drain_completion_at(records: Sequence[LogicalTransactionRecord],
                        recovery_completed_at: float) -> float | None:
    """When the replication backlog drain finished: the moment the last
    obligation committed before the repair point became visible downstream.
    ``None`` when the backlog never drained (the stalled window stayed open)."""
    pending = [
        record.completed_at_monotonic for record in records
        if record.planned_at_monotonic <= recovery_completed_at
        and record.completed_at_monotonic is not None
    ]
    if not pending:
        return None
    return max(pending)


def rerun_sequencing_report(
    records: Sequence[LogicalTransactionRecord],
    *,
    rerun_arrival_at: float,
    recovery_completed_at: float,
    campaign_activity: Sequence[float],
) -> dict:
    """Sequencing judgement for the batch rerun inside the catch-up drain.

    The rerun (event 4) arrives while the peak inflow is still draining; the
    visibility budget spans the overlap, so the agent must sequence it
    (defer the non-critical rerun or throttle the upstream). The judgement is
    data-based: post-recovery visibility breaches are the honest cost of a
    rerun that competed with the drain, a campaign that only ran after the
    backlog drained is a recorded deferral, and a campaign that never ran is
    reported open - none of these are action-name checks.
    """
    drained_at = drain_completion_at(records, recovery_completed_at)
    post_recovery_breaches = sorted(
        record.planned_at_monotonic for record in records
        if not record.good and record.planned_at_monotonic > recovery_completed_at
    )
    campaign_after_arrival = [value for value in campaign_activity if value >= rerun_arrival_at]
    drained = drained_at is not None
    campaign_completed = bool(campaign_after_arrival)
    return {
        "rerun_arrival_at": round(rerun_arrival_at, 3),
        "recovery_completed_at": round(recovery_completed_at, 3),
        "backlog_drained_at": round(drained_at, 3) if drained else None,
        "overlap_present": drained and rerun_arrival_at < drained_at,
        "post_recovery_breach_count": len(post_recovery_breaches),
        "post_recovery_breach_planned_at": [round(value, 3) for value in post_recovery_breaches[:50]],
        "campaign_completed_after_arrival": campaign_completed,
        "campaign_deferred_until_drain": (
            drained and campaign_completed and all(value >= drained_at for value in campaign_after_arrival)
        ),
        "campaign_open": not campaign_completed,
        "sequencing_acceptable": len(post_recovery_breaches) == 0,
    }
