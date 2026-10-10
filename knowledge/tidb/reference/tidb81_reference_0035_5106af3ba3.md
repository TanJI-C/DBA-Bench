# Cached table writes, reverting, limits, and compatibility restrictions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/cached-tables.md`
- Source Title: `Cached Tables`
- Source Heading Path: `Cached Tables > Examples > Write data to a cached table | Cached Tables > Examples > Revert a cached table to a normal table | Cached Tables > Size limit of cached tables | Cached Tables > Compatibility restrictions with other TiDB features | Cached Tables > Compatibility with TiDB migration tools | Cached Tables > See also`
- Source Line Ranges: `131-244`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `br`, `ticdc`, `dumpling`
- Topic Tags: `cached-tables`, `write-latency`, `table-cache-lease`, `nocache`, `ddl-restrictions`, `size-limit`, `feature-compatibility`, `migration-tools`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0035_5106af3ba3`
- Source ID: `tidb-docs-8.1:cached-tables.md#write-data-to-a-cached-table`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f06194d407987dd801b8d792dcca518f3c3762cb801b159472fe3145e4f1e1b2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/cached-tables#write-data-to-a-cached-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/cached-tables.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about cached table write latency, reverting a cached table with NOCACHE before DDL, cached table size limits, unsupported feature combinations, or how BR, TiCDC, and Dumpling treat cached tables.
- Retrieval Keywords: cached tables, INSERT INTO users(id, name) VALUES(1001, 'Davis'), second-level write latency, tidb_table_cache_lease, set @@global.tidb_table_cache_lease = 10, mysql.table_cache_meta, lock_type, lease, ALTER TABLE users NOCACHE, ERROR 8242 (HY000): 'Truncate Table' is unsupported on cache tables., ERROR 8242 (HY000): 'Alter Table' is unsupported on cache tables., 64 MB, ALTER TABLE t CACHE, ALTER TABLE t ADD PARTITION, temporary tables, views, Stale Read, tidb_snapshot, Backup & Restore (BR), TiCDC, Dumpling, ALTER TABLE ... CACHE
- Follow-up Guidance: The source also states that `mysql.table_cache_meta` stores cached table metadata for internal TiDB use, and modifying it is not recommended because unexpected errors might occur.
- Classification Note: This is reference content because it lists cached table behaviors, exact SQL statements and errors, the `tidb_table_cache_lease` variable, the `mysql.table_cache_meta` metadata table, the 64 MB size limit, unsupported features, and migration tool compatibility details.

## Official Source Content

### Write data to a cached table

Cached tables support data writes. For example, you can insert a record into the `users` table:

```sql
INSERT INTO users(id, name) VALUES(1001, 'Davis');
```

```sql
Query OK, 1 row affected (0.00 sec)
```

```sql
SELECT * FROM users;
```

```sql
+------+-------+
| id   | name  |
+------+-------+
| 1001 | Davis |
+------+-------+
1 row in set (0.00 sec)
```

> **Note:**
>
> When you insert data to a cached table, second-level write latency might occur. The latency is controlled by the global environment variable [`tidb_table_cache_lease`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_table_cache_lease-new-in-v600). You can decide whether to use the cached table feature by checking whether the latency is acceptable based on your application. For example, in a read-only scenario, you can increase the value of `tidb_table_cache_lease`:
>
> ```sql
> set @@global.tidb_table_cache_lease = 10;
> ```
>
> The write latency of cached tables is high, because the cached table feature is implemented with a complex mechanism that requires a lease to be set for each cache. When there are multiple TiDB instances, one instance does not know whether the other instances have cached data. If an instance modifies the table data directly, the other instances read the old cache data. To ensure correctness, the cached table implementation uses a lease mechanism to ensure that the data is not modified before the lease expires. That is why the write latency is high.

The metadata of cached tables is stored in the `mysql.table_cache_meta` table. This table records the IDs of all cached tables, the current lock status (`lock_type`), and the lock lease information (`lease`). This table is only internally used in TiDB and you are not recommended to modify it. Otherwise, unexpected errors might occur.

```sql
SHOW CREATE TABLE mysql.table_cache_meta\G
*************************** 1. row ***************************
       Table: table_cache_meta
Create Table: CREATE TABLE `table_cache_meta` (
  `tid` bigint(11) NOT NULL DEFAULT '0',
  `lock_type` enum('NONE','READ','INTEND','WRITE') NOT NULL DEFAULT 'NONE',
  `lease` bigint(20) NOT NULL DEFAULT '0',
  `oldReadLease` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`tid`) /*T![clustered_index] CLUSTERED */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
1 row in set (0.00 sec)
```
### Revert a cached table to a normal table

> **Note:**
>
> Executing DDL statements on a cached table will fail. Before executing DDL statements on a cached table, you need to remove the cache attribute first and set the cached table back to a normal table.

```sql
TRUNCATE TABLE users;
```

```sql
ERROR 8242 (HY000): 'Truncate Table' is unsupported on cache tables.
```

```sql
mysql> ALTER TABLE users ADD INDEX k_id(id);
```

```sql
ERROR 8242 (HY000): 'Alter Table' is unsupported on cache tables.
```

To revert a cached table to a normal table, use `ALTER TABLE t NOCACHE`:

```sql
ALTER TABLE users NOCACHE;
```

```sql
Query OK, 0 rows affected (0.00 sec)
```
## Size limit of cached tables

Cached tables are only suitable for scenarios with small tables, because TiDB loads the data of an entire table into memory, and the cached data becomes invalid after modification and needs to be reloaded.

Currently, the size limit of a cached table is 64 MB in TiDB. If the table data exceeds 64 MB, executing `ALTER TABLE t CACHE` will fail.
## Compatibility restrictions with other TiDB features

Cached tables **DO NOT** support the following features:

- Performing the `ALTER TABLE t ADD PARTITION` operation on partitioned tables is not supported.
- Performing the `ALTER TABLE t CACHE` operation on temporary tables is not supported.
- Performing the `ALTER TABLE t CACHE` operation on views is not supported.
- Stale Read is not supported.
- Direct DDL operations on a cached table are not supported. You need to set the cached table back to a normal table first by using `ALTER TABLE t NOCACHE` before performing DDL operations.

Cached tables **CANNOT** be used in the following scenarios:

- Setting the system variable `tidb_snapshot` to read historical data.
- During modification, the cached data becomes invalid until the data is reloaded.
## Compatibility with TiDB migration tools

The cached table is a TiDB extension to MySQL syntax. Only TiDB can recognize the `ALTER TABLE ... CACHE` statement. TiDB migration tools **DO NOT** support cached tables, including Backup & Restore (BR), TiCDC, and Dumpling. These tools treat cached tables as normal tables.

That is to say, when a cached table is backed up and restored, it becomes a normal table. If the downstream cluster is a different TiDB cluster and you want to continue using the cached table feature, you can manually enable cached tables on the downstream cluster by executing `ALTER TABLE ... CACHE` on the downstream table.
## See also

* [ALTER TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table)
* [System Variables](https://docs.pingcap.com/tidb/stable/system-variables)
