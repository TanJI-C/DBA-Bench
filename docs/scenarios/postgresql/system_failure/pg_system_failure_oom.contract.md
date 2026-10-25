---
doc_id: scenario.postgresql.pg_system_failure_oom
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, system_failure, pg_system_failure_oom]
summary: Current code-backed contract snapshot for pg_system_failure_oom; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
updated: 2026-10-25
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_system_failure_oom`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `system_failure`
- Scenario implementation: `src.scenarios.postgres.system_failure.oom.PgSystemFailureOomScenario`
- Formal entrypoint: `examples/run_pg_system_failure_oom_scenario.py`
- Current description: PostgreSQL process killed by OOM due to memory config exceeding container limit.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `restart_memory_config_oom` | PostgreSQL process killed by OOM due to memory config exceeding container limit. | `hard` |
| 1 | `restart_shared_buffers_oom_simple` | One unsafe shared_buffers override prevents PostgreSQL from serving after restart. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `restart_memory_config_oom`

- Case number: `0`
- Title: PostgreSQL process killed by OOM due to memory config exceeding container limit.
- Alert/symptom: P0 Alert: checkout and BI APIs are returning elevated 5xx errors. Application pools report repeated PostgreSQL connection refused events after the last maintenance restart. The container is still running, but database readiness keeps failing. Nearby telemetry also contains routine report temp-file and checkpoint messages; identify the primary reason PostgreSQL is not serving traffic and repair it.
- Initial-state fields: `container`, `postgres_process`, `status`
- Expected-target fields: `config_fixed`, `status`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.oom.PgSystemFailureOomForRestartMemoryConfigOomEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `restart_shared_buffers_oom_simple`

- Case number: `1`
- Title: One unsafe shared_buffers override prevents PostgreSQL from serving after restart.
- Alert/symptom: P0 Alert: PostgreSQL readiness fails after a maintenance restart while the container remains running. A low-rate calendar health probe was active before the restart. Identify why PostgreSQL is not serving traffic, restore service, and verify the probe query.
- Initial-state fields: `container`, `postgres_process`, `status`
- Expected-target fields: `shared_buffers`, `status`, `work_mem`
- Background profiles: calendar_health_probe
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.oom.PgSystemFailureOomForRestartSharedBuffersOomSimpleEvaluatorCase`
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

- For both Cases, OP opens a fresh login with the Case environment's business database
  and credentials, checks memory settings, and runs the original Case probe on that same
  connection. Agent-session `SET` statements do not establish recovery for new business logins.
- Running `shared_buffers` and its effective next-start configuration must each stay at or
  below `case.safe_shared_buffers` (128MB). A safe pending decrease does not require an extra
  restart. A command-line override retains its PostgreSQL precedence; otherwise the last file
  setting, or the built-in default when no file override remains, determines the next-start value.
- Effective `work_mem` on the fresh business login must stay at or below `case.safe_work_mem`
  (8MB). Database defaults, role-in-current-database defaults, and existing instance-wide repairs
  are accepted according to PostgreSQL precedence. OP does not inspect unrelated logins or
  require a particular configuration source or exact value.
- The `memory_recovery` outcome check records the login identity, running and next-start
  `shared_buffers` in bytes, effective `work_mem` in bytes, and original probe results. Unsafe
  memory settings fail OP before the probe executes; a failed login or business query also fails OP.
- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.postgres.system_failure.oom.PgSystemFailureOomScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/system_failure/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_system_failure_oom_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Fresh-login memory acceptance regressions: `tests/postgres/test_oom_memory_recovery.py`.
  This evaluator correction preserves the fault, alert, DP conditions, reference repair path,
  and visible evidence. Existing registry difficulty calibration and labels are retained.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
