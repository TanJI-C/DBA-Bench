"""TiDB error classification into trusted-ledger attempt outcomes.

Only real database error states are mapped; unknown exception types propagate
so a run fails where the failure happened instead of being silently recorded
as a business result.

MySQL/TiDB errno vocabulary (server errors arrive on
``pymysql.err.MySQLError`` instances, client errors on
``pymysql.err.OperationalError``):

- 1205  lock wait timeout exceeded;
- 3024  query execution interrupted, maximum execution time exceeded;
- 9007  TiDB write conflict (optimistic transaction retryable abort);
- 1213  deadlock found;
- 1317  query execution was interrupted (KILL);
- 1040  too many connections; 1042/1045/1049/1053 host/auth/db errors;
- 2002/2003/2006/2012/2013/2026  pymysql client connection failures.

Commit-result-unknown semantics: an error raised by ``commit()`` (e.g. 2013
lost connection) records the attempt as its classified outcome and the
identity stays open for retry; the instance plan's SQL must be idempotent so a
retry re-checks the business key instead of assuming the commit rolled back.
"""

from __future__ import annotations

import pymysql.err

from src.persistent_scenarios.runtime.ledger import AttemptOutcome, JobAttemptOutcome

_TIMEOUT_ERRNOS = frozenset({1205, 3024})
_CONNECTION_ERRNOS = frozenset({1040, 1042, 1043, 1044, 1045, 1049, 1053, 1152, 1153, 2002, 2003, 2006, 2012, 2013, 2026, 2027})
_ABORT_ERRNOS = frozenset({9007, 1213, 1317})


def _mysql_errno(exc: Exception) -> int | None:
    if not isinstance(exc, pymysql.err.MySQLError):
        raise exc
    args = exc.args
    if not args:
        return None
    errno = args[0]
    if isinstance(errno, bool) or not isinstance(errno, int):
        return None
    return errno


def classify_transaction_outcome(exc: Exception) -> AttemptOutcome:
    """Map a raised MySQL/TiDB error to a ledger attempt outcome."""
    errno = _mysql_errno(exc)
    if errno is None:
        raise exc
    if errno in _TIMEOUT_ERRNOS:
        return AttemptOutcome.TIMED_OUT
    if errno in _CONNECTION_ERRNOS:
        return AttemptOutcome.CONNECTION_REFUSED
    if errno in _ABORT_ERRNOS:
        return AttemptOutcome.ABORTED
    return AttemptOutcome.ABORTED


def classify_job_outcome(exc: Exception) -> JobAttemptOutcome:
    outcome = classify_transaction_outcome(exc)
    if outcome is AttemptOutcome.TIMED_OUT:
        return JobAttemptOutcome.FAILED
    if outcome is AttemptOutcome.CONNECTION_REFUSED:
        return JobAttemptOutcome.FAILED
    return JobAttemptOutcome.FAILED


class WorkloadConnectionFailure(RuntimeError):
    """A workload worker could not open its TiDB connection."""
