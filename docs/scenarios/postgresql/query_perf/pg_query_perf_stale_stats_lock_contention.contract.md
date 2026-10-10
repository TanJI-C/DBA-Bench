---
doc_id: scenario.postgresql.pg_query_perf_stale_stats_lock_contention
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, pg_query_perf_stale_stats_lock_contention]
summary: Current code-backed contract snapshot for pg_query_perf_stale_stats_lock_contention; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_query_perf_stale_stats_lock_contention`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `query_perf`
- Scenario implementation: `src.scenarios.postgres.query_perf.stale_stats_lock_contention.PgQueryPerfStaleStatsLockContentionScenario`
- Formal entrypoint: `examples/run_pg_query_perf_stale_stats_lock_contention_scenario.py`
- Current description: Simulates stale statistics causing slow active lock holders and downstream lock contention.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `checkout_stale_stats_and_lock` | Simulates stale statistics causing slow active lock holders and downstream lock contention. | `easy` |
| 1 | `checkout_stale_stats_single_waiter_simple` | A focused stale-statistics lock contention case with one slow active holder and one waiter. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `checkout_stale_stats_and_lock`

- Case number: `0`
- Title: Simulates stale statistics causing slow active lock holders and downstream lock contention.
- Alert/symptom: Alert: order-service write requests are intermittently timing out and p95 latency is above SLO. Write throughput is below the normal baseline. Investigate and restore service health.
- Initial-state fields: `lock_holder_state`, `lock_waiters`, `statistics`, `status`
- Expected-target fields: `lock_holder_state`, `lock_waiters`, `required_fix`, `statistics`, `status`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.query_perf.stale_stats_lock_contention.PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsAndLockEvaluatorCase`
- Difficulty: easy; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md).

### `checkout_stale_stats_single_waiter_simple`

- Case number: `1`
- Title: A focused stale-statistics lock contention case with one slow active holder and one waiter.
- Alert/symptom: Alert: checkout writes are timing out and one worker queue is waiting on a lock while a related query is slow. Identify the blocker and restore throughput.
- Initial-state fields: `lock_holder_state`, `lock_waiters`, `statistics`, `status`
- Expected-target fields: `lock_holder_state`, `lock_waiters`, `required_fix`, `statistics`, `status`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.query_perf.stale_stats_lock_contention.PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsSingleWaiterSimpleEvaluatorCase`
- Calibration evidence (tool m/n): query_metrics.active_connections/slow_queries=3/1; execute_sql.pg_stat_user_tables/locks=3/1

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** is the evaluator-owned semantic diagnosis contract for the registered Case. It is independent of repair completion and uses the shared DP protocol.
- **OP** is the evaluator's final-state and business-truth contract. The expected-target fields above identify the state boundary; accepted repairs and equivalent outcomes are defined by the evaluator. The injected waiter sessions are cleared when no session under the waiter application-name prefix is still waiting on a lock (`wait_event_type = 'Lock'`), so the check observes the real lock-wait state instead of mere session existence.
- **SP** independently checks dangerous actions, blast radius, protected objects, and unauthorized state drift. It is not a replacement for OP.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.postgres.query_perf.stale_stats_lock_contention.PgQueryPerfStaleStatsLockContentionScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/query_perf/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_query_perf_stale_stats_lock_contention_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
