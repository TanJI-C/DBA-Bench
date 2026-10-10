# TiDB Cloud Dedicated scale feature maintenance notification and impact

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/notification-2023-11-14-scale-feature-maintenance.md`
- Source Title: `2023-11-14 TiDB Cloud Dedicated Scale Feature Maintenance Notification`
- Source Heading Path: `[2023-11-14] TiDB Cloud Dedicated Scale Feature Maintenance Notification | [2023-11-14] TiDB Cloud Dedicated Scale Feature Maintenance Notification > Maintenance window | [2023-11-14] TiDB Cloud Dedicated Scale Feature Maintenance Notification > Impact | [2023-11-14] TiDB Cloud Dedicated Scale Feature Maintenance Notification > Impact > Affected features of TiDB Cloud console UI | [2023-11-14] TiDB Cloud Dedicated Scale Feature Maintenance Notification > Impact > Affected features of TiDB Cloud API | [2023-11-14] TiDB Cloud Dedicated Scale Feature Maintenance Notification > Completion and resumption | [2023-11-14] TiDB Cloud Dedicated Scale Feature Maintenance Notification > Get support`
- Source Line Ranges: `5-42`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `maintenance-window`, `scale-feature`, `vcpu`, `ram`, `cluster-management`, `api`, `console-ui`, `service-impact`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0626_a5dd0c40d7`
- Source ID: `tidb-docs-8.1:tidb-cloud/notification-2023-11-14-scale-feature-maintenance.md#2023-11-14-tidb-cloud-dedicated-scale-feature-maintenance-notification`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `45861d24ddfcb75ffb896bcdcc98017745cdc25f96c3a1b47a73f9ed5a26ad6c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/notification-2023-11-14-scale-feature-maintenance#2023-11-14-tidb-cloud-dedicated-scale-feature-maintenance-notification
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/notification-2023-11-14-scale-feature-maintenance.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about the November 14, 2023 TiDB Cloud Dedicated Scale feature maintenance window and which scaling operations were unavailable in the console UI or API.
- Retrieval Keywords: 2023-11-14 TiDB Cloud Dedicated Scale Feature Maintenance Notification, maintenance window 2023-11-14 16:00 UTC+0 to 2023-11-21 16:00 UTC+0, scale feature maintenance, change vCPU and RAM is disabled, Dedicated Clusters, Modify Cluster page, change node number or storage, TiDB Cloud console UI, Modify clusters, Change the vCPU and RAM of TiDB TiKV or TiFlash nodes, TiDB Cloud API, UpdateCluster, regular operations for data read and write, support team
- Follow-up Guidance: The source states that once the maintenance is successfully completed, the affected functionalities will be reinstated, and users with questions or needing assistance can contact the support team.
- Classification Note: This is classified as a release notification because the official content announces a dated maintenance window, describes service impact, lists affected console UI and API features, and notes completion and support details for TiDB Cloud Dedicated.

## Official Source Content

# [2023-11-14] TiDB Cloud Dedicated Scale Feature Maintenance Notification

This notification describes the details that you need to know about the maintenance for [Scale feature](https://docs.pingcap.com/tidbcloud/scale-tidb-cluster#scale-your-tidb-cluster) of TiDB Cloud Dedicated on November 14, 2023.
## Maintenance window

- Start time: 2023-11-14 16:00 (UTC+0)
- End time: 2023-11-21 16:00 (UTC+0)
- Duration: 7 days

> **Note:**
>
> Updated on 2023-11-16: The end time of the maintenance window has been extended from 2023-11-16 to 2023-11-21.
## Impact

During the maintenance window, [change vCPU and RAM](https://docs.pingcap.com/tidbcloud/scale-tidb-cluster#change-vcpu-and-ram) is disabled and you can not change vCPU and RAM for your Dedicated Clusters. However, you can still change the node number or storage in the Modify Cluster page. Your TiDB cluster will maintain its regular operations for data read and write, ensuring no adverse effects on your online business.
### Affected features of TiDB Cloud console UI

- Cluster level
    - Cluster management
        - Modify clusters
            - Change the vCPU and RAM of TiDB, TiKV, or TiFlash nodes.
 
### Affected features of TiDB Cloud API

- Cluster management
    - [UpdateCluster](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Cluster/operation/UpdateCluster)
## Completion and resumption

Once the maintenance is successfully completed, the affected functionalities will be reinstated, offering you an even better experience.
## Get support

If you have any questions or need assistance, contact our [support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support). We are here to address your concerns and provide any necessary guidance.
