# TiDB Cloud release notes Oct-Dec 2024

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2024.md`
- Source Title: `TiDB Cloud Release Notes in 2024`
- Source Heading Path: `TiDB Cloud Release Notes in 2024 | TiDB Cloud Release Notes in 2024 > December 17, 2024 | TiDB Cloud Release Notes in 2024 > December 3, 2024 | TiDB Cloud Release Notes in 2024 > November 26, 2024 | TiDB Cloud Release Notes in 2024 > November 19, 2024 | TiDB Cloud Release Notes in 2024 > November 12, 2024 | TiDB Cloud Release Notes in 2024 > October 29, 2024 | TiDB Cloud Release Notes in 2024 > October 22, 2024 | TiDB Cloud Release Notes in 2024 > October 15, 2024`
- Source Line Ranges: `5-100`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `tidb`
- Topic Tags: `release-notes`, `backup-restore`, `serverless`, `dedicated`, `recovery-group`, `disaster-recovery`, `version-upgrade`, `branching`, `github-integration`, `pause-resume`, `datadog`, `aws-regions`, `prometheus`, `changefeed-metrics`, `api-deprecation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0644_27d71d2da3`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2024.md#tidb-cloud-release-notes-in-2024`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `29248694f71d46e9c1c6b75e6f7aae8c5a02b63700ef52eccab9f5a47696d41f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2024#tidb-cloud-release-notes-in-2024
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2024.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB Cloud release changes from October to December 2024, including Serverless backup and restore, Recovery Group, branching, pause behavior, metrics, region changes, default version upgrades, or API deprecation.
- Retrieval Keywords: TiDB Cloud Release Notes in 2024, December 17 2024, December 3 2024, November 26 2024, November 19 2024, November 12 2024, October 29 2024, October 22 2024, October 15 2024, TiDB Cloud Serverless backup and restore, restore to a new cluster, backup retention duration, Recovery Group beta, disaster recovery, TiDB Cloud Dedicated on AWS, v8.1.1, v7.5.4, branch.mode, reset, pause duration limit 7 days, Datadog integration beta AP1 Japan, Mumbai ap-south-1, São Paulo sa-east-1, tidbcloud_changefeed_checkpoint_ts, Prometheus integration, MSP deprecated, Partner Management API
- Follow-up Guidance: The source points to related pages for backup and restore, recovery groups, branch management, GitHub integration, pause or resume, Prometheus metrics, and TiDB Cloud Partner for more detailed information.
- Classification Note: This is a release-notes chunk summarizing TiDB Cloud general and API changes across multiple dated entries in late 2024.

## Official Source Content

# TiDB Cloud Release Notes in 2024

This page lists the release notes of [TiDB Cloud](https://www.pingcap.com/tidb-cloud/) in 2024.
## December 17, 2024

**General changes**

- TiDB Cloud Serverless backup and restore changes

    - Support restoring data to a new cluster, providing greater flexibility and ensuring your current cluster's operations remain uninterrupted.

    - Refine backup and restore strategies to align with your cluster plan. For more information, see [Back Up and Restore TiDB Cloud Serverless Data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore-serverless#learn-about-the-backup-setting).

    - Apply the following compatibility policy to help you transition smoothly:

        - Backups created before 2024-12-17T10:00:00Z will follow the previous retention duration across all clusters.
        - The backup time of scalable clusters will retain the current configurations, while the backup time of free clusters will be reset to default settings.
## December 3, 2024

**General changes**

- Introduce the Recovery Group feature (beta) for disaster recovery of [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters deployed on AWS.

    This feature enables you to replicate your databases between TiDB Cloud Dedicated clusters, ensuring rapid recovery in the event of a regional disaster. If you are in the Project Owner role, you can enable this feature by creating a new recovery group and assigning databases to the group. By replicating databases with recovery groups, you can improve disaster readiness, meet stricter availability SLAs, and achieve more aggressive Recovery Point Objectives (RPO) and Recovery Time Objectives (RTO).
  
    For more information, see [Get started with recovery groups](https://docs.pingcap.com/tidb/stable/tidb-cloud/recovery-group-get-started).
## November 26, 2024

**General changes**

- Upgrade the default TiDB version of new [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v7.5.4](https://docs.pingcap.com/tidb/v7.5/release-7.5.4) to [v8.1.1](https://docs.pingcap.com/tidb/stable/release-8.1.1).

- [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) reduces costs for large data writes by up to 80% for the following scenarios:

    - When you perform write operations larger than 16 MiB in [autocommit mode](https://docs.pingcap.com/tidb/stable/transaction-overview#autocommit).
    - When you perform write operations larger than 16 MiB in [optimistic transaction model](https://docs.pingcap.com/tidb/stable/optimistic-transaction).
    - When you [import data into TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-migration-overview#import-data-from-files-to-tidb-cloud).

  This improvement enhances the efficiency and cost-effectiveness of your data operations, providing greater savings as your workload scales.
## November 19, 2024

**General changes**

- [TiDB Cloud Serverless branching (beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-overview) introduces the following improvements to branch management:

    - **Flexible branch creation**: When creating a branch, you can select a specific cluster or branch as the parent and specify a precise point in time to use from the parent. This gives you precise control over the data in your branch.

    - **Branch reset**: You can reset a branch to synchronize it with the latest state of its parent.

    - **Improved GitHub integration**: The [TiDB Cloud Branching](https://github.com/apps/tidb-cloud-branching) GitHub App introduces the [`branch.mode`](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-github-integration#branchmode) parameter, which controls the behavior during pull request synchronization. In the default mode `reset`, the app resets the branch to match the latest changes in the pull request.

  For more information, see [Manage TiDB Cloud Serverless Branches](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-manage) and [Integrate TiDB Cloud Serverless Branching (Beta) with GitHub](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-github-integration).
## November 12, 2024

**General changes**

- Add the pause duration limit for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.

    TiDB Cloud Dedicated now limits the maximum pause duration to 7 days. If you do not manually resume the cluster within 7 days, TiDB Cloud will automatically resume it.

    This change applies only to **organizations created after November 12, 2024**. Organizations created on or before this date will gradually transition to the new pause behavior with prior notification.

    For more information, see [Pause or Resume a TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/pause-or-resume-tidb-cluster).

- [Datadog integration (beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-datadog-integration) adds support for a new region: `AP1` (Japan).

- Support a new AWS region for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters: `Mumbai (ap-south-1)`.

- Remove support for the AWS `São Paulo (sa-east-1)` region for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.
## October 29, 2024

**General changes**

- New metric: add `tidbcloud_changefeed_checkpoint_ts` for Prometheus integration.

    This metric tracks the checkpoint timestamp of a changefeed, representing the largest TSO (Timestamp Oracle) successfully written to the downstream. For more information on available metrics, see [Integrate TiDB Cloud with Prometheus and Grafana (Beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-prometheus-and-grafana-integration#metrics-available-to-prometheus).
## October 22, 2024

**General changes**

- Upgrade the default TiDB version of new [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v7.5.3](https://docs.pingcap.com/tidb/v7.5/release-7.5.3) to [v7.5.4](https://docs.pingcap.com/tidb/v7.5/release-7.5.4).
## October 15, 2024

**API changes**

* [MSP](https://docs.pingcap.com/tidbcloud/api/v1beta1/msp) is deprecated as of October 15, 2024, and will be removed in the future. If you are currently using the MSP API, migrate to the Partner Management API in [TiDB Cloud Partner](https://partner-console.tidbcloud.com/signin).
