"""PostgreSQL error classification into ledger attempt outcomes.

Only real database error states are mapped. Unknown exceptions propagate so
that the run fails where the failure happened instead of being silently
recorded as a business result.
"""

from __future__ import annotations

import psycopg2

from src.persistent_scenarios.runtime.ledger import (
    AttemptOutcome,
    JobAttemptOutcome,
    LedgerTerminal,
)

_TIMEOUT_PGCODES = frozenset({"57014", "55P03", "57P05"})
_CONNECTION_PGCODES = frozenset({"08000", "08001", "08003", "08006", "08004", "53300"})
_DEADLOCK_PGCODE = "40P01"


def classify_transaction_outcome(exc: psycopg2.Error) -> AttemptOutcome:
    pgcode = getattr(exc, "pgcode", None)
    if pgcode in _TIMEOUT_PGCODES:
        return AttemptOutcome.TIMED_OUT
    if pgcode in _CONNECTION_PGCODES:
        return AttemptOutcome.CONNECTION_REFUSED
    if pgcode == _DEADLOCK_PGCODE:
        return AttemptOutcome.ABORTED
    return AttemptOutcome.ABORTED


def classify_job_outcome(exc: psycopg2.Error) -> JobAttemptOutcome:
    outcome = classify_transaction_outcome(exc)
    if outcome is AttemptOutcome.COMMITTED:
        return JobAttemptOutcome.SUCCEEDED
    if outcome is AttemptOutcome.TIMED_OUT:
        return JobAttemptOutcome.FAILED
    if outcome is AttemptOutcome.CONNECTION_REFUSED:
        return JobAttemptOutcome.FAILED
    return JobAttemptOutcome.FAILED


def job_failure_terminal(exc: psycopg2.Error) -> LedgerTerminal:
    """The trusted terminal a final job failure closes its obligation with."""
    if getattr(exc, "pgcode", None) in _TIMEOUT_PGCODES:
        return LedgerTerminal.INCOMPLETE_TIMEOUT
    return LedgerTerminal.INCOMPLETE_ERROR


class WorkloadConnectionFailure(RuntimeError):
    """A workload worker could not open its database connection."""
