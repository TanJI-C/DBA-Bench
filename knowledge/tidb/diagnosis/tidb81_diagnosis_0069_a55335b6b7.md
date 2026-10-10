# Identify high-load SQL and collect execution data

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > Identify high-load SQL | A Practical Guide for SQL Tuning > Identify high-load SQL > Monitor SQL statements using TiDB Dashboard | A Practical Guide for SQL Tuning > Identify high-load SQL > Monitor SQL statements using TiDB Dashboard > SQL Statements page | A Practical Guide for SQL Tuning > Identify high-load SQL > Monitor SQL statements using TiDB Dashboard > Slow Queries page | A Practical Guide for SQL Tuning > Identify high-load SQL > Use other tools to identify Top SQL | A Practical Guide for SQL Tuning > Identify high-load SQL > Gather data on identified SQL statements`
- Source Line Ranges: `80-127`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `sql`, `tidb`
- Topic Tags: `top-sql`, `slow-queries`, `sql-statements`, `dashboard`, `logs`, `views`, `plan-replayer`, `explain-analyze`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0069_a55335b6b7`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#identify-high-load-sql`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `304e6197636e8196d95170ad9b3c141cec5ef7c0279c140bf1965b9e0935211b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#identify-high-load-sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when the need is to identify high-load SQL statements, compare TiDB Dashboard pages for SQL analysis, or gather execution data for a specific SQL statement.
- Retrieval Keywords: Identify high-load SQL, TiDB Dashboard, SQL Statements page, Slow Queries page, Top SQL Page, EXPLAIN ANALYZE, tidb_slow_log_threshold, slow query log, expensive queries in TiDB log, cluster_statements_summary, cluster_processlist, PLAN REPLAYER, PLAN REPLAYER DUMP EXPLAIN, WITH STATS AS OF TIMESTAMP, normalized SQL templates, highest total latency, execution frequency, reads the most data from TiKV
- Follow-up Guidance: For identified top SQL statements, the content says to use PLAN REPLAYER to capture and save SQL execution information and notes that EXPLAIN ANALYZE provides both the execution plan and actual performance metrics.
- Classification Note: This is classified as diagnosis for the dashboard component because the content focuses on monitoring SQL statements, finding slow or resource-intensive queries, and collecting execution information with dashboard pages, views, logs, and PLAN REPLAYER.

## Official Source Content

## Identify high-load SQL

The most efficient way to identify resource-intensive SQL statements is by using [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-overview). You can also use other tools, such as views and logs, to identify high-load SQL statements.
### Monitor SQL statements using TiDB Dashboard
#### SQL Statements page

In [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-overview), navigate to the [**SQL Statements** page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-statement-list) to identify the following:

- The SQL statement with the highest total latency, which is the statement that takes the longest time to execute across multiple executions.
- The number of times each SQL statement has been executed, which helps identify statements with the highest execution frequency.
- Execution details of each SQL statement by clicking it to view `EXPLAIN ANALYZE` results.

TiDB normalizes SQL statements into templates by replacing literals and bind variables with `?`. This normalization and sorting process helps you quickly identify the most resource-intensive queries that might require optimization.

![sql-statements-default](/media/sql-tuning/sql-statements-default.png)
#### Slow Queries page

In [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-overview), navigate to the [**Slow Queries** page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-slow-query) to find the following:

- The slowest SQL queries.
- The SQL query that reads the most data from TiKV.
- The `EXPLAIN ANALYZE` output by clicking a query for detailed execution analysis.

The **Slow Queries** page does not display SQL execution frequency. A query appears on this page if its execution time exceeds the [`tidb_slow_log_threshold`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_slow_log_threshold) configuration item for a single instance.

![slow-query-default](/media/sql-tuning/slow-query-default.png)
### Use other tools to identify Top SQL

In addition to TiDB Dashboard, you can use other tools to identify resource-intensive SQL queries. Each tool offers unique insights and can be valuable for different analysis scenarios. Using a combination of these tools helps ensure comprehensive SQL performance monitoring and optimization.

- [TiDB Dashboard Top SQL Page](https://docs.pingcap.com/tidb/stable/dashboard/top-sql)
- Logs: [slow query log](https://docs.pingcap.com/tidb/stable/identify-slow-queries) and [expensive queries in TiDB log](https://docs.pingcap.com/tidb/stable/identify-expensive-queries)
- Views: [`cluster_statements_summary` view](https://docs.pingcap.com/tidb/stable/statement-summary-tables#the-cluster-tables-for-statement-summary) and [`cluster_processlist` view](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-processlist#cluster_processlist)
### Gather data on identified SQL statements

For the top SQL statements identified, you can use [`PLAN REPLAYER`](https://docs.pingcap.com/tidb/stable/sql-plan-replayer) to capture and save SQL execution information from a TiDB cluster. This tool helps recreate the execution environment for further analysis. To export SQL execution information, use the following syntax:

```sql
PLAN REPLAYER DUMP EXPLAIN [ANALYZE] [WITH STATS AS OF TIMESTAMP expression] sql-statement;
```

Use `EXPLAIN ANALYZE` whenever possible, as it provides both the execution plan and actual performance metrics for more accurate insights into query performance.
