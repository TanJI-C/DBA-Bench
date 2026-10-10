# TiDB statistics, analyze, and MPP-related system variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_allow_function_for_expression_index <span class="version-mark">New in v5.2.0</span> | System Variables > Variable reference > tidb_allow_mpp <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_allow_remove_auto_inc <span class="version-mark">New in v2.1.18 and v3.0.4</span> | System Variables > Variable reference > tidb_analyze_distsql_scan_concurrency <span class="version-mark">New in v7.6.0</span> | System Variables > Variable reference > tidb_analyze_partition_concurrency | System Variables > Variable reference > tidb_analyze_version <span class="version-mark">New in v5.1.0</span> | System Variables > Variable reference > tidb_analyze_skip_column_types <span class="version-mark">New in v7.2.0</span> | System Variables > Variable reference > tidb_auto_analyze_end_time | System Variables > Variable reference > tidb_auto_analyze_partition_batch_size <span class="version-mark">New in v6.4.0</span>`
- Source Line Ranges: `1079-1228`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `tikv`
- Topic Tags: `system-variables`, `statistics`, `analyze`, `auto-analyze`, `mpp`, `expression-indexes`, `concurrency`, `partitioned-tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0716_a318918b6e`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-allow-function-for-expression-index-span-class-version-mark-new-in-v5-2-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3bb89790ba2318c48556d24fabc7c0535723e8c136920c0d19c237812073d3c7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-allow-function-for-expression-index-span-class-version-mark-new-in-v5-2-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables related to expression indexes, TiFlash MPP, removing AUTO_INCREMENT, ANALYZE concurrency, statistics collection versions, skipped column types during ANALYZE, and auto analyze time or partition batch settings.
- Retrieval Keywords: tidb_allow_function_for_expression_index, expression indexes, json_array, lower, md5, tidb_shard, vitess_hash, tidb_allow_mpp, MPP mode, TiFlash, tidb_allow_tiflash_cop, tidb_allow_remove_auto_inc, AUTO_INCREMENT, ALTER TABLE MODIFY, ALTER TABLE CHANGE, tidb_analyze_distsql_scan_concurrency, ANALYZE concurrency, scan TiKV Regions, special indexes, generated virtual columns, tidb_analyze_partition_concurrency, writing TopN and histograms to system tables, tidb_analyze_version, Introduction to Statistics, tidb_analyze_skip_column_types, ANALYZE TABLE t COLUMNS, mysql.analyze_jobs, job_info, json,blob,mediumblob,longblob, tidb_auto_analyze_end_time, automatic update of statistics, tidb_auto_analyze_start_time, tidb_auto_analyze_partition_batch_size, partitioned table, automatically analyzes all partitions in multiple batches
- Follow-up Guidance: The content also points to related material for Control whether to select the MPP mode and Introduction to Statistics, and includes mysql.analyze_jobs job_info examples for skipped column types during ANALYZE.
- Classification Note: This is classified as reference content because it enumerates specific system variables with scope, default values, ranges, and exact behavior descriptions for statistics, analyze, auto-analyze, and MPP features.

## Official Source Content

### tidb_allow_function_for_expression_index New in v5.2.0

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `json_array, json_array_append, json_array_insert, json_contains, json_contains_path, json_depth, json_extract, json_insert, json_keys, json_length, json_merge_patch, json_merge_preserve, json_object, json_pretty, json_quote, json_remove, json_replace, json_search, json_set, json_storage_size, json_type, json_unquote, json_valid, lower, md5, reverse, tidb_shard, upper, vitess_hash`
- This read-only variable is used to show the functions that are allowed to be used for creating [expression indexes](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#expression-index).
### tidb_allow_mpp New in v5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `ON`
- Controls whether to use the MPP mode of TiFlash to execute queries. The value options are as follows:
    - `0` or `OFF`, which means that the MPP mode will not be used. For v7.3.0 or a later version, if you set the value of this variable to `0` or `OFF`, you also need to enable the [`tidb_allow_tiflash_cop`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_allow_tiflash_cop-new-in-v730) variable. Otherwise, queries might return errors.
    - `1` or `ON`, which means that the optimizer determines whether to use the MPP mode based on the cost estimation (by default).

MPP is a distributed computing framework provided by the TiFlash engine, which allows data exchange between nodes and provides high-performance, high-throughput SQL algorithms. For details about the selection of the MPP mode, refer to [Control whether to select the MPP mode](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode#control-whether-to-select-the-mpp-mode).
### tidb_allow_remove_auto_inc New in v2.1.18 and v3.0.4

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to set whether the `AUTO_INCREMENT` property of a column is allowed to be removed by executing `ALTER TABLE MODIFY` or `ALTER TABLE CHANGE` statements. It is not allowed by default.
### tidb_analyze_distsql_scan_concurrency New in v7.6.0

> **Note:**
>
> In versions earlier than v7.6.0, regular `ANALYZE` region scans are controlled by `tidb_distsql_scan_concurrency`, and index statistics scans are controlled by `tidb_index_serial_scan_concurrency`. Therefore, to adjust the concurrency of scanning TiKV Regions for these versions, consider changing the value of `tidb_distsql_scan_concurrency`.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `4`
- Range: `[1, 4294967295]`
- This variable controls the following aspects of `ANALYZE` concurrency:
    - The concurrency of scanning TiKV Regions.
    - The concurrency of scanning Regions for special indexes, such as indexes on generated virtual columns.
### tidb_analyze_partition_concurrency

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `2`. The default value is `1` for v7.4.0 and earlier versions.
- Range: `[1, 18446744073709551615]`
- For manual and auto `ANALYZE`, this variable controls the concurrency for saving `ANALYZE` results, including writing TopN and histograms to system tables.
### tidb_analyze_version New in v5.1.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `2`
- Range: `[1, 2]`
- Controls how TiDB collects statistics.
    - For TiDB Self-Managed, the default value of this variable changes from `1` to `2` starting from v5.3.0.
    - For TiDB Cloud, the default value of this variable changes from `1` to `2` starting from v6.5.0.
    - If your cluster is upgraded from an earlier version, the default value of `tidb_analyze_version` does not change after the upgrade.
- For detailed introduction about this variable, see [Introduction to Statistics](https://docs.pingcap.com/tidb/stable/statistics).
### tidb_analyze_skip_column_types New in v7.2.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: "json,blob,mediumblob,longblob"
- Possible values: "json,blob,mediumblob,longblob,text,mediumtext,longtext"
- This variable controls which types of columns are skipped for statistics collection when executing the `ANALYZE` command to collect statistics. The variable is only applicable for `tidb_analyze_version = 2`. Even if you specify a column using `ANALYZE TABLE t COLUMNS c1, ... , cn`, no statistics will be collected for the specified column if its type is in `tidb_analyze_skip_column_types`.

```
mysql> SHOW CREATE TABLE t;
+-------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Table | Create Table                                                                                                                                                                                                             |
+-------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| t     | CREATE TABLE `t` (
  `a` int(11) DEFAULT NULL,
  `b` varchar(10) DEFAULT NULL,
  `c` json DEFAULT NULL,
  `d` blob DEFAULT NULL,
  `e` longblob DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin |
+-------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)

mysql> SELECT @@tidb_analyze_skip_column_types;
+----------------------------------+
| @@tidb_analyze_skip_column_types |
+----------------------------------+
| json,blob,mediumblob,longblob    |
+----------------------------------+
1 row in set (0.00 sec)

mysql> ANALYZE TABLE t;
Query OK, 0 rows affected, 1 warning (0.05 sec)

mysql> SELECT job_info FROM mysql.analyze_jobs ORDER BY end_time DESC LIMIT 1;
+---------------------------------------------------------------------+
| job_info                                                            |
+---------------------------------------------------------------------+
| analyze table columns a, b with 256 buckets, 500 topn, 1 samplerate |
+---------------------------------------------------------------------+
1 row in set (0.00 sec)

mysql> ANALYZE TABLE t COLUMNS a, c;
Query OK, 0 rows affected, 1 warning (0.04 sec)

mysql> SELECT job_info FROM mysql.analyze_jobs ORDER BY end_time DESC LIMIT 1;
+------------------------------------------------------------------+
| job_info                                                         |
+------------------------------------------------------------------+
| analyze table columns a with 256 buckets, 500 topn, 1 samplerate |
+------------------------------------------------------------------+
1 row in set (0.00 sec)
```
### tidb_auto_analyze_end_time

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Time
- Default value: `23:59 +0000`
- This variable is used to restrict the time window that the automatic update of statistics is permitted. For example, to only allow automatic statistics updates between 1 AM and 3 AM in UTC time, set `tidb_auto_analyze_start_time='01:00 +0000'` and `tidb_auto_analyze_end_time='03:00 +0000'`.
### tidb_auto_analyze_partition_batch_size New in v6.4.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `128`. Before v7.6.0, the default value is `1`.
- Range: `[1, 1024]`
- This variable specifies the number of partitions that TiDB [automatically analyzes](https://docs.pingcap.com/tidb/stable/statistics#automatic-update) when analyzing a partitioned table (which means automatically collecting statistics on a partitioned table).
- If the value of this variable is smaller than the number of partitions, TiDB automatically analyzes all partitions of the partitioned table in multiple batches. If the value of this variable is greater than or equal to the number of partitions, TiDB analyzes all partitions of the partitioned table at the same time.
- If the number of partitions of a partitioned table is far greater than this variable value and the auto-analyze takes a long time, you can increase the value of this variable to reduce the time consumption.
