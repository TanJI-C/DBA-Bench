---
doc_id: scenario.postgresql.pg_query_perf_parameter_sniffing
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, query_perf, pg_query_perf_parameter_sniffing]
summary: Current code-backed contract snapshot for pg_query_perf_parameter_sniffing; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_query_perf_parameter_sniffing`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `query_perf`
- Scenario implementation: `src.scenarios.postgres.query_perf.parameter_sniffing.PgQueryPerfParameterSniffingScenario`
- Formal entrypoint: `examples/run_pg_query_perf_parameter_sniffing_scenario.py`
- Current description: Parameterized customer revenue report has regressed for high-volume bind values.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `branch_order_year_skew` | Parameterized customer revenue report has regressed for high-volume bind values. | `hard` |
| 1 | `branch_order_year_skew_simple` | A compact customer revenue lookup regresses for one high-volume bind value. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `branch_order_year_skew`

- Case number: `0`
- Title: Parameterized customer revenue report has regressed for high-volume bind values.
- Alert/symptom: Alert: customer 360 revenue segmentation dashboard latency is unstable. The report is usually fast for smaller historical cohorts, but the January-February 2001 customer segment now exceeds the dashboard SLO and dominates recent topsql mean/max latency. Diagnose the production query path from database evidence and restore the slow dashboard without changing report semantics.
- Initial-state fields: `report`, `status`
- Expected-target fields: `report`, `status`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.query_perf.parameter_sniffing.PgQueryPerfParameterSniffingForBranchOrderYearSkewEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `branch_order_year_skew_simple`

- Case number: `1`
- Title: A compact customer revenue lookup regresses for one high-volume bind value.
- Alert/symptom: Alert: the customer revenue lookup is slow only for the January-February 2001 cohort. The same prepared report is fast for an empty historical cohort. Diagnose the database-side cause and restore the report without changing its result.
- Initial-state fields: `report`, `status`
- Expected-target fields: `report`, `status`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.query_perf.parameter_sniffing.PgQueryPerfParameterSniffingForBranchOrderYearSkewSimpleEvaluatorCase`
- Difficulty: `hard`; per-case calibration values are maintained in the code registry and the scenario catalogs. The alert names only the business symptom; root-cause details are not embedded.
- Path status: `full-score`; measurement status: `measured`; `valid_for_aggregate=true`
- DP/OP/SP: `True` / `True` / `True`; evaluator output and finalization are successful.
- Static `DifficultyCalibration` metadata is not the formal D/C source and is not a path-validity gate. The formal values are maintained by the Case registry and the difficulty standard, derived from the raw full-score reference trace and the main Agent's semantic evidence coding.
- Contract note: the compact report keeps the January-February 2001 versus empty historical cohort semantics while constraining the corresponding date-key ranges in the parameterized SQL. Its simple Case support state uses the Case-owned `idx_aiopsbench_worker_hot_date` partial index for the hot date range; the full Case keeps the original full branch-order support index. Its causal diagnosis uses the evaluator's `parameter sniffing plan mismatch` alias; the reference entrypoint does not rewrite the Case report.

### Formal reference evidence: `branch_order_year_skew_simple`

- Raw path (complete Agent action sequence; full arguments and results remain in the trace): T1 `query_metrics(topsql)` -> error; T2 the repeated `query_metrics(topsql)` -> error; T3 `execute_sql` `pg_stat_statements` query locating the bind-sensitive report -> success; T4 `execute_sql` `pg_prepared_statements` query -> success; T5 `execute_sql` hot-bind `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` -> success; T6 `execute_sql` `SET plan_cache_mode = 'force_custom_plan'` and `DEALLOCATE ALL` repair -> success; T7 `execute_sql` prepare and post-repair EXPLAIN verification, `query_metrics(topsql)` -> error, `execute_sql` prepared-statement verification -> success, then `submit`.
- Compressed logical path: (1) localize the bind-sensitive customer revenue lookup; (2) identify the generic/custom plan mismatch and its hot-bind performance impact; (3) choose `force_custom_plan` as the scoped plan-cache repair decision. Repeated queries, polling, pagination, repair execution, post-repair verification, and submit are excluded from the diagnosis depth.
- Diagnostic window: a roughly 7-second interval read from the reference run's trace metadata.

- Evidence-unit ledger: maintained by the Case registry and the difficulty standard; units are semantic units from the unfiltered trace results (not SQL rows, log lines, metric samples, or tool calls), with no pre-filtered noise and no filled zero values.

- Workload configuration: Case `background_workload=EMPTY_BACKGROUND_WORKLOAD`; `workload_tag=tpcdsx`, `dataset_scale=1`; runner planned metadata was `planned_qps=0`, `profile_count=0`, `seed=0`, `start_phase=after_faults`, `warmup_seconds=0`, `worker_count=0`, and observed background workload was `{}`. The injector's seeded prepared statements and bind executions are lifecycle SQL, not an Agent `workload/operation event` source family.
- Necessary Case compatibility wiring: the simple Case uses `support_index_variant=hot_window_partial` and `idx_aiopsbench_worker_hot_date`, and its diagnosis report uses the evaluator's `parameter sniffing plan mismatch` alias. No fault composition, workload, topology, parameter meaning, intensity, repair space, safety, evaluator, DP, OP, or SP logic was changed.

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
- The query-performance Cases expose a one-physical-core resource reservation for formal runner isolation; the parameter-sniffing simple Case keeps its existing `1 CPU / 512 MB` PostgreSQL container limit. The resource binding records actual Docker cpuset and NUMA evidence and does not change the fault or workload contract.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.postgres.query_perf.parameter_sniffing.PgQueryPerfParameterSniffingScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/query_perf/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_query_perf_parameter_sniffing_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Current validation target: rerun `branch_order_year_skew_simple` through the formal Mock/reference path with `fault_snapshot=off`; the resulting run ID, raw trace, evaluator output, runtime binding, and cleanup artifact are authoritative for path and measurement status.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
