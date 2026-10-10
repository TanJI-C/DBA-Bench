# Manage dual region backup, manual backups, and backup deletion

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/backup-and-restore.md`
- Source Title: `Back Up and Restore TiDB Cloud Dedicated Data`
- Source Heading Path: `Back Up and Restore TiDB Cloud Dedicated Data > Backup > Turn on dual region backup | Back Up and Restore TiDB Cloud Dedicated Data > Backup > Turn off auto backup | Back Up and Restore TiDB Cloud Dedicated Data > Backup > Turn off dual region backup | Back Up and Restore TiDB Cloud Dedicated Data > Backup > Perform a manual backup | Back Up and Restore TiDB Cloud Dedicated Data > Backup > Delete backups | Back Up and Restore TiDB Cloud Dedicated Data > Backup > Delete backups > Delete backup files | Back Up and Restore TiDB Cloud Dedicated Data > Backup > Delete backups > Delete a running backup job | Back Up and Restore TiDB Cloud Dedicated Data > Restore`
- Source Line Ranges: `105-198`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `br`
- Topic Tags: `dual-region-backup`, `auto-backup`, `manual-backup`, `backup-deletion`, `retention`, `recycle-bin`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0284_217d166a0c`
- Source ID: `tidb-docs-8.1:tidb-cloud/backup-and-restore.md#turn-on-dual-region-backup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d2ed8480f6b9aee807ff12ebab01bf6dbf7508c224482b25e62dae27b7254287`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#turn-on-dual-region-backup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/backup-and-restore.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to manage TiDB Cloud Dedicated dual region backup, turn off auto backup, create a manual backup, delete backup files, delete a running backup job, or understand related retention and cleanup notes.
- Retrieval Keywords: Dual Region Backup, Secondary Region, turn on dual region backup, turn off dual region backup, turn off auto backup, Point-in-time Restore, AWS, Google Cloud, Google Cloud Storage, dual-region pairing, same multi-region code, Tokyo and Osaka, cross-region data protection, approximately 99% of the data can be replicated to the secondary region within an hour, manual backup, Manual Backup, Name, Delete backups, Delete backup files, Delete a running backup job, Pending, Running, recycle bin, backup retention schedule
- Follow-up Guidance: The content states that disabling dual region backup does not immediately delete secondary-region backups, manual backups are retained indefinitely until manually deleted or the account is closed, and deleted-cluster manual backups move to the recycle bin.
- Classification Note: This is operation content because it provides UI procedures and operational notes for backup management actions in TiDB Cloud Dedicated.

## Official Source Content

### Turn on dual region backup

> **Note:**
>
> - Currently, the dual region backup feature is only available for clusters hosted on AWS and Google Cloud.
> - TiDB Cloud Dedicated clusters hosted on Google Cloud work seamlessly with Google Cloud Storage. Similar to Google Cloud Storage, **TiDB Cloud Dedicated supports dual-region pairing only within the same multi-region code as Google dual-region storage**. For example, in Asia, currently you must pair Tokyo and Osaka together for dual-region storage. For more information, refer to [Dual-regions](https://cloud.google.com/storage/docs/locations#location-dr).

TiDB Cloud Dedicated supports dual region backup by replicating backups from your cluster region to another different region. After you enable this feature, all backups are automatically replicated to the specified region. This provides cross-region data protection and disaster recovery capabilities. It is estimated that approximately 99% of the data can be replicated to the secondary region within an hour.

Dual region backup costs include both backup storage usage and cross-region data transfer fees. For more information, refer to [Data Backup Cost](https://www.pingcap.com/tidb-dedicated-pricing-details#backup-storage-cost).

To turn on dual region backup for your TiDB Cloud Dedicated cluster, perform the following steps:

1. Navigate to the [**Backup**](#view-the-backup-page) page of your cluster.

2. Click **Backup Setting**.

3. Toggle the **Dual Region Backup** switch to **On**.

4. From the **Secondary Region** drop-down list, select a region to store the backup files.

5. Click **Save** to save changes.
### Turn off auto backup

> **Note**
>
> Turning off auto backup will also turn off point-in-time restore by default.

To turn off auto backup for your TiDB Cloud Dedicated cluster, perform the following steps:

1. Navigate to the [**Backup**](#view-the-backup-page) page of your cluster.

2. Click **Backup Setting**.

3. Toggle the **Auto Backup** switch to **Off**.

4. Click **Save** to save changes.
### Turn off dual region backup

> **Tip**
>
> Disabling dual region backup does not immediately delete the backups in the secondary region. These backups will be cleaned up later according to the backup retention schedule. To remove them immediately, you can manually [delete the backups](#delete-backups).

To turn off dual region backup for your TiDB Cloud Dedicated cluster, perform the following steps:

1. Navigate to the [**Backup**](#view-the-backup-page) page of your cluster.

2. Click **Backup Setting**.

3. Toggle the **Dual Region Backup** switch to **Off**.

4. Click **Save** to save changes.
### Perform a manual backup

Manual backups are user-initiated backups that enable you to back up your data to a known state as needed, and then restore to that state at any time.

> **Note**
>
> - Manual backups are retained indefinitely until you choose to delete them manually or your account is closed.
> - After a TiDB Cloud Dedicated cluster is deleted, its existing manual backups will be moved to the recycle bin and kept there until manually deleted or your account is closed.

To apply a manual backup to your TiDB Cloud Dedicated cluster, perform the following steps:

1. Navigate to the [**Backup**](#view-the-backup-page) page of your cluster.

2. In the upper-right corner, click **...** > **Manual Backup**. 

3. In the displayed dialog, enter a **Name**.

4. Click **Confirm**. Then your cluster data is backed up.
### Delete backups
#### Delete backup files

To delete an existing backup file for your TiDB Cloud Dedicated cluster, perform the following steps:

1. Navigate to the [**Backup**](#view-the-backup-page) page of your cluster.

2. Locate the corresponding backup file you want to delete, and click **...** > **Delete** in the **Action** column.
#### Delete a running backup job

To delete a running backup job for your TiDB Cloud Dedicated cluster, follow a process similar to [**Delete backup files**](#delete-backup-files).

1. Navigate to the [**Backup**](#view-the-backup-page) page of your cluster.

2. Locate the running backup job that is in the **Pending** or **Running** state, and click **...** > **Delete** in the **Action** column.
## Restore
