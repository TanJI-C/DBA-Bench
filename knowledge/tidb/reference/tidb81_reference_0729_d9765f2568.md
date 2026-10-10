# Multi-statement, nontransactional DML, and optimizer cost variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_multi_statement_mode <span class="version-mark">New in v4.0.11</span> | System Variables > Variable reference > tidb_nontransactional_ignore_error <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > tidb_opt_agg_push_down | System Variables > Variable reference > tidb_opt_broadcast_cartesian_join | System Variables > Variable reference > tidb_opt_concurrency_factor | System Variables > Variable reference > tidb_opt_copcpu_factor | System Variables > Variable reference > tidb_opt_correlation_exp_factor | System Variables > Variable reference > tidb_opt_correlation_threshold | System Variables > Variable reference > tidb_opt_cpu_factor | System Variables > Variable reference > `tidb_opt_derive_topn` <span class="version-mark">New in v7.0.0</span> | System Variables > Variable reference > tidb_opt_desc_factor | System Variables > Variable reference > tidb_opt_disk_factor`
- Source Line Ranges: `3900-4043`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `system-variables`, `optimizer`, `cost-model`, `sql-injection`, `nontransactional-dml`, `multi-statement`, `session-scope`, `global-scope`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0729_d9765f2568`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-multi-statement-mode-span-class-version-mark-new-in-v4-0-11-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d537fa277bbdd45be9c2a6b415cf95b90c56796ed3c532c2ad893e46ffc4f5b4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-multi-statement-mode-span-class-version-mark-new-in-v4-0-11-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables for multi-statement COM_QUERY behavior, non-transactional DML error handling, or optimizer and cost model settings such as aggregate pushdown, broadcast Cartesian join, correlation estimation, and TopN derivation.
- Retrieval Keywords: tidb_multi_statement_mode, COM_QUERY, multiple statements permitted, sql injection attacks, multiStatements, allowMultiQueries, mysqli_multi_query, tidb_nontransactional_ignore_error, non-transactional DML statement, all errors returned together, tidb_opt_agg_push_down, pushing down the aggregate function before Join Projection UnionAll, tidb_opt_broadcast_cartesian_join, Broadcast Cartesian Join, tidb_broadcast_join_threshold_count, tidb_opt_concurrency_factor, Cost Model, CPU cost of starting a Golang goroutine, tidb_opt_copcpu_factor, TiKV Coprocessor process one row, tidb_opt_correlation_exp_factor, column order correlation heuristic estimation, tidb_opt_correlation_threshold, handle column exceeds the threshold value, tidb_opt_cpu_factor, TiDB process one row, tidb_opt_derive_topn, Deriving TopN or Limit from window functions, tidb_opt_desc_factor, scan one row from the disk in descending order, tidb_opt_disk_factor, temporary disk I/O cost
- Follow-up Guidance: The content notes that only the default value OFF for tidb_multi_statement_mode can be considered safe, and several cost model variables and tidb_opt_broadcast_cartesian_join are internally used and not recommended to modify.
- Classification Note: This is reference content because it enumerates system variables with their scope, type, default values, ranges, and exact behavior for TiDB optimizer, SQL execution, and cost model settings.

## Official Source Content

### tidb_multi_statement_mode New in v4.0.11

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `OFF`
- Possible values: `OFF`, `ON`, `WARN`
- This variable controls whether to allow multiple queries to be executed in the same `COM_QUERY` call.
- To reduce the impact of SQL injection attacks, TiDB now prevents multiple queries from being executed in the same `COM_QUERY` call by default. This variable is intended to be used as part of an upgrade path from earlier versions of TiDB. The following behaviors apply:

| Client setting            | `tidb_multi_statement_mode` value | Multiple statements permitted? |
| ------------------------- | --------------------------------- | ------------------------------ |
| Multiple Statements = ON  | OFF                               | Yes                            |
| Multiple Statements = ON  | ON                                | Yes                            |
| Multiple Statements = ON  | WARN                              | Yes                            |
| Multiple Statements = OFF | OFF                               | No                             |
| Multiple Statements = OFF | ON                                | Yes                            |
| Multiple Statements = OFF | WARN                              | Yes (+warning returned)        |

> **Note:**
>
> Only the default value of `OFF` can be considered safe. Setting `tidb_multi_statement_mode=ON` might be required if your application was specifically designed for an earlier version of TiDB. If your application requires multiple statement support, it is recommended to use the setting provided by your client library instead of the `tidb_multi_statement_mode` option. For example:
>
> * [go-sql-driver](https://github.com/go-sql-driver/mysql#multistatements) (`multiStatements`)
> * [Connector/J](https://dev.mysql.com/doc/connector-j/en/connector-j-reference-configuration-properties.html) (`allowMultiQueries`)
> * PHP [mysqli](https://www.php.net/manual/en/mysqli.quickstart.multiple-statement.php) (`mysqli_multi_query`)
### tidb_nontransactional_ignore_error New in v6.1.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable specifies whether to return an error immediately when the error occurs in a non-transactional DML statement.
- When the value is set to `OFF`, the non-transactional DML statement stops immediately at the first error and returns the error. All the following batches are canceled.
- When the value is set to `ON` and an error occurs in a batch, the following batches will continue to be executed until all batches are executed. All errors occurred during the execution process are returned together in the result.
### tidb_opt_agg_push_down

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable is used to set whether the optimizer executes the optimization operation of pushing down the aggregate function to the position before Join, Projection, and UnionAll.
- When the aggregate operation is slow in query, you can set the variable value to ON.
### tidb_opt_broadcast_cartesian_join

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `1`
- Range: `[0, 2]`
- Indicates whether to allow the Broadcast Cartesian Join.
- `0` means that the Broadcast Cartesian Join is not allowed. `1` means that it is allowed based on [`tidb_broadcast_join_threshold_count`](#tidb_broadcast_join_threshold_count-new-in-v50). `2` means that it is always allowed even if the table size exceeds the threshold.
- This variable is internally used in TiDB, and it is **NOT** recommended to modify its value.
### tidb_opt_concurrency_factor

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Range: `[0, 18446744073709551615]`
- Default value: `3.0`
- Indicates the CPU cost of starting a Golang goroutine in TiDB. This variable is internally used in the [Cost Model](https://docs.pingcap.com/tidb/stable/cost-model), and it is **NOT** recommended to modify its value.
### tidb_opt_copcpu_factor

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Range: `[0, 18446744073709551615]`
- Default value: `3.0`
- Indicates the CPU cost for TiKV Coprocessor to process one row. This variable is internally used in the [Cost Model](https://docs.pingcap.com/tidb/stable/cost-model), and it is **NOT** recommended to modify its value.
### tidb_opt_correlation_exp_factor

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `1`
- Range: `[0, 2147483647]`
- When the method that estimates the number of rows based on column order correlation is not available, the heuristic estimation method is used. This variable is used to control the behavior of the heuristic method.
    - When the value is 0, the heuristic method is not used.
    - When the value is greater than 0:
        - A larger value indicates that an index scan will probably be used in the heuristic method.
        - A smaller value indicates that a table scan will probably be used in the heuristic method.
### tidb_opt_correlation_threshold

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Default value: `0.9`
- Range: `[0, 1]`
- This variable is used to set the threshold value that determines whether to enable estimating the row count by using column order correlation. If the order correlation between the current column and the `handle` column exceeds the threshold value, this method is enabled.
### tidb_opt_cpu_factor

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Range: `[0, 2147483647]`
- Default value: `3.0`
- Indicates the CPU cost for TiDB to process one row. This variable is internally used in the [Cost Model](https://docs.pingcap.com/tidb/stable/cost-model), and it is **NOT** recommended to modify its value.
### `tidb_opt_derive_topn` New in v7.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- Controls whether to enable the optimization rule of [Deriving TopN or Limit from window functions](https://docs.pingcap.com/tidb/stable/derive-topn-from-window).
### tidb_opt_desc_factor

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Range: `[0, 18446744073709551615]`
- Default value: `3.0`
- Indicates the cost for TiKV to scan one row from the disk in descending order. This variable is internally used in the [Cost Model](https://docs.pingcap.com/tidb/stable/cost-model), and it is **NOT** recommended to modify its value.
### tidb_opt_disk_factor

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Range: `[0, 18446744073709551615]`
- Default value: `1.5`
- Indicates the I/O cost for TiDB to read or write one byte of data from or to the temporary disk. This variable is internally used in the [Cost Model](https://docs.pingcap.com/tidb/stable/cost-model), and it is **NOT** recommended to modify its value.
