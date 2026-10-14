---
doc_id: scenario.tidb.tidb_health_check_backup_recoverability
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, health_check, tidb_health_check_backup_recoverability]
summary: Current code-backed contract snapshot for tidb_health_check_backup_recoverability; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: en
---

# `tidb_health_check_backup_recoverability`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `health_check`
- Scenario implementation: `src.scenarios.tidb.health_check.backup_recoverability.TidbHealthCheckBackupRecoverabilityScenario`
- Formal entrypoint: `examples/run_tidb_health_check_backup_recoverability_scenario.py`
- Current description: Routine TiDB backup recoverability health check with isolated restore evidence, checkpoint validation, and noisy commerce workload.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `backup_chain_repair_and_restore` | Repair a corrupted TiDB backup-chain object and prove the approved isolated restore reaches the requested checkpoint rather than trusting a green backup job. | `hard` |
| 1 | `single_segment_continuity_repair` | Repair one readable but unreplicated TiDB backup segment and prove isolated restore continuity. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `backup_chain_repair_and_restore`

- Case number: `0`
- Title: Repair a corrupted TiDB backup-chain object and prove the approved isolated restore reaches the requested checkpoint rather than trusting a green backup job.
- Alert/symptom: [Data Protection Recovery Alert] The approved weekly restore validation for the regional commerce cluster did not reach its requested checkpoint. The scheduler still reports a green backup. Determine why the approved restore did not reach its requested checkpoint. Use the available recovery records and live traffic to identify the affected validation, apply a safe correction in the isolated validation environment, and verify the four critical business tables. Never restore over production, mutate the production business tables, or restart a healthy TiDB/TiKV/PD component.
- Initial-state fields: `backup_jobs`, `business_window`, `request_key`, `status`
- Expected-target fields: `checkpoint`, `critical_tables`, `restore_sample`, `restore_status`, `safety`, `selected_chain`
- Background profiles: hc04_checkout_order_lookup, hc04_merchant_order_rollup, hc04_order_line_reconciliation, hc04_payment_settlement_probe, hc04_inventory_snapshot, hc04_backup_catalog_refresh, hc04_checkpoint_window_probe, hc04_restore_queue_probe, hc04_object_store_inventory_scan, hc04_restore_attempt_poll, hc04_live_checkout_event_writer, hc04_business_checksum_probe
- Evaluator: `src.scenarios.evaluation.tidb.health_check.backup_recoverability.TidbHealthCheckBackupRecoverabilityForBackupChainRepairEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): audit_request_join=6/192; backup_catalog=1/7; log_segments=6/97; restore_drills=1/15; archive_objects=12/106; monitoring_events=4/76; business_workload_profiles=6/9

### `single_segment_continuity_repair`

- Case number: `1`
- Title: Repair one readable but unreplicated TiDB backup segment and prove isolated restore continuity.
- Alert/symptom: The routine data-protection recovery sampling found that the current restore chain does not span the requested checkpoint. Correlate the current request, the approved archive source, segment continuity, and the isolated restore records. Distinguish readable-but-unreplicated from a checksum failure, and repair only the single continuity gap on the isolated target; overwriting production tables or modifying business data is forbidden.
> Note: some of the runtime alerts for this scenario are issued in Chinese by the scenario code; the text above is an English rendering for readability.
- Initial-state fields: `fault_shape`, `request_key`, `status`
- Expected-target fields: `continuity_segment`, `critical_tables`, `production`, `restore_status`
- Background profiles: hc04_checkout_order_lookup, hc04_merchant_order_rollup, hc04_order_line_reconciliation, hc04_payment_settlement_probe, hc04_inventory_snapshot, hc04_backup_catalog_refresh, hc04_checkpoint_window_probe, hc04_restore_queue_probe, hc04_object_store_inventory_scan, hc04_restore_attempt_poll, hc04_live_checkout_event_writer, hc04_business_checksum_probe
- Evaluator: `src.scenarios.evaluation.tidb.health_check.backup_recoverability.TidbHealthCheckBackupRecoverabilityForSingleSegmentContinuityEvaluatorCase`
- Calibration evidence (tool m/n): audit_request_join=8/0; backup_catalog=5/0; archive_objects=29/8; restore_drills=3/0; monitoring_events=4/8; isolated_restore_evidence=7/0

## 4. Agent-visible evidence

- The Agent receives the registered alert and the common TiDB tools: `query_metrics`, `execute_sql`, `manage_cluster`, `read_log`, `search_knowledge`, `help`, `submit`, and `exit`.
- Installing this Case registers the HC04 restore runtime and enables `inspect_backup_archive`, `repair_backup_archive`, `run_isolated_restore`, and `inspect_isolated_restore` before the Agent receives its tool schemas. Recovery clears the runtime and revokes these four tools. Ordinary TiDB Cases do not expose them by default; schemas, help, and action dispatch use the same enabled tool set for humans and LLMs.
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

- Scenario and Case source: `src.scenarios.tidb.health_check.backup_recoverability.TidbHealthCheckBackupRecoverabilityScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/health_check/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_health_check_backup_recoverability_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
