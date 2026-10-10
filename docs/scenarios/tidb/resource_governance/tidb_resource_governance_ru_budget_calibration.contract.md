---
doc_id: scenario.tidb.tidb_resource_governance_ru_budget_calibration
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, resource_governance, tidb_resource_governance_ru_budget_calibration]
summary: Current code-backed contract snapshot for tidb_resource_governance_ru_budget_calibration; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `tidb_resource_governance_ru_budget_calibration`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `resource_governance`
- Scenario implementation: `src.scenarios.tidb.resource_governance.ru_budget_calibration.TidbResourceGovernanceRuBudgetCalibrationScenario`
- Formal entrypoint: `examples/run_tidb_resource_governance_ru_budget_calibration_scenario.py`
- Current description: Calibrates RU budgets for mixed OLTP and OLAP workloads under a shared cap.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `mixed_oltp_olap_ru_budget_calibration` | Calibrate RU budgets for mixed OLTP and OLAP workloads. | `hard` |
| 1 | `mixed_oltp_olap_ru_budget_rebalanced` | Rebalance mixed OLTP and OLAP RU budgets under a tighter platform reservation. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `mixed_oltp_olap_ru_budget_calibration`

- Case number: `0`
- Title: Calibrate RU budgets for mixed OLTP and OLAP workloads.
- Alert/symptom: [SEV-2] TiDB resource governance review: order-entry and revenue services share one cluster with archive and dashboard traffic. Users report uneven response time and analytical progress while the admission allocation is under review. Use the live database and workload evidence, including the operations service objectives, to choose a finite bounded allocation for the existing resource groups. Keep service continuity
- Initial-state fields: `resource_control`, `resource_groups`
- Expected-target fields: `burstable`, `max_oltp_p95_ms`, `maximum_total_ru_per_sec`, `min_olap_qps`, `minimum_ru_per_sec`, `resource_control`
- Background profiles: rg01_oltp_order_lookup, rg01_oltp_customer_lookup, rg01_oltp_status_probe, rg01_oltp_order_update, rg01_olap_revenue_rollup, rg01_olap_region_join, rg01_oltp_order_history_probe, rg01_olap_customer_mix, rg01_batch_archive_scan, rg01_batch_customer_rollup, rg01_batch_month_close, rg01_batch_event_rollup
- Evaluator: `src.scenarios.evaluation.tidb.resource_governance.ru_budget_calibration.TidbResourceGovernanceRuBudgetCalibrationEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): query_metrics=16/90; execute_sql=29/39; business_truth=1/0

### `mixed_oltp_olap_ru_budget_rebalanced`

- Case number: `1`
- Title: Rebalance mixed OLTP and OLAP RU budgets under a tighter platform reservation.
- Alert/symptom: [SEV-2] The order-entry and revenue workloads are both online, but the platform reservation for the next reporting window is smaller than the previous allocation. Use current workload and service-objective evidence to choose finite budgets for the existing groups, preserve order truth, and keep resource control enabled. Do not disable admission control or restart nodes.
- Initial-state fields: `platform_reservation`, `resource_control`, `resource_groups`
- Expected-target fields: `burstable`, `max_oltp_p95_ms`, `maximum_total_ru_per_sec`, `min_olap_qps`, `minimum_ru_per_sec`, `resource_control`
- Background profiles: rg01_oltp_order_lookup, rg01_oltp_customer_lookup, rg01_oltp_status_probe, rg01_oltp_order_update, rg01_olap_revenue_rollup, rg01_olap_region_join, rg01_oltp_order_history_probe, rg01_olap_customer_mix, rg01_batch_archive_scan, rg01_batch_customer_rollup, rg01_batch_month_close, rg01_batch_event_rollup
- Evaluator: `src.scenarios.evaluation.tidb.resource_governance.ru_budget_calibration.TidbResourceGovernanceRuBudgetCalibrationRebalancedEvaluatorCase`
- Calibration evidence (tool m/n): execute_sql(resource_groups)=4/0; execute_sql(service_objectives)=8/0; execute_sql(resource_groups_recheck)=4/0; business_truth=1/0

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

- Scenario and Case source: `src.scenarios.tidb.resource_governance.ru_budget_calibration.TidbResourceGovernanceRuBudgetCalibrationScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/resource_governance/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_resource_governance_ru_budget_calibration_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
