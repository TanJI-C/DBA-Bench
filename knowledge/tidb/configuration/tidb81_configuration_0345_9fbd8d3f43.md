# Recommended system variables for performance optimization

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-performance-tuning-config.md`
- Source Title: `Configure TiDB for Optimal Performance`
- Source Heading Path: `Configure TiDB for Optimal Performance > Key settings for common workloads > System variables`
- Source Line Ranges: `36-82`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tiflash`, `tikv`
- Topic Tags: `system-variables`, `sql-settings`, `plan-cache`, `optimizer-fix-control`, `runtime-filter`, `mpp`, `cte-pushdown`, `read-committed`, `linearizability`, `pd-follower`, `experimental-features`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0345_9fbd8d3f43`
- Source ID: `tidb-docs-8.1:tidb-performance-tuning-config.md#system-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8b382f06b6257d344aa2aa27f14b2a0f88c09a568947490ffce613beee26e281`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-performance-tuning-config#system-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-performance-tuning-config.md

## Retrieval Guidance

- Use When: Use this chunk when searching for the exact SQL system variables and optimizer fix controls recommended for TiDB performance optimization in common workloads.
- Retrieval Keywords: System variables, SET GLOBAL tidb_session_plan_cache_size=200, SET GLOBAL tidb_enable_non_prepared_plan_cache=on, SET GLOBAL tidb_ignore_prepared_cache_close_stmt=on, SET GLOBAL tidb_stats_load_sync_wait=2000, SET GLOBAL tidb_enable_inl_join_inner_multi_pattern=on, SET GLOBAL tidb_opt_limit_push_down_threshold=10000, SET GLOBAL tidb_opt_derive_topn=on, SET GLOBAL tidb_runtime_filter_mode=LOCAL, SET GLOBAL tidb_opt_enable_mpp_shared_cte_execution=on, SET GLOBAL tidb_rc_read_check_ts=on, SET GLOBAL tidb_guarantee_linearizability=off, SET GLOBAL pd_enable_follower_handle_region=on, SET GLOBAL tidb_opt_fix_control = '44262:ON,44389:ON,44823:10000,44830:ON,44855:ON,52869:ON', 44262:ON, 44389:ON, 44823:10000, 44830:ON, 44855:ON, 52869:ON, Runtime Filter, Deriving TopN or Limit from window functions, Common Table Expressions CTE pushdown to TiFlash, PD Follower feature, Dynamic pruning mode, IndexRangeScan, PointGet, IndexJoin, index merge automatically
- Follow-up Guidance: The source also explains the impact and notes for each variable, including plan cache behavior, statistics loading wait time, runtime filter local mode, CTE pushdown to TiFlash, read-committed timestamp checking, linearizability trade-off, PD follower handling, and each optimizer fix control entry.
- Classification Note: This chunk is classified as configuration because the official content is a list of exact SET GLOBAL statements and descriptions of system variables and optimizer control options for performance tuning.

## Official Source Content

### System variables

Execute the following SQL commands to apply the recommended settings:

```sql
SET GLOBAL tidb_session_plan_cache_size=200; 
SET GLOBAL tidb_enable_non_prepared_plan_cache=on;
SET GLOBAL tidb_ignore_prepared_cache_close_stmt=on;
SET GLOBAL tidb_stats_load_sync_wait=2000;
SET GLOBAL tidb_enable_inl_join_inner_multi_pattern=on;
SET GLOBAL tidb_opt_limit_push_down_threshold=10000;
SET GLOBAL tidb_opt_derive_topn=on;
SET GLOBAL tidb_runtime_filter_mode=LOCAL;
SET GLOBAL tidb_opt_enable_mpp_shared_cte_execution=on;
SET GLOBAL tidb_rc_read_check_ts=on;
SET GLOBAL tidb_guarantee_linearizability=off;
SET GLOBAL pd_enable_follower_handle_region=on;
SET GLOBAL tidb_opt_fix_control = '44262:ON,44389:ON,44823:10000,44830:ON,44855:ON,52869:ON';
```

The following table outlines the impact of specific system variable configurations:

| System variable | Description | Note |
| ---------| ---- | ----|
| [`tidb_session_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_session_plan_cache_size-new-in-v710) | Increase the maximum number of plans that can be cached from the default `100` to `200`. This improves performance for workloads with many prepared statement patterns. | Increasing this value can lead to higher memory usage for the session plan cache. |
| [`tidb_enable_non_prepared_plan_cache`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_non_prepared_plan_cache)| Enable the [Non-prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache) feature to reduce compile costs for applications that do not use prepared statements. | N/A |
| [`tidb_ignore_prepared_cache_close_stmt`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ignore_prepared_cache_close_stmt-new-in-v600)| Cache plans for applications that use prepared statements but close the plan after each execution. | N/A |
| [`tidb_stats_load_sync_wait`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_stats_load_sync_wait-new-in-v540)| Increase the timeout for synchronously loading statistics from the default 100 milliseconds to 2 seconds. This ensures TiDB loads the necessary statistics before query compilation. | Increasing this value leads to a longer synchronization wait time before query compilation. |
| [`tidb_enable_inl_join_inner_multi_pattern`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_inl_join_inner_multi_pattern-new-in-v700) | Enable Index Join support when the inner table has `Selection` or `Projection` operators on it. | N/A | 
| [`tidb_opt_limit_push_down_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_limit_push_down_threshold)| Increase the threshold that determines whether to push the `Limit` or `TopN` operator down to TiKV. | When multiple index options exist, increasing this variable makes the optimizer favor indexes that can optimize the `ORDER BY` and `Limit` operators. |
| [`tidb_opt_derive_topn`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_derive_topn-new-in-v700)| Enable the optimization rule of [Deriving TopN or Limit from window functions](https://docs.pingcap.com/tidb/stable/derive-topn-from-window). | This is limited to the `ROW_NUMBER()` window function. | 
| [`tidb_runtime_filter_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_runtime_filter_mode-new-in-v720)| Enable [Runtime Filter](https://docs.pingcap.com/tidb/stable/runtime-filter#runtime-filter-mode) in the local mode to improve hash join efficiency. | The variable is introduced in v7.2.0 and is disabled by default for safety. | 
| [`tidb_opt_enable_mpp_shared_cte_execution`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_mpp_shared_cte_execution-new-in-v720)| Enable non-recursive [Common Table Expressions (CTE)](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-with) pushdown to TiFlash. | This is an experimental feature. | 
| [`tidb_rc_read_check_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_rc_read_check_ts-new-in-v600)| For the read-committed isolation level, enabling this variable avoids the latency and cost of getting the global timestamp and optimizes transaction-level read latency. | This feature is incompatible with the Repeatable Read isolation level. | 
| [`tidb_guarantee_linearizability`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_guarantee_linearizability-new-in-v50)| Improve performance by skipping the commit timestamp fetch from the PD server. | This sacrifices linearizability in favor of performance. Only causal consistency is guaranteed. It is not suitable for scenarios requiring strict linearizability. |
| [`pd_enable_follower_handle_region`](https://docs.pingcap.com/tidb/stable/system-variables#pd_enable_follower_handle_region-new-in-v760)| Activate the PD Follower feature, allowing PD followers to process Region requests. This helps distribute load evenly across all PD servers and reduces CPU pressure on the PD leader. | This is an experimental feature. Test in non-production environments. |
| [`tidb_opt_fix_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_fix_control-new-in-v653-and-v710) | Enable advanced query optimization strategies to improve performance through additional optimization rules and heuristics. | Test thoroughly in your environment, as performance improvements vary by workload. |

The following describes the optimizer control configurations that enable additional optimizations:

- [`44262:ON`](https://docs.pingcap.com/tidb/stable/optimizer-fix-controls#44262-new-in-v653-and-v720): Use [Dynamic pruning mode](https://docs.pingcap.com/tidb/stable/partitioned-table#dynamic-pruning-mode) to access the partitioned table when the [GlobalStats](https://docs.pingcap.com/tidb/stable/statistics#collect-statistics-of-partitioned-tables-in-dynamic-pruning-mode) are missing.
- [`44389:ON`](https://docs.pingcap.com/tidb/stable/optimizer-fix-controls#44389-new-in-v653-and-v720): For filters such as `c = 10 and (a = 'xx' or (a = 'kk' and b = 1))`, build more comprehensive scan ranges for `IndexRangeScan`.
- [`44823:10000`](https://docs.pingcap.com/tidb/stable/optimizer-fix-controls#44823-new-in-v730): To save memory, plan cache does not cache queries with parameters exceeding the specified number of this variable. Increase plan cache parameter limit from `200` to `10000` to make plan cache available for query with long in-lists.
- [`44830:ON`](https://docs.pingcap.com/tidb/stable/optimizer-fix-controls#44830-new-in-v657-and-v730): Plan cache is allowed to cache execution plans with the `PointGet` operator generated during physical optimization.
- [`44855:ON`](https://docs.pingcap.com/tidb/stable/optimizer-fix-controls#44855-new-in-v654-and-v730): The optimizer selects `IndexJoin` when the `Probe` side of an `IndexJoin` operator contains a `Selection` operator.
- [`52869:ON`](https://docs.pingcap.com/tidb/stable/optimizer-fix-controls#52869-new-in-v810): The optimizer chooses index merge automatically if the optimizer can choose the single index scan method (other than full table scan) for a query plan.
