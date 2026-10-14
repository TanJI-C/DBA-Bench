---
doc_id: scenario.postgresql.pg_system_failure_io_checkpoint_spikes
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, system_failure, pg_system_failure_io_checkpoint_spikes]
summary: pg_system_failure_io_checkpoint_spikes 的当前基于代码的契约快照；包含其注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_system_failure_io_checkpoint_spikes`

> 这是当前由注册表支撑的场景契约。请先阅读数据库目录进行导航，然后在修改实现之前，到链接的源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`system_failure`
- 场景实现：`src.scenarios.postgres.system_failure.io_checkpoint_spikes.PgSystemFailureIoCheckpointSpikesScenario`
- 正式入口：`examples/run_pg_system_failure_io_checkpoint_spikes_scenario.py`
- 当前描述：模拟由过于激进的检查点设置导致的周期性磁盘 I/O 尖峰。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `checkout_checkpoint_spikes` | 模拟由过于激进的检查点设置导致的周期性磁盘 I/O 尖峰。 | `easy` |
| 1 | `single_checkout_checkpoint_spike_simple` | 单个结账写流暴露出由不安全检查点设置导致的检查点 I/O 尖峰。 | `easy` |

上表中的 Case 集合是当前的代码快照。校准缺失是显式声明的，不得从未注册的标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约公开的状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 和评测器实现所拥有；本文档不会编造代码中不存在的值。

### `checkout_checkpoint_spikes`

- Case 编号：`0`
- 标题：模拟由过于激进的检查点设置导致的周期性磁盘 I/O 尖峰。
- Alert/symptom: [CRITICAL] Order-write path latency has been showing periodic spikes every few dozen seconds; some orders take >5s to ack. Correlate the write stalls with database state, restore safe settings, and verify the reproducibility of the fix, and then submit.
- 初始状态字段：`checkpoint`, `status`, `symptom`
- 期望目标字段：`checkpoint`, `status`, `verification`
- 背景画像：tpcds_q68, tpcds_q73, tpcds_q79, tpcds_q48, tpcds_q81, tpcds_q71, tpcds_q10, tpcds_q87, tpcds_q49, checkpoint_log_noise_statement_timeout_dashboard_refresh, checkpoint_log_noise_missing_billing_rollup, checkpoint_log_noise_invalid_order_batch
- 评测器：`src.scenarios.evaluation.postgres.system_failure.io_checkpoint_spikes.PgSystemFailureIoCheckpointSpikesForCheckoutCheckpointSpikesEvaluatorCase`
- 难度标签与每个 Case 的校准值维护在代码注册表和场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不重复这些实测值。

### `single_checkout_checkpoint_spike_simple`

- Case 编号：`1`
- 标题：单个结账写流暴露出由不安全检查点设置导致的检查点 I/O 尖峰。
- Alert/symptom: Alert: Checkout writes show repeated short latency spikes while PostgreSQL stays available. A low-rate calendar lookup is also active. Correlate the write stalls with database state, restore safe settings, and verify the change.
> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。
- 初始状态字段：`database`, `status`, `symptom`
- 期望目标字段：`checkpoint`, `database_probe`, `status`
- 背景画像：checkout_calendar_lookup
- 评测器：`src.scenarios.evaluation.postgres.system_failure.io_checkpoint_spikes.PgSystemFailureIoCheckpointSpikesForSingleCheckoutCheckpointSpikeSimpleEvaluatorCase`
- 校准证据（工具 m/n）：代码中未声明

## 4. Agent 可见证据

- Agent 接收注册的告警，并通过当前工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`（以运行时实际暴露的为准）。
- 告警只是定向提示，不是根因答案。确切证据、诱饵、可见性限制以及任何知识或历史观测工具，都必须在 Scenario 与评测器源代码中核实。
- 不要把参考报告、注入器证据、评测器自有的观测或隐藏的条件 ID 当作 Agent 可见证据。

## 5. DP / OP / SP 契约

- **DP** 是注册 Case 的评测器自有语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。
- **OP** 是评测器的最终状态与业务真相契约。上文的期望目标字段标识状态边界；被接受的修复与等价结果由评测器定义。
- **SP** 独立检查危险操作、影响半径、受保护对象和未经授权的状态漂移。它不能替代 OP。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从旧文档中复制历史评分公式。

## 6. 修复、归属与恢复

- 使用当前评测器与场景契约所接受的修复族。除非代码明确将其纳入公开契约，否则操作顺序、SQL 写法、索引名称与报告措辞都不是要求。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前五阶段协议释放 Case 持有的连接、会话、线程、进程、文件、配置与数据库状态。

## 7. 代码映射与验证

- 场景与 Case 源代码：`src.scenarios.postgres.system_failure.io_checkpoint_spikes.PgSystemFailureIoCheckpointSpikesScenario`
- 评测器源代码：`src/scenarios/evaluation/postgres/system_failure/` 下的一个或多个模块；确切类名已在上方按 Case 列出。
- 入口：`examples/run_pg_system_failure_io_checkpoint_spikes_scenario.py`
- 聚焦测试、参考运行与追踪记录是证据，而不是第二份契约。
- 在修改本文档之前，请将其与当前注册表、Case 实现、评测器、聚焦测试以及实际验证证据进行比对。
