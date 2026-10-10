# Serverless restore modes, destinations, procedure, and limitations

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/backup-and-restore-serverless.md`
- Source Title: `Back Up and Restore TiDB Cloud Serverless Data`
- Source Heading Path: `Back Up and Restore TiDB Cloud Serverless Data > Restore | Back Up and Restore TiDB Cloud Serverless Data > Restore > Restore mode | Back Up and Restore TiDB Cloud Serverless Data > Restore > Restore destination | Back Up and Restore TiDB Cloud Serverless Data > Restore > Restore timeout | Back Up and Restore TiDB Cloud Serverless Data > Restore > Perform the restore | Back Up and Restore TiDB Cloud Serverless Data > Limitations`
- Source Line Ranges: `60-159`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tiflash`
- Topic Tags: `restore`, `snapshot-restore`, `point-in-time-restore`, `in-place-restore`, `restore-timeout`, `limitations`, `tiflash`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0053_fc5c936180`
- Source ID: `tidb-docs-8.1:tidb-cloud/backup-and-restore-serverless.md#restore`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `894829f63244b6ee71cf3b225e41f07c7108261748d8cb697543045898683067`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore-serverless#restore
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/backup-and-restore-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB Cloud Serverless restore modes, restore destinations, restore timeout behavior, restore steps, or restore limitations.
- Retrieval Keywords: Restore, Snapshot Restore, Point-in-Time Restore, beta, In-place Restore, Restore to a New Cluster, Restore Mode, Destination, Restoring, Available, restore timeout, three hours, mysql schema, user credentials, permissions, system variables, TiFlash replica, manual backups are not supported, more than 1 TiB
- Follow-up Guidance: If a restore is canceled after taking longer than three hours or if larger than 1 TiB datasets need restore-to-new-cluster support, the content points to TiDB Cloud Support for assistance.
- Classification Note: This is classified as recovery because the content describes how TiDB Cloud Serverless restores data, what destinations and time limits apply, and what limitations affect the restore outcome.

## Official Source Content

## Restore

TiDB Cloud Serverless clusters offer restore functionality to help recover data in case of accidental loss or corruption.
### Restore mode

TiDB Cloud Serverless supports snapshot restore and point-in-time restore for your cluster.

- **Snapshot Restore**: restores your cluster from a specific backup snapshot.

- **Point-in-Time Restore (beta)**: restores your cluster to a specific time.

    - Free clusters: not supported.
    - Scalable clusters: restores to any time within the last 14 days, but not before the cluster creation time or after the current time minus one minute.
### Restore destination

TiDB Cloud Serverless supports restoring in-place and restoring to a new cluster.

**In-place restore**

Restore to the current cluster will overwrite existing data. Note the following:

- Existing connections will be terminated once the restore is started.
- The cluster will be unavailable, and new connections will be blocked during the restore process.
- Restore will affect tables in the `mysql` schema. Any changes to user credentials, permissions, or system variables will be reverted to their state at the backup time.

**Restore to a new cluster**

Create and restore to the new cluster. Note the following:

- User credentials and permissions from the source cluster will not be restored to the new cluster.
### Restore timeout

The restore process typically completes within a few minutes. If the restore takes longer than three hours, it is automatically canceled. The outcome of a canceled restore depends on the destination:

- **In-place restore**: the cluster status changes from **Restoring** to **Available**, and the cluster becomes accessible.
- **Restore to a new cluster**: the new cluster is deleted and the source cluster remains unchanged.

If the data is corrupted after a canceled restore and cannot be recovered, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for assistance.
### Perform the restore

To restore your TiDB Cloud Serverless cluster, follow these steps:

1. Navigate to the [**Backup**](#view-the-backup-page) page of your cluster.

2. Click **Restore**. The setting window displays.

3. In **Restore Mode**, you can choose to restore from a specific backup or any point in time.

    <div label="Snapshot Restore">

    To restore from a selected backup snapshot, take the following steps:

    1. Click **Snapshot Restore**.
    2. Select the backup snapshot you want to restore from.

    </div>
    <div label="Point-in-Time Restore">

    To restore to a specific point in time for a scalable cluster, take the following steps:

    1. Click **Point-in-Time Restore**.
    2. Select the date and time you want to restore to.

    </div>

4. In **Destination**, you can choose to restore to a new cluster or restore in-place.

    <div label="Restore to a new cluster">

    To restore to a new cluster, take the following steps:

    1. Click **Restore to a New Cluster**.
    2. Enter a name for the new cluster.
    3. Choose the cluster plan for the new cluster.
    4. If you choose a scalable cluster, set a monthly spending limit, and then configure advanced settings as needed. Otherwise, skip this step.

    </div>
    <div label="Restore in-place">

    To restore in-place, click **In-place Restore**.

    </div>

5. Click **Restore** to begin the restore process.

Once the restore process begins, the cluster status changes to **Restoring**. The cluster will remain unavailable until the restore is complete and the status changes to **Available**.
## Limitations

- If a TiFlash replica is enabled, it will be unavailable for a period after the restore, because the data needs to be rebuilt in TiFlash.
- Manual backups are not supported for TiDB Cloud Serverless clusters.
- Clusters with more than 1 TiB of data do not support restoring to new clusters by default. Contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for assistance with larger datasets.
