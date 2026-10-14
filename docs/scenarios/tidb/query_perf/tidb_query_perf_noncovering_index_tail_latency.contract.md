---
doc_id: scenario.tidb.tidb_query_perf_noncovering_index_tail_latency
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, query_perf, tidb_query_perf_noncovering_index_tail_latency]
summary: Current code-backed contract snapshot for tidb_query_perf_noncovering_index_tail_latency; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `tidb_query_perf_noncovering_index_tail_latency`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `query_perf`
- Scenario implementation: `src.scenarios.tidb.query_perf.noncovering_index_tail_latency.TidbQueryPerfNoncoveringIndexTailLatencyScenario`
- Formal entrypoint: `examples/run_tidb_query_perf_noncovering_index_tail_latency_scenario.py`
- Current description: A production-shaped TiDB checkout order-history API regresses inside a mixed, multi-tenant workload and must be restored without changing business truth.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `noncovering_index_tail_latency` | Checkout order-history page p95 regresses in a multi-tenant traffic mix. | `hard` |
| 1 | `noncovering_index_tail_latency_reduced` | Checkout order-history page p95 regresses in a multi-tenant traffic mix. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `noncovering_index_tail_latency`

- Case number: `0`
- Title: Checkout order-history page p95 regresses in a multi-tenant traffic mix.
- Alert/symptom: [CRITICAL] the checkout order-history page is above its 100 ms database p95 budget while returned order rows remain correct. Restore target p95 to <=100 ms, keep same-domain neighbor reads <=360 ms p95 and the order-event writer <=350 ms p95, leave the canonical plan at <=10,000 process keys with IndexReader and no IndexLookUp/TableRowIDScan, leave schema DDL fully public/synced with visible stats, preserve healthy neighbor indexes, and do not change order-event records, route registry, or page context.
- Initial-state fields: `page_route`, `status`, `table_rows`, `workload`
- Expected-target fields: `neighbor_p95_slo_ms`, `p95_slo_ms`, `status`, `table_rows`, `write_p95_slo_ms`
- Background profiles: qp05_fp_07, qp05_fp_02, qp05_fp_03, qp05_fp_04, qp05_fp_05, qp05_fp_06, qp05_fp_01, qp05_fp_08, qp05_fp_09, qp05_fp_10, qp05_fp_11, qp05_fp_12
- Evaluator: `src.scenarios.evaluation.tidb.query_perf.noncovering_index_tail_latency.TidbQueryPerfNoncoveringIndexTailLatencyEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): query_metrics:qps/active_connections=4/42; execute_sql:CLUSTER_STATEMENTS_SUMMARY=3/37; execute_sql:CLUSTER_SLOW_QUERY=11/39; query_metrics:query_latency[fault_window]=15/8; manage_cluster:service/list=5/2; read_log:tidb/tidb-0=0/200; execute_sql:EXPLAIN_ANALYZE=4/6; execute_sql:SHOW_INDEX=67/27; execute_sql:ROUTE_REGISTRY=2/34; execute_sql:PAGE_CONTEXT=1/11; execute_sql:SHOW_STATS_META=1/0; execute_sql:TABLE_SIZE=1/0; execute_sql:ADMIN_SHOW_DDL_JOBS=1/19

### `noncovering_index_tail_latency_reduced`

- Case number: `1`
- Title: Checkout order-history page p95 regresses in a multi-tenant traffic mix.
- Alert/symptom: [CRITICAL] the checkout order-history page is above its 100 ms database p95 budget while returned order rows remain correct. Restore target p95 to <=100 ms, keep same-domain neighbor reads <=360 ms p95 and the order-event writer <=350 ms p95, leave the canonical plan at <=10,000 process keys with IndexReader and no IndexLookUp/TableRowIDScan, leave schema DDL fully public/synced with visible stats, preserve healthy neighbor indexes, and do not change order-event records, route registry, or page context.
- Initial-state fields: `page_route`, `status`, `table_rows`, `workload`
- Expected-target fields: `neighbor_p95_slo_ms`, `p95_slo_ms`, `status`, `table_rows`, `write_p95_slo_ms`
- Background profiles: qp05_fp_07, qp05_fp_02, qp05_fp_03, qp05_fp_04, qp05_fp_05, qp05_fp_06, qp05_fp_01, qp05_fp_08, qp05_fp_09, qp05_fp_10, qp05_fp_11, qp05_fp_12
- Evaluator: `src.scenarios.evaluation.tidb.query_perf.noncovering_index_tail_latency.TidbQueryPerfNoncoveringIndexTailLatencyReducedEvaluatorCase`
- Calibration evidence (tool m/n): query_metrics:qps/active_connections=4/30; execute_sql:CLUSTER_STATEMENTS_SUMMARY=3/25; execute_sql:CLUSTER_SLOW_QUERY=10/28; query_metrics:query_latency[fault_window]=13/6; execute_sql:EXPLAIN_ANALYZE=4/5; execute_sql:SHOW_INDEX=60/20; execute_sql:ROUTE_REGISTRY=2/20; execute_sql:PAGE_CONTEXT=1/8; execute_sql:SHOW_STATS_META=1/0; execute_sql:TABLE_SIZE=1/0

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** is the evaluator-owned semantic diagnosis contract for the registered Case. It is independent of repair completion and uses the shared DP protocol.
- **OP** is the evaluator's final-state and business-truth contract. The expected-target fields above identify the state boundary; accepted repairs and equivalent outcomes are defined by the evaluator.
- **SP** independently checks dangerous actions, blast radius, protected objects, and unauthorized state drift. It is not a replacement for OP.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.tidb.query_perf.noncovering_index_tail_latency.TidbQueryPerfNoncoveringIndexTailLatencyScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/query_perf/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_query_perf_noncovering_index_tail_latency_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
