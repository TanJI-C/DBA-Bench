"""Required report contracts, canonical SQL and streaming result digests.

Each required report is a downstream delivery with a pre-declared result shape and a
batch cutoff binding. The executing SQL is free: a job body rewritten through the
public queue passes acceptance only when its result satisfies the declared contract.
Correctness is decided by comparing the delivered result digest with the digest of the
canonical reference result recomputed from the append-only fact table at the job's
bound cutoff (integrity verifier `wh_report_result_truth`).
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

from .schema import BATCH_A_ID, BATCH_B_ID


@dataclass(frozen=True, slots=True)
class ReportContract:
    report_id: str
    title: str
    columns: tuple[str, ...]
    ordered: bool
    binds_exact_batch: bool = False
    freshness_declared: bool = False

    def __post_init__(self) -> None:
        if not self.report_id:
            raise ValueError("report contract report_id must be non-empty")
        if not self.columns:
            raise ValueError(f"report contract must declare result columns: report_id={self.report_id!r}")


REPORT_STORE_DAILY_REVENUE = ReportContract(
    report_id="store_daily_revenue",
    title="Daily revenue by store for all batches up to the cutoff",
    columns=("sold_date_sk", "store_sk", "total_quantity", "total_revenue"),
    ordered=True,
)
REPORT_ITEM_MARGIN_TOP50 = ReportContract(
    report_id="item_margin_top50",
    title="Top 50 items by accumulated margin up to the cutoff",
    columns=("item_sk", "margin"),
    ordered=True,
)
REPORT_ITEM_DATE_MATRIX = ReportContract(
    report_id="item_date_matrix",
    title="Item by sold-date quantity matrix up to the cutoff",
    columns=("item_sk", "sold_date_sk", "total_quantity"),
    ordered=False,
)
REPORT_HOT_ITEM_RANGE = ReportContract(
    report_id="hot_item_range",
    title="Quantity and revenue for the skewed item range up to the cutoff",
    columns=("item_sk", "total_quantity", "net_revenue"),
    ordered=True,
)
REPORT_BATCH_CUSTOMER_CONCENTRATION = ReportContract(
    report_id="batch_customer_concentration",
    title="Top 100 customers by quantity inside the exact ingest batch",
    columns=("customer_sk", "total_quantity"),
    ordered=True,
    binds_exact_batch=True,
    freshness_declared=True,
)

REQUIRED_REPORTS: tuple[ReportContract, ...] = (
    REPORT_STORE_DAILY_REVENUE,
    REPORT_ITEM_MARGIN_TOP50,
    REPORT_ITEM_DATE_MATRIX,
    REPORT_HOT_ITEM_RANGE,
    REPORT_BATCH_CUSTOMER_CONCENTRATION,
)
REQUIRED_REPORT_IDS: frozenset[str] = frozenset(report.report_id for report in REQUIRED_REPORTS)

# deliverable_id == job_id: deterministic per (report, ingest batch),
# using the core loader identifier alphabet ([A-Za-z0-9_-], no "__").
def deliverable_job_id(report_id: str, batch_id: int) -> str:
    if report_id not in REQUIRED_REPORT_IDS:
        raise KeyError(f"unknown required report: report_id={report_id!r}, known={sorted(REQUIRED_REPORT_IDS)!r}")
    return f"{report_id}_batch{batch_id}"


def deliverable_cutoff(job_id: str) -> int:
    match = re.fullmatch(r".+_batch(\d+)", job_id)
    if match is None:
        raise ValueError(f"required report job id lost its batch binding: job_id={job_id!r}")
    return int(match.group(1))


def report_contract(report_id: str) -> ReportContract:
    for contract in REQUIRED_REPORTS:
        if contract.report_id == report_id:
            return contract
    raise KeyError(f"unknown required report: report_id={report_id!r}, known={sorted(REQUIRED_REPORT_IDS)!r}")


def canonical_report_sql(report_id: str, cutoff_batch_id: int) -> str:
    """Canonical reference SQL for a report bound to a cutoff; also the default job body."""
    if report_id == REPORT_STORE_DAILY_REVENUE.report_id:
        return (
            "SELECT sold_date_sk, store_sk, sum(quantity) AS total_quantity, "
            "round(sum(net_paid), 2) AS total_revenue "
            f"FROM wh.batch_sales WHERE batch_id <= {cutoff_batch_id} "
            "GROUP BY sold_date_sk, store_sk ORDER BY sold_date_sk, store_sk"
        )
    if report_id == REPORT_ITEM_MARGIN_TOP50.report_id:
        return (
            "SELECT item_sk, round(sum(net_profit), 2) AS margin "
            f"FROM wh.batch_sales WHERE batch_id <= {cutoff_batch_id} "
            "GROUP BY item_sk ORDER BY margin DESC, item_sk LIMIT 50"
        )
    if report_id == REPORT_ITEM_DATE_MATRIX.report_id:
        return (
            "SELECT item_sk, sold_date_sk, sum(quantity) AS total_quantity "
            f"FROM wh.batch_sales WHERE batch_id <= {cutoff_batch_id} "
            "GROUP BY item_sk, sold_date_sk"
        )
    if report_id == REPORT_HOT_ITEM_RANGE.report_id:
        return (
            "SELECT item_sk, sum(quantity) AS total_quantity, round(sum(net_paid), 2) AS net_revenue "
            f"FROM wh.batch_sales WHERE batch_id <= {cutoff_batch_id} "
            "AND item_sk BETWEEN 101 AND 250 GROUP BY item_sk ORDER BY item_sk"
        )
    if report_id == REPORT_BATCH_CUSTOMER_CONCENTRATION.report_id:
        return (
            "SELECT customer_sk, sum(quantity) AS total_quantity "
            f"FROM wh.batch_sales WHERE batch_id = {cutoff_batch_id} "
            "GROUP BY customer_sk ORDER BY total_quantity DESC, customer_sk LIMIT 100"
        )
    raise KeyError(f"no canonical SQL for report: report_id={report_id!r}")


def _row_line(columns: list[str], row: list) -> str:
    return json.dumps({"c": columns, "r": [str(value) for value in row]}, ensure_ascii=False, sort_keys=True)


def streaming_result_digest(cursor, *, ordered: bool) -> str:
    """Deterministic digest over the full result, streamed in chunks.

    Ordered contracts chain row hashes in result order; unordered contracts combine
    row hashes commutatively so only the row multiset matters. Both carry the row
    count so shape drift cannot cancel out.
    """
    if cursor.description is None:
        raise ValueError("report execution produced no result set; the declared contract requires rows")
    columns = [description.name for description in cursor.description]
    chain = hashlib.sha256(("|".join(columns)).encode("utf-8"))
    combine = 0
    count = 0
    while True:
        rows = cursor.fetchmany(20_000)
        if not rows:
            break
        for row in rows:
            line = _row_line(columns, list(row)).encode("utf-8")
            row_digest = hashlib.sha256(line).digest()
            if ordered:
                chain.update(row_digest)
            else:
                combine = (combine + int.from_bytes(row_digest, "big")) % (1 << 256)
            count += 1
    kind = "ordered" if ordered else "multiset"
    tail = chain.hexdigest() if ordered else f"{combine:064x}"
    return f"{kind}:{count}:{tail}"


def reference_result_digest(connection, report_id: str, cutoff_batch_id: int) -> str:
    """Recompute canonical reference truth for (report, cutoff) with a trusted connection."""
    contract = report_contract(report_id)
    with connection.cursor() as cursor:
        cursor.execute(canonical_report_sql(report_id, cutoff_batch_id))
        columns = [description.name for description in cursor.description]
        expected_columns = list(contract.columns)
        if columns != expected_columns:
            raise RuntimeError(
                "canonical report result shape drifted from the declared contract: "
                f"report_id={report_id!r}, expected_columns={expected_columns!r}, actual_columns={columns!r}"
            )
        return streaming_result_digest(cursor, ordered=contract.ordered)


def digest_row_count(result_digest: str) -> int:
    kind, count, _tail = result_digest.split(":", 2)
    if kind not in {"ordered", "multiset"}:
        raise ValueError(f"unknown result digest kind: digest={result_digest!r}")
    return int(count)
