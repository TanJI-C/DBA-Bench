"""Integration tests for the TiDB knowledge graph and its use by DbaiopsAgent.

All tests are mock-only: no LLM calls, no database deployment.
"""

import hashlib
import json
import os
import re
import sys

import pytest

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.agents.baselines.dbaiops.adf import AdaptiveDetectorFunction
from src.agents.baselines.dbaiops.graph import ExperienceGraph
from src.agents.baselines.dbaiops.retriever import ExperienceRetriever
from src.agents.agent import LLMAgent

TIDB_GRAPH_PATH = os.path.join(
    project_root, "data", "knowledge_graph", "tidb_experience_graph.json"
)
PROVENANCE_PATH = os.path.join(
    project_root, "data", "knowledge_graph", "tidb_graph_provenance.jsonl"
)
TIDB_GRAPH_SHA256 = "249ce41f037628d91b9bc9374689bd5c9a45087dff26d00cafeb419ed857243c"

METRIC_CATALOG = {
    "active_connections", "cpu", "disk_io", "disk_usage", "lightning_progress",
    "lightning_throughput", "lightning_workers", "memory", "network_io",
    "pd_leader_distribution", "pd_region_activity", "pd_region_inventory",
    "plan_cardinality", "qps", "query_latency", "resource_group_throttle",
    "resource_group_usage", "statistics_state", "ticdc_progress", "ticdc_sink",
    "transaction_commit", "workload_profile",
}
TOOL_APIS = {"query_metrics", "execute_sql", "query_history",
             "manage_instance", "manage_cluster", "read_log"}

MOCK_REPORT = "Mock TiDB diagnosis report with root cause and recovery solution."

TIDB_TOOL_SURFACE = [
    {"function": {"name": "query_metrics"}},
    {"function": {"name": "execute_sql"}},
    {"function": {"name": "query_history"}},
    {"function": {"name": "manage_cluster"}},
    {"function": {"name": "read_log"}},
]


class FakeTiDBGateway:
    """Gateway returning realistic result shapes for any TiDB tool call."""

    def __init__(self):
        self.calls = []

    def execute(self, api, args, *, thinking="", source=""):
        self.calls.append((api, args))
        if api == "help":
            return {
                "status": "success",
                "definition": {"runtime": {
                    "available_start": "2026-09-08 00:00:00",
                    "available_end": "2026-09-08 01:00:00",
                    "max_history_records_per_response": 100,
                    "enabled_sources": ["topsql", "slow_queries", "component_log"],
                }},
            }
        if api == "query_metrics":
            metric = args.get("metric_type", "unknown")
            return {
                "status": "success",
                "metric": metric,
                "kind": "series",
                "series": {
                    "cluster": {"timestamps": [1, 2, 3, 4],
                                "value": [40.0, 41.0, 40.5, 41.2]}
                },
            }
        if api == "query_history":
            return {"status": "success", "kind": "records",
                    "records": [{"query": "SELECT 1", "duration": 12.0}]}
        if api == "execute_sql":
            return {"status": "success", "columns": ["count"],
                    "result": [[1]]}
        return {"status": "success", "message": "ok"}


def make_inner_llm(monkeypatch, replies, report=MOCK_REPORT):
    inner_llm = LLMAgent(model="mock", url="mock", api_key="mock", use_native_tools=True)
    reply_iter = iter(replies)
    monkeypatch.setattr(
        inner_llm, "_next_llm_actions", lambda max_empty_retries: next(reply_iter)
    )
    monkeypatch.setattr(
        inner_llm, "call_text", lambda prompt, system_prompt=None: report
    )
    return inner_llm


class TestTidbKnowledgeGraphArtifact:
    """Artifact-level contract for the TiDB experience graph."""

    def test_loads_with_expected_scale(self):
        graph = ExperienceGraph(TIDB_GRAPH_PATH)
        assert len(graph.nodes) >= 900
        assert len(graph.edges) >= 1800
        assert len(graph.get_trigger_vertices()) >= 200

    def test_metric_nodes_are_catalog_closed(self):
        graph = ExperienceGraph(TIDB_GRAPH_PATH)
        metrics = graph.get_nodes_by_type("metric")
        assert len(metrics) == len(METRIC_CATALOG)
        for node in metrics:
            metric_type = node.attributes["metric_type"]
            assert metric_type in METRIC_CATALOG, node.id
            assert node.id == f"metric_{metric_type}"

    def test_tool_nodes_use_tidb_apis_only(self):
        graph = ExperienceGraph(TIDB_GRAPH_PATH)
        for node in graph.get_nodes_by_type("tool"):
            api = node.attributes["api"]
            assert api in TOOL_APIS, node.id

    def test_no_postgresql_objects(self):
        blob = open(TIDB_GRAPH_PATH, encoding="utf-8").read()
        for marker in ("pg_stat_", "pg_locks", "pg_catalog"):
            assert marker not in blob

    def test_no_source_identity_in_agent_facing_graph(self):
        blob = open(TIDB_GRAPH_PATH, encoding="utf-8").read().lower()
        assert not re.search(r"kb[-_ ]?first", blob)

    def test_provenance_sidecar_tracks_corpus(self):
        referenced = set()
        with open(PROVENANCE_PATH, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                referenced |= set(entry["source_files"])
        assert len(referenced) >= 1200
        for path in list(referenced)[:50]:
            assert os.path.exists(os.path.join(project_root, path)), path

    def test_file_sha256_matches_pinned_value(self):
        digest = hashlib.sha256(
            open(TIDB_GRAPH_PATH, "rb").read()
        ).hexdigest()
        assert digest == TIDB_GRAPH_SHA256

    def test_retrieval_pipeline_serves_trigger_paths(self):
        graph = ExperienceGraph(TIDB_GRAPH_PATH)
        retriever = ExperienceRetriever(graph, AdaptiveDetectorFunction())
        # trigger_slow_query is a cross-part anchor whose paths currently lack
        # metric/tool leaves — the known enrichment gap.
        for trigger_id in ("trigger_resource_group_throttling",
                           "trigger_runaway_query"):
            retriever.initialize(trigger_id)
            actions = retriever.take_pending_actions()
            evidence = retriever.get_experience_evidence()
            assert actions, trigger_id
            assert evidence, trigger_id


class TestDbaiopsAgentTidbIntegration:
    """DbaiopsAgent selects the TiDB graph for TiDB tool surfaces (mock-only)."""

    def test_tidb_surface_selects_tidb_graph_and_solves(self, monkeypatch):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent

        agent = DbaiopsAgent(model="mock", graph_path="data/knowledge_graph/pg_experience_graph.json")
        agent.set_tools(TIDB_TOOL_SURFACE)
        agent.set_user_prompt(
            "Resource group rg1 RU exceeded, queries are throttled and waiting on quota"
        )
        gateway = FakeTiDBGateway()
        agent.init_env_gateway(gateway)
        agent._llm = make_inner_llm(monkeypatch, replies=[
            ("Evidence is sufficient.", [{"api": "submit", "args": {}}]),
        ])

        submission = agent.solve()

        assert agent._is_tidb is True
        # TiDB graph selected: PG-only metric absent, TiDB trigger matched
        assert "metric_cache_hit_ratio" not in agent._graph.nodes
        assert "trigger_resource_group_throttling" in agent._graph.nodes
        assert agent._matched_trigger.id == "trigger_resource_group_throttling"
        assert submission["report"]["summary"] == MOCK_REPORT
        # TiDB history contract is primed before evolution
        assert gateway.calls[0][0] == "help"

    def test_tidb_action_adaptation_rewrites_history_queries(self):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent

        agent = DbaiopsAgent(model="mock", graph_path="data/knowledge_graph/pg_experience_graph.json")
        agent.set_tools(TIDB_TOOL_SURFACE)
        agent._history_window = ("2026-09-08 00:00:00", "2026-09-08 01:00:00")
        adapted = agent._adapt_tidb_action({
            "api": "execute_sql",
            "args": {"sql_query":
                     "SELECT query FROM information_schema.cluster_statements_summary"},
        })
        assert adapted["api"] == "query_history"
        assert adapted["args"]["source"] in {"topsql", "slow_queries", "component_log"}
        untouched = agent._adapt_tidb_action({
            "api": "execute_sql",
            "args": {"sql_query": "SHOW CONFIG"},
        })
        assert untouched["api"] == "execute_sql"

    def test_pg_surface_keeps_pg_graph(self, monkeypatch):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent

        agent = DbaiopsAgent(model="mock", graph_path="data/knowledge_graph/pg_experience_graph.json")
        agent.set_tools([
            {"function": {"name": "query_metrics"}},
            {"function": {"name": "execute_sql"}},
            {"function": {"name": "manage_instance"}},
        ])
        agent.set_user_prompt("Slow query detected, full table scan on orders table")
        agent.init_env_gateway(FakeTiDBGateway())
        agent._llm = make_inner_llm(monkeypatch, replies=[
            ("Investigating.", []),
        ])

        submission = agent.solve()

        assert agent._is_tidb is False
        assert "metric_cache_hit_ratio" in agent._graph.nodes
        assert agent._matched_trigger.id == "trigger_index_problem"
        assert submission["report"]["summary"] == MOCK_REPORT

    def test_factory_accepts_tidb_graph_manifest(self, monkeypatch, tmp_path):
        from src.agents.factory import build_experiment_agent
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent

        settings = {
            "adf_score_threshold": 1.2,
            "adf_theta": 10.0,
            "frequency_m": 3,
            "frequency_n": 5,
            "graph_path": "data/knowledge_graph/tidb_experience_graph.json",
            "graph_sha256": TIDB_GRAPH_SHA256,
            "max_evolution_depth": 4,
            "top_k": 5,
        }
        monkeypatch.setenv("AIOPS_AGENT_MODE", "dbaiops")
        monkeypatch.setenv("AIOPS_AGENT_SETTINGS", json.dumps(settings))
        monkeypatch.setenv("AIOPS_SEED", "20260718")

        agent = build_experiment_agent("test-model-a", "config/llm_config.json")

        assert isinstance(agent, DbaiopsAgent)
        assert agent.graph_path == "data/knowledge_graph/tidb_experience_graph.json"
        graph = ExperienceGraph(agent.graph_path)
        assert len(graph.get_trigger_vertices()) >= 200
