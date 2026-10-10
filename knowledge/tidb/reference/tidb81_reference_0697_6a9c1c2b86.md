# UNLOCK STATS syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-unlock-stats.md`
- Source Title: `UNLOCK STATS`
- Source Heading Path: `UNLOCK STATS | UNLOCK STATS > Synopsis | UNLOCK STATS > Examples | UNLOCK STATS > MySQL compatibility | UNLOCK STATS > See also`
- Source Line Ranges: `5-76`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `statistics`, `unlock-stats`, `analyze-table`, `partitions`, `mysql-compatibility`, `syntax`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0697_6a9c1c2b86`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-unlock-stats.md#unlock-stats`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6c07bf8c4dde65c2bec3110ac6f4b3da469f6443e3d7f441867e024db04070ff`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-unlock-stats#unlock-stats
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-unlock-stats.md

## Retrieval Guidance

- Use When: Use this content when looking for the UNLOCK STATS statement syntax, partition form, examples showing ANALYZE TABLE succeeding after unlock, or the MySQL compatibility note.
- Retrieval Keywords: UNLOCK STATS, UnlockStatsStmt, UNLOCK STATS t, UNLOCK STATS t PARTITION p1, TableNameList, PartitionNameList, ANALYZE TABLE t, ANALYZE TABLE t PARTITION p1, SHOW WARNINGS, SHOW STATS_LOCKED, LOCK STATS, statistics, partition p1, TiDB extension to MySQL syntax
- Follow-up Guidance: See also Statistics, LOCK STATS, and SHOW STATS_LOCKED.
- Classification Note: This is reference content because it defines the UNLOCK STATS syntax, gives table and partition examples, and states that it is a TiDB extension to MySQL syntax.

## Official Source Content

# UNLOCK STATS

`UNLOCK STATS` is used to unlock the statistics of a table or tables.
## Synopsis

```ebnf+diagram
UnlockStatsStmt ::=
    'UNLOCK' 'STATS' (TableNameList | TableName 'PARTITION' PartitionNameList)

TableNameList ::=
    TableName (',' TableName)*

TableName ::=
    Identifier ( '.' Identifier )?

PartitionNameList ::=
    Identifier ( ',' Identifier )*
```
## Examples

Refer to the examples in [LOCK STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-stats) and create a table `t` and lock its statistics.

Unlock the statistics of table `t`, and `ANALYZE` can be successfully executed.

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

Refer to examples in [LOCK STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-stats) and create a table `t` and lock the statistics of its partition `p1`.

Unlock the statistics of partition `p1`, and `ANALYZE` can be successfully executed.

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
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [Statistics](https://docs.pingcap.com/tidb/stable/statistics#lock-statistics)
* [LOCK STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-stats)
* [SHOW STATS_LOCKED](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-locked)
