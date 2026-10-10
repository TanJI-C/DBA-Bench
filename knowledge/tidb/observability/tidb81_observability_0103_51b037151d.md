# TiDB Cloud Clinic monitoring, slow query analysis, TopSQL, and benchmark reports

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-clinic.md`
- Source Title: `TiDB Cloud Clinic`
- Source Heading Path: `TiDB Cloud Clinic > Monitor advanced metrics | TiDB Cloud Clinic > Analyze top slow queries | TiDB Cloud Clinic > Monitor TopSQL | TiDB Cloud Clinic > Generate benchmark reports`
- Source Line Ranges: `35-123`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`, `tidb`, `tikv`, `dm`, `lightning`, `ticdc`, `tiflash`
- Topic Tags: `metrics`, `grafana`, `slow-queries`, `topsql`, `benchmark-report`, `retention`, `performance-analysis`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0103_51b037151d`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-clinic.md#monitor-advanced-metrics`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f122b5d48aefd2b8fa83405332ea8b940a39980cef1399c0c375a292ab5e9db1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-clinic#monitor-advanced-metrics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-clinic.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB Cloud Clinic observability features such as Grafana dashboards, Top Slow Queries, TopSQL, benchmark reports, retention periods, or how to view these pages from a cluster.
- Retrieval Keywords: Monitor advanced metrics, Grafana, retention policy for advanced metrics is 90 days, Metrics, Backup & Import, DM-Professional, DM-Standard, Lightning, Performance-Overview, TiCDC-Summary, TiDB, TiDB-Resource-Control, TiFlash-Summary, TiKV-Details, User-Node-Info, Analyze top slow queries, slow queries longer than 300 milliseconds, Top Slow Queries, SQL digest, Total latency, Maximum latency, Average latency, Total memory, Maximum memory, Average memory, Total count, retention policy for slow queries is 7 days, Slow Query, Monitor TopSQL, CPU overhead of each SQL statement, TiDB instance, TiKV instance, time picker, Generate benchmark reports, Benchmark Report, Create Report, View
- Follow-up Guidance: The source also points to related documentation for Slow Queries in TiDB Dashboard and TopSQL in TiDB Dashboard.
- Classification Note: This is classified as observability because the content focuses on monitoring metrics, analyzing slow queries and TopSQL, and generating benchmark reports for performance analysis.

## Official Source Content

## Monitor advanced metrics

TiDB Cloud Clinic uses Grafana to provide a comprehensive set of metrics for TiDB clusters. The retention policy for advanced metrics is 90 days.

To view the metrics dashboard, take the following steps:

1. In the [TiDB Cloud Clinic console](https://clinic.pingcap.com/), navigate to the **Cluster** page of a cluster.

2. Click **Metrics**.

3. Click the name of the dashboard you want to view. The dashboard is displayed.

The dashboards and their content are subject to change. Currently, the following dashboards are available:

- Backup & Import
- DM-Professional
- DM-Standard
- Lightning
- Performance-Overview
- TiCDC-Summary
- TiDB
- TiDB-Resource-Control
- TiFlash-Summary
- TiKV-Details
- User-Node-Info
## Analyze top slow queries

By default, SQL queries that take longer than 300 milliseconds are considered slow queries.

On the default [**Slow Queries**](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#slow-query) page in the TiDB Cloud console, identifying performance-impacting queries can be difficult, especially in clusters with a large number of slow queries. The **Top Slow Queries** feature in TiDB Cloud Clinic provides aggregated analysis based on slow query logs. With this feature, you can easily pinpoint queries with performance issues, reducing overall performance tuning time by at least half.

Top Slow Queries displays the top 10 queries aggregated by SQL digest, sorted by the following dimensions:

- Total latency 
- Maximum latency
- Average latency
- Total memory
- Maximum memory
- Average memory
- Total count

To view slow queries in a cluster, take the following steps:

1. In the [TiDB Cloud Clinic console](https://clinic.pingcap.com/), navigate to the **Cluster** page of a cluster.

2. Click **Slow Query**.

3. The top slow queries are displayed in a table. You can sort the results by different columns.

4. (Optional) Click any slow query in the list to view its detailed execution information.

5. (Optional) Filter slow queries by time range, database, or statement type.

The retention policy for slow queries is 7 days.

For more information, see [Slow Queries in TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard-slow-query).
## Monitor TopSQL

TiDB Cloud Clinic provides TopSQL information, enabling you to monitor and visually explore the CPU overhead of each SQL statement in your database in real time. This helps you optimize and resolve database performance issues.

To view TopSQL, take the following steps:

1. In the [TiDB Cloud Clinic console](https://clinic.pingcap.com/), navigate to the **Cluster** page of a cluster.

2. Click **TopSQL**.

3. Select a specific TiDB or TiKV instance to observe its load. You can use the time picker or select a time range in the chart to refine your analysis.

4. Analyze the charts and tables displayed by TopSQL.

For more information, see [TopSQL in TiDB Dashboard](https://docs.pingcap.com/tidb/stable/top-sql). 
## Generate benchmark reports

The **Benchmark Report** feature helps you identify performance issues in a TiDB cluster during performance testing. After completing a stress test, you can generate a benchmark report to analyze the cluster's performance. The report highlights identified bottlenecks and provides optimization suggestions. After applying these suggestions, you can run another round of stress testing and generate a new benchmark report to compare performance improvements.

To generate a benchmark report, take the following steps:

1. In the [TiDB Cloud Clinic console](https://clinic.pingcap.com/), navigate to the **Cluster** page of a cluster.

2. Click **Benchmark Report**.

3. Select the time range to be analyzed in the benchmark report.

4. Click **Create Report** to generate the benchmark report.

5. Wait for report generation to complete. When the report is ready, click **View** to open it.
