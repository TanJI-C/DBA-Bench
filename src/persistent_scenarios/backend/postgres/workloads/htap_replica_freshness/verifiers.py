"""Instance-owned required-state and integrity verifiers."""

from __future__ import annotations

from typing import Any, Mapping


def _truthy(value: Any) -> bool:
    """Normalize a PostgreSQL boolean across drivers: psycopg2 yields Python
    bools, psql -At text yields 't'/'f'."""
    return str(value).strip().lower() in {"t", "true", "1", "yes", "on"}


def _rows(open_connection, target: str, sql: str, application: str = "pg5r-htap4-verifier") -> list[tuple]:
    connection = open_connection(application, target)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        connection.rollback()
    finally:
        connection.close()
    return rows


def order_payment_conservation(open_connection, params: Mapping[str, Any]) -> Mapping[str, Any]:
    rows = _rows(
        open_connection,
        "primary",
        "SELECT (SELECT count(*) FROM frs_orders o LEFT JOIN frs_payments p ON p.order_id = o.order_id "
        "WHERE o.status = 'paid' AND p.payment_id IS NULL) + "
        "(SELECT count(*) FROM frs_orders o JOIN frs_payments p ON p.order_id = o.order_id "
        "WHERE p.amount <> o.amount) AS violations;",
    )
    violations = int(rows[0][0])
    return {
        "passed": violations == 0,
        "violation_count": violations,
        "incorrect_business_ids": [],
        "violation_detail_note": "primary-side conservation must hold row-for-row when violated" if violations else "",
    }


def replication_continuity(open_connection, params: Mapping[str, Any]) -> Mapping[str, Any]:
    """The physical slot is present and active and the standby is in recovery."""
    slot = _rows(
        open_connection,
        "primary",
        f"SELECT active, wal_status FROM pg_replication_slots WHERE slot_name = '{params.get('slot_name', 'frs_replication_slot')}';",
    )
    standby = _rows(open_connection, "standby", "SELECT pg_is_in_recovery();")
    slot_present = len(slot) == 1
    slot_active = slot_present and _truthy(slot[0][0])
    standby_in_recovery = _truthy(standby[0][0])
    return {
        "passed": slot_active and standby_in_recovery,
        "slot_present": slot_present,
        "slot_active": slot_active,
        "slot_wal_status": str(slot[0][1]) if slot_present else None,
        "standby_in_recovery": standby_in_recovery,
    }


def report_deliveries_fresh(open_connection, params: Mapping[str, Any]) -> Mapping[str, Any]:
    """Every delivered report declared a visible watermark and replay LSN."""
    rows = _rows(
        open_connection,
        "primary",
        "SELECT count(*) FROM frs_report_jobs WHERE state = 'delivered' "
        "AND (visible_watermark_seq IS NULL OR replay_lsn IS NULL OR result_digest IS NULL);",
    )
    undeclared = int(rows[0][0])
    return {
        "passed": undeclared == 0,
        "undeclared_delivery_count": undeclared,
        "incorrect_job_ids": [],
    }


VERIFIERS_BY_ID = {
    "htap4_order_payment_conservation": order_payment_conservation,
    "htap4_replication_continuity": replication_continuity,
    "htap4_report_deliveries_fresh": report_deliveries_fresh,
}
