"""Persistent mailbox Agent control surface for PersistentScenario-v2."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import contextmanager
from copy import deepcopy
import json
import threading

from src.scenarios.evaluation.protocol import StructuredReport

from src.persistent_scenarios.runtime.lifecycle import ActionClassification, ActionFact
from src.persistent_scenarios.runtime.mailbox import PersistentScenarioMailbox
from src.persistent_scenarios.runtime.state import PersistentScenarioRun


_AGENT_STATES = frozenset({"active", "idle", "woken"})


class PersistentScenarioAgentGateway:
    """The only interface an PersistentScenario Agent uses for mailbox and database work."""

    def __init__(self, environment: object, control: "PersistentScenarioAgentControl", session_id: str):
        self._environment = environment
        self._control = control
        self._session_id = session_id

    def get_tool_schemas(self):
        return self._environment.get_tool_schemas()

    def mailbox(
        self,
        operation: str,
        *,
        task_ids: list[str] | None = None,
        report: Mapping[str, object] | None = None,
        thinking: str = "",
        source: str = "",
    ) -> Mapping[str, object]:
        return self._control.mailbox(
            operation,
            task_ids=task_ids,
            report=report,
            thinking=thinking,
            source=source,
            session_id=self._session_id,
        )

    def record_agent_state(self, state: str) -> None:
        self._control.record_agent_state(state, session_id=self._session_id)

    def record_agent_conversation(
        self,
        raw_messages: list[Mapping[str, object]],
        phases: list[Mapping[str, object]],
    ) -> None:
        self._control.record_agent_conversation(
            raw_messages,
            phases,
            session_id=self._session_id,
        )

    def record_learning_event(self, event: Mapping[str, object]) -> None:
        self._control.record_learning_event(event, session_id=self._session_id)

    def record_learning_memory(self, snapshot: Mapping[str, object]) -> None:
        self._control.record_learning_memory(snapshot, session_id=self._session_id)

    def record_agent_tool_action(
        self,
        api: str,
        args: Mapping[str, object],
        result: Mapping[str, object],
        *,
        thinking: str = "",
    ) -> None:
        self._control.record_agent_tool_action(api, args, result, thinking=thinking, session_id=self._session_id)

    def execute(self, api: str, args: Mapping[str, object], *, thinking: str = "", source: str = "") -> object:
        return self._control.execute(api, args, thinking=thinking, source=source, session_id=self._session_id)


class PersistentScenarioAgentControl:
    """Owns one persistent session and bookkeeping for the shared mailbox."""

    def __init__(
        self,
        run: PersistentScenarioRun,
        environment: object,
        mailbox: PersistentScenarioMailbox,
        *,
        clock,
        activation_gate=None,
        action_classifier=None,
    ):
        self.run = run
        self.environment = environment
        self._mailbox = mailbox
        self.clock = clock
        self._lock = threading.RLock()
        self._session_id: str | None = None
        self._last_read_pending: frozenset[str] = frozenset()
        # Set while no event activation is in flight; agent-surface SQL waits
        # on it so a scripted repair cannot land between fault application and
        # the engine's arrival-facts snapshot.
        self._activation_gate = activation_gate
        # Backend-provided semantic classifier: PG SQL ->
        # action_class. Core owns the ActionFact type, the backend owns the
        # classification logic.
        self._action_classifier = action_classifier
        self._turn = 0

    _AGENT_BOUNDED_SQL_APIS = frozenset({"execute_sql"})
    _AGENT_SQL_STATEMENT_TIMEOUT = "60s"
    _AGENT_SQL_LOCK_TIMEOUT = "10s"

    @contextmanager
    def _agent_sql_bounds(self, api: str):
        """Bound blocking agent SQL like a real client timeout would.

        Only the Agent-facing action path is bounded: trusted injector and
        evaluator SQL keeps the unrestricted surface.
        """
        environment = self.environment
        setter = getattr(environment, "set_agent_sql_timeouts", None)
        if api not in self._AGENT_BOUNDED_SQL_APIS or setter is None:
            yield
            return
        setter(self._AGENT_SQL_STATEMENT_TIMEOUT, self._AGENT_SQL_LOCK_TIMEOUT)
        try:
            yield
        finally:
            resetter = getattr(environment, "reset_agent_sql_timeouts", None)
            if resetter is not None:
                resetter()

    def register_session(self, session_id: str) -> None:
        with self._lock:
            if not session_id.strip():
                raise ValueError(f"PersistentScenario mailbox session requires a non-empty session_id: session_id={session_id!r}")
            if self._session_id is not None:
                raise ValueError(
                    "PersistentScenario mailbox session already registered: "
                    f"existing_session_id={self._session_id!r}, new_session_id={session_id!r}"
                )
            self._session_id = session_id

    def _require_session(self, session_id: str) -> None:
        if not session_id.strip():
            raise ValueError("PersistentScenario mailbox session requires a non-empty session_id")
        if self._session_id is None:
            raise ValueError(f"PersistentScenario mailbox session is not initialized: session_id={session_id!r}")
        if session_id != self._session_id:
            raise ValueError(
                "PersistentScenario does not permit another mailbox session: "
                f"registered_session_id={self._session_id!r}, session_id={session_id!r}"
            )

    def _begin_action(
        self,
        api: str,
        args: Mapping[str, object],
        *,
        thinking: str,
        source: str,
        session_id: str,
        surface: str,
    ) -> dict[str, object]:
        with self._lock:
            self._require_session(session_id)
            self._turn += 1
            entry = {
                "turn": self._turn,
                "session_id": session_id,
                "api": api,
                "args": deepcopy(dict(args)),
                "owner": "agent",
                "surface": surface,
                "thinking": thinking,
                "source": source,
                "timestamp_start_monotonic": self.clock.monotonic(),
            }
            self.run.action_history.append(entry)
            return entry

    def _finish_action(self, entry: dict[str, object], result: object) -> None:
        with self._lock:
            entry["result"] = deepcopy(result)
            entry["timestamp_end_monotonic"] = self.clock.monotonic()
            self.run.turn_history.append(
                {
                    "turn_number": entry["turn"],
                    "session_id": entry["session_id"],
                    "surface": entry["surface"],
                    "actions": [{"api": entry["api"], "args": deepcopy(entry["args"])}],
                    "results": [{"api": entry["api"], "data": deepcopy(result)}],
                    "thinking": entry["thinking"],
                    "source": entry["source"],
                    "timestamp_start_monotonic": entry["timestamp_start_monotonic"],
                    "timestamp_end_monotonic": entry["timestamp_end_monotonic"],
                }
            )

    def _fail_action(self, entry: dict[str, object], error: BaseException) -> None:
        with self._lock:
            entry["error"] = repr(error)
            entry["timestamp_end_monotonic"] = self.clock.monotonic()
            self.run.turn_history.append(
                {
                    "turn_number": entry["turn"],
                    "session_id": entry["session_id"],
                    "surface": entry["surface"],
                    "actions": [{"api": entry["api"], "args": deepcopy(entry["args"])}],
                    "results": [{"api": entry["api"], "error": repr(error)}],
                    "thinking": entry["thinking"],
                    "source": entry["source"],
                    "timestamp_start_monotonic": entry["timestamp_start_monotonic"],
                    "timestamp_end_monotonic": entry["timestamp_end_monotonic"],
                }
            )

    def mailbox(
        self,
        operation: str,
        *,
        task_ids: list[str] | None = None,
        report: Mapping[str, object] | None = None,
        thinking: str = "",
        source: str = "",
        session_id: str,
    ) -> Mapping[str, object]:
        args: dict[str, object] = {"operation": operation}
        if task_ids is not None:
            args["task_ids"] = list(task_ids)
        if report is not None:
            args["report"] = deepcopy(dict(report))
        entry = self._begin_action(
            "mailbox",
            args,
            thinking=thinking,
            source=source,
            session_id=session_id,
            surface="control",
        )
        try:
            with self._lock:
                self._require_session(session_id)
                if not isinstance(operation, str) or not operation.strip():
                    raise ValueError(
                        "Mailbox operation must be a non-empty string: "
                        f"session_id={session_id!r}, operation={operation!r}"
                    )
                if operation not in {"read", "write", "wait"}:
                    raise ValueError(
                        "Unsupported mailbox operation: "
                        f"session_id={session_id!r}, operation={operation!r}, allowed=['read', 'wait', 'write']"
                    )
                if operation == "read":
                    if task_ids is not None or report is not None:
                        raise ValueError(
                            "Mailbox read does not accept task_ids or report: "
                            f"session_id={session_id!r}, task_ids={task_ids!r}, report_present={report is not None}"
                        )
                    status = self._mailbox.status()
                    self.run.append_timeline(
                        owner="agent",
                        kind="mailbox_read",
                        payload={
                            "session_id": session_id,
                            "revision": status["revision"],
                            "pending_task_ids": [item["task_id"] for item in status["pending"]],
                            "completed_task_ids": [item["task_id"] for item in status["completed"]],
                        },
                    )
                    result = status
                    self._last_read_pending = frozenset(
                        item["task_id"] for item in status["pending"]
                    )
                elif operation == "write":
                    if not isinstance(task_ids, list) or not task_ids:
                        raise ValueError(
                            f"Mailbox write requires a non-empty task_ids list: session_id={session_id!r}, task_ids={task_ids!r}"
                        )
                    if not all(isinstance(task_id, str) and task_id.strip() for task_id in task_ids):
                        raise TypeError(
                            f"Mailbox write requires non-empty string task IDs: session_id={session_id!r}, task_ids={task_ids!r}"
                        )
                    if report is None:
                        raise ValueError(
                            f"Mailbox write requires a report: session_id={session_id!r}, task_ids={task_ids!r}"
                        )
                    StructuredReport.from_mapping(report)
                    completed_at = self.clock.monotonic()
                    completed = self._mailbox.complete_many(task_ids, completed_at, report)
                    status = self._mailbox.status()
                    self.run.append_timeline(
                        owner="agent",
                        kind="mailbox_written",
                        payload={
                            "session_id": session_id,
                            "task_ids": [task.task_id for task in completed],
                            "mailbox_revision": status["revision"],
                        },
                    )
                    result = {
                        "completed_task_ids": [task.task_id for task in completed],
                        "mailbox": status,
                    }
                else:
                    if task_ids is not None or report is not None:
                        raise ValueError(
                            "Mailbox wait does not accept task_ids or report: "
                            f"session_id={session_id!r}, task_ids={task_ids!r}, report_present={report is not None}"
                        )
                    status = self._mailbox.status()
                    stale_pending = [
                        item["task_id"]
                        for item in status["pending"]
                        if item["task_id"] in self._last_read_pending
                    ]
                    if stale_pending:
                        # The guard only punishes work the session already saw
                        # and ignored; tasks published after the last read are a
                        # legitimate wake, so wait returns them immediately.
                        raise ValueError(
                            "Mailbox wait requires no pending tasks already delivered to the session: "
                            f"session_id={session_id!r}, pending_task_ids={stale_pending!r}"
                        )
                    after_revision = status["revision"]
                    self._record_agent_state_locked("idle", session_id)
                    self.run.append_timeline(
                        owner="agent",
                        kind="mailbox_wait_started",
                        payload={"session_id": session_id, "mailbox_revision": after_revision},
                    )

            if operation == "wait":
                revision = self._mailbox.wait_for_pending(after_revision)
                with self._lock:
                    self._require_session(session_id)
                    status = self._mailbox.status()
                    self._record_agent_state_locked("woken", session_id)
                    self.run.append_timeline(
                        owner="agent",
                        kind="mailbox_wait_completed",
                        payload={
                            "session_id": session_id,
                            "mailbox_revision": revision,
                            "pending_task_ids": [item["task_id"] for item in status["pending"]],
                        },
                    )
                    result = {"waited": True, "mailbox": status}
        except Exception as exc:
            self._fail_action(entry, exc)
            raise
        self._finish_action(entry, result)
        return result

    def _classify(self, api: str, args: Mapping[str, object], result: object) -> ActionClassification:
        if self._action_classifier is None:
            raise RuntimeError(
                "PersistentScenario action classifier is not configured: "
                "the backend must provide one"
            )
        classification = self._action_classifier(api, args, result)
        if not isinstance(classification, ActionClassification):
            raise TypeError(
                "PersistentScenario action classifier must return an ActionClassification: "
                f"api={api!r}, got={type(classification).__name__}"
            )
        return classification

    def _record_agent_state_locked(self, state: str, session_id: str) -> None:
        if state not in _AGENT_STATES:
            raise ValueError(
                f"Unsupported PersistentScenario Agent state: session_id={session_id!r}, state={state!r}, allowed={sorted(_AGENT_STATES)!r}"
            )
        records = getattr(self.run, "agent_sessions", None)
        if records is not None:
            matches = [record for record in records if record.get("session_id") == session_id]
            if len(matches) != 1:
                raise RuntimeError(
                    "PersistentScenario Agent state requires exactly one session record: "
                    f"session_id={session_id!r}, matching_records={len(matches)}"
                )
            matches[0]["state"] = state
        status = self._mailbox.status()
        self.run.append_timeline(
            owner="agent",
            kind="agent_mailbox_state",
            payload={
                "session_id": session_id,
                "state": state,
                "mailbox_revision": status["revision"],
                "pending_task_count": status["counts"]["pending"],
            },
        )

    def record_agent_state(self, state: str, *, session_id: str) -> None:
        with self._lock:
            self._require_session(session_id)
            self._record_agent_state_locked(state, session_id)

    def record_agent_conversation(
        self,
        raw_messages: list[Mapping[str, object]],
        phases: list[Mapping[str, object]],
        *,
        session_id: str,
    ) -> None:
        with self._lock:
            self._require_session(session_id)
            if not isinstance(raw_messages, list) or not isinstance(phases, list):
                raise TypeError(
                    "PersistentScenario Agent conversation snapshot must contain lists: "
                    f"session_id={session_id!r}, raw_type={type(raw_messages).__name__}, phases_type={type(phases).__name__}"
                )
            if isinstance(self.run, PersistentScenarioRun):
                snapshot_phases = []
                for phase in phases:
                    phase_copy = deepcopy(dict(phase))
                    phase_copy["session_id"] = session_id
                    snapshot_phases.append(phase_copy)
                self.run.append_agent_conversation(raw_messages, snapshot_phases)
            self.run.append_timeline(
                owner="agent",
                kind="agent_conversation_snapshot",
                payload={
                    "session_id": session_id,
                    "raw_message_count": len(raw_messages),
                    "phase_count": len(phases),
                },
            )

    def record_learning_event(self, event: Mapping[str, object], *, session_id: str) -> None:
        if not isinstance(event, Mapping):
            raise TypeError(f"PersistentScenario learning event must be a mapping: event={event!r}")
        with self._lock:
            self._require_session(session_id)
            if not isinstance(self.run, PersistentScenarioRun):
                raise TypeError(f"PersistentScenario learning requires PersistentScenarioRun: run={self.run!r}")
            recorded = deepcopy(dict(event))
            recorded["session_id"] = session_id
            self.run.learning_events.append(recorded)
            self.run.append_timeline(
                owner="agent",
                kind=str(recorded.get("kind") or "v_expel_memory_event"),
                payload={
                    "session_id": session_id,
                    "card_ids": list(recorded.get("card_ids", [])),
                    "match_count": recorded.get("match_count"),
                },
            )

    def record_learning_memory(self, snapshot: Mapping[str, object], *, session_id: str) -> None:
        if not isinstance(snapshot, Mapping):
            raise TypeError(f"PersistentScenario learning memory must be a mapping: snapshot={snapshot!r}")
        with self._lock:
            self._require_session(session_id)
            self.run.learning_memory = deepcopy(dict(snapshot))
            self.run.append_timeline(
                owner="agent",
                kind="v_expel_memory_updated",
                payload={
                    "session_id": session_id,
                    "card_count": len(snapshot.get("cards") or []),
                    "record_count": len(snapshot.get("records") or []),
                },
            )

    def record_agent_tool_action(
        self,
        api: str,
        args: Mapping[str, object],
        result: Mapping[str, object],
        *,
        thinking: str = "",
        session_id: str,
    ) -> None:
        """Record an agent-side tool action (e.g. the V-ExpeL memory tool) in the run history."""
        if not isinstance(result, Mapping):
            raise TypeError(f"PersistentScenario agent tool result must be a mapping: result={result!r}")
        with self.run.action_lock:
            entry = self._begin_action(api, args, thinking=thinking, source="agent-tool", session_id=session_id, surface="control")
            self._finish_action(entry, result)

    def execute(
        self,
        api: str,
        args: Mapping[str, object],
        *,
        thinking: str = "",
        source: str = "",
        session_id: str,
    ) -> object:
        with self._lock:
            self._require_session(session_id)
        if self._activation_gate is not None:
            self._activation_gate.wait()
        with self.run.action_lock, self._agent_sql_bounds(api):
            entry = self._begin_action(
                api,
                args,
                thinking=thinking,
                source=source,
                session_id=session_id,
                surface="environment",
            )
            payload = dict(args)
            try:
                raw = self.environment.execute_action(api, payload)
                result = json.loads(raw) if isinstance(raw, str) else raw
            except Exception as exc:
                self._fail_action(entry, exc)
                raise RuntimeError(
                    "PersistentScenario Agent environment action failed: "
                    f"session_id={session_id!r}, api={api!r}, args={payload!r}, error={exc!r}"
                ) from exc
            self._finish_action(entry, result)
            if not isinstance(self.run, PersistentScenarioRun):
                raise TypeError(f"PersistentScenario action facts require PersistentScenarioRun: run={self.run!r}")
            classification = self._classify(api, dict(payload), result)
            self.run.action_facts.append(ActionFact(
                sequence=len(self.run.action_history) - 1,
                at_monotonic=entry["timestamp_end_monotonic"],
                action_class=classification.action_class,
                objects=classification.objects,
                guc_name=classification.guc_name,
                guc_value=classification.guc_value,
                details=classification.details,
            ))
            with self._lock:
                self.run.append_timeline(
                    owner="agent",
                    kind="environment_action",
                    payload={"session_id": session_id, "api": api, "args": payload, "action_class": classification.action_class},
                )
            return result
