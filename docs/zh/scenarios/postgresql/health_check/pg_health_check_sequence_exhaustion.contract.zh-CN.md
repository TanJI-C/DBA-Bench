---
doc_id: scenario.postgresql.pg_health_check_sequence_exhaustion
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, health_check, pg_health_check_sequence_exhaustion]
summary: pg_health_check_sequence_exhaustion 的当前代码背书契约快照；包含其注册的 Case、状态边界、评估器身份与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_health_check_sequence_exhaustion`

> 本文件是当前由注册表支撑的场景契约。请先阅读数据库目录进行导航，并在修改实现之前，于链接的源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`health_check`
- 场景实现：`src.scenarios.postgres.health_check.sequence_exhaustion.PgHealthCheckSequenceExhaustionScenario`
- 正式入口：`examples/run_pg_health_check_sequence_exhaustion_scenario.py`
- 当前描述：通过把 INT4 序列推进到接近其最大值来模拟序列耗尽。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `billing_canary_int4_sequence_exhaustion` | 模拟放量前一次带噪声的计费金丝雀失败：由耗尽的 INT4 写路径序列导致。 | `easy` |
| 1 | `billing_sequence_capacity_risk_simple` | 一个处于 INT4 上限的计费写路径序列，附带一个高值的 BIGINT 对比序列。 | `hard` |

上表是当前的代码快照。缺失的校准是显式的，不得从未注册的标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公共状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 和评估器实现所有；本文档不编造代码中不存在的值。

### `billing_canary_int4_sequence_exhaustion`

- Case 编号：`0`
- 标题：模拟放量前一次带噪声的计费金丝雀失败：由耗尽的 INT4 写路径序列导致。
- Alert/symptom: [Pre-ramp Validation] Overnight billing canary writes reported a small number of insert failures while dashboards, reports, and monitor probes stayed mostly healthy. Review the database evidence, separate the current write-path issue from routine background noise, and submit a safe remediation plan.
- 初始状态字段：`column_type`、`last_value`、`sequence`、`status`、`table`
- 期望目标字段：`recommendation`、`sequence`、`status`、`table`
- 背景画像：未声明
- 评估器：`src.scenarios.evaluation.postgres.health_check.sequence_exhaustion.PgHealthCheckSequenceExhaustionForBillingCanaryInt4SequenceExhaustionEvaluatorCase`
- 难度标签与逐 Case 校准值由代码注册表和场景目录维护；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约刻意不重复这些实测值。

### `billing_sequence_capacity_risk_simple`

- Case 编号：`1`
- 标题：一个处于 INT4 上限的计费写路径序列，附带一个高值的 BIGINT 对比序列。
- Alert/symptom: [Pre-ramp Capacity Review] A billing canary write failed while general database checks remained healthy. Identify the capacity-limited database object, bind it to its owning column, exclude the comparison object, and submit a safe migration plan.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`column_type`、`status`、`table`
- 期望目标字段：`recommendation`、`status`
- 背景画像：未声明
- 评估器：`src.scenarios.evaluation.postgres.health_check.sequence_exhaustion.PgHealthCheckSequenceExhaustionForBillingSequenceCapacityRiskSimpleEvaluatorCase`
- 校准证据（工具 m/n）：代码中未声明

## 4. Agent 可见的证据

- Agent 接收注册的告警，并在运行时暴露的范围内通过当前工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`。
- 告警只是定位提示，而不是根因答案。确切的证据、干扰项、可见性限制以及任何知识或历史观测工具，都必须在场景与评估器源代码中核实。
- 不要把参考报告、注入器证据、评估器自有的观测或隐藏的条件 ID 当作 Agent 可见的证据。

## 5. DP / OP / SP 契约

- **DP** 是注册 Case 的评估器自有语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。
- **OP** 是评估器的终态与业务事实契约。上文的期望目标字段界定了状态边界；被接受的修复与等价结果由评估器定义。
- **SP** 独立检查危险操作、影响范围、受保护对象以及未经授权的状态漂移。它不是 OP 的替代品。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从遗留文档复制历史评分公式。

## 6. 修复、归属与恢复

- 使用当前评估器和场景契约接受的修复族。操作顺序、SQL 写法、索引名称和报告措辞都不是硬性要求，除非代码明确将其纳入公共契约。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前的五阶段协议释放 Case 持有的连接、会话、线程、进程、文件、配置和数据库状态。

## 7. 代码地图与验证

- 场景与 Case 源码：`src.scenarios.postgres.health_check.sequence_exhaustion.PgHealthCheckSequenceExhaustionScenario`
- 评估器源码：`src/scenarios/evaluation/postgres/health_check/` 下的一个或多个模块；确切的类已在上方逐 Case 列出。
- 入口：`examples/run_pg_health_check_sequence_exhaustion_scenario.py`
- 聚焦测试、参考运行和轨迹是证据，而不是第二份契约。
- 在修改本文档之前，请将其与当前注册表、Case 实现、评估器、聚焦测试和实际验证证据进行比对。
