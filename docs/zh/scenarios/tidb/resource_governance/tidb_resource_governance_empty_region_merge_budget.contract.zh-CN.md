---
doc_id: scenario.tidb.tidb_resource_governance_empty_region_merge_budget
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, resource_governance, tidb_resource_governance_empty_region_merge_budget]
summary: Current code-backed contract snapshot for tidb_resource_governance_empty_region_merge_budget; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `tidb_resource_governance_empty_region_merge_budget`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `resource_governance`
- Scenario implementation: `src.scenarios.tidb.resource_governance.empty_region_merge_budget.TidbResourceGovernanceEmptyRegionMergeBudgetScenario`
- Formal entrypoint: `examples/run_tidb_resource_governance_empty_region_merge_budget_scenario.py`
- Current description: Govern Empty Region heartbeat and merge scheduling pressure without changing live order data.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `empty_region_merge_budget` | A live order workload coexists with a Region scheduling backlog after recent table maintenance; PD budget and protected online objects must remain healthy. | `hard` |
| 1 | `empty_region_merge_reduced_inventory` | Reduce a smaller Empty Region inventory without widening the PD merge budget. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `empty_region_merge_budget`

- Case number: `0`
- Title: A live order workload coexists with a Region scheduling backlog after recent table maintenance; PD budget and protected online objects must remain healthy.
- Alert/symptom: [WARNING] [Grafana/TiDB-PD/Region health] 集群 Region inventory 持续增长，PD heartbeat 处理和 operator 队列开始占用预算；订单查询仍可执行，但调度延迟和 PD CPU 有上升趋势。请在不修改在线数据、不删除业务表、不重启集群的前提下治理 Region 调度风险，选择有界的 merge/scheduler 预算，观察风险收敛，并证明没有引发新的调度风暴。
- Initial-state fields: `business`, `pd_scheduling`, `region_inventory`, `status`
- Expected-target fields: `business_result_preserved`, `pd_scheduling`, `region_risk`, `status`
- Background profiles: rg07_order_tenant_status_dashboard, rg07_order_point_lookup, rg07_control_region_rollup, rg07_audit_reconciliation, rg07_table_inventory_probe, rg07_business_status_decoy, rg07_audit_recent_decoy
- Evaluator: `src.scenarios.evaluation.tidb.resource_governance.empty_region_merge_budget.TidbResourceGovernanceEmptyRegionMergeBudgetEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): manage_cluster(store/list)=3/0; table_catalog=24/7; pd_config(schedule)=5/38; query_metrics(cpu)=0/27; business_query=0/64

### `empty_region_merge_reduced_inventory`

- Case number: `1`
- Title: Reduce a smaller Empty Region inventory without widening the PD merge budget.
- Alert/symptom: [WARNING] PD scheduling pressure remains visible after a smaller maintenance inventory was cleared. Correlate Empty Region counts, table inventory, scheduler settings, and order truth; restore bounded cross-table merge scheduling and let the inventory converge. Do not modify data, drop the online order tables, or restart the cluster.
- Initial-state fields: `business`, `pd_scheduling`, `region_inventory`, `status`
- Expected-target fields: `business_result_preserved`, `inventory`, `pd_scheduling`, `region_risk`, `status`
- Background profiles: rg07_order_tenant_status_dashboard, rg07_order_point_lookup, rg07_control_region_rollup, rg07_audit_reconciliation, rg07_table_inventory_probe, rg07_business_status_decoy, rg07_audit_recent_decoy
- Evaluator: `src.scenarios.evaluation.tidb.resource_governance.empty_region_merge_budget.TidbResourceGovernanceEmptyRegionMergeBudgetReducedInventoryEvaluatorCase`
- Calibration evidence (tool m/n): manage_cluster(store/list)=3/0; table_catalog=16/6; pd_config(schedule)=5/34; query_metrics(cpu)=0/24; business_query=1/48

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

- Scenario and Case source: `src.scenarios.tidb.resource_governance.empty_region_merge_budget.TidbResourceGovernanceEmptyRegionMergeBudgetScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/resource_governance/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_resource_governance_empty_region_merge_budget_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
