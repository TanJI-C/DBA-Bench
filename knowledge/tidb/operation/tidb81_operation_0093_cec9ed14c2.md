# DM binlog-schema overview, principles, command, and parameters

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-manage-schema.md`
- Source Title: `Manage Table Schemas of Tables to Be Migrated Using TiDB Data Migration`
- Source Heading Path: `Manage Table Schemas of Tables to Be Migrated Using TiDB Data Migration | Manage Table Schemas of Tables to Be Migrated Using TiDB Data Migration > Implementation principles | Manage Table Schemas of Tables to Be Migrated Using TiDB Data Migration > Command | Manage Table Schemas of Tables to Be Migrated Using TiDB Data Migration > Parameters`
- Source Line Ranges: `5-88`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `schema-tracker`, `incremental-replication`, `full-migration`, `binlog`, `ddl`, `paused-state`, `backup`, `parameters`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0093_cec9ed14c2`
- Source ID: `tidb-docs-8.1:dm/dm-manage-schema.md#manage-table-schemas-of-tables-to-be-migrated-using-tidb-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1d09a93ac00242a3718026c5c99229d56ae9d4d64896a8a531300d5d0642e189`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-manage-schema#manage-table-schemas-of-tables-to-be-migrated-using-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-manage-schema.md

## Retrieval Guidance

- Use When: Use this chunk when you need the purpose, schema-tracker principles, command syntax, and constraints of the DM `binlog-schema` command for managing internal table schema during migration.
- Retrieval Keywords: binlog-schema, dmctl binlog-schema, schema tracker, internal table schema, schema-I, schema-U, schema-B, schema-D, incremental replication, task-mode=all, task-mode=incremental, ALTER TABLE, Column count doesn't match value count, Paused state, backup the table schema, operate-schema, --source, -s, MySQL Source ID
- Follow-up Guidance: It also points to the `list`, `update`, and `delete` subcommands and notes that the command can be used only when the data migration task is in the `Paused` state.
- Classification Note: This is classified as an operation chunk because the official content explains how DM maintains internal table schemas and gives the `dmctl binlog-schema` command, subcommands, parameters, and usage constraints.

## Official Source Content

# Manage Table Schemas of Tables to Be Migrated Using TiDB Data Migration

This document describes how to manage the schema of the table in DM during migration using [dmctl](https://docs.pingcap.com/tidb/stable/dm/dmctl-introduction).

When DM performs incremental replication, it first reads the upstream binlog, then creates SQL statements and executes them in the downstream. However, the upstream binlog does not contain the complete table schema. To generate the SQL statements, DM maintains internally the schema information of the table to be migrated. This is called the internal table schema.

To deal with some special occasions, or to handle migration interruptions caused by mismatch of the table schemas, DM provides the `binlog-schema` command to obtain, modify, and delete the internal table schema.
## Implementation principles

The internal table schema comes from the following sources:

- For full data migration (`task-mode=all`), the migration task goes through three stages: dump/load/sync, which means full export, full import, and incremental replication. In the dump stage, DM exports the table schema information along with the data and automatically creates the corresponding table in the downstream. In the sync stage, this table schema is used as the starting table scheme for incremental replication.
- In the sync stage, when DM handles DDL statements such as `ALTER TABLE`, it updates the internal table schema at the same time.
- If the task is an incremental migration (`task-mode=incremental`), in which the downstream has completed creating the table to be migrated, DM obtains the table schema information from the downstream database. This behavior varies with DM versions.

For incremental replication, schema maintenance is complicated. During the whole data replication, the following four table schemas are involved. These schemas might be the consistent or inconsistent with one another:

![schema](/media/dm/operate-schema.png)

* The upstream table schema at the current time, identified as `schema-U`.
* The table schema of the binlog event currently being consumed by DM, identified as `schema-B`. This schema corresponds to the upstream table schema at a historical time.
* The table schema currently maintained in DM (the schema tracker component), identified as `schema-I`.
* The table schema in the downstream TiDB cluster, identified as `schema-D`.

In most cases, the preceding four table schemas are consistent.

When the upstream database performs a DDL operation to change the table schema, `schema-U` is changed. By applying the DDL operation to the internal schema tracker component and the downstream TiDB cluster, DM updates `schema-I` and `schema-D` in an orderly manner to keep them consistent with `schema-U`. Therefore, DM can then normally consume the binlog event corresponding to the `schema-B` table schema. That is, after the DDL operation is successfully migrated, `schema-U`, `schema-B`, `schema-I`, and `schema-D` are still consistent.

Note the following situations that might cause inconsistency:

- During the migration with [optimistic mode sharding DDL support](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-optimistic) enabled, the `schema-D` of the downstream table might be inconsistent with the `schema-B` and `schema-I` of some upstream sharded tables. In such cases, DM still keeps `schema-I` and `schema-B` consistent to ensure that the binlog event corresponding to DML can be parsed normally.

- When the downstream table has more columns than the upstream table, `schema-D` might be inconsistent with `schema-B` and `schema-I`. In the full data migration (`task-mode=all`), DM automatically handles inconsistency. In the incremental migration (`task-mode=incremental`), because the task is on a first start and there is no internal schema information yet, DM automatically reads the downstream schema (`schema-D`) and updates `schema-I` (this behavior varies with DM versions). After that, if DM uses `schema-I` to parse `schema-B`'s binlog, it will report `Column count doesn't match value count` error. For details, refer to [Migrate Data to a Downstream TiDB Table with More Columns](https://docs.pingcap.com/tidb/stable/migrate-with-more-columns-downstream).

You can run the `binlog-schema` command to obtain, modify, or delete the `schema-I` table schema maintained in DM.

> **Note:**
>
> The `binlog-schema` command is supported only in DM v6.0 or later versions. For earlier versions, you must use the `operate-schema` command.
## Command

```bash
help binlog-schema
```

```
manage or show table schema in schema tracker

Usage:
  dmctl binlog-schema [command]

Available Commands:
  delete      delete table schema structure
  list        show table schema structure
  update      update tables schema structure

Flags:
  -h, --help   help for binlog-schema

Global Flags:
  -s, --source strings   MySQL Source ID.

Use "dmctl binlog-schema [command] --help" for more information about a command.
```

> **Note:**
>
> - Because a table schema might change during data migration, to obtain a predictable table schema, currently the `binlog-schema` command can be used only when the data migration task is in the `Paused` state.
> - To avoid data loss due to mishandling, it is **strongly recommended** to get and backup the table schema firstly before you modify the schema.
## Parameters

* `delete`: Deletes the table schema.
* `list`: Lists the table schema.
* `update`: Updates the table schema.
* `-s` or `--source`:
    - Required.
    - Specifies the MySQL source that the operation is applied to.
