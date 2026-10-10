# Serverless backup page and automatic backup settings

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/backup-and-restore-serverless.md`
- Source Title: `Back Up and Restore TiDB Cloud Serverless Data`
- Source Heading Path: `Back Up and Restore TiDB Cloud Serverless Data | Back Up and Restore TiDB Cloud Serverless Data > View the Backup page | Back Up and Restore TiDB Cloud Serverless Data > Automatic backups | Back Up and Restore TiDB Cloud Serverless Data > Automatic backups > Learn about the backup setting | Back Up and Restore TiDB Cloud Serverless Data > Automatic backups > Configure the backup setting`
- Source Line Ranges: `6-59`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `backup`, `automatic-backup`, `backup-retention`, `backup-time`, `backup-page`, `serverless`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0282_94bcaefe2d`
- Source ID: `tidb-docs-8.1:tidb-cloud/backup-and-restore-serverless.md#back-up-and-restore-tidb-cloud-serverless-data`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4e84dbe85441788848f649d2edb481f2e6df3c6a02d269d41f7aa0b3ef500e15`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore-serverless#back-up-and-restore-tidb-cloud-serverless-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/backup-and-restore-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud Serverless Backup page path or the automatic backup cycle, retention, and backup time settings for free clusters versus scalable clusters.
- Retrieval Keywords: Data > Backup, Backup page, Automatic backups, Backup Cycle, Backup Retention, Backup Time, free clusters, scalable clusters, 1 day, 14 days, daily backup, fixed time, configurable, Backup Setting, Confirm
- Follow-up Guidance: For a scalable cluster, the content includes the Backup Setting workflow to schedule the daily backup start time on the Backup page.
- Classification Note: This is classified as operation because the content explains where to view the Backup page and how automatic backup settings work and are configured in TiDB Cloud Serverless.

## Official Source Content

# Back Up and Restore TiDB Cloud Serverless Data

This document describes how to back up and restore your TiDB Cloud Serverless cluster data on TiDB Cloud.

> **Tip:**
>
> To learn how to back up and restore TiDB Cloud Dedicated cluster data, see [Back Up and Restore TiDB Cloud Dedicated Data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore).
## View the Backup page

1. On the [**Clusters**](https://tidbcloud.com/project/clusters) page, click the name of your target cluster to go to its overview page.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. In the left navigation pane, click **Data** > **Backup**.
## Automatic backups

TiDB Cloud Serverless automatically backs up your cluster data, allowing you to restore data from a backup snapshot to minimize data loss in the event of a disaster.
### Learn about the backup setting

Automatic backup settings vary between free clusters and scalable clusters, as shown in the following table:

| Backup setting   | Free clusters | Scalable clusters |
|------------------|--------------|------------------|
| Backup Cycle     | Daily        | Daily            |
| Backup Retention | 1 day        | 14 days          |
| Backup Time      | Fixed time   | Configurable     |

- **Backup Cycle** is the frequency at which backups are taken.

- **Backup Retention** is the duration for which backups are retained. Expired backups cannot be restored.
   
- **Backup Time** is the time when the backup starts to be scheduled. Note that the final backup time might fall behind the configured backup time.
   
    - Free clusters: the backup time is a randomly fixed time.
    - Scalable clusters: you can configure the backup time to every half an hour. The default value is a randomly fixed time.
### Configure the backup setting

To set the backup time for a scalable cluster, perform the following steps:

1. Navigate to the [**Backup**](#view-the-backup-page) page of your cluster.

2. Click **Backup Setting**. This will open the **Backup Setting** window, where you can configure the automatic backup settings according to your requirements.

3. In **Backup Time**, schedule a start time for the daily cluster backup.

4. Click **Confirm**.
