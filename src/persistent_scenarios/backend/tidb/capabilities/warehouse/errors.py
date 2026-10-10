"""TiDB-side job attempt outcome classification (the pymysql analogue of pgerrors).

Every outcome keeps its evidence detail; unknown errors surface as their own class
instead of being folded into a generic failure.
"""

from __future__ import annotations

from typing import Mapping

from src.persistent_scenarios.runtime.ledger import JobAttemptOutcome


def classify_job_outcome(exc: Exception) -> tuple[JobAttemptOutcome, Mapping]:
    """Map a raised exception during a job attempt to (outcome, detail)."""
    import pymysql

    if isinstance(exc, pymysql.err.OperationalError) or isinstance(exc, pymysql.err.InternalError):
        code = exc.args[0] if exc.args else None
        message = str(exc.args[1] if len(exc.args) > 1 else exc)
        if code == 3024:  # max_execution_time exceeded
            return JobAttemptOutcome.FAILED, {"error_code": code, "error_message": message[:400], "timed_out": True}
        if code == 1317:  # query execution was interrupted (KILL TIDB cancel)
            return JobAttemptOutcome.CANCELLED, {"error_code": code, "error_message": message[:400]}
        if code == 8134:  # Out Of Memory Quota (tidb_mem_quota_query exceeded, oom-action=cancel)
            return JobAttemptOutcome.FAILED, {"error_code": code, "error_message": message[:400], "oom": True}
        if code in (2013, 2012):  # lost connection to server
            return JobAttemptOutcome.CONNECTION_REFUSED, {"error_code": code, "error_message": message[:400]}
        return JobAttemptOutcome.FAILED, {"error_code": code, "error_message": message[:400]}
    if isinstance(exc, RuntimeError):
        return JobAttemptOutcome.FAILED, {"error_message": str(exc)[:400]}
    raise exc
