---
doc_id: scenario.tidb.tidb_resource_governance_ru_budget_calibration
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, resource_governance, tidb_resource_governance_ru_budget_calibration]
summary: tidb_resource_governance_ru_budget_calibration 的当前代码化契约快照；包含其已注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `tidb_resource_governance_ru_budget_calibration`

> 这是当前基于注册表的场景契约。请先阅读数据库目录进行导航，然后在修改实现之前，在链接的源代码中核实机制、证据、结果、安全与恢复。

## 1. 身份与范围

- 数据库：`tidb`
- 类别：`resource_governance`
- 场景实现：`src.scenarios.tidb.resource_governance.ru_budget_calibration.TidbResourceGovernanceRuBudgetCalibrationScenario`
- 正式入口：`examples/run_tidb_resource_governance_ru_budget_calibration_scenario.py`
- 当前描述：在共享上限下，为混合 OLTP 与 OLAP 工作负载校准 RU 预算。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `mixed_oltp_olap_ru_budget_calibration` | 为混合 OLTP 与 OLAP 工作负载校准 RU 预算。 | `hard` |
| 1 | `mixed_oltp_olap_ru_budget_rebalanced` | 在更紧的平台预留下重新平衡混合 OLTP 与 OLAP 的 RU 预算。 | `easy` |

上述 Case 集合是当前代码快照。缺失的校准是显式事实，不得从未注册的标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。真实故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现持有；本文档不虚构代码中不存在的值。

### `mixed_oltp_olap_ru_budget_calibration`

- Case 编号：`0`
- 标题：为混合 OLTP 与 OLAP 工作负载校准 RU 预算。
- Alert/symptom: [SEV-2] TiDB resource governance review: order-entry and revenue services share one cluster with archive and dashboard traffic. Users report uneven response time and analytical progress while the admission allocation is under review. Use the live database and workload evidence, including the operations service objectives, to choose a finite bounded allocation for the existing resource groups. Keep service continuity and order/customer truth unchanged. Do not disable resource control or restart nodes as a shortcut.
- 初始状态字段：`resource_control`, `resource_groups`
- 期望目标字段：`burstable`, `max_oltp_p95_ms`, `maximum_total_ru_per_sec`, `min_olap_qps`, `minimum_ru_per_sec`, `resource_control`
- 背景画像：rg01_oltp_order_lookup, rg01_oltp_customer_lookup, rg01_oltp_status_probe, rg01_oltp_order_update, rg01_olap_revenue_rollup, rg01_olap_region_join, rg01_oltp_order_history_probe, rg01_olap_customer_mix, rg01_batch_archive_scan, rg01_batch_customer_rollup, rg01_batch_month_close, rg01_batch_event_rollup
- 评测器：`src.scenarios.evaluation.tidb.resource_governance.ru_budget_calibration.TidbResourceGovernanceRuBudgetCalibrationEvaluatorCase`
- 难度标签与各 Case 的校准值由代码注册表和场景目录维护；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复制这些实测值。
- 校准证据（工具 m/n）：query_metrics=16/90; execute_sql=29/39; business_truth=1/0

### `mixed_oltp_olap_ru_budget_rebalanced`

- Case 编号：`1`
- 标题：在更紧的平台预留下重新平衡混合 OLTP 与 OLAP 的 RU 预算。
- Alert/symptom: [SEV-2] The order-entry and revenue workloads are both online, but the platform reservation for the next reporting window is smaller than the previous allocation. Use current workload and service-objective evidence to choose finite budgets for the existing groups, preserve order truth, and keep resource control enabled. Do not disable admission control or restart nodes.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`platform_reservation`, `resource_control`, `resource_groups`
- 期望目标字段：`burstable`, `max_oltp_p95_ms`, `maximum_total_ru_per_sec`, `min_olap_qps`, `minimum_ru_per_sec`, `resource_control`
- 背景画像：rg01_oltp_order_lookup, rg01_oltp_customer_lookup, rg01_oltp_status_probe, rg01_oltp_order_update, rg01_olap_revenue_rollup, rg01_olap_region_join, rg01_oltp_order_history_probe, rg01_olap_customer_mix, rg01_batch_archive_scan, rg01_batch_customer_rollup, rg01_batch_month_close, rg01_batch_event_rollup
- 评测器：`src.scenarios.evaluation.tidb.resource_governance.ru_budget_calibration.TidbResourceGovernanceRuBudgetCalibrationRebalancedEvaluatorCase`
- 校准证据（工具 m/n）：execute_sql(resource_groups)=4/0; execute_sql(service_objectives)=8/0; execute_sql(resource_groups_recheck)=4/0; business_truth=1/0

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

- 场景与 Case 源代码：`src.scenarios.tidb.resource_governance.ru_budget_calibration.TidbResourceGovernanceRuBudgetCalibrationScenario`
- 评测器源代码：`src/scenarios/evaluation/tidb/resource_governance/` 下的一或多个模块；确切的类已在上方按 Case 列出。
- 入口：`examples/run_tidb_resource_governance_ru_budget_calibration_scenario.py`
- 聚焦测试、参考运行与 trace 只是证据，不是第二份契约。
- 修改本文档之前，请将其与当前注册表、Case 实现、评测器、聚焦测试以及实际验证证据进行比对。
