---
doc_id: scenario.postgresql.pg_resource_governance_pgbouncer_connection_budget
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, resource_governance, pg_resource_governance_pgbouncer_connection_budget]
summary: pg_resource_governance_pgbouncer_connection_budget 的当前基于代码的契约快照；包含其注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_resource_governance_pgbouncer_connection_budget`

> 这是当前基于注册中心的场景（Scenario）契约。请先阅读数据库目录进行导航，然后在修改实现之前，于关联源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`resource_governance`
- 场景实现：`src.scenarios.postgres.resource_governance.pgbouncer_connection_budget.PgResourceGovernancePgbouncerConnectionBudgetScenario`
- 正式入口：`examples/run_pg_resource_governance_pgbouncer_connection_budget_scenario.py`
- 当前描述：在结账、报表与 ETL 工作负载之间治理 PgBouncer 事务池连接预算。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `pool_partition_shortage` | 三工作负载回放下的 PgBouncer 连接预算治理。 | `hard` |
| 1 | `pool_partition_shortage_simple` | 聚焦的 PgBouncer 连接预算治理。 | `easy` |

上方的 Case 集合是当前的代码快照。缺失校准是显式状态，不得从非注册标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现持有；本文档不杜撰代码中不存在的值。

### `pool_partition_shortage`

- Case 编号：`0`
- 标题：三工作负载回放下的 PgBouncer 连接预算治理。
- Alert/symptom: P1 business-capacity alert: checkout, reporting and ETL service degraded during a peak window. PostgreSQL max_connections=40. Reporting must complete at least one unit, ETL must update at least 10 rows, and a scheduled maintenance check must remain available. Restore all services with transaction pooling, keep the existing database and role-level connection ceilings within bounded partitions, and verify queue convergence.
- 初始状态字段：`postgres_headroom`, `status`
- 期望目标字段：`pool_mode`, `postgres_max_connections`, `checkout_role_connection_partition`, `pool_budget`, `queue`, `status`, `workloads`
- 背景工作负载配置：report_tpcds、report_probe、health_probe、report_long_noise、checkout_auxiliary_read、reporting_batch_auxiliary
- 评测器：`src.scenarios.evaluation.postgres.resource_governance.pgbouncer_connection_budget.PgResourceGovernancePgbouncerConnectionBudgetEvaluatorCase`
- 难度：hard；各 Case 的校准值维护在代码注册中心与场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。
- 校准证据（工具 m/n）：SQL/catalog m=3 n=4；metric m=2 n=3；workload/operation event m=1 n=1
- 公开历史：hard Case 使用共享的冻结历史契约：先从 CaseRun 捕获实时的正常与目标窗口，然后在 Agent 交接之前冻结为 12 小时窗口。它以 2 秒粒度、20 秒概览暴露原始 `pgbouncer_pool_clients`、`pgbouncer_pool_servers`、`pgbouncer_pool_rates`、`database_capacity`、`service_slo` 与 `connection_churn`；有界历史记录包括 `component_log`、`topsql` 与 `operation_event`，其中包含被捕获为良性的干扰窗口。simple Case 没有冻结历史。
- 正常窗口捕获除目标捕获突发（2 个客户端）外，还会运行有界的报表池突发（4 个并发客户端，每 120 秒周期内 45 秒），并在 `pgbouncer_pool_clients@testdb/report_user` 上加入 `short-reporting-queue-burst` 这一被捕获为良性的干扰项（2 个窗口 x 30 秒，MAD 0.5）；报表队列现在是一个可被排除的竞争假设，而不是单向佐证。
- 公开的 `config_revision` 操作事件不携带结账角色名或其旧/新连接上限；角色级分区必须从池服务端行为特征加 `pg_roles` 中探明，其中包含被刻意限定上限的邻居角色，因此较低的 `rolconnlimit` 需要按角色进行需求/活动判别。
- `checkout_role_connection_partition_is_bounded` 结果检查除 PostgreSQL 上限之外，还要求 `rolconnlimit(checkout_user) >= recovered_checkout_role_connection_limit`（6），因此部分恢复（2..5）会失败；混合工作负载验收回放还要求回放窗口内成功结账调用达到最低数量。

### `pool_partition_shortage_simple`

- Case 编号：`1`
- 标题：聚焦的 PgBouncer 连接预算治理。
- Alert/symptom: P2 business-capacity alert: checkout and reporting service degraded during a peak window. PostgreSQL max_connections=40 with spare capacity; reporting must complete at least one unit of work. Restore both services with transaction pooling without raising the PostgreSQL ceiling (40), the PgBouncer database-side server budget (16), or the shared pool budget cap (default_pool_size + reserve_pool_size <= 24); verify queue convergence after the change.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`postgres_headroom`, `status`
- 期望目标字段：`pool_mode`, `postgres_max_connections`, `checkout_role_connection_partition`, `pool_budget`, `queue`, `status`, `workloads`
- 背景工作负载配置：report_tpcds、report_probe
- 评测器：`src.scenarios.evaluation.postgres.resource_governance.pgbouncer_connection_budget.PgResourceGovernancePgbouncerConnectionBudgetSimpleEvaluatorCase`
- 校准证据（工具 m/n）：SQL/catalog m=5 n=5；metric m=1 n=0；workload/operation event m=1 n=0
- 机制：事故挤压结账角色分区（`checkout_user` 的 rolconnlimit 从 20 降到 2），而池侧所有预算均健康（`max_db_connections=16`、`default_pool_size=2`、`reserve_pool_size=0`）。`pg_roles` 中还有两个被刻意限定上限的邻居角色（`archive_batch_user` 上限 2、`report_legacy_user` 上限 3），其上限是有意设置的，且二者都没有池路由或会话，因此较低的 `rolconnlimit` 需要按角色进行需求/活动判别。修复必须恢复结账角色分区（rolconnlimit 6..40）并重新平衡池容量，使验收回放恢复结账吞吐。无操作、单层部分修复或方向错误的邻居角色修复，都会在角色检查、回放吞吐下限或安全范围上失败。
- 题面不披露角色连接分区这一修复层级。

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

- Scenario 与 Case 源代码：`src.scenarios.postgres.resource_governance.pgbouncer_connection_budget.PgResourceGovernancePgbouncerConnectionBudgetScenario`
- 评测器源代码：`src/scenarios/evaluation/postgres/resource_governance/` 下的一个或多个模块；确切的类已在上方按 Case 列出。
- 入口：`examples/run_pg_resource_governance_pgbouncer_connection_budget_scenario.py`
- 聚焦测试、参考运行与调用轨迹只是证据，并非第二份契约。
- 在修改本文档之前，请将其与当前注册中心、Case 实现、评测器、聚焦测试以及实时验证证据进行比对。
