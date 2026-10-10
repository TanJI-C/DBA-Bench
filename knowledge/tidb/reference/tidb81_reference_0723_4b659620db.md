# TiDB enablement and execution-related system variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_enable_strict_double_type_check <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_enable_table_partition | System Variables > Variable reference > tidb_enable_telemetry <span class="version-mark">New in v4.0.2 and deprecated in v8.1.0</span> | System Variables > Variable reference > tidb_enable_tiflash_read_for_write_stmt <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_enable_top_sql <span class="version-mark">New in v5.4.0</span> | System Variables > Variable reference > tidb_enable_tso_follower_proxy <span class="version-mark">New in v5.3.0</span> | System Variables > Variable reference > tidb_enable_unsafe_substitute <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_enable_vectorized_expression <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_enable_window_function | System Variables > Variable reference > `tidb_enable_row_level_checksum` <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > tidb_enforce_mpp <span class="version-mark">New in v5.1</span> | System Variables > Variable reference > tidb_evolve_plan_baselines <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_evolve_plan_task_end_time <span class="version-mark">New in v4.0</span>`
- Source Line Ranges: `2617-2830`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tiflash`, `ticdc`, `dashboard`, `cloud`, `sql`
- Topic Tags: `system-variables`, `feature-flags`, `table-partitioning`, `telemetry`, `tiflash`, `top-sql`, `tso`, `generated-columns`, `vectorized-execution`, `window-functions`, `row-checksum`, `mpp`, `plan-baselines`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0723_4b659620db`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-enable-strict-double-type-check-span-class-version-mark-new-in-v5-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4ea4bda89961472db1d33bf178b6ebcef5bbef1096bbf87354b1897fd63b82be`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-enable-strict-double-type-check-span-class-version-mark-new-in-v5-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables that enable or disable specific execution features, partitioning, telemetry, TiFlash read behavior, Top SQL, TSO follower proxy, generated column substitution, vectorized execution, window functions, row-level checksum, MPP enforcement, or plan baseline evolution and scheduling.
- Retrieval Keywords: tidb_enable_strict_double_type_check, DOUBLE(10), ERROR 1149 (42000), tidb_enable_table_partition, TABLE PARTITION, Range partitioning, Hash partitioning, Range column partitioning, tidb_enable_telemetry, deprecated in v8.1.0, telemetry feature is removed, tidb_enable_tiflash_read_for_write_stmt, INSERT INTO SELECT, UPDATE, DELETE, sql_mode, STRICT_TRANS_TABLES, STRICT_ALL_TABLES, tidb_enable_top_sql, Top SQL, tidb_enable_tso_follower_proxy, TSO Follower Proxy, PD leader, PD followers, tidb_tso_client_batch_max_wait_time, tidb_enable_unsafe_substitute, generated columns, tidb_enable_vectorized_expression, vectorized execution, tidb_enable_window_function, window functions, reserved keywords, tidb_enable_row_level_checksum, TiCDC data integrity validation for single-row data, TIDB_ROW_CHECKSUM(), tidb_enforce_mpp, tidb_allow_mpp, TiFlash MPP mode, tidb_evolve_plan_baselines, Baseline Evolution, tidb_evolve_plan_task_end_time, tidb_evolve_plan_task_start_time, tidb_evolve_plan_task_max_time
- Follow-up Guidance: The chunk also provides related constraints and companion settings such as sql_mode strictness for TiFlash read pushdown, tidb_allow_mpp for tidb_enforce_mpp, and the baseline evolution time window variables tidb_evolve_plan_task_start_time, tidb_evolve_plan_task_end_time, and tidb_evolve_plan_task_max_time.
- Classification Note: This is reference content because it enumerates TiDB system variables with scope, persistence, type, default values, possible values, deprecation notes, and feature-specific behavior.

## Official Source Content

### tidb_enable_strict_double_type_check New in v5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to control if tables can be created with invalid definitions of type `DOUBLE`. This setting is intended to provide an upgrade path from earlier versions of TiDB, which were less strict in validating types.
- The default value of `ON` is compatible with MySQL.

For example, the type `DOUBLE(10)` is now considered invalid because the precision of floating point types is not guaranteed. After changing `tidb_enable_strict_double_type_check` to `OFF`, the table is created:

```sql
mysql> CREATE TABLE t1 (id int, c double(10));
ERROR 1149 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use

mysql> SET tidb_enable_strict_double_type_check = 'OFF';
Query OK, 0 rows affected (0.00 sec)

mysql> CREATE TABLE t1 (id int, c double(10));
Query OK, 0 rows affected (0.09 sec)
```

> **Note:**
>
> This setting only applies to the type `DOUBLE` since MySQL permits precision for `FLOAT` types. This behavior is deprecated starting with MySQL 8.0.17, and it is not recommended to specify precision for either `FLOAT` or `DOUBLE` types.
### tidb_enable_table_partition

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `ON`
- Possible values: `OFF`, `ON`, `AUTO`
- This variable is used to set whether to enable the `TABLE PARTITION` feature:
    - `ON` indicates enabling Range partitioning, Hash partitioning, and Range column partitioning with one single column.
    - `AUTO` functions the same way as `ON` does.
    - `OFF` indicates disabling the `TABLE PARTITION` feature. In this case, the syntax that creates a partition table can be executed, but the table created is not a partitioned one.
### tidb_enable_telemetry New in v4.0.2 and deprecated in v8.1.0

> **Warning:**
>
> Starting from v8.1.0, the telemetry feature in TiDB is removed, and this variable is no longer functional. It is retained solely for compatibility with earlier versions.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`

- Before v8.1.0, this variable controls whether to enable the telemetry collection in TiDB.

- This TiDB variable is not applicable to TiDB Cloud.
### tidb_enable_tiflash_read_for_write_stmt New in v6.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether read operations in SQL statements containing `INSERT`, `DELETE`, and `UPDATE` can be pushed down to TiFlash. For example:

    - `SELECT` queries in `INSERT INTO SELECT` statements (typical usage scenario: [TiFlash query result materialization](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-results-materialization))
    - `WHERE` condition filtering in `UPDATE` and `DELETE` statements
- Starting from v7.1.0, this variable is deprecated. When [`tidb_allow_mpp = ON`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_allow_mpp-new-in-v50), the optimizer intelligently decides whether to push a query down to TiFlash based on the [SQL mode](https://docs.pingcap.com/tidb/stable/sql-mode) and the cost estimates of the TiFlash replica. Note that TiDB allows read operations in SQL statements containing `INSERT`, `DELETE`, and `UPDATE` (such as `INSERT INTO SELECT`) to be pushed down to TiFlash only when the [SQL Mode](https://docs.pingcap.com/tidb/stable/sql-mode) of the current session is not strict, which means that the `sql_mode` value does not contain `STRICT_TRANS_TABLES` and `STRICT_ALL_TABLES`.
### tidb_enable_top_sql New in v5.4.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`

- This variable is used to control whether to enable the [Top SQL](https://docs.pingcap.com/tidb/stable/dashboard/top-sql) feature.

- This variable is used to control whether to enable the [Top SQL](https://docs.pingcap.com/tidb/stable/top-sql) feature.
### tidb_enable_tso_follower_proxy New in v5.3.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to enable the TSO Follower Proxy feature. When the value is `OFF`, TiDB only gets TSO from the PD leader. When the value is `ON`, TiDB evenly distributes requests for TSO to all PD servers, and PD followers can also handle TSO requests, thereby reducing the CPU pressure on the PD leader.
- Scenarios for enabling TSO Follower Proxy:
    * Due to the high pressure of TSO requests, the CPU of the PD leader reaches a bottleneck, which causes high latency of TSO RPC requests.
    * The TiDB cluster has many TiDB instances, and increasing the value of [`tidb_tso_client_batch_max_wait_time`](#tidb_tso_client_batch_max_wait_time-new-in-v530) cannot alleviate the high latency issue of TSO RPC requests.

> **Note:**
>
> Suppose that the TSO RPC latency increases for reasons other than a CPU usage bottleneck of the PD leader (such as network issues). In this case, enabling the TSO Follower Proxy might increase the execution latency in TiDB and affect the QPS performance of the cluster.
### tidb_enable_unsafe_substitute New in v6.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to replace expressions with generated columns in an unsafe way. The default value is `OFF`, which means that unsafe replacement is disabled by default. For more details, see [Generated Columns](https://docs.pingcap.com/tidb/stable/generated-columns).
### tidb_enable_vectorized_expression New in v4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether to enable vectorized execution.
### tidb_enable_window_function

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether to enable the support for [window functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions). Note that window functions might use reserved keywords. This might cause SQL statements that can be executed normally to fail to be parsed after TiDB is upgraded. In this case, you can set `tidb_enable_window_function` to `OFF`.
### `tidb_enable_row_level_checksum` New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`

- This variable is used to control whether to enable the [TiCDC data integrity validation for single-row data](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-integrity-check) feature.

- This variable is used to control whether to enable the [TiCDC data integrity validation for single-row data](https://docs.pingcap.com/tidb/stable/ticdc-integrity-check) feature.

- You can use the [`TIDB_ROW_CHECKSUM()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb_row_checksum) function to get the checksum value of a row.
### tidb_enforce_mpp New in v5.1

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`

- To change this default value, modify the [`performance.enforce-mpp`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enforce-mpp) configuration value.

- Controls whether to ignore the optimizer's cost estimation and to forcibly use TiFlash's MPP mode for query execution. The value options are as follows:
    - `0` or `OFF`, which means that the MPP mode is not forcibly used (by default).
    - `1` or `ON`, which means that the cost estimation is ignored and the MPP mode is forcibly used. Note that this setting only takes effect when `tidb_allow_mpp=true`.

MPP is a distributed computing framework provided by the TiFlash engine, which allows data exchange between nodes and provides high-performance, high-throughput SQL algorithms. For details about the selection of the MPP mode, refer to [Control whether to select the MPP mode](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode#control-whether-to-select-the-mpp-mode).
### tidb_evolve_plan_baselines New in v4.0

> **Warning:**
>
> The feature controlled by this variable is experimental. It is not recommended that you use it in the production environment. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to control whether to enable the baseline evolution feature. For detailed introduction or usage , see [Baseline Evolution](https://docs.pingcap.com/tidb/stable/sql-plan-management#baseline-evolution).
- To reduce the impact of baseline evolution on the cluster, use the following configurations:
    - Set `tidb_evolve_plan_task_max_time` to limit the maximum execution time of each execution plan. The default value is 600s.
    - Set `tidb_evolve_plan_task_start_time` and `tidb_evolve_plan_task_end_time` to limit the time window. The default values are respectively `00:00 +0000` and `23:59 +0000`.
### tidb_evolve_plan_task_end_time New in v4.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Time
- Default value: `23:59 +0000`
- This variable is used to set the end time of baseline evolution in a day.
