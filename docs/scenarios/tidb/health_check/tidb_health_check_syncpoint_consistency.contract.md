---
doc_id: scenario.tidb.tidb_health_check_syncpoint_consistency
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, health_check, tidb_health_check_syncpoint_consistency]
summary: Current code-backed contract snapshot for tidb_health_check_syncpoint_consistency; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: en
---

# `tidb_health_check_syncpoint_consistency`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `health_check`
- Scenario implementation: `src.scenarios.tidb.health_check.syncpoint_consistency.TidbHealthCheckSyncpointConsistencyScenario`
- Formal entrypoint: `examples/run_tidb_health_check_syncpoint_consistency_scenario.py`
- Current description: Health-check audit for TiDB upstream/downstream consistency under continuous writes.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `syncpoint_consistency_under_writes` | Primary/secondary snapshot consistency audit under continuous writes | `hard` |
| 1 | `syncpoint_consistency_single_release_repair` | A scoped TiDB syncpoint audit for one release window under continued writes. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `syncpoint_consistency_under_writes`

- Case number: `0`
- Title: Primary/secondary snapshot consistency audit under continuous writes
- Alert/symptom: Morning routine inspection: the new-retail accounting/fulfillment chain experienced a sustained write peak last night. Following the on-call reference material in the knowledge base, complete a reproducible primary/secondary consistency audit and decide whether today's downstream stocktaking can be given the go-ahead. Follow the controlled change boundary and do not modify business tables directly; at the end, restore the temporary audit configuration to its pre-inspection state.
- Initial-state fields: `audit_context`, `mapped_snapshot`, `repair_context`, `surface`
- Expected-target fields: `audit_result`, `direct_count_delta`, `gc_config`, `release_decision`, `repair_workflow`, `syncpoint_selection`
- Background profiles: hc02_live_primary_order_writes, hc02_live_primary_item_writes, hc02_direct_count_decoy, hc02_customer_dashboard, hc02_fulfillment_lag_report, hc02_item_revenue_rollup, hc02_repl_noise_events, hc02_syncpoint_catalog_scan, hc02_runbook_lookup, hc02_audit_window_scan, hc02_binding_history_scan, hc02_release_request_queue_scan
- Evaluator: `src.scenarios.evaluation.tidb.health_check.syncpoint_consistency.TidbHealthCheckSyncpointConsistencyEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): release_metadata_and_binding=13/111; orders_mapped_snapshot=4/45; order_items_mapped_snapshot=8/60; order_item_relationships=2/0; schema_contract=3/12; repair_authorizations_and_jobs=19/390; post_repair_artifact=7/28; gc_retention_control=1/35; background_workload=0/75

### `syncpoint_consistency_single_release_repair`

- Case number: `1`
- Title: A scoped TiDB syncpoint audit for one release window under continued writes.
- Alert/symptom: Routine pre-release consistency review: the current release window shows a primary/secondary direct-count difference during continuous writes. First resolve the current consumer, window, syncpoint, and authorization lease, then perform a row-level comparison by mapped TSO. Address only the small amount of drift still authorized by the current release, wait for the asynchronous worker to finish before re-auditing, and restore the temporary GC retention settings.

> Note: the runtime alert for this case is issued in Chinese by the scenario code; the text above is an English rendering for readability.

- Initial-state fields: `audit_context`, `direct_count_decoy`, `surface`
- Expected-target fields: `audit_result`, `gc_config`, `release_decision`, `repair_workflow`
- Background profiles: hc02_live_primary_order_writes, hc02_live_primary_item_writes, hc02_direct_count_decoy, hc02_customer_dashboard, hc02_fulfillment_lag_report, hc02_item_revenue_rollup, hc02_repl_noise_events, hc02_syncpoint_catalog_scan, hc02_runbook_lookup, hc02_audit_window_scan, hc02_binding_history_scan, hc02_release_request_queue_scan
- Evaluator: `src.scenarios.evaluation.tidb.health_check.syncpoint_consistency.TidbHealthCheckSyncpointConsistencyForSingleReleaseRepairEvaluatorCase`
- Calibration evidence (tool m/n): release_metadata_and_binding=2/8; orders_mapped_snapshot=2/4; order_items_mapped_snapshot=2/5; repair_authorizations_and_jobs=2/22; post_repair_artifact=1/2; gc_retention_control=0/0

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

- Scenario and Case source: `src.scenarios.tidb.health_check.syncpoint_consistency.TidbHealthCheckSyncpointConsistencyScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/health_check/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_health_check_syncpoint_consistency_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
