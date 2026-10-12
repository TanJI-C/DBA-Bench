---
doc_id: scenario.postgresql.pg_query_perf_stale_stats_lock_contention
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, pg_query_perf_stale_stats_lock_contention]
summary: pg_query_perf_stale_stats_lock_contention 的当前基于代码的契约快照；包含其注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_query_perf_stale_stats_lock_contention`

> 这是当前基于注册中心的场景（Scenario）契约。请先阅读数据库目录进行导航，然后在修改实现之前，于关联源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`query_perf`
- 场景实现：`src.scenarios.postgres.query_perf.stale_stats_lock_contention.PgQueryPerfStaleStatsLockContentionScenario`
- 正式入口：`examples/run_pg_query_perf_stale_stats_lock_contention_scenario.py`
- 当前描述：模拟过期统计信息导致活跃锁持有者变慢并引发下游锁竞争。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `checkout_stale_stats_and_lock` | 模拟过期统计信息导致活跃锁持有者变慢并引发下游锁竞争。 | `easy` |
| 1 | `checkout_stale_stats_single_waiter_simple` | 聚焦的过期统计信息锁竞争 Case：一个变慢的活跃持有者与一个等待者。 | `easy` |

上方的 Case 集合是当前的代码快照。缺失校准是显式状态，不得从非注册标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现持有；本文档不杜撰代码中不存在的值。

### `checkout_stale_stats_and_lock`

- Case 编号：`0`
- 标题：模拟过期统计信息导致活跃锁持有者变慢并引发下游锁竞争。
- Alert/symptom: Alert: order-service write requests are intermittently timing out and p95 latency is above SLO. Write throughput is below the normal baseline. Investigate and restore service health.
- 初始状态字段：`lock_holder_state`, `lock_waiters`, `statistics`, `status`
- 期望目标字段：`lock_holder_state`, `lock_waiters`, `required_fix`, `statistics`, `status`
- 背景工作负载配置：未声明
- 评测器：`src.scenarios.evaluation.postgres.query_perf.stale_stats_lock_contention.PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsAndLockEvaluatorCase`
- 难度：easy；各 Case 的校准值维护在代码注册中心与场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。

### `checkout_stale_stats_single_waiter_simple`

- Case 编号：`1`
- 标题：聚焦的过期统计信息锁竞争 Case：一个变慢的活跃持有者与一个等待者。
- Alert/symptom: Alert: checkout writes are timing out and one worker queue is waiting on a lock while a related query is slow. Identify the blocker and restore throughput.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`lock_holder_state`, `lock_waiters`, `statistics`, `status`
- 期望目标字段：`lock_holder_state`, `lock_waiters`, `required_fix`, `statistics`, `status`
- 背景工作负载配置：未声明
- 评测器：`src.scenarios.evaluation.postgres.query_perf.stale_stats_lock_contention.PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsSingleWaiterSimpleEvaluatorCase`
- 校准证据（工具 m/n）：query_metrics.active_connections/slow_queries=3/1；execute_sql.pg_stat_user_tables/locks=3/1

## 4. Agent 可见证据

- Agent 接收已注册的告警，并通过当前工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`（以运行时实际暴露的为准）。
- 告警只是定位提示，而不是根因答案。确切的证据、干扰项、可见性限制以及任何知识或历史观测工具，都必须在 Scenario 与评测器源代码中核实。
- 不得把参考报告、注入器证据、评测器私有的观测或隐藏的条件 ID 当作 Agent 可见证据。

## 5. DP / OP / SP 契约

- **DP** 是针对已注册 Case 的、由评测器持有的语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。
- **OP** 是评测器的最终状态与业务真值契约。上方的期望目标字段标识状态边界；可接受的修复与等价结果由评测器定义。当等待者 application-name 前缀下不再有会话仍在等待锁（`wait_event_type = 'Lock'`）时，注入的等待者会话即被清除，因此该检查观测的是真实的锁等待状态，而非单纯的会话存在性。
- **SP** 独立检查危险操作、影响范围（blast radius）、受保护对象以及未经授权的状态漂移。它不能替代 OP。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从历史遗留文档复制评分公式。

## 6. 修复、归属与恢复

- 使用当前评测器与 Scenario 契约接受的修复族。操作顺序、SQL 写法、索引名称与报告措辞均非硬性要求，除非代码明确将其纳入公开契约。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前五阶段协议释放 Case 持有的连接、会话、线程、进程、文件、配置与数据库状态。

## 7. 代码地图与验证

- Scenario 与 Case 源代码：`src.scenarios.postgres.query_perf.stale_stats_lock_contention.PgQueryPerfStaleStatsLockContentionScenario`
- 评测器源代码：`src/scenarios/evaluation/postgres/query_perf/` 下的一个或多个模块；确切的类已在上方按 Case 列出。
- 入口：`examples/run_pg_query_perf_stale_stats_lock_contention_scenario.py`
- 聚焦测试、参考运行与调用轨迹只是证据，并非第二份契约。
- 在修改本文档之前，请将其与当前注册中心、Case 实现、评测器、聚焦测试以及实时验证证据进行比对。
