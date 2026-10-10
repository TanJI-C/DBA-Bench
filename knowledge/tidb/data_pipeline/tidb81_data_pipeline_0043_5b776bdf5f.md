# Migration overview, prerequisites, and resource planning

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-large-mysql-to-tidb.md`
- Source Title: `Migrate Large Datasets from MySQL to TiDB`
- Source Heading Path: `Migrate Large Datasets from MySQL to TiDB | Migrate Large Datasets from MySQL to TiDB > Prerequisites | Migrate Large Datasets from MySQL to TiDB > Resource requirements | Migrate Large Datasets from MySQL to TiDB > Resource requirements > Disk space for the target TiKV cluster`
- Source Line Ranges: `5-69`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dumpling`, `lightning`, `dm`, `tikv`
- Topic Tags: `migration`, `prerequisites`, `capacity-planning`, `disk-space`, `cpu`, `memory`, `binlog-retention`, `full-load`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0043_5b776bdf5f`
- Source ID: `tidb-docs-8.1:migrate-large-mysql-to-tidb.md#migrate-large-datasets-from-mysql-to-tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6cefef99e9610feededa52a1ca5f911ca84af32099adbde65ee77d7d203988b3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-large-mysql-to-tidb#migrate-large-datasets-from-mysql-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-large-mysql-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when planning a large MySQL-to-TiDB migration and you need the stated prerequisites, resource sizing, binlog retention note, or TiKV storage capacity formula.
- Retrieval Keywords: Migrate Large Datasets from MySQL to TiDB, large datasets around one TiB or more, DM 30~50 GiB/h, TiDB Lightning Physical Import Mode up to 500 GiB/h, prerequisites, Install DM, Install Dumpling and TiDB Lightning, privileges required for DM, privileges required for TiDB Lightning, privileges required for Dumpling, resource requirements, CentOS 7, region-concurrency, 75% of the logical CPU, more than 64 GiB of memory, more than 32 CPU cores, CPU core to memory ratio greater than 1:2, Dumpling disk space, largest single table, increase the binlog storage time in the upstream, information_schema.tables, DATA_LENGTH, INDEX_LENGTH, FORMAT_BYTES, Disk space for the target TiKV cluster, size of the data source x the number of replicas x 2, RocksDB space amplification
- Follow-up Guidance: The source also provides SQL statements that summarize DATA_LENGTH and INDEX_LENGTH in information_schema.tables and identify the 5 largest tables for estimating export and import sizing.
- Classification Note: This is classified as data_pipeline for the shared component because it covers end-to-end migration planning prerequisites and capacity requirements across Dumpling, Lightning, DM, and TiKV.

## Official Source Content

# Migrate Large Datasets from MySQL to TiDB

When the data volume to be migrated is small, you can easily [use DM to migrate data](https://docs.pingcap.com/tidb/stable/migrate-small-mysql-to-tidb), both for full migration and incremental replication. However, because DM imports data at a slow speed (30~50 GiB/h), when the data volume is large, the migration might take a long time. "Large datasets" in this document usually mean data around one TiB or more.

This document describes how to perform the full migration using Dumpling and TiDB Lightning. TiDB Lightning [Physical Import Mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode) can import data at a speed of up to 500 GiB/h. Note that this speed is affected by various factors such as hardware configuration, table schema, and the number of indexes. After the full migration is completed, you can replicate the incremental data using DM.
## Prerequisites

- [Install DM](https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-tiup).
- [Install Dumpling and TiDB Lightning](https://docs.pingcap.com/tidb/stable/migration-tools).
- [Grant the source database and target database privileges required for DM](https://docs.pingcap.com/tidb/stable/dm/dm-worker-intro).
- [Grant the target database privileges required for TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq#what-are-the-privilege-requirements-for-the-target-database).
- [Grant the source database privileges required for Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#export-data-from-tidb-or-mysql).
## Resource requirements

**Operating system**: The example in this document uses fresh CentOS 7 instances. You can deploy a virtual machine either on your local host or in the cloud. Because TiDB Lightning consumes as much CPU resources as needed by default, it is recommended that you deploy it on a dedicated server. If this is not possible, you can deploy it on a single server together with other TiDB components (for example, `tikv-server`) and then configure `region-concurrency` to limit the CPU usage from TiDB Lightning. Usually, you can configure the size to 75% of the logical CPU.

**Memory and CPU**: Because TiDB Lightning consumes high resources, it is recommended to allocate more than 64 GiB of memory and more than 32 CPU cores. To get the best performance, make sure that the CPU core to memory (GiB) ratio is greater than 1:2.

**Disk space**:

- Dumpling requires a disk space that can store the whole data source (or to store all upstream tables to be exported). SSD is recommended. To calculate the required space, see [Downstream storage space requirements](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-requirements#storage-space-of-the-target-database).
- During the import, TiDB Lightning needs temporary space to store the sorted key-value pairs. The disk space should be enough to hold the largest single table from the data source.
- If the full data volume is large, you can increase the binlog storage time in the upstream. This is to ensure that the binlogs are not lost during the incremental replication.

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

The target TiKV cluster must have enough disk space to store the imported data. In addition to [the standard hardware requirements](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements), the storage space of the target TiKV cluster must be larger than **the size of the data source x [the number of replicas](https://docs.pingcap.com/tidb/stable/faq/manage-cluster-faq#is-the-number-of-replicas-in-each-region-configurable-if-yes-how-to-configure-it) x 2**. For example, if the cluster uses 3 replicas by default, the target TiKV cluster must have a storage space larger than 6 times the size of the data source. The formula has `x 2` because:

- Index might take extra space.
- RocksDB has a space amplification effect.
