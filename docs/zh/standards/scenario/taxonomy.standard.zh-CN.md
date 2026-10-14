---
doc_id: standard.scenario.taxonomy
doc_type: standard
status: canonical
audience: [authoring, reviewer, maintainer, runtime_agent]
exposure: agent_safe
scope: [shared, scenario, postgres, tidb]
summary: Defines the current database-specific Scenario category boundaries, Agent tool surface, and the separation between catalog navigation and DP/OP/SP evaluation.
source_of_truth: code
related: [catalog.postgresql-scenarios, catalog.tidb-scenarios, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp]
language: zh-CN
---

# Scenario 分类与工具面

本文定义当前 DBA-Bench Scenario 的分类边界和公共 Agent 工具面。它只说明如何理解和定位
场景，不列举具体 Scenario/Case；正式注册表和 Case 快照见 [PostgreSQL 场景目录](../../../catalogs/postgresql-scenarios.catalog.md)
与 [TiDB 场景目录](../../../catalogs/tidb-scenarios.catalog.md)。

## 1. 当前分类

PostgreSQL 正式 Scenario 只能归入以下五类：

| 类别 | 任务边界 |
| --- | --- |
| `query_perf` | 已知 SQL 或 SQL 指纹发生性能退化，需要定位执行、统计或存储路径问题 |
| `system_failure` | 服务、事务、复制或存储已异常，需要识别主要故障并恢复 |
| `health_check` | 主动巡检、容量、一致性或变更前检查，目标是发现风险并形成可信结论 |
| `business_change` | 升级、迁移、扩缩容、备份恢复、容灾切换和计划内 DDL/DML |
| `resource_governance` | 在业务 SLO、安全或合规约束下治理 RU、并发、存储、拓扑和后台任务预算 |

复合因果链和误导性首屏证据是 Case 的难度与证据结构，不是顶层任务类别。多根因任务
按主要运维目标归入上表；告警归因偏差按真实问题归入对应业务类别。两个数据库的 catalog
分别记录当前注册分布；类别枚举只保留上述五类。

名词本身不决定分类：计划内恢复归入 `business_change`，多数副本丢失后的故障恢复归入
`system_failure`，前台 SLO 下的恢复调速归入 `resource_governance`。不为单个业务主题
额外创建新类别。

## 2. Agent 工具面

Agent 通过公共协议观察和处理 Scenario：

- `query_metrics`：读取环境资源、负载和声明的指标时序；
- `execute_sql`：按任务需要查询数据库状态、锁、对象、业务结果和其他 SQL-backed 细节；
- `manage_instance`：执行显式的实例生命周期动作；
- `read_log`：读取有边界的数据库或容器日志；
- `help`、`submit`、`exit`：协议控制和结构化提交。

工具参数、返回 envelope、权限和安全边界以当前环境与代码协议为准。文档不能把 evaluator
内部观察、注入 evidence 或固定答案冒充 Agent 工具结果。

## 3. 评估边界

DP、OP、SP 是三个独立判定面，定义和实现见 [DP、OP、SP 标准](../../../standards/evaluation/dp-op-sp.standard.md)：

- DP 只判断最终结构化诊断是否表达根因；无根因任务使用 `DiagnosisPass=None`；
- OP 从最终环境、业务真值或可信 artifact 判断任务是否完成，并接受安全且实质等价的修复；
- SP 独立判断动作过程是否造成真实安全问题；效率、动作数量和 MTTR 只作为描述性证据；
- 有效运行的失败交给独立 trace-level judge 按诊断、修复路径和证据语义分类，不用 DP/OP/SP
  的具体值或组合机械推断失败类型。

难度不是评估加权项。`D_s`、`C_s`、reference run、`m/n` 计数和 `Easy`/`Hard` 标签统一见
[Scenario 难度标准](../../../standards/scenario/difficulty.standard.md)。

## 4. 阅读顺序

先读对应数据库 catalog，再读当前 Scenario/Case 合同和代码。catalog 是导航和当前注册表快照，
不替代具体合同。
