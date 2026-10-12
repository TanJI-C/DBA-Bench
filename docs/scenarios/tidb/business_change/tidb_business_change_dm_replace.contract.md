---
doc_id: scenario.tidb.tidb_business_change_dm_replace
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, business_change, tidb_business_change_dm_replace]
summary: Current code-backed contract snapshot for tidb_business_change_dm_replace; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: en
---

# `tidb_business_change_dm_replace`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `business_change`
- Scenario implementation: `src.scenarios.tidb.business_change.dm_replace.TidbBusinessChangeDmReplaceScenario`
- Formal entrypoint: `examples/run_tidb_business_change_dm_replace_scenario.py`
- Current description: A real SQL-backed TiDB Data Migration task pauses twice on downstream-incompatible release DDLs and must resume without losing either following business event.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `failed_ddl_safe_replace` | Keep a DM migration correct after a downstream-incompatible schema DDL pauses synchronization. | `hard` |
| 1 | `failed_ddl_safe_replace_billing` | Resume a billing DM stream after two incompatible release DDLs without losing events. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `failed_ddl_safe_replace`

- Case number: `0`
- Title: Keep a DM migration correct after a downstream-incompatible schema DDL pauses synchronization.
- Alert/symptom: [CRITICAL] A DM migration task's checkpoint has stopped advancing, the downstream business tables are still on the old schema, and the upstream release window has already committed a continuous stream of business events that depend on two new fields. Resume synchronization event by event without losing any event, damaging existing data, or widening the change scope, and provide reproducible upstream/downstream consistency evidence.
- Initial-state fields: `downstream_schema`, `migration`, `pending_business_events`
- Expected-target fields: `downstream_schema`, `migration`, `pending_business_events`
- Background profiles: order_api_pending_schema_read, order_api_amount_rollup, dm_task_status_dashboard, dm_binlog_history_probe, dm_worker_log_tail_probe, archive_reconciliation_decoy, schema_inventory_decoy, dm_task_history_decoy, dm_source_lag_dashboard_decoy, dm_failed_event_fingerprint_decoy, release_region_rollup_probe
- Evaluator: `src.scenarios.evaluation.tidb.business_change.dm_replace.TidbBusinessChangeDmReplaceEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): not declared in code

### `failed_ddl_safe_replace_billing`

- Case number: `1`
- Title: Resume a billing DM stream after two incompatible release DDLs without losing events.
- Alert/symptom: [CRITICAL] The DM checkpoint of billing-api has stopped advancing; the billing downstream still lacks the two fields from this release, but the billing source has already committed order events that depend on these two fields. Distinguish the active billing task from warehouse/historical noise, repair the downstream schema one by one, and restore synchronization without loss; do not modify source business rows, skip a DDL without an equivalent repair, or widen the control-plane write scope.

> Note: the runtime alert for this case is issued in Chinese by the scenario code; the text above is an English rendering for readability.

- Initial-state fields: `downstream_schema`, `migration`, `pending_business_events`
- Expected-target fields: `downstream_schema`, `migration`, `pending_business_events`
- Background profiles: order_api_pending_schema_read, order_api_amount_rollup, dm_task_status_dashboard, dm_binlog_history_probe, dm_worker_log_tail_probe, archive_reconciliation_decoy, schema_inventory_decoy, dm_task_history_decoy, dm_source_lag_dashboard_decoy, dm_failed_event_fingerprint_decoy, release_region_rollup_probe
- Evaluator: `src.scenarios.evaluation.tidb.business_change.dm_replace.TidbBusinessChangeDmReplaceForBillingEvaluatorCase`
- Calibration evidence (tool m/n): execute_sql(target=control,task/event)=25/0; execute_sql(target=source/primary)=5/0; query_metrics=70/0

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

- Scenario and Case source: `src.scenarios.tidb.business_change.dm_replace.TidbBusinessChangeDmReplaceScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/business_change/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_business_change_dm_replace_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
