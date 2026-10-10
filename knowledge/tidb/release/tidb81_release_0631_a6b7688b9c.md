# TiDB Cloud release notes from November to December 2022

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2022.md`
- Source Title: `TiDB Cloud Release Notes in 2022`
- Source Heading Path: `TiDB Cloud Release Notes in 2022 | TiDB Cloud Release Notes in 2022 > December 28, 2022 | TiDB Cloud Release Notes in 2022 > December 27, 2022 | TiDB Cloud Release Notes in 2022 > December 20, 2022 | TiDB Cloud Release Notes in 2022 > December 13, 2022 | TiDB Cloud Release Notes in 2022 > December 6, 2022 | TiDB Cloud Release Notes in 2022 > November 29, 2022 | TiDB Cloud Release Notes in 2022 > November 22, 2022 | TiDB Cloud Release Notes in 2022 > November 15, 2022 | TiDB Cloud Release Notes in 2022 > November 8, 2022`
- Source Line Ranges: `5-167`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `ticdc`, `dm`, `tikv`, `shared`
- Topic Tags: `release-notes`, `serverless`, `dedicated`, `version-upgrade`, `pitr`, `changefeed`, `data-migration`, `sql-editor`, `datadog`, `audit-logging`, `marketplace`, `billing`, `console`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0631_a6b7688b9c`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2022.md#tidb-cloud-release-notes-in-2022`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7f5868e05d64e5e3387aea46e557002d01b27521e473ea8734c14e6253a1911c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2022#tidb-cloud-release-notes-in-2022
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2022.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud release-note changes from November to December 2022 across Serverless Tier, Dedicated Tier, PITR, Changefeeds, Data Migration, SQL Editor, Datadog, audit logging, Marketplace billing, and console updates.
- Retrieval Keywords: TiDB Cloud Release Notes in 2022, December 28, 2022, December 27, 2022, December 20, 2022, December 13, 2022, December 6, 2022, November 29, 2022, November 22, 2022, November 15, 2022, November 8, 2022, Serverless Tier, Dedicated Tier, v6.3.0, v6.4.0, v6.1.2, v6.1.3, point-in-time recovery, PITR, Backup Settings, changefeeds, edit a changefeed, up to 10 changefeeds, Data Migration, Amazon Aurora MySQL, Amazon RDS MySQL, self-hosted MySQL-compatible databases, Import local CSV files to TiDB Cloud, Datadog Dashboard, project name, TiDB Cloud SQL Editor, Web SQL Shell, streaming data change logs to MySQL, streaming data change logs to Apache Kafka, Organization Settings, Connect experience, AWS Marketplace, Google Cloud Marketplace, database audit logging, Give Feedback
- Follow-up Guidance: The content points to related documentation such as Back up and restore TiDB cluster data, Changefeed Overview, Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration, Import local files to TiDB Cloud, Datadog integration, and Database Audit Logging for more details.
- Classification Note: This chunk is classified as a TiDB Cloud release note because it is a dated summary of cloud feature launches, GA and beta status changes, default version upgrades and rollbacks, and console or billing updates.

## Official Source Content

# TiDB Cloud Release Notes in 2022

This page lists the release notes of [TiDB Cloud](https://www.pingcap.com/tidb-cloud/) in 2022.
## December 28, 2022

**General changes**

- Currently, after upgrading the default TiDB version of all [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters from [v6.3.0](https://docs-archive.pingcap.com/tidb/v6.3/release-6.3.0) to [v6.4.0](https://docs-archive.pingcap.com/tidb/v6.4/release-6.4.0), the cold start becomes slower in certain circumstances. So we roll back the default TiDB version of all Serverless Tier clusters from v6.4.0 to v6.3.0, then fix the problem as soon as possible, and upgrade it later again.
## December 27, 2022

**General changes**

- Upgrade the default TiDB version of all [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters from [v6.3.0](https://docs-archive.pingcap.com/tidb/v6.3/release-6.3.0) to [v6.4.0](https://docs-archive.pingcap.com/tidb/v6.4/release-6.4.0).

- The point-in-time recovery (PITR) for Dedicated Tier clusters is now in General Availability (GA).

    PITR supports restoring data of any point in time to a new cluster. To use the PITR feature, make sure that your TiDB cluster version is at least v6.4.0 and the TiKV node size is at least 8 vCPU and 16 GiB.

    You can enable or disable the PITR feature in the **Backup Settings** of the [TiDB Cloud console](https://tidbcloud.com).

    For more information, see [Back up and restore TiDB cluster data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore).

- Support managing multiple changefeeds and editing existing changefeeds.

    - You can now create as many changefeeds as needed to manage different data replication tasks. Currently, each cluster can have up to 10 changefeeds. For more details, refer to [Changefeed overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview).
    - You can edit the configuration of an existing changefeed in the paused status. For more information, see [Edit a changefeed](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview#edit-a-changefeed).

- Support directly migrating data from Amazon Aurora MySQL, Amazon Relational Database Service (RDS) MySQL, or self-hosted MySQL-compatible databases to TiDB Cloud online. This feature is now in General Availability.

    - Provide services in the following 6 regions:
        - AWS Oregon (us-west-2)
        - AWS N. Virginia (us-east-1)
        - AWS Mumbai (ap-south-1)
        - AWS Singapore (ap-southeast-1)
        - AWS Tokyo (ap-northeast-1)
        - AWS Frankfurt (eu-central-1)
    - Support multiple specifications. You can choose an appropriate specification according to the required performance to achieve optimal data migration experience.

  For how to migrate data to TiDB Cloud, refer to [user documentation](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration). For billing details, refer to [Data Migration billing](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing-dm).

- Support importing local CSV files to TiDB Cloud.

    It only takes a few clicks to complete the task configuration, and then your local CSV data can be quickly imported into your TiDB cluster. When using this method, you do not need to provide the cloud storage bucket path and Role ARN. The whole importing process is quick and smooth.

    For more information, see [Import local files to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-import-local-files).
## December 20, 2022

**General changes**

- Add the label `project name` to the [Datadog](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-datadog-integration) Dashboard as a filter to provide project information.

    You can use the filter `project name` to quickly find the cluster you want.
## December 13, 2022

**General changes**

- Introduce TiDB Cloud SQL Editor (Beta) for Serverless Tier.

    This is a web-based SQL editor that allows you to directly edit and run SQL queries against databases of Serverless Tier. You can locate it easily in the left navigation bar of your Serverless Tier cluster.

    For Serverless Tier, the Web SQL Shell is replaced by the SQL Editor.

- Support using [Changefeeds](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview) to stream data for Dedicated Tier.

    - Support [streaming data change logs to MySQL](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-mysql).

      When data is migrated from MySQL/Aurora to TiDB, it is often necessary to use MySQL as a stand-by database to prevent unexpected data migration problems. In this case, you can use MySQL sink to stream data from TiDB to MySQL.

    - Support [streaming data change logs to Apache Kafka](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka) (Beta).

      Streaming TiDB data to the message queue is a very common requirement for data integration scenarios. You can use Kafka sink to realize integration with other data processing systems (such as Snowflake), or support business consuming.

    For more information, refer to [Changefeed Overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview).

- Organization owners can edit the organization's name in **Organization Settings**.

**Console changes**

- Optimize the navigation layout of the [TiDB Cloud console](https://tidbcloud.com) to provide users with a new navigation experience.

    The new layout includes the following changes:

    - Introduce the left navigation bar to maximize screen usage efficiency.
    - Adopt a flatter navigation hierarchy.

- Improve the [**Connect**](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-to-tidb-cluster-serverless) experience for Serverless Tier users.

    Now developers can connect to SQL editor or with their preferred tools in just a few clicks without context switching.
## December 6, 2022

**General changes**

- Upgrade the default TiDB version of new [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v6.1.2](https://docs.pingcap.com/tidb/stable/release-6.1.2) to [v6.1.3](https://docs.pingcap.com/tidb/stable/release-6.1.3).
## November 29, 2022

**General changes**

- Improve the user experience from AWS Marketplace and Google Cloud Marketplace.

    No matter whether you are new to TiDB Cloud or you already have a TiDB Cloud account, now you can link with your AWS or GCP billing account, which makes it easier to complete AWS or GCP Marketplace subscriptions.

    For how to make the link, see [Billing from AWS Marketplace or Google Cloud Marketplace](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#billing-from-aws-marketplace-azure-marketplace-or-google-cloud-marketplace).
## November 22, 2022

**General changes**

* Support directly migrating data from Amazon Aurora MySQL, Amazon Relational Database Service (RDS) MySQL, or self-hosted MySQL-compatible databases to TiDB Cloud online (beta).

    Previously, you needed to pause your business and import data offline, or use third-party tools to migrate data to TiDB Cloud, which was complicated. Now, with the **Data Migration** feature, you only need to perform operations on your TiDB Cloud console and securely migrate your data to TiDB Cloud with minimal downtime.

    In addition, Data Migration provides full and incremental data migration capabilities to migrate both existing data and ongoing changes from your data source to TiDB Cloud.

    Currently, the Data Migration feature is still **in beta**. It is available only for [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters and only in the AWS Oregon (us-west-2) and AWS Singapore (ap-southeast-1) regions. You can create one migration job for free for each organization. To create multiple migration jobs for an organization, you need to [file a ticket](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).

    For detailed information, see [Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration).
## November 15, 2022

**General changes**

* Support point-in-time recovery (PITR) for [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters (beta).

    PITR supports restoring data of any point in time to a new cluster. You can use it to:

    * Reduce RPO in disaster recovery.
    * Resolve data write errors by restoring point-in-time that is before the error event.
    * Audit the historical data of the business.

  To use the PITR feature, make sure that your TiDB cluster version is at least v6.3.0 and the TiKV node size is at least 8 vCPU and 16 GiB.

  By default, backup data is stored in the same region where the cluster is created. In Japan, for TiDB clusters hosted on GCP with PITR enabled, you can choose to store backup data in one or two regions (Tokyo and/or Osaka). Restoring data from an alternative region provides a higher level of data safety and can tolerate region failures.

  For more information, see [Back Up and Restore TiDB Cluster Data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore).

  This feature is still in beta and only available upon request:

    * Click **Help** in the lower-right corner of TiDB Cloud console.
    * In the dialog, fill in "Apply for PITR" in the **Description** field and click **Send**.

* The database audit logging feature is now GA.

    You can use database audit logging to record a history of user access details (such as any SQL statements executed) in logs and conduct a periodic analysis of the database audit logs, which helps keep your database secure.

    For more information, see [Database Audit Logging](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-auditing).
## November 8, 2022

**General changes**

* Improve the user feedback channel.

    Now you can request a demo or credits in **Support** > **Give Feedback** in the TiDB Cloud console. This can be helpful if you want to learn more about TiDB Cloud.

    After receiving your request, we will contact you to provide help as soon as possible.
