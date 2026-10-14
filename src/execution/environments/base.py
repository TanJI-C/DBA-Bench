from abc import ABC, abstractmethod
from datetime import datetime
import inspect
import json
import threading
from typing import Any, Dict, List, Optional, Sequence

from src.agent_language import agent_text
from src.database.system import DatabaseSystem
from src.execution.deployments.base import BaseDeployment
from src.execution.tidb_tool_definitions import control_tool_definitions, canonical_tool_definition
from src.execution.tools import (
    Tool,
    ToolParameter,
    ToolSpec,
    _annotation_to_json_type,
    _resolve_agent_text,
    lazy_agent_text,
)
from src.protocols.report import STRUCTURED_REPORT_JSON_SCHEMA


class BaseEnv(ABC):
    """
    执行与目标层 - 环境层。
    职责：
    1. 是 FaultInjector 和 Workload 发挥作用的最终载体（即"运行中的数据库实例"）。
    2. 对外暴露工具接口，由 Orchestrator 调用 execute_action 统一执行。
    3. 提供 help 方法返回工具信息。
    """

    system: DatabaseSystem

    def __init__(
        self,
        workload=None,
        deployment: Optional[BaseDeployment] = None,
        enabled_tools: Optional[Sequence[str]] = None,
    ):
        self.workload = workload
        self.deployment = deployment
        self._conn = None
        # Event injectors, the Agent action path and trusted evaluators share
        # this connection from concurrent threads; every use must hold the lock.
        self._sql_connection_lock = threading.RLock()
        self._enabled_tool_specs: List[ToolSpec] = []
        self._alias_to_tool_spec: Dict[str, ToolSpec] = {}
        self._configure_tools(enabled_tools)

    def should_recycle_workload_connection(self, connection) -> bool:
        return False

    def close_workload_connection(self, connection) -> None:
        connection.close()

    @staticmethod
    def _parse_metric_timestamp(value: str, parameter: str) -> datetime:
        if not isinstance(value, str):
            raise ValueError(
                f"query_metrics.{parameter} must use YYYY-MM-DD HH:mm:ss, got {value!r}"
            )
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError as exc:
            raise ValueError(
                f"query_metrics.{parameter} must use YYYY-MM-DD HH:mm:ss, got {value!r}"
            ) from exc

    @classmethod
    def _metric_time_range(
        cls,
        start_timestamp: Optional[str],
        end_timestamp: Optional[str],
    ) -> tuple[Optional[datetime], Optional[datetime]]:
        if (start_timestamp is None) != (end_timestamp is None):
            raise ValueError(
                "query_metrics.start_timestamp and query_metrics.end_timestamp must be provided together"
            )
        if start_timestamp is None:
            return None, None
        start = cls._parse_metric_timestamp(start_timestamp, "start_timestamp")
        end = cls._parse_metric_timestamp(end_timestamp, "end_timestamp")
        if start > end:
            raise ValueError(
                "query_metrics.start_timestamp must not be after end_timestamp: "
                f"start_timestamp={start_timestamp!r}, end_timestamp={end_timestamp!r}"
            )
        return start, end

    @staticmethod
    def _metric_success(metric: str, kind: str, **payload) -> str:
        return json.dumps({
            "status": "success",
            "metric": metric,
            "kind": kind,
            **payload,
        }, ensure_ascii=False, default=str)

    @abstractmethod
    def deploy(self):
        """部署环境（启动数据库容器/集群）"""
        pass

    @abstractmethod
    def teardown(self):
        """销毁环境"""
        pass

    def configure_case(self, case) -> None:
        if case.system is not self.system:
            raise TypeError(
                f"Environment/case system mismatch: environment={type(self).__name__}, "
                f"environment_system={self.system.value!r}, case={case.case_id!r}, "
                f"case_system={case.system.value!r}"
            )
        self.configure_runtime(case.runtime)

    @abstractmethod
    def configure_runtime(self, runtime) -> None:
        raise NotImplementedError

    @abstractmethod
    def base_snapshot_name(self, case) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def snapshot_name(self, scenario_id: str, case) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def snapshot_exists(self, snapshot_name: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def select_snapshot(self, snapshot_name: str, base_snapshot_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_snapshot(self, snapshot_name: str, labels: Dict[str, str]) -> None:
        raise NotImplementedError

    def execute_action(self, api: str, args: Dict[str, Any]) -> str:
        """
        统一执行 action 的入口。
        :param api: 工具名
        :param args: 工具参数
        :return: JSON 格式的执行结果
        """
        return self._execute_tool(api, args)

    @Tool(
        description=lazy_agent_text(
            zh="查询当前环境可用工具的帮助信息",
            en="Get help information about the tools available in the current environment",
        ),
        arg_descriptions={"tool_name": lazy_agent_text(
            zh="工具名称，不传则返回所有工具列表",
            en="Tool name; omit it to return the list of all tools",
        )},
        definition=lambda: control_tool_definitions()["help"],
    )
    def help(self, tool_name: Optional[str] = None) -> str:
        """
        返回工具帮助信息。
        :param tool_name: 工具名，None 表示返回所有工具列表
        :return: JSON 格式的帮助信息
        """
        if tool_name is None:
            return json.dumps({
                "status": "success",
                "tools": [
                    {
                        "name": spec.alias,
                        "description": spec.description,
                        "has_definition": spec.definition is not None,
                    }
                    for spec in self.get_tool_specs()
                ],
                "message": agent_text(
                    zh="可用工具列表。使用 help(tool_name) 查看详细参数信息",
                    en="List of available tools. Use help(tool_name) to see detailed parameter information",
                ),
            }, ensure_ascii=False, separators=(",", ":"))
        spec = self._alias_to_tool_spec.get(tool_name)
        if spec is None:
            return json.dumps({
                "status": "error",
                "tool": tool_name,
                "error": f"Unknown tool: {tool_name}",
            }, ensure_ascii=False, separators=(",", ":"))
        result = {
            "status": "success",
            "tool": spec.alias,
            "definition": canonical_tool_definition(spec.definition)
            if spec.definition is not None
            else {
                "name": spec.alias,
                "description": spec.description,
                "parameters": [
                    {
                        "name": parameter.name,
                        "type": parameter.type,
                        "required": parameter.required,
                        "description": parameter.description,
                    }
                    for parameter in spec.parameters
                ],
                "result": {"description": ""},
                "capabilities": {"metrics": [], "resources": []},
                "runtime": {},
            },
        }
        result["definition"].update(self._additional_tool_help(spec.alias))
        return json.dumps(result, ensure_ascii=False, separators=(",", ":"))

    def _additional_tool_help(self, tool_name: str) -> Dict[str, Any]:
        return {}

    @staticmethod
    def _slice_log_output(
        output: str,
        lines: int,
        start_line: Optional[int],
        end_line: Optional[int],
        match_key: Optional[str] = None,
    ) -> dict:
        all_lines = output.splitlines() if output else []
        total_lines = len(all_lines)
        if match_key:
            key = str(match_key)
            folded_key = key.casefold()
            matched_lines = [
                idx + 1
                for idx, line in enumerate(all_lines)
                if folded_key in line.casefold()
            ]
            if start_line is None and end_line is None:
                match_start = 1
                match_end = total_lines
            else:
                match_start = max(int(start_line or 1), 1)
                match_end = (
                    total_lines
                    if end_line == -1
                    else int(end_line)
                    if end_line is not None
                    else match_start + max(int(lines), 1) - 1
                )
            ranges = []
            for matched_line in matched_lines:
                if match_start <= matched_line <= match_end:
                    idx = matched_line - 1
                    ranges.append((max(idx - 1, 0), min(idx + 3, total_lines)))
            merged = []
            for start, end in ranges:
                if merged and start <= merged[-1][1]:
                    merged[-1] = (merged[-1][0], max(merged[-1][1], end))
                else:
                    merged.append((start, end))
            content_lines = [
                line
                for start, end in merged
                for line in all_lines[start:end]
            ]
            page_limit = max(int(lines), 1)
            content_truncated = len(content_lines) > page_limit
            result = {
                "content": "\n".join(content_lines[:page_limit]),
                "total_lines": total_lines,
                "start_line": merged[0][0] + 1 if content_lines else 0,
                "end_line": min(
                    merged[0][0] + len(content_lines[:page_limit])
                    if content_lines
                    else 0,
                    total_lines,
                ),
                "match_key": key,
                "matched_lines": matched_lines,
            }
            if content_truncated:
                result["content_truncated"] = True
            return result
        if start_line is None and end_line is None:
            start = 1
            requested_end = max(int(lines), 1)
        else:
            start = max(int(start_line or 1), 1)
            requested_end = (
                total_lines
                if end_line == -1
                else int(end_line)
                if end_line is not None
                else start + max(int(lines), 1) - 1
            )
        page_limit = max(int(lines), 1)
        end = min(requested_end, start + page_limit - 1)
        content = "\n".join(all_lines[start - 1:end])
        result = {
            "content": content,
            "total_lines": total_lines,
            "start_line": start,
            "end_line": min(end, total_lines) if total_lines else 0,
        }
        if end < requested_end:
            result["content_truncated"] = True
        return result

    @Tool(
        description=lazy_agent_text(
            zh=(
                "提交严格结构化诊断报告并结束诊断流程。diagnosis.conditions 中的 evidence "
                "必须引用已观察到的证据；outcome 必须列出变更和最终验证。提交后不能继续调用工具。"
            ),
            en=(
                "Submit a strictly structured diagnosis report and end the diagnosis process. The evidence in "
                "diagnosis.conditions must cite observed evidence; outcome must list the changes and the final "
                "verification. No tools can be called after submitting."
            ),
        ),
        arg_descriptions={
            "report": lazy_agent_text(
                zh="符合 StructuredReport schema 的诊断报告",
                en="Diagnosis report conforming to the StructuredReport schema",
            ),
        },
        definition=lambda: control_tool_definitions()["submit"],
    )
    def submit(self, report: Dict[str, Any]) -> str:
        return json.dumps({"status": "control", "message": "submit is an Environment terminal tool consumed by Agent.solve()"})

    @Tool(
        description=lazy_agent_text(zh="退出当前诊断流程", en="Exit the current diagnosis process"),
        definition=lambda: control_tool_definitions()["exit"],
    )
    def exit(self) -> str:
        return json.dumps({"status": "exiting"})

    def _configure_tools(self, enabled_tools: Optional[Sequence[str]] = None) -> None:
        all_specs = self._collect_tool_specs()
        requested_tools = enabled_tools if enabled_tools is not None else list(all_specs)

        enabled_specs: List[ToolSpec] = []
        alias_to_tool_spec: Dict[str, ToolSpec] = {}
        for raw_name in requested_tools:
            name = str(raw_name).strip()
            if not name:
                continue
            alias_matches = [
                candidate_id
                for candidate_id, spec in all_specs.items()
                if spec.alias == name
            ]
            if len(alias_matches) > 1:
                raise ValueError(
                    f"Tool alias {name} maps to multiple implementations: {alias_matches}. "
                    "Use the internal tool id when selecting enabled_tools."
                )
            if len(alias_matches) == 1:
                tool_id = alias_matches[0]
            elif name in all_specs:
                tool_id = name
            else:
                raise ValueError(f"Unknown tool name for {self.__class__.__name__}: {name}")

            spec = all_specs[tool_id]
            if spec.alias in alias_to_tool_spec:
                other_id = alias_to_tool_spec[spec.alias].tool_id
                raise ValueError(
                    f"Tool alias conflict in {self.__class__.__name__}: "
                    f"{spec.alias} is provided by both {other_id} and {tool_id}. "
                    "Only one implementation per alias can be enabled."
                )
            alias_to_tool_spec[spec.alias] = spec
            enabled_specs.append(spec)

        self._enabled_tool_specs = enabled_specs
        self._alias_to_tool_spec = alias_to_tool_spec

    def _collect_tool_specs(self) -> Dict[str, ToolSpec]:
        specs: Dict[str, ToolSpec] = {}
        for cls in self.__class__.mro():
            for method_name, func in cls.__dict__.items():
                metadata = getattr(func, "_aiops_tool", None)
                if not metadata:
                    continue
                signature = inspect.signature(func)
                arg_descriptions = metadata.get("arg_descriptions", {})
                parameters = []
                for name, parameter in signature.parameters.items():
                    if name == "self":
                        continue
                    parameters.append(ToolParameter(
                        name=name,
                        type=_annotation_to_json_type(parameter.annotation),
                        required=parameter.default is inspect._empty,
                        description=_resolve_agent_text(arg_descriptions.get(name, "")),
                    ))
                spec = ToolSpec(
                    tool_id=metadata.get("tool_id") or method_name,
                    alias=metadata.get("alias") or method_name,
                    method_name=method_name,
                    description=_resolve_agent_text(metadata.get("description", "")),
                    parameters=tuple(parameters),
                    definition=_resolve_agent_text(metadata.get("definition")),
                )
                if spec.tool_id not in specs:
                    specs[spec.tool_id] = spec
        return specs

    def get_tool_specs(self) -> List[ToolSpec]:
        return list(self._enabled_tool_specs)

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        schemas = [spec.to_openai_schema() for spec in self.get_tool_specs()]
        for schema in schemas:
            function = schema["function"]
            if function["name"] == "submit":
                function["parameters"] = {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["report"],
                    "properties": {"report": STRUCTURED_REPORT_JSON_SCHEMA},
                }
        return schemas

    def build_tool_instructions(self, use_native_tools: bool = False) -> str:
        specs = self.get_tool_specs()
        if use_native_tools:
            tool_names = ", ".join(spec.alias for spec in specs)
            return agent_text(
                zh=(
                    "请分析场景，并通过当前环境提供的 tools 进行函数调用（Function Calling）来执行操作。\n"
                    f"当前环境可用工具: {tool_names}"
                ),
                en=(
                    "Analyze the scenario and perform actions by making function calls (Function Calling) "
                    "with the tools provided by the current environment.\n"
                    f"Tools available in the current environment: {tool_names}"
                ),
            )

        if specs:
            params_label = agent_text(zh="参数", en="Parameters")
            params_notes_label = agent_text(zh="参数说明", en="Parameter descriptions")
            tool_lines = []
            for spec in specs:
                args_str = ", ".join(
                    f"{parameter.name}: {parameter.type}"
                    for parameter in spec.parameters
                )
                tool_lines.append(
                    f"- {spec.alias}: {spec.agent_description()}\n"
                    f"  {params_label}: {args_str}\n"
                    + f"  {params_notes_label}: "
                    + "; ".join(
                        f"{parameter.name}: {parameter.description}"
                        for parameter in spec.parameters
                        if parameter.description
                    )
                )
            formatted_tools = "\n".join(tool_lines)
            return agent_text(
                zh=f"你有以下工具可用：\n{formatted_tools}\n请根据工具描述和参数信息调用合适的工具来执行操作。",
                en=(
                    f"You have the following tools available:\n{formatted_tools}\n"
                    "Call the appropriate tool to perform actions based on the tool descriptions and parameter information."
                ),
            )
        else:
            return agent_text(zh="无可用工具", en="No tools available")

    def _execute_tool(self, api: str, args: Dict[str, Any]) -> str:
        args = args or {}
        spec = self._alias_to_tool_spec.get(api)
        if spec is None:
            return json.dumps({"status": "error", "error": f"Unknown API: {api}"}, ensure_ascii=False)
        method = getattr(self, spec.method_name)
        kwargs = {}
        allowed_args = {parameter.name for parameter in spec.parameters}
        extra_args = [name for name in args if name not in allowed_args]
        if extra_args:
            return json.dumps({
                "status": "error",
                "error": (
                    f"Unexpected argument(s) for {api}: "
                    + ", ".join(sorted(extra_args))
                ),
            }, ensure_ascii=False)
        for parameter in spec.parameters:
            if parameter.required and parameter.name not in args:
                return json.dumps({
                    "status": "error",
                    "error": f"Missing required argument for {api}: {parameter.name}",
                }, ensure_ascii=False)
            if parameter.name in args:
                kwargs[parameter.name] = args[parameter.name]
        try:
            return method(**kwargs)
        except (TypeError, ValueError) as exc:
            return json.dumps({
                "status": "error",
                "error": f"Invalid arguments for {api}: {exc}",
            }, ensure_ascii=False)
