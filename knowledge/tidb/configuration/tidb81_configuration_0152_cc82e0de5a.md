# Persist ANALYZE options and column settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > Persist ANALYZE configurations | Introduction to Statistics > Persist ANALYZE configurations > Enable ANALYZE configuration persistence | Introduction to Statistics > Persist ANALYZE configurations > Disable ANALYZE configuration persistence | Introduction to Statistics > Persist ANALYZE configurations > Persist column configurations`
- Source Line Ranges: `270-367`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `analyze`, `persistence`, `system-variables`, `column-statistics`, `auto-analyze`, `topn`, `sampling`, `histogram-buckets`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0152_cc82e0de5a`
- Source ID: `tidb-docs-8.1:statistics.md#persist-analyze-configurations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `742b6504e9d6d62d99e4cbbcd5bdfd647bada64e82a0f97bd7460c942fafd60d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#persist-analyze-configurations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when asking which `ANALYZE` options can be persisted, how `tidb_persist_analyze_options` and `tidb_analyze_version` affect persistence, or how to inspect persisted analyze options and persisted column settings.
- Retrieval Keywords: Persist ANALYZE configurations, tidb_persist_analyze_options, tidb_analyze_version, WITH NUM BUCKETS, WITH NUM TOPN, WITH NUM SAMPLES, WITH FLOATNUM SAMPLERATE, PREDICATE COLUMNS, ALL COLUMNS, COLUMNS ColumnNameList, mysql.analyze_options, SELECT sample_num, sample_rate, buckets, topn, column_choice, column_ids, SHOW COLUMN_STATS_USAGE, tidb_enable_column_tracking
- Follow-up Guidance: The content includes a query against `mysql.analyze_options` joined with `information_schema.tables` and shows using `SHOW COLUMN_STATS_USAGE` to locate `PREDICATE COLUMNS` and columns whose statistics have been collected.
- Classification Note: This is classified as configuration because it centers on persisted `ANALYZE` settings, related system variables, and persisted column configuration behavior.

## Official Source Content

## Persist ANALYZE configurations

Since v5.4.0, TiDB supports persisting some `ANALYZE` configurations. With this feature, the existing configurations can be easily reused for future statistics collection.

The following are the `ANALYZE` configurations that support persistence:

| Configurations | Corresponding ANALYZE syntax |
| --- | --- |
| The number of histogram buckets | `WITH NUM BUCKETS` |
| The number of Top-N  | `WITH NUM TOPN` |
| The number of samples | `WITH NUM SAMPLES` |
| The sampling rate | `WITH FLOATNUM SAMPLERATE` |
| The `ANALYZE` column type | AnalyzeColumnOption ::= ( 'ALL COLUMNS' \| 'PREDICATE COLUMNS' \| 'COLUMNS' ColumnNameList ) |
| The `ANALYZE` column | ColumnNameList ::= Identifier ( ',' Identifier )* |
### Enable ANALYZE configuration persistence

The `ANALYZE` configuration persistence feature is enabled by default (the system variable `tidb_analyze_version` is `2` and `tidb_persist_analyze_options` is `ON` by default).

The `ANALYZE` configuration persistence feature is disabled by default. To enable the feature, ensure that the system variable `tidb_persist_analyze_options` is `ON` and set the system variable `tidb_analyze_version` to `2`.

You can use this feature to record the persistence configurations specified in the `ANALYZE` statement when executing the statement manually. Once recorded, the next time TiDB automatically updates statistics or you manually collect statistics without specifying these configuration, TiDB will collect statistics according to the recorded configurations.

To query the configuration persisted on a specific table used for auto analyze operations, you can use the following SQL statement:

```sql
SELECT sample_num, sample_rate, buckets, topn, column_choice, column_ids FROM mysql.analyze_options opt JOIN information_schema.tables tbl ON opt.table_id = tbl.tidb_table_id WHERE tbl.table_schema = '{db_name}' AND tbl.table_name = '{table_name}';
```

TiDB will overwrite the previously recorded persistent configuration using the new configurations specified by the latest `ANALYZE` statement. For example, if you run `ANALYZE TABLE t WITH 200 TOPN;`, it will set the top 200 values in the `ANALYZE` statement. Subsequently, executing `ANALYZE TABLE t WITH 0.1 SAMPLERATE;` will set both the top 200 values and a sampling rate of 0.1 for auto `ANALYZE` statements, similar to `ANALYZE TABLE t WITH 200 TOPN, 0.1 SAMPLERATE;`.
### Disable ANALYZE configuration persistence

To disable the `ANALYZE` configuration persistence feature, set the `tidb_persist_analyze_options` system variable to `OFF`. Because the `ANALYZE` configuration persistence feature is not applicable to `tidb_analyze_version = 1`, setting `tidb_analyze_version = 1` can also disable the feature.

After disabling the `ANALYZE` configuration persistence feature, TiDB does not clear the persisted configuration records. Therefore, if you enable this feature again, TiDB continues to collect statistics using the previously recorded persistent configurations.

> **Note:**
>
> When you enable the `ANALYZE` configuration persistence feature again, if the previously recorded persistence configurations are no longer applicable to the latest data, you need to execute the `ANALYZE` statement manually and specify the new persistence configurations.
### Persist column configurations

If you want to persist the column configuration in the `ANALYZE` statement (including `COLUMNS ColumnNameList`, `PREDICATE COLUMNS`, and `ALL COLUMNS`), set the value of the `tidb_persist_analyze_options` system variable to `ON` to enable the [ANALYZE configuration persistence](#persist-analyze-configurations) feature. After enabling the ANALYZE configuration persistence feature:

- When TiDB collects statistics automatically or when you manually collect statistics by executing the `ANALYZE` statement without specifying the column configuration, TiDB continues using the previously persisted configuration for statistics collection.
- When you manually execute the `ANALYZE` statement multiple times with column configuration specified, TiDB overwrites the previously recorded persistent configuration using the new configuration specified by the latest `ANALYZE` statement.

To locate `PREDICATE COLUMNS` and columns on which statistics have been collected, use the [`SHOW COLUMN_STATS_USAGE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-column-stats-usage) statement.

In the following example, after executing `ANALYZE TABLE t PREDICATE COLUMNS;`, TiDB collects statistics on columns `b`, `c`, and `d`, where column `b` is a `PREDICATE COLUMN` and columns `c` and `d` are index columns.

```sql
SET GLOBAL tidb_enable_column_tracking = ON;
Query OK, 0 rows affected (0.00 sec)

CREATE TABLE t (a INT, b INT, c INT, d INT, INDEX idx_c_d(c, d));
Query OK, 0 rows affected (0.00 sec)

-- The optimizer uses the statistics on column b in this query.
SELECT * FROM t WHERE b > 1;
Empty set (0.00 sec)

-- After waiting for a period of time (100 * stats-lease), TiDB writes the collected `PREDICATE COLUMNS` to mysql.column_stats_usage.
-- Specify `last_used_at IS NOT NULL` to show the `PREDICATE COLUMNS` collected by TiDB.
SHOW COLUMN_STATS_USAGE
WHERE db_name = 'test' AND table_name = 't' AND last_used_at IS NOT NULL;
+---------+------------+----------------+-------------+---------------------+------------------+
| Db_name | Table_name | Partition_name | Column_name | Last_used_at        | Last_analyzed_at |
+---------+------------+----------------+-------------+---------------------+------------------+
| test    | t          |                | b           | 2022-01-05 17:21:33 | NULL             |
+---------+------------+----------------+-------------+---------------------+------------------+
1 row in set (0.00 sec)

ANALYZE TABLE t PREDICATE COLUMNS;
Query OK, 0 rows affected, 1 warning (0.03 sec)

-- Specify `last_analyzed_at IS NOT NULL` to show the columns for which statistics have been collected.
SHOW COLUMN_STATS_USAGE
WHERE db_name = 'test' AND table_name = 't' AND last_analyzed_at IS NOT NULL;
+---------+------------+----------------+-------------+---------------------+---------------------+
| Db_name | Table_name | Partition_name | Column_name | Last_used_at        | Last_analyzed_at    |
+---------+------------+----------------+-------------+---------------------+---------------------+
| test    | t          |                | b           | 2022-01-05 17:21:33 | 2022-01-05 17:23:06 |
| test    | t          |                | c           | NULL                | 2022-01-05 17:23:06 |
| test    | t          |                | d           | NULL                | 2022-01-05 17:23:06 |
+---------+------------+----------------+-------------+---------------------+---------------------+
3 rows in set (0.00 sec)
```
