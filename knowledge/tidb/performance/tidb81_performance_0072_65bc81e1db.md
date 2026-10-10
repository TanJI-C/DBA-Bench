# Cached tables overview, setup, and verification

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/cached-tables.md`
- Source Title: `Cached Tables`
- Source Heading Path: `Cached Tables | Cached Tables > Usage scenarios | Cached Tables > Examples | Cached Tables > Examples > Set a normal table to a cached table | Cached Tables > Examples > Verify a cached table`
- Source Line Ranges: `5-130`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `cached-tables`, `read-performance`, `hotspot-tables`, `usage-scenarios`, `alter-table`, `show-create-table`, `trace`, `unionscan`, `memory-cache`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0072_65bc81e1db`
- Source ID: `tidb-docs-8.1:cached-tables.md#cached-tables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `da33caca07ef7e268a3914f516ef37a1cb144ea91e637214e52a934c5821d119`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/cached-tables#cached-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/cached-tables.md

## Retrieval Guidance

- Use When: Use this chunk when you need the overview, setup, and verification details for TiDB cached tables, including how to enable caching on a table and confirm reads come from memory instead of TiKV.
- Retrieval Keywords: cached tables, ALTER TABLE users CACHE, ALTER TABLE ... CACHE, SHOW CREATE TABLE, CACHED ON, TRACE SELECT * FROM users, regionRequest.SendReqCtx, UnionScan, *executor.UnionScanExec.Next, TableReaderExecutor.Open, hotspot Region, small hotspot tables, read-only or rarely updated, less than 4 MiB, write QPS less than 10 times per minute
- Follow-up Guidance: The chunk also shows that `SHOW CREATE TABLE` displays `/* CACHED ON */`, `TRACE` initially includes `regionRequest.SendReqCtx` before the cache is loaded and omits it afterward, and `explain` shows the `UnionScan` operator for cached tables.
- Classification Note: This is classified as performance for the TiDB component because the content explains the cached table feature for frequently accessed but rarely updated small hotspot tables and how it improves read performance by serving data from TiDB memory instead of accessing TiKV.

## Official Source Content

# Cached Tables

In v6.0.0, TiDB introduces the cached table feature for frequently accessed but rarely updated small hotspot tables. When this feature is used, the data of an entire table is loaded into the memory of the TiDB server, and TiDB directly gets the table data from the memory without accessing TiKV, which improves the read performance.

This document describes the usage scenarios of cached tables, the examples, and the compatibility restrictions with other TiDB features.
## Usage scenarios

The cached table feature is suitable for tables with the following characteristics:

- The data volume of the table is small, for example, less than 4 MiB.
- The table is read-only or rarely updated, for example, with a write QPS (queries per second) of less than 10 times per minute.
- The table is frequently accessed, and you expect a better read performance, for example, when encountering hotspots on small tables during direct reads from TiKV.

When the data volume of the table is small but the data is frequently accessed, the data is concentrated on a Region in TiKV and makes it a hotspot Region, which affects the performance. Therefore, the typical usage scenarios of cached tables are as follows:

- Configuration tables, from which applications read the configuration information.
- The tables of exchange rates in the financial sector. These tables are updated only once a day but not in real-time.
- Bank branch or network information tables, which are rarely updated.

Take configuration tables as an example. When the application restarts, the configuration information is loaded in all connections, which causes a high read latency. In this case, you can solve this problem by using the cached tables feature.
## Examples

This section describes the usage of cached tables by examples.
### Set a normal table to a cached table

Suppose that there is a table `users`:

```sql
CREATE TABLE users (
    id BIGINT,
    name VARCHAR(100),
    PRIMARY KEY(id)
);
```

To set this table to a cached table, use the `ALTER TABLE` statement:

```sql
ALTER TABLE users CACHE;
```

```sql
Query OK, 0 rows affected (0.01 sec)
```
### Verify a cached table

To verify a cached table, use the `SHOW CREATE TABLE` statement. If the table is cached, the returned result contains the `CACHED ON` attribute:

```sql
SHOW CREATE TABLE users;
```

```sql
+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Table | Create Table                                                                                                                                                                                                               |
+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| users | CREATE TABLE `users` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin /* CACHED ON */ |
+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

After reading data from a cached table, TiDB loads the data in memory. You can use the [`TRACE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-trace) statement to check whether the data is loaded into memory. When the cache is not loaded, the returned result contains the `regionRequest.SendReqCtx` attribute, which indicates that TiDB reads data from TiKV.

```sql
TRACE SELECT * FROM users;
```

```sql
+------------------------------------------------+-----------------+------------+
| operation                                      | startTS         | duration   |
+------------------------------------------------+-----------------+------------+
| trace                                          | 17:47:39.969980 | 827.73µs   |
|   ├─session.ExecuteStmt                        | 17:47:39.969986 | 413.31µs   |
|   │ ├─executor.Compile                         | 17:47:39.969993 | 198.29µs   |
|   │ └─session.runStmt                          | 17:47:39.970221 | 157.252µs  |
|   │   └─TableReaderExecutor.Open               | 17:47:39.970294 | 47.068µs   |
|   │     └─distsql.Select                       | 17:47:39.970312 | 24.729µs   |
|   │       └─regionRequest.SendReqCtx           | 17:47:39.970454 | 189.601µs  |
|   ├─*executor.UnionScanExec.Next               | 17:47:39.970407 | 353.073µs  |
|   │ ├─*executor.TableReaderExecutor.Next       | 17:47:39.970411 | 301.106µs  |
|   │ └─*executor.TableReaderExecutor.Next       | 17:47:39.970746 | 6.57µs     |
|   └─*executor.UnionScanExec.Next               | 17:47:39.970772 | 17.589µs   |
|     └─*executor.TableReaderExecutor.Next       | 17:47:39.970776 | 6.59µs     |
+------------------------------------------------+-----------------+------------+
12 rows in set (0.01 sec)
```

After executing [`TRACE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-trace) again, the returned result no longer contains the `regionRequest.SendReqCtx` attribute, which indicates that TiDB no longer reads data from TiKV but reads data from the memory instead.

```sql
+----------------------------------------+-----------------+------------+
| operation                              | startTS         | duration   |
+----------------------------------------+-----------------+------------+
| trace                                  | 17:47:40.533888 | 453.547µs  |
|   ├─session.ExecuteStmt                | 17:47:40.533894 | 402.341µs  |
|   │ ├─executor.Compile                 | 17:47:40.533903 | 205.54µs   |
|   │ └─session.runStmt                  | 17:47:40.534141 | 132.084µs  |
|   │   └─TableReaderExecutor.Open       | 17:47:40.534202 | 14.749µs   |
|   ├─*executor.UnionScanExec.Next       | 17:47:40.534306 | 3.21µs     |
|   └─*executor.UnionScanExec.Next       | 17:47:40.534316 | 1.219µs    |
+----------------------------------------+-----------------+------------+
7 rows in set (0.00 sec)
```

Note that the `UnionScan` operator is used to read the cached tables, so you can see `UnionScan` in the execution plan of the cached tables through `explain`:

```sql
+-------------------------+---------+-----------+---------------+--------------------------------+
| id                      | estRows | task      | access object | operator info                  |
+-------------------------+---------+-----------+---------------+--------------------------------+
| UnionScan_5             | 1.00    | root      |               |                                |
| └─TableReader_7         | 1.00    | root      |               | data:TableFullScan_6           |
|   └─TableFullScan_6     | 1.00    | cop[tikv] | table:users   | keep order:false, stats:pseudo |
+-------------------------+---------+-----------+---------------+--------------------------------+
3 rows in set (0.00 sec)
```
