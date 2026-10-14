import json
import subprocess
from types import SimpleNamespace
from unittest.mock import MagicMock

import psycopg2
from psycopg2 import sql
import pytest

from src.execution.environment import PGEnv


def make_env(connection=None):
    env = PGEnv.__new__(PGEnv)
    env._conn = connection
    env.deployment = SimpleNamespace(container_name="config-test", pgdata="/pgdata")
    return env


@pytest.mark.parametrize("value", [
    "cp %p /archive/$(date +%F)/%f",
    "test ! -f /a/%f && cp %p /a/%f",
    "gzip < %p | cat > /a/%f.gz",
    "printf '%s' %p > /a/%f",
    "printf '\\n' > /a/%f\n# still part of the value",
])
def test_offline_set_config_preserves_value_without_shell(monkeypatch, value):
    calls = []
    original = (
        "# archive_command is managed below\n"
        "archive_command = 'true'\n"
        " archive_command = 'false'\n"
        "archive_timeout = '60s'\n"
    )

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(stdout=original if command[3] == "cat" else "")

    monkeypatch.setattr(subprocess, "run", run)
    result = json.loads(make_env()._set_config("archive_command", value))
    assert result["status"] == "success"
    assert calls[0][0] == ["docker", "exec", "config-test", "cat", "/pgdata/postgresql.auto.conf"]
    assert calls[1][0] == ["docker", "exec", "-i", "config-test", "tee", "/pgdata/postgresql.auto.conf"]
    escaped = value.replace("\\", "\\\\").replace("'", "''").replace("\n", "\\n")
    assert calls[1][1]["input"] == (
        "# archive_command is managed below\narchive_timeout = '60s'\n"
        f"archive_command = '{escaped}'\n"
    )


def test_online_set_config_binds_value_as_sql_parameter():
    connection = MagicMock()
    connection.closed = 0
    value = "test ! -f '/a/%f' && cp %p /a/%f"
    result = json.loads(make_env(connection)._set_config("archive_command", value))
    assert result["status"] == "success"
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.execute.assert_called_once_with(
        sql.SQL("ALTER SYSTEM SET {} = %s;").format(sql.Identifier("archive_command")),
        (value,),
    )


def test_online_sql_error_does_not_write_offline_config(monkeypatch):
    connection = MagicMock()
    connection.closed = 0
    connection.cursor.return_value.__enter__.return_value.execute.side_effect = psycopg2.ProgrammingError("bad parameter")
    docker = MagicMock()
    monkeypatch.setattr(subprocess, "run", docker)
    result = json.loads(make_env(connection)._set_config("unknown_setting", "1"))
    assert result["status"] == "error"
    assert "unknown_setting" in result["error"]
    docker.assert_not_called()


def test_failed_offline_read_does_not_overwrite_config(monkeypatch):
    docker = MagicMock(side_effect=subprocess.CalledProcessError(1, ["docker", "exec", "cat"]))
    monkeypatch.setattr(subprocess, "run", docker)
    result = json.loads(make_env()._set_config("archive_command", "true"))
    assert result["status"] == "error"
    assert "config-test" in result["error"]
    assert "archive_command" in result["error"]
    assert docker.call_count == 1


def test_offline_parameter_name_cannot_inject_config_lines(monkeypatch):
    docker = MagicMock()
    monkeypatch.setattr(subprocess, "run", docker)
    result = json.loads(make_env()._set_config("archive_command\nshared_preload_libraries", "true"))
    assert result["status"] == "error"
    assert "Invalid PostgreSQL parameter name" in result["error"]
    docker.assert_not_called()
