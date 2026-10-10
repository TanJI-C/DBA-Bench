# May-June 2023 cloud release updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2023.md`
- Source Title: `TiDB Cloud Release Notes in 2023`
- Source Heading Path: `TiDB Cloud Release Notes in 2023 > June 13, 2023 | TiDB Cloud Release Notes in 2023 > June 6, 2023 | TiDB Cloud Release Notes in 2023 > June 5, 2023 | TiDB Cloud Release Notes in 2023 > June 2, 2023 | TiDB Cloud Release Notes in 2023 > May 30, 2023 | TiDB Cloud Release Notes in 2023 > May 23, 2023 | TiDB Cloud Release Notes in 2023 > May 16, 2023`
- Source Line Ranges: `407-527`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `tikv`, `dashboard`, `dm`
- Topic Tags: `release-notes`, `changefeed`, `amazon-s3`, `storage-scaling`, `metrics-retention`, `key-visualizer`, `index-insight`, `playground`, `data-app`, `github`, `ci-cd`, `naming`, `incremental-migration`, `gtid`, `events`, `csv-import`, `console-navigation`, `slow-query`, `sql-statement`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0639_8972540bff`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2023.md#june-13-2023`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c63391c11527b0821b3d12d0d2ad07733e821ff51ce17999147ed4060f2d1ad3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2023#june-13-2023
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2023.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB Cloud release-note updates from May to June 2023 about changefeed to Amazon S3, TiDB Cloud Dedicated and Serverless changes, console navigation and diagnosis UI updates, Data App GitHub integration, naming updates, incremental migration, and CSV import behavior.
- Retrieval Keywords: June 13 2023, June 6 2023, June 5 2023, June 2 2023, May 30 2023, May 23 2023, May 16 2023, changefeeds to stream data to Amazon S3, Sink to cloud storage, TiDB Cloud Dedicated, TiDB Cloud Serverless, 16 vCPU TiKV, maximum node storage 4 TiB to 6 TiB, monitoring metrics retention period 3 days to 7 days, Key Visualizer, Index Insight beta, Diagnosis page, Index Insight BETA, TiDB Playground, Data App, GitHub, CI/CD, TiDB Cloud Serverless Tier, TiDB Cloud Dedicated Tier, TiDB Self-Managed, incremental data migration, binlog position, global transaction identifier, GTID, ImportData, Events page, Playground removed from the TiDB Cloud console, CSV file, Import Local Files to TiDB Cloud, left navigation entries organized by functional categories, Slow Query, SQL Statement
- Follow-up Guidance: The source points to related documentation such as Sink to cloud storage, Use Index Insight (beta), Deploy Data App automatically with GitHub, Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration, and Import Local Files to TiDB Cloud.
- Classification Note: This chunk is classified as a cloud release-notes entry because the official content is a dated list of TiDB Cloud general and console changes across multiple features and components.

## Official Source Content

## June 13, 2023

**General changes**

- Support using changefeeds to stream data to Amazon S3.

    This enables seamless integration between TiDB Cloud and Amazon S3. It allows real-time data capture and replication from [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters to Amazon S3, ensuring that downstream applications and analytics have access to up-to-date data.

    For more information, see [Sink to cloud storage](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-cloud-storage).

- Increase the maximum node storage of 16 vCPU TiKV for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from 4 TiB to 6 TiB.

    This enhancement increases the data storage capacity of your TiDB Cloud Dedicated cluster, improves workload scaling efficiency, and accommodates growing data requirements.

    For more information, see [Size your cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster).

- Extend the [monitoring metrics retention period](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring#metrics-retention-policy) for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters from 3 days to 7 days.

    By extending the metrics retention period, now you have access to more historical data. This helps you identify trends and patterns of the cluster for better decision-making and faster troubleshooting.

**Console changes**

- Release a new native web infrastructure for the [**Key Visualizer**](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#key-visualizer) page of [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.

    With the new infrastructure, you can easily navigate through the **Key Visualizer** page and access the necessary information in a more intuitive and efficient manner. The new infrastructure also resolves many problems on UX, making the SQL diagnosis process more user-friendly.
## June 6, 2023

**General changes**

- Introduce [Index Insight (beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/index-insight) for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters, which optimizes query performance by providing index recommendations for slow queries.

    With Index Insight, you can improve the overall application performance and efficiency of your database operations in the following ways:

    - Enhanced query performance: Index Insight identifies slow queries and suggests appropriate indexes for them, thereby speeding up query execution, reducing response time, and improving user experience.
    - Cost efficiency: By using Index Insight to optimize query performance, the need for extra computing resources is reduced, enabling you to use existing infrastructure more effectively. This can potentially lead to operational cost savings.
    - Simplified optimization process: Index Insight simplifies the identification and implementation of index improvements, eliminating the need for manual analysis and guesswork. As a result, you can save time and effort with accurate index recommendations.
    - Improved application efficiency: By using Index Insight to optimize database performance, applications running on TiDB Cloud can handle larger workloads and serve more users concurrently, which makes scaling operations of applications more efficient.

  To use Index Insight, navigate to the **Diagnosis** page of your TiDB Cloud Dedicated cluster and click the **Index Insight BETA** tab.

    For more information, see [Use Index Insight (beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/index-insight).

- Introduce [TiDB Playground](https://play.tidbcloud.com/?utm_source=docs&utm_medium=tidb_cloud_release_notes), an interactive platform for experiencing the full capabilities of TiDB, without registration or installation.

    TiDB Playground is an interactive platform designed to provide a one-stop-shop experience for exploring the capabilities of TiDB, such as scalability, MySQL compatibility, and real-time analytics.

    With TiDB Playground, you can try out TiDB features in a controlled environment free from complex configurations in real-time, making it ideal to understand the features in TiDB.

    To get started with TiDB Playground, go to the [**TiDB Playground**](https://play.tidbcloud.com/?utm_source=docs&utm_medium=tidb_cloud_release_notes) page, select a feature you want to explore, and begin your exploration.
## June 5, 2023

**General changes**

- Support connecting your [Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#data-app) to GitHub.

    By [connecting your Data App to GitHub](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-github-connection), you can manage all configurations of the Data App as [code files](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-app-config-files) on Github, which integrates TiDB Cloud Data Service seamlessly with your system architecture and DevOps process.

    With this feature, you can easily accomplish the following tasks, which improves the CI/CD experience of developing Data Apps:

    - Automatically deploy Data App changes with GitHub.
    - Configure CI/CD pipelines of your Data App changes on GitHub with version control.
    - Disconnect from a connected GitHub repository.
    - Review endpoint changes before the deployment.
    - View deployment history and take necessary actions in the event of a failure.
    - Re-deploy a commit to roll back to an earlier deployment.

  For more information, see [Deploy Data App automatically with GitHub](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-github-connection).
## June 2, 2023

**General changes**

- In our pursuit to simplify and clarify, we have updated the names of our products:

    - "TiDB Cloud Serverless Tier" is now called "TiDB Cloud Serverless".
    - "TiDB Cloud Dedicated Tier" is now called "TiDB Cloud Dedicated".
    - "TiDB On-Premises" is now called "TiDB Self-Managed".

    Enjoy the same great performance under these refreshed names. Your experience is our priority.
## May 30, 2023

**General changes**

- Enhance support for incremental data migration for the Data Migration feature in TiDB Cloud.

    You can now specify a binlog position or a global transaction identifier (GTID) to replicate only incremental data generated after the specified position to TiDB Cloud. This enhancement empowers you with greater flexibility to select and replicate the data you need, aligning with your specific requirements.

    For details, refer to [Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration).

- Add a new event type (`ImportData`) to the [**Events**](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-events) page.

- Remove **Playground** from the TiDB Cloud console.

    Stay tuned for the new standalone Playground with an optimized experience.
## May 23, 2023

**General changes**

- When uploading a CSV file to TiDB, you can use not only English letters and numbers, but also characters such as Chinese and Japanese to define column names. However, for special characters, only underscore (`_`) is supported.

    For details, refer to [Import Local Files to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-import-local-files).
## May 16, 2023

**Console changes**

- Introduce the left navigation entries organized by functional categories for both Dedicated and Serverless tiers.

    The new navigation makes it easier and more intuitive for you to discover the feature entries. To view the new navigation, access the overview page of your cluster.

- Release a new native web infrastructure for the following two tabs on the **Diagnosis** page of Dedicated Tier clusters.

    - [Slow Query](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#slow-query)
    - [SQL Statement](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#statement-analysis)

    With the new infrastructure, you can easily navigate through the two tabs and access the necessary information in a more intuitive and efficient manner. The new infrastructure also improves user experience, making the SQL diagnosis process more user-friendly.
