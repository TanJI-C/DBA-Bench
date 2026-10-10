# SHOW STATS_BUCKETS syntax and output columns

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-stats-buckets.md`
- Source Title: `SHOW STATS_BUCKETS`
- Source Heading Path: `SHOW STATS_BUCKETS | SHOW STATS_BUCKETS > Synopsis | SHOW STATS_BUCKETS > Examples | SHOW STATS_BUCKETS > MySQL compatibility | SHOW STATS_BUCKETS > See also`
- Source Line Ranges: `5-64`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `statistics`, `histogram`, `buckets`, `show`, `syntax`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0674_e27723f093`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-stats-buckets.md#show-stats-buckets`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `04e1ca6910eca9a8dd4fb28b1301494c6b211814195da24a6cf056dc5e326ae1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-buckets#show-stats-buckets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-stats-buckets.md

## Retrieval Guidance

- Use When: Use this when looking up the syntax, example filtering, or output columns of the TiDB `SHOW STATS_BUCKETS` statement for histogram bucket information in statistics.
- Retrieval Keywords: SHOW STATS_BUCKETS, ShowStatsBucketsStmt, SHOW STATS_BUCKETS WHERE Table_name='t', ShowLikeOrWhere, Db_name, Table_name, Partition_name, Column_name, Is_index, Bucket_id, Count, Repeats, Lower_bound, Upper_bound, Ndv, statistics, bucket information, TiDB extension to MySQL syntax
- Follow-up Guidance: See also `ANALYZE` and Introduction to Statistics.
- Classification Note: This is reference content because it defines `SHOW STATS_BUCKETS` syntax, lists returned columns and meanings, gives a query example, and notes MySQL compatibility.

## Official Source Content

# SHOW STATS_BUCKETS

The `SHOW STATS_BUCKETS` statement shows the bucket information in [statistics](https://docs.pingcap.com/tidb/stable/statistics).

Currently, the `SHOW STATS_BUCKETS` statement returns the following columns:

| Column name | Description   |
| :-------- | :------------- |
| `Db_name`  |  The database name    |
| `Table_name` | The table name |
| `Partition_name` | The partition name |
| `Column_name` | The column name (when `is_index` is `0`) or the index name (when `is_index` is `1`) |
| `Is_index` | Whether it is an index column or not |
| `Bucket_id` | The ID of a bucket |
| `Count` | The number of all the values that falls on the bucket and the previous buckets |
| `Repeats` | The occurrence number of the maximum value |
| `Lower_bound` | The minimum value |
| `Upper_bound` | The maximum value |
| `Ndv` | The number of distinct values in the bucket. This field is deprecated and always shows `0` due to its inaccurate value. |
## Synopsis

```ebnf+diagram
ShowStatsBucketsStmt ::=
    "SHOW" "STATS_BUCKETS" ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

```sql
SHOW STATS_BUCKETS WHERE Table_name='t';
```

```
+---------+------------+----------------+-------------+----------+-----------+-------+---------+--------------------------+--------------------------+------+
| Db_name | Table_name | Partition_name | Column_name | Is_index | Bucket_id | Count | Repeats | Lower_Bound              | Upper_Bound              | Ndv  |
+---------+------------+----------------+-------------+----------+-----------+-------+---------+--------------------------+--------------------------+------+
| test    | t          |                | a           |        0 |         0 |     1 |       1 | 2023-12-27 00:00:00      | 2023-12-27 00:00:00      |    0 |
| test    | t          |                | a           |        0 |         1 |     2 |       1 | 2023-12-28 00:00:00      | 2023-12-28 00:00:00      |    0 |
| test    | t          |                | ia          |        1 |         0 |     1 |       1 | (NULL, 2)                | (NULL, 2)                |    0 |
| test    | t          |                | ia          |        1 |         1 |     2 |       1 | (NULL, 4)                | (NULL, 4)                |    0 |
| test    | t          |                | ia          |        1 |         2 |     3 |       1 | (2023-12-27 00:00:00, 1) | (2023-12-27 00:00:00, 1) |    0 |
| test    | t          |                | ia          |        1 |         3 |     4 |       1 | (2023-12-28 00:00:00, 3) | (2023-12-28 00:00:00, 3) |    0 |
+---------+------------+----------------+-------------+----------+-----------+-------+---------+--------------------------+--------------------------+------+
6 rows in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [`ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table)
* [Introduction to Statistics](https://docs.pingcap.com/tidb/stable/statistics)
