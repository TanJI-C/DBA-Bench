"""Instance-owned integrity and required-state verifier implementations.

Verifier implementations belong to the instance package because they encode the
business contract; integration assembles `VERIFIERS` into the backend and the final
sampling executes them against a trusted connection plus the sealed `LedgerView`.
Evaluation never executes SQL. Every verifier returns structured facts and raises on
an unverifiable state instead of guessing.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping

from src.persistent_scenarios.runtime.ledger import LedgerTerminal, LedgerView

from .reports import (
    deliverable_cutoff,
    reference_result_digest,
    report_contract,
)
from .store import QueueTables, ingest_stage_spec

# A verifier receives (trusted_connection, ledger_view, params) and returns JSON facts.
VerifierCallable = Callable[[object, LedgerView, Mapping], dict]


def wh_report_result_truth(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """Declared equivalence contract: delivered digest must equal recomputed cutoff truth.

    params: {"deliverables": [{"deliverable_id", "report_id"}], "require_on_time": bool}
    Details carry ``incorrect_job_ids`` (and an empty ``incorrect_business_ids``; this
    instance has no logical transactions) for the evaluator's correctness verdict.
    """
    jobs = {record.job_id: record for record in ledger_view.jobs()}
    results: dict[str, dict] = {}
    incorrect_job_ids: list[str] = []
    for deliverable in params["deliverables"]:
        job_id = deliverable["deliverable_id"]
        report_id = deliverable["report_id"]
        record = jobs.get(job_id)
        if record is None:
            results[job_id] = {"present": False, "digest_match": None, "on_time": None}
            incorrect_job_ids.append(job_id)
            continue
        cutoff = deliverable_cutoff(job_id)
        expected = reference_result_digest(connection, report_id, cutoff)
        contract = report_contract(report_id)
        digest_match = record.result_digest == expected and record.terminal is LedgerTerminal.COMPLETED
        if not digest_match:
            incorrect_job_ids.append(job_id)
        results[job_id] = {
            "present": True,
            "report_id": report_id,
            "cutoff": cutoff,
            "ordered": contract.ordered,
            "freshness_declared": contract.freshness_declared,
            "digest_match": digest_match,
            "on_time": record.delivered_on_time,
            "delivered_at_monotonic": record.delivered_at_monotonic,
        }
    return {
        "passed": not incorrect_job_ids,
        "deliverables": results,
        "incorrect_business_ids": [],
        "incorrect_job_ids": incorrect_job_ids,
    }


def wh_fact_table_batch_invariant(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """Append-only batch fact check: every expected batch carries at least its planned rows.

    params: {"fact_table": "wh.batch_sales", "batch_min_rows": {"0": 60496032, ...}}
    """
    facts = {}
    for batch_text, min_rows in params["batch_min_rows"].items():
        batch_id = int(batch_text)
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT count(*) FROM {params['fact_table']} WHERE batch_id = %s;", (batch_id,)
            )
            actual = int(cursor.fetchone()[0])
        facts[batch_text] = {"actual_rows": actual, "min_rows": int(min_rows), "satisfied": actual >= int(min_rows)}
    return {
        "passed": all(fact["satisfied"] for fact in facts.values()),
        "batches": facts,
        "fact_table": params["fact_table"],
    }


def wh_backup_readable(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """The backup artifact exists and is a genuine readable batch-prefix snapshot.

    params: {"deliverable_id": "routine_backup_read", "passes": 4}
    The frozen timeline puts backup arrival BEFORE the last batch arrival, so the
    snapshot cannot be recomputed against the final table state. It is verified
    structurally instead: the recorded passes must be identical (a stable full
    read), and (fact_rows, fact_digest) must equal the cumulative rows/digest
    over the first K ingested batches of the current table for some K — i.e. the
    artifact matches a real contiguous prefix of the append-only fact table.
    Recorded physical size is kept as evidence but excluded from the match:
    relation size legitimately drifts after later ingests and maintenance.
    """
    jobs = {record.job_id: record for record in ledger_view.jobs()}
    record = jobs.get(params["deliverable_id"])
    if record is None or record.terminal is not LedgerTerminal.COMPLETED or record.result_digest is None:
        return {"passed": False, "present": False, "digest_match": None}
    delivered = json.loads(record.result_digest)
    passes = int(params.get("passes", delivered["passes"]))
    mismatch = {"passed": False, "present": True, "digest_match": False, "passes": passes}
    if int(delivered["passes"]) != passes:
        return mismatch
    pass_facts = json.loads(delivered["passes_digest"])
    if len(pass_facts) != passes:
        return mismatch

    def logical(facts):
        return [(key, value) for key, value in facts if key in ("fact_rows", "fact_digest")]

    # Passes must agree on the logical snapshot (same rows, same content digest);
    # recorded physical size is evidence only: relation size legitimately drifts
    # under concurrent ingest COPY, maintenance, and vacuum.
    snapshot = dict(pass_facts[0])
    if any(logical(facts) != logical(pass_facts[0]) for facts in pass_facts):
        return mismatch
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT batch_id, count(*), COALESCE(sum(hashtext(line_id::text)), 0) "
            "FROM wh.batch_sales GROUP BY batch_id ORDER BY batch_id;"
        )
        batch_facts = cursor.fetchall()
    running_rows = running_digest = 0
    prefix_facts = {(0, 0)}
    for _batch_id, batch_rows, batch_digest in batch_facts:
        running_rows += int(batch_rows)
        running_digest += int(batch_digest)
        prefix_facts.add((running_rows, running_digest))
    return {
        "passed": bool((int(snapshot["fact_rows"]), int(snapshot["fact_digest"])) in prefix_facts),
        "present": True,
        "digest_match": (int(snapshot["fact_rows"]), int(snapshot["fact_digest"])) in prefix_facts,
        "passes": passes,
    }


def wh_staging_tables_present(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """Staged batch payloads survive until evaluation; dropping them breaks recomputability."""
    facts = {}
    for batch_id_text in params["batch_ids"]:
        batch_id = int(batch_id_text)
        spec = ingest_stage_spec(batch_id)
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass(%s);", (spec.stage_table,))
            present = cursor.fetchone()[0] is not None
        facts[batch_id_text] = {"stage_table": spec.stage_table, "present": bool(present)}
    return {
        "passed": all(fact["present"] for fact in facts.values()),
        "staging": facts,
    }


def wh_analytics_continuity(connection, ledger_view: LedgerView, params: Mapping) -> dict:
    """Final service continuity: the queue switches must not have been left disabled.

    Permanently shutting analytics or backup is a contract violation; the final
    effective configuration proves whether the services can continue.
    params: {"require_analytics_enabled": true, "require_backup_enabled": true}
    """
    row = QueueTables._fetchone(
        connection,
        "SELECT analytics_enabled, backup_enabled FROM wh.queue_config WHERE id = 1;",
    )
    if row is None:
        raise RuntimeError("wh.queue_config lost its single configuration row at final sampling")
    analytics_enabled, backup_enabled = bool(row[0]), bool(row[1])
    satisfied = (
        analytics_enabled if params.get("require_analytics_enabled", True) else True
    ) and (
        backup_enabled if params.get("require_backup_enabled", True) else True
    )
    facts = {
        "passed": satisfied,
        "analytics_enabled": analytics_enabled,
        "backup_enabled": backup_enabled,
        "satisfied": satisfied,
    }
    return facts


VERIFIERS: dict[str, VerifierCallable] = {
    "wh_report_result_truth": wh_report_result_truth,
    "wh_fact_table_batch_invariant": wh_fact_table_batch_invariant,
    "wh_backup_readable": wh_backup_readable,
    "wh_staging_tables_present": wh_staging_tables_present,
    "wh_analytics_continuity": wh_analytics_continuity,
}


def verifier(verifier_id: str) -> VerifierCallable:
    instance = VERIFIERS.get(verifier_id)
    if instance is None:
        raise KeyError(f"unknown warehouse reporting verifier: verifier_id={verifier_id!r}, known={sorted(VERIFIERS)!r}")
    return instance
