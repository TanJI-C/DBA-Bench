"""Export run trace data to JSON for visualization.

The agent owns its diagnostic path: each agent implements
``export_diagnostic_trace()`` (see src/agents/trace_protocol.py) and this
module assembles the run-level wrapper (metadata + evaluation) around it.
"""

import copy
import json
import os
import time
from typing import Any, Dict, Optional
from src.trace_serialization import strict_json_dumps, strict_json_loads, validate_trace_document


def export_run_trace(orchestrator, output_dir: str = "logs/traces/") -> str:
    """Export a completed run's trace data to a JSON file.

    Args:
        orchestrator: The Orchestrator instance (after run completes).
        output_dir: Directory to write the trace file.

    Returns:
        Path to the written JSON file.
    """
    agent = orchestrator.agent
    scenario = orchestrator.scenario
    case = orchestrator.case

    agent_trace = agent.export_diagnostic_trace()
    orchestrator_timeline = _extract_orchestrator_timeline(orchestrator)
    turns = _merge_turns_with_orchestrator_results(
        agent_trace.get("turns", []),
        orchestrator_timeline,
    )

    trace = {
        "$schema": "run_trace_v3",
        "metadata": _build_metadata(agent_trace, orchestrator, orchestrator_timeline),
        "prompts": agent_trace.get("prompts", {"system": "", "user": ""}),
        "tool_schema": agent_trace.get("tool_schema", []),
        "turns": turns,
        "diagnostic_structure": agent_trace.get("diagnostic_structure", {"type": "linear"}),
        "evaluation": _extract_evaluation(orchestrator),
        "phase_timings": copy.deepcopy(orchestrator.phase_timings),
        "fault_snapshot": copy.deepcopy(orchestrator.fault_snapshot),
        "finalization": _extract_finalization(orchestrator),
        "injections": _extract_injections(orchestrator),
        "conversation_history": agent_trace.get("conversation_history", []),
        "conversation_history_raw": agent_trace.get("conversation_history_raw", []),
        "conversation_phases": agent_trace.get("conversation_phases", []),
        "orchestrator_timeline": orchestrator_timeline,
        "internal_events": agent_trace.get("internal_events", []),
        "llm_usage": agent_trace.get("llm_usage", []),
        "llm_calls": agent_trace.get("llm_calls", []),
        "context_compaction": agent_trace.get("context_compaction", []),
        "conversation_history_readable": _readable_conversation(
            agent_trace.get("conversation_history", [])
        ),
    }

    # Legacy tree traces can still be rendered by older D-Bot visualization code.
    structure = trace["diagnostic_structure"]
    if structure.get("type") == "tree":
        tree = structure.get("tree", {})
        trace["dbot_extension"] = {
            "hypotheses": structure.get("hypotheses", []),
            "mcts_trees": [tree] if tree.get("nodes") else [],
        }

    output_dir = os.environ.get("AIOPS_TRACE_OUTPUT_DIR", output_dir)
    os.makedirs(output_dir, exist_ok=True)
    scenario_id = scenario.scenario_id
    case_id = case.case_id
    agent_name = agent_trace.get("agent_type", "unknown")
    timestamp = time.strftime("%Y-%m-%d_%H_%M_%S")
    filename = os.environ.get(
        "AIOPS_TRACE_FILENAME",
        f"run_{scenario_id}_{case_id}_{agent_name}_{timestamp}.json",
    )
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        serialized = strict_json_dumps(trace, indent=2) + "\n"
        parsed = strict_json_loads(serialized, context=filepath)
        validate_trace_document(parsed, schema="run_trace_v3", context=filepath)
        f.write(serialized)

    print(f">>> [Visualization] Trace exported to: {filepath}")
    return filepath


def _extract_orchestrator_timeline(orchestrator) -> list:
    """Return a JSON-serializable copy of the canonical run timeline."""
    timeline = getattr(orchestrator, "turn_history", [])
    if not timeline:
        return []
    return copy.deepcopy(timeline)


def _merge_turns_with_orchestrator_results(
    agent_turns: list,
    orchestrator_timeline: list,
) -> list:
    """Use the orchestrator timeline as the source of truth for action results.

    Agent turns keep their agent-specific fields such as thinking, graph context,
    and tree context. The orchestrator timeline supplies real environment
    results because it is the component that executes actions.
    """
    if not orchestrator_timeline:
        return copy.deepcopy(agent_turns)
    if not agent_turns:
        return [_turn_from_timeline_entry(entry) for entry in orchestrator_timeline]

    agent_actions = [
        action
        for turn in agent_turns
        for action in turn.get("actions", [])
        if action.get("api") not in {"submit", "exit"}
    ]
    timeline_actions = [
        action
        for entry in orchestrator_timeline
        for action in entry.get("actions", [])
    ]
    if agent_actions == timeline_actions:
        return _merge_linear_turn_results(agent_turns, orchestrator_timeline)

    by_turn_number = {
        entry.get("turn_number"): entry
        for entry in orchestrator_timeline
        if entry.get("turn_number") is not None
    }
    merged = copy.deepcopy(agent_turns)
    for index, turn in enumerate(merged):
        entry = by_turn_number.get(turn.get("turn_number"))
        if entry is None and index < len(orchestrator_timeline):
            entry = orchestrator_timeline[index]
        if entry is None:
            continue

        if entry.get("results"):
            turn["results"] = copy.deepcopy(entry["results"])
        if not turn.get("actions") and entry.get("actions"):
            turn["actions"] = copy.deepcopy(entry["actions"])
        turn.setdefault("raw_output", entry.get("raw_output"))
        if turn.get("timestamp") is None:
            turn["timestamp"] = entry.get("timestamp_start")

    if len(orchestrator_timeline) > len(merged):
        for entry in orchestrator_timeline[len(merged):]:
            merged.append(_turn_from_timeline_entry(entry))
    return merged


def _merge_linear_turn_results(agent_turns: list, orchestrator_timeline: list) -> list:
    executed = [
        (action, result, entry.get("timestamp_start"))
        for entry in orchestrator_timeline
        for action, result in zip(entry.get("actions", []), entry.get("results", []), strict=True)
    ]
    executed_index = 0
    merged = copy.deepcopy(agent_turns)
    for turn in merged:
        results = []
        timestamps = []
        for action in turn.get("actions", []):
            if action.get("api") in {"submit", "exit"}:
                results.append({"api": action["api"], "status": "submitted", "data": None})
                continue
            executed_action, result, timestamp = executed[executed_index]
            if action.get("action_id") and executed_action.get("action_id"):
                matches = action["action_id"] == executed_action["action_id"]
            else:
                matches = action == executed_action
            if not matches:
                raise RuntimeError(
                    f"Trace action identity mismatch at index={executed_index}: "
                    f"agent_action_id={action.get('action_id')!r}, "
                    f"orchestrator_action_id={executed_action.get('action_id')!r}"
                )
            results.append(copy.deepcopy(result))
            timestamps.append(timestamp)
            executed_index += 1
        turn["results"] = results
        if turn.get("timestamp") is None and timestamps:
            turn["timestamp"] = timestamps[0]
    if executed_index != len(executed):
        raise RuntimeError(
            f"Trace action sequence was not fully consumed: "
            f"consumed={executed_index}, executed={len(executed)}"
        )
    return merged


def _turn_from_timeline_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "turn_number": entry.get("turn_number"),
        "timestamp": entry.get("timestamp_start"),
        "thinking": _extract_thinking(entry.get("raw_output", "")),
        "actions": copy.deepcopy(entry.get("actions", [])),
        "results": copy.deepcopy(entry.get("results", [])),
        "raw_output": entry.get("raw_output", ""),
    }


def _extract_thinking(raw_output: Any) -> str:
    try:
        data = json.loads(raw_output) if isinstance(raw_output, str) else raw_output
    except (json.JSONDecodeError, TypeError):
        return str(raw_output) if raw_output is not None else ""
    if isinstance(data, dict):
        return data.get("thinking", "") or ""
    return str(raw_output) if raw_output is not None else ""


def _build_metadata(agent_trace: Dict[str, Any], orchestrator, orchestrator_timeline: Optional[list] = None) -> Dict[str, Any]:
    """Assemble run metadata without minting a second run identity."""
    turns = agent_trace.get("turns", [])
    timestamp_start = None
    if orchestrator_timeline:
        timestamp_start = orchestrator_timeline[0].get("timestamp_start")
    elif turns:
        timestamp_start = turns[0].get("timestamp")
    return {
        "experiment_id": os.environ.get("AIOPS_EXPERIMENT_ID"),
        "run_id": orchestrator.case_run.run_id,
        "agent_id": os.environ.get("AIOPS_AGENT_ID"),
        "repetition": _optional_int_env("AIOPS_REPETITION"),
        "seed": _optional_int_env("AIOPS_SEED"),
        "timestamp_start": timestamp_start,
        "timestamp_end": time.time(),
        "agent_type": agent_trace.get("agent_type", "unknown"),
        "agent_mode": agent_trace.get("mode"),
        "model": agent_trace.get("model"),
        "provider": agent_trace.get("provider"),
        "reasoning_effort": agent_trace.get("reasoning_effort"),
        "scenario_id": orchestrator.scenario.scenario_id,
        "system": orchestrator.scenario.system.value,
        "case_id": orchestrator.case.case_id,
        "case_title": orchestrator.case.title,
        "scenario_description": orchestrator.scenario.description,
        "background_workload_planned": orchestrator.case_run.background_workload_planned,
        "background_workload_observed": orchestrator.case_run.background_workload_observed,
        "metric_history": _history_audit_summary(orchestrator),
    }


def _optional_int_env(name: str) -> Optional[int]:
    value = os.environ.get(name)
    return int(value) if value is not None else None


def _history_audit_summary(orchestrator) -> Optional[Dict[str, Any]]:
    """Export only procedural-history metadata; metric arrays remain tool results."""
    audit = getattr(orchestrator.case_run, "metric_history", None)
    if not audit:
        return None
    allowed = {
        "schema_version",
        "generator_version",
        "seed",
        "history_sha256",
        "visible_start_ms",
        "visible_end_ms",
        "base_step_seconds",
        "overview_step_seconds",
        "catalog_sha256",
        "metric_count",
        "point_count",
        "source_record_counts",
        "block_count",
        "normal_capture_count",
        "normal_capture_origins",
        "normal_blocks",
        "normal_block_count",
        "normal_capture_ranges",
        "normal_source_capture_ids",
        "crossfade_count",
        "reverse_count",
        "missing_sample_count",
        "crossfade_sample_count",
        "plateau_sample_count",
        "return_to_normal_sample_count",
        "metric_only_sample_count",
        "valley_sample_count",
        "valley_window_count",
        "generated_sample_count",
        "real_sample_count",
        "target_window",
        "aftermath_window",
        "target_lightning_activity",
        "decoy_windows",
        "window_roles",
        "normal_capture_range",
        "normal_capture_count",
        "normal_capture_origins",
        "normal_capture_ranges",
        "normal_source_capture_ids",
        "target_capture_range",
        "aftermath_capture_range",
        "target_lightning_activity",
        "aftermath_strategy",
        "aftermath_capture_range",
        "aftermath_sample_count",
        "aftermath_window",
        "agent_handoff",
        "aftermath",
        "frozen_history_validation",
        "pre_mock_stage_timings",
    }
    unknown = sorted(set(audit) - allowed)
    if unknown:
        raise ValueError(
            "Metric history audit contains fields outside the trace summary contract: "
            f"fields={unknown!r}"
        )
    return copy.deepcopy({key: audit[key] for key in sorted(audit)})


def _extract_evaluation(orchestrator) -> Optional[Dict[str, Any]]:
    """Return the orchestrator's evaluation result if available."""
    return getattr(orchestrator, "_last_eval_result", None)


def _extract_finalization(orchestrator) -> Dict[str, Any]:
    failures = copy.deepcopy(getattr(orchestrator, "_finalization_failures", []))
    return {
        "status": "failed" if failures else "succeeded",
        "failures": failures,
    }


def _extract_injections(orchestrator) -> list[Dict[str, Any]]:
    return [
        {
            "injector": type(record.injector).__name__,
            "state": record.state.value,
            "evidence": copy.deepcopy(record.evidence),
        }
        for record in getattr(orchestrator.case_run, "injections", ())
    ]


def _readable_conversation(messages: Any) -> Any:
    """Add parsed JSON and line-oriented fields for easier manual trace review."""
    if not isinstance(messages, list):
        return messages
    readable = []
    for message in messages:
        if not isinstance(message, dict):
            readable.append(message)
            continue
        item = dict(message)
        content = item.get("content")
        if isinstance(content, str):
            parsed = _try_parse_json(content)
            if parsed is not None:
                item["content_json"] = _enhance_multiline(parsed)
                try:
                    item["content_pretty"] = json.dumps(
                        item["content_json"],
                        ensure_ascii=False,
                        indent=2,
                        default=str,
                    )
                except TypeError:
                    item["content_pretty"] = str(item["content_json"])
            if "\n" in content:
                item["content_lines"] = content.splitlines()
        elif isinstance(content, list):
            item["content_readable"] = _enhance_multiline(content)
        readable.append(item)
    return readable


def _try_parse_json(value: str) -> Optional[Any]:
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None


def _enhance_multiline(value: Any) -> Any:
    if isinstance(value, str):
        parsed = _try_parse_json(value)
        if parsed is not None:
            return _enhance_multiline(parsed)
        if "\n" in value:
            return {"text": value, "text_lines": value.splitlines()}
        return value
    if isinstance(value, list):
        return [_enhance_multiline(item) for item in value]
    if isinstance(value, dict):
        enhanced = {}
        for key, item in value.items():
            enhanced[key] = _enhance_multiline(item)
            if isinstance(item, str) and "\n" in item:
                enhanced[f"{key}_lines"] = item.splitlines()
        return enhanced
    return value
