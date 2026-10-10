# Pessimistic shard merge overview, restrictions, and background

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/feature-shard-merge-pessimistic.md`
- Source Title: `Merge and Migrate Data from Sharded Tables in the Pessimistic Mode`
- Source Heading Path: `Merge and Migrate Data from Sharded Tables in the Pessimistic Mode | Merge and Migrate Data from Sharded Tables in the Pessimistic Mode > Restrictions | Merge and Migrate Data from Sharded Tables in the Pessimistic Mode > Background`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `sharding`, `ddl`, `table-routing`, `binlog`, `row-format`, `incremental-replication`, `schema-consistency`, `migration-restrictions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0013_90ce91dc4a`
- Source ID: `tidb-docs-8.1:dm/feature-shard-merge-pessimistic.md#merge-and-migrate-data-from-sharded-tables-in-the-pessimistic-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1791577151d4b326751e063f1354ba026110019d9503f79d86b0042d2df26d03`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-pessimistic#merge-and-migrate-data-from-sharded-tables-in-the-pessimistic-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/feature-shard-merge-pessimistic.md

## Retrieval Guidance

- Use When: Use this chunk when you need the overview, restrictions, or background for merging sharded tables into one downstream TiDB table with DM in pessimistic mode.
- Retrieval Keywords: Data Migration (DM), pessimistic mode, sharding group, merge and migrate data from sharded tables, downstream TiDB, upstream MySQL or MariaDB, same table schema, sharding DDL usage restrictions, ROW format binlog, incremental replication, table routing, router-rules, dmctl, DM-worker, DROP DATABASE, DROP TABLE, TRUNCATE TABLE, RENAME TABLE, schema consistency, one task containing exactly the sources of sharded tables
- Follow-up Guidance: The source further explains that with ROW binlog, sharding DDL must be migrated carefully because DML from different upstream tables can temporarily use different schema versions such as schema V1 and schema V2.
- Classification Note: This is classified as a DM data pipeline feature because the content describes self-managed sharded-table migration behavior, DDL restrictions, and schema-consistency handling during incremental replication.

## Official Source Content

# Merge and Migrate Data from Sharded Tables in the Pessimistic Mode

This document introduces the sharding support feature provided by Data Migration (DM) in the pessimistic mode (the default mode). This feature allows you to merge and migrate the data of tables with the same table schema in the upstream MySQL or MariaDB instances into one same table in the downstream TiDB.
## Restrictions

DM has the following sharding DDL usage restrictions in the pessimistic mode:

- For a logical **sharding group** (composed of all sharded tables that need to be merged and migrated into one same downstream table), it is limited to use one task containing exactly the sources of sharded tables to perform the migration.
- In a logical **sharding group**, the same DDL statements must be executed in the same order in all upstream sharded tables (the schema name and the table name can be different), and the next DDL statement cannot be executed unless the current DDL operation is completely finished.
    - For example, if you add `column A` to `table_1` before you add `column B`, then you cannot add `column B` to `table_2` before you add `column A`. Executing the DDL statements in a different order is not supported.
- In a sharding group, the corresponding DDL statements should be executed in all upstream sharded tables.
    - For example, if DDL statements are not executed on one or more upstream sharded tables corresponding to `DM-worker-2`, then other DM-workers that have executed the DDL statements pause their migration task and wait for `DM-worker-2` to receive the upstream DDL statements.
- The sharding group migration task does not support `DROP DATABASE`/`DROP TABLE`.
    - The sync unit in DM-worker automatically ignores the `DROP DATABASE`/`DROP TABLE` statement of upstream sharded tables.
- The sharding group migration task does not support `TRUNCATE TABLE`.
    - The sync unit in DM-worker automatically ignores the `TRUNCATE TABLE` statement of upstream sharded tables.
- The sharding group migration task supports `RENAME TABLE`, but with the following limitations (online DDL is supported in another solution):
    - A table can only be renamed to a new name that is not used by any other table.
    - A single `RENAME TABLE` statement can only involve a single `RENAME` operation.
- The sharding group migration task requires each DDL statement to involve operations on only one table.
- The table schema of each sharded table must be the same at the starting point of the incremental replication task, so as to make sure the DML statements of different sharded tables can be migrated into the downstream with a definite table schema, and the subsequent sharding DDL statements can be correctly matched and migrated.
- If you need to change the [table routing](https://docs.pingcap.com/tidb/stable/dm/dm-table-routing) rule, you have to wait for the migration of all sharding DDL statements to complete.
    - During the migration of sharding DDL statements, an error is reported if you use `dmctl` to change `router-rules`.
- If you need to `CREATE` a new table to a sharding group where DDL statements are being executed, you have to make sure that the table schema is the same as the newly modified table schema.
    - For example, both the original `table_1` and `table_2` have two columns (a, b) initially, and have three columns (a, b, c) after the sharding DDL operation, so after the migration the newly created table should also have three columns (a, b, c).
- Because the DM-worker that has received the DDL statements will pause the task to wait for other DM-workers to receive their DDL statements, the delay of data migration will be increased.
## Background

Currently, DM uses the binlog in the `ROW` format to perform the migration task. The binlog does not contain the table schema information. When you use the `ROW` binlog to migrate data, if you have not migrated multiple upstream tables into the same downstream table, then there only exist DDL operations of one upstream table that can update the table schema of the downstream table. The `ROW` binlog can be considered to have the nature of self-description. During the migration process, the DML statements can be constructed accordingly with the column values and the downstream table schema.

However, in the process of merging and migrating sharded tables, if DDL statements are executed on the upstream tables to modify the table schema, then you need to perform extra operations to migrate the DDL statements so as to avoid the inconsistency between the DML statements produced by the column values and the actual downstream table schema.

Here is a simple example:

![shard-ddl-example-1](/media/dm/shard-ddl-example-1.png)

In the above example, the merging process is simplified, where only two MySQL instances exist in the upstream and each instance has only one table. When the migration begins, the table schema version of two sharded tables is marked as `schema V1`, and the table schema version after executing DDL statements is marked as `schema V2`.

Now assume that in the migration process, the binlog data received from the two upstream sharded tables has the following time sequence:

1. When the migration begins, the sync unit in DM-worker receives the DML events of `schema V1` from the two sharded tables.
2. At `t1`, the sharding DDL events from instance 1 are received.
3. From `t2` on, the sync unit receives the DML events of `schema V2` from instance 1; but from instance 2, it still receives the DML events of `schema V1`.
4. At `t3`, the sharding DDL events from instance 2 are received.
5. From `t4` on, the sync unit receives the DML events of `schema V2` from instance 2 as well.

Assume that the DDL statements of sharded tables are not processed during the migration process. After DDL statements of instance 1 are migrated to the downstream, the downstream table schema is changed to `schema V2`. But for instance 2, the sync unit in DM-worker is still receiving DML events of `schema V1` from `t2` to `t3`. Therefore, when the DML statements of `schema V1` are migrated to the downstream, the inconsistency between the DML statements and the table schema can cause errors and the data cannot be migrated successfully.
