---
doc_id: scenario.tidb.tidb_query_perf_statistics_drift
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, query_perf, tidb_query_perf_statistics_drift]
summary: Current code-backed contract snapshot for tidb_query_perf_statistics_drift; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `tidb_query_perf_statistics_drift`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `query_perf`
- Scenario implementation: `src.scenarios.tidb.query_perf.statistics_drift.TidbQueryPerfStatisticsDriftScenario`
- Formal entrypoint: `examples/run_tidb_query_perf_statistics_drift_scenario.py`
- Current description: Deterministic data skew leaves stale TiDB statistics and causes query-plan drift.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `distribution_shift_stale_statistics` | A distributed order aggregate spans two physical shards whose post-collection distribution shifts leave both sides with stale statistics while control shards remain healthy. | `hard` |
| 1 | `distribution_shift_stale_statistics_simple` | A distributed order aggregate spans two physical shards whose post-collection distribution shifts leave both sides with stale statistics while control shards remain healthy. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `distribution_shift_stale_statistics`

- Case number: `0`
- Title: A distributed order aggregate spans two physical shards whose post-collection distribution shifts leave both sides with stale statistics while control shards remain healthy.
- Alert/symptom: [CRITICAL] [Grafana/TiDB-Query-Detail] 某订单聚合 SQL 指纹的 P95 从 25ms 升到 2.8s，同一指纹的处理行数明显增加，但其它相似聚合和集群可用性没有同步异常。请从 SQL 指纹、执行计划、估算/实际行数、统计新鲜度和数据分布中定位真正影响该请求的原因，排除无关 workload、索引定义和集群级故障，并在不改变业务结果的前提下恢复性能。
- Initial-state fields: `control_workload`, `status`, `symptom`
- Expected-target fields: `business_result_consistent`, `estimate_actual_ratio_at_most`, `estimated_rows`, `status`
- Background profiles: qp04_target_order_report, qp04_control_order_report, qp04_statistics_inventory, qp04_control_point_read, qp04_noise_archive_report
- Evaluator: `src.scenarios.evaluation.tidb.query_perf.statistics_drift.TidbQueryPerfStatisticsDriftForDistributionShiftEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): not declared in code

### `distribution_shift_stale_statistics_simple`

- Case number: `1`
- Title: A distributed order aggregate spans two physical shards whose post-collection distribution shifts leave both sides with stale statistics while control shards remain healthy.
- Alert/symptom: [CRITICAL] [Grafana/TiDB-Query-Detail] 某订单聚合 SQL 指纹的 P95 从 25ms 升到 2.8s，同一指纹的处理行数明显增加，但其它相似聚合和集群可用性没有同步异常。请从 SQL 指纹、执行计划、估算/实际行数、统计新鲜度和数据分布中定位真正影响该请求的原因，排除无关 workload、索引定义和集群级故障，并在不改变业务结果的前提下恢复性能。
- Initial-state fields: `control_workload`, `status`, `symptom`
- Expected-target fields: `business_result_consistent`, `estimate_actual_ratio_at_most`, `estimated_rows`, `status`
- Background profiles: qp04_target_order_report, qp04_control_order_report, qp04_statistics_inventory, qp04_control_point_read, qp04_noise_archive_report
- Evaluator: `src.scenarios.evaluation.tidb.query_perf.statistics_drift.TidbQueryPerfStatisticsDriftReducedEvaluatorCase`
- Calibration evidence (tool m/n): execute_sql.fault_plan=10/23; execute_sql.stats_meta=2/4; execute_sql.index_catalog=4/2; execute_sql.session_variable=1/0; query_metrics.query_latency=74/46

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** is the evaluator-owned semantic diagnosis contract for the registered Case. It is independent of repair completion and uses the shared DP protocol.
- **OP** is the evaluator's final-state and business-truth contract. The expected-target fields above identify the state boundary; accepted repairs and equivalent outcomes are defined by the evaluator.
- **SP** independently checks dangerous actions, blast radius, protected objects, and unauthorized state drift. It is not a replacement for OP.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.tidb.query_perf.statistics_drift.TidbQueryPerfStatisticsDriftScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/query_perf/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_query_perf_statistics_drift_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
