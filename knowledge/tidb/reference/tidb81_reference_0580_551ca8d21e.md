# DROP STATS syntax usage examples and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-drop-stats.md`
- Source Title: `DROP STATS`
- Source Heading Path: `DROP STATS | DROP STATS > Synopsis | DROP STATS > Usage | DROP STATS > Examples | DROP STATS > MySQL compatibility | DROP STATS > See also`
- Source Line Ranges: `5-97`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `drop-stats`, `statistics`, `syntax`, `partition`, `globalstats`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0580_551ca8d21e`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-drop-stats.md#drop-stats`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c48454c853c0a3f02cca2dc742f5d6fa959f871386f7390ada696d3510f4c46e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-stats#drop-stats
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-drop-stats.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB SQL syntax and behavior of deleting table statistics, partition statistics, or GlobalStats with DROP STATS.
- Retrieval Keywords: DROP STATS, DropStatsStmt, DROP STATS TableName, DROP STATS TableName PARTITION PartitionNameList, DROP STATS TableName GLOBAL, SHOW STATS_META, GlobalStats, dynamic pruning mode, partitioned table, TiDB extension to MySQL syntax
- Follow-up Guidance: The examples show verifying the result with SHOW STATS_META WHERE db_name='test' and table_name='t', which returns Empty set after DROP STATS t.
- Classification Note: This is reference content because it defines the DROP STATS syntax, describes usage variants for table, PARTITION, and GLOBAL, and notes MySQL compatibility.

## Official Source Content

# DROP STATS

The `DROP STATS` statement is used to delete the statistics of the selected table from the selected database.
## Synopsis

```ebnf+diagram
DropStatsStmt ::=
    'DROP' 'STATS' TableName  ("PARTITION" partition | "GLOBAL")? ( ',' TableName )*

TableName ::=
    Identifier ('.' Identifier)?
```
## Usage

The following statement deletes all statistics of `TableName`. If a partitioned table is specified, this statement deletes statistics of all partitions in this table as well as [GlobalStats generated in dynamic pruning mode](https://docs.pingcap.com/tidb/stable/statistics#collect-statistics-of-partitioned-tables-in-dynamic-pruning-mode).

```sql
DROP STATS TableName
```

```
Query OK, 0 rows affected (0.00 sec)
```

The following statement only deletes statistics of the specified partitions in `PartitionNameList`.

```sql
DROP STATS TableName PARTITION PartitionNameList;
```

```
Query OK, 0 rows affected (0.00 sec)
```

The following statement only deletes GlobalStats generated in dynamic pruning mode of the specified table.

```sql
DROP STATS TableName GLOBAL;
```

```
Query OK, 0 rows affected (0.00 sec)
```
## Examples

```sql
CREATE TABLE t(a INT);
```

```
Query OK, 0 rows affected (0.01 sec)
```

```sql
SHOW STATS_META WHERE db_name='test' and table_name='t';
```

```
+---------+------------+----------------+---------------------+--------------+-----------+
| Db_name | Table_name | Partition_name | Update_time         | Modify_count | Row_count |
+---------+------------+----------------+---------------------+--------------+-----------+
| test    | t          |                | 2020-05-25 20:34:33 |            0 |         0 |
+---------+------------+----------------+---------------------+--------------+-----------+
1 row in set (0.00 sec)
```

```sql
DROP STATS t;
```

```
Query OK, 0 rows affected (0.00 sec)
```

```sql
SHOW STATS_META WHERE db_name='test' and table_name='t';
```

```
Empty set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [Introduction to Statistics](https://docs.pingcap.com/tidb/stable/statistics)
