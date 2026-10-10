# TiDB Cloud release notes for February to March 2023

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2023.md`
- Source Title: `TiDB Cloud Release Notes in 2023`
- Source Heading Path: `TiDB Cloud Release Notes in 2023 > March 21, 2023 | TiDB Cloud Release Notes in 2023 > March 14, 2023 | TiDB Cloud Release Notes in 2023 > March 7, 2023 | TiDB Cloud Release Notes in 2023 > February 28, 2023 | TiDB Cloud Release Notes in 2023 > February 22, 2023 | TiDB Cloud Release Notes in 2023 > February 21, 2023 | TiDB Cloud Release Notes in 2023 > February 17, 2023 | TiDB Cloud Release Notes in 2023 > February 14, 2023`
- Source Line Ranges: `750-912`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`, `tikv`, `tiflash`
- Topic Tags: `release-notes`, `serverless`, `dedicated`, `data-service`, `chat2query`, `data-migration`, `monitoring`, `events`, `sql-diagnosis`, `api`, `cli`, `audit-logging`, `import`, `scaling`, `version-upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0642_2bd5297fe3`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2023.md#march-21-2023`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fdf15af593e1dd417191c8b5b32a06fb6ca15352740ae1eaae300b3a3eb32cc8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2023#march-21-2023
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2023.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB Cloud release-note details from February to March 2023 about Serverless Tier and Dedicated Tier changes such as Data Service (beta), Chat2Query API, SQL Diagnosis, Monitoring, Events, import APIs, audit logging, CLI commands, scaling, and default version upgrades.
- Retrieval Keywords: March 21 2023, March 14 2023, March 7 2023, February 28 2023, February 22 2023, February 21 2023, February 17 2023, February 14 2023, Data Service (beta), Chat2Query API, Serverless Tier, Dedicated Tier, Events page, Database Status, QPS Per DB, Average Query Duration Per DB, Failed Queries Per DB, SQL Diagnosis, slow query data, List all import tasks, Create an import task, Upload a local file for an import task, console audit logging, Owner, Audit Admin, ticloud cluster connect-info, ticloud connect, monitoring metrics retention period, Tokyo (asia-northeast1), UpdateCluster, v6.5.1, v6.6.0
- Follow-up Guidance: The chunk points to related documentation such as Data Service Overview, Get Started with Data Service, Get Started with Chat2Query API, TiDB Cloud cluster events, built-in monitoring, tune performance, API documentation for Import, Console audit logging, CLI reference, and scaling or migration documentation.
- Classification Note: This is a TiDB Cloud release-notes chunk covering cloud product updates across release, console, API, and CLI areas for both Serverless Tier and Dedicated Tier.

## Official Source Content

## March 21, 2023

**General changes**

- Introduce [Data Service (beta)](https://tidbcloud.com/project/data-service) for [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters, which enables you to access data via an HTTPS request using a custom API endpoint.

    With Data Service, you can seamlessly integrate TiDB Cloud with any application or service that is compatible with HTTPS. The following are some common scenarios:

    - Access the database of your TiDB cluster directly from a mobile or web application.
    - Use serverless edge functions to call endpoints and avoid scalability issues caused by database connection pooling.
    - Integrate TiDB Cloud with data visualization projects by using Data Service as a data source.
    - Connect to your database from an environment that MySQL interface does not support.

    In addition, TiDB Cloud provides the [Chat2Query API](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api), a RESTful interface that allows you to generate and execute SQL statements using AI.

    To access Data Service, navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page in the left navigation pane. For more information, see the following documentation:

    - [Data Service Overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-overview)
    - [Get Started with Data Service](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-get-started)
    - [Get Started with Chat2Query API](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api)

- Support decreasing the size of TiDB, TiKV, and TiFlash nodes to scale in a [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) cluster that is hosted on AWS and created after December 31, 2022.

    You can decrease the node size [via the TiDB Cloud console](https://docs.pingcap.com/tidb/stable/tidb-cloud/scale-tidb-cluster#change-vcpu-and-ram) or [via the TiDB Cloud API (beta)](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Cluster/operation/UpdateCluster).

- Support a new GCP region for the [Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration) feature of [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters: `Tokyo (asia-northeast1)`.

    The feature can help you migrate data from MySQL-compatible databases in Google Cloud Platform (GCP) to your TiDB cluster easily and efficiently.

    For more information, see [Migrate MySQL-compatible databases to TiDB Cloud using Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration).

**Console changes**

- Introduce the **Events** page for [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters, which provides the records of main changes to your cluster.

    On this page, you can view the event history for the last 7 days and track important details such as the trigger time and the user who initiated an action. For example, you can view events such as when a cluster was paused or who modified the cluster size.

    For more information, see [TiDB Cloud cluster events](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-events).

- Add the **Database Status** tab to the **Monitoring** page for [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters, which displays the following database-level metrics:

    - QPS Per DB
    - Average Query Duration Per DB
    - Failed Queries Per DB

  With these metrics, you can monitor the performance of individual databases, make data-driven decisions, and take actions to improve the performance of your applications.

  For more information, see [Monitoring metrics for Serverless Tier clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring).
## March 14, 2023

**General changes**

- Upgrade the default TiDB version of new [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v6.5.0](https://docs.pingcap.com/tidb/v6.5/release-6.5.0) to [v6.5.1](https://docs.pingcap.com/tidb/v6.5/release-6.5.1).

- Support modifying column names of the target table to be created by TiDB Cloud when uploading a local CSV file with a header row.

    When importing a local CSV file with a header row to a [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) cluster, if you need TiDB Cloud to create the target table and the column names in the header row do not follow the TiDB Cloud column naming conventions, you will see a warning icon next to the corresponding column name. To resolve the warning, you can move the cursor over the icon and follow the message to edit the existing column names or enter new column names.

    For information about column naming conventions, see [Import local files](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-import-local-files#import-local-files).
## March 7, 2023

**General changes**

- Upgrade the default TiDB version of all [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters from [v6.4.0](https://docs.pingcap.com/tidb/v6.4/release-6.4.0) to [v6.6.0](https://docs.pingcap.com/tidb/v6.6/release-6.6.0).
## February 28, 2023

**General changes**

- Add the [SQL Diagnosis](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance) feature for [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

    With SQL Diagnosis, you can gain deep insights into SQL-related runtime status, which makes the SQL performance tuning more efficient. Currently, the SQL Diagnosis feature for Serverless Tier only provides slow query data.

    To use SQL Diagnosis, click **SQL Diagnosis** on the left navigation bar of your Serverless Tier cluster page.

**Console changes**

- Optimize the left navigation.

    You can navigate pages more efficiently, for example:

    - You can hover the mouse in the upper-left corner to quickly switch between clusters or projects.
    - You can switch between the **Clusters** page and the **Admin** page.

**API changes**

- Release several TiDB Cloud API endpoints for data import：

    - List all import tasks
    - Get an import task
    - Create an import task
    - Update an import task
    - Upload a local file for an import task
    - Preview data before starting an import task
    - Get the role information for import tasks

  For more information, refer to the [API documentation](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Import).
## February 22, 2023

**General changes**

- Support using the [console audit logging](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-console-auditing) feature to track various activities performed by members within your organization in the [TiDB Cloud console](https://tidbcloud.com/).

    The console audit logging feature is only visible to users with the `Owner` or `Audit Admin` role and is disabled by default. To enable it, click <MDSvgIcon name="icon-top-organization" /> **Organization** > **Console Audit Logging** in the upper-right corner of the [TiDB Cloud console](https://tidbcloud.com/).

    By analyzing console audit logs, you can identify suspicious operations performed within your organization, thereby improving the security of your organization's resources and data.

    For more information, see [Console audit logging](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-console-auditing).

**CLI changes**

- Add a new command `ticloud cluster connect-info` for [TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference).

    `ticloud cluster connect-info` is a command that allows you to get the connection string of a cluster. To use this command, [update `ticloud`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-upgrade) to v0.3.2 or a later version.
## February 21, 2023

**General changes**

- Support using the AWS access keys of an IAM user to access your Amazon S3 bucket when importing data to TiDB Cloud.

    This method is simpler than using Role ARN. For more information, refer to [Configure Amazon S3 access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-amazon-s3-access).

- Extend the [monitoring metrics retention period](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring#metrics-retention-policy) from 2 days to a longer period:

    - For Dedicated Tier clusters, you can view metrics data for the past 7 days.
    - For Serverless Tier clusters, you can view metrics data for the past 3 days.

  By extending the metrics retention period, now you have access to more historical data. This helps you identify trends and patterns of the cluster for better decision-making and faster troubleshooting.

**Console changes**

- Release a new native web infrastructure on the Monitoring page of [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

    With the new infrastructure, you can easily navigate through the Monitoring page and access the necessary information in a more intuitive and efficient manner. The new infrastructure also resolves many problems on UX, making the monitoring process a lot more user-friendly.
## February 17, 2023

**CLI changes**

- Add a new command [`ticloud connect`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-shell) for [TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference).

    `ticloud connect` is a command that allows you to connect to your TiDB Cloud cluster from your local machine without installing any SQL clients. After connecting to your TiDB Cloud cluster, you can execute SQL statements in the TiDB Cloud CLI.
## February 14, 2023

**General changes**

- Support decreasing the number of TiKV and TiFlash nodes to scale in a TiDB [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) cluster.

    You can decrease the node number [via the TiDB Cloud console](https://docs.pingcap.com/tidb/stable/tidb-cloud/scale-tidb-cluster#change-node-number) or [via the TiDB Cloud API (beta)](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Cluster/operation/UpdateCluster).

**Console changes**

- Introduce the **Monitoring** page for [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

    The **Monitoring** page provides a range of metrics and data, such as the number of SQL statements executed per second, the average duration of queries, and the number of failed queries, which helps you better understand the overall performance of SQL statements in your Serverless Tier cluster.

    For more information, see [TiDB Cloud built-in monitoring](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring).
