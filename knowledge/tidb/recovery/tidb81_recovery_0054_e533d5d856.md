# Restore backups to a new or deleted TiDB Cloud Dedicated cluster

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/backup-and-restore.md`
- Source Title: `Back Up and Restore TiDB Cloud Dedicated Data`
- Source Heading Path: `Back Up and Restore TiDB Cloud Dedicated Data > Restore > Restore data to a new cluster | Back Up and Restore TiDB Cloud Dedicated Data > Restore > Restore a deleted cluster`
- Source Line Ranges: `199-274`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `restore`, `backup`, `point-in-time-restore`, `recycle-bin`, `cluster-recovery`, `password-settings`, `region-selection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0054_e533d5d856`
- Source ID: `tidb-docs-8.1:tidb-cloud/backup-and-restore.md#restore-data-to-a-new-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `571c83efb68b2a0cc7f3525ba626e69deef0c2deca1c18f6180e116334c89cf6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#restore-data-to-a-new-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/backup-and-restore.md

## Retrieval Guidance

- Use When: Use this when you need the documented steps and constraints for restoring TiDB Cloud Dedicated data to a new cluster or restoring a deleted cluster from the recycle bin.
- Retrieval Keywords: Restore data to a new cluster, Restore a deleted cluster, Restore From Region, Point-in-time Restore, Select Time Point, Select Backup Name, Primary Region, Password Settings, Recycle Bin, Backups, TiDB Cloud console
- Follow-up Guidance: The restore flow ends with the Password Settings dialog box, where you set the root password and click Save.
- Classification Note: This chunk is a TiDB Cloud Dedicated restore procedure covering restore to a new cluster and restore from the recycle bin, including region selection, backup selection, and password settings.

## Official Source Content

### Restore data to a new cluster

> **Note**
>
> When you restore a TiDB cluster from backups, the restore process retains the original time zone setting without overwriting it.

To restore your TiDB Cloud Dedicated cluster data from a backup to a new cluster, take the following steps:

1. Navigate to the [**Backup**](#view-the-backup-page) page of your cluster.

2. Click **Restore**. The setting window displays.

3. In **Restore Mode**, choose **Restore From Region**, indicating the region of backup stores.

    > **Note**
    >
    > - The default value of the **Restore From Region** is the same as the backup cluster.

4. In **Restore Mode**, choose to restore data of any point in time or a selected backup to a new cluster.

    <div label="Select Time Point">

    To restore data of any point in time within the backup retention to a new cluster, make sure that **Point-in-time Restore** in **Backup Setting** is on and then take the following steps:

    - Click **Select Time Point**.
    - Select **Date** and **Time** you want to restore to.

    </div>

    <div label="Select Backup Name">

    To restore a selected backup to the new cluster, take the following steps:

    - Click **Select Backup Name**.
    - Select a backup you want to restore to.

    </div>

5. In **Restore to Region**, select the same region as the **Primary Region** configured in the **Backup Setting**.

6. In the **Restore** window, you can also make the following changes if necessary:

    - Set the cluster name.
    - Update the port number of the cluster.
    - Increase node number, vCPU and RAM, and storage for the cluster.

7. Click **Restore**.

   The cluster restore process starts and the **Password Settings** dialog box is displayed.

8. In the **Password Settings** dialog box, set the root password to connect to your cluster, and then click **Save**.
### Restore a deleted cluster

> **Note:**
>
> You cannot restore a deleted cluster to any point in time. You can only select an automatic or manual backup to restore.

To restore a deleted cluster from recycle bin, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Recycle Bin**.
3. On the **Recycle Bin** page, locate the cluster you want to restore, click **...** in the **Action** column, and then click **Backups**.
4. On the **Backups** page, locate your desired backup time, click **...** in the **Action** column, and then click **Restore**.
5. On the **Restore** page, specify a name for the new cluster, and then make the following changes if necessary:

    - Update the port number of the cluster.
    - Increase the node number, vCPU and RAM, and storage for the cluster.

6. In the **Summary** section, check the restore information, and then click **Restore**.

   The cluster restore process starts and the **Password Settings** dialog box is displayed.

7. In the **Password Settings** dialog box, set the root password to connect to your cluster, and then click **Save**.
