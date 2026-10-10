"""Delivery acceptance facts derived from the trusted ledger.

These helpers classify `JobRecord`s from the core `LedgerView` for the OLAP objective
shapes. Correctness is never decided here: the digest-match facts come from the
instance integrity verifier (`verifiers.py`), and the evaluator composes both.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.persistent_scenarios.runtime.ledger import JobRecord, LedgerTerminal

DELIVERY_ON_TIME_CORRECT = "on_time_correct"
DELIVERY_ON_TIME = "on_time"
DELIVERY_LATE = "late"
DELIVERY_MISSING = "missing"

BACKUP_COMPLETED_ON_TIME = "completed_on_time"
BACKUP_LATE = "late"
BACKUP_MISSING = "missing"


@dataclass(frozen=True, slots=True)
class DeliveryStatus:
    job_id: str
    job_kind: str
    batch_version: str | None
    status: str
    delivered_at_monotonic: float | None
    deadline_at_monotonic: float


def delivery_status(record: JobRecord) -> DeliveryStatus:
    """Ledger-only verdict: on-time, late or missing. Correctness is separate."""
    if record.terminal is LedgerTerminal.COMPLETED and record.delivered_at_monotonic is not None:
        status = DELIVERY_ON_TIME if record.delivered_on_time else DELIVERY_LATE
        delivered = record.delivered_at_monotonic
    else:
        status = DELIVERY_MISSING
        delivered = None
    return DeliveryStatus(
        job_id=record.job_id,
        job_kind=record.job_kind,
        batch_version=record.batch_version,
        status=status,
        delivered_at_monotonic=delivered,
        deadline_at_monotonic=record.deadline_at_monotonic,
    )


def heartbeat_budget_facts(jobs: tuple[JobRecord, ...], budget_seconds: float) -> dict[str, object]:
    heartbeats = [record for record in jobs if record.job_kind == "heartbeat"]
    if not heartbeats:
        raise ValueError("no heartbeat jobs in the ledger; the heartbeat budget class cannot be evaluated")
    within = sum(1 for record in heartbeats if record.delivered_on_time)
    return {
        "budget_seconds": budget_seconds,
        "total": len(heartbeats),
        "on_time": within,
        "late_or_missing": len(heartbeats) - within,
        "on_time_fraction": within / len(heartbeats),
    }
