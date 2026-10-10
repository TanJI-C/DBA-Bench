"""Scripted database fakes shared by the pg5 OLTP instance tests.

`ScriptedConnection` answers `cursor.execute` calls from a list of handlers
matched by SQL substring; unmatched SQL fails loudly so tests catch statement
drift instead of silently passing.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class ExecutedStatement:
    sql: str
    params: object


Handler = Callable[[str, object], object]


class ScriptedCursor:
    def __init__(self, connection: "ScriptedConnection") -> None:
        self._connection = connection
        self.rowcount = -1
        self._rows: list[tuple] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, sql: str, params: object = None) -> None:
        normalized = " ".join(sql.split())
        self._connection.statements.append(ExecutedStatement(normalized, params))
        if normalized.startswith("SET "):  # SET LOCAL / SET TRANSACTION are txn setup, not test assertions
            self._rows, self.rowcount = [], -1
            return
        for fragment, handler in self._connection.handlers:
            if fragment in normalized:
                result = handler(sql, params)
                if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], list):
                    rows, rowcount = result
                    self._rows = rows
                    self.rowcount = rowcount
                elif isinstance(result, Exception):
                    raise result
                else:
                    self._rows, self.rowcount = [], -1
                return
        raise AssertionError(
            f"ScriptedConnection received unexpected SQL: sql={sql!r}, "
            f"known_fragments={[fragment for fragment, _ in self._connection.handlers]!r}"
        )

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return list(self._rows)


class ScriptedConnection:
    def __init__(self, handlers: list[tuple[str, Handler]] | None = None) -> None:
        self.handlers: list[tuple[str, Handler]] = list(handlers or [])
        self.statements: list[ExecutedStatement] = []
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self) -> ScriptedCursor:
        return ScriptedCursor(self)

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

    def close(self) -> None:
        self.closed = True

    # -- test conveniences -------------------------------------------------

    def executed(self, fragment: str) -> list[ExecutedStatement]:
        return [s for s in self.statements if fragment in s.sql]

    def set_handler(self, fragment: str, handler: Handler) -> None:
        self.handlers.append((fragment, handler))


class ScriptedSource:
    """ConnectionSource that lazily creates scripted connections per application."""

    def __init__(self, factory: Callable[[str], ScriptedConnection] | None = None) -> None:
        self._factory = factory
        self._lock = threading.Lock()
        self.connections: dict[str, ScriptedConnection] = {}

    def connection(self, application_name: str) -> ScriptedConnection:
        with self._lock:
            if application_name not in self.connections:
                if self._factory is None:
                    self.connections[application_name] = ScriptedConnection()
                else:
                    self.connections[application_name] = self._factory(application_name)
            return self.connections[application_name]

    def get(self, application_name: str) -> ScriptedConnection:
        return self.connections[application_name]


def constant_rows(rows: list[tuple], rowcount: int = -1):
    return lambda sql, params: (rows, rowcount)


def rowcount_result(rowcount: int):
    return lambda sql, params: ([], rowcount)


def raising(exc: Exception):
    return lambda sql, params: exc


def pg_error(base: type, pgcode: str | None) -> Exception:
    """Builds a psycopg2 error carrying the given pgcode (the attribute is
    readonly on instances, so the subclass carries it as a class attribute)."""

    class _CodedError(base):
        pass

    _CodedError.pgcode = pgcode
    return _CodedError("synthetic database error")
