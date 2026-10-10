# TiFlash late materialization overview, control variable, and execution flow

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-late-materialization.md`
- Source Title: `TiFlash Late Materialization`
- Source Heading Path: `TiFlash Late Materialization | TiFlash Late Materialization > Enable or disable TiFlash late materialization | TiFlash Late Materialization > Implementation mechanism`
- Source Line Ranges: `5-99`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `late-materialization`, `olap`, `filter-pushdown`, `tablescan`, `system-variable`, `session-scope`, `global-scope`, `mpp`, `mvcc`, `bitmap`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0248_98c3a5916d`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-late-materialization.md#tiflash-late-materialization`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `af285dd4fe0b2d06c02ab5dbf7f1b3b17bfe5280f21135d45bda8fdf6d3487b9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-late-materialization#tiflash-late-materialization
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-late-materialization.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiFlash late materialization works, how `tidb_opt_enable_late_materialization` controls it, or how pushed down filters appear in a TiFlash `TableScan` execution plan.
- Retrieval Keywords: TiFlash Late Materialization, tidb_opt_enable_late_materialization, SHOW VARIABLES LIKE 'tidb_opt_enable_late_materialization', SHOW GLOBAL VARIABLES LIKE 'tidb_opt_enable_late_materialization', SET SESSION tidb_opt_enable_late_materialization=OFF, SET GLOBAL tidb_opt_enable_late_materialization=OFF, SET SESSION tidb_opt_enable_late_materialization=ON, SET GLOBAL tidb_opt_enable_late_materialization=ON, fast scan mode, pushed down filter, TableScan operator, TableFullScan_9, MppVersion: 1, mpp[tiflash], WHERE clause, OLAP scenarios, MVCC Bitmap, Filter Bitmap, Final Bitmap, EXPLAIN SELECT a, b, c FROM t1 WHERE a < 1
- Follow-up Guidance: The chunk also shows the TableScan execution flow with `<handle, del_mark, version>`, MVCC filtering, Filter Bitmap generation, `AND` with the MVCC Bitmap, and reading remaining columns by the Final Bitmap.
- Classification Note: This is classified as performance for TiFlash because the official content describes late materialization as an optimization that reduces IO scans and computations for OLAP queries by pushing down part of the filter conditions to TableScan.

## Official Source Content

# TiFlash Late Materialization

> **Note:**
>
> TiFlash late materialization does not take effect in the [fast scan mode](https://docs.pingcap.com/tidb/stable/tiflash/use-fastscan).

TiFlash late materialization is an optimization method to accelerate queries in OLAP scenarios. You can use the [`tidb_opt_enable_late_materialization`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_late_materialization-new-in-v700) system variable to control whether to enable or disable TiFlash late materialization.

- When it is disabled, to process a `SELECT` statement with filter conditions (`WHERE` clause), TiFlash reads all the data from the columns required by the query, and then filters and aggregates the data based on the query conditions.
- When it is enabled, TiFlash supports pushing down part of the filter conditions to the TableScan operator. That is, TiFlash first scans the column data related to the filter conditions that are pushed down to the TableScan operator, filters the rows that meet the condition, and then scans the other column data of these rows for further calculation, thereby reducing IO scans and computations of data processing.

To improve the performance of certain queries in OLAP scenarios, starting from v7.1.0, the TiFlash late materialization feature is enabled by default. The TiDB optimizer can determine which filter conditions to be pushed down based on statistics and filter conditions, and prioritize pushing down the filter conditions with high filtration rates. For detailed algorithms, see the [RFC document](https://github.com/pingcap/tidb/tree/release-8.1/docs/design/2022-12-06-support-late-materialization.md).

For example:

```sql
EXPLAIN SELECT a, b, c FROM t1 WHERE a < 1;
```

```
+-------------------------+----------+--------------+---------------+-------------------------------------------------------+
| id                      | estRows  | task         | access object | operator info                                         |
+-------------------------+----------+--------------+---------------+-------------------------------------------------------+
| TableReader_12          | 12288.00 | root         |               | MppVersion: 1, data:ExchangeSender_11                 |
| └─ExchangeSender_11     | 12288.00 | mpp[tiflash] |               | ExchangeType: PassThrough                             |
|   └─TableFullScan_9     | 12288.00 | mpp[tiflash] | table:t1      | pushed down filter:lt(test.t1.a, 1), keep order:false |
+-------------------------+----------+--------------+---------------+-------------------------------------------------------+
```

In this example, the filter condition `a < 1` is pushed down to the TableScan operator. TiFlash first reads all data from column `a`, and then filters the rows that meet the `a < 1` condition. Next, TiFlash reads columns `b` and `c` from these filtered rows.
## Enable or disable TiFlash late materialization

By default, the `tidb_opt_enable_late_materialization` system variable is `ON` at both the session and global levels, which means that the TiFlash late materialization feature is enabled. You can use the following statement to view the corresponding variable information:

```sql
SHOW VARIABLES LIKE 'tidb_opt_enable_late_materialization';
```

```
+--------------------------------------+-------+
| Variable_name                        | Value |
+--------------------------------------+-------+
| tidb_opt_enable_late_materialization | ON    |
+--------------------------------------+-------+
```

```sql
SHOW GLOBAL VARIABLES LIKE 'tidb_opt_enable_late_materialization';
```

```
+--------------------------------------+-------+
| Variable_name                        | Value |
+--------------------------------------+-------+
| tidb_opt_enable_late_materialization | ON    |
+--------------------------------------+-------+
```

You can modify the `tidb_opt_enable_late_materialization` variable at the session level or at the global level.

- To disable TiFlash late materialization in the current session, use the following statement:

    ```sql
    SET SESSION tidb_opt_enable_late_materialization=OFF;
    ```

- To disable TiFlash late materialization at the global level, use the following statement:

    ```sql
    SET GLOBAL tidb_opt_enable_late_materialization=OFF;
    ```

    After this setting, the `tidb_opt_enable_late_materialization` variable will be enabled by default for both session and global levels in new sessions.

To enable TiFlash late materialization, use the following statements:

```sql
SET SESSION tidb_opt_enable_late_materialization=ON;
```

```sql
SET GLOBAL tidb_opt_enable_late_materialization=ON;
```
## Implementation mechanism

When filter conditions are pushed down to the TableScan operator, the execution process of the TableScan operator mainly includes the following steps:

1. Reads the three columns `<handle, del_mark, version>`, performs multi-version concurrency control (MVCC) filtering, and then generates the MVCC Bitmap.
2. Reads the columns related to the filter conditions, filters the rows that meet the conditions, and then generates the Filter Bitmap.
3. Performs an `AND` operation between the MVCC Bitmap and Filter Bitmap to generate the Final Bitmap.
4. Reads the corresponding rows of the remaining columns according to the Final Bitmap.
5. Merges the data read in steps 2 and 4, and then returns the results.
