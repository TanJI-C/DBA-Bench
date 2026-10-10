"""D-Bot baseline agent aligned with the open-source DB-GPT implementation.

DB-GPT's D-Bot is a multi-agent diagnosis pipeline:
role assignment -> expert diagnosis with tools -> roundtable review -> report.

In AiOpsBench's control-inverted model the agent drives itself: DbotAgent.solve()
runs the pipeline, and each expert's tree-of-thought diagnosis is encapsulated in an
ExpertSolver that owns its own search tree, candidates, and LLM client. Experts run
in parallel through a thread pool; their environment tool calls funnel through the
shared, thread-safe EnvGateway (self.execute).
"""

import json
import math
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Mapping, Optional

import numpy as np

from src.agents.agent import BaseAgent, LLMAgent, split_diagnostic_token_usage
from src.scenarios.evaluation.protocol import structured_submission
from src.agents.baselines.dbot.knowledge import DbotKnowledge
from src.agents.baselines.dbot.mcts import DiagnosisNode, DiagnosisTree, TreeSearchConfig
from src.agents.baselines.dbot.prompts import (
    DBOT_ANOMALY_DESCRIPTION_PROMPT,
    DBOT_ANOMALY_TITLE_PROMPT,
    DBOT_CITATION_MARK_PROMPT,
    DBOT_CITATION_MARK_REACT_FORMAT,
    DBOT_EXPERT_ACTION_PROMPT,
    DBOT_EXPERT_NATIVE_ACTION_PROMPT,
    DBOT_EXPERT_REFLECTION_PROMPT,
    DBOT_EXPERT_ROOT_CAUSE_PROMPT,
    DBOT_EXPERT_SOLUTION_PROMPT,
    DBOT_EXPERT_VOTE_PROMPT,
    DBOT_FINAL_TURN_PROMPT,
    DBOT_LABEL_PROMPT,
    DBOT_REMEDIATION_PLAN_PROMPT,
    DBOT_REMEDIATION_VERIFY_PROMPT,
    DBOT_REPORT_ROOT_CAUSE_PROMPT,
    DBOT_REPORT_SOLUTION_PROMPT,
    DBOT_ROLE_ASSIGNER_PROMPT,
    DBOT_ROUND_TABLE_PROMPT,
    DBOT_SYSTEM_PROMPT,
)
from src.agents.baselines.dbot.tools import (
    CITATION_MARK_TOOL_NAME,
    FINISH_TOOL_NAME,
    citation_mark_tool_schema,
    expert_tool_schemas,
    is_tidb_tool_surface,
    parse_json_input,
    react_tool_names,
    react_tool_prompt,
    split_react_reply,
    validate_react_tool,
)
from src.agents.baselines.dbot.types import DBOT_EXPERT_NAMES, DbotReport, DbotToolStep, ExpertDiagnosis


# DB-GPT metric mappings for PostgreSQL and TiDB.  TiDB has no PostgreSQL
# cache-hit metric; the active mapping is selected from the tool contract.
POSTGRES_METRIC_ACTIONS_BY_PREFIX = {
    "cpu": ["cpu", "active_connections", "qps"],
    "io": ["disk_io", "disk_usage", "cache_hit_ratio"],
    "memory": ["memory", "cache_hit_ratio", "active_connections"],
}
TIDB_METRIC_ACTIONS_BY_PREFIX = {
    "cpu": ["cpu", "active_connections", "qps"],
    "io": ["disk_io", "disk_usage"],
    "memory": ["memory", "active_connections"],
}
PRIMARY_METRIC_BY_PREFIX = {"cpu": "cpu", "io": "disk_io", "memory": "memory"}
WORKLOAD_ACTIONS = ["topsql"]
SLOW_QUERY_ACTIONS = ["slow_queries"]

# Bounded post-report remediation stage: the action tools the ChiefDBA planner
# may execute (intersected with the live tool surface) and the stage size caps.
REMEDIATION_ACTION_TOOLS = ("execute_sql", "manage_instance", "manage_cluster")
REMEDIATION_ACTION_LIMIT = 8
REMEDIATION_VERIFY_LIMIT = 5

# Provider relays mark 429/5xx responses as retryable; a report-stage failure
# otherwise discards a whole finished diagnosis. The OpenAI SDK family also
# surfaces transients as bare messages without an "Error code:" prefix
# (overload, connection drops, request timeouts), so match those too.
# Bounded retries, honoring the relay's retry_after hint.
PROVIDER_RETRY_LIMIT = 2
RETRYABLE_PROVIDER_ERROR = re.compile(
    r"Error code: (429|5\d\d)\b"
    r"|currently overloaded"
    r"|connection error"
    r"|request timed out"
    r"|an error occurred while processing"
    r"|upstream http/2"
    r"|upstream response stream",
    re.IGNORECASE,
)


def _retry_after_seconds(error_text: str) -> float:
    match = re.search(r"'retry_after': (\d+)", error_text)
    return min(float(match.group(1)), 120.0) if match else 30.0


def call_with_provider_retry(call, task: str):
    for attempt in range(PROVIDER_RETRY_LIMIT + 1):
        try:
            return call()
        except RuntimeError as exc:
            if attempt >= PROVIDER_RETRY_LIMIT or not RETRYABLE_PROVIDER_ERROR.search(str(exc)):
                raise
            delay = _retry_after_seconds(str(exc))
            print(
                f"[D-Bot] retryable provider error on {task} "
                f"(attempt {attempt + 1}), retrying in {delay:.0f}s"
            )
            time.sleep(delay)


@dataclass
class DbotParsedAction:
    thought: str
    tool_name: str
    tool_input: Dict[str, Any]
    raw: str
    total_input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


@dataclass
class DbotCandidate:
    simulation_index: int
    terminal_node_id: int
    trajectory: str
    finish: Dict[str, Any] = field(default_factory=dict)
    value: float = 0.0
    reflection: str = ""


class ExpertSolver:
    """One DB-GPT expert's tree-of-thought diagnosis.

    Owns its own search tree, candidate list, reflections, and a dedicated LLM
    client so multiple experts can run concurrently. Environment tool calls go
    through the shared EnvGateway passed to run().
    """

    def __init__(
        self,
        expert_name: str,
        alert: str,
        tool_schemas: List[Dict[str, Any]],
        knowledge: Optional[DbotKnowledge],
        use_native_tools: bool,
        search_config: TreeSearchConfig,
        max_turns: int,
        llm: LLMAgent,
        gateway,
        rng: np.random.Generator,
        history_window: Optional[tuple[str, str]] = None,
        history_window_seconds: int = 300,
        history_limit: int = 100,
        history_source: str = "component_log",
        history_sources: tuple[str, ...] = (),
    ):
        self.expert_name = expert_name
        self.alert = alert
        self._tool_schemas = list(tool_schemas)
        self.knowledge = knowledge
        self.use_native_tools = use_native_tools
        self.config = search_config
        self.max_turns = max_turns
        self.llm = llm
        self.gateway = gateway
        self.rng = rng
        self._is_tidb = is_tidb_tool_surface(self._tool_schemas)
        self._history_window = history_window
        self._history_window_seconds = history_window_seconds
        self._history_limit = history_limit
        self._history_source = history_source
        self._history_sources = history_sources
        self.source = f"dbot:{expert_name}"

        self.diagnosis = ExpertDiagnosis(expert_name=expert_name)
        self.conversation: List[Dict[str, Any]] = []

        self.tree: Optional[DiagnosisTree] = None
        self.current_node: Optional[DiagnosisNode] = None
        self.simulation_index = 0
        self.step_count = 0
        self.turn_count = 0
        self._turn_limit_reached = False
        self.candidates: List[DbotCandidate] = []
        self.selected_candidate: Optional[DbotCandidate] = None
        self.reflections: List[str] = []
        self.last_expansion_start_node: Optional[DiagnosisNode] = None
        self.simulation_started = False
        self.pending_vote_choices: Optional[List[int]] = None

    # --- entry point ---

    def run(self) -> ExpertDiagnosis:
        """Run the full DB-GPT tree-of-thought search then announce root cause + solution."""
        while self.simulation_index < self.config.simulation_count:
            self._start_simulation_if_needed()
            while True:
                if self.turn_count == self.max_turns:
                    parsed = self._next_db_gpt_action(final_turn=True)
                    self._turn_limit_reached = True
                elif self.step_count >= self.config.single_chain_max_step:
                    self._finish_candidate()
                    self._record_reflection(self._reflect())
                    self._vote()
                    break
                else:
                    parsed = self._pop_pending_native_tool()
                    if parsed is None:
                        parsed = self._next_db_gpt_action()
                        self.turn_count += 1
                if parsed.tool_name == FINISH_TOOL_NAME:
                    self._finish_candidate(parsed)
                    self._record_reflection(self._reflect())
                    self._vote()
                    break
                step = self._build_tool_step(
                    self.expert_name, parsed.tool_name, parsed.tool_input, parsed.thought
                )
                expanded_node = self._add_tool_call(parsed)
                if expanded_node.input_token is not None:
                    step.input_token = expanded_node.input_token
                    step.cache_input_token = expanded_node.cache_input_token
                    step.output_token = expanded_node.output_token
                result = self.gateway.execute(
                    step.aiops_action["api"], step.aiops_action["args"],
                    thinking=parsed.thought, source=self.source,
                )
                self._finalize_step_observation(step, result)
                self.diagnosis.steps.append(step)
                self._add_observation(step.db_gpt_observation)
            if self._turn_limit_reached:
                break
        self._finalize_search()
        self._complete_diagnosis()
        return self.diagnosis

    # --- LLM helpers (stateless calls on a dedicated client) ---

    def _call_text(self, prompt: str, task: str) -> str:
        content = call_with_provider_retry(
            lambda: self.llm.call_text(prompt, system_prompt=DBOT_SYSTEM_PROMPT), task,
        )
        if not content.strip():
            raise RuntimeError(f"D-Bot LLM returned empty content for task={task}")
        self.conversation.append({"role": "user", "content": prompt, "task": task})
        self.conversation.append({"role": "assistant", "content": content, "task": task})
        return content.strip()

    def _expert_tools(self) -> List[Dict[str, Any]]:
        return expert_tool_schemas(self._tool_schemas)

    def _next_db_gpt_action(self, final_turn: bool = False) -> DbotParsedAction:
        ctx = self._prompt_context()
        if self.use_native_tools:
            prompt = DBOT_EXPERT_NATIVE_ACTION_PROMPT.format(
                expert_name=ctx["expert_name"],
                alert_info=ctx["alert"],
                trajectory=ctx["trajectory"],
                former_candidates=ctx["former_candidates"],
                reflections=ctx["reflections"],
            )
        else:
            prompt = DBOT_EXPERT_ACTION_PROMPT.format(
                expert_name=ctx["expert_name"],
                alert_info=ctx["alert"],
                tool_names=ctx["tool_names"],
                tool_specs=ctx["tool_specs"],
                trajectory=ctx["trajectory"],
                former_candidates=ctx["former_candidates"],
                reflections=ctx["reflections"],
            )
        if final_turn:
            prompt = f"{prompt}\n\n{DBOT_FINAL_TURN_PROMPT}"

        if self.use_native_tools:
            parsed = self._next_native_tool_action(prompt)
        else:
            reply = self._call_text(prompt, task=f"mcts_action:{self.expert_name}")
            parsed = self._parse_react_action(reply)
            self._attach_latest_token_usage(parsed)

        if final_turn:
            queued_calls = len(getattr(self, "_pending_native_tool_calls", []))
            if parsed.tool_name != FINISH_TOOL_NAME or queued_calls:
                raise RuntimeError(
                    f"D-Bot expert final turn must call only finish: "
                    f"expert={self.expert_name!r}, returned_tool={parsed.tool_name!r}, "
                    f"additional_tool_calls={queued_calls}"
                )
        return parsed

    def _next_native_tool_action(self, prompt: str) -> DbotParsedAction:
        self.llm.set_tools(self._expert_tools())
        task = f"mcts_native_action:{self.expert_name}"

        def _invoke():
            response = self.llm._call_llm([
                {"role": "system", "content": DBOT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ])
            if "error" in response:
                raise RuntimeError(f"D-Bot native tool LLM call failed for expert={self.expert_name}: {response['error']}")
            return response

        response = call_with_provider_retry(_invoke, task)
        parsed, history_msg = self.llm._parse_llm_response_message(response)
        usage_event = self.llm.get_last_usage_event()
        self.conversation.append({"role": "user", "content": prompt, "task": f"mcts_action:{self.expert_name}"})
        self.conversation.append(history_msg)
        if not parsed["has_tool_calls"]:
            content = parsed.get("content") or parsed.get("thinking") or ""
            if not content.strip():
                raise RuntimeError(f"D-Bot native tool LLM returned no tool call for expert={self.expert_name}")
            parsed_action = self._parse_react_action(content)
            parsed_action.total_input_tokens = usage_event["input_tokens"]
            parsed_action.output_tokens = usage_event["output_tokens"]
            return parsed_action
        # ponytail: native-tool LLMs often return several parallel reads
        # in one round. The SolverAgent loop will execute each in sequence as its own
        # step, so we just package the first one here. Extra calls are pulled out by
        # `_pending_native_tool_calls` and consumed on subsequent iterations.
        self._pending_native_tool_calls = list(parsed["tool_calls"][1:])
        self._pending_native_total_input_tokens = usage_event["input_tokens"]
        tool_call = parsed["tool_calls"][0]
        tool_name = tool_call["api"]
        tool_input = tool_call.get("args") or {}
        validate_react_tool(tool_name, self._expert_tools())
        if tool_name == FINISH_TOOL_NAME:
            self._validate_finish_input(tool_input)
        raw = json.dumps({"thinking": parsed["thinking"], "tool_call": tool_call}, ensure_ascii=False, default=str)
        return DbotParsedAction(
            thought=parsed["thinking"],
            tool_name=tool_name,
            tool_input=tool_input,
            raw=raw,
            total_input_tokens=usage_event["input_tokens"],
            output_tokens=usage_event["output_tokens"],
        )

    def _pop_pending_native_tool(self) -> Optional[DbotParsedAction]:
        """Drain one queued native tool_call from the previous LLM round, if any."""
        if not getattr(self, "_pending_native_tool_calls", None):
            return None
        tool_call = self._pending_native_tool_calls.pop(0)
        tool_name = tool_call["api"]
        tool_input = tool_call.get("args") or {}
        try:
            validate_react_tool(tool_name, self._expert_tools())
        except ValueError:
            # Drop unknown tool silently rather than abort the chain.
            return self._pop_pending_native_tool()
        raw = json.dumps(
            {"thinking": "(queued native tool_call from prior round)", "tool_call": tool_call},
            ensure_ascii=False, default=str,
        )
        return DbotParsedAction(
            thought="(queued native tool_call from prior round)",
            tool_name=tool_name,
            tool_input=tool_input,
            raw=raw,
            total_input_tokens=self._pending_native_total_input_tokens,
            output_tokens=0,
        )

    def _attach_latest_token_usage(self, parsed: DbotParsedAction) -> None:
        usage_event = self.llm.get_last_usage_event()
        parsed.total_input_tokens = usage_event["input_tokens"]
        parsed.output_tokens = usage_event["output_tokens"]

    def _reflect(self) -> str:
        if not self.candidates:
            raise RuntimeError(f"Cannot reflect without a terminal candidate: expert={self.expert_name}")
        prompt = DBOT_EXPERT_REFLECTION_PROMPT.format(
            expert_name=self.expert_name,
            alert_info=self.alert,
            trajectory=self.candidates[-1].trajectory,
        )
        return self._call_text(prompt, task=f"mcts_reflect:{self.expert_name}")

    def _vote(self):
        ctx = self._vote_prompt_context()
        prompt = DBOT_EXPERT_VOTE_PROMPT.format(
            expert_name=ctx["expert_name"],
            alert_info=ctx["alert"],
            candidates=ctx["candidates"],
        )
        vote_reply = self._call_text(prompt, task=f"mcts_vote:{self.expert_name}")
        self._complete_vote_round(vote_reply)

    def _finalize_search(self):
        if not self.candidates:
            raise RuntimeError(f"D-Bot expert search ended without terminal candidates: expert={self.expert_name}")
        self._select_best_candidate_by_value()
        self.diagnosis.selected_trajectory = self._final_trajectory()
        self.diagnosis.search = self._search_to_dict()

    def _complete_diagnosis(self):
        diagnosis = self._prepare_expert_diagnosis()
        root_prompt = DBOT_EXPERT_ROOT_CAUSE_PROMPT.format(
            expert_name=self.expert_name,
            alert_info=self.alert,
            selected_trajectory=diagnosis.selected_trajectory,
        )
        root_cause = self._call_text(root_prompt, task=f"expert_root_cause:{self.expert_name}")
        solution_prompt = DBOT_EXPERT_SOLUTION_PROMPT.format(
            expert_name=self.expert_name,
            alert_info=self.alert,
            selected_trajectory=diagnosis.selected_trajectory,
            root_cause=root_cause,
        )
        solutions = self._call_text(solution_prompt, task=f"expert_solution:{self.expert_name}")
        if not root_cause.strip():
            raise RuntimeError(f"Empty expert root cause from {self.expert_name}")
        if not solutions.strip():
            raise RuntimeError(f"Empty expert solution from {self.expert_name}")
        diagnosis.root_cause = root_cause.strip()
        diagnosis.solutions = solutions.strip()

    # --- step builders ---

    def _build_tool_step(self, expert_name, tool_name, tool_input, thought) -> DbotToolStep:
        if tool_name == "whether_is_abnormal_metric":
            return self._build_initial_step(expert_name, thought=thought, tool_input=tool_input)
        if tool_name == "match_diagnose_knowledge":
            return self._build_knowledge_step(expert_name, tool_input, thought)
        if tool_name == "optimize_index_selection":
            return self._build_index_advisor_step(expert_name, tool_input, thought)
        return self._build_env_tool_step(expert_name, tool_name, tool_input, thought)

    def _build_initial_step(self, expert_name, thought=None, tool_input=None) -> DbotToolStep:
        normalized_input = {"metric_name": self._normalize_metric_name(
            (tool_input or {}).get("metric_name") or self._primary_metric_for_expert(expert_name)
        )}
        actions = [{"api": "whether_is_abnormal_metric", "args": normalized_input}]
        metric = normalized_input["metric_name"]
        if self._is_tidb and metric == "cache_hit_ratio":
            raise ValueError(
                "D-Bot TiDB metric profile does not support PostgreSQL cache_hit_ratio: "
                f"expert={expert_name!r}, input={tool_input!r}"
            )
        return DbotToolStep(
            expert_name=expert_name,
            tool_name="whether_is_abnormal_metric",
            tool_input=normalized_input,
            aiops_action=actions[0],
            aiops_actions=actions,
            thought=thought or (
                f"{expert_name} checks whether {metric} is abnormal, "
                "matching DB-GPT's whether_is_abnormal_metric tool."
            ),
        )

    def _build_knowledge_step(self, expert_name, tool_input, thought) -> DbotToolStep:
        metric_prefix = self._metric_prefix_for_expert(expert_name)
        metric_map = TIDB_METRIC_ACTIONS_BY_PREFIX if self._is_tidb else POSTGRES_METRIC_ACTIONS_BY_PREFIX
        system_metrics = list(metric_map[metric_prefix])
        normalized_input = {
            "metric_name": tool_input.get("metric_name", expert_name),
            "alert_metric": tool_input.get("alert_metric", ""),
            "metric_prefix": metric_prefix,
            "system_metrics": system_metrics,
            "workload_metrics": list(WORKLOAD_ACTIONS),
            "slow_query_metrics": list(SLOW_QUERY_ACTIONS),
            "matched_metrics": system_metrics + WORKLOAD_ACTIONS + SLOW_QUERY_ACTIONS,
        }
        actions = [{"api": "match_diagnose_knowledge", "args": {
            "metric_name": normalized_input["metric_name"],
            "alert_metric": normalized_input["alert_metric"],
        }}]
        return DbotToolStep(
            expert_name=expert_name,
            tool_name="match_diagnose_knowledge",
            tool_input=normalized_input,
            aiops_action=actions[0],
            aiops_actions=actions,
            thought=thought or (
                f"{expert_name} gathers DB-GPT-style {metric_prefix} metrics, workload "
                "queries, slow queries, and diagnosis knowledge."
            ),
        )

    def _build_index_advisor_step(self, expert_name, tool_input=None, thought=None) -> DbotToolStep:
        normalized_input = tool_input or {"start_time": "scenario_start", "end_time": "scenario_end"}
        actions = [{"api": "optimize_index_selection", "args": normalized_input}]
        return DbotToolStep(
            expert_name=expert_name,
            tool_name="optimize_index_selection",
            tool_input=normalized_input,
            aiops_action=actions[0],
            aiops_actions=actions,
            thought=thought or (
                f"{expert_name} collects workload, schema, and existing-index evidence "
                "needed by DB-GPT's optimize_index_selection tool."
            ),
        )

    def _build_env_tool_step(self, expert_name, tool_name, tool_input, thought) -> DbotToolStep:
        api = tool_name
        args = dict(tool_input or {})
        if self._is_tidb and api == "read_log":
            api, args = self._history_action("component_log", args)
        elif self._is_tidb and api == "execute_sql":
            sql = str(args.get("sql_query", "")).casefold()
            if "cluster_slow_query" in sql or "slow_query" in sql:
                api, args = self._history_action("slow_queries", args)
            elif "statements_summary" in sql or "pg_stat_statements" in sql:
                api, args = self._history_action("topsql", args)
        actions = [{"api": api, "args": args}]
        return DbotToolStep(
            expert_name=expert_name,
            tool_name=api,
            tool_input=args,
            aiops_action=actions[0],
            aiops_actions=actions,
            thought=thought,
        )

    def _history_action(self, source: str, tool_input: Mapping[str, Any]) -> tuple[str, Dict[str, Any]]:
        if self._history_window is None:
            raise RuntimeError(
                "D-Bot TiDB history query needs a metric/help response with a bounded UTC window: "
                f"source={source!r}, tool_input={dict(tool_input)!r}"
            )
        start, end = self._history_window
        if self._history_sources and source not in self._history_sources:
            source = self._history_source
        if self._history_sources and self._history_source not in self._history_sources:
            raise RuntimeError(
                "D-Bot TiDB history source selection is not enabled by the Case: "
                f"selected={self._history_source!r}, enabled={self._history_sources!r}"
            )
        return "query_history", {
            "source": source,
            "start_timestamp": start,
            "end_timestamp": end,
            "limit": self._history_limit,
        }

    # --- observation handling ---

    def _finalize_step_observation(self, step: DbotToolStep, result: Dict[str, Any]):
        if self._is_tidb and isinstance(result, dict):
            window = result.get("window")
            if isinstance(window, dict) and window.get("available_end"):
                end = datetime.strptime(
                    str(window["available_end"]), "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=timezone.utc)
                start = end - timedelta(seconds=self._history_window_seconds)
                if window.get("available_start"):
                    available_start = datetime.strptime(
                        str(window["available_start"]), "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=timezone.utc)
                    start = max(start, available_start)
                self._history_window = (
                    start.strftime("%Y-%m-%d %H:%M:%S"),
                    end.strftime("%Y-%m-%d %H:%M:%S"),
                )
        raw_results = result.get("results") if isinstance(result, dict) else None
        if step.tool_name == "whether_is_abnormal_metric":
            step.observation = result
            text = json.dumps(result, ensure_ascii=False, default=str)[:1200]
            metric = step.tool_input["metric_name"]
            if result.get("status") == "success":
                step.db_gpt_observation = f"The metric {metric} was checked for abnormality. AiOpsBench result: {text}"
            else:
                step.db_gpt_observation = f"Cannot decide whether the metric {metric} is abnormal. AiOpsBench result: {text}"
            step.top_metrics = self._extract_top_metrics([result])
            return
        if step.tool_name == "match_diagnose_knowledge":
            results = raw_results if isinstance(raw_results, list) else [result]
            step.observation = {"results": results}
            self._attach_matched_knowledge(step, results)
            step.knowledge_items = self._knowledge_items_from_step(step)
            step.top_metrics = self._extract_top_metrics(results)
            step.db_gpt_observation = self._format_knowledge_observation(step, results)
            return
        if step.tool_name == "optimize_index_selection":
            results = raw_results if isinstance(raw_results, list) else [result]
            step.observation = {"results": results}
            index_result = {"results": results}
            step.knowledge_items = self._index_knowledge_from_result(index_result)
            step.db_gpt_observation = self._format_index_advisor_result(index_result)
            return
        step.observation = result
        step.db_gpt_observation = (
            f"Environment tool {step.tool_name} returned for input "
            f"{json.dumps(step.tool_input, ensure_ascii=False, default=str)[:1200]}: "
            f"{json.dumps(result, ensure_ascii=False, default=str)[:1200]}"
        )
        step.top_metrics = self._extract_top_metrics([result])

    def _prepare_expert_diagnosis(self) -> ExpertDiagnosis:
        diagnosis = self.diagnosis
        if not diagnosis.steps:
            candidate = self.selected_candidate
            if candidate is None or not candidate.finish:
                raise RuntimeError(
                    f"D-Bot expert finished without tools or a terminal diagnosis: "
                    f"expert={self.expert_name}"
                )
            diagnosis.knowledge = [{
                "source": f"{self.expert_name}.finish",
                "desc": candidate.finish["knowledge"],
                "type": "model_claim_without_tool_evidence",
            }]
            diagnosis.top_metrics = []
            return diagnosis
        knowledge_items = []
        top_metrics = []
        for step in diagnosis.steps:
            obs_text = json.dumps(step.observation, ensure_ascii=False, default=str)
            knowledge_items.extend(step.knowledge_items)
            top_metrics.extend(step.top_metrics)
            knowledge_items.append({
                "source": f"{self.expert_name}.{step.tool_name}",
                "desc": (step.db_gpt_observation or obs_text)[:500],
                "type": step.tool_name,
            })
        diagnosis.knowledge = knowledge_items
        diagnosis.top_metrics = top_metrics
        return diagnosis

    # --- search (tree-of-thought) ---

    def _prompt_context(self) -> Dict[str, Any]:
        tool_schemas = self._expert_tools()
        return {
            "expert_name": self.expert_name,
            "alert": self.alert,
            "tool_names": ", ".join(react_tool_names(tool_schemas)),
            "tool_specs": react_tool_prompt(tool_schemas),
            "trajectory": self._current_trace() or "No previous tool trajectory in this simulation.",
            "former_candidates": self._format_candidates(),
            "reflections": "\n".join(self.reflections) or "No reflection yet.",
            "simulation_index": self.simulation_index + 1,
            "simulation_count": self.config.simulation_count,
        }

    def _current_trace(self) -> str:
        tree = self._require_tree()
        return tree.get_former_trace(tree.root, self._require_current_node())

    def _parse_react_action(self, reply: str) -> DbotParsedAction:
        context = f"expert={self.expert_name}"
        parts = split_react_reply(reply, context=context)
        tool_name = parts["action"]
        validate_react_tool(tool_name, self._expert_tools())
        tool_input = parse_json_input(parts["action_input"], context=context)
        if tool_name == FINISH_TOOL_NAME:
            self._validate_finish_input(tool_input)
        return DbotParsedAction(
            thought=parts["thought"],
            tool_name=tool_name,
            tool_input=tool_input,
            raw=reply,
        )

    def _add_tool_call(self, parsed: DbotParsedAction) -> DiagnosisNode:
        self._start_simulation_if_needed()
        current_node = self._require_current_node()
        tree = self._require_tree()
        thought_node = tree.add_child(current_node, "Thought", parsed.thought)
        action_node = tree.add_child(thought_node, "Action", parsed.tool_name)
        action_input_node = tree.add_child(
            action_node, "Action Input", json.dumps(parsed.tool_input, ensure_ascii=False),
        )
        if parsed.total_input_tokens is not None:
            token_usage = split_diagnostic_token_usage(
                parsed.total_input_tokens,
                parsed.output_tokens,
                current_node.total_input_tokens(),
            )
            action_input_node.input_token = token_usage["input_token"]
            action_input_node.cache_input_token = token_usage["cache_input_token"]
            action_input_node.output_token = token_usage["output_token"]
        self.current_node = action_input_node
        return action_input_node

    def _add_observation(self, observation: str):
        current_node = self._require_current_node()
        current_node.observation = observation
        self.step_count += 1

    def _finish_candidate(self, parsed: Optional[DbotParsedAction] = None) -> DbotCandidate:
        self._start_simulation_if_needed()
        if parsed is not None:
            self._add_tool_call(parsed)
        current_node = self._require_current_node()
        current_node.is_terminal = True
        trajectory = self._current_trace()
        candidate = DbotCandidate(
            simulation_index=self.simulation_index,
            terminal_node_id=current_node.id,
            trajectory=trajectory,
            finish=parsed.tool_input if parsed and parsed.tool_name == FINISH_TOOL_NAME else {},
        )
        self.candidates.append(candidate)
        self.simulation_index += 1
        self.simulation_started = False
        return candidate

    def _start_simulation_if_needed(self):
        if self.simulation_started:
            return
        if self.tree is None:
            self.tree = DiagnosisTree(alert=self.alert)
        self.current_node = self.tree.root
        self.step_count = 0
        self.last_expansion_start_node = self.tree.root
        self.simulation_started = True
        self._select_existing_prefix_or_expand()

    def _complete_vote_round(self, vote_reply: str):
        if not self.candidates:
            raise RuntimeError(f"No D-Bot candidates to vote for expert={self.expert_name}")
        choices = self.pending_vote_choices or self._vote_choice_indices()
        self.pending_vote_choices = None
        selected_position = self._parse_vote_position(vote_reply, len(choices))
        votes = [0] * len(choices)
        valid_votes = 0
        if selected_position is not None:
            votes[selected_position] += 1
            valid_votes = 1
        else:
            for candidate_idx in choices:
                self._mark_pruned(candidate_idx)
            return
        tree = self._require_tree()
        for position, candidate_idx in enumerate(choices):
            value = (votes[position] / valid_votes - 1 / len(choices)) / math.sqrt(valid_votes)
            candidate = self.candidates[candidate_idx]
            candidate.value += value
            node = tree.get_node(candidate.terminal_node_id)
            while node is not None:
                node.values.append(value)
                node.vote_counts.append(votes[position])
                node = node.parent
        self.selected_candidate = max(
            self.candidates,
            key=lambda candidate: tree.get_node(candidate.terminal_node_id).value_sum(),
        )

    def _select_best_candidate_by_value(self) -> DbotCandidate:
        if not self.candidates:
            raise RuntimeError(f"No D-Bot candidates to select for expert={self.expert_name}")
        tree = self._require_tree()
        self.selected_candidate = max(
            self.candidates,
            key=lambda candidate: tree.get_node(candidate.terminal_node_id).value_sum(),
        )
        return self.selected_candidate

    def _record_reflection(self, reflection: str):
        if not reflection.strip():
            raise ValueError(f"Empty D-Bot reflection for expert={self.expert_name}")
        self.reflections.append(reflection.strip())
        tree = self._require_tree()
        if self.candidates:
            self.candidates[-1].reflection = reflection.strip()
            terminal = tree.get_node(self.candidates[-1].terminal_node_id)
            terminal.reflection.append(reflection.strip())
        start_node = self._require_last_expansion_start_node()
        start_node.reflection.append(reflection.strip())
        if start_node is not tree.root:
            tree.root.reflection.append(reflection.strip())

    def _vote_prompt_context(self) -> Dict[str, str]:
        self.pending_vote_choices = self._vote_choice_indices()
        return {
            "expert_name": self.expert_name,
            "alert": self.alert,
            "candidates": self._format_vote_candidates(self.pending_vote_choices),
        }

    def _final_trajectory(self) -> str:
        tree = self._require_tree()
        if self.selected_candidate:
            return self.selected_candidate.trajectory
        if self.candidates:
            candidate = max(
                self.candidates,
                key=lambda item: tree.get_node(item.terminal_node_id).value_sum(),
            )
            return candidate.trajectory
        return self._current_trace()

    def _search_to_dict(self) -> Dict[str, Any]:
        tree = self._require_tree()
        return {
            "expert_name": self.expert_name,
            "simulation_index": self.simulation_index,
            "step_count": self.step_count,
            "turn_count": self.turn_count,
            "max_turns": self.max_turns,
            "candidates": [
                {
                    "simulation_index": candidate.simulation_index,
                    "terminal_node_id": candidate.terminal_node_id,
                    "trajectory": candidate.trajectory,
                    "finish": candidate.finish,
                    "value": candidate.value,
                    "reflection": candidate.reflection,
                }
                for candidate in self.candidates
            ],
            "selected_candidate": (
                self.selected_candidate.terminal_node_id if self.selected_candidate else None
            ),
            "terminal_node_ids": [candidate.terminal_node_id for candidate in self.candidates],
            "tree": tree.to_json_recursive(),
        }

    def _format_candidates(self) -> str:
        if not self.candidates:
            return "No former candidates."
        tree = self._require_tree()
        return "\n\n".join(
            f"<candidate_{idx}> value={tree.get_node(candidate.terminal_node_id).value_sum():.4f}\n"
            f"{self._candidate_summary(candidate)}"
            for idx, candidate in enumerate(self.candidates)
        )

    def _format_vote_candidates(self, choices: List[int]) -> str:
        tree = self._require_tree()
        lines = []
        for position, candidate_idx in enumerate(choices):
            candidate = self.candidates[candidate_idx]
            value = tree.get_node(candidate.terminal_node_id).value_sum()
            lines.append(f"<candidate_{position}> value={value:.4f}\n{self._candidate_summary(candidate)}")
            if candidate.reflection:
                lines.append(f"Reflection: {candidate.reflection}")
        return "\n\n".join(lines)

    def _candidate_summary(self, candidate: DbotCandidate) -> str:
        """Prompt-facing candidate view: the tool calls made plus the finish payload.

        Observations stay in the search tree and the full trajectory stays on the
        candidate; re-sending them on every later expansion is what made D-Bot
        prompts grow quadratically.
        """
        tree = self._require_tree()
        node = tree.get_node(candidate.terminal_node_id)
        actions = []
        while node is not tree.root:
            if node.node_type == "Action Input" and node.parent.description != FINISH_TOOL_NAME:
                actions.append(f"{node.parent.description}({node.description})")
            node = node.parent
        actions.reverse()
        lines = [f"Actions: {' -> '.join(actions) if actions else 'no tool calls'}"]
        if candidate.finish:
            lines.append(f"Diagnose: {candidate.finish['diagnose']}")
            lines.append(f"Solution: {json.dumps(candidate.finish['solution'], ensure_ascii=False)}")
            lines.append(f"Knowledge: {candidate.finish['knowledge']}")
        else:
            lines.append("The chain reached the step limit without calling finish.")
        return "\n".join(lines)

    def _select_existing_prefix_or_expand(self):
        tree = self._require_tree()
        current_node = self._require_current_node()
        while current_node.children:
            decision = self._make_decision_by_value(current_node)
            if decision == -1:
                self.last_expansion_start_node = current_node
                self.current_node = current_node
                return
            current_node = current_node.children[decision]
            while current_node.node_type != "Action Input" and current_node.children:
                current_node = current_node.children[0]
            if current_node.is_terminal:
                current_node = tree.root
                self.last_expansion_start_node = current_node
                self.current_node = current_node
                return
        self.last_expansion_start_node = current_node
        self.current_node = current_node

    def _make_decision_by_value(self, node: DiagnosisNode) -> int:
        weights = [child.compute_weight() for child in node.children] + [self.config.epsilon_new_node]
        probabilities = self._softmax(weights)
        draw = self.rng.multinomial(1, probabilities)
        for idx, selected in enumerate(draw[:-1]):
            if selected == 1:
                return idx
        if draw[-1] == 1:
            return -1
        raise RuntimeError(f"Cannot choose D-Bot UCT branch for expert={self.expert_name}")

    def _vote_choice_indices(self) -> List[int]:
        count = min(self.config.vote_candidates, len(self.candidates))
        if count <= 0:
            raise RuntimeError(f"D-Bot vote requested without candidates: expert={self.expert_name}")
        ordered = list(range(len(self.candidates)))
        self.rng.shuffle(ordered)
        choices = ordered[:count]
        choices.sort()
        return choices

    def _parse_vote_position(self, vote_reply: str, choice_count: int) -> Optional[int]:
        match = re.findall(r"[\"<]?(?:candidate|Candidate)[ _-]?(\d+)[\">]?", vote_reply)
        if not match:
            return None
        position = int(match[-1])
        if position < 0 or position >= choice_count:
            return None
        return position

    def _mark_pruned(self, candidate_idx: int):
        tree = self._require_tree()
        node = tree.get_node(self.candidates[candidate_idx].terminal_node_id)
        while node is not None:
            node.pruned = True
            node = node.parent

    @staticmethod
    def _softmax(values: List[float]) -> List[float]:
        max_value = max(values)
        exp_values = [math.exp(value - max_value) for value in values]
        total = sum(exp_values)
        return [value / total for value in exp_values]

    # --- knowledge / metrics helpers ---

    def _format_knowledge_observation(self, step: DbotToolStep, results: List[Dict[str, Any]]) -> str:
        metric_lines, slow_lines, workload_lines = [], [], []
        metric_prefix = step.tool_input["metric_prefix"]
        system_metrics = set(step.tool_input["system_metrics"])
        workload_metrics = set(step.tool_input["workload_metrics"])
        slow_query_metrics = set(step.tool_input["slow_query_metrics"])
        for item in results:
            metric = item.get("metric") or item.get("metric_type") or item.get("api")
            value = item.get("records", item.get("series", item.get("snapshot", item)))
            line = f"- {metric}: {json.dumps(value, ensure_ascii=False, default=str)[:900]}"
            if metric in slow_query_metrics:
                slow_lines.append(line)
            elif metric in workload_metrics:
                workload_lines.append(line)
            else:
                metric_lines.append(line)
        knowledge_lines = [
            f"- {item['source']}: {item['desc']}"
            for item in self._knowledge_items_from_step(step)
        ]
        sections = []
        if metric_lines:
            sections.append(
                f"The abnormal metrics are (metric_prefix={metric_prefix}):\n" + "\n".join(metric_lines)
            )
        if workload_lines:
            sections.append("The workload queries are:\n" + "\n".join(workload_lines))
        if slow_lines:
            sections.append("The slow queries that should be optimized are:\n" + "\n".join(slow_lines))
        if knowledge_lines:
            sections.append("The matched knowledge is:\n" + "\n".join(knowledge_lines))
        if not sections:
            raise RuntimeError(f"match_diagnose_knowledge collected no evidence: step={step.to_dict()!r}")
        return "\n\n".join(sections)

    def _attach_matched_knowledge(self, step: DbotToolStep, results: List[Dict[str, Any]]):
        if self.knowledge is None:
            return
        evidence_terms = []
        for item in results:
            metric = item.get("metric") or item.get("metric_type") or item.get("api")
            if metric:
                evidence_terms.append(str(metric))
            value = item.get("records", item.get("series", item.get("snapshot", item)))
            evidence_terms.append(json.dumps(value, ensure_ascii=False, default=str)[:1000])
        query = " ".join([
            step.expert_name,
            step.tool_input["metric_prefix"],
            step.tool_input.get("alert_metric", ""),
            *evidence_terms,
        ])
        snippets = self.knowledge.retrieve(query, expert_name=step.expert_name)
        step.tool_input["matched_knowledge"] = [
            {
                "source": snippet.source,
                "content": snippet.content,
                "metadata": snippet.metadata,
                "relevance": snippet.relevance,
            }
            for snippet in snippets
        ]

    def _knowledge_items_from_step(self, step: DbotToolStep) -> List[Dict[str, Any]]:
        items = []
        for item in step.tool_input.get("matched_knowledge", []):
            items.append({
                "source": item["source"],
                "desc": item["content"][:500],
                "type": "knowledge",
                "metadata": item["metadata"],
                "relevance": item["relevance"],
            })
        return items

    def _extract_top_metrics(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        top_metrics = []
        for item in results:
            metric = item.get("metric") or item.get("metric_type")
            if not metric:
                continue
            top_metrics.append({
                "metric": metric,
                "status": item.get("status", ""),
                "value": item.get(
                    "records", item.get("series", item.get("snapshot", item.get("result", item)))
                ),
            })
        return top_metrics

    def _format_index_advisor_result(self, result: Dict[str, Any]) -> str:
        results = result.get("results") if isinstance(result, dict) else None
        if not isinstance(results, list):
            results = [result]
        labels = [
            "Workload statistics from pg_stat_statements grouped by current database",
            "Database schema columns used by DB-GPT get_columns_from_db",
            "Column statistics and sampled-value proxies used by DB-GPT read_row_query",
            "Existing indexes",
            "hypopg availability for DB-GPT what-if index simulation",
        ]
        sections = []
        for idx, item in enumerate(results):
            label = labels[idx] if idx < len(labels) else f"Index advisor evidence {idx + 1}"
            sections.append(f"{label}:\n{json.dumps(item, ensure_ascii=False, default=str)[:1200]}")
        return (
            "DB-GPT optimize_index_selection adapter collected the workload, schema, "
            "column-statistics, existing-index, and hypopg-availability evidence used by "
            "the upstream Extend index-selection algorithm. The upstream DB-GPT runtime "
            "executes get_index_result(advisor, workload, connector, columns, "
            "column_sampled_values) with an in-process PostgreSQL connector; AiOpsBench "
            "keeps database access behind Orchestrator actions, so this adapter does not "
            "bypass the benchmark tool boundary or regex-generate index recommendations.\n\n"
            + "\n\n".join(sections)
        )

    def _index_knowledge_from_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{
            "source": "optimize_index_selection",
            "desc": self._format_index_advisor_result(result)[:500],
            "type": "index_advisor",
        }]

    @staticmethod
    def _normalize_metric_name(metric_name: str) -> str:
        name = str(metric_name).strip().lower()
        aliases = {
            "cpu_usage": "cpu", "memory_usage": "memory", "mem_usage": "memory",
            "io_usage": "disk_io", "io": "disk_io", "disk": "disk_usage",
            "index": "topsql", "query": "slow_queries", "workload": "topsql",
            "configuration": "active_connections", "recovery": "disk_usage",
        }
        return aliases.get(name, name)

    @staticmethod
    def _primary_metric_for_expert(expert_name: str) -> str:
        return PRIMARY_METRIC_BY_PREFIX[ExpertSolver._metric_prefix_for_expert(expert_name)]

    @staticmethod
    def _metric_prefix_for_expert(expert_name: str) -> str:
        agent_name = expert_name.lower()
        if "cpu" in agent_name or "workload" in agent_name or "index" in agent_name or "query" in agent_name:
            return "cpu"
        if "write" in agent_name or "io" in agent_name:
            return "io"
        if "mem" in agent_name:
            return "memory"
        return "cpu"

    # --- parsing helpers ---

    def _validate_finish_input(self, tool_input: Dict[str, Any]):
        missing = [name for name in ("diagnose", "solution") if name not in tool_input]
        if missing:
            raise ValueError(
                f"D-Bot finish action missing required fields: expert={self.expert_name}, "
                f"missing={missing!r}, input={tool_input!r}"
            )
        if not isinstance(tool_input["diagnose"], str):
            raise ValueError(f"D-Bot finish diagnose must be a string: input={tool_input!r}")
        if not isinstance(tool_input["solution"], list):
            raise ValueError(f"D-Bot finish solution must be a list: input={tool_input!r}")
        # knowledge 缺失不杀 run：部分模型常省略该字段，
        # 补空串让诊断照常进入 roundtable/report，不影响 DP/OP/SP 语义
        if "knowledge" not in tool_input or tool_input["knowledge"] is None:
            tool_input["knowledge"] = ""
        if not isinstance(tool_input["knowledge"], str):
            raise ValueError(f"D-Bot finish knowledge must be a string: input={tool_input!r}")

    def _require_tree(self) -> DiagnosisTree:
        if self.tree is None:
            raise RuntimeError(f"D-Bot search tree is not initialized: expert={self.expert_name}")
        return self.tree

    def _require_current_node(self) -> DiagnosisNode:
        if self.current_node is None:
            raise RuntimeError(f"D-Bot search current node is not initialized: expert={self.expert_name}")
        return self.current_node

    def _require_last_expansion_start_node(self) -> DiagnosisNode:
        if self.last_expansion_start_node is None:
            raise RuntimeError(f"D-Bot search expansion node is not initialized: expert={self.expert_name}")
        return self.last_expansion_start_node


class DbotAgent(BaseAgent):
    """DB-GPT code-first D-Bot adapter: parallel multi-expert diagnosis."""

    LABELS = (
        "highly concurrent commits or highly concurrent inserts",
        "highly concurrent updates",
        "highly deletes",
        "too many indexes",
        "missing indexes",
        "INSERT_LARGE_DATA",
        "IO_CONTENTION",
        "FETCH_LARGE_DATA",
        "CORRELATED SUBQUERY",
        "POOR JOIN PERFORMANCE",
        "CPU CONTENTION",
    )
    required_tool_profile = "db_gpt"
    # TiDBEnv 无 profile 概念：agent 以 is_tidb_tool_surface 按实际工具面自适配
    # （metric/log/SQL 路径均已分叉），仅在支持 profile 的环境（PGEnv）强制 db_gpt。
    tool_profile_optional = True

    def __init__(
        self,
        model: str,
        mode: str = "dbot_code",
        provider: Optional[str] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        config_path: str = "config/llm_config.json",
        use_native_tools: bool = True,
        max_hired_experts: int = 2,
        max_parallel_experts: int = 4,
        knowledge_paths: Optional[List[str]] = None,
        knowledge_top_k: int = 5,
        search_config: Optional[TreeSearchConfig] = None,
        seed: int = 0,
        enable_log: bool = False,
        log_dir: Optional[str] = None,
        **kwargs,
    ):
        if mode != "dbot_code":
            raise ValueError(
                f"Unsupported D-Bot mode for DB-GPT code-first implementation: {mode!r}. "
                "Use mode='dbot_code'."
            )
        if kwargs:
            unexpected = ", ".join(sorted(kwargs))
            raise TypeError(f"Unsupported DbotAgent parameter(s) for code-first DB-GPT mode: {unexpected}")
        super().__init__(enable_log=enable_log, log_dir=log_dir)
        self.mode = mode
        self.model = model
        self.provider = provider
        self.url = url
        self.api_key = api_key
        self.config_path = config_path
        self.use_native_tools = use_native_tools
        self.max_parallel_experts = max_parallel_experts
        self.seed = seed
        self._tools_schema: List[Dict[str, Any]] = []
        self._is_tidb = False
        self._history_source = "component_log"
        self._history_sources: tuple[str, ...] = ()
        self._history_window: Optional[tuple[str, str]] = None
        self._history_window_seconds = 300
        self._history_limit = 100

        self._llm: Optional[LLMAgent] = None
        self._llm_clients: List[LLMAgent] = []
        self._system_prompt = ""
        self._user_prompt = ""
        self._raw_alert = ""
        self._alert = ""
        self._report_title = ""
        self._reporter_initialized = False
        self._trace_entries: List[Dict[str, Any]] = []
        self._conversation: List[Dict[str, Any]] = []
        self._conversation_lock = threading.Lock()

        self.knowledge = DbotKnowledge(knowledge_paths, top_k=knowledge_top_k) if knowledge_paths else None
        expert_names = self.knowledge.expert_names() if self.knowledge else None
        self.max_hired_experts = max_hired_experts
        self.expert_names = list(expert_names or DBOT_EXPERT_NAMES)
        unsupported = sorted(set(self.expert_names) - set(DBOT_EXPERT_NAMES))
        if unsupported:
            raise ValueError(
                "D-Bot local knowledge expert names must match supported DB-GPT experts: "
                f"unsupported={unsupported!r}, supported={list(DBOT_EXPERT_NAMES)!r}"
            )
        self.selected_experts: List[str] = []
        self.diagnoses: Dict[str, ExpertDiagnosis] = {}
        self.reviews: List[Dict[str, str]] = []
        self.report = DbotReport()
        self._search_config = search_config or TreeSearchConfig()
        self._final_report: Optional[DbotReport] = None

    # --- LLM client factory ---

    def _new_llm(self) -> LLMAgent:
        llm = LLMAgent(
            url=self.url,
            api_key=self.api_key,
            system_prompt=DBOT_SYSTEM_PROMPT,
            model=self.model,
            config_path=self.config_path,
            use_native_tools=self.use_native_tools,
            provider=self.provider,
            enable_log=self.enable_log,
            log_dir=self.log_dir,
        )
        self._llm_clients.append(llm)
        return llm

    def _ensure_llm(self):
        if self._llm is None:
            # ponytail: fail fast when --model is missing from llm_config.json instead
            # of letting inner LLMAgent raise after env deploy + teardown (~7min wasted).
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                    if self.model not in cfg:
                        available = ", ".join(sorted(cfg.keys())) or "(none)"
                        raise RuntimeError(
                            f"D-Bot: model {self.model!r} is missing from {self.config_path}; "
                            f"available: {available}. Pass --model to a configured name."
                        )
                except json.JSONDecodeError as exc:
                    raise RuntimeError(
                        f"D-Bot: failed to parse {self.config_path}: {exc}"
                    ) from exc
            self._llm = self._new_llm()

    def set_tools(self, tools: List[Dict[str, Any]]):
        self._tools_schema = list(tools)
        self._is_tidb = is_tidb_tool_surface(tools)
        if self._is_tidb:
            function = next(
                tool.get("function", tool)
                for tool in tools
                if isinstance(tool, dict)
                and tool.get("function", tool).get("name") == "query_history"
            )
            source_values = (
                function.get("parameters", {})
                .get("properties", {})
                .get("source", {})
                .get("enum", [])
            )
            self._history_source = (
                "topsql" if "topsql" in source_values
                else "slow_queries" if "slow_queries" in source_values
                else "component_log"
            )
            self._history_sources = tuple(source_values)

    def set_system_prompt(self, system_prompt: str):
        self._system_prompt = system_prompt

    def set_user_prompt(self, user_prompt: str):
        self._user_prompt = user_prompt
        self._raw_alert = user_prompt
        self._alert = user_prompt
        self._conversation.append({"role": "user", "content": user_prompt})

    # --- main pipeline ---

    def solve(self) -> Dict[str, Any]:
        """Role assignment → parallel expert diagnosis → roundtable → final report."""
        self._initialize_reporter()
        if self._is_tidb:
            self._prime_tidb_history_window()
        self._assign_roles()
        self._run_experts_parallel()
        self._run_roundtable()
        return self._build_submission()

    def _initialize_reporter(self):
        if self._reporter_initialized:
            return
        self._alert = self._call_text_llm(
            DBOT_ANOMALY_DESCRIPTION_PROMPT.format(anomaly_str=self._raw_alert),
            task="report_anomaly_description",
        )
        self._report_title = self._call_text_llm(
            DBOT_ANOMALY_TITLE_PROMPT.format(anomaly_str=self._raw_alert),
            task="report_anomaly_title",
        )
        self._reporter_initialized = True

    def _assign_roles(self):
        prompt = DBOT_ROLE_ASSIGNER_PROMPT.format(
            alert_info=self._alert,
            expert_names=", ".join(self.expert_names),
        )
        reply = self._call_text_llm(prompt, task="role_assignment")
        self._select_experts(self._alert, reply)

    def _prime_tidb_history_window(self) -> None:
        result = self.execute(
            "help",
            {"tool_name": "query_history"},
            thinking="Read the TiDB history tool contract before selecting a bounded UTC window.",
            source="dbot:controller",
        )
        definition = result.get("definition", {}) if isinstance(result, dict) else {}
        runtime = definition.get("runtime", {}) if isinstance(definition, dict) else {}
        available_start = runtime.get("available_start")
        available_end = runtime.get("available_end")
        if not available_start or not available_end:
            raise RuntimeError(
                "D-Bot TiDB history contract did not provide available UTC range: "
                f"result={result!r}"
            )
        max_records = runtime.get("max_history_records_per_response")
        if not isinstance(max_records, int) or max_records <= 0:
            raise RuntimeError(
                "D-Bot TiDB history contract did not provide a positive max_history_records_per_response: "
                f"runtime={runtime!r}"
            )
        enabled_sources = runtime.get("enabled_sources")
        if not isinstance(enabled_sources, list) or not enabled_sources:
            raise RuntimeError(
                "D-Bot TiDB history contract did not provide enabled_sources: "
                f"runtime={runtime!r}"
            )
        self._history_sources = tuple(str(source) for source in enabled_sources)
        if self._history_source not in self._history_sources:
            self._history_source = next(
                source
                for source in ("topsql", "slow_queries", "component_log")
                if source in self._history_sources
            )
        self._history_window_seconds = 300
        self._history_limit = min(100, max_records)
        end = datetime.strptime(str(available_end), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        start = max(
            datetime.strptime(str(available_start), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
            end - timedelta(seconds=self._history_window_seconds),
        )
        self._history_window = (
            start.strftime("%Y-%m-%d %H:%M:%S"),
            end.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def _run_experts_parallel(self):
        """Run each selected expert's tree-of-thought diagnosis concurrently.

        Each ExpertSolver gets its own LLM client (LLM calls are stateless) and
        shares the thread-safe EnvGateway. The DB connection behind the gateway is
        serialized by the gateway lock, so the parallelism speeds up the LLM-bound
        search, not the DB access.
        """
        if self._gateway is None:
            raise RuntimeError("DbotAgent.solve 调用前未注入 EnvGateway。")
        expert_seeds = np.random.SeedSequence(self.seed).spawn(len(self.selected_experts))
        solvers = [
            ExpertSolver(
                expert_name=name,
                alert=self._alert,
                tool_schemas=self._tools_schema,
                knowledge=self.knowledge,
                use_native_tools=self.use_native_tools,
                search_config=self._search_config,
                max_turns=self.max_turns,
                llm=self._new_llm(),
                gateway=self._gateway,
                rng=np.random.default_rng(expert_seed),
                history_window=self._history_window,
                history_window_seconds=self._history_window_seconds,
                history_limit=self._history_limit,
                history_source=self._history_source,
                history_sources=self._history_sources,
            )
            for name, expert_seed in zip(self.selected_experts, expert_seeds)
        ]
        workers = max(1, min(self.max_parallel_experts, len(solvers)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            diagnoses = list(pool.map(self._run_one_expert, solvers))
        for diagnosis in diagnoses:
            self.diagnoses[diagnosis.expert_name] = diagnosis

    def _run_one_expert(self, solver: ExpertSolver) -> ExpertDiagnosis:
        diagnosis = solver.run()
        with self._conversation_lock:
            self._conversation.extend(solver.conversation)
            self._conversation.append({
                "role": "assistant",
                "content": json.dumps(diagnosis.to_dict(), ensure_ascii=False, default=str),
            })
        return diagnosis

    def _run_roundtable(self):
        all_context = self._all_diagnoses_context()
        for expert_name in self.selected_experts:
            previous_reviews = json.dumps(self.reviews, ensure_ascii=False, default=str)
            prompt = (
                DBOT_ROUND_TABLE_PROMPT
                + "\n\nDiagnosis results:\n" + all_context
                + "\n\nPrevious roundtable advice:\n" + previous_reviews
            )
            review = self._call_text_llm(prompt, task=f"roundtable:{expert_name}")
            self._add_review(expert_name, review)

    def _build_submission(self) -> Dict[str, Any]:
        report = self._build_report(self._alert)
        report.title = self._report_title
        report_context = self._report_context(report)
        report.root_cause = self._call_text_llm(
            DBOT_REPORT_ROOT_CAUSE_PROMPT.format(
                root_cause=report.root_cause, report_context=report_context,
            ),
            task="report_root_cause",
        )
        report.solutions = self._call_text_llm(
            DBOT_REPORT_SOLUTION_PROMPT.format(
                solutions=report.solutions, report_context=report_context,
            ),
            task="report_solution",
        )
        citation_markdown = self._format_citations_markdown(report.citations)
        if citation_markdown:
            report.citation_markdown = citation_markdown
            report.root_cause, report.solutions = self._mark_citations(
                report.root_cause, report.solutions, citation_markdown,
            )
        labels_reply = self._call_text_llm(
            DBOT_LABEL_PROMPT.format(root_cause=report.root_cause, labels=self.LABELS),
            task="report_labels",
        )
        report.labels = self._parse_labels(labels_reply)
        self._final_report = report
        self._trace_entries.append({
            "timestamp": time.time(),
            "output": json.dumps({"thinking": "ChiefDBA final report", "actions": []}, ensure_ascii=False),
            "actions": [],
        })
        remediation = self._run_remediation(report)
        if remediation is None:
            changes = [report.solutions]
            verification = [review["review"] for review in self.reviews]
        else:
            changes, verification = remediation
        return structured_submission(
            factor=report.root_cause,
            entity="database",
            evidence=[json.dumps(citation, ensure_ascii=False, default=str) for citation in report.citations],
            changes=changes,
            verification=verification,
            summary=report.title,
        )

    # --- bounded post-report remediation stage ---

    def _run_remediation(self, report: DbotReport) -> Optional[tuple[List[str], List[str]]]:
        """Execute the evidence-backed remediation after the report, then verify.

        The ChiefDBA LLM plans at most REMEDIATION_ACTION_LIMIT actions from the
        finalized report and the live tool surface; each action runs serially
        through the gateway, and a final LLM step proposes at most
        REMEDIATION_VERIFY_LIMIT read-only SQL checks. Returns the submission
        records, or None when no remediation action is planned.
        """
        action_names = self._remediation_action_names()
        if not action_names:
            return None
        plan = self._parse_remediation_plan(
            self._call_text_llm(
                DBOT_REMEDIATION_PLAN_PROMPT.format(
                    alert_info=self._alert,
                    root_cause=report.root_cause,
                    solutions=report.solutions,
                    tool_specs=react_tool_prompt(self._remediation_action_schemas()),
                    max_actions=REMEDIATION_ACTION_LIMIT,
                ),
                task="remediation_plan",
            ),
            action_names,
        )
        actions = plan["actions"]
        self._append_remediation_trace(plan["rationale"], actions)
        if not actions:
            return None
        action_records = []
        for action in actions:
            result = self.execute(
                action["api"], action["args"],
                thinking=f"Execute the remediation action planned by ChiefDBA: {plan['rationale']}",
                source="dbot:remediation",
            )
            action_records.append(
                f"{action['api']}: {self._remediation_args_text(action['args'])}"
                f" -> {self._remediation_result_text(result)}"
            )
            self._append_remediation_trace(
                "Execute the remediation action planned by ChiefDBA.", [action],
            )
        return action_records, self._verify_remediation(action_records)

    def _verify_remediation(self, action_records: List[str]) -> List[str]:
        reply = self._call_text_llm(
            DBOT_REMEDIATION_VERIFY_PROMPT.format(
                action_records="\n".join(action_records),
                max_queries=REMEDIATION_VERIFY_LIMIT,
            ),
            task="remediation_verify",
        )
        verification = self._parse_json_reply(reply, task="remediation_verify")
        queries = verification.get("queries")
        if not isinstance(queries, list):
            raise RuntimeError(
                f"D-Bot remediation verification queries must be a list: reply={reply!r}"
            )
        records = []
        for query in queries[:REMEDIATION_VERIFY_LIMIT]:
            if not isinstance(query, str) or not query.strip():
                raise RuntimeError(
                    f"D-Bot remediation verification query must be a non-empty string: query={query!r}"
                )
            result = self.execute(
                "execute_sql", {"sql_query": query},
                thinking="Verify the remediation result with read-only SQL.",
                source="dbot:remediation",
            )
            records.append(f"execute_sql: {query} -> {self._remediation_result_text(result)}")
            self._append_remediation_trace(
                "Verify the remediation result with read-only SQL.",
                [{"api": "execute_sql", "args": {"sql_query": query}}],
            )
        return records

    def _append_remediation_trace(self, thinking: str, actions: List[Dict[str, Any]]):
        self._trace_entries.append({
            "timestamp": time.time(),
            "output": json.dumps(
                {"thinking": thinking, "actions": actions},
                ensure_ascii=False, default=str,
            ),
            "actions": actions,
        })

    def _parse_remediation_plan(self, reply: str, action_names: List[str]) -> Dict[str, Any]:
        plan = self._parse_json_reply(reply, task="remediation_plan")
        actions = plan.get("actions")
        if not isinstance(actions, list):
            raise RuntimeError(
                f"D-Bot remediation plan actions must be a list: reply={reply!r}"
            )
        available = set(action_names)
        parsed_actions = []
        for action in actions[:REMEDIATION_ACTION_LIMIT]:
            api = action.get("api") if isinstance(action, dict) else None
            args = action.get("args") if isinstance(action, dict) else None
            if not isinstance(api, str) or api not in available:
                raise RuntimeError(
                    f"D-Bot remediation plan action api is not an available remediation tool: "
                    f"api={api!r}, available={sorted(available)!r}"
                )
            if not isinstance(args, dict):
                raise RuntimeError(
                    f"D-Bot remediation plan action args must be an object: api={api!r}, args={args!r}"
                )
            parsed_actions.append({"api": api, "args": args})
        return {"actions": parsed_actions, "rationale": str(plan.get("rationale", ""))}

    def _parse_json_reply(self, reply: str, task: str) -> Dict[str, Any]:
        text = LLMAgent._strip_markdown_codeblock(reply)
        extracted = LLMAgent._extract_json_object(text)
        if extracted is None:
            raise RuntimeError(f"D-Bot {task} reply contains no JSON object: reply={reply!r}")
        try:
            parsed = json.loads(extracted)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"D-Bot {task} reply is not valid JSON: reply={reply!r}") from exc
        if not isinstance(parsed, dict):
            raise RuntimeError(f"D-Bot {task} reply JSON must be an object: parsed={parsed!r}")
        return parsed

    def _remediation_action_names(self) -> List[str]:
        schema_names = set()
        for schema in self._tools_schema:
            function = schema.get("function", schema)
            if isinstance(function, dict) and function.get("name"):
                schema_names.add(function["name"])
        return [name for name in REMEDIATION_ACTION_TOOLS if name in schema_names]

    def _remediation_action_schemas(self) -> List[Dict[str, Any]]:
        names = set(self._remediation_action_names())
        return [
            schema for schema in self._tools_schema
            if isinstance(schema.get("function", schema), Mapping)
            and (schema.get("function", schema)).get("name") in names
        ]

    @staticmethod
    def _remediation_args_text(args: Dict[str, Any]) -> str:
        sql = args.get("sql_query")
        return str(sql)[:300] if isinstance(sql, str) and sql else json.dumps(args, ensure_ascii=False, default=str)[:300]

    @staticmethod
    def _remediation_result_text(result: Dict[str, Any]) -> str:
        return json.dumps(result, ensure_ascii=False, default=str)[:300]

    # --- LLM text helper (DbotAgent-level, sequential) ---

    def _call_text_llm(self, prompt: str, task: str) -> str:
        self._ensure_llm()
        content = call_with_provider_retry(
            lambda: self._llm.call_text(prompt, system_prompt=DBOT_SYSTEM_PROMPT), task,
        )
        if not content.strip():
            raise RuntimeError(
                f"D-Bot LLM returned empty content: task={task!r}, "
                f"prompt_chars={len(prompt)}"
            )
        self._conversation.append({"role": "user", "content": prompt, "task": task})
        self._conversation.append({"role": "assistant", "content": content, "task": task})
        return content.strip()

    def _mark_citations(self, root_cause: str, solutions: str, citations_markdown: str) -> tuple[str, str]:
        """Mark citation indices; the LLM submits both sections through the mark_citations tool.

        Like the expert-phase `finish` tool, this is an internal virtual tool: native
        mode uses SDK tool calling, text mode uses a ReAct Action/Action Input reply.
        """
        self._ensure_llm()
        task = "report_citation_mark"
        prompt = DBOT_CITATION_MARK_PROMPT.format(
            root_cause=root_cause, solutions=solutions, citations=citations_markdown,
        )
        schema = citation_mark_tool_schema()
        if self.use_native_tools:
            self._llm.set_tools([schema])

            def _invoke_citation_mark():
                response = self._llm._call_llm([
                    {"role": "system", "content": DBOT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ])
                if "error" in response:
                    raise RuntimeError(f"D-Bot {task} LLM call failed: {response['error']}")
                return response

            response = call_with_provider_retry(_invoke_citation_mark, task)
            parsed, history_msg = self._llm._parse_llm_response_message(response)
            self._conversation.append({"role": "user", "content": prompt, "task": task})
            self._conversation.append(history_msg)
            if len(parsed["tool_calls"]) != 1:
                raise RuntimeError(
                    f"D-Bot {task} must call {CITATION_MARK_TOOL_NAME!r} exactly once: "
                    f"returned_calls={[call['api'] for call in parsed['tool_calls']]!r}"
                )
            tool_name = parsed["tool_calls"][0]["api"]
            tool_input = parsed["tool_calls"][0].get("args") or {}
            # The shared parser falls back to {"raw": <args string>} when the SDK
            # arguments fail strict JSON parsing; citation payloads carry literal
            # newlines inside their markdown strings, so re-parse leniently.
            if isinstance(tool_input.get("raw"), str):
                tool_input = json.loads(tool_input["raw"], strict=False)
        else:
            reply = self._call_text_llm(prompt + DBOT_CITATION_MARK_REACT_FORMAT, task=task)
            parts = split_react_reply(reply, context=task)
            tool_name = parts["action"]
            tool_input = parse_json_input(parts["action_input"], context=task)
        validate_react_tool(tool_name, [schema])
        missing = [
            name for name in ("root_cause", "solutions")
            if not isinstance(tool_input.get(name), str) or not tool_input[name].strip()
        ]
        if missing:
            raise ValueError(
                f"D-Bot {task} tool input has missing or empty fields: "
                f"missing={missing!r}, input={tool_input!r}"
            )
        return tool_input["root_cause"].strip(), tool_input["solutions"].strip()

    # --- role assignment ---

    def _select_experts(self, alert: str, llm_reply: str = "") -> List[str]:
        selected = self._parse_selected_experts(llm_reply)
        if not selected:
            raise RuntimeError(
                f"D-Bot role assignment selected no experts: alert={alert!r}, reply={llm_reply!r}"
            )
        if len(selected) > self.max_hired_experts:
            selected = selected[: self.max_hired_experts]
        self.selected_experts = selected
        for expert in selected:
            self.diagnoses.setdefault(expert, ExpertDiagnosis(expert_name=expert))
        self.report.selected_experts = selected
        return selected

    def _parse_selected_experts(self, reply: str) -> List[str]:
        """Return expert names in the order the role assigner mentioned them.

        Trimming to max_hired_experts then keeps the assigner's highest-priority
        picks instead of favoring whoever comes first in the registry.
        """
        cleaned = (reply or "").replace("\n", " ").lower()
        matches = [
            (cleaned.find(name.lower()), name)
            for name in self.expert_names
            if name.lower() in cleaned
        ]
        return [name for _, name in sorted(matches)]

    # --- review / report assembly ---

    def _add_review(self, expert_name: str, review: str):
        if expert_name not in self.diagnoses:
            raise RuntimeError(f"Cannot add review for unknown expert={expert_name}")
        self.diagnoses[expert_name].review = review
        self.reviews.append({"expert": expert_name, "review": review})

    def _all_diagnoses_context(self) -> str:
        sections = []
        for expert_name in self.selected_experts:
            diagnosis = self.diagnoses[expert_name]
            sections.append(json.dumps({
                "expert_name": diagnosis.expert_name,
                "root_cause": diagnosis.root_cause[:2000],
                "solutions": diagnosis.solutions[:2000],
                "selected_trajectory": diagnosis.selected_trajectory[-1500:],
                "knowledge": [
                    {
                        "source": item.get("source", ""),
                        "desc": str(item.get("desc", ""))[:500],
                        "type": item.get("type", ""),
                    }
                    for item in diagnosis.knowledge[:12]
                ],
                "top_metrics": [
                    json.dumps(item, ensure_ascii=False, default=str)[:800]
                    for item in diagnosis.top_metrics[:6]
                ],
            }, ensure_ascii=False, default=str))
        return "\n\n".join(sections)

    def _build_report(self, alert: str) -> DbotReport:
        if not self.selected_experts:
            raise RuntimeError("Cannot build D-Bot report before role assignment")
        root_cause_sections, solution_sections, process_sections = [], [], []
        citations, top_metrics = [], []
        for expert_name in self.selected_experts:
            diagnosis = self.diagnoses[expert_name]
            root_cause_sections.append(f"The root causes identified by {expert_name}:\n{diagnosis.root_cause}")
            solution_sections.append(f"The solutions recommended by {expert_name}:\n{diagnosis.solutions}")
            process_sections.append(self._format_process(diagnosis))
            citations.extend(diagnosis.knowledge)
            top_metrics.extend(diagnosis.top_metrics)
        if self.reviews:
            review_text = "\n".join(f"{review['expert']}: {review['review']}" for review in self.reviews)
            root_cause_sections.append(f"Roundtable review:\n{review_text}")
        report = DbotReport(
            title=self._title_from_alert(alert),
            anomaly_description=alert,
            root_cause="\n\n".join(root_cause_sections),
            solutions="\n\n".join(solution_sections),
            labels=self._extract_labels("\n\n".join(root_cause_sections)),
            diagnosis_process="\n\n".join(process_sections),
            citations=citations,
            citation_markdown=self._format_citations_markdown(citations),
            selected_experts=list(self.selected_experts),
            top_metrics=top_metrics,
            roundtable_reviews=list(self.reviews),
        )
        self.report = report
        return report

    @staticmethod
    def _format_process(diagnosis: ExpertDiagnosis) -> str:
        lines = [f"The diagnosis process of {diagnosis.expert_name}:"]
        for idx, step in enumerate(diagnosis.steps, 1):
            actions = step.aiops_actions or [step.aiops_action]
            lines.append(
                f"{idx}. Thought: {step.thought}\n"
                f"   DB-GPT Action: {step.tool_name}\n"
                f"   DB-GPT Action Input: {json.dumps(step.tool_input, ensure_ascii=False)}\n"
                f"   AiOpsBench Actions: {json.dumps(actions, ensure_ascii=False, default=str)}\n"
                f"   Observation: {(step.db_gpt_observation or json.dumps(step.observation, ensure_ascii=False, default=str))[:700]}"
            )
        if diagnosis.review:
            lines.append(f"Roundtable review: {diagnosis.review}")
        return "\n".join(lines)

    def _format_citations_markdown(self, citations: List[Dict[str, Any]]) -> str:
        lines = []
        for idx, citation in enumerate(citations, 1):
            source = citation.get("source", "")
            desc = citation.get("desc", "")
            if desc:
                lines.append(f"[{idx}] {source}. {desc}")
        return "\n".join(lines)

    def _extract_labels(self, text: str) -> List[str]:
        lowered = text.lower()
        labels = []
        for label in self.LABELS:
            if label.lower() in lowered:
                labels.append(label)
        if "cpu" in lowered and "CPU CONTENTION" not in labels:
            labels.append("CPU CONTENTION")
        if "io" in lowered and "IO_CONTENTION" not in labels:
            labels.append("IO_CONTENTION")
        if "index" in lowered and "missing indexes" not in labels:
            labels.append("missing indexes")
        return labels

    def _parse_labels(self, reply: str) -> List[str]:
        labels = []
        lowered = reply.lower()
        for label in self.LABELS:
            if label.lower() in lowered:
                labels.append(label)
        return labels

    def _report_context(self, report: DbotReport) -> str:
        return json.dumps({
            "roundtable_reviews": report.roundtable_reviews,
            "citations": [
                {
                    "source": item.get("source", ""),
                    "desc": str(item.get("desc", ""))[:500],
                    "type": item.get("type", ""),
                }
                for item in report.citations[:20]
            ],
            "top_metrics": [
                json.dumps(item, ensure_ascii=False, default=str)[:800]
                for item in report.top_metrics[:8]
            ],
        }, ensure_ascii=False, default=str)

    def _title_from_alert(self, alert: str) -> str:
        words = re.findall(r"[A-Za-z0-9_]+", alert or "")
        if not words:
            return "Database Anomaly Diagnosis Report"
        return f"Analysis Report of {' '.join(words[:10])}"

    # --- 诊断路径导出（可视化协议） ---

    def _export_prompts(self) -> Dict[str, str]:
        return {"system": self._system_prompt or DBOT_SYSTEM_PROMPT, "user": self._user_prompt or ""}

    def _export_turns(self) -> List[Dict[str, Any]]:
        turns = []
        for idx, entry in enumerate(self._trace_entries, 1):
            data = json.loads(entry["output"])
            turns.append({
                "turn_number": idx,
                "timestamp": entry["timestamp"],
                "thinking": data.get("thinking", ""),
                "actions": [
                    {"api": action.get("api", ""), "args": action.get("args", {})}
                    for action in entry.get("actions", [])
                ],
                "results": [
                    {"api": action.get("api", ""), "status": "executed", "data": None}
                    for action in entry.get("actions", [])
                ],
            })
        return turns

    def _export_structure(self) -> Dict[str, Any]:
        return {
            "type": "db_gpt_multiagent",
            "selected_experts": list(self.selected_experts),
            "expert_diagnoses": [
                self.diagnoses[name].to_dict()
                for name in self.selected_experts
                if name in self.diagnoses
            ],
            "roundtable_reviews": list(self.reviews),
            "report": self._final_report.to_dict() if self._final_report else None,
        }

    def _export_conversation(self) -> List[Dict[str, Any]]:
        return list(self._conversation)

    def _export_llm_usage(self) -> List[Dict[str, Any]]:
        return [
            event
            for llm in self._llm_clients
            for event in llm.get_usage_events()
        ]


class MockDbotAgent(DbotAgent):
    """Scripted D-Bot agent for trace/export tests.

    It exercises the same control-inverted environment path as the real
    code-first agent without making LLM calls.
    """

    def __init__(self, *args, **kwargs):
        kwargs.pop("max_scoring_rounds", None)
        kwargs.pop("max_no_discovery", None)
        super().__init__(*args, **kwargs)

    def solve(self) -> Dict[str, Any]:
        self.selected_experts = ["QueryExpert"]
        self.diagnoses = {"QueryExpert": ExpertDiagnosis(expert_name="QueryExpert")}
        diagnosis = self.diagnoses["QueryExpert"]

        metric_action = {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT pid, usename, datname, state, wait_event_type, wait_event, query, "
                    "extract(epoch FROM clock_timestamp() - query_start) * 1000 AS duration_ms "
                    "FROM pg_stat_activity "
                    "WHERE state = 'active' AND pid <> pg_backend_pid() "
                    "ORDER BY query_start NULLS LAST LIMIT 20;"
                ),
            },
        }
        metric_result = self.execute(
            metric_action["api"], metric_action["args"],
            thinking="Check slow query evidence for a missing index symptom.",
            source="dbot:QueryExpert",
        )
        metric_step = DbotToolStep(
            expert_name="QueryExpert",
            tool_name="execute_sql",
            tool_input={"sql_query": metric_action["args"]["sql_query"]},
            aiops_action=metric_action,
            thought="Check slow query evidence for a missing index symptom.",
            observation=metric_result,
            db_gpt_observation=json.dumps(metric_result, ensure_ascii=False, default=str),
            top_metrics=[{
                "metric": "slow_queries",
                "value": metric_result.get("result", metric_result.get("records")),
            }],
        )
        diagnosis.steps.append(metric_step)
        self._trace_entries.append({
            "timestamp": time.time(),
            "output": json.dumps({
                "thinking": metric_step.thought,
                "actions": [metric_action],
            }, ensure_ascii=False),
            "actions": [metric_action],
        })

        explain_action = {
            "api": "execute_sql",
            "args": {"sql_query": "EXPLAIN SELECT * FROM orders WHERE customer_id = 42"},
        }
        explain_result = self.execute(
            explain_action["api"], explain_action["args"],
            thinking="Inspect the query plan for a sequential scan.",
            source="dbot:QueryExpert",
        )
        explain_step = DbotToolStep(
            expert_name="QueryExpert",
            tool_name="query_sql_plan",
            tool_input={"sql": explain_action["args"]["sql_query"]},
            aiops_action=explain_action,
            thought="Inspect the query plan for a sequential scan.",
            observation=explain_result,
            db_gpt_observation=json.dumps(explain_result, ensure_ascii=False, default=str),
        )
        diagnosis.steps.append(explain_step)
        self._trace_entries.append({
            "timestamp": time.time(),
            "output": json.dumps({
                "thinking": explain_step.thought,
                "actions": [explain_action],
            }, ensure_ascii=False),
            "actions": [explain_action],
        })

        remediation_action = {
            "api": "execute_sql",
            "args": {"sql_query": "CREATE INDEX idx_orders_customer_id ON orders(customer_id)"},
        }
        remediation_result = self.execute(
            remediation_action["api"], remediation_action["args"],
            thinking="Apply the remediation: create the missing customer_id index.",
            source="dbot:QueryExpert",
        )
        remediation_step = DbotToolStep(
            expert_name="QueryExpert",
            tool_name="execute_sql",
            tool_input={"sql_query": remediation_action["args"]["sql_query"]},
            aiops_action=remediation_action,
            thought="Apply the remediation: create the missing customer_id index.",
            observation=remediation_result,
            db_gpt_observation=json.dumps(remediation_result, ensure_ascii=False, default=str),
        )
        diagnosis.steps.append(remediation_step)
        self._trace_entries.append({
            "timestamp": time.time(),
            "output": json.dumps({
                "thinking": remediation_step.thought,
                "actions": [remediation_action],
            }, ensure_ascii=False),
            "actions": [remediation_action],
        })

        diagnosis.root_cause = "Missing index on orders(customer_id) causes sequential scans."
        diagnosis.solutions = "Create an index on orders(customer_id) and verify the query plan."
        diagnosis.top_metrics = metric_step.top_metrics
        diagnosis.knowledge = [{
            "source": "QueryExpert.execute_sql",
            "desc": "EXPLAIN shows Seq Scan on orders; created idx_orders_customer_id and verified it in pg_indexes.",
            "type": "execute_sql",
        }]
        diagnosis.selected_trajectory = "slow_queries -> explain -> missing index"
        diagnosis.search = {
            "type": "scripted_db_gpt_multiagent",
            "selected_expert": "QueryExpert",
        }

        self._final_report = self._build_report(self._alert)
        self._final_report.title = "Mock D-Bot Missing Index Report"
        self._trace_entries.append({
            "timestamp": time.time(),
            "output": json.dumps({"thinking": "ChiefDBA final report", "actions": []}, ensure_ascii=False),
            "actions": [],
        })
        return structured_submission(
            factor=self._final_report.root_cause,
            entity="database",
            evidence=[
                json.dumps(citation, ensure_ascii=False, default=str)
                for citation in self._final_report.citations
            ],
            changes=[self._final_report.solutions],
            verification=[],
            summary=self._final_report.title,
        )
