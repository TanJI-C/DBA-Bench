from __future__ import annotations

import json

import pytest

from src.execution import environment
from src.execution.environment import TiDBEnv
from src.benchmark.run_table import _trace_metrics
from src.knowledge.tidb_knowledge_base import default_persist_dir


class FakeDeployment:
    run_id = "knowledge-tool"
    primary_tidb_endpoint = ("127.0.0.1", 4000)


def tool_names(env):
    return {schema["function"]["name"] for schema in env.get_tool_schemas()}


def knowledge_schema(env):
    return next(
        schema for schema in env.get_tool_schemas()
        if schema["function"]["name"] == "search_knowledge"
    )


def test_unified_tidb_tool_contract_always_exposes_search_knowledge():
    env = TiDBEnv(deployment=FakeDeployment())
    schema = knowledge_schema(env)["function"]["parameters"]

    assert "search_knowledge" in tool_names(env)
    assert "source_scope" not in schema["required"]
    assert {"query", "source_scope", "top_k", "kb_type", "component"} <= set(schema["properties"])


def test_search_dispatches_hierarchical_mode_and_stable_arguments(monkeypatch):
    instances = []

    class FakeKnowledgeBase:
        def __init__(self, *, knowledge_base_mode):
            self.mode = knowledge_base_mode
            instances.append(self)

        def query(self, **kwargs):
            return {
                "status": "success",
                "mode": self.mode,
                **kwargs,
                "results": [{
                    "rank": 1,
                    "score": 0.9,
                    "title": "Pending peer recovery",
                    "version": "8.1",
                    "kb_type": "diagnosis",
                    "component": "tikv",
                    "source_scope": "self_managed",
                    "content": "Inspect the current Region and Store evidence.",
                    "source_id": "tidb-docs-8.1:test.md#section",
                    "source_file": "test.md",
                    "pinned_source_url": "https://github.com/pingcap/docs/blob/d9124e/test.md",
                }],
            }

    monkeypatch.setattr(environment, "TiDBKnowledgeBase", FakeKnowledgeBase)
    env = TiDBEnv(deployment=FakeDeployment())

    result = json.loads(env.execute_action("search_knowledge", {
        "query": "pending peer region count",
        "source_scope": "self_managed",
        "kb_type": "diagnosis",
        "component": "tikv",
        "top_k": 3,
    }))

    assert result["status"] == "success"
    assert "mode" not in result
    assert result["source_scope"] == "self_managed"
    assert result["kb_type"] == "diagnosis"
    assert result["component"] == "tikv"
    assert result["top_k"] == 3
    assert "index" not in result
    assert "source_id" not in result["results"][0]
    assert "pinned_source_url" not in result["results"][0]
    assert result["results"] == [{
        "rank": 1,
        "score": 0.9,
        "title": "Pending peer recovery",
        "version": "8.1",
        "kb_type": "diagnosis",
        "component": "tikv",
        "source_scope": "self_managed",
        "content": "Inspect the current Region and Store evidence.",
    }]
    assert [instance.mode for instance in instances] == ["hierarchical"]


def test_search_reads_shared_unified_index_and_projects_agent_fields(monkeypatch):
    monkeypatch.setenv("AIOPS_TIDB_KB_BACKEND", "sqlite")
    persist_dir = default_persist_dir("sqlite", "hierarchical")
    if not (persist_dir / "manifest.json").is_file():
        pytest.skip(
            "shared unified knowledge index is not built; "
            "run scripts/build_tidb_knowledge_base.py --backend sqlite "
            "--knowledge-mode hierarchical"
        )
    env = TiDBEnv(deployment=FakeDeployment())

    result = json.loads(env.execute_action("search_knowledge", {
        "query": "recover-mvcc min_commit_ts start_ts",
        "source_scope": "self_managed",
        "top_k": 3,
        "kb_type": "recovery",
        "component": "tikv",
    }))

    assert result["status"] == "success"
    assert result["count"] > 0
    assert any("recover-mvcc" in row["content"] for row in result["results"])
    assert all(
        set(row) <= {
            "rank", "score", "title", "version", "kb_type", "component",
            "source_scope", "content",
        }
        for row in result["results"]
    )
    assert "index" not in result


def test_search_defaults_to_all_source_scope(monkeypatch):
    class FakeKnowledgeBase:
        def __init__(self, *, knowledge_base_mode):
            self.mode = knowledge_base_mode

        def query(self, **kwargs):
            return {"status": "success", "mode": self.mode, **kwargs, "results": []}

    monkeypatch.setattr(environment, "TiDBKnowledgeBase", FakeKnowledgeBase)
    env = TiDBEnv(deployment=FakeDeployment())

    result = json.loads(env.execute_action("search_knowledge", {"query": "memory quota"}))

    assert result["status"] == "success"
    assert result["source_scope"] == "all"


def test_missing_index_returns_clear_tool_error(monkeypatch):
    class MissingKnowledgeBase:
        def __init__(self, *, knowledge_base_mode):
            self.mode = knowledge_base_mode

        def query(self, **kwargs):
            raise FileNotFoundError("manifest is not built")

    monkeypatch.setattr(environment, "TiDBKnowledgeBase", MissingKnowledgeBase)
    env = TiDBEnv(deployment=FakeDeployment())

    result = json.loads(env.execute_action("search_knowledge", {"query": "memory quota"}))

    assert result["status"] == "error"
    assert "manifest is not built" in result["error"]
    assert "mode='hierarchical'" in result["error"]


def test_help_matches_unified_search_schema():
    env = TiDBEnv(deployment=FakeDeployment())

    help_payload = json.loads(env.help("search_knowledge"))

    assert help_payload["status"] == "success"
    assert {
        parameter["name"]
        for parameter in help_payload["definition"]["parameters"]
    } >= {
        "query",
        "source_scope",
        "kb_type",
        "component",
    }


def test_experiment_trace_counts_tidb_knowledge_calls():
    metrics = _trace_metrics({
        "turns": [{
            "actions": [
                {"api": "search_knowledge", "args": {}},
                {"api": "query_metrics", "args": {}},
            ],
        }],
    })

    assert metrics["knowledge_call_count"] == 1
