"""Agent-facing structured contracts for the TiDB public tools."""

from __future__ import annotations

from typing import Any

from src.agent_language import agent_text
from src.scenarios.evaluation.protocol import STRUCTURED_REPORT_JSON_SCHEMA
from src.execution.tidb_metrics import CASE_ONLY_METRICS, TIDB_METRIC_CATALOG


def _discovery(resource_name: str, operation_name: str) -> dict[str, str]:
    return {
        "resource_name": resource_name,
        "operation_name": operation_name,
    }


def _target(
    *,
    required: bool,
    value_type: str,
    discovery: dict[str, str] | None,
    format: str | None = None,
    allowed_components: list[str] | None = None,
    allowed_values: list[str] | None = None,
    allowed_formats: list[str] | None = None,
    default_value: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "required": required,
        "value_type": value_type,
        "discovery": discovery,
    }
    if format is not None:
        result["format"] = format
    if allowed_components is not None:
        result["allowed_components"] = allowed_components
    if allowed_values is not None:
        result["allowed_values"] = allowed_values
    if allowed_formats is not None:
        result["allowed_formats"] = allowed_formats
    if default_value is not None:
        result["default_value"] = default_value
    if description is not None:
        result["target_description"] = description
    return result


def _parameter(
    name: str,
    data_type: str | list[str],
    *,
    required: bool,
    description: str,
    unit: str | None = None,
    allowed_values: list[str] | None = None,
    constraints: dict[str, Any] | None = None,
    default_value: Any = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "parameter_name": name,
        "data_type": data_type,
        "required": required,
    }
    if unit is not None:
        result["unit"] = unit
    if allowed_values is not None:
        result["allowed_values"] = allowed_values
    if constraints is not None:
        result["constraints"] = constraints
    if default_value is not None:
        result["default_value"] = default_value
    result["parameter_description"] = description
    return result


def _operation(
    name: str,
    description: str,
    target_definition: dict[str, Any],
    parameters: list[dict[str, Any]] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "operation_name": name,
        "operation_description": description,
        "target_definition": target_definition,
        "parameter_definitions": parameters or [],
    }
    result.update(extra)
    return result


def _resource(
    name: str,
    description: str,
    operations: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "resource_name": name,
        "resource_description": description,
        "operation_definitions": operations,
    }


def _tool(name: str, description: str, **fields: Any) -> dict[str, Any]:
    return {
        "tool_name": name,
        "tool_description": description,
        **fields,
    }


def _canonical_parameter(parameter: dict[str, Any]) -> dict[str, Any]:
    result = {
        "name": parameter["parameter_name"],
        "type": parameter["data_type"],
        "required": parameter["required"],
        "description": parameter["parameter_description"],
    }
    for source, target in (
        ("unit", "unit"),
        ("allowed_values", "allowed_values"),
        ("constraints", "constraints"),
        ("default_value", "default"),
    ):
        if source in parameter:
            result[target] = parameter[source]
    return result


def _canonical_target(target: dict[str, Any]) -> dict[str, Any]:
    result = {
        "required": target["required"],
        "type": target["value_type"],
        "discovery": target["discovery"],
    }
    for source, destination in (
        ("format", "format"),
        ("allowed_components", "allowed_components"),
        ("allowed_values", "allowed_values"),
        ("allowed_formats", "allowed_formats"),
        ("default_value", "default"),
        ("target_description", "description"),
    ):
        if source in target:
            result[destination] = target[source]
    return result


def _canonical_operation(operation: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": operation["operation_name"],
        "description": operation["operation_description"],
        "target": _canonical_target(operation["target_definition"]),
        "parameters": [
            _canonical_parameter(parameter)
            for parameter in operation["parameter_definitions"]
        ],
        "result": {
            "description": operation.get("result_description", ""),
        },
        "constraints": {
            "preconditions": list(operation.get("preconditions", [])),
            "parameter_rules": list(operation.get("parameter_rules", [])),
        },
    }


def _canonical_resource(resource: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": resource["resource_name"],
        "description": resource["resource_description"],
        "operations": [
            _canonical_operation(operation)
            for operation in resource["operation_definitions"]
        ],
    }


def canonical_tool_definition(definition: dict[str, Any]) -> dict[str, Any]:
    """Return the single agent-facing help contract for every structured tool."""
    capabilities = {
        "metrics": [
            {
                "name": metric["metric_name"],
                "description": metric["metric_description"],
                "target_scope": metric["target_scope"],
            }
            for metric in definition.get("metric_definitions", [])
        ],
        "resources": [
            _canonical_resource(resource)
            for resource in definition.get("resource_definitions", [])
        ],
    }
    return {
        "name": definition["tool_name"],
        "description": definition["tool_description"],
        "parameters": [
            _canonical_parameter(parameter)
            for parameter in definition.get("parameter_definitions", [])
        ],
        "result": {
            "description": definition.get("result_description", ""),
        },
        "capabilities": capabilities,
        "runtime": {},
    }


SERVICE_DISCOVERY = _discovery("service", "list")
STORE_DISCOVERY = _discovery("store", "list")
REGION_DISCOVERY = _discovery("region", "list")
ROUTER_DISCOVERY = _discovery("router", "get")

SERVICE_COMPONENTS = ["pd", "tikv", "tidb", "tiflash", "ticdc", "monitoring", "downstream"]
DATABASE_COMPONENTS = ["pd", "tikv", "tidb", "tiflash"]
SERVICE_IDENTITY_TARGET = _target(
    required=True,
    value_type="service_identity",
    discovery=SERVICE_DISCOVERY,
    format="component/component-id",
    allowed_components=SERVICE_COMPONENTS,
)
DATABASE_NODE_TARGET = _target(
    required=True,
    value_type="service_identity",
    discovery=SERVICE_DISCOVERY,
    format="component/component-id",
    allowed_components=DATABASE_COMPONENTS,
)
TIKV_TARGET = _target(
    required=True,
    value_type="service_identity",
    discovery=SERVICE_DISCOVERY,
    format="tikv/tikv-N",
    allowed_components=["tikv"],
)
TIDB_TARGET = _target(
    required=True,
    value_type="service_identity",
    discovery=SERVICE_DISCOVERY,
    format="tidb/tidb-N",
    allowed_components=["tidb"],
)
STORE_TARGET = _target(
    required=True,
    value_type="store_identity",
    discovery=STORE_DISCOVERY,
    format="tikv/tikv-N",
)
OPTIONAL_STORE_TARGET = _target(
    required=False,
    value_type="store_identity",
    discovery=STORE_DISCOVERY,
    format="tikv/tikv-N",
)
NO_TARGET = _target(required=False, value_type="none", discovery=None)
REGION_DISCOVERY = _discovery("region", "get")
REGION_TARGET = _target(
    required=True,
    value_type="region_identity",
    discovery=REGION_DISCOVERY,
    format="region/<region_id>",
)
CHANGEFEED_ID_TARGET = _target(
    required=True,
    value_type="changefeed_id",
    discovery=None,
    format="[a-z0-9][a-z0-9_-]*",
)
LIVE_CAPTURE_TARGET = _target(
    required=True,
    value_type="service_identity",
    discovery=SERVICE_DISCOVERY,
    format="ticdc/ticdc-N",
    allowed_components=["ticdc"],
)
GC_SERVICE_ID_TARGET = _target(
    required=True,
    value_type="service_id",
    discovery=_discovery("gc_safepoint", "list"),
    format="ticdc-service-id",
)

_PUBLIC_METRIC_NAMES = tuple(sorted(TIDB_METRIC_CATALOG.metric_names - CASE_ONLY_METRICS))


TIDB_TOOL_DEFINITIONS: dict[str, dict[str, Any]] = {
    "search_knowledge": _tool(
        "search_knowledge",
        "检索 TiDB 8.1 官方文档，不返回当前集群状态、场景结论或修复结果。",
        parameter_definitions=[
            _parameter("query", "string", required=True, description="自然语言问题、配置名、SQL 标识符或组件概念。"),
            _parameter(
                "source_scope",
                "string",
                required=False,
                default_value="all",
                allowed_values=["self_managed", "cloud", "kubernetes", "developer", "shared", "all"],
                description="检索文档所属的部署范围。",
            ),
            _parameter(
                "top_k",
                "integer",
                required=False,
                default_value=5,
                constraints={"minimum": 1, "maximum": 20},
                description="最多返回的文档片段数量。",
            ),
            _parameter(
                "kb_type",
                "string",
                required=False,
                allowed_values=[
                    "architecture", "configuration", "observability", "diagnosis", "operation",
                    "performance", "recovery", "data_pipeline", "reference", "release",
                ],
                description="可选的文档分类过滤器。",
            ),
            _parameter(
                "component",
                "string",
                required=False,
                allowed_values=[
                    "tidb", "tikv", "pd", "tiflash", "ticdc", "tiproxy", "br", "lightning",
                    "dumpling", "dm", "tiup", "dashboard", "operator", "cloud", "sql",
                    "ecosystem", "shared",
                ],
                description="可选的组件过滤器。",
            ),
        ],
        result_description="返回匹配片段及其文档来源、分类、组件和引用信息。",
    ),
    "query_metrics": _tool(
        "query_metrics",
        "查询基础资源和服务时序；不把 SQL 明细或控制面状态预先包装成场景结论。",
        metric_definitions=[
            {
                "metric_name": "cpu",
                "metric_description": "容器 CPU 使用率，单位 percent。",
                "target_scope": "任意 service identity；不传 target 时按服务返回。",
            },
            {
                "metric_name": "memory",
                "metric_description": "容器工作集相对于内存上限的使用率，单位 percent。",
                "target_scope": "任意 service identity；不传 target 时按数据库服务返回。",
            },
            {
                "metric_name": "disk_io",
                "metric_description": "文件系统读写吞吐，单位 MB/s。",
                "target_scope": "任意 service identity；不传 target 时按数据库服务返回。",
            },
            {
                "metric_name": "disk_usage",
                "metric_description": "容器文件系统使用量，单位 MB。",
                "target_scope": "任意 service identity；不传 target 时返回 cluster 序列。",
            },
            {
                "metric_name": "network_io",
                "metric_description": "容器网络收发吞吐，返回 megabytes_per_second。",
                "target_scope": "任意 service identity；不传 target 时返回 cluster 序列。",
            },
            {
                "metric_name": "qps",
                "metric_description": "TiDB 查询吞吐，单位 queries_per_second。",
                "target_scope": "TiDB endpoint；不传 target 时返回 cluster 序列。",
            },
            {
                "metric_name": "query_latency",
                "metric_description": "TiDB 查询延迟，返回 average_ms、p95_ms、p99_ms。",
                "target_scope": "TiDB endpoint；不传 target 时返回 cluster 序列。",
            },
            {
                "metric_name": "active_connections",
                "metric_description": "TiDB 活跃连接数，单位 connections。",
                "target_scope": "TiDB endpoint；不传 target 时按 TiDB 服务返回。",
            },
        ],
        parameter_definitions=[
            _parameter(
                "metric_type",
                "string",
                required=True,
                allowed_values=[
                    *_PUBLIC_METRIC_NAMES,
                ],
                description="要查询的基础时序指标。",
            ),
            _parameter(
                "target",
                "string",
                required=False,
                description="稳定服务身份；可通过 manage_cluster(service, list) 发现。不同指标对 target 的组件范围不同。",
            ),
            _parameter(
                "start_timestamp",
                "string",
                required=False,
                constraints={"format": "YYYY-MM-DD HH:mm:ss", "paired_with": "end_timestamp"},
                description="时序窗口起点；传入时必须同时传 end_timestamp。",
            ),
            _parameter(
                "end_timestamp",
                "string",
                required=False,
                constraints={"format": "YYYY-MM-DD HH:mm:ss", "paired_with": "start_timestamp"},
                description="时序窗口终点，不能早于 start_timestamp。",
            ),
            _parameter(
                "step_seconds",
                "integer",
                required=False,
                constraints={"exclusive_minimum": 0},
                unit="second",
                description="历史查询的采样步长；必须是当前 Case base step 的正整数倍。",
            ),
        ],
        result_description="返回 status、metric、kind=series、window、counts，以及 timestamps 和对应指标数组；历史任务默认返回完整冻结历史的 overview step。",
    ),
    "execute_sql": _tool(
        "execute_sql",
        "在当前环境可访问的 SQL 连接面上执行 SQL；历史连接面只读，只能查询冻结历史中的原始 SQL 记录。时间条件是定位历史的推荐方式，不是强制条件；全量结果仍受返回行数限制。连接面名称和查询方式由 help('execute_sql') 动态提供。",
        parameter_definitions=[
            _parameter("sql_query", "string", required=True, description="要执行的单条或多语句 SQL；可读写，必须由 Agent 自己决定查询对象和验证方式。"),
            _parameter(
                "target",
                "string",
                required=False,
                default_value="primary",
                description="SQL 连接面名称；必须使用 help('execute_sql') 当前返回的 connection_surfaces.name。",
            ),
        ],
        result_description="最多返回 200 行，且单次结果总量不超过 128 KiB（超长字段裁剪到 2048 字符）；超限时 truncated=true 并附带 truncation_hint 缩窗建议：只 SELECT 需要的列、加 WHERE/LIMIT，或改用 COUNT/SUM 聚合后分页查看。非查询语句返回受影响行数。",
    ),
    "manage_cluster": _tool(
        "manage_cluster",
        "对集群资源执行通用观察和维护；先通过 discovery 指定的观察操作确定稳定 target，再执行需要 target 的操作。",
        parameter_definitions=[
            _parameter("resource", "string", required=True, description="资源类别，必须使用 resource_definitions 中的名称。"),
            _parameter("operation", "string", required=True, description="资源上的操作，必须使用对应 operation_definitions 中的名称。"),
            _parameter("target", "string", required=False, description="资源身份；是否必填、格式和发现方式由所选 resource/operation 决定。"),
            _parameter("parameters", "object", required=False, default_value={}, description="所选 operation 的参数对象；没有参数时省略或传空对象。"),
        ],
        resource_definitions=[
            _resource("service", "集群服务、组件实例和 SQL endpoint。", [
                _operation("list", "列出当前可观察的服务实例、运行状态和 SQL endpoint。", NO_TARGET, result_description="返回 nodes 和 sql_endpoints。"),
                _operation("get", "读取指定服务或整个 cluster 的运行状态。", _target(required=True, value_type="service_or_cluster", discovery=SERVICE_DISCOVERY, format="component/component-id 或 cluster", allowed_values=["cluster"]), result_description="返回一个服务的 state，或 cluster 的 nodes。"),
                *[
                    _operation(
                        operation,
                        description,
                        SERVICE_IDENTITY_TARGET,
                        result_description="返回目标服务的操作结果和最新状态。",
                    )
                    for operation, description in (
                        ("start", "启动指定服务实例。"),
                        ("stop", "停止指定服务实例。"),
                        ("restart", "重启指定服务实例，并在适用时等待服务恢复就绪。"),
                    )
                ],
                _operation("scale_out", "启动一个尚未注册为 PD Store 的 TiKV 实例并等待其注册为 Up。", TIKV_TARGET, result_description="返回 target、state 和新 store_id。"),
                _operation("scale_in", "删除指定 TiKV Store 的 PD 注册，使其进入受控的缩容流程。", TIKV_TARGET, result_description="返回 target、state 和 store_id。", preconditions=["目标 Store 必须为 Up。"]),
                _operation("replace_disk", "替换已经进入 Tombstone 状态的 TiKV Store 磁盘并重新注册实例。", TIKV_TARGET, result_description="返回旧、新 store_id 和最终 Up 状态。", preconditions=["目标 Store 必须为 Tombstone，且必须先完成 scale_in。"]),
                _operation("resize", "调整指定 TiCDC 服务的 CPU 配额。", _target(required=True, value_type="service_identity", discovery=SERVICE_DISCOVERY, format="ticdc/ticdc-0", allowed_values=["ticdc/ticdc-0"]), [
                    _parameter("cpu_limit", "number", required=True, unit="cpu_core", constraints={"exclusive_minimum": 0}, description="新的 CPU 配额，必须大于 0。"),
                ], result_description="返回 target 和 cpu_limit。"),
                _operation("upgrade", "按当前升级运行时对一个数据库组件执行滚动升级。", DATABASE_NODE_TARGET, result_description="返回目标组件和版本观测。", preconditions=["必须已配置 upgrade release，且前置组件已完成升级。"]),
                _operation("rollback", "回滚最近升级的数据库组件。", DATABASE_NODE_TARGET, result_description="返回目标组件和版本观测。", preconditions=["只能回滚最近一个已升级组件。"]),
            ]),
            _resource("store", "PD 管理的 TiKV Store 状态、身份和 operator 速率。", [
                _operation("list", "列出 PD 当前可观察的 Store 及其状态、Region 和 Leader 摘要。", NO_TARGET, result_description="返回 PD stores 数组，并建立后续 Store target 的发现记录。"),
                _operation("get", "读取指定 TiKV Store 的 PD 状态。", STORE_TARGET, result_description="返回 Store 原始状态和 status。"),
                _operation("update", "修改指定 Store 的状态或 operator 速率；一次调用只能表达一种修改。", STORE_TARGET, [
                    _parameter("state", "string", required=False, allowed_values=["Offline", "Up"], description="将 Store 状态设为 Offline 或 Up。"),
                    _parameter("rate", "integer", required=False, unit="operator_per_second", constraints={"exclusive_minimum": 0}, description="Store operator 速率；不能与 state 同时作为有效更新。"),
                ], result_description="返回 PD 更新结果。", parameter_rules=["state 和 rate 至少提供一个；代码按 state 优先。"]),
            ]),
            _resource("region", "PD 管理的 Region 观察和受控 peer removal。", [
                _operation("list", "列出指定 Store 关联的 Region 和 peer 信息，并记录可用于 remove 的 Region ID。", STORE_TARGET, result_description="返回 regions 数组。"),
                _operation("get", "按 Region ID 读取 Region 和 peer 信息；传 target 时同时记录该 Region 的观察关系。", OPTIONAL_STORE_TARGET, [
                    _parameter("region_id", "integer", required=True, constraints={"exclusive_minimum": 0}, description="要查询的 Region ID。"),
                ], result_description="返回单个 Region 的 PD 原始信息。"),
                _operation("remove", "为已确认的 Offline Store 移除一个残留 Region peer，安排 PD 进行 peer replacement。", STORE_TARGET, [
                    _parameter("region_id", "integer", required=True, constraints={"exclusive_minimum": 0}, description="必须来自此前对同一 target 的 region/list 或 region/get 观察。"),
                ], result_description="返回已安排的 Region/Store 操作。", preconditions=["目标 Store 必须 Offline。", "Region 必须包含目标 Store peer。", "Region 至少有三个 peer。"]),
            ]),
            _resource("mvcc_lock", "限定 Region 和完整 peer Store 范围内的 TiKV lock CF 原始观察。", [
                _operation("list", "在每个显式 peer Store 上执行有界 lock CF raw scan；只返回原始扫描结果，不生成根因结论。", REGION_TARGET, [
                    _parameter(
                        "store_targets",
                        "array[string]",
                        required=True,
                        description="目标 Region 当前完整 peer Store target 集合，例如 tikv/tikv-0；必须来自此前观察并且不能遗漏、重复或增加 Store。",
                    ),
                ], result_description="返回 Region 边界、完整 peer Store 集合、版本化工具元数据和每个 peer 的原始 bounded scan 输出。"),
                _operation("resolve", "使用此前同一 Region 和完整 peer Store scope 的观察凭证，执行固定版本的 MVCC lock recovery。", REGION_TARGET, [
                    _parameter(
                        "inspection_id",
                        "string",
                        required=True,
                        description="此前同一 Region 和完整 peer scope 的只读维护检查凭证；不能由 Agent 自行构造。",
                    ),
                ], result_description="返回固定版本、精确 Region/peer scope 和每个 peer 的原始 recovery 输出；不接受任意 from_key/to_key 或全局 --all。", preconditions=["必须先完成同一 Region/peer scope 的只读观察。", "固定版本维护路径由当前 TiDB/TiKV 运行时绑定。"]),
            ]),
            _resource("changefeed_diagnostics", "TiCDC capture 的原始 changefeed、owner、progress 和 error 观察。", [
                _operation("get", "从指定 live capture 读取一个 changefeed 的原始状态。", CHANGEFEED_ID_TARGET, [
                    _parameter("capture_target", "string", required=True, description="已通过 service/list 发现的 live TiCDC capture target。"),
                ], result_description="返回 changefeed API 原始状态和 capture target，不生成根因结论。"),
                _operation("list", "从指定 live capture 读取所有可见 changefeed 的原始状态摘要。", LIVE_CAPTURE_TARGET, result_description="返回 changefeeds 原始数组和 capture target。"),
            ]),
            _resource("gc_safepoint", "PD service GC safepoint owner 的原始观察和精确 changefeed cleanup。", [
                _operation("list", "读取当前 global GC safepoint 和全部 service GC safepoint owner。", NO_TARGET, result_description="返回 PD 原始 service_gc_safe_points 和 gc_safe_point，并登记本次观察。"),
                _operation("remove", "删除精确绑定的 abandoned changefeed，并等待其 service GC safepoint 不再低于 gc_worker。", GC_SERVICE_ID_TARGET, [
                    _parameter("changefeed_id", "string", required=True, description="与 abandoned owner 证据绑定的 exact changefeed ID。"),
                ], result_description="返回 changefeed cleanup 原始输出和删除前后 safepoint owner 快照。", preconditions=["必须先观察同一个 service_id。", "必须证明 owner 无 live runtime/heartbeat。", "不能删除 gc_worker、active、healthy 或 backup owner。"]),
            ]),
            _resource("gc_status", "只能通过 TiKV Prometheus 端点取得的 GC 阶段原始观测。", [
                _operation("get", "读取 TiKV GC worker、resolve locks、delete ranges 和 do_gc 的原始 Prometheus series；SQL 变量、safepoint 和删除范围请用 execute_sql 查询，不生成诊断结论。", NO_TARGET, result_description="返回 GC 阶段原始 Prometheus series 与 SQL GC 变量、safepoint、磁盘和 compaction 原始值。"),
            ]),
            _resource("storage_maintenance", "固定版本、精确 Region 和完整 peer Store 范围内的分布式存储状态维护边界。", [
                _operation("preflight", "对显式完整 peer Store 集合逐一执行固定版本的只读维护前检查，不修改数据。", REGION_TARGET, [
                    _parameter(
                        "store_targets",
                        "array[string]",
                        required=True,
                        description="目标 Region 当前完整 peer Store target 集合；必须精确覆盖 Region peers。",
                    ),
                ], result_description="返回 preflight_id、固定 release/binary identity、supported scope 和每个 peer 的 read-only 原始输出。"),
                _operation("apply", "使用此前 preflight_id 对同一 Region 和完整 peer Store 集合应用固定版本的边界内维护；禁止 --all。", REGION_TARGET, [
                    _parameter(
                        "preflight_id",
                        "string",
                        required=True,
                        description="此前 storage_maintenance/preflight 返回的单次检查凭证；没有 preflight 不能 apply。",
                    ),
                ], result_description="返回每个 peer 的原始维护输出、精确 scope 和固定工具 identity。", preconditions=["必须先完成同一 Region/peer scope 的 read-only preflight。", "不会接受全局 --all scope。"]),
            ]),
            _resource("unsafe_recovery", "PD unsafe recovery 的原始状态和请求提交接口。", [
                _operation("get", "读取 PD unsafe recovery 的原始阶段和结果输出。", NO_TARGET, result_description="返回 PD Control 的原始状态输出。"),
                _operation("start", "向 PD 提交一次异步、集群级且有损的 unsafe recovery 请求。", NO_TARGET, [
                    _parameter(
                        "failed_store_ids",
                        "array",
                        required=True,
                        description=(
                            "当前集群完整的永久失败 TiKV Store ID 集合，包含同一事故中 checkout 范围之外的失败 Store，"
                            "排除健康 Store 和 maintenance-only Store。"
                        ),
                    ),
                ], result_description="返回 PD 的原始注册结果；accepted/Success 只表示请求已登记，不表示异步任务已完成。", preconditions=["Store/Region 现场证据已经完成。", "只使用当前部署中观察到的 Store ID。"]),
            ]),
            _resource("pd_recovery", "PD metadata 恢复的现场检查与原集群 identity 重建执行接口。", [
                _operation("inspect", "读取 PD recovery 的 current 或 history 检查视图。", _target(required=False, value_type="service_identity", discovery=SERVICE_DISCOVERY, format="pd/pd-N"), [
                    _parameter("view", "string", required=False, allowed_values=["current", "history"], description="检查视图，默认 current。"),
                    _parameter("phase", "string", required=False, description="可选的 history 阶段过滤。"),
                    _parameter("record_id", "string", required=False, description="可选的维护记录 ID 过滤。"),
                ], result_description="返回 PD recovery 检查的原始状态输出。"),
                _operation("execute", "基于原集群 identity 证据执行一次固定版本 pd-recover。", _target(required=True, value_type="service_identity", discovery=SERVICE_DISCOVERY, format="pd/pd-N"), [
                    _parameter("cluster_id", "integer", required=True, constraints={"exclusive_minimum": 0}, description="现场观察到的原集群 cluster ID。"),
                    _parameter("alloc_id", "integer", required=True, constraints={"exclusive_minimum": 0}, description="严格高于原集群 allocator high-water 的 alloc-id。"),
                    _parameter(
                        "recovery_branch",
                        "string",
                        required=True,
                        allowed_values=["surviving_member", "entirely_rebuild"],
                        description="PD recovery knowledge: surviving_member 依赖幸存成员重建元数据；entirely_rebuild 在全部 PD 元数据丢失时用原 cluster ID 完整重建。分支必须由现场证据决定。",
                    ),
                    _parameter("record_id", "string", required=True, description="本次恢复绑定的维护记录 ID。"),
                ], result_description="返回 pd-recover 的原始注册结果；Success 只表示请求已登记，不表示元数据已收敛。", preconditions=["必须先完成 clock_status/list 观察。", "cluster_id、alloc_id 与 record_id 必须来自现场证据。"]),
            ]),
            _resource("operator", "PD 当前 operator 列表。", [
                _operation("list", "列出 PD 当前 operator。", NO_TARGET, result_description="返回 operators 数组。"),
                _operation("get", "读取 PD 当前 operator；当前实现与 list 返回同一集合。", NO_TARGET, result_description="返回 operators 数组。"),
            ]),
            _resource("scheduler", "PD 当前 scheduler 列表及受控 scheduler 删除。", [
                _operation("list", "列出 PD 当前 scheduler。", NO_TARGET, result_description="返回 schedulers 数组。"),
                _operation("get", "读取 PD 当前 scheduler；当前实现与 list 返回同一集合。", NO_TARGET, result_description="返回 schedulers 数组。"),
                _operation("remove", "删除一个已观察到的 evict-leader-scheduler。", _target(required=False, value_type="scheduler_identity", discovery=_discovery("scheduler", "list"), format="evict-leader-scheduler/store-id"), [
                    _parameter("type", "string", required=False, allowed_values=["evict-leader-scheduler"], description="观察到的 scheduler 类型；使用 parameters 形式时需要提供。"),
                    _parameter("store_id", "integer", required=False, constraints={"exclusive_minimum": 0}, description="scheduler 绑定的 Store ID；使用 parameters 形式时需要提供。"),
                ], result_description="返回 PD 删除命令的原始输出。", parameter_rules=["可以使用 target=evict-leader-scheduler/<store_id>，或同时提供 type 和 store_id。"]),
            ]),
            _resource("config", "PD 或 TiKV 的运行时配置。", [
                _operation("get", "读取指定 PD 或 TiKV 组件的运行时配置。", _target(required=False, value_type="config_target", discovery=SERVICE_DISCOVERY, allowed_formats=["pd", "tikv/tikv-N"], default_value="pd"), result_description="PD 返回 PD config；TiKV 返回 storage.io_rate_limit。"),
                _operation("update", "修改指定组件允许范围内的运行时配置。", _target(required=False, value_type="config_target", discovery=SERVICE_DISCOVERY, allowed_formats=["pd", "tikv/tikv-N"], default_value="pd"), [
                    _parameter("key", "string", required=True, allowed_values=["schedule.*", "storage.io-rate-limit.max-bytes-per-sec"], description="PD target 只能使用 schedule.*；TiKV target 只能使用 storage.io-rate-limit.max-bytes-per-sec。"),
                    _parameter("value", ["string", "integer", "boolean"], required=True, description="配置值；PD 的 true/false 和整数会按对应类型提交，其他值保留为字符串。"),
                ], result_description="返回配置更新后的原始结果或 TiKV 当前运行时配置。", parameter_rules=["key 的允许范围由 target 决定。"]),
            ]),
            _resource("network", "组件与 PD 控制面的网络连通性观察和恢复，包含 client egress 与 PD ingress 边界。", [
                _operation("get", "读取指定组件与 PD 控制面的 INPUT/OUTPUT 网络访问状态。", SERVICE_IDENTITY_TARGET, result_description="返回网络检查的原始状态。"),
                _operation("update", "允许指定组件访问 PD 控制面并返回当前网络状态；不会重启组件。", SERVICE_IDENTITY_TARGET, [
                    _parameter("access", "string", required=True, allowed_values=["allow"], description="必须为 allow；当前唯一支持的网络更新方向。"),
                ], result_description="返回更新后的网络检查状态。"),
            ]),
            _resource("router", "TiDB SQL endpoint 连接路由器。", [
                _operation("get", "列出所有连接路由器的策略、后端、draining 状态和活跃连接计数。", NO_TARGET, result_description="返回 router_name 到 router status 的映射。"),
                _operation("update", "修改指定连接池的后端选择策略。", _target(required=True, value_type="router_name", discovery=ROUTER_DISCOVERY, format="router-name"), [
                    _parameter("policy", "string", required=True, allowed_values=["round_robin", "least_connections"], description="新的连接分配策略。"),
                ], result_description="返回该连接池更新后的状态。", preconditions=["至少有一个后端未处于 draining。"]),
                _operation("drain", "禁止指定 TiDB backend 接收新连接，同时保留已有连接自然完成。", TIDB_TARGET, result_description="返回所有连接池的更新状态。", preconditions=["必须先使用 distributing policy；不能 drain 最后一个可接收连接的 backend。"]),
            ]),
            _resource("changefeed", "TiCDC changefeed 的状态、执行配置和生命周期。", [
                _operation("get", "读取 changefeed 的 state、error、checkpoint/resolved TSO、lag 和已登记执行配置。", _target(required=True, value_type="changefeed_id", discovery=None, format="[a-z0-9][a-z0-9_-]*"), result_description="返回当前 changefeed 的原始状态和执行配置投影。"),
                _operation("update", "更新当前已登记 changefeed 的公开 sink 执行配置；TiCDC 8.1 可能要求先暂停再更新，但不能重建 changefeed。", _target(required=True, value_type="changefeed_id", discovery=None, format="[a-z0-9][a-z0-9_-]*"), [
                    _parameter("max_txn_row", "integer", required=False, constraints={"minimum": 1, "maximum": 256}, description="每个 sink transaction 的最大 source row 数；合法范围 1..256。"),
                    _parameter("worker_count", "integer", required=False, constraints={"minimum": 1, "maximum": 32}, description="sink worker 数；合法范围 1..32。"),
                    _parameter("batch_dml_enable", "boolean", required=False, description="是否启用 batch DML。"),
                ], result_description="返回 previous/current 原始 execution config 和 controller acknowledgement。", preconditions=["至少提供一个 execution config 参数；target 必须是当前已登记 changefeed；若 controller 拒绝运行中 update，可在授权窗口内 pause 后重试。"]),
                _operation("pause", "暂停指定 changefeed。", _target(required=True, value_type="changefeed_id", discovery=None, format="[a-z0-9][a-z0-9_-]*"), result_description="返回 TiCDC CLI 输出。"),
                _operation("resume", "恢复指定 changefeed。", _target(required=True, value_type="changefeed_id", discovery=None, format="[a-z0-9][a-z0-9_-]*"), result_description="返回 TiCDC CLI 输出。"),
                _operation("recreate", "删除并从指定 start_ts 重新创建同名 changefeed。", _target(required=True, value_type="changefeed_id", discovery=None, format="[a-z0-9][a-z0-9_-]*"), [
                    _parameter("start_ts", "integer", required=True, constraints={"exclusive_minimum": 0}, description="重新创建 changefeed 的起始 TSO。"),
                ], result_description="返回 changefeed_id、running state 和 start_ts。", preconditions=["必须确认起始 TSO 和下游数据语义后再执行。"]),
            ]),
            _resource("job", "当前运行时配置的外部导入或 BR 任务。", [
                _operation("get", "纯读取已配置外部任务的状态；若为 Lightning 返回导入状态，若为 BR 返回最近结果、对象列表和 desired binding。worker lease、job dispatch 与 storage audit 属于 SQL 控制面观测。", NO_TARGET, result_description="结果结构由当前配置的外部 job 类型决定；BR get 不执行 refresh 或其它状态变更。"),
                _operation("check", "执行 Lightning 导入前置检查。", NO_TARGET, result_description="返回检查输出和目标表当前行数。", preconditions=["必须配置 Lightning import controller。"]),
                _operation("update", "更新 Lightning 导入预算并从 checkpoint 继续或恢复。", NO_TARGET, [
                    _parameter("region_concurrency", "integer", required=True, constraints={"exclusive_minimum": 0}, description="Lightning 的区域并发配置。"),
                    _parameter("disk_quota_mb", "integer", required=True, unit="MiB", constraints={"exclusive_minimum": 0}, description="Lightning 本地排序目录的空间配置。"),
                    _parameter("store_write_bwlimit_mib", "integer", required=True, unit="MiB/s", constraints={"exclusive_minimum": 0}, description="TiKV 写入带宽配置。"),
                ], result_description="返回导入进程当前状态。", preconditions=["必须配置 Lightning import controller。"]),
                _operation("wait", "等待当前 Lightning 导入在给定超时时间内结束或达到可报告状态。", NO_TARGET, [
                    _parameter("timeout_seconds", "integer", required=False, default_value=120, unit="second", constraints={"exclusive_minimum": 0}, description="最多等待时间。"),
                ], result_description="返回导入状态、退出码、目标表当前行数和运行时长。", preconditions=["必须配置 Lightning import controller。"]),
                _operation("refresh_binding", "对已通过 SQL 控制面观测确认的 BR worker、失败 execution attempt、失败 request route、request assignment fence、request context、execution stage、observed/desired authority grant、authority lease、opaque authority epoch 和单一 table scope 执行有界 binding/cache refresh，并返回前后 raw revision。attempt_id 必须来自 backup_storage_request_attempts 中与 storage audit 的 dispatch、403 event time 和 stale material 对齐的 failed write attempt；同一 dispatch 下的 completed preflight 或失败后的 replay 不能用于 refresh。", _target(required=True, value_type="br_worker_identity", discovery=_discovery("execute_sql", "query"), format="br-worker-N"), [
                    _parameter("target_scope", "string", required=True, description="必须是当前 BR job 的 table-level target scope，并与 SQL worker lease 观测一致。"),
                    _parameter("request_route_token", "string", required=True, description="失败 request 的 request-data-plane route token；必须由 dispatch/route 的时间窗口和 assignment 证据确认。"),
                    _parameter("request_cache_token", "string", required=True, description="失败 request 的 time-scoped cache snapshot token；必须与 request_route_token 和 request start 同时匹配。"),
                    _parameter("attempt_id", "string", required=True, description="原始 403 对应的 failed-write execution attempt；必须从 backup_storage_request_attempts 发现，并排除同 dispatch 的 completed preflight 与 post-failure replay。"),
                    _parameter("observed_authority_grant_id", "integer", required=True, description="失败 request material 当前实际使用的 active grant；必须与 material credential_id 和 request 时间窗匹配，并证明其 scope/URI 不覆盖 production request。"),
                    _parameter("desired_authority_grant_id", "integer", required=True, description="effective production credential 的 active grant；必须由 credential_id、grant_scope、grant_uri、grant_state 和 request 时间窗联合确认。"),
                    _parameter("authority_lease_id", "integer", required=True, description="失败 request route 对应的 authority grant lease；必须与 route lease_token、assignment_generation、scope、observed/desired grant、revision 和 request 时间窗匹配。"),
                    _parameter("authority_epoch", "string", required=True, description="失败 request 对应的 opaque authority assignment identity；必须与 worker lease 与 authority lease 的 lease_token、assignment_generation、target scope、revision、stale state 和 request 时间窗一致；当控制器事件流显示 authority epoch 已提升时，lease 表列是轮换前的滞后记录，必须以控制器当前 epoch 为准，不能只凭 lease 表列或 lease_id 使用。"),
                    _parameter("request_assignment_fence", "string", required=True, description="失败 request 的 opaque assignment fence；必须同时命中失败 storage audit、dispatch route、request cache、worker lease 和 authority lease，不能由 change_ref、lease id 或 fingerprint 单独推导。"),
                    _parameter("request_context_token", "string", required=True, description="失败 request 的 opaque context token；必须同时命中失败 storage audit、dispatch route、request cache、worker lease 和 authority lease。同一 context 下的 replay attempt 不能只靠 token 区分。"),
                    _parameter("request_stage", "string", required=True, description="失败 storage audit 的请求阶段；必须与实际失败执行尝试一致。"),
                    _parameter("assignment_phase", "string", required=True, description="失败 dispatch/route 的执行阶段；必须覆盖 request_started_at 且与实际失败尝试一致。"),
                    _parameter("assignment_reason", "string", required=True, description="失败 dispatch/route 的执行原因；必须与 request stage、时间窗和实际失败尝试一致。"),
                    _parameter("cache_phase", "string", required=True, description="失败 request cache snapshot 的执行阶段；必须与 route/lease phase 和失败时间窗一致。"),
                ], result_description="返回 acknowledged、worker_id、target_scope、authority_epoch、request_assignment_fence、request_context_token、execution stage、observed_authority_grant_id、desired_authority_grant_id、authority_lease_id、previous 和 current propagation row。", preconditions=["必须先通过 job get 和 SQL 控制面观测确认 worker、scope、失败 route、request assignment fence、request context token、request_stage、assignment phase/reason、失败 cache snapshot、observed/desired authority grant、authority lease 及其 authority epoch 的关联。", "只允许当前 case 的单一 table scope。"]),
                _operation("start", "启动受控 BR backup job；不传凭据时使用 worker observed binding，传入 access_key/secret_key 时只作为一次性显式 override。", NO_TARGET, [
                    _parameter("database", "string", required=True, description="备份目标数据库，必须匹配当前 job runtime。"),
                    _parameter("table", "string", required=True, description="备份目标表，必须匹配当前 job runtime。"),
                    _parameter("access_key", "string", required=False, description="可选的一次性 BR access key；必须与 secret_key 一起传入，不改变 worker binding。"),
                    _parameter("secret_key", "string", required=False, description="可选的一次性 BR secret key；必须与 access_key 一起传入，不改变 worker binding。"),
                ], result_description="返回 status、operation、database、table、exit_code、metrics、credential_source 和 attempt_id 等受限结果。", preconditions=["必须配置 BR backup runtime。"]),
                _operation("observe", "纯读取外部 job 控制器的事件流；不执行任何状态变更。默认只返回最近一段事件，更早的历史（如轮换期间的 epoch 提升或防护进入）必须用时间窗参数回溯。", NO_TARGET, [
                    _parameter("start_timestamp", "string", required=False, description="时间窗起点，格式 YYYY-MM-DD HH:MM:SS；必须与 end_timestamp 一起传入。"),
                    _parameter("end_timestamp", "string", required=False, description="时间窗终点，格式 YYYY-MM-DD HH:MM:SS；必须与 start_timestamp 一起传入。"),
                ], result_description="返回 job_kind、target_scope、controller_events、event_count、total_event_count、oldest_event_at 与 window_applied；事件由控制器自身产生，含 worker serving 心跳、authority epoch 提升与存储防护等原始事件。", preconditions=["必须配置外部 job runtime。"]),
                _operation("release_prefix_quarantine", "对已通过控制器事件流确认隔离身份的存储前缀执行有界防护释放；只作用于单一备份前缀，不改变 worker binding。", NO_TARGET, [
                    _parameter("target_prefix", "string", required=True, description="被隔离的备份对象前缀；必须与控制器事件流中的 quarantined prefix 一致。"),
                    _parameter("quarantine_ref", "string", required=True, description="隔离引用 token；必须来自控制器事件流的 storage_prefix_quarantined 事件。"),
                    _parameter("triggering_change_ref", "string", required=True, description="触发该防护的 rotation change_ref；必须与隔离事件所属的轮换 watch 一致。"),
                ], result_description="返回 released、prefix、bucket、quarantine_ref 与 guard。", preconditions=["必须先通过 job observe 确认隔离前缀、quarantine_ref 与触发轮换的 change_ref。", "身份不匹配时不改变任何状态。"]),
            ]),
            _resource("release", "数据库组件 release 的观察、升级准备和组件级升级。", [
                _operation("get", "读取当前和目标 release 版本。", NO_TARGET, result_description="返回版本观测。"),
                _operation("prepare", "执行升级前的集群和兼容性检查。", NO_TARGET, result_description="返回 cluster_info、兼容性变量和版本观测。", preconditions=["必须配置 business-change case 和 upgrade release。"]),
                _operation("snapshot", "创建业务表 checksum 和 schema 备份边界。", NO_TARGET, result_description="返回业务 checksum 与 schema 观测。", preconditions=["必须配置 business-change case。"]),
                _operation("verify", "在 before 或 after 阶段对所有 TiDB endpoint 读取业务 canary 结果。", NO_TARGET, [
                    _parameter("phase", "string", required=True, allowed_values=["before", "after"], description="canary 阶段。"),
                ], result_description="返回每个 endpoint 的原始查询结果。", preconditions=["必须配置 business-change case。"]),
                _operation("upgrade", "升级一个数据库组件，并在 TiKV 场景迁移 Leader 后重建组件。", DATABASE_NODE_TARGET, result_description="返回目标组件和版本观测。", preconditions=["只能按升级顺序处理 database node。"]),
                _operation("rollback", "回滚最近一次组件升级。", DATABASE_NODE_TARGET, result_description="返回目标组件和版本观测。", preconditions=["只能回滚最近升级的组件。"]),
            ]),
            _resource("monitoring", "集群监控覆盖检查。", [
                _operation("get", "检查 PD、TiKV、TiDB 等数据库目标是否有监控覆盖。", NO_TARGET, result_description="返回监控覆盖验证结果。"),
            ]),
        ],
        result_description="成功返回 resource、operation、target 和原始 result；错误返回同样的定位字段及 error。",
    ),
    "read_log": _tool(
        "read_log",
        "读取指定集群组件的可见日志；默认最多返回 200 行，支持按行号范围或关键字上下文读取。",
        parameter_definitions=[
            _parameter(
                "target",
                "string",
                required=True,
                description="稳定组件身份，例如 pd/pd-0、tikv/tikv-0、tidb/tidb-0、ticdc/ticdc-0；通过 manage_cluster(service, list) 发现。",
            ),
            _parameter(
                "lines",
                "integer",
                required=False,
                default_value=200,
                constraints={"minimum": 1, "maximum": 200},
                unit="line",
                description="从可见日志尾部读取的行数。",
            ),
            _parameter(
                "start_line",
                "integer",
                required=False,
                constraints={"minimum": 1},
                description="可选的 1-based 起始行号；传入后按范围读取日志。",
            ),
            _parameter(
                "end_line",
                "integer",
                required=False,
                constraints={"minimum": -1},
                description="可选的 1-based 结束行号，闭区间；-1 表示最后一行。",
            ),
            _parameter(
                "match_key",
                "string",
                required=False,
                description="可选关键字；返回每条命中行的上一行到下两行上下文，大小写不敏感。",
            ),
            _parameter(
                "start_timestamp",
                "string",
                required=False,
                constraints={"format": "YYYY-MM-DD HH:mm:ss", "timezone": "UTC", "paired_with": "end_timestamp"},
                description="可选冻结历史窗口起点；传入后读取与 query_metrics 相同时间轴上的历史日志。",
            ),
            _parameter(
                "end_timestamp",
                "string",
                required=False,
                constraints={"format": "YYYY-MM-DD HH:mm:ss", "timezone": "UTC", "paired_with": "start_timestamp"},
                description="可选冻结历史窗口终点；不提供时从冻结历史的可见终点读取。返回结果仍受当前 Case 的记录条数限制。",
            ),
        ],
        result_description="返回 target、total_lines、start_line、end_line、page_limit、content；使用 match_key 时额外返回 match_key 和 matched_lines。单页最多返回 lines 行和受限字符数；截断时返回 content_truncated=true，可结合行号分页继续读取。不会返回日志可见边界之前的注入内容。",
    ),
}


def control_tool_definitions() -> dict[str, dict[str, Any]]:
    """Build the help/submit/exit contracts in the run's agent language."""
    return {
        "help": _tool(
            "help",
            agent_text(
                zh="查询当前环境的公共工具列表，或查询一个工具的完整参数和结构化调用定义。",
                en="List the public tools of the current environment, or get the full parameters and structured call definition of one tool.",
            ),
            parameter_definitions=[
                _parameter(
                    "tool_name",
                    "string",
                    required=False,
                    description=agent_text(
                        zh="不传则列出工具；传工具名则返回该工具的详细定义。",
                        en="Omit it to list the tools; pass a tool name to get that tool's detailed definition.",
                    ),
                ),
            ],
            result_description=agent_text(
                zh="help(tool_name) 返回 args 和 definition；复杂工具的 definition 是可直接照着构造 action 的 JSON 对象。",
                en="help(tool_name) returns args and definition; for complex tools, definition is a JSON object you can follow directly to construct an action.",
            ),
        ),
        "submit": _tool(
            "submit",
            agent_text(
                zh=(
                    "提交结构化诊断报告并结束当前诊断；report 必须是顶层对象，且仅包含 diagnosis、"
                    "outcome、summary 三个字段。不要把 outcome 或 summary 放入 diagnosis；结构形状为 "
                    "{diagnosis:{conditions:[...]},outcome:{changes:[...],verification:[...]},summary:string}。"
                    "提交后不能继续调用工具。"
                ),
                en=(
                    "Submit the structured diagnosis report and end the current diagnosis; report must be a top-level "
                    "object containing only the three fields diagnosis, outcome and summary. Do not put outcome or "
                    "summary inside diagnosis; the structure is "
                    "{diagnosis:{conditions:[...]},outcome:{changes:[...],verification:[...]},summary:string}. "
                    "No tools can be called after submitting."
                ),
            ),
            parameter_definitions=[
                _parameter(
                    "report",
                    "object",
                    required=True,
                    description=agent_text(
                        zh=(
                            "符合 StructuredReport schema 的顶层诊断、变更、验证和摘要；"
                            "diagnosis、outcome、summary 必须是同级字段。"
                        ),
                        en=(
                            "Top-level diagnosis, changes, verification and summary conforming to the StructuredReport "
                            "schema; diagnosis, outcome and summary must be sibling fields."
                        ),
                    ),
                ),
            ],
            report_schema=STRUCTURED_REPORT_JSON_SCHEMA,
            result_description=agent_text(
                zh="由 Agent.solve() 消费为终止控制信号；不是普通数据库操作。",
                en="Consumed by Agent.solve() as a terminating control signal; not an ordinary database operation.",
            ),
        ),
        "exit": _tool(
            "exit",
            agent_text(
                zh="放弃当前诊断流程并退出，不执行修复或提交报告。",
                en="Abandon the current diagnosis process and exit without performing a fix or submitting a report.",
            ),
            parameter_definitions=[],
            result_description=agent_text(
                zh="返回 exiting 控制状态。",
                en="Returns the exiting control status.",
            ),
        ),
    }


CONTROL_TOOL_DEFINITIONS: dict[str, dict[str, Any]] = control_tool_definitions()
