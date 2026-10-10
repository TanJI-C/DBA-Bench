# Clustered index compatibility across versions tools and features

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/clustered-indexes.md`
- Source Title: `Clustered Indexes`
- Source Heading Path: `Clustered Indexes > Compatibility | Clustered Indexes > Compatibility > Compatibility with earlier and later TiDB versions | Clustered Indexes > Compatibility > Compatibility with MySQL | Clustered Indexes > Compatibility > Compatibility with TiDB migration tools | Clustered Indexes > Compatibility > Compatibility with other TiDB features`
- Source Line Ranges: `167-226`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `br`, `dm`, `dumpling`, `lightning`, `ticdc`, `shared`
- Topic Tags: `compatibility`, `upgrade`, `downgrade`, `mysql`, `migration-tools`, `br`, `dumpling`, `lightning`, `dm`, `ticdc`, `split-table`, `auto-random`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0057_25c5d8d294`
- Source ID: `tidb-docs-8.1:clustered-indexes.md#compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4a272bb69d617093d84149f2ea00c9e770be17c2d55178dc09efa6de5b874d88`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/clustered-indexes#compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/clustered-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when checking clustered index compatibility across TiDB versions, MySQL syntax handling, migration tools, SPLIT TABLE behavior, or AUTO_RANDOM requirements.
- Retrieval Keywords: Clustered Indexes Compatibility, compatibility with earlier and later TiDB versions, compatibility with MySQL, compatibility with TiDB migration tools, compatibility with other TiDB features, @@tidb_enable_clustered_index, SHOW CREATE TABLE, CLUSTERED, NONCLUSTERED, BR, Dumpling, TiDB Lightning, DM, TiCDC, SPLIT TABLE BY, SPLIT TABLE BETWEEN, Split table region lower value count should be 2, Column count doesn't match value count at row 0, AUTO_RANDOM, Invalid auto random: column a is not the integer primary key, or the primary key is nonclustered
- Follow-up Guidance: The content also explains that upgrading tables with clustered indexes is supported but downgrading is not, and that TiDB specific SQL comments for CLUSTERED and NONCLUSTERED are ignored by MySQL and earlier TiDB versions.
- Classification Note: This is reference content because it summarizes official compatibility rules, tool support, system variable behavior, and exact SQL examples and errors related to clustered indexes.

## Official Source Content

## Compatibility
### Compatibility with earlier and later TiDB versions

TiDB supports upgrading tables with clustered indexes but not downgrading such tables, which means that data in tables with clustered indexes on a later TiDB version is not available on an earlier one.

The clustered index feature is partially supported in TiDB v3.0 and v4.0. It is enabled by default when the following requirements are fully met:

- The table contains a `PRIMARY KEY`.
- The `PRIMARY KEY` consists of only one column.
- The `PRIMARY KEY` is an `INTEGER`.

Since TiDB v5.0, the clustered index feature is fully supported for all types of primary keys, but the default behavior is consistent with TiDB v3.0 and v4.0. To change the default behavior, you can configure the system variable `@@tidb_enable_clustered_index` to `ON` or `OFF`. For more details, see [Create a table with clustered indexes](#create-a-table-with-clustered-indexes).
### Compatibility with MySQL

TiDB specific comment syntax supports wrapping the keywords `CLUSTERED` and `NONCLUSTERED` in a comment. The result of `SHOW CREATE TABLE` also contains TiDB specific SQL comments. MySQL databases and TiDB databases of an earlier version will ignore these comments.
### Compatibility with TiDB migration tools

The clustered index feature is only compatible with the following migration tools in v5.0 and later versions:

- Backup and restore tools: BR, Dumpling, and TiDB Lightning.
- Data migration and replication tools: DM and TiCDC.

However, you cannot convert a table with non-clustered indexes to a table with clustered indexes by backing up and restoring the table using the v5.0 BR tool, and vice versa.
### Compatibility with other TiDB features

For a table with a combined primary key or a single non-integer primary key, if you change the primary key from a non-clustered index to a clustered index, the keys of its row data change as well. Therefore, `SPLIT TABLE BY/BETWEEN` statements that are executable in TiDB versions earlier than v5.0 are no longer workable in v5.0 and later versions of TiDB. If you want to split a table with clustered indexes using `SPLIT TABLE BY/BETWEEN`, you need to provide the value of the primary key column, instead of specifying an integer value. See the following example:

```sql
mysql> create table t (a int, b varchar(255), primary key(a, b) clustered);
Query OK, 0 rows affected (0.01 sec)
mysql> split table t between (0) and (1000000) regions 5;
ERROR 1105 (HY000): Split table region lower value count should be 2
mysql> split table t by (0), (50000), (100000);
ERROR 1136 (21S01): Column count doesn't match value count at row 0
mysql> split table t between (0, 'aaa') and (1000000, 'zzz') regions 5;
+--------------------+----------------------+
| TOTAL_SPLIT_REGION | SCATTER_FINISH_RATIO |
+--------------------+----------------------+
|                  4 |                    1 |
+--------------------+----------------------+
1 row in set (0.00 sec)
mysql> split table t by (0, ''), (50000, ''), (100000, '');
+--------------------+----------------------+
| TOTAL_SPLIT_REGION | SCATTER_FINISH_RATIO |
+--------------------+----------------------+
|                  3 |                    1 |
+--------------------+----------------------+
1 row in set (0.01 sec)
```

The attribute [`AUTO_RANDOM`](https://docs.pingcap.com/tidb/stable/auto-random) can only be used on clustered indexes. Otherwise, TiDB returns the following error:

```sql
mysql> create table t (a bigint primary key nonclustered auto_random);
ERROR 8216 (HY000): Invalid auto random: column a is not the integer primary key, or the primary key is nonclustered
```
