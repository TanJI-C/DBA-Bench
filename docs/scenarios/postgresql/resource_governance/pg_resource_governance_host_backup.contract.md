---
doc_id: scenario.postgresql.pg_resource_governance_host_backup
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, resource_governance, pg_resource_governance_host_backup]
summary: Current code-backed contract snapshot for pg_resource_governance_host_backup; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_resource_governance_host_backup`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `resource_governance`
- Scenario implementation: `src.scenarios.postgres.resource_governance.host_backup.PgResourceGovernanceHostBackupScenario`
- Formal entrypoint: `examples/run_pg_resource_governance_host_backup_scenario.py`
- Current description: Simulates a host backup reader saturating storage read bandwidth and making unrelated reports slow.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `nightly_backup_read_saturation` | Simulates a host backup reader saturating storage read bandwidth while multiple reports are victims. | `easy` |
| 1 | `single_backup_reader_simple` | A focused backup read-saturation case with one backup reader and one report-victim query. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `nightly_backup_read_saturation`

- Case number: `0`
- Title: Simulates a host backup reader saturating storage read bandwidth while multiple reports are victims.
- Alert/symptom: P1 reporting latency alert: several unrelated reports became slow at the same time while database CPU and individual SQL plans look normal. Host storage read latency and iowait are elevated during the backup window. Identify the external backup read stream, avoid per-query tuning, and pause, limit, or move the backup so reports recover.
- Initial-state fields: `disk_read_pressure`, `report_queries`, `status`
- Expected-target fields: `backup_job`, `report_latency`, `status`
- Background profiles: report_latency_victim_customer, report_latency_victim_shipment
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.host_backup.PgResourceGovernanceHostBackupForNightlyBackupReadSaturationEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `single_backup_reader_simple`

- Case number: `1`
- Title: A focused backup read-saturation case with one backup reader and one report-victim query.
- Alert/symptom: P2 storage governance alert: one operational report slowed down during a backup window, and disk read latency is elevated. The database does not show a single bad query plan. Find the backup read stream and govern it without restarting PostgreSQL or changing report SQL.
- Initial-state fields: `disk_read_pressure`, `report_queries`, `status`
- Expected-target fields: `backup_job`, `report_latency`, `status`
- Background profiles: simple_report_latency_victim
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.host_backup.PgResourceGovernanceHostBackupForSingleBackupReaderSimpleEvaluatorCase`
- Calibration evidence (tool m/n): query_metrics.disk_io/slow_queries=2/1; execute_sql.pg_stat_activity/job_catalog=2/1

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

- Scenario and Case source: `src.scenarios.postgres.resource_governance.host_backup.PgResourceGovernanceHostBackupScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/resource_governance/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_resource_governance_host_backup_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
