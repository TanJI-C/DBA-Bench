# SHOW COLUMN_STATS_USAGE syntax, output, and example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-column-stats-usage.md`
- Source Title: `SHOW COLUMN_STATS_USAGE`
- Source Heading Path: `SHOW COLUMN_STATS_USAGE | SHOW COLUMN_STATS_USAGE > Synopsis | SHOW COLUMN_STATS_USAGE > Examples | SHOW COLUMN_STATS_USAGE > MySQL compatibility | SHOW COLUMN_STATS_USAGE > See also`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show statement`, `column statistics`, `statistics usage`, `syntax`, `examples`, `mysql compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0647_4a4ed1db85`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-column-stats-usage.md#show-column-stats-usage`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a58290186d2037890ffd9c4c6bba6a20349804fb2794405abc975c680ada5245`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-column-stats-usage#show-column-stats-usage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-column-stats-usage.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax, output columns, or example result of `SHOW COLUMN_STATS_USAGE`, including how to view the last usage time and collection time of column statistics or locate `PREDICATE COLUMNS` and columns with collected statistics.
- Retrieval Keywords: SHOW COLUMN_STATS_USAGE, ShowColumnStatsUsageStmt, SHOW COLUMN_STATS_USAGE LIKE, SHOW COLUMN_STATS_USAGE WHERE, Db_name, Table_name, Partition_name, Column_name, Last_used_at, Last_analyzed_at, last usage time of column statistics, collection time of column statistics, PREDICATE COLUMNS, TiDB extension to MySQL syntax
- Follow-up Guidance: The source also points to `ANALYZE` and Introduction to Statistics in the See also section.
- Classification Note: This is reference content because it defines the `SHOW COLUMN_STATS_USAGE` statement, its syntax, returned columns, example output, and MySQL compatibility note.

## Official Source Content

# SHOW COLUMN_STATS_USAGE

The `SHOW COLUMN_STATS_USAGE` statement shows the last usage time and collection time of column statistics. You can also use it to locate `PREDICATE COLUMNS` and columns on which statistics have been collected.

Currently, the `SHOW COLUMN_STATS_USAGE` statement returns the following columns:

| Column name | Description            |
| -------- | ------------- |
| `Db_name`  |  The database name    |
| `Table_name` | The table name |
| `Partition_name` | The partition name |
| `Column_name` | The column name |
| `Last_used_at` | The last time when the column statistics were used in the query optimization |
| `Last_analyzed_at` | The last time when the column statistics were collected |
## Synopsis

```ebnf+diagram
ShowColumnStatsUsageStmt ::=
    "SHOW" "COLUMN_STATS_USAGE" ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

```sql
SHOW COLUMN_STATS_USAGE;
```

```
+---------+------------+----------------+-------------+--------------+---------------------+
| Db_name | Table_name | Partition_name | Column_name | Last_used_at | Last_analyzed_at    |
+---------+------------+----------------+-------------+--------------+---------------------+
| test    | t1         |                | id          | NULL         | 2024-05-10 11:04:23 |
| test    | t1         |                | b           | NULL         | 2024-05-10 11:04:23 |
| test    | t1         |                | pad         | NULL         | 2024-05-10 11:04:23 |
| test    | t          |                | a           | NULL         | 2024-05-10 11:37:06 |
| test    | t          |                | b           | NULL         | 2024-05-10 11:37:06 |
+---------+------------+----------------+-------------+--------------+---------------------+
5 rows in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [`ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table)
* [Introduction to Statistics](https://docs.pingcap.com/tidb/stable/statistics)
