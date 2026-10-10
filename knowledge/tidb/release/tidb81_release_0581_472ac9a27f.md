# 8.0.0 system variable compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes > Compatibility changes > System variables`
- Source Line Ranges: `308-326`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `system-variables`, `compatibility-changes`, `deprecation`, `renaming`, `defaults`, `logging`, `transactions`, `ddl`, `statistics`, `optimizer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0581_472ac9a27f`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#system-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `de6f75ca3870c9e07147f9fe7e13699314a5a42b31a4ab94385c98a625f384c9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#system-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB 8.0.0 system variable compatibility changes such as deprecated, renamed, modified, or newly added variables and their exact names and behaviors.
- Retrieval Keywords: TiDB 8.0.0 system variables, tidb_disable_txn_auto_retry deprecated, tidb_ddl_version renamed tidb_enable_fast_create_table, tidb_enable_collect_execution_info index usage statistics, tidb_redact_log MARKER, div_precision_increment, tidb_dml_type standard bulk, tidb_enable_auto_analyze_priority_queue, tidb_enable_parallel_hashagg_spill, tidb_enable_fast_create_table, tidb_load_binding_timeout, tidb_low_resolution_tso_update_interval, tidb_opt_ordering_index_selectivity_ratio, tidb_opt_use_invisible_indexes, tidb_schema_cache_size
- Follow-up Guidance: The content also states that TiDB no longer supports automatic retries of optimistic transactions and mentions Pessimistic transaction mode and application-side retry handling for optimistic transaction conflicts.
- Classification Note: This is a release-note compatibility chunk for TiDB system variables because it enumerates variable-level changes in v8.0.0, including deprecation, renaming, modified behavior, defaults, and newly added variables.

## Official Source Content

### System variables

| Variable name | Change type | Description |
|--------|------------------------------|------|
| [`tidb_disable_txn_auto_retry`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_disable_txn_auto_retry) | Deprecated | Starting from v8.0.0, this system variable is deprecated, and TiDB no longer supports automatic retries of optimistic transactions. It is recommended to use the [Pessimistic transaction mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction). If you encounter optimistic transaction conflicts, you can capture the error and retry transactions in your application. |
| `tidb_ddl_version` | Renamed | Controls whether to enable TiDB DDL V2. Starting from v8.0.0, this variable is renamed to [`tidb_enable_fast_create_table`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_fast_create_table-new-in-v800) to better reflect its purpose. |
| [`tidb_enable_collect_execution_info`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_collect_execution_info) | Modified | Adds a control to whether to record the [usage statistics of indexes](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-index-usage). The default value is `ON`. |
| [`tidb_redact_log`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_redact_log) | Modified | Controls how to handle user information in SAL text when logging TiDB logs and slow logs. The value options are `OFF` (indicating not processing user information in the log) and `ON` (indicating hiding user information in the log). To provide a richer way of processing user information in the log, the `MARKER` option is added in v8.0.0 to support marking log information. |
| [`div_precision_increment`](https://docs.pingcap.com/tidb/stable/system-variables#div_precision_increment-new-in-v800) | Newly added | Controls the number of digits by which to increase the scale of the result of a division operation performed using the `/` operator. This variable is the same as MySQL. |
| [`tidb_dml_type`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_type-new-in-v800) | Newly added | Controls the execution mode of DML statements. The value options are `"standard"` and `"bulk"`. |
| [`tidb_enable_auto_analyze_priority_queue`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_auto_analyze_priority_queue-new-in-v800) | Newly added | Controls whether to enable the priority queue to schedule the tasks of automatically collecting statistics. When this variable is enabled, TiDB prioritizes collecting statistics for the tables that most need statistics. |
| [`tidb_enable_parallel_hashagg_spill`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_parallel_hashagg_spill-new-in-v800) | Newly added | Controls whether TiDB supports disk spill for the parallel HashAgg algorithm. When it is `ON`, disk spill can be triggered for the parallel HashAgg algorithm. This variable will be deprecated when this feature is generally available in a future release. |
| [`tidb_enable_fast_create_table`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_fast_create_table-new-in-v800) | Newly added | Controls whether to enable [TiDB Accerates Table Creation](https://docs.pingcap.com/tidb/stable/accelerated-table-creation). Set the value to `ON` to enable it and `OFF` to disable it. The default value is `ON`. When this variable is enabled, TiDB accelerates table creation by using [`CREATE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table). |
| [`tidb_load_binding_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_load_binding_timeout-new-in-v800) | Newly added | Controls the timeout of loading bindings. If the execution time of loading bindings exceeds this value, the loading will stop. |
| [`tidb_low_resolution_tso_update_interval`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_low_resolution_tso_update_interval-new-in-v800) | Newly added | Controls the interval for updating TiDB [cache timestamp](https://docs.pingcap.com/tidb/stable/system-variables#tidb_low_resolution_tso). |
| [`tidb_opt_ordering_index_selectivity_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_ordering_index_selectivity_ratio-new-in-v800) | Newly added | Controls the estimated number of rows for an index that matches the SQL statement `ORDER BY` when there are `ORDER BY` and `LIMIT` clauses in a SQL statement, but some filter conditions not covered by the index. The default value is `-1`, which means to disable this system variable. |
| [`tidb_opt_use_invisible_indexes`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_use_invisible_indexes-new-in-v800) | Newly added | Controls whether the optimizer can select [invisible indexes](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#invisible-index) for query optimization in the current session. When the variable is set to `ON`, the optimizer can select invisible indexes for query optimization in the session. |
| [`tidb_schema_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_schema_cache_size-new-in-v800)  | Newly added | Controls the upper limit of memory that can be used for caching the schema information to avoid occupying too much memory. When this feature is enabled, the LRU algorithm is used to cache the required tables, effectively reducing the memory occupied by the schema information.    |
