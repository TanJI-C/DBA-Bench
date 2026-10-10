"""End-to-end service objective scoring over the trusted core business ledgers.

OLTP is scored as the fraction of independently planned logical transactions
completed correctly within their business deadline; retries merge into one
business ID and the deadline runs from first submission, queueing and retrying
included. OLAP is scored as a deliverable checklist or a frozen task-class
budget, with ``deliverable_id == job_id`` and deadlines frozen at submission.
HTAP requires both sides to satisfy their own contracts simultaneously; replica
freshness aligns the trusted watermark samples with each delivery moment. There
are no request buckets, no per-bucket p95/QPS gates and no weighted totals.
"""

from __future__ import annotations

from typing import Mapping

from ..model.enums import HtapMode, LoadClass, OlapMode
from ..model.spec import OlapObjective, OltpObjective
from ..runtime.ledger import JobRecord, LedgerTerminal, LedgerView, LogicalTransactionRecord
from ..runtime.lifecycle import IntegrityStatus, ScoringWindow

from .contracts import LedgerIncompleteError


_RESULT_TRUTH_KIND = "result_truth"


def _ledger_views(ledgers: Mapping[str, object]) -> tuple[LedgerView, ...]:
    return tuple(LedgerView(ledger) for ledger in ledgers.values())


def collected_transactions(ledgers: Mapping[str, object]) -> tuple[LogicalTransactionRecord, ...]:
    return _collected_records(ledgers, LedgerView.logical_transactions)


def collected_jobs(ledgers: Mapping[str, object]) -> tuple[JobRecord, ...]:
    return _collected_records(ledgers, LedgerView.jobs)


def collected_freshness_samples(ledgers: Mapping[str, object]) -> tuple:
    return _collected_records(ledgers, LedgerView.freshness_samples)


def incorrect_verdict_ids(integrity_facts) -> tuple[frozenset[str], frozenset[str]]:
    """(business IDs, job IDs) judged wrong by failed result-truth verifiers."""
    return (
        _incorrect_verdict_ids(integrity_facts, "incorrect_business_ids"),
        _incorrect_verdict_ids(integrity_facts, "incorrect_job_ids"),
    )


def _collected_records(ledgers: Mapping[str, object], read) -> tuple:
    records = []
    for view in _ledger_views(ledgers):
        records.extend(read(view))
    return tuple(records)


def _duplicate_free(records, id_field: str) -> None:
    seen = set()
    for record in records:
        identifier = getattr(record, id_field)
        if identifier in seen:
            raise ValueError(
                f"Business ledgers contain two records for one {id_field}: {identifier!r}"
            )
        seen.add(identifier)


def _incorrect_verdict_ids(integrity_facts, id_key: str) -> frozenset[str]:
    """Business IDs judged wrong by a failed result-truth verifier.

    The verifier compares each ledger row's ``result_digest`` against the bound
    business truth; a FAILED verdict lists the offending IDs under
    ``incorrect_business_ids`` / ``incorrect_job_ids`` in ``details``.
    """
    identifiers: set[str] = set()
    for fact in integrity_facts:
        if fact.kind == _RESULT_TRUTH_KIND and fact.status is IntegrityStatus.FAILED:
            identifiers.update(fact.details.get(id_key, ()))
    return frozenset(identifiers)


def _longest_success_gap(completion_times: list[float], window: ScoringWindow) -> float:
    boundaries = [window.scoring_start_monotonic, *sorted(completion_times), window.scoring_end_monotonic]
    return max(boundaries[i + 1] - boundaries[i] for i in range(len(boundaries) - 1))


def _evaluate_oltp(
    objective: OltpObjective,
    window: ScoringWindow,
    transactions: tuple[LogicalTransactionRecord, ...],
    incorrect_business_ids: frozenset[str],
) -> dict[str, object]:
    counts = {
        "completed_within_deadline": 0,
        "deadline_missed": 0,
        "rejected": 0,
        "timed_out": 0,
        "cancelled": 0,
        "unfinished_at_window_end": 0,
        "lost": 0,
        "incorrect_result_count": 0,
    }
    attempt_count = 0
    completion_times: list[float] = []
    service_transactions = [record for record in transactions if record.service_id == objective.service_id]
    for record in service_transactions:
        attempt_count += len(record.attempts)
        if record.terminal is LedgerTerminal.COMPLETED:
            if record.business_id in incorrect_business_ids:
                counts["incorrect_result_count"] += 1
            elif record.completed_at_monotonic <= record.deadline_at_monotonic:
                counts["completed_within_deadline"] += 1
                completion_times.append(float(record.completed_at_monotonic))
            else:
                counts["deadline_missed"] += 1
        elif record.terminal is LedgerTerminal.INCOMPLETE_TIMEOUT:
            counts["timed_out"] += 1
        elif record.terminal is LedgerTerminal.INCOMPLETE_ERROR:
            counts["rejected"] += 1
        elif record.terminal is LedgerTerminal.INCOMPLETE_CANCELLED:
            counts["cancelled"] += 1
        elif not record.attempts:
            counts["lost"] += 1
        else:
            counts["unfinished_at_window_end"] += 1
    denominator = len(service_transactions)
    if denominator == 0:
        raise ValueError(
            f"OLTP objective has an empty denominator: objective_id={objective.objective_id!r}, "
            f"service_id={objective.service_id!r}; the external plan must declare business inputs"
        )
    success_fraction = counts["completed_within_deadline"] / denominator
    longest_gap = _longest_success_gap(completion_times, window)
    outage_pass = None if objective.outage_contract_seconds is None else longest_gap <= objective.outage_contract_seconds
    return {
        "objective_id": objective.objective_id,
        "load_class": LoadClass.OLTP.value,
        "service_id": objective.service_id,
        "denominator": denominator,
        **counts,
        "attempt_count": attempt_count,
        "success_fraction": success_fraction,
        "deadline_seconds": objective.deadline_seconds,
        "min_success_fraction": objective.min_success_fraction,
        "longest_completion_gap_seconds": longest_gap,
        "continuous_outage": {
            "measured_seconds": longest_gap,
            "contract_seconds": objective.outage_contract_seconds,
            "source": objective.outage_source,
            "pass": outage_pass,
        },
        "pass": success_fraction >= objective.min_success_fraction and outage_pass is not False,
    }


def _batch_watermark_value(sample) -> int | None:
    """Batch watermarks record "batch-N" with no time-lag; the ingest cursor lives in detail."""
    value = sample.detail.get("watermark_batch") if isinstance(sample.detail, dict) else None
    if isinstance(value, bool) or not isinstance(value, int):
        watermark = sample.primary_watermark
        if isinstance(watermark, str) and watermark.startswith("batch-"):
            try:
                return int(watermark[len("batch-"):])
            except ValueError:
                return None
        return None
    return value


def _binding_batch(input_batch_binding: str | None) -> tuple[str, int] | None:
    if not input_batch_binding:
        return None
    kind, _, suffix = input_batch_binding.rpartition("_")
    if kind not in ("through_batch", "exact_batch"):
        return None
    try:
        return kind, int(suffix)
    except ValueError:
        return None


def _binding_matches_version(input_batch_binding: str, batch_version: str | None) -> bool:
    """The binding's batch number identifies the consumed input; runtime jobs
    carry it as the plain batch id string ("1"), not the binding spelling."""
    binding = _binding_batch(input_batch_binding)
    if binding is None:
        return batch_version == input_batch_binding
    if batch_version is None:
        return False
    try:
        return int(batch_version) == binding[1]
    except ValueError:
        return batch_version == input_batch_binding


def _delivery_freshness(job: JobRecord, deliverable, freshness_samples) -> dict[str, object] | None:
    if not deliverable.requires_freshness:
        return None
    if job.terminal is not LedgerTerminal.COMPLETED:
        return None
    candidates = [sample for sample in freshness_samples if sample.sampled_at_monotonic <= job.delivered_at_monotonic]
    if not candidates:
        raise LedgerIncompleteError(
            "A freshness-bound delivery has no trusted watermark sample at or before its delivery moment; "
            f"the trusted ledger is incomplete: job_id={job.job_id!r}, deliverable_id={deliverable.deliverable_id!r}, "
            f"delivered_at={job.delivered_at_monotonic!r}"
        )
    sample = max(candidates, key=lambda item: item.sampled_at_monotonic)
    if sample.lag_seconds is not None:
        # Time-lag watermarks (replica freshness) compare against the declared ceiling.
        return {
            "job_id": job.job_id,
            "deliverable_id": deliverable.deliverable_id,
            "sample_id": sample.sample_id,
            "primary_commit_watermark": sample.primary_watermark,
            "replica_visible_watermark": sample.replica_watermark,
            "lag_seconds": sample.lag_seconds,
            "max_freshness_lag_seconds": deliverable.max_freshness_lag_seconds,
            "pass": sample.lag_seconds <= deliverable.max_freshness_lag_seconds,
        }
    # Batch watermarks carry no time-lag by design: freshness is the delivery-moment
    # watermark alignment — the watermark must still cover the
    # batch the deliverable consumed (exact: equal, through: at least).
    watermark_batch = _batch_watermark_value(sample)
    binding = _binding_batch(deliverable.input_batch_binding)
    if watermark_batch is None or binding is None:
        raise LedgerIncompleteError(
            "The latest trusted watermark sample has no comparable batch mapping: "
            f"job_id={job.job_id!r}, sample_id={sample.sample_id!r}, "
            f"watermark={sample.primary_watermark!r}, binding={deliverable.input_batch_binding!r}"
        )
    kind, bound_batch = binding
    watermark_satisfied = watermark_batch == bound_batch if kind == "exact_batch" else watermark_batch >= bound_batch
    return {
        "job_id": job.job_id,
        "deliverable_id": deliverable.deliverable_id,
        "sample_id": sample.sample_id,
        "primary_commit_watermark": sample.primary_watermark,
        "replica_visible_watermark": sample.replica_watermark,
        "lag_seconds": None,
        "max_freshness_lag_seconds": deliverable.max_freshness_lag_seconds,
        "watermark_batch": watermark_batch,
        "input_batch_binding": deliverable.input_batch_binding,
        "watermark_satisfied": watermark_satisfied,
        "pass": watermark_satisfied,
    }


def _evaluate_olap_checklist(objective: OlapObjective, jobs, freshness_samples, incorrect_job_ids) -> dict[str, object]:
    deliverable_results = []
    freshness_results = []
    for deliverable in objective.deliverables:
        # Deliverable identity: deliverable_id == job_id; cancel/retry merge into the
        # same job record, so each deliverable owns exactly zero or one job.
        job = next((record for record in jobs if record.job_id == deliverable.deliverable_id), None)
        # A deliverable legitimately owns zero jobs (never submitted); its
        # verdict is the missing-delivery result below, and freshness has no
        # delivery moment to align against.
        freshness = _delivery_freshness(job, deliverable, freshness_samples) if job is not None else None
        if freshness is not None:
            freshness_results.append(freshness)
        if job is None:
            deliverable_results.append(
                {
                    "deliverable_id": deliverable.deliverable_id,
                    "deadline_seconds": deliverable.deadline_seconds,
                    "terminal_outcome": "missing",
                    "delivered_at_monotonic": None,
                    "input_batch_version": None,
                    "pass": False,
                }
            )
            continue
        delivered = (
            job.terminal is LedgerTerminal.COMPLETED
            and job.delivered_on_time
            and job.job_id not in incorrect_job_ids
            and (deliverable.input_batch_binding is None or _binding_matches_version(deliverable.input_batch_binding, job.batch_version))
            and (freshness is None or freshness["pass"] is True)
        )
        deliverable_results.append(
            {
                "deliverable_id": deliverable.deliverable_id,
                "deadline_seconds": deliverable.deadline_seconds,
                "terminal_outcome": job.terminal.value,
                "delivered_at_monotonic": job.delivered_at_monotonic,
                "input_batch_version": job.batch_version,
                "pass": delivered,
            }
        )
    delivered_on_time = sum(result["pass"] is True for result in deliverable_results)
    return {
        "objective_id": objective.objective_id,
        "load_class": LoadClass.OLAP.value,
        "mode": OlapMode.DELIVERABLE_CHECKLIST.value,
        "service_id": objective.service_id,
        "deliverables": deliverable_results,
        "total": len(deliverable_results),
        "delivered_on_time": delivered_on_time,
        "freshness_results": freshness_results,
        "pass": bool(deliverable_results) and delivered_on_time == len(deliverable_results),
    }


def _evaluate_olap_task_class(objective: OlapObjective, jobs, incorrect_job_ids) -> dict[str, object]:
    service_jobs = [job for job in jobs if job.service_id == objective.service_id]
    if not service_jobs:
        raise ValueError(
            f"Task-class OLAP objective has an empty job ledger: objective_id={objective.objective_id!r}, "
            f"service_id={objective.service_id!r}"
        )
    on_time_correct = sum(
        job.delivered_on_time and job.job_id not in incorrect_job_ids for job in service_jobs
    )
    fraction = on_time_correct / len(service_jobs)
    return {
        "objective_id": objective.objective_id,
        "load_class": LoadClass.OLAP.value,
        "mode": OlapMode.TASK_CLASS_BUDGET.value,
        "service_id": objective.service_id,
        "total_jobs": len(service_jobs),
        "on_time_correct": on_time_correct,
        "on_time_correct_fraction": fraction,
        "min_on_time_correct_fraction": objective.min_on_time_correct_fraction,
        "calibration_evidence_id": objective.calibration_evidence_id,
        "cancelled": sum(job.terminal is LedgerTerminal.INCOMPLETE_CANCELLED for job in service_jobs),
        "unfinished_at_window_end": sum(
            job.terminal is LedgerTerminal.INCOMPLETE_OUTSTANDING for job in service_jobs
        ),
        "deadline_seconds": objective.deadline_seconds,
        "pass": fraction >= objective.min_on_time_correct_fraction,
    }


def _evaluate_olap(objective: OlapObjective, jobs, freshness_samples, incorrect_job_ids) -> dict[str, object]:
    if objective.olap_mode is OlapMode.DELIVERABLE_CHECKLIST:
        return _evaluate_olap_checklist(objective, jobs, freshness_samples, incorrect_job_ids)
    return _evaluate_olap_task_class(objective, jobs, incorrect_job_ids)


def _evaluate_htap(objective, results_by_id: Mapping[str, dict[str, object]]) -> dict[str, object]:
    transaction = results_by_id.get(objective.transaction_objective_id)
    analysis = results_by_id.get(objective.analysis_objective_id)
    if not (isinstance(transaction, dict) and transaction["load_class"] == LoadClass.OLTP.value):
        raise ValueError(
            f"HTAP objective must reference a declared OLTP objective: objective_id={objective.objective_id!r}, "
            f"transaction_objective_id={objective.transaction_objective_id!r}, resolved={transaction is not None}"
        )
    if not (
        isinstance(analysis, dict) and analysis["load_class"] == LoadClass.OLAP.value
    ):
        raise ValueError(
            f"HTAP objective must reference a declared OLAP objective: objective_id={objective.objective_id!r}, "
            f"analysis_objective_id={objective.analysis_objective_id!r}, resolved={analysis is not None}"
        )
    if objective.htap_mode not in (HtapMode.SHARED, HtapMode.REPLICA):
        raise ValueError(
            f"Unknown HTAP mode: objective_id={objective.objective_id!r}, htap_mode={objective.htap_mode!r}"
        )
    return {
        "objective_id": objective.objective_id,
        "load_class": LoadClass.HTAP.value,
        "mode": objective.htap_mode.value,
        "service_id": objective.service_id,
        "transaction_objective_id": objective.transaction_objective_id,
        "transaction_pass": transaction["pass"],
        "analysis_objective_id": objective.analysis_objective_id,
        "analysis_pass": analysis["pass"],
        "freshness_results": list(analysis.get("freshness_results", ())),
        "pass": transaction["pass"] is True and analysis["pass"] is True,
    }


def evaluate_service_objectives(
    services,
    *,
    window: ScoringWindow,
    ledgers: Mapping[str, object],
    integrity_facts,
) -> tuple[bool, list[dict[str, object]]]:
    """Score every declared service objective; returns (all_pass, per-objective results)."""
    transactions = collected_transactions(ledgers)
    jobs = collected_jobs(ledgers)
    freshness_samples = collected_freshness_samples(ledgers)
    _duplicate_free(transactions, "business_id")
    _duplicate_free(jobs, "job_id")
    incorrect_business_ids, incorrect_job_ids = incorrect_verdict_ids(integrity_facts)

    results: list[dict[str, object]] = []
    results_by_id: dict[str, dict[str, object]] = {}
    deferred_htap = []
    for objective in services:
        if objective.load_class is LoadClass.OLTP:
            result = _evaluate_oltp(objective, window, transactions, incorrect_business_ids)
        elif objective.load_class is LoadClass.OLAP:
            result = _evaluate_olap(objective, jobs, freshness_samples, incorrect_job_ids)
        elif objective.load_class is LoadClass.HTAP:
            deferred_htap.append(objective)
            continue
        else:
            raise ValueError(
                f"Unknown service objective load_class: objective_id={objective.objective_id!r}, "
                f"load_class={objective.load_class!r}"
            )
        results.append(result)
        results_by_id[result["objective_id"]] = result
    for objective in deferred_htap:
        result = _evaluate_htap(objective, results_by_id)
        results.append(result)
        results_by_id[result["objective_id"]] = result
    if not results:
        raise ValueError("A Persistent Scenario must declare at least one service objective to evaluate")
    return all(result["pass"] is True for result in results), results
