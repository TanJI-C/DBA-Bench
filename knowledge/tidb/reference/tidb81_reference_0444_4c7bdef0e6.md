# Auto-increment ID differences from MySQL

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/mysql-compatibility.md`
- Source Title: `MySQL Compatibility`
- Source Heading Path: `MySQL Compatibility > Differences from MySQL > Auto-increment ID`
- Source Line Ranges: `78-135`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `auto-increment`, `mysql-compatibility`, `rowid`, `allocator`, `hotspot`, `version-differences`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0444_4c7bdef0e6`
- Source ID: `tidb-docs-8.1:mysql-compatibility.md#auto-increment-id`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d7e4ade8802d506432bd4797cc5ff66a85bce15f3f80f84178d92ae63acacd39`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/mysql-compatibility#auto-increment-id
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/mysql-compatibility.md

## Retrieval Guidance

- Use When: Use this chunk when comparing TiDB and MySQL behavior for AUTO_INCREMENT, shared allocator behavior with _tidb_rowid, or restrictions on modifying the AUTO_INCREMENT attribute.
- Retrieval Keywords: Auto-increment ID, AUTO_INCREMENT, MySQL compatibility mode, Duplicated Error, tidb_allow_remove_auto_inc, ALTER TABLE MODIFY, ALTER TABLE CHANGE, _tidb_rowid, shared allocator, globally unique, incremental within a single TiDB server, not necessarily allocated sequentially, cannot be recovered, v6.6.0 and earlier, v7.0.0, primary keys or index prefixes, AUTO_RANDOM, hotspot
- Follow-up Guidance: The source refers to the AUTO_INCREMENT, AUTO_RANDOM, and Troubleshoot HotSpot Issues documentation for more details.
- Classification Note: This is a reference chunk because it documents TiDB AUTO_INCREMENT semantics, version-specific differences, and related SQL identifiers such as _tidb_rowid and tidb_allow_remove_auto_inc.

## Official Source Content

### Auto-increment ID

+ In TiDB, the auto-incremental column values (IDs) are globally unique and incremental within a single TiDB server. To make the IDs incremental among multiple TiDB servers, you can use the [`AUTO_INCREMENT` MySQL compatibility mode](https://docs.pingcap.com/tidb/stable/auto-increment#mysql-compatibility-mode). However, the IDs are not necessarily allocated sequentially, so it is recommended that you avoid mixing default and custom values to prevent encountering the `Duplicated Error` message.

+ You can use the `tidb_allow_remove_auto_inc` system variable to allow or forbid removing the `AUTO_INCREMENT` column attribute. To remove the column attribute, use the `ALTER TABLE MODIFY` or `ALTER TABLE CHANGE` syntax.

+ TiDB does not support adding the `AUTO_INCREMENT` column attribute, and once removed, it cannot be recovered.

+ For TiDB v6.6.0 and earlier versions, auto-increment columns in TiDB behave the same as in MySQL InnoDB, requiring them to be primary keys or index prefixes. Starting from v7.0.0, TiDB removes this restriction, allowing for more flexible table primary key definitions. [#40580](https://github.com/pingcap/tidb/issues/40580)

For more details, see [`AUTO_INCREMENT`](https://docs.pingcap.com/tidb/stable/auto-increment).

> **Note:**
>
> + If you do not specify a primary key when creating a table, TiDB uses `_tidb_rowid` to identify the row. The allocation of this value shares an allocator with the auto-increment column (if such a column exists). If you specify an auto-increment column as the primary key, TiDB uses this column to identify the row. In this situation, the following situation might occur:

```sql
mysql> CREATE TABLE t(id INT UNIQUE KEY AUTO_INCREMENT);
Query OK, 0 rows affected (0.05 sec)

mysql> INSERT INTO t VALUES();
Query OK, 1 rows affected (0.00 sec)

mysql> INSERT INTO t VALUES();
Query OK, 1 rows affected (0.00 sec)

mysql> INSERT INTO t VALUES();
Query OK, 1 rows affected (0.00 sec)

mysql> SELECT _tidb_rowid, id FROM t;
+-------------+------+
| _tidb_rowid | id   |
+-------------+------+
|           2 |    1 |
|           4 |    3 |
|           6 |    5 |
+-------------+------+
3 rows in set (0.01 sec)
```

As shown, because of the shared allocator, the `id` increments by 2 each time. This behavior changes in [MySQL compatibility mode](https://docs.pingcap.com/tidb/stable/auto-increment#mysql-compatibility-mode), where there is no shared allocator and therefore no skipping of numbers.

> **Note:**
>
> The `AUTO_INCREMENT` attribute might cause hotspot in production environments. See [Troubleshoot HotSpot Issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues) for details. It is recommended to use [`AUTO_RANDOM`](https://docs.pingcap.com/tidb/stable/auto-random) instead.

> **Note:**
>
> The `AUTO_INCREMENT` attribute might cause hotspot in production environments. See [Troubleshoot HotSpot Issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#handle-auto-increment-primary-key-hotspot-tables-using-auto_random) for details. It is recommended to use [`AUTO_RANDOM`](https://docs.pingcap.com/tidb/stable/auto-random) instead.
