# Sharded table merge overview and mode comparison

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/feature-shard-merge.md`
- Source Title: `Merge and Migrate Data from Sharded Tables`
- Source Heading Path: `Merge and Migrate Data from Sharded Tables | Merge and Migrate Data from Sharded Tables > Overview | Merge and Migrate Data from Sharded Tables > Overview > The pessimistic mode | Merge and Migrate Data from Sharded Tables > Overview > The optimistic mode | Merge and Migrate Data from Sharded Tables > Overview > Contrast`
- Source Line Ranges: `5-35`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `sharding`, `merge`, `migration`, `ddl`, `dml`, `pessimistic-mode`, `optimistic-mode`, `schema-coordination`, `data-consistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0028_050afd2099`
- Source ID: `tidb-docs-8.1:dm/feature-shard-merge.md#merge-and-migrate-data-from-sharded-tables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d0604ff36836dc22cc454d45b20cb922f1dba5f040d317b5747ca14cddbffe04`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge#merge-and-migrate-data-from-sharded-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/feature-shard-merge.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how DM merges and migrates data from multiple upstream sharded tables into one downstream TiDB table and how pessimistic mode and optimistic mode differ for coordinating DDL and DML.
- Retrieval Keywords: Data Migration (DM), Merge and Migrate Data from Sharded Tables, shard-mode, pessimistic mode, optimistic mode, sharded tables, DDL, DML, schema change, schema compatible, downstream TiDB, upstream MySQL, upstream MariaDB, suspend DML migration, continue DML migration, DDL execution order, entire shard group is consistent, data inconsistency
- Follow-up Guidance: For details, the source points to shard merge in pessimistic mode and shard merge in optimistic mode.
- Classification Note: This chunk is classified as architecture because it explains DM sharding support behavior, the coordination of DDL and DML across sharded tables, and the mode comparison for schema coordination and data consistency.

## Official Source Content

# Merge and Migrate Data from Sharded Tables

This document introduces the sharding support feature provided by Data Migration (DM). This feature allows you to merge and migrate the data of tables with the same or different table schemas in the upstream MySQL or MariaDB instances into one same table in the downstream TiDB. It supports not only migrating the upstream DML statements, but also coordinating to migrate the table schema change using DDL statements in multiple upstream sharded tables.
## Overview

DM supports merging and migrating the data of multiple upstream sharded tables into one table in TiDB. During the migration, the DDL of each sharded table, and the DML before and after the DDL need to be coordinated. For the usage scenarios, DM supports two different modes: pessimistic mode and optimistic mode.

> **Note:**
>
> - To merge and migrate data from sharded tables, you must set `shard-mode` in the task configuration file.
> - DM uses the pessimistic mode by default for the merge of the sharding support feature. (If there is no special description in the document, use the pessimistic mode by default.)
> - It is not recommended to use this mode if you do not understand the principles and restrictions of the optimistic mode. Otherwise, it may cause serious consequences such as migration interruption and even data inconsistency.
### The pessimistic mode

When an upstream sharded table executes a DDL statement, the migration of this sharded table will be suspended. After all other sharded tables execute the same DDL, the DDL will be executed in the downstream and the data migration task will restart. The advantage of this mode is that it can ensure that the data migrated to the downstream will not go wrong. For details, refer to [shard merge in pessimistic mode](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-pessimistic).
 
### The optimistic mode

DM will automatically modify the DDL executed on a sharded table into a statement compatible with other sharded tables, and then migrate to the downstream. This will not block the DML migration of any sharded tables. The advantage of this mode is that it will not block data migration when processing DDL. However, improper use will cause migration interruption or even data inconsistency. For details, refer to [shard merge in optimistic mode](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-optimistic).
### Contrast

| Pessimistic mode   | Optimistic mode   |
| :----------- | :----------- |
| Sharded tables that executes DDL suspend DML migration | Sharded tables that executes DDL continue DML migration |
| The DDL execution order and statements of each sharded table must be the same | Each sharded table only needs to keep the table schema compatible with each other  |
| The DDL is migrated to the downstream after the entire shard group is consistent | The DDL of each sharded table immediately affects the downstream |
| Wrong DDL operations can be intercepted after the detection | Wrong DDL operations will be migrated to the downstream, which may cause inconsistency between the upstream and downstream data before the detection  |
