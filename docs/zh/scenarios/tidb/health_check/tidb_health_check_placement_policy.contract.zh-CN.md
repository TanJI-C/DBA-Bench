---
doc_id: scenario.tidb.tidb_health_check_placement_policy
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, health_check, tidb_health_check_placement_policy]
summary: Current code-backed contract snapshot for tidb_health_check_placement_policy; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `tidb_health_check_placement_policy`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `health_check`
- Scenario implementation: `src.scenarios.tidb.health_check.placement_policy.TidbHealthCheckPlacementPolicyScenario`
- Formal entrypoint: `examples/run_tidb_health_check_placement_policy_scenario.py`
- Current description: Routine TiDB placement-compliance health check that requires correlating object policy inheritance, asynchronous placement state, fixed-version knowledge, and unchanged business truth under real query noise.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `single_store_voters_pending` | Routine fleet-control review across checkout, customer, fulfillment, archive, and monitoring traffic. | `hard` |
| 1 | `table_policy_inheritance_review` | A TiDB placement review for a table-level policy that blocks inherited placement convergence. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `single_store_voters_pending`

- Case number: `0`
- Title: Routine fleet-control review across checkout, customer, fulfillment, archive, and monitoring traffic.
- Alert/symptom: [Routine TiDB Fleet Review] One live control-plane review remains open after this lane moved to its compact operating profile. User-facing latency, writes, and component health remain below paging thresholds. Identify the exact live review scope from current metadata, distinguish it from approved and historical nearby records, apply the smallest service-owned correction consistent with the fixed-version guidance, and close only that review. Do not change business rows, centrally owned definitions, or healthy components.
- Initial-state fields: `business_traffic`, `queue`, `status`
- Expected-target fields: `business_crc`, `placement_status`, `status`, `target_partition_policy`, `target_table_policy`
- Background profiles: hc08_checkout_order_lookup, hc08_merchant_status_rollup, hc08_fulfillment_event_join, hc08_customer_segment_dashboard, hc08_archive_reconciliation, hc08_risk_audit_top_orders, hc08_review_queue_probe, hc08_service_catalog_refresh, hc08_event_window_reconcile
- Evaluator: `src.scenarios.evaluation.tidb.health_check.placement_policy.TidbHealthCheckPlacementPolicyEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): execute_sql:review_queue=1/3; execute_sql:service_catalog=1/3; execute_sql:table_policy_catalog=1/5; execute_sql:partition_policy_catalog=1/1; execute_sql:policy_catalog=1/3; execute_sql:show_placement=3/5; manage_cluster:service_list=1/4; manage_cluster:store_list=1/0; manage_cluster:region_list=1/69; manage_cluster:operator_list=0/0; manage_cluster:scheduler_list=0/4; search_knowledge:placement_sql=5/0; execute_sql:business_truth=2/0

### `table_policy_inheritance_review`

- Case number: `1`
- Title: A TiDB placement review for a table-level policy that blocks inherited placement convergence.
- Alert/symptom: 例行 placement review：服务目录把当前 open review 映射到一个 table-level custom policy，compact lane 无法收敛。请关联 service-to-table 目录、policy catalog、SHOW PLACEMENT 和健康近邻，确认只存在 table-level override。只把目标 table 恢复为 DEFAULT，保留分区继承、其它对象和业务数据，不重启组件或修改中心 policy 定义。
- Initial-state fields: `business_traffic`, `queue`, `status`
- Expected-target fields: `business_crc`, `partition_policy`, `placement_status`, `status`, `target_table_policy`
- Background profiles: hc08_checkout_order_lookup, hc08_merchant_status_rollup, hc08_fulfillment_event_join, hc08_customer_segment_dashboard, hc08_archive_reconciliation, hc08_risk_audit_top_orders, hc08_review_queue_probe, hc08_service_catalog_refresh, hc08_event_window_reconcile
- Evaluator: `src.scenarios.evaluation.tidb.health_check.placement_policy.TidbHealthCheckPlacementPolicyForTableInheritanceEvaluatorCase`
- Calibration evidence (tool m/n): execute_sql(review_and_service_catalog)=1/1; execute_sql(policy_and_placement_catalog)=1/1; execute_sql(business_truth)=1/0

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- The HC08 retrofit uses the shared hierarchical `search_knowledge` entrypoint and does not select an HC08-specific source, persist directory, or collection. The knowledge response is source-neutral and contains only the contract-approved result fields.
- Case 0 also exposes read-only placement labels and control-plane observations through the existing `manage_cluster` observation operations; these are raw diagnostic evidence, not evaluator-owned target classification.
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

- Scenario and Case source: `src.scenarios.tidb.health_check.placement_policy.TidbHealthCheckPlacementPolicyScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/health_check/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_health_check_placement_policy_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
