# Compatibility changes for system variables in TiDB 6.3.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.3.0.md`
- Source Title: `TiDB 6.3.0 Release Notes`
- Source Heading Path: `TiDB 6.3.0 Release Notes > Compatibility changes > System variables`
- Source Line Ranges: `210-239`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`
- Topic Tags: `system-variables`, `compatibility-changes`, `authentication`, `ddl`, `optimizer`, `plan-cache`, `partition-pruning`, `read-committed`, `fastscan`, `deprecated`, `version-dependent-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0341_be7b54737a`
- Source ID: `tidb-docs-8.1:releases/release-6.3.0.md#system-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c9031b66908c1de7b687c61d9f23ec57322e96c4e843b996f42c418d1242639c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.3.0#system-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.3.0 release-note details about system variable additions, modifications, deprecations, default-value changes, scope changes, or features marked not fully functional.
- Retrieval Keywords: TiDB 6.3.0 system variables, default_authentication_plugin tidb_sm3_password, sql_require_primary_key, tidb_adaptive_closest_read_threshold, tidb_replica_read closest-adaptive, tidb_constraint_check_in_place_pessimistic, tidb_ddl_disk_quota, tidb_ddl_enable_fast_reorg, tidb_ddl_flashback_concurrency, flashback cluster, tidb_enable_exchange_partition deprecated, exchange partitions with tables, tidb_enable_foreign_key, tidb_enable_general_plan_cache, tidb_enable_metadata_lock, Metadata lock, tidb_enable_null_aware_anti_join, tidb_enable_pseudo_for_outdated_stats default OFF, tidb_enable_rate_limit_action default OFF, tidb_mem_quota_query, tidb_enable_tiflash_read_for_write_stmt, TiFlash read for write stmt, tidb_enable_unsafe_substitute, tidb_general_plan_cache_size, tidb_last_plan_replayer_token, PLAN REPLAYER DUMP, tidb_max_paging_size, tidb_opt_force_inline_cte, tidb_opt_three_stage_distinct_agg, COUNT(DISTINCT) three-stage aggregation, tidb_partition_prune_mode dynamic, tidb_rc_read_check_ts INSTANCE, tidb_rc_write_check_ts, tiflash_fastscan, FastScan query results accuracy data consistency
- Follow-up Guidance: Several variables in this list state that the controlled feature is not fully functional in TiDB v6.3.0 and that the default value should not be changed.
- Classification Note: This is a release-note compatibility section for TiDB system variables, summarizing newly added, modified, and deprecated variables and their documented behavior changes in TiDB 6.3.0.

## Official Source Content

### System variables

| Variable name | Change type | Description |
| --- | --- | --- |
| [`default_authentication_plugin`](https://docs.pingcap.com/tidb/stable/system-variables#default_authentication_plugin) | Modified | Adds a new option `tidb_sm3_password`. When this variable is set to `tidb_sm3_password`, SM3 is used as the encryption algorithm. |
| [`sql_require_primary_key`](https://docs.pingcap.com/tidb/stable/system-variables#sql_require_primary_key-new-in-v630)   | Newly added  | Controls whether to enforce the requirement that a table has a primary key. After this variable is enabled, attempting to create or alter a table without a primary key will produce an error.  |
| [`tidb_adaptive_closest_read_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_adaptive_closest_read_threshold-new-in-v630) | Newly added | Controls the threshold at which the TiDB server prefers to send read requests to the replica in the same region as the TiDB server when [`tidb_replica_read`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_replica_read-new-in-v40) is set to `closest-adaptive`.  |
| [`tidb_constraint_check_in_place_pessimistic`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_constraint_check_in_place_pessimistic-new-in-v630) | Newly added | Controls when TiDB checks [unique constraints](https://docs.pingcap.com/tidb/stable/constraints#pessimistic-transactions) in pessimistic transactions. |
| [`tidb_ddl_disk_quota`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_disk_quota-new-in-v630) | Newly added |  Takes effect only when [`tidb_ddl_enable_fast_reorg`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630) is enabled. It sets the usage limit of local storage during backfilling when creating an index.  |
| [`tidb_ddl_enable_fast_reorg`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630) | Newly added | Controls whether to enable the acceleration of `ADD INDEX` and `CREATE INDEX` DDL operations to improve the speed of backfilling when creating an index. |
| [`tidb_ddl_flashback_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_flashback_concurrency-new-in-v630) | Newly added |  Controls the concurrency of `flashback cluster`. The feature controlled by this variable is not fully functional in TiDB v6.3.0. Do not change the default value.  |
| [`tidb_enable_exchange_partition`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_exchange_partition) | Deprecated |  Controls whether to enable the [`exchange partitions with tables`](https://docs.pingcap.com/tidb/stable/partitioned-table#partition-management) feature. The default value is `ON`, that is, `exchange partitions with tables` is enabled by default.  |
| [`tidb_enable_foreign_key`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_foreign_key-new-in-v630) | Newly added |  Controls whether to enable the `FOREIGN KEY` feature. The feature controlled by this variable is not fully functional in TiDB v6.3.0. Do not change the default value.  |
| `tidb_enable_general_plan_cache` | Newly added |  Controls whether to enable the General Plan Cache feature. The feature controlled by this variable is not fully functional in TiDB v6.3.0. Do not change the default value.  |
| [`tidb_enable_metadata_lock`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_metadata_lock-new-in-v630)| Newly added | Specifies whether to enable the [Metadata lock](https://docs.pingcap.com/tidb/stable/metadata-lock) feature. |
| [`tidb_enable_null_aware_anti_join`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_null_aware_anti_join-new-in-v630) | Newly added |  Controls whether TiDB applies Null-Aware Hash Join when Anti Join is generated by subqueries led by special set operators `NOT IN` and `!= ALL`. |
| [`tidb_enable_pseudo_for_outdated_stats`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_pseudo_for_outdated_stats-new-in-v530) | Modified | Controls the behavior of the optimizer on using statistics of a table when the statistics are outdated. The default value changes from `ON` to `OFF`, which means the optimizer still keeps using the statistics of the table even if the statistics of this table are outdated. |
| [`tidb_enable_rate_limit_action`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_rate_limit_action) | Modified | Controls whether to enable the dynamic memory control feature for the operator that reads data. When this variable is set to `ON`, the memory usage might not be under the control of [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query). Therefore, the default value is changed from `ON` to `OFF`. |
| [`tidb_enable_tiflash_read_for_write_stmt`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_tiflash_read_for_write_stmt-new-in-v630) | Newly added |  Controls whether read requests in SQL write statements are pushed down to TiFlash. The feature controlled by this variable is not fully functional in TiDB v6.3.0. Do not change the default value.  |
| [`tidb_enable_unsafe_substitute`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_unsafe_substitute-new-in-v630) | Newly added | Controls whether to replace expressions with generated columns in an unsafe way. |
| `tidb_general_plan_cache_size` | Newly added | Controls the maximum number of execution plans that can be cached by General Plan Cache. The feature controlled by this variable is not fully functional in TiDB v6.3.0. Do not change the default value.  |
| [`tidb_last_plan_replayer_token`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_unsafe_substitute-new-in-v630) | Newly added | Read-only and used to obtain the result of the last `PLAN REPLAYER DUMP` execution in the current session. |
| [tidb_max_paging_size](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_paging_size-new-in-v630) | Newly added | This variable is used to set the minimum number of rows during the coprocessor paging request process. |
| [`tidb_opt_force_inline_cte`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_force_inline_cte-new-in-v630) | Newly added | Controls whether common table expressions (CTEs) in the entire session are inlined or not. The default value is `OFF`, which means that inlining CTE is not enforced by default. |
| [`tidb_opt_three_stage_distinct_agg`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_three_stage_distinct_agg-new-in-v630) | Newly added | Specifies whether to rewrite a `COUNT(DISTINCT)` aggregation into a three-stage aggregation in MPP mode. The default value is `ON`. |
| [`tidb_partition_prune_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_partition_prune_mode-new-in-v51) | Modified | Specifies whether to enable dynamic pruning. Since v6.3.0, the default value changes to `dynamic`. |
| [`tidb_rc_read_check_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_rc_read_check_ts-new-in-v600) | Modified | Used for optimizing the timestamp acquisition, which is suitable for scenarios with read-committed isolation level where read-write conflicts are rare. This feature is oriented to specific service workloads and might cause performance regression in other scenarios. For this reason, since v6.3.0, the scope of this variable changes from `GLOBAL \| SESSION` to `INSTANCE`. That means you can enable this feature for specific TiDB instances. |
| [`tidb_rc_write_check_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_rc_write_check_ts-new-in-v630)  | Newly added | Used for optimizing the acquisition of timestamps and is suitable for scenarios with few point-write conflicts in RC isolation level of pessimistic transactions. Enabling this variable can avoid the latency and overhead brought by obtaining the global timestamps during the execution of point-write statements |
| [`tiflash_fastscan`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_fastscan-new-in-v630) | Newly added | Controls whether to enable FastScan. If [FastScan](https://docs.pingcap.com/tidb/stable/tiflash/use-fastscan) is enabled (set to `ON`), TiFlash provides more efficient query performance, but does not guarantee the accuracy of the query results or data consistency. |
