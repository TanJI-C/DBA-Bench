---
doc_id: scenario.tidb.tidb_business_change_online_ddl_pause_resume
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, business_change, tidb_business_change_online_ddl_pause_resume]
summary: Current code-backed contract snapshot for tidb_business_change_online_ddl_pause_resume; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: en
---

# `tidb_business_change_online_ddl_pause_resume`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `business_change`
- Scenario implementation: `src.scenarios.tidb.business_change.online_ddl_pause_resume.TidbBusinessChangeOnlineDdlPauseResumeScenario`
- Formal entrypoint: `examples/run_tidb_business_change_online_ddl_pause_resume_scenario.py`
- Current description: Resume a paused TiDB online unique-index backfill without duplicating the DDL job.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `paused_unique_index_backfill` | Resume one paused unique-index backfill under concurrent business reads. | `hard` |
| 1 | `paused_unique_index_backfill_billing` | Resume one paused billing unique-index backfill under concurrent payment reads. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `paused_unique_index_backfill`

- Case number: `0`
- Title: Resume one paused unique-index backfill under concurrent business reads.
- Alert/symptom: [CHANGE] The order platform needs to complete the unique lookup key schema change for the current primary route of the order event stream under live read traffic. The cluster currently holds seven similar background index builds that have started but are paused, covering the primary business, historical archive, shadow, replay, canary, mirror, and reporting candidates; the database also retains similar historical DDL, indexes, audit queries, and business route registrations. Do not guess the target from table names, row counts, or the most recent record; route_registry stores only the logical route_key and binding_id, not the physical table. The observation moment for this incident is fixed at 2026-08-02 23:59:59 UTC. route_registry retains multiple active primary/current markers from the staged rollout; do not pick the table by the latest version or the current_route field alone — you must verify the versioned route binding's serving lease, effective time window, and the current observation moment. The cluster also keeps control-plane and data-plane records covering routes, lease/owner, cutover, traffic, runtime, business contracts, schema-change requests, the index catalog, and DDL history; correlate the live evidence to confirm the currently serving relation and the existing schema change. Do not modify business data and do not submit a duplicate schema change; complete the existing change according to the business objective. Before submitting, you must verify that the job has completed, the target index is unique and visible, ADMIN CHECK TABLE passes, there is no duplicate add-index job, and the business truth is unchanged.
- Initial-state fields: `candidate_table_count`, `concurrent_business_reads`, `ddl_job_state`, `index_name`, `index_state`, `paused_add_index_jobs`, `route_resolution_hops`, `status`
- Expected-target fields: `add_index_job_count`, `admin_check`, `business_truth_unchanged`, `ddl_job_state`, `public_unique_index`
- Background profiles: svc_read_01_point, svc_read_01_queue, svc_read_01_rollup, svc_read_01_window, svc_read_01_lookup, svc_read_01_reconciliation, svc_read_01_join, svc_read_01_probe, svc_read_02_point, svc_read_02_queue, svc_read_02_rollup, svc_read_02_window
- Evaluator: `src.scenarios.evaluation.tidb.business_change.online_ddl_pause_resume.TidbBusinessChangeOnlineDdlPauseResumeForPausedIndexBackfillEvaluatorCase`
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md).
- Calibration evidence (tool m/n): execute_sql:statement_summary=0/50; query_metrics:active_connections=0/62; execute_sql:route_registry=1/10; execute_sql:route_binding=1/11; execute_sql:route_lease_fence=1/11; execute_sql:route_owner_heartbeat=1/10; execute_sql:route_cutover_commit=1/11; execute_sql:route_traffic_assignment=1/11; execute_sql:route_runtime_observation=1/11; execute_sql:business_query_contract=1/13; execute_sql:business_query_probe=1/6; execute_sql:schema_change_request=1/11; execute_sql:ddl_history=1/16; execute_sql:ddl_job_query=1/0; execute_sql:index_catalog=0/35; execute_sql:table_cardinality=1/15; execute_sql:column_catalog=1/149; execute_sql:business_truth=1/0

### `paused_unique_index_backfill_billing`

- Case number: `1`
- Title: Resume one paused billing unique-index backfill under concurrent payment reads.
- Alert/symptom: [CHANGE] The settlement platform needs to complete the unique lookup key schema change for the current primary route of billing.events under live read traffic. The cluster currently holds seven similar background index builds that have started but are paused, covering the payment primary business, historical archive, shadow, replay, canary, mirror, and reporting candidates; the database also retains similar historical DDL, indexes, audit queries, and business route registrations. Do not guess the target from table names, row counts, or the most recent record; route_registry stores only the logical route_key and binding_id, not the physical table. The observation moment for this incident is fixed at 2026-08-02 23:59:59 UTC. route_registry retains multiple active primary/current markers from the staged rollout; do not pick the table by the latest version or the current_route field alone — you must verify the versioned route binding's serving lease, effective time window, and the current observation moment. The cluster also keeps control-plane and data-plane records covering routes, lease/owner, cutover, traffic, runtime, business contracts, schema-change requests, the index catalog, and DDL history; correlate the live evidence to confirm the currently serving relation and the existing schema change. Do not modify business data and do not submit a duplicate schema change; complete the existing change according to the business objective. Before submitting, you must verify that the job has completed, the target index is unique and visible, ADMIN CHECK TABLE passes, there is no duplicate add-index job, and the business truth is unchanged.

> Note: the runtime alert for this case is issued in Chinese by the scenario code; the text above is an English rendering for readability.
- Initial-state fields: `candidate_table_count`, `concurrent_business_reads`, `ddl_job_state`, `index_name`, `index_state`, `paused_add_index_jobs`, `route_resolution_hops`, `status`
- Expected-target fields: `add_index_job_count`, `admin_check`, `business_truth_unchanged`, `ddl_job_state`, `public_unique_index`
- Background profiles: svc_read_01_point, svc_read_01_queue, svc_read_01_rollup, svc_read_01_window, svc_read_01_lookup, svc_read_01_reconciliation, svc_read_01_join, svc_read_01_probe, svc_read_02_point, svc_read_02_queue, svc_read_02_rollup, svc_read_02_window
- Evaluator: `src.scenarios.evaluation.tidb.business_change.online_ddl_pause_resume.TidbBusinessChangeOnlineDdlPauseResumeForBillingEvaluatorCase`
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md).
- Calibration evidence (tool m/n): execute_sql:statement_summary=0/50; query_metrics:active_connections=0/62; execute_sql:route_registry=1/10; execute_sql:route_binding=1/11; execute_sql:route_lease_fence=1/11; execute_sql:route_owner_heartbeat=1/10; execute_sql:route_cutover_commit=1/11; execute_sql:route_traffic_assignment=1/11; execute_sql:route_runtime_observation=1/11; execute_sql:business_query_contract=1/13; execute_sql:business_query_probe=1/6; execute_sql:schema_change_request=1/11; execute_sql:ddl_history=1/16; execute_sql:ddl_job_query=1/0; execute_sql:index_catalog=0/35; execute_sql:table_cardinality=1/15; execute_sql:column_catalog=1/149; execute_sql:business_truth=1/0

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

- Scenario and Case source: `src.scenarios.tidb.business_change.online_ddl_pause_resume.TidbBusinessChangeOnlineDdlPauseResumeScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/business_change/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_business_change_online_ddl_pause_resume_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
