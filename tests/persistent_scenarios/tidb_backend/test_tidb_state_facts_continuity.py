"""Continuity required-state sampling on the sealed TiDB trade ledger.

Regression tests for the final-window continuity check: the window must be
judged on the last planned-transaction window (the drain tail between the
frozen input cutoff and the scoring end plans nothing), and lost work must
lower the fraction instead of shrinking the denominator or crashing the
collector.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from src.persistent_scenarios.backend.tidb.assembly import (
    InstanceBinding,
    LazyRuntimeProvider,
    TiDBStateFactProvider,
)
from src.persistent_scenarios.evaluation.required_state import evaluate_required_state
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.persistent_scenarios.model.spec import (
    ContinuityStateSpec,
    compress_persistent_scenario_timeline,
)
from src.persistent_scenarios.runtime.ledger import LedgerTerminal, TrustedLedger

from ..fakes import make_spec

WORKTREE = Path(__file__).resolve().parents[3]
HOTSPOT_YAML = WORKTREE / "src" / "persistent_scenarios" / "tidb" / "tidb_oltp_hotspot_resilience.yaml"


def _hotspot_spec():
    return load_persistent_scenario(HOTSPOT_YAML)


def _build_trade_ledger(path: Path, transactions) -> TrustedLedger:
    """``transactions``: iterable of ``(planned_at, terminal)``; every record is
    closed because the runtime finalizes outstanding work before sealing."""
    ledger = TrustedLedger("trade", path)
    for index, (planned_at, terminal) in enumerate(transactions):
        business_id = f"o{index:06d}"
        ledger.append_planned_transaction(
            business_id=business_id,
            service_id="trade",
            tx_kind="place_order",
            planned_at_monotonic=planned_at,
            deadline_at_monotonic=planned_at + 10.0,
        )
        if terminal is LedgerTerminal.COMPLETED:
            ledger.append_transaction_terminal(
                business_id=business_id,
                terminal=terminal,
                completed_at_monotonic=planned_at + 1.0,
                result_digest=f"order:{business_id}",
            )
        else:
            ledger.append_transaction_terminal(
                business_id=business_id,
                terminal=terminal,
                completed_at_monotonic=None,
                result_digest=None,
            )
    ledger.seal()
    return ledger


def _state_fact_provider(ledger: TrustedLedger) -> TiDBStateFactProvider:
    binding = InstanceBinding(
        scenario_id="test",
        bootstrap=lambda *args: None,
        make_workload=lambda *args: None,
        registry=lambda *args: None,
        integrity={},
        required_state={},
    )
    runtime_provider = LazyRuntimeProvider()
    runtime_provider.attach(SimpleNamespace(ledgers=lambda: {"trade": ledger}))
    return TiDBStateFactProvider(binding, runtime_provider)


def _capture_continuity(ledger: TrustedLedger, spec):
    # The continuity kind samples only the sealed ledgers, never the environment.
    return _state_fact_provider(ledger).capture_required_state_evidence(None, spec)


def test_continuity_facts_judge_the_last_planned_window_when_nothing_completed(tmp_path: Path) -> None:
    """Zero-completions shape: input keeps flowing to the cutoff, every
    transaction aborts, so zero transactions ever complete and a completed-time
    horizon degenerates to 0.0 — the collector must survive it."""
    spec = _hotspot_spec()
    ledger = _build_trade_ledger(
        tmp_path / "trade.jsonl",
        ((index * 10.0, LedgerTerminal.INCOMPLETE_ERROR) for index in range(421)),
    )
    evidence = _capture_continuity(ledger, spec)

    assert len(evidence) == 1
    assert evidence[0].status.name == "CAPTURED"
    # Window [4200 - 300, 4200] holds the 31 transactions planned at 3900..4200.
    assert evidence[0].facts == {"completed": 0, "denominator": 31}


def test_zero_completions_evaluate_honestly_through_required_state(tmp_path: Path) -> None:
    """The run must evaluate on the ledger evidence (continuity fails on the
    merits) instead of the collector raising an infrastructure failure."""
    spec = _hotspot_spec()
    ledger = _build_trade_ledger(
        tmp_path / "trade.jsonl",
        ((index * 10.0, LedgerTerminal.INCOMPLETE_ERROR) for index in range(421)),
    )
    evidence = _capture_continuity(ledger, spec)

    passed, results = evaluate_required_state(spec.required_state, evidence)

    assert passed is False
    assert results[0]["check_id"] == "trade_continuity"
    assert results[0]["pass"] is False
    assert results[0]["evidence"] == {"completed": 0, "denominator": 31}


def test_continuity_fails_when_the_service_stops_completing_after_a_healthy_period(
    tmp_path: Path,
) -> None:
    """Genuine discontinuation: a healthy service whose final-window input no
    longer completes must fail the check (anchoring the completed-time horizon
    on the healthy period passes vacuously)."""
    spec = _hotspot_spec()
    healthy = ((index * 10.0, LedgerTerminal.COMPLETED) for index in range(31))
    discontinued = ((3900.0 + index * 10.0, LedgerTerminal.INCOMPLETE_TIMEOUT) for index in range(31))
    ledger = _build_trade_ledger(tmp_path / "trade.jsonl", [*healthy, *discontinued])

    evidence = _capture_continuity(ledger, spec)
    assert evidence[0].facts == {"completed": 0, "denominator": 31}

    passed, results = evaluate_required_state(spec.required_state, evidence)
    assert passed is False
    assert results[0]["pass"] is False


def test_continuity_window_counts_incomplete_work_in_the_denominator(tmp_path: Path) -> None:
    """Planned-but-failed transactions inside the window are lost work: they
    stay in the denominator and lower the fraction (counting only completed
    records on both sides makes the check vacuous)."""
    spec = _hotspot_spec()
    before_window = ((index * 10.0, LedgerTerminal.COMPLETED) for index in range(369))
    mixed_window = (
        (3900.0 + index * 10.0, LedgerTerminal.COMPLETED if index < 8 else LedgerTerminal.INCOMPLETE_ERROR)
        for index in range(11)
    )
    ledger = _build_trade_ledger(tmp_path / "trade.jsonl", [*before_window, *mixed_window])

    evidence = _capture_continuity(ledger, spec)
    assert evidence[0].facts == {"completed": 8, "denominator": 11}

    passed, _ = evaluate_required_state(spec.required_state, evidence)
    assert passed is False  # 8/11 < min_success_fraction 0.9


def test_compressed_timeline_scales_the_continuity_window() -> None:
    """The continuity window slices the same compressed timeline as the ledger,
    so a compressed run must shrink it with the other scoring boundaries."""
    # The default 12s toy horizon degenerates under ceil-rounding at scale 15
    # (input_stop and event starts both collapse to 1s), tripping the
    # last-event-start < input_stop validation; 60s keeps the boundaries ordered.
    spec = make_spec(horizon_seconds=60)
    spec = replace(spec, required_state=(ContinuityStateSpec("orders_continuity", "orders", 300.0, 0.9),))

    compressed = compress_persistent_scenario_timeline(spec, 15.0)

    assert compressed.required_state[0].window_seconds == 20.0
    assert compressed.required_state[0].min_success_fraction == 0.9
    assert compressed.required_state[0].service_id == "orders"


def test_compressed_hotspot_e2e_shape_still_passes_continuity(tmp_path: Path) -> None:
    """Compressed e2e shape: fault active early, agent
    remediates, the final business-300s window is fully recovered. With the
    scaled window the verdict stays pass; the unscaled window would honestly
    mix the fault period into the final window and fail."""
    spec = compress_persistent_scenario_timeline(_hotspot_spec(), 15.0)
    check = next(item for item in spec.required_state if item.check_id == "trade_continuity")
    assert check.window_seconds == 20.0

    # 280s compressed input span: failures before remediation (~155s), completions after.
    transactions = [
        (index * 1.0, LedgerTerminal.COMPLETED if index >= 160 else LedgerTerminal.INCOMPLETE_TIMEOUT)
        for index in range(281)
    ]
    ledger = _build_trade_ledger(tmp_path / "trade.jsonl", transactions)

    evidence = _capture_continuity(ledger, spec)
    # Window [280 - 20, 280]: the 21 transactions planned in the recovered tail.
    assert evidence[0].facts == {"completed": 21, "denominator": 21}

    passed, results = evaluate_required_state(spec.required_state, evidence)
    assert passed is True
    assert results[0]["pass"] is True

    # Without the compression scaling the window spans the whole compressed run
    # including the fault period - an honest failure, not the verdict to keep.
    unscaled = TiDBStateFactProvider._continuity_facts({"trade": ledger}, "trade", 300.0)
    assert unscaled == {"completed": 121, "denominator": 281}
