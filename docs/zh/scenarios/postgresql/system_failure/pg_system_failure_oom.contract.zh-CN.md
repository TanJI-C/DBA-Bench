---
doc_id: scenario.postgresql.pg_system_failure_oom
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, system_failure, pg_system_failure_oom]
summary: pg_system_failure_oom 的当前基于代码的契约快照；包含其已注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
updated: 2026-10-25
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_system_failure_oom`

> 本文档是当前基于注册表的场景（Scenario）契约。请先阅读数据库目录进行导航，然后在修改实现之前，于链接的源代码中核实机制、证据、结果、安全性与恢复。

## 1. 标识与范围

- 数据库：`postgresql`
- 类别：`system_failure`
- 场景实现：`src.scenarios.postgres.system_failure.oom.PgSystemFailureOomScenario`
- 正式入口：`examples/run_pg_system_failure_oom_scenario.py`
- 当前描述：PostgreSQL 进程因内存配置超过容器上限而被 OOM kill。

## 2. 当前 Case 集合

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `restart_memory_config_oom` | PostgreSQL 进程因内存配置超过容器上限而被 OOM kill。 | `hard` |
| 1 | `restart_shared_buffers_oom_simple` | 一个不安全的 shared_buffers 覆盖导致 PostgreSQL 重启后无法提供服务。 | `easy` |

上方的 Case 集合是当前的代码快照。缺失的校准是显式的，不得从未注册的标签推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现所拥有；本文档不会编造代码中不存在的值。

### `restart_memory_config_oom`

- Case 编号：`0`
- 标题：PostgreSQL 进程因内存配置超过容器上限而被 OOM kill。
- Alert/symptom: P0 Alert: checkout and BI APIs are returning elevated 5xx errors. Application pools report repeated PostgreSQL connection refused events after the last maintenance restart. The container is still running, but database readiness keeps failing. Nearby telemetry also contains routine report temp-file and checkpoint messages; identify the primary reason PostgreSQL is not serving traffic and repair it.
- 初始状态字段：`container`, `postgres_process`, `status`
- 预期目标字段：`config_fixed`, `status`
- 背景画像：未声明
- 评测器：`src.scenarios.evaluation.postgres.system_failure.oom.PgSystemFailureOomForRestartMemoryConfigOomEvaluatorCase`
- 难度标签与各 Case 的校准值维护在代码注册表和场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复制这些实测值。

### `restart_shared_buffers_oom_simple`

- Case 编号：`1`
- 标题：一个不安全的 shared_buffers 覆盖导致 PostgreSQL 重启后无法提供服务。
- Alert/symptom: P0 Alert: PostgreSQL readiness fails after a maintenance restart while the container remains running. A low-rate calendar health probe was active before the restart. Identify why PostgreSQL is not serving traffic, restore service, and verify the probe query.
> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。
- 初始状态字段：`container`, `postgres_process`, `status`
- 预期目标字段：`shared_buffers`, `status`, `work_mem`
- 背景画像：calendar_health_probe
- 评测器：`src.scenarios.evaluation.postgres.system_failure.oom.PgSystemFailureOomForRestartSharedBuffersOomSimpleEvaluatorCase`
- 校准证据（工具 m/n）：代码中未声明

## 4. Agent 可见证据

- Agent 接收注册的题面（alert），并通过当前的工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`（以运行时实际暴露的为准）。
- 题面（alert）只是定向提示，不是根因答案。确切的证据、诱饵、可见性限制以及任何知识或历史观测工具，都必须在场景与评测器源代码中核实。
- 不要把参考报告、注入器证据、评测器私有的观测或隐藏的条件 ID 当作 Agent 可见证据。

## 5. DP / OP / SP 契约

- **DP** 是评测器私有的、针对注册 Case 的语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。
- **OP** 是评测器的最终状态与业务真值契约。上方的预期目标字段标识状态边界；被接受的修复与等价结果由评测器定义。
- **SP** 独立检查危险动作、影响范围、受保护对象与未授权的状态漂移。它不是 OP 的替代品。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从历史遗留文档复制旧的评分公式。

## 6. 处置、归属与恢复

- 两个 Case 的 OP 都使用 Case 环境的业务数据库与登录凭据建立新连接，在同一个连接内
  检查内存配置并执行原 Case 业务探针。Agent 会话中的临时 `SET` 不能证明新业务登录已恢复。
- 运行中的 `shared_buffers` 和下次启动实际采用的配置均须不超过
  `case.safe_shared_buffers`（128MB）。安全的待生效下调不要求额外重启。命令行覆盖遵守
  PostgreSQL 的优先级；否则按配置文件最后一个设置验收，文件覆盖被移除时使用内置默认值。
- 新业务登录的有效 `work_mem` 须不超过 `case.safe_work_mem`（8MB）。数据库默认值、
  角色在当前数据库的默认值及原有实例级修复均按 PostgreSQL 的优先级生效。
  OP 不检查无关登录，不要求指定配置来源或精确恢复到某个值。
- `memory_recovery` 检查记录登录身份、运行及下次启动的 `shared_buffers` 字节数、
  有效 `work_mem` 字节数和原探针结果。已知内存配置不安全时，在执行探针前判定 OP 失败；
  登录失败或业务查询失败也判定 OP 失败。
- 使用当前评测器与场景契约接受的修复族。除非代码明确将其纳入公开契约，否则动作顺序、SQL 拼写、索引名称与报告措辞都不是要求。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前五阶段协议释放 Case 拥有的连接、会话、线程、进程、文件、配置与数据库状态。

## 7. 代码地图与验证

- 场景与 Case 源码：`src.scenarios.postgres.system_failure.oom.PgSystemFailureOomScenario`
- 评测器源码：`src/scenarios/evaluation/postgres/system_failure/` 下的一个或多个模块；确切类已在上方各 Case 中列出。
- 入口：`examples/run_pg_system_failure_oom_scenario.py`
- 聚焦测试、参考运行与 trace 是证据，而非第二份契约。
- 新登录内存验收回归：`tests/postgres/test_oom_memory_recovery.py`。
  本次评测器修正保留故障、题面、DP 条件、参考修复路径和可见证据，沿用代码注册表中的
  既有难度校准与标签。
- 在修改本文档之前，请将其与当前注册表、Case 实现、评测器、聚焦测试与实弹验证证据进行比对。
