from __future__ import annotations

from pathlib import Path

import pytest

from src.agents.agent import LLMAgent
from src.benchmark.token_accounting import (
    ReconstructedCall,
    _reconstructed_calls,
    account_tokens,
    load_token_config,
)


def test_anthropic_reconstruction_uses_protocol_instead_of_model_identity():
    trace = {
        "metadata": {"agent_type": "LLMAgent"},
        "conversation_history": [
            {"role": "system", "content": "Diagnose the database."},
            {"role": "user", "content": "Inspect the failure."},
            {"role": "assistant", "content": "Checking evidence."},
        ],
    }
    anthropic = _reconstructed_calls(trace, "anthropic", [], [])[0]
    openai = _reconstructed_calls(trace, "openai", [], [])[0]
    assert anthropic.input_payload["system"] == "Diagnose the database."
    assert all(message["role"] != "system" for message in anthropic.input_payload["messages"])
    assert openai.input_payload["messages"][0]["role"] == "system"


class UnusedTokenizers:
    def count(self, model: str, text: str) -> int:
        raise AssertionError("Provider-reported usage must not invoke a tokenizer")


class SequentialTokenizers:
    def __init__(self, values: list[int]):
        self.values = iter(values)

    def count(self, model: str, text: str) -> int:
        return next(self.values)


def provider_trace(
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int = 0,
    cache_write_tokens: int = 0,
) -> dict:
    return {
        "$schema": "run_trace_v3",
        "metadata": {"run_id": "run-1", "agent_type": "LLMAgent"},
        "llm_usage": [{
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_input_tokens": cached_tokens,
            "cache_write_input_tokens": cache_write_tokens,
        }],
    }


def test_official_gpt_price_populates_cost():
    config = load_token_config(Path("data/model_token_costs.yaml"))
    result = account_tokens(provider_trace(100, 20), "gpt-5.5", config, UnusedTokenizers())

    assert result["total_tokens"] == 120
    assert result["input_token_cost_usd"] == 0.0005
    assert result["output_token_cost_usd"] == 0.0006
    assert result["total_token_cost_usd"] == 0.0011
    assert result["cost_status"] == "estimated"


def test_official_model_price_populates_cost():
    config = load_token_config(Path("data/model_token_costs.yaml"))
    result = account_tokens(
        provider_trace(1_000_000, 100_000, cached_tokens=100_000),
        "claude-opus-4-8",
        config,
        UnusedTokenizers(),
    )

    assert result["input_token_cost_usd"] == 4.55
    assert result["output_token_cost_usd"] == 2.5
    assert result["total_token_cost_usd"] == 7.05
    assert result["cost_status"] == "estimated"


def test_cache_write_requires_an_explicit_price():
    config = load_token_config(Path("data/model_token_costs.yaml"))
    with pytest.raises(ValueError, match="lacks a cache-write rate"):
        account_tokens(
            provider_trace(100, 20, cache_write_tokens=10),
            "claude-opus-4-8",
            config,
            UnusedTokenizers(),
        )


def test_reconstructed_usage_prices_prior_input_as_cached(monkeypatch):
    monkeypatch.setattr(
        "src.benchmark.token_accounting._tool_schemas",
        lambda system: ([], []),
    )
    trace = {
        "$schema": "run_trace_v3",
        "metadata": {
            "run_id": "run-1",
            "agent_type": "LLMAgent",
            "system": "postgresql",
        },
        "conversation_history": [
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": "first response"},
            {"role": "user", "content": "second"},
            {"role": "assistant", "content": "second response"},
        ],
    }
    config = load_token_config(Path("data/model_token_costs.yaml"))
    result = account_tokens(
        trace,
        "gpt-5.5",
        config,
        SequentialTokenizers([100, 20, 300, 40]),
    )

    assert result["llm_call_count"] == 2
    assert result["input_tokens"] == 400
    assert result["cached_input_tokens"] == 100
    assert result["output_tokens"] == 60
    assert result["input_token_cost_usd"] == 0.00155
    assert result["output_token_cost_usd"] == 0.0018
    assert result["total_token_cost_usd"] == 0.00335
    assert result["token_accounting_method"] == "trace_reconstructed_differential_cache"


def test_reconstructed_usage_rejects_decreasing_input(monkeypatch):
    monkeypatch.setattr(
        "src.benchmark.token_accounting._tool_schemas",
        lambda system: ([], []),
    )
    trace = {
        "$schema": "run_trace_v3",
        "metadata": {
            "run_id": "run-decreasing",
            "agent_type": "LLMAgent",
            "system": "postgresql",
        },
        "conversation_history": [
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": "first response"},
            {"role": "user", "content": "second"},
            {"role": "assistant", "content": "second response"},
        ],
    }
    config = load_token_config(Path("data/model_token_costs.yaml"))

    with pytest.raises(
        ValueError,
        match=(
            "run_id='run-decreasing'.*call_index=2.*"
            "previous_input_tokens=300.*input_tokens=100"
        ),
    ):
        account_tokens(
            trace,
            "gpt-5.5",
            config,
            SequentialTokenizers([300, 20, 100]),
        )


def test_reconstructed_independent_calls_do_not_share_cached_input(monkeypatch):
    monkeypatch.setattr(
        "src.benchmark.token_accounting._tool_schemas",
        lambda system: ([], []),
    )
    monkeypatch.setattr(
        "src.benchmark.token_accounting._reconstructed_calls",
        lambda trace, model, tools, expert_tools: [
            ReconstructedCall({"call": 1}, {"output": 1}),
            ReconstructedCall({"call": 2}, {"output": 2}),
        ],
    )
    trace = {
        "$schema": "run_trace_v3",
        "metadata": {
            "run_id": "run-dbot",
            "agent_type": "DbotAgent",
            "system": "postgresql",
        },
    }
    config = load_token_config(Path("data/model_token_costs.yaml"))
    result = account_tokens(
        trace,
        "gpt-5.5",
        config,
        SequentialTokenizers([300, 20, 100, 10]),
    )

    assert result["input_tokens"] == 400
    assert result["cached_input_tokens"] == 0
    assert result["output_tokens"] == 30
    assert result["input_token_cost_usd"] == 0.002
    assert result["output_token_cost_usd"] == 0.0009
    assert result["total_token_cost_usd"] == 0.0029
    assert result["token_accounting_method"] == "trace_reconstructed_independent_calls"
