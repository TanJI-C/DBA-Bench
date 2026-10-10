import hashlib
import json
import os
import re
import inspect
import re
import shlex
import shutil
import subprocess
import threading
import time
from abc import ABC, abstractmethod
from collections import deque
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple, Union, get_args, get_origin
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlglot import exp, parse
from sqlglot.errors import ParseError

from src.execution.sampler_grid import (
    SAMPLER_LAG_TOLERANCE_INTERVALS,
    SamplerGridStrikes,
)
from src.execution.deployment import (
    BaseDeployment,
    PGDockerDeployment,
    TiDBDockerDeployment,
    lightning_job_id,
    lightning_network_alias,
)
from src.execution.tidb_connection_router import TiDBConnectionRouter
from src.execution.tidb_dr_auto_sync import TiDBDrAutoSyncControl
from src.execution.tidb_tool_definitions import (
    CONTROL_TOOL_DEFINITIONS,
    TIDB_TOOL_DEFINITIONS,
    canonical_tool_definition,
)
from src.execution.history.metrics import (
    MetricFrame,
    MetricQuery,
    MetricService,
    bound_metric_result,
    format_utc_timestamp,
    parse_utc_timestamp,
    render_metric_frame,
    validate_metric_frame,
)
from src.execution.history.records import (
    CapturedRecords,
    FrozenHistoricalRecordStore,
    HistoricalRecordSource,
    HistoricalCoverage,
)
from src.execution.history.timeline import FrozenHistoricalTimeline, FrozenHistoryMetricProvider
from src.execution.history.sql_archive import FrozenHistoricalSqlArchive
from src.execution.postgres_metrics import (
    LivePostgresSamplerMetricProvider,
    POSTGRES_METRIC_CATALOG,
    POSTGRES_QUERY_METRICS_TOOL_DEFINITION,
    PostgresScenarioMetricCatalog,
    postgres_query_metrics_tool_definition,
)
from src.execution.postgres_history import (
    ADDITIVE_COUNTER_FIELDS,
    PG_STATEMENT_SNAPSHOT_SQL,
    PgStatementCounters,
    PgStatementKey,
    PgStatementSnapshot,
    build_slow_query_records_from_logs,
    build_topsql_delta_records,
    capture_statement_snapshot,
    parse_postgres_log_records,
    reject_postgres_public_historical_sql,
)
from src.execution.tidb_history import (
    build_slow_query_records,
    build_topsql_records,
    parse_docker_log_records,
    reject_tidb_public_historical_sql,
)
from src.execution.tidb_metrics import (
    CASE_ONLY_METRICS,
    LivePrometheusMetricProvider,
    PdMetricSampler,
    SQL_BACKED_METRICS,
    TiDBSQLMetricSampler,
    TIDB_METRIC_CATALOG,
)
from src.knowledge.pg_knowledge_base import PGKnowledgeBase
from src.knowledge.tidb_knowledge_base import TiDBKnowledgeBase
from src.scenarios.evaluation.protocol import STRUCTURED_REPORT_JSON_SCHEMA
from src.scenarios.base import (
    DatabaseSystem,
    PostgresCaseRuntime,
    TiDBCaseRuntime,
)


# Agent-facing SQL responses must stay bounded even when a model forgets to
# add a LIMIT to a large diagnostic query. The database query itself is still
# executed normally; the response tells the Agent to refine or aggregate it.
PG_SQL_RESULT_MAX_ROWS = 200
PG_AGENT_SQL_STATEMENT_TIMEOUT = '60s'
PG_AGENT_SQL_LOCK_TIMEOUT = '10s'
PG_SQL_RESULT_MAX_BYTES = 128 * 1024
PG_SQL_VALUE_MAX_CHARS = 2048
SQL_TRUNCATION_HINT = (
    "本次结果超过 128 KiB 已截断：仅返回部分行，超长字段被裁剪到 2048 字符。"
    "请缩小查询窗口后重试：只 SELECT 需要的列（避免对宽系统表使用 SELECT *），"
    "增加 WHERE 过滤或使用更小的 LIMIT，或改用 COUNT/SUM 等聚合；必要时分页逐段查看。"
)


class ReplicationProgressUnavailableError(RuntimeError):
    """A TiCDC feed exists, but its current progress cannot prove delivery health."""

    def __init__(
        self,
        *,
        changefeed_id: str,
        reason: str,
        state: object,
        error: object,
        upstream_tso: int,
        resolved_tso: int,
        checkpoint_tso: int,
    ) -> None:
        self.details = {
            "changefeed_id": changefeed_id,
            "reason": reason,
            "state": state,
            "error": error,
            "upstream_tso": upstream_tso,
            "resolved_tso": resolved_tso,
            "checkpoint_tso": checkpoint_tso,
        }
        super().__init__(
            "TiCDC replication progress is unavailable: "
            f"changefeed_id={changefeed_id!r}, reason={reason!r}, state={state!r}, "
            f"error={error!r}, upstream_tso={upstream_tso}, resolved_tso={resolved_tso}, "
            f"checkpoint_tso={checkpoint_tso}"
        )


def _bounded_cpu_percent(cpu_us_delta: int, elapsed_us: int, cpus: float) -> float:
    """Convert cgroup CPU usage to the catalog's bounded percentage metric."""
    raw_percent = (cpu_us_delta / elapsed_us / cpus) * 100.0
    return round(min(100.0, max(0.0, raw_percent)), 2)


def _bound_sql_value(value: Any) -> Any:
    if isinstance(value, str) and len(value) > PG_SQL_VALUE_MAX_CHARS:
        return value[:PG_SQL_VALUE_MAX_CHARS] + "...[truncated]"
    if isinstance(value, bytes):
        return value[:PG_SQL_VALUE_MAX_CHARS].decode("utf-8", errors="replace") + "...[truncated]"
    if isinstance(value, (list, tuple)):
        return [_bound_sql_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _bound_sql_value(item) for key, item in value.items()}
    return value


def _bound_sql_rows(rows: Sequence[Sequence[Any]]) -> tuple[list[list[Any]], bool]:
    bounded: list[list[Any]] = []
    encoded_bytes = 0
    truncated = len(rows) > PG_SQL_RESULT_MAX_ROWS
    for row in rows[:PG_SQL_RESULT_MAX_ROWS]:
        candidate = [_bound_sql_value(value) for value in row]
        row_bytes = len(json.dumps(candidate, default=str, ensure_ascii=False).encode("utf-8"))
        if bounded and encoded_bytes + row_bytes > PG_SQL_RESULT_MAX_BYTES:
            truncated = True
            break
        bounded.append(candidate)
        encoded_bytes += row_bytes
    return bounded, truncated


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
        return f"{self.description}\n调用定义(JSON): {definition}"

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


@dataclass(frozen=True)
class SqlConnectionSurface:
    """A scenario-registered SQL database exposed through execute_sql."""

    name: str
    database: str
    description: str
    query_examples: Tuple[str, ...]
    write_policy: str = "unrestricted"


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
    description: str,
    arg_descriptions: Optional[Dict[str, str]] = None,
    tool_id: Optional[str] = None,
    definition: Optional[Dict[str, Any]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register an Env method as an agent-visible tool.

    The method name is the internal tool id by default. The alias is the
    function name exposed to the agent. Multiple Env methods may share one alias
    as long as only one of them is enabled for a concrete Env instance.
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
        description="查询当前环境可用工具的帮助信息",
        arg_descriptions={"tool_name": "工具名称，不传则返回所有工具列表"},
        definition=CONTROL_TOOL_DEFINITIONS["help"],
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
                "message": "可用工具列表。使用 help(tool_name) 查看详细参数信息",
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
        description=(
            "提交严格结构化诊断报告并结束诊断流程。diagnosis.conditions 中的 evidence "
            "必须引用已观察到的证据；outcome 必须列出变更和最终验证。提交后不能继续调用工具。"
        ),
        arg_descriptions={
            "report": "符合 StructuredReport schema 的诊断报告",
        },
        definition=CONTROL_TOOL_DEFINITIONS["submit"],
    )
    def submit(self, report: Dict[str, Any]) -> str:
        return json.dumps({"status": "control", "message": "submit is an Environment terminal tool consumed by Agent.solve()"})

    @Tool(
        description="退出当前诊断流程",
        definition=CONTROL_TOOL_DEFINITIONS["exit"],
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
                        description=arg_descriptions.get(name, ""),
                    ))
                spec = ToolSpec(
                    tool_id=metadata.get("tool_id") or method_name,
                    alias=metadata.get("alias") or method_name,
                    method_name=method_name,
                    description=metadata.get("description", ""),
                    parameters=tuple(parameters),
                    definition=metadata.get("definition"),
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
            return (
                "请分析场景，并通过当前环境提供的 tools 进行函数调用（Function Calling）来执行操作。\n"
                f"当前环境可用工具: {tool_names}"
            )

        if specs:
            tool_lines = []
            for spec in specs:
                args_str = ", ".join(
                    f"{parameter.name}: {parameter.type}"
                    for parameter in spec.parameters
                )
                tool_lines.append(
                    f"- {spec.alias}: {spec.agent_description()}\n"
                    f"  参数: {args_str}\n"
                    + "  参数说明: "
                    + "; ".join(
                        f"{parameter.name}: {parameter.description}"
                        for parameter in spec.parameters
                        if parameter.description
                    )
                )
            formatted_tools = "\n".join(tool_lines)
            return f"你有以下工具可用：\n{formatted_tools}\n请根据工具描述和参数信息调用合适的工具来执行操作。"
        else:
            return "无可用工具"

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


class PGEnv(BaseEnv):
    """
    单机 PostgreSQL 环境。
    使用 PGDockerDeployment 进行容器管理。
    """

    # Crash recovery in a small container can take minutes (WAL replay may
    # itself OOM and restart), so one 180s window is not enough. The sampler
    # opens a fresh window per round and only dies after all rounds fail.
    SAMPLER_RECONNECT_TIMEOUT_SEC = 180.0
    SAMPLER_RECONNECT_MAX_ROUNDS = 3
    # Agent-facing SQL shares TiDB's sql_timeout_seconds=35: one runaway
    # diagnostic query (temp spill / unbounded write) must cancel, not fill
    # the disk and kill the environment mid-run. Workload/sampler pools keep
    # their own connections and are unaffected.
    SQL_STATEMENT_TIMEOUT_SECONDS = 35
    # Grid tolerance lives in src/execution/sampler_grid.py and is shared with
    # the TiDB metric-capture grid alignment.

    system = DatabaseSystem.POSTGRESQL

    TOOL_PROFILES = {
        "general_knowledge": (
            "query_metrics",
            "execute_sql",
            "manage_instance",
            "read_log",
            "query_general_knowledge_base",
            "help",
            "submit",
            "exit",
        ),
        "hierarchical_knowledge": (
            "query_metrics",
            "execute_sql",
            "manage_instance",
            "read_log",
            "query_hierarchical_knowledge_base",
            "help",
            "submit",
            "exit",
        ),
        "no_knowledge": (
            "query_metrics",
            "execute_sql",
            "manage_instance",
            "read_log",
            "help",
            "submit",
            "exit",
        ),
        "db_gpt": (
            "whether_is_abnormal_metric",
            "match_diagnose_knowledge",
            "optimize_index_selection",
            "query_metrics",
            "execute_sql",
            "manage_instance",
            "read_log",
            "help",
            "submit",
            "exit",
        ),
    }

    # Keep the Agent surface limited to raw environment observations and
    # scenario-owned providers. SQL-derived detail remains available through
    # execute_sql or direct internal query_metrics() calls.
    AGENT_METRICS = frozenset({
        "cpu",
        "memory",
        "disk_io",
        "active_connections",
        "disk_usage",
        "qps",
        "cache_hit_ratio",
        "workload_activity",
        "filesystem_io",
        "bufferio_waiters",
        "host_pressure",
        "partition_lifecycle",
    })
    FROZEN_HISTORY_PUBLIC_TOOLS = (
        "query_metrics",
        "execute_sql",
        "manage_instance",
        "read_log",
        "help",
        "submit",
        "exit",
    )

    def _frozen_history_public_tools(self) -> tuple[str, ...]:
        tools = [
            "query_metrics",
            "execute_sql",
            "manage_instance",
            "read_log",
        ]
        if self.tool_profile == "general_knowledge":
            tools.append("query_general_knowledge_base")
        elif self.tool_profile == "hierarchical_knowledge":
            tools.append("query_hierarchical_knowledge_base")
        elif self.tool_profile == "db_gpt":
            tools.extend((
                "whether_is_abnormal_metric",
                "match_diagnose_knowledge",
                "optimize_index_selection",
            ))
        elif self.tool_profile != "no_knowledge":
            raise ValueError(
                f"Unsupported PGEnv tool_profile for frozen-history surface: tool_profile={self.tool_profile!r}"
            )
        tools.extend(("help", "submit", "exit"))
        return tuple(tools)

    def select_tool_profile(self, tool_profile: str) -> None:
        self.tool_profile = tool_profile
        try:
            selected_tools = self.TOOL_PROFILES[tool_profile]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported PGEnv tool_profile: {tool_profile}. "
                f"Supported profiles: {', '.join(sorted(self.TOOL_PROFILES))}"
            ) from exc
        self._configure_tools(selected_tools)

    def __init__(self,
                 workload=None,
                 deployment: Optional[BaseDeployment] = None,
                 host: str = "localhost",
                 port: int = 5432,
                 user: str = "postgres",
                 password: str = "password",
                 dbname: str = "testdb",
                 sample_interval_sec: int = 2,
                 tool_profile: str = "general_knowledge",
                 enabled_tools: Optional[Sequence[str]] = None,
                 allow_sampler_jitter: bool = False,
                 allow_sampler_reconnect: bool = False):
        self.tool_profile = tool_profile
        selected_tools = enabled_tools
        if selected_tools is None:
            try:
                selected_tools = self.TOOL_PROFILES[self.tool_profile]
            except KeyError as exc:
                raise ValueError(
                    f"Unsupported PGEnv tool_profile: {self.tool_profile}. "
                    f"Supported profiles: {', '.join(sorted(self.TOOL_PROFILES))}"
                ) from exc
        super().__init__(workload, deployment, enabled_tools=selected_tools)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        if not isinstance(sample_interval_sec, int) or isinstance(sample_interval_sec, bool) or sample_interval_sec <= 0:
            raise ValueError(f"PostgreSQL sample_interval_sec must be a positive integer: sample_interval_sec={sample_interval_sec!r}")
        if not isinstance(allow_sampler_jitter, bool):
            raise ValueError(f"PostgreSQL allow_sampler_jitter must be boolean: value={allow_sampler_jitter!r}")
        if not isinstance(allow_sampler_reconnect, bool):
            raise ValueError(
                f"PostgreSQL allow_sampler_reconnect must be boolean: value={allow_sampler_reconnect!r}"
            )
        self.sample_interval_sec = sample_interval_sec
        self.allow_sampler_jitter = allow_sampler_jitter
        self.allow_sampler_reconnect = allow_sampler_reconnect
        self._metric_catalog = POSTGRES_METRIC_CATALOG
        self._metric_service = MetricService(
            catalog=self._metric_catalog,
            live=LivePostgresSamplerMetricProvider(sample_interval_sec=sample_interval_sec),
        )
        self._sampler_thread: Optional[threading.Thread] = None
        self._sampler_stop = threading.Event()
        self._sampler_condition = threading.Condition()
        self._sampler_conn = None  # 后台线程独立 DB 连接
        self._sampler_reconnected = False
        self._pgss_sampler_reset_observed = False
        self._sampler_failure: Exception | None = None
        self._sampler_grid_strikes = SamplerGridStrikes()
        self._expected_sampler_disconnect_reason: str | None = None
        self._expected_sampler_disconnect_evidence: dict[str, str] | None = None
        self._sampler_last_timestamp_ms: int | None = None
        self._host_cgroup_base: str | None = None
        self._pg_statement_snapshots: deque[PgStatementSnapshot] = deque(maxlen=300)
        self._pg_statement_excluded_queryids: frozenset[int] = frozenset()
        self._case = None
        self._history_timeline: FrozenHistoricalTimeline | None = None
        self._history_sql_archive: FrozenHistoricalSqlArchive | None = None
        # workload runner：后台持续发业务查询，制造"多 fingerprint 噪声"让 agent 自己挑慢的。
        # runner 由 Orchestrator.setup() 启动，env 仅持引用用于查询和 teardown。
        self._workload_runner = None
        # pg_stat_statements 启动基线：deploy 完成时记录的 (userid,dbid,queryid)→counters，
        # topsql 查询时减去基线，从而剔除初始化 SQL 影响、又不破坏历史。
        self._pgss_baseline: PgStatementSnapshot | None = None
        # metrics_hidden() 用：进入 with 块时拍 enter 快照，退出时与 exit 快照差分合入
        # _pgss_baseline，让块内执行的 SQL 对 topsql / slow_queries(finished) 隐身。
        # 用 depth 计数支持嵌套，仅最外层进出生效。
        self._metrics_hidden_depth: int = 0
        self._metrics_hidden_enter_snap: PgStatementSnapshot | None = None
        self._metrics_hidden_allow_pgss_reset: bool | None = None
        self._pg_log_visible_offsets: dict[str, int] = {}
        self._pg_log_hidden_enter_offsets: dict[str, int] | None = None
        self._pg_knowledge_bases: Dict[str, PGKnowledgeBase] = {}
        self._scenario_metric_provider = None
        self._pgbouncer_endpoint: Optional[Dict[str, object]] = None
        self._pgbouncer_runtime_overrides: Dict[str, str] = {}
        self._workload_connection_endpoints: Dict[str, Dict[str, object]] = {}

        if self.deployment is None:
            init_sql_path = None
            workload_data_dir = None
            dataset_manifest_path = None
            image_tag = "default"
            # 临时文件密集的校准负载需要磁盘余量，默认给 8192MB；workload 路径会覆盖成 tpcds 默认值。
            disk_quota_mb = 8192

            if self.workload is not None:
                init_sql_path = self.workload.get_init_sql_path()
                workload_data_dir = self.workload.data_dir
                dataset_manifest_path = self.workload.manifest_path
                image_tag = self.workload.workload_name
                disk_quota_mb = getattr(self.workload, "disk_quota_mb", 8192)

            self.deployment = PGDockerDeployment(
                container_name="aiopsbench-pg",
                postgres_user=user,
                postgres_password=password,
                postgres_db=dbname,
                port=port,
                init_sql_path=init_sql_path,
                workload_data_dir=workload_data_dir,
                dataset_manifest_path=dataset_manifest_path,
                image_name=f"aiopsbench-pg-{image_tag}:latest",
                # 512MB/1CPU 是 Light TPC-DS 在 30s statement timeout 内能跑完的最低配额。
                # resources 参与 baseline 文件命名，改配额会切换到新 baseline 文件。
                # disk_quota 由 env 顶部 disk_quota_mb 传入（workload 默认 8192）。
                resources={
                    "cpus": 1.0,
                    "memory_mb": 512,
                    "shm_size": "256m",
                    "disk_quota_mb": disk_quota_mb,
                },
            )

    def metric_history_catalog(self):
        return self._metric_catalog

    def validate_metric_history_case(self, spec, background_workload) -> None:
        spec.validate(background_workload)
        catalog = self.metric_history_catalog()
        for metric in spec.required_metrics:
            catalog.definition(metric)
            catalog.target_variants(metric, self.deployment)
        for decoy in spec.decoys:
            definition = catalog.definition(decoy.metric)
            if decoy.field not in definition.value_fields:
                raise ValueError(
                    f"Frozen-history decoy field is not in PostgreSQL catalog: decoy_id={decoy.decoy_id!r}, "
                    f"metric={decoy.metric!r}, field={decoy.field!r}, fields={definition.value_fields!r}"
                )
            # HistoryDecoySpec.target selects an assembler source series; it is
            # not the Agent-facing MetricQuery.target contract. Run-local alias
            # targets cannot be validated at configure time and are matched by
            # the assembler's benign-source selection instead.
        unsupported = set(spec.record_sources) - set(HistoricalRecordSource)
        if unsupported:
            raise ValueError(
                f"PostgreSQL frozen-history history has unsupported record sources: "
                f"sources={sorted(item.value for item in unsupported)!r}"
            )

    def metric_history_warmup_seconds(self, required_metrics: tuple[str, ...]) -> float:
        provider = getattr(self, "_scenario_metric_provider", None)
        provider_warmup = getattr(provider, "metric_history_warmup_seconds", None)
        if callable(provider_warmup):
            return float(provider_warmup())
        return max(
            float(self.sample_interval_sec * 2),
            max(float(self.metric_history_catalog().definition(metric).lookback_seconds) for metric in required_metrics),
        )

    def configure_case(self, case) -> None:
        super().configure_case(case)
        self._case = case
        adapter = (
            case.frozen_history_adapter
            if case.frozen_history is not None
            else None
        )
        if adapter is not None:
            if not callable(getattr(adapter, "configure", None)) or not callable(
                getattr(adapter, "metric_definitions", None)
            ):
                raise TypeError(
                    "PostgreSQL frozen-history history adapter must expose configure and metric_definitions: "
                    f"adapter={type(adapter).__name__!r}, case={case.case_id!r}"
                )
            adapter.configure(self, case)
            self._scenario_metric_provider = adapter
            self._metric_catalog = PostgresScenarioMetricCatalog(adapter)
            history_spec = case.frozen_history
            max_points = max(
                300,
                (
                    max(history_spec.normal_capture_seconds, history_spec.fault_capture_seconds)
                    + self.sample_interval_sec - 1
                ) // self.sample_interval_sec + 60,
            )
            self._pg_statement_snapshots = deque(self._pg_statement_snapshots, maxlen=max_points)
            self._metric_service = MetricService(
                catalog=self._metric_catalog,
                live=LivePostgresSamplerMetricProvider(
                    sample_interval_sec=self.sample_interval_sec,
                    max_points=max_points,
                    catalog=self._metric_catalog,
                ),
            )
        spec = getattr(case, "frozen_history", None)
        if spec is not None:
            self.validate_metric_history_case(spec, case.background_workload)
            self._configure_tools(self._frozen_history_public_tools())
            self._refresh_metric_query_tool_spec()

    def _refresh_metric_query_tool_spec(self) -> None:
        definition = postgres_query_metrics_tool_definition(self._metric_catalog)
        history_spec = getattr(getattr(self, "_case", None), "frozen_history", None)
        visible_metrics = tuple(
            getattr(history_spec, "required_metrics", self._metric_catalog.metric_names)
        )
        metric_names = sorted(set(visible_metrics))
        definition["metric_definitions"] = [
            item for item in definition["metric_definitions"]
            if item["metric_name"] in metric_names
        ]
        for parameter in definition["parameter_definitions"]:
            if parameter.get("parameter_name") == "metric_type":
                parameter["allowed_values"] = metric_names
        metric_description = "指标类型，可选当前 Case catalog 值: " + ", ".join(metric_names)
        self._enabled_tool_specs = [
            replace(
                spec,
                parameters=tuple(
                    replace(parameter, description=metric_description)
                    if parameter.name == "metric_type"
                    else parameter
                    for parameter in spec.parameters
                ),
                definition=deepcopy(definition),
            )
            if spec.alias == "query_metrics"
            else spec
            for spec in self._enabled_tool_specs
        ]
        self._alias_to_tool_spec = {
            spec.alias: spec for spec in self._enabled_tool_specs
        }

    def _additional_tool_help(self, tool_name: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        if tool_name in {"query_metrics", "execute_sql", "read_log"} and self._history_timeline is not None:
            spec = self._case.frozen_history
            result["runtime"] = {
                "timezone": "UTC",
                "available_start": format_utc_timestamp(self._history_timeline.visible_start_ms),
                "available_end": format_utc_timestamp(self._history_timeline.visible_end_ms),
                "base_step_seconds": self._history_timeline.base_step_seconds,
                "overview_step_seconds": self._history_timeline.overview_step_seconds,
                "max_history_query_seconds": spec.max_history_query_seconds,
                "enabled_sources": [source.value for source in spec.record_sources],
                "max_history_records_per_response": spec.max_history_records_per_response,
            }
        if tool_name == "execute_sql" and self._history_sql_archive is not None:
            result.setdefault("runtime", {})["connection_surfaces"] = [
                {
                    "name": "primary",
                    "kind": "database",
                    "description": "当前 PostgreSQL 实例",
                },
                {
                    "name": "history",
                    "kind": "frozen_history",
                    "description": "当前 Case 的只读冻结历史 SQL archive",
                    "tables": ["statement_summary", "slow_query"],
                    "write_policy": "read_only",
                    "requires_utc_time_bounds": True,
                },
            ]
        if tool_name == "read_log" and self._history_timeline is not None:
            enabled = set(self._case.frozen_history.record_sources)
            historical_log_types = []
            if HistoricalRecordSource.COMPONENT_LOG in enabled:
                historical_log_types.append("pg_log")
            if HistoricalRecordSource.OPERATION_EVENT in enabled:
                historical_log_types.append("operation_event")
            result.setdefault("runtime", {})["historical_log_types"] = historical_log_types
        if tool_name == "query_metrics":
            provider = getattr(self, "_scenario_metric_provider", None)
            contract = getattr(provider, "agent_contract", None)
            if callable(contract):
                result["case_contract"] = contract()
        return result

    def configure_history_observability(self, spec) -> None:
        self._stop_sampler()
        if not self._ensure_connection():
            raise RuntimeError(
                f"Cannot configure PostgreSQL history observability: host={self.host!r}, port={self.port}, database={self.dbname!r}"
            )
        with self._conn.cursor() as cursor:
            cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'pg_stat_statements'")
            if cursor.fetchone() is None:
                raise RuntimeError(
                    f"PostgreSQL history requires pg_stat_statements extension: database={self.dbname!r}, "
                    f"image={getattr(self.deployment, 'image_name', None)!r}, required_preload='pg_stat_statements'"
                )
            cursor.execute("SHOW shared_preload_libraries")
            preload = str(cursor.fetchone()[0] or "")
            if "pg_stat_statements" not in {item.strip() for item in preload.split(",") if item.strip()}:
                raise RuntimeError(
                    f"PostgreSQL pg_stat_statements is not in shared_preload_libraries: database={self.dbname!r}, "
                    f"shared_preload_libraries={preload!r}"
                )
            for name, value in (
                ("timezone", "UTC"),
                ("log_timezone", "UTC"),
                ("log_line_prefix", "%m [%p] app=%a user=%u db=%d "),
                ("log_min_duration_statement", "0"),
                ("log_lock_waits", "on"),
            ):
                cursor.execute(f"ALTER SYSTEM SET {name} = '{value}'")
            cursor.execute("SELECT pg_reload_conf()")
            if cursor.fetchone()[0] is not True:
                raise RuntimeError("PostgreSQL pg_reload_conf() returned false while configuring history observability")
            reload_deadline = time.monotonic() + 10
            while True:
                cursor.execute(
                    "SELECT current_setting('timezone'), current_setting('log_timezone'), "
                    "current_setting('logging_collector'), current_setting('log_destination'), "
                    "current_setting('log_line_prefix'), current_setting('log_min_duration_statement'), "
                    "current_setting('log_lock_waits')"
                )
                (
                    timezone_value,
                    log_timezone_value,
                    logging_collector,
                    log_destination,
                    log_prefix,
                    log_duration,
                    log_lock_waits,
                ) = (str(value) for value in cursor.fetchone())
                if (
                    timezone_value.casefold() in {"utc", "etc/utc"}
                    and log_timezone_value.casefold() in {"utc", "etc/utc"}
                    and logging_collector.casefold() == "on"
                    and "stderr" in log_destination.casefold()
                    and all(part in log_prefix for part in ("%m", "%p", "%a", "%u", "%d"))
                    and log_duration == "0"
                    and log_lock_waits.casefold() == "on"
                ):
                    break
                if time.monotonic() >= reload_deadline:
                    raise RuntimeError(
                        "PostgreSQL history observability reload did not become active: "
                        f"timezone={timezone_value!r}, log_timezone={log_timezone_value!r}, "
                        f"logging_collector={logging_collector!r}, log_destination={log_destination!r}, "
                        f"log_line_prefix={log_prefix!r}, log_min_duration_statement={log_duration!r}, "
                        f"log_lock_waits={log_lock_waits!r}"
                    )
                time.sleep(0.1)
        required_prefix_parts = ("%m", "%p", "%a", "%u", "%d")
        utc_timezone_names = {"utc", "etc/utc"}
        if (
            timezone_value.casefold() not in utc_timezone_names
            or log_timezone_value.casefold() not in utc_timezone_names
        ):
            raise RuntimeError(
                f"PostgreSQL history timezone configuration is not UTC: timezone={timezone_value!r}, log_timezone={log_timezone_value!r}"
            )
        if logging_collector != "on" or "stderr" not in log_destination:
            raise RuntimeError(
                f"PostgreSQL logs are not capturable: logging_collector={logging_collector!r}, log_destination={log_destination!r}"
            )
        if any(part not in log_prefix for part in required_prefix_parts) or log_duration != "0":
            raise RuntimeError(
                f"PostgreSQL log prefix/duration contract is not active: log_line_prefix={log_prefix!r}, "
                f"log_min_duration_statement={log_duration!r}"
            )
        if log_lock_waits != "on":
            raise RuntimeError(f"PostgreSQL log_lock_waits is not active: log_lock_waits={log_lock_waits!r}")
        # pg_stat_statements updates the currently executing statement after its
        # result is produced, so one snapshot query cannot observe its own entry.
        capture_statement_snapshot(self._conn, int(time.time() * 1000))
        snapshot = capture_statement_snapshot(self._conn, int(time.time() * 1000) + 1)
        expected_query = " ".join(PG_STATEMENT_SNAPSHOT_SQL.split())
        collector_queryids = frozenset(
            key.queryid
            for key, counter in snapshot.counters.items()
            if " ".join(counter.query.split()) == expected_query
        )
        if not collector_queryids:
            raise RuntimeError(
                "PostgreSQL history collector queryid could not be identified by exact normalized SQL: "
                f"expected_query={expected_query!r}, observed_queries={tuple(sorted({counter.query for counter in snapshot.counters.values()}))!r}"
            )
        self._pg_statement_excluded_queryids = collector_queryids
        self._metric_service.live.reset()
        with self._metric_service.live.lock:
            self._pg_statement_snapshots.clear()
        with self._sampler_condition:
            self._sampler_last_timestamp_ms = None
        self._start_sampler()

    def capture_metric_history(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
        *,
        metric_targets: Mapping[str, tuple[str | None, ...]] | None = None,
        rate_windows: Mapping[str, int] | None = None,
    ) -> tuple[MetricFrame, ...]:
        provider = getattr(self, "_scenario_metric_provider", None)
        capture = getattr(provider, "capture_history", None)
        if callable(capture):
            return tuple(capture(metrics, start_epoch_ms, end_epoch_ms, step_seconds))
        with self._sampler_condition:
            while (
                self._sampler_last_timestamp_ms is None
                or self._sampler_last_timestamp_ms < end_epoch_ms
            ):
                self._raise_sampler_failure()
                if self._sampler_thread is None or self._sampler_stop.is_set():
                    raise RuntimeError(
                        "PostgreSQL metric capture cannot reach its requested end because the sampler is not running: "
                        f"requested_end_epoch_ms={end_epoch_ms}, last_timestamp_ms={self._sampler_last_timestamp_ms}"
                    )
                self._sampler_condition.wait()
        self._raise_sampler_failure()
        return self._metric_service.live.capture(metrics, start_epoch_ms, end_epoch_ms, step_seconds)

    @staticmethod
    def _history_snapshot_capacity(spec, sample_interval_sec: int) -> int:
        """Keep capture ticks plus sampler warm-up before the first window."""
        if sample_interval_sec <= 0:
            raise ValueError("sample_interval_sec must be positive")
        capture_seconds = max(int(spec.normal_capture_seconds), int(spec.fault_capture_seconds))
        warmup_seconds = max(60, int(spec.transition_seconds))
        return max(300, capture_seconds // sample_interval_sec + warmup_seconds // sample_interval_sec + 2)

    def capture_history_records(
        self,
        sources: tuple[HistoricalRecordSource, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
    ) -> CapturedRecords:
        provider = getattr(self, "_scenario_metric_provider", None)
        point_records: list = []
        interval_records: list = []
        coverage: list[HistoricalCoverage] = []
        if HistoricalRecordSource.COMPONENT_LOG in sources or HistoricalRecordSource.SLOW_QUERIES in sources:
            raw = self.deployment.read_logs_at_range(start_epoch_ms, end_epoch_ms)
            log_records = parse_postgres_log_records(raw, start_epoch_ms, end_epoch_ms)
            if HistoricalRecordSource.COMPONENT_LOG in sources:
                point_records.extend(log_records)
                coverage.append(HistoricalCoverage(
                    source=HistoricalRecordSource.COMPONENT_LOG,
                    target="postgres",
                    start_ms=start_epoch_ms,
                    end_ms=end_epoch_ms,
                ))
            if HistoricalRecordSource.SLOW_QUERIES in sources:
                point_records.extend(build_slow_query_records_from_logs(log_records))
                coverage.append(HistoricalCoverage(
                    source=HistoricalRecordSource.SLOW_QUERIES,
                    target="postgres",
                    start_ms=start_epoch_ms,
                    end_ms=end_epoch_ms,
                ))
        if HistoricalRecordSource.TOPSQL in sources:
            with self._metric_service.live.lock:
                snapshots = tuple(
                    snapshot
                    for snapshot in self._pg_statement_snapshots
                    if start_epoch_ms <= snapshot.timestamp_ms <= end_epoch_ms
                )
            expected = tuple(range(start_epoch_ms, end_epoch_ms + 1, self.sample_interval_sec * 1000))
            actual = tuple(snapshot.timestamp_ms for snapshot in snapshots)
            if actual != expected:
                raise RuntimeError(
                    f"PostgreSQL TopSQL snapshot coverage is incomplete: requested=({start_epoch_ms},{end_epoch_ms}), "
                    f"expected={expected!r}, actual={actual!r}"
                )
            for previous, current in zip(snapshots, snapshots[1:]):
                interval_records.extend(build_topsql_delta_records(
                    previous,
                    current,
                    excluded_queryids=self._pg_statement_excluded_queryids,
                ))
            coverage.append(HistoricalCoverage(
                source=HistoricalRecordSource.TOPSQL,
                target="postgres",
                start_ms=start_epoch_ms,
                end_ms=end_epoch_ms,
            ))
        provider = self._scenario_metric_provider
        if provider is not None:
            capture = getattr(provider, "capture_history_records", None)
            if callable(capture):
                scenario_records = capture(sources, start_epoch_ms, end_epoch_ms)
                point_records.extend(scenario_records.point_records)
                interval_records.extend(scenario_records.interval_records)
                coverage.extend(scenario_records.coverage)
        return CapturedRecords(
            point_records=tuple(point_records),
            interval_records=tuple(interval_records),
            coverage=tuple(coverage),
        )

    def _sample_additional_metrics(
        self,
        connection,
        timestamp_ms: int,
        base_values: Mapping[str, Mapping[str, float]],
    ) -> Mapping[str, Mapping[str, float]]:
        provider = self._scenario_metric_provider
        if provider is None:
            return {}
        sample = getattr(provider, "sample_metrics", None)
        if not callable(sample):
            raise TypeError(
                "PostgreSQL scenario metric provider must expose sample_metrics: "
                f"provider={type(provider).__name__!r}, case={self._case.case_id!r}"
            )
        values = sample(
            connection=connection,
            timestamp_ms=timestamp_ms,
            elapsed_seconds=float(self.sample_interval_sec),
            base_values=base_values,
        )
        if not isinstance(values, Mapping):
            raise TypeError(
                "PostgreSQL scenario metric provider returned non-mapping samples: "
                f"provider={type(provider).__name__!r}, values={values!r}"
            )
        return values

    def bind_metric_history(self, timeline: FrozenHistoricalTimeline) -> None:
        if self._case is None or getattr(self._case, "frozen_history", None) is None:
            raise RuntimeError(
                f"Cannot bind metric history to a non-history PostgreSQL Case: case={getattr(self._case, 'case_id', None)!r}"
            )
        if not isinstance(timeline, FrozenHistoricalTimeline):
            raise TypeError(f"PostgreSQL metric history must be FrozenHistoricalTimeline, got {type(timeline).__name__}")
        self._metric_service.bind_history(timeline.metric_provider)
        self._history_timeline = timeline
        spec = self._case.frozen_history
        self._history_sql_archive = FrozenHistoricalSqlArchive(
            timeline.record_store,
            max_rows=min(200, int(getattr(spec, "max_history_records_per_response", 200))),
            visible_start_ms=timeline.visible_start_ms,
            visible_end_ms=timeline.visible_end_ms,
            sql_dialect="postgres",
            require_time_bounds=True,
            max_response_bytes=PG_SQL_RESULT_MAX_BYTES,
        )
        self._configure_tools(self._frozen_history_public_tools())
        # Binding frozen history rebuilds the enabled tool list. Refresh the
        # case-owned metric contract afterward so the Agent never receives the
        # generic catalog after setup has completed.
        self._refresh_metric_query_tool_spec()
        refresh_case_tools = getattr(self, "_refresh_rpo_tool_specs", None)
        if callable(refresh_case_tools):
            refresh_case_tools()

    def observe_metric(self, metric_type: str, target: str | None = None) -> str:
        frame = self._metric_service.query_live(MetricQuery(metric=metric_type, target=target))
        start_ms, end_ms = self._metric_service.live.available_range
        return render_metric_frame(
            frame,
            available_start_ms=start_ms,
            available_end_ms=end_ms,
            requested_start_ms=start_ms,
            requested_end_ms=end_ms,
            step_seconds=frame.step_seconds,
        )

    def query_history(
        self,
        source: str,
        start_timestamp: str,
        end_timestamp: str,
        target: str | None = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> str:
        try:
            result = self._query_frozen_history_records(
                source=HistoricalRecordSource(source),
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                target=target,
                filters=filters,
                limit=limit,
            )
            return json.dumps(result, ensure_ascii=False, separators=(",", ":"), default=str)
        except (ValueError, RuntimeError, TypeError, KeyError) as exc:
            return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)

    def _query_frozen_history_records(
        self,
        *,
        source: HistoricalRecordSource,
        start_timestamp: str,
        end_timestamp: str,
        target: str | None,
        filters: Optional[Dict[str, Any]],
        limit: int,
    ) -> Dict[str, Any]:
        if self._history_timeline is None or self._case is None or getattr(self._case, "frozen_history", None) is None:
            raise RuntimeError(
                f"Frozen PostgreSQL history requires a bound frozen-history Case: case={getattr(self._case, 'case_id', None)!r}"
            )
        spec = self._case.frozen_history
        if source not in spec.record_sources:
            raise ValueError(
                f"History source is not enabled by Case: source={source.value!r}, "
                f"enabled={[item.value for item in spec.record_sources]!r}"
            )
        if limit <= 0 or limit > spec.max_history_records_per_response:
            raise ValueError(
                f"History record limit is outside Case budget: source={source.value!r}, limit={limit}, "
                f"max_history_records_per_response={spec.max_history_records_per_response}"
            )
        return self._history_timeline.record_store.query(
            source=source,
            start_ms=parse_utc_timestamp(start_timestamp, "start_timestamp"),
            end_ms=parse_utc_timestamp(end_timestamp, "end_timestamp"),
            target=target,
            filters=filters,
            limit=limit,
            max_window_seconds=getattr(spec, "max_history_query_seconds", None) or None,
            max_response_chars=min(
                PG_SQL_RESULT_MAX_BYTES,
                int(getattr(spec, "max_history_response_chars", PG_SQL_RESULT_MAX_BYTES)),
            ),
        )

    def deploy(self):
        """部署 PG 环境"""
        if self.deployment is None:
            raise RuntimeError("No deployment configured")

        if self.workload is not None:
            print(f"[Env:PGEnv] Preparing workload...")
            self.workload.prepare()

        print(f"[Env:PGEnv] Deploying PostgreSQL...")
        self.deployment.deploy()

        if not self.deployment.wait_for_ready(timeout=600):
            raise RuntimeError("Failed to deploy PostgreSQL: not ready")

        self._ensure_connection()
        if self.workload is not None and self.workload.workload_name == "tpcds":
            from src.workloads.tpcds import TPCDSWorkload

            if not isinstance(self.workload, TPCDSWorkload):
                raise TypeError(
                    "PGEnv workload name and implementation disagree: "
                    f"workload_name={self.workload.workload_name!r}, type={type(self.workload).__name__!r}"
                )
            self.workload.validate_database(self)
        # Frozen-history setup starts its shared workload runner before history
        # observability; avoid sampling the provider during the deployment gap.
        if self._scenario_metric_provider is None:
            self._start_sampler()
        self._snapshot_pgss_baseline()
        print(f"[Env:PGEnv] Deployment complete.")

    def configure_runtime(self, runtime: PostgresCaseRuntime) -> None:
        if not isinstance(runtime, PostgresCaseRuntime):
            raise TypeError(
                f"PGEnv requires PostgresCaseRuntime, got {type(runtime).__name__}"
            )
        if runtime.parameters is not None:
            self.deployment.postgres_runtime_options = runtime.parameters.as_command_line()
        if runtime.resources is not None:
            self.deployment.resources = {
                **self.deployment.resources,
                "cpus": runtime.resources.container_cpu_limit,
                "memory_mb": runtime.resources.container_memory_mb,
            }

    def base_snapshot_name(self, case) -> Optional[str]:
        if getattr(case, "snapshot_unsafe", False):
            return None
        return case.base_image_name

    def snapshot_name(self, scenario_id: str, case) -> Optional[str]:
        base_snapshot_name = self.base_snapshot_name(case)
        if base_snapshot_name is None:
            return None
        repository = base_snapshot_name.partition(":")[0]
        prefix = "aiopsbench-pg-"
        if not repository.startswith(prefix):
            raise ValueError(
                f"Unsupported PostgreSQL base snapshot: case={case.case_id!r}, "
                f"base_snapshot={base_snapshot_name!r}"
            )
        identity = f"{scenario_id}-{case.case_id}".replace("_", "-")
        return f"aiopsbench-pg-fault-{identity}:{repository.removeprefix(prefix)}"

    def snapshot_exists(self, snapshot_name: str) -> bool:
        return PGDockerDeployment.image_exists(snapshot_name)

    def select_snapshot(self, snapshot_name: str, base_snapshot_name: str) -> None:
        self.deployment.image_name = snapshot_name
        self.baseline_image_name = base_snapshot_name

    def save_snapshot(self, snapshot_name: str, labels: Dict[str, str]) -> None:
        import subprocess

        # 快照保存会 stop/start PostgreSQL（docker commit 前后）。后台 sampler
        # 与 reboot/restart 路径一样必须在停机窗口内暂停，否则 allow_sampler_
        # reconnect=False 时 sampler 线程会把停机当故障记录，run 在 teardown
        # 阶段整体失败。与 _run_lifecycle_with_sampler 保持同一语义。
        sampler_was_running = (
            self._sampler_thread is not None and self._sampler_thread.is_alive()
        )
        if sampler_was_running:
            self._stop_sampler()
        try:
            checkpoint = self.execute_sql("SET statement_timeout = '300s'; CHECKPOINT;")
            checkpoint_text = checkpoint if isinstance(checkpoint, str) else json.dumps(
                checkpoint, ensure_ascii=False, default=str
            )
            if '"status": "error"' in checkpoint_text.lower():
                raise RuntimeError(
                    f"PostgreSQL checkpoint failed before snapshot: result={checkpoint_text}"
                )
            deployment = self.deployment
            if not deployment.is_container_running():
                raise RuntimeError(
                    f"Cannot save PostgreSQL snapshot: container={deployment.container_name!r} is not running"
                )
            if not deployment.stop_pg():
                raise RuntimeError(
                    f"Cannot stop PostgreSQL before snapshot: container={deployment.container_name!r}"
                )
            command = ["docker", "commit"]
            for key, value in labels.items():
                command.extend(["--change", f"LABEL {key}={json.dumps(str(value))}"])
            command.extend([deployment.container_name, snapshot_name])
            result = subprocess.run(command, capture_output=True, text=True)
            if not deployment.start_pg():
                raise RuntimeError(
                    f"Cannot restart PostgreSQL after snapshot: container={deployment.container_name!r}, "
                    f"snapshot={snapshot_name!r}, commit_returncode={result.returncode}, "
                    f"commit_stderr={result.stderr.strip()!r}"
                )
            if result.returncode != 0:
                raise RuntimeError(
                    f"PostgreSQL snapshot commit failed: snapshot={snapshot_name!r}, "
                    f"container={deployment.container_name!r}, returncode={result.returncode}, "
                    f"stderr={result.stderr.strip()!r}"
                )
            if not deployment.wait_for_ready(timeout=600):
                raise RuntimeError(
                    f"PostgreSQL did not become ready after snapshot: snapshot={snapshot_name!r}"
                )
            if not self.reconnect():
                raise RuntimeError(
                    f"PostgreSQL reconnect failed after snapshot: snapshot={snapshot_name!r}, "
                    f"container={deployment.container_name!r}"
                )
            self.refresh_pgss_baseline()
        finally:
            if sampler_was_running:
                self._start_sampler()

    def _capture_pgss_snapshot(self) -> PgStatementSnapshot:
        if not self._ensure_connection():
            raise RuntimeError(
                f"PostgreSQL pg_stat_statements snapshot connection failed: host={self.host!r}, "
                f"port={self.port}, database={self.dbname!r}"
            )
        with self._conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'")
            if cursor.fetchone() is None:
                raise RuntimeError(
                    f"PostgreSQL pg_stat_statements snapshot requires installed extension: "
                    f"database={self.dbname!r}, image={getattr(self.deployment, 'image_name', None)!r}"
                )
        return capture_statement_snapshot(self._conn, int(time.time() * 1000))

    def _snapshot_pgss_baseline(self):
        """部署完成时刻拍一张 pg_stat_statements 快照，作为 topsql 减去初始化 SQL 累计的基线。

        不调用 pg_stat_statements_reset()——它会清空所有历史；这里改用差分模型，
        既保留全量历史给手动诊断，也允许 topsql 给出"故障注入后增量"视图。
        """
        snap = self._capture_pgss_snapshot()
        self._pgss_baseline = snap
        print(f"[Env:PGEnv] pg_stat_statements baseline snapshot: {len(snap.counters)} entries.")

    def refresh_pgss_baseline(self):
        # 场景注入器在隐藏准备工作后需要重拍 pgss baseline，保留手动刷新入口。
        return self._snapshot_pgss_baseline()

    @contextmanager
    def metrics_hidden(self, *, allow_pgss_reset: bool = False):
        """块内执行的 SQL 对 topsql / slow_queries(finished) 隐身。

        机制：进入时拍 pg_stat_statements 快照 enter，退出时拍 exit，将 (exit-enter) 增量
        合入 _pgss_baseline。topsql / slow_queries 内部已做 (current - baseline) delta 过滤，
        因此块内执行的 SQL 计数贡献被吸收，agent 看不到。

        - 仅作用于基于 pg_stat_statements 的指标；pg_stat_activity 实时态、cgroup 资源指标
          不受影响（这些指标本身在 SQL 跑完后就回到正常水位，不需要隐身）。
        - 同时推进 PostgreSQL 日志可见 offset，使故障注入期间的 reload/config 日志
          不会通过 read_log(pg_log) 泄露给 Agent；hidden 块之后的新日志仍可见。
        - 支持嵌套：用 depth 计数器，仅最外层 enter/exit 真正拍快照。
        - 跨 with 边界的 queryid（块前已有、块内继续执行）只吸收块内增量，块外执行仍可见。
        - 只有显式声明 allow_pgss_reset=True 的生命周期块才允许块内 PostgreSQL 重启或
          pg_stat_statements_reset() 使快照键消失；此时退出快照成为新的 baseline。
        - enter/exit snapshot 或日志 offset 读取失败直接抛错。
        """
        if self._metrics_hidden_depth == 0:
            self._metrics_hidden_enter_snap = self._capture_pgss_snapshot()
            self._pg_log_hidden_enter_offsets = self._pg_log_snapshot()
            self._metrics_hidden_allow_pgss_reset = allow_pgss_reset
        elif allow_pgss_reset and not self._metrics_hidden_allow_pgss_reset:
            raise RuntimeError(
                "PostgreSQL metrics_hidden nested block cannot enable pg_stat_statements reset "
                "after the outer block was created without allow_pgss_reset=True"
            )
        self._metrics_hidden_depth += 1
        try:
            yield
        finally:
            self._metrics_hidden_depth -= 1
            if self._metrics_hidden_depth == 0:
                enter_snap = self._metrics_hidden_enter_snap
                self._metrics_hidden_enter_snap = None
                reset_allowed = bool(self._metrics_hidden_allow_pgss_reset)
                self._metrics_hidden_allow_pgss_reset = None
                if enter_snap is None:
                    raise RuntimeError("PostgreSQL metrics_hidden exit has no enter statement snapshot")
                exit_snap = self._capture_pgss_snapshot()
                self._absorb_pgss_delta(
                    enter_snap,
                    exit_snap,
                    allow_pgss_reset=reset_allowed,
                )
                exit_log_offsets = self._pg_log_snapshot()
                if self._pg_log_hidden_enter_offsets is None:
                    raise RuntimeError("PostgreSQL metrics_hidden exit has no enter log snapshot")
                missing = tuple(sorted(
                    set(self._pg_log_hidden_enter_offsets) - set(exit_log_offsets)
                ))
                if missing:
                    raise RuntimeError(
                        "PostgreSQL log file disappeared during metrics_hidden: "
                        f"missing_files={missing!r}, enter_offsets={self._pg_log_hidden_enter_offsets!r}, "
                        f"exit_offsets={exit_log_offsets!r}"
                    )
                shrinking = {
                    path: (self._pg_log_hidden_enter_offsets[path], exit_log_offsets[path])
                    for path in self._pg_log_hidden_enter_offsets
                    if exit_log_offsets[path] < self._pg_log_hidden_enter_offsets[path]
                }
                if shrinking:
                    raise RuntimeError(
                        "PostgreSQL log file shrank during metrics_hidden: "
                        f"files={shrinking!r}"
                    )
                self._pg_log_visible_offsets = exit_log_offsets
                self._pg_log_hidden_enter_offsets = None

    def _absorb_pgss_delta(
        self,
        enter_snap: PgStatementSnapshot,
        exit_snap: PgStatementSnapshot,
        *,
        allow_pgss_reset: bool = False,
    ):
        """将 (exit - enter) 增量累加进 _pgss_baseline。

        - 块内首次出现的 queryid（enter 没有）：完整吸收 → topsql/slow_queries 看不到
        - 跨边界 queryid：只吸收块内部分，块外执行仍然可见（calls_delta 仍 > 0）
        """
        if enter_snap.timestamp_ms >= exit_snap.timestamp_ms:
            raise RuntimeError(
                f"PostgreSQL hidden snapshots are not increasing: enter_timestamp_ms={enter_snap.timestamp_ms}, "
                f"exit_timestamp_ms={exit_snap.timestamp_ms}"
            )
        if self._pgss_baseline is None:
            raise RuntimeError("PostgreSQL metrics_hidden requires an initialized pg_stat_statements baseline")
        zero = PgStatementCounters(
            query="",
            calls=0,
            total_exec_time_ms=0.0,
            rows=0,
            shared_blks_hit=0,
            shared_blks_read=0,
            shared_blks_written=0,
            temp_blks_read=0,
            temp_blks_written=0,
        )
        missing_keys = sorted(
            key
            for key, counter in enter_snap.counters.items()
            if key not in exit_snap.counters
            and any(getattr(counter, field) != 0 for field in ADDITIVE_COUNTER_FIELDS)
        )
        if missing_keys:
            if not allow_pgss_reset:
                raise RuntimeError(
                    "PostgreSQL pg_stat_statements key disappeared during metrics_hidden: "
                    f"enter_timestamp_ms={enter_snap.timestamp_ms}, exit_timestamp_ms={exit_snap.timestamp_ms}, "
                    f"keys={missing_keys!r}"
                )
            self._pgss_baseline = PgStatementSnapshot(
                timestamp_ms=exit_snap.timestamp_ms,
                counters=exit_snap.counters,
            )
            print(
                "[Env:PGEnv] metrics_hidden observed an explicit PostgreSQL stats reset/restart; "
                f"new baseline entries={len(exit_snap.counters)}."
            )
            self._pgss_sampler_reset_observed = True
            return
        counters = dict(self._pgss_baseline.counters)
        absorbed = 0
        for key, current in exit_snap.counters.items():
            previous = enter_snap.counters.get(key, zero)
            base = self._pgss_baseline.counters.get(key, zero)
            values: dict[str, int | float] = {}
            decreasing = {}
            for field in ADDITIVE_COUNTER_FIELDS:
                delta = getattr(current, field) - getattr(previous, field)
                if delta < 0:
                    decreasing[field] = delta
                values[field] = getattr(base, field) + delta
            if decreasing:
                raise RuntimeError(
                    "PostgreSQL pg_stat_statements counter moved backwards during metrics_hidden: "
                    f"query_key={key!r}, enter_timestamp_ms={enter_snap.timestamp_ms}, "
                    f"exit_timestamp_ms={exit_snap.timestamp_ms}, fields={decreasing!r}"
                )
            counters[key] = PgStatementCounters(
                query=current.query or base.query,
                calls=int(values["calls"]),
                total_exec_time_ms=float(values["total_exec_time_ms"]),
                rows=int(values["rows"]),
                shared_blks_hit=int(values["shared_blks_hit"]),
                shared_blks_read=int(values["shared_blks_read"]),
                shared_blks_written=int(values["shared_blks_written"]),
                temp_blks_read=int(values["temp_blks_read"]),
                temp_blks_written=int(values["temp_blks_written"]),
            )
            if values["calls"] - getattr(previous, "calls") > 0:
                absorbed += 1
        self._pgss_baseline = PgStatementSnapshot(
            timestamp_ms=exit_snap.timestamp_ms,
            counters=counters,
        )
        print(f"[Env:PGEnv] metrics_hidden absorbed pgss delta on {absorbed} queryid(s).")

    def teardown(self):
        """销毁 PG 环境（保留数据）"""
        failures = []
        if self._history_sql_archive is not None:
            archive = self._history_sql_archive
            self._history_sql_archive = None
            try:
                archive.close()
            except Exception as exc:
                failures.append(("close history SQL archive", exc))
        for operation, callback in (
            ("stop sampler", self._stop_sampler),
            ("stop workload runner", self._stop_workload_runner),
            ("clear PgBouncer endpoint", self.clear_pgbouncer_endpoint),
        ):
            try:
                callback()
            except Exception as exc:
                failures.append((operation, exc))
        if self.deployment is not None:
            try:
                self.deployment.teardown()
            except Exception as exc:
                failures.append(("teardown deployment", exc))
        self._conn = None
        self._scenario_metric_provider = None
        if failures:
            details = "; ".join(f"{operation}: {exc!r}" for operation, exc in failures)
            raise RuntimeError(f"PostgreSQL environment teardown failed: {details}") from failures[0][1]

    def attach_scenario_metric_provider(self, provider) -> None:
        if self._scenario_metric_provider is not None and self._scenario_metric_provider is not provider:
            raise RuntimeError("a scenario metric provider is already attached")
        self._scenario_metric_provider = provider

    def detach_scenario_metric_provider(self, provider=None) -> None:
        if provider is None or self._scenario_metric_provider is provider:
            self._scenario_metric_provider = None

    def attach_workload_runner(self, runner):
        """Attach a WorkloadRunner instance. Caller is responsible for start()/stop()."""
        # 仅持有引用；连接与线程由 runner 自管，teardown 时统一停止。
        self._workload_runner = runner

    def _query_workload_activity(self, limit: int = 20) -> str:
        """返回 workload runner 内部聚合的 fingerprint 实时 mean_ms / p95_ms。

        进程内 ring buffer 聚合，500 条记录的 sort+group ≈ 0.1ms；不走 DB。
        """
        runner = getattr(self, "_workload_runner", None)
        if runner is None:
            return json.dumps({
                "status": "error",
                "error": "workload runner not attached",
            }, ensure_ascii=False)
        activity = runner.get_activity(limit=limit)
        return self._metric_success(
            "workload_activity",
            "snapshot",
            snapshot={
                "total_runs": activity["total_runs"],
                "active_profiles": activity["active_profiles"],
                "worker_count": activity["worker_count"],
                "window_seconds": activity["window_seconds"],
                "profiles": activity["value"],
            },
        )

    def _stop_workload_runner(self):
        runner = getattr(self, "_workload_runner", None)
        if runner is None:
            return
        try:
            runner.stop()
        except Exception:
            pass
        self._workload_runner = None

    def _ensure_connection(self):
        """确保数据库连接可用"""
        if self._conn is not None:
            try:
                with self._conn.cursor() as cur:
                    cur.execute("SELECT 1")
                return True
            except Exception:
                self._conn = None
        import psycopg2
        for attempt in range(10):
            try:
                self._conn = psycopg2.connect(
                    host=self.host, port=self.port,
                    user=self.user, password=self.password, dbname=self.dbname,
                    connect_timeout=3
                )
                self._conn.autocommit = True
                with self._conn.cursor() as _timeout_cursor:
                    _timeout_cursor.execute(
                        f"SET statement_timeout = {self.SQL_STATEMENT_TIMEOUT_SECONDS * 1000}"
                    )
                print(f"[Env:PGEnv] Connected to PostgreSQL.")
                return True
            except Exception as e:
                if attempt == 0:
                    print(f"[Env:PGEnv] Connection attempt {attempt+1} failed: {e}")
                time.sleep(1)
        print("[Env:PGEnv] Failed to connect after 10 attempts.")
        return False

    def reconnect(self):
        """强制重新建立数据库连接"""
        previous = self._conn
        self._conn = None
        if previous is not None:
            previous.close()
        return self._ensure_connection()

    def open_workload_connection(self, application_name: str, target: Optional[str] = None):
        import psycopg2
        endpoint = None
        if target is not None:
            endpoint = self._workload_connection_endpoints.get(str(target))
            if endpoint is None:
                raise ValueError(
                    "PostgreSQL workload pool is not configured: "
                    f"target={target!r}, pools={sorted(self._workload_connection_endpoints)}"
                )
        conn = psycopg2.connect(
            host=str(endpoint["host"]) if endpoint else self.host,
            port=int(endpoint["port"]) if endpoint else self.port,
            user=str(endpoint["user"]) if endpoint else self.user,
            password=str(endpoint["password"]) if endpoint else self.password,
            dbname=str(endpoint["dbname"]) if endpoint else self.dbname,
            connect_timeout=3,
            application_name=application_name,
        )
        conn.autocommit = False
        return conn

    def configure_pgbouncer_endpoint(
        self,
        host: str,
        port: int,
        *,
        admin_user: str = "postgres",
        admin_password: str = "password",
        admin_dbname: str = "pgbouncer",
    ) -> None:
        """Register a scenario-owned PgBouncer admin endpoint.

        The endpoint is opt-in so ordinary PostgreSQL cases retain their existing
        tool surface and workload routing semantics.
        """
        if int(port) <= 0:
            raise ValueError(f"PgBouncer port must be positive: port={port!r}")
        self._pgbouncer_endpoint = {
            "host": str(host),
            "port": int(port),
            "user": str(admin_user),
            "password": str(admin_password),
            "dbname": str(admin_dbname),
        }
        self._pgbouncer_runtime_overrides.clear()

    def clear_pgbouncer_endpoint(self) -> None:
        self._pgbouncer_endpoint = None
        self._pgbouncer_runtime_overrides.clear()
        self._workload_connection_endpoints.clear()

    def configure_workload_connection_pool(
        self,
        pool: str,
        host: str,
        port: int,
        *,
        user: str,
        password: str,
        dbname: str,
    ) -> None:
        pool_name = str(pool).strip()
        if not pool_name:
            raise ValueError("PgBouncer workload pool name must not be empty")
        if int(port) <= 0:
            raise ValueError(f"PgBouncer workload port must be positive: port={port!r}")
        self._workload_connection_endpoints[pool_name] = {
            "host": str(host),
            "port": int(port),
            "user": str(user),
            "password": str(password),
            "dbname": str(dbname),
        }

    def _pgbouncer_admin_query(self, sql: str) -> tuple[list[str], list[list[object]]]:
        if self._pgbouncer_endpoint is None:
            raise RuntimeError("PgBouncer admin endpoint is not configured for this environment")
        import psycopg2

        endpoint = self._pgbouncer_endpoint
        conn = psycopg2.connect(
            host=str(endpoint["host"]),
            port=int(endpoint["port"]),
            user=str(endpoint["user"]),
            password=str(endpoint["password"]),
            dbname=str(endpoint["dbname"]),
            connect_timeout=3,
        )
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                columns = [column.name for column in cur.description] if cur.description else []
                rows = [list(row) for row in cur.fetchall()] if cur.description else []
            return columns, rows
        finally:
            conn.close()

    def pgbouncer_admin_query(self, sql: str) -> str:
        try:
            columns, rows = self._pgbouncer_admin_query(sql)
            return json.dumps(
                {"status": "success", "columns": columns, "result": rows},
                default=str,
                ensure_ascii=False,
            )
        except Exception as exc:
            return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)

    def configure_workload_session(self, connection, profile):
        from src.scenarios.workloads import WORKLOAD_LOCK_TIMEOUT, WORKLOAD_STATEMENT_TIMEOUT
        with connection.cursor() as cur:
            if profile.application_name:
                cur.execute(
                    "SELECT set_config('application_name', %s, false);",
                    (profile.application_name,),
                )
            cur.execute(f"SET LOCAL statement_timeout = '{WORKLOAD_STATEMENT_TIMEOUT}';")
            cur.execute(f"SET LOCAL lock_timeout = '{WORKLOAD_LOCK_TIMEOUT}';")

    def execute_workload_profile(self, connection, profile):
        with connection.cursor() as cur:
            cur.execute(profile.sql)
            result_rows = len(cur.fetchall()) if cur.description else cur.rowcount
        connection.commit() if profile.commit else connection.rollback()
        return {"session_setup_statements": 0, "result_rows": result_rows}

    def _start_sampler(self):
        """Start the background sampler on the fixed UTC epoch-ms grid."""
        if getattr(self, "disable_generic_sampler", False):
            return
        if self._sampler_thread is not None and self._sampler_thread.is_alive():
            return
        self._raise_sampler_failure()
        self._sampler_stop.clear()
        self._sampler_grid_strikes = SamplerGridStrikes()
        self._sampler_thread = threading.Thread(
            target=self._run_resource_sampler, daemon=True)
        self._sampler_thread.start()

    def _stop_sampler(self):
        """Stop the sampler and surface any failure raised by its thread."""
        self._sampler_stop.set()
        if self._sampler_thread is not None:
            self._sampler_thread.join(timeout=10)
            if self._sampler_thread.is_alive():
                raise RuntimeError("PostgreSQL sampler thread did not stop within 10 seconds")
            self._sampler_thread = None
        if self._sampler_conn is not None:
            self._sampler_conn.close()
            self._sampler_conn = None
        self._raise_sampler_failure()

    def _reset_cgroup_io_sampler_state(self) -> None:
        """Reset host-side cgroup state after the Docker container is recreated."""
        self._prev_io_sample = None
        self._host_cgroup_base = None

    def _run_lifecycle_with_sampler(self, action: str, perform) -> str:
        """Run a PG process lifecycle action with the background sampler kept consistent.

        The instance downtime the action causes is marked as an expected sampler
        disconnect (so a sampler failure already recorded from that downtime is
        accepted once instead of failing the rest of the run), sampling is paused
        for the duration like in the reboot path, and ``finally`` resumes sampling
        so the run cannot stay dead after the instance recovers.
        """
        sampler_was_running = self._sampler_thread is not None and self._sampler_thread.is_alive()
        self._expected_sampler_disconnect_reason = f"manage_instance('{action}')"
        self._expected_sampler_disconnect_evidence = {
            "action": action,
            "sampler_was_running": str(sampler_was_running),
        }
        try:
            if sampler_was_running:
                self._stop_sampler()
            return perform()
        finally:
            if self._scenario_metric_provider is None:
                self._start_sampler()
            self._expected_sampler_disconnect_reason = None
            self._expected_sampler_disconnect_evidence = None

    def _drop_sampler_tick(self, exc: Exception, timestamp_ms: int) -> None:
        """Discard a sampler tick whose PostgreSQL connection died mid-query.

        Only used when the scenario opted into sampler reconnect tolerance
        (``allow_sampler_reconnect``); the dead connection is closed so the
        next tick reconnects from scratch.
        """
        print(f"[Env:PGEnv] Sampler tick dropped after PostgreSQL connection loss: "
              f"timestamp_ms={timestamp_ms}, error={exc}")
        if self._sampler_conn is not None:
            try:
                self._sampler_conn.close()
            except Exception:
                pass
            self._sampler_conn = None
        self._sampler_reconnected = True

    def _accept_expected_sampler_failure(self) -> bool:
        """Swallow the one pending sampler failure when a lifecycle action
        declared its instance downtime as an expected disconnect."""
        if self._sampler_failure is None:
            return False
        reason = self._expected_sampler_disconnect_reason
        if reason is None:
            return False
        print(
            "[Env:PGEnv] Sampler failure accepted as expected disconnect: "
            f"reason={reason!r}, evidence={self._expected_sampler_disconnect_evidence!r}, "
            f"error={self._sampler_failure}"
        )
        self._expected_sampler_disconnect_reason = None
        self._expected_sampler_disconnect_evidence = None
        self._sampler_failure = None
        return True

    def _raise_sampler_failure(self) -> None:
        if self._accept_expected_sampler_failure():
            return
        failure = self._sampler_failure
        if failure is not None:
            raise RuntimeError(f"PostgreSQL sampler thread failed: error={failure}") from failure

    @property
    def _sampler_lag_strikes(self) -> int:
        return self._sampler_grid_strikes.strikes

    def _sampler_record_tick_lag(self, tick_elapsed_seconds: float) -> None:
        """Count sustained over-tolerance ticks; in-tolerance ticks decay the count.

        A single slow tick (host stall, crash-recovery reconnect inside the tick)
        must not kill the sampler: it raises the strike count by one while any
        tick finishing within SAMPLER_LAG_TOLERANCE_INTERVALS grid intervals
        decays the count back toward zero. Only SAMPLER_LAG_STRIKES_LIMIT net
        strikes mean the fixed-grid contract is unmet and the sampler gives up.
        """
        if tick_elapsed_seconds <= self.sample_interval_sec * SAMPLER_LAG_TOLERANCE_INTERVALS:
            self._sampler_grid_strikes.decay()
            return
        self._sampler_grid_strikes.strike(
            detail=(
                f"tick_elapsed_seconds={tick_elapsed_seconds:.3f}, "
                f"tolerance_seconds={self.sample_interval_sec * SAMPLER_LAG_TOLERANCE_INTERVALS}"
            )
        )

    def _run_resource_sampler(self) -> None:
        try:
            self._resource_sampler_loop()
        except Exception as exc:
            self._sampler_failure = exc
            self._sampler_stop.set()
            with self._sampler_condition:
                self._sampler_condition.notify_all()

    def _sampler_ensure_conn(self):
        """为后台采集线程维护独立 DB 连接。"""
        if self._sampler_conn is not None:
            try:
                with self._sampler_conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                return self._sampler_conn
            except Exception:
                if not self.allow_sampler_reconnect:
                    raise
                try:
                    self._sampler_conn.close()
                except Exception:
                    pass
                self._sampler_conn = None
                self._sampler_reconnected = True
        import psycopg2
        last_error = None
        reconnect_rounds = self.SAMPLER_RECONNECT_MAX_ROUNDS if self.allow_sampler_reconnect else 1
        for round_index in range(1, reconnect_rounds + 1):
            reconnect_deadline = (
                time.monotonic() + self.SAMPLER_RECONNECT_TIMEOUT_SEC
                if self.allow_sampler_reconnect
                else None
            )
            while True:
                if self._sampler_stop.is_set():
                    return self._sampler_conn
                try:
                    self._sampler_conn = psycopg2.connect(
                        host=self.host,
                        port=self.port,
                        user=self.user,
                        password=self.password,
                        dbname=self.dbname,
                        connect_timeout=3,
                        application_name="aiopsbench-history-sampler",
                    )
                    self._sampler_conn.autocommit = True
                    return self._sampler_conn
                except Exception as exc:
                    last_error = exc
                    if not self.allow_sampler_reconnect:
                        raise
                    remaining = reconnect_deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    if self._sampler_stop.wait(min(0.5, remaining)):
                        return self._sampler_conn
            print(
                f"[Env:PGEnv] Sampler reconnect window {round_index}/{reconnect_rounds} exhausted, "
                f"opening another window: timeout_sec={self.SAMPLER_RECONNECT_TIMEOUT_SEC}, "
                f"error={last_error}"
            )
        raise RuntimeError(
            "PostgreSQL sampler could not reconnect within the allowed restart windows: "
            f"rounds={reconnect_rounds}, timeout_sec_per_round={self.SAMPLER_RECONNECT_TIMEOUT_SEC}, "
            f"error={last_error}"
        ) from last_error

    def _resource_sampler_loop(self):
        """Collect all PG metrics on one fixed UTC epoch-ms grid."""
        import psycopg2

        previous_cpu_us = None
        previous_cpu_timestamp = None
        previous_hits = None
        previous_reads = None
        previous_snapshot = None
        interval_ms = self.sample_interval_sec * 1000
        next_timestamp_ms = (int(time.time() * 1000) // interval_ms + 1) * interval_ms

        while not self._sampler_stop.is_set():
            wait_seconds = next_timestamp_ms / 1000 - time.time()
            if wait_seconds > 0 and self._sampler_stop.wait(wait_seconds):
                return
            if self._sampler_stop.is_set():
                return
            timestamp_ms = next_timestamp_ms
            tick_started_mono = time.monotonic()
            values: dict[str, dict[str, float]] = {}

            cpu_us = self._read_cpu_usage_usec()
            if previous_cpu_us is not None:
                if cpu_us < previous_cpu_us:
                    raise RuntimeError(
                        f"PostgreSQL cgroup CPU counter moved backwards: previous={previous_cpu_us}, current={cpu_us}, "
                        f"timestamp_ms={timestamp_ms}"
                    )
                elapsed_us = (timestamp_ms - previous_cpu_timestamp) * 1000
                cpus = self._effective_cpus()
                if elapsed_us <= 0 or cpus <= 0:
                    raise RuntimeError(
                        f"PostgreSQL CPU sampler interval is invalid: previous_timestamp_ms={previous_cpu_timestamp}, "
                        f"timestamp_ms={timestamp_ms}, cpus={cpus}"
                    )
                values["cpu"] = {
                    "percent": _bounded_cpu_percent(cpu_us - previous_cpu_us, elapsed_us, cpus)
                }
            previous_cpu_us = cpu_us
            previous_cpu_timestamp = timestamp_ms

            values["memory"] = {"percent": self._sample_memory()}
            io = self._sample_disk_io()
            if io is not None:
                values["disk_io"] = {
                    "read_mb_per_second": io[0],
                    "write_mb_per_second": io[1],
                }

            sampler_conn = self._sampler_ensure_conn()
            if sampler_conn is None:
                return
            if self._sampler_reconnected:
                # A PostgreSQL restart can reset SQL statistics counters while
                # the container cgroup counters remain continuous.
                previous_hits = None
                previous_reads = None
                previous_snapshot = None
                self._sampler_reconnected = False
            try:
                with sampler_conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT count(*) FROM pg_stat_activity WHERE backend_type = 'client backend'"
                    )
                    values["active_connections"] = {"connections": float(cursor.fetchone()[0] or 0)}
                    cursor.execute(
                        "SELECT sum(blks_hit), sum(blks_read) FROM pg_stat_database "
                        "WHERE datname = current_database()"
                    )
                    hits, reads = (int(value or 0) for value in cursor.fetchone())
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as exc:
                if not self.allow_sampler_reconnect:
                    raise
                # A fault lifecycle may restart PostgreSQL mid-tick. Drop the
                # tick, refresh the connection and delta baselines at the next
                # tick, and keep the sampler alive for the rest of the run.
                self._drop_sampler_tick(exc, timestamp_ms)
                previous_hits = None
                previous_reads = None
                previous_snapshot = None
                next_timestamp_ms += interval_ms
                continue
            if previous_hits is not None:
                delta_hits = hits - previous_hits
                delta_reads = reads - previous_reads
                if delta_hits < 0 or delta_reads < 0:
                    raise RuntimeError(
                        f"PostgreSQL pg_stat_database counters moved backwards: previous=({previous_hits},{previous_reads}), "
                        f"current=({hits},{reads}), timestamp_ms={timestamp_ms}"
                    )
                if delta_hits + delta_reads > 0:
                    values["cache_hit_ratio"] = {
                        "percent": round(delta_hits * 100.0 / (delta_hits + delta_reads), 2)
                    }
            previous_hits = hits
            previous_reads = reads

            try:
                snapshot = capture_statement_snapshot(sampler_conn, timestamp_ms)
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as exc:
                if not self.allow_sampler_reconnect:
                    raise
                self._drop_sampler_tick(exc, timestamp_ms)
                previous_hits = None
                previous_reads = None
                previous_snapshot = None
                next_timestamp_ms += interval_ms
                continue
            calls = sum(
                counter.calls
                for key, counter in snapshot.counters.items()
                if key.queryid not in self._pg_statement_excluded_queryids
            )
            if previous_snapshot is not None:
                previous_calls = sum(
                    counter.calls
                    for key, counter in previous_snapshot.counters.items()
                    if key.queryid not in self._pg_statement_excluded_queryids
                )
                if calls < previous_calls:
                    # pg_stat_statements is reset by several legitimate fault
                    # lifecycles (and may reset on a PostgreSQL restart). The
                    # sampler starts a fresh delta window at the reset tick.
                    self._pgss_sampler_reset_observed = False
                else:
                    elapsed_seconds = (snapshot.timestamp_ms - previous_snapshot.timestamp_ms) / 1000
                    if elapsed_seconds <= 0:
                        raise RuntimeError(
                            f"PostgreSQL statement snapshot interval is invalid: previous={previous_snapshot.timestamp_ms}, "
                            f"current={snapshot.timestamp_ms}"
                        )
                    values["qps"] = {"queries_per_second": round((calls - previous_calls) / elapsed_seconds, 3)}
            previous_snapshot = snapshot

            try:
                values.update(self._sample_additional_metrics(sampler_conn, timestamp_ms, values))
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as exc:
                if not self.allow_sampler_reconnect:
                    raise
                self._drop_sampler_tick(exc, timestamp_ms)
                previous_hits = None
                previous_reads = None
                previous_snapshot = None
                next_timestamp_ms += interval_ms
                continue

            with self._metric_service.live.lock:
                self._metric_service.live.append_sample(timestamp_ms, values)
                self._pg_statement_snapshots.append(snapshot)
            with self._sampler_condition:
                self._sampler_last_timestamp_ms = timestamp_ms
                self._sampler_condition.notify_all()
            next_timestamp_ms += interval_ms
            tick_elapsed_seconds = time.monotonic() - tick_started_mono
            if (
                tick_elapsed_seconds > self.sample_interval_sec * SAMPLER_LAG_TOLERANCE_INTERVALS
                and self.allow_sampler_jitter
            ):
                # Some scenario workloads deliberately make one generic
                # catalog sample slower than its nominal period. Preserve
                # the aligned metric contract, skip only the missed grid
                # points, and resume at the next future tick. Scenario-
                # owned observers remain responsible for causal evidence.
                next_timestamp_ms = (
                    int(time.time() * 1000) // interval_ms + 1
                ) * interval_ms
                continue
            self._sampler_record_tick_lag(tick_elapsed_seconds)

    def _read_cpu_usage_usec(self) -> int:
        """读取容器 cgroup CPU 累计使用微秒数。"""
        if self._detect_cgroup_version():
            stat = self._cgroup_read("/sys/fs/cgroup/cpu.stat")
            for line in stat.splitlines():
                if line.startswith("usage_usec"):
                    return int(line.split()[1])
            raise RuntimeError(f"PostgreSQL cgroup cpu.stat lacks usage_usec: stat={stat!r}")
        raw = self._cgroup_read("/sys/fs/cgroup/cpuacct/cpuacct.usage")
        return int(raw.strip()) // 1000

    def _effective_cpus(self) -> float:
        """读取容器 CPU 配额（核数）。"""
        if self._detect_cgroup_version():
            cpu_max = self._cgroup_read("/sys/fs/cgroup/cpu.max")
            parts = cpu_max.split()
            if len(parts) != 2 or parts[0] == "max":
                raise RuntimeError(f"PostgreSQL cgroup cpu.max does not define a finite quota: value={cpu_max!r}")
            quota, period = int(parts[0]), int(parts[1])
            if quota <= 0 or period <= 0:
                raise RuntimeError(f"PostgreSQL cgroup cpu.max quota is invalid: value={cpu_max!r}")
            return quota / period
        else:
            quota = self._cgroup_read("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
            period = self._cgroup_read("/sys/fs/cgroup/cpu/cpu.cfs_period_us")
            quota_value, period_value = int(quota.strip()), int(period.strip())
            if quota_value <= 0 or period_value <= 0:
                raise RuntimeError(f"PostgreSQL cgroup CPU quota is invalid: quota={quota!r}, period={period!r}")
            return quota_value / period_value

    def _container_top_cpu_processes(self) -> dict:
        """Return a generic top-process CPU snapshot from inside the PG container."""
        import subprocess

        deployment = getattr(self, "deployment", None)
        container_name = getattr(deployment, "container_name", None)
        if not container_name:
            return {"top_processes": [], "external_cpu_percent": 0.0}
        try:
            result = subprocess.run(
                [
                    "docker", "exec", container_name,
                    "bash", "-lc",
                    "ps -eo pid=,ppid=,comm=,pcpu=,args= --sort=-pcpu",
                ],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode != 0:
                return {"top_processes": [], "external_cpu_percent": 0.0}
            rows = []
            postgres_cpu = 0.0
            external_cpu = 0.0
            for line in result.stdout.splitlines():
                parts = line.strip().split(None, 4)
                if len(parts) < 5:
                    continue
                pid_raw, ppid_raw, comm, pcpu_raw, args = parts
                if "ps -eo" in args or "head -n" in args:
                    # Skip the snapshot's own observation shell.
                    continue
                try:
                    pid = int(pid_raw)
                    ppid = int(ppid_raw)
                    pcpu = float(pcpu_raw)
                except ValueError:
                    continue
                lowered = f"{comm} {args}".lower()
                is_db = any(term in lowered for term in ("postgres", "postmaster", "pg_ctl"))
                rows.append({
                    "pid": pid,
                    "ppid": ppid,
                    "comm": comm,
                    "args": args[:120],
                    "cpu_percent": pcpu,
                    "process_type": "database" if is_db else "external",
                })
                if is_db:
                    postgres_cpu += pcpu
                else:
                    external_cpu += pcpu
            return {
                "top_processes": rows,
                "postgres_cpu_percent": round(postgres_cpu, 1),
                "external_cpu_percent": round(external_cpu, 1),
            }
        except Exception:
            return {"top_processes": [], "external_cpu_percent": 0.0}

    def _sample_memory(self) -> float:
        """采样内存使用率（去 page cache 后的真实压力百分比）。"""
        cur, mx, stat, inactive_key = self._memory_cgroup_snapshot()
        used = int(cur.strip())
        limit = self._parse_cgroup_memory_limit(mx)
        if limit is None:
            raise RuntimeError(f"PostgreSQL cgroup memory limit is unavailable: raw_limit={mx!r}")
        inactive_file = None
        for line in stat.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] == inactive_key:
                inactive_file = int(parts[1])
                break
        if inactive_file is None:
            raise RuntimeError(f"PostgreSQL cgroup memory.stat lacks {inactive_key}: stat={stat!r}")
        if used < inactive_file:
            raise RuntimeError(
                f"PostgreSQL cgroup memory counters are inconsistent: used_bytes={used}, "
                f"inactive_file_bytes={inactive_file}"
            )
        real_used = used - inactive_file
        return round(real_used / limit * 100.0, 1)

    def _memory_cgroup_snapshot(self):
        if self._detect_cgroup_version():
            return (
                self._cgroup_read("/sys/fs/cgroup/memory.current"),
                self._cgroup_read("/sys/fs/cgroup/memory.max"),
                self._cgroup_read("/sys/fs/cgroup/memory.stat"),
                "inactive_file",
            )
        return (
            self._cgroup_read("/sys/fs/cgroup/memory/memory.usage_in_bytes"),
            self._cgroup_read("/sys/fs/cgroup/memory/memory.limit_in_bytes"),
            self._cgroup_read("/sys/fs/cgroup/memory/memory.stat"),
            "total_inactive_file",
        )

    def _parse_cgroup_memory_limit(self, raw: Optional[str]) -> Optional[int]:
        if raw is None:
            return None
        value = raw.strip()
        if not value or value == "max":
            return None
        limit = int(value)
        if limit > (1 << 62):
            return None
        return limit

    def _memory_limit_context(self) -> dict:
        try:
            _, mx, _, _ = self._memory_cgroup_snapshot()
            limit = self._parse_cgroup_memory_limit(mx)
            if limit is None:
                return {"memory_limit_mb": None, "memory_limit_bytes": None}
            return {
                "memory_limit_mb": round(limit / 1024 / 1024, 2),
                "memory_limit_bytes": limit,
            }
        except Exception:
            return {"memory_limit_mb": None, "memory_limit_bytes": None}

    def _sample_disk_io(self) -> Optional[tuple[float, float]]:
        """采样容器 cgroup 累计读/写字节并计算本 tick 吞吐。"""
        total_r = total_w = 0
        if self._detect_cgroup_version():
            stat = self._cgroup_read("/sys/fs/cgroup/io.stat")
            for line in stat.splitlines():
                for token in line.split():
                    if token.startswith("rbytes="):
                        total_r += int(token.split("=", 1)[1])
                    elif token.startswith("wbytes="):
                        total_w += int(token.split("=", 1)[1])
        else:
            stat = self._cgroup_read("/sys/fs/cgroup/blkio/blkio.io_service_bytes_recursive")
            for line in stat.splitlines():
                parts = line.split()
                if len(parts) == 3 and parts[1] == "Read":
                    total_r += int(parts[2])
                elif len(parts) == 3 and parts[1] == "Write":
                    total_w += int(parts[2])
        now_mono = time.monotonic()
        previous = getattr(self, "_prev_io_sample", None)
        self._prev_io_sample = (now_mono, total_r, total_w)
        if previous is None:
            return None
        if total_r < previous[1] or total_w < previous[2]:
            raise RuntimeError(
                f"PostgreSQL cgroup I/O counters moved backwards: previous=({previous[1]},{previous[2]}), "
                f"current=({total_r},{total_w})"
            )
        elapsed_seconds = now_mono - previous[0]
        if elapsed_seconds <= 0:
            raise RuntimeError(f"PostgreSQL cgroup I/O sampler interval is invalid: elapsed_seconds={elapsed_seconds}")
        return (
            round((total_r - previous[1]) / (1024 ** 2) / elapsed_seconds, 3),
            round((total_w - previous[2]) / (1024 ** 2) / elapsed_seconds, 3),
        )

    def _cgroup_read(self, path: str) -> str:
        """Read a container cgroup file without routing every sample through Docker CLI."""
        import subprocess

        if self._host_cgroup_base is None:
            inspect = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Pid}}", self.deployment.container_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if inspect.returncode == 0 and inspect.stdout.strip().isdigit():
                pid = inspect.stdout.strip()
                try:
                    with open(f"/proc/{pid}/cgroup", encoding="utf-8") as cgroup_file:
                        cgroup_lines = cgroup_file.read().splitlines()
                    unified = next(
                        (line.split(":", 2)[2] for line in cgroup_lines if line.startswith("0::")),
                        None,
                    )
                    if unified:
                        candidate = os.path.join("/sys/fs/cgroup", unified.lstrip("/"))
                        if os.path.isdir(candidate):
                            self._host_cgroup_base = candidate
                except (OSError, IndexError):
                    pass

        if self._host_cgroup_base is not None:
            relative_path = path.removeprefix("/sys/fs/cgroup/").lstrip("/")
            host_path = os.path.join(self._host_cgroup_base, relative_path)
            try:
                with open(host_path, encoding="utf-8") as cgroup_file:
                    return cgroup_file.read()
            except OSError:
                self._host_cgroup_base = None

        result = subprocess.run(
            ["docker", "exec", self.deployment.container_name, "cat", path],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"PostgreSQL cgroup read failed: path={path!r}, returncode={result.returncode}, "
                f"stderr={result.stderr.strip()!r}"
            )
        return result.stdout

    def _detect_cgroup_version(self) -> bool:
        """探测容器 cgroup 版本，True 表示 v2。结果缓存。"""
        if getattr(self, "_cgroup_v2", None) is not None:
            return self._cgroup_v2
        try:
            self._cgroup_read("/sys/fs/cgroup/cgroup.controllers")
            self._cgroup_v2 = True
        except RuntimeError:
            self._cgroup_v2 = False
        return self._cgroup_v2

    def _connection_snapshot(self, cur) -> dict:
        cur.execute(
            "SELECT state, count(*) FROM pg_stat_activity "
            "WHERE backend_type = 'client backend' GROUP BY state;")
        states = {row[0] or "null": int(row[1]) for row in cur.fetchall()}
        cur.execute(
            "SELECT wait_event_type, count(*) FROM pg_stat_activity "
            "WHERE backend_type = 'client backend' AND wait_event_type IS NOT NULL "
            "GROUP BY wait_event_type;")
        wait_types = {row[0] or "null": int(row[1]) for row in cur.fetchall()}
        cur.execute("SHOW max_connections;")
        return {
            "max_connections": int(cur.fetchone()[0]),
            "states": states,
            "wait_types": wait_types,
            "lock_waiting_sessions": wait_types.get("Lock", 0),
        }

    def _get_pg_knowledge_base(self, knowledge_base_mode: str) -> PGKnowledgeBase:
        if knowledge_base_mode not in self._pg_knowledge_bases:
            self._pg_knowledge_bases[knowledge_base_mode] = PGKnowledgeBase(
                knowledge_base_mode=knowledge_base_mode,
            )
        return self._pg_knowledge_bases[knowledge_base_mode]

    def _query_pg_knowledge_base(self, query: str, top_k: int,
                                 max_chars_per_result: int,
                                 knowledge_base_mode: str,
                                 kb_type: Optional[str] = None) -> str:
        knowledge_base = self._get_pg_knowledge_base(knowledge_base_mode)
        try:
            top_k_int = int(top_k)
        except (TypeError, ValueError):
            top_k_int = 5
        try:
            max_chars_int = int(max_chars_per_result)
        except (TypeError, ValueError):
            max_chars_int = 1600
        result = knowledge_base.query(
            query=query,
            top_k=top_k_int,
            max_chars_per_result=max_chars_int,
            kb_type=kb_type,
        )
        return json.dumps(result, ensure_ascii=False, default=str)

    @Tool(
        alias="query_knowledge_base",
        description=(
            "检索本地PostgreSQL 16官方文档通用知识库。该工具不做类型过滤，"
            "适合查询系统视图含义、参数语义、SQL语法、诊断线索、修复动作、索引/锁/"
            "MVCC/autovacuum/WAL等官方文档内容。"
        ),
        arg_descriptions={
            "query": "面向PostgreSQL文档的自然语言检索问题",
            "top_k": "返回片段数量，默认5，最大20",
            "max_chars_per_result": "每个片段最多返回字符数，默认1600",
        },
    )
    def query_general_knowledge_base(self, query: str, top_k: int = 5,
                                     max_chars_per_result: int = 1600) -> str:
        return self._query_pg_knowledge_base(
            query=query,
            top_k=top_k,
            max_chars_per_result=max_chars_per_result,
            knowledge_base_mode="general",
            kb_type=None,
        )

    @Tool(
        alias="query_knowledge_base",
        description=(
            "检索本地PostgreSQL 16官方文档层级知识库。可用 kb_type 限定 "
            "configuration/guide/solution/fact；不同类型分别覆盖配置、原理、操作建议和事实信息。"
        ),
        arg_descriptions={
            "query": "面向PostgreSQL文档的自然语言检索问题",
            "top_k": "返回片段数量，默认5，最大20",
            "max_chars_per_result": "每个片段最多返回字符数，默认1600",
            "kb_type": "可选知识类型过滤: configuration, guide, solution, fact",
        },
    )
    def query_hierarchical_knowledge_base(self, query: str, top_k: int = 5,
                                          max_chars_per_result: int = 1600,
                                          kb_type: Optional[str] = None) -> str:
        return self._query_pg_knowledge_base(
            query=query,
            top_k=top_k,
            max_chars_per_result=max_chars_per_result,
            knowledge_base_mode="hierarchical",
            kb_type=kb_type,
        )

    @Tool(
        alias="query_metrics",
        tool_id="query_metrics",
        description=POSTGRES_QUERY_METRICS_TOOL_DEFINITION["tool_description"],
        arg_descriptions={
            "metric_type": (
                "指标类型，可选 catalog 值: "
                + ", ".join(sorted(POSTGRES_METRIC_CATALOG.metric_names))
                + "; 当前 Case 还可用 filesystem_io、bufferio_waiters、host_pressure、"
                "partition_lifecycle 四类原始场景观测；先用 help('query_metrics') 查看字段、单位、"
                "baseline、采样窗口和最终恢复合同"
            ),
            "target": "目标对象；cpu 传 top_process/top_processes 返回容器内 top CPU 进程快照，disk_usage 返回根文件系统观测，其他指标按场景定义",
            "limit": "workload_activity 或场景 provider 使用，返回前 N 条记录，默认 20",
            "start_timestamp": "时序指标开始时间，必须与 end_timestamp 同时提供，格式 YYYY-MM-DD HH:mm:ss",
            "end_timestamp": "时序指标结束时间，必须与 start_timestamp 同时提供，格式 YYYY-MM-DD HH:mm:ss",
        },
        definition=POSTGRES_QUERY_METRICS_TOOL_DEFINITION,
    )
    def _query_metrics_for_agent(
        self,
        metric_type: str,
        target: str = None,
        limit: Optional[int] = None,
        start_timestamp: Optional[str] = None,
        end_timestamp: Optional[str] = None,
        step_seconds: Optional[int] = None,
    ) -> str:
        metric = str(metric_type or "").strip().lower()
        case_catalog = getattr(self, "_metric_catalog", None)
        case_metrics = getattr(case_catalog, "metric_names", ())
        history_spec = getattr(getattr(self, "_case", None), "frozen_history", None)
        if history_spec is not None:
            case_metrics = set(history_spec.required_metrics)
        allowed_metrics = case_metrics if history_spec is not None else self.AGENT_METRICS | set(case_metrics)
        if metric not in allowed_metrics:
            return json.dumps({
                "status": "error",
                "metric": metric,
                "error": f"Unknown PG environment metric_type: {metric_type}",
            }, ensure_ascii=False)
        if metric == "disk_usage":
            return self._query_container_filesystem_usage_for_agent()
        return bound_metric_result(self.query_metrics(
            metric_type=metric_type,
            target=target,
            limit=limit,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            step_seconds=step_seconds,
        ))

    def _query_container_filesystem_usage_for_agent(self) -> str:
        """Return only container filesystem capacity, not database size detail."""
        import subprocess

        container = getattr(self.deployment, "container_name", None)
        if not container:
            return json.dumps({
                "status": "error",
                "metric": "disk_usage",
                "error": "No deployment container configured",
            }, ensure_ascii=False)
        try:
            result = subprocess.run(
                [
                    "docker", "exec", container,
                    "df", "--output=used,avail,pcent", "-B1", "/",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except Exception as exc:
            return json.dumps({
                "status": "error",
                "metric": "disk_usage",
                "error": str(exc),
            }, ensure_ascii=False)
        if result.returncode != 0:
            return json.dumps({
                "status": "error",
                "metric": "disk_usage",
                "error": result.stderr.strip() or f"df exit_code={result.returncode}",
            }, ensure_ascii=False)
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if len(lines) < 2:
            return json.dumps({
                "status": "error",
                "metric": "disk_usage",
                "error": "Container df returned no filesystem row",
            }, ensure_ascii=False)
        fields = lines[-1].split()
        if len(fields) < 3:
            return json.dumps({
                "status": "error",
                "metric": "disk_usage",
                "error": f"Unexpected container df output: {result.stdout.strip()}",
            }, ensure_ascii=False)
        try:
            used_bytes = int(fields[0])
            available_bytes = int(fields[1])
            usage_percent = float(fields[2].rstrip("%"))
        except ValueError as exc:
            return json.dumps({
                "status": "error",
                "metric": "disk_usage",
                "error": f"Invalid container df output: {exc}",
            }, ensure_ascii=False)
        return self._metric_success(
            "disk_usage",
            "snapshot",
            snapshot={
                "filesystem": "/",
                "used_mb": round(used_bytes / (1024 ** 2), 2),
                "available_mb": round(available_bytes / (1024 ** 2), 2),
                "usage_percent": usage_percent,
                "source": "container_df",
            },
        )

    def query_metrics(self, metric_type: str, target: str = None,
                      threshold_ms: Optional[int] = None,
                      tables: Optional[str] = None,
                      limit: Optional[int] = None,
                      start_timestamp: Optional[str] = None,
                      end_timestamp: Optional[str] = None,
                      step_seconds: Optional[int] = None) -> str:
        self._raise_sampler_failure()
        start_time, end_time = self._metric_time_range(
            start_timestamp, end_timestamp
        )
        metric_lower = metric_type.lower()
        if metric_lower == "cpu" and target in {"top_process", "top_processes"}:
            series = json.loads(self.query_metrics(
                metric_type=metric_type,
                target=None,
                threshold_ms=threshold_ms,
                tables=tables,
                limit=limit,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                step_seconds=step_seconds,
            ))
            if series.get("status") != "success":
                return json.dumps(series, ensure_ascii=False)
            series["current"] = self._container_top_cpu_processes()
            return json.dumps(series, ensure_ascii=False)
        provider = getattr(self, "_scenario_metric_provider", None)
        provider_query = getattr(provider, "query", None)
        if callable(provider_query) and metric_lower in {
            "filesystem_io",
            "bufferio_waiters",
            "host_pressure",
            "partition_lifecycle",
        }:
            return provider_query(metric_lower, target, start_time, end_time)
        if metric_lower in self._metric_catalog.metric_names:
            try:
                start_ms = parse_utc_timestamp(start_timestamp, "start_timestamp") if start_timestamp is not None else None
                end_ms = parse_utc_timestamp(end_timestamp, "end_timestamp") if end_timestamp is not None else None
                history_timeline = self._history_timeline
                if history_timeline is not None:
                    # Frozen-history observations must be served by the frozen
                    # timeline.  Querying the live service first returns the
                    # sampler's 2-second grid and only changes the envelope
                    # metadata afterwards, which can expand a wide overview
                    # into hundreds of thousands of prompt tokens.
                    frame = history_timeline.metric_provider.query(MetricQuery(
                        metric=metric_lower,
                        target=target,
                        start_epoch_ms=start_ms,
                        end_epoch_ms=end_ms,
                        step_seconds=step_seconds,
                    ))
                else:
                    frame = self._metric_service.query_public(MetricQuery(
                        metric=metric_lower,
                        target=target,
                        start_epoch_ms=start_ms,
                        end_epoch_ms=end_ms,
                        step_seconds=step_seconds,
                    ))
                if self._history_timeline is not None:
                    available_start_ms = self._history_timeline.visible_start_ms
                    available_end_ms = self._history_timeline.visible_end_ms
                    requested_start_ms = start_ms if start_ms is not None else available_start_ms
                    requested_end_ms = end_ms if end_ms is not None else available_end_ms
                    requested_step = step_seconds or (
                        self._history_timeline.base_step_seconds
                        if start_ms is not None
                        else self._history_timeline.overview_step_seconds
                    )
                else:
                    available_start_ms, available_end_ms = self._metric_service.live.available_range
                    requested_start_ms = start_ms if start_ms is not None else available_start_ms
                    requested_end_ms = end_ms if end_ms is not None else available_end_ms
                    requested_step = step_seconds or frame.step_seconds
                return render_metric_frame(
                    frame,
                    available_start_ms=available_start_ms,
                    available_end_ms=available_end_ms,
                    requested_start_ms=requested_start_ms,
                    requested_end_ms=requested_end_ms,
                    step_seconds=requested_step,
                    # `limit` is an overview budget. Explicit historical
                    # windows must retain their complete evidence series;
                    # their size is controlled by the window/step contract.
                    max_points=(
                        (limit if limit is not None else 20)
                        if start_timestamp is None and end_timestamp is None
                        else None
                    ),
                )
            except (ValueError, RuntimeError, TypeError, KeyError) as exc:
                return json.dumps({"status": "error", "metric": metric_lower, "error": str(exc)}, ensure_ascii=False)
        if not self._ensure_connection():
            return json.dumps({"status": "error", "error": "No database connection."}, ensure_ascii=False)
        # workload_activity 是进程内数据，不走 DB。
        if metric_type.lower() == "workload_activity":
            return self._query_workload_activity(limit=limit or 20)
        try:
            with self._conn.cursor() as cur:
                metric_lower = metric_type.lower()
                if metric_lower == "slow_queries":
                    threshold = int(threshold_ms) if threshold_ms is not None else 5000
                    if threshold <= 0:
                        raise ValueError(
                            f"slow_queries threshold_ms must be positive: threshold_ms={threshold_ms!r}"
                        )
                    threshold_sec = threshold / 1000.0
                    # 1) 当前仍在执行的长查询 + idle in transaction 长事务
                    cur.execute(
                        """
                        SELECT pid, usename AS username, datname AS database_name,
                               state, wait_event_type, wait_event, query,
                               extract(epoch from (NOW() - query_start)) as query_duration_sec,
                               extract(epoch from (NOW() - xact_start)) as xact_duration_sec
                        FROM pg_stat_activity
                        WHERE ((state = 'active' AND query_start < NOW() - make_interval(secs => %s))
                           OR (state = 'idle in transaction' AND xact_start < NOW() - INTERVAL '30 seconds'))
                          AND backend_type = 'client backend'
                          AND pid <> pg_backend_pid();
                        """,
                        (threshold_sec,))
                    columns = [desc[0] for desc in cur.description]
                    running = [dict(zip(columns, row)) for row in cur.fetchall()]
                    for r in running:
                        r["source"] = "running" if r.get("state") == "active" else "idle_in_transaction"
                    # 2) 已完成的慢 SQL（pg_stat_statements）
                    finished = []
                    cur.execute(
                        """
                        SELECT userid, dbid, queryid, query,
                               round(mean_exec_time::numeric, 2) AS mean_ms,
                               round(max_exec_time::numeric, 2) AS max_ms,
                               calls
                        FROM pg_stat_statements
                        WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
                          AND (mean_exec_time > %s OR max_exec_time > %s)
                        ORDER BY mean_exec_time DESC
                        LIMIT 10;
                        """,
                        (threshold, threshold))
                    baseline = self._pgss_baseline.counters if self._pgss_baseline is not None else {}
                    for row in cur.fetchall():
                        uid, did, qid, query, mean_ms, max_ms, calls = row
                        calls = int(calls or 0)
                        base = baseline.get((uid, did, qid))
                        base_calls = base.calls if base is not None else 0
                        if calls < base_calls:
                            raise RuntimeError(
                                "PostgreSQL pg_stat_statements calls counter moved backwards while reading slow_queries: "
                                f"query_key={(uid, did, qid)!r}, baseline_calls={base_calls}, current_calls={calls}"
                            )
                        calls_delta = calls - base_calls
                        if base is not None and calls_delta <= 0:
                            continue
                        finished.append({
                            "queryid": qid,
                            "query": query,
                            "mean_ms": mean_ms,
                            "max_ms": max_ms,
                            "calls": calls_delta if base else calls,
                            "source": "finished",
                        })
                    results = running + finished
                    return self._metric_success(
                        "slow_queries", "records",
                        threshold_ms=threshold,
                        records=results,
                    )
                elif metric_lower in {"active_connections", "cpu", "memory", "disk_io"}:
                    raise AssertionError(
                        f"PostgreSQL sampler metric reached the SQL branch unexpectedly: metric={metric_lower!r}"
                    )
                elif metric_lower == "disk_usage":
                    if isinstance(target, str) and target.isidentifier():
                        cur.execute("SELECT to_regclass(%s)::text;", (target,))
                        # Fall through to a direct table query if the target relation exists.
                        relation = cur.fetchone()[0]
                        if relation:
                            cur.execute("""
                                SELECT
                                    pg_total_relation_size(to_regclass(%s))::bigint AS total_bytes,
                                    pg_relation_size(to_regclass(%s))::bigint AS heap_bytes;
                            """, (target, target))
                            total_bytes, heap_bytes = cur.fetchone()
                            cur.execute(f"SELECT reltuples::bigint FROM pg_class WHERE oid = to_regclass(%s);", (target,))
                            estimated_rows = cur.fetchone()[0]
                            return self._metric_success(
                                "disk_usage", "snapshot", target=target,
                                snapshot={
                                    "total_mb": round(total_bytes / (1024**2), 2),
                                    "heap_mb": round(heap_bytes / (1024**2), 2),
                                    "estimated_rows": int(estimated_rows or 0),
                                },
                            )

                    try:
                        cur.execute("SELECT coalesce(sum(size), 0) FROM pg_ls_waldir();")
                        wal_bytes = int(cur.fetchone()[0] or 0)
                    except Exception:
                        wal_bytes = 0

                    # --- 四类明细：data / wal / temp / log ---
                    wal_mb = round(wal_bytes / (1024**2), 2)

                    # data: 所有数据库大小汇总
                    try:
                        cur.execute("SELECT coalesce(sum(pg_database_size(oid)), 0)::bigint FROM pg_database;")
                        data_mb = round(int(cur.fetchone()[0] or 0) / (1024**2), 2)
                    except Exception:
                        self._conn.rollback()
                        data_mb = 0.0

                    # temp: pg_ls_tmpdir() 实时临时文件（PG12+）
                    try:
                        cur.execute("SELECT coalesce(sum(size), 0) FROM pg_ls_tmpdir();")
                        temp_mb = round(int(cur.fetchone()[0] or 0) / (1024**2), 2)
                    except Exception:
                        self._conn.rollback()
                        temp_mb = 0.0

                    # log: 容器内日志文件大小
                    import subprocess as _sp
                    log_mb = 0.0
                    try:
                        container_name = self.deployment.container_name
                        r = _sp.run([
                            "docker", "exec", container_name,
                            "bash", "-c", "du -sb /var/log/postgresql 2>/dev/null | cut -f1"
                        ], capture_output=True, text=True, timeout=10)
                        if r.returncode == 0 and r.stdout.strip():
                            log_mb = round(int(r.stdout.strip()) / (1024**2), 2)
                    except Exception:
                        pass

                    used_mb = round(data_mb + wal_mb + temp_mb + log_mb, 2)

                    # --- 可写层剩余空间（df 读取） ---
                    import subprocess as _sp
                    available_mb = None
                    try:
                        container_name = self.deployment.container_name
                        r = _sp.run([
                            "docker", "exec", container_name,
                            "df", "--output=avail", "-B1", "/"
                        ], capture_output=True, text=True, timeout=10)
                        if r.returncode == 0:
                            lines = r.stdout.strip().splitlines()
                            if len(lines) >= 2:
                                available_mb = round(int(lines[1].strip()) / (1024 ** 2), 2)
                    except Exception:
                        pass

                    return self._metric_success(
                        "disk_usage", "snapshot",
                        snapshot={
                            "used_mb": used_mb,
                            "available_mb": available_mb,
                            "data_mb": data_mb,
                            "wal_mb": wal_mb,
                            "temp_mb": temp_mb,
                            "log_mb": log_mb,
                        },
                    )
                elif metric_lower == "qps":
                    raise AssertionError("PostgreSQL qps metric must be served by the sampler provider")
                elif metric_lower == "topsql":
                    if self._pgss_baseline is None:
                        raise RuntimeError("PostgreSQL topsql requires an initialized pg_stat_statements baseline")
                    current = capture_statement_snapshot(self._conn, int(time.time() * 1000))
                    interval_records = build_topsql_delta_records(
                        self._pgss_baseline,
                        current,
                        excluded_queryids=self._pg_statement_excluded_queryids,
                    )
                    rows = [
                        {
                            "queryid": int(record.payload["digest"]),
                            "query": record.payload["sql_text"],
                            "calls": record.payload["exec_count"],
                            "total_ms": round(float(record.payload["sum_latency"]), 2),
                            "mean_ms": round(float(record.payload["avg_latency"]), 2),
                            "rows": record.payload["rows"],
                            "shared_blks_hit": record.payload["shared_blks_hit"],
                            "shared_blks_read": record.payload["shared_blks_read"],
                            "shared_blks_written": record.payload["shared_blks_written"],
                            "temp_blks_read": record.payload["temp_blks_read"],
                            "temp_blks_written": record.payload["temp_blks_written"],
                        }
                        for record in interval_records
                    ]
                    rows.sort(key=lambda row: row["total_ms"], reverse=True)
                    return self._metric_success(
                        "topsql", "records", scope="since_deploy", records=rows[:10]
                    )
                elif metric_lower == "cache_hit_ratio":
                    raise AssertionError("PostgreSQL cache_hit_ratio metric must be served by the sampler provider")
                elif metric_lower == "dead_tuples":
                    table_list = []
                    if isinstance(tables, str) and tables.strip():
                        for raw in tables.split(","):
                            name = raw.strip()
                            # 仅保留合法标识符，避免 SQL 注入
                            if name and name.replace("_", "").isalnum():
                                table_list.append(name)
                    if table_list:
                        placeholders = ",".join(["%s"] * len(table_list))
                        cur.execute(f"""
                            SELECT schemaname, relname AS table_name, n_live_tup, n_dead_tup,
                                   round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0), 4) AS dead_ratio,
                                   last_autovacuum, last_vacuum
                            FROM pg_stat_user_tables
                            WHERE relname IN ({placeholders})
                            ORDER BY n_dead_tup DESC;
                        """, tuple(table_list))
                    else:
                        cur.execute("""
                            SELECT schemaname, relname AS table_name, n_live_tup, n_dead_tup,
                                   round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0), 4) AS dead_ratio,
                                   last_autovacuum, last_vacuum
                            FROM pg_stat_user_tables
                            ORDER BY n_dead_tup DESC
                            LIMIT 10;
                        """)
                    columns = [desc[0] for desc in cur.description]
                    results = [dict(zip(columns, row)) for row in cur.fetchall()]
                    for r in results:
                        if r.get("dead_ratio") is not None:
                            r["dead_ratio"] = float(r["dead_ratio"])
                    return self._metric_success(
                        "dead_tuples", "records", records=results
                    )
                else:
                    return json.dumps({"status": "error", "error": f"Unknown metric_type: {metric_type}"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False)

    def set_agent_sql_timeouts(self, statement_timeout: str, lock_timeout: str) -> None:
        """Bound blocking agent SQL like a real client timeout would.

        Only the Agent action path uses this: an agent statement that waits on
        a lock or runs forever must fail with a visible timeout instead of
        wedging the scenario run. Trusted injector/evaluator SQL is unaffected.
        """
        with self._sql_connection_lock:
            if not self._ensure_connection():
                return
            try:
                with self._conn.cursor() as cur:
                    cur.execute(f"SET statement_timeout = '{statement_timeout}'; SET lock_timeout = '{lock_timeout}';")
            except Exception:
                self._conn = None

    def reset_agent_sql_timeouts(self) -> None:
        with self._sql_connection_lock:
            if self._conn is None:
                return
            try:
                with self._conn.cursor() as cur:
                    cur.execute("SET statement_timeout = 0; SET lock_timeout = 0;")
            except Exception:
                self._conn = None

    @Tool(
        description=(
            "执行 PostgreSQL 当前实例或只读冻结历史连接面上的 SQL。"
            "返回结果最多 200 行且不超过 128 KiB，超限时 truncated=true 并附带 truncation_hint；"
            "此时请缩小查询窗口：只选需要的列、加 WHERE/LIMIT，或改用聚合后分页查看。"
        ),
        arg_descriptions={"sql_query": "要执行的 SQL 语句", "target": "连接面名称；不传、传 'primary' 或传告警中的实例名 'postgresql-primary' 使用当前 PostgreSQL 实例，'history' 表示只读冻结历史"},
    )
    def execute_sql(self, sql_query: str, target: Optional[str] = None) -> str:
        if target == "history":
            if self._history_sql_archive is None:
                return json.dumps({"status": "error", "error": "PostgreSQL history SQL surface is unavailable"}, ensure_ascii=False)
            try:
                columns, rows, row_count, truncated = self._history_sql_archive.execute(sql_query)
                payload = {"status": "success", "columns": columns, "result": rows, "row_count": row_count, "truncated": truncated}
                if truncated:
                    payload["truncation_hint"] = SQL_TRUNCATION_HINT
                return json.dumps(payload, ensure_ascii=False, default=str)
            except (ValueError, RuntimeError, TypeError) as exc:
                return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)
        if target == "postgresql-primary":
            # Alerts and docs name the instance postgresql-primary; agents echo
            # that name back as the SQL target. It is the primary surface.
            target = "primary"
        if target == "standby":
            return self._execute_standby_sql(sql_query)
        if target not in {None, "primary"}:
            return json.dumps({"status": "error", "error": f"Unknown PostgreSQL SQL target: {target!r}; valid targets: omit the argument, 'primary' (current instance), 'postgresql-primary' (alert instance name), 'standby' (read-only replica endpoint, when configured), or 'history' (frozen history)"}, ensure_ascii=False)
        return self._execute_sql_surface(sql_query, enforce_history_guard=True)

    def _execute_standby_sql(self, sql_query: str) -> str:
        """Read-only SQL against the configured standby endpoint.

        The route only exists when a scenario registered a "standby" workload
        connection pool; the session is forced read-only so remediation SQL
        can never reach the replica by accident.
        """
        endpoint = self._workload_connection_endpoints.get("standby")
        if endpoint is None:
            return json.dumps({"status": "error", "error": f"PostgreSQL standby endpoint is not configured: pools={sorted(self._workload_connection_endpoints)}"}, ensure_ascii=False)
        import psycopg2

        try:
            connection = psycopg2.connect(
                host=str(endpoint["host"]),
                port=int(endpoint["port"]),
                user=str(endpoint["user"]),
                password=str(endpoint["password"]),
                dbname=str(endpoint["dbname"]),
                connect_timeout=3,
                application_name="aiopsbench-standby-sql",
            )
        except psycopg2.Error as exc:
            return json.dumps({"status": "error", "error": f"PostgreSQL standby connection failed: {exc!r}"}, ensure_ascii=False)
        try:
            connection.set_session(readonly=True, autocommit=True)
            with connection.cursor() as cur:
                cur.execute(sql_query)
                if cur.description:
                    fetchmany = getattr(cur, "fetchmany", None)
                    fetched = fetchmany(PG_SQL_RESULT_MAX_ROWS + 1) if callable(fetchmany) else cur.fetchall()
                    result, truncated = _bound_sql_rows(fetched)
                    payload = {"status": "success", "columns": [column.name for column in cur.description], "result": result}
                    if truncated:
                        payload.update({"truncated": True, "returned_rows": len(result), "row_limit": PG_SQL_RESULT_MAX_ROWS, "byte_limit": PG_SQL_RESULT_MAX_BYTES})
                else:
                    payload = {"status": "success", "columns": [], "result": []}
            return json.dumps(payload, ensure_ascii=False, default=str)
        except psycopg2.Error as exc:
            return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)
        finally:
            connection.close()

    def execute_sql_trusted(self, sql_query: str) -> str:
        """Execute current-state SQL for evaluator and injector trusted checks."""
        return self._execute_sql_surface(sql_query, enforce_history_guard=False)

    def _execute_sql_surface(self, sql_query: str, *, enforce_history_guard: bool) -> str:
        with self._sql_connection_lock:
            return self._execute_sql_surface_locked(sql_query, enforce_history_guard)

    def _execute_sql_surface_locked(self, sql_query: str, enforce_history_guard: bool) -> str:
        if not self._ensure_connection():
            return json.dumps({"status": "error", "error": "PostgreSQL 服务未运行或无法连接。请使用 manage_instance('start') 启动服务。"}, ensure_ascii=False)
        if enforce_history_guard and self._history_timeline is not None:
            try:
                reject_postgres_public_historical_sql(sql_query)
            except (ValueError, RuntimeError, TypeError) as exc:
                return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)
        connection = self._conn
        if connection is None:
            # A concurrent caller's failure may have dropped the shared
            # connection between the readiness check and here; reconnect once.
            if not self._ensure_connection():
                return json.dumps({"status": "error", "error": "PostgreSQL 服务未运行或无法连接。请使用 manage_instance('start') 启动服务。"}, ensure_ascii=False)
            connection = self._conn
        try:
            with connection.cursor() as cur:
                cur.execute(sql_query)
                if cur.description:
                    fetchmany = getattr(cur, "fetchmany", None)
                    fetched = (
                        fetchmany(PG_SQL_RESULT_MAX_ROWS + 1)
                        if callable(fetchmany)
                        else cur.fetchall()
                    )
                    result, truncated = _bound_sql_rows(fetched)
                    payload = {
                        "status": "success",
                        "columns": [column.name for column in cur.description],
                        "result": result,
                    }
                    if truncated:
                        payload.update({
                            "truncated": True,
                            "returned_rows": len(result),
                            "row_limit": PG_SQL_RESULT_MAX_ROWS,
                            "byte_limit": PG_SQL_RESULT_MAX_BYTES,
                            "truncation_hint": SQL_TRUNCATION_HINT,
                        })
                    return json.dumps(payload, default=str, ensure_ascii=False)
                else:
                    connection.commit()
                    return json.dumps({"status": "success", "message": "SQL executed."}, ensure_ascii=False)
        except Exception as e:
            self._conn = None
            return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False)

    @Tool(
        description="DB-GPT D-Bot semantic tool：检查指定指标是否异常",
        arg_descriptions={
            "metric_name": "指标名称，如 cpu_usage、memory_usage、io_usage、slow_queries、workload、query",
        },
    )
    def whether_is_abnormal_metric(self, metric_name: str) -> str:
        metric_type = self._db_gpt_metric_name(metric_name)
        return self.query_metrics(metric_type=metric_type)

    @Tool(
        description=(
            "DB-GPT D-Bot semantic tool：按专家类型聚合诊断证据，包含系统指标、workload、"
            "slow queries 和可选 PostgreSQL 知识库片段"
        ),
        arg_descriptions={
            "metric_name": "专家名或指标名，如 CpuExpert、MemoryExpert、IoExpert、QueryExpert",
            "alert_metric": "告警指标或告警摘要，可选",
        },
    )
    def match_diagnose_knowledge(self, metric_name: str, alert_metric: str = "") -> str:
        metric_prefix = self._db_gpt_metric_prefix(metric_name)
        system_metrics = {
            "cpu": ["cpu", "active_connections", "qps"],
            "io": ["disk_io", "disk_usage", "cache_hit_ratio"],
            "memory": ["memory", "cache_hit_ratio", "active_connections"],
        }[metric_prefix]
        metrics = system_metrics + ["topsql", "slow_queries"]
        results = []
        for metric in metrics:
            kwargs: Dict[str, Any] = {"metric_type": metric}
            if metric == "slow_queries":
                kwargs["threshold_ms"] = 1000
            results.append(json.loads(self.query_metrics(**kwargs)))

        knowledge = []
        if "query_knowledge_base" in self._alias_to_tool_spec:
            query = " ".join([metric_name, alert_metric, *metrics]).strip()
            knowledge = json.loads(self.execute_action("query_knowledge_base", {"query": query, "top_k": 5}))

        return json.dumps({
            "status": "success",
            "metric_prefix": metric_prefix,
            "system_metrics": system_metrics,
            "workload_metrics": ["topsql"],
            "slow_query_metrics": ["slow_queries"],
            "results": results,
            "knowledge": knowledge,
        }, ensure_ascii=False, default=str)

    @Tool(
        description=(
            "DB-GPT D-Bot semantic tool：收集索引优化所需的 workload、schema、列统计、已有索引"
            "和 hypopg 可用性证据"
        ),
        arg_descriptions={
            "start_time": "诊断窗口开始时间，可选",
            "end_time": "诊断窗口结束时间，可选",
        },
    )
    def optimize_index_selection(self, start_time: str = "", end_time: str = "") -> str:
        queries = [
            (
                "workload",
                "SELECT current_database() AS dbname, query AS sql, calls, "
                "total_exec_time, mean_exec_time "
                "FROM pg_stat_statements "
                "WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database()) "
                "AND query NOT ILIKE '%pg_stat_statements%' "
                "AND query NOT ILIKE 'EXPLAIN%' "
                "ORDER BY total_exec_time DESC LIMIT 10;",
            ),
            (
                "schema",
                "SELECT table_schema, table_name, column_name, data_type "
                "FROM information_schema.columns "
                "WHERE table_schema NOT IN ('pg_catalog', 'information_schema') "
                "ORDER BY table_schema, table_name, ordinal_position;",
            ),
            (
                "column_statistics",
                "SELECT schemaname, tablename, attname, null_frac, n_distinct, "
                "most_common_vals::text AS most_common_vals, histogram_bounds::text AS histogram_bounds "
                "FROM pg_stats "
                "WHERE schemaname NOT IN ('pg_catalog', 'information_schema') "
                "ORDER BY schemaname, tablename, attname;",
            ),
            (
                "existing_indexes",
                "SELECT schemaname, tablename, indexname, indexdef "
                "FROM pg_indexes "
                "WHERE schemaname NOT IN ('pg_catalog', 'information_schema') "
                "ORDER BY schemaname, tablename, indexname;",
            ),
            (
                "hypopg_available",
                "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'hypopg') "
                "AS hypopg_available;",
            ),
        ]
        evidence = [
            {"name": name, "result": json.loads(self.execute_sql(sql_query))}
            for name, sql_query in queries
        ]
        return json.dumps({
            "status": "success",
            "start_time": start_time,
            "end_time": end_time,
            "evidence": evidence,
        }, ensure_ascii=False, default=str)

    @staticmethod
    def _db_gpt_metric_name(metric_name: str) -> str:
        name = str(metric_name).strip().lower()
        aliases = {
            "cpu_usage": "cpu",
            "memory_usage": "memory",
            "mem_usage": "memory",
            "io_usage": "disk_io",
            "io": "disk_io",
            "disk": "disk_usage",
            "index": "topsql",
            "query": "slow_queries",
            "workload": "topsql",
            "configuration": "active_connections",
            "recovery": "disk_usage",
        }
        return aliases.get(name, name)

    @staticmethod
    def _db_gpt_metric_prefix(metric_name: str) -> str:
        name = str(metric_name).strip().lower()
        if "cpu" in name or "workload" in name or "index" in name or "query" in name:
            return "cpu"
        if "write" in name or "io" in name:
            return "io"
        if "mem" in name:
            return "memory"
        return "cpu"

    def _restart_pg_instance(self) -> str:
        if not self.deployment.restart_pg():
            return json.dumps({"status": "error", "error": "pg_ctl restart failed"})
        self._conn = None
        if not self.deployment.wait_for_ready(timeout=60):
            return json.dumps({"status": "error", "error": "PG not ready after restart"})
        self._ensure_connection()
        return json.dumps({"status": "success", "action": "restart"})

    def _start_pg_instance(self) -> str:
        if not self.deployment.start_pg():
            return json.dumps({"status": "error", "error": "pg_ctl start failed"})
        if not self.deployment.wait_for_ready(timeout=60):
            return json.dumps({"status": "error", "error": "PG not ready after start"})
        self._ensure_connection()
        return json.dumps({"status": "success", "action": "start"})

    @Tool(
        description=(
            "管理数据库实例（进程控制与配置管理）。"
            "get_config/set_config/reset_config 的 target 可以是 PostgreSQL 参数，"
            "也可以是少量实例级 OS 进程资源限制。"
            "terminate_process 仅用于终止容器内指定的非 PostgreSQL OS 进程；"
            "数据库会话应通过 execute_sql 执行 pg_terminate_backend。"
            "validate_backup 仅用于备份/RPO 场景，校验容器内物理备份文件和归档 WAL 可恢复链；"
            "它不是通用 SQL 查询，也不能由普通数据库连接替代。"
            "配置 PgBouncer endpoint 后，pgbouncer_show_*、pgbouncer_set_config 和 "
            "pgbouncer_reload 用于真实连接池 admin 操作。"
        ),
        arg_descriptions={
            "action": "操作类型，可选值: restart, start, stop, reboot, get_config, set_config, reset_config, terminate_process, validate_backup, pgbouncer_show_pools, pgbouncer_show_config, pgbouncer_show_stats, pgbouncer_set_config, pgbouncer_reload。terminate_process 只面向非 PostgreSQL OS 进程；validate_backup 只面向备份/RPO 场景；reboot 为重启整台机器的高危操作，仅在明确需要机器级重启时使用",
            "target": "目标实例名、配置参数名、进程资源名、进程标识或备份目录；terminate_process 使用 PID 或简单进程名；validate_backup 使用容器内备份目录或 manifest 路径",
            "value": "配置值（用于 set_config 或 pgbouncer_set_config；validate_backup、SHOW 和 reload 可留空）",
        },
    )
    def manage_instance(self, action: str, target: str = None, value: str = None) -> str:
        controller = getattr(self, "_rpo_controller", None)
        if controller is not None and action in {
            "archive_status",
            "rpo_topology",
            "recover_archive",
            "pitr_restore",
            "validate_backup",
        }:
            return controller.handle_manage_instance(action, target, value)
        if self.deployment is None:
            return json.dumps({"status": "error", "error": "No deployment configured"})

        if action == "pgbouncer_show_pools":
            return self.pgbouncer_admin_query("SHOW POOLS;")
        elif action == "pgbouncer_show_config":
            return self.pgbouncer_admin_query("SHOW CONFIG;")
        elif action == "pgbouncer_show_stats":
            return self.pgbouncer_admin_query("SHOW STATS;")
        elif action == "pgbouncer_reload":
            return self._reload_pgbouncer()
        elif action == "pgbouncer_set_config":
            return self._set_pgbouncer_config(target, value)
        elif action == "restart":
            print(f"[Env:PGEnv] Restarting PostgreSQL process...")
            return self._run_lifecycle_with_sampler("restart", self._restart_pg_instance)
        elif action == "stop":
            print(f"[Env:PGEnv] Stopping PostgreSQL process...")
            if not self.deployment.stop_pg():
                return json.dumps({"status": "error", "error": "pg_ctl stop failed"})
            self._conn = None
            return json.dumps({"status": "success", "action": "stop"})
        elif action == "start":
            print(f"[Env:PGEnv] Starting PostgreSQL process...")
            return self._run_lifecycle_with_sampler("start", self._start_pg_instance)
        elif action == "reboot":
            print(f"[Env:PGEnv] Rebooting machine (docker stop/start)...")
            sampler_was_running = self._sampler_thread is not None and self._sampler_thread.is_alive()
            self._expected_sampler_disconnect_reason = "manage_instance('reboot')"
            self._expected_sampler_disconnect_evidence = {
                "action": "reboot",
                "sampler_was_running": str(sampler_was_running),
            }
            if sampler_was_running:
                self._stop_sampler()
            self._reset_cgroup_io_sampler_state()
            try:
                if not self.deployment.reboot_machine():
                    return json.dumps({"status": "error", "error": "Machine reboot failed"})
                self._conn = None
                timeout = int(self.deployment.resources.get("reboot_ready_timeout_sec", 120))
                if not self.deployment.wait_for_ready(timeout=timeout):
                    return json.dumps({"status": "error", "error": "PG not ready after reboot"})
                self._ensure_connection()
                return json.dumps({"status": "success", "action": "reboot"})
            finally:
                self._reset_cgroup_io_sampler_state()
                if self._scenario_metric_provider is None:
                    self._start_sampler()
                self._expected_sampler_disconnect_reason = None
                self._expected_sampler_disconnect_evidence = None
        elif action == "get_config":
            return self._get_config(target)
        elif action == "set_config":
            return self._set_config(target, value)
        elif action == "reset_config":
            return self._reset_config(target)
        elif action == "terminate_process":
            return self._terminate_process(target)
        elif action == "validate_backup":
            return self._validate_backup(target)
        else:
            return json.dumps({"status": "error", "error": f"Unknown action: {action}"})

    def _set_pgbouncer_config(self, target: str, value: str) -> str:
        allowed = {
            "pool_mode",
            "default_pool_size",
            "reserve_pool_size",
            "reserve_pool_timeout",
            "max_db_connections",
            "max_user_connections",
            "max_client_conn",
        }
        key = str(target or "").strip().casefold()
        if key not in allowed:
            return json.dumps(
                {"status": "error", "error": f"Unsupported PgBouncer setting: {target!r}", "allowed": sorted(allowed)},
                ensure_ascii=False,
            )
        if value is None or not str(value).strip():
            return json.dumps({"status": "error", "error": "Missing PgBouncer setting value"}, ensure_ascii=False)
        normalized = str(value).strip()
        if len(normalized) > 64 or any(character in normalized for character in "\r\n;'\\"):
            return json.dumps({"status": "error", "error": "Invalid PgBouncer setting value"}, ensure_ascii=False)
        result = self.pgbouncer_admin_query(f"SET {key} = '{normalized}';")
        try:
            payload = json.loads(result)
        except json.JSONDecodeError:
            payload = {}
        if payload.get("status") == "success":
            self._pgbouncer_runtime_overrides[key] = normalized
        return result

    def _reload_pgbouncer(self) -> str:
        result = self.pgbouncer_admin_query("RELOAD;")
        try:
            payload = json.loads(result)
        except json.JSONDecodeError:
            payload = {}
        if payload.get("status") != "success":
            return result
        reapplied = []
        for key, value in self._pgbouncer_runtime_overrides.items():
            reapplied_result = self.pgbouncer_admin_query(f"SET {key} = '{value}';")
            try:
                reapplied_payload = json.loads(reapplied_result)
            except json.JSONDecodeError:
                reapplied_payload = {}
            if reapplied_payload.get("status") != "success":
                return json.dumps(
                    {"status": "error", "error": f"Failed to reapply PgBouncer setting: {key}"},
                    ensure_ascii=False,
                )
            reapplied.append(key)
        return json.dumps(
            {"status": "success", "action": "reload", "reapplied": reapplied},
            ensure_ascii=False,
        )

    def _get_config(self, param_name: str) -> str:
        if not param_name:
            return json.dumps({"status": "error", "error": "Missing param name (target)"})
        import subprocess
        if self._is_nofile_config(param_name):
            try:
                payload = self.deployment.get_pg_nofile_limit()
                if payload.get("status") != "success":
                    return json.dumps(payload, ensure_ascii=False)
                return json.dumps({
                    "status": "success",
                    "param": "nofile",
                    "value": payload.get("configured", "(default)"),
                    "running_soft": payload.get("running_soft", "(unknown)"),
                    "running_hard": payload.get("running_hard", "(unknown)"),
                    "source": "os_process_limit",
                }, ensure_ascii=False)
            except Exception as e:
                return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False)
        if self._conn is not None:
            try:
                with self._conn.cursor() as cur:
                    cur.execute(f"SHOW {param_name};")
                    val = cur.fetchone()[0]
                return json.dumps({"status": "success", "param": param_name, "value": val, "source": "runtime"})
            except Exception:
                pass
        container = self.deployment.container_name
        try:
            result = subprocess.run(
                ["docker", "exec", container, "cat",
                 f"{self.deployment.pgdata}/postgresql.auto.conf"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                if key.strip() == param_name:
                    return json.dumps({"status": "success", "param": param_name, "value": val.strip().strip("'"), "source": "auto.conf"})
            return json.dumps({"status": "success", "param": param_name, "value": "(default)", "source": "default"})
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)})

    def _set_config(self, param_name: str, value: str) -> str:
        if not param_name or value is None:
            return json.dumps({"status": "error", "error": "Missing param name (target) or value"})
        import subprocess
        if self._is_nofile_config(param_name):
            try:
                limit = int(str(value).strip())
            except ValueError:
                return json.dumps({"status": "error", "error": "nofile value must be an integer"}, ensure_ascii=False)
            if limit < 8:
                return json.dumps({"status": "error", "error": "nofile value is too low"}, ensure_ascii=False)
            try:
                if not self.deployment.set_pg_nofile_limit(limit):
                    return json.dumps({"status": "error", "error": "failed to write nofile limit"}, ensure_ascii=False)
                return json.dumps({
                    "status": "success",
                    "action": "set_config",
                    "param": "nofile",
                    "value": str(limit),
                    "note": "OS process nofile limit written; restart PostgreSQL to apply",
                }, ensure_ascii=False)
            except Exception as e:
                return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False)
        if self._conn is not None:
            try:
                with self._conn.cursor() as cur:
                    cur.execute(f"ALTER SYSTEM SET {param_name} = '{value}';")
                return json.dumps({"status": "success", "action": "set_config", "param": param_name, "value": value, "note": "需要 restart/reload 生效"})
            except Exception:
                pass
        container = self.deployment.container_name
        try:
            sed_cmd = f"grep -q \"^{param_name}\" {self.deployment.pgdata}/postgresql.auto.conf && " \
                      f"sed -i \"s|^{param_name}.*|{param_name} = '{value}'|\" {self.deployment.pgdata}/postgresql.auto.conf || " \
                      f"echo \"{param_name} = '{value}'\" >> {self.deployment.pgdata}/postgresql.auto.conf"
            subprocess.run(
                ["docker", "exec", container, "bash", "-c", sed_cmd],
                capture_output=True, text=True, timeout=10, check=True
            )
            return json.dumps({"status": "success", "action": "set_config", "param": param_name, "value": value, "note": "已写入 auto.conf，需要 start/restart 生效"})
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)})

    def _reset_config(self, param_name: str) -> str:
        if not param_name:
            return json.dumps({"status": "error", "error": "Missing param name (target)"})
        import subprocess
        if self._is_nofile_config(param_name):
            try:
                if not self.deployment.reset_pg_nofile_limit():
                    return json.dumps({"status": "error", "error": "failed to reset nofile limit"}, ensure_ascii=False)
                return json.dumps({
                    "status": "success",
                    "action": "reset_config",
                    "param": "nofile",
                    "note": "OS process nofile limit reset; restart PostgreSQL to apply",
                }, ensure_ascii=False)
            except Exception as e:
                return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False)
        if self._conn is not None:
            try:
                with self._conn.cursor() as cur:
                    cur.execute(f"ALTER SYSTEM RESET {param_name};")
                return json.dumps({"status": "success", "action": "reset_config", "param": param_name})
            except Exception:
                pass
        container = self.deployment.container_name
        try:
            subprocess.run(
                ["docker", "exec", container, "sed", "-i",
                 f"/^{param_name}/d", f"{self.deployment.pgdata}/postgresql.auto.conf"],
                capture_output=True, text=True, timeout=10, check=True
            )
            return json.dumps({"status": "success", "action": "reset_config", "param": param_name, "note": "已从 auto.conf 移除，需要 start/restart 生效"})
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)})

    def _is_nofile_config(self, param_name: str) -> bool:
        return str(param_name or "").lower().strip() in {
            "nofile",
            "ulimit_n",
            "ulimit_nofile",
            "max_open_files",
            "open_files",
        }

    def _terminate_process(self, target: str) -> str:
        import re
        import subprocess

        if not target:
            return json.dumps({"status": "error", "error": "Missing process target"})
        target_text = str(target).strip()
        if target_text.casefold() in {"postgres", "postmaster", "postgresql"}:
            return json.dumps({
                "status": "error",
                "action": "terminate_process",
                "target": target_text,
                "error": (
                    "Refusing to terminate the PostgreSQL server process; use a lifecycle action "
                    "or execute_sql with pg_terminate_backend for a database session"
                ),
            }, ensure_ascii=False)
        if target_text.isdigit():
            pid = int(target_text)
            command = (
                f"comm=$(ps -p {pid} -o comm= 2>/dev/null || true); "
                "case \"$comm\" in postgres|postmaster|postgres:*) exit 4;; esac; "
                f"kill -TERM {pid} && printf '%s\\n' {pid}"
            )
        else:
            if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,64}", target_text):
                return json.dumps({"status": "error", "error": "Process target must be a PID or simple name"}, ensure_ascii=False)
            command = (
                "roots=$(ps -eo pid=,args= | awk "
                f"'$0 ~ /{target_text}/ && $0 !~ /awk/ && $0 !~ /ps -eo/ {{print $1}}'); "
                "test -n \"$roots\" || exit 3; "
                "all=\"$roots\"; frontier=\"$roots\"; "
                "for depth in $(seq 1 8); do "
                "children=''; "
                "for parent in $frontier; do "
                "found=$(pgrep -P \"$parent\" 2>/dev/null || true); "
                "children=\"$children $found\"; "
                "done; "
                "frontier=$(printf '%s\\n' $children | awk 'NF && !seen[$1]++'); "
                "test -n \"$frontier\" || break; "
                "all=\"$all $frontier\"; "
                "done; "
                "pids=$(printf '%s\\n' $all | awk 'NF && !seen[$1]++'); "
                "kill -TERM $pids; "
                "sleep 0.2; "
                "kill -KILL $roots 2>/dev/null || true; "
                "printf '%s\\n' $pids"
            )
        try:
            result = subprocess.run(
                ["docker", "exec", self.deployment.container_name, "bash", "-lc", command],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode not in (0,):
                return json.dumps({
                    "status": "error",
                    "action": "terminate_process",
                    "target": target_text,
                    "error": result.stderr.strip() or result.stdout.strip() or f"exit_code={result.returncode}",
                }, ensure_ascii=False)
            killed = [line.strip() for line in result.stdout.splitlines() if line.strip().isdigit()]
            return json.dumps({
                "status": "success",
                "action": "terminate_process",
                "target": target_text,
                "killed_pids": killed,
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False)

    def _safe_container_path(self, path: str, label: str) -> str:
        import posixpath
        import re

        if not path:
            raise ValueError(f"Missing {label}")
        normalized = posixpath.normpath(str(path).strip())
        allowed_prefixes = (
            "/tmp/",
            "/var/tmp/",
            "/var/lib/postgresql/backup/",
        )
        if not normalized.startswith(allowed_prefixes):
            raise ValueError(f"{label} must be under /tmp, /var/tmp, or /var/lib/postgresql/backup")
        if not re.fullmatch(r"[A-Za-z0-9_./:=@+-]+", normalized):
            raise ValueError(f"{label} contains unsupported characters")
        return normalized

    def _docker_read_text(self, path: str) -> str:
        import subprocess

        result = subprocess.run(
            ["docker", "exec", self.deployment.container_name, "cat", path],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            raise FileNotFoundError(result.stderr.strip() or result.stdout.strip() or path)
        return result.stdout

    def _docker_file_size(self, path: str):
        import subprocess

        result = subprocess.run(
            [
                "docker", "exec", self.deployment.container_name,
                "bash", "-lc", f"test -f '{path}' && stat -c %s '{path}'",
            ],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return None
        try:
            return int(result.stdout.strip())
        except ValueError:
            return None

    def _validate_backup(self, target: str) -> str:
        import posixpath
        import subprocess

        try:
            target_path = self._safe_container_path(target, "backup target")
            if target_path.endswith(".json"):
                manifest_path = target_path
                backup_root = posixpath.dirname(target_path)
            else:
                backup_root = target_path
                manifest_path = posixpath.join(target_path, "backup_manifest.json")

            manifest = json.loads(self._docker_read_text(manifest_path))
            backup_root = self._safe_container_path(
                manifest.get("base_backup_path") or backup_root,
                "base backup path",
            )
            archive_dir = self._safe_container_path(
                manifest.get("archive_dir"),
                "archive directory",
            )
            backup_id = str(manifest.get("backup_id") or posixpath.basename(backup_root))

            sandbox_dir = f"/tmp/pg_restore_sandbox/{backup_id}"
            subprocess.run(
                [
                    "docker", "exec", self.deployment.container_name,
                    "bash", "-lc", f"rm -rf '{sandbox_dir}' && mkdir -p '{sandbox_dir}'",
                ],
                capture_output=True, text=True, timeout=15,
            )

            recovery_log = [
                f"restore sandbox initialized at {sandbox_dir}",
                f"loaded backup manifest {manifest_path}",
            ]
            checked_files = []
            base_backup_ok = True
            for item in manifest.get("files", []):
                rel_path = str(item.get("path") or "")
                expected_size = int(item.get("size_bytes") or 0)
                full_path = self._safe_container_path(
                    posixpath.join(backup_root, rel_path),
                    "backup file path",
                )
                actual_size = self._docker_file_size(full_path)
                ok = actual_size == expected_size and expected_size > 0
                checked_files.append({
                    "path": rel_path,
                    "expected_size_bytes": expected_size,
                    "actual_size_bytes": actual_size,
                    "ok": ok,
                })
                if not ok:
                    base_backup_ok = False
            recovery_log.append(
                f"base backup file check {'passed' if base_backup_ok else 'failed'} "
                f"({sum(1 for item in checked_files if item['ok'])}/{len(checked_files)} files)"
            )

            missing_segments = []
            previous_end_time = manifest.get("backup_stop_time")
            wal_chain = sorted(
                manifest.get("wal_chain", []),
                key=lambda item: int(item.get("sequence", 0)),
            )
            for segment in wal_chain:
                wal_file = str(segment.get("wal_file") or "")
                wal_path = self._safe_container_path(
                    posixpath.join(archive_dir, wal_file),
                    "archive WAL path",
                )
                size = self._docker_file_size(wal_path)
                if size is None or size <= 0:
                    missing_segments.append({
                        "wal_file": wal_file,
                        "sequence": int(segment.get("sequence") or 0),
                        "start_time": segment.get("start_time"),
                        "end_time": segment.get("end_time"),
                        "path": wal_path,
                    })
                    break
                recovery_log.append(
                    f"replayed archived WAL {wal_file} through {segment.get('end_time')}"
                )
                previous_end_time = segment.get("end_time") or previous_end_time

            archive_chain_ok = not missing_segments
            requested_target_time = manifest.get("requested_recovery_target_time")
            latest_recoverable_time = (
                previous_end_time
                or manifest.get("latest_recoverable_time")
                or manifest.get("backup_stop_time")
            )
            if missing_segments:
                first_missing = missing_segments[0]
                recovery_log.append(
                    "archive gap detected: missing "
                    f"{first_missing['wal_file']} covering "
                    f"{first_missing.get('start_time')}..{first_missing.get('end_time')}"
                )
                recovery_log.append(
                    f"recovery cannot proceed past {latest_recoverable_time}; "
                    f"requested target was {requested_target_time}"
                )
            else:
                recovery_log.append(
                    f"archive chain is continuous through requested target {requested_target_time}"
                )

            return json.dumps({
                "status": "success",
                "action": "validate_backup",
                "backup_id": backup_id,
                "backup_path": backup_root,
                "manifest_path": manifest_path,
                "archive_dir": archive_dir,
                "validation_status": "passed" if base_backup_ok and archive_chain_ok else "failed",
                "base_backup_ok": base_backup_ok,
                "archive_chain_ok": archive_chain_ok,
                "recoverable": bool(base_backup_ok and archive_chain_ok),
                "checked_files": checked_files,
                "missing_wal_segments": missing_segments,
                "latest_recoverable_time": latest_recoverable_time,
                "requested_recovery_target_time": requested_target_time,
                "recovery_log": recovery_log,
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "action": "validate_backup",
                "error": str(e),
            }, ensure_ascii=False)

    def _pg_log_size(self) -> int:
        return sum(self._pg_log_snapshot().values())

    def _pg_log_snapshot(self) -> dict[str, int]:
        snapshot = self.deployment.postgres_log_sizes()
        if not snapshot:
            raise RuntimeError(
                f"PostgreSQL log snapshot is empty: container={self.deployment.container_name!r}"
            )
        return snapshot

    def _reset_pg_log_visibility(self) -> None:
        self._pg_log_visible_offsets = self._pg_log_snapshot()

    def _read_visible_pg_log(self) -> str:
        output, offsets = self.deployment.read_postgres_logs_after(self._pg_log_visible_offsets)
        self._pg_log_visible_offsets = offsets
        return output.strip()

    @Tool(
        description="读取系统、数据库日志或当前 Case 声明的冻结 operation event 记录",
        arg_descriptions={
            "log_type": "日志类型，可选值: dmesg, docker_logs, pg_log, operation_event；operation_event 必须同时提供 start_timestamp 与 end_timestamp",
            "lines": "返回行数/记录数上限；operation_event 只支持此分页上限，不支持 start_line/end_line/match_key",
            "start_line": "1-based 起始行号；仅文本日志可用，operation_event 禁止使用",
            "end_line": "1-based 结束行号；仅文本日志可用，operation_event 禁止使用",
            "match_key": "文本日志关键字；operation_event 禁止使用，应改用 filters",
            "start_timestamp": "冻结历史窗口起点；必须与 end_timestamp 一起提供（operation_event 必填）",
            "end_timestamp": "冻结历史窗口终点；必须与 start_timestamp 一起提供（operation_event 必填）",
            "target": "可选的冻结历史记录目标；不传时覆盖 Case 中该来源的所有目标",
            "filters": "可选的冻结历史字段过滤条件；仅适用于 operation_event",
        },
    )
    def read_log(
        self,
        log_type: str,
        lines: int = 100,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        match_key: Optional[str] = None,
        start_timestamp: Optional[str] = None,
        end_timestamp: Optional[str] = None,
        target: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        import subprocess
        container_name = self.deployment.container_name
        try:
            if (start_timestamp is None) != (end_timestamp is None):
                raise ValueError("read_log.start_timestamp and read_log.end_timestamp must be provided together")
            if start_timestamp is not None:
                history_limit = int(lines)
                if history_limit <= 0:
                    raise ValueError(f"Historical log line limit must be positive: lines={lines!r}")
                source = {
                    "pg_log": HistoricalRecordSource.COMPONENT_LOG,
                    "operation_event": HistoricalRecordSource.OPERATION_EVENT,
                }.get(log_type)
                if source is None:
                    raise ValueError(
                        "Frozen PostgreSQL log windows support log_type='pg_log' or 'operation_event'"
                    )
                if log_type == "pg_log" and filters:
                    raise ValueError("read_log.filters is supported only for operation_event")
                if log_type == "operation_event" and (start_line is not None or end_line is not None or match_key is not None):
                    raise ValueError(
                        "operation_event returns structured records and does not support line slicing or match_key"
                    )
                result = self._query_frozen_history_records(
                    source=source,
                    start_timestamp=start_timestamp,
                    end_timestamp=end_timestamp,
                    target=target,
                    filters=filters,
                    limit=min(history_limit, int(getattr(self._case.frozen_history, "max_history_records_per_response", 200))),
                )
                if log_type == "operation_event":
                    return json.dumps({"log_type": log_type, **result}, ensure_ascii=False, separators=(",", ":"), default=str)
                records = result["records"]
                content = "\n".join(f"{record['timestamp']} {record.get('message', '')}" for record in records)
                page = self._slice_log_output(content, lines, start_line, end_line, match_key)
                return json.dumps({
                    "status": "success",
                    "log_type": log_type,
                    "window": result["window"],
                    "coverage": result["coverage"],
                    "truncated": result["truncated"],
                    **page,
                }, ensure_ascii=False)
            if log_type == "operation_event":
                raise ValueError("operation_event requires start_timestamp and end_timestamp")
            controller = getattr(self, "_rpo_controller", None)
            if controller is not None:
                delegated = controller.read_log(log_type)
                if delegated is not None:
                    return delegated
            if log_type == "dmesg":
                result = subprocess.run(
                    ["dmesg"], capture_output=True, text=True, timeout=10
                )
                output = result.stdout.strip()
                page = self._slice_log_output(output, lines, start_line, end_line, match_key)
                if not page["content"]:
                    page["content"] = f"(no log entries matched match_key: {match_key})" if match_key else "(no kernel log entries available)"
                return json.dumps({"status": "success", "log_type": "dmesg", **page}, ensure_ascii=False)

            elif log_type == "docker_logs":
                result = subprocess.run(
                    ["docker", "logs", container_name],
                    capture_output=True, text=True, timeout=10
                )
                output = (result.stdout + result.stderr).strip()
                page = self._slice_log_output(output, lines, start_line, end_line, match_key)
                if not page["content"]:
                    page["content"] = f"(no log entries matched match_key: {match_key})" if match_key else "(no docker log entries)"
                return json.dumps({"status": "success", "log_type": "docker_logs", **page}, ensure_ascii=False)

            elif log_type == "pg_log":
                output = self._read_visible_pg_log()
                page = self._slice_log_output(output, lines, start_line, end_line, match_key)
                if not page["content"]:
                    page["content"] = f"(no log entries matched match_key: {match_key})" if match_key else "(no PostgreSQL log entries)"
                return json.dumps({"status": "success", "log_type": "pg_log", **page}, ensure_ascii=False)

            else:
                return json.dumps({"status": "error", "error": f"Unknown log_type: {log_type}. Supported: dmesg, docker_logs, pg_log, operation_event"})
        except subprocess.TimeoutExpired:
            return json.dumps({"status": "error", "error": f"Timeout reading {log_type} logs"})
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)})

    def get_deployment(self) -> BaseDeployment:
        """获取部署器引用"""
        return self.deployment

_BR_REFRESH_IDENTITY_REJECTION = (
    "BR binding refresh rejected: the presented authority chain does not verify "
    "against the current control-plane state; no state changed."
)


class _BrRefreshIdentityError(ValueError):
    """Internal: one BR binding refresh identity check failed.

    The message carries internal diagnostic detail (supplied vs expected
    tuples) and must never be surfaced to the agent verbatim; the focused
    runtime replaces it with the uniform rejection text.
    """


class TiDBEnv(BaseEnv):
    """TiDB database semantics and agent tools for one benchmark run."""

    system = DatabaseSystem.TIDB
    CONNECTION_ROUTER_TARGET = "connection-router"
    SQL_TIMEOUT_SECONDS = 35
    BOOTSTRAP_SQL_TIMEOUT_SECONDS = 300
    EXTERNAL_LOG_MAX_LINE_CHARS = 4000
    EXTERNAL_LOG_MAX_CONTENT_CHARS = 24000

    PUBLIC_TOOLS = (
        "query_metrics",
        "execute_sql",
        "manage_cluster",
        "read_log",
        "search_knowledge",
        "help",
        "submit",
        "exit",
    )
    FROZEN_HISTORY_PUBLIC_TOOLS = PUBLIC_TOOLS
    HC04_RESTORE_TOOLS = (
        "inspect_backup_archive",
        "repair_backup_archive",
        "run_isolated_restore",
        "inspect_isolated_restore",
    )
    COMPOSE_SERVICE_LABEL = "container_label_com_docker_compose_service"
    CASE_ONLY_HISTORY_METRICS = CASE_ONLY_METRICS
    RESOURCE_QUERIES = {
        "cpu": ("sum(rate(container_cpu_usage_seconds_total{selector}[10s]))", "cores"),
        "disk_usage": ("sum(container_fs_usage_bytes{selector})", "bytes"),
        "network_io": (
            "sum(rate(container_network_receive_bytes_total{selector}[10s]) + "
            "rate(container_network_transmit_bytes_total{selector}[10s]))",
            "bytes_per_second",
        ),
    }
    TIME_SERIES_METRICS = TIDB_METRIC_CATALOG.metric_names

    def __init__(
        self,
        *,
        run_id: Optional[str] = None,
        workload=None,
        deployment: Optional[BaseDeployment] = None,
        port_base: int = 4000,
        tidb_readiness_timeout_sec: int = 1800,
        warm_tidb_readiness_timeout_sec: int = 300,
        user: str = "root",
        password: str = "",
        dbname: str = "test",
        sample_interval_sec: float = 2.0,
        return_window_seconds: int = 60,
        workload_runner_config: Optional[Dict[str, Any]] = None,
        image_group_key: Optional[str] = None,
        storage_key: Optional[str] = None,
        storage_root: Optional[str] = None,
        enabled_tools: Optional[Sequence[str]] = None,
    ):
        if deployment is None:
            if run_id is None:
                raise ValueError("TiDBEnv requires run_id when deployment is not provided")
            deployment = TiDBDockerDeployment(
                run_id=run_id,
                port_base=port_base,
                storage_key=storage_key,
                storage_root=storage_root,
                image_group_key=image_group_key,
                tidb_readiness_timeout_sec=tidb_readiness_timeout_sec,
                warm_tidb_readiness_timeout_sec=warm_tidb_readiness_timeout_sec,
            )
        elif any(
            value is not None
            for value in (image_group_key, storage_key, storage_root)
        ):
            raise ValueError(
                "TiDBEnv deployment options require the default TiDBDockerDeployment: "
                f"deployment={type(deployment).__name__}, image_group_key={image_group_key!r}, "
                f"storage_key={storage_key!r}, storage_root={storage_root!r}"
            )
        self._sql_connection_surfaces: Dict[str, SqlConnectionSurface] = {}
        super().__init__(
            workload,
            deployment,
            enabled_tools=self.PUBLIC_TOOLS if enabled_tools is None else enabled_tools,
        )
        self.run_id = deployment.run_id
        self.host, self.port = deployment.primary_tidb_endpoint
        self.user = user
        self.password = password
        self.dbname = dbname
        self.sample_interval_sec = sample_interval_sec
        self.return_window_seconds = return_window_seconds
        self.sql_timeout_seconds = 35
        self.workload_runner_config = workload_runner_config or {}
        self._conn = None
        self._secondary_conn = None
        self._secondary_host = None
        self._secondary_port = None
        self._secondary_password = None
        self._replication_endpoint = None
        self._workload_runner = None
        self._connection_routers: Dict[str, TiDBConnectionRouter] = {}
        self._dr_auto_sync_control: TiDBDrAutoSyncControl | None = None
        self._k08_pitr_runtime = None
        self._clock_status_observed = False
        self._connection_router_connections: Dict[int, str] = {}
        self._workload_connection_invalidation_generation = 0
        self._workload_session_setups: Dict[int, dict[str, object]] = {}
        self._connection_router_invalidation_rules: Dict[
            str, tuple[frozenset[str], tuple[str, ...]]
        ] = {}
        self._visible_since = time.time()
        self._metrics_hidden_depth = 0
        self._log_visible_lines: Dict[str, int] = {}
        self._tidb_knowledge_bases: Dict[str, TiDBKnowledgeBase] = {}
        self._import_controller = None
        self._storage_recovery_contract = None
        self._known_store_ids: Dict[str, int] = {}
        self._observed_gc_safepoint: dict[str, object] | None = None
        self._observed_changefeed_diagnostics: dict[tuple[str, str], dict[str, object]] = {}
        self._observed_region_ids: Dict[str, set[int]] = {}
        self._br_backup_runtime: Optional[Dict[str, Any]] = None
        self._br_backup_attempt_no = 0
        self._last_br_backup_result: Optional[Dict[str, Any]] = None
        self._hc04_restore_runtime: Optional[Dict[str, Any]] = None
        self._hc04_restore_attempt_no = 0
        self._k08_pitr_runtime = None
        self._mvcc_recovery_guard: Optional[Dict[str, Any]] = None
        self._case = None
        self._history_sql_archive: FrozenHistoricalSqlArchive | None = None
        if int(sample_interval_sec) != sample_interval_sec or sample_interval_sec <= 0:
            raise ValueError(
                f"TiDB sample_interval_sec must be a positive whole number: sample_interval_sec={sample_interval_sec!r}"
            )
        self._sql_metric_sampler = TiDBSQLMetricSampler(run_id=self.run_id)
        self._pd_metric_sampler = PdMetricSampler(
            deployment=self.deployment,
            run_id=self.run_id,
            sample_interval_sec=int(sample_interval_sec),
        )
        self._metric_service = MetricService(
            catalog=TIDB_METRIC_CATALOG,
            live=LivePrometheusMetricProvider(
                deployment=self.deployment,
                run_id=self.run_id,
                sample_interval_sec=int(sample_interval_sec),
                return_window_seconds=return_window_seconds,
                sql_metric_provider=self._sql_metric_sampler.query,
                pd_metric_provider=self._pd_metric_sampler.query,
                workload_profile_provider=self._capture_workload_profile_metric,
            )
        )
        self._history_timeline: FrozenHistoricalTimeline | None = None
        self._metric_capture_padding_events: list[dict[str, object]] = []

    def metric_history_catalog(self):
        return TIDB_METRIC_CATALOG

    def _case_query_metrics_definition(self) -> dict[str, Any] | None:
        history_spec = getattr(getattr(self, "_case", None), "frozen_history", None)
        if history_spec is None:
            return None
        definition = deepcopy(TIDB_TOOL_DEFINITIONS["query_metrics"])
        static_metrics = {
            item["metric_name"]: item
            for item in definition.get("metric_definitions", [])
        }
        target_scopes = {
            "resource_group_usage": "explicit resource-group name selected by this Case",
            "resource_group_throttle": "explicit resource-group name selected by this Case",
            "transaction_commit": "TiDB endpoint selected by this Case",
            "statistics_state": "SQL-backed table series selected by this Case",
            "plan_cardinality": "SQL digest series selected by this Case",
            "lightning_progress": "the Case Lightning job",
            "lightning_throughput": "the Case Lightning job",
            "lightning_workers": "the Case Lightning job",
            "workload_profile": "the Case frontend workload profiles",
            "pd_region_inventory": "the Case PD cluster Region inventory",
            "pd_region_activity": "the Case PD cluster scheduling activity",
            "pd_leader_distribution": "the Case TiKV leader distribution",
            "ticdc_progress": "the Case changefeed checkpoint and resolved progress",
            "ticdc_sink": "the Case changefeed sink throughput and flush activity",
        }
        metric_definitions = []
        for raw_metric in history_spec.required_metrics:
            metric = str(raw_metric).casefold()
            item = static_metrics.get(metric)
            if item is None:
                item = {
                    "metric_name": metric,
                    "metric_description": "Case-scoped raw historical series.",
                    "target_scope": target_scopes.get(metric, "Case-selected target"),
                }
            metric_definitions.append(item)
        definition["metric_definitions"] = metric_definitions
        for parameter in definition["parameter_definitions"]:
            if parameter["parameter_name"] == "metric_type":
                parameter["allowed_values"] = [
                    str(metric).casefold() for metric in history_spec.required_metrics
                ]
                break
        return definition

    def _configure_tools(self, enabled_tools: Optional[Sequence[str]] = None) -> None:
        super()._configure_tools(enabled_tools)
        metric_definition = self._case_query_metrics_definition()
        if metric_definition is None:
            return
        self._enabled_tool_specs = [
            replace(spec, definition=deepcopy(metric_definition))
            if spec.alias == "query_metrics" and metric_definition is not None
            else spec
            for spec in self._enabled_tool_specs
        ]
        self._alias_to_tool_spec = {
            spec.alias: spec for spec in self._enabled_tool_specs
        }

    def validate_metric_history_case(self, spec, background_workload) -> None:
        spec.validate(background_workload)
        catalog = self.metric_history_catalog()
        for metric in spec.required_metrics:
            catalog.definition(metric)
            normalized_metric = str(metric).casefold()
            selected_targets = spec.metric_targets.get(normalized_metric)
            if normalized_metric == "workload_profile":
                if selected_targets is not None and tuple(selected_targets) != (None,):
                    raise ValueError(
                        "TiDB workload_profile history must capture the Case frontend profiles through target=None: "
                        f"selected_targets={tuple(selected_targets)!r}"
                    )
                targets = (None,)
            else:
                targets = (
                    tuple(selected_targets)
                    if selected_targets is not None
                    else catalog.target_variants(normalized_metric, self.deployment)
                )
            if not targets or len(set(targets)) != len(targets):
                raise ValueError(
                    "TiDB frozen-history Case target selection must be non-empty and unique: "
                    f"metric={normalized_metric!r}, targets={targets!r}"
                )
            for target in targets:
                catalog.validate_target(normalized_metric, target, self.deployment)
        for decoy in spec.decoys:
            definition = catalog.definition(decoy.metric)
            if decoy.field not in definition.value_fields:
                raise ValueError(
                    f"Frozen-history decoy field is not in catalog: decoy_id={decoy.decoy_id!r}, "
                    f"metric={decoy.metric!r}, field={decoy.field!r}, fields={definition.value_fields!r}"
                )
            if str(decoy.metric).casefold() == "workload_profile":
                frontend_profiles = {
                    profile.name
                    for profile in background_workload.profiles
                    if profile.tier == "FRONTEND_SLO"
                }
                if decoy.target not in frontend_profiles:
                    raise ValueError(
                        "TiDB workload_profile decoy target must be a Case frontend profile: "
                        f"decoy_id={decoy.decoy_id!r}, target={decoy.target!r}, "
                        f"frontend_profiles={sorted(frontend_profiles)!r}"
                    )
            else:
                catalog.validate_target(decoy.metric, decoy.target, self.deployment)
            selected_targets = spec.metric_targets.get(str(decoy.metric).casefold())
            if selected_targets is not None and str(decoy.metric).casefold() != "workload_profile":
                series_targets = {
                    target
                    for target in selected_targets
                    if target is not None
                }
                if decoy.target is not None and decoy.target not in series_targets:
                    raise ValueError(
                        "TiDB frozen-history decoy target is outside the Case target selection: "
                        f"decoy_id={decoy.decoy_id!r}, metric={decoy.metric!r}, target={decoy.target!r}, "
                        f"selected={tuple(selected_targets)!r}"
                    )
        unsupported = set(spec.record_sources) - set(HistoricalRecordSource)
        if unsupported:
            raise ValueError(
                f"TiDB frozen-history history has unsupported record sources: sources={sorted(item.value for item in unsupported)!r}"
            )

    def metric_samples_fresh(self, window_seconds: int = 30) -> bool:
        return self.deployment.prometheus_services_fresh(window_seconds)

    def metric_history_warmup_seconds(self, required_metrics: tuple[str, ...]) -> float:
        spec = getattr(self._case, "frozen_history", None)
        rate_windows = getattr(spec, "metric_rate_windows", {}) if spec is not None else {}
        return max(
            max(
                float(self.metric_history_catalog().definition(metric).lookback_seconds),
                float(rate_windows.get(str(metric).casefold(), 0)),
            )
            for metric in required_metrics
        )

    def configure_case(self, case) -> None:
        history_spec = getattr(case, "frozen_history", None)
        if (
            history_spec is not None
            and "lightning_progress" in tuple(history_spec.required_metrics)
        ):
            # Must be declared before super().configure_case() renders the
            # Prometheus scrape configuration for the deployment.
            self.deployment.enable_lightning_scrape_target(
                f"{lightning_network_alias(self.deployment.run_id)}:8287"
            )
        super().configure_case(case)
        self._case = case
        changefeed_id = getattr(case, "changefeed_id", None)
        self.deployment.metric_changefeed_target = (
            f"changefeed/{changefeed_id}" if changefeed_id is not None else None
        )
        if history_spec is not None:
            self.validate_metric_history_case(history_spec, case.background_workload)
            self._configure_tools(self.FROZEN_HISTORY_PUBLIC_TOOLS)

    def configure_runtime(self, runtime: TiDBCaseRuntime) -> None:
        if not isinstance(runtime, TiDBCaseRuntime):
            raise TypeError(
                f"TiDBEnv requires TiDBCaseRuntime, got {type(runtime).__name__}"
            )
        self.deployment.configure_runtime(runtime)
        self.sql_timeout_seconds = runtime.sql_timeout_seconds
        self.host, self.port = self.deployment.primary_tidb_endpoint

    def configure_history_observability(self, spec) -> None:
        """Configure the real TiDB statement summary before frozen-history capture."""
        connection = self._ensure_connection()
        statements = (
            "SET GLOBAL tidb_enable_stmt_summary = 1",
            "SET GLOBAL tidb_stmt_summary_refresh_interval = 30",
            "SET GLOBAL tidb_stmt_summary_history_size = 60",
            "SET GLOBAL tidb_stmt_summary_max_stmt_count = 10000",
        )
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
        sql_metrics = tuple(
            str(metric).casefold()
            for metric in spec.required_metrics
            if str(metric).casefold() in SQL_BACKED_METRICS
        )
        if sql_metrics:
            contract = getattr(self._case, "metric_history_adapter_config", None)
            if contract is None:
                raise RuntimeError(
                    "TiDB SQL-backed metric history requires metric_history_adapter_config: "
                    f"run_id={self.run_id!r}, case={getattr(self._case, 'case_id', None)!r}, metrics={sql_metrics!r}"
                )
            if "statistics_state" in sql_metrics:
                self._wait_statistics_meta_ready(contract)
            self._sql_metric_sampler.configure(
                metrics=sql_metrics,
                step_seconds=spec.base_step_seconds,
                contract=contract,
                connection_factory=lambda application_name: self._connect(
                    self.dbname,
                    application_name=application_name,
                ),
            )
            self._sql_metric_sampler.start()
        if {
            "pd_region_inventory",
            "pd_region_activity",
            "pd_leader_distribution",
        }.intersection(str(metric).casefold() for metric in spec.required_metrics):
            self._pd_metric_sampler.start()

    def _wait_statistics_meta_ready(self, contract: Mapping[str, object]) -> None:
        """Block until every contract table has an ANALYZE row in SHOW STATS_META.

        The SQL metric sampler asserts a stats-meta row per contract table on
        every step; ANALYZE in the workload kit publishes that row
        asynchronously, so wait here rather than failing the first sample.
        """
        database = str(contract["database"])
        tables = tuple(str(item) for item in contract["tables"])
        deadline = time.monotonic() + 120
        missing: tuple[str, ...] = tables
        while True:
            connection = self._ensure_connection()
            with connection.cursor() as cursor:
                present = set()
                for table in tables:
                    cursor.execute(
                        "SHOW STATS_META WHERE Db_name=%s AND Table_name=%s",
                        (database, table),
                    )
                    if cursor.fetchall():
                        present.add(table)
            missing = tuple(table for table in tables if table not in present)
            if not missing:
                return
            if time.monotonic() > deadline:
                raise RuntimeError(
                    "TiDB statistics metadata was not published before frozen-history capture: "
                    f"run_id={self.run_id!r}, database={database!r}, missing_tables={missing!r}"
                )
            time.sleep(2)

    def capture_metric_history(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
        *,
        metric_targets: Mapping[str, tuple[str | None, ...]] | None = None,
        rate_windows: Mapping[str, int] | None = None,
    ) -> tuple:
        if start_epoch_ms >= end_epoch_ms:
            raise ValueError(
                "TiDB metric capture window must be positive: "
                f"run_id={self.run_id!r}, start_epoch_ms={start_epoch_ms}, end_epoch_ms={end_epoch_ms}"
            )
        if step_seconds <= 0 or (end_epoch_ms - start_epoch_ms) % (step_seconds * 1000):
            raise ValueError(
                "TiDB metric capture window must align to a positive step: "
                f"run_id={self.run_id!r}, start_epoch_ms={start_epoch_ms}, "
                f"end_epoch_ms={end_epoch_ms}, step_seconds={step_seconds}"
            )
        self._sql_metric_sampler.raise_if_failed()
        expected_timestamps = tuple(
            range(start_epoch_ms, end_epoch_ms + 1, step_seconds * 1000)
        )
        controller = self._import_controller
        frames: list[MetricFrame] = []
        lightning_metrics = {
            "lightning_progress",
            "lightning_throughput",
            "lightning_workers",
        }
        for raw_metric in metrics:
            metric = str(raw_metric).casefold()
            definition = self.metric_history_catalog().definition(metric)
            selected_targets = (
                metric_targets.get(metric)
                if metric_targets is not None
                else None
            )
            if metric == "workload_profile":
                targets = (None,)
            elif metric in lightning_metrics:
                job_target = lightning_job_id(self.run_id)
                if selected_targets is None or tuple(selected_targets) == (None,):
                    targets = (job_target,)
                elif tuple(selected_targets) == (job_target,):
                    targets = (job_target,)
                else:
                    raise ValueError(
                        "TiDB frozen-history Lightning capture requires one Case job target: "
                        f"metric={metric!r}, selected_targets={tuple(selected_targets)!r}, "
                        f"expected={job_target!r}"
                    )
            else:
                targets = (
                    tuple(selected_targets)
                    if selected_targets is not None
                    else self.metric_history_catalog().target_variants(metric, self.deployment)
                )
            if not targets or len(set(targets)) != len(targets):
                raise ValueError(
                    "TiDB metric capture target selection must be non-empty and unique: "
                    f"run_id={self.run_id!r}, metric={metric!r}, targets={targets!r}"
                )
            for target in targets:
                is_lightning = metric in lightning_metrics
                if (
                    is_lightning
                    and controller is not None
                    and controller.phase == "ready_to_import"
                ):
                    frame = MetricFrame(
                        metric=metric,
                        query_target=target,
                        step_seconds=step_seconds,
                        series={target: {
                            field: tuple(0.0 for _ in expected_timestamps)
                            for field in definition.value_fields
                        }},
                        timestamps_ms={target: expected_timestamps},
                    )
                else:
                    frame = self._metric_service.live.query(MetricQuery(
                        metric=metric,
                        target=target,
                        start_epoch_ms=start_epoch_ms,
                        end_epoch_ms=end_epoch_ms,
                        step_seconds=step_seconds,
                        rate_window_seconds=(
                            rate_windows.get(metric)
                            if rate_windows is not None
                            else None
                        ),
                    ))
                    if (
                        is_lightning
                        and controller is not None
                        and controller.phase == "reconfigure_required"
                    ):
                        frame = self._pad_stopped_lightning_frame(
                            frame,
                            expected_timestamps,
                            run_id=self.run_id,
                            metric=metric,
                            query_target=target,
                        )
                frame = self._align_metric_capture_to_grid(
                    frame,
                    expected_timestamps,
                    run_id=self.run_id,
                    metric=metric,
                    query_target=target,
                )
                validate_metric_frame(frame, self.metric_history_catalog())
                if is_lightning:
                    # 冻结历史报错会逐字枚举帧级 target；帧挂 job id 等于把事故身份
                    # 递给任何一次失败查询。事故与诱饵的判别只能在 series 层做。
                    frame = replace(frame, query_target=None)
                frames.append(frame)
        return tuple(frames)

    @staticmethod
    def _pad_stopped_lightning_frame(
        frame: MetricFrame,
        expected_timestamps: tuple[int, ...],
        *,
        run_id: str,
        metric: str,
        query_target: str | None,
    ) -> MetricFrame:
        if len(frame.series) != 1:
            raise RuntimeError(
                "Stopped Lightning metric must contain exactly one series: "
                f"run_id={run_id!r}, metric={metric!r}, query_target={query_target!r}, "
                f"series={tuple(frame.series)!r}"
            )
        series_target, observed_fields = next(iter(frame.series.items()))
        observed_timestamps = frame.timestamps_ms[series_target]
        if not observed_timestamps:
            raise RuntimeError(
                "Stopped Lightning metric has no observed samples before handoff: "
                f"run_id={run_id!r}, metric={metric!r}, query_target={query_target!r}"
            )
        expected_index = {timestamp: index for index, timestamp in enumerate(expected_timestamps)}
        if any(timestamp not in expected_index for timestamp in observed_timestamps):
            raise RuntimeError(
                "Stopped Lightning metric contains a sample outside the capture grid: "
                f"run_id={run_id!r}, metric={metric!r}, query_target={query_target!r}, "
                f"observed_timestamps={observed_timestamps!r}, expected_timestamps={expected_timestamps!r}"
            )
        first_index = expected_index[observed_timestamps[0]]
        last_index = expected_index[observed_timestamps[-1]]
        expected_observed = expected_timestamps[first_index:last_index + 1]
        if observed_timestamps != expected_observed:
            raise RuntimeError(
                "Stopped Lightning metric has a gap while the container was observable: "
                f"run_id={run_id!r}, metric={metric!r}, query_target={query_target!r}, "
                f"observed_timestamps={observed_timestamps!r}, expected_observed={expected_observed!r}"
            )
        padded_fields = {
            field: tuple(
                0.0 if index < first_index or index > last_index
                else values[index - first_index]
                for index, _ in enumerate(expected_timestamps)
            )
            for field, values in observed_fields.items()
        }
        return MetricFrame(
            metric=frame.metric,
            query_target=frame.query_target,
            step_seconds=frame.step_seconds,
            series={series_target: padded_fields},
            timestamps_ms={series_target: expected_timestamps},
        )

    @staticmethod
    def _metric_capture_tolerance_ms(step_seconds: int) -> int:
        """A sample may land at most 4 grid steps (never below 10s) away from its slot."""
        return max(4 * step_seconds, 10) * 1000

    def _align_metric_capture_to_grid(
        self,
        frame: MetricFrame,
        expected_timestamps: tuple[int, ...],
        *,
        run_id: str,
        metric: str,
        query_target: str | None,
    ) -> MetricFrame:
        if all(
            timestamps == expected_timestamps
            for timestamps in frame.timestamps_ms.values()
        ):
            return frame
        step_ms = frame.step_seconds * 1000
        tolerance_ms = self._metric_capture_tolerance_ms(frame.step_seconds)
        grid_start_ms = expected_timestamps[0]
        aligned_series: dict[str, dict[str, tuple[float, ...]]] = {}
        aligned_timestamps: dict[str, tuple[int, ...]] = {}
        for series_target, observed_timestamps in frame.timestamps_ms.items():
            if observed_timestamps == expected_timestamps:
                aligned_series[series_target] = dict(frame.series[series_target])
                aligned_timestamps[series_target] = expected_timestamps
                continue
            if not observed_timestamps:
                raise RuntimeError(
                    "TiDB metric capture series has no observed samples: "
                    f"run_id={run_id!r}, metric={metric!r}, query_target={query_target!r}, "
                    f"series_target={series_target!r}, expected_timestamps={expected_timestamps!r}"
                )
            # One Prometheus-side scrape outage produces the same gap run
            # in every series at once, so each series carries its own
            # strike budget: a correlated outage counts once per series
            # instead of multiplying into a shared counter, and only
            # sustained degradation of one series fails the frame.
            strikes = SamplerGridStrikes()
            # Anchor every sample to its nearest grid slot. A sample beyond the
            # slot tolerance is skipped like a missed sample, and two candidates
            # for one slot keep the closer one — both count toward the shared
            # strike budget instead of failing the frame outright.
            assignments: dict[int, int] = {}
            skipped_samples = 0
            max_deviation_ms = 0
            for observed_index, timestamp in enumerate(observed_timestamps):
                raw_offset = round((timestamp - grid_start_ms) / step_ms)
                nearest_index = min(max(raw_offset, 0), len(expected_timestamps) - 1)
                deviation_ms = abs(timestamp - expected_timestamps[nearest_index])
                if deviation_ms > tolerance_ms:
                    skipped_samples += 1
                    continue
                if nearest_index in assignments:
                    incumbent_index, incumbent_deviation = assignments[nearest_index]
                    if deviation_ms < incumbent_deviation:
                        assignments[nearest_index] = observed_index
                        skipped_samples += 1
                    continue
                assignments[nearest_index] = observed_index
                max_deviation_ms = max(max_deviation_ms, deviation_ms)
            observed_fields = frame.series[series_target]
            gap_indices = [index for index in range(len(expected_timestamps)) if index not in assignments]
            if gap_indices:
                started_at_ms = self._restart_padded_target_started_at_ms(
                    series_target,
                    grid_start_ms,
                    expected_timestamps[-1],
                )
                # Contiguous missing-slot runs are one anomaly event each; a
                # stretch of at least SAMPLER_LAG_TOLERANCE_INTERVALS anchored
                # slots between events decays the count. Jitter padding fills
                # the skipped slots with 0.0; restart-explained padding keeps
                # its own provenance and does not strike.
                strike_detail = (
                    f"run_id={run_id!r}, metric={metric!r}, query_target={query_target!r}, "
                    f"series_target={series_target!r}, tolerance_ms={tolerance_ms}, "
                    f"skipped_samples={skipped_samples}"
                )
                anchored_run = 0
                gap_lookup = set(gap_indices)
                for index in range(len(expected_timestamps)):
                    if index in gap_lookup:
                        if anchored_run >= SAMPLER_LAG_TOLERANCE_INTERVALS:
                            strikes.decay()
                        anchored_run = 0
                        continue
                    anchored_run += 1
                for gap_run in self._contiguous_index_runs(gap_indices):
                    if started_at_ms is None:
                        strikes.strike(detail=strike_detail)
                        self._record_metric_capture_padding(
                            run_id=run_id,
                            metric=metric,
                            query_target=query_target,
                            series_target=series_target,
                            padded_timestamps_ms=tuple(
                                expected_timestamps[index] for index in gap_run
                            ),
                            container_started_at_ms=None,
                            max_reanchor_deviation_ms=max_deviation_ms,
                            reason="jitter",
                        )
                aligned_series[series_target] = {
                    field: tuple(
                        values[assignments[index]] if index in assignments else 0.0
                        for index in range(len(expected_timestamps))
                    )
                    for field, values in observed_fields.items()
                }
                aligned_timestamps[series_target] = expected_timestamps
                if started_at_ms is not None:
                    self._record_metric_capture_padding(
                        run_id=run_id,
                        metric=metric,
                        query_target=query_target,
                        series_target=series_target,
                        padded_timestamps_ms=tuple(
                            expected_timestamps[index] for index in gap_indices
                        ),
                        container_started_at_ms=started_at_ms,
                        max_reanchor_deviation_ms=max_deviation_ms,
                        reason="restart",
                    )
                continue
            aligned_series[series_target] = {
                field: tuple(values[assignments[index]] for index in range(len(expected_timestamps)))
                for field, values in observed_fields.items()
            }
            aligned_timestamps[series_target] = expected_timestamps
        return MetricFrame(
            metric=frame.metric,
            query_target=frame.query_target,
            step_seconds=frame.step_seconds,
            series=aligned_series,
            timestamps_ms=aligned_timestamps,
        )

    @staticmethod
    def _contiguous_index_runs(indices: list[int]) -> list[list[int]]:
        runs: list[list[int]] = []
        for index in indices:
            if runs and index == runs[-1][-1] + 1:
                runs[-1].append(index)
            else:
                runs.append([index])
        return runs

    def _restart_padded_target_started_at_ms(
        self,
        series_target: str,
        window_start_ms: int,
        window_end_ms: int,
    ) -> int | None:
        """Return when the target container last started if that start happened inside the window."""
        if series_target not in self.deployment.NODES:
            return None
        service = self.deployment.NODES[series_target]
        container_id = self.deployment._service_container_id(service)
        inspect = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.StartedAt}}", container_id],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if inspect.returncode != 0:
            raise RuntimeError(
                "TiDB metric capture could not read the container start time for restart padding: "
                f"series_target={series_target!r}, container_id={container_id!r}, "
                f"returncode={inspect.returncode}, stderr={inspect.stderr.strip()!r}"
            )
        started_at_ms = self._parse_docker_started_at_ms(inspect.stdout)
        if window_start_ms < started_at_ms <= window_end_ms:
            return started_at_ms
        return None

    @staticmethod
    def _parse_docker_started_at_ms(value: str) -> int:
        match = re.fullmatch(
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?Z",
            value.strip(),
        )
        if match is None:
            raise RuntimeError(
                f"Docker inspect returned an unparsable UTC StartedAt: value={value!r}"
            )
        started_at = datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        milliseconds = int((match.group(2) or "").ljust(3, "0")[:3] or 0)
        return int(started_at.timestamp()) * 1000 + milliseconds

    def _record_metric_capture_padding(
        self,
        *,
        run_id: str,
        metric: str,
        query_target: str | None,
        series_target: str,
        padded_timestamps_ms: tuple[int, ...],
        container_started_at_ms: int | None,
        max_reanchor_deviation_ms: int,
        reason: str,
    ) -> None:
        event = {
            "run_id": run_id,
            "metric": metric,
            "query_target": query_target,
            "series_target": series_target,
            "padded_timestamps_ms": padded_timestamps_ms,
            "fill_value": 0.0,
            "container_started_at_ms": container_started_at_ms,
            "max_reanchor_deviation_ms": max_reanchor_deviation_ms,
            "reason": reason,
        }
        self._metric_capture_padding_events.append(event)
        print(
            f">>> [TiDBEnv] Padded {len(padded_timestamps_ms)} restart-gap sample(s) with 0.0 for "
            f"{metric!r}/{series_target!r}: padded_timestamps_ms={padded_timestamps_ms!r}, "
            f"container_started_at_ms={container_started_at_ms}"
        )

    @property
    def metric_capture_padding_events(self) -> tuple[dict[str, object], ...]:
        """Deterministic restart-padding metadata recorded during metric capture."""
        return tuple(self._metric_capture_padding_events)


    def finalize_metric_history_capture(self, start_epoch_ms: int, end_epoch_ms: int) -> None:
        controller = self._import_controller
        if controller is not None:
            status = controller.status()
            if status["import"]["state"] != "reconfigure_required":
                raise RuntimeError(
                    "TiDB frozen-history Lightning target capture did not finish at checkpoint handoff: "
                    f"run_id={self.run_id!r}, start_epoch_ms={start_epoch_ms}, "
                    f"end_epoch_ms={end_epoch_ms}, status={status!r}"
                )
        self._sql_metric_sampler.stop()
        self._sql_metric_sampler.raise_if_failed()
        self._pd_metric_sampler.stop()

    def _capture_workload_profile_metric(self, query: MetricQuery) -> MetricFrame:
        runner = self._workload_runner
        if runner is None:
            raise RuntimeError(
                f"TiDB workload_profile history requires an attached WorkloadRunner: run_id={self.run_id!r}"
            )
        spec = self._case.frozen_history
        selected = spec.metric_targets.get("workload_profile")
        if selected is not None and tuple(selected) != (None,):
            raise ValueError(
                "TiDB workload_profile capture only accepts target=None and uses the Case frontend profiles: "
                f"selected_targets={tuple(selected)!r}"
            )
        profile_names = tuple(
            profile.name
            for profile in self._case.background_workload.profiles
            if profile.tier == "FRONTEND_SLO"
        )
        if query.start_epoch_ms is None or query.end_epoch_ms is None:
            raise ValueError(
                f"TiDB workload_profile history requires an explicit capture window: query={query!r}"
            )
        return runner.capture_profile_metric(
            start_epoch_ms=query.start_epoch_ms,
            end_epoch_ms=query.end_epoch_ms,
            step_seconds=query.step_seconds or spec.base_step_seconds,
            profile_names=profile_names,
        )

    def capture_history_records(
        self,
        sources: tuple[HistoricalRecordSource, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
    ) -> CapturedRecords:
        point_records = []
        interval_records = []
        coverage = []
        if HistoricalRecordSource.COMPONENT_LOG in sources:
            for target in self.deployment.list_nodes():
                if target.startswith("monitoring/"):
                    continue
                raw = self.deployment.read_logs_at_range(target, start_epoch_ms, end_epoch_ms)
                point_records.extend(parse_docker_log_records(raw, target, start_epoch_ms, end_epoch_ms))
                coverage.append(HistoricalCoverage(
                    source=HistoricalRecordSource.COMPONENT_LOG,
                    target=target,
                    start_ms=start_epoch_ms,
                    end_ms=end_epoch_ms,
                ))
            controller = self._import_controller
            if controller is not None:
                raw = controller.history_log_output(start_epoch_ms, end_epoch_ms)
                if raw is None:
                    raise RuntimeError(
                        f"Lightning controller did not provide history logs: run_id={self.run_id!r}, "
                        f"window=({start_epoch_ms},{end_epoch_ms})"
                    )
                target = "lightning/lightning-0"
                point_records.extend(
                    parse_docker_log_records(raw, target, start_epoch_ms, end_epoch_ms)
                )
                coverage.append(HistoricalCoverage(
                    source=HistoricalRecordSource.COMPONENT_LOG,
                    target=target,
                    start_ms=start_epoch_ms,
                    end_ms=end_epoch_ms,
                ))
        if HistoricalRecordSource.TOPSQL in sources:
            rows = self._query_rows(
                "SELECT INSTANCE, RESOURCE_GROUP, DIGEST, PLAN_DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY, "
                "AVG_TOTAL_KEYS, AVG_PROCESSED_KEYS, AVG_MEM, MAX_MEM, AVG_DISK, MAX_DISK, "
                "SUMMARY_BEGIN_TIME, SUMMARY_END_TIME "
                "FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY_HISTORY "
                "WHERE SUMMARY_END_TIME >= FROM_UNIXTIME(%s) AND SUMMARY_BEGIN_TIME <= FROM_UNIXTIME(%s) "
                "UNION ALL "
                "SELECT INSTANCE, RESOURCE_GROUP, DIGEST, PLAN_DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY, "
                "AVG_TOTAL_KEYS, AVG_PROCESSED_KEYS, AVG_MEM, MAX_MEM, AVG_DISK, MAX_DISK, "
                "SUMMARY_BEGIN_TIME, SUMMARY_END_TIME "
                "FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY "
                "WHERE SUMMARY_END_TIME >= FROM_UNIXTIME(%s) AND SUMMARY_BEGIN_TIME <= FROM_UNIXTIME(%s)",
                (start_epoch_ms / 1000, end_epoch_ms / 1000, start_epoch_ms / 1000, end_epoch_ms / 1000),
            )
            interval_records.extend(build_topsql_records(rows, "cluster", start_epoch_ms, end_epoch_ms))
            coverage.append(HistoricalCoverage(
                source=HistoricalRecordSource.TOPSQL,
                target="cluster",
                start_ms=start_epoch_ms,
                end_ms=end_epoch_ms,
            ))
        if HistoricalRecordSource.SLOW_QUERIES in sources:
            rows = self._query_rows(
                "SELECT TIME, INSTANCE, DIGEST, QUERY, QUERY_TIME, PROCESS_TIME, WAIT_TIME, BACKOFF_TIME, "
                "TOTAL_KEYS, PROCESS_KEYS, MEM_MAX, DISK_MAX "
                "FROM INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY "
                "WHERE TIME BETWEEN FROM_UNIXTIME(%s) AND FROM_UNIXTIME(%s)",
                (start_epoch_ms / 1000, end_epoch_ms / 1000),
            )
            point_records.extend(build_slow_query_records(rows, "cluster", start_epoch_ms, end_epoch_ms))
            coverage.append(HistoricalCoverage(
                source=HistoricalRecordSource.SLOW_QUERIES,
                target="cluster",
                start_ms=start_epoch_ms,
                end_ms=end_epoch_ms,
            ))
        return CapturedRecords(
            point_records=tuple(point_records),
            interval_records=tuple(interval_records),
            coverage=tuple(coverage),
        )

    def register_sql_connection_surface(
        self,
        name: str,
        *,
        database: str,
        description: str,
        query_examples: Sequence[str],
        write_policy: str = "unrestricted",
    ) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ValueError(f"Invalid SQL connection surface name: name={name!r}")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", database):
            raise ValueError(
                f"Invalid SQL connection surface database: name={name!r}, database={database!r}"
            )
        if not description.strip():
            raise ValueError(f"SQL connection surface description is empty: name={name!r}")
        examples = tuple(query_examples)
        if not examples or any(not example.strip() for example in examples):
            raise ValueError(
                f"SQL connection surface requires non-empty query examples: name={name!r}"
            )
        if write_policy not in {"unrestricted", "dm_action", "read_only"}:
            raise ValueError(
                f"Unsupported SQL connection surface write policy: name={name!r}, "
                f"write_policy={write_policy!r}"
            )
        if name in {"primary", "replica", "downstream"} or name in self.deployment.tidb_endpoints:
            raise ValueError(f"SQL connection surface name is reserved: name={name!r}")
        surface = SqlConnectionSurface(
            name=name,
            database=database,
            description=description,
            query_examples=examples,
            write_policy=write_policy,
        )
        existing = self._sql_connection_surfaces.get(name)
        if existing is not None and existing != surface:
            raise RuntimeError(
                f"SQL connection surface registration conflicts: name={name!r}, "
                f"existing={existing!r}, requested={surface!r}"
            )
        self._sql_connection_surfaces[name] = surface

    @staticmethod
    def _sql_mutation_candidate(sql_query: str) -> bool:
        return bool(re.search(
            r"(?:^|;)\s*(?:ALTER|CREATE|DROP|TRUNCATE|INSERT|UPDATE|DELETE|REPLACE|MERGE|CALL|GRANT|REVOKE|WITH)\b",
            sql_query,
            re.IGNORECASE,
        ))

    @staticmethod
    def _is_read_only_sql_statement(statement: exp.Expression) -> bool:
        return statement.key in {"select", "show", "describe", "explain"}

    @staticmethod
    def _is_dm_action_insert(statement: exp.Expression) -> bool:
        if not isinstance(statement, exp.Insert):
            return False
        target = statement.this.this if isinstance(statement.this, exp.Schema) else statement.this
        if not isinstance(target, exp.Table):
            return False
        return target.name.casefold() == "dm_actions" and (
            not target.db or target.db.casefold() == "dm_control"
        )

    @classmethod
    def _validate_sql_write_policy(
        cls,
        sql_query: str,
        *,
        surface: SqlConnectionSurface,
        allow_action_insert: bool,
    ) -> None:
        if not cls._sql_mutation_candidate(sql_query):
            return
        try:
            statements = parse(sql_query, read="mysql")
        except ParseError as exc:
            raise ValueError(
                f"SQL write-policy validation could not parse query: "
                f"surface={surface.name!r}, query={sql_query!r}, error={exc}"
            ) from exc
        if not statements:
            raise ValueError(
                f"SQL write-policy validation found no statement: surface={surface.name!r}, "
                f"query={sql_query!r}"
            )
        if all(cls._is_read_only_sql_statement(statement) for statement in statements):
            return
        if allow_action_insert and len(statements) == 1 and cls._is_dm_action_insert(statements[0]):
            return
        raise ValueError(
            f"SQL write policy rejected mutation: surface={surface.name!r}, "
            f"write_policy={surface.write_policy!r}; only a single INSERT INTO dm_actions "
            "is writable"
        )

    @classmethod
    def _validate_registered_sql_write_policies(
        cls,
        sql_query: str,
        *,
        selected_target: str,
        surfaces: Dict[str, SqlConnectionSurface],
    ) -> None:
        selected_surface = surfaces.get(selected_target)
        if selected_surface is not None and selected_surface.write_policy != "unrestricted":
            cls._validate_sql_write_policy(
                sql_query,
                surface=selected_surface,
                allow_action_insert=True,
            )
        for surface in surfaces.values():
            if surface.write_policy == "unrestricted" or surface is selected_surface:
                continue
            database_pattern = rf"(?:`{re.escape(surface.database)}`|{re.escape(surface.database)})\s*\."
            use_pattern = rf"\bUSE\s+(?:`{re.escape(surface.database)}`|{re.escape(surface.database)})\b"
            database_ddl_pattern = (
                rf"\b(?:ALTER|CREATE|DROP)\s+(?:DATABASE|SCHEMA)\s+"
                rf"(?:IF\s+(?:NOT\s+)?EXISTS\s+)?"
                rf"(?:`{re.escape(surface.database)}`|{re.escape(surface.database)})\b"
            )
            if (
                re.search(database_pattern, sql_query, re.IGNORECASE)
                or re.search(use_pattern, sql_query, re.IGNORECASE)
                or re.search(database_ddl_pattern, sql_query, re.IGNORECASE)
            ):
                cls._validate_sql_write_policy(
                    sql_query,
                    surface=surface,
                    allow_action_insert=False,
                )

    def unregister_sql_connection_surface(self, name: str) -> None:
        if name not in self._sql_connection_surfaces:
            raise ValueError(f"SQL connection surface is not registered: name={name!r}")
        del self._sql_connection_surfaces[name]

    def set_sql_connection_surface_write_policy(self, name: str, write_policy: str) -> None:
        if name not in self._sql_connection_surfaces:
            raise ValueError(f"SQL connection surface is not registered: name={name!r}")
        if write_policy not in {"unrestricted", "dm_action", "read_only"}:
            raise ValueError(
                f"Unsupported SQL connection surface write policy: name={name!r}, "
                f"write_policy={write_policy!r}"
            )
        surface = self._sql_connection_surfaces[name]
        self._sql_connection_surfaces[name] = SqlConnectionSurface(
            name=surface.name,
            database=surface.database,
            description=surface.description,
            query_examples=surface.query_examples,
            write_policy=write_policy,
        )

    def _sql_connection_surface_help(self) -> list[dict[str, Any]]:
        surfaces = [
            {
                "name": "primary",
                "kind": "tidb_endpoint",
                "database": self.dbname,
                "description": "默认 TiDB SQL endpoint；查询当前集群业务数据、information_schema 和 TiDB 系统表。",
                "query_examples": [
                    "SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables",
                    "SELECT ... FROM <observed_table>",
                ],
            },
        ]
        if self._secondary_host is not None:
            surfaces.append({
                "name": "replica",
                "kind": "tidb_endpoint",
                "database": self.dbname,
                "description": "已配置的第二个 TiDB SQL endpoint；用于读取副本侧 schema、数据和状态。",
                "query_examples": [
                    "SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables",
                    "SELECT ... FROM <observed_table>",
                ],
            })
        for target in sorted(self.deployment.tidb_endpoints):
            surfaces.append({
                "name": target,
                "kind": "tidb_endpoint",
                "database": self.dbname,
                "description": "指定 TiDB SQL endpoint；用于比较该实例的 SQL 可见状态。",
                "query_examples": [
                    "SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables",
                    "SELECT ... FROM <observed_table>",
                ],
            })
        if getattr(self.deployment, "downstream_port", None) is not None:
            surfaces.append({
                "name": "downstream",
                "kind": "database_endpoint",
                "description": "复制运行时的独立下游数据库 endpoint；用于读取下游 schema、业务数据和复制结果。",
                "query_examples": [
                    "SHOW DATABASES",
                    "SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables",
                    "SELECT ... FROM <observed_table>",
                ],
            })
        surfaces.extend(
            self._surface_help_payload(surface)
            for surface in self._sql_connection_surfaces.values()
        )
        return surfaces

    @staticmethod
    def _surface_help_payload(surface: SqlConnectionSurface) -> dict[str, object]:
        payload = {
            "name": surface.name,
            "kind": "frozen_history" if surface.name == "history" else "database",
            "database": surface.database,
            "description": surface.description,
            "query_examples": list(surface.query_examples),
        }
        if surface.write_policy != "unrestricted":
            payload["write_policy"] = surface.write_policy
        return payload

    def _additional_tool_help(self, tool_name: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        history_spec = getattr(getattr(self, "_case", None), "frozen_history", None)
        if tool_name == "query_metrics" and history_spec is not None:
            result["runtime"] = {
                "allowed_metrics": [
                    str(metric).casefold() for metric in history_spec.required_metrics
                ],
            }
        if tool_name == "execute_sql":
            result["runtime"] = {
                "connection_surfaces": self._sql_connection_surface_help(),
            }
        if tool_name in {"query_metrics", "execute_sql"} and self._history_timeline is not None:
            spec = self._case.frozen_history
            result.setdefault("runtime", {}).update({
                "timezone": "UTC",
                "available_start": format_utc_timestamp(self._history_timeline.visible_start_ms),
                "available_end": format_utc_timestamp(self._history_timeline.visible_end_ms),
                "base_step_seconds": self._history_timeline.base_step_seconds,
                "overview_step_seconds": self._history_timeline.overview_step_seconds,
                "enabled_sources": [source.value for source in spec.record_sources],
                "max_history_records_per_response": spec.max_history_records_per_response,
            })
        return result

    def _pd_store(self, target: str) -> dict:
        service = target.rsplit("/", 1)[-1]
        stores = self.deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
        matches = [
            item["store"] | {"status": item["status"]}
            for item in stores
            if service == str(item["store"]["address"]).split(":", 1)[0]
        ]
        if len(matches) == 1:
            store = matches[0]
            self._known_store_ids[service] = int(store["id"])
            return store
        if len(matches) > 1:
            raise ValueError(
                f"TiDB target does not resolve to exactly one PD store: target={target!r}, "
                f"matches={matches!r}"
            )
        store_id = self._known_store_ids.get(service)
        if store_id is None:
            raise ValueError(
                f"TiDB target is absent from active PD stores and has no observed Store ID: "
                f"target={target!r}, known_store_ids={self._known_store_ids!r}"
            )
        payload = self.deployment.pd_request("GET", f"/pd/api/v1/store/{store_id}")
        store = payload["store"] | {"status": payload["status"]}
        if str(store["address"]).split(":", 1)[0] != service:
            raise ValueError(
                f"PD Store identity changed while resolving target: target={target!r}, "
                f"expected_service={service!r}, observed_store={store!r}"
            )
        return store

    def _remember_pd_stores(self, payload: dict) -> None:
        for item in payload["stores"]:
            service = str(item["store"]["address"]).split(":", 1)[0]
            self._known_store_ids[service] = int(item["store"]["id"])

    @staticmethod
    def _mvcc_region_id(target: str) -> int:
        match = re.fullmatch(r"region/([1-9][0-9]*)", str(target))
        if match is None:
            raise ValueError(f"MVCC target must use region/<positive-id>: target={target!r}")
        return int(match.group(1))

    def _mvcc_gc_phase_status(self) -> dict[str, Any]:
        phase_queries = {
            "gc_worker": '{__name__=~"tikv_.*gc.*"}',
            "resolve_locks": '{__name__=~".*resolve.*lock.*"}',
            "delete_ranges": '{__name__=~".*delete.*range.*"}',
            "do_gc": '{__name__=~".*do_gc.*"}',
        }
        prometheus = {
            phase: self._prometheus_instant_payload(query)
            for phase, query in phase_queries.items()
        }
        return {
            "prometheus_raw": prometheus,
        }

    def _changefeed_diagnostics(
        self,
        operation: str,
        capture_target: str,
        changefeed_id: str | None = None,
    ) -> dict[str, object]:
        if operation == "list":
            result = self.deployment.changefeed_diagnostics(capture_target)
            for item in result["changefeeds"]:
                if isinstance(item, dict) and isinstance(item.get("id"), str):
                    self._observed_changefeed_diagnostics[(capture_target, item["id"])] = item
            return result
        if changefeed_id is None:
            raise ValueError("changefeed diagnostics get requires changefeed_id")
        result = self.deployment.changefeed_diagnostics(capture_target, changefeed_id)
        self._observed_changefeed_diagnostics[(capture_target, changefeed_id)] = result["changefeeds"]
        return result

    def _gc_safepoint_list(self) -> dict[str, object]:
        result = self.deployment.gc_safepoint_list()
        self._observed_gc_safepoint = result
        return result

    def _gc_safepoint_remove(
        self,
        service_id: str,
        parameters: dict[str, Any],
    ) -> dict[str, object]:
        if set(parameters) != {"changefeed_id"}:
            raise ValueError(
                "gc_safepoint remove requires exactly parameters.changefeed_id: "
                f"service_id={service_id!r}, parameters={sorted(parameters)}"
            )
        if self._observed_gc_safepoint is None:
            raise ValueError("gc_safepoint remove requires a prior gc_safepoint list observation")
        changefeed_id = str(parameters["changefeed_id"])
        owners = [
            owner
            for owner in self._observed_gc_safepoint["service_gc_safe_points"]
            if isinstance(owner, dict) and str(owner.get("service_id")) == service_id
        ]
        if len(owners) != 1:
            raise ValueError(
                "gc_safepoint remove requires exactly one previously observed owner: "
                f"service_id={service_id!r}, matches={owners!r}"
            )
        owner_before_safe_point = int(owners[0]["safe_point"])
        workers_before = [
            owner
            for owner in self._observed_gc_safepoint["service_gc_safe_points"]
            if isinstance(owner, dict) and str(owner.get("service_id")) == "gc_worker"
        ]
        if len(workers_before) != 1:
            raise ValueError(
                "gc_safepoint remove requires exactly one previously observed gc_worker owner: "
                f"service_id={service_id!r}, workers={workers_before!r}"
            )
        worker_before_safe_point = int(workers_before[0]["safe_point"])
        if service_id == "gc_worker":
            raise ValueError("gc_safepoint remove cannot target gc_worker")
        capture_targets = sorted({
            capture_target
            for capture_target, observed_changefeed_id in self._observed_changefeed_diagnostics
            if observed_changefeed_id == changefeed_id
        })
        states = self.deployment.node_states()
        stopped_captures = sorted(
            target
            for target, state in states.items()
            if target.startswith("ticdc/") and not state["running"]
        )
        if capture_targets:
            if len(capture_targets) != 1:
                raise ValueError(
                    "gc_safepoint remove requires one observed capture for the exact changefeed: "
                    f"service_id={service_id!r}, changefeed_id={changefeed_id!r}, "
                    f"capture_targets={capture_targets!r}"
                )
            capture_target = capture_targets[0]
            if states.get(capture_target, {}).get("running"):
                if len(stopped_captures) != 1:
                    raise ValueError(
                        "gc_safepoint remove cannot uniquely bind the stopped owner capture: "
                        f"service_id={service_id!r}, changefeed_id={changefeed_id!r}, "
                        f"capture_target={capture_target!r}, stopped_captures={stopped_captures!r}"
                    )
                owner_runtime_target = stopped_captures[0]
            else:
                owner_runtime_target = capture_target
        else:
            # abandoned capture 处于停止状态，其 changefeed 无法经由任何合法观察
            # 进入 diagnostics 记录；此时 owner 只能绑定到当前唯一停止的 TiCDC capture。
            if len(stopped_captures) != 1:
                raise ValueError(
                    "gc_safepoint remove requires exactly one stopped TiCDC capture to bind the "
                    f"abandoned owner: service_id={service_id!r}, changefeed_id={changefeed_id!r}, "
                    f"stopped_captures={stopped_captures!r}"
                )
            capture_target = stopped_captures[0]
            owner_runtime_target = capture_target
        if owner_runtime_target not in states or not owner_runtime_target.startswith("ticdc/"):
            raise ValueError(
                "gc_safepoint remove owner_runtime_target is not a TiCDC service: "
                f"owner_runtime_target={owner_runtime_target!r}, states={sorted(states)!r}"
            )
        if states[owner_runtime_target]["running"]:
            raise ValueError(
                "gc_safepoint remove requires the mapped abandoned capture to be stopped: "
                f"owner_runtime_target={owner_runtime_target!r}, state={states[owner_runtime_target]!r}"
            )
        if capture_target not in states or not capture_target.startswith("ticdc/"):
            raise ValueError(
                "gc_safepoint remove capture_target is not a TiCDC service: "
                f"capture_target={capture_target!r}, states={sorted(states)!r}"
            )
        capture_was_stopped = not states[capture_target]["running"]
        if capture_was_stopped:
            if capture_target != owner_runtime_target:
                raise ValueError(
                    "gc_safepoint remove can only temporarily start the stopped owner capture: "
                    f"capture_target={capture_target!r}, owner_runtime_target={owner_runtime_target!r}"
                )
            self.deployment.start_component(capture_target)
            self.deployment._wait(
                capture_target,
                lambda: self.deployment.changefeed_diagnostics(capture_target, changefeed_id),
                180,
            )
        self._changefeed_diagnostics("get", capture_target, changefeed_id)
        before = self.deployment.gc_safepoint_list()
        result = self.deployment.remove_changefeed(capture_target, changefeed_id)

        def wait_for_owner_release() -> None:
            current = self.deployment.gc_safepoint_list()
            matches = [
                owner
                for owner in current["service_gc_safe_points"]
                if isinstance(owner, dict) and str(owner.get("service_id")) == service_id
            ]
            if len(matches) > 1:
                raise RuntimeError(
                    "TiCDC service GC safepoint has duplicate exact owners after changefeed removal: "
                    f"service_id={service_id!r}, changefeed_id={changefeed_id!r}, owners={matches!r}"
                )
            workers = [
                owner
                for owner in current["service_gc_safe_points"]
                if isinstance(owner, dict) and str(owner.get("service_id")) == "gc_worker"
            ]
            if len(workers) != 1:
                raise RuntimeError(
                    "TiCDC service GC safepoint cleanup requires exactly one gc_worker owner: "
                    f"service_id={service_id!r}, changefeed_id={changefeed_id!r}, workers={workers!r}"
                )
            feeds = self.deployment.changefeed_diagnostics(capture_target)["changefeeds"]
            if any(
                isinstance(feed, dict) and str(feed.get("id")) == changefeed_id
                for feed in feeds
            ):
                raise RuntimeError(
                    "TiCDC changefeed still exists after removal request: "
                    f"capture_target={capture_target!r}, changefeed_id={changefeed_id!r}, feeds={feeds!r}"
                )
            if matches:
                owner_safe_point = int(matches[0]["safe_point"])
                worker_safe_point = int(workers[0]["safe_point"])
                baseline_was_released = owner_before_safe_point >= worker_before_safe_point
                owner_advanced = owner_safe_point > owner_before_safe_point
                if owner_safe_point < worker_safe_point or not (baseline_was_released or owner_advanced):
                    raise RuntimeError(
                        "TiCDC service GC safepoint owner did not release after exact changefeed removal: "
                        f"service_id={service_id!r}, changefeed_id={changefeed_id!r}, "
                        f"owner_before={owner_before_safe_point}, owner_after={owner_safe_point}, "
                        f"worker_before={worker_before_safe_point}, worker_after={worker_safe_point}"
                    )

        self.deployment._wait(capture_target, wait_for_owner_release, 180)
        after = self.deployment.gc_safepoint_list()
        self._observed_gc_safepoint = after
        return {
            "service_id": service_id,
            "changefeed_id": changefeed_id,
            "owner_runtime_target": owner_runtime_target,
            "before": before,
            "cleanup": result,
            "after": after,
            "capture_started_for_cleanup": capture_was_stopped,
            "capture_running_after_cleanup": bool(
                self.deployment.node_states()[capture_target]["running"]
            ),
        }

    def configure_br_backup_runtime(self, runtime: Dict[str, Any]) -> None:
        if self._br_backup_runtime is not None:
            raise RuntimeError(f"TiDB BR backup runtime is already configured: run_id={self.run_id!r}")
        self._br_backup_runtime = dict(runtime)

    def clear_br_backup_runtime(self) -> None:
        if self._br_backup_runtime is None:
            raise RuntimeError(f"TiDB BR backup runtime is not configured: run_id={self.run_id!r}")
        self._br_backup_runtime = None
        self._br_backup_attempt_no = 0
        self._last_br_backup_result = None

    def _require_br_backup_runtime(self) -> Dict[str, Any]:
        if self._br_backup_runtime is None:
            raise RuntimeError(f"TiDB BR backup runtime is not configured: run_id={self.run_id!r}")
        return self._br_backup_runtime

    def configure_mvcc_recovery_guard(self, guard: Dict[str, Any]) -> None:
        if self._mvcc_recovery_guard is not None:
            raise RuntimeError(
                f"TiDB MVCC recovery guard is already configured: run_id={self.run_id!r}, "
                f"configured={self._mvcc_recovery_guard!r}"
            )
        self._mvcc_recovery_guard = dict(guard)

    def clear_mvcc_recovery_guard(self) -> None:
        if self._mvcc_recovery_guard is None:
            raise RuntimeError(
                f"TiDB MVCC recovery guard is not configured: run_id={self.run_id!r}"
            )
        self._mvcc_recovery_guard = None

    def mvcc_recovery_guard_active(self) -> bool:
        return self._mvcc_recovery_guard is not None

    def configure_hc04_restore_runtime(self, runtime: Dict[str, Any]) -> None:
        if self._hc04_restore_runtime is not None:
            raise RuntimeError(
                f"TiDB HC04 restore runtime is already configured: run_id={self.run_id!r}"
            )
        self._hc04_restore_runtime = dict(runtime)
        self._hc04_restore_attempt_no = 0
        tools = tuple(spec.tool_id for spec in self.get_tool_specs()
                      if spec.tool_id not in self.HC04_RESTORE_TOOLS)
        self._configure_tools((*tools, *self.HC04_RESTORE_TOOLS))

    def clear_hc04_restore_runtime(self) -> None:
        if self._hc04_restore_runtime is None:
            raise RuntimeError(
                f"TiDB HC04 restore runtime is not configured: run_id={self.run_id!r}"
            )
        self._hc04_restore_runtime = None
        self._hc04_restore_attempt_no = 0
        self._configure_tools(tuple(spec.tool_id for spec in self.get_tool_specs()
                                    if spec.tool_id not in self.HC04_RESTORE_TOOLS))

    def _require_hc04_restore_runtime(self) -> Dict[str, Any]:
        if self._hc04_restore_runtime is None:
            raise ValueError(
                f"TiDB HC04 restore runtime is not configured: run_id={self.run_id!r}"
            )
        return self._hc04_restore_runtime

    def configure_k08_pitr_runtime(self, runtime) -> None:
        if self._k08_pitr_runtime is not None:
            raise RuntimeError(
                f"TiDB K08 PITR runtime is already configured: run_id={self.run_id!r}"
            )
        self._k08_pitr_runtime = runtime

    def clear_k08_pitr_runtime(self) -> None:
        if self._k08_pitr_runtime is None:
            raise RuntimeError(
                f"TiDB K08 PITR runtime is not configured: run_id={self.run_id!r}"
            )
        self._k08_pitr_runtime = None

    def owns_k08_pitr_runtime(self, runtime) -> bool:
        return self._k08_pitr_runtime is runtime

    def _require_k08_pitr_runtime(self):
        if self._k08_pitr_runtime is None:
            raise RuntimeError(
                f"TiDB K08 PITR runtime is not configured: run_id={self.run_id!r}"
            )
        return self._k08_pitr_runtime

    def _hc04_rows(self, sql: str, params: tuple = ()) -> list[tuple]:
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(sql, params)
            return list(cursor.fetchall())

    def _hc04_execute(self, sql: str, params: tuple = ()) -> None:
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(sql, params)

    @staticmethod
    def _hc04_hash(path: str) -> str:
        digest = hashlib.sha256()
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _hc04_approved_source(self, runtime: Dict[str, Any], target_segment: str) -> tuple[int, str]:
        rows = self._hc04_rows(
            f"SELECT a.source_object_id, a.source_segment, o.segment_name, o.checksum "
            f"FROM {runtime['db']}.{runtime['approval_table']} a "
            f"JOIN {runtime['db']}.{runtime['object_inventory_table']} o "
            "ON o.object_id = a.source_object_id "
            "WHERE a.request_key = %s AND a.selected_backup_id = %s "
            "AND a.source_segment = %s "
            "AND a.source_role = 'primary' AND a.restore_mode = 'isolated' "
            "AND a.approval_state = 'APPROVED' AND a.approved_by = 'dr-owner' "
            "ORDER BY a.approved_at DESC, a.approval_id DESC LIMIT 1",
            (runtime["request_key"], runtime["selected_backup_id"], target_segment),
        )
        if len(rows) != 1:
            raise RuntimeError(
                "HC04 approved source must identify exactly one object: "
                f"request_key={runtime['request_key']!r}, "
                f"selected_backup_id={runtime['selected_backup_id']!r}, rows={rows!r}"
            )
        source_object_id, source_segment, catalog_segment, catalog_checksum = rows[0]
        if str(source_segment) != target_segment or str(catalog_segment) != target_segment:
            raise RuntimeError(
                "HC04 approved source segment does not match the active fault: "
                f"source_object_id={source_object_id!r}, source_segment={source_segment!r}, "
                f"catalog_segment={catalog_segment!r}, target_segment={target_segment!r}"
            )
        source_path = runtime["object_files"].get(int(source_object_id))
        if source_path is None or not os.path.isfile(source_path):
            raise RuntimeError(
                "HC04 approved source object is not readable: "
                f"source_object_id={source_object_id!r}, source_path={source_path!r}"
            )
        source_checksum = self._hc04_hash(source_path)
        if source_checksum != str(catalog_checksum):
            raise RuntimeError(
                "HC04 approved source checksum disagrees with archive inventory: "
                f"source_object_id={source_object_id!r}, catalog_checksum={catalog_checksum!r}, "
                f"actual_checksum={source_checksum!r}"
            )
        return int(source_object_id), source_checksum

    @Tool(
        description=(
            "查看指定 backup 的对象存储 inventory 和 log-segment continuity 未过滤结果。结果来自当前 case 的"
            "真实对象文件及 TiDB 审计表，不是提交报告的解析结果；需要结合恢复请求和审批记录判断对象关系。"
        ),
        arg_descriptions={
            "backup_id": "批准恢复请求中的 backup_id",
        },
    )
    def inspect_backup_archive(self, backup_id: str) -> str:
        runtime = self._require_hc04_restore_runtime()
        if backup_id != runtime["selected_backup_id"]:
            raise ValueError(
                "HC04 archive inspection target is outside the approved request: "
                f"requested={backup_id!r}, approved={runtime['selected_backup_id']!r}"
            )
        object_rows = self._hc04_rows(
            f"SELECT object_id, backup_id, segment_name, region, object_status, readable, replicated, legal_hold, checksum "
            f"FROM {runtime['db']}.{runtime['object_inventory_table']} "
            "WHERE backup_id = %s ORDER BY object_id DESC",
            (backup_id,),
        )
        segment_rows = self._hc04_rows(
            f"SELECT segment_name, present, checksum_status, object_status, replica_status, usable_for_restore "
            f"FROM {runtime['db']}.{runtime['log_segment_table']} "
            "WHERE backup_id = %s ORDER BY segment_id DESC",
            (backup_id,),
        )
        return json.dumps({
            "status": "success",
            "backup_id": backup_id,
            "objects": object_rows,
            "segments": segment_rows,
        }, ensure_ascii=False, default=str)

    @Tool(
        description=(
            "从当前 case 已登记的归档对象副本恢复一个指定 segment。工具只允许复制对象存储中的"
            "现有对象，不允许修改 TiDB 业务表、审计请求或生产集群；复制后会按实际 SHA-256 更新"
            "归档可用性状态。返回值只表示复制操作完成，最终恢复能力需要通过后续状态检查确认。"
        ),
        arg_descriptions={
            "source_object_id": "对象目录中的源 object_id",
            "target_segment": "要修复的 segment_name",
        },
    )
    def repair_backup_archive(self, source_object_id: int, target_segment: str) -> str:
        runtime = self._require_hc04_restore_runtime()
        if target_segment not in runtime["fault_segments"]:
            raise ValueError(
                "HC04 archive repair target is outside the active fault: "
                f"requested={target_segment!r}, fault_segments={runtime['fault_segments']!r}"
            )
        source_row = self._hc04_rows(
            f"SELECT object_id, backup_id, segment_name, checksum FROM {runtime['db']}.{runtime['object_inventory_table']} "
            "WHERE object_id = %s",
            (source_object_id,),
        )
        if len(source_row) != 1:
            raise ValueError(
                "HC04 archive repair source object must identify exactly one object: "
                f"source_object_id={source_object_id!r}, rows={source_row!r}"
            )
        object_id, source_backup_id, source_segment, source_catalog_checksum = source_row[0]
        if str(source_segment) != target_segment:
            raise ValueError(
                "HC04 archive repair source segment does not match target: "
                f"source_object_id={source_object_id!r}, source_segment={source_segment!r}, "
                f"target_segment={target_segment!r}"
            )
        source_path = runtime["object_files"].get(int(object_id))
        target_path = runtime["primary_object_paths"][target_segment]
        if source_path is None or not os.path.isfile(source_path):
            raise RuntimeError(
                "HC04 archive repair source object is not readable: "
                f"source_object_id={source_object_id!r}, source_backup_id={source_backup_id!r}, "
                f"source_path={source_path!r}"
            )
        approved_source_object_id, approved_checksum = self._hc04_approved_source(runtime, target_segment)
        shutil.copyfile(source_path, target_path)
        actual_checksum = self._hc04_hash(target_path)
        valid = (
            actual_checksum == str(source_catalog_checksum)
            and actual_checksum == approved_checksum
            and int(object_id) == approved_source_object_id
        )
        self._hc04_execute(
            f"UPDATE {runtime['db']}.{runtime['object_inventory_table']} "
            "SET object_status = %s, readable = 1, replicated = %s, checksum = %s "
            "WHERE object_id = %s",
            (
                "AVAILABLE" if valid else "CORRUPT",
                1 if valid else 0,
                actual_checksum,
                runtime["primary_object_ids"][target_segment],
            ),
        )
        self._hc04_execute(
            f"UPDATE {runtime['db']}.{runtime['log_segment_table']} "
            "SET present = 1, checksum_status = %s, object_status = %s, replica_status = %s, usable_for_restore = %s "
            "WHERE backup_id = %s AND segment_name = %s",
            (
                "OK" if valid else "MISMATCH",
                "READABLE" if valid else "READABLE_BUT_INVALID",
                "REPLICATED" if valid else "NOT_REPLICATED",
                1 if valid else 0,
                runtime["selected_backup_id"],
                target_segment,
            ),
        )
        return json.dumps({
            "status": "success",
            "operation": "repair_backup_archive",
            "source_object_id": int(object_id),
            "source_backup_id": str(source_backup_id),
            "target_segment": target_segment,
        }, ensure_ascii=False)

    def _hc04_source_truth(self, runtime: Dict[str, Any]) -> dict[str, tuple[int, int]]:
        queries = {
            runtime["orders_table"]: f"SELECT COUNT(*), COALESCE(SUM(order_id), 0) FROM {runtime['db']}.{runtime['snapshot_orders_table']}",
            runtime["order_lines_table"]: f"SELECT COUNT(*), COALESCE(SUM(line_id), 0) FROM {runtime['db']}.{runtime['snapshot_order_lines_table']}",
            runtime["payments_table"]: f"SELECT COUNT(*), COALESCE(SUM(payment_id), 0) FROM {runtime['db']}.{runtime['snapshot_payments_table']}",
            runtime["inventory_table"]: f"SELECT COUNT(*), COALESCE(SUM(sku_id), 0) FROM {runtime['db']}.{runtime['snapshot_inventory_table']}",
        }
        return {
            table: tuple(int(value) for value in self._hc04_rows(sql)[0])
            for table, sql in queries.items()
        }

    def _hc04_restore_tables(self, runtime: Dict[str, Any]) -> tuple[dict, ...]:
        tables = (
            (runtime["orders_table"], runtime["snapshot_orders_table"], runtime["sandbox_orders_table"], "order_id"),
            (runtime["order_lines_table"], runtime["snapshot_order_lines_table"], runtime["sandbox_order_lines_table"], "line_id"),
            (runtime["payments_table"], runtime["snapshot_payments_table"], runtime["sandbox_payments_table"], "payment_id"),
            (runtime["inventory_table"], runtime["snapshot_inventory_table"], runtime["sandbox_inventory_table"], "sku_id"),
        )
        truth = self._hc04_source_truth(runtime)
        checks = []
        for table, snapshot, sandbox, key in tables:
            self._hc04_execute(f"DELETE FROM {runtime['db']}.{sandbox}")
            self._hc04_execute(
                f"INSERT INTO {runtime['db']}.{sandbox} SELECT * FROM {runtime['db']}.{snapshot}"
            )
            row = self._hc04_rows(
                f"SELECT COUNT(*), COALESCE(SUM({key}), 0) FROM {runtime['db']}.{sandbox}"
            )[0]
            restored = (int(row[0]), int(row[1]))
            expected = truth[table]
            checks.append({
                "table_name": table,
                "source_rows": expected[0],
                "restored_rows": restored[0],
                "source_checksum": expected[1],
                "restored_checksum": restored[1],
                "checksum_status": "MATCH" if restored == expected else "MISMATCH",
            })
        return tuple(checks)

    @Tool(
        description=(
            "在独立的 HC04 sandbox 中重新执行恢复验证。失败或成功都会写入 restore attempt、"
            "checkpoint 和四张关键表的实际校验结果；调用结果只报告恢复状态，详细状态需要单独检查。"
        ),
    )
    def run_isolated_restore(self) -> str:
        runtime = self._require_hc04_restore_runtime()
        self._hc04_restore_attempt_no += 1
        attempt_id = f"{runtime['selected_drill_id']}-attempt-{self._hc04_restore_attempt_no:03d}"
        started = time.monotonic()
        valid_chain = True
        for segment in runtime["fault_segments"]:
            _, expected_checksum = self._hc04_approved_source(runtime, segment)
            object_hash = self._hc04_hash(runtime["primary_object_paths"][segment])
            chain_rows = self._hc04_rows(
                f"SELECT usable_for_restore, checksum_status FROM {runtime['db']}.{runtime['log_segment_table']} "
                "WHERE backup_id = %s AND segment_name = %s",
                (runtime["selected_backup_id"], segment),
            )
            valid_chain = valid_chain and (
                len(chain_rows) == 1
                and int(chain_rows[0][0]) == 1
                and str(chain_rows[0][1]).casefold() == "ok"
                and object_hash == expected_checksum
            )
        if valid_chain:
            checks = self._hc04_restore_tables(runtime)
            success = all(item["checksum_status"] == "MATCH" for item in checks)
            checkpoint_status = "COMPLETE" if success else "FAILED"
            checksum_status = "MATCH" if success else "MISMATCH"
            restore_status = "SUCCESS" if success else "FAILED"
            failure_class = "NONE" if success else "CHECKSUM_VALIDATION_FAILED"
            log_excerpt = "isolated restore completed and all critical table checks matched" if success else "isolated restore copied data but critical table checks did not match"
        else:
            checks = tuple()
            success = False
            checkpoint_status = "GAP"
            checksum_status = "NOT_VERIFIED"
            restore_status = "FAILED"
            failure_class = "CHECKPOINT_NOT_REACHED"
            log_excerpt = "isolated restore did not reach the requested checkpoint"
        duration = max(1, int(round(time.monotonic() - started)))
        observed_rto_seconds = duration
        observed_rpo_seconds = 0 if success else None
        source_truth = self._hc04_source_truth(runtime)
        total_source_rows = sum(value[0] for value in source_truth.values())
        restored_rows = sum(item["restored_rows"] for item in checks)
        self._hc04_execute(
            f"INSERT INTO {runtime['db']}.{runtime['restore_attempt_table']} "
            "(attempt_id, drill_id, backup_id, status, isolated, checkpoint_status, checksum_status, "
            "observed_rpo_seconds, observed_rto_seconds, restore_duration_seconds, failure_class, log_excerpt) "
            "VALUES (%s, %s, %s, %s, 1, %s, %s, %s, %s, %s, %s, %s)",
            (
                attempt_id,
                runtime["selected_drill_id"],
                runtime["selected_backup_id"],
                restore_status,
                checkpoint_status,
                checksum_status,
                observed_rpo_seconds,
                observed_rto_seconds,
                duration,
                failure_class,
                log_excerpt,
            ),
        )
        self._hc04_execute(
            f"UPDATE {runtime['db']}.{runtime['restore_drill_table']} SET status = %s, checkpoint_status = %s, "
            "checksum_status = %s, restore_duration_seconds = %s, business_crc_status = %s, "
            "source_rows = %s, restored_rows = %s, failure_class = %s, log_excerpt = %s WHERE drill_id = %s",
            (
                restore_status,
                checkpoint_status,
                checksum_status,
                duration,
                "MATCH" if success else "NOT_VERIFIED",
                total_source_rows,
                restored_rows,
                failure_class,
                log_excerpt,
                runtime["selected_drill_id"],
            ),
        )
        self._hc04_execute(
            f"DELETE FROM {runtime['db']}.{runtime['restore_check_table']} WHERE drill_id = %s",
            (runtime["selected_drill_id"],),
        )
        if checks:
            for item in checks:
                self._hc04_execute(
                    f"INSERT INTO {runtime['db']}.{runtime['restore_check_table']} "
                    "(drill_id, table_name, source_rows, restored_rows, source_checksum, restored_checksum, checksum_status, critical) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, 1)",
                    (
                        runtime["selected_drill_id"], item["table_name"], item["source_rows"], item["restored_rows"],
                        item["source_checksum"], item["restored_checksum"], item["checksum_status"],
                    ),
                )
        return json.dumps({
            "status": "success",
            "operation": "run_isolated_restore",
            "attempt_id": attempt_id,
            "restore_status": restore_status,
            "checkpoint_status": checkpoint_status,
            "checksum_status": checksum_status,
        }, ensure_ascii=False, default=str)

    @Tool(
        description="读取 HC04 当前 restore attempts、最后一次恢复状态和 sandbox 校验结果。",
    )
    def inspect_isolated_restore(self) -> str:
        runtime = self._require_hc04_restore_runtime()
        attempts = self._hc04_rows(
            f"SELECT attempt_id, status, checkpoint_status, checksum_status, failure_class FROM {runtime['db']}.{runtime['restore_attempt_table']} "
            "WHERE drill_id = %s ORDER BY attempt_id",
            (runtime["selected_drill_id"],),
        )
        checks = self._hc04_rows(
            f"SELECT table_name, source_rows, restored_rows, source_checksum, restored_checksum, checksum_status "
            f"FROM {runtime['db']}.{runtime['restore_check_table']} WHERE drill_id = %s ORDER BY table_name",
            (runtime["selected_drill_id"],),
        )
        return json.dumps({"status": "success", "attempts": attempts, "checks": checks}, ensure_ascii=False, default=str)


    def capture_br_source_truth(self, case) -> Dict[str, int]:
        runtime = self._require_br_backup_runtime()
        if (case.database, case.table) != (runtime["database"], runtime["table"]):
            raise ValueError(
                "TiDB BR source truth target mismatch: "
                f"case={case.database}.{case.table}, runtime={runtime['database']}.{runtime['table']}"
            )
        sql = (
            f"SELECT COUNT(*), COALESCE(SUM(event_id), 0), "
            f"BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_type, amount, payload))) "
            f"FROM {runtime['database']}.{runtime['table']}"
        )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
        if row is None or len(row) != 3:
            raise RuntimeError(
                "TiDB BR source truth query returned an invalid row: "
                f"run_id={self.run_id!r}, sql={sql!r}, row={row!r}"
            )
        return {
            "row_count": int(row[0]),
            "event_id_sum": int(row[1]),
            "crc": int(row[2]),
        }

    @staticmethod
    def _parse_br_metrics(output: str) -> Dict[str, object]:
        def integer(name: str, pattern: str) -> Optional[int]:
            match = re.search(pattern, output, re.IGNORECASE)
            return int(match.group(1)) if match else None

        checksum_values = re.findall(r"Checksum[^\n]*?([0-9]+(?:\.[0-9]+)?)%", output, re.IGNORECASE)
        return {
            "total_ranges": integer("total_ranges", r"total-ranges=(\d+)"),
            "ranges_succeed": integer("ranges_succeed", r"ranges-succeed=(\d+)"),
            "ranges_failed": integer("ranges_failed", r"ranges-failed=(\d+)"),
            "checksum_percent": float(checksum_values[-1]) if checksum_values else None,
        }

    def _record_br_backup_attempt(
        self,
        runtime: Dict[str, Any],
        result: Dict[str, object],
    ) -> str:
        self._br_backup_attempt_no += 1
        attempt_id = f"{runtime['run_prefix']}-{self._br_backup_attempt_no:03d}"
        dispatch_id = f"{attempt_id}-dispatch"
        route_token = (
            runtime["request_route_token"]
            if self._br_backup_attempt_no == 1
            else "rt-1a6d4c8e2f90"
            if self._br_backup_attempt_no == 2
            else f"rt-{hashlib.sha256(attempt_id.encode('utf-8')).hexdigest()[:12]}"
        )
        lease_token = (
            runtime["target_lease_token"]
            if result["http_status"] == 403
            else runtime["post_handoff_lease_token"]
        )
        material_handle = str(result["material_handle"])
        request_assignment_fence = str(
            result["request_assignment_fence"]
        )
        request_context_token = str(result["request_context_token"])
        request_started_at = (
            "2026-08-01 23:58:40"
            if result["http_status"] == 403
            else "2026-08-01 23:59:40"
        )
        event_time = (
            "2026-08-01 23:58:47"
            if result["http_status"] == 403
            else "2026-08-01 23:59:46"
        )
        metrics = result["metrics"]
        status = str(result["status"])
        error_text = str(result.get("error", ""))[-2048:]
        result["dispatch_id"] = dispatch_id
        result["audit_dispatch_id"] = dispatch_id
        result["lease_token"] = lease_token
        result["material_handle"] = material_handle
        result["request_assignment_fence"] = request_assignment_fence
        result["request_context_token"] = request_context_token
        request_stage = "backup_upload"
        assignment_phase = (
            runtime.get("target_execution_phase", "dispatch_window")
            if result["http_status"] == 403
            else "retry_data_plane"
        )
        assignment_reason = (
            runtime.get("target_execution_reason", "storage-write")
            if result["http_status"] == 403
            else "post-refresh-retry"
        )
        result["request_stage"] = request_stage
        result["assignment_phase"] = assignment_phase
        result["assignment_reason"] = assignment_reason
        result["cache_phase"] = assignment_phase
        is_failed_write = result["http_status"] == 403 and self._br_backup_attempt_no == 1
        if is_failed_write:
            runtime["failed_dispatch_id"] = dispatch_id
            runtime["failed_request_started_at"] = request_started_at
            runtime["failed_request_event_time"] = event_time
            runtime["failed_request_attempt_id"] = f"{attempt_id}-write"
            runtime["failed_request_route_token"] = route_token
            runtime["failed_request_assignment_fence"] = request_assignment_fence
            runtime["failed_request_context_token"] = request_context_token
            runtime["failed_request_stage"] = request_stage
            runtime["failed_request_assignment_phase"] = assignment_phase
            runtime["failed_request_assignment_reason"] = assignment_reason
            runtime["failed_request_cache_phase"] = assignment_phase
        sql = (
            f"INSERT INTO {runtime['history_table']} "
            "(job_id, storage_uri, database_name, table_name, status, error_text, "
            "ranges_total, ranges_succeed, ranges_failed, checksum_percent, actor) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        values = (
            attempt_id,
            runtime["storage"],
            runtime["database"],
            runtime["table"],
            status,
            error_text,
            metrics["total_ranges"],
            metrics["ranges_succeed"],
            metrics["ranges_failed"],
            metrics["checksum_percent"],
            "br-agent",
        )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(sql, values)
            cursor.execute(
                f"INSERT INTO {runtime['dispatch_routes_table']} "
                "(route_token, dispatch_id, target_scope, executor_handle, lease_token, route_generation, valid_from, "
                "valid_to, route_state, assignment_phase, route_reason, request_assignment_fence, request_context_token) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    route_token,
                    dispatch_id,
                    result["target_scope"],
                    result["executor_handle"],
                    lease_token,
                    3000 + self._br_backup_attempt_no,
                    request_started_at,
                    "2026-08-01 23:59:00" if result["http_status"] == 403 else None,
                    "released" if result["http_status"] == 403 else "active",
                    assignment_phase,
                    assignment_reason,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            cursor.execute(
                f"INSERT INTO {runtime['job_dispatches_table']} "
                "(dispatch_id, job_id, target_scope, storage_uri, dispatch_generation, "
                "dispatched_at, released_at, dispatch_state, assignment_phase, assignment_reason, request_assignment_fence, request_context_token) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    dispatch_id,
                    attempt_id,
                    result["target_scope"],
                    runtime["storage"],
                    3000 + self._br_backup_attempt_no,
                    request_started_at,
                    "2026-08-01 23:59:00" if result["http_status"] == 403 else None,
                    "released" if result["http_status"] == 403 else "active",
                    assignment_phase,
                    assignment_reason,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            cursor.execute(
                f"INSERT INTO {runtime['storage_audit_table']} "
                "(job_id, target_scope, storage_uri, dispatch_id, http_status, access_key_fingerprint, "
                "policy_decision, request_stage, request_started_at, event_time, request_assignment_fence, request_context_token) VALUES "
                "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    attempt_id,
                    result["target_scope"],
                    runtime["storage"],
                    dispatch_id,
                    result["http_status"],
                    result["access_key_fingerprint"],
                    result.get("policy_decision", "allow"),
                    request_stage,
                    request_started_at,
                    event_time,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            if is_failed_write:
                cursor.execute(
                    f"INSERT INTO {runtime['request_attempts_table']} "
                    "(attempt_id, dispatch_id, target_scope, request_context_token, request_assignment_fence, "
                    "request_started_at, event_time, request_stage, execution_phase, execution_reason, attempt_sequence, "
                    "operation_name, attempt_state, access_key_fingerprint, http_status) VALUES "
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        runtime["failed_request_attempt_id"],
                        dispatch_id,
                        result["target_scope"],
                        request_context_token,
                        request_assignment_fence,
                        request_started_at,
                        event_time,
                        request_stage,
                        assignment_phase,
                        assignment_reason,
                        int(runtime["failed_request_attempt_sequence"]),
                        "put_backup_chunk",
                        "failed",
                        result["access_key_fingerprint"],
                        403,
                    ),
                )
        return attempt_id

    def br_prefix_quarantine_state(self) -> Optional[Dict[str, object]]:
        """Current storage-guard quarantine state for the BR backup prefix."""
        runtime = self._require_br_backup_runtime()
        if not runtime.get("storage_prefix_quarantine"):
            return None
        return {
            "prefix": runtime["object_prefix"],
            "bucket": runtime["bucket"],
            "quarantine_ref": runtime["prefix_quarantine_ref"],
            "active": bool(runtime.get("prefix_quarantine_active")),
        }

    def _release_br_prefix_quarantine(
        self,
        target_prefix: str,
        quarantine_ref: str,
        triggering_change_ref: str,
    ) -> Dict[str, object]:
        runtime = self._require_br_backup_runtime()
        mismatch = not (
            target_prefix == runtime["object_prefix"]
            and quarantine_ref == runtime["prefix_quarantine_ref"]
            and triggering_change_ref == runtime["target_change_ref"]
        )
        if mismatch or not runtime.get("prefix_quarantine_active"):
            raise _BrRefreshIdentityError(
                "BR storage prefix quarantine release rejected: the presented quarantine "
                "identity does not verify against the storage guard state; no state changed."
            )
        runtime["prefix_quarantine_active"] = False
        return {
            "released": True,
            "prefix": runtime["object_prefix"],
            "bucket": runtime["bucket"],
            "quarantine_ref": runtime["prefix_quarantine_ref"],
            "guard": "bucket-denial-rate-guard",
        }

    def _record_br_quarantine_denial(
        self,
        runtime: Dict[str, Any],
        result: Dict[str, object],
    ) -> None:
        # r11: every denied write is announced on the controller stream, but
        # the release ticket itself is issued only by the storage guard into
        # its ticket table on the first denial, so the release identity
        # cannot be observed before the denied attempt happened.
        denial_count = int(runtime.get("quarantine_denial_count", 0)) + 1
        runtime["quarantine_denial_count"] = denial_count
        denial_seconds = 2 * 60 + 3 + 20 * (denial_count - 1)
        at = f"2026-08-02 00:{denial_seconds // 60:02d}:{denial_seconds % 60:02d}"
        event = {
            "event": "storage_write_denied",
            "prefix": runtime["object_prefix"],
            "bucket": runtime["bucket"],
            "guard": "bucket-denial-rate-guard",
            "dispatch_id": result["dispatch_id"],
            "access_key_fingerprint": result["access_key_fingerprint"],
            "at": at,
        }
        runtime["controller_events"] = [event] + list(
            runtime.get("controller_events", ())
        )
        if runtime.get("quarantine_ticket_issued"):
            return
        runtime["quarantine_ticket_issued"] = True
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {runtime['quarantine_tickets_table']} "
                "(ticket_ref, prefix, bucket, guard, triggering_change_ref, "
                "issued_at, ticket_state) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    runtime["prefix_quarantine_ref"],
                    runtime["object_prefix"],
                    runtime["bucket"],
                    "bucket-denial-rate-guard",
                    runtime["target_change_ref"],
                    at,
                    "active",
                ),
            )

    def _run_br_backup(
        self,
        database: str,
        table: str,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ) -> Dict[str, object]:
        runtime = self._require_br_backup_runtime()
        expected_target = (runtime["database"], runtime["table"])
        if (database, table) != expected_target:
            raise ValueError(
                "BR backup target is outside the active case contract: "
                f"requested={database}.{table}, expected={expected_target[0]}.{expected_target[1]}"
            )
        if (access_key is None) != (secret_key is None):
            raise ValueError(
                "BR backup credentials must be supplied together: "
                f"database={database!r}, table={table!r}, access_key_supplied={access_key is not None}, "
                f"secret_key_supplied={secret_key is not None}"
            )
        credential_source = "explicit_override" if access_key is not None else "worker_observed_binding"
        access_key = runtime["observed_access_key"] if access_key is None else access_key
        secret_key = runtime["observed_secret_key"] if secret_key is None else secret_key
        # r9: the storage denial-rate guard quarantines the backup prefix after
        # repeated denied writes. Wrong credentials still fail authentication
        # (real 403 below); correct credentials hit the guard and are denied
        # by policy until the quarantine is released through the bounded op.
        if (
            runtime.get("storage_prefix_quarantine")
            and runtime.get("prefix_quarantine_active")
            and access_key == runtime["correct_access_key"]
        ):
            result = {
                "status": "error",
                "operation": "br_backup_table",
                "database": database,
                "table": table,
                "exit_code": 1,
                "metrics": self._parse_br_metrics(""),
                "output": "",
                "credential_source": credential_source,
                "access_key_fingerprint": self._br_access_key_fingerprint(access_key),
                "target_scope": runtime["target_scope"],
                "executor_handle": runtime["target_executor_handle"],
                "material_handle": (
                    runtime["observed_material_handle"]
                    if credential_source == "worker_observed_binding"
                    else "mh-explicit-override"
                ),
                "request_assignment_fence": (
                    runtime["target_assignment_fence"]
                    if self._br_backup_attempt_no == 0
                    else runtime["retry_assignment_fence"]
                ),
                "request_context_token": (
                    runtime["target_request_context"]
                    if self._br_backup_attempt_no == 0
                    else runtime["retry_request_context"]
                ),
                "http_status": 403,
                "policy_decision": "deny",
                "error": (
                    "BR failed: failed to get region of bucket admission: Forbidden: "
                    "quarantine policy denies writes to prefix "
                    f"{runtime['object_prefix']}"
                ),
            }
            attempt_id = self._record_br_backup_attempt(runtime, result)
            self._record_br_quarantine_denial(runtime, result)
            result["attempt_id"] = attempt_id
            self._last_br_backup_result = result
            return result
        container_name = (
            f"aiopsbench-br-{hashlib.sha256(self.run_id.encode()).hexdigest()[:12]}-"
            f"{self._br_backup_attempt_no + 1:03d}"
        )
        command = [
            "docker", "run", "--rm", "--name", container_name,
            "--network", runtime["network_name"],
            "-e", f"AWS_ACCESS_KEY_ID={access_key}",
            "-e", f"AWS_SECRET_ACCESS_KEY={secret_key}",
            "--entrypoint", "/br", runtime["br_image"],
            "backup", "table",
            "--pd", runtime["pd_endpoint"],
            "--db", database,
            "--table", table,
            "--storage", runtime["storage"],
            "--send-credentials-to-tikv=true",
            "--checksum=true",
            "--log-file", "-",
        ]
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=int(runtime["timeout_seconds"]))
            output = "\n".join(part for part in (stdout, stderr) if part)
            status = "success" if process.returncode == 0 else "error"
            error = output if status == "error" else ""
            exit_code = process.returncode
        except subprocess.TimeoutExpired as exc:
            process.kill()
            stdout, stderr = process.communicate()
            cleanup = subprocess.run(
                ["docker", "rm", "--force", container_name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if cleanup.returncode != 0:
                raise RuntimeError(
                    "Timed-out BR backup container cleanup failed: "
                    f"run_id={self.run_id!r}, container={container_name!r}, "
                    f"returncode={cleanup.returncode}, stdout={cleanup.stdout.strip()!r}, "
                    f"stderr={cleanup.stderr.strip()!r}"
                ) from exc
            output = "\n".join(part for part in (stdout, stderr) if part)
            status = "error"
            error = (
                f"BR backup timed out: timeout_seconds={runtime['timeout_seconds']}, "
                f"output={output}"
            )
            exit_code = 124
        redacted_output = output
        redacted_error = error
        for value in {access_key}:
            redacted_output = redacted_output.replace(value, "<redacted-access-key>")
            redacted_error = redacted_error.replace(value, "<redacted-access-key>")
        for value in {secret_key}:
            redacted_output = redacted_output.replace(value, "<redacted-secret-key>")
            redacted_error = redacted_error.replace(value, "<redacted-secret-key>")
        result = {
            "status": status,
            "operation": "br_backup_table",
            "database": database,
            "table": table,
            "exit_code": exit_code,
            "metrics": self._parse_br_metrics(output),
            "output": redacted_output,
            "credential_source": credential_source,
            "access_key_fingerprint": self._br_access_key_fingerprint(access_key),
            "target_scope": runtime["target_scope"],
            "executor_handle": runtime["target_executor_handle"],
            "material_handle": (
                runtime["observed_material_handle"]
                if credential_source == "worker_observed_binding"
                else "mh-explicit-override"
            ),
            "request_assignment_fence": (
                runtime["target_assignment_fence"]
                if self._br_backup_attempt_no == 0
                else runtime["retry_assignment_fence"]
            ),
            "request_context_token": (
                runtime["target_request_context"]
                if self._br_backup_attempt_no == 0
                else runtime["retry_request_context"]
            ),
            "http_status": 200 if status == "success" else 403,
        }
        if redacted_error:
            result["error"] = redacted_error
        attempt_id = self._record_br_backup_attempt(runtime, result)
        result["attempt_id"] = attempt_id
        self._last_br_backup_result = result
        return result

    def _list_br_objects(self, runtime: Dict[str, str]) -> tuple[str, ...]:
        backupmeta_path = (
            f"admission/{runtime['bucket']}/"
            f"{runtime['object_prefix'].rstrip('/')}/backupmeta"
        )
        script = (
            "mc alias set admission http://"
            f"{runtime['minio_container']}:9000 {runtime['correct_access_key']} "
            f"{runtime['correct_secret_key']} >/dev/null && "
            f"mc stat {shlex.quote(backupmeta_path)}"
        )
        completed = subprocess.run(
            [
                "docker", "run", "--rm", "--network", runtime["network_name"],
                "--entrypoint", "/bin/sh", runtime["mc_image"], "-c", script,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if completed.returncode != 0:
            not_found = completed.stderr.casefold()
            if "object does not exist" in not_found or "nosuchkey" in not_found or "not found" in not_found:
                return ()
            raise RuntimeError(
                "BR object listing failed: "
                f"run_id={self.run_id!r}, returncode={completed.returncode}, "
                f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
            )
        evidence = tuple(line for line in completed.stdout.splitlines() if line.strip())
        return (backupmeta_path, *evidence)

    @staticmethod
    def _br_access_key_fingerprint(access_key: str) -> str:
        return hashlib.sha256(access_key.encode("utf-8")).hexdigest()[:16]

    def _br_binding_propagation(self, runtime: Dict[str, Any]) -> list[dict[str, object]]:
        desired_binding_id = int(runtime["desired_binding_id"])
        desired_revision = int(runtime["desired_revision"])
        observed_binding_id = int(runtime["observed_binding_id"])
        observed_revision = int(runtime["observed_revision"])
        desired_credential_id = int(runtime["desired_credential_id"])
        return [
            {
                "worker_id": runtime["target_worker"],
                "target_scope": runtime["target_scope"],
                "desired_binding_id": desired_binding_id,
                "desired_revision": desired_revision,
                "desired_credential_id": desired_credential_id,
                "observed_binding_id": observed_binding_id,
                "observed_revision": observed_revision,
                "observed_material_handle": runtime["observed_material_handle"],
                "lease_state": "converged" if observed_revision == desired_revision else "stale",
                "last_heartbeat": "2026-08-01 23:59:58" if observed_revision == desired_revision else "2026-08-01 23:58:41",
                "change_ref": runtime["target_change_ref"],
            },
            {
                "worker_id": runtime["healthy_worker"],
                "target_scope": runtime["target_scope"],
                "desired_binding_id": desired_binding_id,
                "desired_revision": desired_revision,
                "desired_credential_id": desired_credential_id,
                "observed_binding_id": desired_binding_id,
                "observed_revision": desired_revision,
                "observed_material_handle": runtime["correct_material_handle"],
                "lease_state": "converged",
                "last_heartbeat": "2026-08-01 23:59:59",
                "change_ref": runtime["target_change_ref"],
            },
        ]

    def _br_storage_observations(self, runtime: Dict[str, Any]) -> dict[str, object]:
        return {
            "target_scope": runtime["target_scope"],
            "target_storage_uri": runtime["storage"],
            "object_store_state": "healthy",
            "target_prefix_policy": "allow",
            "canary_scope": f"{runtime['target_scope']}/rehearsal",
            "canary_worker": runtime["healthy_worker"],
            "canary_write_state": "success",
            "last_forbidden_worker": runtime["target_worker"],
            "last_forbidden_material_handle": runtime["target_material_handle"],
            "last_forbidden_at": "2026-08-01 23:58:47",
        }

    def _br_request_cache_state(self, runtime: Dict[str, Any]) -> list[dict[str, object]]:
        sql = (
            f"SELECT cache_token, route_token, target_scope, worker_handle, material_handle, cache_phase, "
            f"valid_from, valid_to, cache_state, change_ref, request_assignment_fence, request_context_token "
            f"FROM {runtime['request_cache_table']} "
            "WHERE target_scope=%s ORDER BY valid_from DESC, cache_token DESC"
        )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(sql, (runtime["target_scope"],))
            rows = cursor.fetchall()
        return [
            {
                "cache_token": str(row[0]),
                "route_token": str(row[1]),
                "target_scope": str(row[2]),
                "worker_handle": str(row[3]),
                "material_handle": str(row[4]),
                "cache_phase": str(row[5]),
                "valid_from": str(row[6]),
                "valid_to": None if row[7] is None else str(row[7]),
                "cache_state": str(row[8]),
                "change_ref": str(row[9]),
                "request_assignment_fence": str(row[10]),
                "request_context_token": str(row[11]),
            }
            for row in rows
        ]

    def _refresh_br_binding_cache(
        self,
        target: str,
        target_scope: str,
        request_route_token: str,
        request_cache_token: str,
        attempt_id: str,
        observed_authority_grant_id: int,
        desired_authority_grant_id: int,
        authority_lease_id: int,
        authority_epoch: str,
        request_assignment_fence: str,
        request_context_token: str,
        request_stage: str,
        assignment_phase: str,
        assignment_reason: str,
        cache_phase: str,
    ) -> dict[str, object]:
        runtime = self._require_br_backup_runtime()
        try:
            return self._refresh_br_binding_cache_checked(
                runtime,
                target,
                target_scope,
                request_route_token,
                request_cache_token,
                attempt_id,
                observed_authority_grant_id,
                desired_authority_grant_id,
                authority_lease_id,
                authority_epoch,
                request_assignment_fence,
                request_context_token,
                request_stage,
                assignment_phase,
                assignment_reason,
                cache_phase,
            )
        except _BrRefreshIdentityError:
            if not runtime.get("uniform_refresh_rejection", False):
                raise
            raise ValueError(_BR_REFRESH_IDENTITY_REJECTION) from None

    def _refresh_br_binding_cache_checked(
        self,
        runtime: Dict[str, Any],
        target: str,
        target_scope: str,
        request_route_token: str,
        request_cache_token: str,
        attempt_id: str,
        observed_authority_grant_id: int,
        desired_authority_grant_id: int,
        authority_lease_id: int,
        authority_epoch: str,
        request_assignment_fence: str,
        request_context_token: str,
        request_stage: str,
        assignment_phase: str,
        assignment_reason: str,
        cache_phase: str,
    ) -> dict[str, object]:
        # r4 focused authority model: lease rows carry the desired sentinel 0
        # and the validator derives the unique request-time-valid production
        # grant from the control-plane credential and the grants window.
        derive_desired_from_grants = bool(runtime.get("derive_desired_from_grants", False))
        if target != runtime["target_worker"]:
            raise _BrRefreshIdentityError(
                "BR binding refresh target does not match the failed request assignment; no state changed: "
                f"attempted_target={target!r}, target_scope={target_scope!r}, "
                f"request_route_token={request_route_token!r}, request_cache_token={request_cache_token!r}, "
                f"run_id={self.run_id!r}"
            )
        if target_scope != runtime["target_scope"]:
            raise _BrRefreshIdentityError(
                "BR binding refresh scope is outside the approved table scope: "
                f"target_scope={target_scope!r}, expected={runtime['target_scope']!r}, run_id={self.run_id!r}"
            )
        request_started_at = runtime["failed_request_started_at"]
        failed_dispatch_id = runtime["failed_dispatch_id"]
        failed_request_assignment_fence = runtime["failed_request_assignment_fence"]
        failed_request_context_token = runtime["failed_request_context_token"]
        failed_request_stage = runtime["failed_request_stage"]
        failed_request_assignment_phase = runtime["failed_request_assignment_phase"]
        failed_request_assignment_reason = runtime["failed_request_assignment_reason"]
        failed_request_cache_phase = runtime["failed_request_cache_phase"]
        failed_request_event_time = runtime["failed_request_event_time"]
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT attempt_id, dispatch_id, target_scope, request_context_token, request_assignment_fence, "
                f"request_started_at, event_time, request_stage, execution_phase, execution_reason, attempt_sequence, "
                f"operation_name, attempt_state, access_key_fingerprint, http_status "
                f"FROM {runtime['request_attempts_table']} WHERE attempt_id=%s",
                (attempt_id,),
            )
            attempt_rows = cursor.fetchall()
        if len(attempt_rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires one failed-write execution attempt from the request ledger; no state changed: "
                f"attempt_id={attempt_id!r}, failed_dispatch_id={failed_dispatch_id!r}, "
                f"target_scope={target_scope!r}, rows={attempt_rows!r}"
            )
        attempt_row = attempt_rows[0]
        if not (
            str(attempt_row[0]) == attempt_id
            and str(attempt_row[1]) == failed_dispatch_id
            and str(attempt_row[2]) == target_scope
            and str(attempt_row[3]) == failed_request_context_token
            and str(attempt_row[4]) == failed_request_assignment_fence
            and str(attempt_row[5]) == request_started_at
            and str(attempt_row[6]) == failed_request_event_time
            and str(attempt_row[7]) == failed_request_stage
            and str(attempt_row[8]) == failed_request_assignment_phase
            and str(attempt_row[9]) == failed_request_assignment_reason
            and str(attempt_row[11]) == "put_backup_chunk"
            and str(attempt_row[12]) == "failed"
            and int(attempt_row[14]) == 403
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh candidate does not satisfy the complete failed-request identity contract; no state changed: "
                f"attempt_id={attempt_id!r}, target_scope={target_scope!r}, "
                f"operation={attempt_row[11]!r}, attempt_state={attempt_row[12]!r}"
            )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT job_id, target_scope, storage_uri, dispatch_id, http_status, access_key_fingerprint, "
                f"policy_decision, request_stage, request_started_at, event_time, request_assignment_fence, "
                f"request_context_token FROM {runtime['storage_audit_table']} "
                "WHERE dispatch_id=%s AND target_scope=%s AND http_status=403 "
                "AND request_stage=%s AND request_started_at=%s AND event_time=%s "
                "AND request_assignment_fence=%s AND request_context_token=%s",
                (
                    failed_dispatch_id,
                    target_scope,
                    failed_request_stage,
                    request_started_at,
                    failed_request_event_time,
                    failed_request_assignment_fence,
                    failed_request_context_token,
                ),
            )
            audit_rows = cursor.fetchall()
        if (
            len(audit_rows) != 1
            or str(audit_rows[0][3]) != str(attempt_row[1])
            or str(audit_rows[0][5]) != str(attempt_row[13])
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh request ledger does not map to one failed storage audit event; no state changed: "
                f"attempt_id={attempt_id!r}, failed_dispatch_id={failed_dispatch_id!r}, "
                f"request_started_at={request_started_at!r}, event_time={failed_request_event_time!r}, "
                f"audit_rows={audit_rows!r}"
            )
        if request_context_token != failed_request_context_token:
            raise _BrRefreshIdentityError(
                "BR binding refresh request context does not identify the failed request; no state changed: "
                f"supplied_context={request_context_token!r}, failed_context={failed_request_context_token!r}, "
                f"target_scope={target_scope!r}, request_route_token={request_route_token!r}, "
                f"request_cache_token={request_cache_token!r}"
            )
        supplied_phases = {
            "request_stage": request_stage,
            "assignment_phase": assignment_phase,
            "assignment_reason": assignment_reason,
            "cache_phase": cache_phase,
        }
        failed_phases = {
            "request_stage": failed_request_stage,
            "assignment_phase": failed_request_assignment_phase,
            "assignment_reason": failed_request_assignment_reason,
            "cache_phase": failed_request_cache_phase,
        }
        if supplied_phases != failed_phases:
            raise _BrRefreshIdentityError(
                "BR binding refresh execution phase does not identify the failed request; no state changed: "
                f"supplied={supplied_phases!r}, failed={failed_phases!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT route_token, dispatch_id, target_scope, executor_handle, lease_token, route_generation, "
                f"valid_from, valid_to, route_state, assignment_phase, route_reason, request_assignment_fence, request_context_token "
                f"FROM {runtime['dispatch_routes_table']} "
                "WHERE route_token=%s AND dispatch_id=%s AND target_scope=%s "
                "AND valid_from <= %s AND (valid_to IS NULL OR valid_to > %s) "
                "AND request_assignment_fence=%s AND request_context_token=%s",
                (
                    request_route_token,
                    failed_dispatch_id,
                    target_scope,
                    request_started_at,
                    request_started_at,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            route_rows = cursor.fetchall()
        if len(route_rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires the request-time route for the failed dispatch: "
                f"request_route_token={request_route_token!r}, failed_dispatch_id={failed_dispatch_id!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}, rows={route_rows!r}"
            )
        route_row = route_rows[0]
        if (
            str(route_row[11]) != request_assignment_fence
            or str(route_row[12]) != request_context_token
            or request_assignment_fence != failed_request_assignment_fence
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh route assignment fence/context is not the failed request identity; no state changed: "
                f"request_route_token={request_route_token!r}, supplied_fence={request_assignment_fence!r}, "
                f"supplied_context={request_context_token!r}, failed_fence={failed_request_assignment_fence!r}, "
                f"failed_context={failed_request_context_token!r}, route_fence={route_row[11]!r}, "
                f"route_context={route_row[12]!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        if (
            str(route_row[3]) != runtime["target_executor_handle"]
            or str(route_row[4]) != runtime["target_lease_token"]
            or int(route_row[5]) != 3001
            or str(route_row[8]) != "released"
            or str(route_row[9]) != assignment_phase
            or str(route_row[10]) != assignment_reason
            ):
            raise _BrRefreshIdentityError(
                "BR binding refresh route is not the failed request data-plane executor: "
                f"request_route_token={request_route_token!r}, failed_dispatch_id={failed_dispatch_id!r}, "
                f"target_scope={target_scope!r}, route={route_row!r}"
            )
        route_generation = int(route_row[5])
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT assignment_id, executor_handle, lease_token, assignment_generation, worker_handle, "
                f"target_scope, valid_from, valid_to, assignment_state "
                f"FROM {runtime['worker_registry_table']} "
                "WHERE executor_handle=%s AND lease_token=%s AND assignment_generation=%s "
                "AND target_scope=%s AND valid_from <= %s AND (valid_to IS NULL OR valid_to > %s)",
                (
                    runtime["target_executor_handle"],
                    runtime["target_lease_token"],
                    route_generation,
                    target_scope,
                    request_started_at,
                    request_started_at,
                ),
            )
            registry_rows = cursor.fetchall()
        if len(registry_rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires one request-time worker registry assignment: "
                f"request_route_token={request_route_token!r}, lease_token={runtime['target_lease_token']!r}, "
                f"assignment_generation={route_generation}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, rows={registry_rows!r}"
            )
        registry_row = registry_rows[0]
        if (
            str(registry_row[1]) != runtime["target_executor_handle"]
            or str(registry_row[2]) != runtime["target_lease_token"]
            or int(registry_row[3]) != route_generation
            or str(registry_row[4]) != runtime["target_worker_handle"]
            or str(registry_row[5]) != target_scope
            or str(registry_row[8]) != "active"
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh registry assignment is not the failed request identity: "
                f"request_route_token={request_route_token!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, registry={registry_row!r}"
            )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT lease_id, lease_token, assignment_generation, authority_epoch, worker_id, target_scope, change_ref, request_assignment_fence, request_context_token, execution_phase, execution_reason "
                f"FROM {runtime['worker_leases_table']} "
                "WHERE lease_token=%s AND assignment_generation=%s AND target_scope=%s "
                "AND valid_from <= %s AND (valid_to IS NULL OR valid_to > %s) "
                "AND request_assignment_fence=%s AND request_context_token=%s",
                (
                    runtime["target_lease_token"],
                    route_generation,
                    target_scope,
                    request_started_at,
                    request_started_at,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            worker_lease_rows = cursor.fetchall()
        if len(worker_lease_rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires one request-time worker lease identity: "
                f"request_route_token={request_route_token!r}, lease_token={runtime['target_lease_token']!r}, "
                f"assignment_generation={route_generation}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, rows={worker_lease_rows!r}"
            )
        worker_lease_row = worker_lease_rows[0]
        if (
            str(worker_lease_row[7]) != request_assignment_fence
            or str(worker_lease_row[8]) != request_context_token
            or str(worker_lease_row[9]) != assignment_phase
            or str(worker_lease_row[10]) != assignment_reason
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh worker lease fence/context does not identify the failed request; no state changed: "
                f"request_route_token={request_route_token!r}, supplied_fence={request_assignment_fence!r}, "
                f"supplied_context={request_context_token!r}, worker_lease_fence={worker_lease_row[7]!r}, "
                f"worker_lease_context={worker_lease_row[8]!r}, worker_lease_phase={worker_lease_row[9]!r}, "
                f"worker_lease_reason={worker_lease_row[10]!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}"
            )
        # r9: under epoch_from_observation the lease-table epoch columns lag the
        # controller's live promoted epoch, so the supplied epoch is verified
        # against the runtime live epoch instead of the stale table column.
        if runtime.get("epoch_from_observation"):
            if authority_epoch != runtime["live_authority_epoch"]:
                raise _BrRefreshIdentityError(
                    "BR binding refresh authority epoch does not identify the failed worker lease; no state changed: "
                    f"supplied_authority_epoch={authority_epoch!r}, request_route_token={request_route_token!r}, "
                    f"target={target!r}, target_scope={target_scope!r}, request_started_at={request_started_at!r}"
                )
        elif str(worker_lease_row[3]) != authority_epoch:
            raise _BrRefreshIdentityError(
                "BR binding refresh authority epoch does not identify the failed worker lease; no state changed: "
                f"supplied_authority_epoch={authority_epoch!r}, request_route_token={request_route_token!r}, "
                f"target={target!r}, target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        if (
            str(worker_lease_row[1]) != runtime["target_lease_token"]
            or int(worker_lease_row[2]) != route_generation
            or str(worker_lease_row[4]) != target
            or str(worker_lease_row[5]) != target_scope
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh worker lease is not the failed request identity: "
                f"request_route_token={request_route_token!r}, target={target!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}, "
                f"worker_lease={worker_lease_row!r}"
            )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT cache_token, route_token, target_scope, worker_handle, material_handle, cache_phase, "
                f"valid_from, valid_to, cache_state, change_ref, request_assignment_fence, request_context_token FROM {runtime['request_cache_table']} "
                "WHERE cache_token=%s AND target_scope=%s "
                "AND valid_from <= %s AND (valid_to IS NULL OR valid_to > %s) "
                "AND request_assignment_fence=%s AND request_context_token=%s",
                (
                    request_cache_token,
                    target_scope,
                    request_started_at,
                    request_started_at,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            rows = cursor.fetchall()
        if len(rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires one request cache snapshot joined to the failed route: "
                f"request_route_token={request_route_token!r}, request_cache_token={request_cache_token!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}, rows={rows!r}"
            )
        cache_row = rows[0]
        if str(cache_row[10]) != request_assignment_fence or str(cache_row[11]) != request_context_token:
            raise _BrRefreshIdentityError(
                "BR binding refresh request cache fence/context does not identify the failed request; no state changed: "
                f"request_route_token={request_route_token!r}, request_cache_token={request_cache_token!r}, "
                f"supplied_fence={request_assignment_fence!r}, cache_fence={cache_row[10]!r}, "
                f"supplied_context={request_context_token!r}, cache_context={cache_row[11]!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        if (
            str(cache_row[3]) != runtime["target_worker_handle"]
            or str(cache_row[4]) != runtime["target_material_handle"]
            or str(cache_row[5]) != cache_phase
            or str(cache_row[8]) != "serving"
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh request cache token is not the failed request assignment snapshot: "
                f"request_route_token={request_route_token!r}, request_cache_token={request_cache_token!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}, "
                f"worker_handle={cache_row[3]!r}, material_handle={cache_row[4]!r}, "
                f"cache_phase={cache_row[5]!r}, expected_cache_phase={cache_phase!r}, cache_state={cache_row[8]!r}"
            )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT material_handle, credential_id, target_scope, storage_uri, material_status, valid_from, valid_to "
                f"FROM {runtime['worker_materials_table']} WHERE material_handle=%s",
                (str(cache_row[4]),),
            )
            material_rows = cursor.fetchall()
        if len(material_rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires one material row for the failed request cache: "
                f"material_handle={cache_row[4]!r}, target_scope={target_scope!r}, rows={material_rows!r}"
            )
        material_row = material_rows[0]
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT grant_id, credential_id, grant_scope, grant_uri, grant_state, valid_from, valid_to "
                f"FROM {runtime['credential_grants_table']} WHERE grant_id IN (%s, %s)",
                (observed_authority_grant_id, desired_authority_grant_id),
            )
            grant_rows = cursor.fetchall()
        if len(grant_rows) != 2:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires distinct observed and desired authority grant rows: "
                f"observed_authority_grant_id={observed_authority_grant_id!r}, "
                f"desired_authority_grant_id={desired_authority_grant_id!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, rows={grant_rows!r}"
            )
        grants_by_id = {int(row[0]): row for row in grant_rows}
        observed_grant = grants_by_id[observed_authority_grant_id]
        desired_grant = grants_by_id[desired_authority_grant_id]

        def valid_at(grant: tuple) -> bool:
            grant_valid_from = str(grant[5])
            grant_valid_to = None if grant[6] is None else str(grant[6])
            return (
                str(grant[4]) == "active"
                and grant_valid_from <= request_started_at
                and (grant_valid_to is None or grant_valid_to > request_started_at)
            )

        if not (
            observed_authority_grant_id != desired_authority_grant_id
            and int(observed_grant[0]) == observed_authority_grant_id
            and int(observed_grant[1]) == int(material_row[1])
            and str(material_row[2]) == target_scope
            and valid_at(observed_grant)
            and not (str(observed_grant[2]) == target_scope and str(observed_grant[3]) == runtime["storage"])
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh observed authority grant does not identify the failed material's non-production authority; no state changed: "
                f"observed_authority_grant_id={observed_authority_grant_id!r}, material={material_row!r}, "
                f"grant={observed_grant!r}, target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        if not (
            int(desired_grant[0]) == desired_authority_grant_id
            and int(desired_grant[1]) == int(runtime["desired_credential_id"])
            and str(desired_grant[2]) == target_scope
            and str(desired_grant[3]) == runtime["storage"]
            and valid_at(desired_grant)
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh desired authority grant does not cover the failed production request; no state changed: "
                f"desired_authority_grant_id={desired_authority_grant_id!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, grant={desired_grant!r}"
            )
        if derive_desired_from_grants:
            with self._ensure_connection().cursor() as cursor:
                cursor.execute(
                    f"SELECT grant_id FROM {runtime['credential_grants_table']} "
                    "WHERE credential_id=%s AND grant_scope=%s AND grant_uri=%s AND grant_state='active' "
                    "AND valid_from<=%s AND (valid_to IS NULL OR valid_to>%s)",
                    (
                        int(runtime["desired_credential_id"]),
                        target_scope,
                        runtime["storage"],
                        request_started_at,
                        request_started_at,
                    ),
                )
                derived_grant_ids = [int(row[0]) for row in cursor.fetchall()]
            if derived_grant_ids != [desired_authority_grant_id]:
                raise _BrRefreshIdentityError(
                    "BR binding refresh desired authority grant is not the unique request-time-valid "
                    "production grant derived from the control-plane credential and the grants window; no state changed: "
                    f"desired_authority_grant_id={desired_authority_grant_id!r}, derived_grant_ids={derived_grant_ids!r}, "
                    f"desired_credential_id={int(runtime['desired_credential_id'])}, target_scope={target_scope!r}, "
                    f"request_started_at={request_started_at!r}"
                )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT lease_id, lease_token, assignment_generation, authority_epoch, target_scope, observed_grant_id, desired_grant_id, "
                f"observed_revision, desired_revision, lease_state, valid_from, valid_to, change_ref, request_assignment_fence, request_context_token, execution_phase, execution_reason "
                f"FROM {runtime['authority_leases_table']} WHERE lease_id=%s",
                (authority_lease_id,),
            )
            authority_lease_rows = cursor.fetchall()
        if len(authority_lease_rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires one authority grant lease row: "
                f"authority_lease_id={authority_lease_id!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, rows={authority_lease_rows!r}"
            )
        authority_lease = authority_lease_rows[0]
        if (
            str(authority_lease[13]) != request_assignment_fence
            or str(authority_lease[14]) != request_context_token
            or str(authority_lease[15]) != assignment_phase
            or str(authority_lease[16]) != assignment_reason
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh authority lease fence/context does not identify the failed request; no state changed: "
                f"authority_lease_id={authority_lease_id!r}, supplied_fence={request_assignment_fence!r}, "
                f"authority_fence={authority_lease[13]!r}, supplied_context={request_context_token!r}, "
                f"authority_context={authority_lease[14]!r}, authority_phase={authority_lease[15]!r}, "
                f"authority_reason={authority_lease[16]!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}"
            )
        change_refs = {
                "cache": str(cache_row[9]),
                "worker_lease": str(worker_lease_row[6]),
                "authority_lease": str(authority_lease[12]),
                "target": str(runtime["target_change_ref"]),
            }
        if len(set(change_refs.values())) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh change_ref does not identify one rotation watch across the failed request cache, worker lease, and authority lease; no state changed: "
                f"request_route_token={request_route_token!r}, request_cache_token={request_cache_token!r}, "
                f"authority_lease_id={authority_lease_id!r}, change_refs={change_refs!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        if runtime.get("epoch_from_observation"):
            if authority_epoch != runtime["live_authority_epoch"]:
                raise _BrRefreshIdentityError(
                    "BR binding refresh authority epoch does not identify the failed authority lease; no state changed: "
                    f"supplied_authority_epoch={authority_epoch!r}, authority_lease_id={authority_lease_id!r}, "
                    f"target_scope={target_scope!r}, request_started_at={request_started_at!r}"
                )
        elif str(authority_lease[3]) != authority_epoch:
            raise _BrRefreshIdentityError(
                "BR binding refresh authority epoch does not identify the failed authority lease; no state changed: "
                f"supplied_authority_epoch={authority_epoch!r}, authority_lease_id={authority_lease_id!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        lease_valid_from = str(authority_lease[10])
        lease_valid_to = None if authority_lease[11] is None else str(authority_lease[11])
        if not (
            int(authority_lease[0]) == authority_lease_id
            and str(authority_lease[1]) == runtime["target_lease_token"]
            and int(authority_lease[2]) == route_generation
            and str(authority_lease[4]) == target_scope
            and int(authority_lease[5]) == observed_authority_grant_id
            and int(authority_lease[6]) == (0 if derive_desired_from_grants else desired_authority_grant_id)
            and int(authority_lease[7]) < int(authority_lease[8])
            and str(authority_lease[9]) == "stale"
            and lease_valid_from <= request_started_at
            and (lease_valid_to is None or lease_valid_to > request_started_at)
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh authority grant lease is not the stale failed-request lease; no state changed: "
                f"authority_lease_id={authority_lease_id!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, lease={authority_lease!r}"
            )
        with self._ensure_connection().cursor() as cursor:
            # r9: under epoch_from_observation the row still carries the
            # pre-promotion epoch column, so the update matches on the stored
            # row epoch and converges the row onto the live promoted epoch.
            row_epoch = str(authority_lease[3])
            cursor.execute(
                f"UPDATE {runtime['authority_leases_table']} SET observed_grant_id=%s, observed_revision=%s, "
                "lease_state='converged', authority_epoch=%s WHERE lease_id=%s AND lease_token=%s AND assignment_generation=%s "
                "AND authority_epoch=%s AND target_scope=%s AND request_assignment_fence=%s AND request_context_token=%s",
                (
                    desired_authority_grant_id,
                    int(authority_lease[8]),
                    authority_epoch,
                    authority_lease_id,
                    runtime["target_lease_token"],
                    route_generation,
                    row_epoch,
                    target_scope,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    "SF06 authority grant lease refresh updated an unexpected row count: "
                    f"run_id={self.run_id!r}, authority_lease_id={authority_lease_id!r}, "
                    f"target_scope={target_scope!r}, rowcount={cursor.rowcount}"
                )
        previous = self._br_binding_propagation(runtime)[0]
        runtime["observed_binding_id"] = runtime["desired_binding_id"]
        runtime["observed_revision"] = runtime["desired_revision"]
        runtime["observed_material_handle"] = runtime["correct_material_handle"]
        runtime["request_cache_material_handle"] = runtime["correct_material_handle"]
        runtime["observed_access_key"] = runtime["correct_access_key"]
        runtime["observed_secret_key"] = runtime["correct_secret_key"]
        self._update_br_worker_lease(runtime)
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"UPDATE {runtime['request_cache_table']} "
                "SET cache_state='serving', change_ref=%s, request_assignment_fence=%s "
                "WHERE target_scope=%s AND cache_phase='retry_data_plane' "
                "AND cache_state='standby'",
                (
                    "br-rotation-watch-20260801-2359-refresh",
                    runtime["retry_assignment_fence"],
                    runtime["target_scope"],
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    "SF06 request material cache refresh updated an unexpected row count: "
                    f"run_id={self.run_id!r}, target_scope={runtime['target_scope']!r}, "
                    f"rowcount={cursor.rowcount}"
                )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"UPDATE {runtime['bindings_relation']} SET credential_id=%s "
                "WHERE binding_id=%s AND target_scope=%s AND role='primary' "
                "AND binding_state='effective'",
                (
                    int(runtime["desired_credential_id"]),
                    int(runtime["desired_binding_id"]),
                    runtime["target_scope"],
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    "SF06 effective binding refresh updated an unexpected row count: "
                    f"run_id={self.run_id!r}, binding_id={runtime['desired_binding_id']!r}, "
                    f"target_scope={runtime['target_scope']!r}, rowcount={cursor.rowcount}"
                )
        current = self._br_binding_propagation(runtime)[0]
        return {
            "acknowledged": True,
            "worker_id": target,
            "target_scope": target_scope,
            "authority_epoch": authority_epoch,
            "observed_authority_grant_id": observed_authority_grant_id,
            "desired_authority_grant_id": desired_authority_grant_id,
            "authority_lease_id": authority_lease_id,
            "request_assignment_fence": request_assignment_fence,
            "request_context_token": request_context_token,
            "previous": previous,
            "current": current,
        }

    def _update_br_worker_lease(self, runtime: Dict[str, Any]) -> None:
        row_epoch = runtime["target_authority_epoch"]
        # r9: under epoch_from_observation the converged worker lease also
        # advances onto the live promoted epoch.
        target_epoch = (
            runtime.get("live_authority_epoch")
            if runtime.get("epoch_from_observation")
            else row_epoch
        )
        sql = (
            f"UPDATE {runtime['worker_leases_table']} "
            "SET observed_binding_id=%s, observed_revision=%s, "
            "observed_material_handle=%s, lease_state='converged', "
            "authority_epoch=%s, last_heartbeat='2026-08-01 23:59:58' "
            "WHERE lease_id=%s AND lease_token=%s AND assignment_generation=%s "
                "AND authority_epoch=%s AND target_scope=%s AND request_assignment_fence=%s AND request_context_token=%s"
        )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                sql,
                (
                    int(runtime["desired_binding_id"]),
                    int(runtime["desired_revision"]),
                    runtime["correct_material_handle"],
                    target_epoch,
                    int(runtime["target_lease_id"]),
                    runtime["target_lease_token"],
                    int(runtime["target_assignment_generation"]),
                    row_epoch,
                    runtime["target_scope"],
                    runtime["target_assignment_fence"],
                    runtime["target_request_context"],
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    "SF06 worker lease refresh updated an unexpected row count: "
                    f"run_id={self.run_id!r}, worker={runtime['target_worker']!r}, "
                    f"target_scope={runtime['target_scope']!r}, rowcount={cursor.rowcount}"
                )

    def _read_br_effective_binding(self, runtime: Dict[str, Any]) -> Dict[str, object]:
        sql = (
            f"SELECT b.binding_id, b.credential_id, b.role, b.binding_state, "
            f"b.effective_from, b.effective_to, b.change_ticket, "
            f"c.profile_name, c.status "
            f"FROM {runtime['bindings_relation']} b "
            f"JOIN {runtime['credentials_relation']} c ON c.credential_id = b.credential_id "
            "WHERE b.target_scope = %s AND b.binding_state = 'effective' "
            "ORDER BY b.effective_from DESC, b.binding_id DESC"
        )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(sql, (runtime["target_scope"],))
            rows = cursor.fetchall()
        if len(rows) != 1:
            raise RuntimeError(
                "SF06 effective BR runtime binding is not unique: "
                f"run_id={self.run_id!r}, target_scope={runtime['target_scope']!r}, rows={rows!r}"
            )
        row = rows[0]
        return {
            "binding_id": int(row[0]),
            "credential_id": int(row[1]),
            "role": str(row[2]),
            "binding_state": str(row[3]),
            "effective_from": str(row[4]),
            "effective_to": None if row[5] is None else str(row[5]),
            "change_ticket": str(row[6]),
            "profile_name": str(row[7]),
            "credential_status": str(row[8]),
        }

    def inspect_br_backup_state(self) -> Dict[str, object]:
        runtime = self._require_br_backup_runtime()
        objects = self._list_br_objects(runtime)
        return {
            "last_result": self._last_br_backup_result,
            "objects": list(objects),
            "object_count": len(objects),
            "has_backupmeta": any("backupmeta" in item.casefold() for item in objects),
            "desired_binding": self._read_br_effective_binding(runtime),
            "effective_binding": self._read_br_effective_binding(runtime),
            "propagation": self._br_binding_propagation(runtime),
            "storage_observations": self._br_storage_observations(runtime),
            "request_cache": self._br_request_cache_state(runtime),
        }

    def base_snapshot_name(self, case) -> Optional[str]:
        return self.deployment.base_image_snapshot_name()

    def snapshot_name(self, scenario_id: str, case) -> Optional[str]:
        return self.deployment.image_group_snapshot_name()

    def disable_image_group(self) -> None:
        self.deployment.disable_image_group()

    def snapshot_exists(self, snapshot_name: str) -> bool:
        return self.deployment.image_group_exists(snapshot_name)

    def select_snapshot(self, snapshot_name: str, base_snapshot_name: str) -> None:
        self.deployment.select_image_group(snapshot_name, base_snapshot_name)

    def save_snapshot(self, snapshot_name: str, labels: Dict[str, str]) -> None:
        self.deployment.save_image_group(snapshot_name, labels)

    def _connect(
        self,
        database: Optional[str] = None,
        application_name: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        target: Optional[str] = None,
    ):
        if timeout_seconds is None:
            timeout_seconds = self.sql_timeout_seconds
        if target is None:
            host, port = self.host, self.port
        else:
            if target not in self.deployment.tidb_endpoints:
                raise ValueError(
                    f"Unknown TiDB SQL target {target!r}; "
                    f"expected one of {sorted(self.deployment.tidb_endpoints)}"
            )
            host, port = self.deployment.tidb_endpoints[target]
        return self._connect_at(
            host,
            port,
            database=database,
            application_name=application_name,
            read_timeout=timeout_seconds,
            write_timeout=timeout_seconds,
        )

    def _connect_at(
        self,
        host: str,
        port: int,
        *,
        database: Optional[str] = None,
        application_name: Optional[str] = None,
        read_timeout: int = SQL_TIMEOUT_SECONDS,
        write_timeout: int = SQL_TIMEOUT_SECONDS,
        password: Optional[str] = None,
    ):
        import pymysql
        from pymysql.constants import CLIENT

        conn = pymysql.connect(
            host=host,
            port=port,
            user=self.user,
            password=self.password if password is None else password,
            database=database,
            charset="utf8mb4",
            autocommit=True,
            connect_timeout=5,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            client_flag=CLIENT.MULTI_STATEMENTS,
        )
        if application_name:
            with conn.cursor() as cur:
                cur.execute("SET @aiopsbench_application_name = %s", (application_name,))
        return conn

    def deploy(self):
        if self.workload is not None:
            self.workload.prepare()
        self.deployment.deploy()
        if not isinstance(self.deployment, TiDBDockerDeployment):
            raise TypeError(
                f"TiDBEnv requires TiDBDockerDeployment for deploy, got {type(self.deployment).__name__}"
            )
        try:
            if self.deployment.image_group_reused:
                print(
                    f"[Env:TiDBEnv] Skipping init SQL because TiDB data image was reused: "
                    f"snapshot={self.deployment.image_group_name!r}, "
                    f"image_group_key={self.deployment.image_group_key!r}"
                )
            elif self.deployment.persistent_state_reused:
                print(
                    f"[Env:TiDBEnv] Skipping init SQL because persistent baseline was reused: "
                    f"storage_key={self.deployment.storage_key!r}"
                )
            else:
                self._execute_init_sql()
                if self.deployment.persistent_storage_enabled:
                    self.deployment.persist_initial_state()
        finally:
            self.deployment.release_persistence_lock()
            self.deployment.release_image_group_lock()
        self.reconnect()
        self._visible_since = time.time()
        self._log_visible_lines = {
            target: len(self.deployment.read_logs(target, lines=10000).splitlines())
            for target in self.deployment.list_nodes()
        }

    def _execute_init_sql(self):
        if self.workload is None:
            conn = self._connect(
                timeout_seconds=self.BOOTSTRAP_SQL_TIMEOUT_SECONDS,
            )
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS {self.dbname}")
            conn.close()
            return
        path = self.workload.get_init_sql_path()
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"TiDB init SQL not found: run_id={self.run_id!r}, path={path!r}"
            )
        with open(path, encoding="utf-8") as handle:
            sql = handle.read()
        conn = self._connect(
            timeout_seconds=self.BOOTSTRAP_SQL_TIMEOUT_SECONDS,
        )
        with conn.cursor() as cur:
            cur.execute(sql)
            while cur.nextset():
                pass
        conn.close()

    def teardown(self):
        self._sql_metric_sampler.stop()
        self._pd_metric_sampler.stop()
        self._stop_workload_runner()
        if self._conn is not None:
            self._conn.close()
            self._conn = None
        if self._secondary_conn is not None:
            self._secondary_conn.close()
            self._secondary_conn = None
        self._secondary_password = None
        if self._history_sql_archive is not None:
            self._history_sql_archive.close()
            self._history_sql_archive = None
        self.deployment.teardown()

    def _ensure_connection(self, target: str = "primary"):
        if target == "primary":
            if self._conn is not None:
                try:
                    self._conn.ping(reconnect=False)
                    return self._conn
                except Exception:
                    self._conn.close()
                    self._conn = None
            self._conn = self._connect(
                self.dbname,
                timeout_seconds=self.sql_timeout_seconds,
            )
            return self._conn
        if target == "replica":
            if (
                self._secondary_host is None
                or self._secondary_port is None
                or self._secondary_password is None
            ):
                raise RuntimeError(
                    f"TiDB secondary endpoint is not configured: run_id={self.run_id!r}"
                )
            if self._secondary_conn is not None:
                try:
                    self._secondary_conn.ping(reconnect=False)
                    return self._secondary_conn
                except Exception:
                    self._secondary_conn.close()
                    self._secondary_conn = None
            self._secondary_conn = self._connect_at(
                self._secondary_host,
                self._secondary_port,
                database=self.dbname,
                read_timeout=self.sql_timeout_seconds,
                write_timeout=self.sql_timeout_seconds,
                password=self._secondary_password,
            )
            return self._secondary_conn
        raise ValueError(
            f"Unsupported TiDB SQL target {target!r}; expected 'primary' or 'replica'"
        )

    def configure_secondary_endpoint(self, host: str, port: int, password: str) -> None:
        if self._secondary_conn is not None:
            self._secondary_conn.close()
            self._secondary_conn = None
        self._secondary_host = host
        self._secondary_port = int(port)
        self._secondary_password = password

    def clear_secondary_endpoint(self) -> None:
        if self._secondary_conn is not None:
            self._secondary_conn.close()
            self._secondary_conn = None
        self._secondary_host = None
        self._secondary_port = None
        self._secondary_password = None

    def configure_replication_endpoint(
        self,
        host: str,
        port: int,
        changefeed_id: str,
        container_name: str,
        downstream_container_name: str,
        *,
        target: str,
        max_cpu_limit: float,
        max_downstream_cpu_limit: float,
        sink_uri: str,
    ) -> None:
        parsed_sink_uri = urlsplit(str(sink_uri))
        sink_parameters = dict(parse_qsl(parsed_sink_uri.query, keep_blank_values=True))
        required_parameters = {"worker-count", "max-txn-row", "batch-dml-enable"}
        missing_parameters = sorted(required_parameters - sink_parameters.keys())
        if missing_parameters:
            raise ValueError(
                "TiDB replication endpoint sink URI is missing execution parameters: "
                f"changefeed_id={changefeed_id!r}, missing={missing_parameters!r}, sink_uri={sink_uri!r}"
            )
        self._replication_endpoint = {
            "host": host,
            "port": int(port),
            "changefeed_id": changefeed_id,
            "container_name": container_name,
            "downstream_container_name": downstream_container_name,
            "target": target,
            "max_cpu_limit": float(max_cpu_limit),
            "max_downstream_cpu_limit": float(max_downstream_cpu_limit),
            "sink_uri": str(sink_uri),
        }

    def clear_replication_endpoint(self) -> None:
        self._replication_endpoint = None

    def current_tso(self) -> int:
        conn = self._connect()
        try:
            conn.begin()
            with conn.cursor() as cur:
                cur.execute("SELECT @@tidb_current_ts AS current_tso")
                rows = cur.fetchall()
            conn.rollback()
        finally:
            conn.close()
        if len(rows) != 1 or len(rows[0]) != 1:
            raise RuntimeError(
                f"TiDB current TSO query returned an invalid result: run_id={self.run_id!r}, rows={rows!r}"
            )
        tso = int(rows[0][0])
        if tso <= 0:
            raise RuntimeError(
                f"TiDB current TSO must be positive after starting a transaction: run_id={self.run_id!r}, tso={tso}"
            )
        return tso

    def _replication_metric(self) -> str:
        if self._replication_endpoint is None:
            raise RuntimeError(f"TiCDC endpoint is not configured: run_id={self.run_id!r}")
        from urllib.request import urlopen

        endpoint = self._replication_endpoint
        url = (
            f"http://{endpoint['host']}:{endpoint['port']}/api/v1/changefeeds/"
            f"{endpoint['changefeed_id']}"
        )
        with urlopen(url, timeout=5) as response:
            changefeed = json.load(response)
        source_tso = self.current_tso()
        checkpoint_tso = int(changefeed["checkpoint_tso"])
        if checkpoint_tso <= 0:
            raise RuntimeError(
                f"TiCDC checkpoint TSO must be positive: changefeed_id={endpoint['changefeed_id']!r}, "
                f"checkpoint_tso={checkpoint_tso}"
            )
        if source_tso < checkpoint_tso:
            raise RuntimeError(
                f"TiDB current TSO is older than TiCDC checkpoint: changefeed_id={endpoint['changefeed_id']!r}, "
                f"source_tso={source_tso}, checkpoint_tso={checkpoint_tso}"
            )
        source_physical_ms = source_tso >> 18
        checkpoint_physical_ms = checkpoint_tso >> 18
        lag_seconds = round((source_physical_ms - checkpoint_physical_ms) / 1000, 3)
        if lag_seconds < 0:
            raise RuntimeError(
                f"TiCDC checkpoint lag must be non-negative: changefeed_id={endpoint['changefeed_id']!r}, "
                f"source_tso={source_tso}, checkpoint_tso={checkpoint_tso}, lag_seconds={lag_seconds}"
            )
        return self._metric_success(
            "replication",
            "snapshot",
            snapshot={
                "changefeed_id": endpoint["changefeed_id"],
                "replication_target": endpoint["target"],
                "state": changefeed["state"],
                "error": changefeed.get("error"),
                "upstream_tso": source_tso,
                "checkpoint_tso": checkpoint_tso,
                "checkpoint_time": changefeed["checkpoint_time"],
                "lag_seconds": lag_seconds,
            },
        )

    def _replication_cpu_limit(self) -> float:
        if self._replication_endpoint is None:
            raise RuntimeError(f"TiCDC endpoint is not configured: run_id={self.run_id!r}")
        endpoint = self._replication_endpoint
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.HostConfig.NanoCpus}}", endpoint["container_name"]],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"TiCDC CPU limit query failed: target={endpoint['target']!r}, "
                f"container={endpoint['container_name']!r}, stdout={result.stdout.strip()!r}, "
                f"stderr={result.stderr.strip()!r}"
            )
        nano_cpus = int(result.stdout.strip())
        if nano_cpus <= 0:
            raise RuntimeError(
                f"TiCDC CPU limit must be positive: target={endpoint['target']!r}, "
                f"container={endpoint['container_name']!r}, nano_cpus={nano_cpus}"
            )
        return round(nano_cpus / 1_000_000_000, 3)

    def _replication_downstream_cpu_limit(self) -> float:
        if self._replication_endpoint is None:
            raise RuntimeError(f"TiCDC endpoint is not configured: run_id={self.run_id!r}")
        endpoint = self._replication_endpoint
        result = subprocess.run(
            [
                "docker",
                "inspect",
                "--format",
                "{{.HostConfig.NanoCpus}}",
                endpoint["downstream_container_name"],
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"TiCDC downstream CPU limit query failed: target='downstream/mysql-0', "
                f"container={endpoint['downstream_container_name']!r}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        nano_cpus = int(result.stdout.strip())
        if nano_cpus <= 0:
            raise RuntimeError(
                "TiCDC downstream CPU limit must be positive: "
                f"target='downstream/mysql-0', container={endpoint['downstream_container_name']!r}, "
                f"nano_cpus={nano_cpus}"
            )
        return round(nano_cpus / 1_000_000_000, 3)

    def reconnect(self):
        if self._conn is not None:
            self._conn.close()
        self._conn = self._connect(self.dbname)
        return self._conn

    def open_workload_connection(
        self,
        application_name: str,
        connection_pool: Optional[str] = None,
        *,
        target: Optional[str] = None,
    ):
        if connection_pool is not None and target is not None:
            raise ValueError(
                "TiDB workload connection cannot select both a connection pool and a target: "
                f"application_name={application_name!r}, connection_pool={connection_pool!r}, "
                f"target={target!r}"
            )
        if target is not None:
            if target == "replica":
                return self._connect_at(
                    self._secondary_host,
                    self._secondary_port,
                    database=self.dbname,
                    application_name=application_name,
                    password=self._secondary_password,
                )
            return self._connect(self.dbname, application_name, target=target)
        if not self._connection_routers:
            if connection_pool is not None:
                raise ValueError(
                    "TiDB workload connection pool is not configured: "
                    f"application_name={application_name!r}, connection_pool={connection_pool!r}"
                )
            return self._connect(self.dbname, application_name)
        if connection_pool is None:
            if len(self._connection_routers) != 1:
                raise ValueError(
                    "TiDB workload connection pool is required when multiple routers exist: "
                    f"application_name={application_name!r}, pools={sorted(self._connection_routers)}"
                )
            connection_pool = next(iter(self._connection_routers))
        router = self._connection_routers[connection_pool]
        target = router.target_for_new_connection()
        host, port = self.deployment.tidb_endpoints[target]
        connection = self._connect_at(
            host,
            port,
            database=self.dbname,
            application_name=application_name,
        )
        router.register_connection(connection, target)
        self._connection_router_connections[id(connection)] = connection_pool
        return connection

    def close_workload_connection(self, connection) -> None:
        self._workload_session_setups.pop(id(connection), None)
        connection_pool = self._connection_router_connections.pop(id(connection), None)
        if connection_pool is not None:
            self._connection_routers[connection_pool].release_connection(connection)
        if connection.open:
            connection.close()

    def should_recycle_workload_connection(self, connection) -> bool:
        connection_pool = self._connection_router_connections.get(id(connection))
        if connection_pool is None:
            return False
        return self._connection_routers[connection_pool].should_recycle(connection)

    def invalidate_workload_connections(self) -> None:
        """Invalidate application connections after an internal control-plane write."""
        for router in self._connection_routers.values():
            router.invalidate_connections()
        self._workload_connection_invalidation_generation += 1

    def workload_connection_invalidation_generation(self) -> int:
        return self._workload_connection_invalidation_generation

    def open_long_running_connection(self, application_name: str):
        return self._connect(
            self.dbname,
            application_name,
            timeout_seconds=300,
        )

    def configure_dr_auto_sync(self, case) -> TiDBDrAutoSyncControl:
        """Register the K09-owned DR Auto-Sync control plane for this Case."""
        if self._dr_auto_sync_control is not None:
            raise RuntimeError(
                f"TiDB DR Auto-Sync control is already configured: run_id={self.run_id!r}"
            )
        self.initialize_connection_routers({
            "k09-business-router": {"initial_target": case.primary_endpoint},
        })
        self._dr_auto_sync_control = TiDBDrAutoSyncControl(self, case)
        return self._dr_auto_sync_control

    def dr_replication_control(self) -> TiDBDrAutoSyncControl:
        if self._dr_auto_sync_control is None:
            raise RuntimeError(
                f"K09 DR Auto-Sync control is not configured: run_id={self.run_id!r}"
            )
        return self._dr_auto_sync_control

    def configure_k08_pitr_runtime(self, controller: object) -> None:
        if self._k08_pitr_runtime is not None:
            raise RuntimeError(f"TiDB K08 PITR runtime is already configured: run_id={self.run_id!r}")
        self._k08_pitr_runtime = controller

    def owns_k08_pitr_runtime(self, controller: object) -> bool:
        return self._k08_pitr_runtime is controller

    def clear_k08_pitr_runtime(self) -> None:
        if self._k08_pitr_runtime is None:
            raise RuntimeError(f"TiDB K08 PITR runtime is not configured: run_id={self.run_id!r}")
        self._k08_pitr_runtime = None

    def _require_k08_pitr_runtime(self):
        if self._k08_pitr_runtime is None:
            raise RuntimeError(f"TiDB K08 PITR runtime is not configured: run_id={self.run_id!r}")
        return self._k08_pitr_runtime

    def initialize_connection_routers(self, routers: Dict[str, Dict[str, object]]) -> None:
        if self._connection_routers:
            raise RuntimeError(
                f"TiDB connection routers are already initialized: run_id={self.run_id!r}"
            )
        self._connection_routers = {
            name: TiDBConnectionRouter(
                self.deployment.tidb_endpoints,
                str(config["initial_target"]),
            )
            for name, config in routers.items()
        }

    def connection_router_status(self, router_name: str) -> dict[str, object]:
        if router_name not in self._connection_routers:
            raise RuntimeError(
                f"Unknown TiDB connection router: run_id={self.run_id!r}, "
                f"router={router_name!r}, routers={sorted(self._connection_routers)}"
            )
        return self._connection_routers[router_name].status()

    def connection_router_statuses(self) -> Dict[str, dict[str, object]]:
        if not self._connection_routers:
            raise RuntimeError(
                f"TiDB connection routers are not initialized: run_id={self.run_id!r}"
            )
        return {
            name: router.status()
            for name, router in self._connection_routers.items()
        }

    def set_connection_router_policy(self, router_name: str, policy: str) -> dict[str, object]:
        if router_name not in self._connection_routers:
            raise ValueError(
                f"Unknown TiDB connection router: run_id={self.run_id!r}, "
                f"router={router_name!r}, routers={sorted(self._connection_routers)}"
            )
        return self._connection_routers[router_name].set_policy(policy)

    def register_connection_router_invalidation(
        self,
        name: str,
        *,
        tables: Sequence[str],
        routers: Sequence[str],
    ) -> None:
        normalized_tables = frozenset(str(table).casefold() for table in tables)
        router_names = tuple(str(router) for router in routers)
        missing = sorted(set(router_names) - set(self._connection_routers))
        if missing:
            raise ValueError(
                "TiDB router invalidation references unknown routers: "
                f"name={name!r}, missing={missing!r}, routers={sorted(self._connection_routers)!r}"
            )
        rule = (normalized_tables, router_names)
        existing = self._connection_router_invalidation_rules.get(name)
        if existing is not None and existing != rule:
            raise RuntimeError(
                "TiDB router invalidation registration conflicts: "
                f"name={name!r}, existing={existing!r}, requested={rule!r}"
            )
        self._connection_router_invalidation_rules[name] = rule

    def unregister_connection_router_invalidation(self, name: str) -> None:
        if name not in self._connection_router_invalidation_rules:
            raise ValueError(f"TiDB router invalidation is not registered: name={name!r}")
        del self._connection_router_invalidation_rules[name]

    def _invalidate_connection_routers_for_sql(self, sql_query: str) -> None:
        if not self._connection_router_invalidation_rules:
            return
        if re.match(r"^\s*(?:INSERT|UPDATE|DELETE)\b", sql_query, re.IGNORECASE) is None:
            return
        from sqlglot import exp, parse

        mutated_tables = set()
        for statement in parse(sql_query, read="mysql"):
            if not isinstance(statement, (exp.Insert, exp.Update, exp.Delete)):
                continue
            table = statement.find(exp.Table)
            if table is None:
                raise ValueError(f"TiDB mutation has no target table: sql={sql_query!r}")
            mutated_tables.add(
                f"{table.db}.{table.name}".casefold() if table.db else table.name.casefold()
            )
        invalidated = False
        for tables, routers in self._connection_router_invalidation_rules.values():
            if mutated_tables.isdisjoint(tables):
                continue
            for router_name in routers:
                self._connection_routers[router_name].invalidate_connections()
            invalidated = True
        if invalidated:
            self._workload_connection_invalidation_generation += 1

    def drain_connection_routers(self, target: str) -> Dict[str, dict[str, object]]:
        if not self._connection_routers:
            raise RuntimeError(
                f"TiDB connection routers are not initialized: run_id={self.run_id!r}"
            )
        for router in self._connection_routers.values():
            router.validate_drain(target)
        return {
            name: router.drain(target)
            for name, router in self._connection_routers.items()
        }

    def reset_connection_routers(self) -> None:
        if not self._connection_routers:
            raise RuntimeError(
                f"TiDB connection routers are not initialized: run_id={self.run_id!r}"
            )
        for router in self._connection_routers.values():
            router.reset()
        self._connection_router_connections.clear()
        self._connection_routers = {}

    def probe_database_backends(self) -> dict[str, object]:
        probes = {}
        for target, (host, port) in self.deployment.tidb_endpoints.items():
            connection = self._connect_at(
                host,
                port,
                database=self.dbname,
                application_name=f"rg08-backend-probe-{target.rsplit('/', 1)[1]}",
            )
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
            connection.close()
            if row != (1,):
                raise RuntimeError(
                    f"TiDB backend probe returned an unexpected result: target={target!r}, row={row!r}"
                )
            probes[target] = {"host": host, "port": port, "select_1": True}
        return probes

    def workload_activity_snapshot(self) -> dict[str, object]:
        if self._workload_runner is None:
            raise RuntimeError(
                f"TiDB workload runner is not attached: run_id={self.run_id!r}"
            )
        return self._workload_runner.get_activity(limit=50)

    def workload_activity_observation(self, limit: int = 50) -> str:
        if self._workload_runner is None:
            raise RuntimeError(f"TiDB workload runner is not attached: run_id={self.run_id!r}")
        activity = self._workload_runner.get_activity(limit=limit)
        return self._metric_success(
            "workload_activity",
            "snapshot",
            snapshot={
                "total_runs": activity["total_runs"],
                "active_profiles": activity["active_profiles"],
                "worker_count": activity["worker_count"],
                "window_seconds": activity["window_seconds"],
                "profiles": activity["value"],
            },
        )

    def cluster_info_observation(self) -> str:
        rows = self._query_rows(
            "SELECT TYPE, INSTANCE, VERSION, START_TIME, UPTIME "
            "FROM INFORMATION_SCHEMA.CLUSTER_INFO ORDER BY TYPE, INSTANCE"
        )
        return self._metric_success("cluster_info", "snapshot", snapshot={"nodes": rows})

    def node_health_observation(self) -> str:
        return self._metric_success(
            "node_health", "snapshot", snapshot={"nodes": self.deployment.node_states()}
        )

    def region_count_observation(self, target: Optional[str] = None) -> str:
        return self._region_count_metric(target, None, None)

    def region_health_observation(self) -> str:
        snapshot = self._region_health_snapshot()
        snapshot.update(self.deployment.region_health_observation())
        return self._metric_success(
            "region_health",
            "snapshot",
            snapshot=snapshot,
        )

    def pd_scheduling_observation(self) -> str:
        return self._pd_scheduling_metric()

    def placement_progress_observation(self) -> str:
        rows = self._query_rows("SHOW PLACEMENT")
        return self._metric_success(
            "placement_progress", "snapshot", snapshot={"nodes": rows}
        )

    def replication_observation(self) -> str:
        return self._replication_metric()

    def ticdc_progress_observation(self, target: Optional[str] = None) -> str:
        if getattr(self.deployment, "replication_runtime", None) is not None:
            return self._live_ticdc_progress_metric(target, None)
        return self._ticdc_metric("ticdc_progress", target, None, None)

    def ticdc_pipeline_observation(self, target: Optional[str] = None) -> str:
        return self._ticdc_metric("ticdc_pipeline", target, None, None)

    def gc_progress_observation(self, target: Optional[str] = None) -> str:
        return self._ticdc_metric("gc_progress", target, None, None)

    def _mvcc_gc_status(self) -> dict[str, Any]:
        variables = self._query_rows(
            "SELECT VARIABLE_NAME AS variable_name, VARIABLE_VALUE AS variable_value FROM mysql.tidb "
            "WHERE VARIABLE_NAME IN ('tikv_gc_safe_point', 'tikv_gc_last_run_time', 'tikv_gc_life_time') "
            "ORDER BY VARIABLE_NAME"
        )
        global_variables = self._query_rows(
            "SHOW GLOBAL VARIABLES WHERE Variable_name IN ('tidb_gc_life_time', 'tidb_gc_enable')"
        )
        safe_rows = [r for r in variables if str(r["variable_name"]).casefold() == "tikv_gc_safe_point"]
        if len(safe_rows) != 1:
            raise RuntimeError(f"TiDB GC status requires one safe-point row: rows={safe_rows!r}")
        safe_text = str(safe_rows[0]["variable_value"])
        try:
            safe_ms = int(datetime.strptime(safe_text, "%Y%m%d-%H:%M:%S.%f %z").timestamp() * 1000)
        except ValueError as exc:
            raise RuntimeError(f"TiDB GC safe point has invalid timestamp: value={safe_text!r}") from exc
        pending = []
        for service in self.deployment.COMPONENTS["tikv"]:
            output = self.deployment.exec(f"tikv/{service}", ["wget", "-qO-", "-T", "5", "http://127.0.0.1:20180/metrics"])
            values = [float(line.rsplit(None, 1)[-1]) for line in output.splitlines() if re.match(r"^tikv_engine_pending_compaction_bytes(?:{|\\s)", line)]
            if not values:
                raise RuntimeError(f"TiKV metrics contain no pending compaction series: service={service!r}")
            pending.extend(values)
        docker_root = self.deployment._docker_info()[2]
        current_tso = self.current_tso()
        prometheus_raw = {
            phase: self._prometheus_instant_payload(query)
            for phase, query in {
                "gc_worker": '{__name__=~"tikv_.*gc.*"}',
                "resolve_locks": '{__name__=~".*resolve.*lock.*"}',
                "delete_ranges": '{__name__=~".*delete.*range.*"}',
                "do_gc": '{__name__=~".*do_gc.*"}',
            }.items()
        }
        return {
            "sql_variables": variables,
            "global_variables": global_variables,
            "current_tso": current_tso,
            "gc_safe_point_tso": safe_ms << 18,
            "gc_headroom_seconds": int((current_tso >> 18) / 1000 - safe_ms / 1000),
            "disk_free_bytes": int(shutil.disk_usage(docker_root).free),
            "compaction_pending": int(max(pending)),
            "prometheus_raw": prometheus_raw,
        }

    def slow_queries_observation(self) -> str:
        start, end = self._prometheus_range(None, None)
        rows = self._query_rows(
            "SELECT TIME, INSTANCE, DIGEST, QUERY, QUERY_TIME, PROCESS_TIME, "
            "WAIT_TIME, BACKOFF_TIME, TOTAL_KEYS, PROCESS_KEYS, MEM_MAX, DISK_MAX "
            "FROM INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY "
            "WHERE TIME BETWEEN FROM_UNIXTIME(%s) AND FROM_UNIXTIME(%s) "
            "ORDER BY TIME DESC LIMIT 50",
            (start, end),
        )
        return self._metric_success("slow_queries", "records", records=rows)

    def topsql_observation(self) -> str:
        start, end = self._prometheus_range(None, None)
        rows = self._query_rows(
            "SELECT INSTANCE, RESOURCE_GROUP, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY, "
            "AVG_TOTAL_KEYS, AVG_PROCESSED_KEYS, AVG_MEM, MAX_MEM, AVG_DISK, MAX_DISK "
            "FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY "
            "WHERE SUMMARY_END_TIME >= FROM_UNIXTIME(%s) "
            "AND SUMMARY_BEGIN_TIME <= FROM_UNIXTIME(%s) "
            "ORDER BY SUM_LATENCY DESC LIMIT 50",
            (start, end),
        )
        return self._metric_success("topsql", "records", records=rows)

    def observe_metric(
        self,
        metric: str,
        target: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> str:
        """Trusted scenario/evaluator observation; never registered as an agent tool."""
        metric = metric.casefold()
        if metric == "workload_activity":
            return self.workload_activity_observation(50 if limit is None else limit)
        if metric == "cluster_info":
            return self.cluster_info_observation()
        if metric == "node_health":
            return self.node_health_observation()
        if metric == "region_count":
            return self.region_count_observation(target)
        if metric == "region_health":
            return self.region_health_observation()
        if metric == "pd_scheduling":
            return self.pd_scheduling_observation()
        if metric == "placement_progress":
            return self.placement_progress_observation()
        if metric == "replication":
            return self.replication_observation()
        if metric == "ticdc_progress":
            return self.ticdc_progress_observation(target)
        if metric == "ticdc_pipeline":
            return self.ticdc_pipeline_observation(target)
        if metric == "gc_progress":
            return self.gc_progress_observation(target)
        if metric == "slow_queries":
            return self.slow_queries_observation()
        if metric == "topsql":
            return self.topsql_observation()
        if metric in self.TIME_SERIES_METRICS:
            frame = self._metric_service.query_live(MetricQuery(metric=metric, target=target))
            timestamps = [timestamp for values in frame.timestamps_ms.values() for timestamp in values]
            return render_metric_frame(
                frame,
                available_start_ms=min(timestamps),
                available_end_ms=max(timestamps),
                requested_start_ms=min(timestamps),
                requested_end_ms=max(timestamps),
                step_seconds=frame.step_seconds,
            )
        raise ValueError(f"Unknown trusted TiDB metric: metric={metric!r}")

    @staticmethod
    def _execute_sql_on_connection(connection, sql_query: str, *, bound_result: bool = False) -> str:
        result, columns, row_count, fetched = [], [], 0, 0
        byte_truncated = False
        with connection.cursor() as cur:
            cur.execute(sql_query)
            while True:
                if cur.description:
                    columns = [column[0] for column in cur.description]
                    rows = cur.fetchmany(201)
                    fetched = len(rows)
                    row_count = fetched
                    if bound_result:
                        # agent 面：与 PG 路径同一套边界（单值 2048 字符 + 128KiB
                        # 总量）。宽表（如 information_schema.statements_summary）
                        # 单行可达数百 KB，不设上限时一次查询即可撑爆对话上下文。
                        result, byte_truncated = _bound_sql_rows(rows)
                    else:
                        # 场景内部/评估器面：夹具校验与证据读取需要完整结果。
                        result = rows[:200]
                else:
                    row_count = cur.rowcount
                if not cur.nextset():
                    break
        truncated = fetched > 200 or byte_truncated
        payload = {
            "status": "success",
            "columns": columns,
            "result": result,
            "row_count": row_count,
            "truncated": truncated,
        }
        if truncated and bound_result:
            payload["truncation_hint"] = SQL_TRUNCATION_HINT
        return json.dumps(payload, ensure_ascii=False, default=str)

    def initialize_workload_session(self, connection, profile):
        connection_id = id(connection)
        if connection_id in self._workload_session_setups:
            raise RuntimeError(
                "TiDB workload session was initialized twice: "
                f"profile={profile.name!r}, connection_id={connection_id}"
            )
        with connection.cursor() as cur:
            for statement in profile.connection_setup_statements:
                cur.execute(statement)
            if profile.session_setup is not None:
                self._cache_workload_session_config(cur, connection_id, profile)

    def _cache_workload_session_config(self, cur, connection_id, profile):
        cur.execute(profile.session_setup.config_query)
        rows = cur.fetchall()
        if len(rows) != 1:
            raise RuntimeError(
                "TiDB workload session setup configuration must return exactly one row: "
                f"profile={profile.name!r}, query={profile.session_setup.config_query!r}, "
                f"rows={rows!r}"
            )
        self._workload_session_setups[connection_id] = {
            "configuration": tuple(rows[0]),
            "checkout_number": 0,
        }

    def configure_workload_session(self, connection, profile):
        return None

    def execute_workload_profile(self, connection, profile):
        if profile.transactional:
            connection.begin()
        session_setup_statements = 0
        with connection.cursor() as cur:
            if profile.session_setup is not None:
                connection_id = id(connection)
                if connection_id not in self._workload_session_setups:
                    self._cache_workload_session_config(cur, connection_id, profile)
                state = self._workload_session_setups[connection_id]
                state["checkout_number"] = int(state["checkout_number"]) + 1
                session_setup_statements = profile.session_setup.statement_count(
                    state["configuration"],
                    int(state["checkout_number"]),
                )
                if session_setup_statements < 0:
                    raise ValueError(
                        "TiDB workload session setup count must be non-negative: "
                        f"profile={profile.name!r}, count={session_setup_statements}"
                    )
                for _ in range(session_setup_statements):
                    cur.execute(profile.session_setup.statement)
            cur.execute(profile.sql)
            result_rows = len(cur.fetchall()) if cur.description else cur.rowcount
        if profile.transactional:
            connection.commit() if profile.commit else connection.rollback()
        if self._connection_routers:
            connection_pool = self._connection_router_connections.get(id(connection))
            if connection_pool is None:
                raise RuntimeError(
                    f"TiDB workload connection is not registered: connection_id={id(connection)}"
                )
            router = self._connection_routers[connection_pool]
            if router.should_recycle(connection):
                self.close_workload_connection(connection)
        return {
            "session_setup_statements": session_setup_statements,
            "result_rows": result_rows,
        }

    def attach_workload_runner(self, runner):
        if self._workload_runner is not None:
            raise RuntimeError(f"TiDB workload runner already attached: run_id={self.run_id!r}")
        self._workload_runner = runner

    def begin_workload_observation_window(self, before_reset: Optional[Callable[[], None]] = None) -> None:
        if self._workload_runner is None:
            raise RuntimeError(
                "TiDB workload observation window requires an attached runner: "
                f"run_id={self.run_id!r}"
            )
        self._workload_runner.begin_observation_window(before_reset=before_reset)

    def wait_for_workload_observation_window(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError(
                "TiDB workload observation wait must be non-negative: "
                f"seconds={seconds!r}"
            )
        time.sleep(seconds)

    def attach_import_controller(self, controller) -> None:
        if self._import_controller is not None:
            raise RuntimeError(
                f"TiDB import controller already attached: run_id={self.run_id!r}"
            )
        self._import_controller = controller

    @property
    def import_controller(self):
        if self._import_controller is None:
            raise RuntimeError(f"TiDB import controller is not attached: run_id={self.run_id!r}")
        return self._import_controller

    def _stop_workload_runner(self):
        if self._workload_runner is not None:
            self._workload_runner.stop()
            self._workload_runner = None

    @contextmanager
    def metrics_hidden(self):
        self._metrics_hidden_depth += 1
        try:
            yield
        finally:
            self._metrics_hidden_depth -= 1
            if self._metrics_hidden_depth == 0:
                self._visible_since = time.time()
                self._log_visible_lines = {
                    target: len(self.deployment.read_logs(target, lines=10000).splitlines())
                    for target in self.deployment.list_nodes()
                }

    def _query_rows(
        self,
        sql: str,
        args=(),
        target: str = "primary",
    ) -> List[Dict[str, Any]]:
        import pymysql
        with self._ensure_connection(target).cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql, args)
            return list(cur.fetchall())

    def _require_business_change_case(self):
        if self._case is None:
            raise RuntimeError("TiDB business-change action requires a configured scenario case")
        required = ("database", "table", "row_count")
        missing = [name for name in required if not hasattr(self._case, name)]
        if missing:
            raise RuntimeError(
                f"TiDB business-change action received a case without required fields: "
                f"case={self._case.case_id!r}, missing={missing!r}"
            )
        return self._case

    def _business_checksum(self, case) -> list[dict[str, Any]]:
        return self._query_rows(
            f"SELECT COUNT(*) AS row_count, "
            f"CAST(SUM(amount * 100) AS SIGNED) AS amount_cents, "
            f"CAST(SUM(tenant_id) AS SIGNED) AS tenant_sum "
            f"FROM {case.database}.{case.table}"
        )

    def _canary_queries(self, case) -> tuple[str, ...]:
        table = f"{case.database}.{case.table}"
        return (
            f"SELECT COUNT(*) AS row_count, CAST(SUM(amount * 100) AS SIGNED) AS amount_cents, "
            f"CAST(SUM(tenant_id) AS SIGNED) AS tenant_sum FROM {table}",
            f"SELECT event_type, COUNT(*) AS event_count, "
            f"CAST(SUM(amount * 100) AS SIGNED) AS amount_cents FROM {table} "
            "GROUP BY event_type ORDER BY event_type",
            f"SELECT tenant_id, COUNT(*) AS event_count FROM {table} "
            "GROUP BY tenant_id ORDER BY tenant_id LIMIT 32",
            f"SELECT event_id, event_type, amount FROM {table} "
            "WHERE tenant_id = 17 ORDER BY event_time DESC LIMIT 32",
        )

    def _run_canary_on_endpoint(self, target: str, case) -> dict[str, Any]:
        import pymysql

        host, port = self.deployment.tidb_endpoints[target]
        results = []
        with pymysql.connect(
            host=host,
            port=port,
            user=self.user,
            password=self.password,
            database=case.database,
            charset="utf8mb4",
            autocommit=True,
            connect_timeout=5,
            read_timeout=self.sql_timeout_seconds,
            write_timeout=self.sql_timeout_seconds,
        ) as connection:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                for sql in self._canary_queries(case):
                    cursor.execute(sql)
                    results.append(list(cursor.fetchall()))
        encoded = json.dumps(results, ensure_ascii=False, sort_keys=True, default=str).encode()
        return {
            "target": target,
            "endpoint": f"{host}:{port}",
            "result_digest": hashlib.sha256(encoded).hexdigest(),
            "query_count": len(results),
            "rows": results,
        }

    def _run_upgrade_canary(self, phase: str) -> dict[str, Any]:
        case = self._require_business_change_case()
        if phase not in {"before", "after"}:
            raise ValueError(f"BC01 canary phase must be before or after: phase={phase!r}")
        endpoints = {
            target: self._run_canary_on_endpoint(target, case)
            for target in self.deployment.tidb_endpoints
        }
        digest = hashlib.sha256(
            json.dumps(
                {target: item["result_digest"] for target, item in endpoints.items()},
                sort_keys=True,
            ).encode()
        ).hexdigest()
        event = self.deployment.record_upgrade_event(
            f"canary_{phase}",
            endpoint_count=len(endpoints),
            result_digest=digest,
            endpoints=endpoints,
        )
        return event

    def _create_upgrade_backup(self) -> dict[str, Any]:
        case = self._require_business_change_case()
        checksum = self._business_checksum(case)
        schema = self._query_rows(f"SHOW CREATE TABLE {case.database}.{case.table}")
        payload = {"checksum": checksum, "schema": schema, "rpo": "0"}
        digest = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode()
        ).hexdigest()
        event = self.deployment.record_upgrade_event(
            "backup_created",
            backup_id=f"bc01-{self.run_id}-logical-manifest",
            manifest_digest=digest,
            checksum=checksum,
            schema_digest=hashlib.sha256(
                json.dumps(schema, ensure_ascii=False, sort_keys=True, default=str).encode()
            ).hexdigest(),
            rpo="0",
        )
        return event

    def _run_upgrade_precheck(self) -> dict[str, Any]:
        case = self._require_business_change_case()
        deployment = self.deployment
        readiness = deployment.wait_for_upgrade_precheck()
        cluster_info = self._query_rows(
            "SELECT TYPE, INSTANCE, VERSION FROM information_schema.cluster_info "
            "ORDER BY TYPE, INSTANCE"
        )
        variables = self._query_rows(
            "SELECT VARIABLE_NAME, VARIABLE_VALUE FROM mysql.tidb "
            "WHERE VARIABLE_NAME IN ('new_collation_enabled', 'tidb_server_version') "
            "ORDER BY VARIABLE_NAME"
        )
        event = deployment.record_upgrade_event(
            "upgrade_precheck",
            readiness=readiness,
            current_version=deployment.release.version,
            target_version=deployment.upgrade_release.version if deployment.upgrade_release else None,
            cluster_info=cluster_info,
            compatibility_variables=variables,
            business_table=f"{case.database}.{case.table}",
        )
        return event

    def _prometheus_range(
        self,
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> tuple[float, float]:
        if start_timestamp is None:
            end = time.time()
            return max(self._visible_since, end - self.return_window_seconds), end
        start = start_timestamp.timestamp()
        end = end_timestamp.timestamp()
        visible_since_second = int(self._visible_since)
        if start < visible_since_second:
            raise ValueError(
                "query_metrics.start_timestamp precedes the TiDB metric visibility boundary: "
                f"start_timestamp={start_timestamp:%Y-%m-%d %H:%M:%S}, "
                f"visible_since={datetime.fromtimestamp(self._visible_since):%Y-%m-%d %H:%M:%S}"
            )
        if start < self._visible_since:
            rounding_gap = self._visible_since - start
            if start_timestamp.microsecond and rounding_gap <= 1e-6:
                return self._visible_since, end
        return start, end

    def _prometheus_payload(
        self,
        query: str,
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> list:
        start, end = self._prometheus_range(start_timestamp, end_timestamp)
        return self._prometheus_payload_at_range(query, start, end)

    def _prometheus_payload_at_range(
        self,
        query: str,
        start: float,
        end: float,
    ) -> list:
        from urllib.parse import urlencode
        from urllib.request import urlopen

        params = urlencode({
            "query": query,
            "start": start,
            "end": end,
            "step": self.sample_interval_sec,
        })
        url = f"http://127.0.0.1:{self.deployment.prometheus_port}/api/v1/query_range?{params}"
        with urlopen(url, timeout=5) as response:
            payload = json.load(response)
        result = payload["data"]["result"]
        if payload["status"] != "success":
            raise RuntimeError(
                f"Prometheus query failed: run_id={self.run_id!r}, "
                f"query={query!r}, payload={payload!r}"
            )
        return result

    def _prometheus_instant_payload(self, query: str) -> list[dict[str, Any]]:
        from urllib.parse import urlencode
        from urllib.request import urlopen

        params = urlencode({"query": query})
        url = f"http://127.0.0.1:{self.deployment.prometheus_port}/api/v1/query?{params}"
        with urlopen(url, timeout=5) as response:
            payload = json.load(response)
        if payload["status"] != "success":
            raise RuntimeError(
                f"Prometheus instant query failed: run_id={self.run_id!r}, "
                f"query={query!r}, payload={payload!r}"
            )
        result = payload["data"]["result"]
        if not isinstance(result, list):
            raise TypeError(
                f"Prometheus instant query returned a non-list result: "
                f"run_id={self.run_id!r}, query={query!r}, result={result!r}"
            )
        return result

    def _prometheus_instant_scalar(self, query: str) -> float:
        result = self._prometheus_instant_payload(query)
        if len(result) != 1:
            raise RuntimeError(
                f"Prometheus instant query must return exactly one series: "
                f"run_id={self.run_id!r}, query={query!r}, series={len(result)}"
            )
        return float(result[0]["value"][1])

    @staticmethod
    def _prometheus_samples(result: dict) -> tuple[list[str], list[float]]:
        samples = result["values"]
        return (
            [datetime.fromtimestamp(float(item[0])).strftime("%Y-%m-%d %H:%M:%S") for item in samples],
            [float(item[1]) for item in samples],
        )

    def _prometheus_query(
        self,
        query: str,
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> tuple[list[str], list[float]]:
        result = self._prometheus_payload(query, start_timestamp, end_timestamp)
        if len(result) != 1:
            raise RuntimeError(
                f"Prometheus query must return exactly one series: "
                f"run_id={self.run_id!r}, query={query!r}, series={len(result)}"
            )
        return self._prometheus_samples(result[0])

    def _prometheus_query_at_range(
        self,
        query: str,
        start: float,
        end: float,
    ) -> tuple[list[str], list[float]]:
        result = self._prometheus_payload_at_range(query, start, end)
        if len(result) != 1:
            raise RuntimeError(
                f"Prometheus query must return exactly one series: "
                f"run_id={self.run_id!r}, query={query!r}, series={len(result)}"
            )
        return self._prometheus_samples(result[0])

    def _prometheus_query_by_service(
        self,
        query: str,
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> dict[str, tuple[list[str], list[float]]]:
        return self._prometheus_query_by_label(
            query, self.COMPOSE_SERVICE_LABEL, start_timestamp, end_timestamp
        )

    def _prometheus_query_by_label(
        self,
        query: str,
        label: str,
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> dict[str, tuple[list[str], list[float]]]:
        result = self._prometheus_payload(query, start_timestamp, end_timestamp)
        series = {}
        for item in result:
            key = item["metric"][label]
            if key in series:
                raise RuntimeError(
                    f"Prometheus query returned duplicate {label!r} series: "
                    f"run_id={self.run_id!r}, query={query!r}, value={key!r}"
                )
            series[key] = self._prometheus_samples(item)
        return series

    def _resource_selector(self, target: Optional[str]) -> str:
        labels = [
            f'container_label_com_docker_compose_project="{self.deployment.project_name}"'
        ]
        if target is not None:
            labels.append(
                f'container_label_com_docker_compose_service="{self.deployment.NODES[target]}"'
            )
        return "{" + ",".join(labels) + "}"

    def _metric(self, metric: str, target: str, timestamps, **values):
        return self._metric_success(
            metric,
            "series",
            series={target: {"timestamps": timestamps, **values}},
        )

    def _cpu_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        if target is None:
            selector = self._resource_selector(None)
            query = (
                f"sum by ({self.COMPOSE_SERVICE_LABEL}) "
                f"(rate(container_cpu_usage_seconds_total{selector}[10s]))"
            )
            by_service = self._prometheus_query_by_service(
                query, start_timestamp, end_timestamp
            )
            service_to_target = {
                service: node
                for node, service in self.deployment.NODES.items()
                if node in self.deployment.database_nodes
            }
            missing = sorted(set(service_to_target) - set(by_service))
            if missing:
                raise RuntimeError(
                    f"Prometheus CPU query is missing TiDB services: "
                    f"run_id={self.run_id!r}, services={missing}"
                )
            series = {}
            for service, node in service_to_target.items():
                timestamps, cores = by_service[service]
                cpu_limit = self.deployment.node_cpu_limits[node]
                values = [round(value / cpu_limit * 100, 2) for value in cores]
                series[node] = {
                    "timestamps": timestamps,
                    "percent": values,
                }
            return self._metric_success("cpu", "series", series=series)

        if target not in self.deployment.NODES:
            raise ValueError(
                f"Unknown TiDB target {target!r}; expected one of {self.deployment.list_nodes()}"
            )
        selector = self._resource_selector(target)
        query = f"sum(rate(container_cpu_usage_seconds_total{selector}[10s]))"
        timestamps, cores = self._prometheus_query(
            query, start_timestamp, end_timestamp
        )
        cpu_limit = self.deployment.node_cpu_limits[target]
        values = [round(value / cpu_limit * 100, 2) for value in cores]
        return self._metric("cpu", target, timestamps, percent=values)

    def _resource_metric(
        self,
        metric: str,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        if metric == "cpu":
            return self._cpu_metric(target, start_timestamp, end_timestamp)
        if target is not None and target not in self.deployment.NODES:
            raise ValueError(
                f"Unknown TiDB target {target!r}; expected one of {self.deployment.list_nodes()}"
            )
        template, _ = self.RESOURCE_QUERIES[metric]
        query = template.format(selector=self._resource_selector(target))
        timestamps, values = self._prometheus_query(
            query, start_timestamp, end_timestamp
        )
        value_name = "megabytes" if metric == "disk_usage" else "megabytes_per_second"
        converted = [round(value / 1024**2, 3) for value in values]
        return self._metric(
            metric, target or "cluster", timestamps, **{value_name: converted}
        )

    def _database_service_targets(self, node_type: Optional[str] = None) -> dict[str, str]:
        return {
            service: target
            for target, service in self.deployment.NODES.items()
            if target in self.deployment.database_nodes
            and (node_type is None or target.startswith(f"{node_type}/"))
        }

    def _require_service_series(self, metric: str, expected_services, *series_maps) -> None:
        for series in series_maps:
            missing = sorted(set(expected_services) - set(series))
            if missing:
                raise RuntimeError(
                    f"Prometheus {metric} query is missing TiDB services: "
                    f"run_id={self.run_id!r}, services={missing}"
                )

    def _memory_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        if target is not None and target not in self.deployment.NODES:
            raise ValueError(
                f"Unknown TiDB target {target!r}; expected one of {self.deployment.list_nodes()}"
            )
        selector = self._resource_selector(target)
        group = f" by ({self.COMPOSE_SERVICE_LABEL})" if target is None else ""
        query = (
            f"100 * sum{group}(container_memory_working_set_bytes{selector}) / "
            f"sum{group}(container_spec_memory_limit_bytes{selector})"
        )
        if target is not None:
            timestamps, values = self._prometheus_query(
                query, start_timestamp, end_timestamp
            )
            return self._metric(
                "memory", target, timestamps,
                percent=[round(value, 2) for value in values],
            )

        by_service = self._prometheus_query_by_service(
            query, start_timestamp, end_timestamp
        )
        service_to_target = self._database_service_targets()
        self._require_service_series("memory", service_to_target, by_service)
        series = {}
        for service, node in service_to_target.items():
            timestamps, samples = by_service[service]
            values = [round(value, 2) for value in samples]
            series[node] = {
                "timestamps": timestamps,
                "percent": values,
            }
        return self._metric_success("memory", "series", series=series)

    def _disk_io_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        if target is not None and target not in self.deployment.NODES:
            raise ValueError(
                f"Unknown TiDB target {target!r}; expected one of {self.deployment.list_nodes()}"
            )
        selector = self._resource_selector(target)
        group = f" by ({self.COMPOSE_SERVICE_LABEL})" if target is None else ""
        queries = {
            "read_bytes_per_second": (
                f"sum{group}(rate(container_fs_reads_bytes_total{selector}[10s]))"
            ),
            "write_bytes_per_second": (
                f"sum{group}(rate(container_fs_writes_bytes_total{selector}[10s]))"
            ),
        }
        if target is not None:
            read_timestamps, reads = self._prometheus_query(
                queries["read_bytes_per_second"], start_timestamp, end_timestamp
            )
            write_timestamps, writes = self._prometheus_query(
                queries["write_bytes_per_second"], start_timestamp, end_timestamp
            )
            if read_timestamps != write_timestamps:
                raise RuntimeError(
                    f"Prometheus disk_io timestamps differ: run_id={self.run_id!r}, "
                    f"target={target!r}"
                )
            return self._metric(
                "disk_io", target, read_timestamps,
                read_mb_per_second=[round(value / 1024**2, 3) for value in reads],
                write_mb_per_second=[round(value / 1024**2, 3) for value in writes],
            )

        read_by_service = self._prometheus_query_by_service(
            queries["read_bytes_per_second"], start_timestamp, end_timestamp
        )
        write_by_service = self._prometheus_query_by_service(
            queries["write_bytes_per_second"], start_timestamp, end_timestamp
        )
        service_to_target = self._database_service_targets()
        self._require_service_series(
            "disk_io", service_to_target, read_by_service, write_by_service
        )
        series = {}
        for service, node in service_to_target.items():
            timestamps, reads = read_by_service[service]
            write_timestamps, writes = write_by_service[service]
            if timestamps != write_timestamps:
                raise RuntimeError(
                    f"Prometheus disk_io timestamps differ: run_id={self.run_id!r}, "
                    f"target={node!r}"
                )
            series[node] = {
                "timestamps": timestamps,
                "read_mb_per_second": [round(value / 1024**2, 3) for value in reads],
                "write_mb_per_second": [round(value / 1024**2, 3) for value in writes],
            }
        return self._metric_success("disk_io", "series", series=series)

    def _qps_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        selector = ""
        if target is not None:
            if target not in self.deployment.tidb_endpoints:
                raise ValueError(
                    f"QPS target must be a TiDB node: target={target!r}, "
                    f"expected={list(self.deployment.tidb_endpoints)}"
                )
            selector = f'{{instance="{self.deployment.NODES[target]}:10080"}}'
        query = f"sum(rate(tidb_server_query_total{selector}[10s]))"
        timestamps, values = self._prometheus_query(
            query, start_timestamp, end_timestamp
        )
        return self._metric(
            "qps", target or "cluster", timestamps, queries_per_second=values
        )

    def _latency_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        if start_timestamp is None:
            end_timestamp = datetime.fromtimestamp(time.time())
            start_timestamp = datetime.fromtimestamp(
                max(
                    self._visible_since,
                    end_timestamp.timestamp() - self.return_window_seconds,
                ) + 1e-6
            )
        matcher = ""
        if target is not None:
            if target not in self.deployment.tidb_endpoints:
                raise ValueError(f"query_latency target must be a TiDB node: target={target!r}")
            matcher = f'instance="{self.deployment.NODES[target]}:10080"'
        selector = "{" + matcher + "}" if matcher else ""
        queries = {
            "average_seconds": (
                f"sum(rate(tidb_server_handle_query_duration_seconds_sum{selector}[10s])) / "
                f"sum(rate(tidb_server_handle_query_duration_seconds_count{selector}[10s]))"
            ),
            "p95_seconds": (
                "histogram_quantile(0.95, sum by (le) "
                f"(rate(tidb_server_handle_query_duration_seconds_bucket{selector}[10s])))"
            ),
            "p99_seconds": (
                "histogram_quantile(0.99, sum by (le) "
                f"(rate(tidb_server_handle_query_duration_seconds_bucket{selector}[10s])))"
            ),
        }
        range_start, range_end = self._prometheus_range(
            start_timestamp, end_timestamp
        )
        series = {
            name: self._prometheus_query_at_range(query, range_start, range_end)
            for name, query in queries.items()
        }
        timestamps = series["average_seconds"][0]
        if any(data[0] != timestamps for data in series.values()):
            raise RuntimeError(f"Prometheus latency timestamps differ: run_id={self.run_id!r}")
        return self._metric(
            "query_latency", target or "cluster", timestamps,
            average_ms=[round(value * 1000, 3) for value in series["average_seconds"][1]],
            p95_ms=[round(value * 1000, 3) for value in series["p95_seconds"][1]],
            p99_ms=[round(value * 1000, 3) for value in series["p99_seconds"][1]],
        )

    def _active_connections_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        if target is not None and target not in self.deployment.tidb_endpoints:
            raise ValueError(
                f"active_connections target must be a TiDB node: target={target!r}, "
                f"expected={list(self.deployment.tidb_endpoints)}"
            )
        matcher = (
            f'{{instance="{self.deployment.NODES[target]}:10080"}}'
            if target is not None else ""
        )
        query = f"sum{' by (instance)' if target is None else ''}(tidb_server_connections{matcher})"
        if target is not None:
            timestamps, values = self._prometheus_query(
                query, start_timestamp, end_timestamp
            )
            return self._metric(
                "active_connections", target, timestamps, connections=values
            )

        by_instance = self._prometheus_query_by_label(
            query, "instance", start_timestamp, end_timestamp
        )
        instance_to_target = {
            f"{service}:10080": node
            for service, node in self._database_service_targets("tidb").items()
        }
        self._require_service_series(
            "active_connections", instance_to_target, by_instance
        )
        series = {}
        for instance, node in instance_to_target.items():
            timestamps, values = by_instance[instance]
            series[node] = {
                "timestamps": timestamps,
                "connections": values,
            }
        return self._metric_success(
            "active_connections", "series", series=series
        )

    def _region_count_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        tikv_targets = self._database_service_targets("tikv")
        if target is not None and target not in tikv_targets.values():
            raise ValueError(
                f"region_count target must be a TiKV node: target={target!r}, "
                f"expected={list(tikv_targets.values())}"
            )
        matcher = (
            f',address="{self.deployment.NODES[target]}:20160"'
            if target is not None else ""
        )
        group = " by (address, store)" if target is None else ""
        query = (
            f'max{group}(pd_scheduler_store_status{{type="region_count"{matcher}}})'
        )
        if target is not None:
            timestamps, values = self._prometheus_query(
                query, start_timestamp, end_timestamp
            )
            return self._metric(
                "region_count", target, timestamps,
                regions=[int(value) for value in values],
            )

        result = self._prometheus_payload(query, start_timestamp, end_timestamp)
        by_address = {}
        for item in result:
            address = item["metric"]["address"]
            if address in by_address:
                raise RuntimeError(
                    f"Prometheus region_count query returned duplicate address series: "
                    f"run_id={self.run_id!r}, address={address!r}"
                )
            timestamps, values = self._prometheus_samples(item)
            by_address[address] = (timestamps, [int(value) for value in values])
        address_to_target = {
            f"{service}:20160": node for service, node in tikv_targets.items()
        }
        self._require_service_series("region_count", address_to_target, by_address)
        series = {}
        for address, node in address_to_target.items():
            timestamps, values = by_address[address]
            series[node] = {
                "timestamps": timestamps,
                "regions": values,
            }
        return self._metric_success("region_count", "series", series=series)

    def _region_health_metric(self) -> str:
        return self._metric_success(
            "region_health",
            "snapshot",
            snapshot=self._region_health_snapshot(),
        )

    def _region_health_snapshot(self) -> dict[str, object]:
        total_regions = self._prometheus_instant_scalar(
            'max(pd_scheduler_store_status{type="region_count"})'
        )
        empty_regions = self._prometheus_instant_scalar(
            'max(pd_regions_status{type="empty-region-count"})'
        )
        undersized_regions = self._prometheus_instant_scalar(
            'max(pd_regions_status{type="undersized-region-count"})'
        )
        pending_peer_regions = self._prometheus_instant_scalar(
            'max(pd_regions_status{type="pending-peer-region-count"})'
        )
        if total_regions <= 0:
            raise RuntimeError(
                f"PD reported a non-positive region count: run_id={self.run_id!r}, "
                f"total_regions={total_regions}"
            )
        return {
            "total_regions": int(total_regions),
            "empty_regions": int(empty_regions),
            "empty_ratio": round(empty_regions / total_regions, 6),
            "undersized_regions": int(undersized_regions),
            "pending_peer_regions": int(pending_peer_regions),
        }

    def _pd_scheduling_metric(self) -> str:
        queries = {
            "heartbeat_rate": (
                'sum(rate(pd_scheduler_region_heartbeat{type="report",status="recv"}[30s])) '
                "or vector(0)"
            ),
            "heartbeat_handle_rate": (
                "sum(rate(pd_scheduler_handle_region_heartbeat_duration_seconds_count[30s])) "
                "or vector(0)"
            ),
            "operator_create_rate": (
                'sum(rate(pd_schedule_operators_count{event="create"}[30s])) or vector(0)'
            ),
            "operator_finish_rate": (
                'sum(rate(pd_schedule_operators_count{event="finish"}[30s])) or vector(0)'
            ),
            "merge_operator_create_rate": (
                'sum(rate(pd_schedule_operators_count{event="create",type=~".*merge.*"}[30s])) '
                "or vector(0)"
            ),
            "merge_operator_finish_rate": (
                'sum(rate(pd_schedule_operators_count{event="finish",type=~".*merge.*"}[30s])) '
                "or vector(0)"
            ),
            "region_operator_limit": (
                'max(pd_config_status{type="region-schedule-limit"}) or vector(0)'
            ),
            "pd_cpu_percent": (
                "max(pd_server_cluster_state_cpu_usage) or vector(0)"
            ),
        }
        values = {
            name: round(self._prometheus_instant_scalar(query), 6)
            for name, query in queries.items()
        }
        return self._metric_success("pd_scheduling", "snapshot", snapshot=values)

    def _get_tidb_knowledge_base(self, knowledge_base_mode: str) -> TiDBKnowledgeBase:
        if knowledge_base_mode not in self._tidb_knowledge_bases:
            self._tidb_knowledge_bases[knowledge_base_mode] = TiDBKnowledgeBase(
                knowledge_base_mode=knowledge_base_mode,
            )
        return self._tidb_knowledge_bases[knowledge_base_mode]

    def _search_tidb_knowledge(
        self,
        *,
        query: str,
        source_scope: str,
        top_k: int,
        max_chars_per_result: int,
        knowledge_base_mode: str,
        kb_type: Optional[str] = None,
        component: Optional[str] = None,
    ) -> str:
        try:
            result = self._get_tidb_knowledge_base(knowledge_base_mode).query(
                query=query,
                source_scope=source_scope,
                top_k=top_k,
                kb_type=kb_type,
                component=component,
                max_chars_per_result=max_chars_per_result,
            )
            allowed = {"status", "query", "source_scope", "kb_type", "component", "top_k", "count", "results"}
            projected = {key: value for key, value in result.items() if key in allowed}
            projected["results"] = [
                {key: value for key, value in row.items() if key in {"rank", "score", "title", "version", "kb_type", "component", "source_scope", "content"}}
                for row in result.get("results", [])
            ]
            return json.dumps(projected, ensure_ascii=False, default=str)
        except (FileNotFoundError, ValueError, RuntimeError) as exc:
            return json.dumps({
                "status": "error",
                "error": (
                    f"TiDB knowledge query failed: mode={knowledge_base_mode!r}, "
                    f"query={query!r}, source_scope={source_scope!r}, kb_type={kb_type!r}, "
                    f"component={component!r}, top_k={top_k!r}, "
                    f"max_chars_per_result={max_chars_per_result!r}, error={exc}"
                ),
            }, ensure_ascii=False)

    @Tool(
        description=(
            "检索 TiDB 8.1 官方文档知识库。所有 TiDB 场景使用同一检索接口；"
            "过滤条件只限定文档范围，不提供场景结论或故障状态。"
        ),
        arg_descriptions={
            "query": "面向 TiDB 官方文档的自然语言或精确标识符查询",
            "source_scope": "文档范围: self_managed, cloud, kubernetes, developer, shared, all；默认 all",
            "top_k": "返回结果数量，默认 5，范围 1-20",
            "kb_type": "可选文档分类",
            "component": "可选组件分类",
        },
        definition=TIDB_TOOL_DEFINITIONS["search_knowledge"],
    )
    def search_knowledge(
        self,
        query: str,
        source_scope: str = "all",
        top_k: int = 5,
        kb_type: Optional[str] = None,
        component: Optional[str] = None,
    ) -> str:
        return self._search_tidb_knowledge(
            query=query,
            source_scope=source_scope,
            top_k=top_k,
            kb_type=kb_type,
            component=component,
            max_chars_per_result=1600,
            knowledge_base_mode="hierarchical",
        )

    @Tool(
        description=(
            "查询通用 TiDB 基础资源和服务时序。结果只包含原始时间序列，"
            "SQL-backed 的查询明细、集群表和控制面状态请通过 execute_sql 或 manage_cluster 观察。"
        ),
        arg_descriptions={
            "metric_type": (
                "当前 Case 在 help('query_metrics') 返回的 allowed_metrics 中声明的指标；"
                "非历史 Case 只允许基础资源和服务时序"
            ),
            "target": "稳定节点身份，例如 tikv/tikv-0；不传时返回集群或各服务时序",
            "start_timestamp": "时序指标开始时间，必须与 end_timestamp 同时提供，格式 YYYY-MM-DD HH:mm:ss",
            "end_timestamp": "时序指标结束时间，必须与 start_timestamp 同时提供，格式 YYYY-MM-DD HH:mm:ss",
            "step_seconds": "历史时序采样步长；必须是 Case base step 的正整数倍",
        },
        definition=TIDB_TOOL_DEFINITIONS["query_metrics"],
    )
    def query_metrics(
        self,
        metric_type: str,
        target: Optional[str] = None,
        limit: Optional[int] = None,
        start_timestamp: Optional[str] = None,
        end_timestamp: Optional[str] = None,
        step_seconds: Optional[int] = None,
    ) -> str:
        metric = metric_type.lower()
        try:
            history_spec = getattr(self._case, "frozen_history", None)
            allowed_metrics = (
                frozenset(str(item).casefold() for item in history_spec.required_metrics)
                if history_spec is not None
                else self.TIME_SERIES_METRICS - self.CASE_ONLY_HISTORY_METRICS
            )
            if metric not in allowed_metrics:
                raise ValueError(f"Unknown TiDB metric_type {metric_type!r}")
            if (start_timestamp is None) != (end_timestamp is None):
                raise ValueError(
                    "query_metrics.start_timestamp and query_metrics.end_timestamp must be provided together"
                )
            start_ms = parse_utc_timestamp(start_timestamp, "start_timestamp") if start_timestamp is not None else None
            end_ms = parse_utc_timestamp(end_timestamp, "end_timestamp") if end_timestamp is not None else None
            query = MetricQuery(
                metric=metric,
                target=target,
                start_epoch_ms=start_ms,
                end_epoch_ms=end_ms,
                step_seconds=step_seconds,
            )
            frame = self._metric_service.query_public(query)
            if self._history_timeline is not None:
                available_start_ms = self._history_timeline.visible_start_ms
                available_end_ms = self._history_timeline.visible_end_ms
                requested_start_ms = start_ms if start_ms is not None else available_start_ms
                requested_end_ms = end_ms if end_ms is not None else available_end_ms
                requested_step = step_seconds or (
                    self._history_timeline.base_step_seconds
                    if start_ms is not None
                    else self._history_timeline.overview_step_seconds
                )
            else:
                timestamps = [timestamp for values in frame.timestamps_ms.values() for timestamp in values]
                available_start_ms = min(timestamps)
                available_end_ms = max(timestamps)
                requested_start_ms = start_ms if start_ms is not None else available_start_ms
                requested_end_ms = end_ms if end_ms is not None else available_end_ms
                requested_step = step_seconds or frame.step_seconds
            return bound_metric_result(render_metric_frame(
                frame,
                available_start_ms=available_start_ms,
                available_end_ms=available_end_ms,
                requested_start_ms=requested_start_ms,
                requested_end_ms=requested_end_ms,
                step_seconds=requested_step,
                # Keep explicit evidence windows complete; only compact
                # no-window overviews use the per-target point limit.
                max_points=(
                    (limit if limit is not None else 20)
                    if start_timestamp is None and end_timestamp is None
                    else None
                ),
            ))
        except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
            return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)

    def bind_metric_history(self, timeline: FrozenHistoricalTimeline) -> None:
        if self._case is None or getattr(self._case, "frozen_history", None) is None:
            raise RuntimeError(
                f"Cannot bind metric history to a non-history Case: run_id={self.run_id!r}, case={getattr(self._case, 'case_id', None)!r}"
            )
        if not isinstance(timeline, FrozenHistoricalTimeline):
            raise TypeError(f"TiDB metric history must be FrozenHistoricalTimeline, got {type(timeline).__name__}")
        self._metric_service.bind_history(timeline.metric_provider)
        self._history_timeline = timeline
        spec = self._case.frozen_history
        self._history_sql_archive = FrozenHistoricalSqlArchive(
            timeline.record_store,
            max_rows=min(200, spec.max_history_records_per_response),
            visible_start_ms=timeline.visible_start_ms,
            visible_end_ms=timeline.visible_end_ms,
        )
        self.register_sql_connection_surface(
            "history",
            database="aiops_metric_history",
            description="当前 Case 的只读冻结历史；UTC 时间轴与 query_metrics 一致。只能查询 statement_summary 和 slow_query。",
            query_examples=(
                "SELECT * FROM statement_summary WHERE event_start_utc < '2030-01-01 00:10:00' AND event_end_utc >= '2030-01-01 00:00:00'",
                "SELECT * FROM slow_query WHERE event_time_utc >= '2030-01-01 00:00:00' AND event_time_utc < '2030-01-01 00:10:00'",
            ),
            write_policy="read_only",
        )
        self._configure_tools(self.FROZEN_HISTORY_PUBLIC_TOOLS)

    def get_frozen_history_record_store_for_evaluator(self) -> FrozenHistoricalRecordStore:
        if self._history_timeline is None:
            raise RuntimeError(
                f"TiDB frozen history record store is unavailable before history binding: run_id={self.run_id!r}"
            )
        return self._history_timeline.record_store

    def get_frozen_history_metric_provider_for_evaluator(self) -> FrozenHistoryMetricProvider:
        if self._history_timeline is None:
            raise RuntimeError(
                f"TiDB frozen history metric provider is unavailable before history binding: run_id={self.run_id!r}"
            )
        return self._history_timeline.metric_provider

    def _live_ticdc_progress_metric(
        self,
        changefeed_id: Optional[str],
        start_timestamp: Optional[datetime],
    ) -> str:
        if changefeed_id is None:
            raise ValueError(
                "Live TiCDC ticdc_progress requires target=changefeed_id: "
                f"run_id={self.run_id!r}"
            )
        if start_timestamp is not None:
            raise ValueError(
                "Live TiCDC ticdc_progress is a current snapshot and does not accept a time range: "
                f"changefeed_id={changefeed_id!r}"
            )
        changefeed = self.replication_status(changefeed_id)
        checkpoint_tso = int(changefeed["checkpoint_tso"])
        resolved_tso = int(changefeed["resolved_ts"])
        if checkpoint_tso <= 0 or resolved_tso <= 0:
            raise ReplicationProgressUnavailableError(
                changefeed_id=changefeed_id,
                reason="non_positive_tso",
                state=changefeed.get("state"),
                error=changefeed.get("error"),
                upstream_tso=0,
                resolved_tso=resolved_tso,
                checkpoint_tso=checkpoint_tso,
            )
        if resolved_tso < checkpoint_tso:
            raise ReplicationProgressUnavailableError(
                changefeed_id=changefeed_id,
                reason="resolved_before_checkpoint",
                state=changefeed.get("state"),
                error=changefeed.get("error"),
                upstream_tso=0,
                resolved_tso=resolved_tso,
                checkpoint_tso=checkpoint_tso,
            )
        lag_seconds = round(
            ((resolved_tso >> 18) - (checkpoint_tso >> 18)) / 1000,
            3,
        )
        return self._metric_success(
            "ticdc_progress",
            "snapshot",
            snapshot={
                "changefeed_id": changefeed_id,
                "state": changefeed["state"],
                "error": changefeed.get("error"),
                "resolved_tso": resolved_tso,
                "checkpoint_tso": checkpoint_tso,
                "checkpoint_time": changefeed["checkpoint_time"],
                "lag_seconds": lag_seconds,
            },
        )

    def _ticdc_metric(
        self,
        metric: str,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        family = {
            "ticdc_progress": "progress",
            "ticdc_pipeline": "pipeline",
            "gc_progress": "resource",
        }[metric]
        end = end_timestamp or datetime.now()
        start = start_timestamp or end - timedelta(seconds=self.return_window_seconds)
        clauses = ["family = %s", "sample_ts BETWEEN %s AND %s"]
        parameters = [family, start, end]
        if target is not None:
            clauses.append("target = %s")
            parameters.append(target)
        rows = self._query_rows(
            "SELECT sample_id, sample_ts, component, metric_name, target, value, "
            "text_value, unit FROM benchops.rg06_cdc_metrics WHERE "
            + " AND ".join(clauses)
            + " ORDER BY sample_ts DESC, sample_id DESC LIMIT 200",
            parameters,
        )
        return self._metric_success(
            metric,
            "records",
            window={
                "start_timestamp": start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_timestamp": end.strftime("%Y-%m-%d %H:%M:%S"),
            },
            records=rows,
        )

    @Tool(
        description=(
            "执行当前环境可访问 SQL 连接面上的 SQL，最多返回 200 行。"
            "连接面、用途和查询方式请先通过 help('execute_sql') 获取。"
            "SQL 结果由查询本身决定，不预先聚合为场景结论。"
        ),
        arg_descriptions={
            "sql_query": "要执行的 SQL 语句",
            "target": "连接面名称；先通过 help('execute_sql') 获取当前可用连接面；不传时使用 primary",
        },
        definition=TIDB_TOOL_DEFINITIONS["execute_sql"],
    )
    def execute_sql(self, sql_query: str, target: Optional[str] = None) -> str:
        return self._execute_sql_surface(sql_query, target, enforce_history_guard=True)

    def execute_sql_trusted(self, sql_query: str, target: Optional[str] = None) -> str:
        """Execute current-state SQL for evaluator and injector trusted checks."""
        return self._execute_sql_surface(sql_query, target, enforce_history_guard=False)

    def _execute_sql_surface(
        self,
        sql_query: str,
        target: Optional[str],
        *,
        enforce_history_guard: bool,
    ) -> str:
        import pymysql

        selected_target = target or "primary"
        if enforce_history_guard and self._k08_pitr_runtime is not None:
            self._k08_pitr_runtime.observe_agent_sql(selected_target, sql_query)
        connection = None
        close_connection = True
        try:
            if selected_target == "history":
                if self._history_sql_archive is None:
                    raise RuntimeError(
                        f"TiDB history SQL surface is unavailable: run_id={self.run_id!r}"
                    )
                columns, rows, row_count, truncated = self._history_sql_archive.execute(sql_query)
                payload = {
                    "status": "success",
                    "columns": columns,
                    "result": rows,
                    "row_count": row_count,
                    "truncated": truncated,
                }
                if truncated:
                    payload["truncation_hint"] = SQL_TRUNCATION_HINT
                return json.dumps(payload, ensure_ascii=False, default=str)
            if enforce_history_guard and selected_target != "downstream" and self._history_timeline is not None:
                reject_tidb_public_historical_sql(sql_query)
            self._validate_registered_sql_write_policies(
                sql_query,
                selected_target=selected_target,
                surfaces=self._sql_connection_surfaces,
            )
            if selected_target == "downstream":
                connection = self._downstream_connection()
            elif selected_target == "primary":
                connection = self._ensure_connection()
                close_connection = False
            elif selected_target == "replica":
                connection = self._ensure_connection("replica")
                close_connection = False
            elif selected_target in self._sql_connection_surfaces:
                connection = self._connect(
                    self._sql_connection_surfaces[selected_target].database
                )
            elif selected_target in self.deployment.tidb_endpoints:
                connection = self._connect(self.dbname, target=selected_target)
            else:
                raise ValueError(
                    f"Unknown TiDB SQL connection surface: target={selected_target!r}. "
                    "Call help('execute_sql') to inspect the current connection surfaces."
                )
            result = self._execute_sql_on_connection(
                connection, sql_query, bound_result=enforce_history_guard
            )
            if enforce_history_guard and self._k08_pitr_runtime is not None:
                self._k08_pitr_runtime.observe_agent_sql(selected_target, sql_query)
            self._invalidate_connection_routers_for_sql(sql_query)
            return result
        except (pymysql.MySQLError, ValueError, RuntimeError) as exc:
            return json.dumps({
                "status": "error",
                "error": f"TiDB SQL failed: target={selected_target!r}, query={sql_query!r}, error={exc}",
            }, ensure_ascii=False)
        finally:
            if close_connection and connection is not None:
                connection.close()

    def execute_internal_sql(self, sql_query: str) -> str:
        """Execute scenario-owned SQL on a private control-plane connection."""
        connection = self._connect(self.dbname)
        try:
            result = self._execute_sql_on_connection(connection, sql_query)
            self._invalidate_connection_routers_for_sql(sql_query)
            return result
        finally:
            connection.close()

    def _manage_connection_router(
        self,
        action: str,
        target: str,
        value: Optional[str],
    ) -> str:
        if not self._connection_routers:
            raise RuntimeError(
                f"TiDB connection routers are not initialized: run_id={self.run_id!r}"
            )
        if action == "get_config":
            if target != self.CONNECTION_ROUTER_TARGET or value is not None:
                raise ValueError(
                    "get_config for TiDB connection routers requires target='connection-router' "
                    f"and no value: target={target!r}, value={value!r}"
                )
            payload = {"routers": self.connection_router_statuses()}
        elif action == "set_load_balance":
            if target not in self._connection_routers or value is None:
                raise ValueError(
                    "set_load_balance requires target to be a configured router and value to be "
                    "round_robin or least_connections: "
                    f"target={target!r}, value={value!r}, routers={sorted(self._connection_routers)}"
                )
            payload = self.set_connection_router_policy(target, value)
        elif action == "drain":
            if target not in self.deployment.NODES or value is not None:
                raise ValueError(
                    "drain requires a TiDB backend target and no value: "
                    f"target={target!r}, value={value!r}"
                )
            payload = {"routers": self.drain_connection_routers(target)}
        else:
            raise ValueError(
                f"Unknown TiDB connection-router action: action={action!r}, target={target!r}, "
                f"routers={sorted(self._connection_routers)}"
            )
        return json.dumps(
            {"status": "success", "action": action, "target": target, **payload},
            ensure_ascii=False,
        )

    def _read_tikv_runtime_config(self, target: str) -> dict[str, Any]:
        output = self.deployment.exec(
            target,
            ["sh", "-lc", "wget -qO- --timeout=5 http://127.0.0.1:20180/config"],
        )
        payload = json.loads(output)
        return {
            "storage": {
                "io_rate_limit": payload["storage"]["io-rate-limit"],
            },
        }

    def tikv_io_rate_limit(self, target: str) -> dict[str, Any]:
        return dict(self._read_tikv_runtime_config(target)["storage"]["io_rate_limit"])

    def set_tikv_io_rate_limit(
        self,
        target: str,
        max_bytes_per_sec: int | str,
    ) -> dict[str, Any]:
        key = "storage.io-rate-limit.max-bytes-per-sec"
        body = json.dumps({key: max_bytes_per_sec}, separators=(",", ":"))
        output = self.deployment.exec(
            target,
            [
                "wget", "-qO-", "--timeout=5", "--content-on-error",
                "--method=POST", "--header=Content-Type: application/json",
                f"--body-data={body}", "http://127.0.0.1:20180/config",
            ],
        )
        if output.strip() and output.strip() != "{}":
            payload = json.loads(output)
            if payload.get("error"):
                raise RuntimeError(
                    f"TiKV config update failed: target={target!r}, "
                    f"max_bytes_per_sec={max_bytes_per_sec!r}, response={payload!r}"
                )
        return self.tikv_io_rate_limit(target)

    def _service_states(self) -> Dict[str, Dict[str, Any]]:
        states = self.deployment.node_states()
        return {
            target: {
                key: value
                for key, value in state.items()
                if key != "container_id"
            }
            for target, state in states.items()
        }

    def _control_service(self, operation: str, target: str) -> Dict[str, Any]:
        external = self._replication_endpoint
        if external is not None and target == "ticdc/ticdc-0":
            if operation not in {"start", "stop", "restart"}:
                raise ValueError(
                    f"Unsupported TiCDC service operation: operation={operation!r}"
                )
            completed = subprocess.run(
                ["docker", operation, external["container_name"]],
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"TiCDC service operation failed: operation={operation!r}, "
                    f"target={target!r}, stdout={completed.stdout.strip()!r}, "
                    f"stderr={completed.stderr.strip()!r}"
                )
            return {"target": target, "running": operation != "stop"}
        if target == "pd":
            if operation != "restart":
                raise ValueError(
                    f"Unsupported TiDB PD quorum service operation: operation={operation!r}"
                )
            self.deployment.restart_pd_quorum()
            states = self._service_states()
            pd_names = sorted(name for name in states if name.startswith("pd/"))
            for name in pd_names:
                self.deployment._wait(
                    name,
                    self.deployment._check_pd,
                    self.deployment.warm_tidb_readiness_timeout_sec,
                )
            return {"nodes": pd_names}
        if target not in self.deployment.NODES:
            raise ValueError(
                f"Unknown TiDB service target {target!r}; expected one of {self.deployment.list_nodes()}"
            )
        method = {
            "restart": self.deployment.restart_component,
            "start": self.deployment.start_component,
            "stop": self.deployment.stop_component,
        }[operation]
        method(target)
        if target == "tidb/tidb-0":
            if self._conn is not None:
                self._conn.close()
                self._conn = None
            if operation != "stop":
                self.deployment._wait(
                    target,
                    self.reconnect,
                    self.deployment.warm_tidb_readiness_timeout_sec,
                )
        elif operation != "stop" and target.startswith("pd/"):
            self.deployment._wait(
                target,
                self.deployment._check_pd,
                self.deployment.warm_tidb_readiness_timeout_sec,
            )
        elif operation != "stop" and target.startswith("tikv/"):
            service = target.split("/", 1)[1]
            self.deployment._wait(
                target,
                lambda: self.deployment._check_tikv_target(service),
                self.deployment.warm_tidb_readiness_timeout_sec,
            )
        return {"target": target, "state": self._service_states().get(target)}

    def _resize_service(self, target: str, cpu_limit: float) -> Dict[str, Any]:
        if cpu_limit <= 0:
            raise ValueError(
                f"service resize requires a positive CPU limit: target={target!r}, cpu_limit={cpu_limit!r}"
            )
        external = self._replication_endpoint
        if external is not None and target == external["target"]:
            if cpu_limit > external["max_cpu_limit"]:
                raise ValueError(
                    f"TiCDC resize exceeds the authorized bound: target={target!r}, "
                    f"cpu_limit={cpu_limit!r}, max_cpu_limit={external['max_cpu_limit']!r}"
                )
            previous_cpu_limit = self._replication_cpu_limit()
            completed = subprocess.run(
                ["docker", "update", "--cpus", str(cpu_limit), external["container_name"]],
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"TiCDC resize failed: target={target!r}, cpu_limit={cpu_limit!r}, "
                    f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
                )
            return {
                "target": target,
                "previous_cpu_limit": previous_cpu_limit,
                "cpu_limit": float(cpu_limit),
            }
        if external is not None and target == "downstream/mysql-0":
            if cpu_limit > external["max_downstream_cpu_limit"]:
                raise ValueError(
                    "downstream MySQL resize exceeds the authorized bound: "
                    f"target={target!r}, cpu_limit={cpu_limit!r}, "
                    f"max_cpu_limit={external['max_downstream_cpu_limit']!r}"
                )
            previous_cpu_limit = self._replication_downstream_cpu_limit()
            completed = subprocess.run(
                [
                    "docker",
                    "update",
                    "--cpus",
                    str(cpu_limit),
                    external["downstream_container_name"],
                ],
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    "downstream MySQL resize failed: "
                    f"target={target!r}, cpu_limit={cpu_limit!r}, "
                    f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
                )
            return {
                "target": target,
                "previous_cpu_limit": previous_cpu_limit,
                "cpu_limit": float(cpu_limit),
            }
        raise ValueError(f"service resize is unsupported for target={target!r}")

    def _changefeed_state(self, changefeed_id: str) -> Dict[str, Any]:
        if self._replication_endpoint is not None:
            if changefeed_id != self._replication_endpoint["changefeed_id"]:
                raise ValueError(
                    f"Unknown configured changefeed: target={changefeed_id!r}, "
                    f"expected={self._replication_endpoint['changefeed_id']!r}"
                )
            changefeed = self.replication_status(changefeed_id)
            checkpoint_tso = int(changefeed["checkpoint_tso"])
            resolved_tso = int(changefeed.get("resolved_ts") or changefeed.get("resolved_tso") or self.current_tso())
            if checkpoint_tso <= 0 or resolved_tso <= 0:
                raise RuntimeError(
                    f"TiCDC TSOs must be positive: changefeed_id={changefeed_id!r}, "
                    f"checkpoint_tso={checkpoint_tso}, resolved_tso={resolved_tso}"
                )
            lag_seconds = round(((resolved_tso >> 18) - (checkpoint_tso >> 18)) / 1000, 3)
            return {
                "changefeed_id": changefeed_id,
                "state": changefeed["state"],
                "error": changefeed.get("error"),
                "resolved_tso": resolved_tso,
                "checkpoint_tso": checkpoint_tso,
                "checkpoint_time": changefeed["checkpoint_time"],
                "lag_seconds": lag_seconds,
                "execution_config": self._replication_sink_config(),
            }
        changefeed = self.replication_status(changefeed_id)
        result = {
            "changefeed_id": changefeed_id,
            "state": changefeed.get("state"),
            "error": changefeed.get("error"),
            "checkpoint_tso": changefeed.get("checkpoint_tso"),
            "checkpoint_time": changefeed.get("checkpoint_time"),
        }
        if "resolved_ts" in changefeed:
            result["resolved_tso"] = changefeed["resolved_ts"]
        if "resolved_tso" in changefeed:
            result["resolved_tso"] = changefeed["resolved_tso"]
        return result

    def _replication_sink_config(self) -> dict[str, object]:
        endpoint = self._replication_endpoint
        if endpoint is None:
            raise RuntimeError(f"TiDB replication endpoint is not configured: run_id={self.run_id!r}")
        parsed = urlsplit(endpoint["sink_uri"])
        parameters = dict(parse_qsl(parsed.query, keep_blank_values=True))
        try:
            worker_count = int(parameters["worker-count"])
            max_txn_row = int(parameters["max-txn-row"])
            batch_dml_enable = parameters["batch-dml-enable"].casefold()
        except (KeyError, ValueError) as exc:
            raise ValueError(
                "TiDB replication endpoint sink URI has invalid execution parameters: "
                f"changefeed_id={endpoint['changefeed_id']!r}, sink_uri={endpoint['sink_uri']!r}"
            ) from exc
        if batch_dml_enable not in {"true", "false"}:
            raise ValueError(
                "TiDB replication endpoint batch-dml-enable must be true or false: "
                f"changefeed_id={endpoint['changefeed_id']!r}, value={batch_dml_enable!r}"
            )
        return {
            "worker_count": worker_count,
            "max_txn_row": max_txn_row,
            "batch_dml_enable": batch_dml_enable == "true",
        }

    def _update_replication_sink_config(
        self,
        changefeed_id: str,
        parameters: Dict[str, Any],
    ) -> dict[str, object]:
        endpoint = self._replication_endpoint
        if endpoint is None or changefeed_id != endpoint["changefeed_id"]:
            raise ValueError(
                "TiDB replication execution update requires the registered changefeed: "
                f"requested={changefeed_id!r}, registered="
                f"{None if endpoint is None else endpoint['changefeed_id']!r}"
            )
        allowed = {"max_txn_row", "worker_count", "batch_dml_enable"}
        unknown = sorted(set(parameters) - allowed)
        if unknown:
            raise ValueError(
                "TiDB replication execution update contains unsupported parameters: "
                f"changefeed_id={changefeed_id!r}, unknown={unknown!r}, allowed={sorted(allowed)!r}"
            )
        if not parameters:
            raise ValueError(
                "TiDB replication execution update requires at least one parameter: "
                f"changefeed_id={changefeed_id!r}"
            )
        previous = self._replication_sink_config()
        current = dict(previous)
        if "max_txn_row" in parameters:
            max_txn_row = int(parameters["max_txn_row"])
            if not 1 <= max_txn_row <= 256:
                raise ValueError(
                    "TiDB replication max_txn_row is outside the public range: "
                    f"changefeed_id={changefeed_id!r}, max_txn_row={max_txn_row!r}, allowed=1..256"
                )
            current["max_txn_row"] = max_txn_row
        if "worker_count" in parameters:
            worker_count = int(parameters["worker_count"])
            if not 1 <= worker_count <= 32:
                raise ValueError(
                    "TiDB replication worker_count is outside the public range: "
                    f"changefeed_id={changefeed_id!r}, worker_count={worker_count!r}, allowed=1..32"
                )
            current["worker_count"] = worker_count
        if "batch_dml_enable" in parameters:
            batch_dml_enable = parameters["batch_dml_enable"]
            if not isinstance(batch_dml_enable, bool):
                raise TypeError(
                    "TiDB replication batch_dml_enable must be boolean: "
                    f"changefeed_id={changefeed_id!r}, value={batch_dml_enable!r}"
                )
            current["batch_dml_enable"] = batch_dml_enable

        parsed = urlsplit(endpoint["sink_uri"])
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query.update({
            "worker-count": str(current["worker_count"]),
            "max-txn-row": str(current["max_txn_row"]),
            "batch-dml-enable": "true" if current["batch_dml_enable"] else "false",
        })
        sink_uri = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))
        completed = subprocess.run(
            [
                "docker",
                "exec",
                endpoint["container_name"],
                "/cdc",
                "cli",
                "changefeed",
                "update",
                "--server=http://127.0.0.1:8300",
                "--changefeed-id",
                changefeed_id,
                "--sink-uri",
                sink_uri,
                "--no-confirm",
            ],
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "TiDB replication execution update failed: "
                f"changefeed_id={changefeed_id!r}, requested={parameters!r}, "
                f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
            )
        endpoint["sink_uri"] = sink_uri
        return {
            "changefeed_id": changefeed_id,
            "previous": previous,
            "current": current,
            "controller_acknowledgement": completed.stdout.strip(),
        }

    def _changefeed_lifecycle(self, operation: str, changefeed_id: str) -> Dict[str, Any]:
        if operation not in {"pause", "resume"}:
            raise ValueError(
                f"Unsupported changefeed lifecycle operation: operation={operation!r}"
            )
        output = self._run_ticdc_cli([
            operation,
            "--server=http://127.0.0.1:8300",
            f"--changefeed-id={changefeed_id}",
        ])
        return {"changefeed_id": changefeed_id, "operation": operation, "output": output}

    def _recreate_changefeed(self, changefeed_id: str, start_ts: int) -> Dict[str, Any]:
        if start_ts <= 0:
            raise ValueError(
                f"changefeed recreate requires a positive start_ts: changefeed_id={changefeed_id!r}, start_ts={start_ts}"
            )
        self._run_ticdc_cli([
            "remove",
            "--server=http://127.0.0.1:8300",
            f"--changefeed-id={changefeed_id}",
        ])
        from time import monotonic, sleep
        from urllib.error import HTTPError

        deadline = monotonic() + 60
        while monotonic() < deadline:
            try:
                self.replication_status(changefeed_id)
            except HTTPError as exc:
                if exc.code == 404:
                    break
                if exc.code == 400:
                    body = exc.read().decode("utf-8", errors="replace")
                    if "CDC:ErrChangeFeedNotExists" in body:
                        break
                raise
            sleep(1)
        else:
            raise RuntimeError(
                f"TiCDC changefeed did not disappear after remove: changefeed_id={changefeed_id!r}"
            )
        output = self._run_ticdc_cli([
            "create",
            "--server=http://127.0.0.1:8300",
            "--sink-uri=mysql://root@mysql-0:3306/",
            f"--changefeed-id={changefeed_id}",
            f"--start-ts={int(start_ts)}",
            "--no-confirm",
        ])
        return {
            "changefeed_id": changefeed_id,
            "state": "running",
            "start_ts": int(start_ts),
            "output": output,
        }

    @staticmethod
    def _br_job_result(result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if result is None:
            return None
        keys = (
            "status", "operation", "database", "table", "exit_code", "metrics",
            "attempt_id", "output", "error", "credential_source",
        )
        return {key: result[key] for key in keys if key in result}

    @staticmethod
    def _agent_import_status(status: Dict[str, Any]) -> Dict[str, Any]:
        import_status = status["import"]
        active_job = {
            "job_id": status["job_id"],
            "target": status["target"],
            "state": import_status["state"],
            "phase": import_status["phase"],
            "reconfigure_required": import_status["reconfigure_required"],
            "exit_code": import_status["exit_code"],
            "expected_rows": import_status["expected_rows"],
            "target_rows": import_status["target_rows"],
            "phase1_rows": import_status["phase1_rows"],
            "duration_seconds": import_status["duration_seconds"],
            "source_directory": status["source"]["directory"],
            "checkpoint_directory": status["source"]["checkpoint_directory"],
        }
        return {
            "precheck": status["precheck"],
            "checkpoint_enabled": status["checkpoint_enabled"],
            "safe_bounds": status["safe_bounds"],
            # 列表位置不能携带信号：事故 job 固定排第一就是"第一个=事故"的捷径。
            "jobs": sorted(
                [active_job, *status["other_jobs"]],
                key=lambda job: job["job_id"],
            ),
        }

    @staticmethod
    def _agent_upgrade_precheck_result(details: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "current_version": details["current_version"],
            "target_version": details["target_version"],
            "cluster_info": details["cluster_info"],
            "compatibility_variables": details["compatibility_variables"],
        }

    @staticmethod
    def _agent_upgrade_backup_result(details: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "checksum": details["checksum"],
            "schema": details["schema"],
        }

    @staticmethod
    def _agent_canary_result(phase: str, details: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "phase": phase,
            "endpoints": {
                target: {
                    "endpoint": endpoint["endpoint"],
                    "query_count": endpoint["query_count"],
                    "rows": endpoint["rows"],
                }
                for target, endpoint in details["endpoints"].items()
            },
        }

    @staticmethod
    def _agent_component_change_result(details: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "target": details["target"],
            "component": details["component"],
            "from_version": details["from_version"],
            "to_version": details["to_version"],
        }

    @staticmethod
    def _agent_monitoring_result(details: Dict[str, Any]) -> Dict[str, Any]:
        return {"targets": details["targets"]}

    def execute_bootstrap_sql(self, sql_query: str) -> str:
        """Execute scenario-owned setup SQL without changing the Agent SQL contract."""
        import pymysql

        try:
            connection = self._connect(
                timeout_seconds=self.BOOTSTRAP_SQL_TIMEOUT_SECONDS,
            )
            try:
                return self._execute_sql_on_connection(connection, sql_query)
            finally:
                connection.close()
        except pymysql.MySQLError as exc:
            return json.dumps({
                "status": "error",
                "error": f"TiDB bootstrap SQL failed: query={sql_query!r}, error={exc}",
            }, ensure_ascii=False)

    @Tool(
        description=(
            "对集群资源执行通用观察和维护。resource 表示资源类别，operation 表示通用操作，"
            "target 标识资源，parameters 承载该资源的具体值。返回原始资源状态或操作结果，"
            "不返回场景、故障或修复结论。"
        ),
        arg_descriptions={
            "resource": "service, store, region, mvcc_lock, gc_status, storage_maintenance, unsafe_recovery, pd_identity, pd_recovery, clock_status, dr_replication, restore, operator, scheduler, config, network, router, changefeed_diagnostics, gc_safepoint, changefeed, job, release 或 monitoring",
            "operation": "list, get, start, refresh_binding, stop, restart, update, remove, pause, resume, recreate, wait 或 verify",
            "target": "稳定资源身份；观察集合时可不传",
            "parameters": "资源操作参数，例如标识符、配置值、时间点或等待秒数",
        },
        definition=TIDB_TOOL_DEFINITIONS["manage_cluster"],
    )
    def manage_cluster(
        self,
        resource: str,
        operation: str,
        target: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Run a resource-neutral observation or maintenance operation."""
        parameters = {} if parameters is None else parameters
        try:
            resource = str(resource).casefold()
            operation = str(operation).casefold()
            result: Any
            if resource == "service":
                if operation == "list":
                    result = {
                        "nodes": self._service_states(),
                        "sql_endpoints": sorted(self.deployment.tidb_endpoints),
                    }
                elif operation == "get":
                    if target is None:
                        raise ValueError("manage_cluster service get requires target")
                    external = self._replication_endpoint
                    if external is not None and target == external["target"]:
                        result = {
                            "target": target,
                            "cpu_limit": self._replication_cpu_limit(),
                        }
                    elif external is not None and target == "downstream/mysql-0":
                        result = {
                            "target": target,
                            "cpu_limit": self._replication_downstream_cpu_limit(),
                        }
                    else:
                        states = self._service_states()
                        if target == "cluster":
                            result = {"nodes": states}
                        else:
                            if target not in states:
                                raise ValueError(
                                    f"Unknown service target: target={target!r}, expected={sorted(states)}"
                                )
                            result = {"target": target, "state": states[target]}
                elif operation in {"start", "stop", "restart"}:
                    if target is None:
                        raise ValueError(
                            f"manage_cluster service {operation} requires target"
                        )
                    result = self._control_service(operation, target)
                elif operation in {"scale_out", "scale_in", "replace_disk"}:
                    if target is None:
                        raise ValueError(
                            f"manage_cluster service {operation} requires target"
                        )
                    method = {
                        "scale_out": self.deployment.scale_out_tikv,
                        "scale_in": self.deployment.scale_in_tikv,
                        "replace_disk": self.deployment.replace_tikv_disk,
                    }[operation]
                    result = method(target)
                elif operation in {"upgrade", "rollback"}:
                    if target is None:
                        raise ValueError(
                            f"manage_cluster service {operation} requires target"
                        )
                    method = (
                        self.deployment.upgrade_component
                        if operation == "upgrade"
                        else self.deployment.rollback_component
                    )
                    result = self._agent_component_change_result(method(target))
                elif operation == "resize":
                    if target is None or "cpu_limit" not in parameters:
                        raise ValueError(
                            "manage_cluster service resize requires target and parameters.cpu_limit"
                        )
                    result = self._resize_service(target, float(parameters["cpu_limit"]))
                else:
                    raise ValueError(
                        f"Unsupported service operation: operation={operation!r}"
                    )
            elif resource == "store":
                if operation == "list":
                    payload = self.deployment.pd_request("GET", "/pd/api/v1/stores")
                    self._remember_pd_stores(payload)
                    result = payload
                elif operation == "get":
                    if target is None:
                        raise ValueError("manage_cluster store get requires target")
                    result = self._pd_store(target)
                elif operation == "update":
                    if target is None:
                        raise ValueError("manage_cluster store update requires target")
                    store = self._pd_store(target)
                    if "state" in parameters:
                        state = str(parameters["state"])
                        if state not in {"Offline", "Up"}:
                            raise ValueError(
                                f"Unsupported Store state: target={target!r}, state={state!r}"
                            )
                        result = self.deployment.pd_request(
                            "POST",
                            f"/pd/api/v1/store/{store['id']}/state?state={state}",
                        )
                    elif "rate" in parameters:
                        rate = int(parameters["rate"])
                        if rate <= 0:
                            raise ValueError(
                                f"Store operator rate must be positive: target={target!r}, rate={rate}"
                            )
                        result = self.deployment.pd_request(
                            "POST",
                            f"/pd/api/v1/store/{store['id']}/limit",
                            {"rate": rate},
                        )
                    else:
                        raise ValueError(
                            "manage_cluster store update requires parameters.state or parameters.rate"
                        )
                else:
                    raise ValueError(
                        f"Unsupported store operation: operation={operation!r}"
                    )
            elif resource == "region":
                if operation == "list":
                    if target is None:
                        raise ValueError("manage_cluster region list requires a Store target")
                    store = self._pd_store(target)
                    result = self.deployment.pd_request(
                        "GET", f"/pd/api/v1/regions/store/{store['id']}"
                    )
                    self._observed_region_ids.setdefault(target, set()).update(
                        int(region["id"]) for region in result["regions"]
                    )
                elif operation == "get":
                    if "region_id" not in parameters:
                        raise ValueError("manage_cluster region get requires parameters.region_id")
                    region_id = int(parameters["region_id"])
                    if region_id <= 0:
                        raise ValueError(f"Region ID must be positive: region_id={region_id}")
                    result = self.deployment.pd_request(
                        "GET", f"/pd/api/v1/region/id/{region_id}"
                    )
                    if target is not None:
                        self._observed_region_ids.setdefault(target, set()).add(region_id)
                elif operation == "remove":
                    if target is None or "region_id" not in parameters:
                        raise ValueError(
                            "manage_cluster region remove requires target and parameters.region_id"
                        )
                    region_id = int(parameters["region_id"])
                    store = self._pd_store(target)
                    if region_id not in self._observed_region_ids.get(target, set()):
                        raise ValueError(
                            f"Region must be observed before removal: target={target!r}, region_id={region_id}"
                        )
                    if store.get("state_name") != "Offline":
                        raise ValueError(
                            f"Region removal requires an Offline Store: target={target!r}, store={store!r}"
                        )
                    region = self.deployment.pd_request(
                        "GET", f"/pd/api/v1/region/id/{region_id}"
                    )
                    peer_store_ids = {int(peer["store_id"]) for peer in region.get("peers") or ()}
                    if int(store["id"]) not in peer_store_ids:
                        raise ValueError(
                            f"Region target Store is not a peer: target={target!r}, region_id={region_id}"
                        )
                    if len(peer_store_ids) < 3:
                        raise ValueError(
                            f"Region removal requires at least three peers: region_id={region_id}, peers={sorted(peer_store_ids)}"
                        )
                    result = self.deployment.remove_region_peer(region_id, int(store["id"]))
                else:
                    raise ValueError(
                        f"Unsupported region operation: operation={operation!r}"
                    )
            elif resource == "mvcc_lock":
                if operation not in {"list", "resolve"}:
                    raise ValueError(
                        f"Unsupported mvcc_lock operation: operation={operation!r}"
                    )
                if target is None:
                    raise ValueError("manage_cluster mvcc_lock list requires a Region target")
                region_id = self._mvcc_region_id(target)
                if operation == "list":
                    if set(parameters) != {"store_targets"}:
                        raise ValueError(
                            "mvcc_lock list requires exactly parameters.store_targets; "
                            f"region_id={region_id}, parameters={sorted(parameters)}"
                        )
                    store_targets = parameters["store_targets"]
                    if not isinstance(store_targets, list):
                        raise ValueError(
                            "mvcc_lock list requires parameters.store_targets as a list: "
                            f"region_id={region_id}, store_targets={store_targets!r}"
                        )
                    result = self.deployment.mvcc_lock_list(
                        region_id,
                        store_targets,
                        128,
                    )
                else:
                    if self._mvcc_recovery_guard is not None:
                        if set(parameters) != {"inspection_id", "key", "lock_type", "start_ts"}:
                            raise ValueError(
                                "mvcc_lock resolve requires exactly parameters.inspection_id, "
                                "key, lock_type, start_ts (key-level recovery; region-level "
                                "recovery is unavailable while the Region holds in-flight "
                                f"transaction locks): region_id={region_id}, "
                                f"parameters={sorted(parameters)}"
                            )
                        result = self.deployment.mvcc_lock_resolve_key(
                            region_id,
                            str(parameters["inspection_id"]),
                            str(parameters["key"]),
                            str(parameters["lock_type"]),
                            parameters["start_ts"],
                        )
                    else:
                        if set(parameters) != {"inspection_id"}:
                            raise ValueError(
                                "mvcc_lock resolve requires exactly parameters.inspection_id: "
                                f"region_id={region_id}, parameters={sorted(parameters)}"
                            )
                        result = self.deployment.mvcc_recovery_execute(
                            region_id,
                            str(parameters["inspection_id"]),
                        )
            elif resource == "changefeed_diagnostics":
                if operation == "list":
                    if target is None:
                        raise ValueError("changefeed_diagnostics list requires a capture target")
                    result = self._changefeed_diagnostics("list", target)
                elif operation == "get":
                    if target is None or "capture_target" not in parameters:
                        raise ValueError(
                            "changefeed_diagnostics get requires target=changefeed_id and parameters.capture_target"
                        )
                    result = self._changefeed_diagnostics(
                        "get",
                        str(parameters["capture_target"]),
                        target,
                    )
                else:
                    raise ValueError(
                        f"Unsupported changefeed_diagnostics operation: operation={operation!r}"
                    )
            elif resource == "gc_safepoint":
                if operation == "list":
                    result = self._gc_safepoint_list()
                elif operation == "remove":
                    if target is None:
                        raise ValueError(
                            "manage_cluster gc_safepoint remove requires target=service_id"
                        )
                    result = self._gc_safepoint_remove(target, parameters)
                else:
                    raise ValueError(
                        f"Unsupported gc_safepoint operation: operation={operation!r}"
                    )
            elif resource == "gc_status":
                if operation != "get":
                    raise ValueError(
                        f"Unsupported gc_status operation: operation={operation!r}"
                    )
                result = self._mvcc_gc_status()
                # prometheus_raw is a ~270KB metrics dump that would otherwise
                # persist in the agent conversation for the rest of the run;
                # K01 evaluation still reads it via the direct _mvcc_gc_status path.
                result.pop("prometheus_raw")
            elif resource == "storage_maintenance":
                if operation not in {"preflight", "apply"}:
                    raise ValueError(
                        f"Unsupported storage_maintenance operation: operation={operation!r}"
                    )
                if target is None:
                    raise ValueError(
                        f"manage_cluster storage_maintenance {operation} requires a Region target"
                    )
                region_id = self._mvcc_region_id(target)
                if operation == "preflight" and set(parameters) != {"store_targets"}:
                    raise ValueError(
                        "storage_maintenance preflight requires exactly parameters.store_targets: "
                        f"region_id={region_id}, parameters={sorted(parameters)}"
                    )
                if operation == "preflight":
                    store_targets = parameters["store_targets"]
                    if not isinstance(store_targets, list):
                        raise ValueError(
                            "storage_maintenance preflight requires parameters.store_targets as a list: "
                            f"region_id={region_id}, store_targets={store_targets!r}"
                        )
                    result = self.deployment.mvcc_recovery_inspect(region_id, store_targets)
                    result = dict(result)
                    preflight_id = result.pop("inspection_id")
                    result["preflight_id"] = preflight_id
                else:
                    if set(parameters) != {"preflight_id"}:
                        raise ValueError(
                            "storage_maintenance apply requires exactly parameters.preflight_id: "
                            f"region_id={region_id}, parameters={sorted(parameters)}"
                        )
                    if self._mvcc_recovery_guard is not None:
                        self.deployment.mvcc_recovery_apply_interlock(
                            region_id,
                            str(parameters["preflight_id"]),
                        )
                    result = self.deployment.mvcc_recovery_execute(
                        region_id,
                        str(parameters["preflight_id"]),
                    )
                    result = dict(result)
                    preflight_id = result.pop("inspection_id")
                    result["preflight_id"] = preflight_id
            elif resource == "unsafe_recovery":
                if target is not None:
                    raise ValueError(
                        "manage_cluster unsafe_recovery does not accept target: "
                        f"target={target!r}"
                    )
                if operation == "get":
                    result = {
                        "state": "observed",
                        "output": self.deployment.online_unsafe_recovery("get"),
                    }
                elif operation == "start":
                    if set(parameters) != {"failed_store_ids"}:
                        raise ValueError(
                            "manage_cluster unsafe_recovery start requires exactly parameters.failed_store_ids: "
                            f"parameters={sorted(parameters)!r}"
                        )
                    raw_ids = parameters["failed_store_ids"]
                    if (
                        not isinstance(raw_ids, list)
                        or not raw_ids
                        or any(isinstance(store_id, bool) for store_id in raw_ids)
                    ):
                        raise ValueError(
                            "manage_cluster unsafe_recovery start requires a non-empty integer list: "
                            f"failed_store_ids={raw_ids!r}"
                        )
                    failed_store_ids = tuple(sorted(int(store_id) for store_id in raw_ids))
                    if len(failed_store_ids) != len(raw_ids) or any(
                        store_id <= 0 for store_id in failed_store_ids
                    ):
                        raise ValueError(
                            "manage_cluster unsafe_recovery failed_store_ids must be unique positive integers: "
                            f"failed_store_ids={raw_ids!r}"
                        )
                    result = self.deployment.online_unsafe_recovery(
                        "start",
                        failed_store_ids,
                    )
                else:
                    raise ValueError(
                        f"Unsupported unsafe_recovery operation: operation={operation!r}"
                    )
            elif resource == "pd_identity":
                if operation != "get":
                    raise ValueError(
                        f"Unsupported pd_identity operation: operation={operation!r}"
                    )
                result = self.deployment.pd_identity_observation()
            elif resource == "pd_recovery":
                if operation == "inspect":
                    view = parameters.get("view", "current")
                    if not isinstance(view, str):
                        raise ValueError(
                            "manage_cluster pd_recovery inspect view must be a string: "
                            f"view={view!r}"
                        )
                    phase = parameters.get("phase")
                    if phase is not None and not isinstance(phase, str):
                        raise ValueError(
                            "manage_cluster pd_recovery inspect phase must be a string: "
                            f"phase={phase!r}"
                        )
                    record_id = parameters.get("record_id")
                    if record_id is not None and not isinstance(record_id, str):
                        raise ValueError(
                            "manage_cluster pd_recovery inspect record_id must be a string: "
                            f"record_id={record_id!r}"
                        )
                    result = self.deployment.pd_recovery_inspection(view, phase, target, record_id)
                elif operation == "execute":
                    if target is None:
                        raise ValueError("manage_cluster pd_recovery execute requires a PD target")
                    if not self._clock_status_observed:
                        raise RuntimeError(
                            "manage_cluster pd_recovery execute requires a successful clock_status/list observation: "
                            f"target={target!r}"
                        )
                    required = {"cluster_id", "alloc_id", "recovery_branch", "record_id"}
                    if set(parameters) != required:
                        raise ValueError(
                            "manage_cluster pd_recovery execute requires exactly the evidence-bound parameters: "
                            f"target={target!r}, expected={sorted(required)!r}, parameters={sorted(parameters)!r}"
                        )
                    result = self.deployment.execute_pd_recovery(
                        target,
                        int(parameters["cluster_id"]),
                        int(parameters["alloc_id"]),
                        parameters["recovery_branch"],
                        parameters["record_id"],
                    )
                else:
                    raise ValueError(
                        f"Unsupported pd_recovery operation: operation={operation!r}"
                    )
            elif resource == "clock_status":
                if operation != "list":
                    raise ValueError(
                        f"Unsupported clock_status operation: operation={operation!r}"
                    )
                result = self.deployment.clock_status_observation()
                self._clock_status_observed = True
            elif resource == "dr_replication":
                control = self.dr_replication_control()
                if operation == "get":
                    result = control.snapshot()
                elif operation == "topology":
                    snapshot = control.snapshot()
                    result = {
                        "pd_leader": self.deployment.current_pd_leader(),
                        "stores": snapshot["stores"],
                        "placement": snapshot["placement"],
                        "regions": snapshot["regions"],
                    }
                elif operation == "fence_get":
                    result = control.fence_get()
                elif operation == "fence_apply":
                    if target is None or parameters:
                        raise ValueError(
                            "dr_replication fence_apply requires target and no parameters"
                        )
                    result = control.fence_apply(target)
                elif operation == "transition":
                    if "mode" not in parameters:
                        raise ValueError(
                            "dr_replication transition requires parameters.mode"
                        )
                    if set(parameters) - {"mode", "failed_store_ids"}:
                        raise ValueError(
                            "dr_replication transition accepts only mode and failed_store_ids: "
                            f"parameters={sorted(parameters)}"
                        )
                    result = control.transition(
                        str(parameters["mode"]),
                        failed_store_ids=parameters.get("failed_store_ids"),
                    )
                elif operation == "wait":
                    if set(parameters) != {"mode"}:
                        raise ValueError(
                            "dr_replication wait requires exactly parameters.mode"
                        )
                    result = control.wait(
                        str(parameters["mode"]),
                    )
                else:
                    raise ValueError(
                        f"Unsupported dr_replication operation: operation={operation!r}"
                    )
            elif resource == "restore":
                result = self._require_k08_pitr_runtime().restore_operation(
                    operation, target, parameters
                )
            elif resource == "operator":
                if operation not in {"list", "get"}:
                    raise ValueError(
                        f"Unsupported operator operation: operation={operation!r}"
                    )
                result = self.deployment.pd_request("GET", "/pd/api/v1/operators")
            elif resource == "scheduler":
                if operation in {"list", "get"}:
                    result = self.deployment.pd_request("GET", "/pd/api/v1/schedulers")
                elif operation == "remove":
                    scheduler_type = str(parameters.get("type", ""))
                    store_id = parameters.get("store_id")
                    if target and store_id is None:
                        match = re.fullmatch(
                            r"(evict-leader-scheduler)[/-]([0-9]+)", target
                        )
                        if match:
                            scheduler_type, store_id = match.group(1), int(match.group(2))
                    if scheduler_type != "evict-leader-scheduler" or store_id is None:
                        raise ValueError(
                            "scheduler remove requires the observed scheduler type and store_id"
                        )
                    leader = self.deployment.pd_request("GET", "/pd/api/v1/leader")
                    result = self.deployment.exec(
                        f"pd/{leader['name']}",
                        [
                            "curl", "-fsS", "-X", "DELETE",
                            "http://127.0.0.1:2379/pd/api/v1/scheduler-config/"
                            f"evict-leader-scheduler/delete/{int(store_id)}",
                        ],
                    )
                else:
                    raise ValueError(
                        f"Unsupported scheduler operation: operation={operation!r}"
                    )
            elif resource == "config":
                config_target = target or "pd"
                if operation == "get":
                    if config_target == "pd":
                        result = self.deployment.pd_request("GET", "/pd/api/v1/config")
                    elif config_target.startswith("tikv/"):
                        result = self._read_tikv_runtime_config(config_target)
                    else:
                        raise ValueError(
                            f"Unsupported config target: target={config_target!r}"
                        )
                elif operation == "update":
                    if config_target == "pd":
                        key = parameters.get("key")
                        value = parameters.get("value")
                        if key is None or value is None:
                            raise ValueError(
                                "PD config update requires parameters.key and parameters.value"
                            )
                        if not isinstance(key, str) or not key.startswith("schedule."):
                            raise ValueError(
                                f"PD config updates must target schedule.*: key={key!r}"
                            )
                        normalized = str(value).casefold()
                        if normalized in {"true", "false"}:
                            parsed_value: object = normalized
                        else:
                            try:
                                parsed_value = int(value)
                            except ValueError:
                                parsed_value = str(value)
                        result = self.deployment.pd_request(
                            "POST", "/pd/api/v1/config", {key: parsed_value}
                        )
                    elif config_target.startswith("tikv/"):
                        key = parameters.get("key")
                        value = parameters.get("value")
                        if key != "storage.io-rate-limit.max-bytes-per-sec" or value is None:
                            raise ValueError(
                                "TiKV config update requires key=storage.io-rate-limit.max-bytes-per-sec and value"
                            )
                        observed = self.set_tikv_io_rate_limit(config_target, int(value))
                        result = {"storage": {"io_rate_limit": observed}}
                    else:
                        raise ValueError(
                            f"Unsupported config target: target={config_target!r}"
                        )
                else:
                    raise ValueError(
                        f"Unsupported config operation: operation={operation!r}"
                    )
            elif resource == "network":
                if target is None:
                    raise ValueError("manage_cluster network operation requires target")
                if operation == "get":
                    result = self.deployment.inspect_pd_network(target)
                elif operation == "update":
                    access = parameters.get("access")
                    if access != "allow":
                        raise ValueError(
                            f"Unsupported network access state: target={target!r}, access={access!r}"
                        )
                    self.deployment.allow_pd_network(target)
                    result = self.deployment.inspect_pd_network(target)
                else:
                    raise ValueError(
                        f"Unsupported network operation: operation={operation!r}"
                    )
            elif resource == "router":
                if operation == "get":
                    result = self.connection_router_statuses()
                elif operation == "update":
                    if target is None or "policy" not in parameters:
                        raise ValueError(
                            "router update requires target and parameters.policy"
                        )
                    result = self.set_connection_router_policy(
                        target, str(parameters["policy"])
                    )
                elif operation == "drain":
                    if target is None:
                        raise ValueError("router drain requires a TiDB target")
                    result = self.drain_connection_routers(target)
                else:
                    raise ValueError(
                        f"Unsupported router operation: operation={operation!r}"
                    )
            elif resource == "changefeed":
                if target is None:
                    raise ValueError("manage_cluster changefeed operation requires target")
                if operation == "list":
                    result = self.deployment.changefeed_diagnostics(target)
                elif operation == "get":
                    result = self._changefeed_state(target)
                elif operation == "update":
                    result = self._update_replication_sink_config(target, parameters)
                elif operation in {"pause", "resume"}:
                    result = self._changefeed_lifecycle(operation, target)
                elif operation == "recreate":
                    start_ts = int(parameters.get("start_ts", 0))
                    result = self._recreate_changefeed(target, start_ts)
                else:
                    raise ValueError(
                        f"Unsupported changefeed operation: operation={operation!r}"
                    )
            elif resource == "restore":
                result = self._require_k08_pitr_runtime().restore_operation(
                    operation, target, parameters
                )
            elif resource == "job":
                if operation == "get":
                    if self._import_controller is not None:
                        result = self._agent_import_status(self.import_controller.status())
                    elif self._br_backup_runtime is not None:
                        state = self.inspect_br_backup_state()
                        result = {
                            "last_result": self._br_job_result(state["last_result"]),
                            "objects": state["objects"],
                            "desired_binding": state["desired_binding"],
                        }
                    else:
                        raise RuntimeError(f"No managed external job is configured: run_id={self.run_id!r}")
                elif operation == "check":
                    status = self.import_controller.precheck()
                    result = {
                        "target_rows": status["target_rows"],
                        "output_tail": status["output_tail"],
                    }
                elif operation == "update":
                    required = (
                        "region_concurrency", "disk_quota_mb", "store_write_bwlimit_mib"
                    )
                    missing = [name for name in required if name not in parameters]
                    if missing:
                        raise ValueError(
                            f"job update is missing parameters: missing={missing!r}"
                        )
                    status = self.import_controller.apply_budget(
                        region_concurrency=parameters["region_concurrency"],
                        disk_quota_mb=parameters["disk_quota_mb"],
                        store_write_bwlimit_mib=parameters["store_write_bwlimit_mib"],
                        job_id=parameters.get("job_id"),
                    )
                    result = {"state": status["import_state"]}
                elif operation == "wait":
                    timeout_seconds = int(parameters.get("timeout_seconds", 120))
                    result = self._agent_import_status(
                        self.import_controller.wait(timeout_seconds)
                    )
                elif operation == "observe":
                    if self._br_backup_runtime is None:
                        raise RuntimeError(f"No managed external job is configured: run_id={self.run_id!r}")
                    runtime = self._br_backup_runtime
                    events = list(runtime.get("controller_events", ()))
                    # r10: the default observe window returns only the most
                    # recent controller events; older entries (for example an
                    # epoch promotion before the latest heartbeat burst) must
                    # be read back through the explicit time-window parameters.
                    default_window = 8
                    start_text = parameters.get("start_timestamp")
                    end_text = parameters.get("end_timestamp")
                    if (start_text is None) != (end_text is None):
                        raise ValueError(
                            "job observe start_timestamp and end_timestamp must be provided together"
                        )
                    windowed = events
                    if start_text is not None:
                        windowed = [
                            event for event in events
                            if str(start_text) <= event["at"] <= str(end_text)
                        ]
                    else:
                        windowed = events[:default_window]
                    oldest_at = events[-1]["at"] if events else None
                    result = {
                        "job_kind": "br_backup",
                        "target_scope": runtime["target_scope"],
                        "controller_events": windowed,
                        "event_count": len(windowed),
                        "total_event_count": len(events),
                        "oldest_event_at": oldest_at,
                        "window_applied": start_text is not None,
                    }
                elif operation == "release_prefix_quarantine":
                    if self._br_backup_runtime is None:
                        raise RuntimeError(f"No managed external job is configured: run_id={self.run_id!r}")
                    runtime = self._br_backup_runtime
                    if not runtime.get("storage_prefix_quarantine"):
                        raise ValueError(
                            "release_prefix_quarantine requires parameters.target_prefix, "
                            "parameters.quarantine_ref, and parameters.triggering_change_ref"
                        )
                    required = {"target_prefix", "quarantine_ref", "triggering_change_ref"}
                    if not required.issubset(parameters):
                        raise ValueError(
                            "release_prefix_quarantine is missing parameters: "
                            f"missing={sorted(required - set(parameters))!r}"
                        )
                    result = self._release_br_prefix_quarantine(
                        str(parameters["target_prefix"]),
                        str(parameters["quarantine_ref"]),
                        str(parameters["triggering_change_ref"]),
                    )
                elif operation == "refresh_binding":
                    required = {
                        "target_scope",
                        "request_route_token",
                        "request_cache_token",
                        "attempt_id",
                        "observed_authority_grant_id",
                        "desired_authority_grant_id",
                        "authority_lease_id",
                        "authority_epoch",
                        "request_assignment_fence",
                        "request_context_token",
                        "request_stage",
                        "assignment_phase",
                        "assignment_reason",
                        "cache_phase",
                    }
                    if target is None or not required.issubset(parameters):
                        raise ValueError(
                            "BR binding refresh requires target worker, parameters.target_scope, "
                            "parameters.request_route_token, and the observed failed request "
                            "parameters.request_cache_token and parameters.attempt_id, plus parameters.observed_authority_grant_id and "
                            "parameters.desired_authority_grant_id, parameters.authority_lease_id, and "
                            "parameters.authority_epoch"
                            ", parameters.request_assignment_fence, parameters.request_context_token, "
                            "parameters.request_stage, parameters.assignment_phase, parameters.assignment_reason, "
                            "and parameters.cache_phase"
                        )
                    result = self._refresh_br_binding_cache(
                        target,
                        str(parameters["target_scope"]),
                        str(parameters["request_route_token"]),
                        str(parameters["request_cache_token"]),
                        str(parameters["attempt_id"]),
                        int(parameters["observed_authority_grant_id"]),
                        int(parameters["desired_authority_grant_id"]),
                        int(parameters["authority_lease_id"]),
                        str(parameters["authority_epoch"]),
                        str(parameters["request_assignment_fence"]),
                        str(parameters["request_context_token"]),
                        str(parameters["request_stage"]),
                        str(parameters["assignment_phase"]),
                        str(parameters["assignment_reason"]),
                        str(parameters["cache_phase"]),
                        )
                elif operation == "start":
                    required = ("database", "table")
                    missing = [name for name in required if name not in parameters]
                    if missing:
                        raise ValueError(
                            f"job start is missing parameters: missing={missing!r}"
                        )
                    credential_keys = {"access_key", "secret_key"} & parameters.keys()
                    if credential_keys not in (set(), {"access_key", "secret_key"}):
                        raise ValueError(
                            "BR job start requires both access_key and secret_key for an explicit override: "
                            f"provided={sorted(credential_keys)!r}"
                        )
                    result = self._run_br_backup(
                        parameters["database"],
                        parameters["table"],
                        parameters.get("access_key"),
                        parameters.get("secret_key"),
                    )
                    result = self._br_job_result(result)
                else:
                    raise ValueError(
                        f"Unsupported job operation: operation={operation!r}"
                    )
            elif resource == "restore":
                runtime = self._k08_pitr_runtime
                if runtime is None:
                    raise RuntimeError(
                        f"PITR restore runtime is not configured: run_id={self.run_id!r}"
                    )
                result = runtime.restore_operation(operation, target, parameters)
            elif resource == "unsafe_recovery":
                if operation == "get":
                    result = self.deployment.online_unsafe_recovery("get")
                elif operation == "start":
                    result = self.deployment.online_unsafe_recovery(
                        "start", tuple(int(item) for item in parameters["failed_store_ids"])
                    )
                else:
                    raise ValueError(f"Unsupported unsafe_recovery operation: operation={operation!r}")
            elif resource == "pd_identity":
                if operation != "get":
                    raise ValueError(f"Unsupported pd_identity operation: operation={operation!r}")
                result = self.deployment.pd_identity_observation()
            elif resource == "pd_recovery":
                if operation == "inspect":
                    result = self.deployment.pd_recovery_inspection(
                        view=str(parameters.get("view", "current")),
                        phase=parameters.get("phase"),
                        target=target,
                        record_id=parameters.get("record_id"),
                    )
                elif operation == "execute":
                    result = self.deployment.execute_pd_recovery(target, **parameters)
                else:
                    raise ValueError(f"Unsupported pd_recovery operation: operation={operation!r}")
            elif resource == "release":
                if operation == "get":
                    result = self.deployment.upgrade_agent_observation()
                elif operation not in {"prepare", "snapshot", "verify", "upgrade", "rollback"}:
                    raise ValueError(f"Unsupported release operation: operation={operation!r}")
                elif self.deployment.upgrade_release is None:
                    raise ValueError(
                        "release "
                        + operation
                        + " is unavailable on this case: no upgrade release configured"
                        + f" (current_release={self.deployment.release.version!r})"
                    )
                elif operation == "prepare":
                    details = self._run_upgrade_precheck()
                    result = self._agent_upgrade_precheck_result(details)
                elif operation == "snapshot":
                    result = self._agent_upgrade_backup_result(self._create_upgrade_backup())
                elif operation == "verify":
                    phase = str(parameters.get("phase", ""))
                    if phase not in {"before", "after"}:
                        raise ValueError(
                            "release verify requires parameters.phase=before or after"
                        )
                    details = self._run_upgrade_canary(phase)
                    result = self._agent_canary_result(phase, details)
                elif operation in {"upgrade", "rollback"}:
                    if target is None:
                        raise ValueError(
                            f"release {operation} requires a component target"
                        )
                    method = (
                        self.deployment.upgrade_component
                        if operation == "upgrade"
                        else self.deployment.rollback_component
                    )
                    result = self._agent_component_change_result(method(target))
                else:
                    raise ValueError(
                        f"Unsupported release operation: operation={operation!r}"
                    )
            elif resource == "clock_status":
                if operation != "list":
                    raise ValueError(f"Unsupported clock_status operation: operation={operation!r}")
                result = self.deployment.clock_status_observation()
            elif resource == "mvcc_lock" and operation == "list":
                region_id = int(str(target).split("/", 1)[1])
                result = self.deployment.mvcc_lock_list(region_id, parameters["store_targets"], 128)
            elif resource == "mvcc_lock" and operation == "resolve":
                region_id = int(str(target).split("/", 1)[1])
                result = self.deployment.mvcc_recovery_execute(region_id, parameters["inspection_id"])
            elif resource == "gc_status" and operation == "get":
                result = self._mvcc_gc_status()
            elif resource == "storage_maintenance":
                region_id = int(str(target).split("/", 1)[1])
                if operation == "preflight":
                    result = self.deployment.mvcc_recovery_inspect(region_id, parameters["store_targets"])
                    result["preflight_id"] = result["inspection_id"]
                elif operation == "apply":
                    result = self.deployment.mvcc_recovery_execute(region_id, parameters["preflight_id"])
                else:
                    raise ValueError(f"Unsupported storage_maintenance operation: operation={operation!r}")
            elif resource == "gc_safepoint" and operation == "list":
                result = self.deployment.gc_safepoint_list()
            elif resource == "gc_safepoint" and operation == "remove":
                result = self.deployment.gc_safepoint_remove(str(target))
            elif resource == "monitoring":
                if operation != "get":
                    raise ValueError(
                        f"Unsupported monitoring operation: operation={operation!r}"
                    )
                result = self._agent_monitoring_result(
                    self.deployment.verify_monitoring_coverage()
                )
            else:
                raise ValueError(
                    f"Unknown manage_cluster resource: resource={resource!r}"
                )
            return json.dumps(
                {
                    "status": "success",
                    "resource": resource,
                    "operation": operation,
                    "target": target,
                    "result": result,
                },
                ensure_ascii=False,
                default=str,
            )
        except (ValueError, RuntimeError, OSError, KeyError, json.JSONDecodeError) as exc:
            return json.dumps(
                {
                    "status": "error",
                    "resource": resource,
                    "operation": operation,
                    "target": target,
                    "error": str(exc),
                },
                ensure_ascii=False,
            )

    def execute_sql_with_timeout(self, sql_query: str, timeout_seconds: int) -> str:
        import pymysql

        conn = self._connect(self.dbname, timeout_seconds=timeout_seconds)
        try:
            return self._execute_sql_on_connection(conn, sql_query)
        except pymysql.MySQLError as exc:
            return json.dumps({
                "status": "error",
                "error": f"TiDB SQL failed: query={sql_query!r}, error={exc}",
            }, ensure_ascii=False)
        finally:
            conn.close()

    def _downstream_connection(self):
        import pymysql
        from pymysql.constants import CLIENT

        port = self.deployment.downstream_port
        if port is None:
            raise RuntimeError(f"TiDB replication downstream is not configured: run_id={self.run_id!r}")
        return pymysql.connect(
            host="127.0.0.1",
            port=port,
            user="root",
            password="",
            charset="utf8mb4",
            autocommit=True,
            connect_timeout=5,
            read_timeout=self.sql_timeout_seconds,
            write_timeout=self.sql_timeout_seconds,
            client_flag=CLIENT.MULTI_STATEMENTS,
        )

    def _ticdc_url(self, path: str) -> str:
        port = self.deployment.ticdc_port
        if port is None:
            raise RuntimeError(f"TiCDC is not configured: run_id={self.run_id!r}")
        return f"http://127.0.0.1:{port}{path}"

    def replication_status(self, changefeed_id: str) -> dict:
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", changefeed_id):
            raise ValueError(f"Invalid TiCDC changefeed_id: {changefeed_id!r}")
        from urllib.request import urlopen

        endpoint = self._replication_endpoint
        if endpoint is not None:
            if changefeed_id != endpoint["changefeed_id"]:
                raise ValueError(
                    "External TiCDC status requires the registered changefeed: "
                    f"requested={changefeed_id!r}, registered={endpoint['changefeed_id']!r}"
                )
            url = (
                f"http://{endpoint['host']}:{endpoint['port']}/api/v1/changefeeds/"
                f"{changefeed_id}"
            )
        else:
            url = self._ticdc_url(f"/api/v1/changefeeds/{changefeed_id}")
        with urlopen(url, timeout=5) as response:
            payload = json.load(response)
        if not isinstance(payload, dict):
            raise TypeError(
                f"TiCDC changefeed status must be an object: changefeed_id={changefeed_id!r}, "
                f"payload_type={type(payload).__name__}"
            )
        return payload

    def _run_ticdc_cli(self, arguments: list[str]) -> str:
        endpoint = self._replication_endpoint
        if endpoint is not None:
            completed = subprocess.run(
                [
                    "docker",
                    "exec",
                    endpoint["container_name"],
                    "/cdc",
                    "cli",
                    "changefeed",
                    *arguments,
                ],
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    "External TiCDC CLI command failed: "
                    f"container={endpoint['container_name']!r}, arguments={arguments!r}, "
                    f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
                )
            return completed.stdout.strip()
        return self.deployment.exec("ticdc/ticdc-0", ["/cdc", "cli", "changefeed", *arguments])

    @Tool(
        description="读取指定集群组件的可见日志；默认返回最多 200 行，支持按行号范围或关键字上下文读取。",
        arg_descriptions={
            "target": "稳定组件身份，例如 pd/pd-0、tikv/tikv-0、tidb/tidb-0 或 ticdc/ticdc-0",
            "lines": "尾部行数，默认 200，最大 200",
            "start_line": "可选的 1-based 起始行号；传入后按范围读取日志",
            "end_line": "可选的 1-based 结束行号，闭区间；-1 表示最后一行",
            "match_key": "可选关键字；返回每条命中行的上一行到下两行上下文，大小写不敏感",
            "start_timestamp": "可选的冻结历史窗口起点；必须与 end_timestamp 一起提供",
            "end_timestamp": "可选的冻结历史窗口终点；必须与 start_timestamp 一起提供",
        },
        definition=TIDB_TOOL_DEFINITIONS["read_log"],
    )
    def read_log(
        self,
        target: str,
        lines: int = 200,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        match_key: Optional[str] = None,
        start_timestamp: Optional[str] = None,
        end_timestamp: Optional[str] = None,
    ) -> str:
        page_limit = min(max(int(lines), 1), 200)
        try:
            if (start_timestamp is None) != (end_timestamp is None):
                raise ValueError("read_log.start_timestamp and read_log.end_timestamp must be provided together")
            if start_timestamp is not None:
                if self._history_timeline is None or self._case is None:
                    raise RuntimeError(f"Frozen historical logs are unavailable: run_id={self.run_id!r}")
                if not target:
                    raise ValueError("Historical log reads require an explicit component target")
                start_ms = parse_utc_timestamp(start_timestamp, "start_timestamp")
                end_ms = parse_utc_timestamp(end_timestamp, "end_timestamp")
                if start_ms >= end_ms:
                    raise ValueError(
                        "Historical log window must be positive: "
                        f"start_timestamp={start_timestamp!r}, end_timestamp={end_timestamp!r}"
                    )
                records = self._history_timeline.record_store.query(
                    source=HistoricalRecordSource.COMPONENT_LOG,
                    start_ms=start_ms,
                    end_ms=end_ms,
                    target=target,
                    filters=None,
                    limit=min(page_limit, self._case.frozen_history.max_history_records_per_response),
                )["records"]
                content = "\n".join(
                    f"{record['timestamp']} {record.get('message', '')}" for record in records
                )
                page = self._slice_log_output(content, page_limit, start_line, end_line, match_key)
                page["page_limit"] = page_limit
                return json.dumps(
                    {"status": "success", "target": target, "records": records, **page},
                    ensure_ascii=False,
                )
            external = self._replication_endpoint
            if external is not None and target == "ticdc/ticdc-0":
                result = subprocess.run(
                    ["docker", "logs", "--timestamps", external["container_name"]],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    raise RuntimeError(
                        f"TiCDC log read failed: target={target!r}, "
                        f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
                    )
                visible = (result.stdout + result.stderr).splitlines()
                page = self._slice_log_output(
                    "\n".join(visible),
                    page_limit,
                    start_line,
                    end_line,
                    match_key,
                )
                page["content"], page["content_truncated"] = self._bound_external_log_content(
                    page["content"].splitlines()
                )
                page["page_limit"] = page_limit
                if not page["content"] and match_key:
                    page["content"] = f"(no log entries matched match_key: {match_key})"
                return json.dumps({"status": "success", "target": target, **page}, ensure_ascii=False)
            if external is not None and target == "downstream/mysql-0":
                result = subprocess.run(
                    ["docker", "logs", "--timestamps", external["downstream_container_name"]],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    raise RuntimeError(
                        f"downstream log read failed: target={target!r}, "
                        f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
                    )
                visible = (result.stdout + result.stderr).splitlines()
                page = self._slice_log_output(
                    "\n".join(visible),
                    page_limit,
                    start_line,
                    end_line,
                    match_key,
                )
                page["content"], page["content_truncated"] = self._bound_external_log_content(
                    page["content"].splitlines()
                )
                page["page_limit"] = page_limit
                if not page["content"] and match_key:
                    page["content"] = f"(no log entries matched match_key: {match_key})"
                return json.dumps({"status": "success", "target": target, **page}, ensure_ascii=False)
            if target in {"br/snapshot", "br/log-backup", "br/restore"}:
                runtime = self._k08_pitr_runtime
                if runtime is None:
                    raise RuntimeError(
                        f"PITR restore runtime is not configured: run_id={self.run_id!r}"
                    )
                content = runtime.read_log(target)
                page = self._slice_log_output(content, page_limit, start_line, end_line, match_key)
                page["content"], page["content_truncated"] = self._bound_external_log_content(
                    page["content"].splitlines()
                )
                page["page_limit"] = page_limit
                if not page["content"] and match_key:
                    page["content"] = f"(no log entries matched match_key: {match_key})"
                return json.dumps({"status": "success", "target": target, **page}, ensure_ascii=False)
            if target not in self.deployment.NODES:
                raise ValueError(
                    f"Unknown TiDB target {target!r}; expected one of {self.deployment.list_nodes()}"
                )
            all_lines = self.deployment.read_logs(target, lines=10000).splitlines()
            visible = all_lines[self._log_visible_lines.get(target, 0):]
            page = self._slice_log_output(
                "\n".join(visible),
                page_limit,
                start_line,
                end_line,
                match_key,
            )
            if match_key:
                page["content"], content_truncated = self._bound_external_log_content(
                    page["content"].splitlines()
                )
                if content_truncated:
                    page["content_truncated"] = True
            page["page_limit"] = page_limit
            if not page["content"] and match_key:
                page["content"] = f"(no log entries matched match_key: {match_key})"
            return json.dumps({"status": "success", "target": target, **page}, ensure_ascii=False)
        except (ValueError, RuntimeError) as exc:
            return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)

    @classmethod
    def _bound_external_log_content(cls, lines: list[str]) -> tuple[str, bool]:
        chunks = []
        content_length = 0
        truncated = False
        for line in lines:
            if len(line) > cls.EXTERNAL_LOG_MAX_LINE_CHARS:
                marker = " ... [line truncated by TiDBEnv]"
                line = line[: cls.EXTERNAL_LOG_MAX_LINE_CHARS - len(marker)] + marker
                truncated = True
            separator_length = 1 if chunks else 0
            remaining = cls.EXTERNAL_LOG_MAX_CONTENT_CHARS - content_length - separator_length
            if remaining <= 0:
                truncated = True
                break
            if len(line) > remaining:
                marker = " ... [content truncated by TiDBEnv]"
                if remaining <= len(marker):
                    chunks.append(marker[:remaining])
                else:
                    chunks.append(line[: remaining - len(marker)] + marker)
                truncated = True
                break
            chunks.append(line)
            content_length += separator_length + len(line)
        return "\n".join(chunks), truncated

    def get_deployment(self) -> BaseDeployment:
        return self.deployment


class TiDBBusinessChangeEnv(TiDBEnv):
    """TiDB environment exposing the SQL-backed DM control plane."""

    def __init__(
        self,
        *,
        run_id: Optional[str] = None,
        workload=None,
        deployment: Optional[BaseDeployment] = None,
        port_base: int = 4000,
        user: str = "root",
        password: str = "",
        dbname: str = "test",
        sample_interval_sec: float = 2.0,
        return_window_seconds: int = 60,
        workload_runner_config: Optional[Dict[str, Any]] = None,
        image_group_key: Optional[str] = None,
    ):
        super().__init__(
            run_id=run_id,
            workload=workload,
            deployment=deployment,
            port_base=port_base,
            user=user,
            password=password,
            dbname=dbname,
            sample_interval_sec=sample_interval_sec,
            return_window_seconds=return_window_seconds,
            workload_runner_config=workload_runner_config,
            image_group_key=image_group_key,
        )
