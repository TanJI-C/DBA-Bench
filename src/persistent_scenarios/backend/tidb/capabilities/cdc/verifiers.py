"""Instance-owned verifiers for tidb_cdc_downstream_freshness.

Verifiers encode the instance business contract and
are executed by the backend during final sampling to produce trusted facts;
evaluation never runs SQL. Changefeed state and checkpoint TSO are auxiliary
evidence only - the decision inputs are the source-commit ledger and the
downstream business markers.

Convention: every verifier is
callable as ``__call__(params, *, upstream, downstream, ledger_view)``
returning a JSON-safe detail mapping with a top-level ``passed`` bool.
``upstream``/``downstream`` are live DBAPI connections; ``ledger_view`` is a
core ``LedgerView`` over one trusted ledger.
"""

from __future__ import annotations

from typing import Mapping

from src.persistent_scenarios.runtime.ledger import LedgerTerminal, LedgerView

from .markers import fetch_downstream_versions, fetch_upstream_committed, pair_orders
from .schema import UPSTREAM_DATABASE, ORDERS_TABLE


class _Verifier:
    verifier_id: str = ""
    kind: str = ""

    def detail(self, passed: bool, **fields) -> Mapping[str, object]:
        return {"verifier_id": self.verifier_id, "kind": self.kind, "passed": passed, **fields}


class CdcMarkerPairingVerifier(_Verifier):
    """DataIntegrity: every source-committed order in the check range is
    visible downstream with the committed version and marker - no holes
    before the promised watermark."""

    verifier_id = "cdc_marker_pairing"
    kind = "result_truth"

    def __call__(self, params, *, upstream, downstream, ledger_view) -> Mapping[str, object]:
        from_order_id = int(params.get("from_order_id", 1))
        through_order_id = params.get("through_order_id")
        up_cursor = upstream.cursor()
        down_cursor = downstream.cursor()
        if through_order_id is None:
            # the promised watermark is the sampling instant: every source commit
            # up to final sampling must be visible downstream
            up_cursor.execute(f"SELECT COALESCE(MAX(order_id), 0) FROM {UPSTREAM_DATABASE}.{ORDERS_TABLE}")
            through_order_id = int(up_cursor.fetchall()[0][0])
        through_order_id = int(through_order_id)
        up_cursor.execute(
            f"SELECT order_id, version, marker FROM {UPSTREAM_DATABASE}.{ORDERS_TABLE} "
            f"WHERE order_id >= {from_order_id} AND order_id <= {through_order_id}"
        )
        committed = {
            int(row[0]): (int(row[1]), str(row[2]))
            for row in up_cursor.fetchall()
        }
        observed = fetch_downstream_versions(down_cursor, sorted(committed))
        missing = []
        stale = []
        marker_mismatch = []
        for order_id, (version, marker) in committed.items():
            down = observed.get(order_id)
            if down is None:
                missing.append(order_id)
            elif down[0] < version:
                stale.append([order_id, version, down[0]])
            elif down[2] != marker:
                marker_mismatch.append(order_id)
        report = {
            "checked": len(committed),
            "missing_order_ids": missing[:500],
            "missing_count": len(missing),
            "stale_versions": stale[:500],
            "stale_count": len(stale),
            "marker_mismatch_order_ids": marker_mismatch[:500],
            "marker_mismatch_count": len(marker_mismatch),
        }
        return self.detail(not (missing or stale or marker_mismatch), **report)


class CdcUpstreamLedgerConservationVerifier(_Verifier):
    """DataIntegrity: the upstream order table and the source-commit ledger
    agree. The orders table stores one row per business key updated in place,
    so conservation is decided per order: the row must carry exactly the
    newest ledger-committed (version, marker) - a newer row proves older
    commits applied, a missing or diverging row is a lost commit, and a row
    without ledger backing is fabricated. ``exclude_order_ids`` removes rows
    authored outside the trading ledger (fault-injection probe orders) from
    the pairing universe on both sides."""

    verifier_id = "cdc_upstream_ledger_conservation"
    kind = "result_truth"

    def __call__(self, params, *, upstream, downstream, ledger_view) -> Mapping[str, object]:
        from_order_id = int(params.get("from_order_id", 1_000_000))
        excluded = {int(order_id) for order_id in params.get("exclude_order_ids", ())}
        up_cursor = upstream.cursor()
        up_cursor.execute(
            f"SELECT order_id, version, marker FROM {UPSTREAM_DATABASE}.{ORDERS_TABLE} "
            f"WHERE order_id >= {from_order_id}"
        )
        rows = {int(row[0]): (int(row[1]), str(row[2]))
                for row in up_cursor.fetchall() if int(row[0]) not in excluded}
        latest: dict[int, tuple[int, str]] = {}
        for record in ledger_view.logical_transactions():
            if record.terminal is not LedgerTerminal.COMPLETED or record.result_digest is None:
                continue
            order_id_str, version_str, _state, marker = record.result_digest.split(":", 3)
            order_id, version = int(order_id_str), int(version_str)
            known = latest.get(order_id)
            if known is None or version >= known[0]:
                latest[order_id] = (version, marker)
        ledger_missing_in_db = [
            {"order_id": order_id, "ledger_version": version, "db_version": rows[order_id][0]
             if order_id in rows else None}
            for order_id, (version, marker) in sorted(latest.items())
            if rows.get(order_id) != (version, marker)
        ]
        db_missing_in_ledger = [
            {"order_id": order_id, "db_version": version}
            for order_id, (version, _marker) in sorted(rows.items())
            if order_id not in latest
        ]
        return self.detail(
            not ledger_missing_in_db and not db_missing_in_ledger,
            ledger_orders=len(latest),
            workload_db_rows=len(rows),
            ledger_missing_in_db=ledger_missing_in_db[:500],
            ledger_missing_in_db_count=len(ledger_missing_in_db),
            db_missing_in_ledger=db_missing_in_ledger[:500],
            db_missing_in_ledger_count=len(db_missing_in_ledger),
        )


class CdcDownstreamCaughtUpVerifier(_Verifier):
    """RequiredState (business continuation): orders the source committed in
    the final catch-up window are all visible downstream - the replication
    path is still advancing at the horizon, not merely historically complete.

    The window is derived from the visibility ledger (assembly must wire the
    visibility ledger view): the anchor is the latest planned obligation and
    the range covers every order committed within ``window_seconds`` of it.
    """

    verifier_id = "cdc_downstream_caught_up"
    kind = "business_state"

    def __call__(self, params, *, upstream, downstream, ledger_view) -> Mapping[str, object]:
        window_seconds = float(params["window_seconds"])
        records = ledger_view.logical_transactions()
        if not records:
            raise ValueError(
                "cdc_downstream_caught_up requires a non-empty visibility ledger view; "
                "assembly must wire the visibility ledger"
            )
        anchor = max(record.planned_at_monotonic for record in records)
        order_ids = {
            int(record.business_id.split(":")[0].removeprefix("order-"))
            for record in records
            if record.business_id.startswith("order-")
            and anchor - record.planned_at_monotonic <= window_seconds
        }
        if not order_ids:
            raise ValueError(
                "cdc_downstream_caught_up found no commits inside the catch-up window: "
                f"anchor={anchor}, window_seconds={window_seconds}"
            )
        up_cursor = upstream.cursor()
        down_cursor = downstream.cursor()
        committed = fetch_upstream_committed(up_cursor, sorted(order_ids))
        report = pair_orders(down_cursor, committed)
        return self.detail(report.complete,
                           window_seconds=window_seconds,
                           window_order_count=len(committed),
                           **report.as_details())


class CdcVisibilityDeadlineVerifier(_Verifier):
    """RequiredState (freshness contract): over the whole run the fraction of
    visibility obligations resolved within the business deadline meets the
    declared minimum - state=normal with a frozen checkpoint cannot hide it."""

    verifier_id = "cdc_visibility_deadline"
    kind = "business_state"

    def __call__(self, params, *, upstream, downstream, ledger_view) -> Mapping[str, object]:
        if not isinstance(ledger_view, LedgerView):
            raise TypeError(
                f"cdc_visibility_deadline requires a core LedgerView: value={type(ledger_view).__name__}"
            )
        min_fraction = float(params["min_success_fraction"])
        records = ledger_view.logical_transactions()
        total = len(records)
        good = sum(1 for record in records if record.good)
        fraction = good / total if total else 0.0
        worst = max(
            (record.completed_at_monotonic - record.planned_at_monotonic
             for record in records
             if record.terminal is LedgerTerminal.COMPLETED and record.completed_at_monotonic),
            default=None,
        )
        return self.detail(
            total > 0 and fraction >= min_fraction,
            total_obligations=total,
            good_obligations=good,
            success_fraction=round(fraction, 6),
            min_success_fraction=min_fraction,
            worst_visible_seconds=round(worst, 3) if worst is not None else None,
        )


VERIFIERS: tuple[_Verifier, ...] = (
    CdcMarkerPairingVerifier(),
    CdcUpstreamLedgerConservationVerifier(),
    CdcDownstreamCaughtUpVerifier(),
    CdcVisibilityDeadlineVerifier(),
)
