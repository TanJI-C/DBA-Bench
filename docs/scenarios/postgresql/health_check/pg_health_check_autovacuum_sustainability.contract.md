---
doc_id: scenario.postgresql.pg_health_check_autovacuum_sustainability
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, health_check, pg_health_check_autovacuum_sustainability]
summary: Current code-backed contract snapshot for pg_health_check_autovacuum_sustainability; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_health_check_autovacuum_sustainability`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `health_check`
- Scenario implementation: `src.scenarios.postgres.health_check.autovacuum_sustainability.PgHealthCheckAutovacuumSustainabilityScenario`
- Formal entrypoint: `examples/run_pg_health_check_autovacuum_sustainability_scenario.py`
- Current description: Audits whether PostgreSQL autovacuum cleanup capacity remains sustainable under real churn.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `capacity_deficit` | Hard autovacuum sustainability review with multi-table churn, OLTP and TPC-DS noise. | `hard` |
| 1 | `capacity_deficit_simple` | Easy autovacuum sustainability review with one target, one decoy and one deterministic OLTP profile. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `capacity_deficit`

- Case number: `0`
- Title: Hard autovacuum sustainability review with multi-table churn, OLTP and TPC-DS noise.
- Alert/symptom: [Scheduled PostgreSQL Health Check] The next trading window is expected to increase write volume. Start with the compact metric overview, select one candidate relation/window, then use bounded history queries to review relation maintenance sustainability and prove that the next replay window keeps cleanup bounded without disabling maintenance or degrading OLTP. Change only relations whose repeated completed maintenance cycles prove a sustained deficit; relations that recover within the published replay window are healthy business objects and must remain unchanged. Acceptance uses the latest 8 samples: target backlog growth must be <=300 tuples, effective removal must reach at least 75% of generation, OLTP p99 must be <=6000 ms, and success rate must be >=0.98. From adjacent raw samples, generation is the sum of positive deltas in `n_tup_ins`, `n_tup_upd` and `n_tup_del`. When `last_autovacuum` or `last_vacuum` advances, effective removal is `max(previous n_dead_tup + generation - current n_dead_tup, 0)`; otherwise it is zero. HARD HISTORY BOUNDARIES: first call query_metrics without timestamps for the compact overview; then choose exactly one evidence interval no longer than 900 seconds and use that same interval for the required metrics/logs. Never request a multi-hour explicit window, never retry an identical failed window, and after a history-window error either select a narrower interval or submit the evidence already collected.
- Initial-state fields: `database`, `relation_mix`, `status`, `workload`
- Expected-target fields: `autovacuum`, `backlog`, `oltp_p99_ms`, `status`, `target`
- Background profiles: business_write_01, business_write_02, business_write_03, business_write_04, business_write_05, business_write_06, business_write_07, business_write_08, tpcds_light_q3, tpcds_medium_q2
- Evaluator: `src.scenarios.evaluation.postgres.health_check.autovacuum_sustainability.PgHealthCheckAutovacuumSustainabilityForCapacityDeficitEvaluatorCase`
- Public history: frozen-history history is captured from the live CaseRun before fault activation, then frozen before Agent handoff. It exposes raw `relation_churn`, `vacuum_cleanup`, `dead_tuple_backlog`, `maintenance_io`, `oltp_service`, and `xmin_horizon` on a 2-second grid with 20-second overview; bounded historical records are `operation_event` and `component_log`.
- History geometry: 12-hour visible timeline, 900-second normal capture, 600-second target capture, target age 1,800-10,800 seconds, and two captured-benign relation-churn competitors selected from the real normal capture. The public history contains no diagnosis or derived deficit field, and current-state outcome verification uses the trusted live replay rather than frozen history.
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md).
- Measurement status: `path_status=full-score`, `measurement_status=measured`.
- Trusted acceptance replay: models the announced next write window with `replay_churn_multiplier=3.0` applied to the target relation's post-baseline churn batch; live churn, normal/target capture, decoys, history geometry and query budgets are unchanged. OutcomePass `target_controlled` requires a bounded per-relation capacity increase on the diagnosed target (`autovacuum_enabled=true` plus target reloptions leaving the configured baseline), so no-op, wrong-target and global repairs cannot pass.
- Diagnostic window: the reference evidence queries use a bounded 900-second interval over the visible tail, where the persistent target deficit state remains visible; the frozen target window truth is `2026-09-14 17:36:10` through `2026-09-14 17:39:08` UTC.
- Raw path: `T1 overview relation_churn/dead_tuple_backlog/maintenance_io`; `T2 target-window relation_churn/vacuum_cleanup/dead_tuple_backlog, operation_event history, component_log history, and reloptions for all eight relations`; `T3 target-scoped ALTER TABLE repair followed by VACUUM`; `T4 sleep, repeat VACUUM, workload_activity, final catalog read, and submit`.
- Compressed path: (1) establish the eight-relation long-window candidate set and normal/target windows; (2) jointly compare churn generation, vacuum cleanup, and dead-tuple backlog across windows; (3) use operation-event, component-log, and reloptions context to confirm a target-specific sustained deficit and exclude healthy neighbors/static shortcuts; (4) choose a target-only bounded cleanup-capacity repair while preserving autovacuum.
- Depth accounting: repeated queries, polling, pagination, repair execution, repair-after verification, and submit are excluded from the diagnosis depth.
- Evidence-unit ledger: maintained by the Case registry and the difficulty standard; units are semantic units from the unfiltered trace results, with no pre-filtered noise and no filled zero values.
  `metric` causal units are target churn generation, target cleanup shortfall, target backlog growth, and target-specific neighbor contrast; its noise units are the normal relation regime, healthy-neighbor comparison set, the captured healthy-target burst, the captured healthy-neighbor burst, and maintenance-I/O context. The `log` result contained observer query-log context but no usable automatic-vacuum causal record, so it contributes one semantic noise unit and no causal unit. The `SQL/catalog` causal unit is the target's ordinary/shared reloptions context; the seven protected-neighbor comparison context is noise. The `operation_event` window returned no completed vacuum event, which is observable negative evidence and one causal unit, not a fabricated zero or a mechanically counted empty result.
- Overall complexity: `C = (12 + 34 + 15) / (15 + 41 + 19) = 61/75 = 0.813333`.
- Workload: ten live profiles (`business_write_01` through `business_write_08`, `tpcds_light_q3`, `tpcds_medium_q2`), planned QPS `0.81`, `worker_count=3`, workload seed `44801` (`0xAF01`), history seed `20260914`, `start_phase=before_faults`, warmup `5s`; all ten profiles ran during the CaseRun normal/target captures, and the retained injector churn plus pgbench drive the trusted replay.
- History/runtime evidence: live frozen-history history SHA-256 `051344f41cf3070e8d7fb3f4557683f6ac58281929605b1fe9672aa2ced0c5a8`; visible range `2026-09-14 08:06:32` through `2026-09-14 20:06:30` UTC; normal capture `20:01:28`-`20:03:28`; target capture `20:03:30`-`20:06:30`; target window truth `17:36:10`-`17:39:08` with four decoys adjacent before it (`healthy-target-burst`, `metric-only-backlog-wave`, `metric-only-cleanup-wave`, `healthy-neighbor-burst`); `missing_sample_count=0`, `generated_sample_count=353965` (post-target plateau retention plus 60 metric-only decoy samples), `point_count=583200`, `metric_only_sample_count=60`. No frozen staging SQL or fabricated metric was used.
- `DifficultyCalibration` is metadata only: its `diagnostic_depth` agrees with this trace audit, while its legacy causal/noise evidence-unit fields are not used to compute the family-weighted complexity; missing calibration/tool-evidence/source-ledger metadata is not a path validity failure.

### `capacity_deficit_simple`

- Case number: `1`
- Title: Easy autovacuum sustainability review with one target, one decoy and one deterministic OLTP profile.
- Alert/symptom: [Scheduled PostgreSQL Health Check] One relation is accumulating cleanup work during a predictable write profile. Compare the target with the decoy, apply only a bounded target-level control, and verify the next write window.
- Initial-state fields: `relation_mix`, `status`, `workload`
- Expected-target fields: `autovacuum`, `backlog`, `oltp_p99_ms`, `status`, `target`
- Background profiles: pgbench_oltp_target_simple
- Evaluator: `src.scenarios.evaluation.postgres.health_check.autovacuum_sustainability.PgHealthCheckAutovacuumSustainabilityForCapacityDeficitSimpleEvaluatorCase`
- Difficulty: hard; D=3, C=0.678571, reference=pending_pg_hc_mf01_capacity_deficit_simple_reference
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

- Scenario and Case source: `src.scenarios.postgres.health_check.autovacuum_sustainability.PgHealthCheckAutovacuumSustainabilityScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/health_check/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_health_check_autovacuum_sustainability_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
