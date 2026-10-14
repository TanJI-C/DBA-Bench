from dataclasses import dataclass
import inspect
from functools import partial
import json
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
    get_args,
    get_origin,
)

from src.agent_language import agent_text
from src.execution.tidb_tool_definitions import canonical_tool_definition


def lazy_agent_text(*, zh: str, en: str) -> Callable[[], str]:
    """Defer ``agent_text`` until a tool spec is built, so the run's language applies."""
    return partial(agent_text, zh=zh, en=en)


def _resolve_agent_text(value: Any) -> Any:
    return value() if callable(value) else value


@dataclass(frozen=True)
class ToolParameter:
    name: str
    type: str
    required: bool
    description: str = ""


@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    alias: str
    method_name: str
    description: str
    parameters: Tuple[ToolParameter, ...]
    definition: Optional[Dict[str, Any]] = None

    def agent_description(self) -> str:
        if self.definition is None:
            return self.description
        definition = json.dumps(
            canonical_tool_definition(self.definition),
            ensure_ascii=False,
            separators=(",", ":"),
        )
        label = agent_text(zh="调用定义(JSON)", en="Call definition (JSON)")
        return f"{self.description}\n{label}: {definition}"

    def to_openai_schema(self) -> Dict[str, Any]:
        properties = {
            parameter.name: {
                "type": parameter.type,
                "description": parameter.description,
            }
            for parameter in self.parameters
        }
        # Keep native function-calling constraints aligned with the bound
        # catalog.  Frozen-history cases replace the generic metric definition
        # at runtime; exposing its allowed values prevents models from
        # selecting metrics owned by another database or scenario.
        if self.definition is not None:
            definitions = self.definition.get("parameter_definitions", [])
            by_name = {
                item.get("parameter_name"): item
                for item in definitions
                if isinstance(item, Mapping)
            }
            for name, item in by_name.items():
                allowed = item.get("allowed_values")
                if name in properties and isinstance(allowed, list) and allowed:
                    properties[name]["enum"] = list(allowed)
        required = [
            parameter.name
            for parameter in self.parameters
            if parameter.required
        ]
        return {
            "type": "function",
            "function": {
                "name": self.alias,
                "description": self.agent_description(),
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


def _annotation_to_json_type(annotation: Any) -> str:
    if annotation is inspect._empty:
        return "string"
    origin = get_origin(annotation)
    if origin is Union:
        non_none = [arg for arg in get_args(annotation) if arg is not type(None)]
        return _annotation_to_json_type(non_none[0]) if non_none else "string"
    if origin in (list, List, tuple, Tuple, Sequence):
        return "array"
    if origin in (dict, Dict):
        return "object"
    if annotation is bool:
        return "boolean"
    if annotation is int:
        return "integer"
    if annotation is float:
        return "number"
    return "string"


def Tool(
    *,
    alias: Optional[str] = None,
    description: Union[str, Callable[[], str]],
    arg_descriptions: Optional[Dict[str, Union[str, Callable[[], str]]]] = None,
    tool_id: Optional[str] = None,
    definition: Optional[Union[Dict[str, Any], Callable[[], Dict[str, Any]]]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register an Env method as an agent-visible tool.

    The method name is the internal tool id by default. The alias is the
    function name exposed to the agent. Multiple Env methods may share one alias
    as long as only one of them is enabled for a concrete Env instance.
    ``description``, each ``arg_descriptions`` value and ``definition`` may be a
    zero-argument callable; it is called when the Env builds its tool specs, so
    agent-facing text follows the run's language.
    """
    arg_descriptions = arg_descriptions or {}

    def decorate(func: Callable[..., Any]) -> Callable[..., Any]:
        setattr(func, "_aiops_tool", {
            "alias": alias or func.__name__,
            "description": description,
            "arg_descriptions": arg_descriptions,
            "tool_id": tool_id or func.__name__,
            "definition": definition,
        })
        return func

    return decorate
