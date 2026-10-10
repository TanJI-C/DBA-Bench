"""pymysql error classification tests."""

import pymysql.err
import pytest

from src.persistent_scenarios.backend.tidb.tidberrors import (
    classify_job_outcome,
    classify_transaction_outcome,
)
from src.persistent_scenarios.runtime.ledger import AttemptOutcome, JobAttemptOutcome


@pytest.mark.parametrize("errno", [1205, 3024])
def test_timeouts(errno):
    exc = pymysql.err.OperationalError(errno, "timeout")
    assert classify_transaction_outcome(exc) is AttemptOutcome.TIMED_OUT


@pytest.mark.parametrize("errno", [1040, 1045, 2002, 2003, 2006, 2013])
def test_connection_failures(errno):
    exc = pymysql.err.OperationalError(errno, "connection problem")
    assert classify_transaction_outcome(exc) is AttemptOutcome.CONNECTION_REFUSED
    assert classify_job_outcome(exc) is JobAttemptOutcome.FAILED


@pytest.mark.parametrize("errno", [9007, 1213, 1317])
def test_retryable_abort(errno):
    exc = pymysql.err.OperationalError(errno, "conflict")
    assert classify_transaction_outcome(exc) is AttemptOutcome.ABORTED


def test_unknown_mysql_error_is_aborted():
    exc = pymysql.err.OperationalError(1062, "Duplicate entry")
    assert classify_transaction_outcome(exc) is AttemptOutcome.ABORTED


def test_non_mysql_exception_propagates():
    with pytest.raises(RuntimeError):
        classify_transaction_outcome(RuntimeError("not a database error"))
