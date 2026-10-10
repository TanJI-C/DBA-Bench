---
doc_id: scenario.postgresql.pg_resource_governance_audit_logging
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, resource_governance, pg_resource_governance_audit_logging]
summary: Current code-backed contract snapshot for pg_resource_governance_audit_logging; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_resource_governance_audit_logging`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `resource_governance`
- Scenario implementation: `src.scenarios.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingScenario`
- Formal entrypoint: `examples/run_pg_resource_governance_audit_logging_scenario.py`
- Current description: Simulates excessive audit logging that amplifies disk writes under a high-QPS OLTP workload.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `audit_orders_role_logging` | Simulates excessive audit logging that amplifies disk writes under a high-QPS OLTP workload. | `easy` |
| 1 | `orders_write_audit_scope_simple` | A focused audit logging case with one checkout table and one compliance role. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `audit_orders_role_logging`

- Case number: `0`
- Title: Simulates excessive audit logging that amplifies disk writes under a high-QPS OLTP workload.
- Alert/symptom: P1 production alert: after a compliance logging rollout, checkout transaction throughput dropped by more than half and disk write bandwidth is near saturation. WAL volume and table bloat do not explain the write amplification. Identify the logging source and restore transaction throughput without disabling required compliance coverage.
- Initial-state fields: `audit_scope`, `disk_write_amplification`, `status`, `transaction_throughput`
- Expected-target fields: `audit_scope`, `statement_logging`, `status`, `transaction_throughput`
- Background profiles: checkout_status_rollup, payment_reconciliation_preview, checkout_live_touch_probe, receipt_latency_probe, missing_compliance_cache_log_noise
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `orders_write_audit_scope_simple`

- Case number: `1`
- Title: A focused audit logging case with one checkout table and one compliance role.
- Alert/symptom: P2 compliance rollout alert: checkout write throughput dropped after audit logging was enabled. Disk writes are elevated, but WAL and table growth do not explain the spike. Keep required write/DDL/role audit coverage while restoring transaction throughput.
- Initial-state fields: `audit_scope`, `disk_write_amplification`, `status`
- Expected-target fields: `audit_scope`, `statement_logging`, `status`
- Background profiles: checkout_status_rollup
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingForOrdersWriteAuditScopeSimpleEvaluatorCase`
- Calibration evidence (tool m/n): query_metrics.disk_io/qps=2/1; execute_sql.pg_settings/log_probe=3/1

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

- Scenario and Case source: `src.scenarios.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/resource_governance/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_resource_governance_audit_logging_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
