# January 2025 TiDB Cloud release updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-release-notes.md`
- Source Title: `TiDB Cloud Release Notes in 2025`
- Source Heading Path: `TiDB Cloud Release Notes in 2025 > January 14, 2025 | TiDB Cloud Release Notes in 2025 > January 2, 2025`
- Source Line Ranges: `273-347`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `pd`, `tikv`, `ticdc`, `tidb`
- Topic Tags: `release-notes`, `aws-region`, `notifications`, `node-groups`, `private-connect`, `kafka`, `changefeed`, `debezium`, `dispatcher`, `iam-roles`, `serverless`, `high-availability`, `version-upgrade`, `data-export`, `parquet`, `gcs`, `azure-blob`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0652_8a54b420f8`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-release-notes.md#january-14-2025`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `666181dc2cab5afa4d6be35193edc1a10eadf00b9622c5ce3a90736f88dbe6d2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-release-notes#january-14-2025
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-release-notes.md

## Retrieval Guidance

- Use When: Use this chunk when looking for January 2025 TiDB Cloud release-note details about new cloud regions, notifications, TiDB node groups, Private Connect for Kafka, Kafka changefeed options, IAM role changes, Serverless high availability, default version updates, or Serverless data export enhancements.
- Retrieval Keywords: January 14 2025, January 2 2025, TiDB Cloud release notes 2025, Jakarta (ap-southeast-3), Notification feature, TiDB Cloud console, TiDB node groups, Overview of TiDB Node Group, Private Connect (beta), Private Link, Private Service Connect, generic Kafka in AWS and Google Cloud, changefeed sink to Apache Kafka, Private Data Link costs, Debezium protocol, TiCDC Debezium Protocol, single partition dispatcher, different partition dispatchers for different tables, timestamp dispatcher, column value dispatcher, Project Viewer, Organization Billing Viewer, Organization Member, Organization Viewer, Organization Billing Admin, Organization Billing Manager, Organization Console Audit Admin, Organization Console Audit Manager, Identity Access Management, regional high availability (beta), TiDB Cloud Serverless, AWS Tokyo (ap-northeast-1), PD and TiKV, automatic failover, default TiDB version, v8.1.1, v8.1.2, data export service, Google Cloud Storage, Azure Blob Storage, Parquet files, Export Data from TiDB Cloud Serverless, Configure External Storage Access for TiDB Cloud Serverless
- Follow-up Guidance: The source points to related documentation for Notifications, TiDB Node Group, Kafka Private Link or Private Service Connect setup, Changefeed Sink to Apache Kafka, Identity Access Management, High Availability in TiDB Cloud Serverless, and Serverless export and external storage configuration.
- Classification Note: This chunk is classified as a cloud release note because it summarizes dated TiDB Cloud feature, availability, role, version, and console changes announced on January 14 and January 2, 2025.

## Official Source Content

## January 14, 2025

**General changes**

- Support a new AWS region for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters: `Jakarta (ap-southeast-3)`.

- Introduce the Notification feature, which enables you to stay informed instantly with TiDB Cloud updates and alerts through the [TiDB Cloud console](https://tidbcloud.com/).

    For more information, see [Notifications](https://docs.pingcap.com/tidb/stable/tidb-cloud/notifications).
## January 2, 2025

**General changes**

- Support creating TiDB node groups for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters to enhance resource management flexibility. 

    For more information, see [Overview of TiDB Node Group](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-node-group-overview).

- Support connecting [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters to generic Kafka in AWS and Google Cloud through Private Connect (beta).

    Private Connect leverages Private Link or Private Service Connect technologies from cloud providers to enable changefeeds in the TiDB Cloud VPC to connect to Kafka in customers' VPCs using private IP addresses, as if those Kafkas were hosted directly within the TiDB Cloud VPC. This feature helps prevent VPC CIDR conflicts and meets security compliance requirements.

    - For Apache Kafka in AWS, follow the instructions in [Set Up Self-Hosted Kafka Private Link Service in AWS](https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service) to configure the network connection.

    - For Apache Kafka in Google Cloud, follow the instructions in [Set Up Self-Hosted Kafka Private Service Connect in Google Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-self-hosted-kafka-private-service-connect) to configure the network connection.
  
  Note that using this feature incurs additional [Private Data Link costs](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing-ticdc-rcu#private-data-link-cost).

    For more information, see [Changefeed Sink to Apache Kafka](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka#network).

- Introduce additional configurable options for Kafka changefeeds:

    - Support using the Debezium protocol. Debezium is a tool for capturing database changes. It converts each captured database change into a message called an event, and sends these events to Kafka. For more information, see [TiCDC Debezium Protocol](https://docs.pingcap.com/tidb/v8.1/ticdc-debezium).

    - Support defining a single partition dispatcher for all tables, or different partition dispatchers for different tables. 

    - Introduce two new dispatcher types for the partition distribution of Kafka messages: timestamp and column value.

  For more information, see [Sink to Apache Kafka](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka).

- Enhance roles in TiDB Cloud:

    - Introduce the `Project Viewer` and `Organization Billing Viewer` roles to enhance granular access control on TiDB Cloud.

    - Rename the following roles:

        - `Organization Member` to `Organization Viewer`
        - `Organization Billing Admin` to `Organization Billing Manager`
        - `Organization Console Audit Admin` to `Organization Console Audit Manager`

  For more information, see [Identity Access Management](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#organization-roles).

- Regional high availability (beta) for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

    This feature is designed for workloads that require maximum infrastructure redundancy and business continuity. Key functions include:

    - Nodes are distributed across multiple availability zones to ensure high availability in the event of a zone failure.
    - Critical OLTP (Online Transactional Processing) components, such as PD and TiKV, are replicated across availability zones for redundancy.
    - Automatic failover minimizes service disruption during a primary zone failure.
  
  This feature is currently available only in the AWS Tokyo (ap-northeast-1) region and can be enabled only during cluster creation.
  
    For more information, see [High Availability in TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-high-availability).

- Upgrade the default TiDB version of new [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v8.1.1](https://docs.pingcap.com/tidb/v8.1/release-8.1.1) to [v8.1.2](https://docs.pingcap.com/tidb/v8.1/release-8.1.2).

**Console changes**

- Strengthen the data export service:

    - Support exporting data from [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) to Google Cloud Storage and Azure Blob Storage through the [TiDB Cloud console](https://tidbcloud.com/).

    - Support exporting data in Parquet files through the [TiDB Cloud console](https://tidbcloud.com/).

  For more information, see [Export Data from TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-export) and [Configure External Storage Access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage).
