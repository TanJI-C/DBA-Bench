---
doc_id: scenario.postgresql.pg_resource_governance_io_context_workload
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, pg_resource_governance_io_context_workload]
summary: Current code-backed contract snapshot for pg_resource_governance_io_context_workload; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_resource_governance_io_context_workload`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `resource_governance`
- Scenario implementation: `src.scenarios.postgres.resource_governance.io_context_workload.PgResourceGovernanceIoContextWorkloadScenario`
- Formal entrypoint: `examples/run_pg_resource_governance_io_context_workload_scenario.py`
- Current description: PG16 I/O context and workload buckets distinguish a causal batch worker from read-count noise.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `report_is_pressure` | PG16 I/O context identifies a workload window that violates the OLTP SLO. | `hard` |
| 1 | `report_is_pressure_simple` | A reduced I/O-context case separates a causal workload from read-count noise. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `report_is_pressure`

- Case number: `0`
- Title: PG16 I/O context identifies a workload window that violates the OLTP SLO.
- Alert/symptom: [FIRING: WARNING] alertname=PostgresCacheHitAndReadPressure service=checkout-oltp instance=postgresql-primary severity=warning summary=Several I/O windows show lower cache hit and higher reads while one transaction window misses SLO description=Compare the historical I/O context, device queue, workload buckets and transaction p99. Keep all required jobs within their deadlines while controlling the actual source of impact.
- Initial-state fields: `alert`, `required_observation`, `status`, `visible_symptom`
- Expected-target fields: `oltp_slo`, `required_jobs`, `status`, `target_workload`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.io_context_workload.PgResourceGovernanceIoContextWorkloadForReportIsPressureEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): query_metrics=2/2; execute_sql=6/7

### `report_is_pressure_simple`

- Case number: `1`
- Title: A reduced I/O-context case separates a causal workload from read-count noise.
- Alert/symptom: [FIRING: WARNING] alertname=PostgresCacheHitAndReadPressure service=checkout-oltp instance=postgresql-primary severity=warning summary=Two I/O windows raised reads while OLTP p99 missed SLO description=Use I/O time, queue and the application bucket to control the causal workload, then verify the OLTP SLO and every required job without changing their results.
- Initial-state fields: `alert`, `required_observation`, `status`, `visible_symptom`
- Expected-target fields: `oltp_slo`, `required_jobs`, `status`, `target_workload`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.io_context_workload.PgResourceGovernanceIoContextWorkloadForReportIsPressureSimpleEvaluatorCase`
- Calibration evidence (tool m/n): query_metrics=1/1; execute_sql=3/1

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

- Scenario and Case source: `src.scenarios.postgres.resource_governance.io_context_workload.PgResourceGovernanceIoContextWorkloadScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/resource_governance/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_resource_governance_io_context_workload_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
