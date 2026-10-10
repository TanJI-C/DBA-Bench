# SHOW STATS_LOCKED syntax and usage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-stats-locked.md`
- Source Title: `SHOW STATS_LOCKED`
- Source Heading Path: `SHOW STATS_LOCKED | SHOW STATS_LOCKED > Synopsis | SHOW STATS_LOCKED > Examples | SHOW STATS_LOCKED > MySQL compatibility | SHOW STATS_LOCKED > See also`
- Source Line Ranges: `5-74`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `pd`
- Topic Tags: `statistics`, `locked-stats`, `show-statement`, `syntax`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0677_baad3f8516`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-stats-locked.md#show-stats-locked`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c19f2ce46f0dc71c24c701343606f27a6d6bdca265925ac4f3d04ffd3d84ce20`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-locked#show-stats-locked
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-stats-locked.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, output columns, examples, or MySQL compatibility of the `SHOW STATS_LOCKED` statement that shows tables whose statistics are locked.
- Retrieval Keywords: SHOW STATS_LOCKED, ShowStatsLockedStmt, SHOW STATS_LOCKED LIKE, SHOW STATS_LOCKED WHERE, Db_name, Table_name, Partition_name, Status, locked statistics, LOCK STATS, UNLOCK STATS, TiDB extension to MySQL syntax
- Follow-up Guidance: The source also points to related material on `Statistics`, `LOCK STATS`, and `UNLOCK STATS`.
- Classification Note: The official content is reference material because it defines `SHOW STATS_LOCKED` syntax, returned columns, an example result, and its MySQL compatibility.

## Official Source Content

# SHOW STATS_LOCKED

`SHOW STATS_LOCKED` shows the tables whose statistics are locked.

Currently, the `SHOW STATS_LOCKED` statement returns the following columns:

| Column name | Description            |
| -------- | ------------- |
| `Db_name` | The database name |
| `Table_name` | The table name |
| `Partition_name` | The partition name |
| `Status` | The statistics status, such as `locked` |
## Synopsis

```ebnf+diagram
ShowStatsLockedStmt ::= 'SHOW' 'STATS_LOCKED' ShowLikeOrWhereOpt

ShowLikeOrWhereOpt ::= 'LIKE' SimpleExpr | 'WHERE' Expression
```
## Examples

Create table `t`, and insert data into it. When the statistics of table `t` are not locked, the `ANALYZE` statement can be successfully executed.

```sql
mysql> CREATE TABLE t(a INT, b INT);
Query OK, 0 rows affected (0.03 sec)

mysql> INSERT INTO t VALUES (1,2), (3,4), (5,6), (7,8);
Query OK, 4 rows affected (0.00 sec)
Records: 4  Duplicates: 0  Warnings: 0

mysql> ANALYZE TABLE t;
Query OK, 0 rows affected, 1 warning (0.02 sec)

mysql> SHOW WARNINGS;
+-------+------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Level | Code | Message                                                                                                                                                                                                               |
+-------+------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Note  | 1105 | Analyze use auto adjusted sample rate 1.000000 for table test.t, reason to use this rate is "Row count in stats_meta is much smaller compared with the row count got by PD, use min(1, 15000/4) as the sample-rate=1" |
+-------+------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

Lock the statistics of table `t` and execute `SHOW STATS_LOCKED`. The output shows that the statistics of table `t` have been locked.

```sql
mysql> LOCK STATS t;
Query OK, 0 rows affected (0.00 sec)

mysql> SHOW STATS_LOCKED;
+---------+------------+----------------+--------+
| Db_name | Table_name | Partition_name | Status |
+---------+------------+----------------+--------+
| test    | t          |                | locked |
+---------+------------+----------------+--------+
1 row in set (0.01 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [Statistics](https://docs.pingcap.com/tidb/stable/statistics#lock-statistics)
* [LOCK STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-stats)
* [UNLOCK STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-unlock-stats)
