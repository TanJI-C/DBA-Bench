# TiDB Cloud maintenance window overview, operations, notifications, configuration, and FAQs

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/configure-maintenance-window.md`
- Source Title: `Configure Maintenance Window`
- Source Heading Path: `Configure Maintenance Window | Configure Maintenance Window > Allowed and disallowed operations during a maintenance window | Configure Maintenance Window > Get notifications for maintenance windows | Configure Maintenance Window > View and configure maintenance windows | Configure Maintenance Window > FAQs`
- Source Line Ranges: `5-95`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `maintenance-window`, `scheduled-maintenance`, `allowed-operations`, `disallowed-operations`, `email-notifications`, `project-settings`, `rescheduling`, `deadlines`, `cluster-availability`, `backups`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0214_4f5fa513bb`
- Source ID: `tidb-docs-8.1:tidb-cloud/configure-maintenance-window.md#configure-maintenance-window`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4b590b4a11238a7a17a15b6e0ccdf3e15eb0bad7984fedf8e5990c9b50303ac5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-maintenance-window#configure-maintenance-window
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/configure-maintenance-window.md

## Retrieval Guidance

- Use When: Use this when answering questions about TiDB Cloud Dedicated maintenance windows, including what operations are allowed during maintenance, email notification timing, how to view or change the maintenance window start time, reschedule tasks, default schedule behavior, and FAQ details about availability and backups.
- Retrieval Keywords: Configure Maintenance Window, maintenance window, TiDB Cloud Dedicated clusters, allowed and disallowed operations during a maintenance window, SQL operations, Create clusters, Delete clusters, Create backup tasks, Restore clusters, Access cluster pages, Modify pause or resume clusters, Change security settings in the TiDB Cloud console, Create private links, configure VPC peering, Create import tasks, migration jobs, changefeeds, Get notifications for maintenance windows, Two weeks before, 72 hours before, started, completed, Project Settings > Maintenance, Maintenance Window Setting, Reschedule, deadline, maintenance window is enabled by default and cannot be disabled, 03:00 AM every Wednesday, time zone of your TiDB Cloud organization, temporary connection disruptions, QPS fluctuations, backup restore migration and replication tasks can still run normally, Creating, Paused, automatic or manual backup
- Follow-up Guidance: If a maintenance task must be rescheduled beyond the deadline, the content says to contact TiDB Cloud Support for assistance.
- Classification Note: The classification is configuration because the content explains how to view and configure the maintenance window in the TiDB Cloud console, including changing the start time and rescheduling maintenance tasks.

## Official Source Content

# Configure Maintenance Window

A maintenance window is a designated timeframe during which planned maintenance tasks, such as operating system updates, security patches, and infrastructure upgrades, are performed automatically to ensure the reliability, security, and performance of the TiDB Cloud service.

During a maintenance window, the maintenance is executed on TiDB Cloud Dedicated clusters one by one so the overall impact is minimal. Although there might be temporary connection disruptions or QPS fluctuations, the clusters remain available, and the existing data import, backup, restore, migration, and replication tasks can still run normally.

By configuring the maintenance window, you can easily schedule and manage maintenance tasks to minimize the maintenance impact. For example, you can set the start time of the maintenance window to avoid peak hours of your application workloads.

> **Note:**
>
> The maintenance window feature is only available for [TiDB Cloud Dedicated clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).
## Allowed and disallowed operations during a maintenance window

During a maintenance window, some operations are allowed, while some are not.

- Allowed operations:

    - SQL operations
    - Create clusters
    - Delete clusters
    - Create backup tasks
    - Restore clusters
    - Access cluster pages

- Disallowed operations:

    - Modify, pause, or resume clusters
    - Change security settings in the TiDB Cloud console
    - Create private links or configure VPC peering
    - Create import tasks, migration jobs, or changefeeds
    - Scale specifications of migration jobs or changefeeds
## Get notifications for maintenance windows

To avoid potential disruptions, it is important to be aware of the maintenance schedules and plan your operations accordingly.

For every maintenance window, TiDB Cloud sends four email notifications to all project members at the following time points:

- Two weeks before a maintenance window starts (excluding urgent maintenance tasks)
- 72 hours before a maintenance window starts
- The time when a maintenance window is started
- The time when a maintenance window is completed
## View and configure maintenance windows

Regular maintenance ensures that essential updates are performed to safeguard TiDB Cloud from security threats, performance issues, and unreliability. Therefore, the maintenance window is enabled by default and cannot be disabled.

> **Note:**
>
> - For the default project automatically created when you first sign up for TiDB Cloud, the maintenance window starts at 03:00 AM every Wednesday (based on the time zone of your TiDB Cloud organization).
> - For new projects that you create, you can set a custom start time for the maintenance window during project setup.

You can modify the start time to your preferred time or reschedule maintenance tasks until the deadline as follows:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Maintenance**.
3. On the **Maintenance** page, check the maintenance information.

     - If any maintenance tasks are displayed, check the descriptions, scheduled start time, and deadline. The maintenance tasks will start at the designated time.

     - If there is no maintenance data, it means no maintenance task is scheduled recently.

4. (Optional) Click **Maintenance Window Setting** to modify the start time of the maintenance window. Note that the maintenance will be performed at the specified start time only if there is a maintenance window planned for that week.

5. To reschedule a specific maintenance task, click **...** > **Reschedule** in the **Action** column, and choose a new time before the deadline.

    If you need to reschedule the maintenance task beyond the deadline, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support#tidb-cloud-support) for assistance.
## FAQs

- What are maintenance tasks?

    Maintenance tasks typically include operating system updates, security patches, and infrastructure upgrades.

- Can I disable a maintenance window?

    No. The maintenance window is enabled by default and cannot be disabled. You can modify the start time of the maintenance window or reschedule a maintenance task until the deadline. For more information, see [View and configure maintenance windows](#view-and-configure-maintenance-windows).

- How long does a maintenance window last?

    It depends. For each project, maintenance is executed on eligible TiDB clusters one by one. The duration of maintenance varies depending on the number of clusters, cluster data size, and the maintenance tasks to be performed.

- Will maintenance tasks be performed on clusters in any status?

    No. TiDB Cloud checks the cluster status before performing a maintenance task on a cluster.

    - If the cluster is in the **Creating** or **Paused** status, maintenance tasks are not required.
    - If the cluster is running an automatic or manual backup, the maintenance will be delayed and triggered until the current backup is successfully completed. Note that for clusters with large data volumes, the backup process might take a long time, such as 12 hours. To minimize the impact on the clusters, it is recommended to carefully set the start time for backups and the maintenance window.
    - If the cluster is in any other status, the maintenance tasks will start as scheduled.
