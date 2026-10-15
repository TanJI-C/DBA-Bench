"""Fixture guards for the long_running_tx scenario family.

Covers the two defenses against environment-dominated session-count scoring:
the evaluator fixture pre-check (missing contract sessions without agent
termination invalidate the run instead of producing OP=False) and the
injector activation-time session contract assertion."""

import json
import sys
import threading
import time
from unittest.mock import MagicMock

import pytest

from src.scenarios import ALL_SCENARIOS
from src.scenarios.base import CaseRun
from src.scenarios.evaluation.postgres.health_check.long_running_tx import (
    LongRunningTxFixtureMissingError,
)
from src.scenarios.postgres.health_check.long_running_tx import (
    PgHealthCheckLongRunningTxInjector,
)

SCENARIO_ID = "pg_health_check_long_running_tx"
CASE_ID = "single_idle_transaction_cleanup_simple"
BLOCKER = "checkout-rw-pool-simple"
DECOY = "payment-short-tx-simple"


def _scenario_case():
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == SCENARIO_ID)
    return scenario, scenario.get_case(CASE_ID)


REPORT = {
    "diagnosis": {"conditions": [
        {
            "type": "blocking_session",
            "factor": "idle-in-transaction holding cleanup horizon",
            "entity": f"PID 79 ({BLOCKER})",
            "evidence": ["stale session blocks cleanup"],
        },
        {
            "type": "vacuum_cleanup_blocked",
            "factor": "cleanup blocked by old snapshot",
            "entity": "table_customer",
            "evidence": ["cleanup horizon cannot advance"],
        },
        {
            "type": "decoy_excluded",
            "factor": "short idle transaction must be preserved",
            "entity": DECOY,
            "evidence": ["unrelated session left untouched"],
        },
        {
            "type": "target_cleanup",
            "factor": "terminate only the stale blocker then vacuum customer",
            "entity": "customer",
            "evidence": ["targeted blocker cleanup"],
        },
        {
            "type": "timeout",
            "factor": "configure a five minute idle transaction timeout",
            "entity": "idle_in_transaction_session_timeout",
            "evidence": ["idle timeout guardrail"],
        },
    ]},
    "outcome": {
        "changes": [
            f"terminated {BLOCKER} then vacuumed customer",
            "set idle_in_transaction_session_timeout to 5min",
        ],
        "verification": ["verified the case-specific final state"],
    },
    "summary": "The stale blocker was removed and the short decoy transaction was preserved.",
}


class FixtureCountsFakeEnv:
    """Serve the session-count probes plus the remaining LTX outcome queries."""

    def __init__(self, *, blocker_count, decoy_count, recovered=True):
        self.blocker_count = blocker_count
        self.decoy_count = decoy_count
        self.recovered = recovered
        self.user = "postgres"
        self.dbname = "testdb"

    def open_workload_connection(self, application_name):
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (
            300000 if self.recovered else 0, "configuration file",
        )
        return conn

    def execute_sql(self, sql):
        normalized = sql.casefold()
        if "pg_stat_activity" in normalized:
            if DECOY in normalized:
                rows = [[self.decoy_count]]
            else:
                rows = [[self.blocker_count]]
        elif "n_dead_tup" in normalized:
            rows = [[0 if self.recovered else 1200]]
        else:
            rows = [[1]]
        return json.dumps({"status": "success", "result": rows})


def _terminate_by_name_action(app_name, *, status="success"):
    return {
        "api": "execute_sql",
        "args": {
            "sql_query": (
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                f"WHERE application_name='{app_name}';"
            )
        },
        "result": {"status": status},
    }


def _terminate_by_pid_action(pid, *, status="success"):
    return {
        "api": "execute_sql",
        "args": {"sql_query": f"SELECT pg_terminate_backend({pid});"},
        "result": {"status": status},
    }


def _repair_action():
    return {
        "api": "execute_sql",
        "args": {
            "sql_query": (
                f"ALTER SYSTEM SET idle_in_transaction_session_timeout='5min'; VACUUM customer"
            )
        },
        "result": {"status": "success"},
    }


def _evaluate(env, actions):
    scenario, case = _scenario_case()
    run = CaseRun(
        run_id=f"test-ltx-fixture-guard-{CASE_ID}",
        scenario=scenario,
        case=case,
        env=env,
        action_history=[*actions, {"api": "submit", "args": REPORT}],
    )
    return case.evaluator(env).evaluate(run)


def test_fixture_missing_without_agent_termination_is_invalid_not_op_false():
    env = FixtureCountsFakeEnv(blocker_count=0, decoy_count=1)
    with pytest.raises(LongRunningTxFixtureMissingError) as excinfo:
        _evaluate(env, [_repair_action()])
    assert "LTX-FIXTURE-MISSING:" in str(excinfo.value)
    assert BLOCKER in str(excinfo.value)


def test_decoy_fixture_missing_after_blocker_fix_is_invalid_not_op_false():
    env = FixtureCountsFakeEnv(blocker_count=0, decoy_count=0)
    with pytest.raises(LongRunningTxFixtureMissingError) as excinfo:
        _evaluate(env, [_terminate_by_name_action(BLOCKER), _repair_action()])
    assert "LTX-FIXTURE-MISSING:" in str(excinfo.value)
    assert "role=decoy" in str(excinfo.value)
    assert DECOY in str(excinfo.value)


def test_agent_killed_decoy_scores_op_false_instead_of_invalidation():
    env = FixtureCountsFakeEnv(blocker_count=0, decoy_count=0)
    result = _evaluate(
        env,
        [
            _terminate_by_name_action(BLOCKER),
            _terminate_by_name_action(DECOY),
            _repair_action(),
        ],
    )
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["decoy_preserved"]["pass"] is False
    assert result["outcome"]["checks"]["decoy_preserved"]["actual"] == 0


def test_correct_remediation_with_intact_fixture_passes_op():
    env = FixtureCountsFakeEnv(blocker_count=0, decoy_count=1)
    result = _evaluate(env, [_terminate_by_name_action(BLOCKER), _repair_action()])
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)


def test_pid_termination_observed_with_application_name_is_attributed():
    env = FixtureCountsFakeEnv(blocker_count=0, decoy_count=1)
    observation = {
        "api": "execute_sql",
        "args": {"sql_query": "SELECT pid, application_name, state FROM pg_stat_activity"},
        "result": {"status": "success", "result": [[79, BLOCKER, "idle in transaction"]]},
    }
    result = _evaluate(env, [observation, _terminate_by_pid_action(79), _repair_action()])
    assert result["OutcomePass"] is True


def test_pid_termination_without_prior_observation_does_not_attribute():
    env = FixtureCountsFakeEnv(blocker_count=0, decoy_count=1)
    with pytest.raises(LongRunningTxFixtureMissingError):
        _evaluate(env, [_terminate_by_pid_action(123), _repair_action()])


def test_failed_termination_call_does_not_attribute():
    env = FixtureCountsFakeEnv(blocker_count=0, decoy_count=1)
    with pytest.raises(LongRunningTxFixtureMissingError):
        _evaluate(env, [_terminate_by_name_action(BLOCKER, status="error"), _repair_action()])


class _FakeActivityCursor:
    def __init__(self, counts):
        self._counts = counts
        self.description = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, statement):
        if "select" in statement.casefold():
            self.description = ("blockers", "decoys", "active_noise", "idle_noise")

    def fetchall(self):
        return [list(self._counts)]


class _FakeActivityConnection:
    def __init__(self, counts):
        self._counts = counts
        self.autocommit = False
        self.closed = False

    def cursor(self):
        return _FakeActivityCursor(self._counts)

    def close(self):
        self.closed = True


class _FakeActivityEnv:
    """counts = (blockers, decoys, active_noise, idle_noise) read from pg_stat_activity."""

    host = "localhost"
    port = 15432
    user = "postgres"
    password = "postgres"
    dbname = "postgres"

    def __init__(self, counts):
        self._counts = counts

    def open_workload_connection(self, actor):
        return _FakeActivityConnection(self._counts)


def _injector(env):
    injector = PgHealthCheckLongRunningTxInjector()
    injector.env = env
    injector.app_name = BLOCKER
    injector.decoy_app_name = DECOY
    injector.table = "customer"
    injector.dead_tuple_rows = 1200
    injector.idle_timeout = "2h"
    injector._stop_event = threading.Event()
    injector._thread_error = None
    return injector


@pytest.mark.parametrize("counts", [(1, 0, 1, 1), (0, 2, 1, 1), (1, 0, 0, 1)])
def test_activation_assertion_raises_when_session_contract_violated(monkeypatch, counts):
    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    injector = _injector(_FakeActivityEnv(counts))
    with pytest.raises(RuntimeError, match="session contract"):
        injector._assert_noise_observable()


def test_activation_assertion_passes_on_contract_counts(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    injector = _injector(_FakeActivityEnv((1, 1, 1, 1)))
    injector._assert_noise_observable()


class _FakeHolderCursor:
    description = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, statement):
        return None


class _FakeHolderConnection:
    autocommit = False
    closed = False

    def cursor(self):
        return _FakeHolderCursor()

    def rollback(self):
        return None

    def close(self):
        self.closed = True


class _FakePsycopg2:
    @staticmethod
    def connect(**kwargs):
        return _FakeHolderConnection()


def test_blocker_start_verification_requires_exactly_one_session(monkeypatch):
    monkeypatch.setitem(sys.modules, "psycopg2", _FakePsycopg2())
    injector = _injector(_FakeActivityEnv((0, 1, 1, 1)))
    injector._stop_event = None
    try:
        with pytest.raises(RuntimeError, match="does not match the contract"):
            injector._start_runtime()
    finally:
        if injector._stop_event is not None:
            injector._stop_event.set()


def test_blocker_start_verification_accepts_single_session(monkeypatch):
    monkeypatch.setitem(sys.modules, "psycopg2", _FakePsycopg2())
    injector = _injector(_FakeActivityEnv((1, 1, 1, 1)))
    injector._stop_event = None
    try:
        injector._start_runtime()
        assert injector._thread_error is None
    finally:
        if injector._stop_event is not None:
            injector._stop_event.set()
