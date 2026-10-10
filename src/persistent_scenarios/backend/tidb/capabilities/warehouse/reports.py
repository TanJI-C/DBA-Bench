"""Report contracts and frozen-truth computation for the warehouse delivery service.

A report is recomputed over the fact table up to a batch cutoff; the delivered
digest must equal that recomputation (the "through_batch" binding), so stale
results can never pass as a newer report. All SQL is TiDB-dialect against `wh.*`.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib


@dataclass(frozen=True, slots=True)
class ReportContract:
    report_id: str
    sql_template: str          # formatted with {cutoff}
    ordered: bool              # True: row order is part of the result identity


REPORT_CONTRACTS = (
    ReportContract(
        "region_daily_revenue",
        "SELECT region_id, DATE(order_ts) AS day, SUM(amount) AS revenue, COUNT(*) AS orders "
        "FROM wh.orders WHERE batch_id <= {cutoff} "
        "GROUP BY region_id, DATE(order_ts) ORDER BY region_id, day",
        ordered=True,
    ),
    ReportContract(
        "item_margin_top50",
        "SELECT item_id, SUM(amount - quantity * unit_cost) AS margin "
        "FROM wh.orders WHERE batch_id <= {cutoff} "
        "GROUP BY item_id ORDER BY margin DESC, item_id LIMIT 50",
        ordered=True,
    ),
    ReportContract(
        "warehouse_throughput",
        "SELECT warehouse_id, DATE(order_ts) AS day, SUM(quantity) AS units "
        "FROM wh.orders WHERE batch_id <= {cutoff} "
        "GROUP BY warehouse_id, DATE(order_ts) ORDER BY warehouse_id, day",
        ordered=True,
    ),
    ReportContract(
        "channel_settlement",
        "SELECT channel, batch_id, SUM(amount) AS amount, COUNT(*) AS orders "
        "FROM wh.orders WHERE batch_id <= {cutoff} "
        "GROUP BY channel, batch_id ORDER BY channel, batch_id",
        ordered=True,
    ),
    ReportContract(
        "region_group_share",
        "SELECT r.group_name, SUM(o.amount) AS amount "
        "FROM wh.orders o JOIN wh.dim_region r ON r.region_id = o.region_id "
        "WHERE o.batch_id <= {cutoff} "
        "GROUP BY r.group_name ORDER BY r.group_name",
        ordered=True,
    ),
)
REPORT_CONTRACTS_BY_ID = {contract.report_id: contract for contract in REPORT_CONTRACTS}

REQUIRED_REPORT_IDS = (
    "region_daily_revenue",
    "item_margin_top50",
    "warehouse_throughput",
    "channel_settlement",
    "region_group_share",
)

BATCH_SUFFIXES = ("batch1", "batch2")


def deliverable_report_id(deliverable_id: str) -> str:
    """`region_daily_revenue_batch1` -> `region_daily_revenue`; unknown suffixes raise."""
    for suffix in BATCH_SUFFIXES:
        if deliverable_id.endswith(f"_{suffix}"):
            return deliverable_id[: -len(suffix) - 1]
    raise KeyError(f"deliverable id does not carry a batch suffix: deliverable_id={deliverable_id!r}")


def deliverable_cutoff(deliverable_id: str) -> int:
    """through_batch binding: a batch2 report covers history plus batches 1 and 2."""
    return deliverable_batch_number(deliverable_id)


def deliverable_batch_number(deliverable_id: str) -> int:
    if deliverable_id.endswith("_batch1"):
        return 1
    if deliverable_id.endswith("_batch2"):
        return 2
    raise KeyError(f"deliverable id does not carry a batch suffix: deliverable_id={deliverable_id!r}")


def report_sql(report_id: str, cutoff: int) -> str:
    contract = REPORT_CONTRACTS_BY_ID[report_id]
    return contract.sql_template.format(cutoff=int(cutoff))


def streaming_result_digest(cursor, *, ordered: bool) -> tuple[str, int]:
    """Hash the result rows (in delivery order, or sorted for unordered sets); return digest and row count."""
    digest = hashlib.sha256()
    rows = list(cursor.fetchall())
    if not ordered:
        rows = sorted(rows, key=lambda row: tuple(str(value) for value in row))
    for row in rows:
        digest.update("\x1f".join(str(value) for value in row).encode("utf-8"))
        digest.update(b"\x1e")
    return digest.hexdigest(), len(rows)


def deliverable_job_id(report_id: str, batch_number: int) -> str:
    return f"{report_id}_batch{batch_number}"
