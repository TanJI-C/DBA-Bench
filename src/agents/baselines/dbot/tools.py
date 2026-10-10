"""D-Bot schema-derived ReAct tool helpers."""

import json
import re
from typing import Any, Dict, Iterable, List, Mapping

from src.agents.baselines.telemetry import is_tidb_history_tool_surface


FINISH_TOOL_NAME = "finish"
CITATION_MARK_TOOL_NAME = "mark_citations"
GLOBAL_CONTROL_TOOL_NAMES = {"submit", "exit"}


def is_tidb_tool_surface(tool_schemas: Iterable[Mapping[str, Any]]) -> bool:
    """TiDB surface requires the shared query_history tool plus the TiDB management tool."""
    schemas = list(tool_schemas)
    has_history_tool = any(
        (tool.get("function", tool) or {}).get("name") == "query_history"
        for tool in schemas
        if isinstance(tool, Mapping)
    )
    return is_tidb_history_tool_surface(schemas) if has_history_tool else False


def split_react_reply(text: str, context: str) -> Dict[str, str]:
    match = re.search(
        r"(?is)^\s*Thought\s*:\s*(?P<thought>.*?)\n\s*Action\s*:\s*(?P<action>[^\n]+)\n\s*Action Input\s*:\s*(?P<input>.*)\s*$",
        text.strip(),
    )
    if not match:
        raise ValueError(
            f"D-Bot {context} reply does not match Thought/Action/Action Input format: {text!r}"
        )
    return {
        "thought": match.group("thought").strip(),
        "action": match.group("action").strip(),
        "action_input": match.group("input").strip(),
    }


def parse_json_input(raw: str, context: str) -> Dict[str, Any]:
    value = raw.strip()
    if value.startswith("(") and value.endswith(")"):
        value = value[1:-1].strip()
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"D-Bot {context} action input is not valid JSON: {raw!r}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"D-Bot {context} action input must be a JSON object: input={raw!r}")
    return parsed


def tool_names_from_schemas(tool_schemas: Iterable[Dict[str, Any]]) -> List[str]:
    names = []
    for schema in tool_schemas:
        function = schema.get("function", schema)
        name = function.get("name")
        if name:
            names.append(name)
    return names


def react_tool_names(tool_schemas: Iterable[Dict[str, Any]]) -> List[str]:
    return tool_names_from_schemas(tool_schemas)


def react_tool_prompt(tool_schemas: Iterable[Dict[str, Any]]) -> str:
    lines = []
    for schema in tool_schemas:
        function = schema.get("function", schema)
        name = function["name"]
        description = function.get("description", "")
        parameters = function.get("parameters", {}).get("properties", {})
        required = set(function.get("parameters", {}).get("required", []))
        args = []
        for arg_name, spec in parameters.items():
            marker = "required" if arg_name in required else "optional"
            args.append(f"{arg_name}: {spec.get('type', 'string')} ({marker})")
        arg_text = ", ".join(args) if args else "no arguments"
        lines.append(f"- {name}: {description}\n  Action Input JSON fields: {arg_text}")
    return "\n".join(lines)


def validate_react_tool(tool_name: str, tool_schemas: Iterable[Dict[str, Any]]) -> None:
    names = react_tool_names(tool_schemas)
    if tool_name not in names:
        raise ValueError(f"D-Bot tool {tool_name!r} is not available; available={names!r}")


def finish_tool_schema() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": FINISH_TOOL_NAME,
            "description": (
                "Finish the current D-Bot expert trajectory candidate with a "
                "structured diagnosis, solution list, and supporting knowledge."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "diagnose": {"type": "string", "description": "Root cause diagnosis for this candidate"},
                    "solution": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Recommended solutions for this candidate",
                    },
                    "knowledge": {
                        "type": "string",
                        "description": "Evidence or knowledge used by this candidate",
                    },
                },
                "required": ["diagnose", "solution", "knowledge"],
            },
        },
    }


def citation_mark_tool_schema() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": CITATION_MARK_TOOL_NAME,
            "description": (
                "Submit the final D-Bot report sections after marking citation indices "
                "in each paragraph that relies on a citation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "root_cause": {
                        "type": "string",
                        "description": "Root cause analysis with citation indices marked",
                    },
                    "solutions": {
                        "type": "string",
                        "description": "Solutions with citation indices marked",
                    },
                },
                "required": ["root_cause", "solutions"],
            },
        },
    }


def expert_tool_schemas(tool_schemas: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    schemas = []
    for schema in tool_schemas:
        function = schema.get("function", schema)
        if function["name"] not in GLOBAL_CONTROL_TOOL_NAMES:
            schemas.append(schema)
    schemas.append(finish_tool_schema())
    return schemas
