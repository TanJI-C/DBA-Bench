"""Panda baseline agent for AiOpsBench.

Implements the Panda framework (AWS AI Labs) for database performance debugging:
Grounding (RAG + T2T) → Diagnosis → Verification → Affordance → Feedback.
"""

import json
import re
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.agents.agent import BaseAgent, LLMAgent
from src.agents.baselines.panda.affordance import PandaAffordance
from src.agents.baselines.panda.feedback import PandaFeedbackStore
from src.agents.baselines.panda.grounding import (
    PandaContextAggregator,
    PandaDocumentRetriever,
    PandaTelemetryToText,
)
from src.agents.baselines.panda.prompts import (
    PANDA_DIAGNOSIS_PROMPT,
    PANDA_SYSTEM_PROMPT,
)
from src.agents.baselines.panda.types import GroundingContext, TelemetryFeature
from src.agents.baselines.panda.verification import PandaVerifier, PandaSourceAttribution
from src.agents.baselines.telemetry import metric_names_from_tools, parse_metric_response


STANDARD_METRICS = [
    "cpu", "memory", "disk_io", "active_connections", "disk_usage",
    "qps", "cache_hit_ratio",
]


class PandaAgent(BaseAgent):
    """
    Panda baseline agent for database performance debugging.

    Modes:
    - panda_basic:    LLM + proactive T2T (no RAG, no verification)
    - panda_rag:      + Document retrieval (embedding-based)
    - panda_verified: + Verification mechanism (NLI + retry K=3)
    - panda_full:     + Affordance + Feedback (all components)
    """

    use_native_tools: bool = True

    def __init__(
        self,
        model: str,
        mode: str = "panda_full",
        provider: Optional[str] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        config_path: str = "config/llm_config.json",
        use_native_tools: bool = True,
        knowledge_paths: Optional[List[str]] = None,
        knowledge_top_k: int = 5,
        max_verification_retries: int = 3,
        max_initial_metrics: int = 7,
        require_evidence_for_high_risk: bool = True,
        allowed_tools: Optional[List[str]] = None,
        db_type: str = "postgresql",
        enable_log: bool = False,
        log_dir: Optional[str] = None,
    ):
        super().__init__(enable_log=enable_log, log_dir=log_dir)
        self.mode = mode
        self.model = model
        self.provider = provider
        self.url = url
        self.api_key = api_key
        self.config_path = config_path
        self.use_native_tools = use_native_tools
        self.max_initial_metrics = max_initial_metrics
        self.db_type = db_type
        self._allowed_tools_explicit = allowed_tools is not None
        self._metrics_to_collect = list(STANDARD_METRICS)
        self.allowed_tools = allowed_tools or [
            "query_metrics", "execute_sql", "manage_instance",
            "read_log", "submit",
        ]

        self._llm: Optional[LLMAgent] = None
        self._system_prompt: str = ""
        self._user_prompt: str = ""
        self._alert: str = ""
        self._history_window_seconds = 300
        self._history_limit = 100
        self._history_enabled = False
        self._tools_schema: List[Dict[str, Any]] = []
        self._evidence: List[Dict[str, Any]] = []
        self._telemetry_features: List[TelemetryFeature] = []
        self._schema_info: str = ""
        self._grounding_context: Optional[GroundingContext] = None
        self._verification_retries: int = 0

        # T2T is always active
        self._t2t = PandaTelemetryToText()
        self._aggregator = PandaContextAggregator()

        # Document retriever (panda_rag and above)
        self._retriever: Optional[PandaDocumentRetriever] = None
        if mode in ("panda_rag", "panda_verified", "panda_full"):
            self._retriever = PandaDocumentRetriever(
                paths=knowledge_paths or [], top_k=knowledge_top_k,
            )

        # Verification (panda_verified and above)
        self._verifier: Optional[PandaVerifier] = None
        self._max_verification_retries = max_verification_retries
        self._source_attribution: Optional[PandaSourceAttribution] = None
        if mode in ("panda_verified", "panda_full"):
            self._source_attribution = PandaSourceAttribution()

        # Affordance (panda_full only)
        self._affordance: Optional[PandaAffordance] = None
        if mode == "panda_full":
            self._affordance = PandaAffordance(
                require_evidence_for_high_risk=require_evidence_for_high_risk,
            )

        # Feedback (panda_full only)
        self._feedback: Optional[PandaFeedbackStore] = None
        if mode == "panda_full":
            self._feedback = PandaFeedbackStore()

    # --- Setup methods (called by Orchestrator) ---

    def reset(self):
        """Reset agent state for a new diagnostic case."""
        self._evidence = []
        self._telemetry_features = []
        self._schema_info = ""
        self._history_window_seconds = 300
        self._history_limit = 100
        self._grounding_context = None
        self._verification_retries = 0
        self._t2t = PandaTelemetryToText()
        self.action_history = []
        if self._llm:
            self._llm.reset_conversation()

    def _ensure_llm(self):
        """Lazily initialize the underlying LLM agent."""
        if self._llm is not None:
            return
        self._llm = LLMAgent(
            url=self.url,
            api_key=self.api_key,
            system_prompt="",
            model=self.model,
            config_path=self.config_path,
            use_native_tools=self.use_native_tools,
            provider=self.provider,
            enable_log=self.enable_log,
            log_dir=self.log_dir,
        )
        if self.mode in ("panda_verified", "panda_full"):
            self._verifier = PandaVerifier(
                call_llm_fn=self._call_llm_for_verification,
                max_retries=self._max_verification_retries,
            )
        if self._affordance:
            self._affordance._call_llm = self._call_llm_for_verification

    def set_system_prompt(self, system_prompt: str):
        self._system_prompt = system_prompt
        self._ensure_llm()
        panda_sys = PANDA_SYSTEM_PROMPT.format(
            tool_descriptions=self._format_tool_descriptions()
        )
        combined = panda_sys + "\n\n" + system_prompt
        self._llm.set_system_prompt(combined)

    def set_user_prompt(self, user_prompt: str):
        self._user_prompt = user_prompt
        self._alert = user_prompt
        self._ensure_llm()
        self._llm.set_user_prompt(user_prompt)

    def set_tools(self, tools: List[Dict[str, Any]]):
        self._tools_schema = tools
        names = {
            str((tool.get("function", tool) or {}).get("name", ""))
            for tool in tools
            if isinstance(tool, dict)
        }
        if "query_metrics" in names:
            self._metrics_to_collect = list(metric_names_from_tools(tools))
        self._history_enabled = "query_history" in names
        if self._history_enabled:
            if not self._allowed_tools_explicit:
                self.allowed_tools = [
                    "query_metrics", "query_history", "execute_sql",
                    "manage_cluster", "help", "submit",
                ]
        self._ensure_llm()
        self._llm.set_tools(tools)

    def parse_action(self, raw_input: str) -> Dict[str, Any]:
        """Parse raw input into action dict (kept for trace compatibility)."""
        self._ensure_llm()
        return self._llm._parse_llm_response(raw_input).get("action", {"api": "noop", "args": {}})

    # --- Main loop ---

    def solve(self) -> Dict[str, Any]:
        """Panda methodology as a self-driven flow:
        proactive metric collection → grounding → LLM diagnosis (native tools) →
        verification (retry) → affordance filter → submission.
        """
        self._ensure_llm()

        # Turn 1: proactive metric + schema collection
        for action in self._get_proactive_actions():
            api = action["api"]
            args = action.get("args", {})
            result = self.execute(
                api, args,
                thinking="Proactively collecting metrics for T2T analysis",
                source="panda",
            )
            self._ingest_evidence(action, result)

        if self._history_enabled:
            self._load_history_contract()
            history_action = self._build_history_action()
            if history_action is not None:
                result = self.execute(
                    history_action["api"], history_action["args"],
                    thinking="Querying the bounded TiDB historical window selected from telemetry",
                    source="panda",
                )
                self._ingest_evidence(history_action, result)

        # Build grounding context and inject into the LLM conversation
        self._grounding_context = self._build_grounding_context()
        self._update_llm_with_context()

        # LLM-driven diagnosis / remediation loop
        for _ in range(self.max_turns):
            thinking, actions = self._llm._next_llm_actions(max_empty_retries=2)
            if not actions:
                break

            submit_action = self._find_submit_action(actions)
            if submit_action:
                actions = self._finalize_submit(submit_action, actions)
                submit_action = self._find_submit_action(actions)

            if self._affordance:
                context_str = self._grounding_context.aggregated_prompt if self._grounding_context else ""
                actions = self._affordance.filter_actions(
                    actions, evidence_count=len(self._evidence), context=context_str
                )

            for action in actions:
                api = action.get("api", "")
                args = action.get("args", {}) or {}
                if api == "exit":
                    return {}
                if api == "submit":
                    return args
                result = self.execute(api, args, thinking=thinking, source="panda")
                self._ingest_evidence(action, result)
                self._llm._feed_tool_result(result, tool_call_id=action.get("id"), api=api)

        return {}

    def _finalize_submit(self, submit_action: Dict[str, Any],
                         actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run verification (with retry) and source attribution before submitting."""
        while submit_action and self._verifier:
            verification = self._verify_before_submit(submit_action)
            if verification.verdict == "accept":
                return self._add_source_citations(actions)
            if self._verification_retries >= self._max_verification_retries:
                break
            self._verification_retries += 1
            _, actions = self._regenerate_diagnosis_actions()
            submit_action = self._find_submit_action(actions)
        return actions

    def _ingest_evidence(self, action: Dict[str, Any], result: Any):
        """Update evidence store, T2T features, schema info, feedback from one result."""
        api = action.get("api", "")
        result_str = json.dumps(result, ensure_ascii=False) if isinstance(result, dict) else str(result)
        self._evidence.append({
            "action": f"{api}({json.dumps(action.get('args', {}), ensure_ascii=False)})",
            "result": result_str[:500],
        })
        if api == "query_metrics":
            self._process_metric_result(action, result)
        if api == "execute_sql":
            sql = action.get("args", {}).get("sql_query", "")
            if "information_schema" in sql.lower() or "\\d" in sql:
                self._schema_info = result_str[:1000]
        if self._feedback:
            self._feedback.store_interaction(
                query=self._alert,
                actions=[action],
                observations=[result_str[:200]],
            )

    # --- Internal helper methods ---

    def _get_proactive_actions(self) -> List[Dict[str, Any]]:
        """Generate initial metric collection + schema query actions."""
        actions = []
        for metric in self._metrics_to_collect[: self.max_initial_metrics]:
            actions.append({
                "api": "query_metrics",
                "args": {"metric_type": metric, "target": None},
            })
        schema_sql = self._get_schema_query()
        actions.append({
            "api": "execute_sql",
            "args": {"sql_query": schema_sql},
        })
        return actions

    def _get_schema_query(self) -> str:
        """Get schema discovery SQL for the target database type."""
        if self.db_type == "tidb":
            return ("SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables "
                    "WHERE TABLE_SCHEMA NOT IN ('mysql', 'INFORMATION_SCHEMA', "
                    "'PERFORMANCE_SCHEMA', 'METRICS_SCHEMA') LIMIT 20;")
        return ("SELECT schemaname, tablename FROM pg_tables "
                "WHERE schemaname NOT IN ('pg_catalog', 'information_schema') LIMIT 20;")

    def _build_history_action(self) -> Optional[Dict[str, Any]]:
        history_function = next(
            (
                tool.get("function", tool)
                for tool in self._tools_schema
                if isinstance(tool, dict)
                and tool.get("function", tool).get("name") == "query_history"
            ),
            None,
        )
        if history_function is None:
            return None
        source_values = (
            history_function.get("parameters", {})
            .get("properties", {})
            .get("source", {})
            .get("enum", [])
        )
        source = "topsql" if "topsql" in source_values else (
            "slow_queries" if "slow_queries" in source_values else "component_log"
        )
        available_end = None
        for evidence in reversed(self._evidence):
            try:
                result = json.loads(evidence["result"])
            except (KeyError, json.JSONDecodeError, TypeError):
                continue
            window = result.get("window") if isinstance(result, dict) else None
            if isinstance(window, dict) and window.get("available_end"):
                available_end = datetime.strptime(
                    window["available_end"], "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=timezone.utc)
                break
        if available_end is None:
            raise RuntimeError("Panda TiDB history query requires a metric response with available_end")
        available_start = available_end - timedelta(seconds=self._history_window_seconds)
        return {
            "api": "query_history",
            "args": {
                "source": source,
                "start_timestamp": available_start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_timestamp": available_end.strftime("%Y-%m-%d %H:%M:%S"),
                "limit": self._history_limit,
            },
        }

    def _load_history_contract(self) -> None:
        result = self.execute(
            "help",
            {"tool_name": "query_history"},
            thinking="Reading the bounded history contract before selecting a window",
            source="panda",
        )
        runtime = result["definition"]["runtime"]
        max_records = runtime["max_history_records_per_response"]
        enabled_sources = tuple(runtime["enabled_sources"])
        if not isinstance(max_records, int) or max_records <= 0:
            raise RuntimeError(f"Panda history max record limit is invalid: runtime={runtime!r}")
        if not enabled_sources:
            raise RuntimeError(f"Panda history has no enabled sources: runtime={runtime!r}")
        self._history_window_seconds = 300
        self._history_limit = min(100, max_records)

    def _process_metric_result(self, action: Dict, result: Any):
        """Extract T2T features from a metric query result."""
        metric_type = action.get("args", {}).get("metric_type", "unknown")
        if isinstance(result, dict) and result.get("kind") == "series":
            self._telemetry_features.extend(
                self._t2t.extract_series_features(
                    parse_metric_response(result, metric=metric_type)
                )
            )
            return
        values = self._extract_numeric_values(result)
        if values:
            feature = self._t2t.extract_features(metric_type, values)
            self._telemetry_features.append(feature)

    def _extract_numeric_values(self, result: Any) -> List[float]:
        """Extract numeric values from a metric query result."""
        values = []
        if isinstance(result, dict):
            if result.get("kind") == "series":
                for series in result["series"].values():
                    for name, samples in series.items():
                        if name != "timestamps":
                            values.extend(float(value) for value in samples)
                return values
            data = result.get("result", result.get("data", result))
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, (int, float)):
                        values.append(float(item))
                    elif isinstance(item, dict):
                        if "value" in item and isinstance(item["value"], (int, float)):
                            values.append(float(item["value"]))
                        else:
                            for v in item.values():
                                if isinstance(v, (int, float)):
                                    values.append(float(v))
                                    break
            elif isinstance(data, (int, float)):
                values.append(float(data))
        elif isinstance(result, list):
            for item in result:
                if isinstance(item, (int, float)):
                    values.append(float(item))
        return values

    def _build_grounding_context(self) -> GroundingContext:
        """Build grounding context from collected evidence.

        Paper: compute correlations, identify problematic metrics,
        then retrieve docs based on alert + anomaly summaries.
        """
        # Compute cross-metric correlations (paper requirement)
        if len(self._telemetry_features) > 1:
            self._telemetry_features = self._t2t.compute_correlations(
                self._telemetry_features
            )

        # Identify problematic metrics (paper requirement)
        problematic, anomaly_summaries = self._t2t.identify_problematic_metrics(
            self._telemetry_features
        )

        # Retrieve docs using alert + anomaly info as query
        documents = []
        if self._retriever:
            query = self._alert
            if anomaly_summaries:
                query += " " + " ".join(anomaly_summaries[:3])
            snippets = self._retriever.retrieve(query)
            documents = snippets

        feedback_examples = []
        if self._feedback:
            feedback_examples = self._feedback.retrieve_similar(self._alert)

        # Include anomaly summaries in telemetry text
        telemetry_texts = [f.text_summary for f in self._telemetry_features]
        if anomaly_summaries:
            telemetry_texts.extend(anomaly_summaries)

        return GroundingContext(
            documents=[s.content for s in documents],
            telemetry_text=telemetry_texts,
            schema_info=self._schema_info,
            aggregated_prompt=json.dumps({
                "alert": self._alert,
                "problematic_metrics": anomaly_summaries,
                "telemetry_analysis": [f.text_summary for f in self._telemetry_features],
                "relevant_documents": [s.content for s in documents][:3],
                "schema_context": self._schema_info,
                "previous_interactions": feedback_examples,
            }, indent=2, ensure_ascii=False),
        )

    def _update_llm_with_context(self):
        """Inject grounding context into the LLM conversation as a user message."""
        if not self._grounding_context:
            return
        ctx = self._grounding_context
        telemetry_text = "\n".join(ctx.telemetry_text) if ctx.telemetry_text else "No telemetry data yet."
        docs_text = "\n---\n".join(ctx.documents[:3]) if ctx.documents else "No relevant documents found."
        feedback_text = "None."
        if self._feedback:
            similar = self._feedback.retrieve_similar(self._alert, top_k=3)
            if similar:
                feedback_text = "\n".join(similar)

        enriched_prompt = PANDA_DIAGNOSIS_PROMPT.format(
            alert=self._alert,
            telemetry_features=telemetry_text,
            retrieved_docs=docs_text,
            schema_info=ctx.schema_info or "Not yet collected.",
            feedback_examples=feedback_text,
        )
        self._llm._conversation_history.append({
            "role": "user",
            "content": enriched_prompt,
        })

    def _find_submit_action(self, actions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find a submit action in the action list."""
        for action in actions:
            if action.get("api") == "submit":
                return action
        return None

    def _verify_before_submit(self, submit_action: Dict[str, Any]):
        """Run NLI verification: check diagnosis against retrieved docs (per paper).

        Paper: premise = retrieved documents and tickets, NOT tool execution results.
        """
        condition = submit_action["args"]["report"]["diagnosis"]["conditions"][0]
        root_cause = condition["factor"]
        retrieved_docs = []
        if self._grounding_context:
            retrieved_docs = self._grounding_context.documents
        return self._verifier.verify(root_cause, retrieved_docs)

    def _regenerate_diagnosis_actions(self) -> Tuple[str, List[Dict[str, Any]]]:
        """Regenerate diagnosis after verification failure (per paper).

        Paper: "reruns the generation process to obtain a new answer and verifies it."
        Adds a user message telling the LLM that its previous diagnosis was not
        supported by documentation, then re-runs one LLM step.
        """
        retry_prompt = (
            "Your previous diagnosis could not be verified against the retrieved "
            "troubleshooting documents. The evidence from documentation does not "
            "sufficiently support your conclusion. Please reconsider the available "
            "information and generate a different, more well-supported diagnosis. "
            "Focus on root causes that are explicitly mentioned or strongly implied "
            "by the retrieved documents and telemetry data."
        )
        self._llm._conversation_history.append({
            "role": "user",
            "content": retry_prompt,
        })
        return self._llm._next_llm_actions(max_empty_retries=2)

    def _add_source_citations(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add inline source citations to submit action's root_cause/solution.

        Paper: "Panda splits the output and the reference passages in individual
        sentences and provides inline citation if the output sentences are taken
        verbatim from the reference passages."
        """
        if not self._source_attribution or not self._grounding_context:
            return actions
        source_docs = self._grounding_context.documents
        if not source_docs:
            return actions
        result = []
        for action in actions:
            if action.get("api") == "submit":
                args = dict(action["args"])
                report = dict(args["report"])
                diagnosis = dict(report["diagnosis"])
                conditions = [dict(condition) for condition in diagnosis["conditions"]]
                conditions[0]["factor"] = self._source_attribution.attribute(
                    conditions[0]["factor"], source_docs
                )
                diagnosis["conditions"] = conditions
                report["diagnosis"] = diagnosis
                args["report"] = report
                result.append({"api": "submit", "args": args})
            else:
                result.append(action)
        return result

    def _format_tool_descriptions(self) -> str:
        """Format tool schemas into a readable description."""
        if not self._tools_schema:
            return "query_metrics, execute_sql, manage_instance, read_log, submit"
        parts = []
        for tool in self._tools_schema:
            func = tool.get("function", tool)
            name = func.get("name", "unknown")
            desc = func.get("description", "")
            parts.append(f"- {name}: {desc[:80]}")
        return "\n".join(parts)

    def _call_llm_for_verification(self, messages: List[Dict[str, str]]) -> str:
        """Call LLM for verification (separate from main conversation)."""
        self._ensure_llm()
        response = self._llm._call_llm(messages)
        if isinstance(response, dict):
            content = response.get("content", "")
            if isinstance(content, list):
                return " ".join(
                    block.get("text", "") for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                )
            return str(content)
        return str(response)

    # --- 诊断路径导出（linear 结构） ---

    def _export_prompts(self) -> Dict[str, str]:
        return {"system": self._system_prompt or "", "user": self._alert or ""}

    def _export_structure(self) -> Dict[str, Any]:
        return {
            "type": "linear",
            "evidence_count": len(self._evidence),
            "telemetry_features": [
                {
                    "metric_name": f.metric_name,
                    "trend": f.trend,
                    "text_summary": f.text_summary,
                }
                for f in self._telemetry_features
            ],
        }

    def _export_conversation(self) -> List[Dict[str, Any]]:
        if self._llm and hasattr(self._llm, "get_conversation_history"):
            return self._llm.get_conversation_history()
        return []
