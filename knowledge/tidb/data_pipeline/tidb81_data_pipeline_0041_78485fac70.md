# Migration overview and sharded-table prerequisites

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-large-mysql-shards-to-tidb.md`
- Source Title: `Migrate and Merge MySQL Shards of Large Datasets to TiDB`
- Source Heading Path: `Migrate and Merge MySQL Shards of Large Datasets to TiDB | Migrate and Merge MySQL Shards of Large Datasets to TiDB > Prerequisites | Migrate and Merge MySQL Shards of Large Datasets to TiDB > Prerequisites > Check conflicts for Sharded Tables`
- Source Line Ranges: `5-71`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dumpling`, `lightning`, `dm`, `tidb`
- Topic Tags: `migration`, `shard-merge`, `prerequisites`, `primary-key-conflict`, `unique-index-conflict`, `schema-design`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0041_78485fac70`
- Source ID: `tidb-docs-8.1:migrate-large-mysql-shards-to-tidb.md#migrate-and-merge-mysql-shards-of-large-datasets-to-tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7bf3a23f9e601740a87af2a38bae5d297274e4a54aca53fe4132c4ae0d7cac6a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-large-mysql-shards-to-tidb#migrate-and-merge-mysql-shards-of-large-datasets-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-large-mysql-shards-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented overview and prerequisites for migrating and merging large MySQL sharded datasets into TiDB, including sharded-table conflict checks for primary keys and unique indexes.
- Retrieval Keywords: Migrate and Merge MySQL Shards of Large Datasets to TiDB, large datasets more than 1 TiB, TiDB Lightning, TiDB DM, Dumpling, Check conflicts for Sharded Tables, primary key conflict, unique index conflict, Handle conflicts between primary keys or unique indexes across multiple sharded tables, my_db1, my_db2, table1, table2, table3, table4, mydb.table5, CREATE TABLE `table1`, CREATE TABLE `table5`, AUTO_INCREMENT, UNIQUE KEY `sid` (`sid`), INDEX (`id`)
- Follow-up Guidance: The source next outlines using Dumpling to export full data, TiDB Lightning to import into `mydb.table5`, and optionally TiDB DM for incremental replication.
- Classification Note: This is classified as data_pipeline because the content describes the end-to-end migration flow and the prerequisite schema design checks needed to merge sharded data.

## Official Source Content

# Migrate and Merge MySQL Shards of Large Datasets to TiDB

If you want to migrate a large MySQL dataset (for example, more than 1 TiB) from different partitions into TiDB, and you are able to suspend all the TiDB cluster write operations from your business during the migration, you can use TiDB Lightning to do the migration quickly. After migration, you can also use TiDB DM to perform incremental replication according to your business needs. "Large datasets" in this document usually mean data around one TiB or more.

This document uses an example to walk through the whole procedure of such kind of migration.

If the data size of the MySQL shards is less than 1 TiB, you can follow the procedure described in [Migrate and Merge MySQL Shards of Small Datasets to TiDB](https://docs.pingcap.com/tidb/stable/migrate-small-mysql-shards-to-tidb), which supports both full and incremental migration and the steps are easier.

The example in this document assumes that you have two databases, `my_db1` and `my_db2`. You use Dumpling to export two tables `table1` and `table2` from `my_db1`, and two tables `table3` and `table4` from `my_db2`, respectively. After that, you use TiDB Lightning to import and merge the four exported tables into the same `table5` from `mydb` in the target TiDB.

In this document, you can migrate data following this procedure:

1. Use Dumpling to export full data. In this example, you export 2 tables respectively from 2 upstream databases:

    - Export `table1` and `table2` from `my_db1`
    - Export `table3` and `table4` from `my_db2`

2. Start TiDB Lightning to migrate data to `mydb.table5` in TiDB.

3. (Optional) Use TiDB DM to perform incremental replication.
## Prerequisites

Before getting started, see the following documents to prepare for the migration task.

- [Deploy a DM Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-tiup)
- [Use TiUP to Deploy Dumpling and Lightning](https://docs.pingcap.com/tidb/stable/migration-tools)
- [Downstream privilege requirements for Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#export-data-from-tidb-or-mysql)
- [Downstream privilege requirements for TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-requirements)
- [Downstream storage space for TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-requirements)
- [Privileges required by DM-worker](https://docs.pingcap.com/tidb/stable/dm/dm-worker-intro)
### Check conflicts for Sharded Tables

If the migration involves merging data from different sharded tables, primary key or unique index conflicts may occur during the merge. Therefore, before migration, you need to take a deep look at the current sharding scheme from the business point of view, and find a way to avoid conflicts. For more details, see [Handle conflicts between primary keys or unique indexes across multiple sharded tables](https://docs.pingcap.com/tidb/stable/dm/shard-merge-best-practices#handle-conflicts-between-primary-keys-or-unique-indexes-across-multiple-sharded-tables). The following is a brief description.

Assume that tables 1~4 have the same table structure as follows.

```sql
CREATE TABLE `table1` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sid` bigint(20) NOT NULL,
  `pid` bigint(20) NOT NULL,
  `comment` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sid` (`sid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
```

For those four tables, the `id` column is the primary key. It is auto-incremental, which will cause different sharded tables to generate duplicated `id` ranges and cause the primary key conflict on the target table during the migration. On the other hand, the `sid` column is the sharding key, which ensures that the index is unique globally. So you can remove the unique constraint of the `id` column in the target `table5` to avoid the data merge conflicts.

```sql
CREATE TABLE `table5` (
  `id` bigint(20) NOT NULL,
  `sid` bigint(20) NOT NULL,
  `pid` bigint(20) NOT NULL,
  `comment` varchar(255) DEFAULT NULL,
  INDEX (`id`),
  UNIQUE KEY `sid` (`sid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
```
