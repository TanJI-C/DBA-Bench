"""Instance-owned integrity and required-state verifiers for the warehouse delivery.

Verifier implementations belong to the instance package because they encode the
business contract; integration assembles `VERIFIERS` into the
backend and the final sampling executes them against a trusted connection plus the
sealed `LedgerView`. Evaluation never executes SQL. Every verifier returns structured
facts and raises on an unverifiable state instead of guessing.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from src.persistent_scenarios.runtime.ledger import LedgerTerminal, LedgerView

from .reports import REPORT_CONTRACTS_BY_ID, report_sql, streaming_result_digest
from .schema import BATCH_REGISTRY, CONFIG_TABLE, FACT_TABLE, stage_spec

# A verifier receives (trusted_connection, ledger_view, params) and returns JSON facts.
VerifierCallable = Callable[[object, LedgerView, Mapping], dict]


def wh_report_result_truth(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """Delivered digest must equal the recomputed cutoff truth over the bound batches.

    params: {"deliverables": [{"deliverable_id", "report_id"}], "require_on_time": bool}
    The through_batch binding makes a stale result (an older cutoff) fail against the
    newer recomputation, so old batch results can never pass as a newer report.

    Batch truth can change mid-run when the upstream correction
    wave re-publishes a batch. Each deliverable therefore also records the batch's
    `republished_at` marker and whether the delivery happened after it, so a digest
    mismatch is honestly attributable to a delivery over superseded inputs.
    """
    jobs = {record.job_id: record for record in ledger_view.jobs()}
    results: dict[str, dict] = {}
    incorrect_job_ids: list[str] = []
    republished_at: dict[int, float | None] = {}
    with connection.cursor() as cursor:
        for deliverable in params["deliverables"]:
            job_id = deliverable["deliverable_id"]
            report_id = deliverable["report_id"]
            record = jobs.get(job_id)
            if record is None:
                results[job_id] = {"present": False, "digest_match": None, "on_time": None}
                incorrect_job_ids.append(job_id)
                continue
            batch_number = int(job_id.rsplit("batch", 1)[1])
            contract = REPORT_CONTRACTS_BY_ID[report_id]
            with_contract_sql = report_sql(report_id, batch_number)
            cursor.execute(with_contract_sql)
            expected, _rows = streaming_result_digest(cursor, ordered=contract.ordered)
            connection.rollback()
            digest_match = record.terminal is LedgerTerminal.COMPLETED and record.result_digest == expected
            if not digest_match:
                incorrect_job_ids.append(job_id)
            if batch_number not in republished_at:
                republished_at[batch_number] = _batch_republished_at(connection, batch_number)
            batch_republished_at = republished_at[batch_number]
            delivered_at = record.delivered_at_monotonic
            results[job_id] = {
                "present": True,
                "report_id": report_id,
                "batch_cutoff": batch_number,
                "ordered": contract.ordered,
                "digest_match": digest_match,
                "on_time": record.delivered_on_time,
                "delivered_at_monotonic": delivered_at,
                "batch_republished_at": batch_republished_at,
                "delivered_after_republish": (
                    None if delivered_at is None or batch_republished_at is None
                    else delivered_at >= batch_republished_at
                ),
            }
    return {
        "deliverables": results,
        "incorrect_business_ids": [],
        "incorrect_job_ids": incorrect_job_ids,
    }


def _batch_republished_at(connection, batch_number: int) -> float | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT republished_at FROM {BATCH_REGISTRY} WHERE batch_id = %s;",
            (batch_number,),
        )
        row = cursor.fetchone()
    connection.rollback()
    return None if row is None or row[0] is None else float(row[0])


def wh_fact_table_batch_invariant(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """Append-only batch fact check: every expected batch carries at least its planned rows.

    params: {"fact_table": "wh.orders", "batch_min_rows": {"0": 1000000, ...}}
    """
    facts = {}
    for batch_text, min_rows in params["batch_min_rows"].items():
        batch_id = int(batch_text)
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {params['fact_table']} WHERE batch_id = %s;", (batch_id,))
            actual = int(cursor.fetchone()[0])
        connection.rollback()
        facts[batch_text] = {"actual_rows": actual, "min_rows": int(min_rows), "satisfied": actual >= int(min_rows)}
    return {"batches": facts, "fact_table": params["fact_table"]}


def wh_staging_tables_present(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """Staged batch payloads survive until evaluation; dropping them breaks recomputability.

    params: {"batch_ids": ["1", "2"]}
    """
    facts = {}
    for batch_id_text in params["batch_ids"]:
        spec = stage_spec(int(batch_id_text))
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='wh' AND table_name=%s;",
                (spec.stage_table.split(".")[1],),
            )
            present = int(cursor.fetchone()[0]) > 0
        connection.rollback()
        facts[batch_id_text] = {"stage_table": spec.stage_table, "present": present}
    return {"staging": facts}


def wh_analytics_continuity(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """Final service continuity: the queue switches must not have been left disabled.

    Permanently shutting analytics or ingest is a contract violation; the final
    effective configuration proves whether the services can continue (pausing
    all ingest instead of governing it is a wrong action).
    params: {"require_analytics_enabled": true, "require_ingest_enabled": true}
    """
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT analytics_enabled, ingest_enabled FROM {CONFIG_TABLE} WHERE id = 1;"
        )
        row = cursor.fetchone()
    connection.rollback()
    if row is None:
        raise RuntimeError(f"{CONFIG_TABLE} lost its single configuration row at final sampling")
    analytics_enabled, ingest_enabled = bool(row[0]), bool(row[1])
    facts = {
        "analytics_enabled": analytics_enabled,
        "ingest_enabled": ingest_enabled,
        "satisfied": (
            analytics_enabled if params.get("require_analytics_enabled", True) else True
        ) and (
            ingest_enabled if params.get("require_ingest_enabled", True) else True
        ),
    }
    return facts


def wh_statistics_current(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """Statistics health: analyzed row count must be within the allowed ratio of actual rows.

    The final evidence proves the agent kept statistics maintenance in place; ANALYZE
    as a performed action is never required by the evaluator, the
    effective statistics state is what matters.
    params: {"fact_table": "wh.orders", "max_modify_count_ratio": 0.5}
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT sm.modify_count, sm.count FROM mysql.stats_meta sm "
            "JOIN information_schema.tables ist ON ist.tidb_table_id = sm.table_id "
            "WHERE ist.table_schema = %s AND ist.table_name = %s;",
            tuple(params["fact_table"].split(".")),
        )
        row = cursor.fetchone()
    connection.rollback()
    if row is None:
        raise RuntimeError(
            f"no statistics row for the fact table: fact_table={params['fact_table']!r}"
        )
    modify_count, analyzed_count = int(row[0]), int(row[1])
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {params['fact_table']};")
        actual = int(cursor.fetchone()[0])
    connection.rollback()
    # stats_meta semantics (measured on v8.1.0): `count` is the row
    # count at the last full analyze and `modify_count` accumulates writes since, but
    # the delta flush is lazy (observed lag > 60s, flushed with the next write). Final
    # sampling runs well after the last input, so the ratio is meaningful there; a
    # verifier read inside the active publish window can still see modify_count = 0.
    total = analyzed_count + modify_count
    stale_fraction = modify_count / total if total > 0 else 1.0
    facts = {
        "fact_table": params["fact_table"],
        "analyzed_count": analyzed_count,
        "modify_count": modify_count,
        "actual_rows": actual,
        "max_modify_count_ratio": float(params["max_modify_count_ratio"]),
        "stale_fraction": round(stale_fraction, 4),
        "satisfied": stale_fraction <= float(params["max_modify_count_ratio"]),
    }
    return facts


VERIFIERS: dict[str, VerifierCallable] = {
    "wh_report_result_truth": wh_report_result_truth,
    "wh_fact_table_batch_invariant": wh_fact_table_batch_invariant,
    "wh_staging_tables_present": wh_staging_tables_present,
    "wh_analytics_continuity": wh_analytics_continuity,
    "wh_statistics_current": wh_statistics_current,
}


def verifier(verifier_id: str) -> VerifierCallable:
    instance = VERIFIERS.get(verifier_id)
    if instance is None:
        raise KeyError(f"unknown warehouse delivery verifier: verifier_id={verifier_id!r}, known={sorted(VERIFIERS)!r}")
    return instance
