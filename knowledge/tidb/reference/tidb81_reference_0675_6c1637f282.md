# SHOW STATS_HEALTHY syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-stats-healthy.md`
- Source Title: `SHOW STATS_HEALTHY`
- Source Heading Path: `SHOW STATS_HEALTHY | SHOW STATS_HEALTHY > Synopsis | SHOW STATS_HEALTHY > Examples | SHOW STATS_HEALTHY > MySQL compatibility | SHOW STATS_HEALTHY > See also`
- Source Line Ranges: `5-91`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `statistics`, `health`, `analyze`, `syntax`, `mysql-compatibility`, `examples`, `query-plans`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0675_6c1637f282`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-stats-healthy.md#show-stats-healthy`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c6b7f2a3478f9f5e4ff8c83717a1525d011cda923511e4888f2e000eea1ebfa0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-healthy#show-stats-healthy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-stats-healthy.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the `SHOW STATS_HEALTHY` statement syntax, output columns, examples of health percentages after `ANALYZE` or deletes, or its MySQL compatibility status.
- Retrieval Keywords: SHOW STATS_HEALTHY, ShowStatsHealthyStmt, SHOW STATS_HEALTHY LIKE, SHOW STATS_HEALTHY WHERE, Db_name, Table_name, Partition_name, Healthy, ANALYZE TABLE, tidb_auto_analyze_ratio, statistics health, healthy percentage between 0 and 100, TiDB extension to MySQL syntax
- Follow-up Guidance: The source also points to `ANALYZE` and Introduction to Statistics, and states that `ANALYZE` runs automatically when health drops below `tidb_auto_analyze_ratio`.
- Classification Note: This is reference content because it defines `SHOW STATS_HEALTHY` syntax, result columns, examples, and MySQL compatibility for the SQL statement.

## Official Source Content

# SHOW STATS_HEALTHY

The `SHOW STATS_HEALTHY` statement shows an estimation of how accurate statistics are believed to be. Tables with a low percentage health may generate sub-optimal query execution plans.

The health of a table can be improved by running the [`ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) statement. `ANALYZE` runs automatically when the health drops below the [`tidb_auto_analyze_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_auto_analyze_ratio) threshold.

Currently, the `SHOW STATS_HEALTHY` statement returns the following columns:

| Column name | Description            |
| -------- | ------------- |
| `Db_name` | The database name |
| `Table_name` | The table name |
| `Partition_name` | The partition name |
| `Healthy` | The healthy percentage between 0 and 100 |
## Synopsis

```ebnf+diagram
ShowStatsHealthyStmt ::=
    "SHOW" "STATS_HEALTHY" ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

Load example data and run `ANALYZE`:

```sql
CREATE TABLE t1 (
 id INT NOT NULL PRIMARY KEY auto_increment,
 b INT NOT NULL,
 pad VARBINARY(255),
 INDEX(b)
);

INSERT INTO t1 SELECT NULL, FLOOR(RAND()*1000), RANDOM_BYTES(255) FROM dual;
INSERT INTO t1 SELECT NULL, FLOOR(RAND()*1000), RANDOM_BYTES(255) FROM t1 a JOIN t1 b JOIN t1 c LIMIT 100000;
INSERT INTO t1 SELECT NULL, FLOOR(RAND()*1000), RANDOM_BYTES(255) FROM t1 a JOIN t1 b JOIN t1 c LIMIT 100000;
INSERT INTO t1 SELECT NULL, FLOOR(RAND()*1000), RANDOM_BYTES(255) FROM t1 a JOIN t1 b JOIN t1 c LIMIT 100000;
INSERT INTO t1 SELECT NULL, FLOOR(RAND()*1000), RANDOM_BYTES(255) FROM t1 a JOIN t1 b JOIN t1 c LIMIT 100000;
INSERT INTO t1 SELECT NULL, FLOOR(RAND()*1000), RANDOM_BYTES(255) FROM t1 a JOIN t1 b JOIN t1 c LIMIT 100000;
INSERT INTO t1 SELECT NULL, FLOOR(RAND()*1000), RANDOM_BYTES(255) FROM t1 a JOIN t1 b JOIN t1 c LIMIT 100000;
SELECT SLEEP(1);
ANALYZE TABLE t1;
SHOW STATS_HEALTHY; # should be 100% healthy
```

```sql
...
mysql> SHOW STATS_HEALTHY;
+---------+------------+----------------+---------+
| Db_name | Table_name | Partition_name | Healthy |
+---------+------------+----------------+---------+
| test    | t1         |                |     100 |
+---------+------------+----------------+---------+
1 row in set (0.00 sec)
```

Perform a bulk update deleting approximately 30% of the records. Check the health of the statistics:

```sql
DELETE FROM t1 WHERE id BETWEEN 101010 AND 201010; # delete about 30% of records
SHOW STATS_HEALTHY; 
```

```sql
mysql> SHOW STATS_HEALTHY;
+---------+------------+----------------+---------+
| Db_name | Table_name | Partition_name | Healthy |
+---------+------------+----------------+---------+
| test    | t1         |                |      50 |
+---------+------------+----------------+---------+
1 row in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [ANALYZE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table)
* [Introduction to Statistics](https://docs.pingcap.com/tidb/stable/statistics)
