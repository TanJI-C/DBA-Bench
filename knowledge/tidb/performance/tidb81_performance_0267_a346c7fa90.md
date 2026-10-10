# TiFlash FastScan overview, restrictions, configuration, and mechanism

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/use-fastscan.md`
- Source Title: `Use FastScan`
- Source Heading Path: `Use FastScan | Use FastScan > Restrictions | Use FastScan > Enable and disable FastScan | Use FastScan > Mechanism of FastScan`
- Source Line Ranges: `5-103`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `sql`, `tidb`
- Topic Tags: `fastscan`, `olap`, `query-performance`, `consistency`, `accuracy`, `restrictions`, `session-variables`, `global-variables`, `compaction`, `gc-safe-point`, `tablescan`, `mvcc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0267_a346c7fa90`
- Source ID: `tidb-docs-8.1:tiflash/use-fastscan.md#use-fastscan`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0934df7813b1331cf08164d166c56194fbf8c0e8c21f8ac15f2c0345ab67d28f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/use-fastscan#use-fastscan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/use-fastscan.md

## Retrieval Guidance

- Use When: Use this chunk when answering about TiFlash FastScan behavior, its accuracy and consistency tradeoff, restrictions with historical or deleted rows, session or global variable control, or the scan mechanism it skips for OLAP queries.
- Retrieval Keywords: TiFlash FastScan, tiflash_fastscan, Use FastScan, OLAP query performance, accuracy of query results, data consistency, old data of a table, multiple historical versions of data with the same primary key, data that has been deleted, GC safe point, ALTER TABLE ... COMPACT, show variables like 'tiflash_fastscan', show global variables like 'tiflash_fastscan', set session tiflash_fastscan=ON, set global tiflash_fastscan=ON, set session tiflash_fastscan=OFF, set global tiflash_fastscan=OFF, tidb_isolation_read_engines='tiflash', TableScan operator, Delta layer, Stable layer, Sort Merge, Range Filter, MVCC + Column Filter
- Follow-up Guidance: The source also shows that old data is physically cleaned only after compaction and when its versions are older than the GC safe point, and that a new global setting takes effect only in new sessions.
- Classification Note: This is classified as a TiFlash performance topic because the content describes FastScan as a way to speed up OLAP queries by omitting Sort Merge and the MVCC part of normal TableScan, while noting reduced accuracy and consistency.

## Official Source Content

# Use FastScan

This document describes how to use FastScan to speed up queries in Online Analytical Processing (OLAP) scenarios.

By default, TiFlash guarantees the precision of query results and data consistency. With the feature FastScan, TiFlash provides more efficient query performance, but does not guarantee the accuracy of query results and data consistency.

Some OLAP scenarios allow for some tolerance to the accuracy of the query results. In these cases, if you need higher query performance, you can enable the FastScan feature at the session or global level. You can choose whether to enable the FastScan feature by configuring the variable [`tiflash_fastscan`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_fastscan-new-in-v630).
## Restrictions

When the FastScan feature is enabled, your query results might include old data of a table. This means that you might get multiple historical versions of data with the same primary key or data that has been deleted.

For example:

```sql
CREATE TABLE t1 (a INT PRIMARY KEY, b INT);
ALTER TABLE t1 SET TIFLASH REPLICA 1;
INSERT INTO t1 VALUES(1,2);
INSERT INTO t1 VALUES(10,20);
UPDATE t1 SET b = 4 WHERE a = 1;
DELETE FROM t1 WHERE a = 10;
SET SESSION tidb_isolation_read_engines='tiflash';

SELECT * FROM t1;
+------+------+
| a    | b    |
+------+------+
|    1 |    4 |
+------+------+

SET SESSION tiflash_fastscan=ON;
SELECT * FROM t1;
+------+------+
| a    | b    |
+------+------+
|    1 |    2 |
|    1 |    4 |
|   10 |   20 |
+------+------+
```

Although TiFlash can automatically initiate compaction of old data in the background, the old data will not be cleaned up physically until it has been compacted and its data versions are older than the GC safe point. After the physical cleaning, the cleaned old data will no longer be returned in FastScan mode. The timing of data compaction is automatically triggered by various factors. You can also manually trigger data compaction using the [`ALTER TABLE ... COMPACT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table-compact) statement.
## Enable and disable FastScan

By default, the variable is `tiflash_fastscan=OFF` at the session level and global level, that is, the FastScan feature is not enabled. You can view the variable information by using the following statement.

```
show variables like 'tiflash_fastscan';

+------------------+-------+
| Variable_name    | Value |
+------------------+-------+
| tiflash_fastscan | OFF   |
+------------------+-------+
```

```
show global variables like 'tiflash_fastscan';

+------------------+-------+
| Variable_name    | Value |
+------------------+-------+
| tiflash_fastscan | OFF   |
+------------------+-------+
```

You can configure the variable `tiflash_fastscan` at the session level and global level. If you need to enable FastScan in the current session, you can do so with the following statement:

```
set session tiflash_fastscan=ON;
```

You can also set `tiflash_fastscan` at the global level. The new setting will take effect in new sessions, but will not take effect in the current and previous sessions. Besides, in new sessions, `tiflash_fastscan` of the session level and global level will both take the new value.

```
set global tiflash_fastscan=ON;
```

You can disable FastScan using the following statement.

```
set session tiflash_fastscan=OFF;
set global tiflash_fastscan=OFF;
```
## Mechanism of FastScan

Data in the storage layer of TiFlash is stored in two layers: Delta layer and Stable layer.

By default, FastScan is not enabled, and the TableScan operator processes data in the following steps:

1. Read data: create separate data streams in the Delta layer and Stable layer to read the respective data.
2. Sort Merge: merge the data streams created in step 1. Then return the data after sorting in the order of (primary key column, timestamp column).
3. Range Filter: according to the data range, filter the data generated in step 2, and then return the data.
4. MVCC + Column Filter: filter the data generated in step 3 through MVCC (that is, filtering the data version according to the primary key column and the timestamp column) and through columns (that is, filtering out unneeded columns), and then return the data.

FastScan gains faster query speed by sacrificing some data consistency. Step 2 and the MVCC part in step 4 in the normal scan process are omitted in FastScan, thus improving query performance.
