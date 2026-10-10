import json

import pytest

from src.agents.agent import LLMAgent
from src.agents.cache_breaker import (
    DEFAULT_CONSECUTIVE_MISSES,
    CacheBreakerConfig,
    CacheCircuitBreaker,
    CacheCircuitBreakerError,
)
def _anthropic_tool_response(api, args):
    return {
        "type": "message",
        "role": "assistant",
        "usage": {
            "input_tokens": 100,
            "output_tokens": 20,
            "cache_read_input_tokens": 0,
            "cache_creation_input_tokens": 0,
        },
        "content": [
            {"type": "text", "text": f"Call {api}."},
            {"type": "tool_use", "id": f"tool_{api}", "name": api, "input": args},
        ],
    }


def test_breaker_config_defaults():
    config = CacheBreakerConfig.from_entry({"url": "x"})
    assert config.enabled is True
    assert config.consecutive_misses == DEFAULT_CONSECUTIVE_MISSES == 5


def test_breaker_config_per_model_override_and_validation():
    config = CacheBreakerConfig.from_entry(
        {"cache_circuit_breaker": {"enabled": True, "consecutive_misses": 3}}
    )
    assert (config.enabled, config.consecutive_misses) == (True, 3)

    disabled = CacheBreakerConfig.from_entry({"cache_circuit_breaker": {"enabled": False}})
    assert (disabled.enabled, disabled.consecutive_misses) == (False, 5)

    with pytest.raises(ValueError, match="consecutive_misses"):
        CacheBreakerConfig.from_entry({"cache_circuit_breaker": {"consecutive_misses": 0}})
    with pytest.raises(ValueError, match="enabled"):
        CacheBreakerConfig.from_entry({"cache_circuit_breaker": {"enabled": "yes"}})


def test_breaker_counts_consecutive_diagnostic_misses_only():
    breaker = CacheCircuitBreaker(CacheBreakerConfig(consecutive_misses=3), "cache-model")
    breaker.record(0, "diagnostic", "llm-call-000001")
    breaker.record(0, "diagnostic", "llm-call-000002")
    assert breaker.tripped is False
    breaker.record(0, "summary", "llm-call-000003")  # non-diagnostic: ignored
    assert breaker.tripped is False
    breaker.record(0, "diagnostic", "llm-call-000004")
    assert breaker.tripped is True
    assert [e["call_id"] for e in breaker.miss_events] == [
        "llm-call-000001",
        "llm-call-000002",
        "llm-call-000004",
    ]
    assert "cache-model" in breaker.error_message()


def test_breaker_hit_resets_streak():
    breaker = CacheCircuitBreaker(CacheBreakerConfig(consecutive_misses=3), "cache-model")
    for _ in range(4):
        breaker.record(0, "diagnostic")
        breaker.record(22945, "diagnostic")
    assert breaker.tripped is False


def test_disabled_breaker_never_trips():
    breaker = CacheCircuitBreaker(CacheBreakerConfig(enabled=False, consecutive_misses=1), "m")
    breaker.record(0, "diagnostic")
    assert breaker.tripped is False


def test_breaker_report_written_to_attempt_dir(tmp_path):
    breaker = CacheCircuitBreaker(CacheBreakerConfig(consecutive_misses=2), "cache-model")
    breaker.record(0, "diagnostic", "llm-call-000001")
    breaker.record(0, "diagnostic", "llm-call-000002")
    path = breaker.report(str(tmp_path))
    payload = json.load(open(path))
    assert payload["schema"] == "aiopsbench_cache_circuit_breaker_v1"
    assert payload["model"] == "cache-model"
    assert payload["consecutive_misses"] == 2
    assert payload["threshold"] == 2
    assert len(payload["miss_events"]) == 2
    assert breaker.report(None) is None


def _zero_cache_anthropic_response(api, args):
    response = _anthropic_tool_response(api, args)
    response["usage"]["cache_read_input_tokens"] = 0
    response["usage"]["cache_creation_input_tokens"] = 0
    return response


def test_agent_trips_and_writes_report_after_consecutive_misses(tmp_path, monkeypatch):
    config_path = tmp_path / "llm_config.json"
    config_path.write_text(json.dumps({
        "cache-model": {
            "url": "https://example.com",
            "api_key": "k",
            "cache_circuit_breaker": {"enabled": True, "consecutive_misses": 2},
        }
    }))
    monkeypatch.setenv("AIOPS_TRACE_OUTPUT_DIR", str(tmp_path / "attempt-001"))

    import anthropic as anthropic_module

    class FakeMessages:
        @staticmethod
        def stream(**payload):
            calls = FakeMessages.stream_calls
            FakeMessages.stream_calls += 1
            api = "query_metrics" if calls == 1 else "submit"
            response = _zero_cache_anthropic_response(api, {"diagnosis": "x"} if api == "submit" else {"metric_type": "cpu"})
            return _FakeStream(response)

    FakeMessages.stream_calls = 0

    class _FakeStream:
        def __init__(self, response):
            self._response = response

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def get_final_message(self):
            return self._response

    class FakeAnthropic:
        def __init__(self, **kwargs):
            self.messages = FakeMessages()

    monkeypatch.setattr(anthropic_module, "Anthropic", FakeAnthropic)

    agent = LLMAgent(url="https://example.com", api_key="k", provider="anthropic",
                     model="cache-model", config_path=str(config_path))

    agent._call_llm([{"role": "user", "content": "turn1"}])
    with pytest.raises(CacheCircuitBreakerError, match="consecutive cache-miss calls=2"):
        agent._call_llm([{"role": "user", "content": "turn2"}])

    report_path = tmp_path / "attempt-001" / "cache_circuit_breaker_report.json"
    payload = json.load(open(report_path))
    assert payload["model"] == "cache-model"
    assert payload["consecutive_misses"] == 2


def test_agent_breaker_disabled_by_config_entry_runs_normally(tmp_path, monkeypatch):
    config_path = tmp_path / "llm_config.json"
    config_path.write_text(json.dumps({
        "cache-model": {
            "url": "https://example.com",
            "api_key": "k",
            "cache_circuit_breaker": {"enabled": False, "consecutive_misses": 1},
        }
    }))
    monkeypatch.setenv("AIOPS_TRACE_OUTPUT_DIR", str(tmp_path / "attempt-001"))

    import anthropic as anthropic_module

    class FakeMessages:
        @staticmethod
        def stream(**payload):
            return _FakeStream(_zero_cache_anthropic_response("submit", {"diagnosis": "x"}))

    class _FakeStream:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def get_final_message(self):
            return self._response

    class FakeAnthropic:
        def __init__(self, **kwargs):
            self.messages = FakeMessages()

    monkeypatch.setattr(anthropic_module, "Anthropic", FakeAnthropic)

    agent = LLMAgent(url="https://example.com", api_key="k", provider="anthropic",
                     model="cache-model", config_path=str(config_path))
    # disabled breaker: repeated misses never raise
    for _ in range(3):
        agent._call_llm([{"role": "user", "content": "turn"}])
    assert not (tmp_path / "attempt-001" / "cache_circuit_breaker_report.json").exists()


def test_agent_loads_breaker_config_from_file(tmp_path):
    config_path = tmp_path / "llm_config.json"
    config_path.write_text(json.dumps({
        "cache-model": {
            "url": "https://example.com",
            "api_key": "k",
            "cache_circuit_breaker": {"consecutive_misses": 4},
        }
    }))
    agent = LLMAgent(url="https://example.com", api_key="k", provider="anthropic",
                     model="cache-model", config_path=str(config_path))
    assert agent._cache_breaker.config.consecutive_misses == 4
    assert agent._cache_breaker.config.enabled is True

    default_agent = LLMAgent(url="https://example.com", api_key="k", provider="anthropic",
                             model="cache-model",
                             config_path=str(tmp_path / "missing.json"))
    assert default_agent._cache_breaker.config.consecutive_misses == DEFAULT_CONSECUTIVE_MISSES
