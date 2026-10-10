# Migration tools scenarios and limitations overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migration-tools.md`
- Source Title: `TiDB Migration Tools Overview`
- Source Heading Path: `TiDB Migration Tools Overview | TiDB Migration Tools Overview > [TiDB Data Migration (DM)](/dm/dm-overview.md) | TiDB Migration Tools Overview > [TiDB Lightning](/tidb-lightning/tidb-lightning-overview.md) | TiDB Migration Tools Overview > [Dumpling](/dumpling-overview.md) | TiDB Migration Tools Overview > [TiCDC](/ticdc/ticdc-overview.md) | TiDB Migration Tools Overview > [Backup & Restore (BR)](/br/backup-and-restore-overview.md) | TiDB Migration Tools Overview > [sync-diff-inspector](/sync-diff-inspector/sync-diff-inspector-overview.md)`
- Source Line Ranges: `5-87`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dm`, `lightning`, `dumpling`, `ticdc`, `br`, `ecosystem`, `tidb`, `tikv`
- Topic Tags: `migration`, `tool-selection`, `upstream-downstream`, `full-import`, `incremental-replication`, `backup-restore`, `data-replication`, `limitations`, `advantages`, `consistency-check`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0442_651b5740db`
- Source ID: `tidb-docs-8.1:migration-tools.md#tidb-migration-tools-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b8132b7ab30ef9171f0888da6377e49c4b07e5fbf3116e2c6da6d6bdafc5d421`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migration-tools#tidb-migration-tools-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migration-tools.md

## Retrieval Guidance

- Use When: Use this overview when selecting among TiDB migration tools based on full data migration, incremental data migration, backup and restore, data replication, supported upstreams and downstreams, advantages, and limitations.
- Retrieval Keywords: TiDB Migration Tools Overview, TiDB Data Migration (DM), TiDB Lightning, Dumpling, TiCDC, Backup & Restore (BR), sync-diff-inspector, full data migration, incremental data migration, backup and restore, data replication, supported upstreams and downstreams, advantages and limitations, MySQL-compatible databases to TiDB, full data import into TiDB, full data export from MySQL or TiDB, pulling TiKV change logs, consistent state with any upstream TSO, new_collation_enabled, mysql.tidb, CREATE SEQUENCE, SEQUENCE, valid index, physical import mode, logical import mode
- Follow-up Guidance: The source also includes an installation section for these tools using TiUP and links to each tool overview.
- Classification Note: This chunk is classified as reference because it summarizes user scenarios, upstream and downstream support, advantages, and limitations for multiple migration tools without giving a single procedure.

## Official Source Content

# TiDB Migration Tools Overview

TiDB provides multiple data migration tools for different scenarios such as full data migration, incremental data migration, backup and restore, and data replication.

This document introduces the user scenarios, supported upstreams and downstreams, advantages, and limitations of these tools. You can choose the right tool according to your needs.

<!--The following diagram shows the user scenario of each migration tool.

!TiDB Migration Tools media/migration-tools.png-->
## [TiDB Data Migration (DM)](https://docs.pingcap.com/tidb/stable/dm/dm-overview)

- **User scenario**: Data migration from MySQL-compatible databases to TiDB
- **Upstream**: MySQL, MariaDB, Aurora
- **Downstream**: TiDB
- **Advantages**:
    - A convenient and unified data migration task management tool that supports full data migration and incremental replication
    - Support filtering tables and operations
    - Support shard merge and migration
- **Limitation**: Data import speed is roughly the same as that of TiDB Lightning's [logical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode), and a lot lower than that of TiDB Lightning's [physical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode). So it is recommended to use DM to migrate full data with a size of less than 1 TiB.
## [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview)

- **User scenario**: Full data import into TiDB
- **Upstream (the imported source file)**:
    - Files exported from Dumpling
    - Parquet files exported by Amazon Aurora, Apache Hive, and Snowflake
    - CSV files
    - Data from local disks or Amazon S3
- **Downstream**: TiDB
- **Advantages**:
    - Support quickly importing a large amount of data and quickly initializing a specific table in a TiDB cluster
    - Support checkpoints to store the import progress, so that `tidb-lightning` continues importing from where it lefts off after restarting
    - Support data filtering
- **Limitation**:
    - If [physical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage) is used for data import, during the import process, the TiDB cluster cannot provide services.
    - If you do not want the TiDB services to be impacted, perform the data import according to TiDB Lightning [logical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode-usage).
## [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview)

- **User scenario**: Full data export from MySQL or TiDB
- **Upstream**: MySQL, TiDB
- **Downstream (the output file)**: SQL, CSV
- **Advantages**:
    - Support the table-filter feature that enables you to filter data easier
    - Support exporting data to Amazon S3
- **Recommendation**:
    - If you want to restore the exported data to a database other than TiDB, it is recommended to use Dumpling.
    - If you want to restore the exported data to another TiDB cluster, it is recommended to use Backup & Restore (BR).
## [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview)

- **User scenario**: This tool is implemented by pulling TiKV change logs. It can restore cluster data to a consistent state with any upstream TSO, and support other systems to subscribe to data changes.
- **Upstream**: TiDB
- **Downstream**: TiDB, MySQL, Kafka, MQ, Confluent, storage services such as Amazon S3, GCS, Azure Blob Storage, and NFS.
- **Advantages**: Provide TiCDC Open Protocol
- **Limitation**: TiCDC only replicates tables that have at least one valid index. The following scenarios are not supported:
    - The TiKV cluster that uses RawKV alone.
    - The DDL operation `CREATE SEQUENCE` and the `SEQUENCE` function in TiDB.
## [Backup & Restore (BR)](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview)

- **User scenario**: Migrate a large amount of TiDB cluster data by backing up and restoring data
- **Upstream**: TiDB
- **Downstream (the output file)**: SST, backup.meta files, backup.lock files
- **Advantages**:
    - Suitable for migrating data to another TiDB cluster
    - Support backing up data to an external storage for disaster recovery
- **Limitation**:
    - When BR restores data to the upstream cluster of TiCDC or Drainer, the restored data cannot be replicated to the downstream by TiCDC or Drainer.
    - BR supports operations only between clusters that have the same `new_collation_enabled` value in the `mysql.tidb` table.
## [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview)

- **User scenario**: Comparing data stored in the databases with the MySQL protocol
- **Upstream**: TiDB, MySQL
- **Downstream**: TiDB, MySQL
- **Advantages**: Can be used to repair data in the scenario where a small amount of data is inconsistent
- **Limitation**:
    - Online check is not supported for data migration between MySQL and TiDB.
    - JSON, BIT, BINARY, BLOB and other types of data are not supported.
