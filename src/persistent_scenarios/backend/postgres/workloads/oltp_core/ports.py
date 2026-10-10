"""Module-local ports and adapters for the pg5 OLTP workload drivers.

These types are structural Protocols on purpose: core runtime clocks and
scripted test fakes satisfy them without any adapter layer.
"""

from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from typing import Any, Mapping, Protocol


class Clock(Protocol):
    def monotonic(self) -> float: ...
    def wait_until(self, deadline: float, stop: threading.Event) -> bool: ...


class DBConnection(Protocol):
    """A real psycopg2-style connection (autocommit off)."""

    def cursor(self) -> Any: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def close(self) -> None: ...


class ConnectionSource(Protocol):
    """Opens one real database connection per call; caller owns closing it."""

    def connection(self, application_name: str) -> DBConnection: ...


class TcpConnectionSource:
    """Opens per-role TCP connections; used by the experiment drivers so the
    workload authenticates as the instance application roles instead of the
    DBA superuser."""

    def __init__(self, *, host: str, port: int, user: str, password: str, dbname: str) -> None:
        self._connect_kwargs = {
            "host": host,
            "port": int(port),
            "user": user,
            "password": password,
            "dbname": dbname,
        }

    def connection(self, application_name: str) -> DBConnection:
        import psycopg2

        return psycopg2.connect(
            application_name=application_name,
            connect_timeout=3,
            **self._connect_kwargs,
        )


class EvidenceLedgerFile:
    """Append-only, hash-chained JSONL evidence file owned by the driver process.

    The database superuser cannot write host files, so this file is the trusted
    external truth for the run. Records are chained with sha256 to make any
    tampering detectable.
    """

    def __init__(self, path: Path, run_id: str) -> None:
        if path.exists():
            raise ValueError(
                "Evidence ledger file must not already exist: "
                f"path={str(path)!r}, run_id={run_id!r}"
            )
        self._path = path
        self._run_id = run_id
        self._lock = threading.Lock()
        self._previous_digest = ""
        self._sequence = 0
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    @property
    def path(self) -> Path:
        return self._path

    def append(self, record: Mapping[str, Any]) -> str:
        with self._lock:
            self._sequence += 1
            envelope = {
                "run_id": self._run_id,
                "seq": self._sequence,
                "prev": self._previous_digest,
                "record": dict(record),
            }
            line = json.dumps(envelope, ensure_ascii=False, sort_keys=True)
            digest = hashlib.sha256(line.encode("utf-8")).hexdigest()
            envelope["digest"] = digest
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(envelope, ensure_ascii=False, sort_keys=True) + "\n")
            self._previous_digest = digest
            return digest

    def verify_chain(self) -> int:
        """Re-reads the file and verifies the hash chain; returns record count."""

        previous = ""
        sequence = 0
        with self._path.open("r", encoding="utf-8") as handle:
            for raw in handle:
                envelope = json.loads(raw)
                stored = envelope["digest"]
                body = dict(envelope)
                del body["digest"]
                recomputed = hashlib.sha256(
                    json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")
                ).hexdigest()
                if recomputed != stored:
                    raise ValueError(
                        "Evidence ledger hash chain broken: "
                        f"path={str(self._path)!r}, seq={envelope.get('seq')!r}"
                    )
                if envelope["prev"] != previous or envelope["seq"] != sequence + 1:
                    raise ValueError(
                        "Evidence ledger chain order invalid: "
                        f"path={str(self._path)!r}, seq={envelope.get('seq')!r}, expected_seq={sequence + 1}"
                    )
                previous = stored
                sequence += 1
        if sequence != self._sequence:
            raise ValueError(
                "Evidence ledger file lost records written by this process: "
                f"path={str(self._path)!r}, file_records={sequence}, written={self._sequence}"
            )
        return sequence
