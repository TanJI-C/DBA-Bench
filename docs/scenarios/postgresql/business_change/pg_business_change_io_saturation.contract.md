---
doc_id: scenario.postgresql.pg_business_change_io_saturation
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, pg_business_change_io_saturation]
summary: Current code-backed contract for pg_business_change_io_saturation; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_business_change_io_saturation`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `business_change`
- Scenario implementation: `src.scenarios.postgres.business_change.io_saturation.PgBusinessChangeIoSaturationScenario`
- Formal entrypoint: `examples/run_pg_business_change_io_saturation_scenario.py`
- Current description: Slow-query alert caused by background maintenance saturating database I/O.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `reporting_maintenance_io_saturation` | Slow-query alert caused by background maintenance saturating database I/O. | `hard` |
| 1 | `vacuum_report_io_victim_simple` | Slow report alerts caused by a maintenance refresh saturating I/O. | `hard` |
| 2 | `archive_backlog_io_pressure` | I/O saturation alert caused by a stalled WAL archive slot rather than report SQL regressions. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `reporting_maintenance_io_saturation`

- Case number: `0`
- Title: Slow-query alert caused by background maintenance saturating database I/O.
- Alert/symptom: [FIRING: WARNING] alertname=PostgresReportQueryLatencyHigh service=tpcds-reporting instance=postgresql-primary severity=warning summary=Multiple TPC-DS report query fingerprints exceeded the slow-query threshold description=In the last 5m, customer revenue, regional sales, and inventory trend reports all exceeded 5s latency; p95 report latency is 18.4s. Please diagnose the shared cause of the concurrent query slowdow
- Initial-state fields: `alert`, `status`, `table`, `visible_symptom`
- Expected-target fields: `maintenance_sessions`, `root_cause`, `status`, `table`
- Background profiles: regional_sales_dashboard_refresh, report_temp_spill_rollup, invoice_cpu_rollup, order_status_touch_worker, missing_report_cache_log_noise
- Evaluator: `src.scenarios.evaluation.postgres.business_change.io_saturation.PgBusinessChangeIoSaturationForReportingMaintenanceIoSaturationEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
### `vacuum_report_io_victim_simple`

- Case number: `1`
- Title: Slow report alerts caused by a maintenance refresh saturating I/O.
- Alert/symptom: [FIRING: WARNING] alertname=PostgresReportQueryLatencyHigh service=ops-reporting instance=postgresql-primary severity=warning summary=Two operational reports crossed the slow-query threshold together description=Recent slow-query samples point at customer aging and shipment status reports, while host storage latency is elevated. Determine whether the reports share an infrastructure cause or independent SQL regression
- Initial-state fields: `alert`, `status`, `table`, `visible_symptom`
- Expected-target fields: `maintenance_sessions`, `root_cause`, `status`, `table`
- Background profiles: regional_sales_dashboard_refresh, report_temp_spill_rollup
- Evaluator: `src.scenarios.evaluation.postgres.business_change.io_saturation.PgBusinessChangeIoSaturationForVacuumReportIoVictimSimpleEvaluatorCase`
- Calibration is measured per Case against the live reference workload; the tool-hit ledger and rho values are maintained by the Case registry and the [difficulty standard](../../../standards/scenario/difficulty.standard.md), not restated in this contract.
### `archive_backlog_io_pressure`

- Case number: `2`
- Title: I/O saturation alert caused by a stalled WAL archive slot rather than report SQL regressions.
- Alert/symptom: [FIRING: WARNING] alertname=PostgresDiskIOLatencyHigh service=checkout-writes instance=postgresql-primary severity=warning summary=Database write latency and report latency rose while disk I/O stayed elevated description=Recent dashboards show several report samples and checkout writes slower than normal, but the WAL/archive panel also shows unusual backlog growth. Determine whether the visible slow SQL is the root c
- Initial-state fields: `alert`, `fault_mechanism`, `status`, `table`, `visible_symptom`
- Expected-target fields: `maintenance_sessions`, `root_cause`, `status`, `table`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.business_change.io_saturation.PgBusinessChangeIoSaturationForArchiveBacklogIoPressureEvaluatorCase`

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

- Scenario and Case source: `src.scenarios.postgres.business_change.io_saturation.PgBusinessChangeIoSaturationScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/business_change/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_business_change_io_saturation_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
