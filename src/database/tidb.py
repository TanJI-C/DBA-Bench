"""Shared TiDB business-integrity SQL and result validation."""

import json
import re
from collections.abc import Callable

from src.database.sql import execute_result_rows, require_one_result_row


def render_tidb_plan(rows: list) -> str:
    if not rows:
        raise ValueError(f"TiDB EXPLAIN returned no rows: rows={rows!r}")
    return "\n".join(" | ".join(str(value) for value in row) for row in rows).casefold()


def executed_tidb_plan_rows(rows: list) -> list:
    """Keep only plan operators that executed or processed catalog keys."""
    if not rows:
        raise ValueError(f"TiDB EXPLAIN returned no rows: rows={rows!r}")
    executed = []
    for row in rows:
        if len(row) < 3:
            raise ValueError(f"TiDB EXPLAIN row has no actual-row column: row={row!r}")
        actual_rows = float(str(row[2]).strip())
        execution_info = " | ".join(str(value) for value in row[5:]).casefold()
        has_processed_keys = bool(
            re.search(
                r"(?:total_process_keys|proc_keys|processed_keys):\s*[1-9][0-9]*",
                execution_info,
            )
        )
        if actual_rows != 0 or has_processed_keys:
            executed.append(row)
    return executed


def processed_keys(rows: list) -> int:
    text = render_tidb_plan(rows)
    total_matches = re.findall(r"\btotal_process_keys:\s*([0-9]+)", text)
    if total_matches:
        return sum(int(value) for value in total_matches)
    matches = re.findall(
        r"(?<![A-Za-z0-9_])(?:proc_keys|processed_keys):\s*([0-9]+)",
        text,
    )
    if not matches:
        raise RuntimeError(f"TiDB EXPLAIN ANALYZE has no processed-key metric: rows={rows!r}")
    return sum(int(value) for value in matches)


def catalog_processed_keys(
    rows: list,
    *,
    table_name: str,
    index_name: str,
    table_alias: str,
) -> int:
    """Count processed rows for the catalog scan, excluding route metadata scans."""
    table_token = f"table:{table_name.casefold()}"
    alias_token = f"table:{table_alias.casefold()}"
    index_token = f"index:{index_name.casefold()}"
    total = 0
    matched = False
    for row in rows:
        if len(row) < 3:
            text = " ".join(str(value) for value in row).casefold()
            if "scan" not in text or index_name.casefold() not in text:
                raise ValueError(f"TiDB EXPLAIN row has no actual-row column: row={row!r}")
            metrics = re.findall(
                r"(?:total_process_keys|proc_keys|processed_keys):\s*([0-9]+)",
                text,
            )
            if not metrics:
                raise RuntimeError(
                    f"TiDB EXPLAIN catalog row has no processed-key metric: row={row!r}"
                )
            matched = True
            total += sum(int(value) for value in metrics)
            continue
        operator = str(row[0]).casefold()
        access = " ".join(str(value) for value in row[4:]).casefold()
        if "scan" not in operator or not (
            table_token in access
            or alias_token in access
            or index_token in access
            or index_name.casefold() in access
        ):
            continue
        matched = True
        execution_info = " | ".join(str(value) for value in row[5:]).casefold()
        metrics = re.findall(
            r"(?:total_process_keys|proc_keys|processed_keys):\s*([0-9]+)",
            execution_info,
        )
        total += sum(int(value) for value in metrics) if metrics else int(float(str(row[2]).strip()))
    if not matched:
        raise RuntimeError(
            "TiDB EXPLAIN ANALYZE has no catalog scan for the requested target: "
            f"table={table_name!r}, index={index_name!r}, rows={rows!r}"
        )
    return total


def qp01_plan_metrics(rows: list) -> dict[str, object]:
    text = json.dumps(rows, ensure_ascii=False, default=str).casefold()
    scan_rows = [
        row
        for row in rows
        if isinstance(row, (list, tuple))
        and row
        and len(row) > 4
        and "table:o" in str(row[4]).casefold()
        and any(
            operator in str(row[0]).casefold()
            for operator in (
                "indexrangescan",
                "indexfullscan",
                "tablerangescan",
                "tablefullscan",
            )
        )
    ]
    if len(scan_rows) != 1:
        raise RuntimeError(f"QP01 EXPLAIN ANALYZE has no catalog scan actRows: rows={rows!r}")
    index_scan = scan_rows[0]
    policy_scan_rows = [
        row
        for row in rows
        if isinstance(row, (list, tuple))
        and len(row) > 4
        and "table:p" in str(row[4]).casefold()
        and any(
            operator in str(row[0]).casefold()
            for operator in (
                "tablerangescan",
                "indexrangescan",
                "indexfullscan",
                "tablefullscan",
            )
        )
    ]
    process_keys = re.search(r"proc_keys:\s*([0-9]+)", text)
    return {
        "plan": rows,
        "index_scan_rows": int(index_scan[2]),
        "catalog_scan_operator": str(index_scan[0]).casefold(),
        "policy_scan_rows": max((int(row[2]) for row in policy_scan_rows), default=None),
        "process_keys": int(process_keys.group(1)) if process_keys else None,
        "plan_text": text,
    }


_TIDB_SCAN_OPERATORS = (
    "indexrangescan",
    "indexfullscan",
    "tablerangescan",
    "tablefullscan",
)


def tidb_plan_metrics(rows: list, table: str) -> dict[str, object]:
    """Extract generic TiDB scan facts without depending on an index name."""
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"TiDB plan rows must be a non-empty list: rows={rows!r}")

    text = json.dumps(rows, ensure_ascii=False, default=str).casefold()
    table_name = table.casefold()
    scan_rows = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or not row:
            continue
        operator = str(row[0]).casefold()
        row_text = " ".join(str(value) for value in row).casefold()
        if table_name not in row_text or not any(
            operator_name in operator for operator_name in _TIDB_SCAN_OPERATORS
        ):
            continue
        if len(row) < 3:
            raise ValueError(
                f"TiDB scan row must expose estimated and actual rows: table={table!r}, row={row!r}"
            )
        try:
            actual_rows = float(row[2])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"TiDB scan row actual-row column is not numeric: table={table!r}, row={row!r}"
            ) from exc
        scan_rows.append(
            {
                "operator": str(row[0]),
                "actual_rows": int(actual_rows),
                "row": list(row),
            }
        )

    if not scan_rows:
        raise RuntimeError(
            f"TiDB EXPLAIN ANALYZE has no scan row for table={table!r}: rows={rows!r}"
        )

    process_key_values = [
        int(value)
        for value in re.findall(r"(?:total_)?process_keys:\s*([0-9]+)", text)
    ]
    process_key_values.extend(
        int(value) for value in re.findall(r"proc_keys:\s*([0-9]+)", text)
    )
    scan_volume = max([item["actual_rows"] for item in scan_rows] + process_key_values)
    return {
        "plan_text": text,
        "scan_rows": tuple(scan_rows),
        "scan_volume": scan_volume,
        "process_keys": max(process_key_values, default=None),
        "has_index_reader": "indexreader" in text,
        "has_index_lookup": "indexlookup" in text,
        "has_table_row_id_scan": "tablerowidscan" in text,
        "index_definitions": tuple(re.findall(r"index:[^,\]]+", text)),
        "range_fragments": tuple(re.findall(r"range:\s*[^,\]]+", text)),
    }


def execute_integrity_tuple(
    execute: Callable[[str], object],
    sql: str,
    context: str,
) -> tuple[int, int, int]:
    row = require_one_result_row(execute_result_rows(execute, sql, context), context)
    if len(row) != 3:
        raise ValueError(f"{context} expected three integrity columns: sql={sql!r}, row={row!r}")
    return tuple(int(value) for value in row)


def table_cache_lease_integrity_sql(
    db: str,
    table: str,
    *,
    cache_table: str,
    cache_integrity_sql: str,
    orders_table: str,
    inventory_table: str,
    pricing_table: str,
    healthy_cache_table_names: tuple[str, ...],
) -> str:
    if table == cache_table:
        return cache_integrity_sql
    if table == orders_table:
        return (
            "SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
            "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, tenant_id, sku_id, amount, status))), 0) "
            f"FROM {db}.{table}"
        )
    if table == inventory_table:
        return (
            "SELECT COUNT(*), COALESCE(SUM(sku_id), 0), "
            "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', sku_id, warehouse_id, available, reserved))), 0) "
            f"FROM {db}.{table}"
        )
    if table == pricing_table:
        return (
            "SELECT COUNT(*), COALESCE(SUM(rule_id), 0), "
            "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', rule_id, tenant_id, category, discount_pct, priority, active))), 0) "
            f"FROM {db}.{table}"
        )
    if table in healthy_cache_table_names:
        return (
            "SELECT COUNT(*), COALESCE(SUM(sku_id), 0), "
            "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', sku_id, tenant_id, category, price, stock))), 0) "
            f"FROM {db}.{table}"
        )
    raise ValueError(f"table-cache-lease integrity query requested for unknown table: table={table!r}")
