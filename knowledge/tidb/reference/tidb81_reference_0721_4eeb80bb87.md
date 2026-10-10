# TiDB execution and optimizer enablement variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_enable_mutation_checker <span class="version-mark">New in v6.0.0</span> | System Variables > Variable reference > tidb_enable_new_cost_interface <span class="version-mark">New in v6.2.0</span> | System Variables > Variable reference > tidb_enable_new_only_full_group_by_check <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > tidb_enable_noop_functions <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_enable_noop_variables <span class="version-mark">New in v6.2.0</span> | System Variables > Variable reference > tidb_enable_null_aware_anti_join <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_enable_outer_join_reorder <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > `tidb_enable_inl_join_inner_multi_pattern` <span class="version-mark">New in v7.0.0</span> | System Variables > Variable reference > tidb_enable_ordered_result_mode | System Variables > Variable reference > tidb_enable_paging <span class="version-mark">New in v5.4.0</span> | System Variables > Variable reference > tidb_enable_parallel_apply <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_enable_parallel_hashagg_spill <span class="version-mark">New in v8.0.0</span> | System Variables > Variable reference > tidb_enable_pipelined_window_function | System Variables > Variable reference > tidb_enable_plan_cache_for_param_limit <span class="version-mark">New in v6.6.0</span>`
- Source Line Ranges: `2275-2437`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `dumpling`
- Topic Tags: `system-variables`, `session-scope`, `global-scope`, `optimizer`, `cost-model`, `group-by`, `noop-functions`, `noop-variables`, `anti-join`, `join-reorder`, `index-join`, `ordered-results`, `paging`, `coprocessor`, `parallel-apply`, `hashagg-spill`, `window-functions`, `plan-cache`, `experimental`, `upgrade-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0721_4eeb80bb87`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-enable-mutation-checker-span-class-version-mark-new-in-v6-0-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `901353018e850e7b26d17cd29302623424495f459f0431fad00ce6cc9936f56d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-enable-mutation-checker-span-class-version-mark-new-in-v6-0-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables that enable or change optimizer, execution, paging, noop behavior, mutation checking, or plan cache behavior, including upgrade-related default changes.
- Retrieval Keywords: tidb_enable_mutation_checker, TiDB mutation checker, consistency between data and indexes, DML statements rollback, tidb_enable_new_cost_interface, refactored Cost Model, tidb_enable_new_only_full_group_by_check, ONLY_FULL_GROUP_BY, tidb_enable_noop_functions, LOCK IN SHARE MODE, SQL_CALC_FOUND_ROWS, START TRANSACTION READ ONLY, SET TRANSACTION READ ONLY, GROUP BY <expr> ASC|DESC, tidb_enable_noop_variables, setting *variable_name* has no effect in TiDB, variable *variable_name* has no effect in TiDB, INFORMATION_SCHEMA.CLIENT_ERRORS_SUMMARY_GLOBAL, tidb_enable_null_aware_anti_join, Null Aware Hash Join, ANTI JOIN, NOT IN, != ALL, tidb_enable_outer_join_reorder, Join Reorder, Outer Join, tidb_enable_inl_join_inner_multi_pattern, Index Join, Selection, Projection, tidb_enable_ordered_result_mode, sort the final output result automatically, tidb_enable_paging, coprocessor requests, IndexLookup, Limit, Unified read pool CPU, Dumpling, tidb_min_paging_size, tidb_max_paging_size, tidb_enable_parallel_apply, Apply operator, correlated subqueries, tidb_executor_concurrency, tidb_enable_parallel_hashagg_spill, parallel HashAgg, disk spill, experimental, tidb_enable_pipelined_window_function, pipeline execution algorithm, window functions, tidb_enable_plan_cache_for_param_limit, Prepared Plan Cache, LIMIT ?
- Follow-up Guidance: The chunk also points to related identifiers and references such as SET_VAR applicability, INFORMATION_SCHEMA.CLIENT_ERRORS_SUMMARY_GLOBAL, tidb_executor_concurrency, tidb_min_paging_size, tidb_max_paging_size, Join Reorder, window functions, and Troubleshoot Inconsistency Between Data and Indexes.
- Classification Note: This is a reference chunk because it enumerates TiDB system variables with scope, persistence, type, default values, and exact behavior for execution and optimizer features.

## Official Source Content

### tidb_enable_mutation_checker New in v6.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether to enable TiDB mutation checker, which is a tool used to check consistency between data and indexes during the execution of DML statements. If the checker returns an error for a statement, TiDB rolls back the execution of the statement. Enabling this variable causes a slight increase in CPU usage. For more information, see [Troubleshoot Inconsistency Between Data and Indexes](https://docs.pingcap.com/tidb/stable/troubleshoot-data-inconsistency-errors).
- For new clusters of v6.0.0 or later versions, the default value is `ON`. For existing clusters that upgrade from versions earlier than v6.0.0, the default value is `OFF`.
### tidb_enable_new_cost_interface New in v6.2.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- TiDB v6.2.0 refactors the implementation of previous cost model. This variable controls whether to enable the refactored Cost Model implementation.
- This variable is enabled by default because the refactored Cost Model uses the same cost formula as before, which does not change the plan decision.
- If your cluster is upgraded from v6.1 to v6.2, this variable remains `OFF`, and it is recommended to enable it manually. If your cluster is upgraded from a version earlier than v6.1, this variable sets to `ON` by default.
### tidb_enable_new_only_full_group_by_check New in v6.1.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable controls the behavior when TiDB performs the `ONLY_FULL_GROUP_BY` check. For detailed information about `ONLY_FULL_GROUP_BY`, see the [MySQL documentation](https://dev.mysql.com/doc/refman/8.0/en/sql-mode.html#sqlmode_only_full_group_by). In v6.1.0, TiDB handles this check more strictly and correctly.
- To avoid potential compatibility issues caused by version upgrades, the default value of this variable is `OFF` in v6.1.0.
### tidb_enable_noop_functions New in v4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `OFF`
- Possible values: `OFF`, `ON`, `WARN`
- By default, TiDB returns an error when you attempt to use the syntax for functionality that is not yet implemented. When the variable value is set to `ON`, TiDB silently ignores such cases of unavailable functionality, which is helpful if you cannot make changes to the SQL code.
- Enabling `noop` functions controls the following behaviors:
    * `LOCK IN SHARE MODE` syntax
    * `SQL_CALC_FOUND_ROWS` syntax
    * `START TRANSACTION READ ONLY` and `SET TRANSACTION READ ONLY` syntax
    * The `tx_read_only`, `transaction_read_only`, `offline_mode`, `super_read_only`, `read_only` and `sql_auto_is_null` system variables
    * `GROUP BY <expr> ASC|DESC` syntax

> **Warning:**
>
> Only the default value of `OFF` can be considered safe. Setting `tidb_enable_noop_functions=1` might lead to unexpected behaviors in your application, because it permits TiDB to ignore certain syntax without providing an error. For example, the syntax `START TRANSACTION READ ONLY` is permitted, but the transaction remains in read-write mode.
### tidb_enable_noop_variables New in v6.2.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `ON`
- If you set the variable value to `OFF`, TiDB behaves as follows:
    * When you use `SET` to set a `noop` variable, TiDB returns the `"setting *variable_name* has no effect in TiDB"` warning.
    * The result of `SHOW [SESSION | GLOBAL] VARIABLES` does not include `noop` variables.
    * When you use `SELECT` to read a `noop` variable, TiDB returns the `"variable *variable_name* has no effect in TiDB"` warning.
- To check whether a TiDB instance has set and read the `noop` variable, you can use the `SELECT * FROM INFORMATION_SCHEMA.CLIENT_ERRORS_SUMMARY_GLOBAL;` statement.
### tidb_enable_null_aware_anti_join New in v6.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: Before v7.0.0, the default value is `OFF`. Starting from v7.0.0, the default value is `ON`.
- Type: Boolean
- This variable controls whether TiDB applies Null Aware Hash Join when ANTI JOIN is generated by subqueries led by special set operators `NOT IN` and `!= ALL`.
- When you upgrade from an earlier version to a v7.0.0 or later cluster, the feature is automatically enabled, meaning that this variable is set to `ON`.
### tidb_enable_outer_join_reorder New in v6.1.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `ON`
- Since v6.1.0, the [Join Reorder](https://docs.pingcap.com/tidb/stable/join-reorder) algorithm of TiDB supports Outer Join. This variable controls whether TiDB enables the Join Reorder's support for Outer Join.
- If your cluster is upgraded from an earlier version of TiDB, note the following:

    - If the TiDB version before the upgrade is earlier than v6.1.0, the default value of this variable after the upgrade is `ON`.
    - If the TiDB version before the upgrade is v6.1.0 or later, the default value of the variable after the upgrade follows the value before the upgrade.
### `tidb_enable_inl_join_inner_multi_pattern` New in v7.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable controls whether Index Join is supported when the inner table has `Selection` or `Projection` operators on it. The default value `OFF` means that Index Join is not supported in this scenario.
### tidb_enable_ordered_result_mode

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- Specifies whether to sort the final output result automatically.
- For example, with this variable enabled, TiDB processes `SELECT a, MAX(b) FROM t GROUP BY a` as `SELECT a, MAX(b) FROM t GROUP BY a ORDER BY a, MAX(b)`.
### tidb_enable_paging New in v5.4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `ON`
- This variable controls whether to use the method of paging to send coprocessor requests. For TiDB versions in [v5.4.0, v6.2.0), this variable only takes effect on the `IndexLookup` operator; for v6.2.0 and later, this variable takes effect globally. Starting from v6.4.0, the default value of this variable is changed from `OFF` to `ON`.
- User scenarios:

    - In all OLTP scenarios, it is recommended to use the method of paging.
    - For read queries that use `IndexLookup` and `Limit` and that `Limit` cannot be pushed down to `IndexScan`, there might be high latency for the read queries and high usage for TiKV `Unified read pool CPU`. In such cases, because the `Limit` operator only requires a small set of data, if you set [`tidb_enable_paging`](#tidb_enable_paging-new-in-v540) to `ON`, TiDB processes less data, which reduces query latency and resource consumption.
    - In scenarios such as data export using [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) and full table scan, enabling paging can effectively reduce the memory consumption of TiDB processes.

> **Note:**
>
> In OLAP scenarios where TiKV is used as the storage engine instead of TiFlash, enabling paging might cause performance regression in some cases. If the regression occurs, consider using this variable to disable paging, or using the [`tidb_min_paging_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_min_paging_size-new-in-v620) and [`tidb_max_paging_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_paging_size-new-in-v630) variables to adjust the range of rows for paging size.
### tidb_enable_parallel_apply New in v5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to enable concurrency for the `Apply` operator. The number of concurrencies is controlled by the `tidb_executor_concurrency` variable. The `Apply` operator processes correlated subqueries and has no concurrency by default, so the execution speed is slow. Setting this variable value to `1` can increase concurrency and speed up execution. Currently, concurrency for `Apply` is disabled by default.
### tidb_enable_parallel_hashagg_spill New in v8.0.0

> **Warning:**
>
> Currently, the feature controlled by this variable is experimental. It is not recommended that you use it in production environments. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON` for v8.1.0; `OFF` for v8.1.1 and later 8.1 patch versions
- This variable controls whether TiDB supports disk spill for the parallel HashAgg algorithm. When it is `ON`, disk spill can be triggered for the parallel HashAgg algorithm. This variable will be deprecated after this feature is generally available in a future release.
### tidb_enable_pipelined_window_function

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable specifies whether to use the pipeline execution algorithm for [window functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions).
### tidb_enable_plan_cache_for_param_limit New in v6.6.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether Prepared Plan Cache caches execution plans with a variable as the `LIMIT` parameter (`LIMIT ?`). The default value is `ON`, which means Prepared Plan Cache supports caching such execution plans. Note that Prepared Plan Cache does not support caching execution plans with a variable that is greater than 10000.
