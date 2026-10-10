from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any

import yaml

from .models import RunRecord


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def atomic_write_json(path: Path, data: Any) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


class ExperimentStore:
    def __init__(self, root: Path, experiment_id: str):
        self.root = root.resolve() / experiment_id
        self.runs_dir = self.root / "runs"
        self._lock = threading.RLock()

    def initialize(self, manifest: dict[str, Any], environment: dict[str, Any]) -> None:
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = self.root / "manifest.yaml"
        rendered = yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False)
        if manifest_path.exists() and manifest_path.read_text(encoding="utf-8") != rendered:
            raise ValueError(
                f"Experiment {self.root.name!r} already exists with a different manifest: {manifest_path}"
            )
        atomic_write_text(manifest_path, rendered)
        if not (self.root / "environment.json").exists():
            atomic_write_json(self.root / "environment.json", environment)

    def run_dir(self, run_id: str) -> Path:
        return self.runs_dir / run_id

    def attempt_dir(self, run_id: str, attempt: int) -> Path:
        return self.run_dir(run_id) / "attempts" / f"{attempt:03d}"

    def attempt_path(self, run_id: str, attempt: int) -> Path:
        return self.attempt_dir(run_id, attempt) / "attempt.json"

    def record_path(self, run_id: str) -> Path:
        return self.run_dir(run_id) / "run.json"

    def load(self, run_id: str) -> RunRecord | None:
        path = self.record_path(run_id)
        if not path.exists():
            return None
        return RunRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def save(self, record: RunRecord) -> None:
        with self._lock:
            atomic_write_json(self.record_path(record.run_id), record.as_dict())
            self.rebuild_index()

    def save_attempt(self, record: RunRecord) -> None:
        if record.status not in {"succeeded", "failed", "timed_out", "interrupted"}:
            raise ValueError(
                f"Attempt snapshot requires a terminal run: run_id={record.run_id!r}, "
                f"attempt={record.attempt}, status={record.status!r}"
            )
        path = self.attempt_path(record.run_id, record.attempt)
        if path.exists():
            raise FileExistsError(
                f"Attempt snapshot already exists: run_id={record.run_id!r}, "
                f"attempt={record.attempt}, path={path}"
            )
        atomic_write_json(path, record.as_dict())

    def records(self) -> list[RunRecord]:
        with self._lock:
            records = [
                RunRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))
                for path in sorted(self.runs_dir.glob("*/run.json"))
            ]
            return sorted(records, key=lambda item: item.run_id)

    def rebuild_index(self) -> None:
        with self._lock:
            records = self.records()
            lines = [json.dumps(record.as_dict(), ensure_ascii=False) for record in records]
            atomic_write_text(self.root / "runs.jsonl", "\n".join(lines) + ("\n" if lines else ""))
            failures = [
                json.dumps(record.as_dict(), ensure_ascii=False)
                for record in records
                if record.status in {"failed", "timed_out", "interrupted"}
            ]
            atomic_write_text(
                self.root / "failures.jsonl",
                "\n".join(failures) + ("\n" if failures else ""),
            )
