# BR recommended backup, retention, and restore practices

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-use-overview.md`
- Source Title: `Usage Overview of TiDB Backup and Restore`
- Source Heading Path: `Usage Overview of TiDB Backup and Restore | Usage Overview of TiDB Backup and Restore > Recommended practices | Usage Overview of TiDB Backup and Restore > Recommended practices > How to back up data? | Usage Overview of TiDB Backup and Restore > Recommended practices > How to manage backup data? | Usage Overview of TiDB Backup and Restore > Recommended practices > How to restore data?`
- Source Line Ranges: `5-62`
- Source Scope: `shared`
- Primary Component: `br`
- Related Components: `tikv`, `tiup`, `cloud`
- Topic Tags: `backup-methods`, `full-backup`, `log-backup`, `pitr`, `backup-storage`, `retention-period`, `directory-layout`, `restore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0024_0ee80d48d7`
- Source ID: `tidb-docs-8.1:br/br-use-overview.md#usage-overview-of-tidb-backup-and-restore`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8fdc8e027b29eb2c3f5b80dbfa052c1c2633c746bac21be30741d455060027bf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-use-overview#usage-overview-of-tidb-backup-and-restore
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-use-overview.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official BR overview of recommended full backup, log backup, backup retention period, backup directory layout, and restore methods including PITR.
- Retrieval Keywords: tiup br log start, tiup br backup full, tiup br log truncate, tiup br restore, tiup br restore point, full backup, log backup, PITR, backup retention period, backup-${cluster-id}, fullbackup-202209081330, backup-${cluster-id}/logbackup, Amazon S3, Google Cloud Storage, GCS, Azure Blob Storage, MinIO, NFS, POSIX file system
- Follow-up Guidance: The source also points to the Start log backup guide and the snapshot backup guide for command details.
- Classification Note: This is classified as operation content because it describes recommended BR backup, storage management, retention, and restore practices using specific BR commands and storage layouts.

## Official Source Content

# Usage Overview of TiDB Backup and Restore

This document describes best practices of using TiDB backup and restore features, including how to choose a backup method, how to manage backup data, and how to install and deploy the backup and restore tool.
## Recommended practices

Before using TiDB backup and restore features, it is recommended that you understand the recommended backup and restore solutions.
### How to back up data?

**TiDB provides two types of backup. Which one should I use?** Full backup contains the full data of a cluster at a certain point in time. Log backup contains the data changes written to TiDB. It is recommended to use both types of backup at the same time:

- **[Start log backup](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide#start-log-backup)**: Run the `tiup br log start` command to start the log backup task. After that, the task keeps running on all TiKV nodes and backs up TiDB data changes to the specified storage in small batches regularly.
- **Perform [snapshot (full) backup](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#back-up-cluster-snapshots) regularly**: Run the `tiup br backup full` command to back up the snapshot of the cluster to the specified storage. For example, back up the cluster snapshot at 0:00 AM every day.
### How to manage backup data?

BR provides only basic backup and restore features, and does not support backup management. Therefore, you need to decide how to manage backup data on your own, which might involve the following questions?

* Which backup storage system should I choose?
* In which directory should I place the backup data during a backup task?
* In what way should I organize the directory of the full backup data and log backup data?
* How to handle the historical backup data in the storage system?

The following sections will answer these questions one by one.

**Choose a backup storage system**

It is recommended that you store backup data to Amazon S3, Google Cloud Storage (GCS), or Azure Blob Storage. Using these systems, you do not need to worry about the backup capacity and bandwidth allocation.

If the TiDB cluster is deployed in a self-built data center, the following practices are recommended:

* Build [MinIO](https://docs.min.io/docs/minio-quickstart-guide.html) as the backup storage system, and use the S3 protocol to back up data to MinIO.
* Mount Network File System (NFS, such as NAS) disks to br command-line tool and all TiKV instances, and use the POSIX file system interface to write backup data to the corresponding NFS directory.

> **Note:**
>
> If you do not choose NFS or a storage system that supports Amazon S3, GCS, or Azure Blob Storage protocols, the data backed up is generated at each TiKV node. **Note that this is not the recommended way to use BR**, because collecting the backup data might result in data redundancy and operation and maintenance problems.

**Organize the backup data directory**

* Store the snapshot backup and log backup in the same directory for unified management, for example, `backup-${cluster-id}`.
* Store each snapshot backup in a directory with the backup date included, for example, `backup-${cluster-id}/fullbackup-202209081330`.
* Store the log backup in a fixed directory, for example, `backup-${cluster-id}/logbackup`. The log backup program creates subdirectories under the `logbackup` directory every day to distinguish the data backed up each day.

**Handle historical backup data**

Assume that you need to set the life cycle for each backup data, for example, 7 days. Such a life cycle is called **backup retention period**, which will also be mentioned in backup tutorials.

* To perform PITR, you need to restore the full backup before the restore point, and the log backup between the full backup and the restore point. Therefore, **It is recommended to only delete the log backup before the full snapshot**. For log backups that exceed the backup retention period, you can use `tiup br log truncate` command to delete the backup before the specified time point.
* For backup data that exceeds the retention period, you can delete or archive the backup directory.
### How to restore data?

- To restore only full backup data, you can use `tiup br restore` to perform a full restore of the specified backup.
- If you have started log backup and regularly performed a full backup, you can run the `tiup br restore point` command to restore data to any time point within the backup retention period.
