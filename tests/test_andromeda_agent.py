"""Tests for Andromeda baseline agent."""

import json
import os
import sys
import pytest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.baselines.andromeda.types import MetricAnomaly, AndromedaDiagnosis
from src.agents.baselines.andromeda.telemetry import AndromedaTelemetry
from src.agents.baselines.andromeda.retriever import AndromedaRetriever, RetrievedDocument
from src.agents.baselines.andromeda.agent import AndromedaAgent, Phase


class TestAndromedaTypes:
    def test_metric_anomaly_to_text(self):
        anomaly = MetricAnomaly(
            metric_name="cpu",
            timestamp="2024-01-01T00:00:00",
            value=95.0,
            expected_range=(10.0, 80.0),
            residual=15.0,
            severity=3.0,
        )
        text = anomaly.to_text()
        assert "cpu" in text
        assert "95" in text
        assert "above" in text
        assert "3.0" in text

    def test_metric_anomaly_below(self):
        anomaly = MetricAnomaly(
            metric_name="cache_hit_ratio",
            timestamp=None,
            value=0.5,
            expected_range=(0.9, 1.0),
            residual=-0.4,
            severity=4.0,
        )
        text = anomaly.to_text()
        assert "below" in text
        assert "cache_hit_ratio" in text


class TestAndromedaTelemetry:
    def test_scalar_anomaly_check(self):
        telemetry = AndromedaTelemetry()
        telemetry.add_metric_data("cache_hit_ratio", json.dumps({"value": 0.5}))
        anomalies = telemetry.detect_anomalies()
        assert len(anomalies) >= 1
        assert anomalies[0].metric_name == "cache_hit_ratio"

    def test_no_anomaly_for_normal_values(self):
        telemetry = AndromedaTelemetry()
        telemetry.add_metric_data("cpu", json.dumps({"value": 50.0}))
        anomalies = telemetry.detect_anomalies()
        assert len(anomalies) == 0

    def test_anomaly_texts(self):
        telemetry = AndromedaTelemetry()
        telemetry.add_metric_data("cpu", json.dumps({"value": 99.0}))
        telemetry.detect_anomalies()
        texts = telemetry.get_anomaly_texts()
        assert len(texts) >= 1
        assert "cpu" in texts[0]


class TestAndromedaRetriever:
    def test_keyword_fallback(self):
        retriever = AndromedaRetriever(model_name="nonexistent", top_k=3)
        retriever._documents = [
            RetrievedDocument(content="shared_buffers memory config", source="test.md", doc_type="manual"),
            RetrievedDocument(content="unrelated content about networking", source="net.md", doc_type="manual"),
            RetrievedDocument(content="work_mem sort operations memory", source="test2.md", doc_type="manual"),
        ]
        results = retriever._keyword_retrieve("memory configuration")
        assert len(results) >= 1
        assert "memory" in results[0].content.lower()


class TestAndromedaAgent:
    def test_initial_phase(self):
        agent = AndromedaAgent(model="mock-model", config_path="config/llm_config.json")
        assert agent._phase == Phase.COLLECT_TELEMETRY

    def test_solve_collects_telemetry_then_reasons(self):
        """solve() should query all telemetry metrics, logs/config, then reason and submit."""
        agent = AndromedaAgent(model="mock-model", config_path="config/llm_config.json")

        calls = []

        class FakeGateway:
            def execute(self, api, args, *, thinking="", source=""):
                calls.append({"api": api, "args": args})
                if api == "query_metrics":
                    return {"result": json.dumps({"value": 50}), "metric_type": args.get("metric_type")}
                return {"result": "ok"}

        # Stub internal reasoning so the test stays offline.
        agent._call_llm = lambda prompt: '{"knobs": [], "root_cause": "test", "recommendations": []}'

        agent.init_env_gateway(FakeGateway())
        agent.set_user_prompt("high cpu alert")
        submission = agent.solve()

        metric_calls = [c for c in calls if c["api"] == "query_metrics"]
        assert len(metric_calls) == 7
        assert {call["args"]["metric_type"] for call in metric_calls} == {
            "cpu", "memory", "disk_io", "active_connections", "disk_usage",
            "qps", "cache_hit_ratio",
        }
        assert any(c["api"] == "read_log" for c in calls)
        assert any(c["api"] == "execute_sql" for c in calls)
        assert submission["report"]["diagnosis"]["conditions"][0]["factor"] == "test"
        assert agent._phase == Phase.SUBMIT
