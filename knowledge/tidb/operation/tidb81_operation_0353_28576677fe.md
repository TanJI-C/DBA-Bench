# TiDB Cloud console maintenance window, impact, and affected features

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/notification-2024-09-15-console-maintenance.md`
- Source Title: `2024-09-15 TiDB Cloud Console Maintenance Notification`
- Source Heading Path: `[2024-09-15] TiDB Cloud Console Maintenance Notification | [2024-09-15] TiDB Cloud Console Maintenance Notification > Maintenance window | [2024-09-15] TiDB Cloud Console Maintenance Notification > Reason for maintenance | [2024-09-15] TiDB Cloud Console Maintenance Notification > Impact | [2024-09-15] TiDB Cloud Console Maintenance Notification > Impact > Affected features of TiDB Cloud console UI | [2024-09-15] TiDB Cloud Console Maintenance Notification > Impact > Affected features of TiDB Cloud API | [2024-09-15] TiDB Cloud Console Maintenance Notification > Completion and resumption | [2024-09-15] TiDB Cloud Console Maintenance Notification > Get support`
- Source Line Ranges: `5-92`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `maintenance`, `maintenance-window`, `service-impact`, `console-ui`, `api`, `cluster-management`, `backup`, `restore`, `import`, `changefeed`, `network-access`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0353_28576677fe`
- Source ID: `tidb-docs-8.1:tidb-cloud/notification-2024-09-15-console-maintenance.md#2024-09-15-tidb-cloud-console-maintenance-notification`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3d766d94c487eb271640e54099b57d37c149fc4725ca5a6af9c112adc61adee8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/notification-2024-09-15-console-maintenance#2024-09-15-tidb-cloud-console-maintenance-notification
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/notification-2024-09-15-console-maintenance.md

## Retrieval Guidance

- Use When: Use this when the question is about the TiDB Cloud console maintenance on 2024-09-15, including the maintenance window, intermittent disruptions in create or update operations, and which console UI or API features are affected while cluster read and write remain regular.
- Retrieval Keywords: 2024-09-15 TiDB Cloud Console Maintenance Notification, TiDB Cloud console maintenance window, Start time 8:00 UTC+0, End time 8:10 UTC+0, approximately 10 minutes, intermittent disruptions, creating and updating within the TiDB Cloud console UI and API, TiDB cluster will maintain its regular operations for data read and write, affected features of TiDB Cloud console UI, Cluster management, Create clusters, Delete clusters, Scale clusters, Pause or Resume clusters, Change cluster password, Change cluster traffic filter, Import, Create an import job, Data Migration, Create a migration job, Changefeed, Create a changefeed job, Backup, Create a manual backup job, Auto backup job, Restore, Create a restore Job, Database audit log, Test connectivity, Add or delete access record, Enable or disable Database audit logging, Restart database audit logging, Network access, Create a private endpoint, Delete a private endpoint, Add VPC Peering, Delete VPC Peering, Maintenance, Change maintenance window, Defer task, Recycle Bin, Restore clusters, affected features of TiDB Cloud API, CreateCluster, DeleteCluster, UpdateCluster, CreateAwsCmek, CreateBackup, DeleteBackup, CreateRestoreTask, CreateImportTask, UpdateImportTask, support team
- Follow-up Guidance: The source also states that users cannot modify the maintenance timing for the TiDB Cloud console, some users might experience an additional 20-minute maintenance window during the next 3 months with email notification in advance, and affected functionalities will be reinstated after completion.
- Classification Note: This chunk is classified as an operation topic for the cloud component because it is a TiDB Cloud maintenance notification describing a scheduled maintenance window, service impact, affected console UI and API operations, and support contact information.

## Official Source Content

# [2024-09-15] TiDB Cloud Console Maintenance Notification

This notification describes the details that you need to know about the [TiDB Cloud console](https://tidbcloud.com/) maintenance on September 15, 2024.
## Maintenance window

- Date: 2024-09-15
- Start time: 8:00 (UTC+0)
- End time: 8:10 (UTC+0)
- Duration: Approximately 10 minutes

> **Note:**
>
> - Currently, users cannot modify the maintenance timing for the TiDB Cloud console, so you need to plan accordingly in advance.
> - During the next 3 months, some users might experience an additional 20-minute maintenance window. Affected users will receive an email notification in advance.
## Reason for maintenance

We are upgrading the meta database services of the TiDB Cloud console to enhance performance and efficiency. This improvement aims to provide a better experience for all users as part of our ongoing commitment to delivering high-quality services.
## Impact

During the maintenance window, you might experience intermittent disruptions in functionalities related to creating and updating within the TiDB Cloud console UI and API. However, your TiDB cluster will maintain its regular operations for data read and write, ensuring no adverse effects on your online business.
### Affected features of TiDB Cloud console UI

- Cluster level
    - Cluster management
        - Create clusters
        - Delete clusters
        - Scale clusters
        - Pause or Resume clusters
        - Change cluster password
        - Change cluster traffic filter
    - Import
        - Create an import job
    - Data Migration
        - Create a migration job
    - Changefeed
        - Create a changefeed job
    - Backup
        - Create a manual backup job
        - Auto backup job
    - Restore
        - Create a restore Job
    - Database audit log
        - Test connectivity
        - Add or delete access record
        - Enable or disable Database audit logging
        - Restart database audit logging
- Project level
    - Network access
        - Create a private endpoint
        - Delete a private endpoint
        - Add VPC Peering
        - Delete VPC Peering
    - Maintenance
        - Change maintenance window
        - Defer task
    - Recycle Bin
        - Delete clusters
        - Delete backups
        - Restore clusters
### Affected features of TiDB Cloud API

- Cluster management
    - [CreateCluster](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Cluster/operation/CreateCluster)
    - [DeleteCluster](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Cluster/operation/DeleteCluster)
    - [UpdateCluster](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Cluster/operation/UpdateCluster)
    - [CreateAwsCmek](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Cluster/operation/CreateAwsCmek)
- Backup
    - [CreateBackup](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Backup/operation/CreateBackup)
    - [DeleteBackup](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Backup/operation/DeleteBackup)
- Restore
    - [CreateRestoreTask](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Restore/operation/CreateRestoreTask)
- Import
    - [CreateImportTask](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Import/operation/CreateImportTask)
    - [UpdateImportTask](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Import/operation/UpdateImportTask)
## Completion and resumption

Once the maintenance is successfully completed, the affected functionalities will be reinstated, offering you an even better experience.
## Get support

If you have any questions or need assistance, contact our [support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support). We are here to address your concerns and provide any necessary guidance.
