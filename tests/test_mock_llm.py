import json
import os
import sys

import pytest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import (
    FINAL_TURN_SUBMIT_PROMPT,
    LLM_DEFAULT_MAX_OUTPUT_TOKENS,
    LLM_REQUEST_MAX_RETRIES,
    LLM_REQUEST_TIMEOUT_SECONDS,
    LLMAgent,
    MockLLMAgent,
    require_final_submission,
)


class FakeGateway:
    """最小网关：记录每次工具调用并返回固定结果，供 solve() 驱动。"""

    def __init__(self):
        self.calls = []

    def execute(self, api, args, *, thinking="", source=""):
        self.calls.append({"api": api, "args": args, "thinking": thinking, "source": source})
        return {"api": api, "status": "success", "result": {"data": "mock_data"}}


def _openai_tool_response(*tool_calls, input_tokens=100, output_tokens=20):
    return {
        "usage": {
            "prompt_tokens": input_tokens,
            "completion_tokens": output_tokens,
            "prompt_tokens_details": {"cached_tokens": 0},
        },
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": f"call_{index}",
                        "type": "function",
                        "function": {
                            "name": api,
                            "arguments": json.dumps(args),
                        },
                    }
                    for index, (api, args) in enumerate(tool_calls, 1)
                ],
            }
        }]
    }


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


class _FakeAnthropicStream:
    def __init__(self, response):
        self._response = response

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self._response


def _anthropic_stream_response(response):
    return _FakeAnthropicStream(response)


def _openai_stream_from_response(response):
    from types import SimpleNamespace

    choice = response["choices"][0]
    message = choice["message"]
    delta = SimpleNamespace(
        content=message.get("content"),
        reasoning_content=message.get("reasoning_content"),
        tool_calls=[
            SimpleNamespace(
                index=index,
                id=tool_call.get("id"),
                type=tool_call.get("type"),
                function=SimpleNamespace(
                    name=tool_call["function"]["name"],
                    arguments=tool_call["function"]["arguments"],
                ),
            )
            for index, tool_call in enumerate(message.get("tool_calls") or [])
        ] or None,
    )
    usage = response.get("usage")
    return iter([
        SimpleNamespace(
            id=response.get("id"),
            created=response.get("created"),
            model=response.get("model"),
            usage=None,
            choices=[SimpleNamespace(delta=delta, finish_reason=choice.get("finish_reason"))],
        ),
        SimpleNamespace(
            id=None,
            created=None,
            model=None,
            usage=SimpleNamespace(model_dump=lambda: usage) if usage else None,
            choices=[],
        ),
    ])



def _prompt_action_response(api, args):
    return {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": json.dumps({
                    "thinking": f"Call {api}.",
                    "action": {"api": api, "args": args},
                }),
            }
        }]
    }


def test_mock_agent_requires_explicit_submission():
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="test")
    agent.set_mock_responses([
        {"thinking": "Inspect only.", "action": {"api": "query_metrics", "args": {"metric_type": "cpu"}}}
    ])
    agent.init_env_gateway(FakeGateway())
    agent.max_turns = 1

    with pytest.raises(RuntimeError, match="reached max_turns without submission"):
        agent.solve()


def test_mock_agent_honors_scripted_delay_without_emitting_a_tool_call(monkeypatch):
    delays = []
    monkeypatch.setattr("src.agents.agent.time.sleep", delays.append)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="test")
    agent.set_mock_responses([
        {"thinking": "Wait for recovery telemetry.", "delay_seconds": 2.5, "actions": []},
        {"thinking": "Submit.", "action": {"api": "submit", "args": {"report": {}}}},
    ])

    assert agent.solve() == {"report": {}}
    assert delays == [2.5]
    assert [entry["parsed_action"]["api"] for entry in agent.action_history] == ["submit"]


def test_llm_agent_requires_an_action_before_submission(monkeypatch):
    agent = LLMAgent(url="mock", api_key="mock", model="mock-model")
    agent.max_turns = 1
    monkeypatch.setattr(agent, "_next_llm_actions", lambda _retries: ("", []))

    with pytest.raises(RuntimeError, match="produced no actions before submission"):
        agent.solve()


def test_llm_agent_adds_final_prompt_and_accepts_submission(monkeypatch):
    agent = LLMAgent(url="mock", api_key="mock", model="mock-model")
    agent.init_env_gateway(FakeGateway())
    agent.max_turns = 1
    replies = iter([
        ("Inspect CPU.", [{"api": "query_metrics", "args": {"metric_type": "cpu"}}]),
        ("Summarize and submit.", [{"api": "submit", "args": {"diagnosis": "CPU saturation"}}]),
    ])
    monkeypatch.setattr(agent, "_next_llm_actions", lambda _retries: next(replies))

    submission = agent.solve()

    assert submission == {"diagnosis": "CPU saturation"}
    assert any(
        message.get("content") == FINAL_TURN_SUBMIT_PROMPT
        for message in agent.get_conversation_history()
    )
    assert [entry["parsed_action"]["api"] for entry in agent.action_history] == [
        "query_metrics",
        "submit",
    ]


def test_repeated_identical_tool_rounds_abort_diagnosis(monkeypatch):
    agent = LLMAgent(url="mock", api_key="mock", model="mock-model")
    agent.init_env_gateway(FakeGateway())
    replies = iter([
        ("Query fleet.", [{"api": "query_metrics", "args": {"metric_type": "fleet"}}]),
        ("Query fleet again.", [{"api": "query_metrics", "args": {"metric_type": "fleet"}}]),
        ("Query fleet third time.", [{"api": "query_metrics", "args": {"metric_type": "fleet"}}]),
        ("Submit.", [{"api": "submit", "args": {"diagnosis": "never reached"}}]),
    ])
    monkeypatch.setattr(agent, "_next_llm_actions", lambda _retries: next(replies))

    with pytest.raises(RuntimeError, match="MODEL-LOOP-ABORT"):
        agent.solve()

    # 第 3 轮在执行前熔断：只有前两轮真正触达环境
    assert [call["api"] for call in agent.gateway.calls] == ["query_metrics", "query_metrics"]


def test_two_identical_rounds_then_distinct_round_completes(monkeypatch):
    agent = LLMAgent(url="mock", api_key="mock", model="mock-model")
    agent.init_env_gateway(FakeGateway())
    replies = iter([
        ("Query fleet.", [{"api": "query_metrics", "args": {"metric_type": "fleet"}}]),
        ("Query fleet again.", [{"api": "query_metrics", "args": {"metric_type": "fleet"}}]),
        ("Narrow down.", [{"api": "query_metrics", "args": {"metric_type": "replica_lwlock"}}]),
        ("Submit.", [{"api": "submit", "args": {"diagnosis": "lwlock cascade"}}]),
    ])
    monkeypatch.setattr(agent, "_next_llm_actions", lambda _retries: next(replies))

    submission = agent.solve()

    assert submission == {"diagnosis": "lwlock cascade"}


def test_llm_agent_rejects_non_submit_action_in_final_turn(monkeypatch):
    agent = LLMAgent(url="mock", api_key="mock", model="mock-model")
    agent.init_env_gateway(FakeGateway())
    agent.max_turns = 1
    replies = iter([
        ("Inspect CPU.", [{"api": "query_metrics", "args": {"metric_type": "cpu"}}]),
        ("Inspect again.", [{"api": "query_metrics", "args": {"metric_type": "cpu"}}]),
    ])
    monkeypatch.setattr(agent, "_next_llm_actions", lambda _retries: next(replies))

    with pytest.raises(
        RuntimeError,
        match=r"LLMAgent final turn must contain exactly one submit: returned_actions=\['query_metrics'\]",
    ):
        agent.solve()


@pytest.mark.parametrize(
    ("provider", "use_native_tools", "responses"),
    [
        (
            "openai",
            True,
            [
                _openai_tool_response(("query_metrics", {"metric_type": "cpu"})),
                _openai_tool_response(("submit", {"diagnosis": "CPU saturation"})),
            ],
        ),
        (
            "anthropic",
            True,
            [
                _anthropic_tool_response("query_metrics", {"metric_type": "cpu"}),
                _anthropic_tool_response("submit", {"diagnosis": "CPU saturation"}),
            ],
        ),
        (
            "openai",
            False,
            [
                _prompt_action_response("query_metrics", {"metric_type": "cpu"}),
                _prompt_action_response("submit", {"diagnosis": "CPU saturation"}),
            ],
        ),
    ],
    ids=["openai-native", "anthropic-native", "prompt-json"],
)
def test_final_submit_round_uses_real_response_parser(
    monkeypatch, provider, use_native_tools, responses
):
    agent = LLMAgent(
        url="mock",
        api_key="mock",
        provider=provider,
        model="claude-test" if provider == "anthropic" else "gpt-test",
        use_native_tools=use_native_tools,
    )
    agent.init_env_gateway(FakeGateway())
    agent.max_turns = 1
    queued_responses = iter(responses)
    request_messages = []

    def fake_call(messages):
        request_messages.append(list(messages))
        return next(queued_responses)

    monkeypatch.setattr(agent, "_call_llm", fake_call)

    submission = agent.solve(max_empty_retries=0)

    assert submission == {"diagnosis": "CPU saturation"}
    assert any(
        message.get("content") == FINAL_TURN_SUBMIT_PROMPT
        for message in request_messages[-1]
    )
    assert [entry["parsed_action"]["api"] for entry in agent.action_history] == [
        "query_metrics",
        "submit",
    ]


def test_prompt_parser_accepts_gateway_xml_tool_markup():
    agent = LLMAgent(url="mock", api_key="mock", model="claude-test")
    agent.set_tools([
        {
            "type": "function",
            "function": {"name": "query_metrics"},
        }
    ])

    parsed = agent._parse_llm_response(
        "query_metrics\n\n"
        '<parameter name="metric_type">disk_io</parameter>\n'
        '<parameter name="target">pd-0</parameter>\n'
        '<parameter name="start_timestamp">now-30m</parameter>\n'
        '<parameter name="end_timestamp">now</parameter>\n'
        "</invoke>"
    )

    assert parsed["action"] == {
        "api": "query_metrics",
        "args": {
            "metric_type": "disk_io",
            "target": "pd-0",
            "start_timestamp": "now-30m",
            "end_timestamp": "now",
        },
    }


def test_prompt_parser_accepts_gateway_tool_name_and_json_arguments():
    agent = LLMAgent(url="mock", api_key="mock", model="claude-test")
    agent.set_tools([
        {
            "type": "function",
            "function": {"name": "help"},
        }
    ])

    parsed = agent._parse_llm_response('help\n\n{"tool_name":"read_log"}')

    assert parsed["action"] == {
        "api": "help",
        "args": {"tool_name": "read_log"},
    }


def test_prompt_parser_accepts_gateway_parameterless_tool_call():
    agent = LLMAgent(url="mock", api_key="mock", model="claude-test")
    agent.set_tools([
        {
            "type": "function",
            "function": {"name": "inspect_pd_schedulers"},
        }
    ])

    parsed = agent._parse_llm_response(
        "I will inspect the scheduler state.\n\ninspect_pd_schedulers"
    )

    assert parsed["action"] == {
        "api": "inspect_pd_schedulers",
        "args": {},
    }


def test_prompt_parser_accepts_gateway_empty_invoke_element():
    agent = LLMAgent(url="mock", api_key="mock", model="claude-test")
    agent.set_tools([
        {
            "type": "function",
            "function": {"name": "inspect_pd_schedulers"},
        }
    ])

    parsed = agent._parse_llm_response(
        "_calls\n<invoke name=\"inspect_pd_schedulers\">\n"
        "</invoke>\n</function_calls>"
    )

    assert parsed["action"] == {
        "api": "inspect_pd_schedulers",
        "args": {},
    }


def test_prompt_parser_accepts_gateway_tool_call_marker():
    agent = LLMAgent(url="mock", api_key="mock", model="claude-test")
    agent.set_tools([
        {
            "type": "function",
            "function": {"name": "help"},
        }
    ])

    parsed = agent._parse_llm_response(
        "助手[TOOL_CALL] help {\"tool_name\": \"inspect_pd_schedulers\"}"
    )

    assert parsed["action"] == {
        "api": "help",
        "args": {"tool_name": "inspect_pd_schedulers"},
    }


def test_prompt_parser_accepts_gateway_markdown_tool_call_marker():
    agent = LLMAgent(url="mock", api_key="mock", model="claude-test")
    agent.set_tools([
        {
            "type": "function",
            "function": {"name": "inspect_pd_schedulers"},
        }
    ])

    parsed = agent._parse_llm_response("_[Tool call: inspect_pd_schedulers]_")

    assert parsed["action"] == {
        "api": "inspect_pd_schedulers",
        "args": {},
    }


def test_prompt_parser_accepts_gateway_fenced_tool_arguments():
    agent = LLMAgent(url="mock", api_key="mock", model="claude-test")
    agent.set_tools([
        {
            "type": "function",
            "function": {"name": "submit"},
        }
    ])

    parsed = agent._parse_llm_response(
        "_[Tool call: submit]_\n"
        "```json\n{\"report\": {\"summary\": \"done\"}}\n```"
    )

    assert parsed["action"] == {
        "api": "submit",
        "args": {"report": {"summary": "done"}},
    }


def test_prompt_parser_accepts_gateway_prefixed_tool_markup():
    agent = LLMAgent(url="mock", api_key="mock", model="claude-test")
    agent.set_tools([
        {
            "type": "function",
            "function": {"name": "query_metrics"},
        }
    ])

    parsed = agent._parse_llm_response(
        "toolquery_metrics\n"
        '<parameter name="metric_type">disk_io</parameter>\n'
        "</invoke>"
    )

    assert parsed["action"] == {
        "api": "query_metrics",
        "args": {"metric_type": "disk_io"},
    }


def test_llm_trace_splits_new_and_previous_turn_input_tokens(monkeypatch):
    agent = LLMAgent(url="mock", api_key="mock", model="mock-model", use_native_tools=True)
    agent.init_env_gateway(FakeGateway())
    agent.max_turns = 2
    responses = iter([
        _openai_tool_response(
            ("query_metrics", {"metric_type": "cpu"}),
            input_tokens=120,
            output_tokens=15,
        ),
        _openai_tool_response(
            ("submit", {"diagnosis": "CPU saturation"}),
            input_tokens=155,
            output_tokens=12,
        ),
    ])

    def fake_call(messages):
        response = next(responses)
        agent._record_usage(response)
        return response

    monkeypatch.setattr(agent, "_call_llm", fake_call)

    agent.solve(max_empty_retries=0)

    turns = agent.export_diagnostic_trace()["turns"]
    assert {
        key: turns[0][key]
        for key in ("input_token", "cache_input_token", "output_token")
    } == {"input_token": 120, "cache_input_token": 0, "output_token": 15}
    assert {
        key: turns[1][key]
        for key in ("input_token", "cache_input_token", "output_token")
    } == {"input_token": 35, "cache_input_token": 120, "output_token": 12}


def test_llm_trace_treats_a_smaller_provider_total_as_a_fresh_segment(monkeypatch):
    agent = LLMAgent(
        url="https://api.anthropic.com",
        api_key="mock",
        provider="anthropic",
        model="claude-test",
        use_native_tools=True,
    )
    agent.init_env_gateway(FakeGateway())
    agent.max_turns = 2
    responses = iter([
        _openai_tool_response(
            ("query_metrics", {"metric_type": "cpu"}),
            input_tokens=10_068,
            output_tokens=15,
        ),
        _openai_tool_response(
            ("submit", {"diagnosis": "CPU saturation"}),
            input_tokens=3_634,
            output_tokens=12,
        ),
    ])

    def fake_call(messages):
        response = next(responses)
        agent._record_usage(response)
        return response

    monkeypatch.setattr(agent, "_call_llm", fake_call)

    agent.solve(max_empty_retries=0)

    turns = agent.export_diagnostic_trace()["turns"]
    assert turns[1]["input_token"] == 3_634
    assert turns[1]["cache_input_token"] == 0


@pytest.mark.parametrize("actions", [[], [
    {"api": "submit", "args": {"diagnosis": "first"}},
    {"api": "submit", "args": {"diagnosis": "second"}},
]], ids=["no-tool", "multiple-submit"])
def test_final_submission_requires_exactly_one_submit(actions):
    with pytest.raises(RuntimeError, match="final turn must contain exactly one submit"):
        require_final_submission("LLMAgent", actions)


def test_openai_native_final_round_ignores_tools_after_submit(monkeypatch):
    agent = LLMAgent(
        url="mock",
        api_key="mock",
        model="mock-model",
        use_native_tools=True,
    )
    agent._append_final_turn_prompt()
    monkeypatch.setattr(
        agent,
        "_call_llm",
        lambda messages: _openai_tool_response(
            ("submit", {"diagnosis": "done"}),
            ("query_metrics", {"metric_type": "cpu"}),
        ),
    )

    _, submission = agent._next_final_submission(max_empty_retries=0, agent_name="LLMAgent")

    assert submission == {"diagnosis": "done"}


def test_openai_client_uses_bounded_timeout_and_retries(monkeypatch):
    import openai

    client_kwargs = {}
    payload = {}

    class FakeCompletions:
        @staticmethod
        def create(**request):
            payload.update(request)
            return _openai_stream_from_response(
                _openai_tool_response(("submit", {"diagnosis": "done"}))
            )

    class FakeClient:
        chat = type("FakeChat", (), {"completions": FakeCompletions()})()

    def fake_openai(**kwargs):
        client_kwargs.update(kwargs)
        return FakeClient()

    monkeypatch.setattr(openai, "OpenAI", fake_openai)
    agent = LLMAgent(
        url="https://example.com/v1",
        api_key="test",
        model="gpt-test",
        max_output_tokens=1024,
        reasoning_effort="xhigh",
    )

    agent._call_openai_llm([{"role": "user", "content": "test"}])

    assert client_kwargs["timeout"] == LLM_REQUEST_TIMEOUT_SECONDS
    assert client_kwargs["max_retries"] == LLM_REQUEST_MAX_RETRIES
    assert payload["max_tokens"] == 1024
    assert payload["reasoning_effort"] == "xhigh"
    assert agent.get_usage_events() == [{
        "call_id": "llm-call-000001",
        "provider": "openai",
        "model": "gpt-test",
        "input_tokens": 100,
        "output_tokens": 20,
        "cached_input_tokens": 0,
        "cache_write_input_tokens": 0,
        "reasoning_effort": "xhigh",
    }]


def test_openai_client_records_explicit_reasoning_effort(monkeypatch):
    import openai

    payload = {}

    class FakeCompletions:
        @staticmethod
        def create(**request):
            payload.update(request)
            return _openai_stream_from_response(
                _openai_tool_response(("submit", {"diagnosis": "done"}))
            )

    class FakeClient:
        chat = type("FakeChat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr(openai, "OpenAI", lambda **kwargs: FakeClient())
    agent = LLMAgent(
        url="https://example.com/v1",
        api_key="test",
        model="test-model-a",
        reasoning_effort="xhigh",
    )

    agent._call_openai_llm([{"role": "user", "content": "test"}])

    assert payload["reasoning_effort"] == "xhigh"
    assert "temperature" not in payload
    assert agent.get_usage_events()[0]["reasoning_effort"] == "xhigh"


def test_openai_reasoning_effort_is_forwarded_without_sampling_temperature(monkeypatch):
    import openai

    payload = {}

    class FakeCompletions:
        @staticmethod
        def create(**request):
            payload.update(request)
            return _openai_stream_from_response(
                _openai_tool_response(("submit", {"diagnosis": "done"}))
            )

    class FakeClient:
        chat = type("FakeChat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr(openai, "OpenAI", lambda **kwargs: FakeClient())
    agent = LLMAgent(
        url="https://example.com/v1",
        api_key="test",
        model="test-model-a",
        reasoning_effort="xhigh",
    )

    agent._call_openai_llm([{"role": "user", "content": "test"}])

    assert payload["reasoning_effort"] == "xhigh"
    assert "temperature" not in payload


def test_anthropic_tool_results_merge_without_desynchronizing_trace():
    agent = LLMAgent(
        url="https://example.com/v1/messages",
        api_key="test",
        model="claude-test",
        provider="anthropic",
    )
    first = {
        "role": "user",
        "content": [{"type": "tool_result", "tool_use_id": "tool-1", "content": "one"}],
    }
    second = {
        "role": "user",
        "content": [{"type": "tool_result", "tool_use_id": "tool-2", "content": "two"}],
    }

    agent._append_anthropic_conversation_message(first)
    agent._append_anthropic_conversation_message(second)

    assert len(agent._conversation_history) == 2
    assert agent._conversation_raw_history == agent._conversation_history
    assert agent._conversation_phases[-1]["messages"] == agent._conversation_history
    assert [block["tool_use_id"] for block in agent._conversation_history[-1]["content"]] == [
        "tool-1",
        "tool-2",
    ]


def test_anthropic_client_uses_bounded_timeout_and_retries(monkeypatch):
    import anthropic

    client_kwargs = {}
    request_payloads = []

    class FakeMessages:
        @staticmethod
        def stream(**payload):
            request_payloads.append(payload)
            return _anthropic_stream_response(
                _anthropic_tool_response("submit", {"diagnosis": "done"})
            )

    class FakeClient:
        messages = FakeMessages()

    def fake_anthropic(**kwargs):
        client_kwargs.update(kwargs)
        return FakeClient()

    monkeypatch.setattr(anthropic, "Anthropic", fake_anthropic)
    agent = LLMAgent(
        url="https://example.com",
        api_key="test",
        model="claude-test",
        provider="anthropic",
    )

    agent._call_anthropic_llm([{"role": "user", "content": "test"}])

    assert client_kwargs["timeout"] == LLM_REQUEST_TIMEOUT_SECONDS
    assert client_kwargs["max_retries"] == LLM_REQUEST_MAX_RETRIES
    assert "temperature" not in request_payloads[0]
    assert request_payloads[0]["max_tokens"] == LLM_DEFAULT_MAX_OUTPUT_TOKENS


def main():
    print("=" * 60)
    print("MockLLMAgent 单元测试 (无需 Docker)")
    print("=" * 60)

    agent = MockLLMAgent(
        url="http://localhost:8000",
        api_key="mock-key",
        system_prompt="Mock system prompt; Orchestrator normally injects the Env prompt.",
        enable_log=True,
    )

    gateway = FakeGateway()
    agent.init_env_gateway(gateway)
    agent.max_turns = 20

    print("\n--- 测试 solve() 自驱动循环 ---\n")
    submission = agent.solve()
    print(f"submission: {submission}")
    print(f"网关收到 {len(gateway.calls)} 次工具调用:")
    for call in gateway.calls:
        print(f"  - {call['api']}({call['args']})")

    assert gateway.calls, "solve() 应至少触发一次环境调用"
    assert all(c["api"] not in ("submit", "exit") for c in gateway.calls), \
        "submit/exit 不应作为环境调用打到网关"

    print("\n--- 测试 print_history() ---\n")
    agent.print_history()

    print("\n--- 测试 reset_conversation() ---\n")
    agent.reset_conversation()
    print("对话已重置")
    print(f"当前对话历史长度: {len(agent.get_conversation_history())}")

    print("\n=== 全部测试通过 ===")


def test_anthropic_payload_carries_metadata_user_id(monkeypatch):
    agent = LLMAgent(
        url="mock",
        api_key="mock",
        provider="anthropic",
        model="claude-test",
        reasoning_effort="low",
    )
    captured = {}

    class FakeStream:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def get_final_message(self):
            return {
                "type": "message",
                "role": "assistant",
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 5,
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                },
                "content": [{"type": "text", "text": "ok"}],
            }

    class FakeMessages:
        def stream(self, **kwargs):
            captured.update(kwargs)
            return FakeStream()

    class FakeAnthropic:
        def __init__(self, **kwargs):
            self.messages = FakeMessages()

    import anthropic as anthropic_module

    monkeypatch.setattr(anthropic_module, "Anthropic", FakeAnthropic)

    dumped = agent._call_anthropic_llm([{"role": "user", "content": "hi"}])

    assert agent.metadata_user_id.startswith("aiopsbench-")
    assert captured["metadata"] == {"user_id": agent.metadata_user_id}
    assert captured["output_config"] == {"effort": "low"}
    assert "reasoning_effort" not in captured
    assert dumped["content"][0]["text"] == "ok"


def test_llm_config_provides_default_reasoning_effort(tmp_path):
    import json as _json

    cfg = {
        "claude-test": {
            "url": "https://example.com",
            "api_key": "k",
            "reasoning_effort": "low",
        }
    }
    path = tmp_path / "llm_config.json"
    path.write_text(_json.dumps(cfg))

    agent = LLMAgent(model="claude-test", config_path=str(path))
    assert agent.reasoning_effort == "low"


def test_anthropic_metadata_user_id_is_shared_across_agents(monkeypatch):
    import anthropic as anthropic_module

    monkeypatch.setattr(anthropic_module, "Anthropic", lambda **_k: None)
    first = LLMAgent(url="mock", api_key="mock", provider="anthropic", model="claude-test")
    second = LLMAgent(url="mock", api_key="mock", provider="anthropic", model="claude-test")
    assert first.metadata_user_id == second.metadata_user_id == "aiopsbench-shared"


def test_openai_llm_streams_with_usage_and_metadata_free_payload(monkeypatch):
    from types import SimpleNamespace

    agent = LLMAgent(url="mock", api_key="mock", provider="openai", model="gpt-test")
    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return iter([
                SimpleNamespace(
                    id="chatcmpl-1", created=123, model="gpt-test", usage=None,
                    choices=[SimpleNamespace(
                        delta=SimpleNamespace(
                            content=None, reasoning_content=None,
                            tool_calls=[SimpleNamespace(
                                index=0, id="call_1", type="function",
                                function=SimpleNamespace(
                                    name="query_metrics",
                                    arguments='{"metric_ty',
                                ),
                            )],
                        ),
                        finish_reason=None,
                    )],
                ),
                SimpleNamespace(
                    id=None, created=None, model=None, usage=None,
                    choices=[SimpleNamespace(
                        delta=SimpleNamespace(
                            content=None, reasoning_content=None,
                            tool_calls=[SimpleNamespace(
                                index=0, id=None, type=None,
                                function=SimpleNamespace(
                                    name=None, arguments='pe": "cpu"}',
                                ),
                            )],
                        ),
                        finish_reason="tool_calls",
                    )],
                ),
                SimpleNamespace(
                    id=None, created=None, model=None,
                    usage=SimpleNamespace(model_dump=lambda: {
                        "prompt_tokens": 100,
                        "completion_tokens": 20,
                        "prompt_tokens_details": {"cached_tokens": 80},
                    }),
                    choices=[],
                ),
            ])

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    import openai as openai_module

    monkeypatch.setattr(openai_module, "OpenAI", FakeOpenAI)

    dumped = agent._call_openai_llm([{"role": "user", "content": "hi"}])

    assert captured["stream"] is True
    assert captured["stream_options"] == {"include_usage": True}
    message = dumped["choices"][0]["message"]
    assert message["tool_calls"][0]["function"]["name"] == "query_metrics"
    assert message["tool_calls"][0]["function"]["arguments"] == '{"metric_type": "cpu"}'
    assert dumped["usage"]["prompt_tokens"] == 100
    assert dumped["choices"][0]["finish_reason"] == "tool_calls"


def test_openai_streaming_keeps_reasoning_content_and_text():
    from types import SimpleNamespace

    chunks = [
        SimpleNamespace(id="chatcmpl-2", created=1, model="glm-test", usage=None, choices=[
            SimpleNamespace(
                delta=SimpleNamespace(content="答", reasoning_content="想", tool_calls=None),
                finish_reason=None,
            ),
        ]),
        SimpleNamespace(id=None, created=None, model=None, usage=None, choices=[
            SimpleNamespace(
                delta=SimpleNamespace(content="案", reasoning_content=None, tool_calls=None),
                finish_reason="stop",
            ),
        ]),
        SimpleNamespace(
            id=None, created=None, model=None,
            usage=SimpleNamespace(model_dump=lambda: {"prompt_tokens": 5, "completion_tokens": 3}),
            choices=[],
        ),
    ]
    dumped = LLMAgent._assemble_openai_stream(iter(chunks))
    message = dumped["choices"][0]["message"]
    assert message["content"] == "答案"
    assert message["reasoning_content"] == "想"
    assert dumped["usage"]["completion_tokens"] == 3


if __name__ == "__main__":
    main()
