"""Public control-table readers for the pg5 OLTP instances.

The client retry configuration and the release task queue are real tables
consumed by real workers; the DBA edits them through SQL and the workers pick
the changes up on their next poll. The trigger-backed audit trail lives in
`schema.py`; this module only reads and enforces the driver-visible contract.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Mapping

from .ports import Clock, ConnectionSource, DBConnection


@dataclass(frozen=True, slots=True)
class ClientConfig:
    config_version: int
    request_timeout_ms: int
    max_retries: int
    retry_backoff_ms: int
    retry_jitter_ms: int

    def __post_init__(self) -> None:
        if self.request_timeout_ms <= 0:
            raise ValueError(f"request_timeout_ms must be positive: value={self.request_timeout_ms!r}")
        if self.max_retries < 0:
            raise ValueError(f"max_retries must be non-negative: value={self.max_retries!r}")
        for name in ("retry_backoff_ms", "retry_jitter_ms"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative: value={getattr(self, name)!r}")


CLIENT_CONFIG_SQL = (
    "SELECT config_version, request_timeout_ms, max_retries, retry_backoff_ms, retry_jitter_ms "
    "FROM ops.client_config WHERE id = 1;"
)


def read_client_config(connection: DBConnection) -> ClientConfig:
    with connection.cursor() as cursor:
        cursor.execute(CLIENT_CONFIG_SQL)
        row = cursor.fetchone()
    if row is None:
        raise ValueError("ops.client_config has no row with id=1; the dataset image is incomplete")
    return ClientConfig(int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[4]))


@dataclass(frozen=True, slots=True)
class ReleaseTask:
    task_id: str
    kind: str
    ddl_statement: str | None
    depends_on: str | None
    lock_timeout_ms: int
    batch_rows: int
    rate_rows_per_second: int
    paused: bool
    window_start: float
    status: str
    rows_done: int

    def __post_init__(self) -> None:
        if self.kind not in {"ddl", "backfill"}:
            raise ValueError(f"Unknown release task kind: task_id={self.task_id!r}, kind={self.kind!r}")
        if self.status not in {"pending", "waiting_dependency", "running", "done", "failed"}:
            raise ValueError(f"Unknown release task status: task_id={self.task_id!r}, status={self.status!r}")


RELEASE_TASK_SQL = (
    "SELECT task_id, kind, ddl_statement, depends_on, lock_timeout_ms, batch_rows, "
    "rate_rows_per_second, paused, window_start, status, rows_done "
    "FROM ops.release_tasks WHERE task_id = %(task_id)s;"
)


def read_release_task(connection: DBConnection, task_id: str) -> ReleaseTask:
    with connection.cursor() as cursor:
        cursor.execute(RELEASE_TASK_SQL, {"task_id": task_id})
        row = cursor.fetchone()
    if row is None:
        raise ValueError(f"ops.release_tasks has no row for the requested task: task_id={task_id!r}")
    return ReleaseTask(
        str(row[0]), str(row[1]),
        None if row[2] is None else str(row[2]),
        None if row[3] is None else str(row[3]),
        int(row[4]), int(row[5]), int(row[6]), bool(row[7]), float(row[8]), str(row[9]), int(row[10]),
    )


class ClientConfigPoller:
    """Background poller that keeps the driver's active retry policy current."""

    def __init__(self, source: ConnectionSource, clock: Clock, poll_seconds: float) -> None:
        self._source = source
        self._clock = clock
        self._poll_seconds = poll_seconds
        self._lock = threading.Lock()
        self._active: ClientConfig | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._connection = None
        self._error: BaseException | None = None

    def start(self) -> None:
        if self._thread is not None:
            raise RuntimeError("ClientConfigPoller cannot start twice")
        self._connection = self._source.connection("config_poller")
        config = read_client_config(self._connection)
        self._connection.commit()
        with self._lock:
            self._active = config
        self._thread = threading.Thread(
            target=self._loop, name="pg5-oltp-client-config-poller", daemon=True
        )
        self._thread.start()

    def active(self) -> ClientConfig:
        with self._lock:
            if self._active is None:
                raise RuntimeError(
                    "Client retry policy requested before the first successful control-table read"
                )
            return self._active

    def applied_version(self) -> int:
        return self.active().config_version

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=10)
            if self._thread.is_alive():
                raise RuntimeError("ClientConfigPoller thread did not stop within its join timeout")
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        if self._error is not None:
            raise RuntimeError(
                f"ClientConfigPoller failed while reading ops.client_config: error={self._error!r}"
            ) from self._error

    def _loop(self) -> None:
        try:
            while not self._stop.is_set():
                config = read_client_config(self._connection)
                self._connection.commit()
                with self._lock:
                    self._active = config
                self._clock.wait_until(self._clock.monotonic() + self._poll_seconds, self._stop)
        except BaseException as exc:  # noqa: BLE001 - poller failure must surface at stop()
            self._error = exc
            self._stop.set()


def column_exists(connection: DBConnection, table: str, column: str) -> bool:
    schema, name = table.split(".")
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = %(schema)s AND table_name = %(name)s AND column_name = %(column)s;",
            {"schema": schema, "name": name, "column": column},
        )
        row = cursor.fetchone()
    connection.commit()
    return row is not None


def effective_guc(connection: DBConnection, guc: str) -> str:
    with connection.cursor() as cursor:
        cursor.execute(f"SHOW {guc};")
        row = cursor.fetchone()
    if row is None:
        raise ValueError(f"SHOW returned no value: guc={guc!r}")
    connection.commit()
    return str(row[0])
