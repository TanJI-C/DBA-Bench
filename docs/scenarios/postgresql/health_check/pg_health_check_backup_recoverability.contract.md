---
doc_id: scenario.postgresql.pg_health_check_backup_recoverability
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, health_check, pg_health_check_backup_recoverability]
summary: Current code-backed contract snapshot for pg_health_check_backup_recoverability; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_health_check_backup_recoverability`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `health_check`
- Scenario implementation: `src.scenarios.postgres.health_check.backup_recoverability.PgHealthCheckBackupRecoverabilityScenario`
- Formal entrypoint: `examples/run_pg_health_check_backup_recoverability_scenario.py`
- Current description: Simulates a DR health check where a physical backup cannot recover to the requested target because an archived WAL segment is missing.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `missing_wal_recovery_gap` | Production DR readiness audit with multiple backup chains and one selected unrecoverable recovery window. | `hard` |
| 1 | `single_missing_wal_gap_simple` | A focused DR audit with one selected chain, one healthy comparison chain, and a single missing WAL segment. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `missing_wal_recovery_gap`

- Case number: `0`
- Title: Production DR readiness audit with multiple backup chains and one selected unrecoverable recovery window.
- Alert/symptom: [DR Readiness Audit] The scheduled recoverability audit for a production recovery window needs manual evidence review. Validate the selected backup chain, restore-drill evidence, archive continuity, and the most recent recoverable point for the business recovery target. Several historical drills and monitoring events are present in the catalog, so separate current-window evidence from operational noise before submitting.
- Initial-state fields: `audit_batch_id`, `business_service`, `recovery_window_label`, `requested_recovery_target_time`, `status`
- Expected-target fields: `archive_gap_detected`, `backup_id`, `business_rpo_risk`, `latest_recoverable_time`, `missing_wal_file`, `status`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.health_check.backup_recoverability.PgHealthCheckBackupRecoverabilityForMissingWalRecoveryGapEvaluatorCase`
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md).
- Calibration evidence (tool m/n): SQL/catalog causal={selected audit chain, A7 archive gap, derived 02:31 latest recoverable point}; noise={standby-seed competing recovery source cluster incl. second pending drill, reporting-clone failure cluster, timeline-1 historical drills, retention-expiry explanation, delayed-archive hypothesis cluster (lag warning / retry drained / bucket backlog), unrelated monitoring chatter}. `ops_dr.backup_sets` and the backup manifest no longer carry a precomputed `latest_recoverable_time`; the point is derived from archive continuity or `validate_backup` replay.

### `single_missing_wal_gap_simple`

- Case number: `1`
- Title: A focused DR audit with one selected chain, one healthy comparison chain, and a single missing WAL segment.
- Alert/symptom: [DR Readiness Review] The selected business recovery window has not been signed off. Verify the chosen backup, archive continuity, sandbox restore evidence, and the latest safe recovery point. A prior healthy chain remains visible for comparison.
- Initial-state fields: `audit_batch_id`, `business_service`, `status`
- Expected-target fields: `archive_gap_detected`, `business_rpo_risk`, `status`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.health_check.backup_recoverability.PgHealthCheckBackupRecoverabilityForSingleMissingWalGapSimpleEvaluatorCase`
- Calibration evidence (tool m/n): not declared in code

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

- Scenario and Case source: `src.scenarios.postgres.health_check.backup_recoverability.PgHealthCheckBackupRecoverabilityScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/health_check/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_health_check_backup_recoverability_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
