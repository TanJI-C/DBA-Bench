from __future__ import annotations

import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CANONICAL_RE = re.compile(r"^run_(?P<run_id>.+)__a(?P<attempt>\d{3})\.json$")
LEGACY_RE = re.compile(
    r"^run_(?P<scenario>.+)_(?P<agent>LLMAgent|MockLLMAgent|DbotAgent|DbaiopsAgent|HumanAgent)"
    r"_(?P<timestamp>\d{4}-\d{2}-\d{2}_\d{2}_\d{2}_\d{2}|\d{10})\.json$"
)


def parse_trace_filename(filename: str) -> dict[str, Any]:
    canonical = CANONICAL_RE.fullmatch(filename)
    if canonical:
        run_id = canonical.group("run_id")
        parts = run_id.split("__")
        if len(parts) != 5:
            return {"filename_status": "invalid_filename"}
        experiment_id, scenario_id, case_id, agent_id, repetition = parts
        if not re.fullmatch(r"r\d{3}", repetition):
            return {"filename_status": "invalid_filename"}
        if scenario_id == "persistent-scenario":
            persistent_scenario_id = case_id
            return {
                "filename_status": "valid",
                "filename_format": "persistent_scenario_v1",
                "scenario_kind": "persistent",
                "experiment_id": experiment_id,
                "run_id": run_id,
                "scenario_id": persistent_scenario_id,
                "agent_id": agent_id,
                "repetition": int(repetition.removeprefix("r")),
                "attempt": int(canonical.group("attempt")),
            }
        return {
            "filename_status": "valid",
            "filename_format": "experiment_v1",
            "experiment_id": experiment_id,
            "run_id": run_id,
            "scenario_id": scenario_id,
            "case_id": case_id,
            "agent_id": agent_id,
            "repetition": int(repetition.removeprefix("r")),
            "attempt": int(canonical.group("attempt")),
        }

    legacy = LEGACY_RE.fullmatch(filename)
    if legacy:
        raw_timestamp = legacy.group("timestamp")
        timestamp = (
            datetime.strptime(raw_timestamp, "%Y-%m-%d_%H_%M_%S")
            .replace(tzinfo=timezone.utc)
            .timestamp()
            if "_" in raw_timestamp
            else float(raw_timestamp)
        )
        return {
            "filename_status": "valid",
            "filename_format": "legacy_v2",
            "scenario": legacy.group("scenario"),
            "agent_type": legacy.group("agent"),
            "timestamp": timestamp,
        }
    return {"filename_status": "invalid_filename"}


def trace_summary(path: Path) -> dict[str, Any]:
    stat = path.stat()
    parsed_name = parse_trace_filename(path.name)
    base = {
        "filename": path.name,
        "size_bytes": stat.st_size,
        "mtime": stat.st_mtime,
        **parsed_name,
    }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            **base,
            "parse_status": "invalid_json",
            "parse_error": f"line {exc.lineno}, column {exc.colno}: {exc.msg}",
        }

    metadata = data.get("metadata", {})
    schema = data.get("$schema")
    if schema == "persistent_scenario_trace_v2" and not isinstance(data.get("persistent_scenario_evaluation"), dict):
        return {
            **base,
            "parse_status": "invalid_schema",
            "schema": "persistent_scenario_trace_v2",
            "formal_eligible": data.get("formal_eligible"),
            "parse_error": "persistent_scenario_trace_v2 requires a persistent_scenario_evaluation object",
        }
    if schema == "persistent_scenario_trace_v2":
        evaluation = data["persistent_scenario_evaluation"]
    elif not isinstance(data.get("evaluation"), dict):
        return {
            **base,
            "parse_status": "unsupported_schema",
            "schema": schema,
            "formal_eligible": False,
        }
    else:
        evaluation = data["evaluation"]
    structure = data.get("diagnostic_structure", {})
    return {
        **base,
        "parse_status": "valid",
        "schema": schema,
        "scenario_kind": metadata.get("scenario_kind") or base.get("scenario_kind", "bounded"),
        "scenario": metadata.get("scenario_name") or base.get("scenario"),
        "scenario_id": metadata.get("scenario_id") or base.get("scenario_id"),
        "case_id": metadata.get("case_id") or base.get("case_id"),
        "agent_type": metadata.get("agent_type") or base.get("agent_type"),
        "agent_id": metadata.get("agent_id") or base.get("agent_id"),
        "experiment_id": metadata.get("experiment_id") or base.get("experiment_id"),
        "run_id": metadata.get("run_id") or base.get("run_id"),
        "repetition": metadata.get("repetition") or base.get("repetition"),
        "seed": metadata.get("seed"),
        "timestamp": (
            metadata.get("timestamp_end_wall")
            if schema == "persistent_scenario_trace_v2"
            else metadata.get("timestamp_end") or base.get("timestamp") or stat.st_mtime
        ),
        "diagnosis_pass": evaluation.get("DiagnosisPass") if isinstance(evaluation, dict) else None,
        "outcome_pass": evaluation.get("OutcomePass") if isinstance(evaluation, dict) else None,
        "safe_pass": evaluation.get("SafePass") if isinstance(evaluation, dict) else None,
        "formal_eligible": data.get("formal_eligible") if schema == "persistent_scenario_trace_v2" else None,
        "has_evaluation": isinstance(evaluation, dict),
        "structure_type": structure.get("type"),
    }


class TraceIndex:
    _instances: dict[Path, "TraceIndex"] = {}
    _instances_lock = threading.Lock()

    @classmethod
    def for_directory(cls, traces_dir: str | Path) -> "TraceIndex":
        root = Path(traces_dir).resolve()
        with cls._instances_lock:
            if root not in cls._instances:
                cls._instances[root] = cls(root)
            return cls._instances[root]

    def __init__(self, root: Path):
        self.root = root
        self._entries: dict[str, dict[str, Any]] = {}
        self._signatures: dict[str, tuple[int, int]] = {}
        self._lock = threading.Lock()

    def refresh(self) -> list[dict[str, Any]]:
        with self._lock:
            files = sorted(self.root.glob("run_*.json")) if self.root.exists() else []
            names = {path.name for path in files}
            for removed in self._entries.keys() - names:
                del self._entries[removed]
                del self._signatures[removed]
            for path in files:
                stat = path.stat()
                signature = (stat.st_mtime_ns, stat.st_size)
                if self._signatures.get(path.name) != signature:
                    self._entries[path.name] = trace_summary(path)
                    self._signatures[path.name] = signature
            return list(self._entries.values())

    def query(self, params: dict[str, list[str]]) -> dict[str, Any]:
        entries = self.refresh()
        query = params.get("q", [""])[0].strip().lower()
        if query:
            entries = [entry for entry in entries if query in " ".join(
                str(entry.get(key) or "")
                for key in ("filename", "scenario", "scenario_id", "case_id", "scenario_kind", "agent_type", "agent_id", "experiment_id", "run_id")
            ).lower()]

        for parameter, fields in {
            "scenario": ("scenario", "scenario_id"),
            "agent": ("agent_type", "agent_id"),
            "experiment": ("experiment_id",),
            "schema": ("schema",),
            "structure": ("structure_type",),
            "scenario_kind": ("scenario_kind",),
            "parse_status": ("parse_status",),
            "filename_status": ("filename_status",),
        }.items():
            values = set(params.get(parameter, []))
            if values:
                entries = [entry for entry in entries if any(entry.get(field) in values for field in fields)]

        evaluation = params.get("evaluation", [""])[0]
        if evaluation == "scored":
            entries = [entry for entry in entries if entry.get("outcome_pass") is not None]
        elif evaluation == "unscored":
            entries = [entry for entry in entries if entry.get("outcome_pass") is None]
        elif evaluation == "success":
            entries = [entry for entry in entries if entry.get("safe_pass") is True]
        elif evaluation == "failed":
            entries = [entry for entry in entries if entry.get("safe_pass") is False]

        from_value = params.get("from", [""])[0]
        to_value = params.get("to", [""])[0]
        if from_value:
            start = datetime.fromisoformat(from_value).replace(tzinfo=timezone.utc).timestamp()
            entries = [entry for entry in entries if entry.get("timestamp") is not None and entry["timestamp"] >= start]
        if to_value:
            end = datetime.fromisoformat(to_value).replace(tzinfo=timezone.utc).timestamp() + 86400
            entries = [entry for entry in entries if entry.get("timestamp") is not None and entry["timestamp"] < end]

        sort = params.get("sort", ["timestamp_desc"])[0]
        sort_fields = {
            "timestamp_desc": ("timestamp", True),
            "timestamp_asc": ("timestamp", False),
            "score_desc": ("safe_pass", True),
            "score_asc": ("safe_pass", False),
            "size_desc": ("size_bytes", True),
        }
        if sort not in sort_fields:
            raise ValueError(f"Unknown trace sort: {sort!r}")
        field, reverse = sort_fields[sort]
        entries.sort(key=lambda entry: (entry.get(field) is not None, entry.get(field) or 0), reverse=reverse)

        total = len(entries)
        offset = int(params.get("offset", ["0"])[0])
        limit = int(params.get("limit", ["100"])[0])
        if offset < 0 or limit < 1 or limit > 500:
            raise ValueError(f"Invalid pagination: offset={offset}, limit={limit}; limit must be 1..500")
        items = entries[offset:offset + limit]
        all_entries = self.refresh()
        filters = {
            "scenarios": sorted({entry.get("scenario_id") or entry.get("scenario") for entry in all_entries if entry.get("scenario_id") or entry.get("scenario")}),
            "agents": sorted({entry.get("agent_id") or entry.get("agent_type") for entry in all_entries if entry.get("agent_id") or entry.get("agent_type")}),
            "experiments": sorted({entry["experiment_id"] for entry in all_entries if entry.get("experiment_id")}),
            "scenario_kinds": sorted({entry["scenario_kind"] for entry in all_entries if entry.get("scenario_kind")}),
            "schemas": sorted({entry["schema"] for entry in all_entries if entry.get("schema")}),
            "structure_types": sorted({entry["structure_type"] for entry in all_entries if entry.get("structure_type")}),
        }
        return {"total": total, "offset": offset, "limit": limit, "items": items, "filters": filters}
