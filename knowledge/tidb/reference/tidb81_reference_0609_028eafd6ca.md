# LOCK STATS syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-lock-stats.md`
- Source Title: `LOCK STATS`
- Source Heading Path: `LOCK STATS | LOCK STATS > Synopsis | LOCK STATS > Examples`
- Source Line Ranges: `5-80`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `pd`
- Topic Tags: `statistics`, `lock-stats`, `analyze`, `partitions`, `show-stats-locked`, `syntax`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0609_028eafd6ca`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-lock-stats.md#lock-stats`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `953ad2b595f33f8160845a645cb47f4827ea9a2a902936ebb1afbf81e582719c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-stats#lock-stats
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-lock-stats.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the `LOCK STATS` SQL syntax, examples of locking table or partition statistics, or the warning and inspection output related to locked statistics during `ANALYZE`.
- Retrieval Keywords: LOCK STATS, LockStatsStmt, TableNameList, PartitionNameList, LOCK STATS t, TableName PARTITION PartitionNameList, SHOW STATS_LOCKED, ANALYZE TABLE t, skip analyze locked table: test.t, Behaviors of locking statistics, statistics locked, partitions
- Follow-up Guidance: The source points to `Behaviors of locking statistics` for details on the behavior after statistics are locked.
- Classification Note: This is reference content because it provides the `LOCK STATS` statement syntax and concrete SQL examples with `SHOW STATS_LOCKED`, `ANALYZE`, and warning output.

## Official Source Content

# LOCK STATS

`LOCK STATS` is used to lock the statistics of tables or partitions. When the statistics is locked, TiDB does not automatically update the statistics of the table or partition. For details on the behavior, see [Behaviors of locking statistics](https://docs.pingcap.com/tidb/stable/statistics#behaviors-of-locking-statistics).
## Synopsis

```ebnf+diagram
LockStatsStmt ::=
    'LOCK' 'STATS' (TableNameList) | (TableName 'PARTITION' PartitionNameList)

TableNameList ::=
    TableName (',' TableName)*

TableName ::=
    Identifier ( '.' Identifier )?

PartitionNameList ::=
    Identifier ( ',' Identifier )*
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

Lock the statistics of table `t` and execute `ANALYZE`. From the output of `SHOW STATS_LOCKED`, you can see that the statistics of table `t` have been locked. The warning message shows that the `ANALYZE` statement has skipped table `t`.

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

mysql> ANALYZE TABLE t;
Query OK, 0 rows affected, 2 warnings (0.00 sec)

mysql> SHOW WARNINGS;
+---------+------+-----------------------------------------------------------------------------------------------------------------------------------------+
| Level   | Code | Message                                                                                                                                 |
+---------+------+-----------------------------------------------------------------------------------------------------------------------------------------+
| Note    | 1105 | Analyze use auto adjusted sample rate 1.000000 for table test.t, reason to use this rate is "use min(1, 110000/8) as the sample-rate=1" |
| Warning | 1105 | skip analyze locked table: test.t                                                                                                       |
+---------+------+-----------------------------------------------------------------------------------------------------------------------------------------+
2 rows in set (0.00 sec)
```

In addition, you can also lock the statistics of a partition using `LOCK STATS`. For example:

Create a partition table `t`, and insert data into it. When the statistics of partition `p1` are not locked, the `ANALYZE` statement can be successfully executed.
