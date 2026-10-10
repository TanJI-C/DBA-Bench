"""Instance-owned required-state and integrity verifier implementations.

Verifier implementations belong to the instance
package (they encode the business contract), integration wires them into the
backend, and the backend executes them during final sampling to produce
trusted facts; evaluation never runs SQL.

Result-truth verifiers emit evaluation-compatible details: a FAILED verdict
lists the offending identities under ``incorrect_business_ids`` /
``incorrect_job_ids`` (evaluation/slo.py consumes exactly these keys).
"""

from __future__ import annotations

from typing import Mapping

from .ledger import OrderBookSnapshot, verify_conservation
from .ports import DBConnection
from ..business_priority.archive import verify_archive_delivery, verify_archive_tradeoff
from ..online_change.backfill import verify_backfill_delivery, verify_release_index

_SAMPLE_CAP = 500


def commerce_ledger_conservation(params: Mapping[str, object], *, ops, snapshot: OrderBookSnapshot) -> Mapping[str, object]:
    """Integrity check (result_truth): the external trade ledger and the database agree."""

    report = verify_conservation(ops, snapshot)
    return {
        "verifier_id": "commerce_ledger_conservation",
        "kind": "result_truth",
        "passed": report.conserved,
        "denominator_ops": report.denominator_ops,
        "committed_ops": report.committed_ops,
        "good_ops": report.good_ops,
        "incorrect_business_ids": list(report.incorrect_business_ids)[:_SAMPLE_CAP],
        "incorrect_business_id_count": len(report.incorrect_business_ids),
        "failures": list(report.failures)[:50],
    }


def archive_delivery(params: Mapping[str, object], *, ops, snapshot: OrderBookSnapshot) -> Mapping[str, object]:
    """Integrity check (result_truth): every eligible history order reached the archive."""

    cutoff = float(params["cutoff_created_at"])
    job_id = str(params.get("job_id", "orders-history-archive"))
    deadline_note = str(params.get("deadline_note", ""))
    failures = verify_archive_delivery(snapshot, cutoff_created_at=cutoff, deadline_note=deadline_note)
    return {
        "verifier_id": "archive_delivery",
        "kind": "result_truth",
        "passed": not failures,
        "cutoff_created_at": cutoff,
        "incorrect_job_ids": [] if not failures else [job_id],
        "failures": list(failures)[:50],
    }


def _backfill_incorrect_ids(snapshot: OrderBookSnapshot) -> tuple[list[str], int]:
    from ..oltp_core.schema import promo_tier_for_amount

    incorrect: list[str] = []
    for order_id, row in snapshot.orders.items():
        expected = promo_tier_for_amount(row.amount_cents)
        if row.promo_tier is None or row.promo_tier != expected:
            incorrect.append(order_id)
    return incorrect, len(incorrect)


def backfill_completeness(params: Mapping[str, object], *, ops, snapshot: OrderBookSnapshot) -> Mapping[str, object]:
    """Integrity check (result_truth): every order carries the derived promotion tier."""

    backfill_job_id = str(params.get("backfill_job_id", "backfill_promo_tier"))
    failures = verify_backfill_delivery(snapshot)
    incorrect_ids, incorrect_count = _backfill_incorrect_ids(snapshot)
    return {
        "verifier_id": "backfill_completeness",
        "kind": "result_truth",
        "passed": not failures,
        "rows_checked": len(snapshot.orders),
        "incorrect_business_ids": incorrect_ids[:_SAMPLE_CAP],
        "incorrect_business_id_count": incorrect_count,
        "incorrect_job_ids": [] if not failures else [backfill_job_id],
        "failures": list(failures)[:50],
    }


def release_index_valid(params: Mapping[str, object], *, ops, snapshot: OrderBookSnapshot,
                        connection: DBConnection | None = None) -> Mapping[str, object]:
    """Required-state check: a valid index serves the released query pattern."""

    schema = str(params.get("schema", "shop"))
    table = str(params.get("table", "orders"))
    column = str(params["column"])
    indexes: dict[str, tuple[bool, set[str]]] = {}
    if connection is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT i.relname, ix.indisvalid, a.attname "
                "FROM pg_index ix "
                "JOIN pg_class i ON i.oid = ix.indexrelid "
                "JOIN pg_class t ON t.oid = ix.indrelid "
                "JOIN pg_namespace n ON n.oid = t.relnamespace "
                "JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey::int2[]) "
                "WHERE n.nspname = %(schema)s AND t.relname = %(table)s;",
                {"schema": schema, "table": table},
            )
            rows = cursor.fetchall()
        for index_name, is_valid, attribute in rows:
            valid, columns = indexes.setdefault(str(index_name), (bool(is_valid), set()))
            columns.add(str(attribute))
    failures = verify_release_index(indexes, table=f"{schema}.{table}", column=column)
    return {
        "verifier_id": "release_index_valid",
        "passed": not failures,
        "indexes": {name: (valid, sorted(cols)) for name, (valid, cols) in indexes.items()},
        "failures": list(failures)[:20],
    }


def archive_delivery_tradeoff(params: Mapping[str, object], *, ops, snapshot: OrderBookSnapshot,
                              connection: DBConnection) -> Mapping[str, object]:
    """Integrity check (result_truth): the archive control history honours the
    published delivery contract (peak-window rate cap, rate ceiling, deferral
    budget). Reads the trigger-maintained ops.archive_state_audit trail."""

    job_id = str(params.get("job_id", "orders-history-archive"))
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT changed_at, enabled, rate_rows_per_second, rows_moved FROM ops.archive_state_audit "
            "WHERE job_id = %(job_id)s ORDER BY audit_seq;",
            {"job_id": job_id},
        )
        rows = cursor.fetchall()
    controls = [(float(row[0]), bool(row[1]), int(row[2]), int(row[3])) for row in rows]
    failures, summary = verify_archive_tradeoff(
        controls,
        scoring_start_epoch=float(params["scoring_start_epoch"]),
        peak_window_start_seconds=float(params["peak_window_start_seconds"]),
        peak_window_end_seconds=float(params["peak_window_end_seconds"]),
        peak_grace_seconds=float(params["peak_grace_seconds"]),
        peak_rate_cap_rows_per_second=int(params["peak_rate_cap_rows_per_second"]),
        rate_ceiling_rows_per_second=int(params["rate_ceiling_rows_per_second"]),
        deferral_budget_seconds=float(params["deferral_budget_seconds"]),
        total_rows=int(params["total_history_rows"]),
        horizon_seconds=float(params["horizon_seconds"]),
        deadline_note=str(params.get("deadline_note", "")),
    )
    return {
        "verifier_id": "archive_delivery_tradeoff",
        "kind": "result_truth",
        "passed": not failures,
        "incorrect_job_ids": [] if not failures else [job_id],
        "failures": list(failures)[:50],
        "control_changes": len(controls),
        **summary,
    }


VERIFIERS = {
    "commerce_ledger_conservation": commerce_ledger_conservation,
    "archive_delivery": archive_delivery,
    "archive_delivery_tradeoff": archive_delivery_tradeoff,
    "backfill_completeness": backfill_completeness,
    "release_index_valid": release_index_valid,
}


def run_verifier(verifier_id: str, params: Mapping[str, object], **evidence) -> Mapping[str, object]:
    verifier = VERIFIERS.get(verifier_id)
    if verifier is None:
        raise ValueError(
            f"Unknown instance verifier: verifier_id={verifier_id!r}, known={sorted(VERIFIERS)!r}"
        )
    return verifier(params, **evidence)
