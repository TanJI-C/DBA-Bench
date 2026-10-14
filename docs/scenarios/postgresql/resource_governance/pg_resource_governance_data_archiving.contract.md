---
doc_id: scenario.postgresql.pg_resource_governance_data_archiving
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, resource_governance, pg_resource_governance_data_archiving]
summary: Current code-backed contract snapshot for pg_resource_governance_data_archiving; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: en
---

# `pg_resource_governance_data_archiving`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `resource_governance`
- Scenario implementation: `src.scenarios.postgres.resource_governance.data_archiving.PgResourceGovernanceDataArchivingScenario`
- Formal entrypoint: `examples/run_pg_resource_governance_data_archiving_scenario.py`
- Current description: Simulates cold order-history archiving and physical space reclaim under online workload constraints.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `order_history_cold_archive` | Simulates cold order-history archiving and physical space reclaim under online workload constraints. | `easy` |
| 1 | `order_history_quarter_archive_simple` | A smaller cold order-history archive with one live sentinel stream and one decoy read profile. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `order_history_cold_archive`

- Case number: `0`
- Title: Simulates cold order-history archiving and physical space reclaim under online workload constraints.
- Alert/symptom: P1 storage capacity alert: the data directory usage of the single-node PostgreSQL instance has stayed above 80%, and the order_history table's footprint is growing markedly with an abnormal proportion of cold data. The business is still writing online, there is currently no downtime window, and reclamation methods that hold an ACCESS EXCLUSIVE lock for a long time are forbidden. Archive the cold data older than one year and reclaim the physical space while avoiding blocking core transactions.

> Note: some of the runtime alerts for this scenario are issued in Chinese by the scenario code; the text above is an English rendering for readability.
- Initial-state fields: `cold_data`, `physical_space`, `status`
- Expected-target fields: `cold_data`, `physical_space`, `status`, `strategy`
- Background profiles: order_retention_dashboard_rollup, customer_history_payload_rollup, recent_order_touch_probe, archive_table_existence_probe, missing_retention_summary_log_noise
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.data_archiving.PgResourceGovernanceDataArchivingForOrderHistoryColdArchiveEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `order_history_quarter_archive_simple`

- Case number: `1`
- Title: A smaller cold order-history archive with one live sentinel stream and one decoy read profile.
- Alert/symptom: P2 storage governance alert: order_history_q1 has a compact set of one-year-old rows consuming live-table space while checkout writes continue. Archive the cold slice and reclaim physical space without long ACCESS EXCLUSIVE maintenance or VACUUM FULL.
- Initial-state fields: `cold_data`, `physical_space`, `status`
- Expected-target fields: `cold_data`, `physical_space`, `status`, `strategy`
- Background profiles: order_retention_dashboard_rollup
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.data_archiving.PgResourceGovernanceDataArchivingForOrderHistoryQuarterArchiveSimpleEvaluatorCase`
- Calibration evidence (tool m/n): query_metrics.disk_usage/workload_activity=2/1; execute_sql.archive_verification=3/1

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

- Scenario and Case source: `src.scenarios.postgres.resource_governance.data_archiving.PgResourceGovernanceDataArchivingScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/resource_governance/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_resource_governance_data_archiving_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
