# TiDB execution, index access, isolation read, and session info variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_hashagg_partial_concurrency | System Variables > Variable reference > tidb_historical_stats_duration <span class="version-mark">New in v6.6.0</span> | System Variables > Variable reference > tidb_idle_transaction_timeout <span class="version-mark">New in v7.6.0</span> | System Variables > Variable reference > tidb_ignore_prepared_cache_close_stmt <span class="version-mark">New in v6.0.0</span> | System Variables > Variable reference > tidb_ignore_inlist_plan_digest <span class="version-mark">New in v7.6.0</span> | System Variables > Variable reference > tidb_index_join_batch_size | System Variables > Variable reference > tidb_index_join_double_read_penalty_cost_rate <span class="version-mark">New in v6.6.0</span> | System Variables > Variable reference > tidb_index_lookup_concurrency | System Variables > Variable reference > tidb_index_lookup_join_concurrency | System Variables > Variable reference > tidb_index_merge_intersection_concurrency <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > tidb_index_lookup_size | System Variables > Variable reference > tidb_index_serial_scan_concurrency | System Variables > Variable reference > tidb_init_chunk_size | System Variables > Variable reference > tidb_isolation_read_engines <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_last_ddl_info <span class="version-mark">New in v6.0.0</span> | System Variables > Variable reference > tidb_last_query_info <span class="version-mark">New in v4.0.14</span>`
- Source Line Ranges: `3208-3405`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`, `tiflash`, `shared`
- Topic Tags: `system-variables`, `execution-concurrency`, `index-lookup`, `hash-aggregation`, `plan-digest`, `prepared-plan-cache`, `historical-stats`, `idle-transactions`, `read-engines`, `session-metadata`, `ddl`, `dml`, `memory`, `deprecated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0725_e0783dd349`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-hashagg-partial-concurrency`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `544a035e151af7a07e91d8b0bda1b67fb4d909f52c5a44941e066b96dbe04484`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-hashagg-partial-concurrency
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables for execution concurrency, index lookup and index join behavior, isolation read engines, historical statistics retention, idle transaction timeout, prepared cache close handling, plan digest behavior for IN lists, initial chunk size, or read-only session metadata about the last DDL or DML statement.
- Retrieval Keywords: tidb_hashagg_partial_concurrency, tidb_executor_concurrency, hash aggregation partial phase, tidb_historical_stats_duration, historical statistics retained in the storage, tidb_idle_transaction_timeout, idle timeout for transactions in a user session, tidb_ignore_prepared_cache_close_stmt, COM_STMT_CLOSE, DEALLOCATE PREPARE, tidb_ignore_inlist_plan_digest, Plan Digests, IN list, tidb_index_join_batch_size, index lookup join batch size, tidb_index_join_double_read_penalty_cost_rate, tidb_cost_model_version, hash join, tiflash join, tidb_index_lookup_concurrency, index lookup operation, tidb_index_lookup_join_concurrency, tidb_index_merge_intersection_concurrency, dynamic pruning mode, partitioned tables, tidb_index_lookup_size, tidb_index_serial_scan_concurrency, ANALYZE TABLE, tidb_analyze_distsql_scan_concurrency, tidb_init_chunk_size, single chunk memory, 16 MiB, tidb_isolation_read_engines, tikv,tiflash,tidb, tidb_last_ddl_info, last DDL query string, seq_num, tidb_last_query_info, txn_scope, start_ts, for_update_ts, ru_consumption
- Follow-up Guidance: The content also notes deprecations and fallback behavior for several concurrency variables, including use of tidb_executor_concurrency, and identifies when SET_VAR applies.
- Classification Note: This chunk is reference content because it defines variable scope, defaults, ranges, units, read-only status, deprecation notes, and exact meanings for multiple TiDB system variables.

## Official Source Content

### tidb_hashagg_partial_concurrency

> **Warning:**
>
> Since v5.0, this variable is deprecated. Instead, use [`tidb_executor_concurrency`](#tidb_executor_concurrency-new-in-v50) for setting.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `-1`
- Range: `[1, 256]`
- Unit: Threads
- This variable is used to set the concurrency of executing the concurrent `hash aggregation` algorithm in the `partial` phase.
- When the parameter of the aggregate function is not distinct, `HashAgg` is run concurrently and respectively in two phases - the `partial` phase and the `final` phase.
- A value of `-1` means that the value of `tidb_executor_concurrency` will be used instead.
### tidb_historical_stats_duration New in v6.6.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Duration
- Default value: `168h`, which means 7 days
- This variable controls the duration that the historical statistics are retained in the storage.
### tidb_idle_transaction_timeout New in v7.6.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 31536000]`
- Unit: Seconds
- This variable controls the idle timeout for transactions in a user session. When a user session is in a transactional state and remains idle for a duration exceeding the value of this variable, TiDB will terminate the session. An idle user session means that there are no active requests and the session is waiting for new requests.
- The default value `0` means unlimited.
### tidb_ignore_prepared_cache_close_stmt New in v6.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to set whether to ignore the commands for closing prepared statement cache.
- When this variable is set to `ON`, the `COM_STMT_CLOSE` command of the Binary protocol and the [`DEALLOCATE PREPARE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-deallocate) statement of the text protocol are ignored. For details, see [Ignore the `COM_STMT_CLOSE` command and the `DEALLOCATE PREPARE` statement](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache#ignore-the-com_stmt_close-command-and-the-deallocate-prepare-statement).
### tidb_ignore_inlist_plan_digest New in v7.6.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether TiDB ignores the element differences in the `IN` list across different queries when generating Plan Digests.

    - When it is the default value `OFF`, TiDB does not ignore the element differences (including the difference in the number of elements) in the `IN` list when generating Plan Digests. The element differences in the `IN` list result in different Plan Digests.
    - When it is set to `ON`, TiDB ignores the element differences (including the difference in the number of elements) in the `IN` list and uses `...` to replace elements in the `IN` list in Plan Digests. In this case, TiDB generates the same Plan Digests for `IN` queries of the same type.
### tidb_index_join_batch_size

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `25000`
- Range: `[1, 2147483647]`
- Unit: Rows
- This variable is used to set the batch size of the `index lookup join` operation.
- Use a bigger value in OLAP scenarios, and a smaller value in OLTP scenarios.
### tidb_index_join_double_read_penalty_cost_rate New in v6.6.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Default value: `0`
- Range: `[0, 18446744073709551615]`
- This variable determines whether to apply a penalty cost to the selection of index join, which reduces the likelihood of the optimizer selecting index join, and increases the likelihood of selecting alternative join methods such as hash join and tiflash join.
- When index join is selected, many table lookup requests are triggered, which consumes too many resources. You can use this variable to reduce the likelihood of the optimizer selecting index join.
- This variable takes effect only when the [`tidb_cost_model_version`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_cost_model_version-new-in-v620) variable is set to `2`.
### tidb_index_lookup_concurrency

> **Warning:**
>
> Since v5.0, this variable is deprecated. Instead, use [`tidb_executor_concurrency`](#tidb_executor_concurrency-new-in-v50) for setting.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `-1`
- Range: `[1, 256]`
- Unit: Threads
- This variable is used to set the concurrency of the `index lookup` operation.
- Use a bigger value in OLAP scenarios, and a smaller value in OLTP scenarios.
- A value of `-1` means that the value of `tidb_executor_concurrency` will be used instead.
### tidb_index_lookup_join_concurrency

> **Warning:**
>
> Since v5.0, this variable is deprecated. Instead, use [`tidb_executor_concurrency`](#tidb_executor_concurrency-new-in-v50) for setting.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `-1`
- Range: `[1, 256]`
- Unit: Threads
- This variable is used to set the concurrency of the `index lookup join` algorithm.
- A value of `-1` means that the value of `tidb_executor_concurrency` will be used instead.
### tidb_index_merge_intersection_concurrency New in v6.5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: `-1`
- Range: `[1, 256]`
- This variable sets the maximum concurrency for the intersection operations that index merge performs. It is effective only when TiDB accesses partitioned tables in the dynamic pruning mode. The actual concurrency is the smaller value of `tidb_index_merge_intersection_concurrency` and the number of partitions of the partitioned table.
- The default value `-1` means that the value of `tidb_executor_concurrency` is used.
### tidb_index_lookup_size

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `20000`
- Range: `[1, 2147483647]`
- Unit: Rows
- This variable is used to set the batch size of the `index lookup` operation.
- Use a bigger value in OLAP scenarios, and a smaller value in OLTP scenarios.
### tidb_index_serial_scan_concurrency

> **Warning:**
>
> This variable is deprecated and no longer controls execution behavior. The concurrency of sequential index scans is now controlled by [`tidb_executor_concurrency`](#tidb_executor_concurrency-new-in-v50), and [`ANALYZE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) uses [`tidb_analyze_distsql_scan_concurrency`](#tidb_analyze_distsql_scan_concurrency-new-in-v760) to control the concurrency of index statistics scans.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `1`
- Range: `[1, 256]`
- Unit: Threads
- This variable remains only for backward compatibility. Use [`tidb_executor_concurrency`](#tidb_executor_concurrency-new-in-v50) to control the concurrency of sequential index scans, or [`tidb_analyze_distsql_scan_concurrency`](#tidb_analyze_distsql_scan_concurrency-new-in-v760) to control the concurrency of index statistics scans.
### tidb_init_chunk_size

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `32`
- Range: `[1, 32]`
- Unit: Rows
- This variable is used to set the number of rows for the initial chunk during the execution process. The number of rows for a chunk directly affects the amount of memory required for a single query. You can roughly estimate the memory needed for a single chunk by considering the total width of all columns in the query and the number of rows for the chunk. Combining this with the concurrency of the executor, you can make a rough estimation of the total memory required for a single query. It is recommended that the total memory for a single chunk does not exceed 16 MiB.
### tidb_isolation_read_engines New in v4.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: `tikv,tiflash,tidb`
- This variable is used to set the storage engine list that TiDB can use when reading data.
### tidb_last_ddl_info New in v6.0.0

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- Type: String
- This is a read-only variable. It is internally used in TiDB to get the information of the last DDL operation within the current session.
    - "query": The last DDL query string.
    - "seq_num": The sequence number for each DDL operation. It is used to identify the order of DDL operations.
### tidb_last_query_info New in v4.0.14

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- This is a read-only variable. It is internally used in TiDB to query the transaction information of the last DML statement. The information includes:
    - `txn_scope`: The scope of the transaction, which can be `global` or `local`.
    - `start_ts`: The start timestamp of the transaction.
    - `for_update_ts`: The `for_update_ts` of the previously executed DML statement. This is an internal term of TiDB used for tests. Usually, you can ignore this information.
    - `error`: The error message, if any.
    - `ru_consumption`: Consumed [RU](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru) for executing the statement.
