# BR deployment requirements and usage methods

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-use-overview.md`
- Source Title: `Usage Overview of TiDB Backup and Restore`
- Source Heading Path: `Usage Overview of TiDB Backup and Restore > Deploy and use BR | Usage Overview of TiDB Backup and Restore > Deploy and use BR > Use br command-line tool (recommended) | Usage Overview of TiDB Backup and Restore > Deploy and use BR > Use SQL statements | Usage Overview of TiDB Backup and Restore > Deploy and use BR > Use TiDB Operator on Kubernetes | Usage Overview of TiDB Backup and Restore > See also`
- Source Line Ranges: `63-100`
- Source Scope: `shared`
- Primary Component: `br`
- Related Components: `sql`, `operator`, `tiup`, `tikv`
- Topic Tags: `deployment-requirements`, `resource-planning`, `command-line`, `sql-backup`, `sql-restore`, `kubernetes`, `operator`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0025_3c2b06790b`
- Source ID: `tidb-docs-8.1:br/br-use-overview.md#deploy-and-use-br`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `178c44889fa461e0c2c5e1752e4b8fe9e01d6f8f0fd6cd68abec67e17234715e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-use-overview#deploy-and-use-br
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-use-overview.md

## Retrieval Guidance

- Use When: Use this chunk when you need BR deployment requirements or the official ways to use backup and restore through the br command-line tool, SQL statements, or TiDB Operator on Kubernetes.
- Retrieval Keywords: Deploy and use BR, tiup install br, br command-line tool, BACKUP, RESTORE, SHOW BACKUPS|RESTORES, TiDB Operator, Kubernetes, Amazon S3, GCS, Azure Blob Storage, more than 8 cores and 16 GiB memory, at least two additional CPU cores, backup network bandwidth, IOPS
- Follow-up Guidance: The source links to the TiDB Snapshot Backup and Restore Guide, TiDB Log Backup and PITR Guide, TiDB Backup and Restore Use Cases, and Back Up and Restore Data Using TiDB Operator.
- Classification Note: This is classified as operation content because it lists resource and bandwidth requirements for BR and summarizes the supported backup and restore usage methods.

## Official Source Content

## Deploy and use BR

To deploy BR, ensure that the following requirements are met:

- BR, TiKV nodes, and the backup storage system provide network bandwidth that is greater than the backup speed. If the target cluster is particularly large, the threshold of backup and restore speed is limited by the bandwidth of the backup network.
- The backup storage system provides sufficient read and write performance (IOPS). Otherwise, they might become a performance bottleneck during backup or restore.
- TiKV nodes have at least two additional CPU cores and high performance disks for backups. Otherwise, the backup might have an impact on the services running on the cluster.
- BR runs on a node with more than 8 cores and 16 GiB memory.

You can use backup and restore features in several ways, such as via the command-line tool, by running SQL commands, and using TiDB Operator. The following sections describe these three methods in detail.
### Use br command-line tool (recommended)

TiDB supports backup and restore using br command-line tool.

* You can run the `tiup install br` command to [install br command-line tool using TiUP online](https://docs.pingcap.com/tidb/stable/migration-tools#install-tools-using-tiup).
* For details about how to use `br` commands to back up and restore data, refer to the following documents:

    * [TiDB Snapshot Backup and Restore Guide](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide)
    * [TiDB Log Backup and PITR Guide](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide)
    * [TiDB Backup and Restore Use Cases](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-use-cases)
### Use SQL statements

TiDB supports full backup and restore using SQL statements:

- [`BACKUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-backup): backs up full snapshot data.
- [`RESTORE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-restore): restores snapshot backup data.
- [`SHOW BACKUPS|RESTORES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-backups): views the backup and restore progress.
### Use TiDB Operator on Kubernetes

On Kubernetes, you can use TiDB Operator to back up TiDB cluster data to Amazon S3, GCS, or Azure Blob Storage, and restore data from the backup data in such systems. For details, see [Back Up and Restore Data Using TiDB Operator](https://docs.pingcap.com/tidb-in-kubernetes/stable/backup-restore-overview).
## See also

- [TiDB Backup and Restore Overview](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview)
- [TiDB Backup and Restore Architecture](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-design)
