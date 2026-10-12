---
doc_id: scenario.postgresql.pg_resource_governance_audit_logging
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, resource_governance, pg_resource_governance_audit_logging]
summary: pg_resource_governance_audit_logging 的当前基于代码的契约快照；包含其注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_resource_governance_audit_logging`

> 这是当前基于注册中心的场景（Scenario）契约。请先阅读数据库目录进行导航，然后在修改实现之前，于关联源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`resource_governance`
- 场景实现：`src.scenarios.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingScenario`
- 正式入口：`examples/run_pg_resource_governance_audit_logging_scenario.py`
- 当前描述：模拟高 QPS OLTP 工作负载下过量审计日志放大磁盘写入。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `audit_orders_role_logging` | 模拟高 QPS OLTP 工作负载下过量审计日志放大磁盘写入。 | `easy` |
| 1 | `orders_write_audit_scope_simple` | 聚焦的审计日志 Case：一张结账表与一个合规角色。 | `easy` |

上方的 Case 集合是当前的代码快照。缺失校准是显式状态，不得从非注册标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现持有；本文档不杜撰代码中不存在的值。

### `audit_orders_role_logging`

- Case 编号：`0`
- 标题：模拟高 QPS OLTP 工作负载下过量审计日志放大磁盘写入。
- Alert/symptom: P1 production alert: after a compliance logging rollout, checkout transaction throughput dropped by more than half and disk write bandwidth is near saturation. WAL volume and table bloat do not explain the write amplification. Identify the logging source and restore transaction throughput without disabling required compliance coverage.
- 初始状态字段：`audit_scope`, `disk_write_amplification`, `status`, `transaction_throughput`
- 期望目标字段：`audit_scope`, `statement_logging`, `status`, `transaction_throughput`
- 背景工作负载配置：checkout_status_rollup、payment_reconciliation_preview、checkout_live_touch_probe、receipt_latency_probe、missing_compliance_cache_log_noise
- 评测器：`src.scenarios.evaluation.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingEvaluatorCase`
- 难度标签与各 Case 的校准值维护在代码注册中心与场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复述这些实测值。

### `orders_write_audit_scope_simple`

- Case 编号：`1`
- 标题：聚焦的审计日志 Case：一张结账表与一个合规角色。
- Alert/symptom: P2 compliance rollout alert: checkout write throughput dropped after audit logging was enabled. Disk writes are elevated, but WAL and table growth do not explain the spike. Keep required write/DDL/role audit coverage while restoring transaction throughput.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`audit_scope`, `disk_write_amplification`, `status`
- 期望目标字段：`audit_scope`, `statement_logging`, `status`
- 背景工作负载配置：checkout_status_rollup
- 评测器：`src.scenarios.evaluation.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingForOrdersWriteAuditScopeSimpleEvaluatorCase`
- 校准证据（工具 m/n）：query_metrics.disk_io/qps=2/1；execute_sql.pg_settings/log_probe=3/1

## 4. Agent 可见证据

- Agent 接收已注册的告警，并通过当前工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`（以运行时实际暴露的为准）。
- 告警只是定位提示，而不是根因答案。确切的证据、干扰项、可见性限制以及任何知识或历史观测工具，都必须在 Scenario 与评测器源代码中核实。
- 不得把参考报告、注入器证据、评测器私有的观测或隐藏的条件 ID 当作 Agent 可见证据。

## 5. DP / OP / SP 契约

- **DP** 是针对已注册 Case 的、由评测器持有的语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。
- **OP** 是评测器的最终状态与业务真值契约。上方的期望目标字段标识状态边界；可接受的修复与等价结果由评测器定义。
- **SP** 独立检查危险操作、影响范围（blast radius）、受保护对象以及未经授权的状态漂移。它不能替代 OP。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从历史遗留文档复制评分公式。

## 6. 修复、归属与恢复

- 使用当前评测器与 Scenario 契约接受的修复族。操作顺序、SQL 写法、索引名称与报告措辞均非硬性要求，除非代码明确将其纳入公开契约。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前五阶段协议释放 Case 持有的连接、会话、线程、进程、文件、配置与数据库状态。

## 7. 代码地图与验证

- Scenario 与 Case 源代码：`src.scenarios.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingScenario`
- 评测器源代码：`src/scenarios/evaluation/postgres/resource_governance/` 下的一个或多个模块；确切的类已在上方按 Case 列出。
- 入口：`examples/run_pg_resource_governance_audit_logging_scenario.py`
- 聚焦测试、参考运行与调用轨迹只是证据，并非第二份契约。
- 在修改本文档之前，请将其与当前注册中心、Case 实现、评测器、聚焦测试以及实时验证证据进行比对。
