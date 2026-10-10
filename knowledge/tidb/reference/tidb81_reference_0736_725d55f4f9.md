# Optimizer cost, distinct aggregation, partition pruning, and analyze options variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_opt_range_max_size <span class="version-mark">New in v6.4.0</span> | System Variables > Variable reference > tidb_opt_scan_factor | System Variables > Variable reference > tidb_opt_seek_factor | System Variables > Variable reference > tidb_opt_skew_distinct_agg <span class="version-mark">New in v6.2.0</span> | System Variables > Variable reference > tidb_opt_three_stage_distinct_agg <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_opt_tiflash_concurrency_factor | System Variables > Variable reference > tidb_opt_use_invisible_indexes <span class="version-mark">New in v8.0.0</span> | System Variables > Variable reference > tidb_opt_write_row_id | System Variables > Variable reference > tidb_optimizer_selectivity_level | System Variables > Variable reference > tidb_partition_prune_mode <span class="version-mark">New in v5.1</span> | System Variables > Variable reference > tidb_persist_analyze_options <span class="version-mark">New in v5.4.0</span>`
- Source Line Ranges: `4610-4762`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`, `tiflash`
- Topic Tags: `system-variables`, `optimizer`, `cost-model`, `range-building`, `warnings`, `distinct-aggregation`, `mpp`, `invisible-indexes`, `rowid`, `partition-pruning`, `globalstats`, `analyze`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0736_725d55f4f9`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-opt-range-max-size-span-class-version-mark-new-in-v6-4-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3e07f5cf72c72221bb5853381b79c5db84e12427c4527c7c803a39cf47f09230`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-opt-range-max-size-span-class-version-mark-new-in-v6-4-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables related to optimizer range-building warnings, cost model factors, DISTINCT aggregation rewrites, TiFlash and MPP behavior, invisible indexes, _tidb_rowid writes, partition pruning mode, or ANALYZE configuration persistence.
- Retrieval Keywords: tidb_opt_range_max_size, Memory capacity of 100 bytes for 'tidb_opt_range_max_size' exceeded when building ranges, SHOW WARNINGS, IndexFullScan, EXPLAIN SELECT * FROM t USE INDEX (idx) WHERE a IN (10,20,30) AND b IN (40,50,60), tidb_opt_scan_factor, tidb_opt_seek_factor, Cost Model, tidb_opt_skew_distinct_agg, TiFlash, COUNT(DISTINCT), two-level aggregate functions, tidb_opt_three_stage_distinct_agg, three-stage aggregation, MPP mode, tidb_opt_tiflash_concurrency_factor, tidb_opt_use_invisible_indexes, invisible indexes, tidb_opt_write_row_id, _tidb_rowid, INSERT REPLACE UPDATE, tidb_optimizer_selectivity_level, tidb_partition_prune_mode, dynamic pruning mode, GlobalStats, static-only, dynamic-only, tidb_persist_analyze_options, ANALYZE configuration persistence
- Follow-up Guidance: The content notes that dynamic partition pruning uses static mode before GlobalStats are collected, and that some variables are internally used in the Cost Model or apply only in specific cases such as TiFlash or one COUNT(DISTINCT) in MPP mode.
- Classification Note: This chunk is classified as reference content because it lists variable scopes, types, defaults, ranges, possible values, and documented behavior for multiple TiDB system variables.

## Official Source Content

```sql
+---------+------+---------------------------------------------------------------------------------------------------------------------------------------------+
| Level   | Code | Message                                                                                                                                     |
+---------+------+---------------------------------------------------------------------------------------------------------------------------------------------+
| Warning | 1105 | Memory capacity of 1500 bytes for 'tidb_opt_range_max_size' exceeded when building ranges. Less accurate ranges such as full range are chosen |
+---------+------+---------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

Then set the upper limit of memory usage to 100 bytes:

```sql
set @@tidb_opt_range_max_size = 100;
```

```sql
Query OK, 0 rows affected (0.00 sec)
```

```sql
EXPLAIN SELECT * FROM t USE INDEX (idx) WHERE a IN (10,20,30) AND b IN (40,50,60);
```

In the 100-byte memory limit, the optimizer chooses `IndexFullScan`, and uses a warning to inform the user that the memory required to build exact scan ranges exceeds the limit of `tidb_opt_range_max_size`.

```sql
+-------------------------------+----------+-----------+--------------------------+----------------------------------------------------+
| id                            | estRows  | task      | access object            | operator info                                      |
+-------------------------------+----------+-----------+--------------------------+----------------------------------------------------+
| IndexLookUp_8                 | 8000.00  | root      |                          |                                                    |
| ├─Selection_7(Build)          | 8000.00  | cop[tikv] |                          | in(test.t.a, 10, 20, 30), in(test.t.b, 40, 50, 60) |
| │ └─IndexFullScan_5           | 10000.00 | cop[tikv] | table:t, index:idx(a, b) | keep order:false, stats:pseudo                     |
| └─TableRowIDScan_6(Probe)     | 8000.00  | cop[tikv] | table:t                  | keep order:false, stats:pseudo                     |
+-------------------------------+----------+-----------+--------------------------+----------------------------------------------------+
4 rows in set, 1 warning (0.00 sec)
```

```sql
SHOW WARNINGS;
```

```sql
+---------+------+---------------------------------------------------------------------------------------------------------------------------------------------+
| Level   | Code | Message                                                                                                                                     |
+---------+------+---------------------------------------------------------------------------------------------------------------------------------------------+
| Warning | 1105 | Memory capacity of 100 bytes for 'tidb_opt_range_max_size' exceeded when building ranges. Less accurate ranges such as full range are chosen |
+---------+------+---------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

</details>
### tidb_opt_scan_factor

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Range: `[0, 2147483647]`
- Default value: `1.5`
- Indicates the cost for TiKV to scan one row of data from the disk in ascending order. This variable is internally used in the [Cost Model](https://docs.pingcap.com/tidb/stable/cost-model), and it is **NOT** recommended to modify its value.
### tidb_opt_seek_factor

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Range: `[0, 2147483647]`
- Default value: `20`
- Indicates the start-up cost for TiDB to request data from TiKV. This variable is internally used in the [Cost Model](https://docs.pingcap.com/tidb/stable/cost-model), and it is **NOT** recommended to modify its value.
### tidb_opt_skew_distinct_agg New in v6.2.0

> **Note:**
>
> The query performance optimization by enabling this variable is effective **only for TiFlash**.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable sets whether the optimizer rewrites the aggregate functions with `DISTINCT` to the two-level aggregate functions, such as rewriting `SELECT b, COUNT(DISTINCT a) FROM t GROUP BY b` to `SELECT b, COUNT(a) FROM (SELECT b, a FROM t GROUP BY b, a) t GROUP BY b`. When the aggregation column has serious skew and the `DISTINCT` column has many different values, this rewriting can avoid the data skew in the query execution and improve the query performance.
### tidb_opt_three_stage_distinct_agg New in v6.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `ON`
- This variable specifies whether to rewrite a `COUNT(DISTINCT)` aggregation into a three-stage aggregation in MPP mode.
- This variable currently applies to an aggregation that only contains one `COUNT(DISTINCT)`.
### tidb_opt_tiflash_concurrency_factor

- Scope: SESSION | GLOBAL
- Persists to cluster: YES
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Range: `[0, 2147483647]`
- Default value: `24.0`
- Indicates the concurrency number of TiFlash computation. This variable is internally used in the Cost Model, and it is NOT recommended to modify its value.
### tidb_opt_use_invisible_indexes New in v8.0.0

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable controls whether the optimizer can select [invisible indexes](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#invisible-index) for query optimization in the current session. Invisible indexes are maintained by DML statements, but will not be used by the query optimizer. This is useful in scenarios where you want to double-check before removing an index permanently. When the variable is set to `ON`, the optimizer can select invisible indexes for query optimization in the session.
### tidb_opt_write_row_id

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable is used to control whether to allow `INSERT`, `REPLACE`, and `UPDATE` statements to operate on the `_tidb_rowid` column. This variable can be used only when you import data using TiDB tools.
### tidb_optimizer_selectivity_level

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `0`
- Range: `[0, 2147483647]`
- This variable controls the iteration of the optimizer's estimation logic. After changing the value of this variable, the estimation logic of the optimizer will change greatly. Currently, `0` is the only valid value. It is not recommended to set it to other values.
### tidb_partition_prune_mode New in v5.1

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Enumeration
- Default value: `dynamic`
- Possible values: `static`, `dynamic`, `static-only`, `dynamic-only`
- Specifies whether to use `dynamic` or `static` mode for partitioned tables. Note that dynamic partitioning is effective only after full table-level statistics, or GlobalStats, are collected. Before GlobalStats are collected, TiDB will use the `static` mode instead. For detailed information about GlobalStats, see [Collect statistics of partitioned tables in dynamic pruning mode](https://docs.pingcap.com/tidb/stable/statistics#collect-statistics-of-partitioned-tables-in-dynamic-pruning-mode). For details about the dynamic pruning mode, see [Dynamic Pruning Mode for Partitioned Tables](https://docs.pingcap.com/tidb/stable/partitioned-table#dynamic-pruning-mode).
### tidb_persist_analyze_options New in v5.4.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether to enable the [ANALYZE configuration persistence](https://docs.pingcap.com/tidb/stable/statistics#persist-analyze-configurations) feature.
