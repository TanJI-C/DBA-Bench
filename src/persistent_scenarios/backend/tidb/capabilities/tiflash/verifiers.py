"""Instance-owned integrity and required-state verifiers for the HTAP isolation service.

Same contract as the warehouse verifiers: implementations
belong to the instance package, run against a trusted connection plus the sealed
`LedgerView`, return structured facts and raise on unverifiable states.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from src.persistent_scenarios.runtime.ledger import LedgerTerminal, LedgerView

from .schema import (
    CONFIG_TABLE,
    ORDERS_TABLE,
    RESULT_TABLE,
    ROUTING_HEALTHY_PREFERENCES,
    analysis_report_sql,
    tenant_analysis_sql,
)
from ..warehouse.reports import streaming_result_digest

# Report identities whose delivered truth recomputes over the tenant table.
TENANT_REPORT_IDS = frozenset({"tenant_region_heavy_analysis"})

VerifierCallable = Callable[[object, LedgerView, Mapping], dict]


def htap_trade_orders_conserved(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """Trade-side conservation: ledger-planned trades that committed exist in the table.

    The trade loop inserts with an app-generated MAX(order_id)+1 id; the ledger holds
    every logical trade with its outcome, so a committed count must equal the number of
    committed ledger records plus the seeded history rows.
    params: {"orders_table": "htap.orders", "history_rows": 800000}
    """
    records = ledger_view.logical_transactions()
    committed = [r for r in records if r.terminal is LedgerTerminal.COMPLETED]
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {params['orders_table']};")
        actual = int(cursor.fetchone()[0])
    connection.rollback()
    history_rows = int(params.get("history_rows", 0))
    expected = history_rows + len(committed)
    return {
        "orders_table": params["orders_table"],
        "ledger_committed_trades": len(committed),
        "history_rows": history_rows,
        "expected_rows": expected,
        "actual_rows": actual,
        "satisfied": actual == expected,
    }


def htap_analysis_result_truth(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """Delivered analysis digest must equal the recomputed truth of its declared snapshot.

    Each delivery row declares its snapshot marker (order count at submission); the
    verifier recomputes the snapshot-bound analysis truth and compares digests, so a
    result computed over a stale or truncated dataset cannot pass as current:
    results correspond to their declared snapshot. The tenant report
    identity recomputes over the tenant table.
    params: {"deliverables": [{"deliverable_id", "report_id"}], "require_on_time": bool}
    """
    jobs = {record.job_id: record for record in ledger_view.jobs()}
    results: dict[str, dict] = {}
    incorrect_job_ids: list[str] = []
    for deliverable in params["deliverables"]:
        job_id = deliverable["deliverable_id"]
        record = jobs.get(job_id)
        if record is None:
            results[job_id] = {"present": False, "digest_match": None, "on_time": None}
            incorrect_job_ids.append(job_id)
            continue
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT snapshot_marker, engine_used FROM {RESULT_TABLE} WHERE job_id = %s;", (job_id,)
            )
            result_row = cursor.fetchone()
        connection.rollback()
        if result_row is None:
            results[job_id] = {"present": False, "digest_match": None, "on_time": None}
            incorrect_job_ids.append(job_id)
            continue
        marker, engine_used = int(result_row[0]), result_row[1]
        truth_sql = tenant_analysis_sql(marker) if deliverable["report_id"] in TENANT_REPORT_IDS else analysis_report_sql(marker)
        with connection.cursor() as cursor:
            cursor.execute(truth_sql)
            expected, _rows = streaming_result_digest(cursor, ordered=True)
        connection.rollback()
        digest_match = record.terminal is LedgerTerminal.COMPLETED and record.result_digest == expected
        if not digest_match:
            incorrect_job_ids.append(job_id)
        results[job_id] = {
            "present": True,
            "report_id": deliverable["report_id"],
            "snapshot_marker": marker,
            "digest_match": digest_match,
            "on_time": record.delivered_on_time,
            "delivered_at_monotonic": record.delivered_at_monotonic,
            "engine_used": str(engine_used) if engine_used else None,
        }
    return {
        "deliverables": results,
        "incorrect_business_ids": [],
        "incorrect_job_ids": incorrect_job_ids,
    }


def htap_analytics_config_continuity(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """Final effective configuration: analytics must not have been left disabled, and
    the published routing template must keep the column-store replica reachable.

    Permanently shutting the analysis side cannot protect the trading side (the
    known wrong path); the final config rows prove continuation capacity. The routing
    acceptance set is the routing-healthy subset of the public ENGINE_PREFERENCES
    enum: `tikv_only` is the known-bad scheduler release and cannot be the final
    published template (the zero path), while both `auto` and
    `tiflash_preferred` are accepted - no single fixed value is required.
    params: {"config_table": "htap.analytics_config", "require_analysis_enabled": true,
             "require_routing_healthy": true}
    """
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT config_key, config_value FROM {CONFIG_TABLE};")
        config = {str(key): str(value) for key, value in cursor.fetchall()}
    connection.rollback()
    for required in ("engine_preference", "analysis_enabled", "dashboard_enabled"):
        if required not in config:
            raise RuntimeError(f"analytics config lost its {required!r} row at final sampling")
    analysis_enabled = config["analysis_enabled"].lower() == "true"
    dashboard_enabled = config["dashboard_enabled"].lower() == "true"
    routing_healthy = config["engine_preference"] in ROUTING_HEALTHY_PREFERENCES
    facts = {
        "config": config,
        "analysis_enabled": analysis_enabled,
        "dashboard_enabled": dashboard_enabled,
        "engine_preference": config["engine_preference"],
        "routing_healthy": routing_healthy,
        "routing_healthy_preferences": list(ROUTING_HEALTHY_PREFERENCES),
        "satisfied": (
            analysis_enabled if params.get("require_analysis_enabled", True) else True
        ) and (
            dashboard_enabled if params.get("require_dashboard_enabled", True) else True
        ) and (
            routing_healthy if params.get("require_routing_healthy", False) else True
        ),
    }
    return facts


def htap_tenant_replica_attached(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """The tenant tables onboarded during the run carry their TiFlash placement at
    seal time: a placement attachment deferred by the onboarding
    pipeline inside the node's maintenance window must have been re-established.

    params: {"schema": "htap", "table": "tenant_orders"}
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT AVAILABLE, PROGRESS, REPLICA_COUNT FROM information_schema.tiflash_replica "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;",
            (params["schema"], params["table"]),
        )
        row = cursor.fetchone()
    connection.rollback()
    if row is None:
        return {"present": False, "available": None, "replica_count": None, "satisfied": False}
    available, progress, replica_count = int(row[0]), float(row[1]), int(row[2])
    return {
        "present": True,
        "available": bool(available),
        "progress": progress,
        "replica_count": replica_count,
        # Replica progress stays mechanism observation only: the
        # placement must be re-attached (replica_count >= 1), the rebuild must not
        # have been dropped, and lag never gates correctness.
        "satisfied": replica_count >= 1,
    }


def htap_tiflash_replica_present(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """The TiFlash replica stays registered and available for the shared analysis side.

    params: {"schema": "htap", "table": "orders"}
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT AVAILABLE, PROGRESS, REPLICA_COUNT FROM information_schema.tiflash_replica "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;",
            (params["schema"], params["table"]),
        )
        row = cursor.fetchone()
    connection.rollback()
    if row is None:
        return {"present": False, "available": None, "satisfied": False}
    available, progress, replica_count = int(row[0]), float(row[1]), int(row[2])
    return {
        "present": True,
        "available": bool(available),
        "progress": progress,
        "replica_count": replica_count,
        # Replica progress is mechanism observation only: it never
        # gates correctness, but the replica must not have been dropped entirely.
        "satisfied": replica_count >= 1,
    }


VERIFIERS: dict[str, VerifierCallable] = {
    "htap_trade_orders_conserved": htap_trade_orders_conserved,
    "htap_analysis_result_truth": htap_analysis_result_truth,
    "htap_analytics_config_continuity": htap_analytics_config_continuity,
    "htap_tiflash_replica_present": htap_tiflash_replica_present,
    "htap_tenant_replica_attached": htap_tenant_replica_attached,
}


def verifier(verifier_id: str) -> VerifierCallable:
    instance = VERIFIERS.get(verifier_id)
    if instance is None:
        raise KeyError(f"unknown htap isolation verifier: verifier_id={verifier_id!r}, known={sorted(VERIFIERS)!r}")
    return instance
