# TiDB Cloud diagnosis and performance analysis features

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tune-performance.md`
- Source Title: `Analyze and Tune Performance`
- Source Heading Path: `Analyze and Tune Performance | Analyze and Tune Performance > View the Diagnosis page | Analyze and Tune Performance > Slow Query | Analyze and Tune Performance > Statement Analysis | Analyze and Tune Performance > Key Visualizer | Analyze and Tune Performance > Index Insight (beta)`
- Source Line Ranges: `5-90`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`, `sql`, `tidb`
- Topic Tags: `diagnosis-page`, `slow-query`, `statement-analysis`, `key-visualizer`, `index-insight`, `performance-analysis`, `cluster-monitoring`, `dedicated-tier`, `serverless-limitations`, `beta-feature`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0207_46b00743df`
- Source ID: `tidb-docs-8.1:tidb-cloud/tune-performance.md#analyze-and-tune-performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e71839de51a6fd78f80ccbc8a73c1f21f4bb9f45170f7f14383f1a461bb7f3ae`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#analyze-and-tune-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tune-performance.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB Cloud performance diagnosis features, how to open the Diagnosis page, or what Slow Query, Statement Analysis, Key Visualizer, and Index Insight provide in TiDB Cloud.
- Retrieval Keywords: Analyze and Tune Performance, Diagnosis page, Monitoring > Diagnosis, Slow Query, SQL Statement, Statement Analysis, Key Visualizer, Index Insight (beta), TiDB Cloud Dedicated, TiDB Cloud Serverless, slow queries more than 300 milliseconds, Statement Execution Details in TiDB Dashboard, Slow Queries in TiDB Dashboard, dashboard-key-visualizer
- Follow-up Guidance: The content also states that Key Visualizer and Index Insight (beta) are unavailable for TiDB Cloud Serverless clusters, and that both are only available for TiDB Cloud Dedicated clusters.
- Classification Note: This is classified as cloud performance content because it describes TiDB Cloud diagnosis and performance analysis pages and feature availability, including cluster-tier limitations.

## Official Source Content

# Analyze and Tune Performance

TiDB Cloud provides [Slow Query](#slow-query), [Statement Analysis](#statement-analysis), [Key Visualizer](#key-visualizer), and [Index Insight (beta)](#index-insight-beta) to analyze performance.

- Slow Query lets you search and view all slow queries in your TiDB cluster, and explore the bottlenecks of each slow query by viewing its execution plan, SQL execution information, and other details.

- Statement Analysis enables you to directly observe the SQL execution on the page, and easily locate performance problems without querying the system tables.

- Key Visualizer helps you observe TiDB's data access patterns and data hotspots.

- Index Insight provides you with meaningful and actionable index recommendations.

> **Note:**
>
> Currently, **Key Visualizer** and **Index Insight (beta)** are unavailable for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.
## View the Diagnosis page

1. On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target cluster to go to its overview page.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. In the left navigation pane, click **Monitoring** > **Diagnosis**.
## Slow Query

By default, SQL queries that take more than 300 milliseconds are considered as slow queries.

To view slow queries in a cluster, perform the following steps:

1. Navigate to the [**Diagnosis**](#view-the-diagnosis-page) page of a cluster.

2. Click the **Slow Query** tab.

3. Click any slow query in the list to display its detailed execution information.

4. (Optional) You can filter slow queries based on the target time range, the related databases, and SQL keywords. You can also limit the number of slow queries to be displayed.

The results are displayed in the form of a table, and you can sort the results by different columns.

For more information, see [Slow Queries in TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard-slow-query).
## Statement Analysis

To use the statement analysis, perform the following steps:

1. Navigate to the [**Diagnosis**](#view-the-diagnosis-page) page of a cluster.

2. Click the **SQL Statement** tab.

3. Select the time period to be analyzed in the time interval box. Then you can get the execution statistics of SQL statements of all databases in this period.

4. (Optional) If you only care about certain databases, you can select the corresponding schema(s) in the next box to filter the results.

The results are displayed in the form of a table, and you can sort the results by different columns.

For more information, see [Statement Execution Details in TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard-statement-details).
## Key Visualizer

> **Note:**
>
> Key Visualizer is only available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.

To view the key analytics, perform the following steps:

1. Navigate to the [**Diagnosis**](#view-the-diagnosis-page) page of a cluster.

2. Click the **Key Visualizer** tab.

On the **Key Visualizer** page, a large heat map shows changes on access traffic over time. The average values ​​along each axis of the heat map are shown below and on the right side. The left side is the table name, index name and other information.

For more information, see [Key Visualizer](https://docs.pingcap.com/tidb/stable/dashboard-key-visualizer).
## Index Insight (beta)

The Index Insight feature in TiDB Cloud provides powerful capabilities to optimize query performance by offering recommended indexes for slow queries that are not utilizing indexes effectively.

> **Note:**
>
> Index Insight is currently in beta and only available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.

For more information, see [Index Insight](https://docs.pingcap.com/tidb/stable/tidb-cloud/index-insight).
