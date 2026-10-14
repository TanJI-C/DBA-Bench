"""Persistent mailbox Agent protocol for PersistentScenario-v2."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass

from src.protocols.report import STRUCTURED_REPORT_JSON_SCHEMA
from src.persistent_scenarios.runtime.ports import (
    PersistentScenarioAgentProtocolError,
    PersistentScenarioAgentProviderError,
)


PERSISTENT_SCENARIO_CONTROL_TOOL_SCHEMAS = (
    {
        "type": "function",
        "function": {
            "name": "mailbox",
            "description": (
                "Read the shared mailbox, record completed work with a structured report, or wait for new work. "
                "Use operation='read' to inspect pending and completed items, operation='write' to complete one or more "
                "task_ids with report, and operation='wait' only when no pending work remains. "
                "A report has exactly three sibling keys: diagnosis, outcome, and summary; outcome and summary are "
                "not inside diagnosis. Canonical shape: "
                "{\"diagnosis\":{\"conditions\":[]},\"outcome\":{\"changes\":[],\"verification\":[]},"
                "\"summary\":\"brief audit note\"}."
            ),
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "required": ["operation"],
                "properties": {
                    "operation": {"type": "string", "enum": ["read", "write", "wait"]},
                    "task_ids": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string"},
                        "description": "Required for write; the work items that this report covers.",
                    },
                    "report": STRUCTURED_REPORT_JSON_SCHEMA,
                },
            },
        },
    },
)


@dataclass(frozen=True, slots=True)
class PersistentScenarioAgentContext:
    scenario_id: str
    session_id: str
    gateway: object
    stop_signal: object

    def __post_init__(self) -> None:
        if not self.scenario_id.strip() or not self.session_id.strip():
            raise ValueError(
                f"PersistentScenario mailbox context requires non-empty identity: scenario_id={self.scenario_id!r}, session_id={self.session_id!r}"
            )


class PersistentScenarioAgent(ABC):
    def __init__(self) -> None:
        self.context: PersistentScenarioAgentContext | None = None

    def start(self, context: PersistentScenarioAgentContext) -> None:
        if self.context is not None:
            raise RuntimeError(f"{type(self).__name__} cannot start twice")
        self.context = context

    @abstractmethod
    def run_until_stop(self) -> Mapping[str, object]:
        raise NotImplementedError

    def _require_context(self) -> PersistentScenarioAgentContext:
        if self.context is None:
            raise RuntimeError(f"{type(self).__name__} requires start()")
        return self.context


class LLMPersistentScenarioAgent(PersistentScenarioAgent):
    """One LLM conversation that is repeatedly woken by the mailbox."""

    def __init__(
        self,
        turn_handler: Callable[..., Mapping[str, object]],
        max_turns: int = 30,
        *,
        mailbox_read_hook: Callable[["LLMPersistentScenarioAgent", PersistentScenarioAgentContext, object], None] | None = None,
        mailbox_write_hook: Callable[["LLMPersistentScenarioAgent", PersistentScenarioAgentContext, object], None] | None = None,
        extra_tool_schemas: tuple[Mapping[str, object], ...] = (),
    ):
        super().__init__()
        if max_turns < 1:
            raise ValueError(f"LLMPersistentScenarioAgent max_turns must be positive: max_turns={max_turns}")
        self.turn_handler = turn_handler
        self.max_turns = max_turns
        self.mailbox_read_hook = mailbox_read_hook
        self.mailbox_write_hook = mailbox_write_hook
        self.extra_tool_schemas = tuple(extra_tool_schemas)
        self.history: list[dict[str, object]] = []
        self.activation_count = 0
        self._conversation_snapshotter: Callable[[], Mapping[str, object]] | None = None
        self._conversation_result_feeder: Callable[..., None] | None = None

    @classmethod
    def from_llm_client(
        cls,
        client,
        max_turns: int = 30,
        *,
        mailbox_read_hook: Callable[["LLMPersistentScenarioAgent", PersistentScenarioAgentContext, object], None] | None = None,
        mailbox_write_hook: Callable[["LLMPersistentScenarioAgent", PersistentScenarioAgentContext, object], None] | None = None,
        extra_tool_schemas: tuple[Mapping[str, object], ...] = (),
        system_prompt_suffix: str = "",
    ) -> "LLMPersistentScenarioAgent":
        state = {"configured": False, "fed_history": 0, "activation_count": 0}

        def conversation_snapshot() -> Mapping[str, object]:
            if hasattr(client, "get_conversation_trace"):
                return client.get_conversation_trace()
            messages = [deepcopy(dict(message)) for message in client._conversation_history]
            return {
                "raw": messages,
                "phases": [{"phase_index": 0, "messages": deepcopy(messages), "compaction": None}],
            }

        def feed_result(result, *, api: str, tool_call_id: object) -> None:
            client._feed_tool_result(result, tool_call_id=tool_call_id, api=api)
            state["fed_history"] += 1

        def turn_handler(context, turn, history):
            if not state["configured"]:
                tools = context.gateway.get_tool_schemas()
                environment_tools = [
                    schema
                    for schema in tools
                    if schema.get("function", {}).get("name") not in {"submit", "exit"}
                ]
                client.set_tools(environment_tools + list(PERSISTENT_SCENARIO_CONTROL_TOOL_SCHEMAS) + list(agent.extra_tool_schemas))
                system_prompt = (
                    "You are the database operations Agent that continuously operates one database system for the entire long-running task. "
                    "There is exactly one persistent mailbox session and one continuing conversation; never create, request, "
                    "or assume another Agent session. The mailbox is the shared work document. At the start of every activation, "
                    "call mailbox with operation='read' and use its live pending and completed lists. If pending work exists, "
                    "use ordinary database tools to investigate and operate the system, then call mailbox with operation='write', "
                    "the task_ids you consider finished, and a report. The report itself has exactly three sibling keys: "
                    "diagnosis, outcome, and summary; outcome and summary must not be nested inside diagnosis. Use this "
                    "shape: {\"diagnosis\":{\"conditions\":[]},\"outcome\":{\"changes\":[],\"verification\":[]},"
                    "\"summary\":\"brief audit note\"}. Every report must contain diagnosis.conditions, "
                    "outcome.changes, outcome.verification, and summary; outcome.plan is optional. The report is an audit note, "
                    "not proof of recovery or a pass/fail result. When no pending work remains, call mailbox with operation='wait'. "
                    "That call suspends this same conversation until new work is appended or the task ends. Completed work remains "
                    "visible for continuity and audit. Do not invent hidden work or private implementation details. "
                    "Treat pg_terminate_backend as a high-impact operation: never terminate sessions in bulk using only datname, "
                    "state, xact_start, backend_xmin, age, or a broad application-name pattern. First verify the single blocker "
                    "from current evidence, then terminate only that one session using its exact PID or an exact application_name "
                    "equality. Preserve waiters, decoys, unrelated work, and work belonging to other ongoing work. Do not use "
                    "manage_instance restart or stop for a lock or transaction cleanup while PostgreSQL is healthy. Verify "
                    "the effect of every change and preserve unrelated work."
                )
                if system_prompt_suffix:
                    system_prompt += " " + system_prompt_suffix.strip()
                client.set_system_prompt(system_prompt)
                state["configured"] = True
            for item in history[state["fed_history"]:]:
                client._feed_tool_result(item["result"], tool_call_id=item.get("tool_call_id"), api=item["api"])
            state["fed_history"] = len(history)
            if turn == 1:
                prompt = (
                    "The system has started this persistent mailbox session. "
                    "Call mailbox with operation='read' now and continue only with the live document."
                    if state["activation_count"] == 0
                    else "The system has resumed this persistent mailbox session after new work arrived. "
                    "Call mailbox with operation='read' now and continue the live document."
                )
                prompt_message = {"role": "user", "content": prompt}
                if hasattr(client, "_append_conversation_message"):
                    client._append_conversation_message(prompt_message)
                else:
                    client._conversation_history.append(prompt_message)
                state["activation_count"] += 1
            snapshot = conversation_snapshot()
            context.gateway.record_agent_conversation(snapshot["raw"], snapshot["phases"])
            thinking, actions = client._next_llm_actions(max_empty_retries=2)
            return {"thinking": thinking, "actions": actions}

        agent = cls(
            turn_handler,
            max_turns=max_turns,
            mailbox_read_hook=mailbox_read_hook,
            mailbox_write_hook=mailbox_write_hook,
            extra_tool_schemas=extra_tool_schemas,
        )
        agent._conversation_snapshotter = conversation_snapshot
        agent._conversation_result_feeder = feed_result
        agent._llm_client = client
        return agent

    def llm_usage_events(self) -> list[dict[str, object]]:
        """Per-LLM-call provider token usage from the wrapped client, if any."""
        client = getattr(self, "_llm_client", None)
        if client is not None and hasattr(client, "llm_usage_events"):
            return client.llm_usage_events()
        return []

    def run_until_stop(self) -> Mapping[str, object]:
        context = self._require_context()
        while not context.stop_signal.is_set():
            self.activation_count += 1
            context.gateway.record_agent_state("active")
            self._run_activation()
        return {
            "status": "horizon_reached",
            "activations": self.activation_count,
            "turns": len(self.history),
        }

    def _run_activation(self) -> None:
        context = self._require_context()
        for turn in range(1, self.max_turns + 1):
            try:
                response = self.turn_handler(context, turn, tuple(self.history))
            except PersistentScenarioAgentProtocolError:
                raise
            except Exception as exc:
                raise PersistentScenarioAgentProviderError(
                    "PersistentScenario Agent provider failed while producing a mailbox turn: "
                    f"session_id={context.session_id!r}, turn={turn}, error={exc!r}"
                ) from exc
            if not isinstance(response, Mapping):
                raise PersistentScenarioAgentProtocolError(
                    f"PersistentScenario LLM turn must return a mapping: session_id={context.session_id!r}, turn={turn}, value={response!r}"
                )
            actions = response.get("actions")
            if not isinstance(actions, list) or not actions:
                raise PersistentScenarioAgentProtocolError(
                    f"PersistentScenario LLM turn must contain a non-empty actions list: session_id={context.session_id!r}, turn={turn}, response={response!r}"
                )
            thinking = str(response.get("thinking", ""))
            self._record_conversation(context)
            for action in actions:
                if self._dispatch(action, thinking):
                    return
        raise PersistentScenarioAgentProtocolError(
            f"LLMPersistentScenarioAgent reached max turns without observing an empty mailbox: session_id={context.session_id!r}, max_turns={self.max_turns}"
        )

    def _dispatch(self, action: object, thinking: str) -> bool:
        context = self._require_context()
        if not isinstance(action, Mapping):
            raise PersistentScenarioAgentProtocolError(f"PersistentScenario action must be a mapping: action={action!r}")
        api = action.get("api")
        args = action.get("args", {})
        if not isinstance(api, str) or not api.strip() or not isinstance(args, Mapping):
            raise PersistentScenarioAgentProtocolError(f"PersistentScenario action has invalid api/args: action={action!r}")
        result: object | None = None
        try:
            if api == "mailbox":
                operation = self._string_arg(args, "operation", api)
                result = context.gateway.mailbox(
                    operation,
                    task_ids=args.get("task_ids"),
                    report=args.get("report"),
                )
                terminal = operation == "wait"
            elif api == "memory":
                result = self._handle_memory_tool(args, context)
                context.gateway.record_agent_tool_action("memory", args, result, thinking=thinking)
                terminal = False
            else:
                result = context.gateway.execute(api, args, thinking=thinking, source="llm-persistent_scenario")
                terminal = False
        except (TypeError, ValueError, RuntimeError) as exc:
            # Control-contract rejections and environment action failures
            # (e.g. an unknown connection target, SQL errors) are recoverable
            # tool misuse: feed the rejection back as the tool result so the
            # model can re-format or pick another target, exactly like every
            # other tool error. Only structural garbage (checked above) stays
            # terminal.
            result = {
                "error": (
                    f"{api} rejected: {exc}. Follow the tool schema exactly "
                    "(structured objects, not JSON-encoded strings; use a valid "
                    "target) and retry."
                )
            }
            self.history.append(self._history_item(api, args, result, thinking, action))
            if self._conversation_result_feeder is not None:
                self._conversation_result_feeder(result, api=api, tool_call_id=action.get("id"))
            self._record_conversation(context)
            return False
        self.history.append(self._history_item(api, args, result, thinking, action))
        if self._conversation_result_feeder is not None:
            self._conversation_result_feeder(
                result,
                api=api,
                tool_call_id=action.get("id"),
            )
        if api == "mailbox" and args.get("operation") == "read" and self.mailbox_read_hook is not None:
            self.mailbox_read_hook(self, context, result)
        if api == "mailbox" and args.get("operation") == "write" and self.mailbox_write_hook is not None:
            self.mailbox_write_hook(self, context, result)
        self._record_conversation(context)
        return terminal

    def _handle_memory_tool(self, args: Mapping[str, object], context: PersistentScenarioAgentContext) -> Mapping[str, object]:
        raise PersistentScenarioAgentProtocolError(
            "PersistentScenario memory tool is not registered for this agent: api='memory' requires an agent that provides it"
        )

    def _record_conversation(self, context: PersistentScenarioAgentContext) -> None:
        if self._conversation_snapshotter is None:
            return
        snapshot = self._conversation_snapshotter()
        context.gateway.record_agent_conversation(snapshot["raw"], snapshot["phases"])

    @staticmethod
    def _history_item(
        api: str,
        args: Mapping[str, object],
        result: object,
        thinking: str,
        action: Mapping[str, object],
    ) -> dict[str, object]:
        return {
            "api": api,
            "args": dict(args),
            "result": {"status": "recorded"} if result is None else result,
            "thinking": thinking,
            "tool_call_id": action.get("id"),
        }

    @staticmethod
    def _string_arg(args: Mapping[str, object], name: str, api: str) -> str:
        value = args.get(name)
        if not isinstance(value, str) or not value.strip():
            # ValueError, not ProtocolError: a missing/malformed argument is
            # recoverable tool misuse; _dispatch feeds it back to the model.
            raise ValueError(f"PersistentScenario {api} requires a non-empty string {name}: args={dict(args)!r}")
        return value
