---
doc_id: scenario.tidb.tidb_resource_governance_rg06
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, resource_governance, tidb_resource_governance_rg06]
summary: tidb_resource_governance_rg06 的当前代码化契约快照；包含其已注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `tidb_resource_governance_rg06`

> 这是当前基于注册表的场景契约。请先阅读数据库目录进行导航，然后在修改实现之前，在链接的源代码中核实机制、证据、结果、安全与恢复。

## 1. 身份与范围

- 数据库：`tidb`
- 类别：`resource_governance`
- 场景实现：`src.scenarios.tidb.resource_governance.rg06_ticdc_checkpoint_lag.TidbResourceGovernanceRg06Scenario`
- 正式入口：`examples/run_tidb_resource_governance_rg06_scenario.py`
- 当前描述：在真实 SQL 源/汇测试装置、前台业务工作负载与 GC 余量约束下，治理 TiCDC checkpoint 延迟与 sink 预算。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `ticdc_checkpoint_sink_budget` | 在前台与下游 SLO 约束下调优一条滞后的 TiCDC 风格流水线。 | `hard` |
| 1 | `ticdc_reconcile_sink_budget` | 调优对账 changefeed，而不干扰归档 feed。 | `easy` |

上述 Case 集合是当前代码快照。缺失的校准是显式事实，不得从未注册的标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。真实故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现持有；本文档不虚构代码中不存在的值。

### `ticdc_checkpoint_sink_budget`

- Case 编号：`0`
- 标题：在前台与下游 SLO 约束下调优一条滞后的 TiCDC 风格流水线。
- Alert/symptom: [CRITICAL] archive freshness has breached its customer window while the replication service still reports NORMAL. Online order reads and downstream archive readers share this TiDB cluster, and the retention guard is active. Determine which registered business flow is affected and choose a bounded synchronization budget without changing business data or global resource settings.
- 初始状态字段：`foreground`, `retention`, `state`, `symptom`
- 期望目标字段：`max_budget_load_factor`, `max_checkpoint_lag_rows`, `max_downstream_p95_ms`, `max_error_count`, `max_foreground_p95_ms`, `max_overload_events`, `min_gc_headroom_seconds`, `min_sink_rows_per_second`, `safe_sink_batch_rows`, `safe_sink_workers`, `safe_sink_write_budget`, `safe_sorter_memory_mb`, `state`
- 背景画像：rg06_source_order_lookup, rg06_source_tenant_rollup, rg06_sink_order_lookup, rg06_sink_tenant_rollup, rg06_reconcile_source_lookup, rg06_reconcile_sink_lookup, rg06_archive_retention_scan, rg06_observability_health
- 评测器：`src.scenarios.evaluation.tidb.resource_governance.rg06_ticdc_checkpoint_lag.TidbResourceGovernanceRg06EvaluatorCase`
- 难度标签与各 Case 的校准值由代码注册表和场景目录维护；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复制这些实测值。
- 校准证据（工具 m/n）：execute_sql(rg06_changefeed_registry)=1/1; execute_sql(rg06_cdc_metrics.progress)=18/182; execute_sql(rg06_cdc_metrics.pipeline)=21/179; execute_sql(rg06_cdc_metrics.resource)=3/197; execute_sql(rg06_cdc_config)=1/0

### `ticdc_reconcile_sink_budget`

- Case 编号：`1`
- 标题：调优对账 changefeed，而不干扰归档 feed。
- Alert/symptom: [CRITICAL] the settlement reconciliation mirror has breached its freshness window while the archive feed reports normal service. Inspect the changefeed registry and raw progress, pipeline, resource, and GC evidence to identify the affected feed. Apply a bounded local sink budget, preserve the archive feed and foreground order truth, and do not change global settings or data.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`foreground`, `protected_neighbor`, `state`, `symptom`
- 期望目标字段：`max_budget_load_factor`, `max_checkpoint_lag_rows`, `max_downstream_p95_ms`, `max_error_count`, `max_foreground_p95_ms`, `max_overload_events`, `min_gc_headroom_seconds`, `min_sink_rows_per_second`, `protected_neighbor`, `safe_sink_batch_rows`, `safe_sink_workers`, `safe_sink_write_budget`, `safe_sorter_memory_mb`, `state`, `target_changefeed`
- 背景画像：rg06_source_order_lookup, rg06_source_tenant_rollup, rg06_sink_order_lookup, rg06_sink_tenant_rollup, rg06_reconcile_source_lookup, rg06_reconcile_sink_lookup, rg06_archive_retention_scan, rg06_observability_health
- 评测器：`src.scenarios.evaluation.tidb.resource_governance.rg06_ticdc_checkpoint_lag.TidbResourceGovernanceRg06NeighborFeedEvaluatorCase`
- 校准证据（工具 m/n）：execute_sql(changefeed_registry)=2/0; execute_sql(cdc_metrics.progress)=332/0; execute_sql(cdc_config)=1/0; execute_sql(cdc_metrics.pipeline)=105/95

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

- 场景与 Case 源代码：`src.scenarios.tidb.resource_governance.rg06_ticdc_checkpoint_lag.TidbResourceGovernanceRg06Scenario`
- 评测器源代码：`src/scenarios/evaluation/tidb/resource_governance/` 下的一或多个模块；确切的类已在上方按 Case 列出。
- 入口：`examples/run_tidb_resource_governance_rg06_scenario.py`
- 聚焦测试、参考运行与 trace 只是证据，不是第二份契约。
- 修改本文档之前，请将其与当前注册表、Case 实现、评测器、聚焦测试以及实际验证证据进行比对。
