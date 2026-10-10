# INSPECTION_SUMMARY table structure and usage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-inspection-summary.md`
- Source Title: `INSPECTION_SUMMARY`
- Source Heading Path: `INSPECTION_SUMMARY`
- Source Line Ranges: `5-85`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `inspection_summary`, `inspection_rules`, `monitoring`, `summary`, `metrics`, `quantile`, `time_range`, `diagnostics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0392_d32cfad8d6`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-inspection-summary.md#inspection-summary`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9bad940b87bf709463d91bca5f1331318a48d5f08f437cf1e6ad824f3b6b3dd8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-inspection-summary#inspection-summary
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-inspection-summary.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about the structure, fields, predicates, time-range hints, or example queries for `information_schema.inspection_summary` monitoring summaries.
- Retrieval Keywords: information_schema.inspection_summary, INSPECTION_SUMMARY, DESC inspection_summary, inspection_rules where type='summary', RULE, INSTANCE, METRICS_NAME, LABEL, QUANTILE, AVG_VALUE, MIN_VALUE, MAX_VALUE, COMMENT, select * from inspection_summary where rule='ddl' and quantile in (0.80, 0.90, 0.99, 0.999), select * from inspection_summary where rule in ('read-link', 'ddl'), time_range('2020-03-07 12:00:00','2020-03-07 13:00:00'), read-link, DDL-related monitoring metrics, compare the data of two different periods
- Follow-up Guidance: The source also includes a join query that compares `inspection_summary` results for two different `time_range` periods on `metrics_name`, `instance`, and `label`, ordered by `ratio DESC`.
- Classification Note: This is reference content because it defines the `inspection_summary` table schema, explains each field, and shows grounded SQL usage examples for summary rules and time-range diagnostics.

## Official Source Content

# INSPECTION_SUMMARY

In some scenarios, you might need to pay attention only to the monitoring summary of specific links or modules. For example, the number of threads for Coprocessor in the thread pool is configured as 8. If the CPU usage of Coprocessor reaches 750%, you can determine that a risk exists and Coprocessor might become a bottleneck in advance. However, some monitoring metrics vary greatly due to different user workloads, so it is difficult to define specific thresholds. It is important to troubleshoot issues in this scenario, so TiDB provides the `inspection_summary` table for link summary.

> **Note:**
>
> This table is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).

The structure of the `information_schema.inspection_summary` inspection summary table is as follows:

```sql
USE information_schema;
DESC inspection_summary;
```

```sql
+--------------+--------------+------+------+---------+-------+
| Field        | Type         | Null | Key  | Default | Extra |
+--------------+--------------+------+------+---------+-------+
| RULE         | varchar(64)  | YES  |      | NULL    |       |
| INSTANCE     | varchar(64)  | YES  |      | NULL    |       |
| METRICS_NAME | varchar(64)  | YES  |      | NULL    |       |
| LABEL        | varchar(64)  | YES  |      | NULL    |       |
| QUANTILE     | double       | YES  |      | NULL    |       |
| AVG_VALUE    | double(22,6) | YES  |      | NULL    |       |
| MIN_VALUE    | double(22,6) | YES  |      | NULL    |       |
| MAX_VALUE    | double(22,6) | YES  |      | NULL    |       |
| COMMENT      | varchar(256) | YES  |      | NULL    |       |
+--------------+--------------+------+------+---------+-------+
9 rows in set (0.00 sec)
```

Field description:

* `RULE`: Summary rules. Because new rules are being added continuously, you can execute the `select * from inspection_rules where type='summary'` statement to query the latest rule list.
* `INSTANCE`: The monitored instance.
* `METRICS_NAME`: The monitoring metrics name.
* `QUANTILE`: Takes effect on monitoring tables that contain `QUANTILE`. You can specify multiple percentiles by pushing down predicates. For example, you can execute `select * from inspection_summary where rule='ddl' and quantile in (0.80, 0.90, 0.99, 0.999)` to summarize the DDL-related monitoring metrics and query the P80/P90/P99/P999 results. `AVG_VALUE`, `MIN_VALUE`, and `MAX_VALUE` respectively indicate the average value, minimum value, and maximum value of the aggregation.
* `COMMENT`: The comment about the corresponding monitoring metric.

> **Note:**
>
> Because summarizing all results causes overhead, it is recommended to display the specific `rule` in the SQL predicate to reduce overhead. For example, executing `select * from inspection_summary where rule in ('read-link', 'ddl')` summarizes the read link and DDL-related monitoring metrics.

Usage example:

Both the diagnostic result table and the diagnostic monitoring summary table can specify the diagnostic time range using `hint`. `select /*+ time_range('2020-03-07 12:00:00','2020-03-07 13:00:00') */* from inspection_summary` is the monitoring summary for the `2020-03-07 12:00:00` to `2020-03-07 13:00:00` period. Like the monitoring summary table, you can use the `inspection_summary` table to quickly find the monitoring items with large differences by comparing the data of two different periods.

The following example compares the monitoring metrics of read links in two time periods:

* `(2020-01-16 16:00:54.933, 2020-01-16 16:10:54.933)`
* `(2020-01-16 16:10:54.933, 2020-01-16 16:20:54.933)`

```sql
SELECT
  t1.avg_value / t2.avg_value AS ratio,
  t1.*,
  t2.*
FROM
  (
    SELECT
      /*+ time_range("2020-01-16 16:00:54.933", "2020-01-16 16:10:54.933")*/ *
    FROM information_schema.inspection_summary WHERE rule='read-link'
  ) t1
  JOIN
  (
    SELECT
      /*+ time_range("2020-01-16 16:10:54.933", "2020-01-16 16:20:54.933")*/ *
    FROM information_schema.inspection_summary WHERE rule='read-link'
  ) t2
  ON t1.metrics_name = t2.metrics_name
  and t1.instance = t2.instance
  and t1.label = t2.label
ORDER BY
  ratio DESC;
```
