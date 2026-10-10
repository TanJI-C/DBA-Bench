# View backup page and enable auto backup with PITR scheduling

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/backup-and-restore.md`
- Source Title: `Back Up and Restore TiDB Cloud Dedicated Data`
- Source Heading Path: `Back Up and Restore TiDB Cloud Dedicated Data > Backup | Back Up and Restore TiDB Cloud Dedicated Data > Backup > View the Backup page | Back Up and Restore TiDB Cloud Dedicated Data > Backup > Turn on auto backup | Back Up and Restore TiDB Cloud Dedicated Data > Backup > Turn on auto backup > Turn on Point-in-time Restore | Back Up and Restore TiDB Cloud Dedicated Data > Backup > Turn on auto backup > Configure backup schedule`
- Source Line Ranges: `23-104`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `br`
- Topic Tags: `backup`, `auto-backup`, `pitr`, `backup-schedule`, `retention`, `manual-backup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0283_7a5fed0ae5`
- Source ID: `tidb-docs-8.1:tidb-cloud/backup-and-restore.md#backup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8c695be95b9bec6a8c6df703a687931dfb1f7dfa7dcd3a8ed46f652fd3d34d77`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#backup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/backup-and-restore.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud Dedicated Backup page path or wants the documented steps and notes for enabling Auto Backup, Point-in-time Restore, backup schedule, backup time, or backup retention.
- Retrieval Keywords: Clusters page, Data > Backup, Backup page, Backup Setting, Auto Backup, Point-in-time Restore, v6.4.0 or later, snapshot backup, log backup, manual backup, Daily Backup, Weekly Backup, Backup Cycle, Backup Time, Backup Retention, 2:00 AM, backup jobs are automatically delayed when data import jobs are in progress, DO NOT run manual backups during data import or cluster scaling, recycle bin
- Follow-up Guidance: The content notes that Point-in-Time Restore only takes effect after the next backup task is completed, and weekly backup enables Point-in-time Restore by default and it cannot be disabled.
- Classification Note: This is operation content because it gives navigation and step-by-step UI procedures for viewing Backup settings and configuring automatic backup behavior.

## Official Source Content

## Backup
### View the Backup page

1. On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target cluster to go to its overview page.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. In the left navigation pane, click **Data** > **Backup**.
### Turn on auto backup

TiDB Cloud Dedicated supports both [snapshot backup](https://docs.pingcap.com/tidb/stable/br-snapshot-guide) and [log backup](https://docs.pingcap.com/tidb/stable/br-pitr-guide). Snapshot backup enables you to restore data to the backup point. By default, snapshot backups are taken automatically and stored according to your backup retention policy. You can disable auto backup at any time.
#### Turn on Point-in-time Restore

> **Note**
>
> The Point-in-time Restore feature is supported for TiDB Cloud Dedicated clusters that are v6.4.0 or later.

This feature supports restoring data of any point in time to a new cluster. You can use it to:

- Reduce RPO in disaster recovery.
- Resolve cases of data write errors by restoring point-in-time that is before the error event.
- Audit the historical data of the business.

It is strongly recommended to turn on this feature. The cost is the same as snapshot backup. For more information, refer to [Data Backup Cost](https://www.pingcap.com/tidb-dedicated-pricing-details#backup-storage-cost).

To turn on this feature for your TiDB Cloud Dedicated cluster, perform the following steps:

1. Navigate to the [**Backup**](#view-the-backup-page) page of your cluster.

2. Click **Backup Setting**.

3. Toggle the **Auto Backup** switch to **On**.

4. Toggle the **Point-in-time Restore** switch to **On**.

    > **Warning**
    >
    > Point-in-Time Restore only takes effect after the next backup task is completed. To make it take effect earlier, you can [manually perform a backup](#perform-a-manual-backup) after enabling it.

5. Click **Save** to save changes.
#### Configure backup schedule

TiDB Cloud Dedicated supports daily and weekly backup schedules. By default, the backup schedule is set to daily. You can choose a specific time of the day or week to start snapshot backup.

To configure the backup schedule for your TiDB Cloud Dedicated cluster, perform the following steps:

1. Navigate to the [**Backup**](#view-the-backup-page) page of your cluster.

2. Click **Backup Setting**.

3. Toggle the **Auto Backup** switch to **On**.

4. Configure the backup schedule as follows:

    - In **Backup Cycle**, click either the **Daily Backup** or **Weekly Backup** tab. For **Weekly Backup**, you need to specify the days of the week for the backup.

        > **Warning**
        >
        > - When weekly backup is enabled, the Point-in-time Restore feature is enabled by default and cannot be disabled.
        > - If you change the backup cycle from weekly to daily, the Point-in-time Restore feature remains its original setting. You can manually disable it if needed.

    - In **Backup Time**, schedule a start time for the daily or weekly cluster backup.

        If you do not specify a preferred backup time, TiDB Cloud assigns a default backup time, which is 2:00 AM in the time zone of the region where the cluster is located.

        > **Note**
        >
        > - Backup jobs are automatically delayed when data import jobs are in progress. **DO NOT** run manual backups during data import or cluster scaling.

    - In **Backup Retention**, configure the minimum backup data retention period. The default period is 7 days. To minimize the impact on business, it is recommended to schedule automatic backup during periods of low workloads.

        > **Note**
        >
        > - All auto-backups, except the latest one, will be deleted if their lifetime exceeds the retention period. The latest auto-backup will not be deleted unless you delete it manually. This ensures that you can restore cluster data if accidental deletion occurs.
        > - After you delete a cluster, auto-backups with a lifetime within the retention period will be moved to the recycle bin.
