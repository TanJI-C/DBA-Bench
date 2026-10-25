from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import psycopg2
import pytest

from src.scenarios import SCENARIOS_BY_ID
from src.scenarios.evaluation.postgres.system_failure.oom import MemoryRecoveryVerifier


CASES = SCENARIOS_BY_ID["pg_system_failure_oom"].scenario.cases
MIB = 1024**2


@pytest.fixture(params=CASES, ids=lambda case: case.case_id)
def recovery(request):
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = ("testdb", "postgres", 128 * MIB, 8 * MIB, 128 * MIB)
    cursor.fetchall.return_value = [(2001, 365)]
    env = SimpleNamespace(
        open_workload_connection=Mock(return_value=connection),
        execute_sql=Mock(side_effect=AssertionError("must not use the Agent session")),
        manage_instance=Mock(side_effect=AssertionError("must not read Agent configuration")),
    )
    context = SimpleNamespace(case_run=SimpleNamespace(case=request.param, env=env))
    return context, connection, cursor


def test_memory_and_original_probe_use_one_fresh_login(recovery):
    context, connection, cursor = recovery
    check = MemoryRecoveryVerifier().verify(context)
    assert check.passed
    assert check.actual["database"] == "testdb"
    assert check.actual["role"] == "postgres"
    assert check.actual["probe_rows"] == [(2001, 365)]
    context.case_run.env.open_workload_connection.assert_called_once()
    assert cursor.execute.call_args_list[-1].args == (context.case_run.case.tpcds_memory_safety_probe_sql,)
    assert cursor.execute.call_count == 2
    assert connection.autocommit is True
    connection.close.assert_called_once()


@pytest.mark.parametrize("shared,work,next_shared", [
    (128, 512, 128),  # An Agent-only SET cannot repair the fresh business login.
    (256, 8, 128),   # A safe file setting does not repair the running instance yet.
    (128, 8, 768),   # A running instance must not retain a dangerous restart setting.
])
def test_unsafe_memory_fails_before_running_probe(recovery, shared, work, next_shared):
    context, connection, cursor = recovery
    cursor.fetchone.return_value = ("testdb", "postgres", shared * MIB, work * MIB, next_shared * MIB)
    check = MemoryRecoveryVerifier().verify(context)
    assert not check.passed
    assert check.actual["probe_executed"] is False
    assert cursor.execute.call_count == 1
    connection.close.assert_called_once()


def test_smaller_safe_values_and_safe_pending_restart_are_accepted(recovery):
    context, _, cursor = recovery
    cursor.fetchone.return_value = ("testdb", "postgres", 64 * MIB, 4 * MIB, 32 * MIB)
    assert MemoryRecoveryVerifier().verify(context).passed


def test_unavailable_business_login_is_failed_outcome(recovery):
    context, _, _ = recovery
    context.case_run.env.open_workload_connection.side_effect = psycopg2.OperationalError("connection refused")
    check = MemoryRecoveryVerifier().verify(context)
    assert not check.passed
    assert "connection refused" in check.actual["connection_error"]


def test_business_query_failure_is_failed_outcome_and_closes_connection(recovery):
    context, connection, cursor = recovery
    cursor.execute.side_effect = [None, psycopg2.errors.QueryCanceled("statement timeout")]
    check = MemoryRecoveryVerifier().verify(context)
    assert not check.passed
    assert check.actual["probe_executed"] is True
    assert "statement timeout" in check.actual["business_query_error"]
    connection.close.assert_called_once()


def test_invalid_persistent_memory_is_failed_outcome(recovery):
    context, connection, cursor = recovery
    cursor.execute.side_effect = psycopg2.errors.InvalidParameterValue("invalid memory size")
    check = MemoryRecoveryVerifier().verify(context)
    assert not check.passed
    assert "invalid memory size" in check.actual["configuration_error"]
    connection.close.assert_called_once()


def test_unexpected_evaluator_error_propagates(recovery):
    context, connection, cursor = recovery
    cursor.execute.side_effect = RuntimeError("broken evaluator")
    with pytest.raises(RuntimeError, match="broken evaluator"):
        MemoryRecoveryVerifier().verify(context)
    connection.close.assert_called_once()
