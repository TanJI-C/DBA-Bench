"""Exporter for the append-only ``persistent_scenario_trace_v2`` artifact."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from collections.abc import Mapping
from typing import Any
from src.trace_serialization import strict_json_dumps, strict_json_loads, validate_trace_document

from .encoding import jsonable
from .lifecycle import TRACE_SCHEMA


def _write_jsonl(path: Path, records: list[Any]) -> str:
    text = "".join(strict_json_dumps(jsonable(record)) + "\n" for record in records)
    for line_number, line in enumerate(text.splitlines(), 1):
        strict_json_loads(line, context=f"{path}:{line_number}")
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_persistent_scenario_trace(persistent_scenario_run, output_dir: str | os.PathLike[str]) -> str:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    filename = os.environ.get("AIOPS_TRACE_FILENAME", f"run_{persistent_scenario_run.run_id}__a001.json")
    if not filename.endswith(".json"):
        raise ValueError(f"Persistent Scenario trace filename must end with .json: filename={filename!r}")
    artifact_prefix = Path(filename).stem
    artifact_names = {
        "timeline": f"{artifact_prefix}__timeline.jsonl",
        "events": f"{artifact_prefix}__events.jsonl",
        "telemetry": f"{artifact_prefix}__telemetry.jsonl",
        "agent_sessions": f"{artifact_prefix}__agent_sessions.jsonl",
        "agent_conversation_raw": f"{artifact_prefix}__agent_conversation_raw.jsonl",
        "agent_conversation_phases": f"{artifact_prefix}__agent_conversation_phases.jsonl",
        "learning_events": f"{artifact_prefix}__learning_events.jsonl",
        "mailbox_history": f"{artifact_prefix}__mailbox_history.jsonl",
        "checkpoints": f"{artifact_prefix}__checkpoints.jsonl",
        "safety_checkpoints": f"{artifact_prefix}__safety_checkpoints.jsonl",
    }
    ledger_artifacts: dict[str, str] = {}
    artifacts = {
        "timeline": _write_jsonl(root / artifact_names["timeline"], persistent_scenario_run.canonical_timeline),
        "events": _write_jsonl(root / artifact_names["events"], persistent_scenario_run.events),
        "telemetry": _write_jsonl(root / artifact_names["telemetry"], persistent_scenario_run.trusted_telemetry),
        "agent_sessions": _write_jsonl(root / artifact_names["agent_sessions"], persistent_scenario_run.agent_sessions),
        "agent_conversation_raw": _write_jsonl(
            root / artifact_names["agent_conversation_raw"], persistent_scenario_run.agent_conversation_raw
        ),
        "agent_conversation_phases": _write_jsonl(
            root / artifact_names["agent_conversation_phases"], persistent_scenario_run.agent_conversation_phases
        ),
        "learning_events": _write_jsonl(root / artifact_names["learning_events"], persistent_scenario_run.learning_events),
        "mailbox_history": _write_jsonl(root / artifact_names["mailbox_history"], persistent_scenario_run.mailbox_history),
        "checkpoints": _write_jsonl(root / artifact_names["checkpoints"], persistent_scenario_run.checkpoints),
        "safety_checkpoints": _write_jsonl(
            root / artifact_names["safety_checkpoints"], persistent_scenario_run.safety_checkpoints
        ),
    }
    for ledger_id, ledger in persistent_scenario_run.ledgers.items():
        name = f"{artifact_prefix}__ledger_{ledger_id}.jsonl"
        ledger_artifacts[ledger_id] = name
        target = root / name
        target.write_bytes(ledger.path.read_bytes())
        artifacts[f"ledger:{ledger_id}"] = hashlib.sha256(target.read_bytes()).hexdigest()
    spec_json = strict_json_dumps(jsonable(persistent_scenario_run.spec), sort_keys=True)
    source_spec = persistent_scenario_run.source_spec or persistent_scenario_run.spec
    source_spec_json = strict_json_dumps(jsonable(source_spec), sort_keys=True)
    trace = {
        "$schema": TRACE_SCHEMA,
        "metadata": {
            "scenario_kind": "persistent",
            "scenario_id": persistent_scenario_run.spec.scenario_id,
            "citation_tag": persistent_scenario_run.spec.citation_tag,
            "family_id": persistent_scenario_run.spec.family_id,
            "system": persistent_scenario_run.spec.system.value,
            "run_id": persistent_scenario_run.run_id,
            "timestamp_start_wall": persistent_scenario_run.started_wall,
            "timestamp_end_wall": persistent_scenario_run.ended_wall,
            "timestamp_start_monotonic": persistent_scenario_run.started_monotonic,
            "timestamp_end_monotonic": persistent_scenario_run.ended_monotonic,
        },
        "run_mode": persistent_scenario_run.run_mode,
        "formal_eligible": persistent_scenario_run.formal_eligible,
        "persistent_scenario_spec": jsonable(persistent_scenario_run.spec),
        "source_persistent_scenario_spec": jsonable(source_spec),
        "environment_profile": jsonable(persistent_scenario_run.spec.environment),
        "persistent_scenario_spec_hash": hashlib.sha256(spec_json.encode("utf-8")).hexdigest(),
        "source_persistent_scenario_spec_hash": hashlib.sha256(source_spec_json.encode("utf-8")).hexdigest(),
        "calibration_evidence_id": persistent_scenario_run.spec.calibration.evidence_id,
        "calibration_evidence_hash": persistent_scenario_run.calibration_evidence_hash,
        "time_scale": persistent_scenario_run.time_scale,
        "early_stop_reason": persistent_scenario_run.early_stop_reason,
        "evaluation_mode": persistent_scenario_run.evaluation_mode,
        "canonical_timeline": jsonable(persistent_scenario_run.canonical_timeline),
        "alert_truth_map": dict(persistent_scenario_run.alert_truth_map),
        "agent_sessions": jsonable(persistent_scenario_run.agent_sessions),
        "agent_llm_usage": jsonable(persistent_scenario_run.agent_llm_usage),
        "agent_conversation_raw": jsonable(persistent_scenario_run.agent_conversation_raw),
        "agent_conversation_phases": jsonable(persistent_scenario_run.agent_conversation_phases),
        "learning_events": jsonable(persistent_scenario_run.learning_events),
        "learning_memory": jsonable(persistent_scenario_run.learning_memory),
        "mailbox": jsonable(persistent_scenario_run.mailbox_state),
        "mailbox_history": jsonable(persistent_scenario_run.mailbox_history),
        "agent_turns": jsonable(persistent_scenario_run.turn_history),
        "action_history": jsonable(persistent_scenario_run.action_history),
        "event_runs": jsonable(persistent_scenario_run.events),
        "checkpoints": jsonable(persistent_scenario_run.checkpoints),
        "safety_checkpoints": jsonable(persistent_scenario_run.safety_checkpoints),
        "business_ledgers": {
            ledger_id: {"artifact": ledger_artifacts[ledger_id], "path": str(ledger.path)}
            for ledger_id, ledger in persistent_scenario_run.ledgers.items()
        },
        "business_window": jsonable(persistent_scenario_run.business_window),
        "action_facts": jsonable(persistent_scenario_run.action_facts),
        "integrity_facts": jsonable(persistent_scenario_run.integrity_facts),
        "required_state_evidence": jsonable(persistent_scenario_run.required_state_evidence),
        "validity": jsonable(persistent_scenario_run.validity),
        "input_versions": jsonable(persistent_scenario_run.input_versions),
        "trusted_telemetry_summary": {"count": len(persistent_scenario_run.trusted_telemetry), "artifact": artifact_names["telemetry"]},
        "persistent_scenario_evaluation": jsonable(persistent_scenario_run.evaluation),
        "pre_cleanup_evaluation": jsonable(persistent_scenario_run.pre_cleanup_evaluation),
        "failure_certificate": jsonable(persistent_scenario_run.failure_certificate),
        "cleanup": jsonable(persistent_scenario_run.cleanup),
        "runtime_evidence": jsonable(persistent_scenario_run.runtime_evidence),
        "gate_result": jsonable(persistent_scenario_run.gate_result),
        "artifacts": artifacts,
    }
    path = root / filename
    serialized = strict_json_dumps(trace, indent=2) + "\n"
    parsed = strict_json_loads(serialized, context=str(path))
    validate_trace_document(parsed, schema=TRACE_SCHEMA, context=str(path))
    path.write_text(serialized, encoding="utf-8")
    return str(path)
