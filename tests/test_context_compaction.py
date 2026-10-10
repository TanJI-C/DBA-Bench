from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Dict

import pytest

from src.agents.agent import LLMAgent
from src.agents.context_compaction import (
    CONTEXT_SUMMARY_SYSTEM_PROMPT,
    DEFAULT_CONTEXT_WINDOW_TOKENS,
    SUMMARY_MESSAGE_PREFIX,
    ContextCompactionConfig,
    ContextCompactionError,
    SUMMARY_HEADINGS,
    build_summary_user_prompt,
    select_compaction,
    split_history_into_rounds,
)
from src.benchmark.manifest import load_manifest


def _native_round(index: int) -> list[dict]:
    call_id = f"call-{index}"
    return [
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": call_id,
                "type": "function",
                "function": {"name": "execute_sql", "arguments": json.dumps({"sql": index})},
            }],
        },
        {
            "role": "tool",
            "tool_call_id": call_id,
            "content": json.dumps({"rows": index}),
        },
    ]


def _prompt_round(index: int) -> list[dict]:
    return [
        {"role": "assistant", "content": json.dumps({"action": index})},
        {"role": "user", "content": f"[工具执行结果] execute_sql: {{\"rows\": {index}}}"},
    ]


def _config(**overrides) -> ContextCompactionConfig:
    values = {
        "enabled": True,
        "context_window_tokens": 10,
        "trigger_ratio": 0.5,
        "keep_recent_rounds": 1,
        "summary_max_output_tokens": 64,
    }
    values.update(overrides)
    return ContextCompactionConfig(**values)


def test_compaction_preserves_first_round_and_complete_native_pairs():
    history = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "inspect the database"},
        *_native_round(1),
        *_native_round(2),
        *_native_round(3),
    ]
    large_result = '{"rows": [' + ("42," * 5000) + "]}"
    history[3]["content"] = large_result

    selection = select_compaction(history, _config())

    assert selection is not None
    assert [message["tool_call_id"] for message in selection.old_messages if message["role"] == "tool"] == [
        "call-2"
    ]
    compacted = selection.apply("OBSERVED FACTS\n- exact fact")
    assert compacted[2:4] == history[2:4]
    assert compacted[3]["content"] == large_result
    assert compacted[4]["content"].startswith(SUMMARY_MESSAGE_PREFIX)
    assert compacted[-2:] == history[-2:]
    _, rounds = split_history_into_rounds(compacted)
    assert all(not round_.is_tool_round or len(round_.messages) == 2 for round_ in rounds)


def test_compaction_keeps_prompt_tool_result_with_its_assistant_round():
    history = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "inspect"},
        *_prompt_round(1),
        *_prompt_round(2),
        *_prompt_round(3),
    ]

    selection = select_compaction(history, _config())

    assert selection is not None
    assert selection.old_messages[-1]["content"].endswith('{"rows": 2}')


def test_compaction_rejects_orphan_or_mismatched_tool_results():
    with pytest.raises(ContextCompactionError, match="Orphan tool result"):
        split_history_into_rounds([
            {"role": "user", "content": "inspect"},
            {"role": "tool", "tool_call_id": "orphan", "content": "result"},
        ])

    with pytest.raises(ContextCompactionError, match="do not match"):
        split_history_into_rounds([
            {"role": "user", "content": "inspect"},
            *_native_round(1)[:1],
            {"role": "tool", "tool_call_id": "wrong", "content": "result"},
        ])


def _make_agent_with_history(**config_overrides) -> LLMAgent:
    agent = LLMAgent(
        model="mock-model",
        url="mock",
        api_key="mock",
        context_compaction=_config(context_window_tokens=10000, trigger_ratio=0.01, **config_overrides),
    )
    agent._conversation_history = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "inspect"},
        *_native_round(1),
        *_native_round(2),
        *_native_round(3),
    ]
    return agent


def test_no_usage_records_mean_no_compaction():
    agent = _make_agent_with_history()
    original = [dict(message) for message in agent._conversation_history]

    agent._maybe_compact_context()

    assert agent._conversation_history == original
    assert agent._context_compaction_events == []


def test_burst_compaction_when_round_growth_exceeds_burst_ratio():
    agent = _make_agent_with_history()
    agent._llm_prompt_tokens = 3000
    agent._llm_completion_tokens = 100
    agent._llm_round_growth_tokens = [0, 8000]

    agent._maybe_compact_context()

    assert agent._context_compaction_events[0]["mode"] == "burst"
    assert len(agent._conversation_history) == 3
    assert agent._conversation_history[0] == {"role": "system", "content": "system"}
    assert agent._conversation_history[1] == {"role": "user", "content": "inspect"}
    assert agent._conversation_history[-1]["content"].startswith("[上下文超限压缩]")
    assert "可能丢失重要信息" in agent._conversation_history[-1]["content"]
    # 压缩后精确记账基线重置
    assert agent._llm_prompt_tokens is None
    assert agent._llm_round_growth_tokens == []


def test_repeated_burst_compaction_replaces_old_warning():
    agent = _make_agent_with_history()
    agent._llm_prompt_tokens = 3000
    agent._llm_completion_tokens = 100
    agent._llm_round_growth_tokens = [0, 8000]
    agent._maybe_compact_context()

    agent._conversation_history.extend(_native_round(1))
    agent._llm_prompt_tokens = 3000
    agent._llm_completion_tokens = 100
    agent._llm_round_growth_tokens = [0, 8000]
    agent._maybe_compact_context()

    warnings = [
        message["content"] for message in agent._conversation_history
        if message["role"] == "user" and message["content"].startswith("[上下文超限压缩]")
    ]
    assert len(warnings) == 1
    assert agent._context_compaction_events[1]["mode"] == "burst"


def test_burst_fallback_when_no_summarizable_rounds(monkeypatch):
    agent = LLMAgent(
        model="mock-model",
        url="mock",
        api_key="mock",
        context_compaction=_config(context_window_tokens=10000, trigger_ratio=0.01),
    )
    agent._conversation_history = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "inspect"},
        *_native_round(1),
    ]
    monkeypatch.setattr(agent, "_summarize_old_history", lambda _: "summary")
    agent._llm_prompt_tokens = 9500
    agent._llm_completion_tokens = 100
    agent._llm_round_growth_tokens = [0, 100]

    agent._maybe_compact_context()

    assert agent._context_compaction_events[0]["mode"] == "burst"
    assert len(agent._conversation_history) == 3


def test_later_request_replaces_only_old_rounds_and_records_compaction(monkeypatch):
    agent = LLMAgent(
        model="mock-model",
        url="mock",
        api_key="mock",
        context_compaction=_config(context_window_tokens=10000, trigger_ratio=0.01),
    )
    agent._conversation_history = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "inspect"},
        *_native_round(1),
        *_native_round(2),
        *_native_round(3),
    ]
    agent._conversation_history[5]["content"] = "x" * 2000
    agent._synchronize_conversation_trace()
    raw_before_compaction = deepcopy(agent._conversation_raw_history)
    first_phase_before_compaction = deepcopy(agent._conversation_phases[0])
    monkeypatch.setattr(
        agent,
        "_summarize_old_history",
        lambda _: "\n".join(f"{heading}\n- pid=42" for heading in SUMMARY_HEADINGS),
    )
    agent._llm_prompt_tokens = 9500
    agent._llm_completion_tokens = 200
    agent._llm_round_growth_tokens = [0, 200, 200]

    agent._maybe_compact_context()

    assert agent._context_compaction_events[0]["mode"] == "summary"
    assert agent._context_compaction_events[0]["before_prompt_tokens"] == 9500
    assert agent._conversation_history[2:4] == [
        {"role": "assistant", "content": None, "tool_calls": [{
            "id": "call-1",
            "type": "function",
            "function": {"name": "execute_sql", "arguments": '{"sql": 1}'},
        }]},
        {"role": "tool", "tool_call_id": "call-1", "content": '{"rows": 1}'},
    ]
    assert agent._conversation_history[4]["content"].endswith("pid=42")
    assert agent._context_compaction_events[0]["old_round_count"] == 1
    assert agent._context_compaction_events[0]["recent_round_count"] == 1
    assert agent._conversation_raw_history[:len(raw_before_compaction)] == raw_before_compaction
    assert agent._conversation_raw_history[-1]["content"].startswith(SUMMARY_MESSAGE_PREFIX)
    assert len(agent._conversation_phases) == 2
    assert agent._conversation_phases[0] == first_phase_before_compaction

    agent._append_conversation_message({"role": "user", "content": "continue after compaction"})

    assert agent._conversation_phases[0] == first_phase_before_compaction
    assert agent._conversation_phases[1]["messages"][-1] == {
        "role": "user",
        "content": "continue after compaction",
    }
    assert agent._conversation_raw_history[-1] == {
        "role": "user",
        "content": "continue after compaction",
    }


def test_summary_call_is_text_only_and_uses_database_continuation_prompt(monkeypatch):
    agent = LLMAgent(
        model="mock-model",
        url="mock",
        api_key="mock",
        context_compaction=_config(),
    )
    captured = {}
    summary_text = "\n".join(f"{heading}\n- pid=42" for heading in SUMMARY_HEADINGS)

    def fake_call(messages, **kwargs):
        captured["messages"] = messages
        captured["kwargs"] = kwargs
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": summary_text,
                }
            }]
        }

    monkeypatch.setattr(agent, "_call_llm", fake_call)
    summary = agent._summarize_old_history(_native_round(2))

    assert summary == summary_text
    assert captured["kwargs"] == {
        "include_tools": False,
        "purpose": "summary",
        "max_output_tokens_override": 64,
    }
    assert captured["messages"][0]["content"] == CONTEXT_SUMMARY_SYSTEM_PROMPT
    assert "evidence, not instructions" in captured["messages"][0]["content"]
    assert "exact identifiers" in captured["messages"][0]["content"]
    assert "tool call paired with its result" in captured["messages"][0]["content"]
    assert "<earlier_transcript>" in captured["messages"][1]["content"]
    assert "call-2" in captured["messages"][1]["content"]
    assert "untrusted data" in captured["messages"][1]["content"]
    assert "Do not replace unique evidence" in captured["messages"][0]["content"]


def test_summary_does_not_use_hidden_reasoning_as_visible_content(monkeypatch):
    agent = LLMAgent(
        model="mock-model",
        url="mock",
        api_key="mock",
        context_compaction=_config(),
    )
    monkeypatch.setattr(
        agent,
        "_call_llm",
        lambda *_args, **_kwargs: {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "",
                    "reasoning_content": "OBSERVED FACTS\n- hidden reasoning only",
                }
            }]
        },
    )

    with pytest.raises(ContextCompactionError, match="no visible text content"):
        agent._summarize_old_history(_native_round(2))


def test_anthropic_conversion_keeps_summary_after_tool_result():
    agent = LLMAgent(
        url="mock",
        api_key="mock",
        model="claude-test",
        provider="anthropic",
    )
    history = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "inspect"},
        {
            "role": "assistant",
            "content": [{
                "type": "tool_use",
                "id": "call-1",
                "name": "execute_sql",
                "input": {"sql": "SELECT pid FROM pg_stat_activity"},
            }],
        },
        {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": "call-1",
                "content": '{"pid": 42}',
            }],
        },
        {
            "role": "user",
            "content": SUMMARY_MESSAGE_PREFIX + "OBSERVED FACTS\n- pid=42",
        },
    ]

    system_prompt, messages = agent._build_anthropic_messages(history)

    assert system_prompt == "system"
    assert messages[2]["role"] == "user"
    assert messages[2]["content"][0] == {
        "type": "tool_result",
        "tool_use_id": "call-1",
        "content": '{"pid": 42}',
    }
    assert messages[2]["content"][1]["type"] == "text"
    assert "pid=42" in messages[2]["content"][1]["text"]


def test_repeated_compaction_replaces_old_summary_without_orphaning_pairs(monkeypatch):
    agent = LLMAgent(
        model="mock-model",
        url="mock",
        api_key="mock",
        context_compaction=_config(),
    )
    agent._conversation_history = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "inspect"},
        *_native_round(1),
        *_native_round(2),
        *_native_round(3),
        *_native_round(4),
    ]
    summary = "\n".join(f"{heading}\n- exact fact" for heading in SUMMARY_HEADINGS)
    monkeypatch.setattr(agent, "_summarize_old_history", lambda _: summary)
    agent.context_compaction = _config(context_window_tokens=10000, trigger_ratio=0.01)
    agent._llm_prompt_tokens = 9500
    agent._llm_completion_tokens = 200
    agent._llm_round_growth_tokens = [0, 200, 200, 200]
    agent._maybe_compact_context()

    agent._conversation_history.extend(_native_round(5))
    agent._llm_prompt_tokens = 9500
    agent._llm_completion_tokens = 200
    agent._llm_round_growth_tokens = [0, 200]
    agent._maybe_compact_context()

    assert sum(
        message.get("content", "").startswith(SUMMARY_MESSAGE_PREFIX)
        for message in agent._conversation_history
        if message.get("role") == "user" and isinstance(message.get("content"), str)
    ) == 1
    _, rounds = split_history_into_rounds(agent._conversation_history)
    assert all(not round_.is_tool_round or len(round_.messages) == 2 for round_ in rounds)


def test_summary_usage_does_not_advance_diagnostic_turn_accounting():
    agent = LLMAgent(url="mock", api_key="mock", model="mock-model")
    agent._record_usage({
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 10,
            "prompt_tokens_details": {"cached_tokens": 0},
        }
    })
    agent._accept_diagnostic_turn()

    agent._record_usage(
        {
            "usage": {
                "prompt_tokens": 900,
                "completion_tokens": 20,
                "prompt_tokens_details": {"cached_tokens": 0},
            }
        },
        purpose="summary",
    )
    agent._record_usage({
        "usage": {
            "prompt_tokens": 140,
            "completion_tokens": 11,
            "prompt_tokens_details": {"cached_tokens": 0},
        }
    })
    agent._accept_diagnostic_turn()

    assert agent.diagnostic_turn_count() == 2
    assert agent._diagnostic_turn_usage[1] == {
        "input_token": 40,
        "cache_input_token": 100,
        "output_token": 11,
    }
    assert agent.get_usage_events()[1]["purpose"] == "summary"


@pytest.mark.parametrize(
    "settings",
    [
        {"context_compaction": {"enabled": True}},
        {"other": {}},
        {"context_compaction": {
            "enabled": True,
            "context_window_tokens": 100,
            "trigger_ratio": 1.0,
            "keep_recent_rounds": 1,
            "summary_max_output_tokens": 64,
            "burst_ratio": 0.5,
        }},
        {"context_compaction": {
            "enabled": True,
            "trigger_ratio": 0.8,
            "keep_recent_rounds": 1,
            "summary_max_output_tokens": 64,
            "burst_ratio": 1.5,
        }},
    ],
)
def test_context_compaction_settings_reject_incomplete_or_invalid_values(settings):
    with pytest.raises(ValueError):
        ContextCompactionConfig.from_settings(settings)


def test_context_compaction_settings_accept_full_valid_values():
    config = ContextCompactionConfig.from_settings({
        "context_compaction": {
            "enabled": True,
            "trigger_ratio": 0.8,
            "keep_recent_rounds": 2,
            "summary_max_output_tokens": 1024,
            "burst_ratio": 0.6,
        }
    })

    assert config.enabled is True
    assert config.trigger_ratio == 0.8
    assert config.keep_recent_rounds == 2
    assert config.summary_max_output_tokens == 1024
    assert config.burst_ratio == 0.6


def test_empty_llm_settings_enable_compaction_with_default_window():
    config = ContextCompactionConfig.from_settings({})

    assert config.enabled is True
    assert config.context_window_tokens == DEFAULT_CONTEXT_WINDOW_TOKENS == 200_000
    assert config.burst_ratio == 0.5


def test_default_agent_compaction_is_enabled_and_binds_model_window(tmp_path):
    config_path = tmp_path / "llm_config.json"
    config_path.write_text(
        json.dumps({
            "gpt-test": {
                "url": "https://example.invalid/v1",
                "api_key": "test-key",
                "context_window_tokens": 131072,
            }
        }),
        encoding="utf-8",
    )

    agent = LLMAgent(model="gpt-test", config_path=str(config_path))

    assert agent.context_compaction.enabled is True
    assert agent.context_compaction.context_window_tokens == 131072
    assert agent.context_compaction.trigger_tokens == 117964


def test_enabled_compaction_defaults_to_200k_context_window():
    config = ContextCompactionConfig(enabled=True)

    assert config.context_window_tokens == 200_000
    assert config.trigger_ratio == 0.90
    assert config.trigger_tokens == 180_000


def test_enabled_compaction_binds_model_context_window_from_llm_config(tmp_path):
    config_path = tmp_path / "llm_config.json"
    config_path.write_text(
        json.dumps({
            "gpt-test": {
                "url": "https://example.invalid/v1",
                "api_key": "test-key",
                "context_window_tokens": 131072,
            }
        }),
        encoding="utf-8",
    )
    settings = {
        "context_compaction": {
            "enabled": True,
            "trigger_ratio": 0.8,
            "keep_recent_rounds": 3,
            "summary_max_output_tokens": 2048,
            "burst_ratio": 0.5,
        }
    }

    agent = LLMAgent(
        model="gpt-test",
        config_path=str(config_path),
        context_compaction=ContextCompactionConfig.from_settings(settings),
    )

    assert agent.context_compaction.context_window_tokens == 131072
    assert agent.context_compaction.trigger_tokens == 104857


def test_enabled_compaction_uses_200k_when_llm_config_lacks_context_window(tmp_path):
    config_path = tmp_path / "llm_config.json"
    config_path.write_text(
        json.dumps({
            "gpt-test": {
                "url": "https://example.invalid/v1",
                "api_key": "test-key",
            }
        }),
        encoding="utf-8",
    )

    agent = LLMAgent(
        model="gpt-test",
        config_path=str(config_path),
        context_compaction=ContextCompactionConfig.from_settings({
            "context_compaction": {
                "enabled": True,
                "trigger_ratio": 0.8,
                "keep_recent_rounds": 3,
                "summary_max_output_tokens": 2048,
                "burst_ratio": 0.5,
            }
        }),
    )

    assert agent.context_compaction.context_window_tokens == 200_000


def test_manifest_accepts_explicit_llm_compaction_settings(tmp_path):
    manifest_path = tmp_path / "compaction.yaml"
    manifest_path.write_text(
        """
experiment_id: compaction
benchmark:
  systems: [postgresql]
  categories: [query_perf]
  scenarios: []
agents:
  - id: llm-summary
    mode: llm
    model: gpt-test
    settings:
      context_compaction:
        enabled: true
        trigger_ratio: 0.8
        keep_recent_rounds: 3
        summary_max_output_tokens: 2048
        burst_ratio: 0.5
repetitions: 1
seeds: [1]
""".strip(),
        encoding="utf-8",
    )

    manifest = load_manifest(manifest_path)

    assert manifest.agents[0].settings["context_compaction"]["enabled"] is True


def _length_error() -> Dict[str, Any]:
    return {
        "error": {
            "code": 400,
            "message": "Range of input length should be [1, 202745]",
            "type": "invalid_request_error",
        }
    }


def test_is_context_length_error_matches_provider_variants():
    assert LLMAgent._is_context_length_error(_length_error())
    assert LLMAgent._is_context_length_error(
        {"error": {"message": "This model's maximum context length is 200000 tokens"}}
    )
    assert LLMAgent._is_context_length_error("prompt is too long: 210000 tokens > 200000")
    assert not LLMAgent._is_context_length_error({"error": {"message": "Upstream rate limit exceeded"}})
    assert not LLMAgent._is_context_length_error({"error": {"message": "quota exceeded"}})


def test_length_error_on_single_giant_round_recovers_via_burst(monkeypatch):
    agent = LLMAgent(
        model="mock-model",
        url="mock",
        api_key="mock",
        context_compaction=_config(context_window_tokens=10000, trigger_ratio=0.01),
    )
    agent._conversation_history = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "inspect"},
        *_native_round(1),
    ]
    monkeypatch.setattr(
        agent,
        "_call_llm",
        lambda *_a, **_k: {"choices": [{"message": {"role": "assistant", "content": json.dumps({"action": 1})}}]},
    )

    recovered = agent._recover_from_context_length_error()

    assert recovered is not None
    assert len(agent._conversation_history) == 3
    assert agent._conversation_history[-1]["content"].startswith("[上下文超限压缩]")
    assert agent._context_compaction_events[0]["mode"] == "burst"


def test_length_error_recovers_via_summary_then_retries(monkeypatch):
    agent = LLMAgent(
        model="mock-model",
        url="mock",
        api_key="mock",
        context_compaction=_config(context_window_tokens=10000, trigger_ratio=0.01),
    )
    agent._conversation_history = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "inspect"},
        *_native_round(1),
        *_native_round(2),
        *_native_round(3),
    ]
    summary = "\n".join(f"{heading}\n- exact fact" for heading in SUMMARY_HEADINGS)

    def fake_call(messages, **kwargs):
        if kwargs.get("purpose") == "summary":
            return {"choices": [{"message": {"role": "assistant", "content": summary}}]}
        return {"choices": [{"message": {"role": "assistant", "content": json.dumps({"action": 9})}}]}

    monkeypatch.setattr(agent, "_call_llm", fake_call)

    recovered = agent._recover_from_context_length_error()

    assert recovered is not None
    assert agent._context_compaction_events[0]["mode"] == "summary"
    _, rounds = split_history_into_rounds(agent._conversation_history)
    assert len(rounds) == 3


def test_summary_failure_on_length_error_escalates_to_burst(monkeypatch):
    agent = LLMAgent(
        model="mock-model",
        url="mock",
        api_key="mock",
        context_compaction=_config(context_window_tokens=10000, trigger_ratio=0.01),
    )
    agent._conversation_history = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "inspect"},
        *_native_round(1),
        *_native_round(2),
        *_native_round(3),
    ]
    summary = "\n".join(f"{heading}\n- exact fact" for heading in SUMMARY_HEADINGS)
    diagnostic_responses = [_length_error(), _length_error(), _length_error()]

    def fake_call(messages, **kwargs):
        if kwargs.get("purpose") == "summary":
            return {"choices": [{"message": {"role": "assistant", "content": summary}}]}
        response = diagnostic_responses.pop(0)
        if "error" in response:
            return response
        return {"choices": [{"message": {"role": "assistant", "content": json.dumps({"action": 9})}}]}

    monkeypatch.setattr(agent, "_call_llm", fake_call)

    recovered = agent._recover_from_context_length_error()

    assert recovered is None
    assert [event["mode"] for event in agent._context_compaction_events] == ["summary", "burst"]
    assert len(agent._conversation_history) == 3


def test_unrecoverable_length_error_returns_none(monkeypatch):
    agent = LLMAgent(
        model="mock-model",
        url="mock",
        api_key="mock",
        context_compaction=_config(context_window_tokens=10000, trigger_ratio=0.01),
    )
    agent._conversation_history = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "inspect"},
    ]
    monkeypatch.setattr(agent, "_call_llm", lambda *_a, **_k: _length_error())

    assert agent._recover_from_context_length_error() is None
    assert agent._context_compaction_events == []
