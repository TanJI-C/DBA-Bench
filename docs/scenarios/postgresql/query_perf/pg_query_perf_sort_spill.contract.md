---
doc_id: scenario.postgresql.pg_query_perf_sort_spill
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, query_perf, pg_query_perf_sort_spill]
summary: Current code-backed contract snapshot for pg_query_perf_sort_spill; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_query_perf_sort_spill`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `query_perf`
- Scenario implementation: `src.scenarios.postgres.query_perf.sort_spill.PgQueryPerfSortSpillScenario`
- Formal entrypoint: `examples/run_pg_query_perf_sort_spill_scenario.py`
- Current description: Simulates sort spill to disk due to insufficient work_mem.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `branch_order_sort_spill` | Simulates sort spill to disk due to insufficient work_mem. | `easy` |
| 1 | `branch_order_sort_spill_simple` | Simulates a compact branch-margin ranking spilling its sort to disk. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `branch_order_sort_spill`

- Case number: `0`
- Title: Simulates sort spill to disk due to insufficient work_mem.
- Alert/symptom: Alert: the finance channel revenue report slowed sharply after 10:00. The same monthly channel margin query that usually finishes quickly now runs for much longer, while monitoring shows elevated database read/write I/O during the report window. Identify the cause and provide a verifiable, non-destructive fix. Affected query: /* finance_reporting: top_200_channel_revenue_q3_with_margin_decile */ WITH catalog_revenue
- Initial-state fields: `sort_method`, `status`, `work_mem`
- Expected-target fields: `sort_method`, `status`, `work_mem`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.query_perf.sort_spill.PgQueryPerfSortSpillForBranchOrderSortSpillEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `branch_order_sort_spill_simple`

- Case number: `1`
- Title: Simulates a compact branch-margin ranking spilling its sort to disk.
- Alert/symptom: Alert: the branch margin dashboard's top-20 ranking is slow during the daily close, with elevated database I/O. The result set is small but the aggregation and ordering step takes much longer than usual. Identify the database resource constraint and provide a verifiable, non-destructive fix. Affected query: /* finance_reporting: branch_margin_top_simple */ WITH branch_product_margin AS MATERIALIZED ( SELECT bol_branc
- Initial-state fields: `sort_method`, `status`, `work_mem`
- Expected-target fields: `sort_method`, `status`, `work_mem`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.query_perf.sort_spill.PgQueryPerfSortSpillSimpleEvaluatorCase`
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

- Scenario and Case source: `src.scenarios.postgres.query_perf.sort_spill.PgQueryPerfSortSpillScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/query_perf/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_query_perf_sort_spill_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
