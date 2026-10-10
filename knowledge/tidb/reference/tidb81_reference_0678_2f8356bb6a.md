# SHOW STATS_META syntax, output columns, and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-stats-meta.md`
- Source Title: `SHOW STATS_META`
- Source Heading Path: `SHOW STATS_META | SHOW STATS_META > Synopsis | SHOW STATS_META > Examples | SHOW STATS_META > MySQL compatibility | SHOW STATS_META > See also`
- Source Line Ranges: `5-75`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `statistics`, `metadata`, `show-statements`, `syntax`, `filtering`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0678_2f8356bb6a`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-stats-meta.md#show-stats-meta`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9ee56f9e228ae36b1ae7260f2f28c36fdee4de148d7b28c9598604a4c4ad0b12`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-meta#show-stats-meta
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-stats-meta.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about the syntax, output columns, filtering, examples, or MySQL compatibility of `SHOW STATS_META` in TiDB.
- Retrieval Keywords: SHOW STATS_META, ShowStatsMetaStmt, ShowLikeOrWhere, LIKE SimpleExpr, WHERE Expression, db_name, table_name, partition_name, update_time, modify_count, row_count, SHOW STATS_META WHERE table_name = 't2', TiDB extension to MySQL syntax, statistics metadata
- Follow-up Guidance: This page also points to `ANALYZE` and `Introduction to Statistics` in the See also section.
- Classification Note: This is reference content because it defines the `SHOW STATS_META` statement, lists its output columns, shows syntax and examples, and notes that `update_time` reflects updates to `modify_count` and `row_count` from DML statements.

## Official Source Content

# SHOW STATS_META

You can use `SHOW STATS_META` to view how many rows are in a table and how many rows are changed in that table. When using this statement, you can filter the needed information by the `ShowLikeOrWhere` clause.

Currently, the `SHOW STATS_META` statement outputs 6 columns:

| Column name | Description            |
| -------- | ------------- |
| db_name  |  Database name    |
| table_name | Table name |
| partition_name| Partition name |
| update_time | Last updated time |
| modify_count | The number of rows modified |
| row_count | The total row count |

> **Note:**
>
> The `update_time` is updated when TiDB updates the `modify_count` and `row_count` fields according to DML statements. So `update_time` is not the last execution time of the `ANALYZE` statement.
## Synopsis

```ebnf+diagram
ShowStatsMetaStmt ::=
    "SHOW" "STATS_META" ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

```sql
SHOW STATS_META;
```

```sql
+---------+------------+----------------+---------------------+--------------+-----------+
| Db_name | Table_name | Partition_name | Update_time         | Modify_count | Row_count |
+---------+------------+----------------+---------------------+--------------+-----------+
| test    | t0         |                | 2020-05-15 16:58:00 |            0 |         0 |
| test    | t1         |                | 2020-05-15 16:58:04 |            0 |         0 |
| test    | t2         |                | 2020-05-15 16:58:11 |            0 |         0 |
| test    | s          |                | 2020-05-22 19:46:43 |            0 |         0 |
| test    | t          |                | 2020-05-25 12:04:21 |            0 |         0 |
+---------+------------+----------------+---------------------+--------------+-----------+
5 rows in set (0.00 sec)
```

```sql
SHOW STATS_META WHERE table_name = 't2';
```

```sql
+---------+------------+----------------+---------------------+--------------+-----------+
| Db_name | Table_name | Partition_name | Update_time         | Modify_count | Row_count |
+---------+------------+----------------+---------------------+--------------+-----------+
| test    | t2         |                | 2020-05-15 16:58:11 |            0 |         0 |
+---------+------------+----------------+---------------------+--------------+-----------+
1 row in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [ANALYZE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table)
* [Introduction to Statistics](https://docs.pingcap.com/tidb/stable/statistics)
