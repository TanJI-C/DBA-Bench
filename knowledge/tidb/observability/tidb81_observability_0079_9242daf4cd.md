# Statement summary tables overview and variants

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statement-summary-tables.md`
- Source Title: `Statement Summary Tables`
- Source Heading Path: `Statement Summary Tables | Statement Summary Tables > `statements_summary` | Statement Summary Tables > `statements_summary_history` | Statement Summary Tables > `statements_summary_evicted` | Statement Summary Tables > The `cluster` tables for statement summary`
- Source Line Ranges: `5-128`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `cloud`, `sql`
- Topic Tags: `statement summary`, `sql monitoring`, `digest`, `plan digest`, `history`, `eviction`, `cluster tables`, `resource group`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0079_9242daf4cd`
- Source ID: `tidb-docs-8.1:statement-summary-tables.md#statement-summary-tables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1b13a6c6e0e8eda04e6b52bb55844f0b3874413fa97fc0b3bcf0e959f6e716ea`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statement-summary-tables#statement-summary-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statement-summary-tables.md

## Retrieval Guidance

- Use When: Use this content when you need TiDB statement summary table names, what each table stores, how SQL is grouped by digest and plan digest, or how to view single-server versus cluster-wide SQL monitoring statistics.
- Retrieval Keywords: statements_summary, statements_summary_history, statements_summary_evicted, cluster_statements_summary, cluster_statements_summary_history, cluster_statements_summary_evicted, information_schema, SQL digest, plan digest, DIGEST_TEXT, PLAN_DIGEST, QUERY_SAMPLE_TEXT, SUMMARY_BEGIN_TIME, SUMMARY_END_TIME, tidb_stmt_summary_refresh_interval, tidb_stmt_summary_max_stmt_count, tidb_stmt_summary_enable_persistent, evicted statements Others row, resource group aggregation, INSTANCE field
- Follow-up Guidance: If you need cluster-wide data instead of a single TiDB server, query the corresponding `cluster_statements_summary`, `cluster_statements_summary_history`, or `cluster_statements_summary_evicted` table, where `INSTANCE` identifies the TiDB server address.
- Classification Note: This is observability content because it describes `information_schema` statement summary tables and related fields used to monitor SQL performance, history, and evictions in TiDB.

## Official Source Content

# Statement Summary Tables

To better handle SQL performance issues, MySQL has provided [statement summary tables](https://dev.mysql.com/doc/refman/8.0/en/performance-schema-statement-summary-tables.html) in `performance_schema` to monitor SQL with statistics. Among these tables, `events_statements_summary_by_digest` is very useful in locating SQL problems with its abundant fields such as latency, execution times, rows scanned, and full table scans.

Therefore, starting from v4.0.0-rc.1, TiDB provides system tables in `information_schema` (_not_ `performance_schema`) that are similar to `events_statements_summary_by_digest` in terms of features.

- [`statements_summary`](#statements_summary)
- [`statements_summary_history`](#statements_summary_history)
- [`cluster_statements_summary`](#statements_summary_evicted)
- [`cluster_statements_summary_history`](#statements_summary_evicted)
- [`statements_summary_evicted`](#statements_summary_evicted)

> **Note:**
>
> The preceding tables are not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

This document details these tables and introduces how to use them to troubleshoot SQL performance issues.
## `statements_summary`

`statements_summary` is a system table in `information_schema`. `statements_summary` groups the SQL statements by the resource group, the SQL digest and the plan digest, and provides statistics for each SQL category.

The "SQL digest" here means the same as used in slow logs, which is a unique identifier calculated through normalized SQL statements. The normalization process ignores constant, blank characters, and is case insensitive. Therefore, statements with consistent syntaxes have the same digest. For example:

```sql
SELECT * FROM employee WHERE id IN (1, 2, 3) AND salary BETWEEN 1000 AND 2000;
select * from EMPLOYEE where ID in (4, 5) and SALARY between 3000 and 4000;
```

After normalization, they are both of the following category:

```sql
select * from employee where id in (...) and salary between ? and ?;
```

The "plan digest" here refers to the unique identifier calculated through normalized execution plan. The normalization process ignores constants. The same SQL statements might be grouped into different categories because the same statements might have different execution plans. SQL statements of the same category have the same execution plan.

`statements_summary` stores the aggregated results of SQL monitoring metrics. In general, each of the monitoring metrics includes the maximum value and average value. For example, the execution latency metric corresponds to two fields: `AVG_LATENCY` (average latency) and `MAX_LATENCY` (maximum latency).

To make sure that the monitoring metrics are up to date, data in the `statements_summary` table is periodically cleared, and only recent aggregated results are retained and displayed. The periodical data clearing is controlled by the `tidb_stmt_summary_refresh_interval` system variable. If you happen to make a query right after the clearing, the data displayed might be very little.

The following is a sample output of querying `statements_summary`:

```
   SUMMARY_BEGIN_TIME: 2020-01-02 11:00:00
     SUMMARY_END_TIME: 2020-01-02 11:30:00
            STMT_TYPE: Select
          SCHEMA_NAME: test
               DIGEST: 0611cc2fe792f8c146cc97d39b31d9562014cf15f8d41f23a4938ca341f54182
          DIGEST_TEXT: select * from employee where id = ?
          TABLE_NAMES: test.employee
          INDEX_NAMES: NULL
          SAMPLE_USER: root
           EXEC_COUNT: 3
          SUM_LATENCY: 1035161
          MAX_LATENCY: 399594
          MIN_LATENCY: 301353
          AVG_LATENCY: 345053
    AVG_PARSE_LATENCY: 57000
    MAX_PARSE_LATENCY: 57000
  AVG_COMPILE_LATENCY: 175458
  MAX_COMPILE_LATENCY: 175458
  ...........
              AVG_MEM: 103
              MAX_MEM: 103
              AVG_DISK: 65535
              MAX_DISK: 65535
    AVG_AFFECTED_ROWS: 0
           FIRST_SEEN: 2020-01-02 11:12:54
            LAST_SEEN: 2020-01-02 11:25:24
    QUERY_SAMPLE_TEXT: select * from employee where id=3100
     PREV_SAMPLE_TEXT:
          PLAN_DIGEST: f415b8d52640b535b9b12a9c148a8630d2c6d59e419aad29397842e32e8e5de3
                 PLAN:  Point_Get_1     root    1       table:employee, handle:3100
```

> **Note:**
>
> - In TiDB, the time unit of fields in statement summary tables is nanosecond (ns), whereas in MySQL the time unit is picosecond (ps).
> - Starting from v7.5.1 and v7.6.0, for clusters with [resource control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) enabled, `statements_summary` will be aggregated by resource group, for example, the same statements executed in different resource groups will be collected as different records.
## `statements_summary_history`

The table schema of `statements_summary_history` is identical to that of `statements_summary`. `statements_summary_history` saves the history data of a time range. By checking history data, you can troubleshoot anomalies and compare monitoring metrics of different time ranges.

The fields `SUMMARY_BEGIN_TIME` and `SUMMARY_END_TIME` represent the start time and the end time of the historical time range.
## `statements_summary_evicted`

The [`tidb_stmt_summary_max_stmt_count`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_stmt_summary_max_stmt_count-new-in-v40) system variable limits the number of SQL digests that the `statements_summary` and `statements_summary_history` tables can store in memory totally. Once this limit is exceeded, TiDB evicts the least recently used SQL digests from both `statements_summary` and `statements_summary_history` tables.

> **Note:**
>
> When [`tidb_stmt_summary_enable_persistent`](#persist-statements-summary) is enabled, data in the `statements_summary_history` table is persisted to the disk. In this case, `tidb_stmt_summary_max_stmt_count` only limits the number of SQL digests that the `statements_summary` table can store in memory, and TiDB evicts the least recently used SQL digests only from the `statements_summary` table when `tidb_stmt_summary_max_stmt_count` is exceeded.

The `statements_summary_evicted` table records the period during which the eviction occurs and the number of SQL digests evicted during that period. This table helps you evaluate whether `tidb_stmt_summary_max_stmt_count` is properly configured for your workload. If this table contains records, it indicates that the number of SQL digests exceeded `tidb_stmt_summary_max_stmt_count` at some time point.

On the [SQL statements page of TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-statement-list#others), the information about evicted statements is displayed in the `Others` row.

On the [SQL statements tab of the Diagnosis page](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#statement-analysis), the information about evicted statements is displayed in the `Others` row.
## The `cluster` tables for statement summary

The `statements_summary`, `statements_summary_history`, and `statements_summary_evicted` tables only show the statement summary of a single TiDB server. To query the data of the entire cluster, you need to query the `cluster_statements_summary`, `cluster_statements_summary_history`, or `cluster_statements_summary_evicted` tables.

`cluster_statements_summary` displays the `statements_summary` data of each TiDB server. `cluster_statements_summary_history` displays the `statements_summary_history` data of each TiDB server. `cluster_statements_summary_evicted` displays the `statements_summary_evicted` data of each TiDB server. These tables use the `INSTANCE` field to represent the address of the TiDB server. The other fields are the same as those in `statements_summary`, `statements_summary_history`, and `statements_summary_evicted`.
