# Lock and unlock statistics for partitions and locking behaviors

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > Lock statistics | Introduction to Statistics > Lock statistics > Behaviors of locking statistics`
- Source Line Ranges: `638-720`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `pd`
- Topic Tags: `statistics`, `lock-stats`, `analyze`, `partitions`, `warnings`, `show-warnings`, `show-stats-locked`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0234_0e078dcf66`
- Source ID: `tidb-docs-8.1:statistics.md#lock-statistics`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d150bfc819c4963a47b7334a87559e6764129c804606fa5d0a1e5c5f67267c62`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#lock-statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when you need details about locking or unlocking partition statistics, checking locked status, and understanding how ANALYZE behaves on locked partitions or partitioned tables.
- Retrieval Keywords: LOCK STATS, UNLOCK STATS, SHOW STATS_LOCKED, ANALYZE TABLE t PARTITION p1, SHOW WARNINGS, skip analyze locked table: test.t partition (p1), Behaviors of locking statistics, partitioned table statistics lock, truncate a partition, exchange a partition
- Follow-up Guidance: The source also states that locking a partitioned table locks all partitions, and that truncating a table or partition releases the statistics lock on that table or partition.
- Classification Note: This is classified as an operation topic because the content shows SQL operations for LOCK STATS, UNLOCK STATS, SHOW STATS_LOCKED, ANALYZE, and the resulting lock behaviors.

## Official Source Content

```sql
mysql> CREATE TABLE t(a INT, b INT) PARTITION BY RANGE (a) (PARTITION p0 VALUES LESS THAN (10), PARTITION p1 VALUES LESS THAN (20), PARTITION p2 VALUES LESS THAN (30));
Query OK, 0 rows affected (0.03 sec)

mysql> INSERT INTO t VALUES (1,2), (3,4), (5,6), (7,8);
Query OK, 4 rows affected (0.00 sec)
Records: 4  Duplicates: 0  Warnings: 0

mysql> ANALYZE TABLE t;
Query OK, 0 rows affected, 6 warning (0.02 sec)

mysql> SHOW WARNINGS;
+---------+------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Level   | Code | Message                                                                                                                                                                                                                              |
+---------+------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Warning | 1105 | disable dynamic pruning due to t has no global stats                                                                                                                                                                                 |
| Note    | 1105 | Analyze use auto adjusted sample rate 1.000000 for table test.t's partition p0, reason to use this rate is "Row count in stats_meta is much smaller compared with the row count got by PD, use min(1, 15000/4) as the sample-rate=1" |
| Warning | 1105 | disable dynamic pruning due to t has no global stats                                                                                                                                                                                 |
| Note    | 1105 | Analyze use auto adjusted sample rate 1.000000 for table test.t's partition p1, reason to use this rate is "TiDB assumes that the table is empty, use sample-rate=1"                                                                 |
| Warning | 1105 | disable dynamic pruning due to t has no global stats                                                                                                                                                                                 |
| Note    | 1105 | Analyze use auto adjusted sample rate 1.000000 for table test.t's partition p2, reason to use this rate is "TiDB assumes that the table is empty, use sample-rate=1"                                                                 |
+---------+------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
6 rows in set (0.01 sec)
```

Lock the statistics of partition `p1` and execute `ANALYZE`. The warning message shows that the `ANALYZE` statement has skipped partition `p1`.

```sql
mysql> LOCK STATS t PARTITION p1;
Query OK, 0 rows affected (0.00 sec)

mysql> SHOW STATS_LOCKED;
+---------+------------+----------------+--------+
| Db_name | Table_name | Partition_name | Status |
+---------+------------+----------------+--------+
| test    | t          | p1             | locked |
+---------+------------+----------------+--------+
1 row in set (0.00 sec)

mysql> ANALYZE TABLE t PARTITION p1;
Query OK, 0 rows affected, 2 warnings (0.01 sec)

mysql> SHOW WARNINGS;
+---------+------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Level   | Code | Message                                                                                                                                                              |
+---------+------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Note    | 1105 | Analyze use auto adjusted sample rate 1.000000 for table test.t's partition p1, reason to use this rate is "TiDB assumes that the table is empty, use sample-rate=1" |
| Warning | 1105 | skip analyze locked table: test.t partition (p1)                                                                                                                     |
+---------+------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
2 rows in set (0.00 sec)
```

Unlock the statistics of partition `p1` and `ANALYZE` can be successfully executed again.
```sql
mysql> UNLOCK STATS t PARTITION p1;
Query OK, 0 rows affected (0.00 sec)

mysql> ANALYZE TABLE t PARTITION p1;
Query OK, 0 rows affected, 1 warning (0.01 sec)

mysql> SHOW WARNINGS;
+-------+------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Level | Code | Message                                                                                                                                                              |
+-------+------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Note  | 1105 | Analyze use auto adjusted sample rate 1.000000 for table test.t's partition p1, reason to use this rate is "TiDB assumes that the table is empty, use sample-rate=1" |
+-------+------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
### Behaviors of locking statistics

* If you lock the statistics on a partitioned table, the statistics of all partitions on the partitioned table are locked.
* If you truncate a table or partition, the statistics lock on the table or partition will be released.

The following table describes the behaviors of locking statistics:

| | Delete the whole table | Truncate the whole table | Truncate a partition | Create a new partition | Delete a partition | Reorganize a partition | Exchange a partition |
|----------------------------|------------|----------------------------------------------------------------|----------------------------------------------------------------|----------------|----------------------------------------------|----------------------------------------------|--------------------------|
| A non-partitioned table is locked | The lock is invalid | The lock is invalid because TiDB deletes the old table, so the lock information is also deleted | / | / | / | / | / |
| A partitioned table and the whole table is locked | The lock is invalid | The lock is invalid because TiDB deletes the old table, so the lock information is also deleted | The old partition lock information is invalid, and the new partition is automatically locked | The new partition is automatically locked | The lock information of the deleted partition is cleared, and the lock of the whole table continues to take effect | The lock information of the deleted partition is cleared, and the new partition is automatically locked | The lock information is transferred to the exchanged table, and the new partition is automatically locked |
| A partitioned table and only some partitions are locked | The lock is invalid | The lock is invalid because TiDB deletes the old table, so the lock information is also deleted | The lock is invalid because TiDB deletes the old table, so the lock information is also deleted | / | The deleted partition lock information is cleared | The deleted partition lock information is cleared | The lock information is transferred to the exchanged table |
