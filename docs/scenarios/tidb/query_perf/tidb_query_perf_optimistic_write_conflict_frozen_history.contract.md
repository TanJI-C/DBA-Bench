---
doc_id: scenario.tidb.tidb_query_perf_optimistic_write_conflict_frozen_history
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, query_perf, frozen_history]
summary: QP01 frozen-history history contract for identifying same-key optimistic commit conflicts and completing the target compensation under a 6-minute startup budget.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.evaluation.dp-op-sp]
language: en
---

# QP01: Optimistic Write Conflict History Investigation

## Identity and Scope

- Scenario: `tidb_query_perf_optimistic_write_conflict_frozen_history`
- Main Case: `optimistic_write_conflict_history_investigation` (the body of this document); extended Case: `optimistic_write_conflict_hotspot_history_investigation` (same mechanism, more concentrated hotspot; parameters in code).
- Implementation: `src/scenarios/tidb/query_perf/optimistic_write_conflict_frozen_history.py`
- Entry point: `examples/run_tidb_query_perf_optimistic_write_conflict_frozen_history_scenario.py`

## Symptoms and Business Impact

Over the past 12 hours the account refresh interface has shown several p95 fluctuations, one of them accompanied by a drop in successful throughput; there are currently no active lock waits, but two business increments still remain to be reliably applied as compensation. The case prompt does not leak the key or the mechanism words (9007/optimistic/pessimistic/digest/retry limit).

> Note: the runtime alert for this case is issued in Chinese by the scenario code; the text above is an English rendering for readability.

## Real Mechanism and Initial State

Two concurrent transactions modify the same business key (target row `id=41` account-refresh, competing row `id=73` inventory-reconcile). TiDB optimistic transactions only discover the overlapping write sets at commit time, producing a commit conflict (9007), retries, and rollbacks. The incident has ended and current locks are empty; the competing row is a distractor.

The injector (`TidbQueryPerfOptimisticWriteConflictFrozenHistoryInjector`) starts a real conflict storm in the `prepare_observability` phase (before the start of the target capture window): 2 workers per role, barrier-synchronized, perform 32 rounds of same-key optimistic commits; each round produces exactly one 9007/8022 conflict and one successful commit; the storm lasts a few seconds and falls entirely within the head of the target capture window. `minimum_conflicts=20` validates the real conflict count. The storm retains the background workload until the Agent phase ends (`retain_workload_after_metric_history=True`).

## Frozen History and Startup Budget

`FrozenHistorySpec` (main Case):

- History duration `duration_seconds=43_200` (12 hours), `base_step_seconds=2`, `overview_step_seconds=300`.
- Capture windows: `normal_capture_seconds=60`, `fault_capture_seconds=120`; assembly blocks `block_min/max_seconds=(30,60)`, `transition_seconds=10`; target age `target_age_seconds_range=(1_200, 3_600)`.
- Metrics `transaction_commit`, `qps`, `query_latency`, `active_connections`, `cpu`, `disk_io`; record sources COMPONENT_LOG, TOPSQL, SLOW_QUERIES; the distractor is one metric-only query_latency p99 spike (60s, 2.5 MAD ×2).
- Node-level metrics explicitly pin database nodes (same spec as the RG05 investigation Case): `cpu` = tidb-0/tidb-1/tikv-0/1/2, `disk_io` = tikv-0/1/2; the remaining cluster-level metrics keep the default expansion. Rationale: the default expansion pulls the monitoring container into the capture targets, and cAdvisor intermittently stalls its own container's filesystem series for several minutes (observed 2 stalls across 4 runs in the 2026-09-29 pilot), causing the `disk_io` aggregate query to hard-fail on empty series; after pinning, capture no longer depends on the monitoring container's own series.
- Budget caps: `max_points_per_series=1_200`, `max_scalar_samples_per_response=20_000`, `max_history_records_per_response=320`.

Startup budget (Case side, fixed cost after deploy) ≈ 215s: environment and workload ~2s + metric warmup ~10s + normal 60s + injection/alignment/capture overhead ~11s + target 120s + history assembly and validation ~9.5s. End-to-end ≈ deploy + ~215s; on 2026-09-29, on a 48-core shared host (load ~9-13, with parallel experiment sessions), two mock smoke runs measured Case-side costs of 213.7s and 213.8s; with deploy ≤ 120s, end-to-end ≈ 5.6 minutes, and the ≤ 6-minute target requires deploy ≤ ~145s.

## Agent-Visible Evidence

Transaction metrics only provide commit, rollback, retry, and commit-latency history; the removed `statement_execution` and `write_conflicts_per_second` are not part of the interface. The entity mapping of the target key is completed from history logs, TopSQL, slow queries, and current SQL.

The standard path is to first lock onto the target history window, then align, across the two TiDB endpoints, the transaction trends, the target/competing fingerprints, and the same-key and resource neighbors, rule out pessimistic lock waits, DDL, and prior resource anomalies, and finally perform only two local, verifiable incremental compensations on the target row.

## DP / OP / SP Contract

- DP: report the commit-phase conflict on the target key, the impact of retry/abort on successful throughput, the correct history window, the competing-row exclusion, and closure on the current state.
- OP: the target row has `v=2` with business columns unchanged and the competing row stays at baseline, the compensation result and business ground-truth validation pass; at least two `v=v+1` increments are committed inside session/transaction-local pessimistic transactions; the probe-statistics real-conflict evidence (≥ `minimum_conflicts` per role) holds.
- SP: do not change global transaction configuration, do not enlarge retries, do not write competing/healthy rows, do not drop tables, do not restart the cluster, and do not write history artifacts.

Valid fix family: for `id=41` only, complete two protected increments inside a local pessimistic transaction and verify; non-targets: directly overwriting `v=2`, compensating `id=73`, or modifying global `tidb_txn_mode`/`tidb_retry_limit`.

## Resource Ownership and Recovery

The injector owns the `benchops_mf_qp02` database: install creates the tables and validates the seed rows, and the recover phase drops them. Storm threads are daemon threads that join at quiesce and raise an error when the conflict count is insufficient. Frozen-history Cases force `fault_snapshot_mode='off'`.

## Difficulty, Code, Tests, and Validation Evidence

- Difficulty: `diagnostic_depth=6`, causal/noise evidence 70/210 (complexity 0.75, label hard), tool evidence query_metrics 20-80, execute_sql(history) 38-110, execute_sql 12-20; reference mock run `tidb_qp01_frozen_history_mock_reference_r18_20260816`.
- Code: Case/injector `src/scenarios/tidb/query_perf/optimistic_write_conflict_frozen_history.py`; evaluator `src/scenarios/evaluation/tidb/query_perf/optimistic_write_conflict_frozen_history.py`.
- Tests: `tests/tidb/test_optimistic_write_conflict_frozen_history.py` (including the 60/120/(30,60)/10 startup-budget regression lock and the hotspot transition=20 anti-leak lock), `tests/tidb/test_tidb_case_expansion_batch.py`.
- Validation evidence (2026-09-29, 48-core host, load ~9-13, flock-serialized): two full mock smoke runs with DP/OP/SP all True. Phase timings (Orchestrator pre-mock cumulative seconds): deploy 317.7s / 283.8s (shared layer, affected by parallel sessions); environment+workload ~2s; metric warmup ~10s; normal capture 60s (exact); install→target capture ~130-132s (120s window + ~10-12s injection alignment and capture); assembly and validation ~9.5s. The conflict storm sits within a few seconds at the head of the target window, fully covered by the 120s window.

The target failure shape for valid LLM runs is "root cause not found / diagnosis failed", typically manifesting as a truncated causal chain or noise anchoring: the model stops at generic rollback/lock wait, or treats TiKV/Raft/safe-ts resource noise as the primary cause; subsequent wrong compensation is a secondary outcome. Failure types come from the full-trace judge and are not mechanically derived from the DP/OP/SP booleans.
