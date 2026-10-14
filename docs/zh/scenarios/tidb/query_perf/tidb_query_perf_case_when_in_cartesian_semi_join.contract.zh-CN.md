---
doc_id: scenario.tidb.tidb_query_perf_case_when_in_cartesian_semi_join
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, query_perf, tidb_query_perf_case_when_in_cartesian_semi_join]
summary: Current code-backed contract snapshot for tidb_query_perf_case_when_in_cartesian_semi_join; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `tidb_query_perf_case_when_in_cartesian_semi_join`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `query_perf`
- Scenario implementation: `src.scenarios.tidb.query_perf.case_when_in_cartesian_semi_join.TidbQueryPerfCaseWhenInCartesianSemiJoinScenario`
- Formal entrypoint: `examples/run_tidb_query_perf_case_when_in_cartesian_semi_join_scenario.py`
- Current description: Four nullable CASE IN subqueries expand into Cartesian semi joins over non-unique memberships in TiDB.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `case_when_in_cartesian_semi_join` | Four nullable scalar IN expressions expand into Cartesian semi joins over non-unique memberships. | `hard` |
| 1 | `case_when_in_cartesian_semi_join_simple` | Four nullable scalar IN expressions expand into Cartesian semi joins over non-unique memberships. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `case_when_in_cartesian_semi_join`

- Case number: `0`
- Title: Four nullable scalar IN expressions expand into Cartesian semi joins over non-unique memberships.
- Alert/symptom: [CRITICAL] [TiDB/Order-Risk-Report] 风险规则报表的 P95 从 20ms 上升到数秒，同一报表指纹的处理量和 TiDB root CPU 同步增加；集群成员、存储副本和其它点查没有明显异常。请定位这个报表查询的执行退化原因，在保持命中结果、scope_c/scope_d 差异化 NULL 语义不变的前提下恢复性能。
- Initial-state fields: `endpoint`, `report`, `status`
- Expected-target fields: `cartesian_join_removed`, `null_semantics_preserved`, `result_consistent`, `status`
- Background profiles: qp06_order_risk_report, qp06_rule_point_lookup, qp06_gate_point_lookup, qp06_region_point_lookup, qp06_case_point_probe, qp06_schema_inventory, qp06_equivalent_join_decoy
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../../standards/scenario/difficulty.standard.md).
- Evaluator: `src.scenarios.evaluation.tidb.query_perf.case_when_in_cartesian_semi_join.TidbQueryPerfCaseWhenInCartesianSemiJoinEvaluatorCase`
- Calibration evidence (tool m/n): not declared in code

### `case_when_in_cartesian_semi_join_simple`

- Case number: `1`
- Title: Four nullable scalar IN expressions expand into Cartesian semi joins over non-unique memberships.
- Alert/symptom: [CRITICAL] [TiDB/Order-Risk-Report] 风险规则报表的 P95 从 20ms 上升到数秒，同一报表指纹的处理量和 TiDB root CPU 同步增加；集群成员、存储副本和其它点查没有明显异常。请从报表指纹、view 定义和执行计划中定位这个报表查询的执行退化原因，在保持命中结果、scope_c/scope_d 差异化 NULL 语义和风险规则数据不变的前提下恢复性能，并把修复范围限定在报表端点本身。
- Initial-state fields: `endpoint`, `report`, `status`
- Expected-target fields: `cartesian_join_removed`, `null_semantics_preserved`, `result_consistent`, `status`
- Background profiles: qp06_order_risk_report, qp06_rule_point_lookup, qp06_gate_point_lookup, qp06_region_point_lookup
- Evaluator: `src.scenarios.evaluation.tidb.query_perf.case_when_in_cartesian_semi_join.TidbQueryPerfCaseWhenInCartesianSemiJoinSimplifiedEvaluatorCase`
- Calibration ledger: maintained by the Case registry and the [difficulty standard](../../../../standards/scenario/difficulty.standard.md); counting basis is all reference-path key tools with unfiltered results.

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** is the evaluator-owned semantic diagnosis contract for the registered Case. It is independent of repair completion and uses the shared DP protocol.
- **OP** is the evaluator's final-state and business-truth contract. The expected-target fields above identify the state boundary; accepted repairs and equivalent outcomes are defined by the evaluator. The rewritten view must express an equality join rewrite (including the `IN (SELECT ...)` semi-join form); the dynamic `LIKE CONCAT(...)` scope that made the join degenerate stays banned, while the historical ban on the scalar `IN` form itself is dropped because the equality rewrite is what the business semantics require.
- **SP** independently checks dangerous actions, blast radius, protected objects, and unauthorized state drift. It is not a replacement for OP.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.tidb.query_perf.case_when_in_cartesian_semi_join.TidbQueryPerfCaseWhenInCartesianSemiJoinScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/query_perf/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_query_perf_case_when_in_cartesian_semi_join_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
