# Index Insight overview, setup, usage, and best practices

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/index-insight.md`
- Source Title: `Index Insight (Beta)`
- Source Heading Path: `Index Insight (Beta) | Index Insight (Beta) > Introduction | Index Insight (Beta) > Usage | Index Insight (Beta) > Usage > Before you begin | Index Insight (Beta) > Usage > Step 1: Enable Index Insight | Index Insight (Beta) > Usage > Step 2: Manually trigger Index Insight | Index Insight (Beta) > Usage > Step 3: View index recommendations | Index Insight (Beta) > Usage > Step 4: Implement index recommendations | Index Insight (Beta) > Best practices | Index Insight (Beta) > Best practices > Regularly trigger Index Insight | Index Insight (Beta) > Best practices > Analyze impact before implementing indexes | Index Insight (Beta) > Best practices > Monitor performance`
- Source Line Ranges: `5-91`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `index recommendations`, `slow queries`, `activation`, `sql user`, `privileges`, `manual trigger`, `diagnosis page`, `performance monitoring`, `best practices`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0196_37f7cb9c10`
- Source ID: `tidb-docs-8.1:tidb-cloud/index-insight.md#index-insight-beta`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `665127f28b67f0ac4ab59bc4645b56512cdb76bfdd141b25a09cace9312f1040`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/index-insight#index-insight-beta
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/index-insight.md

## Retrieval Guidance

- Use When: Use this when the user needs how Index Insight (Beta) works in TiDB Cloud Dedicated, including activation, manual check-up, SQL user privileges, viewing recommendations, and implementation best practices.
- Retrieval Keywords: Index Insight (Beta), TiDB Cloud Dedicated, Diagnosis page, Index Insight overview, Index Insight BETA, Activate, Check Up, slow queries from the past three hours, Index Insight Details, index recommendations, related slow queries, execution plans, relevant metrics, CREATE user 'index_insight_user'@'%' IDENTIFIED by 'random_password', GRANT SELECT ON information_schema.*, GRANT SELECT ON mysql.*, GRANT PROCESS, REFERENCES ON *.*, FLUSH PRIVILEGES, monitor query performance, analyze impact before implementing indexes
- Follow-up Guidance: The source also includes best practices to trigger Index Insight periodically, analyze query execution plans and disk space trade-offs before creating indexes, and monitor performance after implementation.
- Classification Note: This is classified as performance because the official content describes using Index Insight to identify slow queries and recommend indexes to optimize query performance in TiDB Cloud.

## Official Source Content

# Index Insight (Beta)

The Index Insight (beta) feature in TiDB Cloud provides powerful capabilities to optimize query performance by offering index recommendations for slow queries that are not using indexes effectively. This document walks you through the steps to enable and utilize the Index Insight feature effectively.

> **Note:**
>
> Index Insight is currently in beta and only available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.
## Introduction

The Index Insight feature provides you with the following benefits:

- Enhanced query performance: Index Insight identifies slow queries and suggests appropriate indexes for them, thereby speeding up query execution, reducing response time, and improving user experience.
- Cost efficiency: By using Index Insight to optimize query performance, the need for extra computing resources is reduced, enabling you to use existing infrastructure more effectively. This can potentially lead to operational cost savings.
- Simplified optimization process: Index Insight simplifies the identification and implementation of index improvements, eliminating the need for manual analysis and guesswork. As a result, you can save time and effort with accurate index recommendations.
- Improved application efficiency: By using Index Insight to optimize database performance, applications running on TiDB Cloud can handle larger workloads and serve more users concurrently, which makes scaling operations of applications more efficient.
## Usage

This section introduces how to enable the Index Insight feature and obtain recommended indexes for slow queries.
### Before you begin

Before enabling the Index Insight feature, make sure that you have created a TiDB Cloud Dedicated cluster. If you do not have one, follow the steps in [Create a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster) to create one.
### Step 1: Enable Index Insight

1. Navigate to the [**Diagnosis**](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#view-the-diagnosis-page) page of your TiDB Cloud Dedicated cluster.

2. Click the **Index Insight BETA** tab. The **Index Insight overview** page is displayed.

3. To use the Index Insight feature, you need to create a dedicated SQL user, which is used to trigger the feature and receive index recommendations. The following SQL statements create a new SQL user with required privileges, including read privilege for `information_schema` and `mysql`, and `PROCESS` and `REFERENCES` privileges for all databases. Replace `'index_insight_user'` and `'random_password'` with your values.

    ```sql
    CREATE user 'index_insight_user'@'%' IDENTIFIED by 'random_password';
    GRANT SELECT ON information_schema.* TO 'index_insight_user'@'%';
    GRANT SELECT ON mysql.* TO 'index_insight_user'@'%';
    GRANT PROCESS, REFERENCES ON *.* TO 'index_insight_user'@'%';
    FLUSH PRIVILEGES;
    ```

    > **Note:**
    >
    > To connect to your TiDB Cloud Dedicated cluster, see [Connect to a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-to-tidb-cluster).

4. Enter the username and password of the SQL user created in the preceding step. Then, click **Activate** to initiate the activation process.
### Step 2: Manually trigger Index Insight

To obtain index recommendations for slow queries, you can manually trigger the Index Insight feature by clicking **Check Up** in the upper-right corner of the **Index Insight overview** page.

Then, the feature begins scanning slow queries from the past three hours. After the scan finishes, it provides a list of index recommendations based on its analysis.
### Step 3: View index recommendations

To view the details of a specific index recommendation, click the insight from the list. The **Index Insight Details** page is displayed.

On this page, you can find the index recommendations, related slow queries, execution plans, and relevant metrics. This information helps you better understand the performance issues and evaluate the potential impact of implementing the index recommendations.
### Step 4: Implement index recommendations

Before implementing the index recommendations, you need to first review and evaluate the recommendations from the **Index Insight Details** page.

To implement the index recommendations, follow these steps:

1. Evaluate the impact of the proposed index on existing queries and workload.
2. Consider the storage requirements and potential trade-offs associated with the index implementation.
3. Use appropriate database management tools to create the index recommendations on the relevant tables.
4. Monitor the performance after implementing the indexes to assess the improvements.
## Best practices

This section introduces some best practices for using the Index Insight feature.
### Regularly trigger Index Insight

To maintain optimized indexes, it is recommended to trigger the Index Insight feature periodically, such as every day, or whenever substantial changes occur in your queries or database schema.
### Analyze impact before implementing indexes

Before implementing the index recommendations, analyze the potential impact on query execution plans, disk space, and any trade-offs involved. Prioritize implementing indexes that provide the most significant performance improvements.
### Monitor performance

Regularly monitor query performance after implementing the index recommendations. This helps you confirm the improvements and make further adjustments if necessary.
