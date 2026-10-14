---
doc_id: scenario.postgresql.pg_resource_governance_audit_logging
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, resource_governance, pg_resource_governance_audit_logging]
summary: Defines real pgAudit session/object logging, scoped compliance coverage, snapshot recovery, and measured reference evidence for the audit logging Cases.
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
| 1 | `orders_write_audit_scope_simple` | A focused pgAudit case with one checkout table and one compliance audit role. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `audit_orders_role_logging`

- Case number: `0`
- Title: Simulates excessive audit logging that amplifies disk writes under a high-QPS OLTP workload.
- Alert/symptom: P1 production alert: a compliance logging rollout caused excessive checkout log writes not explained by WAL or table growth. Restore normal checkout operation while retaining real audit records for INSERT/UPDATE/DELETE, DDL and role changes. Routine checkout SELECTs must not produce statement or audit logs, and checkout reads/writes must succeed. No particular native statement-logging setting is required.
- Initial-state fields: `audit_scope`, `disk_write_amplification`, `status`
- Expected-target fields: `audit_scope`, `business_read_write`, `checkout_read_logging`, `status`
- Background profiles: checkout_status_rollup, payment_reconciliation_preview, checkout_live_touch_probe, receipt_latency_probe, missing_compliance_cache_log_noise
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `orders_write_audit_scope_simple`

- Case number: `1`
- Title: A focused pgAudit case with one checkout table and one compliance audit role.
- Alert/symptom: P2 compliance rollout alert: checkout log writes increased after audit logging was enabled, without corresponding WAL or table growth. Retain real audit records for INSERT/UPDATE/DELETE, DDL and role changes while eliminating routine checkout SELECT logs. Checkout reads/writes must succeed; no particular native statement-logging setting is required.
- Initial-state fields: `audit_scope`, `disk_write_amplification`, `status`
- Expected-target fields: `audit_scope`, `business_read_write`, `checkout_read_logging`, `status`
- Background profiles: checkout_status_rollup
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingForOrdersWriteAuditScopeSimpleEvaluatorCase`
- Calibration: current real-pgAudit reference evidence is described below; measured values are owned by the code registry.

### Real pgAudit mechanism and acceptance

The dedicated PostgreSQL 16 image installs `postgresql-16-pgaudit`. Both Cases
preload `pg_stat_statements,pgaudit`, install `CREATE EXTENSION pgaudit` before
enabling its audit settings, and retain the original business workload. The
initial state enables native `log_statement=all`, pgAudit session logging
`pgaudit.log=all`, and object auditing through the compliance role's SELECT,
INSERT, UPDATE and DELETE privileges. These real logging paths amplify reads.

Final acceptance evaluates actual behavior. On a fresh connection, the evaluator
runs an ordinary checkout SELECT, an UPDATE of its existing row, an INSERT/DELETE
of a probe row, CREATE TEMP TABLE and CREATE ROLE. All writes and probe objects
are rolled back. It requires real pgAudit records for INSERT, UPDATE, DELETE,
CREATE TABLE (including its object identity) and CREATE ROLE, one successful non-null checkout read, a successful
UPDATE of that checkout row, and zero logs for the ordinary checkout SELECT.
Both native statement/duration logs and pgAudit session/object READ records count
as unnecessary read logging. The existing positive business-row check remains.

The evaluator reads the append-only log segment and isolates entries by the fresh
backend PID using the shared PostgreSQL log parser and standard CSV parsing for
pgAudit records. A final LOG marker from that backend confirms the preceding
records have arrived before absence of READ logs is judged. Collection polls up
to 20 times at 100 ms intervals; inability to collect the marker is an explicit
log-collection error, not a business latency threshold. Probe SQL failures remain
explicit errors, and transactions/connections are cleaned up on failures.

The reference repair sets `pgaudit.log='write,ddl,role'`, revokes the audit role's
SELECT privilege, and uses native `log_statement=none`. This is one valid repair,
not a required configuration. Native `none`, `mod` or `ddl`, alternate/empty object
audit roles, equivalent masks and additional harmless audit classes are accepted
when actual outcomes satisfy the same contract. ROLE is an audit class;
`pgaudit.role` selects an object-audit role whose SELECT privilege can continue
logging reads even when session READ is disabled. Disabling real audit coverage,
leaving checkout READ logging, or breaking business reads/writes fails. Placeholder
GUCs/native statements alone cannot produce the required structured audit records.

There is no numerical throughput/latency, disk-I/O or log-volume SLO in this Case.
The result proves required audit behavior, removal of checkout READ logging and
business availability; it does not claim that a throughput SLO has been measured.
The public alert discloses the behavioral acceptance requirements.

Runtime sessions stop before snapshots. The extension, role and privileges are
persisted, and activation verifies them before recreating checkout workers.
Recovery stops workers, resets pgAudit/native settings, reloads through a fresh
connection, then drops the extension, business table and owned audit role.

### Reference path and calibration evidence

The reference logical path has two hops: excessive log writes under active checkout traffic
→ repeated checkout statements in server logs without corresponding WAL/table
growth → overlapping native and pgAudit session/object READ policies exceed
required write/DDL/role coverage. Settings, extension metadata, role grants and
real logs expose the final compound causal state. Repair and verification calls
do not add diagnostic depth.

Calibration measures the same initial fault, workload and diagnostic evidence; behavioral outcome probes run after diagnostic sampling and do not add diagnostic depth. Previous native-logging calibration is superseded. The current registry stores
new reference measurements; the catalog reflects their labels. The validation
script below records unfiltered `pg_settings` rows and table-grant rows under the
same live workload, all server log lines appended during a declared three-second
window, and the initial disk-I/O/QPS series returned to the reference agent.
Settings count five causal rows (`shared_preload_libraries`, `pgaudit.log`,
`pgaudit.role`, `log_statement`, `log_min_duration_statement`); grants count the
four owned audit-role privileges; log lines count actual checkout-table audit or
statement entries; disk writes/QPS are causal samples and disk reads competing
samples. Other rows/lines are retained as observable units. Full m/n, sample
windows, workload, audit-proof logs and run IDs are written to
`logs/calibration/pg-audit-reference-<case_id>.json`. No frozen results or data
artifacts are rewritten.

```bash
conda run -n aiops python scripts/validate_pg_audit_logging.py audit_orders_role_logging
conda run -n aiops python scripts/validate_pg_audit_logging.py orders_write_audit_scope_simple
```

The script also proves real WRITE/DDL/ROLE log records with native logging off,
absence of a marked read-only SELECT, rejection of table- or column-level object SELECT grants, and
acceptance of native none/mod/ddl, session-only and subtractive-mask configurations.

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
