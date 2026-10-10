from __future__ import annotations

import json
from copy import deepcopy

import pytest

from src.agents.agent import LLMAgent
from src.agents.context_compaction import ContextCompactionConfig
from src.agents.loop_guard import (
    TOOL_LOOP_ABORT_MARKER,
    LoopGuardConfig,
    check_loop,
    round_signature,
)
from src.benchmark.manifest import load_manifest


def _sig(api: str, args: dict) -> str:
    return round_signature([{"api": api, "args": args}])


def test_default_guard_enabled_with_data_calibrated_thresholds():
    config = LoopGuardConfig()

    assert config.enabled is True
    assert config.consecutive_limit == 3
    assert config.min_ratio_rounds == 12
    assert config.min_distinct_ratio == 0.5


def test_disabled_guard_never_fires_on_degenerate_history():
    signatures = [_sig("query_metrics", {"metric_type": i % 2}) for i in range(40)]
    config = LoopGuardConfig(enabled=False)

    assert check_loop(signatures, config) is None


def test_consecutive_identical_rounds_fire_at_limit():
    config = LoopGuardConfig()
    same = _sig("query_metrics", {"metric_type": "cpu"})

    assert check_loop([same, same], config) is None
    assert "连续 3 轮" in check_loop([same, same, same], config)


def test_cycling_pattern_fires_via_distinct_ratio():
    # lwlock 真实模式：5 个查询周期性循环，相邻轮不相同
    config = LoopGuardConfig()
    cycle = [_sig("query_metrics", {"metric_type": f"m{i}"}) for i in range(5)]
    signatures = (cycle * 4)[:24]

    reason = check_loop(signatures, config)

    assert reason is not None
    assert "僵化" in reason


def test_healthy_mixed_history_never_fires():
    config = LoopGuardConfig()
    # 24 轮、18 种不同调用（ratio 0.75），含若干重复但不到连续 3 次
    signatures = [_sig("execute_sql", {"sql": i}) for i in range(18)]
    signatures.insert(5, signatures[2])
    signatures.insert(10, signatures[7])
    signatures.append(signatures[0])
    signatures.append(signatures[1])
    signatures.append(signatures[3])

    assert check_loop(signatures, config) is None


def test_ratio_rule_requires_min_rounds():
    config = LoopGuardConfig()
    # 11 轮全相同但未到 min_ratio_rounds：由连续规则接管，ratio 规则不触发
    same = _sig("query_metrics", {"metric_type": "cpu"})
    signatures = [same] * 11

    assert check_loop(signatures, config) is not None  # 连续规则先触发
    short = check_loop(signatures[:2] + [_sig("execute_sql", {"sql": 1})], config) is None
    assert short


def test_from_settings_validation():
    config = LoopGuardConfig.from_settings({"enabled": True, "min_distinct_ratio": 0.6})

    assert config.enabled is True
    assert config.min_distinct_ratio == 0.6
    assert LoopGuardConfig.from_settings(None).enabled is True

    with pytest.raises(ValueError, match="unknown keys"):
        LoopGuardConfig.from_settings({"unknown": 1})
    with pytest.raises(ValueError, match="min_ratio_rounds"):
        LoopGuardConfig.from_settings({"min_ratio_rounds": 0})
    with pytest.raises(ValueError, match="min_distinct_ratio"):
        LoopGuardConfig.from_settings({"min_distinct_ratio": 1.5})


class _FakeGateway:
    def __init__(self):
        self.calls = []

    def execute(self, api, args, *, thinking="", source=""):
        self.calls.append({"api": api, "args": args})
        return {"api": api, "status": "success", "result": {"data": "mock"}}


def _agent_with_cycling_replies() -> LLMAgent:
    agent = LLMAgent(url="mock", api_key="mock", model="mock-model")
    agent.init_env_gateway(_FakeGateway())
    cycle = [
        ("query_metrics", {"metric_type": f"metric_{i}", "target": "fleet"})
        for i in range(5)
    ]
    counter = {"n": 0}

    def fake_next(_retries):
        api, args = cycle[counter["n"] % 5]
        counter["n"] += 1
        return ("thinking", [{"api": api, "args": args}])

    agent._next_llm_actions = fake_next
    return agent


def test_agent_aborts_cycling_diagnosis_before_turn_limit():
    agent = _agent_with_cycling_replies()
    agent.max_turns = 40
    agent.context_compaction = ContextCompactionConfig(enabled=False)
    agent.loop_guard = LoopGuardConfig(min_ratio_rounds=12)

    with pytest.raises(RuntimeError, match=TOOL_LOOP_ABORT_MARKER):
        agent.solve()

    # 第 12 轮在多样性检查失败时于执行前终止：恰好执行了 11 轮的工具调用
    assert len(agent.gateway.calls) == 11


def test_loop_guard_switch_off_allows_full_run(monkeypatch):
    agent = _agent_with_cycling_replies()
    agent.max_turns = 12
    agent.loop_guard = LoopGuardConfig(enabled=False)
    monkeypatch.setattr(
        agent,
        "_next_final_submission",
        lambda max_empty_retries, agent_name: ("", {"diagnosis": "done"}),
    )

    assert agent.solve() == {"diagnosis": "done"}


def _native_round(index: int, metric: str, result_size: int = 5000) -> list[dict]:
    return [
        {"role": "assistant", "content": None, "tool_calls": [{
            "id": f"call-{index}", "type": "function",
            "function": {"name": "query_metrics",
                         "arguments": json.dumps({"metric_type": metric})},
        }]},
        {"role": "tool", "tool_call_id": f"call-{index}", "content": "x" * result_size},
    ]


def test_burst_warning_contains_dropped_tool_ledger_and_prohibition():
    agent = LLMAgent(url="mock", api_key="mock", model="mock-model")
    agent._conversation_history = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "inspect"},
        *(message for i in range(3) for message in _native_round(i, f"m{i}")),
    ]

    assert agent._apply_burst_compaction(reason="test") is True

    warning = agent._conversation_history[-1]["content"]
    assert warning.startswith("[上下文超限压缩]")
    assert "已执行过的工具调用" in warning
    assert "query_metrics" in warning
    assert '"metric_type": "m0"' in warning
    assert "禁止重复以上调用" in warning
    # 清单去重：3 个不同调用各出现一次
    assert warning.count("query_metrics") == 3


def test_burst_ledger_dedupes_repeated_calls():
    agent = LLMAgent(url="mock", api_key="mock", model="mock-model")
    agent._conversation_history = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "inspect"},
        *(message for _ in range(4) for message in _native_round(1, "same")),
    ]

    agent._apply_burst_compaction(reason="test")

    warning = agent._conversation_history[-1]["content"]
    assert warning.count("query_metrics") == 1


def test_manifest_accepts_loop_guard_settings(tmp_path):
    manifest_path = tmp_path / "guard.yaml"
    manifest_path.write_text(
        """
experiment_id: loop-guard
benchmark:
  systems: [postgresql]
  categories: [query_perf]
  scenarios: []
agents:
  - id: llm-guarded
    mode: llm
    model: gpt-test
    settings:
      context_compaction:
        enabled: true
        trigger_ratio: 0.8
        keep_recent_rounds: 3
        summary_max_output_tokens: 2048
        burst_ratio: 0.5
      loop_guard:
        enabled: true
        min_ratio_rounds: 12
        min_distinct_ratio: 0.5
repetitions: 1
seeds: [1]
""".strip(),
        encoding="utf-8",
    )

    manifest = load_manifest(manifest_path)

    assert manifest.agents[0].settings["loop_guard"]["enabled"] is True


def test_manifest_rejects_unknown_llm_setting_keys(tmp_path):
    manifest_path = tmp_path / "bad.yaml"
    manifest_path.write_text(
        """
experiment_id: bad-settings
benchmark:
  systems: [postgresql]
  categories: [query_perf]
  scenarios: []
agents:
  - id: llm-bad
    mode: llm
    model: gpt-test
    settings:
      unknown_key: {}
repetitions: 1
seeds: [1]
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unknown keys"):
        load_manifest(manifest_path)


def test_factory_builds_agent_with_loop_guard_from_settings(tmp_path):
    from src.agents.factory import build_benchmark_agent

    config_path = tmp_path / "llm_config.json"
    config_path.write_text(
        json.dumps({"gpt-test": {"url": "https://example.invalid/v1", "api_key": "k"}}),
        encoding="utf-8",
    )
    agent = build_benchmark_agent(
        agent_name="llm",
        model="gpt-test",
        config_path=str(config_path),
        settings={
            "context_compaction": {
                "enabled": False,
                "trigger_ratio": 0.9,
                "keep_recent_rounds": 3,
                "summary_max_output_tokens": 2048,
                "burst_ratio": 0.5,
            },
            "loop_guard": {"enabled": True, "min_ratio_rounds": 10},
        },
        seed=1,
    )

    assert agent.loop_guard.enabled is True
    assert agent.loop_guard.min_ratio_rounds == 10
    assert agent.context_compaction.enabled is False
