"""Trusted-checkpoint compiler for V-ExpeL experience cards.

Learning intakes happen only at trusted checkpoints. Persistent Scenario v2
emits warmup/arrival/horizon samples, so the horizon-final checkpoint —
captured after evaluation has materialized the run result — is the one
learnable signal: safety comes from the checkpoint's trusted safety facts and
the outcome verdict from the materialized run evaluation. Nothing is learned
from agent self-reports alone.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import hashlib
import json
import re
import threading

from src.persistent_scenarios.runtime.lifecycle import CheckpointReason

from .memory import MEMORY_SCHEMA, ExperienceRecord, MemoryCard, VExpeLMemory, card_id_for


_SQL_LITERAL_RE = re.compile(r"'(?:''|[^'])*'|\b\d+(?:\.\d+)?\b")


def _sanitize_text(value: object, forbidden: tuple[str, ...]) -> str:
    text = str(value).strip()
    for identifier in forbidden:
        if identifier:
            text = text.replace(identifier, "[internal-id]")
    return text


def _report_values(report: Mapping[str, object], section: str) -> tuple[str, ...]:
    raw = report.get(section, [])
    if raw is None:
        return ()
    if not isinstance(raw, (list, tuple)) or any(not isinstance(item, str) for item in raw):
        raise TypeError(f"V-ExpeL report section must be a list of strings: section={section!r}, value={raw!r}")
    return tuple(raw)


def _task_map(run) -> dict[str, Mapping[str, object]]:
    tasks: dict[str, Mapping[str, object]] = {}
    for change in run.mailbox_history:
        if not isinstance(change, Mapping):
            raise TypeError(f"V-ExpeL mailbox history entry must be a mapping: entry={change!r}")
        task = change.get("task")
        if not isinstance(task, Mapping):
            raise TypeError(f"V-ExpeL mailbox history task must be a mapping: entry={change!r}")
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError(f"V-ExpeL mailbox history task_id must be non-empty: task={task!r}")
        tasks[task_id] = task
    return tasks


def _select_task(run, checkpoint) -> Mapping[str, object]:
    tasks = _task_map(run)
    if checkpoint.event_id is not None:
        target_ids = [
            task_id
            for task_id, event_id in run.alert_truth_map.items()
            if event_id == checkpoint.event_id
        ]
        if target_ids:
            try:
                return tasks[target_ids[0]]
            except KeyError as exc:
                raise ValueError(
                    "V-ExpeL event target is absent from the public mailbox history: "
                    f"event_id={checkpoint.event_id!r}, target_id={target_ids[0]!r}"
                ) from exc
    if not tasks:
        raise ValueError(
            "V-ExpeL cannot compile a checkpoint without a mailbox task: "
            f"checkpoint_id={checkpoint.checkpoint_id!r}, run_id={run.run_id!r}"
        )
    visible_tasks = tuple(tasks.values())
    return max(
        visible_tasks,
        key=lambda task: float(task.get("created_at_monotonic", checkpoint.evaluated_at_monotonic)),
    )


def _forbidden_identifiers(run, checkpoint) -> tuple[str, ...]:
    values = [run.run_id, checkpoint.event_id, checkpoint.checkpoint_id]
    values.extend(event.event_id for event in run.spec.events)
    values.extend(event.capability_id for event in run.spec.events)
    return tuple(value for value in values if isinstance(value, str) and value)


def _task_cue(task: Mapping[str, object], forbidden: tuple[str, ...]) -> str:
    values = [task.get(key) for key in ("title", "description", "severity", "category") if task.get(key) is not None]
    symptoms = task.get("symptoms", [])
    if not isinstance(symptoms, list):
        raise TypeError(f"V-ExpeL task symptoms must be a list: task={task!r}")
    values.extend(symptoms)
    cue = " | ".join(_sanitize_text(value, forbidden) for value in values if str(value).strip())
    if not cue:
        raise ValueError(f"V-ExpeL cannot compile an empty task cue: task={task!r}")
    return cue


def _action_text(action: Mapping[str, object], forbidden: tuple[str, ...]) -> str | None:
    api = action.get("api")
    if not isinstance(api, str) or not api.strip():
        raise ValueError(f"V-ExpeL action api must be non-empty: action={action!r}")
    if api == "mailbox":
        return None
    args = action.get("args", {})
    if not isinstance(args, Mapping):
        raise TypeError(f"V-ExpeL action args must be a mapping: action={action!r}")
    if api == "execute_sql":
        sql = args.get("sql_query")
        if not isinstance(sql, str) or not sql.strip():
            raise ValueError(f"V-ExpeL execute_sql action lacks sql_query: action={action!r}")
        sanitized = _SQL_LITERAL_RE.sub("<value>", sql.strip())
        return _sanitize_text(f"execute_sql: {sanitized}", forbidden)
    if api == "manage_instance":
        instance_action = args.get("action")
        if not isinstance(instance_action, str) or not instance_action.strip():
            raise ValueError(f"V-ExpeL manage_instance action lacks action: action={instance_action!r}")
        return _sanitize_text(f"manage_instance: {instance_action.strip()}", forbidden)
    return _sanitize_text(api, forbidden)


def _attempted_actions(run, task: Mapping[str, object], checkpoint) -> tuple[str, ...]:
    start = float(task.get("created_at_monotonic", checkpoint.evaluated_at_monotonic))
    end = float(task.get("completed_at_monotonic", checkpoint.evaluated_at_monotonic) or checkpoint.evaluated_at_monotonic)
    end = min(end, checkpoint.evaluated_at_monotonic)
    actions: list[str] = []
    forbidden = _forbidden_identifiers(run, checkpoint)
    for action in run.action_history:
        if not isinstance(action, Mapping):
            raise TypeError(f"V-ExpeL action history entry must be a mapping: action={action!r}")
        action_start = action.get("timestamp_start_monotonic")
        if action_start is not None and float(action_start) < start:
            continue
        if action_start is not None and float(action_start) > end:
            continue
        text = _action_text(action, forbidden)
        if text is not None:
            actions.append(text)
    return tuple(actions)


def _trusted_status(checkpoint, run) -> tuple[bool, bool, bool]:
    """(available, passed, safe) at the horizon-final checkpoint."""
    safety = checkpoint.safety
    safe = safety.get("PersistentScenarioSafePass")
    if not isinstance(safe, bool):
        raise TypeError(
            "V-ExpeL requires the canonical trusted safety boolean: "
            f"checkpoint_id={checkpoint.checkpoint_id!r}, safety={safety!r}"
        )
    evaluation = run.evaluation
    if not isinstance(evaluation, Mapping):
        return False, False, safe
    outcome_pass = evaluation.get("OutcomePass")
    if not isinstance(outcome_pass, bool):
        return False, False, safe
    return True, outcome_pass, safe


class VExpeLCompiler:
    """Compiles public trajectories only after trusted evaluation checkpoints.

    Trusted checkpoints only *intake* experience records; consolidation into
    memory cards happens when the Agent writes its next report
    (see ``flush_pending``), so banked experience is auditable against the
    report that triggered it. Records still originate exclusively from
    trusted checkpoints.
    """

    def __init__(self, memory: VExpeLMemory) -> None:
        self.memory = memory
        self._lock = threading.RLock()
        self._observed_checkpoint_ids: set[str] = set()
        self._pending: list[tuple[ExperienceRecord, MemoryCard]] = []

    def observe(self, checkpoint, run) -> Mapping[str, object] | None:
        if checkpoint.reason is not CheckpointReason.HORIZON_FINAL:
            return None
        with self._lock:
            if checkpoint.checkpoint_id in self._observed_checkpoint_ids:
                raise ValueError(
                    "V-ExpeL trusted checkpoint was observed twice: "
                    f"checkpoint_id={checkpoint.checkpoint_id!r}"
                )
            available, passed, safe = _trusted_status(checkpoint, run)
            if not available:
                # Evaluation has not materialized yet: leave the checkpoint
                # unconsumed so a later trusted sample can still drive learning.
                return None
            self._observed_checkpoint_ids.add(checkpoint.checkpoint_id)
            task = _select_task(run, checkpoint)
            forbidden = _forbidden_identifiers(run, checkpoint)
            cue = _task_cue(task, forbidden)
            actions = _attempted_actions(run, task, checkpoint)
            report = task.get("report", {})
            if report is None:
                report = {}
            if not isinstance(report, Mapping):
                raise TypeError(f"V-ExpeL mailbox report must be a mapping: task={task!r}")
            outcome_report = report.get("outcome", {})
            if not isinstance(outcome_report, Mapping):
                raise TypeError(f"V-ExpeL report outcome must be a mapping: task={task!r}")
            changes = tuple(_sanitize_text(value, forbidden) for value in _report_values(outcome_report, "changes"))
            verification = tuple(_sanitize_text(value, forbidden) for value in _report_values(outcome_report, "verification"))
            report_summary = _sanitize_text(report.get("summary", "no public summary"), forbidden)
            kind = "procedure" if passed and safe else "anti_pattern"
            trusted_outcome = "pass" if passed else "fail"
            trusted_safety = "pass" if safe else "fail"
            record_seed = {
                "cue": cue,
                "kind": kind,
                "actions": actions,
                "changes": changes,
                "verification": verification,
                "trusted_outcome": trusted_outcome,
                "trusted_safety": trusted_safety,
                "summary": report_summary,
                "checkpoint_observation": checkpoint.checkpoint_id,
            }
            record_id = "experience-" + hashlib.sha256(
                json.dumps(record_seed, ensure_ascii=True, sort_keys=True, default=str).encode("utf-8")
            ).hexdigest()[:16]
            record = ExperienceRecord(
                record_id=record_id,
                cue=cue,
                kind=kind,
                attempted_actions=actions,
                reported_changes=changes,
                reported_verification=verification,
                trusted_outcome=trusted_outcome,
                trusted_safety=trusted_safety,
            )
            if kind == "procedure":
                lesson = (
                    f"For this symptom pattern, the trusted run completed safely. "
                    f"Reported result: {report_summary}. Re-check live evidence before applying the sequence."
                )
            else:
                lesson = (
                    f"Avoid treating the previous attempt as a repair for this symptom pattern. "
                    f"The trusted result was outcome={trusted_outcome}, safety={trusted_safety}; "
                    "diagnose current evidence before changing state."
                )
            candidate = MemoryCard(
                card_id=card_id_for(kind, cue),
                kind=kind,
                cue=cue,
                lesson=lesson,
                actions=actions,
                verification=verification,
            )
            # The episode is ending: no further report write will flush
            # pending evidence, so consolidate inline.
            event = self._consolidation_event(record, candidate, checkpoint.reason.value)
            run.learning_events.append(deepcopy(event))
            run.learning_memory = self.memory.snapshot()
            run.append_timeline(
                owner="learner",
                kind="v_expel_memory_consolidated",
                payload={
                    "record_id": record.record_id,
                    "card_id": candidate.card_id,
                    "card_kind": candidate.kind,
                    "checkpoint_reason": checkpoint.reason.value,
                },
            )
            return event

    def flush_pending(self) -> list[Mapping[str, object]]:
        """Consolidate every trusted record intake since the last flush.

        Called by the Agent after each mailbox report write; returns one
        learning event per consolidated record (empty when nothing is pending).
        """
        with self._lock:
            pending, self._pending = self._pending, []
        return [self._consolidation_event(record, candidate, "mailbox_report_write") for record, candidate in pending]

    def _consolidation_event(self, record: ExperienceRecord, candidate: MemoryCard, trigger: str) -> Mapping[str, object]:
        operations = self.memory.consolidate(record, candidate)
        return {
            "kind": "memory_consolidated",
            "schema": MEMORY_SCHEMA,
            "trigger": trigger,
            "record_id": record.record_id,
            "operations": list(operations),
            "card_count": len(self.memory.snapshot().get("cards", ())),
        }
