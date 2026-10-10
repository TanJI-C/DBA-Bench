# Data migration, export, import, and backup tools

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ecosystem-tool-user-guide.md`
- Source Title: `TiDB Tools Overview`
- Source Heading Path: `TiDB Tools Overview > Data management tools | TiDB Tools Overview > Data management tools > Data migration - TiDB Data Migration (DM) | TiDB Tools Overview > Data management tools > Full data export - Dumpling | TiDB Tools Overview > Data management tools > Full data import - TiDB Lightning | TiDB Tools Overview > Data management tools > Backup and restore - Backup & Restore (BR)`
- Source Line Ranges: `37-114`
- Source Scope: `all`
- Primary Component: `ecosystem`
- Related Components: `dm`, `dumpling`, `lightning`, `br`, `operator`, `tidb`, `tikv`
- Topic Tags: `data-management`, `migration`, `full-load`, `incremental-replication`, `export`, `import`, `backup`, `restore`, `kubernetes-support`, `deprecation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0021_19f475bb5a`
- Source ID: `tidb-docs-8.1:ecosystem-tool-user-guide.md#data-management-tools`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8536fd244c5d9b926e30b200b21ff26934728ede4dd96c0a07f6aecbc5a349f4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ecosystem-tool-user-guide#data-management-tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ecosystem-tool-user-guide.md

## Retrieval Guidance

- Use When: Use this chunk when selecting TiDB tools for full migration, incremental replication, full export, full import, or backup and restore, including data volume guidance and deprecation notes.
- Retrieval Keywords: TiDB Data Migration, DM, Dumpling, TiDB Lightning, Backup & Restore, BR, full data migration, incremental data replication, full data export, full data import, backup and restore, less than 1 TB, greater than 1 TB, Logical Import Mode, Physical Import Mode, Syncer tool is no longer maintained, Loader tool is no longer maintained, mydumper deprecated, snapshot backup, log backup, PITR, SST + backupmeta file
- Follow-up Guidance: The chunk states that for data volume greater than 1 TB, use Dumpling for full export, TiDB Lightning for import, and DM for incremental replication.
- Classification Note: This is classified as data_pipeline because the content maps tools to data movement workflows including migration, export, import, replication, backup, and restore.

## Official Source Content

## Data management tools

 TiDB provides multiple data management tools, such as import and export, backup and restore, incremental data replication, and data validation.
### Data migration - TiDB Data Migration (DM)

[TiDB Data Migration](https://docs.pingcap.com/tidb/stable/dm/dm-overview) (DM) is a tool that supports full data migration and incremental data replication from MySQL/MariaDB to TiDB.

The following are the basics of DM:

- Source: MySQL/MariaDB
- Target: TiDB clusters
- Supported TiDB versions: all versions
- Kubernetes support: use [TiDB Operator](https://github.com/pingcap/tidb-operator) to deploy TiDB DM on Kubernetes.

If the data volume is less than 1 TB, it is recommended to migrate data from MySQL/MariaDB to TiDB directly using DM. The migration process includes full data migration and incremental data replication.

If the data volume is greater than 1 TB , take the following steps:

1. Use [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) to export the full data from MySQL/MariaDB.
2. Use [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) to import the data exported in Step 1 to the TiDB cluster.
3. Use TiDB DM to replicate the incremental data from MySQL/MariaDB to TiDB.

> **Note:**
>
> The Syncer tool is no longer maintained. For scenarios related to Syncer, it is recommended that you use DM to perform incremental replication.
### Full data export - Dumpling

[Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) supports logical full data export from MySQL or TiDB.

The following are the basics of Dumpling:

- Source: MySQL/TiDB clusters
- Output: SQL/CSV files
- Supported TiDB versions: all versions
- Kubernetes support: No

> **Note:**
>
> PingCAP previously maintained a fork of the [mydumper project](https://github.com/maxbube/mydumper) with enhancements specific to TiDB. Starting from v7.5.0, [Mydumper](https://docs-archive.pingcap.com/tidb/v4.0/mydumper-overview/) is deprecated and most of its features have been replaced by [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview). It is strongly recommended that you use Dumpling instead of mydumper.
### Full data import - TiDB Lightning

[TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) supports full data import of a large dataset into a TiDB cluster.

TiDB Lightning supports the following modes:

- `Physical Import Mode`: TiDB Lightning parses data into ordered key-value pairs and directly imports them into TiKV. This mode is usually for importing a large amount of data (at the TB level) to a new cluster. During the import, the cluster cannot provide services.
- `Logical Import Mode`: This mode uses TiDB/MySQL as the backend, which is slower than the `Physical Import Mode` but can be performed online. It also supports importing data to MySQL.

The following are the basics of TiDB Lightning:

- Data source:
    - The output files of Dumpling
    - Other compatible CSV files
    - Parquet files exported from Amazon Aurora, Apache Hive, or Snowflake
- Supported TiDB versions: v2.1 and later versions
- Kubernetes support: Yes. See [Quickly restore data into a TiDB cluster on Kubernetes using TiDB Lightning](https://docs.pingcap.com/tidb-in-kubernetes/stable/restore-data-using-tidb-lightning) for details.

> **Note:**
>
> The Loader tool is no longer maintained. For scenarios related to Loader, it is recommended that you use `Logical Import Mode` instead.
### Backup and restore - Backup & Restore (BR)

[Backup & Restore](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview) (BR) is a command-line tool for distributed backup and restore of the TiDB cluster data. BR can effectively back up and restore TiDB clusters of huge data volume.

The following are the basics of BR:

- Input and output data source

    - Snapshot backup and restore: [SST + `backupmeta` file](https://docs.pingcap.com/tidb/stable/br/br-snapshot-architecture#backup-files)
    - Log backup and PITR: [Log backup files](https://docs.pingcap.com/tidb/stable/br/br-log-architecture#log-backup-files)

- Supported TiDB versions: v4.0 and later versions
- Kubernetes support: Yes. See [Back up Data to S3-Compatible Storage Using BR](https://docs.pingcap.com/tidb-in-kubernetes/stable/backup-to-aws-s3-using-br) and [Restore Data from S3-Compatible Storage Using BR](https://docs.pingcap.com/tidb-in-kubernetes/stable/restore-from-aws-s3-using-br) for details.
