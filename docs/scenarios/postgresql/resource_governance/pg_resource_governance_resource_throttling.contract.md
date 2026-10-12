---
doc_id: scenario.postgresql.pg_resource_governance_resource_throttling
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, resource_governance, pg_resource_governance_resource_throttling]
summary: Current code-backed contract snapshot for pg_resource_governance_resource_throttling; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: en
---

# `pg_resource_governance_resource_throttling`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `resource_governance`
- Scenario implementation: `src.scenarios.postgres.resource_governance.resource_throttling.PgResourceGovernanceResourceThrottlingScenario`
- Formal entrypoint: `examples/run_pg_resource_governance_resource_throttling_scenario.py`
- Current description: Simulates mixed OLTP and reporting workload contention and requires role-level resource isolation.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `tenant_report_role_throttling` | Simulates mixed OLTP and reporting workload contention and requires role-level resource isolation. | `easy` |
| 1 | `single_report_role_limit_simple` | A focused resource isolation case with one report role, one OLTP role, and one nearby analytics decoy. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `tenant_report_role_throttling`

- Case number: `0`
- Title: Simulates mixed OLTP and reporting workload contention and requires role-level resource isolation.
- Alert/symptom: P1 mixed-business resource alert: on a single-node PostgreSQL instance, CPU usage has stayed persistently high, core transaction interface P95 latency has risen from the millisecond level to the second level, and QPS has dropped noticeably. The number of active sessions on the same instance is rising and long-running SQL exists. Investigate the source of the resource consumption, restore core transaction latency without restarting the instance and while complying with security requirements, and reduce the risk of recurrence.

> Note: some of the runtime alerts for this scenario are issued in Chinese by the scenario code; the text above is an English rendering for readability.
- Initial-state fields: `resource_contention`, `status`, `transaction_latency`
- Expected-target fields: `report_query`, `resource_isolation`, `status`, `transaction_latency`
- Background profiles: tenant_dashboard_rollup, customer_segment_export_preview, etl_ledger_backfill_probe, order_api_point_probe, missing_report_cache_log_noise
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.resource_throttling.PgResourceGovernanceResourceThrottlingForTenantReportRoleThrottlingEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `single_report_role_limit_simple`

- Case number: `1`
- Title: A focused resource isolation case with one report role, one OLTP role, and one nearby analytics decoy.
- Alert/symptom: P2 mixed workload alert: checkout point reads on the shared PostgreSQL instance have slowed from millisecond latency to several hundred milliseconds while instance CPU usage stays elevated and the number of active sessions keeps growing. Investigate the source of the resource usage, restore core transaction latency without restarting the instance, and reduce the risk of recurrence.
- Initial-state fields: `resource_contention`, `status`, `transaction_latency`
- Expected-target fields: `report_query`, `resource_isolation`, `status`, `transaction_latency`
- Background profiles: tenant_dashboard_rollup, customer_segment_export_preview, etl_ledger_backfill_probe, order_api_point_probe
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.resource_throttling.PgResourceGovernanceResourceThrottlingForSingleReportRoleLimitSimpleEvaluatorCase`
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md).
- Calibration evidence (tool m/n): query_metrics.cpu/qps=1/1; execute_sql.pg_stat_activity/role_settings=3/4

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

- Scenario and Case source: `src.scenarios.postgres.resource_governance.resource_throttling.PgResourceGovernanceResourceThrottlingScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/resource_governance/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_resource_governance_resource_throttling_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
