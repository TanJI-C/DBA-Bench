# Migration overview, prerequisites, and shard conflict checks

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-small-mysql-shards-to-tidb.md`
- Source Title: `Migrate and Merge MySQL Shards of Small Datasets to TiDB`
- Source Heading Path: `Migrate and Merge MySQL Shards of Small Datasets to TiDB | Migrate and Merge MySQL Shards of Small Datasets to TiDB > Prerequisites | Migrate and Merge MySQL Shards of Small Datasets to TiDB > Prerequisites > Check conflicts for the sharded tables`
- Source Line Ranges: `5-67`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `sql`
- Topic Tags: `mysql-shards`, `shard-merge`, `prerequisites`, `conflict-checking`, `primary-key`, `unique-index`, `schema-design`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0048_f2ef6c42e4`
- Source ID: `tidb-docs-8.1:migrate-small-mysql-shards-to-tidb.md#migrate-and-merge-mysql-shards-of-small-datasets-to-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `79f77fd1f5ba3a4a26f3381ed1ae779646e6da0c67c58841e64c6722391a0100`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-small-mysql-shards-to-tidb#migrate-and-merge-mysql-shards-of-small-datasets-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-small-mysql-shards-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the migration overview and prerequisites for merging multiple MySQL shards of small datasets into one downstream TiDB database with DM, including checking primary key or unique index conflicts before shard merge.
- Retrieval Keywords: Migrate and Merge MySQL Shards of Small Datasets to TiDB, small datasets around or less than one TiB, DM migrate MySQL shards, Deploy a DM Cluster Using TiUP, Privileges required by DM-worker, Check conflicts for the sharded tables, Handle conflicts between primary keys or unique indexes across multiple sharded tables, sale_01, sale_02, store_01, store_02, PRIMARY KEY (`id`), UNIQUE KEY `sid` (`sid`), Remove the primary key attribute of the auto-increment primary key, CREATE TABLE `sale`
- Follow-up Guidance: The source points to related guidance for handling conflicts between primary keys or unique indexes across multiple sharded tables and for removing the primary key attribute from the auto-increment primary key column.
- Classification Note: Classified as data_pipeline for the dm component because the content describes DM-based shard migration prerequisites, dataset scope, and schema conflict checks for merging sharded MySQL tables into TiDB.

## Official Source Content

# Migrate and Merge MySQL Shards of Small Datasets to TiDB

If you want to migrate and merge multiple MySQL database instances upstream to one TiDB database downstream, and the amount of data is not too large, you can use DM to migrate MySQL shards. "Small datasets" in this document usually mean data around or less than one TiB. Through examples in this document, you can learn the operation steps, precautions, and troubleshooting of the migration.

This document applies to migrating MySQL shards less than 1 TiB in total. If you want to migrate MySQL shards with a total of more than 1 TiB of data, it will take a long time to migrate only using DM. In this case, it is recommended that you follow the operation introduced in [Migrate and Merge MySQL Shards of Large Datasets to TiDB](https://docs.pingcap.com/tidb/stable/migrate-large-mysql-shards-to-tidb) to perform migration.

This document takes a simple example to illustrate the migration procedure. The MySQL shards of the two data source MySQL instances in the example are migrated to the downstream TiDB cluster.

In this example, both MySQL Instance 1 and MySQL Instance 2 contain the following schemas and tables. In this example, you migrate and merge tables from `store_01` and `store_02` schemas with a `sale` prefix in both instances, into the downstream `sale` table in the `store` schema.

| Schema | Table |
|:------|:------|
| store_01 | sale_01, sale_02 |
| store_02 | sale_01, sale_02 |

Target schemas and tables:

| Schema | Table |
|:------|:------|
| store | sale |
## Prerequisites

Before starting the migration, make sure you have completed the following tasks:

- [Deploy a DM Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-tiup)
- [Privileges required by DM-worker](https://docs.pingcap.com/tidb/stable/dm/dm-worker-intro)
### Check conflicts for the sharded tables

If the migration involves merging data from different sharded tables, primary key or unique index conflicts may occur during the merge. Therefore, before migration, you need to take a deep look at the current sharding scheme from the business point of view, and find a way to avoid the conflicts. For more details, see [Handle conflicts between primary keys or unique indexes across multiple sharded tables](https://docs.pingcap.com/tidb/stable/dm/shard-merge-best-practices#handle-conflicts-between-primary-keys-or-unique-indexes-across-multiple-sharded-tables). The following is a brief description.

In this example, `sale_01` and `sale_02` have the same table structure as follows

```sql
CREATE TABLE `sale_01` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sid` bigint(20) NOT NULL,
  `pid` bigint(20) NOT NULL,
  `comment` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sid` (`sid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
```

The `id` column is the primary key, and the `sid` column is the sharding key. The `id` column is auto-incremental, and duplicated multiple sharded table ranges will cause data conflicts. The `sid` can ensure that the index is globally unique, so you can follow the steps in [Remove the primary key attribute of the auto-increment primary key](https://docs.pingcap.com/tidb/stable/dm/shard-merge-best-practices#remove-the-primary-key-attribute-from-the-column) to bypasses the `id` column.

```sql
CREATE TABLE `sale` (
  `id` bigint(20) NOT NULL,
  `sid` bigint(20) NOT NULL,
  `pid` bigint(20) NOT NULL,
  `comment` varchar(255) DEFAULT NULL,
  INDEX (`id`),
  UNIQUE KEY `sid` (`sid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
```
