# Delete a TiDB Cloud cluster and backup implications

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/delete-tidb-cluster.md`
- Source Title: `Delete a TiDB Cluster`
- Source Heading Path: `Delete a TiDB Cluster`
- Source Line Ranges: `5-42`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cluster-deletion`, `backups`, `restore`, `recycle-bin`, `retention`, `charges`, `serverless`, `dedicated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0321_df42505dba`
- Source ID: `tidb-docs-8.1:tidb-cloud/delete-tidb-cluster.md#delete-a-tidb-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `67598fb55cb680530d03cbcadd3139de58eba42906ad287f9e049eb7ef6987ec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/delete-tidb-cluster#delete-a-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/delete-tidb-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to delete a TiDB Cloud cluster and what happens to backups, restore ability, recycle bin retention, or backup charges after deletion.
- Retrieval Keywords: Delete a TiDB Cluster, TiDB Cloud cluster deletion, Clusters page, Delete, I understand, delete it, <organization name>/<project name>/<cluster name>, manual backup, automatic backup, charging policy for backups, restore the cluster, TiDB Cloud Dedicated, TiDB Cloud Serverless, recycle bin, Restore a deleted cluster, retention period, default retention period is 7 days, backups will continue to incur charges until deleted, Export Data from TiDB Cloud Serverless
- Follow-up Guidance: The source points to Back Up and Restore TiDB Cloud Dedicated Data, Restore a deleted cluster, and Export Data from TiDB Cloud Serverless for backup, restore, and export details.
- Classification Note: This is classified as a cloud operation because the content describes the UI steps to delete a TiDB Cloud cluster and the resulting backup and restore implications for Dedicated and Serverless clusters.

## Official Source Content

# Delete a TiDB Cluster

This document describes how to delete a TiDB cluster on TiDB Cloud.

You can delete a cluster at any time by performing the following steps:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.
2. In the row of your target cluster to be deleted, click **...**.

    > **Tip:**
    >
    > Alternatively, you can also click the name of the target cluster to go to its overview page, and then click **...** in the upper-right corner.

3. Click **Delete** in the drop-down menu.
4. In the cluster deleting window, confirm the deletion:

    - If you have at least one manual or automatic backup, you can see the number of backups and the charging policy for backups. Click **Continue** and enter `<organization name>/<project name>/<cluster name>`.
    - If you do not have any backups, just enter `<organization name>/<project name>/<cluster name>`.

    If you want to restore the cluster sometime in the future, make sure that you have a backup of the cluster. Otherwise, you cannot restore it anymore. For more information about how to back up TiDB Cloud Dedicated clusters, see [Back Up and Restore TiDB Cloud Dedicated Data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore).

    > **Note:**
    >
    > [TiDB Cloud Serverless clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) do not support restoring data after the deletion. If you want to delete a TiDB Cloud Serverless cluster and restore its data in the future, see [Export Data from TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-export) to export your data as a backup.

5. Click **I understand, delete it**.

    Once a backed up TiDB Cloud Dedicated cluster is deleted, the existing backup files of the cluster are moved to the recycle bin.

    - Automatic backups will expire and be automatically deleted once the retention period ends. The default retention period is 7 days if you don't modify it.
    - Manual backups will be kept in the Recycle Bin until manually deleted.

    > **Note:**
    >
    > Please be aware that backups will continue to incur charges until deleted.

    If you want to restore a TiDB Cloud Dedicated cluster from recycle bin, see [Restore a deleted cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#restore-a-deleted-cluster).
