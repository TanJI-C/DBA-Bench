# Overview, requirements, and resource sizing for Dumpling and Lightning

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/backup-and-restore-using-dumpling-lightning.md`
- Source Title: `Back up and Restore Data Using Dumpling and TiDB Lightning`
- Source Heading Path: `Back up and Restore Data Using Dumpling and TiDB Lightning | Back up and Restore Data Using Dumpling and TiDB Lightning > Requirements | Back up and Restore Data Using Dumpling and TiDB Lightning > Resource requirements | Back up and Restore Data Using Dumpling and TiDB Lightning > Resource requirements > Disk space for the target TiKV cluster`
- Source Line Ranges: `5-83`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dumpling`, `lightning`, `tikv`, `tiup`
- Topic Tags: `backup`, `restore`, `prerequisites`, `installation`, `resource-planning`, `disk-space`, `cpu`, `memory`, `s3`, `gcs`, `azure`, `sql-estimation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0003_db648211ad`
- Source ID: `tidb-docs-8.1:backup-and-restore-using-dumpling-lightning.md#back-up-and-restore-data-using-dumpling-and-tidb-lightning`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `70107a1de121eacb1e8a77a9e446f67cf7597c4ea6cce73c464664e56b9772d7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/backup-and-restore-using-dumpling-lightning#back-up-and-restore-data-using-dumpling-and-tidb-lightning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/backup-and-restore-using-dumpling-lightning.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented requirements, installation commands, and resource sizing guidance for backing up and restoring full data with Dumpling and TiDB Lightning.
- Retrieval Keywords: tiup install dumpling, tiup install tidb-lightning, Dumpling privileges, TiDB Lightning privileges, resource requirements, region-concurrency, 75% of the logical CPU, more than 64 GiB of memory, more than 32 CPU cores, CPU core to memory ratio greater than 1:2, Amazon S3, Google Cloud Storage, GCS, Azure Blob Storage, information_schema.tables, DATA_LENGTH, INDEX_LENGTH, FORMAT_BYTES, Disk space for the target TiKV cluster, size of the data source x the number of replicas x 2, RocksDB space amplification
- Follow-up Guidance: The chunk also provides SQL statements on information_schema.tables to estimate exported data volume and a formula for target TiKV storage sizing based on data size, replicas, and extra space for indexes and RocksDB amplification.
- Classification Note: This is classified as an operation chunk because the content defines prerequisites, installation steps, and capacity planning details for running Dumpling and TiDB Lightning.

## Official Source Content

# Back up and Restore Data Using Dumpling and TiDB Lightning

This document introduces how to use Dumpling and TiDB Lightning to back up and restore full data of TiDB.

If you need to back up a small amount of data (for example, less than 50 GiB) and do not require high backup speed, you can use [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) to export data from the TiDB database and then use [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) to restore the data into another TiDB database. 

If you need to back up larger databases, the recommended method is to use [BR](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview). Note that Dumpling can be used to export large databases, but BR is a better tool for that.
## Requirements

- Install Dumpling:

    ```shell
    tiup install dumpling
    ```

- Install TiDB Lightning:

    ```shell
    tiup install tidb-lightning
    ```

- [Grant the source database privileges required for Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#export-data-from-tidb-or-mysql)
- [Grant the target database privileges required for TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-requirements#privileges-of-the-target-database)
## Resource requirements

**Operating system**: The example in this document uses fresh CentOS 7 instances. You can deploy a virtual machine either on your local host or in the cloud. Because TiDB Lightning consumes as much CPU resources as needed by default, it is recommended that you deploy it on a dedicated server. If this is not possible, you can deploy it on a single server together with other TiDB components (for example, `tikv-server`) and then configure `region-concurrency` to limit the CPU usage from TiDB Lightning. Usually, you can configure the size to 75% of the logical CPU.

**Memory and CPU**: Because TiDB Lightning consumes high resources, it is recommended to allocate more than 64 GiB of memory and more than 32 CPU cores. To get the best performance, make sure that the CPU core to memory (GiB) ratio is greater than 1:2.

**Disk space**:

It is recommended to use Amazon S3, Google Cloud Storage (GCS), or Azure Blob Storage as the external storage. With such a cloud storage, you can store backup files quickly without being limited by the disk space.

If you need to save data of one backup task to the local disk, note the following limitations:

- Dumpling requires a disk space that can store the whole data source (or to store all upstream tables to be exported). To calculate the required space, see [Downstream storage space requirements](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-requirements#storage-space-of-the-target-database).
- During the import, TiDB Lightning needs temporary space to store the sorted key-value pairs. The disk space should be enough to hold the largest single table from the data source.

**Note**: It is difficult to calculate the exact data volume exported by Dumpling from MySQL, but you can estimate the data volume by using the following SQL statement to summarize the `DATA_LENGTH` field in the `information_schema.tables` table:

```sql
-- Calculate the size of all schemas
SELECT
  TABLE_SCHEMA,
  FORMAT_BYTES(SUM(DATA_LENGTH)) AS 'Data Size',
  FORMAT_BYTES(SUM(INDEX_LENGTH)) 'Index Size'
FROM
  information_schema.tables
GROUP BY
  TABLE_SCHEMA;

-- Calculate the 5 largest tables
SELECT 
  TABLE_NAME,
  TABLE_SCHEMA,
  FORMAT_BYTES(SUM(data_length)) AS 'Data Size',
  FORMAT_BYTES(SUM(index_length)) AS 'Index Size',
  FORMAT_BYTES(SUM(data_length+index_length)) AS 'Total Size'
FROM
  information_schema.tables
GROUP BY
  TABLE_NAME,
  TABLE_SCHEMA
ORDER BY
  SUM(DATA_LENGTH+INDEX_LENGTH) DESC
LIMIT
  5;
```
### Disk space for the target TiKV cluster

The target TiKV cluster must have enough disk space to store the imported data. In addition to [the standard hardware requirements](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements), the storage space of the target TiKV cluster must be larger than **the size of the data source x [the number of replicas](https://docs.pingcap.com/tidb/stable/faq/manage-cluster-faq#is-the-number-of-replicas-in-each-region-configurable-if-yes-how-to-configure-it) x 2**. For example, if the cluster uses 3 replicas by default, the target TiKV cluster must have a storage space larger than 6 times the size of the data source. The formula has x 2 because:

- Index might take extra space.
- RocksDB has a space amplification effect.
