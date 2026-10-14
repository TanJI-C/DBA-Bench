---
doc_id: scenario.tidb.tidb_query_perf_noncovering_index_tail_latency
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, query_perf, tidb_query_perf_noncovering_index_tail_latency]
summary: tidb_query_perf_noncovering_index_tail_latency 的当前代码化契约快照；包含其已注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `tidb_query_perf_noncovering_index_tail_latency`

> 这是当前基于注册表的场景契约。请先阅读数据库目录进行导航，然后在修改实现之前，在链接的源代码中核实机制、证据、结果、安全与恢复。

## 1. 身份与范围

- 数据库：`tidb`
- 类别：`query_perf`
- 场景实现：`src.scenarios.tidb.query_perf.noncovering_index_tail_latency.TidbQueryPerfNoncoveringIndexTailLatencyScenario`
- 正式入口：`examples/run_tidb_query_perf_noncovering_index_tail_latency_scenario.py`
- 当前描述：一个生产形态的 TiDB 结算订单历史 API 在混合的多租户工作负载中发生退化，必须在不改变业务真相的前提下恢复。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `noncovering_index_tail_latency` | 结算订单历史页面的 p95 在多租户流量混合中发生退化。 | `hard` |
| 1 | `noncovering_index_tail_latency_reduced` | 结算订单历史页面的 p95 在多租户流量混合中发生退化。 | `hard` |

上述 Case 集合是当前代码快照。缺失的校准是显式事实，不得从未注册的标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。真实故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现持有；本文档不虚构代码中不存在的值。

### `noncovering_index_tail_latency`

- Case 编号：`0`
- 标题：结算订单历史页面的 p95 在多租户流量混合中发生退化。
- Alert/symptom: [CRITICAL] the checkout order-history page is above its 100 ms database p95 budget while returned order rows remain correct. Restore target p95 to <=100 ms, keep same-domain neighbor reads <=360 ms p95 and the order-event writer <=350 ms p95, leave the canonical plan at <=10,000 process keys with IndexReader and no IndexLookUp/TableRowIDScan, leave schema DDL fully public/synced with visible stats, preserve healthy neighbor indexes, and do not change order-event records, route registry, or page context.
- 初始状态字段：`page_route`, `status`, `table_rows`, `workload`
- 期望目标字段：`neighbor_p95_slo_ms`, `p95_slo_ms`, `status`, `table_rows`, `write_p95_slo_ms`
- 背景画像：qp05_fp_07, qp05_fp_02, qp05_fp_03, qp05_fp_04, qp05_fp_05, qp05_fp_06, qp05_fp_01, qp05_fp_08, qp05_fp_09, qp05_fp_10, qp05_fp_11, qp05_fp_12
- 评测器：`src.scenarios.evaluation.tidb.query_perf.noncovering_index_tail_latency.TidbQueryPerfNoncoveringIndexTailLatencyEvaluatorCase`
- 难度标签与各 Case 的校准值由代码注册表和场景目录维护；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复制这些实测值。
- 校准证据（工具 m/n）：query_metrics:qps/active_connections=4/42; execute_sql:CLUSTER_STATEMENTS_SUMMARY=3/37; execute_sql:CLUSTER_SLOW_QUERY=11/39; query_metrics:query_latency[fault_window]=15/8; manage_cluster:service/list=5/2; read_log:tidb/tidb-0=0/200; execute_sql:EXPLAIN_ANALYZE=4/6; execute_sql:SHOW_INDEX=67/27; execute_sql:ROUTE_REGISTRY=2/34; execute_sql:PAGE_CONTEXT=1/11; execute_sql:SHOW_STATS_META=1/0; execute_sql:TABLE_SIZE=1/0; execute_sql:ADMIN_SHOW_DDL_JOBS=1/19

### `noncovering_index_tail_latency_reduced`

- Case 编号：`1`
- 标题：结算订单历史页面的 p95 在多租户流量混合中发生退化。
- Alert/symptom: [CRITICAL] the checkout order-history page is above its 100 ms database p95 budget while returned order rows remain correct. Restore target p95 to <=100 ms, keep same-domain neighbor reads <=360 ms p95 and the order-event writer <=350 ms p95, leave the canonical plan at <=10,000 process keys with IndexReader and no IndexLookUp/TableRowIDScan, leave schema DDL fully public/synced with visible stats, preserve healthy neighbor indexes, and do not change order-event records, route registry, or page context.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`page_route`, `status`, `table_rows`, `workload`
- 期望目标字段：`neighbor_p95_slo_ms`, `p95_slo_ms`, `status`, `table_rows`, `write_p95_slo_ms`
- 背景画像：qp05_fp_07, qp05_fp_02, qp05_fp_03, qp05_fp_04, qp05_fp_05, qp05_fp_06, qp05_fp_01, qp05_fp_08, qp05_fp_09, qp05_fp_10, qp05_fp_11, qp05_fp_12
- 评测器：`src.scenarios.evaluation.tidb.query_perf.noncovering_index_tail_latency.TidbQueryPerfNoncoveringIndexTailLatencyReducedEvaluatorCase`
- 校准证据（工具 m/n）：query_metrics:qps/active_connections=4/30; execute_sql:CLUSTER_STATEMENTS_SUMMARY=3/25; execute_sql:CLUSTER_SLOW_QUERY=10/28; query_metrics:query_latency[fault_window]=13/6; execute_sql:EXPLAIN_ANALYZE=4/5; execute_sql:SHOW_INDEX=60/20; execute_sql:ROUTE_REGISTRY=2/20; execute_sql:PAGE_CONTEXT=1/8; execute_sql:SHOW_STATS_META=1/0; execute_sql:TABLE_SIZE=1/0

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

- 场景与 Case 源代码：`src.scenarios.tidb.query_perf.noncovering_index_tail_latency.TidbQueryPerfNoncoveringIndexTailLatencyScenario`
- 评测器源代码：`src/scenarios/evaluation/tidb/query_perf/` 下的一或多个模块；确切的类已在上方按 Case 列出。
- 入口：`examples/run_tidb_query_perf_noncovering_index_tail_latency_scenario.py`
- 聚焦测试、参考运行与 trace 只是证据，不是第二份契约。
- 修改本文档之前，请将其与当前注册表、Case 实现、评测器、聚焦测试以及实际验证证据进行比对。
