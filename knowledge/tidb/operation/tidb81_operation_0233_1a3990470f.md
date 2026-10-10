# Lock and unlock table statistics

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > Lock statistics`
- Source Line Ranges: `563-637`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `pd`
- Topic Tags: `statistics`, `lock-stats`, `analyze`, `table-statistics`, `partition-statistics`, `warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0233_1a3990470f`
- Source ID: `tidb-docs-8.1:statistics.md#lock-statistics`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fc5c0c37ff1c8f4d96563b137a76ffb996bc6719e54e25729b20f0b337958f7e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#lock-statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when asking how locked table or partition statistics affect ANALYZE behavior and how to view or change the lock state in TiDB.
- Retrieval Keywords: LOCK STATS, UNLOCK STATS, SHOW STATS_LOCKED, ANALYZE TABLE, lock statistics, locked table statistics, partition statistics, skip analyze locked table: test.t, statistics of a table cannot be modified
- Follow-up Guidance: The content also shows that SHOW WARNINGS can display the warning "skip analyze locked table: test.t" after ANALYZE TABLE on a locked table.
- Classification Note: This is an operation topic because the content demonstrates SQL operations to lock, unlock, inspect, and analyze table or partition statistics in TiDB.

## Official Source Content

## Lock statistics

Starting from v6.5.0, TiDB supports locking statistics. After the statistics of a table or a partition are locked, the statistics of the table cannot be modified and the `ANALYZE` statement cannot be executed on the table. For example:

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

Lock the statistics of table `t` and execute `ANALYZE`. The warning message shows that the `ANALYZE` statement has skipped table `t`.

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

Unlock the statistics of table `t` and `ANALYZE` can be successfully executed again.

```sql
mysql> UNLOCK STATS t;
Query OK, 0 rows affected (0.01 sec)

mysql> ANALYZE TABLE t;
Query OK, 0 rows affected, 1 warning (0.03 sec)

mysql> SHOW WARNINGS;
+-------+------+-----------------------------------------------------------------------------------------------------------------------------------------+
| Level | Code | Message                                                                                                                                 |
+-------+------+-----------------------------------------------------------------------------------------------------------------------------------------+
| Note  | 1105 | Analyze use auto adjusted sample rate 1.000000 for table test.t, reason to use this rate is "use min(1, 110000/8) as the sample-rate=1" |
+-------+------+-----------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

In addition, you can also lock the statistics of a partition using [`LOCK STATS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-stats). For example:

Create a partition table `t`, and insert data into it. When the statistics of partition `p1` are not locked, the `ANALYZE` statement can be successfully executed.
