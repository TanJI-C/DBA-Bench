---
doc_id: scenario.postgresql.pg_health_check_config_drift
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, health_check, pg_health_check_config_drift]
summary: Current code-backed contract snapshot for pg_health_check_config_drift; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_health_check_config_drift`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `health_check`
- Scenario implementation: `src.scenarios.postgres.health_check.config_drift.PgHealthCheckConfigDriftScenario`
- Formal entrypoint: `examples/run_pg_health_check_config_drift_scenario.py`
- Current description: Simulates a capacity-upgraded PostgreSQL instance whose memory settings still reflect an old baseline.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `memory_resize_config_drift` | Simulates a capacity review where PostgreSQL runtime settings lag behind the current instance profile amid normal operational noise. | `hard` |
| 1 | `cache_baseline_drift_simple` | A focused post-resize audit with two stale cache parameters and one intentional work_mem guardrail. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `memory_resize_config_drift`

- Case number: `0`
- Title: Simulates a capacity review where PostgreSQL runtime settings lag behind the current instance profile amid normal operational noise.
- Alert/symptom: [Routine Fleet Health] The weekly capacity review for pg-primary-17 shows lower cache headroom and throughput elasticity than peers with the same instance class. The window also includes reporting jobs, connection-pool churn, and post-maintenance notes. Inspect the live instance profile and database state, separate actionable baseline variance from normal operational noise, and submit a production-safe change plan wi
- Initial-state fields: `memory_mb`, `postgres_memory_params`, `status`
- Expected-target fields: `drift_identified`, `recommended_params`, `status`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.health_check.config_drift.PgHealthCheckConfigDriftForMemoryResizeConfigDriftEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `cache_baseline_drift_simple`

- Case number: `1`
- Title: A focused post-resize audit with two stale cache parameters and one intentional work_mem guardrail.
- Alert/symptom: [Routine Fleet Review] Cache headroom on a resized PostgreSQL node trails comparable instances. Inspect the live allocation and settings sources, separate intentional concurrency limits from stale cache sizing, and provide a staged change, validation, and rollback plan.
- Initial-state fields: `memory_mb`, `postgres_memory_params`, `status`
- Expected-target fields: `drift_identified`, `recommended_params`, `status`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.health_check.config_drift.PgHealthCheckConfigDriftForCacheBaselineDriftSimpleEvaluatorCase`
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

- Scenario and Case source: `src.scenarios.postgres.health_check.config_drift.PgHealthCheckConfigDriftScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/health_check/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_health_check_config_drift_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
