# TiDB Cloud DM maintenance window and impact notification

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/notification-2024-04-11-dm-feature-maintenance.md`
- Source Title: `2024-04-11 TiDB Cloud Data Migration (DM) Feature Maintenance Notification`
- Source Heading Path: `[2024-04-11] TiDB Cloud Data Migration (DM) Feature Maintenance Notification | [2024-04-11] TiDB Cloud Data Migration (DM) Feature Maintenance Notification > Maintenance window | [2024-04-11] TiDB Cloud Data Migration (DM) Feature Maintenance Notification > Impact | [2024-04-11] TiDB Cloud Data Migration (DM) Feature Maintenance Notification > Completion and resumption | [2024-04-11] TiDB Cloud Data Migration (DM) Feature Maintenance Notification > Get support`
- Source Line Ranges: `5-49`
- Source Scope: `cloud`
- Primary Component: `dm`
- Related Components: `cloud`
- Topic Tags: `maintenance`, `notification`, `maintenance-window`, `service-impact`, `regional-availability`, `task-interruption`, `task-resumption`, `full-data-migration`, `incremental-migration`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0627_bf1532711e`
- Source ID: `tidb-docs-8.1:tidb-cloud/notification-2024-04-11-dm-feature-maintenance.md#2024-04-11-tidb-cloud-data-migration-dm-feature-maintenance-notification`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dfe5b3adf831bdbc52f2f8d91d9d892d06071ed175f4981f442e49f3fb8ec7a6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/notification-2024-04-11-dm-feature-maintenance#2024-04-11-tidb-cloud-data-migration-dm-feature-maintenance-notification
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/notification-2024-04-11-dm-feature-maintenance.md

## Retrieval Guidance

- Use When: Use this when looking for the April 11, 2024 TiDB Cloud Data Migration (DM) maintenance window, affected regions, and service impact details for TiDB Cloud Dedicated.
- Retrieval Keywords: [2024-04-11] TiDB Cloud Data Migration (DM) Feature Maintenance Notification, TiDB Cloud Dedicated, Data Migration (DM) feature, maintenance window, 2024-04-11 08:00 (UTC+0), 2024-04-11 09:00 (UTC+0), AWS us-west-2, AWS us-east-1, AWS ap-southeast-1, AWS ap-northeast-2, AWS eu-central-1, AWS sa-east-1, Google Cloud us-west1, Google Cloud asia-northeast1, Google Cloud asia-southeast1, DM console unavailable for up to 30 minutes, incremental migration interrupted for up to 30 minutes, do not purge the binary log of the MySQL database, exporting and importing full data, cannot be resumed after the upgrade, support team
- Follow-up Guidance: The source also states that after maintenance the affected functionalities will be reinstated, and users with questions can contact the support team.
- Classification Note: This is a release notification because the official content announces a scheduled maintenance event for the TiDB Cloud DM feature, including timing, impacted regions, and expected service effects.

## Official Source Content

# [2024-04-11] TiDB Cloud Data Migration (DM) Feature Maintenance Notification

This notification describes the details that you need to know about the maintenance for [Data Migration (DM) feature](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration) of TiDB Cloud Dedicated on April 11, 2024.
## Maintenance window

- Start time: 2024-04-11 08:00 (UTC+0)
- End time: 2024-04-11 09:00 (UTC+0)
- Duration: 1 hour
## Impact

During the maintenance window, the DM feature for TiDB Cloud Dedicated clusters in the following regions will be affected:

- Cloud provider: AWS, region: Oregon (us-west-2)
- Cloud provider: AWS, region: N. Virginia (us-east-1)
- Cloud provider: AWS, region: Singapore (ap-southeast-1)
- Cloud provider: AWS, region: Seoul (ap-northeast-2)
- Cloud provider: AWS, region: Frankfurt (eu-central-1)
- Cloud provider: AWS, region: São Paulo (sa-east-1)
- Cloud provider: AWS, region: Oregon (us-west-2)
- Cloud provider: Google Cloud, region: Oregon (us-west1)
- Cloud provider: Google Cloud, region: Tokyo (asia-northeast1)
- Cloud provider: Google Cloud, region: Singapore (asia-southeast1)

The maintenance only affects the DM feature in the TiDB cluster. All the other functionalities remain unaffected. You can continue to manage the TiDB cluster and perform read/write operations or other operations as usual.

For clusters deployed on AWS:

- During the upgrade, the DM tasks can keep running without disruption. The DM console can be used normally.

For clusters deployed on Google Cloud:

- The DM console will be unavailable for up to 30 minutes. During this period, you cannot create or manage DM tasks.
- If a DM task is in the incremental migration stage, it will be interrupted for up to 30 minutes. During this period, do not purge the binary log of the MySQL database. The DM task will automatically resume after the upgrade is completed.
- If a DM task is in the stage of exporting and importing full data, it will fail during the upgrade, and cannot be resumed after the upgrade. It is recommended not to create any DM task on the day when the upgrade is performed, to ensure that no DM tasks are in the stage of exporting and importing full data when the upgrade starts.
## Completion and resumption

Once the maintenance is successfully completed, the affected functionalities will be reinstated, offering you a better experience.
## Get support

If you have any questions or need assistance, contact our [support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support). We are here to address your concerns and provide any necessary guidance.
