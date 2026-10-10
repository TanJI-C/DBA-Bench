"""Instance-owned required-state and integrity verifiers.

Verifier ids registered here are referenced by spec.required_state and
spec.integrity_checks; integration assembles them into the backend and final
sampling executes them against trusted connections only.
"""

from __future__ import annotations

from typing import Any, Mapping


def _rows(open_connection, sql: str, application: str = "pg5r-htap3-verifier") -> list[tuple]:
    connection = open_connection(application, "primary")
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        connection.rollback()
    finally:
        connection.close()
    return rows


def order_payment_conservation(open_connection, params: Mapping[str, Any]) -> Mapping[str, Any]:
    """Every paid order has exactly one payment of equal amount."""
    rows = _rows(
        open_connection,
        "SELECT (SELECT count(*) FROM htap_orders o LEFT JOIN htap_payments p ON p.order_id = o.order_id "
        "WHERE o.status = 'paid' AND p.payment_id IS NULL) + "
        "(SELECT count(*) FROM htap_orders o JOIN htap_payments p ON p.order_id = o.order_id "
        "WHERE p.amount <> o.amount) AS violations, "
        "(SELECT count(*) FROM htap_orders WHERE status = 'paid');",
    )
    violations = int(rows[0][0])
    if violations != 0:
        detail_rows = _rows(
            open_connection,
            "SELECT o.order_id FROM htap_orders o LEFT JOIN htap_payments p ON p.order_id = o.order_id "
            "WHERE o.status = 'paid' AND p.payment_id IS NULL UNION ALL "
            "SELECT o.order_id FROM htap_orders o JOIN htap_payments p ON p.order_id = o.order_id "
            "WHERE p.amount <> o.amount LIMIT 100;",
        )
        incorrect = [str(row[0]) for row in detail_rows]
    else:
        incorrect = []
    return {
        "passed": violations == 0,
        "violation_count": violations,
        "incorrect_business_ids": incorrect,
        "paid_order_count": int(rows[0][1]),
    }


def inventory_non_negative(open_connection, params: Mapping[str, Any]) -> Mapping[str, Any]:
    rows = _rows(open_connection, "SELECT count(*) FROM htap_inventory WHERE on_hand < 0 OR reserved < 0;")
    return {"passed": int(rows[0][0]) == 0, "violation_count": int(rows[0][0])}


def export_checkpoints_complete(open_connection, params: Mapping[str, Any]) -> Mapping[str, Any]:
    """Every committed export binding covers its bound range without gaps."""
    connection = open_connection("pg5r-htap3-verifier", "primary")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT j.ref, j.range_end, COALESCE(c.last_line_id, 0), COALESCE(c.pages, 0), COALESCE(c.page_rows, 0) "
                "FROM htap_analysis_jobs j LEFT JOIN ("
                "SELECT export_id, max(last_line_id) AS last_line_id, count(*) AS pages, sum(page_rows) AS page_rows "
                "FROM htap_export_checkpoints GROUP BY export_id) c ON c.export_id = j.binding "
                "WHERE j.kind = 'export' AND j.state = 'done';"
            )
            rows = cursor.fetchall()
        connection.rollback()
    finally:
        connection.close()
    incomplete = []
    for ref, bound_line_id, last_line, pages, page_rows in rows:
        if int(last_line) < int(bound_line_id) or int(pages) == 0 or int(page_rows) < int(bound_line_id):
            incomplete.append(str(ref))
    return {
        "passed": len(incomplete) == 0,
        "checked_export_count": len(rows),
        "incomplete_export_bindings": incomplete,
        "incorrect_job_ids": incomplete,
    }


def analysis_role_timeout_effective(open_connection, params: Mapping[str, Any]) -> Mapping[str, Any]:
    """The analyst role's idle-in-transaction protection is in force."""
    rows = _rows(
        open_connection,
        "SELECT COALESCE((SELECT option FROM unnest(COALESCE(rolconfig, '{}')) AS option "
        "WHERE option LIKE 'idle_in_transaction_session_timeout=%'), '0') "
        "FROM pg_roles WHERE rolname = 'htap_analyst';",
    )
    raw = str(rows[0][0])
    value = raw.split("=", 1)[1] if "=" in raw else "0"
    from src.persistent_scenarios.backend.postgres.workloads.htap_common.pg_values import interval_seconds

    timeout_ms = int(interval_seconds(value) * 1000)
    minimum_ms = int(params.get("min_timeout_ms", 0))
    return {"passed": timeout_ms >= minimum_ms, "effective_timeout_ms": timeout_ms, "min_timeout_ms": minimum_ms}


def tenant_quota_allocation_effective(open_connection, params: Mapping[str, Any]) -> Mapping[str, Any]:
    """The per-tenant isolation decision honors the business priority contract.

    Every competing tenant must carry a finite, positive concurrency quota, and
    the platinum tenant's guaranteed share must be at least the standard
    tenant's. Structural checks only: any allocation satisfying the contract
    passes (equivalent repairs are accepted, exact numbers are not dictated).
    The tier labels are the seeded business contract (schema bootstrap).
    """
    platinum_tenant = str(params["platinum_tenant"])
    standard_tenant = str(params["standard_tenant"])
    rows = _rows(open_connection, "SELECT tenant, tier, max_concurrency FROM htap_tenant_quota;")
    quotas = {str(row[0]): (str(row[1]), row[2]) for row in rows}
    problems: list[dict[str, Any]] = []
    for tenant, expected_tier in ((platinum_tenant, "platinum"), (standard_tenant, "standard")):
        if tenant not in quotas:
            problems.append({"tenant": tenant, "reason": "missing_quota_row"})
            continue
        tier, raw = quotas[tenant]
        if tier != expected_tier:
            problems.append({"tenant": tenant, "reason": "tier_label_changed", "tier": tier})
        elif raw is None:
            problems.append({"tenant": tenant, "reason": "quota_not_allocated"})
        elif int(raw) <= 0:
            problems.append({"tenant": tenant, "reason": "quota_not_positive", "max_concurrency": int(raw)})
    if not problems:
        platinum_quota = int(quotas[platinum_tenant][1])
        standard_quota = int(quotas[standard_tenant][1])
        if platinum_quota < standard_quota:
            problems.append(
                {
                    "reason": "priority_contract_violated",
                    "platinum_quota": platinum_quota,
                    "standard_quota": standard_quota,
                }
            )
    return {
        "passed": not problems,
        "problems": problems,
        "quotas": {tenant: {"tier": tier, "max_concurrency": raw} for tenant, (tier, raw) in quotas.items()},
    }


VERIFIERS_BY_ID = {
    "htap3_order_payment_conservation": order_payment_conservation,
    "htap3_inventory_non_negative": inventory_non_negative,
    "htap3_export_checkpoints_complete": export_checkpoints_complete,
    "htap3_analysis_role_timeout_effective": analysis_role_timeout_effective,
    "htap3_tenant_quota_allocation_effective": tenant_quota_allocation_effective,
}
