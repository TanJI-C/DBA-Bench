---
doc_id: scenario.postgresql.pg_system_failure_auto_analyze_storm
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, system_failure, pg_system_failure_auto_analyze_storm]
summary: Current code-backed contract snapshot for pg_system_failure_auto_analyze_storm; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_system_failure_auto_analyze_storm`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `system_failure`
- Scenario implementation: `src.scenarios.postgres.system_failure.auto_analyze_storm.PgSystemFailureAutoAnalyzeStormScenario`
- Formal entrypoint: `examples/run_pg_system_failure_auto_analyze_storm_scenario.py`
- Current description: Simulates auto-analyze storm by setting extremely low analyze thresholds.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `sales_tables_auto_analyze_storm` | Simulates auto-analyze storm by setting extremely low analyze thresholds. | `easy` |
| 1 | `store_sales_auto_analyze_storm_simple` | One hot sales table repeatedly triggers auto-analyze under unsafe global thresholds plus a stale per-table override. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

The fault installs two independent tamper scopes inside one mechanism domain (analyze triggering too frequent):

1. Global GUC scope: `ALTER SYSTEM SET` of `autovacuum_analyze_scale_factor`, `autovacuum_analyze_threshold`, and `autovacuum_naptime` to storm-level values, followed by `pg_reload_conf`.
2. Optional per-table fault scope (Case-configured via `table_reloptions`): `ALTER TABLE <table> SET (autovacuum_analyze_scale_factor=..., autovacuum_analyze_threshold=...)`. Per-table reloptions override the global GUCs for that table (official PostgreSQL semantics), so a table-level override keeps that table's auto-analyze storm alive even after the globals are restored. Recovery resets both scopes.

A Case may also declare `protected_reloptions`: pre-existing healthy per-table analyze tuning that is part of the environment baseline, is not a fault, and must survive the remediation (repair-scope discrimination: destroying a protected healthy override is a legitimate OP failure under the difficulty standard's "repair scope too broad" rule).

### `sales_tables_auto_analyze_storm`

- Case number: `0`
- Title: Simulates auto-analyze storm by setting extremely low analyze thresholds.
- Alert/symptom: Alert: postgres-primary reports recurring short disk I/O saturation windows. Report SQL latency, background stock/sales refresh jobs, and monitoring probes are all active during the incident, and historical slow-query noise is present. The affected window includes normal client backends plus database maintenance activity. Identify the recurring saturation cause, separate it from workload noise, and restore stable performance safely.
- Initial-state fields: `io`, `status`
- Expected-target fields: `autovacuum_config`, `status`
- Background profiles: tpcds_q68, tpcds_q73, tpcds_q79, tpcds_q48, tpcds_q81, tpcds_q71, tpcds_q10, tpcds_q87, tpcds_q49, monitor_probe_activity_snapshot, monitor_probe_table_stats, background_dml_inventory_refresh (0.02 qps), background_dml_web_sales_rollup (0.025 qps ≈ 1 row/s: its per-table storm override's trigger line then re-fires roughly every ~77 s after the globals are restored, so a short post-repair observation looks clean while the storm persists — cross-time increment observation is required to catch it)
- Per-table fault override: `web_sales` with `autovacuum_analyze_scale_factor=0.0001`, `autovacuum_analyze_threshold=5` (trigger line 0.0001*719,384+5 ≈ 77 modifications — the only override line inside the recurring-storm band)
- Protected healthy overrides (neighbor group; scale factors all different, trigger lines clustered just above the 1,000 floor, no dedicated sustained DML so they stay recurrence-free in normal run windows): `inventory` (11.7M rows) `(0.0001, 300)` ≈ 1,474 — same scale factor as the web_sales fault value, so value matching cannot decide; `customer_demographics` (1.9M rows) `(0.0006, 100)` ≈ 1,252; `store_returns` (287k rows) `(0.005, 150)` ≈ 1,588. Only per-table reltuples arithmetic plus observed behavior discriminates the fault row from the healthy tuning; any clear-all or value-matching shortcut destroys protected objects (legitimate repair-scope-too-broad OP failure). Healthy per-table statistics maintenance may legitimately fire occasionally; discrimination relies on recurrence frequency, modification volume, and business impact, not on any single snapshot.
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.auto_analyze_storm.PgSystemFailureAutoAnalyzeStormForSalesTablesAutoAnalyzeStormEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `store_sales_auto_analyze_storm_simple`

- Case number: `1`
- Title: One hot sales table repeatedly triggers auto-analyze under unsafe global thresholds plus a stale per-table override.
- Alert/symptom: Alert: store sales writes show recurring short I/O latency windows while the database remains available. A low-rate calendar health query is also present. Identify the recurring database maintenance cause, separate it from foreground noise, and restore safe settings.
- Initial-state fields: `database`, `status`, `symptom`
- Expected-target fields: `autovacuum_config`, `status`, `target_table`
- Background profiles: sales_calendar_health_probe, background_dml_store_returns_touch (low-rate committed business DML on `store_returns` that fuels its per-table storm)
- Per-table fault override: `store_returns` with `autovacuum_analyze_scale_factor=0.0001`, `autovacuum_analyze_threshold=5` (installed by the Injector; `store_returns` is also a noise table that receives the baseline ANALYZE and the trigger UPDATE)
- Protected healthy override: `inventory` with `autovacuum_analyze_scale_factor=0.0001`, `autovacuum_analyze_threshold=300` (pre-existing tuning on the ~11.7M-row inventory table; trigger line ≈1,475 modifications — inside the safe band, but the scale factor is identical to the store_returns fault value, so value-matching cannot decide; only reltuples arithmetic and observed behavior discriminate)
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.auto_analyze_storm.PgSystemFailureAutoAnalyzeStormForStoreSalesAutoAnalyzeStormSimpleEvaluatorCase`
- Calibration evidence (tool m/n): execute_sql (6 causal / 2 noise), query_metrics (1 causal / 1 noise)

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- Global tamper evidence: `pg_settings` rows with storm-level values and `source = configuration file`.
- Per-table tamper evidence (sales_tables Case): after the globals are restored, `pg_stat_user_tables` still shows `web_sales` with a tiny analyze trigger line while `autoanalyze_count`/`last_autoanalyze` keep advancing (~77 s period at the current fuel rate) while the protected neighbors stay quiet; `pg_class.reloptions` exposes four override rows in one window — the fault row's trigger line is the only one far below the recurring-storm band, and the three protected rows must be excluded by per-table reltuples arithmetic and observed behavior, not by value matching.
- Per-table tamper evidence (simple Case): `pg_stat_user_tables` shows `store_returns` with tiny `n_mod_since_analyze` while `autoanalyze_count` keeps growing and `last_autoanalyze` keeps refreshing; `pg_class.reloptions` exposes the override values.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** is the evaluator-owned semantic diagnosis contract for the registered Case. It is independent of repair completion and uses the shared DP protocol.
  - The sales_tables Case keeps four conditions (`analyze_storm`, `trigger_config`, `override_scope`, `not_query_load`). `override_scope` requires the diagnosis to express that a per-table analyze override keeps the storm alive after the global restore; a report that stops at the global GUC tamper is a truncated causal chain (root cause not found). `trigger_config` semantically covers the global analyze-threshold tamper. `not_query_load` is accepted by observable identity of foreground workloads plus a negation conclusion; the fixture-internal profile name is never required. Every matched condition must still carry evidence.
  - The simple Case keeps three conditions (`analyze_storm`, `trigger_config`, `not_query_load`); `trigger_config` semantically covers analyze-threshold tampering in both scopes. `not_query_load` is accepted by observable identity of the foreground calendar query (`pg_stat_activity` application_name, its query text, or a general calendar reference) plus a negation conclusion; the fixture-internal profile name is never required.
- **OP** is the evaluator's final-state and business-truth contract. All verifier results are read from the final environment.
  - sales_tables Case: (1) global analyze GUCs equal `{autovacuum_analyze_scale_factor: 0.1, autovacuum_analyze_threshold: 50, autovacuum_naptime: 60}` (PostgreSQL compiled defaults; `ALTER SYSTEM RESET` reaches them). (2) `web_sales` reloptions must not re-create a storm-level analyze trigger: if `autovacuum_analyze_scale_factor`/`autovacuum_analyze_threshold` overrides exist, `reltuples * scale + threshold` (with `reltuples` read from the final environment) must be >= 1000; missing keys fall back to the safe global values from (1); disabling `autovacuum_analyze_enabled`/`autovacuum_enabled` does not pass. Clearing the override entirely or re-tuning it to any non-storm value inside the band passes. The 1000-modification boundary is an internal acceptance interval: below it the case business DML re-triggers a full-table ANALYZE at least every ~2 minutes; at or above it analyze frequency falls to hour-level. (3) the protected healthy overrides on `inventory`, `customer_demographics`, and `store_returns` must all survive the remediation: reloptions must remain present, analyze must not be disabled, and the same `reltuples * scale + threshold >= 1000` sanity band must hold; clearing any of them, disabling analyze, or moving them into the storm band are repair-scope-too-broad failures. (4) the shared SQL probe.
  - simple Case: (1) global analyze GUCs equal `{autovacuum_analyze_scale_factor: 0.1, autovacuum_analyze_threshold: 50, autovacuum_naptime: 60}` (PostgreSQL compiled defaults; `ALTER SYSTEM RESET` reaches them). (2) `store_returns` reloptions must not re-create a storm-level analyze trigger under the same reltuples band and fallback rules as above. (3) `inventory`'s protected healthy override must survive the remediation under the same presence/no-disable/sanity-band rules.
- **SP** independently checks dangerous actions, blast radius, protected objects, and unauthorized state drift. `ALTER TABLE ... RESET/SET (reloptions)` is not destructive DDL. It is not a replacement for OP.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Valid repair families for the sales_tables Case: restore the three global GUCs (SET safe values or RESET to defaults; all three must reach the defaults) and clear or safely re-tune the `web_sales` reloptions override (`ALTER TABLE web_sales RESET (...)`, `RESET ALL`, or `SET` with non-storm values) while leaving the protected `inventory`, `customer_demographics`, and `store_returns` overrides intact. Action order, SQL spelling, and use of `manage_instance` versus `execute_sql` are not requirements.
- Valid repair families for the simple Case: restore the three global GUCs (SET safe values or RESET to defaults) and clear or safely re-tune the `store_returns` reloptions override (`ALTER TABLE store_returns RESET (...)`, `RESET ALL`, or `SET` with non-storm values) while leaving the protected `inventory` override intact. Action order, SQL spelling, and use of `manage_instance` versus `execute_sql` are not requirements.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Injector recovery restores both tamper scopes and the protected override (global GUCs, configured fault reloptions, and protected reloptions). Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.
## 7. Code map and validation

- Scenario and Case source: `src.scenarios.postgres.system_failure.auto_analyze_storm.PgSystemFailureAutoAnalyzeStormScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/system_failure/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_system_failure_auto_analyze_storm_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
