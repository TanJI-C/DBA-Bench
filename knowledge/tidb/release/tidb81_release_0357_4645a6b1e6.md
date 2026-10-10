# Compatibility changes for system variables in 6.4.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.4.0.md`
- Source Title: `TiDB 6.4.0 Release Notes`
- Source Heading Path: `TiDB 6.4.0 Release Notes > Compatibility changes > System variables`
- Source Line Ranges: `277-306`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `system-variables`, `compatibility-changes`, `defaults`, `scopes`, `memory-control`, `statistics`, `optimizer`, `prepared-plan-cache`, `clustered-index`, `paging`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0357_4645a6b1e6`
- Source ID: `tidb-docs-8.1:releases/release-6.4.0.md#system-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `faf946994473774390c01d0b43f9a7484008381827e85668caf18e82165d71cf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.4.0#system-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.4.0 compatibility changes and newly added system variables, especially default value changes, scope changes, and variables related to memory control, statistics loading, prepared plan cache, clustered index, paging, external timestamp read, and optimizer behavior.
- Retrieval Keywords: TiDB 6.4.0 system variables, Compatibility changes, max_execution_time read-only statements, tidb_constraint_check_in_place_pessimistic GLOBAL scope removed, pessimistic-txn.constraint-check-in-place-pessimistic, tidb_ddl_flashback_concurrency, FLASHBACK CLUSTER TO TIMESTAMP, tidb_enable_clustered_index default ON, tidb_enable_paging default ON, tidb_enable_prepared_plan_cache SESSION scope, tidb_prepared_plan_cache_size SESSION scope, tidb_memory_usage_alarm_ratio default 0.7, tidb_opt_agg_push_down GLOBAL scope, tidb_stats_load_sync_wait default 100, tidb_stats_load_pseudo_timeout default ON, last_sql_use_alloc, tidb_auto_analyze_partition_batch_size, tidb_enable_external_ts_read, tidb_external_ts, tidb_enable_gogc_tuner, tidb_enable_reuse_chunk, tidb_enable_prepared_plan_cache_memory_monitor, tidb_gogc_tuner_threshold, tidb_memory_usage_alarm_keep_record_num, tidb_opt_prefix_index_single_scan, tidb_opt_range_max_size, tidb_server_memory_limit, tidb_server_memory_limit_gc_trigger, tidb_server_memory_limit_sess_min_size
- Follow-up Guidance: This chunk also lists each affected variable’s change type and description, including defaults, scope changes, and the related feature or statement it controls.
- Classification Note: This is a release-note compatibility section for TiDB system variables in 6.4.0, covering modified variables and newly added variables with their documented behavior changes.

## Official Source Content

### System variables

| Variable name | Change type | Description |
|--------|------------------------------|------|
| [`max_execution_time`](https://docs.pingcap.com/tidb/stable/system-variables#max_execution_time) | Modified | Before v6.4.0, this variable takes effect on all types of statements. Starting from v6.4.0, this variable only controls the maximum execution time of read-only statements. |
| [`tidb_constraint_check_in_place_pessimistic`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_constraint_check_in_place_pessimistic-new-in-v630) | Modified | Removes the GLOBAL scope and allows you to modify the default value using the [`pessimistic-txn.constraint-check-in-place-pessimistic`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#constraint-check-in-place-pessimistic-new-in-v640) configuration item. This variable controls when TiDB checks the unique constraints in pessimistic transactions. |
| [`tidb_ddl_flashback_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_flashback_concurrency-new-in-v630) | Modified | Takes effect starting from v6.4.0 and controls the concurrency of [`FLASHBACK CLUSTER TO TIMESTAMP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster). The default value is `64`. |
| [`tidb_enable_clustered_index`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_clustered_index-new-in-v50) | Modified | Changes the default value from `INT_ONLY` to `ON`, meaning that primary keys are created as clustered indexes by default.|
| [`tidb_enable_paging`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_paging-new-in-v540) | Modified | Changes the default value from `OFF` to `ON`, meaning that the method of paging to send coprocessor requests is used by default. |
| [`tidb_enable_prepared_plan_cache`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_prepared_plan_cache-new-in-v610) | Modified | Adds the SESSION scope. This variable controls whether to enable [Prepared Plan Cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache). |
| [`tidb_memory_usage_alarm_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_memory_usage_alarm_ratio) | Modified | Changes the default value from `0.8` to `0.7`. This variable controls the memory usage ratio that triggers the tidb-server memory alarm. |
| [`tidb_opt_agg_push_down`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_agg_push_down) | Modified | Adds the GLOBAL scope. This variable controls whether the optimizer executes the optimization operation of pushing down the aggregate function to the position before Join, Projection, and UnionAll. |
| [`tidb_prepared_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_prepared_plan_cache_size-new-in-v610) | Modified | Adds the SESSION scope. This variable controls the maximum number of plans that can be cached in a session. |
| [`tidb_stats_load_sync_wait`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_stats_load_sync_wait-new-in-v540) | Modified | Changes the default value from `0` to `100`, meaning that the SQL execution can wait for at most 100 milliseconds by default to synchronously load complete column statistics. |
| [`tidb_stats_load_pseudo_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_stats_load_pseudo_timeout-new-in-v540) | Modified | Changes the default value from `OFF` to `ON`, meaning that the SQL optimization gets back to using pseudo statistics after reaching the timeout of synchronously loading complete column statistics. |
| [`last_sql_use_alloc`](https://docs.pingcap.com/tidb/stable/system-variables#last_sql_use_alloc-new-in-v640) | Newly added | Shows whether the previous statement uses a cached chunk object (chunk allocation). This variable is read-only and the default value is `OFF`. |
| [`tidb_auto_analyze_partition_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_auto_analyze_partition_batch_size-new-in-v640) | Newly added | Specifies the number of partitions that TiDB can [automatically analyzes](https://docs.pingcap.com/tidb/stable/statistics#automatic-update) at a time when analyzing a partitioned table (which means automatically collecting statistics on a partitioned table). The default value is `1`.|
| [`tidb_enable_external_ts_read`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_external_ts_read-new-in-v640) | Newly added | Controls whether TiDB reads data with the timestamp specified by [`tidb_external_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_external_ts-new-in-v640). The default value is `OFF`. |
| [`tidb_enable_gogc_tuner`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_gogc_tuner-new-in-v640) | Newly added | Controls whether to enable GOGC Tuner. The default value is `ON`. |
| [`tidb_enable_reuse_chunk`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_reuse_chunk-new-in-v640) | Newly added | Controls whether TiDB enables chunk objects cache. The default value is `ON`, meaning that TiDB prefers to use the cached chunk object and only requests from the system if the requested object is not in the cache. If the value is `OFF`, TiDB requests chunk objects from the system directly. |
| [`tidb_enable_prepared_plan_cache_memory_monitor`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_prepared_plan_cache_memory_monitor-new-in-v640) | Newly added | Controls whether to count the memory consumed by the execution plans cached in the Prepared Plan Cache. The default value is `ON`.|
| [`tidb_external_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_external_ts-new-in-v640) | Newly added | The default value is `0`. If [`tidb_enable_external_ts_read`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_external_ts_read-new-in-v640) is set to `ON`, TiDB reads data with the timestamp specified by this variable.|
| [`tidb_gogc_tuner_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gogc_tuner_threshold-new-in-v640) | Newly added | Specifies the maximum memory threshold for tuning GOGC. When the memory exceeds this threshold, GOGC Tuner stops working. The default value is `0.6`. |
| [`tidb_memory_usage_alarm_keep_record_num`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_memory_usage_alarm_keep_record_num-new-in-v640) | Newly added | When the tidb-server memory usage exceeds the memory alarm threshold and triggers an alarm, TiDB only retains the status files generated during the recent 5 alarms by default. You can adjust this number with this variable. |
| [`tidb_opt_prefix_index_single_scan`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_prefix_index_single_scan-new-in-v640) | Newly added | Controls whether the TiDB optimizer pushes down some filter conditions to the prefix index to avoid unnecessary table lookup and to improve query performance. The default value is `ON`. |
| [`tidb_opt_range_max_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_range_max_size-new-in-v640) | Newly added | Specifies the upper limit of memory usage for the optimizer to construct a scan range. The default value is `67108864` (64 MiB). |
| [`tidb_server_memory_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit-new-in-v640) | Newly added | Controls the upper limit of memory usage for the optimizer to build scan ranges (experimental). The default value is `0`, meaning that there is no memory limit. |
| [`tidb_server_memory_limit_gc_trigger`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit_gc_trigger-new-in-v640) | Newly added | Controls the threshold at which TiDB tries to trigger GC (experimental). The default value is `70%`. |
| [`tidb_server_memory_limit_sess_min_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit_sess_min_size-new-in-v640) | Newly added | After you enable the memory limit, TiDB will terminate the SQL statement with the highest memory usage on the current instance. This variable specifies the minimum memory usage of the SQL statement to be terminated. The default value is `134217728` (128 MiB).|
