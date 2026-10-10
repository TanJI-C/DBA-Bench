from __future__ import annotations

import json
import hashlib
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.baselines.dbaiops.agent import DbaiopsAgent
from src.agents.baselines.dbot.agent import DbotAgent
from src.agents.agent import LLMAgent
from src.agents.factory import build_experiment_agent


DBOT_KNOWLEDGE_SHA256 = "adb91efde4bd4811e4c5a202d201275a2642a77800c686786cdbb1ea0e158f40"
DBAIOPS_GRAPH_SHA256 = "ff7699c317673bc503d5e09cf5da20982cc09e2dad3c2ff23c9d12988baaebae"


def test_experiment_factory_builds_seeded_dbot(monkeypatch, tmp_path):
    knowledge = tmp_path / "CpuExpert.jsonl"
    knowledge.write_text(
        '{"expert_name":"CpuExpert","cause_name":"cpu","desc":"high CPU","metrics":"cpu","steps":"inspect topsql"}\n',
        encoding="utf-8",
    )
    knowledge_hash = hashlib.sha256(knowledge.read_bytes()).hexdigest()
    config = tmp_path / "llm_config.json"
    config.write_text(
        json.dumps({"test-model-a": {"url": "http://mock.invalid/v1", "api_key": "mock"}}),
        encoding="utf-8",
    )
    settings = {
        "knowledge_paths": [str(knowledge)],
        "knowledge_sha256": {str(knowledge): knowledge_hash},
        "knowledge_top_k": 5,
        "max_hired_experts": 2,
        "max_parallel_experts": 2,
        "mode": "dbot_code",
        "search": {
            "epsilon_new_node": 0.3,
            "simulation_count": 2,
            "single_chain_max_step": 24,
            "vote_candidates": 2,
        },
        "use_native_tools": True,
    }
    monkeypatch.setenv("AIOPS_AGENT_MODE", "dbot")
    monkeypatch.setenv("AIOPS_AGENT_SETTINGS", json.dumps(settings))
    monkeypatch.setenv("AIOPS_SEED", "20260718")

    agent = build_experiment_agent("test-model-a", str(config))

    assert isinstance(agent, DbotAgent)
    assert agent.seed == 20260718
    assert agent.required_tool_profile == "db_gpt"
    assert agent._search_config.simulation_count == 2


def test_experiment_factory_builds_frozen_dbaiops(monkeypatch, tmp_path):
    settings = {
        "adf_score_threshold": 1.2,
        "adf_theta": 10.0,
        "frequency_m": 3,
        "frequency_n": 5,
        "graph_path": "data/knowledge_graph/pg_experience_graph.json",
        "graph_sha256": DBAIOPS_GRAPH_SHA256,
        "max_evolution_depth": 4,
        "top_k": 5,
    }
    monkeypatch.setenv("AIOPS_AGENT_MODE", "dbaiops")
    monkeypatch.setenv("AIOPS_AGENT_SETTINGS", json.dumps(settings))
    monkeypatch.setenv("AIOPS_SEED", "20260718")

    config = tmp_path / "llm_config.json"
    config.write_text(
        json.dumps({"test-model-a": {"url": "http://mock.invalid/v1", "api_key": "mock"}}),
        encoding="utf-8",
    )

    agent = build_experiment_agent("test-model-a", str(config))

    assert isinstance(agent, DbaiopsAgent)
    assert agent.graph_path == "data/knowledge_graph/pg_experience_graph.json"
    assert agent.max_evolution_depth == 4
    assert agent._top_k == 5


def test_experiment_factory_accepts_explicit_reasoning_effort(monkeypatch, tmp_path):
    config = tmp_path / "llm_config.json"
    config.write_text(
        json.dumps({"test-model-c": {"url": "http://mock.invalid/v1", "api_key": "mock"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("AIOPS_AGENT_MODE", "llm")
    monkeypatch.setenv("AIOPS_AGENT_SETTINGS", "{}")
    monkeypatch.setenv("AIOPS_SEED", "20260822")
    monkeypatch.setenv("AIOPS_REASONING_EFFORT", "high")

    agent = build_experiment_agent(
        "test-model-c",
        str(config),
        reasoning_effort="xhigh",
    )

    assert isinstance(agent, LLMAgent)
    assert agent.reasoning_effort == "xhigh"
