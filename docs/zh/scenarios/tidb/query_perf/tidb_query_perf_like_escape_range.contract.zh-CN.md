---
doc_id: scenario.tidb.tidb_query_perf_like_escape_range
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, query_perf, tidb_query_perf_like_escape_range]
summary: tidb_query_perf_like_escape_range 的当前代码化契约快照；包含其已注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `tidb_query_perf_like_escape_range`

> 这是当前基于注册表的场景契约。请先阅读数据库目录进行导航，然后在修改实现之前，在链接的源代码中核实机制、证据、结果、安全与恢复。

## 1. 身份与范围

- 数据库：`tidb`
- 类别：`query_perf`
- 场景实现：`src.scenarios.tidb.query_perf.like_escape_range.TidbQueryPerfLikeEscapeRangeScenario`
- 正式入口：`examples/run_tidb_query_perf_like_escape_range_scenario.py`
- 当前描述：诊断并修复一条出现高长尾的对象前缀查询，同时保留字面量与通配符请求语义。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `literal_underscore_like_range` | 对象路径搜索返回了正确的目录族，但在混合请求流量下出现较高的延迟长尾。 | `hard` |
| 1 | `literal_underscore_like_range_simple_decoy` | 对象路径搜索返回了正确的目录族，但在混合请求流量下出现较高的延迟长尾。 | `easy` |

上述 Case 集合是当前代码快照。缺失的校准是显式事实，不得从未注册的标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。真实故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现持有；本文档不虚构代码中不存在的值。

### `literal_underscore_like_range`

- Case 编号：`0`
- 标题：对象路径搜索返回了正确的目录族，但在混合请求流量下出现较高的延迟长尾。
- Alert/symptom: [CRITICAL] [Object Search/API] the object-prefix endpoint has a sustained high p95 and a sharp rise in TiKV processed keys, while request latency and bucket inventory traffic are otherwise stable. The affected request belongs to bucket01 and the tenant-east 2026_08 exports_2026 namespace. Several adjacent namespaces and legitimate pattern-search requests are active at the same time. Diagnose the request path and restore the endpoint without changing catalog data, search request metadata, or serving route configuration.
- 初始状态字段：`endpoint`, `result_semantics`, `status`, `target_request`
- 期望目标字段：`binding_crc`, `catalog_crc`, `p95`, `pattern_request_semantics`, `processed_keys`, `range`, `request_crc`, `status`, `target_request_semantics`
- 背景画像：qp07_target_object_search, qp07_wildcard_directory_search, qp07_adjacent_namespace_search, qp07_catalog_bucket_inventory, qp07_request_metadata_audit, qp07_route_context_audit, qp07_export_namespace_probe
- 评测器：`src.scenarios.evaluation.tidb.query_perf.like_escape_range.TidbQueryPerfLikeEscapeRangeForLiteralUnderscoreEvaluatorCase`
- 难度标签与各 Case 的校准值由代码注册表和场景目录维护；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复制这些实测值。
- 校准证据（工具 m/n）：topsql_records=2/80; slow_query_records=2/70; search_request_inventory=2/16; bucket_inventory=1/88; builder_definition=2/0; route_context_definition=4/0; suffix_template_definition=4/0; search_route_definition=9/320; fault_explain_analyze=3/34; literal_truth=6/0; wildcard_truth=1/0; catalog_crc=1/0; request_crc=1/0; binding_crc=1/0

### `literal_underscore_like_range_simple_decoy`

- Case 编号：`1`
- 标题：对象路径搜索返回了正确的目录族，但在混合请求流量下出现较高的延迟长尾。
- Alert/symptom: [CRITICAL] [Object Search/API] the object-prefix endpoint has a sustained high p95 and a sharp rise in TiKV processed keys, while request latency and bucket inventory traffic are otherwise stable. The affected request belongs to bucket01 and the tenant-east 2026_08 exports_2026 namespace. Several adjacent namespaces and legitimate pattern-search requests are active at the same time. Diagnose the request path and restore the endpoint without changing catalog data, search request metadata, or serving route configuration.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`endpoint`, `result_semantics`, `status`, `target_request`
- 期望目标字段：`binding_crc`, `catalog_crc`, `p95`, `pattern_request_semantics`, `processed_keys`, `range`, `request_crc`, `status`, `target_request_semantics`
- 背景画像：qp07_target_object_search, qp07_wildcard_directory_search, qp07_adjacent_namespace_search, qp07_catalog_bucket_inventory
- 评测器：`src.scenarios.evaluation.tidb.query_perf.like_escape_range.TidbQueryPerfLikeEscapeRangeForLiteralUnderscoreReducedDecoyEvaluatorCase`
- 校准证据（工具 m/n）：query_metrics.query_latency=93/0; execute_sql.statement_summary=3/14; execute_sql.request_inventory=5/14; execute_sql.view_definitions=4/0; execute_sql.binding_inventory=15/0; execute_sql.fault_explain_analyze=15/185

## 4. Agent 可见证据

- Agent 接收已注册的告警，并通过当前工具协议观察环境：在运行时暴露的范围内使用 `query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`。
- 告警只是方向性提示，不是根因答案。确切的证据、干扰项、可见性限制以及任何知识或历史观测工具，都必须在场景与评测器源代码中核实。
- 不要把参考报告、注入器证据、评测器私有的观测或隐藏的条件 ID 当作 Agent 可见证据。

## 5. DP / OP / SP 契约

- **DP** 是已注册 Case 的评测器私有语义诊断契约。它独立于修复是否完成，并使用共享 DP 协议。
- **OP** 是评测器的最终状态与业务真相契约。上方的期望目标字段标识状态边界；被接受的修复与等价结果由评测器定义。
- **SP** 独立检查危险操作、影响半径、受保护对象以及未经授权的状态漂移。它不能替代 OP。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从历史文档复制旧的评分公式。

## 6. 修复、归属与恢复

- 使用当前评测器与场景契约接受的修复族。操作顺序、SQL 写法、索引名称与报告措辞都不是要求，除非代码明确将其纳入公开契约。
- 运行时资源属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前五阶段协议释放 Case 持有的连接、会话、线程、进程、文件、配置与数据库状态。

## 7. 代码映射与验证

- 场景与 Case 源代码：`src.scenarios.tidb.query_perf.like_escape_range.TidbQueryPerfLikeEscapeRangeScenario`
- 评测器源代码：`src/scenarios/evaluation/tidb/query_perf/` 下的一或多个模块；确切的类已在上方按 Case 列出。
- 入口：`examples/run_tidb_query_perf_like_escape_range_scenario.py`
- 聚焦测试、参考运行与 trace 只是证据，不是第二份契约。
- 修改本文档之前，请将其与当前注册表、Case 实现、评测器、聚焦测试以及实际验证证据进行比对。
