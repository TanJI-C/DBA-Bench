# Plan cache, memory control, and execution diagnostics variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_enable_plan_cache_for_subquery <span class="version-mark">New in v7.0.0</span> | System Variables > Variable reference > tidb_enable_plan_replayer_capture | System Variables > Variable reference > tidb_enable_plan_replayer_continuous_capture <span class="version-mark">New in v7.0.0</span> | System Variables > Variable reference > tidb_enable_prepared_plan_cache <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > tidb_enable_prepared_plan_cache_memory_monitor <span class="version-mark">New in v6.4.0</span> | System Variables > Variable reference > tidb_enable_pseudo_for_outdated_stats <span class="version-mark">New in v5.3.0</span> | System Variables > Variable reference > tidb_enable_rate_limit_action | System Variables > Variable reference > tidb_enable_resource_control <span class="version-mark">New in v6.6.0</span> | System Variables > Variable reference > tidb_enable_reuse_chunk <span class="version-mark">New in v6.4.0</span> | System Variables > Variable reference > tidb_enable_slow_log | System Variables > Variable reference > tidb_enable_tmp_storage_on_oom | System Variables > Variable reference > tidb_enable_stmt_summary <span class="version-mark">New in v3.0.4</span>`
- Source Line Ranges: `2438-2616`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `cloud`, `sql`
- Topic Tags: `system-variables`, `plan-cache`, `plan-replayer`, `prepared-statements`, `statistics`, `memory-control`, `oom`, `resource-control`, `chunk-cache`, `slow-log`, `statement-summary`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0722_8b6a1d5122`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-enable-plan-cache-for-subquery-span-class-version-mark-new-in-v7-0-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c6b399f618de889490773da139c6bbcee94f8655193deaff2beab6bff8d749c9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-enable-plan-cache-for-subquery-span-class-version-mark-new-in-v7-0-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB system variables for plan cache behavior, plan replayer capture, outdated statistics handling, memory control, chunk cache, slow log, temporary storage on OOM, resource control, or statement summary.
- Retrieval Keywords: tidb_enable_plan_cache_for_subquery, tidb_enable_plan_replayer_capture, PLAN REPLAYER CAPTURE, tidb_enable_plan_replayer_continuous_capture, PLAN REPLAYER CONTINUOUS CAPTURE, tidb_enable_prepared_plan_cache, Prepared Plan Cache, tidb_enable_prepared_plan_cache_memory_monitor, memory management of Prepared Plan Cache, tidb_enable_pseudo_for_outdated_stats, ANALYZE, pseudo statistics, pseudo-estimate-ratio, tidb_enable_rate_limit_action, tidb_mem_quota_query, tidb_distsql_scan_concurrency, tidb_enable_resource_control, resource groups, tidb_enable_reuse_chunk, chunk objects cache, tidb_enable_slow_log, tidb_enable_tmp_storage_on_oom, oom-use-tmp-storage, tidb_enable_stmt_summary, information_schema.STATEMENTS_SUMMARY, statement summary
- Follow-up Guidance: The source also states scope, default value, whether each variable persists to the cluster, whether it applies to SET_VAR, and notes such as TiDB Cloud restrictions or previous tidb.toml and configuration item names for some variables.
- Classification Note: This chunk is classified as a reference because it is a variable reference listing exact system variable names and their documented scope, defaults, behavior, and related notes.

## Official Source Content

### tidb_enable_plan_cache_for_subquery New in v7.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether Prepared Plan Cache caches queries that contain subqueries.
### tidb_enable_plan_replayer_capture

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether to enable the `PLAN REPLAYER CAPTURE` feature. The default value `ON` means to enable the `PLAN REPLAYER CAPTURE` feature.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether to enable the [`PLAN REPLAYER CAPTURE` feature](https://docs.pingcap.com/tidb/stable/sql-plan-replayer#use-plan-replayer-capture-to-capture-target-plans). The default value `ON` means to enable the `PLAN REPLAYER CAPTURE` feature.
### tidb_enable_plan_replayer_continuous_capture New in v7.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to enable the `PLAN REPLAYER CONTINUOUS CAPTURE` feature. The default value `OFF` means to disable the feature.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to enable the [`PLAN REPLAYER CONTINUOUS CAPTURE` feature](https://docs.pingcap.com/tidb/stable/sql-plan-replayer#use-plan-replayer-continuous-capture). The default value `OFF` means to disable the feature.
### tidb_enable_prepared_plan_cache New in v6.1.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `ON`
- Determines whether to enable [Prepared Plan Cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache). When it is enabled, the execution plans of `Prepare` and `Execute` are cached so that the subsequent executions skip optimizing the execution plans, which brings performance improvement.
- This setting was previously a `tidb.toml` option (`prepared-plan-cache.enabled`), but changed to a system variable starting from TiDB v6.1.0.
### tidb_enable_prepared_plan_cache_memory_monitor New in v6.4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `ON`
- This variable controls whether to count the memory consumed by the execution plans cached in the Prepared Plan Cache. For details, see [Memory management of Prepared Plan Cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache#memory-management-of-prepared-plan-cache).
### tidb_enable_pseudo_for_outdated_stats New in v5.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable controls the behavior of the optimizer on using statistics of a table when the statistics are outdated.

- The optimizer determines whether the statistics of a table is outdated in this way: since the last time `ANALYZE` is executed on a table to get the statistics, if 80% of the table rows are modified (the modified row count divided by the total row count), the optimizer determines that the statistics of this table is outdated. You can change this ratio using the [`pseudo-estimate-ratio`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#pseudo-estimate-ratio) configuration.

- The optimizer determines whether the statistics of a table is outdated in this way: since the last time `ANALYZE` is executed on a table to get the statistics, if 80% of the table rows are modified (the modified row count divided by the total row count), the optimizer determines that the statistics of this table is outdated.

- By default (with the variable value `OFF`), when the statistics of a table is outdated, the optimizer still keeps using the statistics of the table. If you set the variable value to `ON`, the optimizer determines that the statistics of the table is no longer reliable except for the total row count. Then, the optimizer uses the pseudo statistics.
- If the data on a table is frequently modified without executing `ANALYZE` on this table in time, to keep the execution plan stable, it is recommended to set the variable value to `OFF`.
### tidb_enable_rate_limit_action

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to enable the dynamic memory control feature for the operator that reads data. By default, this operator enables the maximum number of threads that [`tidb_distsql_scan_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_distsql_scan_concurrency) allows to read data. When the memory usage of a single SQL statement exceeds [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query) each time, the operator that reads data stops one thread.

- When the operator that reads data has only one thread left and the memory usage of a single SQL statement constantly exceeds [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query), this SQL statement triggers other memory control behaviors, such as [spilling data to disk](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_tmp_storage_on_oom).
- This variable controls memory usage effectively when an SQL statement only reads data. If computing operations (such as join or aggregation operations) are required, memory usage might not be under the control of `tidb_mem_quota_query`, which increases the risk of OOM.

- When the operator that reads data has only one thread left and the memory usage of a single SQL statement continues to exceed [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query), this SQL statement triggers other memory control behaviors, such as spilling data to disk.
### tidb_enable_resource_control New in v6.6.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `ON`
- Type: Boolean
- This variable is a switch for [the resource control feature](https://docs.pingcap.com/tidb/stable/tidb-resource-control). When this variable is set to `ON`, the TiDB cluster can isolate application resources based on resource groups.
### tidb_enable_reuse_chunk New in v6.4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `ON`
- Value options: `OFF`, `ON`
- This variable controls whether TiDB enables chunk objects cache. If the value is `ON`, TiDB prefers to use the cached chunk object and only requests from the system if the requested object is not in the cache. If the value is `OFF`, TiDB requests chunk objects from the system directly.
### tidb_enable_slow_log

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether to enable the slow log feature.
### tidb_enable_tmp_storage_on_oom

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `ON`
- Value options: `OFF`, `ON`
- Controls whether to enable the temporary storage for some operators when a single SQL statement exceeds the memory quota specified by the system variable [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query).
- Before v6.3.0, you can enable or disable this feature by using the TiDB configuration item `oom-use-tmp-storage`. After upgrading the cluster to v6.3.0 or a later version, the TiDB cluster will initialize this variable using the value of `oom-use-tmp-storage` automatically. After that, changing the value of `oom-use-tmp-storage` **does not** take effect anymore.
### tidb_enable_stmt_summary New in v3.0.4

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether to enable the statement summary feature. If enabled, SQL execution information like time consumption is recorded to the `information_schema.STATEMENTS_SUMMARY` system table to identify and troubleshoot SQL performance issues.
