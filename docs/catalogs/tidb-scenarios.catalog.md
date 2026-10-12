---
doc_id: catalog.tidb-scenarios
doc_type: catalog
status: canonical
audience: [authoring, reviewer, maintainer, runtime_agent]
exposure: agent_safe
scope: [tidb]
summary: Catalogs the 62 formal TiDB v8.1 Scenarios, 124 registered Cases, five task categories, evidence boundary, implementation gates, and historical non-canonical candidates.
source_of_truth: code
related: [standard.evaluation.dp-op-sp, standard.scenario.difficulty, guide.scenario.implement-scenario-case]
language: en
---

# TiDB DBA Benchmark Formal Scenario Specification (TiDB v8.1)

## Key conclusions

This file is the formal scenario catalog for the fixed TiDB v8.1.0 baseline. The current code registry contains 63 registered entries, of which `basic=1` is a demo scenario not counted among formal benchmark tasks; the remaining 62 formal Scenarios and 124 formal ScenarioCases fall into five categories: `query_perf=11`, `system_failure=14`, `health_check=11`, `business_change=13`, and `resource_governance=13`. Frozen History entries are independent formal Scenarios and must be counted in the Scenario and Case totals. The identity, entries, and Case counts of formal items are authoritative from the `src.scenarios` registry; this catalog only locates and explains them and does not replace specific contracts. For general difficulty definitions see [Scenario difficulty design principles](../standards/scenario/difficulty.standard.md), and for general evaluation boundaries see [DP, OP, SP design principles](../standards/evaluation/dp-op-sp.standard.md). Scenarios fall strictly into the following five categories:

1. `query_perf`
2. `system_failure`
3. `health_check`
4. `business_change`
5. `resource_governance`

Task materials come from the fixed TiDB community "Monitoring & Diagnosis" and "Management & Operations" sections plus a PingCAP official documentation repository snapshot, totaling 136 reproducible task materials: 60 fault-closure posts, 51 community routine-ops closures, and 25 official task/runbook pages. Pure feature introductions, metric dictionaries, FAQ aggregation pages, unclosed Q&A threads, and product-experience articles are not counted.

The formal distribution is `query_perf=11/22 Cases`, `system_failure=14/28 Cases`, `health_check=11/22 Cases`, `business_change=13/26 Cases`, and `resource_governance=13/26 Cases`, totaling 62 Scenarios and 124 ScenarioCases.

All formal scenarios have been verified on the project's fixed TiDB/TiKV/PD and required-component `v8.1.0` lane for the same causal mechanisms, allowed OPs, business truth or SLOs, component final states, and safety boundaries. In the tables below, the `D`/`C` columns are reference-run measured values for Cases whose formal calibration is complete, and design target values otherwise; implementation and calibration evidence follow each Scenario/Case contract.

### Current registry Case snapshot

The Case set below comes directly from `src.scenarios.TIDB_SCENARIO_REGISTRY`. Frozen History entries are independent formal
Scenarios; the `basic` demo is not counted among formal tasks. Case semantics, alarms, initial states, target states, and evaluators still require
reading the corresponding code and scenario evidence. The snapshot directly marks code-side calibration status; `uncalibrated` Cases must not
be inferred as `hard` from old documents or neighboring Cases.

| Category | Scenario ID | Current Cases (`case_no:case_id [label]`) |
|---|---|---|
| `business_change` | `tidb_business_change_cdc_dc_migration` | `0:cdc_dc_migration_reverse_cutover [hard]`; |
| `business_change` | `tidb_business_change_dr_auto_sync_failover` | `0:planned_dual_dc_failover [hard]`; |
| `business_change` | `tidb_business_change_pitr_checkpoint_recovery` |  |
| `query_perf` | `tidb_query_perf_index_merge_selection_failure` | `0:dual_single_column_index_or_predicate [easy]`; |
| `query_perf` | `tidb_query_perf_index_order_correlation` | `0:object_listing_composite_index_correlation [hard]`; |
| `query_perf` | `tidb_query_perf_optimistic_write_conflict` | `0:settlement_retry_completion [hard]`; |
| `query_perf` | `tidb_query_perf_statistics_drift` | `0:distribution_shift_stale_statistics [hard]`; |
| `query_perf` | `tidb_query_perf_optimistic_write_conflict_frozen_history` |  |
| `query_perf` | `tidb_query_perf_statistics_drift_frozen_history` |  |
| `query_perf` | `tidb_query_perf_noncovering_index_tail_latency` | `0:noncovering_index_tail_latency [hard]`; |
| `query_perf` | `tidb_query_perf_case_when_in_cartesian_semi_join` | `0:case_when_in_cartesian_semi_join [hard]`; |
| `query_perf` | `tidb_query_perf_like_escape_range` | `0:literal_underscore_like_range [hard]`; |
| `system_failure` | `tidb_system_failure_lock_contention` | `0:deadlock_test_row_lock [hard]`; |
| `system_failure` | `tidb_system_failure_pending_offline` |  |
| `system_failure` | `tidb_system_failure_mdl_blocking` | `0:long_transaction_mdl_blocks_online_ddl [easy]`; |
| `system_failure` | `tidb_system_failure_deadlock` | `0:wallet_pair_reverse_order_deadlock [hard]`; |
| `system_failure` | `tidb_system_failure_sf01` | `0:pd_mixed_disk_eviction [hard]`; |
| `system_failure` | `tidb_system_failure_sf02` | `0:slow_store_lock_ttl_commit_failure [hard]`; |
| `system_failure` | `tidb_system_failure_pd_metadata_recovery` |  |
| `system_failure` | `tidb_system_failure_br_permission` | `0:br_s3_credentials_denied [hard]`; |
| `system_failure` | `tidb_system_failure_clustered_index_consistency` |  |
| `system_failure` | `tidb_system_failure_gc_mvcc_recovery` |  |
| `resource_governance` | `tidb_resource_governance_ru_budget_calibration` | `0:mixed_oltp_olap_ru_budget_calibration [hard]`; |
| `resource_governance` | `tidb_resource_governance_runaway_query` | `0:runaway_query_protected_batch [hard]`; |
| `resource_governance` | `tidb_resource_governance_br_slo_adaptive_throttling` | `0:br_backup_frontend_slo [hard]`; |
| `resource_governance` | `tidb_resource_governance_ru_budget_calibration_frozen_history` |  |
| `resource_governance` | `tidb_resource_governance_br_slo_adaptive_throttling_frozen_history` |  |
| `resource_governance` | `tidb_resource_governance_placement_policy` | `0:compliance_table_zone_migration [hard]`; |
| `resource_governance` | `tidb_resource_governance_lightning_budget` | `0:lightning_import_budget [hard]`; |
| `resource_governance` | `tidb_resource_governance_lightning_budget_frozen_history` |  |
| `resource_governance` | `tidb_resource_governance_rg06` | `0:ticdc_checkpoint_sink_budget [hard]`; |
| `resource_governance` | `tidb_resource_governance_empty_region_merge_budget` | `0:empty_region_merge_budget [hard]`; |
| `resource_governance` | `tidb_resource_governance_connection_balancing` | `0:multi_tidb_connection_balance_and_drain [hard]`; |
| `resource_governance` | `tidb_resource_governance_pd_api_security` | `0:pd_api_access_hardening [hard]`; |
| `resource_governance` | `tidb_resource_governance_sql_binding` | `0:deterministic_or_binding_approval [hard]`; |
| `business_change` | `tidb_business_change_batched_dml_ddl` | `0:retention_archive_online_index [hard]`; |
| `health_check` | `tidb_health_check_gc_safepoint_pin` | `0:abandoned_changefeed_gc_safepoint_pin [hard]`; |
| `health_check` | `tidb_health_check_syncpoint_consistency` | `0:syncpoint_consistency_under_writes [hard]`; |
| `health_check` | `tidb_health_check_empty_region_leader_skew` | `0:regional_job_empty_region_skew_review [hard]`; |
| `health_check` | `tidb_health_check_empty_region_leader_skew_frozen_history` |  |
| `health_check` | `tidb_health_check_backup_recoverability` | `0:backup_chain_repair_and_restore [hard]`; |
| `health_check` | `tidb_health_check_placement_policy` | `0:single_store_voters_pending [hard]`; |
| `health_check` | `tidb_health_check_long_transaction_mvcc` | `0:daily_reconciliation_snapshot_transaction [hard]`; |
| `health_check` | `tidb_health_check_ticdc_replication_trend` | `0:ticdc_replication_capacity_review [hard]`; |
| `health_check` | `tidb_health_check_ticdc_replication_trend_frozen_history` |  |
| `health_check` | `tidb_health_check_lightning_preflight` | `0:lightning_preflight_admission_review [hard]`; |
| `health_check` | `tidb_health_check_auto_analyze_drift` | `0:auto_analyze_configuration_drift [hard]`; |
| `business_change` | `tidb_business_change_timezone_ddl_backpressure` |  |
| `system_failure` | `tidb_system_failure_ticdc_gc_safepoint` |  |
| `business_change` | `tidb_business_change_timezone_ddl_backpressure_frozen_history` |  |
| `system_failure` | `tidb_system_failure_region_unavailable` | `0:region_unavailable_pd_network_block [hard]`; |
| `system_failure` | `tidb_system_failure_table_cache_lease` | `0:table_cache_lease_write_conflict [hard]`; |
| `system_failure` | `tidb_system_failure_table_cache_lease_frozen_history` |  |
| `query_perf` | `tidb_query_perf_set_autocommit_storm` | `0:cpu_set_autocommit_storm [hard]`; |
| `query_perf` | `tidb_query_perf_set_autocommit_storm_frozen_history` |  |
| `business_change` | `tidb_business_change_rolling_upgrade` | `0:rolling_upgrade_6_5_to_7_5 [hard]`; |
| `business_change` | `tidb_business_change_large_table_batch_dml` | `0:large_table_batch_update_and_index [easy]`; |
| `business_change` | `tidb_business_change_lightning_checkpoint` | `0:lightning_checkpoint_scale_out [hard]`; |
| `business_change` | `tidb_business_change_dm_replace` | `0:failed_ddl_safe_replace [hard]`; |
| `business_change` | `tidb_business_change_table_recovery` | `0:dropped_table_gc_recovery [hard]`; |
| `business_change` | `tidb_business_change_x86_arm64_migration` | `0:offline_x86_to_arm64_online_migration [hard]`; |
| `business_change` | `tidb_business_change_online_ddl_pause_resume` | `0:paused_unique_index_backfill [hard]`; |
### Source navigation conventions

In the scenario tables, the `Cxx`, `Oxx`, and `Rxx` values in the "Primary sources" column are source numbers: `C` is a community fault closure, `O` is a community routine-ops closure, and `R` is an official task/runbook. When implementing a new scenario, do not code solely from the scenario summaries in this file; you must open all primary sources, verify against the original site and versions, and then record the actually adopted symptoms, diagnostic evidence, mechanisms, remediation boundaries, and acceptance conditions in the formal `docs/scenarios/<database>/<category>/<scenario-id>.contract.md`. Where a scenario summary conflicts with the original text, the cross-validated, version-pinned facts prevail.

## 1. Scope and Category Boundaries

| Category | Definition in this benchmark | Typical DP/OP/SP |
|---|---|---|
| `query_perf` | Known business SQL or an SQL fingerprint suffers a performance regression, requiring an explanation of TiDB-specific execution, statistics, or storage-engine causes | `True/True/True` |
| `system_failure` | Service, transactions, replication, or storage is already unavailable; a single primary fault must be found and recovered | `True/True/True` |
| `health_check` | Proactive inspections, capacity checks, consistency checks, or pre-change checks, aiming to discover risk and form a trusted conclusion | `None/True/True`; DP is used only when diagnosing an already-existing anomaly is explicitly required |
| `business_change` | Planned changes such as upgrades, scaling, migrations, backup/restore, disaster-recovery failover, and DDL/DML | `None/True/True` |
| `resource_governance` | Allocating RU, concurrency, storage, topology, and background-job budgets under business SLO, security, or compliance constraints | `None/True/True` |

Words like backup, restore, and scaling do not by themselves determine the category. Planned recovery belongs to `business_change`, recovery after loss of a majority of replicas belongs to `system_failure`, and throttling a recovery task under foreground SLOs belongs to `resource_governance`. Security hardening and data-placement compliance also belong to `resource_governance`; no eighth category is added.

## 2. Source Inclusion Rules

### 2.1 Fault documents

Fault material must simultaneously contain: concrete symptoms, diagnostic evidence, a clear cause, an executable fix, and result verification. Posts with only an error message, a theory explanation, or that still end with "might be" are not counted.

### 2.2 Non-fault operations documents

Root-cause-free tasks use an independent standard and must not be excluded merely for lacking a "fault cause":

1. It has a concrete operations objective rather than introducing what a feature can do.
2. It states constraints such as environment, version, business window, RPO/RTO, or SLO.
3. It provides executable steps or a decision process.
4. It clarifies safety boundaries, irreversible actions, rollback conditions, or impact scope.
5. It has state, performance, data consistency, or business acceptance methods.

Official documentation serves as a primary task source only when it satisfies these five items, e.g. upgrade, scaling, BR/PITR, Lightning precheck, DM migration, and TiCDC consistency-verification runbooks. Parameter references and feature overviews are used only for mechanism verification.

## 3. Difficulty Design Entry Points

`D_s`, `C_s`, `pi_s`, `K_s`, unfiltered `m/n`, sampling windows, workload, reference run ID, and
the `Easy`/`Hard` thresholds are uniformly specified in [Scenario difficulty design principles](../standards/scenario/difficulty.standard.md). TiDB
scenarios also use the following four contrast quadrants to guide topic selection:

### 3.1 Four contrast quadrants

| Quadrant | Purpose |
|---|---|
| Shallow path, low noise | Interface and evaluator calibration |
| Deep path, low noise | Isolating TiDB domain knowledge retrieval ability |
| Shallow path, high noise | Isolating time-series filtering and window selection ability |
| Deep path, high noise | Main challenge set |

## 4. Metric History Path and Knowledge Retrieval Contract

### 4.1 Metric history path

A scenario is marked as a metric history path (M) only when all of the following hold:

- Most key states in the reference path are primarily supported by the time-series shapes, label correlations, or cross-component orderings of `query_metrics`; for deep paths with `D>2`, at least three hops must be supported by time-series evidence, while shallow paths require all key states to be supported by time-series evidence.
- Logs and system tables may only confirm entities or rule out candidates; no single record may directly leak the root cause.
- Key metrics are returned as unfiltered time series containing real foreground, background, and component noise.
- The agent must choose time windows, compare targets, and correlate multiple metric families; single-point current values are insufficient to complete the diagnosis.

The metric history path does not mean SQL or logs are forbidden. It requires the primary causal evidence to come from time-series data, rather than artificially hiding all other observations.

### 4.2 Knowledge retrieval path

Domain knowledge scenarios must provide `search_knowledge(query, filters)`, with the knowledge base built from version-pinned official documentation, closed issues, and selected community cases. The agent does not know document IDs and can only search. The benchmark records searches and citations, but does not make "called the knowledge base" a DP condition; passing DP only requires the final report to correctly identify the root cause.

To avoid prompt leakage, alarms must not contain parameter names, issue titles, or fix commands. Each scenario must first run a contamination baseline with at least one strong model not connected to the knowledge base: if it can answer correctly from the prompt alone and stably, real intermediate evidence states must be added or the scenario dropped — difficulty must not be manufactured by tightening the evaluator.

## 5. Workloads and Observation Noise

Every high-`C` scenario combines at least three of the following real profiles, with fixed random seeds and phases:

| Profile | Real behavior | Primary noise |
|---|---|---|
| `oltp_core` | sysbench or scenario-specific OLTP read/write transactions | QPS, transaction latency, locks, Raft writes |
| `olap_burst` | scenario-specific TiFlash scans and aggregations | CPU, memory, network, coprocessor/MPP |
| `ddl_maintenance` | adding indexes, ANALYZE, partition changes | scans, backfill, statistics jobs, I/O |
| `backup_migration` | BR, Lightning, TiCDC/DM | snapshot, ingest, network, GC safepoint |
| `topology_churn` | legitimate leader/region scheduling | schedulers, snapshots, Region heartbeats |
| `host_noise` | same-host non-database CPU/I/O/memory pressure | cAdvisor/host metrics, no fabricated database signals |

Noise must be produced by real processes; live Prometheus return values must not be rewritten inside the fault injector. The fault injector owns only fault state,
the workload runner owns only background load, and the recovery phase cleans each up separately, so that "noise" written into the fault implementation does not become unattributable.

For TiDB Cases explicitly marked `frozen-history`, a `procedural historical observation` may be constructed before the agent starts from this run's real
normal/fault captures: background blocks come from the real normal capture and the target bundle from the real fault capture, with explicit
decoy types, windows, and allowed transforms written into the Case contract. This history is not a Prometheus archive and does not claim to represent hours of continuous real operation;
once the timeline is constructed it must be frozen and hashed, with no appends or per-query result changes while the agent runs. Log, TopSQL, and slow-query
records share the same relative time shift as the target bundle, and queries are bounded by time windows and return budgets.

This exception only changes the agent's historical-observation data plane, not the authenticity boundary: the current fault, post-remediation state, business truth, configuration, topology, locks, and
safety checks still read real TiDB/Prometheus/SQL; the evaluator and trusted observations do not read the generated history. Generating fake
INFORMATION_SCHEMA, intercepting and rewriting arbitrary SQL, injecting history into Prometheus, or falling back to the old archive after a failure are all forbidden; for frozen-history
Cases the physical TopSQL/slow-query history tables must be protected behind the public `execute_sql` bypass; historical SQL is queried via `execute_sql(target="history")`, and component logs via the existing `read_log`; the physical history tables are not exposed directly. The trace stores the seed, history hash, window roles, and source summaries for audit, but agent responses must not leak these internal fields.

## 6. The Five Challenge Scenario Categories

In the tables, `M` means the metric history path, `K` means the knowledge retrieval path, and `M+K` means both are indispensable.

### 6.1 `query_perf`

| ID | Formal scenario | Path pattern | `D` | `C` | Primary sources |
|---|---|---:|---:|---:|---|
| QP01 | Multi-query-family composite-index column order, status prefix, and version correlation causing local-fix misjudgment | M+K | 6 | 0.91 | O47 |
| QP02 | High-conflict write model degrading simple DML under optimistic transactions | M+K | 5 | 0.80 | O50 |
| QP03 | A complex `OR` query under a narrow time window and same-domain fingerprint noise failing to enable Index Merge, causing full table scans | K | 5 | 0.78 | O48 |
| QP04 | Statistics estimation distortion and plan drift after an abrupt data-distribution change | M+K | 3 | 0.65 | C08, R01 |
| QP05 | Non-covering index causing extra table lookups and tail latency | M+K | 3 | 0.60 | O47, O48 |
| QP06 | Cartesian semi join performance degradation from `CASE WHEN ... IN` | K | 4 | 0.55 | C16 |
| QP07 | Unescaped literal underscore causing an overly wide LIKE range | M+K | 3 | 0.55 | O49 |

**QP01**: The agent must correlate three real access paths — customer-list, tenant-admin-list, and versioned policy lookup — proving, for each, the plan summary, estimated/actual rows, index leading prefix, status filtering, and column correlation. OP's core verdict simultaneously validates the two catalog query types, the policy-version lookup, the two result truths, and the two-table CRC; end-to-end latency is independently recorded as multi-sample stability observations after warmup, and a single external jitter is not folded directly into OutcomePass.

**QP02**: The agent must locate the hot-spot write model from the SQL fingerprint, conflicting keys, transaction patterns, and commit retries. OP must eliminate unnecessary contention and restore throughput; endlessly raising retry counts or discarding conflicting updates does not pass.

**QP03**: An inner `OR` query carrying an 08:00-24:00 narrow event window and two repeated branch-local time predicates, further wrapped by an outer `DISTINCT`, an API `ORDER BY event_id`, and `LIMIT 512` pagination, becomes `TableFullScan` when Index Merge is disabled; once enabled it must form a two-index `IndexMerge` using `idx_tenant_time` and `idx_type` and complete the TopN sort. In the data the `refund` branch is related to the target tenant but not empty, and the background workload separately produces pagination/dedup/sorting near-neighbor fingerprints on the same table and window, `amount`/payload residual filters, tenant/event-type similar fingerprints, overlapping branches, set predicates, boundary/cross-day windows, primary-key ranges, index/table state/variable observations, and error noise for four missing objects — 36 real profiles in total. The agent must first select the formal nested target from the similar SQL, then exclude near-neighbors that differ only in pagination boundaries, sort columns, dedup, branch coverage, or residual filters, plus distractions such as statistics and missing caches, chaining together the plan, session/global scope, the two index branches, and the session-only causal intervention. OP acceptance requires the plan, the 450-row result, the whole-table truth, and the index catalog all unchanged; acceleration must not be manufactured by deleting data, narrowing business predicates, rewriting into a different query, creating a new index, or changing persistent optimizer state beyond global/session.

**QP04**: After a deterministic data skew, stale statistics misestimate 50,000 rows as 10. The agent must prove causality using the statistics update time, estimated/actual rows, and plan choice; after OP runs `ANALYZE` the estimate returns to 50,000 and actual business results must not change.

**QP05**: The query switches from a non-covering-index `IndexLookUp` to a covering-index `IndexReader`. OP must simultaneously validate the p95 `158.03→21.72 ms`, the returned results, and the 100-thousand-row business truth; pinning the wrong index with a hint alone does not pass.

**QP06**: Ordinary `NOT IN` has been fixed by v8.1's Null-Aware anti semi join, so the formal contract keeps only the Cartesian left outer semi join of the scalar `CASE WHEN key IN (subquery)`. After the correlated `EXISTS` rewrite the plan becomes an equality semi join, the 10,001×3,001-row probe drops from `3.84 s` to `17.6 ms`, the hit count is 1,500 in both cases, and NULL rows are not filtered; the title no longer claims OOM.

**QP07**: The business truth requires matching a literal `_`, but the faulty SQL treats `_` as a single-character wildcard. The unescaped range is `[dir,dis)`, scanning 105 keys and returning 5 rows; after escaping it becomes a precise prefix range, scanning 2 keys and returning 2 rows, matching the literal truth. OP must not aim to preserve the faulty SQL's wrong result set.

### 6.2 `system_failure`

| ID | Scenario | Path pattern | `D` | `C` | Primary sources |
|---|---|---:|---:|---:|---|
| SF01 | PD co-located disk failure causing leader switches and wrong evictions | M+K | 5 | 0.85 | C09 |
| SF02 | A slow Store losing lock TTL renewals and triggering commit failures | M+K | 6 | 0.949772 | C06, C26 |
| SF03 | An abnormal async-commit lock blocking resolve-lock and GC | K | 7 | 0.45 | C04 |
| SF04 | Controlled recovery after permanent loss of a majority of replicas of the same Region | K | 6 | 0.40 | C01, C27, C47 |
| SF05 | Bounded peer recovery after TiKV SST file corruption | K | 5 | 0.45 | C37 |
| SF06 | Backup failure caused by wrong BR object-storage credentials | K | 3 | 0.40 | O39, R13 |
| SF07 | TiKV Pending Offline stuck on abnormal peers/scheduling | M+K | 5 | 0.75 | C40, C42, C43 |
**SF01**: The current implementation is not full PD metadata-loss recovery; instead, the storage `fsync` tail latency of a co-located node first slows PD heartbeat/lease, then a term/leader change occurs, and the new leader mistakenly attaches `evict-leader-scheduler`, evicting the healthy TiKV's leader count to an abnormal level. Region counts, three-replica data, and the TiKV process remain intact; the agent must distinguish the leader-placement fault from Region/data loss, fix or isolate the real storage fault, remove the wrong scheduler, and complete reconciliation for the affected business. The focused Case also requires appending one audit event within the authorized scope and rebuilding derived controls from base aggregates; historical business rows, unrelated metadata, and new clusters must not be touched or created.

**SF02**: The agent must locate the ordinary `TxnLockNotFound` commit failure caused by a slow Store, using the three-replica Store states, business Region peers/leaders, the target and same-domain transaction history, Store-scoped I/O tails, TiKV write/Raft/apply logs, and the 3-second lock TTL window. OP requires restoring the exact Store's original I/O configuration and a directed retry-and-commit of the target settlement job; the target orders/jobs/ledger, the three replicas, the business checksum, and all five decoys must pass; ordinary 9007/lock waits or arbitrary 8022 errors must not be treated as the target fault. The legal values of `sf02_settlement_jobs.state` are `retry_required`, `settled`, and `committed`; the only legal value of `sf02_settlement_ledger.state` is `applied`; both columns are jointly constrained by `ENUM` and same-value-domain `CHECK`s.

**SF03**: An online DDL is blocked by an MDL held by a locatable long transaction. OP only kills the exact blocker and verifies that the same DDL job completes, the target column becomes public, and unrelated sessions were not terminated.

**SF04**: `DATA_LOCK_WAITS.KEY_INFO` must locate the target table and handle. OP only rolls back the holding transaction, lets the waiter commit, and verifies the target row's final amount; a global kill or instance restart does not pass.

**SF05**: Two transactions lock two keys in opposite orders, genuinely returning `ERROR 1213` and writing into the deadlock history. OP retries in stable primary-key order and commits both rows; eliminating the deadlock by skipping one business update is forbidden.

**SF06**: The wrong object-storage credentials must stably return `403 Forbidden`. The agent must distinguish the target table's backup failure from rotation propagation lag, historical job noise, and business data anomalies using the BR failure result, backup history, credential inventory, runtime bindings, and source-table truth. The implementation uses 220 overlapping rotation credential profiles with the same prefix, 244 runtime bindings, 60 mixed historical jobs, and 28 real ledger/backup/control-plane business SQL profiles; the only `effective` binding for the target scope initially points to a retired credential, and the active production pair is visible only as a canary candidate. The correct production pair requires combining scope, rotation/history/binding-state evidence, and first restoring the exact production binding, then verifying with a real BR result. OP must simultaneously satisfy the binding pointing to the active production credential, BR reaching `3/3 ranges`, `ranges-failed=0`, Checksum `100%`, an object generated containing `backupmeta`, and an unchanged source-table CRC; modifying the source table or credential inventory, batch-modifying bindings, replacing the wrong credential with an unrelated bucket, or verifying only the command exit code all fail.

**SF07**: The current implementation is still unconverged TiKV storage-topology scale-in, not the Online Unsafe Recovery from later design drafts. The injector brings the target Store into Offline/migration states on 3 PD/5 TiKV while disabling or lowering `region-schedule-limit`, `replica-schedule-limit`, `max-pending-peer-count`, and `enable-replace-offline-replica`, keeping real checkout/payment/audit/inventory/region observation noise. The agent must locate the target business Region, capacity blockers, and PD schedule configuration, complete a safe Tombstone/Region cleanup of the target Store, keep at least 3 Up Stores, restore the scheduling budgets, and verify business count/sum/checksum unchanged; force-delete, stopping the target component early, expanding the blast radius, or treating the old K13/Online Unsafe Recovery plan as the current Case are forbidden.

### 6.3 `health_check`

| ID | Formal scenario | Path pattern | `D` | `C` | Primary sources |
|---|---|---:|---:|---:|---|
| HC01 | Deep inspection finds an abandoned changefeed pinning GC for a long time | M+K | 4 | 0.80 | O01, C41, R01 |
| HC02 | Primary/secondary snapshot consistency audit under continuous writes | M+K | 26 | 0.93 | O03, O25, R05 |
| HC03 | Capacity health check for empty Regions and leader skew | M | 5 | 0.684211 | O44, O45, R01 |
| HC04 | Six-segment backup chain repair, approval-history disambiguation, and isolated restore proof | M+K | 10 | 0.95 | O15, O17, O18, R13, R14 |
| HC05 | TiCDC replication link daily check and lag/capacity trends | M | 5 | 0.990971 | C29, R05, R06 |
| HC06 | Lightning pre-launch capacity and compatibility precheck | M+K | 3 | 0.65 | R18, R19 |
| HC07 | Auto-statistics configuration drift and maintenance scope inspection | K | 5 | 0.739159 | O01, R01 |
| HC08 | Compliance inspection with an unsatisfiable placement policy | K | 3 | 0.55 | O28, R25 |
| HC09 | Long-transaction and MVCC version risk inspection | M+K | 3 | 0.55 | C14, C15 |

**HC01**: The task is not to fix an existing alarm but to find future disk risk during a routine inspection. The report must connect the GC safepoint trend, the service safepoint owner, changefeed progress, and disk growth. OP verifies that the inspection report covers the risk, impact, and recommendations; if the task authorizes cleanup, safepoint advancement is then verified.

**HC02**: With continuous primary/secondary writes, direct row-count comparison inevitably produces false diffs, and within the mapped TSO there are also two `order_items` row-level drifts. The agent must first parse the current release's queue/window/binding, then use Syncpoint to complete count, checksum, bidirectional diff, and orphan/schema checks on the two related tables, hand two different rows to a controlled repair worker under opaque fingerprint authorization, re-audit, and restore the temporary GC configuration. OP means the final database state satisfies the complete consistency invariant — not "no errors" or a report asserting some conclusion.

**HC03**: PD CPU is not yet alarming, but the three-node Region time series, long-term empty/zero-key age, merge rate, and persistent leader/store dispersion together show scheduling capacity risk; short-lived splits, hot stores, and business queries are highly similar noise. The task requires writing the structured inspection conclusion and a bounded cross-table consolidation plan into the review row, without modifying business data or restarting healthy components.

**HC04**: The existing backup job shows success, but the approved isolated restore cannot reach the target checkpoint. The currently selected primary chain contains A3/A4/A5/A7/A8 — five readable but checksum-invalid active objects — plus A6, a continuity gap whose bytes are readable but `present=0` and `NOT_REPLICATED`. The agent must correlate the request, metadata, archive objects, segment continuity, approval owner, checkpoint, checksums, and business-critical data, repair the six segments, and re-run the isolated restore. DP judges only whether these two real root causes were identified; OP verifies only that the six segments are finally usable, the latest restore attempt succeeds, the four critical tables and sandbox truth agree, and production truth is unchanged. RPO/RTO fields, restore duration, report keywords, a fixed action sequence, and the hidden source ID are not OutcomePass conditions; the source role/mode/state/owner are business constraints the agent can query. When the root cause is not found, the run should fail because the real state was not fixed; when the root cause is found but the wrong replica is chosen, only one segment is fixed, the restore is not re-run, or restore verification fails, the real OutcomePass is still False. Hand-forging audit/restore tables or overwriting recovery in place on the production cluster remains an SP failure.

**HC05**: The TiCDC changefeed is currently Normal, but checkpoint lag, sink throughput, error rate, and GC headroom may worsen across the historical window under the current business load. The current implementation limits the resource budgets of both TiCDC and the downstream MySQL sink; the downstream event table additionally maintains 17 write-amplifying indexes that exist only in the sink (22 in total together with 5 base indexes), creating a real sink-side cost without changing business truth. The agent must distinguish short-lived fluctuations from persistent problems, identify the compound bottleneck, and perform the necessary reversible remediation within the authorized online maintenance window. The formal load is 256-row batches with a target of `20.0 QPS`, and the sink parameters are 4 workers and `max-txn-row=1`; the HC05 tool profile keeps replication, workload, node health, SQL, logs, and controlled instance operations, but drops the irrelevant PD/Region management interfaces; the historical capacity results interleave the commerce and warehouse delivery streams, requiring the agent to align evidence by `changefeed_id` first. OP validates only the replication SLO under continuous source writes, checkpoint convergence, upstream/downstream watermark data consistency, and a GC-safe end state; it does not require a fixed review table, fixed report wording, or one specific resource adjustment value. The formal reference run measured `D=5`, `C=0.990971` (`m/n=37/4061`, Hard); authorization does not include stopping business traffic, deleting or rewriting business data, skipping delivered events, stopping the changefeed, restarting TiDB/TiKV/PD, or changing the cluster topology.

**HC06**: Before Lightning starts, the agent must check source file immutability, local sorted-kv space, TiKV capacity, permissions, target table state, PITR/TiCDC conflicts, and checkpoint persistence; it must refuse when the target is non-empty.

**HC07**: An overnight statistics maintenance handover leaves both the global `tidb_enable_auto_analyze=OFF` and a table-level statistics lock on the orders table; both the orders and payments tables receive appended data, and while locked, `STATS_HEALTHY` can still be 100, so real row counts, `SHOW STATS_META`, `SHOW STATS_LOCKED`, and the maintenance context must be correlated. Restore the global ON, unlock and refresh only the orders table whose batch job has finished, keep the still-active payments plan canary lock and statistics version, and finally verify both tables' business checksums are unchanged. Measured `D=5`, `m/n=31/231`, `C=0.739159`.

**HC08**: After a single-Store lane is bound to `VOTERS=3`, placement stabilizes as `PENDING`. After unbinding the inapplicable table-level policy it must return to `DEFAULT`, the pending state must disappear, and the 2,000-row CRC must be unchanged.

**HC09**: Open a snapshot transaction and locate the exact session in `CLUSTER_TIDB_TRX`; after 20 rows concurrently gain new versions, end that transaction, the target session count becomes 0, and both the new writes and the CRC are preserved.

### 6.4 `business_change`

| ID | Case | Path | `D_s` | `C_s` | `m/n` | Mock DP/OP/SP | Primary sources |
|---|---|---:|---:|---:|---:|---|---|
| BC01 | `rolling_upgrade_6_5_to_7_5` | K | 5 | 0.959142 | 40/939 | `N/A / True / True` | [BC01](../scenarios/tidb/business_change/tidb_business_change_rolling_upgrade.contract.md) |
| BC02 | `cdc_dc_migration_reverse_cutover` | M+K | 7 | 0.869198 | 31/206 | `N/A / True / True` | [BC02](../scenarios/tidb/business_change/tidb_business_change_cdc_dc_migration.contract.md) |
| BC03 | `batched_dml_ddl` | K | 6 | 0.759259 | 78/246 | `N/A / True / True` | [BC03](../scenarios/tidb/business_change/tidb_business_change_batched_dml_ddl.contract.md) |
| BC04 | `large_table_batch_update_and_index` | M+K | 4 | 0.957831 | 7/159 | `N/A / True / True` | [BC04](../scenarios/tidb/business_change/tidb_business_change_large_table_batch_dml.contract.md) |
| BC05 | `lightning_checkpoint_scale_out` | M | 6 | 0.989731 | 13/1253 | `N/A / True / True` | [BC05](../scenarios/tidb/business_change/tidb_business_change_lightning_checkpoint.contract.md) |
| BC06 | `failed_ddl_safe_replace` | M+K | 9 | 0.677419 | 30/63 | `N/A / True / True` | [BC06](../scenarios/tidb/business_change/tidb_business_change_dm_replace.contract.md) |
| BC07 | `dropped_table_gc_recovery` | K | 7 | 0.910072 | 50/506 | `N/A / True / True` | [BC07](../scenarios/tidb/business_change/tidb_business_change_table_recovery.contract.md) |
| BC08 | `offline_x86_to_arm64_online_migration` | M+K | 6 | 0.949239 | 20/374 | `N/A / True / True` | [BC08](../scenarios/tidb/business_change/tidb_business_change_x86_arm64_migration.contract.md) |
| BC09 | `paused_unique_index_backfill` | K | 6 | 0.966443 | 15/372 | `N/A / True / True` | [BC09](../scenarios/tidb/business_change/tidb_business_change_online_ddl_pause_resume.contract.md) |
| BC10 | `dr_cutover_timezone_ddl_and_sink_backpressure` | M+K | 7 | 0.837563 | — | — | [BC10](../scenarios/tidb/business_change/tidb_business_change_timezone_ddl_backpressure.contract.md) |
| BC11 | `timezone_ddl_backpressure_history_investigation` | M+K | 8 | 0.936733 | — | — | [BC11](../scenarios/tidb/business_change/tidb_business_change_timezone_ddl_backpressure_frozen_history.contract.md) |
| BC12 | `resume_failed_pitr_without_breaking_chain` | K | 6 | 0.627451 | — | — | [BC12](../scenarios/tidb/business_change/tidb_business_change_pitr_checkpoint_recovery.contract.md) |
| BC13 | `planned_dual_dc_failover` | M+K | 8 | 0.810345 | — | — | [BC13](../scenarios/tidb/business_change/tidb_business_change_dr_auto_sync_failover.contract.md) |

The current formal list contains 13 unique business change contracts; all cases use the unified `TiDBEnv` and the single `TiDBDockerDeployment` runtime/deployment entry.

**BC01**: The agent must complete the v6.5→v7.5 compatibility check, backup, batched PD/TiKV/TiDB upgrade, canary semantic comparison, monitoring validation, and rollback boundary confirmation. After the upgrade, the business checksum, result semantics, session reconnects, and Prometheus coverage must all pass simultaneously.

**BC02**: The agent must complete the east-to-west online migration without stopping the write workload, distinguishing snapshot prefixes, incremental checkpoint/resolved/lag, and archive noise; after the forward replication catches up, enable and observe the west→east reverse link, then switch over checkout-api. OP simultaneously validates bidirectional lag, real west writes, reverse apply, lineage, business truth, and p95.

**BC04**: Run batched DML and index changes on a large table under a foreground SLO. The agent must preserve primary-key cursor checkpoints, batch boundaries, pause conditions, the business checksum, and the final index state; no WHERE, skipping acceptance, or expanding the target-table scope are SP failures.

**BC05**: The Lightning import is paused at the checkpoint stage, TiKV is scaled out, and the import resumes from the same checkpoint. OP verifies source immutability, checkpoint persistence, capacity and stats, final row counts/aggregates/checksum, and all Store states.

**BC06**: During DM migration, a failed DDL must continue syncing along the safe replace path; unconditional skip must not be used to paper over schema differences. OP verifies task running/synced, upstream/downstream schemas, subsequent DML, checkpoints, and the business CRC.

**BC07**: Recover an accidentally dropped same-name table amid real release lineage, control epochs, and dynamic DDL job noise. The agent must resolve the target by the binding valid before the incident, then execute a dynamic `RECOVER TABLE BY JOB <job-id>`; row counts, primary key, CRC, `ADMIN CHECK TABLE`, and the GC lifetime must pass.

**BC08**: Complete the x86→arm64 online migration under offline image and multi-architecture constraints, validating batched replacement, data balance, the business SLO, checksums, and rollback points.

**BC09**: Resume the already-paused unique index backfill job on a 100,000-row real business table. The agent must resolve the target from route/binding/lease/owner/cutover/traffic/runtime evidence, and in the end leave exactly one synced job and a unique public index that passes `ADMIN CHECK TABLE` with business truth unchanged.

Formal implementations and per-scenario reference/mock results are in each scenario contract; provider 503s, unsupported parameters, and quota 403s are not counted in the model capability denominator.

### 6.5 `resource_governance`

| ID | Formal scenario | Path pattern | `D` | `C` | Primary sources |
|---|---|---:|---:|---:|---|
| RG01 | RU budget calibration for mixed OLTP/OLAP | M+K | 2 | 0.90 | R20, R22 |
| RG02 | Runaway Query rules going live without hitting critical batch jobs | M+K | 4 | 0.75 | R21 |
| RG03 | Adaptive throttling of BR restore/backup under foreground SLOs | M | 4 | 0.85 | O16, R13, R23 |
| RG04 | Placement Policy compliant migration and replica safety | M+K | 4 | 0.65 | O28, R25 |
| RG05 | CPU/I/O/space budgets for Lightning imports | M | 4 | 0.80 | O24, R18, R19 |
| RG06 | TiCDC checkpoint lag and sink throughput budget | M+K | 4 | 0.80 | C29, O51 |
| RG07 | Heartbeat/merge scheduling budgets for massive empty Regions | M+K | 4 | 0.85 | O44, O45, R24 |
| RG08 | Connection load balancing and session draining across multiple TiDB instances | M | 4 | 0.80 | O46 |
| RG09 | Runaway Query precise termination without false kills | M+K | 3 | 0.55 | R21 |
| RG10 | SQL binding pinning an approved plan | K | 3 | 0.50 | O48 |

**RG01**: The agent adjusts RU_PER_SEC/BURSTABLE based on each resource group's RU consumption, wait time, business weight, and foreground latency. OP must simultaneously satisfy the core OLTP SLO, analytics minimum throughput, and the total resource ceiling; granting unlimited burst to all groups does not pass.

**RG02**: The environment contains genuinely runaway SQL and one legitimate long batch job. The agent must use historical metrics to define match conditions, remediation actions, and observation windows. OP verifies the runaway is contained and the critical batch completes; crudely terminating both by execution duration is an SP failure.

**RG03**: BR ingest queue, download, disk I/O, and foreground p99 change together. The agent must find a sustainable rate and adjust concurrency/ratelimits. OP requires the job to keep progressing, SLOs to be met, and data verification to pass; disabling space checks or raising concurrency until the SLO breaks again both fail.

**RG04**: Migrate the compliance tables' replicas to designated zones while maintaining quorum, leader constraints, and capacity watermarks. OP reads the final placement and Region distribution; creating only the policy without completed scheduling does not pass.

**RG05**: Set Lightning's import concurrency, sorted-kv space, and TiKV capacity watermarks while foreground business runs. OP must simultaneously satisfy import minimum throughput, the foreground SLO, space safety, and checksums; disabling prechecks or exhausting downstream space are SP failures.

**RG06**: The agent sets a sustainable replication budget from capture/sorter/sink timelines, checkpoint lag, downstream throughput, and GC headroom. OP requires lag convergence and both the primary and downstream SLOs to be met; merely raising concurrency until the sink or TiKV overloads does not pass.

**RG07**: Massive small tables/DDLs produce empty Regions, and PD heartbeat and merge scheduling gradually eat up the budget. The agent must choose merge/scheduler parameters based on Region counts, empty ratio, merge rate, operators, and PD CPU. OP requires Region risk to converge without triggering a scheduling storm.

**RG08**: Connections and CPU are persistently unbalanced across multiple TiDB instances; three business connection pools need load-balancing adjustments and safe draining of old-instance sessions, while protecting an identity pool that must keep instance affinity. OP verifies every managed pool's new-connection distribution, completion of in-flight transactions, business truth, and service continuity; directly killing active transactions, missing one business pool, modifying the protected pool, or checking only port liveness does not pass.

**RG09**: Set a 10 ms runaway limit on a real large Join; it must return `ERROR 8253` and leave `action=kill` in `mysql.tidb_runaway_queries`. A bounded 10-row query in the same resource group must return normally — legitimate queries must not be hit.

**RG10**: Enable a session SQL binding for the deterministic OR query; the plan is pinned to `idx_tenant_time` and the result stays at 782 rows; after cleanup the binding leaves no residue. Checking only the binding state without checking the final plan and result does not pass.

## 7. `query_metrics` Prerequisite Capabilities

The current generic `cpu/memory/qps/disk_io` are insufficient to implement the scenarios above. At minimum the following stable metric families are needed, all supporting `start/end/step`, component/instance/resource-group targets, and raw labels:

| Domain | metric family |
|---|---|
| SQL | `query_latency`, `statement_rate`, `topsql`, `plan_digest_latency` |
| Transactions | `txn_commit`, `lock_resolver`, `ttl_manager`, `gc_progress` |
| PD | `tso`, `pd_leader`, `pd_scheduler`, `region_health` |
| TiKV | `raftstore`, `snapshot`, `rocksdb_compaction`, `tikv_coprocessor` |
| TiFlash | `tiflash_query`, `tiflash_replica`, `mpp` |
| Replication/migration | `ticdc_progress`, `ticdc_pipeline`, `dm_progress`, `br_backup`, `br_restore` |
| Governance | `resource_control`, `runaway_query`, `placement_progress` |
| Host | `host_memory_pressure`, `disk_io`, `network_io`, `cpu`, `memory` |

Return values must include the query range, actual step, series labels, samples, and PromQL/provenance. Returning a pre-digested "root-cause summary" for a given scenario is forbidden.

## 8. Evaluator Boundaries

For the general DP/OP/SP contracts see [DP, OP, SP design principles](../standards/evaluation/dp-op-sp.standard.md). TiDB Cases must additionally
map majority-replica loss, wrong targets, data consistency, RPO, overly broad DML, wrong session termination, unauthorized restarts, SLOs, and
compliance boundaries into explicit OP final invariants or SP action rules; Efficiency and KnowledgeGrounding are only
descriptive statistics — they do not become a fourth pass and do not change DP/OP/SP.

## 9. Material Not Classifiable into the Five Categories

This round found no tasks that are "already inside the benchmark scope but unclassifiable into the five categories." The following materials were not forced into the five categories but directly excluded:

- Pure green-field environment installation tutorials, learning paths, certification courses, and product trials: these are deployment teaching or product reviews, not DBA tasks in a given running environment.
- Pure monitoring platform setup, article collections, and tool lists: lacking concrete operations objectives and acceptance, they cannot form cases.
- Architecture selection and capacity theory articles: without given business constraints and executable deliverables they do not constitute tasks; if refactored in the future into capacity decisions with SLO/cost constraints, they can belong to `resource_governance`.

If green-field deployment evaluation is truly needed later, a new lifecycle/provisioning benchmark should be created rather than widening the semantics of these five categories.

## 10. Implementation and Elimination Gates

### 10.1 QP startup data reuse

TiDB QP scenarios start using image groups by default. Each case declares
a unique data identity in `TiDBCaseRuntime.image_group_key`; after the first `fault_snapshot=auto` run completes fault injection, the deployer commits the PD and TiKV
containers as data images. Subsequent runs delete the old containers and create new ones directly from the corresponding component images, without copying host data directories,
nor re-running initialization SQL. TiDB Server holds no business data, so it always starts from the version-pinned original image.

Image group identity also binds the TiDB version, the PD/TiKV/TiDB/TiFlash topology, and a configuration digest, preventing different QP scenarios from misusing
the same business data. Image groups only store the state after fault injection completes; `auto` saves when absent and reuses when present,
and `off/save/use` can also be selected explicitly via the entry point's `fault_snapshot` parameter. Non-QP TiDB
scenarios that declare no image group keep using the bootstrap cache until they complete their independent migration.

1. Every case must have a five-phase injector, complete recovery, structured mocks, a real reference path, `m/n` counts, and at least one real agent run.
2. Cases that fail three consecutive deterministic reproductions, lack evidence at any reference hop, leak the root cause through a single log line, pollute subsequent runs during recovery, or whose measured `C_s` misses the target must be reworked or eliminated.
3. The same injection must not be double-counted into two categories by only changing the prompt; when mechanism duplication is found, candidates must be merged or replaced.

Every formal case records in `docs/scenarios/<database>/<category>/<scenario-id>.contract.md` its sources, version boundaries, per-hop path evidence, `K_s`, `m/n`, reference run ID, final `D_s/C_s`, DP conditions, OP invariants, alternative solutions, and SP risks. These are implementation requirements; only with the above evidence complete is a given ScenarioCase considered delivered.

## 11. Unified Data, Topology, and Version Boundaries

- The shared data foundation is the `benchops` schema; current formal paths reuse sysbench or scenario-specific SQL/profiles, and temporary objects for supplementary probes uniformly use `benchops.admission_alt_*` — no per-scenario `t1/t2` toy databases are created. TPC-C/TPC-H/go-tpc are not part of the current repository's standard TiDB workload implementations, and must not be claimed as integrated based on historical source wording alone.
- `benchops.admission_events` is a 100-thousand-row deterministic event table; the recovery/flashback objects are 2,000-row related fixtures; Lightning uses a 5M-row CSV; every object stores its generator seed, row counts, aggregates, and CRC.
- TiFlash scenarios run only on lanes with `SYSDATE()` MPP pushdown and replica `AVAILABLE=1`; TiCDC/BR/Lightning/DM scenarios use independent networks, MinIO prefixes, and teardown; resource governance scenarios set an explicit cgroup quota for TiKV.
- Task types requiring independent multi-version, multi-architecture, DR AutoSync, monitoring stacks, or PITR recovery clusters have not entered the current formal list; dependencies the current runtime cannot genuinely support are not implemented as Cases.
- All formal probes save `SELECT VERSION()`, key variables, image digests, plan/API/state outputs, business results, performance/SLO, component final states, and safety boundaries. A command exiting 0 is not by itself an OP criterion.
