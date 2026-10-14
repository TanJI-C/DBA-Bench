"""An out-of-process agent drives the normal agent gateway over HTTP.

The benchmark process stays the only path to the environment: the remote agent
receives prompts and tool schemas, proposes one action at a time, and the
benchmark executes every action through ``EnvGateway`` so that evaluation sees
the full action history. Protocol (all bodies are JSON):

- ``POST {endpoint}/sessions`` -> ``{"id": ...}``; body carries run identity,
  prompts, tool schemas, tool help and ``max_turns``.
- ``GET {endpoint}/sessions/{id}/next`` -> ``{"action": null}`` on a long-poll
  timeout, or ``{"action": {"id", "api", "args", "thinking"?, "turn_id"?,
  "usage"?}}``.
- ``POST {endpoint}/sessions/{id}/result`` with ``{"action_id", "result",
  "turns_used", "max_turns"}`` after every executed tool action.
- ``POST {endpoint}/sessions/{id}/finish`` with ``{"evaluation", "error"}``
  once evaluation, cleanup and trace export are done.

Consecutive actions that share a ``turn_id`` count as one turn, mirroring the
parallel tool calls of one LLM response; an action without ``turn_id`` is a
turn of its own. After ``max_turns`` tool turns the next action must be
``submit``. ``usage`` is an optional list of provider token-usage records for
the model calls behind the action, used for efficiency and cost accounting.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List
from urllib.parse import urlparse
from urllib.request import ProxyHandler, Request, build_opener

from src.agents.agent import BaseAgent

LONG_POLL_TIMEOUT_SECONDS = 35
USAGE_TOKEN_FIELDS = (
    "input_tokens",
    "output_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
)


def validate_endpoint(endpoint: Any) -> str:
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise ValueError(f"remote agent endpoint must be a non-empty string, got {endpoint!r}")
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(
            f"remote agent endpoint must be an absolute http(s) URL, got {endpoint!r}"
        )
    return endpoint.rstrip("/")


def _usage_event(raw: Any, call_number: int) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError(f"remote agent usage record must be an object, got {raw!r}")
    for field in ("provider", "model"):
        if not isinstance(raw.get(field), str) or not raw[field]:
            raise ValueError(
                f"remote agent usage record needs a non-empty {field!r}: record={raw!r}"
            )
    event = {
        "call_id": f"remote-call-{call_number:06d}",
        "provider": raw["provider"],
        "model": raw["model"],
        "input_tokens": raw.get("input_tokens"),
        "output_tokens": raw.get("output_tokens"),
        "cached_input_tokens": raw.get("cached_input_tokens", 0),
        "cache_write_input_tokens": raw.get("cache_write_input_tokens", 0),
    }
    invalid = {
        key: event[key]
        for key in USAGE_TOKEN_FIELDS
        if not isinstance(event[key], int) or isinstance(event[key], bool) or event[key] < 0
    }
    if invalid:
        raise ValueError(
            f"remote agent usage record needs non-negative integer token counts: "
            f"invalid={invalid}, record={raw!r}"
        )
    return event


class RemoteAgent(BaseAgent):
    use_native_tools = True
    requires_tool_help = True

    def __init__(self, endpoint: str):
        super().__init__()
        self.endpoint = validate_endpoint(endpoint)
        self.session_id = None
        self.tools_schema: List[Dict[str, Any]] = []
        self.tool_help: Dict[str, Any] = {}
        self.system_prompt = ""
        self.user_prompt = ""
        self.turns_used = 0
        self._usage_events: List[Dict[str, Any]] = []
        self._http = build_opener(ProxyHandler({}))

    def set_tools(self, tools):
        self.tools_schema = tools

    def set_tool_help(self, tool_help):
        self.tool_help = tool_help

    def set_system_prompt(self, system_prompt):
        self.system_prompt = system_prompt

    def set_user_prompt(self, user_prompt):
        self.user_prompt = user_prompt

    def _request(self, path: str, body: Any = None) -> Dict[str, Any]:
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode()
        request = Request(
            self.endpoint + path, data=data, headers={"Content-Type": "application/json"}
        )
        with self._http.open(request, timeout=LONG_POLL_TIMEOUT_SECONDS + 5) as response:
            return json.load(response)

    def _record_usage(self, usage: Any) -> None:
        if usage is None:
            return
        if not isinstance(usage, list):
            raise ValueError(f"remote agent action usage must be a list, got {usage!r}")
        for raw in usage:
            event = _usage_event(raw, len(self._usage_events) + 1)
            self._usage_events.append(event)
            self.model_usage_history.append({
                "provider": event["provider"],
                "model": event["model"],
                "input_tokens": event["input_tokens"],
                "cache_input_tokens": event["cached_input_tokens"]
                + event["cache_write_input_tokens"],
                "output_tokens": event["output_tokens"],
            })

    def solve(self) -> Dict[str, Any]:
        session = self._request("/sessions", {
            "experiment_id": os.environ.get("AIOPS_EXPERIMENT_ID"),
            "agent_id": os.environ.get("AIOPS_AGENT_ID"),
            "run_id": os.environ["AIOPS_RUN_ID"],
            "scenario_id": os.environ["AIOPS_SCENARIO_ID"],
            "case_id": os.environ["AIOPS_CASE_ID"],
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "tools": self.tools_schema,
            "tool_help": self.tool_help,
            "max_turns": self.max_turns,
        })
        if not isinstance(session.get("id"), str) or not session["id"]:
            raise RuntimeError(f"Remote agent returned no session id: response={session!r}")
        self.session_id = session["id"]
        current_turn = None
        while True:
            action = self._request(f"/sessions/{self.session_id}/next")["action"]
            if action is None:  # Long-poll timeout, not an execution failure.
                continue
            if not isinstance(action.get("id"), str) or not isinstance(action.get("api"), str):
                raise RuntimeError(
                    f"Remote agent action needs string 'id' and 'api': action={action!r}"
                )
            api, args = action["api"], action.get("args") or {}
            self._record_usage(action.get("usage"))
            self.record_action(json.dumps(action, ensure_ascii=False), action)
            if api == "exit":
                raise RuntimeError(
                    f"Remote agent exited without submitting a diagnosis: session={self.session_id}"
                )
            if api == "submit":
                return args
            turn_id = action.get("turn_id")
            if turn_id is None or turn_id != current_turn:
                if self.turns_used >= self.max_turns:
                    raise RuntimeError(
                        f"Remote agent started a tool turn after max_turns={self.max_turns} "
                        f"without submitting: session={self.session_id}, api={api!r}"
                    )
                self.turns_used += 1
                current_turn = turn_id
            result = self.execute(
                api, args, thinking=action.get("thinking", ""), source="remote",
                action_id=action["id"],
            )
            self.action_history[-1]["result"] = result
            self._request(f"/sessions/{self.session_id}/result", {
                "action_id": action["id"],
                "result": result,
                "turns_used": self.turns_used,
                "max_turns": self.max_turns,
            })

    def on_run_finished(self, evaluation, error):
        if self.session_id is not None:
            self._request(
                f"/sessions/{self.session_id}/finish", {"evaluation": evaluation, "error": error}
            )

    def _export_prompts(self):
        return {"system": self.system_prompt, "user": self.user_prompt}

    def _export_llm_usage(self) -> List[Dict[str, Any]]:
        return [dict(event) for event in self._usage_events]
