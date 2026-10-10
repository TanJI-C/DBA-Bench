"""Append-only external business ledger stored outside the database container.

The ledger lives in the run directory on the host filesystem. The tested agent
only reaches the database through its tool surface, so these records are the
trusted copy that evaluation compares against database-side state.
"""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Mapping


class ExternalJsonlLedger:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path = path
        self._lock = threading.Lock()
        self._seq = 0
        with self._lock:
            if path.exists():
                self._seq = len(path.read_text(encoding="utf-8").splitlines())

    @property
    def path(self) -> Path:
        return self._path

    def append(self, kind: str, **fields: Any) -> dict[str, Any]:
        with self._lock:
            self._seq += 1
            record = {
                "seq": self._seq,
                "kind": kind,
                "wall_utc": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
                **fields,
            }
            line = json.dumps(record, ensure_ascii=False, sort_keys=True, default=str)
            with open(self._path, "a", encoding="utf-8") as handle:
                handle.write(line + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            return record

    def read_all(self) -> tuple[dict[str, Any], ...]:
        with self._lock:
            if not self._path.exists():
                return ()
            lines = self._path.read_text(encoding="utf-8").splitlines()
        records = []
        for index, line in enumerate(lines):
            record = json.loads(line)
            if record.get("seq") != index + 1:
                raise ValueError(
                    "External ledger sequence is not contiguous: "
                    f"path={self._path!r}, line={index + 1}, seq={record.get('seq')!r}"
                )
            records.append(record)
        return tuple(records)

    def read_kind(self, kind: str) -> tuple[dict[str, Any], ...]:
        return tuple(record for record in self.read_all() if record["kind"] == kind)

    def entry_count(self) -> int:
        with self._lock:
            return self._seq
