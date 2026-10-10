from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import yaml


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _normalize_openai_messages(messages: list[dict]) -> list[dict]:
    normalized_messages = []
    for message in messages:
        normalized = dict(message)
        content = normalized.get("content")
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    text_parts.append(json.dumps(block, ensure_ascii=False))
                elif block.get("type") == "tool_result":
                    text_parts.append(block.get("content", ""))
            normalized["content"] = "\n".join(text_parts)
        normalized_messages.append(normalized)
    return normalized_messages


def _openai_tool_calls_to_anthropic(message: dict) -> list[dict]:
    blocks = []
    if message.get("content"):
        blocks.append({"type": "text", "text": str(message["content"])})
    for tool_call in message.get("tool_calls", []) or []:
        function = tool_call.get("function", {})
        arguments = function.get("arguments", {})
        inputs = arguments if isinstance(arguments, dict) else json.loads(arguments or "{}")
        blocks.append(
            {
                "type": "tool_use",
                "id": tool_call.get("id", ""),
                "name": function.get("name", "unknown"),
                "input": inputs,
            }
        )
    return blocks


def _append_anthropic_message(messages: list[dict], message: dict) -> None:
    content = message.get("content", "")
    if content in ("", []):
        return
    if messages and messages[-1].get("role") == message.get("role"):
        previous = messages[-1].get("content", "")
        first = (
            previous
            if isinstance(previous, list)
            else [{"type": "text", "text": str(previous)}]
        )
        second = content if isinstance(content, list) else [{"type": "text", "text": str(content)}]
        messages[-1]["content"] = first + second
    else:
        messages.append(message)


def _anthropic_messages(messages: list[dict]) -> tuple[str, list[dict]]:
    system_parts = []
    output = []
    for message in messages:
        role = message.get("role")
        content = message.get("content", "")
        if role == "system" and content:
            system_parts.append(str(content))
        elif role in {"user", "assistant"}:
            normalized = {"role": role, "content": content if content is not None else ""}
            if role == "assistant" and message.get("tool_calls"):
                normalized["content"] = _openai_tool_calls_to_anthropic(message)
            _append_anthropic_message(output, normalized)
        elif role == "tool":
            _append_anthropic_message(
                output,
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": message.get("tool_call_id", ""),
                            "content": content
                            if isinstance(content, str)
                            else json.dumps(content, ensure_ascii=False),
                        }
                    ],
                },
            )
    return "\n\n".join(system_parts), output


def _anthropic_tools(tools: list[dict]) -> list[dict]:
    return [
        {
            "name": tool["function"]["name"],
            "description": tool["function"].get("description", ""),
            "input_schema": tool["function"].get(
                "parameters", {"type": "object", "properties": {}}
            ),
        }
        for tool in tools
    ]


def _request_payload(protocol: str, messages: list[dict], tools: list[dict]) -> dict:
    if protocol == "anthropic":
        system, converted = _anthropic_messages(messages)
        payload = {"messages": converted}
        if system:
            payload["system"] = system
        if tools:
            payload["tools"] = _anthropic_tools(tools)
        return payload
    payload = {"messages": _normalize_openai_messages(messages)}
    if tools:
        payload["tools"] = tools
    return payload


def _output_payload(protocol: str, message: dict) -> Any:
    if protocol == "anthropic":
        if message.get("tool_calls"):
            return _openai_tool_calls_to_anthropic(message)
        return message.get("content", "")
    output = {"content": message.get("content")}
    if message.get("tool_calls"):
        output["tool_calls"] = message["tool_calls"]
    return output


def _native_tool_calls(message: dict) -> bool:
    if message.get("tool_calls"):
        return True
    content = message.get("content")
    return isinstance(content, list) and any(
        isinstance(block, dict) and block.get("type") == "tool_use" for block in content
    )


@dataclass(frozen=True)
class ReconstructedCall:
    input_payload: dict
    output_payload: Any


def _react_calls(trace: dict, protocol: str, tools: list[dict]) -> list[ReconstructedCall]:
    history = trace.get("conversation_history", [])
    native = any(
        message.get("role") == "assistant" and _native_tool_calls(message)
        for message in history
    )
    return [
        ReconstructedCall(
            _request_payload(protocol, history[:index], tools if native else []),
            _output_payload(protocol, message),
        )
        for index, message in enumerate(history)
        if message.get("role") == "assistant"
    ]


def _dbaiops_calls(trace: dict, protocol: str, tools: list[dict]) -> list[ReconstructedCall]:
    calls = []
    for turn in trace["turns"]:
        messages = turn.get("messages")
        if not messages:
            continue
        tool_calls = [
            {
                "type": "function",
                "function": {
                    "name": action["api"],
                    "arguments": canonical_json(action.get("args", {})),
                },
            }
            for action in turn.get("actions", [])
        ]
        output = {"role": "assistant", "content": None, "tool_calls": tool_calls}
        calls.append(
            ReconstructedCall(
                _request_payload(protocol, messages, tools),
                _output_payload(protocol, output),
            )
        )
    return calls


def _dbot_calls(trace: dict, protocol: str, tools: list[dict]) -> list[ReconstructedCall]:
    history = trace.get("conversation_history", [])
    calls = []
    for index, message in enumerate(history):
        if message.get("role") != "user" or not message.get("task"):
            continue
        if index + 1 >= len(history) or history[index + 1].get("role") != "assistant":
            raise ValueError(
                f"D-Bot task has no assistant response: run_id={trace['metadata']['run_id']!r}, "
                f"history_index={index}"
            )
        assistant = history[index + 1]
        system = trace.get("prompts", {}).get("system")
        if not system:
            raise ValueError(
                f"D-Bot trace lacks its system prompt: run_id={trace['metadata']['run_id']!r}"
            )
        calls.append(
            ReconstructedCall(
                _request_payload(
                    protocol,
                    [
                        {"role": "system", "content": system},
                        {"role": "user", "content": message.get("content", "")},
                    ],
                    tools if _native_tool_calls(assistant) else [],
                ),
                _output_payload(protocol, assistant),
            )
        )
    return calls


def _reconstructed_calls(
    trace: dict, protocol: str, tools: list[dict], expert_tools: list[dict]
) -> list[ReconstructedCall]:
    agent_type = trace["metadata"]["agent_type"]
    if agent_type == "LLMAgent":
        return _react_calls(trace, protocol, tools)
    if agent_type == "DbaiopsAgent":
        return _dbaiops_calls(trace, protocol, tools)
    if agent_type == "DbotAgent":
        return _dbot_calls(trace, protocol, expert_tools)
    raise ValueError(
        f"Unsupported trace agent type: run_id={trace['metadata']['run_id']!r}, "
        f"agent_type={agent_type!r}"
    )


class Tokenizers:
    def __init__(self, config: dict, cache_dir: Path):
        self.config = config
        self.cache_dir = cache_dir
        self.loaded: dict[str, Any] = {}

    def count(self, model: str, text: str) -> int:
        tokenizer = self._load(model)
        spec = self.config["models"][model]["tokenizer"]
        if spec["backend"] == "huggingface":
            return len(tokenizer.encode(text, add_special_tokens=False))
        return len(tokenizer.encode(text))

    def _load(self, model: str) -> Any:
        if model in self.loaded:
            return self.loaded[model]
        spec = self.config["models"][model]["tokenizer"]
        target = self.cache_dir / spec["cache_key"]
        if spec["backend"] == "huggingface":
            from transformers import AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(
                target,
                local_files_only=True,
                trust_remote_code=False,
                use_fast=True,
            )
        elif spec["backend"] == "tiktoken":
            os.environ["TIKTOKEN_CACHE_DIR"] = str(target)
            import tiktoken

            tokenizer = tiktoken.get_encoding(spec["encoding"])
        else:
            raise ValueError(
                f"Unsupported tokenizer backend: model={model!r}, backend={spec['backend']!r}"
            )
        self.loaded[model] = tokenizer
        return tokenizer


def load_token_config(path: Path) -> dict:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    if config["schema_version"] != 1:
        raise ValueError(f"Unsupported token config schema: path={path}")
    return config


def _rates(
    pricing: dict,
    input_tokens: int,
    cached_input_tokens: int,
    cache_write_input_tokens: int,
) -> tuple[float | None, float | None, float | None, float | None]:
    if pricing["status"] != "official":
        return None, None, None, None
    if "tiers" in pricing:
        matches = [tier for tier in pricing["tiers"] if input_tokens <= tier["max_input_tokens"]]
        if not matches:
            raise ValueError(
                f"No pricing tier covers input_tokens={input_tokens}: tiers={pricing['tiers']}"
            )
        tier = matches[0]
        if cached_input_tokens and "cached_input_usd_per_million" not in tier:
            raise ValueError(
                f"Pricing tier lacks a cached-input rate: input_tokens={input_tokens}, "
                f"cached_input_tokens={cached_input_tokens}, tier={tier}"
            )
        if cache_write_input_tokens and "cache_write_input_usd_per_million" not in tier:
            raise ValueError(
                f"Pricing tier lacks a cache-write rate: input_tokens={input_tokens}, "
                f"cache_write_input_tokens={cache_write_input_tokens}, tier={tier}"
            )
        input_rate = tier["input_usd_per_million"]
        return (
            input_rate,
            tier.get("cached_input_usd_per_million"),
            tier.get("cache_write_input_usd_per_million"),
            tier["output_usd_per_million"],
        )
    input_rate = pricing["input_usd_per_million"]
    if cache_write_input_tokens and "cache_write_input_usd_per_million" not in pricing:
        raise ValueError(
            f"Model pricing lacks a cache-write rate: input_tokens={input_tokens}, "
            f"cache_write_input_tokens={cache_write_input_tokens}, pricing={pricing}"
        )
    return (
        input_rate,
        pricing["cached_input_usd_per_million"],
        pricing.get("cache_write_input_usd_per_million"),
        pricing["output_usd_per_million"],
    )


@cache
def _tool_schemas(system: str) -> tuple[list[dict], list[dict]]:
    from src.agents.baselines.dbot.tools import expert_tool_schemas
    from src.execution.environment import PGEnv, TiDBEnv

    environments = {
        "postgresql": lambda: PGEnv(tool_profile="general_knowledge"),
        "tidb": lambda: TiDBEnv(run_id="token-accounting"),
    }
    try:
        env = environments[system]()
    except KeyError as exc:
        raise ValueError(f"Unsupported trace database system: system={system!r}") from exc
    tools = env.get_tool_schemas()
    return tools, expert_tool_schemas(tools)


def account_tokens(
    trace: dict,
    model: str,
    config: dict,
    tokenizers: Tokenizers,
) -> dict[str, Any]:
    if trace.get("$schema") != "run_trace_v3":
        raise ValueError(
            f"Unsupported trace schema: run_id={trace.get('metadata', {}).get('run_id')!r}, "
            f"schema={trace.get('$schema')!r}"
        )
    provider_usage = trace.get("llm_usage", [])
    if provider_usage:
        values = []
        for event in provider_usage:
            token_fields = {
                "input_tokens": event.get("input_tokens"),
                "output_tokens": event.get("output_tokens"),
                "cached_input_tokens": event.get("cached_input_tokens", 0),
                "cache_write_input_tokens": event.get("cache_write_input_tokens", 0),
            }
            if not all(isinstance(value, int) for value in token_fields.values()):
                raise ValueError(
                    f"Provider usage lacks integer token counts: "
                    f"run_id={trace['metadata']['run_id']!r}, event={event!r}"
                )
            values.append(
                (
                    event["input_tokens"],
                    event["output_tokens"],
                    event.get("cached_input_tokens", 0),
                    event.get("cache_write_input_tokens", 0),
                )
            )
        method = "provider_reported"
        tokenizer_match = "provider_reported"
    else:
        tools, expert_tools = _tool_schemas(trace["metadata"]["system"])
        protocol = config["models"][model].get("protocol", "openai")
        calls = _reconstructed_calls(trace, protocol, tools, expert_tools)
        agent_type = trace["metadata"]["agent_type"]
        cumulative_context = agent_type in {"LLMAgent", "DbaiopsAgent"}
        values = []
        previous_input = 0
        for index, call in enumerate(calls):
            call_input = tokenizers.count(model, canonical_json(call.input_payload))
            if cumulative_context and call_input < previous_input:
                raise ValueError(
                    "Reconstructed input tokens decreased between calls: "
                    f"run_id={trace['metadata']['run_id']!r}, call_index={index + 1}, "
                    f"previous_input_tokens={previous_input}, input_tokens={call_input}"
                )
            values.append(
                (
                    call_input,
                    tokenizers.count(model, canonical_json(call.output_payload)),
                    previous_input if cumulative_context else 0,
                    0,
                )
            )
            previous_input = call_input
        method = (
            "trace_reconstructed_differential_cache"
            if cumulative_context
            else "trace_reconstructed_independent_calls"
        )
        tokenizer_match = config["models"][model]["tokenizer"]["match"]

    input_tokens = sum(value[0] for value in values)
    output_tokens = sum(value[1] for value in values)
    cached_input_tokens = sum(value[2] for value in values)
    cache_write_input_tokens = sum(value[3] for value in values)
    input_cost = 0.0
    output_cost = 0.0
    pricing = config["models"][model]["pricing"]
    cost_available = True
    for call_input, call_output, call_cached, call_cache_write in values:
        if call_cached + call_cache_write > call_input:
            raise ValueError(
                f"Cached input exceeds total input: run_id={trace['metadata']['run_id']!r}, "
                f"input_tokens={call_input}, cached_input_tokens={call_cached}, "
                f"cache_write_input_tokens={call_cache_write}"
            )
        input_rate, cached_rate, cache_write_rate, output_rate = _rates(
            pricing, call_input, call_cached, call_cache_write
        )
        if input_rate is None or output_rate is None:
            cost_available = False
            break
        input_cost += (
            (call_input - call_cached - call_cache_write) * input_rate
        ) / 1_000_000
        if call_cached:
            input_cost += call_cached * cached_rate / 1_000_000
        if call_cache_write:
            input_cost += call_cache_write * cache_write_rate / 1_000_000
        output_cost += call_output * output_rate / 1_000_000
    return {
        "llm_call_count": len(values),
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "cache_write_input_tokens": cache_write_input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_token_cost_usd": round(input_cost, 10) if cost_available else None,
        "output_token_cost_usd": round(output_cost, 10) if cost_available else None,
        "total_token_cost_usd": round(input_cost + output_cost, 10)
        if cost_available
        else None,
        "token_accounting_method": method,
        "tokenizer_match": tokenizer_match,
        "cost_status": "estimated" if cost_available else "price_unverified",
        "pricing_version": config["pricing_version"],
    }
