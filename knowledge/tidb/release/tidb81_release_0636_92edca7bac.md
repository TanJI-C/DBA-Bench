# TiDB Cloud 2023 release notes: Sep 19 to Dec 5 updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2023.md`
- Source Title: `TiDB Cloud Release Notes in 2023`
- Source Heading Path: `TiDB Cloud Release Notes in 2023 | TiDB Cloud Release Notes in 2023 > December 5, 2023 | TiDB Cloud Release Notes in 2023 > November 28, 2023 | TiDB Cloud Release Notes in 2023 > November 21, 2023 | TiDB Cloud Release Notes in 2023 > November 14, 2023 | TiDB Cloud Release Notes in 2023 > November 7, 2023 | TiDB Cloud Release Notes in 2023 > October 31, 2023 | TiDB Cloud Release Notes in 2023 > October 25, 2023 | TiDB Cloud Release Notes in 2023 > October 11, 2023 | TiDB Cloud Release Notes in 2023 > October 10, 2023 | TiDB Cloud Release Notes in 2023 > September 28, 2023 | TiDB Cloud Release Notes in 2023 > September 19, 2023`
- Source Line Ranges: `5-154`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `ticdc`, `sql`, `ecosystem`, `shared`
- Topic Tags: `release-notes`, `serverless`, `dedicated`, `changefeed`, `backup-restore`, `sql-bindings`, `user-accounts`, `data-migration`, `physical-mode`, `logical-mode`, `alerting`, `resource-usage`, `support-plan`, `dual-region-backup`, `kafka`, `vercel`, `billing-api`, `serverless-driver`, `cost-estimation`, `ru-costs`, `branching`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0636_92edca7bac`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2023.md#tidb-cloud-release-notes-in-2023`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7794b7cf34b3d707c244fc3cb2d41c21fcb6217a3587f7b8eb6cffdba55fe8aa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2023#tidb-cloud-release-notes-in-2023
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2023.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud release note updates from September 19 to December 5, 2023 covering Serverless, Dedicated, changefeed, backup and restore, Data Migration, alerting, support plan, Billing API, and branching features.
- Retrieval Keywords: TiDB Cloud Release Notes in 2023, December 5 2023, November 28 2023, November 21 2023, November 14 2023, November 7 2023, October 31 2023, October 25 2023, October 11 2023, October 10 2023, September 28 2023, September 19 2023, resume a failed changefeed, Changefeed states, Connect to TiDB Cloud Serverless, restore user accounts and SQL bindings by default, SQL statement RU costs, Diagnosis page, SQL Statement tab, Data Migration physical mode, logical mode, 110 MiB/s, event filters for changefeeds, resource usage alerts, TiDB Cloud Built-in Alerting, Enterprise support plan, dual region backup beta, Google Cloud, AWS, Apache Kafka GA, Vercel Preview Deployments, Billing API v1beta1, serverless driver beta for JavaScript, Usage This Month
- Follow-up Guidance: The content points to related documentation such as Changefeed overview, Back up and restore TiDB Cloud Dedicated data, TiDB Cloud Built-in Alerting, TiDB Cloud Support, API documentation (v1beta1), and TiDB Cloud serverless driver (beta).
- Classification Note: This is a cloud release-notes chunk because it summarizes dated TiDB Cloud feature and console changes across Dedicated and Serverless offerings in late 2023.

## Official Source Content

# TiDB Cloud Release Notes in 2023

This page lists the release notes of [TiDB Cloud](https://www.pingcap.com/tidb-cloud/) in 2023.
## December 5, 2023

**General changes**

- [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) enables you to resume a failed changefeed, which saves your effort to recreate a new one.

    For more information, see [Changefeed states](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview#changefeed-states).

**Console changes**

- Enhance the connection experience for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless).

    Refine the **Connect** dialog interface to offer TiDB Cloud Serverless users a smoother and more efficient connection experience. In addition, TiDB Cloud Serverless introduces more client types and allows you to select the desired branch for connection.

    For more information, see [Connect to TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection-serverless).
## November 28, 2023

**General changes**

- [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) supports restoring SQL bindings from backups.

    TiDB Cloud Dedicated now restores user accounts and SQL bindings by default when restoring from a backup. This enhancement is available for clusters of v6.2.0 or later versions, streamlining the data restoration process. The restoration of SQL bindings ensures the smooth reintegration of query-related configurations and optimizations, providing you with a more comprehensive and efficient recovery experience.

    For more information, see [Back up and restore TiDB Cloud Dedicated data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore).

**Console changes**

- [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) supports monitoring SQL statement RU costs.

    TiDB Cloud Serverless now provides detailed insights into each SQL statement's [Request Units (RUs)](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#request-unit). You can view both the **Total RU** and **Mean RU** costs per SQL statement. This feature helps you identify and analyze RU costs, offering opportunities for potential cost savings in your operations.

    To check your SQL statement RU details, navigate to the **Diagnosis** page of [your TiDB Cloud Serverless cluster](https://tidbcloud.com/project/clusters) and then click the **SQL Statement** tab.
## November 21, 2023

**General changes**

- [Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration) supports high-speed physical mode for TiDB clusters deployed on Google Cloud.

    Now you can use physical mode for TiDB clusters deployed on AWS and Google Cloud. The migration speed of physical mode can reach up to 110 MiB/s, which is 2.4 times faster than logical mode. The improved performance is suitable for quickly migrating large datasets to TiDB Cloud.

    For more information, see [Migrate existing data and incremental data](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration#migrate-existing-data-and-incremental-data).
## November 14, 2023

**General changes**

- When you restore data from TiDB Cloud Dedicated clusters, the default behavior is now modified from restoring without user accounts to restoring with all user accounts.

    For more information, see [Back Up and Restore TiDB Cloud Dedicated Data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore).

- Introduce event filters for changefeeds.

    This enhancement empowers you to easily manage event filters for changefeeds directly through the [TiDB Cloud console](https://tidbcloud.com/), streamlining the process of excluding specific events from changefeeds and providing better control over data replication downstream.

    For more information, see [Changefeed](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview#edit-a-changefeed).
## November 7, 2023

**General changes**

- Add the following resource usage alerts. The new alerts are disabled by default. You can enable them as needed.

    - Max memory utilization across TiDB nodes exceeded 70% for 10 minutes
    - Max memory utilization across TiKV nodes exceeded 70% for 10 minutes
    - Max CPU utilization across TiDB nodes exceeded 80% for 10 minutes
    - Max CPU utilization across TiKV nodes exceeded 80% for 10 minutes

  For more information, see [TiDB Cloud Built-in Alerting](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-built-in-alerting#resource-usage-alerts).
## October 31, 2023

**General changes**

- Support directly upgrading to the Enterprise support plan in the TiDB Cloud console without contacting sales.

    For more information, see [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
## October 25, 2023

**General changes**

- [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) supports dual region backup (beta) on Google Cloud.

    TiDB Cloud Dedicated clusters hosted on Google Cloud work seamlessly with Google Cloud Storage. Similar to the [Dual-regions](https://cloud.google.com/storage/docs/locations#location-dr) feature of Google Cloud Storage, the pair of regions that you use for the dual-region in TiDB Cloud Dedicated must be within the same multi-region. For example, Tokyo and Osaka are in the same multi-region `ASIA` so they can be used together for dual-region storage.

    For more information, see [Back Up and Restore TiDB Cloud Dedicated Data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#turn-on-dual-region-backup).

- The feature of [streaming data change logs to Apache Kafka](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka) is now in General Availability (GA).

    After a successful 10-month beta trial, the feature of streaming data change logs from TiDB Cloud to Apache Kafka becomes generally available. Streaming data from TiDB to a message queue is a common need in data integration scenarios. You can use Kafka sink to integrate with other data processing systems (such as Snowflake) or support business consumption.

    For more information, see [Changefeed overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview).
## October 11, 2023

**General changes**

- Support [dual region backup (beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#turn-on-dual-region-backup) for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters deployed on AWS.

    You can now replicate backups across geographic regions within your cloud provider. This feature provides an additional layer of data protection and disaster recovery capabilities.

    For more information, see [Back up and restore TiDB Cloud Dedicated data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore).

- Data Migration now supports both physical mode and logical mode for migrating existing data.

    In physical mode, the migration speed can reach up to 110 MiB/s. Compared with 45 MiB/s in logical mode, the migration performance has improved significantly.

    For more information, see [Migrate existing data and incremental data](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration#migrate-existing-data-and-incremental-data).
## October 10, 2023

**General changes**

- Support using TiDB Cloud Serverless branches in [Vercel Preview Deployments](https://vercel.com/docs/deployments/preview-deployments), with TiDB Cloud Vercel integration.

    For more information, see [Connect with TiDB Cloud Serverless branching](https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-vercel#connect-with-tidb-cloud-serverless-branching).
## September 28, 2023

**API changes**

- Introduce a TiDB Cloud Billing API endpoint to retrieve the bill for the given month of a specific organization.

    This Billing API endpoint is released in TiDB Cloud API v1beta1, which is the latest API version of TiDB Cloud. For more information, refer to the [API documentation (v1beta1)](https://docs.pingcap.com/tidbcloud/api/v1beta1#tag/Billing).
## September 19, 2023

**General changes**

- Remove 2 vCPU TiDB and TiKV nodes from [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.

    The 2 vCPU option is no longer available on the **Create Cluster** page or the **Modify Cluster** page.

- Release [TiDB Cloud serverless driver (beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver) for JavaScript.

    TiDB Cloud serverless driver for JavaScript allows you to connect to your [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) cluster over HTTPS. It is particularly useful in edge environments where TCP connections are limited, such as [Vercel Edge Function](https://vercel.com/docs/functions/edge-functions) and [Cloudflare Workers](https://workers.cloudflare.com/).

    For more information, see [TiDB Cloud serverless driver (beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver).

**Console changes**

- For [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters, you can get an estimation of cost in the **Usage This Month** panel or while setting up the spending limit.
