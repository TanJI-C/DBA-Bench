# FLASHBACK CLUSTER examples and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-flashback-cluster.md`
- Source Title: `FLASHBACK CLUSTER`
- Source Heading Path: `FLASHBACK CLUSTER > Example | FLASHBACK CLUSTER > MySQL compatibility`
- Source Line Ranges: `80-189`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `examples`, `timestamp`, `tso`, `ddl-conflict`, `progress-log`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0594_a48a37c3cf`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-flashback-cluster.md#example`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ebe24d20da18557148d704790335f78b67849768045c56c6f8ed026fffb06f38`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster#example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-flashback-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when you need examples, an error case for overlapping DDL, or the MySQL compatibility note for `FLASHBACK CLUSTER`.
- Retrieval Keywords: FLASHBACK CLUSTER examples, FLASHBACK CLUSTER TO TIMESTAMP '2022-09-28 17:24:16', FLASHBACK CLUSTER TO TSO 446113975683252225, ADMIN SHOW DDL JOBS 1, Detected another DDL job, flashback cluster stats, complete regions, total regions, This statement is a TiDB extension to MySQL syntax
- Follow-up Guidance: Review the example output and log line format if you need to confirm flashback progress or a DDL-conflict failure.
- Classification Note: This chunk is an examples and compatibility reference because it shows timestamp and TSO usage, a DDL conflict error, progress logging, and the MySQL compatibility statement.

## Official Source Content

## Example

The following example shows how to flashback a cluster to a specific timestamp to restore newly inserted data:

```sql
mysql> CREATE TABLE t(a INT);
Query OK, 0 rows affected (0.09 sec)

mysql> SELECT * FROM t;
Empty set (0.01 sec)

mysql> SELECT now();
+---------------------+
| now()               |
+---------------------+
| 2022-09-28 17:24:16 |
+---------------------+
1 row in set (0.02 sec)

mysql> INSERT INTO t VALUES (1);
Query OK, 1 row affected (0.02 sec)

mysql> SELECT * FROM t;
+------+
| a    |
+------+
|    1 |
+------+
1 row in set (0.01 sec)

mysql> FLASHBACK CLUSTER TO TIMESTAMP '2022-09-28 17:24:16';
Query OK, 0 rows affected (0.20 sec)

mysql> SELECT * FROM t;
Empty set (0.00 sec)
```

The following example shows how to flashback a cluster to a specific TSO to precisely restore mistakenly deleted data:

```sql
mysql> INSERT INTO t VALUES (1);
Query OK, 1 row affected (0.02 sec)

mysql> SELECT * FROM t;
+------+
| a    |
+------+
|    1 |
+------+
1 row in set (0.01 sec)


mysql> BEGIN;
Query OK, 0 rows affected (0.00 sec)

mysql> SELECT @@tidb_current_ts;  -- Get the current TSO
+--------------------+
| @@tidb_current_ts  |
+--------------------+
| 446113975683252225 |
+--------------------+
1 row in set (0.00 sec)

mysql> ROLLBACK;
Query OK, 0 rows affected (0.00 sec)


mysql> DELETE FROM t;
Query OK, 1 rows affected (0.00 sec)


mysql> FLASHBACK CLUSTER TO TSO 446113975683252225;
Query OK, 0 rows affected (0.20 sec)

mysql> SELECT * FROM t;
+------+
| a    |
+------+
|    1 |
+------+
1 row in set (0.01 sec)
```

If there is a DDL statement that is not completely executed at the time specified in the `FLASHBACK` statement, the `FLASHBACK` statement fails:

```sql
mysql> ALTER TABLE t ADD INDEX k(a);
Query OK, 0 rows affected (0.56 sec)

mysql> ADMIN SHOW DDL JOBS 1;
+--------+---------+-----------------------+------------------------+--------------+-----------+----------+-----------+---------------------+---------------------+---------------------+--------+
| JOB_ID | DB_NAME | TABLE_NAME            | JOB_TYPE               | SCHEMA_STATE | SCHEMA_ID | TABLE_ID | ROW_COUNT | CREATE_TIME         | START_TIME          | END_TIME            | STATE  |
+--------+---------+-----------------------+------------------------+--------------+-----------+----------+-----------+---------------------+---------------------+---------------------+--------+
|     84 | test    | t                     | add index /* ingest */ | public       |         2 |       82 |         0 | 2023-01-29 14:33:11 | 2023-01-29 14:33:11 | 2023-01-29 14:33:12 | synced |
+--------+---------+-----------------------+------------------------+--------------+-----------+----------+-----------+---------------------+---------------------+---------------------+--------+
1 rows in set (0.01 sec)

mysql> FLASHBACK CLUSTER TO TIMESTAMP '2023-01-29 14:33:12';
ERROR 1105 (HY000): Detected another DDL job at 2023-01-29 14:33:12 +0800 CST, can't do flashback
```

Through the log, you can obtain the execution progress of `FLASHBACK`. The following is an example:

```
[2022/10/09 17:25:59.316 +08:00] [INFO] [cluster.go:463] ["flashback cluster stats"] ["complete regions"=9] ["total regions"=10] []
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
