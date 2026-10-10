---
doc_id: scenario.postgresql.pg_system_failure_temp_file_explosion
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, system_failure, pg_system_failure_temp_file_explosion]
summary: Current code-backed contract snapshot for pg_system_failure_temp_file_explosion; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_system_failure_temp_file_explosion`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `system_failure`
- Scenario implementation: `src.scenarios.postgres.system_failure.temp_file_explosion.PgSystemFailureTempFileExplosionScenario`
- Formal entrypoint: `examples/run_pg_system_failure_temp_file_explosion_scenario.py`
- Current description: Simulates write failures caused by one reporting batch spilling temp files amid normal production noise.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `nightly_margin_temp_exhaustion` | Simulates write failures caused by one reporting batch spilling temp files amid normal production noise. | `hard` |
| 1 | `daily_sales_temp_exhaustion_simple` | One daily sales rollup fills PostgreSQL scratch space beside a same-role retry batch. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `nightly_margin_temp_exhaustion`

- Case number: `0`
- Title: Simulates write failures caused by one reporting batch spilling temp files amid normal production noise.
- Alert/symptom: Alert: PostgreSQLWriteFailuresHigh. Order writes and several scheduled jobs are intermittently failing with storage-related errors, while OLTP reads and monitoring probes still connect normally. Several BI/reporting queries and routine collectors are active on the primary. Identify the production source of the write failures, restore write availability, and prevent the same batch from immediately exhausting scratch s
- Initial-state fields: `noise`, `status`, `symptom`
- Expected-target fields: `culprit_application`, `culprit_job`, `culprit_role`, `required_temp_file_limit`, `status`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.temp_file_explosion.PgSystemFailureTempFileExplosionForNightlyMarginTempExhaustionEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `daily_sales_temp_exhaustion_simple`

- Case number: `1`
- Title: One daily sales rollup fills PostgreSQL scratch space beside a same-role retry batch.
- Alert/symptom: Alert: Scheduled writes fail with a storage-related error while PostgreSQL remains reachable and a low-rate date probe succeeds. A cancelled retry batch uses the same report role and application identity. Identify the active scratch-space consumer by job, restore writes, and prevent that batch from exhausting temp storage again.
- Initial-state fields: `status`, `symptom`
- Expected-target fields: `culprit_application`, `culprit_job`, `culprit_role`, `required_temp_file_limit`, `status`
- Background profiles: date_health_probe
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.temp_file_explosion.PgSystemFailureTempFileExplosionForDailySalesTempExhaustionSimpleEvaluatorCase`
- Calibration ledger: maintained by the Case registry and the [难度标准](../../../standards/scenario/difficulty.standard.md).

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The target rollup and a cancelled retry share the same role and application identity; their stable job markers allow the Agent to distinguish the active scratch-space consumer.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** is the evaluator-owned semantic diagnosis contract for the registered Case. It is independent of repair completion and uses the shared DP protocol.
- **OP** is the evaluator's final-state and business-truth contract. The expected-target fields above identify the state boundary; accepted repairs and equivalent outcomes are defined by the evaluator.
- For the simple Case, OP accepts a predeclared range of safe role-scoped persistent temp limits rather than one reference value. The bounds remain evaluator-internal; the mock uses one accepted value and every value in the interval is accepted.
- **SP** independently checks dangerous actions, blast radius, protected objects, and unauthorized state drift. It is not a replacement for OP.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.postgres.system_failure.temp_file_explosion.PgSystemFailureTempFileExplosionScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/system_failure/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_system_failure_temp_file_explosion_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
