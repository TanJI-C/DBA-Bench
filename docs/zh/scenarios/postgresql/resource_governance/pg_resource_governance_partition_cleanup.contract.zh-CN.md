---
doc_id: scenario.postgresql.pg_resource_governance_partition_cleanup
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, pg_resource_governance_partition_cleanup]
summary: pg_resource_governance_partition_cleanup 的当前基于代码的契约快照；包含其注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_resource_governance_partition_cleanup`

> 这是当前基于注册中心的场景（Scenario）契约。请先阅读数据库目录进行导航，然后在修改实现之前，于关联源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`resource_governance`
- 场景实现：`src.scenarios.postgres.resource_governance.partition_cleanup.PgResourceGovernancePartitionCleanupScenario`
- 正式入口：`examples/run_pg_resource_governance_partition_cleanup_scenario.py`
- 当前描述：由真实文件系统支撑的分区保留期清理造成的主机 CPU 压力。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `filesystem_cleanup_pressure` | 由文件系统支撑的保留期分区清理造成的主机 CPU 压力。 | `hard` |
| 1 | `filesystem_cleanup_pressure_simple` | 简化的文件系统分区清理压力，伴随 OLTP 尾延迟。 | `easy` |

上方的 Case 集合是当前的代码快照。缺失校准是显式状态，不得从非注册标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现持有；本文档不杜撰代码中不存在的值。

### `filesystem_cleanup_pressure`

- Case 编号：`0`
- 标题：由文件系统支撑的保留期分区清理造成的主机 CPU 压力。
- Alert/symptom: [FIRING: WARNING] alertname=PostgresHostCpuPressure service=oltp-orders instance=postgresql-primary severity=warning summary=Host CPU pressure and OLTP tail latency exceeded SLO description=The database host had a short CPU pressure episode while transaction tail latency rose. The episode has recovered on its own. Reports, backup, and maintenance jobs were active in the same window. An application change was rolled out on this host earlier today. (Full recovery contract and case-specific observation names are published through the runtime `help` contract; the alert intentionally carries no diagnostic hints.)
- 初始状态字段：`alert`, `status`, `visible_symptom`
- 期望目标字段：`legal_hold`, `retention`, `root_cause`, `status`
- 背景工作负载配置：pc-hard-tpcds-q14、pc-hard-tpcds-q75、pc-hard-tpcds-q95
- 评测器：`src.scenarios.evaluation.postgres.resource_governance.partition_cleanup.PgResourceGovernancePartitionCleanupForFilesystemCleanupPressureEvaluatorCase`
- 难度标签与各 Case 的校准值维护在代码注册中心与场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复述这些实测值。
- 夹具（Fixture）：`pc_hard_retention_policy` 公布已批准的法律保留（legal hold）清单；目录初始含一个过期分区，其 `legal_hold` 标志与该清单矛盾；在因果链被确认之后，一个存活的过期配置自动化会话（`pc-hard-config-agent`）每隔几秒就把存储的快照——`retention_days=30, paused=true`——重新应用到清理作业上。重新应用在辅助函数 `aiopsbench_retention_worker_feed` 内部运行，因此 `pg_stat_activity.query` 与 `pg_stat_statements` 都不会显示越界的 UPDATE 文本；会话表面只显示一次中性调用。当其会话被终止时，该代理会永久退出（脆弱自动化语义）。因此，恢复需要把观测到的配置回翻与活跃会话（或其辅助函数）关联起来，并在修复作业行之前先止住源头。
- 恢复闸门说明：主机级 CPU PSI（`cpu_pressure_some_avg10`）在共享主机上是同租户噪声，仅作为可观测性信息上报；阻断恢复的阈值是文件系统 I/O 与 OLTP 延迟上限加上所有最终状态不变式。

#### 标准诊断与修复路径

题面只是主机压力/OLTP 症状。参考诊断先把原始
`filesystem_io` 序列与 `bufferio_waiters` 关联，再对比主机压力与 PostgreSQL 查询 CPU，
最后把 `partition_lifecycle` 与清理作业及 OLTP 受害者连接起来。报表、备份、
checkpoint 与小分区活动是同域噪声，而非答案。

解释性的参考修复是：限制或暂停保留期工作进程，保留法律保留（legal hold），
把目录中的 `legal_hold` 标志与已批准的 `pc_hard_retention_policy` 清单对齐，禁用漂移源治理作业
（或把其时间跨度收回已公布范围内），把清理作业的 `retention_days` 校正回该范围内，通过保留期工作流
完成所有到期的非保留清理，把作业恢复为启用/未暂停，并验证已公布的恢复窗口。
OP 不要求完全一致的 SQL、顺序、对象名称或工具序列；实质等价的
批量、调度或清理存储变更同样有效。

OutcomePass 要求：恰好一个仍处于挂载状态的法律保留分区、零个被分离（detach）的分区、零个到期的非保留
分区、不存在已删除目录/表的不匹配、没有启用中且时间跨度超出已公布范围的治理作业、
作业处于启用且未暂停状态并满足 `1 <= retention_days <= max_retention_days`，以及至少
`recovery_sample_count` 个样本落在公开的文件系统 I/O 与 OLTP p99 限值内。
文件系统 I/O 上限为 60 MB/s：它容忍清理之后更长的干扰尾（报表/备份/
压缩器），同时仍然拒绝用于确立故障的 100+ MB/s 清理尖峰。
主机级 CPU PSI 只是上报的观测值，不作为恢复闸门。它
不检查报告措辞、固定操作顺序或额外的
仅供参考查询。

### `filesystem_cleanup_pressure_simple`

- Case 编号：`1`
- 标题：简化的文件系统分区清理压力，伴随 OLTP 尾延迟。
- Alert/symptom: [FIRING: WARNING] alertname=PostgresHostCpuPressure service=checkout-api instance=postgresql-primary severity=warning summary=Host pressure and checkout tail latency crossed SLO together description=Checkout latency rose during a host pressure episode that is now clear. A small number of cleanup and reporting jobs were also active. Preserve the retention boundary and legal hold. You may use the case-specific filesystem_io, bufferio_waiters, host_pressure, and partition_lifecycle observations exposed by query_metrics. For final recovery, keep the cleanup job enabled and unpaused, preserve the legal hold, remove all due non-hold partitions through the retention cleanup workflow without detached leftovers, and verify the last 2 samples are within the published filesystem-I/O and OLTP latency limits; host CPU pressure stays a reported observation.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`alert`, `status`, `visible_symptom`
- 期望目标字段：`legal_hold`, `retention`, `root_cause`, `status`
- 背景工作负载配置：pc-easy-tpcds-q14
- 评测器：`src.scenarios.evaluation.postgres.resource_governance.partition_cleanup.PgResourceGovernancePartitionCleanupForFilesystemCleanupPressureSimpleEvaluatorCase`

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

- Scenario 与 Case 源代码：`src.scenarios.postgres.resource_governance.partition_cleanup.PgResourceGovernancePartitionCleanupScenario`
- 评测器源代码：`src/scenarios/evaluation/postgres/resource_governance/` 下的一个或多个模块；确切的类已在上方按 Case 列出。
- 入口：`examples/run_pg_resource_governance_partition_cleanup_scenario.py`
- 聚焦测试、参考运行与调用轨迹只是证据，并非第二份契约。
- 在修改本文档之前，请将其与当前注册中心、Case 实现、评测器、聚焦测试以及实时验证证据进行比对。
