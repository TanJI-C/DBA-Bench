from types import SimpleNamespace

import pytest

from examples import run_tidb_system_failure_gc_mvcc_recovery_scenario as example


def mock_writer(monkeypatch, results):
    agent = object.__new__(example.K01ReferenceMockAgent)
    agent.case = SimpleNamespace(runtime=SimpleNamespace(sql_timeout_seconds=2))
    calls = []
    responses = iter(results)
    agent.execute = lambda api, args, **kwargs: calls.append((api, args)) or next(responses)
    clock = [0]
    monkeypatch.setattr(example.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(example.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + 2))
    return agent, calls


def test_mock_authorized_write_waits_only_for_schema_recovery(monkeypatch):
    agent, calls = mock_writer(monkeypatch, [
        {"status": "error", "error": "TiDB SQL failed: error=(8027, 'Information schema is out of date')"},
        {"status": "success", "rows_affected": 1},
    ])

    assert agent._write_after_schema_recovery("INSERT authorized row")["rows_affected"] == 1
    assert calls == [("execute_sql", {"sql_query": "INSERT authorized row"})] * 2


def test_mock_authorized_write_exposes_other_sql_errors_immediately(monkeypatch):
    agent, calls = mock_writer(monkeypatch, [{"status": "error", "error": "permission denied"}])

    with pytest.raises(RuntimeError, match="permission denied"):
        agent._write_after_schema_recovery("INSERT authorized row")
    assert len(calls) == 1


def test_mock_authorized_write_schema_wait_has_a_deadline(monkeypatch):
    stale = {"status": "error", "error": "TiDB SQL failed: error=(8027, 'Information schema is out of date')"}
    agent, calls = mock_writer(monkeypatch, [stale, stale])

    with pytest.raises(RuntimeError, match="schema did not recover.*deadline"):
        agent._write_after_schema_recovery("INSERT authorized row")
    assert len(calls) == 2
