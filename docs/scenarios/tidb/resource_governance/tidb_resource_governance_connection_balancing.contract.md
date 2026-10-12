---
doc_id: scenario.tidb.tidb_resource_governance_connection_balancing
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, resource_governance, tidb_resource_governance_connection_balancing]
summary: Current code-backed contract snapshot for tidb_resource_governance_connection_balancing; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `tidb_resource_governance_connection_balancing`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `resource_governance`
- Scenario implementation: `src.scenarios.tidb.resource_governance.connection_balancing.TidbResourceGovernanceConnectionBalancingScenario`
- Formal entrypoint: `examples/run_tidb_resource_governance_connection_balancing_scenario.py`
- Current description: Multiple TiDB SQL instances require application connection rebalance and graceful session drain.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `multi_tidb_connection_balance_and_drain` | Rebalance affected TiDB connection pools and gracefully drain the affected SQL instance. | `hard` |
| 1 | `multi_tidb_alternate_target_drain` | Rebalance the affected pools and drain the alternate TiDB backend. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `multi_tidb_connection_balance_and_drain`

- Case number: `0`
- Title: Rebalance affected TiDB connection pools and gracefully drain the affected SQL instance.
- Alert/symptom: [P1] [TiDB/Connection Service] checkout and order-dashboard latency is unstable. The release window requires reviewing application connection placement without interrupting in-flight orders. Inspect time-windowed connection, CPU, QPS, query-latency, workload and cluster evidence; separate affected application traffic from stable background traffic; then complete a reversible load-balancer transition and verify business results, endpoint availability and session drain.
- Initial-state fields: `initial_policy`, `required_operation`, `status`, `topology`
- Expected-target fields: `accepted_policies`, `all_tidb_endpoints_serving`, `business_data_preserved`, `drained_active_connections`, `draining_target`, `protected_router_policy`, `protected_router_target`, `status`
- Background profiles: rg08_checkout_order_lookup, rg08_customer_dashboard_rollup, rg08_inventory_reconciliation, rg08_finance_export_preview, rg08_checkout_write_probe, rg08_cache_refresh_probe, rg08_long_order_transaction, rg08_settlement_status_probe, rg08_instance_identity_probe
- Evaluator: `src.scenarios.evaluation.tidb.resource_governance.connection_balancing.TidbResourceGovernanceConnectionBalancingEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): query_metrics(active_connections)=4/20; query_metrics(cpu)=3/58; query_metrics(qps)=2/6; query_metrics(query_latency)=2/6; manage_cluster(service/list)=3/11; manage_cluster(router/get)=4/0

### `multi_tidb_alternate_target_drain`

- Case number: `1`
- Title: Rebalance the affected pools and drain the alternate TiDB backend.
- Alert/symptom: [P1] Connection placement is unstable during a release window. Compare the three SQL backends, identify the backend carrying the affected application pools, and move those pools before draining that backend. Preserve settlement continuity and in-flight work while keeping the settlement pool within the application-pool rebalance scope; only the identity probe affinity is protected. Preserve endpoint continuity and order truth.
- Initial-state fields: `initial_policy`, `required_operation`, `status`, `topology`
- Expected-target fields: `accepted_policies`, `all_tidb_endpoints_serving`, `business_data_preserved`, `drained_active_connections`, `draining_target`, `protected_router_policy`, `protected_router_target`, `status`
- Background profiles: rg08_checkout_order_lookup, rg08_customer_dashboard_rollup, rg08_inventory_reconciliation, rg08_finance_export_preview, rg08_checkout_write_probe, rg08_cache_refresh_probe, rg08_long_order_transaction, rg08_settlement_status_probe, rg08_instance_identity_probe
- Evaluator: `src.scenarios.evaluation.tidb.resource_governance.connection_balancing.TidbResourceGovernanceConnectionBalancingAlternateTargetEvaluatorCase`
- Calibration evidence (tool m/n): query_metrics(active_connections)=4/16; query_metrics(cpu)=3/45; query_metrics(qps)=2/6; query_metrics(query_latency)=2/6; manage_cluster(service/list)=2/9; manage_cluster(router/get)=2/0

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

- Scenario and Case source: `src.scenarios.tidb.resource_governance.connection_balancing.TidbResourceGovernanceConnectionBalancingScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/resource_governance/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_resource_governance_connection_balancing_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
