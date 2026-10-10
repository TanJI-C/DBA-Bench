import json

from src.execution.environment import PGEnv


def make_stub_env():
    env = PGEnv.__new__(PGEnv)
    env._history_sql_archive = None
    executed = []
    env._execute_sql_surface = lambda sql, enforce_history_guard: (
        executed.append(sql) or json.dumps({"status": "success"})
    )
    return env, executed


def test_execute_sql_accepts_alert_instance_name_as_primary_alias():
    env, executed = make_stub_env()

    result = PGEnv.execute_sql(env, "SELECT 1;", target="postgresql-primary")

    assert json.loads(result)["status"] == "success"
    assert executed == ["SELECT 1;"]


def test_execute_sql_still_rejects_unknown_targets():
    env, executed = make_stub_env()

    result = PGEnv.execute_sql(env, "SELECT 1;", target="replica-1")

    assert "Unknown PostgreSQL SQL target" in result
    assert executed == []
