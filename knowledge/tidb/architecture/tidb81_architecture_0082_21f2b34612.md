# Shard migration overview and example environment

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-sql-shards.md`
- Source Title: `Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud`
- Source Heading Path: `Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud | Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Environment information in the example | Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Environment information in the example > Upstream cluster | Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Environment information in the example > DM | Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Environment information in the example > External storage | Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Environment information in the example > Downstream cluster`
- Source Line Ranges: `5-50`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`, `shared`
- Topic Tags: `shard-merge`, `migration-scenario`, `environment`, `upstream-mysql`, `downstream-schema`, `external-storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0082_21f2b34612`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-sql-shards.md#migrate-and-merge-mysql-shards-of-large-datasets-to-tidb-cloud`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c748dbb321acffb298aba1c8c91cf35a8f0fd02876d00fcdf8f6b1fb45f6d100`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-sql-shards#migrate-and-merge-mysql-shards-of-large-datasets-to-tidb-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-sql-shards.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the example architecture and environment for migrating and merging MySQL shards of a large dataset into TiDB Cloud, including upstream MySQL instances, DM, external storage, and the downstream target table.
- Retrieval Keywords: Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud, MySQL v5.7.18, TiDB Data Migration (DM), DM v5.3.0, Deploy a DM Cluster Using TiUP, Amazon S3, store_01, store_02, sale_01, sale_02, CREATE TABLE sale_01, auto_increment primary key, store.sales
- Follow-up Guidance: After full data migration, you can use TiDB Data Migration (DM) to perform incremental migration according to your business needs.
- Classification Note: This is classified as architecture because the content defines the migration scenario, component layout, example versions, shard topology, and the downstream merged table `store.sales`.

## Official Source Content

# Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud

This document describes how to migrate and merge a large MySQL dataset (for example, more than 1 TiB) from different partitions into TiDB Cloud. After full data migration, you can use [TiDB Data Migration (DM)](https://docs.pingcap.com/tidb/stable/dm-overview) to perform incremental migration according to your business needs.

The example in this document uses a complex shard migration task across multiple MySQL instances, and involves handling conflicts in auto-increment primary keys. The scenario in this example is also applicable to merging data from different sharded tables within a single MySQL instance.
## Environment information in the example

This section describes the basic information of the upstream cluster, DM, and downstream cluster used in the example.
### Upstream cluster

The environment information of the upstream cluster is as follows:

- MySQL version: MySQL v5.7.18
- MySQL instance1:
    - schema `store_01` and table `[sale_01, sale_02]`
    - schema `store_02` and table `[sale_01, sale_02]`
- MySQL instance 2:
    - schema `store_01`and table `[sale_01, sale_02]`
    - schema `store_02`and table `[sale_01, sale_02]`
- Table structure:

  ```sql
  CREATE TABLE sale_01 (
  id bigint(20) NOT NULL auto_increment,
  uid varchar(40) NOT NULL,
  sale_num bigint DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY ind_uid (uid)
  );
  ```
### DM

The version of DM is v5.3.0. You need to deploy TiDB DM manually. For detailed steps, see [Deploy a DM Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/deploy-a-dm-cluster-using-tiup).
### External storage

This document uses the Amazon S3 as an example.
### Downstream cluster

The sharded schemas and tables are merged into the table `store.sales`.
