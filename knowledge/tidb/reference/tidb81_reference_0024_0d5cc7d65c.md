# BR overview, usage restrictions, features, storage, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/backup-and-restore-overview.md`
- Source Title: `TiDB Backup & Restore Overview`
- Source Heading Path: `TiDB Backup & Restore Overview | TiDB Backup & Restore Overview > Before you use | TiDB Backup & Restore Overview > Before you use > Restrictions | TiDB Backup & Restore Overview > Before you use > Some tips | TiDB Backup & Restore Overview > Use backup and restore | TiDB Backup & Restore Overview > BR features | TiDB Backup & Restore Overview > BR features > Back up cluster data | TiDB Backup & Restore Overview > BR features > Back up cluster data > Backup performance and impact on TiDB clusters | TiDB Backup & Restore Overview > BR features > Restore backup data | TiDB Backup & Restore Overview > BR features > Restore backup data > Restore performance and impact on TiDB clusters | TiDB Backup & Restore Overview > Backup storage | TiDB Backup & Restore Overview > Compatibility | TiDB Backup & Restore Overview > Compatibility > Compatibility with other features`
- Source Line Ranges: `5-119`
- Source Scope: `shared`
- Primary Component: `br`
- Related Components: `tidb`, `tikv`, `cloud`, `operator`, `lightning`
- Topic Tags: `backup`, `restore`, `pitr`, `restrictions`, `prerequisites`, `performance`, `storage`, `compatibility`, `versioning`, `disaster-recovery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0024_0d5cc7d65c`
- Source ID: `tidb-docs-8.1:br/backup-and-restore-overview.md#tidb-backup-restore-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `946deced97afdfe6dec68b1f102a9da07847622c697c89f444e7f30f8a791058`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview#tidb-backup-restore-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/backup-and-restore-overview.md

## Retrieval Guidance

- Use When: Use this chunk when you need an overview of TiDB BR capabilities, restrictions, backup storage options, performance characteristics, and compatibility conditions for backup, restore, or PITR.
- Retrieval Keywords: TiDB Backup & Restore Overview, BR overview, PITR restrictions, PITR only supports restoring data to an empty cluster, BR does not support running multiple backup tasks on a cluster at the same time, BR does not support running snapshot backup tasks and data restore tasks at the same time, br restore point, full backup, log backup, snapshot backup, Recovery Point Objective as short as five minutes, backup.num-threads, Amazon S3, Google Cloud Storage, GCS, Azure Blob Storage, NFS, S3-compatible file storage services, tidb_enable_clustered_index, new_collation_enabled, mysql.tidb, new_collations_enabled_on_first_bootstrap mismatch, default not found, GBK charset, Global temporary tables, TiDB Lightning Physical Import
- Follow-up Guidance: For detailed procedures, the content points to Snapshot backup, PITR, Restore snapshot backup, Restore a database or a table, external storage URI, and backup storage authentication documents.
- Classification Note: This is reference content because it summarizes BR usage restrictions, supported backup and restore modes, storage backends, performance figures, and feature compatibility notes from the official overview.

## Official Source Content

# TiDB Backup & Restore Overview

Based on the Raft protocol and a reasonable deployment topology, TiDB realizes high availability of clusters. When a few nodes in the cluster fail, the cluster can still be available. On this basis, to further ensure data safety, TiDB provides the Backup & Restore (BR) feature as the last resort to recover data from natural disasters and misoperations.

BR satisfies the following requirements:

- Back up cluster data to a disaster recovery (DR) system with an RPO as short as 5 minutes, reducing data loss in disaster scenarios.
- Handle the cases of misoperations from applications by rolling back data to a time point before the error event.
- Perform history data auditing to meet the requirements of judicial supervision.
- Clone the production environment, which is convenient for troubleshooting, performance tuning, and simulation testing.
## Before you use

This section describes the prerequisites for using TiDB backup and restore, including restrictions, usage tips and compatibility issues. For more information about the compatibility of the BR tool with other features or versions, see [Compatibility](#compatibility).
### Restrictions

- PITR only supports restoring data to **an empty cluster**.
- PITR only supports cluster-level restore and does not support database-level or table-level restore.
- PITR does not support restoring the data of user tables or privilege tables from system tables.
- BR does not support running multiple backup tasks on a cluster **at the same time**.
- BR does not support running snapshot backup tasks and data restore tasks on a cluster **at the same time**.
- When restoring a cluster using PITR, you cannot run a log backup task or use TiCDC to replicate data to a downstream cluster.
### Some tips

Snapshot backup:

- It is recommended that you perform the backup operation during off-peak hours to minimize the impact on applications.
- It is recommended that you execute multiple backup or restore tasks one by one. Running multiple backup tasks in parallel leads to low performance. Worse still, a lack of collaboration between multiple tasks might result in task failures and affect cluster performance.

Snapshot restore:

- BR uses resources of the target cluster as much as possible. Therefore, it is recommended that you restore data to a new cluster or an offline cluster. Avoid restoring data to a production cluster. Otherwise, your application will be affected inevitably.

Backup storage and network configuration:

- It is recommended that you store backup data to a storage system that is compatible with Amazon S3, GCS, or Azure Blob Storage.
- You need to ensure that BR, TiKV, and the backup storage system have enough network bandwidth, and that the backup storage system can provide sufficient read and write performance (IOPS). Otherwise, they might become a performance bottleneck during backup and restore.
## Use backup and restore

The way to use BR varies with the deployment method of TiDB. This document introduces how to use the br command-line tool to back up and restore TiDB cluster data in an on-premise deployment.

For information about how to use this feature in other deployment scenarios, see the following documents:

- [Back Up and Restore TiDB Deployed on TiDB Cloud](https://docs.pingcap.com/tidbcloud/backup-and-restore): It is recommended that you create TiDB clusters on [TiDB Cloud](https://www.pingcap.com/tidb-cloud/?from=en). TiDB Cloud offers fully managed databases to let you focus on your applications.
- [Back Up and Restore Data Using TiDB Operator](https://docs.pingcap.com/tidb-in-kubernetes/stable/backup-restore-overview): If you deploy a TiDB cluster using TiDB Operator on Kubernetes, it is recommended to back up and restore data using Kubernetes CustomResourceDefinition (CRD).
## BR features

TiDB BR provides the following features:

- Back up cluster data: You can back up full data (**full backup**) of the cluster at a certain time point, or back up the data changes in TiDB (**log backup**, in which log means KV changes in TiKV).

- Restore backup data:

    - You can **restore a full backup** or **specific databases or tables** in a full backup.
    - Based on backup data (full backup and log backup), you can restore the target cluster to any time point of the backup cluster. This type of restore is called point-in-time recovery, or PITR for short.
### Back up cluster data

Full backup backs up all data of a cluster at a specific time point. TiDB supports the following way of full backup:

- Back up cluster snapshots: A snapshot of a TiDB cluster contains transactionally consistent data at a specific time. For details, see [Snapshot backup](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#back-up-cluster-snapshots).

Full backup occupies much storage space and contains only cluster data at a specific time point. If you want to choose the restore point as required, that is, to perform point-in-time recovery (PITR), you can use the following two ways of backup at the same time:

- Start [log backup](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide#start-log-backup). After log backup is started, the task keeps running on all TiKV nodes and backs up TiDB incremental data in small batches to the specified storage periodically.
- Perform snapshot backup regularly. Back up the full cluster data to the backup storage, for example, perform cluster snapshot backup at 0:00 AM every day.
#### Backup performance and impact on TiDB clusters

- When CPU and I/O resources are sufficient in the cluster, the snapshot backup has a limited impact on the TiDB cluster, generally staying below 20%. With appropriate configuration of the TiDB cluster, this impact can be further minimized to 10% or even less. When CPU and I/O resources are insufficient, you can adjust the TiKV configuration item [`backup.num-threads`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#num-threads-1) to change the number of worker threads used by the backup task to reduce the impact of the backup task on the TiDB cluster. The backup speed of a TiKV node is scalable and ranges from 50 MB/s to 100 MB/s. For more information, see [Backup performance and impact](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#performance-and-impact-of-snapshot-backup).
- When there are only log backup tasks, the impact on the cluster is about 5%. Log backup flushes all the changes generated after the last refresh every 3-5 minutes to the backup storage, which can **achieve a Recovery Point Objective (RPO) as short as five minutes**.
### Restore backup data

Corresponding to the backup features, you can perform two types of restore: full restore and PITR.

- Restore a full backup

    - Restore cluster snapshot backup: You can restore snapshot backup data to an empty cluster or a cluster that does not have data conflicts (with the same schema or tables). For details, see [Restore snapshot backup](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#restore-cluster-snapshots). In addition, you can restore specific databases or tables from the backup data and filter out unwanted data. For details, see [Restore specific databases or tables from backup data](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#restore-a-database-or-a-table).

- Restore data to any point in time (PITR)

    - By running the `br restore point` command, you can restore the latest snapshot backup data before recovery time point and log backup data to a specified time. BR automatically determines the restore scope, accesses backup data, and restores data to the target cluster in turn.
#### Restore performance and impact on TiDB clusters

- Data restore is performed at a scalable speed. Generally, the speed is 1 GiB/s per TiKV node. For more details, see [Restore performance and impact](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#performance-and-impact-of-snapshot-restore).
- On each TiKV node, PITR can restore log data at 30 GiB/h. For more details, see [PITR performance and impact](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide#performance-capabilities-of-pitr).
## Backup storage

TiDB supports backing up data to Amazon S3, Google Cloud Storage (GCS), Azure Blob Storage, NFS, and other S3-compatible file storage services. For details, see the following documents:

- [Specify backup storage in URI](https://docs.pingcap.com/tidb/stable/external-storage-uri)
- [Configure access privileges to backup storages](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages#authentication)
## Compatibility
### Compatibility with other features

Backup and restore might go wrong when some TiDB features are enabled or disabled. If these features are not consistently enabled or disabled during backup and restore, compatibility issues might occur.

| Feature | Issue | Solution |
|  ----  | ----  | ----- |
|GBK charset|| BR of versions earlier than v5.4.0 does not support restoring `charset=GBK` tables. No version of BR supports recovering `charset=GBK` tables to TiDB clusters earlier than v5.4.0. |
| Clustered index | [#565](https://github.com/pingcap/br/issues/565) | Make sure that the value of the `tidb_enable_clustered_index` global variable during restore is consistent with that during backup. Otherwise, data inconsistency might occur, such as `default not found` error and inconsistent data index. |
| New collation  | [#352](https://github.com/pingcap/br/issues/352)       | Make sure that the value of the `new_collation_enabled` variable in the `mysql.tidb` table during restore is consistent with that during backup. Otherwise, inconsistent data index might occur and checksum might fail to pass. For more information, see [FAQ - Why does BR report `new_collations_enabled_on_first_bootstrap` mismatch?](https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq#why-is-new_collation_enabled-mismatch-reported-during-restore). |
| Global temporary tables | | Make sure that you are using v5.3.0 or a later version of BR to back up and restore data. Otherwise, an error occurs in the definition of the backed global temporary tables. |
| TiDB Lightning Physical Import| | If the upstream database uses the physical import mode of TiDB Lightning, data cannot be backed up in log backup. It is recommended to perform a full backup after the data import. For more information, see [When the upstream database imports data using TiDB Lightning in the physical import mode, the log backup feature becomes unavailable. Why?](https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq#when-the-upstream-database-imports-data-using-tidb-lightning-in-the-physical-import-mode-the-log-backup-feature-becomes-unavailable-why).|
