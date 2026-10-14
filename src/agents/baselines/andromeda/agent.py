"""Andromeda baseline agent for AiOpsBench.

Implements the Andromeda (SIGMOD 2025) pipeline as an interactive agent:
- Multi-Source Evidence Retrieval (dense retrieval from historical Q&A + manuals)
- Troublesome Telemetry Retrieval (STL anomaly detection + ranking)
- Two-phase Configuration Reasoning (knob identification → value recommendation)

The single-shot pipeline is mapped to a multi-turn state machine
to fit the AiOpsBench Orchestrator's interactive loop.
"""

import json
import logging
import os
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from src.agents.agent import BaseAgent, LLMAgent
from src.protocols.report import structured_submission
from src.agents.baselines.andromeda.prompts import (
    NO_ANOMALY_TEXT,
    NO_EVIDENCE_TEXT,
    PHASE1_KNOB_IDENTIFICATION_PROMPT,
    PHASE2_VALUE_RECOMMENDATION_PROMPT,
    SYSTEM_PROMPT,
)
from src.agents.baselines.andromeda.retriever import AndromedaRetriever
from src.agents.baselines.andromeda.telemetry import AndromedaTelemetry
from src.agents.baselines.andromeda.types import (
    AndromedaDiagnosis,
    KnobRecommendation,
)
from src.agents.baselines.telemetry import metric_names_from_tools, parse_metric_response

logger = logging.getLogger(__name__)


class Phase(Enum):
    COLLECT_TELEMETRY = "collect_telemetry"
    COLLECT_LOGS_CONFIG = "collect_logs_config"
    ANALYZE_AND_REASON = "analyze_and_reason"
    GET_KNOB_VALUES = "get_knob_values"
    SUBMIT = "submit"


METRICS_TO_COLLECT = [
    "cpu", "memory", "disk_io", "active_connections", "disk_usage",
    "qps", "cache_hit_ratio",
]


class AndromedaAgent(BaseAgent):
    """Andromeda baseline agent implementing the paper's RAG + STL + two-phase reasoning.

    State machine phases:
      1. collect_telemetry — query_metrics for all metric types
      2. collect_logs_config — read_log + get_config
      3. analyze_and_reason — STL → retrieval → Phase 1 → Phase 2
      4. get_knob_values — (optional) get_config for identified knobs
      5. submit — submit final diagnosis
    """

    use_native_tools = True

    def __init__(
        self,
        model: str,
        provider: Optional[str] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        config_path: str = "config/llm_config.json",
        use_native_tools: bool = True,
        knowledge_dir: Optional[str] = None,
        retrieval_model: str = "BAAI/bge-base-en-v1.5",
        retrieval_top_k: int = 5,
        stl_period: int = 60,
        anomaly_threshold: float = 3.0,
        db_type: str = "postgresql",
        enable_log: bool = False,
        log_dir: Optional[str] = None,
    ):
        super().__init__()
        self.use_native_tools = use_native_tools
        self.db_type = db_type
        self._metrics_to_collect = list(METRICS_TO_COLLECT)

        self._llm_kwargs = dict(
            model=model,
            provider=provider,
            url=url,
            api_key=api_key,
            config_path=config_path,
            use_native_tools=False,
        )
        self._llm: Optional[LLMAgent] = None

        if knowledge_dir is None:
            knowledge_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                ))),
                "knowledge", "andromeda",
            )

        self._retriever = AndromedaRetriever(
            model_name=retrieval_model,
            knowledge_dir=knowledge_dir,
            top_k=retrieval_top_k,
        )
        self._telemetry = AndromedaTelemetry(
            period=stl_period,
            anomaly_threshold=anomaly_threshold,
        )

        self._phase = Phase.COLLECT_TELEMETRY
        self._metrics_collected: List[str] = []
        self._logs_config_received: int = 0
        self._log_text: str = ""
        self._history_source: str = "component_log"
        self._history_sources: Tuple[str, ...] = ()
        self._history_enabled = False
        self._history_window_seconds = 60
        self._history_limit = 100
        self._config_text: str = ""
        self._diagnosis: Optional[AndromedaDiagnosis] = None
        self._alert_text: str = ""
        self._system_prompt: str = ""

        self.enable_log = enable_log
        self.log_dir = log_dir

    # --- BaseAgent interface ---

    def set_system_prompt(self, system_prompt: str) -> None:
        self._system_prompt = system_prompt

    def set_user_prompt(self, user_prompt: str) -> None:
        self._alert_text = user_prompt

    def set_tools(self, tools: List[Dict[str, Any]]) -> None:
        names = {
            str((tool.get("function", tool) or {}).get("name", ""))
            for tool in tools
            if isinstance(tool, dict)
        }
        if "query_metrics" in names:
            self._metrics_to_collect = list(metric_names_from_tools(tools))
        self._history_enabled = "query_history" in names
        self._tools_schema = list(tools)

    def reset(self) -> None:
        """Reset agent state for reuse across scenarios."""
        self._phase = Phase.COLLECT_TELEMETRY
        self._metrics_collected = []
        self._logs_config_received = 0
        self._log_text = ""
        self._history_source = "component_log"
        self._history_sources = ()
        self._history_window_seconds = 60
        self._history_limit = 100
        self._config_text = ""
        self._diagnosis = None
        self._alert_text = ""
        self._system_prompt = ""
        self._telemetry = AndromedaTelemetry(
            period=self._telemetry.period,
            anomaly_threshold=self._telemetry.anomaly_threshold,
        )
        self.action_history = []
        if self._llm:
            self._llm.reset_conversation()

    def parse_action(self, raw_input: str) -> Dict[str, Any]:
        data = json.loads(raw_input)
        if "action" in data:
            return data["action"]
        if "api" in data:
            return data
        raise ValueError(f"Andromeda action has neither action nor api: {data!r}")

    def solve(self) -> Dict[str, Any]:
        """Andromeda pipeline mapped to a self-driven flow:
        collect telemetry → collect logs/config → STL+RAG+two-phase reasoning →
        (optional) fetch knob values → return diagnosis submission.
        """
        # Phase 1: telemetry collection for STL anomaly detection
        for metric in self._metrics_to_collect:
            result = self.execute(
                "query_metrics", {"metric_type": metric},
                thinking=f"[Andromeda] Collecting telemetry: {metric}", source="andromeda",
            )
            self._telemetry.add_metric_data(metric, result)
            self._metrics_collected.append(metric)

        # Phase 2: logs + configuration
        if self._history_enabled:
            self._log_text = "(historical log window will be selected after telemetry analysis)"
        else:
            self._log_text = self._result_to_text(self.execute(
                "read_log", {"log_type": "pg_log", "lines": 100},
                thinking="[Andromeda] Collecting execution logs", source="andromeda",
            )) or "(no logs available)"
        config_query = "SHOW VARIABLES" if self.db_type == "tidb" else "SHOW ALL"
        self._config_text = self._result_to_text(self.execute(
            "execute_sql", {"sql_query": config_query},
            thinking="[Andromeda] Collecting current configuration", source="andromeda",
        )) or "(no config available)"

        # Phase 3: STL + retrieval + two-phase reasoning (internal LLM/text)
        anomalies = self._telemetry.detect_anomalies()
        anomaly_texts = self._telemetry.get_anomaly_texts()
        if anomaly_texts:
            ranked_texts = self._retriever.rank_telemetry_texts(self._alert_text, anomaly_texts)
            telemetry_summary = "\n".join(f"- {t}" for t in ranked_texts[:5])
        else:
            telemetry_summary = NO_ANOMALY_TEXT

        if self._history_enabled:
            self._load_history_contract()
            history_start, history_end = self._history_window(anomalies)
            self._log_text = self._result_to_text(self.execute(
                "query_history",
                {
                    "source": self._history_source,
                    "start_timestamp": history_start,
                    "end_timestamp": history_end,
                    "limit": self._history_limit,
                },
                thinking="[Andromeda] Querying the candidate UTC history window",
                source="andromeda",
            )) or "(no historical log records)"

        qa_docs = self._retriever.retrieve_by_type(self._alert_text, "historical_qa")
        manual_docs = self._retriever.retrieve_by_type(self._alert_text, "manual")
        qa_text = "\n\n".join(f"[{d.source}] {d.content}" for d in qa_docs) if qa_docs else NO_EVIDENCE_TEXT
        manual_text = "\n\n".join(f"[{d.source}] {d.content}" for d in manual_docs) if manual_docs else NO_EVIDENCE_TEXT

        phase1_prompt = PHASE1_KNOB_IDENTIFICATION_PROMPT.format(
            alert_text=self._alert_text,
            telemetry_text=telemetry_summary,
            historical_qa_text=qa_text,
            manual_text=manual_text,
            log_text=self._log_text[:2000] if self._log_text else "No logs available.",
        )
        phase1_knobs = self._parse_phase1_knobs(self._call_llm(phase1_prompt))

        evidence_text = f"Historical Q&A:\n{qa_text}\n\nManual:\n{manual_text}"
        phase2_prompt = PHASE2_VALUE_RECOMMENDATION_PROMPT.format(
            alert_text=self._alert_text,
            phase1_knobs=json.dumps(phase1_knobs),
            current_config=self._config_text[:2000] if self._config_text else "Not available.",
            telemetry_text=telemetry_summary,
            evidence_text=evidence_text[:3000],
        )
        self._diagnosis = self._parse_phase2_diagnosis(
            self._call_llm(phase2_prompt), anomalies, phase1_knobs
        )

        # Phase 4: build submission
        self._phase = Phase.SUBMIT
        return self._build_submission()

    @staticmethod
    def _result_to_text(result: Any) -> str:
        if isinstance(result, dict):
            raw = result.get("result", result.get("content", result.get("output", result)))
        else:
            raw = result
        if isinstance(raw, (list, dict)):
            return json.dumps(raw, ensure_ascii=False, default=str)
        return str(raw) if raw is not None else ""

    def _build_submission(self) -> Dict[str, Any]:
        """Build the final diagnosis submission from the reasoning result."""
        if self._diagnosis:
            root_cause = self._diagnosis.root_cause
            recommendations = []
            for rec in self._diagnosis.knob_recommendations:
                recommendations.append(
                    f"Set {rec.knob_name} = {rec.recommended_value} "
                    f"(currently: {rec.current_value or 'unknown'}). "
                    f"Reason: {rec.rationale}"
                )
            submit_text = (
                f"Root Cause: {root_cause}\n"
                f"Recommendations:\n" +
                "\n".join(f"  - {r}" for r in recommendations)
            )
        else:
            submit_text = f"Unable to determine root cause from available evidence. Alert: {self._alert_text}"
        evidence = self._telemetry.get_anomaly_texts()
        return structured_submission(
            factor=root_cause if self._diagnosis else "undetermined",
            entity="database",
            evidence=evidence,
            changes=recommendations,
            verification=["Andromeda telemetry was collected after remediation"],
            summary=submit_text,
        )

    def _history_window(self, anomalies: List[Any]) -> Tuple[str, str]:
        if anomalies:
            raw_timestamp = anomalies[0].timestamp
            if raw_timestamp is None:
                raise RuntimeError("TiDB Andromeda anomaly does not contain a timestamp")
            try:
                timestamp_ms = int(raw_timestamp)
            except ValueError:
                parsed = datetime.fromisoformat(str(raw_timestamp).replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                timestamp_ms = int(parsed.timestamp() * 1000)
        else:
            timestamps = []
            for raw in self._telemetry._raw_metrics.values():
                if isinstance(raw, dict) and raw.get("kind") == "series":
                    timestamps.extend(
                        timestamp
                        for series in parse_metric_response(raw)
                        for timestamp in series.timestamps_ms
                    )
            if not timestamps:
                raise RuntimeError("TiDB Andromeda history query needs a metric timestamp window")
            timestamp_ms = timestamps[-1]
        available_start_ms = None
        available_end_ms = None
        for raw in self._telemetry._raw_metrics.values():
            if isinstance(raw, dict) and isinstance(raw.get("window"), dict):
                window = raw["window"]
                if window.get("available_start") and window.get("available_end"):
                    start = datetime.strptime(window["available_start"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    end = datetime.strptime(window["available_end"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    available_start_ms = int(start.timestamp() * 1000)
                    available_end_ms = int(end.timestamp() * 1000)
                    break
        start_ms = timestamp_ms - 30_000
        end_ms = timestamp_ms + 30_000
        if available_start_ms is not None:
            start_ms = max(start_ms, available_start_ms)
        if available_end_ms is not None:
            end_ms = min(end_ms, available_end_ms)
        max_window_ms = self._history_window_seconds * 1000
        if end_ms - start_ms > max_window_ms:
            half_window_ms = max_window_ms // 2
            start_ms = timestamp_ms - half_window_ms
            end_ms = start_ms + max_window_ms
            if available_start_ms is not None and start_ms < available_start_ms:
                start_ms = available_start_ms
                end_ms = start_ms + max_window_ms
            if available_end_ms is not None and end_ms > available_end_ms:
                end_ms = available_end_ms
                start_ms = end_ms - max_window_ms
        if start_ms >= end_ms:
            raise RuntimeError(
                "TiDB Andromeda candidate history window is empty after visible-range clipping: "
                f"timestamp_ms={timestamp_ms}, available=({available_start_ms},{available_end_ms})"
            )
        history_functions = [
            tool.get("function", tool)
            for tool in getattr(self, "_tools_schema", [])
            if isinstance(tool, dict)
        ]
        source_values = next(
            (
                function.get("parameters", {}).get("properties", {}).get("source", {}).get("enum")
                for function in history_functions
                if function.get("name") == "query_history"
            ),
            None,
        )
        if source_values:
            if "topsql" in source_values:
                self._history_source = "topsql"
            elif "slow_queries" in source_values:
                self._history_source = "slow_queries"
        return (
            datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            datetime.fromtimestamp(end_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        )

    def _load_history_contract(self) -> None:
        result = self.execute(
            "help",
            {"tool_name": "query_history"},
            thinking="[Andromeda] Reading the bounded history contract",
            source="andromeda",
        )
        runtime = result["definition"]["runtime"]
        max_records = runtime["max_history_records_per_response"]
        enabled_sources = tuple(runtime["enabled_sources"])
        if not isinstance(max_records, int) or max_records <= 0:
            raise RuntimeError(f"Andromeda history max record limit is invalid: runtime={runtime!r}")
        if not enabled_sources:
            raise RuntimeError(f"Andromeda history has no enabled sources: runtime={runtime!r}")
        self._history_sources = enabled_sources
        if self._history_source not in enabled_sources:
            self._history_source = next(
                source
                for source in ("topsql", "slow_queries", "component_log")
                if source in enabled_sources
            )
        self._history_window_seconds = 60
        self._history_limit = min(100, max_records)

    # --- LLM interaction ---

    def _call_llm(self, prompt: str) -> str:
        """Call the underlying LLM for one-shot reasoning (lazy initialization)."""
        if self._llm is None:
            self._llm = LLMAgent(**self._llm_kwargs)
        return self._llm.call_text(prompt, system_prompt=SYSTEM_PROMPT)

    # --- Response parsing ---

    def _parse_phase1_knobs(self, llm_output: str) -> List[str]:
        """Extract knob names from Phase 1 LLM response."""
        try:
            json_str = self._extract_json(llm_output)
            data = json.loads(json_str)
            knobs = data.get("knobs", [])
            if isinstance(knobs, list):
                return [str(k) for k in knobs]
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
        # Fallback: look for knob-like patterns
        import re
        patterns = re.findall(r'[a-z_]+(?:_[a-z_]+)+', llm_output)
        return list(set(p for p in patterns if len(p) > 5))[:5]

    def _parse_phase2_diagnosis(
        self, llm_output: str, anomalies: List, phase1_knobs: List[str]
    ) -> AndromedaDiagnosis:
        """Parse Phase 2 LLM response into AndromedaDiagnosis."""
        recommendations = []
        root_cause = "Configuration issue detected"

        try:
            json_str = self._extract_json(llm_output)
            data = json.loads(json_str)
            root_cause = data.get("root_cause", root_cause)
            for rec in data.get("recommendations", []):
                recommendations.append(KnobRecommendation(
                    knob_name=rec.get("knob", ""),
                    current_value=rec.get("current_value"),
                    recommended_value=rec.get("recommended_value", ""),
                    rationale=rec.get("rationale", ""),
                ))
        except (json.JSONDecodeError, TypeError, ValueError):
            root_cause = llm_output[:200] if llm_output else root_cause

        return AndromedaDiagnosis(
            root_cause=root_cause,
            anomalies=anomalies,
            knob_recommendations=recommendations,
            phase1_knobs=phase1_knobs,
        )

    def _extract_json(self, text: str) -> str:
        """Extract JSON block from LLM output (may be wrapped in markdown)."""
        import re
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text

    # --- 诊断路径导出（linear 结构） ---

    def _export_prompts(self) -> Dict[str, str]:
        return {"system": self._system_prompt or "", "user": self._alert_text or ""}

    def _export_structure(self) -> Dict[str, Any]:
        structure: Dict[str, Any] = {"type": "linear", "phase": self._phase.value}
        if self._diagnosis is not None:
            structure["diagnosis"] = {
                "root_cause": self._diagnosis.root_cause,
                "phase1_knobs": self._diagnosis.phase1_knobs,
                "recommendations": [
                    {
                        "knob_name": r.knob_name,
                        "current_value": r.current_value,
                        "recommended_value": r.recommended_value,
                        "rationale": r.rationale,
                    }
                    for r in self._diagnosis.knob_recommendations
                ],
            }
        return structure
