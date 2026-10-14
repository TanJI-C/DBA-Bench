"""DBAIOps baseline agent for AiOpsBench.

Paper: "DBAIOps: A Reasoning LLM-Enhanced Database Operation and Maintenance System
using Knowledge Graphs" (VLDB 2026).

Architecture: ExperienceGraph + AnomalyModel + Two-Stage Graph Evolution + Reasoning LLM.
The paper's pipeline is adapted to AiOpsBench's interactive agent model:
- Trigger matching uses alert keywords (the interactive entry point), then the matched
  trigger's detection equation is evaluated once per evolution iteration with M/N
  frequency control (paper Section 5.1).
- The Two-Stage Graph Evolution loop queries every metric/tool node on the evolved
  paths and re-samples SQL-backed snapshot metrics so the ADF receives a growing value
  sequence per metric (paper Section 6.1).
- After remediation, the RootCauseAnalyser stage generates the structured diagnosis
  report via the ⟨Sa, Sl, Sm, Se, So⟩ prompt (paper Section 6.2).
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.agents.agent import BaseAgent, LLMAgent
from src.protocols.report import StructuredReport, structured_submission
from src.agents.baselines.dbaiops.adf import AdaptiveDetectorFunction
from src.agents.baselines.dbaiops.anomaly_model import (
    AnomalyModel,
    compute_trend,
)
from src.agents.baselines.dbaiops.graph import ExperienceGraph
from src.agents.baselines.dbaiops.prompts import (
    DBAIOPS_DIAGNOSIS_PROMPT,
    DBAIOPS_FALLBACK_PROMPT,
    DBAIOPS_REMEDIATION_PROMPT,
    DBAIOPS_SYSTEM_PROMPT,
)
from src.agents.baselines.dbaiops.retriever import (
    ExperienceRetriever,
    SQL_BACKED_METRIC_QUERIES,
)
from src.agents.baselines.dbaiops.types import AnomalyEquation, GraphNode
from src.agents.baselines.telemetry import is_tidb_history_tool_surface, parse_metric_response


@dataclass
class DiagnosticStep:
    """One step in the DBAIOps diagnostic trace.

    A step corresponds to one LLM turn or one graph-driven decision.
    It may contain multiple actions (when LLM calls multiple tools at once).
    """

    turn_number: int
    source: str  # "graph" | "llm_fallback" | "llm_diagnosis" | "llm_remediation"
    thinking: str
    actions: List[Dict[str, Any]]
    results: List[Optional[Dict[str, Any]]] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    graph_context: Optional[Dict[str, Any]] = None
    adf_snapshot: Optional[List[Dict[str, Any]]] = None
    messages: Optional[List[Dict[str, Any]]] = None
    input_token: Optional[int] = None
    cache_input_token: Optional[int] = None
    output_token: Optional[int] = None


# SQL statements with these prefixes only read state; anything else counts as a
# remediation change for outcome.changes.
_READ_ONLY_SQL_PREFIXES = ("SELECT", "EXPLAIN", "SHOW")


class DbaiopsAgent(BaseAgent):
    """DBAIOps baseline: Knowledge Graph + Reasoning LLM.

    The paper's Two-Stage Graph Evolution maps to the agent action loop:
    - Proximity Discovery → agent collects all metrics/tools on the evolved paths
    - ADF evaluation → agent decides whether to continue or submit
    - Evolution terminates → LLM remediates → RootCauseAnalyser report → submit
    """

    use_native_tools: bool = True
    mode: str = "dbaiops"

    def __init__(
        self,
        model: str,
        graph_path: str = "data/knowledge_graph/pg_experience_graph.json",
        tidb_graph_path: str = "data/knowledge_graph/tidb_experience_graph.json",
        config_path: str = "config/llm_config.json",
        provider: Optional[str] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        adf_theta: float = 10.0,
        adf_score_threshold: float = 1.2,
        frequency_m: int = 3,
        frequency_n: int = 5,
        max_evolution_depth: int = 4,
        top_k: int = 5,
        enable_log: bool = False,
        log_dir: Optional[str] = None,
    ):
        super().__init__(enable_log=enable_log, log_dir=log_dir)
        self.model = model
        self.graph_path = graph_path
        self.tidb_graph_path = tidb_graph_path
        self.config_path = config_path
        self.provider = provider
        self.url = url
        self.api_key = api_key
        self.max_evolution_depth = max_evolution_depth
        self._top_k = top_k
        self._frequency_m = frequency_m
        self._frequency_n = frequency_n

        # Core components (paper architecture)
        self._graph: Optional[ExperienceGraph] = None
        self._adf = AdaptiveDetectorFunction(
            theta=adf_theta, score_threshold=adf_score_threshold
        )
        self._retriever: Optional[ExperienceRetriever] = None
        self._anomaly_models: Dict[str, AnomalyModel] = {}

        # LLM for remediation and RootCauseAnalyser (paper Section 6.2)
        self._llm: Optional[LLMAgent] = None

        # Agent state
        self._system_prompt: str = ""
        self._user_prompt: str = ""
        self._alert: str = ""
        self._tools: List[Dict[str, Any]] = []
        self._conversation: List[Dict[str, Any]] = []
        self._observations: List[Dict[str, Any]] = []
        self._matched_trigger: Optional[GraphNode] = None
        self._initialized: bool = False
        self._diagnosis_report: str = ""
        self._diagnosis_prompt: str = ""
        self._turn: int = 0
        self._in_remediation: bool = False
        self._steps: List[DiagnosticStep] = []
        self._anomaly_evaluations: List[Dict[str, Any]] = []
        self._executed_changes: List[str] = []
        self._is_tidb = False
        self._history_source = "component_log"
        self._history_sources: Tuple[str, ...] = ()
        self._history_window: Optional[Tuple[str, str]] = None
        self._history_window_seconds = 300
        self._history_limit = 100

    def _ensure_initialized(self):
        """Lazy initialization of graph, retriever and anomaly models."""
        if self._initialized:
            return
        # Target-conditional knowledge: TiDB tool surface selects the TiDB graph
        # (detected in set_tools before solve); PG targets keep graph_path.
        graph_path = self.tidb_graph_path if self._is_tidb else self.graph_path
        self._graph = ExperienceGraph(graph_path)
        self._retriever = ExperienceRetriever(
            self._graph, self._adf,
            max_depth=self.max_evolution_depth,
            top_k=self._top_k,
        )
        # Build anomaly models from trigger vertices (paper Section 5.1)
        models: Dict[str, AnomalyModel] = {}
        for trigger in self._graph.get_trigger_vertices():
            attrs = trigger.attributes
            if "metric_raw" in attrs and "threshold_1" in attrs:
                metric_composite = attrs.get("metric_composite")
                if metric_composite is None and attrs.get("trend_condition") is not None:
                    # Paper: METRIC_composite is derived from METRIC_raw itself via
                    # volatility analysis; the graph carries no dedicated vertex.
                    metric_composite = f"{attrs['metric_raw']}#trend"
                eq = AnomalyEquation(
                    metric_raw=attrs["metric_raw"],
                    threshold_1=attrs["threshold_1"],
                    metric_composite=metric_composite,
                    threshold_2=attrs.get("threshold_2"),
                    trend_condition=attrs.get("trend_condition"),
                    frequency_m=attrs.get("frequency_m", self._frequency_m),
                    frequency_n=attrs.get("frequency_n", self._frequency_n),
                    inverted=bool(attrs.get("inverted", False)),
                )
                models[trigger.id] = AnomalyModel(
                    model_id=trigger.id,
                    trigger_vertex_id=trigger.id,
                    equations=[eq],
                )
        self._anomaly_models = models
        self._initialized = True

    def _ensure_llm(self):
        """Lazy initialization of LLM client with native tool calling."""
        if self._llm is not None:
            return
        self._llm = LLMAgent(
            model=self.model,
            provider=self.provider,
            url=self.url,
            api_key=self.api_key,
            config_path=self.config_path,
            use_native_tools=True,
        )
        if self._tools:
            self._llm.set_tools(self._tools)

    def set_system_prompt(self, system_prompt: str):
        self._system_prompt = system_prompt

    def set_user_prompt(self, user_prompt: str):
        self._user_prompt = user_prompt
        self._alert = user_prompt

    def set_tools(self, tools: List[Dict[str, Any]]):
        self._tools = tools
        names = {
            str((tool.get("function", tool) or {}).get("name", ""))
            for tool in tools
            if isinstance(tool, dict)
        }
        self._is_tidb = (
            is_tidb_history_tool_surface(tools)
            if "query_history" in names
            else False
        )
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

    def solve(self) -> Dict[str, Any]:
        """DBAIOps Two-Stage Graph Evolution mapped to a self-driven flow:
        trigger matching → graph evolution (collect metrics, resample snapshots,
        ADF, anomaly equations) → LLM remediation loop → diagnosis report.
        """
        self._ensure_initialized()
        if self._is_tidb:
            self._prime_tidb_history_window()
            # The cache-hit-ratio metric vertex has no counterpart on the TiDB surface.
            self._retriever.exclude_metric_types.add("cache_hit_ratio")
        self._matched_trigger = self._match_trigger_by_keywords(self._alert)

        if self._matched_trigger is None:
            # No graph path: let the LLM drive from the alert + observations.
            return self._run_llm_loop(self._build_fallback_prompt())

        # Graph evolution: collect metrics on evolved paths until ADF terminates.
        assert self._retriever is not None
        self._retriever.initialize(self._matched_trigger.id)
        is_first = True
        while self._turn < self.max_turns:
            if self._retriever.should_terminate():
                break
            progressed = False
            for node, action in self._retriever.take_pending_actions():
                if self._turn >= self.max_turns:
                    break
                progressed = True
                self._execute_graph_action(node, action, is_first=is_first)
                is_first = False
            for node, action in self._retriever.take_snapshot_resample_actions():
                if self._turn >= self.max_turns:
                    break
                progressed = True
                self._execute_graph_action(node, action, is_first=False)
            if not progressed:
                break
            self._record_trigger_anomaly_evaluation()
            self._retriever.evolve()

        # Evolution finished → LLM-driven diagnosis & remediation.
        return self._run_llm_loop(self._build_diagnosis_prompt())

    def _execute_graph_action(self, node: GraphNode, action: Dict[str, Any], *,
                              is_first: bool):
        action = self._adapt_tidb_action(action)
        self._turn += 1
        thinking = self._build_graph_thinking(action, node.id, is_first=is_first)
        self._record_step("graph", thinking, [action], self._build_graph_context(node.id))
        result = self.execute(
            action["api"], action.get("args", {}),
            thinking=thinking, source="dbaiops:graph",
        )
        self._observations.append(result)
        self._backfill_last_step(result)
        self._extract_metrics_from_result(result, node)

    def _record_trigger_anomaly_evaluation(self):
        """Paper Section 5.1: evaluate the matched trigger's detection equation once
        per evolution iteration; M/N frequency control accumulates across iterations."""
        if self._matched_trigger is None or not self._retriever or not self._retriever.state:
            return
        model = self._anomaly_models.get(self._matched_trigger.id)
        if model is None:
            return
        metric_values: Dict[str, Any] = {}
        for eq in model.equations:
            values = self._resolve_metric_series(eq.metric_raw)
            if values:
                metric_values[eq.metric_raw] = values[-1]
                metric_values[f"{eq.metric_raw}#trend"] = compute_trend(list(values))
        self._anomaly_evaluations.append({
            "iteration": self._retriever.state.depth + 1,
            "metric_values": metric_values,
            "raw_anomaly": model.evaluate_raw(metric_values) if metric_values else False,
            "frequency_confirmed": model.evaluate(metric_values) if metric_values else False,
        })

    def _resolve_metric_series(self, metric_raw: str) -> List[float]:
        """Map a trigger's METRIC_raw name to its accumulated value sequence."""
        assert self._retriever is not None and self._retriever.state is not None
        accumulated = self._retriever.state.accumulated_metrics
        if metric_raw in accumulated:
            return accumulated[metric_raw]
        prefixed = f"{metric_raw}["
        for key, values in accumulated.items():
            if key.startswith(prefixed):
                return values
        spec = SQL_BACKED_METRIC_QUERIES.get(metric_raw)
        if spec:
            candidates = [f"{metric_raw}.{spec['value_column']}"] if spec["value_column"] else []
            candidates.append(f"{metric_raw}.row_count")
            for key in candidates:
                if key in accumulated:
                    return accumulated[key]
        return []

    def _build_diagnosis_prompt(self) -> str:
        assert self._retriever is not None
        experience = self._retriever.get_experience_evidence()
        prompt = DBAIOPS_REMEDIATION_PROMPT.format(
            anomaly_description=self._alert,
            detection_condition=self._get_detection_condition(),
            anomaly_verdict=self._format_anomaly_verdict(),
            metric_evidence=self._format_metric_evidence(),
            metrics_summary=self._format_observations(),
            experience_paths="\n".join(experience) if experience else "No graph experience available.",
        )
        self._diagnosis_prompt = prompt
        return prompt

    def _build_fallback_prompt(self) -> str:
        return DBAIOPS_FALLBACK_PROMPT.format(
            alert=self._alert,
            observations=self._format_observations(),
        )

    def _build_final_report_prompt(self) -> str:
        """Paper Section 6.2: RootCauseAnalyser prompt ⟨Sa, Sl, Sm, Se, So⟩."""
        assert self._retriever is not None
        experience = self._retriever.get_experience_evidence()
        return DBAIOPS_DIAGNOSIS_PROMPT.format(
            anomaly_description=self._alert,
            detection_condition=self._get_detection_condition(),
            metrics_summary=self._format_metric_evidence(),
            experience_paths="\n".join(experience) if experience else "No graph experience available.",
        )

    def _finalize_submission(self) -> Dict[str, Any]:
        """Generate the structured diagnosis report and submit it.

        Runs on every termination path (text-only reply, LLM submit, final-turn
        prompt) so the submitted factor always follows the paper's report contract.
        """
        self._ensure_llm()
        assert self._llm is not None
        self._diagnosis_prompt = self._build_final_report_prompt()
        self._diagnosis_report = self._llm.call_text(
            self._diagnosis_prompt,
            system_prompt=DBAIOPS_SYSTEM_PROMPT,
        )
        # The RootCauseAnalyser report is its own LLM turn
        self._turn += 1
        self._record_step(
            "llm_diagnosis",
            f"[LLM诊断报告] {self._diagnosis_report[:500]}",
            [{"api": "submit", "args": {}}],
            None,
        )
        self._in_remediation = False
        return structured_submission(
            factor=self._diagnosis_report,
            entity="database",
            evidence=[json.dumps(item, ensure_ascii=False, default=str) for item in self._observations],
            changes=self._executed_changes or ["No explicit remediation was reported"],
            verification=(
                ["Remediation actions were executed via tool calls; see outcome.changes and evidence."]
                if self._executed_changes
                else ["Diagnosis generated from collected observations without remediation actions."]
            ),
            summary=self._diagnosis_report,
        )

    def _prime_tidb_history_window(self) -> None:
        result = self.execute(
            "help",
            {"tool_name": "query_history"},
            thinking="Read the TiDB history tool contract before selecting a bounded window.",
            source="dbaiops:graph",
        )
        self._observations.append(result)
        definition = result.get("definition", {}) if isinstance(result, dict) else {}
        runtime = definition.get("runtime", {}) if isinstance(definition, dict) else {}
        available_start = runtime.get("available_start")
        available_end = runtime.get("available_end")
        if not available_start or not available_end:
            raise RuntimeError(
                "DBAIOps TiDB history contract did not provide available UTC range: "
                f"result={result!r}"
            )
        max_records = runtime.get("max_history_records_per_response")
        if not isinstance(max_records, int) or max_records <= 0:
            raise RuntimeError(
                "DBAIOps TiDB history contract did not provide a positive max_history_records_per_response: "
                f"runtime={runtime!r}"
            )
        enabled_sources = runtime.get("enabled_sources")
        if not isinstance(enabled_sources, list) or not enabled_sources:
            raise RuntimeError(
                "DBAIOps TiDB history contract did not provide enabled_sources: "
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

    def _adapt_tidb_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        if not self._is_tidb:
            return action
        api = action.get("api")
        args = dict(action.get("args", {}) or {})
        if api == "read_log" or (
            api == "execute_sql"
            and any(
                marker in str(args.get("sql_query", "")).casefold()
                for marker in (
                    "cluster_slow_query", "slow_query", "statements_summary",
                    "pg_stat_statements",
                )
            )
        ):
            if self._history_window is None:
                raise RuntimeError(
                    "DBAIOps TiDB history action requires a primed UTC window: "
                    f"action={action!r}"
                )
            return {
                "api": "query_history",
                "args": {
                    "source": self._history_source,
                    "start_timestamp": self._history_window[0],
                    "end_timestamp": self._history_window[1],
                    "limit": self._history_limit,
                },
            }
        return action

    def _run_llm_loop(self, prompt: str) -> Dict[str, Any]:
        """Drive the inner LLM with native tool calling until it stops calling tools.

        The LLM's tool calls are executed through the parent gateway (self.execute);
        termination (text-only reply or submit) routes into the RootCauseAnalyser
        report generation.
        """
        self._ensure_llm()
        assert self._llm is not None
        self._llm.set_system_prompt(DBAIOPS_SYSTEM_PROMPT)
        self._llm.set_user_prompt(prompt)
        self._in_remediation = True

        while self._turn < self.max_turns:
            self._turn += 1
            llm_messages = self._snapshot_llm_messages()
            diagnostic_turn_count = self._llm.diagnostic_turn_count()
            thinking, actions = self._llm._next_llm_actions(max_empty_retries=2)
            token_usage = self._llm.get_diagnostic_turn_usage_after(diagnostic_turn_count)
            if self._is_tidb:
                actions = [self._adapt_tidb_action(action) for action in actions]

            if not actions or actions[0].get("api") in (None, "noop", "unknown"):
                # Text-only response → RootCauseAnalyser report → submit.
                return self._finalize_with_report(llm_messages, token_usage, thinking)

            self._record_step("llm_remediation", f"[LLM修复] {thinking}", actions, None,
                              messages=llm_messages, token_usage=token_usage)
            for action in actions:
                api = action.get("api", "")
                args = action.get("args", {}) or {}
                if api == "exit":
                    raise RuntimeError(
                        f"DbaiopsAgent exited without submitting a diagnosis: turn={self._turn}"
                    )
                if api == "submit":
                    report = args.get("report")
                    if isinstance(report, dict):
                        # The LLM submitted an explicit structured report —
                        # honor it when it matches the evaluation protocol
                        # (per-condition entities must be preserved for exact
                        # diagnosis matching). On shape drift fall back to the
                        # agent's own RootCauseAnalyser report instead of
                        # failing the run at the orchestrator's re-validation.
                        try:
                            StructuredReport.from_mapping(report)
                        except (TypeError, ValueError):
                            return self._finalize_with_report(llm_messages, token_usage, thinking)
                        self._in_remediation = False
                        self._record_step(
                            "llm_diagnosis",
                            f"[LLM提交结构化报告] {thinking}",
                            [{"api": "submit", "args": {"report": report}}],
                            None,
                            messages=llm_messages,
                            token_usage=token_usage,
                        )
                        return {"report": report}
                    return self._finalize_with_report(llm_messages, token_usage, thinking)
                result = self.execute(api, args, thinking=thinking, source="dbaiops:llm")
                self._observations.append(result)
                self._backfill_last_step(result)
                self._llm._feed_tool_result(result, tool_call_id=action.get("id"), api=api)
                if self._is_remediation_action(api, args):
                    self._executed_changes.append(f"{api}({self._summarize_args(args)})")

        self._llm._append_final_turn_prompt()
        llm_messages = self._snapshot_llm_messages()
        self._turn += 1
        diagnostic_turn_count = self._llm.diagnostic_turn_count()
        thinking, submission = self._llm._next_final_submission(
            max_empty_retries=2,
            agent_name="DbaiopsAgent",
        )
        token_usage = self._llm.get_diagnostic_turn_usage_after(diagnostic_turn_count)
        self._record_step(
            "llm_diagnosis",
            f"[LLM最终总结] {thinking}",
            [{"api": "submit", "args": submission}],
            None,
            messages=llm_messages,
            token_usage=token_usage,
        )
        return self._finalize_submission()

    def _finalize_with_report(self, llm_messages: List[Dict[str, Any]],
                              token_usage: Optional[Dict[str, int]],
                              thinking: str) -> Dict[str, Any]:
        llm_messages = llm_messages + [{"role": "assistant", "content": thinking}]
        submission = self._finalize_submission()
        step = self._steps[-1]
        step.messages = llm_messages
        step.input_token = token_usage["input_token"] if token_usage else None
        step.cache_input_token = token_usage["cache_input_token"] if token_usage else None
        step.output_token = token_usage["output_token"] if token_usage else None
        return submission

    @staticmethod
    def _is_remediation_action(api: str, args: Dict[str, Any]) -> bool:
        if api == "execute_sql":
            sql = str(args.get("sql_query", "")).lstrip()
            return bool(sql) and not sql.upper().startswith(_READ_ONLY_SQL_PREFIXES)
        if api == "manage_instance":
            return str(args.get("action", "")).lower() in {"set_config", "restart"}
        return False

    @staticmethod
    def _summarize_args(args: Dict[str, Any]) -> str:
        return str(args.get("sql_query") or json.dumps(args, ensure_ascii=False, default=str))[:200]

    def _backfill_last_step(self, result: Dict[str, Any]):
        """Fill the first pending result slot of the most recent step."""
        self._conversation.append({"role": "tool", "content": result})
        if self._steps:
            step = self._steps[-1]
            for i, r in enumerate(step.results):
                if r is None:
                    step.results[i] = result
                    break

    def reset(self):
        """Reset agent state for a new scenario."""
        self._alert = ""
        self._conversation.clear()
        self._observations.clear()
        self._matched_trigger = None
        self._diagnosis_report = ""
        self._diagnosis_prompt = ""
        self._turn = 0
        self._in_remediation = False
        self._steps.clear()
        self._anomaly_evaluations.clear()
        self._executed_changes.clear()
        self._is_tidb = False
        self._history_source = "component_log"
        self._history_sources = ()
        self._history_window = None
        self._history_window_seconds = 300
        self._history_limit = 100
        if self._retriever:
            self._retriever.state = None
        if self._llm:
            self._llm.reset_conversation()
        for model in self._anomaly_models.values():
            model.reset()

    # --- Helper methods ---

    def _snapshot_llm_messages(self) -> List[Dict[str, Any]]:
        """Snapshot the internal LLM's conversation history for trace recording."""
        if not self._llm:
            return []
        return self._llm.get_conversation_history()

    def _record_step(self, source: str, thinking: str,
                     actions: List[Dict[str, Any]],
                     graph_context: Optional[Dict[str, Any]],
                     messages: Optional[List[Dict[str, Any]]] = None,
                     token_usage: Optional[Dict[str, int]] = None):
        """Record a diagnostic step (one thinking + multiple actions)."""
        adf_snapshot = None
        if self._retriever and self._retriever.state and self._retriever.state.adf_results:
            adf_snapshot = [
                {"metric": r.metric, "score": r.score,
                 "is_abnormal": r.is_abnormal, "sigma": r.sigma,
                 "deviation": r.deviation}
                for r in self._retriever.state.adf_results
            ]
        step = DiagnosticStep(
            turn_number=self._turn,
            source=source,
            thinking=thinking,
            actions=actions,
            results=[None] * len(actions),
            graph_context=graph_context,
            adf_snapshot=adf_snapshot,
            messages=messages,
            input_token=token_usage["input_token"] if token_usage else None,
            cache_input_token=token_usage["cache_input_token"] if token_usage else None,
            output_token=token_usage["output_token"] if token_usage else None,
        )
        self._steps.append(step)
        self._conversation.append({"role": "assistant", "content": thinking})

    def _build_graph_thinking(self, action: Dict[str, Any],
                              node_id: Optional[str],
                              is_first: bool = False) -> str:
        """Build structured thinking text for graph-driven tool calls."""
        assert self._retriever is not None
        state = self._retriever.state
        depth = state.depth if state else 0
        trigger_name = self._matched_trigger.name if self._matched_trigger else "?"
        trigger_id = self._matched_trigger.id if self._matched_trigger else "?"

        path_chain = ""
        current_node_name = ""
        current_node_type = ""
        if node_id and self._retriever:
            path_names = self._retriever.get_current_path_for_node(node_id)
            if path_names:
                path_chain = " → ".join(path_names)
            node = self._graph.nodes.get(node_id) if self._graph else None
            if node:
                current_node_name = node.name
                current_node_type = node.type

        api = action.get("api", "?")
        args_summary = ", ".join(
            f"{k}={v!r}" for k, v in action.get("args", {}).items()
        )

        lines = [f"[知识图谱自动探索] 演化深度={depth}/{self.max_evolution_depth}"]
        if is_first:
            lines.append(f"匹配触发节点: {trigger_name} ({trigger_id})")
        if path_chain:
            lines.append(f"当前路径: {path_chain}")
        if current_node_name:
            lines.append(f"当前节点: {current_node_name} ({current_node_type})")
        lines.append(f"自动调用工具: {api}({args_summary})")

        return "\n".join(lines)

    def _build_graph_context(self, node_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Build graph context dict for the current step."""
        if not node_id or not self._graph:
            return None
        node = self._graph.nodes.get(node_id)
        if not node:
            return None
        path_names = self._retriever.get_current_path_for_node(node_id) if self._retriever else None
        return {
            "node_id": node.id,
            "node_type": node.type,
            "node_name": node.name,
            "node_content": node.content,
            "path": path_names,
            "trigger_id": self._matched_trigger.id if self._matched_trigger else None,
            "trigger_name": self._matched_trigger.name if self._matched_trigger else None,
        }

    def _match_trigger_by_keywords(self, alert_text: str) -> Optional[GraphNode]:
        """Match alert text to a trigger vertex via keyword overlap."""
        if not self._graph:
            return None
        alert_lower = alert_text.lower()
        best_trigger = None
        best_score = 0

        for trigger in self._graph.get_trigger_vertices():
            keywords = trigger.attributes.get("keywords", [])
            score = sum(1 for kw in keywords if kw.lower() in alert_lower)
            if score > best_score:
                best_score = score
                best_trigger = trigger

        return best_trigger

    def _extract_metrics_from_result(self, result: Dict[str, Any],
                                     node: GraphNode):
        """Extract metric samples from a graph-phase tool result for the ADF.

        Series responses carry their full history and replace the stored sequence;
        records/rows responses append one sample per query (row count plus the
        declared value column); snapshot responses append their numeric fields.
        """
        if not self._retriever or not self._retriever.state:
            return
        if node.type != "metric":
            return
        metric_key = node.attributes.get("metric_type", node.name)
        state = self._retriever.state

        if result.get("kind") == "series":
            self._extract_series_metrics(result, metric_key, state)
            return

        if result.get("kind") == "records":
            records = result.get("records") or []
            self._append_metric_sample(f"{metric_key}.row_count", float(len(records)))
            column = SQL_BACKED_METRIC_QUERIES.get(metric_key, {}).get("value_column")
            if column:
                total = sum(
                    float(record[column])
                    for record in records
                    if isinstance(record.get(column), (int, float))
                )
                self._append_metric_sample(f"{metric_key}.{column}", total)
            return

        columns = result.get("columns")
        rows = result.get("result")
        if isinstance(columns, list) and isinstance(rows, list):
            self._append_metric_sample(f"{metric_key}.row_count", float(len(rows)))
            column = SQL_BACKED_METRIC_QUERIES.get(metric_key, {}).get("value_column")
            if column and column in columns:
                index = columns.index(column)
                total = sum(
                    float(row[index])
                    for row in rows
                    if isinstance(row[index], (int, float))
                )
                self._append_metric_sample(f"{metric_key}.{column}", total)
            return

        snapshot = result.get("snapshot")
        if isinstance(snapshot, dict):
            for sub_key, value in snapshot.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    self._append_metric_sample(f"{metric_key}.{sub_key}", float(value))

    def _append_metric_sample(self, key: str, value: float):
        assert self._retriever is not None and self._retriever.state is not None
        accumulated = self._retriever.state.accumulated_metrics
        accumulated.setdefault(key, []).append(value)

    def _extract_series_metrics(self, result: Dict[str, Any], metric_key: str,
                                state) -> None:
        try:
            for series in parse_metric_response(result):
                key = f"{metric_key}[{series.series_target}].{series.field}"
                state.accumulated_metrics[key] = list(series.values)
            return
        except ValueError as exc:
            # Loaded hosts can stall the sampler and break the strict
            # uniform-step contract (shared with STL-based baselines). ADF only
            # needs the value sequence, so extract leniently with a visible
            # warning instead of failing the episode.
            print(f"[DbaiopsAgent] strict metric parse failed ({exc}); "
                  "extracting series values leniently")
        for target, series in (result.get("series") or {}).items():
            if not isinstance(series, dict):
                continue
            for field, values in series.items():
                if field == "timestamps" or not isinstance(values, list):
                    continue
                clean = [float(v) for v in values
                         if isinstance(v, (int, float)) and not isinstance(v, bool)]
                if clean:
                    state.accumulated_metrics[f"{metric_key}[{target}].{field}"] = clean

    def _get_detection_condition(self) -> str:
        """Get the detection condition string for the matched trigger."""
        if not self._matched_trigger:
            return "N/A"
        attrs = self._matched_trigger.attributes
        parts = []
        if "metric_raw" in attrs:
            parts.append(f"{attrs['metric_raw']} > {attrs.get('threshold_1', '?')}")
        if "threshold_2" in attrs and "trend_condition" in attrs:
            trend_names = {0: "stable", 1: "sharp_decline", 2: "slow_decline",
                          3: "sharp_rise", 4: "slow_rise", 5: "fluctuating"}
            trend = trend_names.get(attrs["trend_condition"], "unknown")
            parts.append(f"OR (trend={trend} AND {attrs['metric_raw']} > {attrs['threshold_2']})")
        return " ".join(parts) if parts else "N/A"

    def _format_anomaly_verdict(self) -> str:
        """Format the M/N frequency-controlled detection-equation verdict."""
        if not self._anomaly_evaluations:
            return "No detection-equation evaluation was performed (no matching samples collected)."
        true_count = sum(1 for e in self._anomaly_evaluations if e["raw_anomaly"])
        last = self._anomaly_evaluations[-1]
        values = json.dumps(last["metric_values"], ensure_ascii=False, default=str)
        return (
            f"Detection condition held in {true_count}/{len(self._anomaly_evaluations)} evolution "
            f"iterations; frequency-controlled anomaly verdict: "
            f"{'CONFIRMED' if last['frequency_confirmed'] else 'NOT CONFIRMED'}. "
            f"Latest evaluated values: {values}"
        )

    def _format_metric_evidence(self) -> str:
        """Format per-metric key statistics with ADF verdicts (paper Sm)."""
        state = self._retriever.state if self._retriever else None
        if not state or not state.accumulated_metrics:
            return "No metric samples were collected."
        adf_by_metric = {r.metric: r for r in state.adf_results}
        lines = []
        for key, values in sorted(state.accumulated_metrics.items()):
            if not values:
                continue
            stats = (
                f"n={len(values)}, latest={values[-1]:.4g}, "
                f"mean={sum(values) / len(values):.4g}, "
                f"min={min(values):.4g}, max={max(values):.4g}"
            )
            adf = adf_by_metric.get(key)
            if adf:
                stats += (
                    f" | ADF: score={adf.score:.3f}, sigma={adf.sigma:.4g}, "
                    f"baseline={adf.baseline:.4g}, deviation={adf.deviation:.4g}, "
                    f"abnormal={'YES' if adf.is_abnormal else 'no'}"
                )
            lines.append(f"- {key}: {stats}")
        return "\n".join(lines)

    def _format_observations(self) -> str:
        """Format collected observations for LLM prompt."""
        if not self._observations:
            return "No observations collected yet."
        lines = []
        for i, obs in enumerate(self._observations[-10:], 1):
            lines.append(f"{i}. {json.dumps(obs, ensure_ascii=False, default=str)[:200]}")
        return "\n".join(lines)

    # --- 诊断路径导出（graph 结构） ---

    def _export_prompts(self) -> Dict[str, str]:
        return {"system": self._system_prompt or "", "user": self._user_prompt or ""}

    def _export_turns(self) -> List[Dict[str, Any]]:
        """Build turns from step log with full think-action-result."""
        turns = []
        for step in self._steps:
            turn: Dict[str, Any] = {
                "turn_number": step.turn_number,
                "timestamp": step.timestamp,
                "thinking": step.thinking,
                "source": step.source,
                "actions": [{"api": a.get("api", ""), "args": a.get("args", {})}
                            for a in step.actions],
                "results": [{"api": step.actions[i].get("api", "") if i < len(step.actions) else "",
                             "status": "executed" if r else "pending",
                             "data": r}
                            for i, r in enumerate(step.results)],
            }
            if step.graph_context:
                turn["graph_context"] = step.graph_context
            if step.adf_snapshot:
                turn["adf_snapshot"] = step.adf_snapshot
            if step.messages is not None:
                turn["messages"] = step.messages
            if step.input_token is not None:
                turn.update({
                    "input_token": step.input_token,
                    "cache_input_token": step.cache_input_token,
                    "output_token": step.output_token,
                })
            turns.append(turn)
        return turns

    def _export_structure(self) -> Dict[str, Any]:
        trigger = self._matched_trigger.to_dict() if self._matched_trigger else None
        if trigger:
            trigger = {k: trigger.get(k) for k in ("id", "type", "name", "content")}

        state = self._retriever.state if self._retriever else None
        evolution: Dict[str, Any] = {
            "max_depth": self.max_evolution_depth,
            "depth": 0,
            "history": [],
            "final_paths": [],
            "adf_results": [],
            "cross_edges": [],
        }
        if state is not None:
            evolution["depth"] = state.depth
            evolution["history"] = state.adf_history
            evolution["final_paths"] = [
                {
                    "nodes": [
                        {"id": n.id, "type": n.type,
                         "name": n.name, "content": n.content}
                        for n in path.nodes
                    ],
                    "edges": [
                        {"source": e.source, "target": e.target, "type": e.type}
                        for e in path.edges
                    ],
                }
                for path in state.expanded_paths
            ]
            evolution["adf_results"] = [
                {"metric": r.metric, "score": r.score,
                 "is_abnormal": r.is_abnormal,
                 "sigma": r.sigma, "deviation": r.deviation}
                for r in state.adf_results
            ]
            evolution["cross_edges"] = [
                {"source": e.source, "target": e.target, "type": e.type}
                for e in state.cross_edges_created
            ]

        return {
            "type": "graph",
            "trigger": trigger,
            "evolution": evolution,
            "anomaly_evaluations": list(self._anomaly_evaluations),
            "executed_changes": list(self._executed_changes),
            "diagnosis_report": self._diagnosis_report or "",
            "diagnosis_prompt": self._diagnosis_prompt or "",
        }

    def _export_conversation(self) -> List[Dict[str, Any]]:
        return list(self._conversation)

    def _export_llm_usage(self) -> List[Dict[str, Any]]:
        return [] if self._llm is None else self._llm.get_usage_events()


class MockDbaiopsAgent(DbaiopsAgent):
    """Scripted DBAIOps agent for trace/export tests."""

    def solve(self) -> Dict[str, Any]:
        self._matched_trigger = GraphNode(
            id="trigger_index_problem",
            type="trigger",
            name="Missing index trigger",
            content="Slow query with full table scan indicates a missing index.",
        )

        graph_action = {
            "api": "execute_sql",
            "args": {"sql_query": SQL_BACKED_METRIC_QUERIES["slow_queries"]["sql"]},
        }
        self._turn += 1
        self._record_step(
            "graph",
            "[知识图谱自动探索] 通过 execute_sql 查询活动 SQL 以确认缺失索引症状。",
            [graph_action],
            {
                "node_id": "trigger_index_problem",
                "node_type": "trigger",
                "node_name": "Missing index trigger",
                "node_content": "Slow query with full table scan indicates a missing index.",
                "path": ["Missing index trigger"],
                "trigger_id": "trigger_index_problem",
                "trigger_name": "Missing index trigger",
            },
        )
        graph_result = self.execute(
            graph_action["api"], graph_action["args"],
            thinking="[知识图谱自动探索] 通过 execute_sql 查询活动 SQL 以确认缺失索引症状。",
            source="dbaiops:graph",
        )
        self._observations.append(graph_result)
        self._backfill_last_step(graph_result)

        remediation_action = {
            "api": "execute_sql",
            "args": {"sql_query": "CREATE INDEX idx_orders_customer_id ON orders(customer_id)"},
        }
        self._turn += 1
        self._record_step(
            "llm_remediation",
            "[LLM修复] 根据图谱证据创建缺失索引。",
            [remediation_action],
            None,
            messages=[
                {"role": "system", "content": DBAIOPS_SYSTEM_PROMPT},
                {"role": "user", "content": self._user_prompt},
            ],
        )
        remediation_result = self.execute(
            remediation_action["api"], remediation_action["args"],
            thinking="[LLM修复] 根据图谱证据创建缺失索引。",
            source="dbaiops:llm",
        )
        self._observations.append(remediation_result)
        self._backfill_last_step(remediation_result)
        self._executed_changes.append(f"execute_sql({remediation_action['args']['sql_query']})")

        self._diagnosis_prompt = self._user_prompt
        self._diagnosis_report = "Missing index on orders(customer_id); index creation completed."
        return structured_submission(
            factor=self._diagnosis_report,
            entity="database",
            evidence=[json.dumps(item, ensure_ascii=False, default=str) for item in self._observations],
            changes=list(self._executed_changes),
            verification=["Remediation actions were executed via tool calls; see outcome.changes and evidence."],
            summary=self._diagnosis_report,
        )
