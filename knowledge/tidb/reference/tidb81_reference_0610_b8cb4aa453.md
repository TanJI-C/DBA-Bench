# LOCK STATS examples, compatibility, and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-lock-stats.md`
- Source Title: `LOCK STATS`
- Source Heading Path: `LOCK STATS > Examples | LOCK STATS > MySQL compatibility | LOCK STATS > See also`
- Source Line Ranges: `81-143`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `pd`
- Topic Tags: `statistics`, `lock-stats`, `analyze-table`, `partitioned-table`, `show-warnings`, `show-stats-locked`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0610_b8cb4aa453`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-lock-stats.md#examples`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `42dd8db4474e61d23d7ffd695e557df96d57663c6140f16de15f525be258fa09`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-stats#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-lock-stats.md

## Retrieval Guidance

- Use When: Use this chunk when looking for a LOCK STATS example on a partitioned table, the SHOW STATS_LOCKED output after locking a partition, or the warning shown when ANALYZE TABLE skips locked statistics.
- Retrieval Keywords: LOCK STATS t PARTITION p1, ANALYZE TABLE t PARTITION p1, SHOW STATS_LOCKED, SHOW WARNINGS, skip analyze locked table: test.t partition (p1), partitioned table, locked statistics, UNLOCK STATS, TiDB extension to MySQL syntax
- Follow-up Guidance: For unlock statistics, see UNLOCK STATS; related statements also include SHOW STATS_LOCKED and the Statistics lock statistics documentation.
- Classification Note: This is reference content because it provides SQL examples, warning outputs, MySQL compatibility, and related statements for LOCK STATS.

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

For information on unlock statistics, see [UNLOCK STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-unlock-stats).
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [Statistics](https://docs.pingcap.com/tidb/stable/statistics#lock-statistics)
* [UNLOCK STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-unlock-stats)
* [SHOW STATS_LOCKED](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-locked)
