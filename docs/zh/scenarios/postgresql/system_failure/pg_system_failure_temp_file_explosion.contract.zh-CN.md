---
doc_id: scenario.postgresql.pg_system_failure_temp_file_explosion
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, system_failure, pg_system_failure_temp_file_explosion]
summary: pg_system_failure_temp_file_explosion 的当前基于代码的契约快照；包含其已注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_system_failure_temp_file_explosion`

> 本文档是当前基于注册表的场景（Scenario）契约。请先阅读数据库目录进行导航，然后在修改实现之前，于链接的源代码中核实机制、证据、结果、安全性与恢复。

## 1. 标识与范围

- 数据库：`postgresql`
- 类别：`system_failure`
- 场景实现：`src.scenarios.postgres.system_failure.temp_file_explosion.PgSystemFailureTempFileExplosionScenario`
- 正式入口：`examples/run_pg_system_failure_temp_file_explosion_scenario.py`
- 当前描述：模拟一个报表批次在正常生产噪声中溢出临时文件所导致的写入失败。

## 2. 当前 Case 集合

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `nightly_margin_temp_exhaustion` | 模拟一个报表批次在正常生产噪声中溢出临时文件所导致的写入失败。 | `hard` |
| 1 | `daily_sales_temp_exhaustion_simple` | 一个每日销售汇总批处理填满 PostgreSQL 暂存空间，旁边还有一个同角色的重试批次。 | `hard` |

上方的 Case 集合是当前的代码快照。缺失的校准是显式的，不得从未注册的标签推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现所拥有；本文档不会编造代码中不存在的值。

### `nightly_margin_temp_exhaustion`

- Case 编号：`0`
- 标题：模拟一个报表批次在正常生产噪声中溢出临时文件所导致的写入失败。
- Alert/symptom: Alert: PostgreSQLWriteFailuresHigh. Order writes and several scheduled jobs are intermittently failing with storage-related errors, while OLTP reads and monitoring probes still connect normally. Several BI/reporting queries and routine collectors are active on the primary. Identify the production source of the write failures, restore write availability, and prevent the same batch from immediately exhausting scratch space again.
- 初始状态字段：`noise`, `status`, `symptom`
- 预期目标字段：`culprit_application`, `culprit_job`, `culprit_role`, `required_temp_file_limit`, `status`
- 背景画像：未声明
- 评测器：`src.scenarios.evaluation.postgres.system_failure.temp_file_explosion.PgSystemFailureTempFileExplosionForNightlyMarginTempExhaustionEvaluatorCase`
- 难度标签与各 Case 的校准值维护在代码注册表和场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复制这些实测值。

### `daily_sales_temp_exhaustion_simple`

- Case 编号：`1`
- 标题：一个每日销售汇总批处理填满 PostgreSQL 暂存空间，旁边还有一个同角色的重试批次。
- Alert/symptom: Alert: Scheduled writes fail with a storage-related error while PostgreSQL remains reachable and a low-rate date probe succeeds. A cancelled retry batch uses the same report role and application identity. Identify the active scratch-space consumer by job, restore writes, and prevent that batch from exhausting temp storage again.
> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。
- 初始状态字段：`status`, `symptom`
- 预期目标字段：`culprit_application`, `culprit_job`, `culprit_role`, `required_temp_file_limit`, `status`
- 背景画像：date_health_probe
- 评测器：`src.scenarios.evaluation.postgres.system_failure.temp_file_explosion.PgSystemFailureTempFileExplosionForDailySalesTempExhaustionSimpleEvaluatorCase`
- 校准台账：由 Case 注册表与[难度标准](../../../../standards/scenario/difficulty.standard.md)维护。

## 4. Agent 可见证据

- Agent 接收注册的题面（alert），并通过当前的工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`（以运行时实际暴露的为准）。
- 目标汇总批次与一个已取消的重试批次共享相同的角色与应用身份；它们稳定的作业标记让 Agent 能够区分当前活跃的暂存空间消耗者。
- 题面（alert）只是定向提示，不是根因答案。确切的证据、诱饵、可见性限制以及任何知识或历史观测工具，都必须在场景与评测器源代码中核实。
- 不要把参考报告、注入器证据、评测器私有的观测或隐藏的条件 ID 当作 Agent 可见证据。

## 5. DP / OP / SP 契约

- **DP** 是评测器私有的、针对注册 Case 的语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。
- **OP** 是评测器的最终状态与业务真值契约。上方的预期目标字段标识状态边界；被接受的修复与等价结果由评测器定义。
- 两个 Case 均接受既有预先声明的、安全的、角色范围的持久 temp limit 区间，而不是单一参考值。区间边界仍是评测器内部信息；mock 使用一个被接受的值，区间内的每个值都会被接受。
- OP 以故障报表账号真实登录业务数据库，建立独立新连接，从 `pg_settings` 读取实际生效的 `temp_file_limit` 及来源。角色默认与角色/数据库覆盖只要实际生效值在区间内均可通过。配在其他数据库或角色、角色默认被业务数据库的宽松或无限制设置覆盖、未提交的修改、仅在 Agent 当前会话修改均不能通过；存在多条正确配置记录不会导致失败。
- 限制必须来自报表角色的持久设置（来源为 `user` 或 `database user`）；仅给整个数据库或实例设置限制不能替代限定角色的修复。禁止报表账号登录不能通过。原有故障会话清理和 SQL 可用性检查继续保留。
- **SP** 独立检查危险动作、影响范围、受保护对象与未授权的状态漂移。它不是 OP 的替代品。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从历史遗留文档复制旧的评分公式。

## 6. 处置、归属与恢复

- 使用当前评测器与场景契约接受的修复族。除非代码明确将其纳入公开契约，否则动作顺序、SQL 拼写、索引名称与报告措辞都不是要求。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前五阶段协议释放 Case 拥有的连接、会话、线程、进程、文件、配置与数据库状态。

## 7. 代码地图与验证

- 场景与 Case 源码：`src.scenarios.postgres.system_failure.temp_file_explosion.PgSystemFailureTempFileExplosionScenario`
- 评测器源码：`src/scenarios/evaluation/postgres/system_failure/` 下的一个或多个模块；确切类已在上方各 Case 中列出。
- 入口：`examples/run_pg_system_failure_temp_file_explosion_scenario.py`
- 聚焦测试、参考运行与 trace 是证据，而非第二份契约。
- 在修改本文档之前，请将其与当前注册表、Case 实现、评测器、聚焦测试与实弹验证证据进行比对。
- 范围回归：`tests/postgres/test_temp_file_limit_scope.py`；设置 `DBA_BENCH_LIVE_TEMP_LIMIT=1` 可执行隔离 PostgreSQL 验证，覆盖配置优先级、未提交/仅会话修复、登录可用性和真实临时文件溢出取消，不属于吞吐基准测试。
