# TiDB Cloud console maintenance window and affected features on 2023-08-31

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/notification-2023-08-31-console-maintenance.md`
- Source Title: `2023-08-31 TiDB Cloud Console Maintenance Notification`
- Source Heading Path: `[2023-08-31] TiDB Cloud Console Maintenance Notification | [2023-08-31] TiDB Cloud Console Maintenance Notification > Maintenance window | [2023-08-31] TiDB Cloud Console Maintenance Notification > Reason for maintenance | [2023-08-31] TiDB Cloud Console Maintenance Notification > Impact | [2023-08-31] TiDB Cloud Console Maintenance Notification > Impact > Affected features of TiDB Cloud console UI | [2023-08-31] TiDB Cloud Console Maintenance Notification > Impact > Affected features of TiDB Cloud API | [2023-08-31] TiDB Cloud Console Maintenance Notification > Completion and resumption | [2023-08-31] TiDB Cloud Console Maintenance Notification > Get support`
- Source Line Ranges: `5-91`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `maintenance`, `maintenance-window`, `service-impact`, `console-ui`, `api`, `cluster-management`, `backup`, `restore`, `import`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0351_51e4ebd991`
- Source ID: `tidb-docs-8.1:tidb-cloud/notification-2023-08-31-console-maintenance.md#2023-08-31-tidb-cloud-console-maintenance-notification`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0e8f6de26218de42bc29196d9d6a80d163c240beed32aa0ef17897c60df2981e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/notification-2023-08-31-console-maintenance#2023-08-31-tidb-cloud-console-maintenance-notification
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/notification-2023-08-31-console-maintenance.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about the TiDB Cloud console maintenance on 2023-08-31, including the maintenance window, the reason for maintenance, and which console UI or API create and update features might be intermittently disrupted.
- Retrieval Keywords: 2023-08-31 TiDB Cloud Console Maintenance Notification, TiDB Cloud console maintenance, maintenance window 8:00 10:00 UTC+0, approximately 2 hours, upgrading the meta database services, intermittent disruptions, creating and updating within the TiDB Cloud console UI and API, cluster regular operations for data read and write, CreateCluster, DeleteCluster, UpdateCluster, CreateAwsCmek, CreateBackup, DeleteBackup, CreateRestoreTask, CreateImportTask, UpdateImportTask, cluster management, backup, restore, import, network access, maintenance window, recycle bin, database audit log, support team
- Follow-up Guidance: If users have questions or need assistance, the source says to contact the support team, and it states that affected functionalities will be reinstated once the maintenance is successfully completed.
- Classification Note: This is classified as a cloud operation notification because the content announces a TiDB Cloud console maintenance window and describes its service impact on console UI and API features.

## Official Source Content

# [2023-08-31] TiDB Cloud Console Maintenance Notification

This notification describes the details that you need to know about the [TiDB Cloud console](https://tidbcloud.com/) maintenance on August 31, 2023.
## Maintenance window

- Date: 2023-08-31
- Start time: 8:00 (UTC+0)
- End time: 10:00 (UTC+0)
- Duration: Approximately 2 hours

> **Note:**
>
> Currently, users cannot modify the maintenance timing for the TiDB Cloud console, so you need to plan accordingly in advance.
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
