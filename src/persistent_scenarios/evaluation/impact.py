"""Per-service impact evidence derived from the trusted core ledgers.

This is review evidence only: it never gates a pass. Losses are reported per
service category, so overlapping event windows are never summed into a
fabricated system-wide total loss figure.
"""

from __future__ import annotations

from ..runtime.ledger import LedgerTerminal


def _latest_lag(delivered_at_monotonic: float, freshness_samples) -> float | None:
    candidates = [sample for sample in freshness_samples if sample.sampled_at_monotonic <= delivered_at_monotonic]
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.sampled_at_monotonic).lag_seconds


def impact_by_service(transactions, jobs, freshness_samples, incorrect_business_ids, incorrect_job_ids) -> list[dict[str, object]]:
    service_ids: list[str] = []
    for record in (*transactions, *jobs):
        if record.service_id not in service_ids:
            service_ids.append(record.service_id)
    impact: dict[str, dict[str, object]] = {service_id: {
        "service_id": service_id,
        "failed_transactions": 0,
        "late_completions": 0,
        "lost_transactions": 0,
        "incorrect_results": 0,
        "missed_deliveries": 0,
        "freshness_deliveries_with_lag": 0,
    } for service_id in service_ids}
    for record in transactions:
        item = impact[record.service_id]
        if record.terminal in (LedgerTerminal.INCOMPLETE_TIMEOUT, LedgerTerminal.INCOMPLETE_ERROR,
                               LedgerTerminal.INCOMPLETE_CANCELLED, LedgerTerminal.INCOMPLETE_OUTSTANDING):
            item["failed_transactions"] += 1
            if record.terminal is LedgerTerminal.INCOMPLETE_OUTSTANDING and not record.attempts:
                item["lost_transactions"] += 1
        elif record.business_id in incorrect_business_ids:
            item["incorrect_results"] += 1
        elif record.completed_at_monotonic > record.deadline_at_monotonic:
            item["late_completions"] += 1
    for record in jobs:
        item = impact[record.service_id]
        delivered_on_time = record.delivered_on_time and record.job_id not in incorrect_job_ids
        if not delivered_on_time:
            item["missed_deliveries"] += 1
        elif record.result_digest is not None:
            lag = _latest_lag(float(record.delivered_at_monotonic), freshness_samples)
            if lag is not None and lag > 0:
                item["freshness_deliveries_with_lag"] += 1
    return [impact[service_id] for service_id in service_ids]
