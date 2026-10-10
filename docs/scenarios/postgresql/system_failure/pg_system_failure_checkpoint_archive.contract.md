---
doc_id: scenario.postgresql.pg_system_failure_checkpoint_archive
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, pg_system_failure_checkpoint_archive]
summary: Current code-backed contract snapshot for pg_system_failure_checkpoint_archive; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_system_failure_checkpoint_archive`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `system_failure`
- Scenario implementation: `src.scenarios.postgres.system_failure.checkpoint_archive.PgSystemFailureCheckpointArchiveScenario`
- Formal entrypoint: `examples/run_pg_system_failure_checkpoint_archive_scenario.py`
- Current description: Simulates independent checkpoint pressure and archive throughput loss with joint replay and PITR validation.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `checkpoint_archive_dual_fault` | PostgreSQL 16 checkpoint pressure and archive throughput fail together. | `hard` |
| 1 | `checkpoint_archive_dual_fault_simple` | A shorter checkpoint/archive dual-fault window with one write job and one archive target. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `checkpoint_archive_dual_fault`

- Case number: `0`
- Title: PostgreSQL 16 checkpoint pressure and archive throughput fail together.
- Alert/symptom: [CRITICAL] Historical checkout traffic showed recurring latency spikes while WAL headroom narrowed and the recovery objective was at risk. Read the compact metric overview first, select one candidate window, then use bounded history queries before applying bounded workload or recovery-capacity changes; never scan the full history. Preserve durability, do not restart the primary, and do not stop all writes. The current service is quiet. Prove the next mixed write/report/backup window is safe.
- Initial-state fields: `authorization`, `status`, `symptoms`
- Expected-target fields: `pitr`, `replay`, `status`, `write_control`
- Background profiles: checkpoint_archive_oltp, checkpoint_archive_tpcds_report, checkpoint_archive_tpcds_report_secondary, checkpoint_archive_normal_wal_burst
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.checkpoint_archive.PgSystemFailureCheckpointArchiveForDualFaultEvaluatorCase`
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md).
- Calibration evidence (tool m/n, from the reference trace's decisive results): query_metrics.seven_series_overview=5/2; read_log.operation_event.job_batch_normal_window=50/45; read_log.operation_event.archive_attempt_baseline_windows=0/22; execute_sql.current_registry_and_binding_surfaces=2/2. Counting units: metric series per overview result; operation-event rows per bounded-window result (returned rows under the declared limit); current-state result rows per control surface.
- Information boundary: the hard Case applies the same boundary as the simple Case — the current-state control tables `warehouse_refresh_controls`, `archive_transfer_policy`, and `archive_transfer_limits` publish only their active values (`publish_safe_profiles=False`); no safe-value comparison exists in current state. `archive_endpoint_storage_limits.safe_spare_mb` remains public as the spare-capacity rule. The healthy batch cadence (refresh 120 rows/750ms; maintenance 40 rows/1000ms) is observable only as frozen-history `job_batch` operation events in the normal capture window (`run_healthy_workload_in_normal_capture=True`). The published CHECK bounds (1..800, 10..5000, 1..120, 0..5000) stay public; the acceptance intervals are evaluator-internal and not restated in agent-visible text.
- Public history: the hard Case captures the declared live normal and target windows from the CaseRun before Agent handoff, then freezes those observations. The history exposes raw checkpoint, WAL, archive, storage, service-SLO, batch-progress, and bounded operation-event evidence; it does not add a derived diagnosis field.
- Reference path (pi_s): alert (quiet incident, historical latency spikes, WAL headroom and recovery risk) → compact overview and candidate windows (bounded overview budget plus public help runtime boundaries) → bounded-window metric correlation for both chains (WAL/FPI→requested checkpoints→device queue→OLTP p99; delivery<generation→retries→backlog→`pg_wal`) → writer attribution by comparing normal-window `job_batch` healthy cadence (120/750) against the fault cadence (800/250) → exclusion of metric-only and captured-benign decoy windows plus binding/route coherence checks → current-state mapping onto the concrete control rows, transfer policy/limit, repository quota (`496+256=752`), and route-generation mismatch → root cause and bounded targeted repair, with migration of the active binding to the healthy neighbor as the equivalent repair.
- Contract note: hard acceptance replays the declared bounded `q75` report profile used by the live hard workload; the `checkpoint_archive_dual_fault_simple` Case replays its declared `q3` profile. The report replay remains part of joint OutcomePass. The captured-benign hard report decoy uses the real normal-window `service_slo.transactions_per_sec` field because its p99 field may be flat on a low-CPU worker.
- Lifecycle note: teardown reads the required `checkpoint_archive_oltp` p99 field from the declared live observation profile before stopping the sampler. A missing field is an observation-contract error; it is not replaced with a default value and does not change the fault or outcome contract. Recovery drops the task-owned write table by design; the history adapter reports zero rows for the dropped relation instead of failing the sampler stop path.
- Path status: `full-score`; measurement status: `measured`; `valid_for_aggregate=true`; `DP/OP/SP=True/True/True`.
- Workload and window: four live profiles (`checkpoint_archive_oltp`, `checkpoint_archive_tpcds_report`, `checkpoint_archive_tpcds_report_secondary`, `checkpoint_archive_normal_wal_burst`), `worker_count=1`, `start_phase=before_faults`, warmup `2s`. Frozen history visible window `2026-09-15T03:17:24Z`-`2026-09-15T15:17:22Z` (43198s, base step 2s, overview 300s); normal capture `15:11:54Z`-`15:13:54Z` with healthy-cadence `job_batch` events (refresh 120/750, maintenance 40/1000); target window `12:55:50Z`-`12:58:48Z` (178s, end age 8314s); decoys at `10:26:50Z`-`10:32:08Z` (normal OLTP wave, backup read, metric-only checkpoint wave, report I/O, metric-only archive wave). History hash `2b3bee46af9bf5ea3200955ff7df148564d5a9b6b0d47fac8dd1dacc32ac03ef`; generated/missing/metric-only samples `104199/0/60`.
- Pre-mock startup stages for the reference run: deploy `49.1s`, environment and workload start `76.6s`, warmup `80.6s`, normal capture `200.3s`, target capture `398.4s`, history assembly and validation `423.0s`. The reference/mock run reports `DP/OP/SP=True/True/True` with joint replay, two physical backups, marker PITR, and archive convergence all true; zero-mode keeps SP failing.
- Validation evidence: focused tests in `tests/postgres/test_checkpoint_archive_scenario.py` cover the unpublished-safe-profile boundary for both cases, the healthy-workload normal capture for both cases, hard state-helper acceptance shapes, the recovery drop tolerance of the history adapter, full-history scan rejections at both window budgets, and the entrypoint model contract.

### `checkpoint_archive_dual_fault_simple`

- Case number: `1`
- Title: A shorter checkpoint/archive dual-fault window with one write job and one archive target.
- Alert/symptom: [SEV2] Recent OLTP writes showed short latency spikes and the recovery objective is at risk during the next mixed workload window. Read the compact metric overview first, select one candidate window, then use bounded database and business-workload controls within the published incident scope; never scan the full history. Do not disable durability, delete recovery data, restart the primary, or change unrelated jobs. The incident is currently quiet. Investigate the historical evidence, restore safe operation, and prove recovery with a small repeatable replay.
- Initial-state fields: `status`, `symptom`, `scope`
- Expected-target fields: `pitr`, `replay`, `status`, `write_control`
- Background profiles: checkpoint_archive_oltp, checkpoint_archive_tpcds_report_simple, checkpoint_archive_tpcds_catalog_report
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.checkpoint_archive.PgSystemFailureCheckpointArchiveForDualFaultSimpleEvaluatorCase`
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md).
- Calibration evidence (tool m/n, from the reference trace's decisive results): query_metrics.seven_series_overview=5/5; read_log.operation_event.job_batch_normal_window=19/73; read_log.operation_event.archive_attempt_target_window=11/5; execute_sql.current_control_and_binding_surfaces=3/3. Counting units: metric series per overview result; operation-event rows per bounded-window result (returned rows under the declared limit); current-state result rows per control surface.
- Mechanism: two physical chains share one target window. The governed write job `warehouse_refresh_simple` runs its incident profile (800 rows/batch, 250ms pause, 128KB payload) through the whole window, driving WAL/FPI growth, requested checkpoints, device queue pressure, and OLTP p99 spikes; from +90s into the window the archive side is squeezed (transfer policy and limit throttled to 24 segments/min with 2500ms pauses, repository quota cut to 512MB so `available_mb=16` falls below the published 256MB spare rule, and the active route generation drops to 16 against registry/state 17), producing delivery retries, backlog, `pg_wal` growth, and PITR risk.
- Information boundary: the current-state control tables `warehouse_refresh_controls`, `archive_transfer_policy`, and `archive_transfer_limits` publish only their active values (`publish_safe_profiles=False`); no safe-value comparison exists in current state. `archive_endpoint_storage_limits.safe_spare_mb` remains public as the spare-capacity rule. The healthy batch cadence (refresh 1 row/5000ms; maintenance 40 rows/1000ms) is observable only as frozen-history `job_batch` operation events in the normal window (`run_healthy_workload_in_normal_capture=True`). The healthy neighbor job must survive the repair (`protect_unrelated_job_profile=True`): joint OutcomePass additionally requires artifact key `maintenance_control_unchanged_pass`.
- Bounded-window contract (no new tools; shared frozen-history layer): record queries wider than `max_history_query_seconds=1200` fail with an explicit budget error; explicit metric windows above `max_points_per_series=2000` on the 2s base grid fail with a point-budget error; both budgets are surfaced through the tools' help runtime block.
- Reference path (pi_s): alert (quiet incident, historical latency spikes, recovery risk) → h1 overview and candidate windows (target plus four decoys) → h2 same-window dual-chain attribution batch over mutually independent queries (writer cadence by comparing target-window `job_batch` profiles (800/250) against normal-window profiles (1/5000); archive attribution from same-window delivery retries and backlog appearing after the in-window throttle point; exclusion of metric-only checkpoint/qps/archive bursts (no matching records) and the captured read burst (no write-path consequence); current-state mapping onto the concrete control rows, transfer policy/limit, repository quota, and route-generation mismatch) → c_s root cause (writer cadence drift plus archive throttle/quota/route squeeze) and bounded targeted repair.
- Public history: visible window `2026-09-14T13:49:34Z`-`2026-09-14T19:49:32Z` (21600s, base step 2s, overview 300s); normal capture `19:44:16Z`-`19:46:16Z`; target window `19:06:06Z`-`19:09:04Z` (178s, end age 2428s); decoy windows metric-only-checkpoint-burst `16:00:30Z`, metric-only-qps-burst `16:01:50Z`, metric-only-archive-burst `16:03:10Z`, captured-read-burst `16:04:30Z` (captured benign). Seed `13570050`; history hash `38a7b4e57609ac9a29bef9a27621ee0c0f3e083fb6bf16fa7140aca306d379ff`; generated/missing/metric-only samples `35429/0/90`; operation events `17958`.
- OP acceptance intervals (evaluator-internal bounds, not republished to the Agent): write profile `batch_rows<=1 AND pause_ms>=5000` — the CHECK bounds (1..800, 10..5000) make this the single safe point, equal to the historical healthy profile; archive policy and limit `max_segments_per_minute>=120 AND pause_ms<=0` — the published CHECK capacity bound, i.e. remove the throttle entirely; repository `available_mb>=256` with `safe_spare_mb` unchanged — quota `496+256=752`; route/binding generations coherent with a valid lease, or an equivalent migration of the active binding to the healthy neighbor. These bounds are not restated in agent-visible text because the frozen-history evidence plus the published CHECK bounds determine them.
- Runtime and startup evidence: pre-mock stages for the reference run — deploy `135.1s`, environment and workload start `200.4s`, warmup `204.4s`, normal capture `323.7s`, target capture `519.7s`, history assembly and validation `521.2s`; reference/mock run reports `DP/OP/SP=True/True/True` with joint replay, two physical backups, marker PITR, and archive convergence all true.
- Validation evidence: focused tests in `tests/postgres/test_checkpoint_archive_scenario.py` cover the unpublished-safe-profile boundary (hard publishes, simple does not), the protected neighbor job OP key, simple state-helper acceptance shapes, full-history scan rejections at both window budgets, and the entrypoint model contract.

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

- Scenario and Case source: `src.scenarios.postgres.system_failure.checkpoint_archive.PgSystemFailureCheckpointArchiveScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/system_failure/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_system_failure_checkpoint_archive_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
