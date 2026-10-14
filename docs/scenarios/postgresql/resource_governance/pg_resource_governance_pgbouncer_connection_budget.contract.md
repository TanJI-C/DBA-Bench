---
doc_id: scenario.postgresql.pg_resource_governance_pgbouncer_connection_budget
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, resource_governance, pg_resource_governance_pgbouncer_connection_budget]
summary: Current code-backed contract snapshot for pg_resource_governance_pgbouncer_connection_budget; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_resource_governance_pgbouncer_connection_budget`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `resource_governance`
- Scenario implementation: `src.scenarios.postgres.resource_governance.pgbouncer_connection_budget.PgResourceGovernancePgbouncerConnectionBudgetScenario`
- Formal entrypoint: `examples/run_pg_resource_governance_pgbouncer_connection_budget_scenario.py`
- Current description: Govern PgBouncer transaction-pool budgets across checkout, reporting and ETL workloads.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `pool_partition_shortage` | PgBouncer connection budget governance under a three-workload replay. | `hard` |
| 1 | `pool_partition_shortage_simple` | Focused PgBouncer connection budget governance. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `pool_partition_shortage`

- Case number: `0`
- Title: PgBouncer connection budget governance under a three-workload replay.
- Alert/symptom: P1 business-capacity alert: checkout, reporting and ETL service degraded during a peak window. PostgreSQL max_connections=40. Reporting must complete at least one unit, ETL must update at least 10 rows, and a scheduled maintenance check must remain available. Restore all services with transaction pooling, keep the existing database and role-level connection ceilings within bounded partitions, and verify queue convergence.
- Initial-state fields: `postgres_headroom`, `status`
- Expected-target fields: `pool_mode`, `postgres_max_connections`, `checkout_role_connection_partition`, `pool_budget`, `queue`, `status`, `workloads`
- Background profiles: report_tpcds, report_probe, health_probe, report_long_noise, checkout_auxiliary_read, reporting_batch_auxiliary
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.pgbouncer_connection_budget.PgResourceGovernancePgbouncerConnectionBudgetEvaluatorCase`
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md).
- Calibration evidence (tool m/n): SQL/catalog m=3 n=4; metric m=2 n=3; workload/operation event m=1 n=1
- Public history: the hard Case captures 360 seconds of normal activity and 180 seconds of target activity, then freezes the shared frozen history over a 12-hour window. The longer normal capture supplies distinct sources for the repeated captured-benign windows, including three 60-second connection-churn windows; the previous 120-second capture could not supply them. It exposes raw `pgbouncer_pool_clients`, `pgbouncer_pool_servers`, `pgbouncer_pool_rates`, `database_capacity`, `service_slo`, and `connection_churn` on a 2-second grid with 20-second overview; bounded historical records are `component_log`, `topsql`, and `operation_event`. The simple Case has no frozen history. This configuration repair preserves the fault and DP/OP/SP contracts. The stated D/C values are existing calibration snapshots; this repair has no new live m/n measurement.
- Normal capture additionally runs the bounded reporting-pool burst (4 concurrent clients, 45 s per 120 s period) in addition to the target capture burst (2 clients), and adds the `short-reporting-queue-burst` captured-benign decoy (2 windows x 30 s, MAD 0.5) on `pgbouncer_pool_clients@testdb/report_user`; the reporting queue is now a recoverable competing hypothesis instead of one-directional corroboration.
- The public `config_revision` operation event does not carry the checkout role name or its old/new connection limit; role-level partition must be discovered from pool-server behavior signatures plus `pg_roles`, which contains the deliberately bounded neighbor roles so a low `rolconnlimit` requires per-role demand/activity discrimination.
- The `checkout_role_connection_partition_is_bounded` outcome check requires `rolconnlimit(checkout_user) >= recovered_checkout_role_connection_limit` (6) in addition to the PostgreSQL ceiling, so partial restorations (2..5) fail; the mixed-workload acceptance replay additionally requires a minimum number of successful checkout calls inside the replay window.

### `pool_partition_shortage_simple`

- Case number: `1`
- Title: Focused PgBouncer connection budget governance.
- Alert/symptom: P2 business-capacity alert: checkout and reporting service degraded during a peak window. PostgreSQL max_connections=40 with spare capacity; reporting must complete at least one unit of work. Restore both services with transaction pooling without raising the PostgreSQL ceiling (40), the PgBouncer database-side server budget (16), or the shared pool budget cap (default_pool_size + reserve_pool_size <= 24); verify queue convergence after the change.
- Initial-state fields: `postgres_headroom`, `status`
- Expected-target fields: `pool_mode`, `postgres_max_connections`, `checkout_role_connection_partition`, `pool_budget`, `queue`, `status`, `workloads`
- Background profiles: report_tpcds, report_probe
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.pgbouncer_connection_budget.PgResourceGovernancePgbouncerConnectionBudgetSimpleEvaluatorCase`
- Calibration evidence (tool m/n): SQL/catalog m=5 n=5; metric m=1 n=0; workload/operation event m=1 n=0
- Mechanism: the incident squeezes the checkout role partition (`checkout_user` rolconnlimit reduced from 20 to 2) while all pooler-side budgets are healthy (`max_db_connections=16`, `default_pool_size=2`, `reserve_pool_size=0`). `pg_roles` also contains two deliberately bounded neighbor roles (`archive_batch_user` limit 2, `report_legacy_user` limit 3) whose limits are intentional and which have no pool route or sessions, so a low `rolconnlimit` requires per-role demand/activity discrimination. The repair must restore the checkout role partition (rolconnlimit 6..40) and re-balance pool sizing so the acceptance replay restores checkout throughput. A no-op, a single-layer partial repair, or a misdirected neighbor-role repair fails the role check, the replay throughput floor, or the safety scope.
- The alert does not disclose the role-connection-partition repair layer.

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

The shared captured-benign admission fix is covered by focused history admission tests.
No new live PostgreSQL run or m/n recalibration was performed for this configuration repair.

- Scenario and Case source: `src.scenarios.postgres.resource_governance.pgbouncer_connection_budget.PgResourceGovernancePgbouncerConnectionBudgetScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/resource_governance/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_resource_governance_pgbouncer_connection_budget_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
