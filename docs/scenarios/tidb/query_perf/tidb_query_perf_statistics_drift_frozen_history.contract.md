---
doc_id: scenario.tidb.tidb_query_perf_statistics_drift_frozen_history
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, query_perf, frozen_history]
summary: QP02 frozen-history history contract for reconstructing statistics drift, cardinality drift, and an affected-session plan setting.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.evaluation.dp-op-sp]
---

# QP02：统计分布漂移历史调查

## 身份与故障原理

- Scenario：`tidb_query_perf_statistics_drift_frozen_history`
- Case：`statistics_drift_history_investigation`
- 实现：`src/scenarios/tidb/query_perf/statistics_drift_frozen_history.py`
- 入口：`examples/run_tidb_query_perf_statistics_drift_frozen_history_scenario.py`

两张目标订单分片先完成统计收集，之后匹配值大量增加，统计信息却仍反映旧分布。估算行数和真实扫描行数逐步偏离，计划和延迟随后恶化；受影响诊断 session 还关闭了 IndexMerge。control/noise 分片提供同域对照。

## Agent 可见证据

指标为 `statistics_state`、`plan_cardinality`、`query_latency`、`qps`、`cpu` 和 `disk_io`。前两个指标由 Case 独立 SQL sampler 采集历史窗口：分别记录表行数/统计行数/修改数/统计年龄，以及受控 `EXPLAIN ANALYZE` 的估算行、实际行和扫描行。`estimate_actual_ratio` 是业务验收阈值，不是 Agent 指标字段；`statement_execution` 已删除，因为 TopSQL/current SQL 足以提供可追踪的执行信息。

标准路径是比较 target/control/noise 的历史先后，确认 target 的分布变化晚于上次统计收集，再把 cardinality、计划、扫描和延迟串起来，最后只刷新两张 target 统计信息并在受影响 session 打开 IndexMerge。

## 通过标准

- DP：target 与 control 的范围、统计新鲜度、估算/实际/扫描偏离、affected-session 设置和因果先后全部成立。
- OP：target 计划恢复，估算/实际比例满足 Case 阈值，业务结果与六张表完整性保持一致。
- SP：只修改 target 统计和诊断 session；禁止全局变量、业务数据/schema/index 变更、停业务和重启组件。

QP02 有效 target LLM 失败属于“未找到根因 / 诊断失败 / 证据误读”：模型把 control 当成受影响对象，刷新错误表并验证错误查询，没有建立 target 分布漂移到统计/计划/延迟的链条。它不是“找到根因但修复失败”。
