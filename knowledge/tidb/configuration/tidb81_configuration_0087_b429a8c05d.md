# Optimistic sharding mode overview, configuration, and restrictions

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/feature-shard-merge-optimistic.md`
- Source Title: `Merge and Migrate Data from Sharded Tables in Optimistic Mode`
- Source Heading Path: `Merge and Migrate Data from Sharded Tables in Optimistic Mode | Merge and Migrate Data from Sharded Tables in Optimistic Mode > Background | Merge and Migrate Data from Sharded Tables in Optimistic Mode > Configuration of the optimistic mode | Merge and Migrate Data from Sharded Tables in Optimistic Mode > Restrictions`
- Source Line Ranges: `5-65`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `optimistic mode`, `sharding ddl`, `task configuration`, `strict optimistic shard mode`, `restrictions`, `type 1 ddl`, `type 2 ddl`, `data consistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0087_b429a8c05d`
- Source ID: `tidb-docs-8.1:dm/feature-shard-merge-optimistic.md#merge-and-migrate-data-from-sharded-tables-in-optimistic-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `60b23ab0be019618a4695a056a1fc523ab35279562f38b46f664a5f8cb1a81bd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-optimistic#merge-and-migrate-data-from-sharded-tables-in-optimistic-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/feature-shard-merge-optimistic.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about enabling DM optimistic sharding mode, its restrictions, Type 1 versus Type 2 DDL, or the effect of strict optimistic shard mode on sharded DDL migration.
- Retrieval Keywords: shard-mode optimistic, strict-optimistic-shard-mode, optimistic mode, pessimistic mode, Type 1 DDL, Type 2 DDL, ALTER TABLE table_name MODIFY COLUMN column_name VARCHAR(20), ALTER TABLE table_name RENAME COLUMN column_1 TO column_2, ALTER TABLE table_name ADD COLUMN column_1 NOT NULL, ALTER TABLE table_name RENAME INDEX index_1 TO index_2, DROP TABLE not supported, DROP DATABASE not supported, TRUNCATE TABLE not supported, current_timestamp rand() uuid() default value
- Follow-up Guidance: The document also describes risks of optimistic mode misuse and the implementation principle involving DM-worker, DM-master, and composite schema merging.
- Classification Note: This is classified as configuration because the content centers on setting `shard-mode` to `optimistic`, optionally enabling `strict-optimistic-shard-mode`, and the documented restrictions that govern task behavior.

## Official Source Content

# Merge and Migrate Data from Sharded Tables in Optimistic Mode

This document introduces the sharding support feature provided by Data Migration (DM) in the optimistic mode. This feature allows you to merge and migrate the data of tables with the same or different table schema(s) in the upstream MySQL or MariaDB instances into one same table in the downstream TiDB.

> **Note:**
>
> If you do not have an in-depth understanding of the optimistic mode and its restrictions, it is **NOT** recommended to use this mode. Otherwise, migration interruption or even data inconsistency might occur.
## Background

DM supports executing DDL statements on sharded tables online, which is called sharding DDL, and uses the "pessimistic mode" by default. In this mode, when a DDL statement is executed in an upstream sharded table, data migration of this table is paused until the same DDL statement is executed in all other sharded tables. Only by then this DDL statement is executed in the downstream and data migration resumes.

The pessimistic mode guarantees that the data migrated to the downstream is always correct, but it pauses the data migration, which is bad for making A/B changes in the upstream. In some cases, users might spend a long time executing DDL statements in a single sharded table and change the schemas of other sharded tables only after a period of validation. In the pessimistic mode, these DDL statements block data migration and cause many binlog events to pile up.

Therefore, an "optimistic mode" is needed. In this mode, a DDL statement executed on a sharded table is automatically converted to a statement that is compatible with other sharded tables, and then immediately migrated to the downstream. In this way, the DDL statement does not block any sharded table from executing DML migration.
## Configuration of the optimistic mode

To use the optimistic mode, specify the `shard-mode` item in the task configuration file as `optimistic`. You can restrict the behavior of the optimistic mode by enabling the `strict-optimistic-shard-mode` configuration. For the detailed sample configuration file, see [DM Advanced Task Configuration File](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full).
## Restrictions

It takes some risks to use the optimistic mode. Follow these rules when you use it:

- Ensure that the schema of every sharded table is consistent with each other before and after you execute a batch of DDL statements.
- If you perform an A/B test, perform the test **ONLY** on one sharded table.
- After the A/B test is finished, migrate only the most direct DDL statement(s) to the final schema. Do not re-execute every right or wrong step of the test.

    For example, if you have executed `ADD COLUMN A INT; DROP COLUMN A; ADD COLUMN A FLOAT;` in a sharded table, you only need to execute `ADD COLUMN A FLOAT` in other sharded tables. You do not need to execute all of the three DDL statements again.

- Observe the status of the DM migration when executing the DDL statement. When an error is reported, you need to determine whether this batch of DDL statements will cause data inconsistency.

In the optimistic mode, most of the DDL statements executed in the upstream are automatically migrated to the downstream with no extra effort required. These DDL statements are called "Type 1 DDL".

DDL statements that change the column name, the column type, or the column default value are called "Type 2 DDL". When you execute Type 2 DDL statements in the upstream, make sure that you execute the DDL statements in all sharded tables in the same order.

Some examples of Type 2 DDL statements are as follows:

- Alter the type of a column: `ALTER TABLE table_name MODIFY COLUMN column_name VARCHAR(20)`.
- Rename a column: `ALTER TABLE table_name RENAME COLUMN column_1 TO column_2;`.
- Add a `NOT NULL` column without a default value: `ALTER TABLE table_name ADD COLUMN column_1 NOT NULL;`.
- Rename an index: `ALTER TABLE table_name RENAME INDEX index_1 TO index_2;`.

When the sharded tables execute the DDL statements above, if `strict-optimistic-shard-mode: true` is set, the task is directly interrupted and an error is reported. If `strict-optimistic-shard-mode: false` is set or not specified, different execution order of the DDL statements in sharded tables will cause migration interruption. For example:

- Shard 1 renames a column and then alters the column type:
    1. Rename a column: `ALTER TABLE table_name RENAME COLUMN column_1 TO column_2;`.
    2. Alter the column type: `ALTER TABLE table_name MODIFY COLUMN column_3 VARCHAR(20);`.
- Shard 2 alters a column type and then renames the column:
    1. Alter a column type: `ALTER TABLE table_name MODIFY COLUMN column_3 VARCHAR(20)`.
    2. Rename a column: `ALTER TABLE table_name RENAME COLUMN column_1 TO column_2;`.

In addition, the following restrictions apply to both the optimistic mode and the pessimistic mode:

- `DROP TABLE` or `DROP DATABASE` is not supported.
- `TRUNCATE TABLE` is not supported.
- Each DDL statement must involve operations on only one table.
- The DDL statement that is not supported in TiDB is also not supported in DM.
- The default value of a newly added column must not contain `current_timestamp`, `rand()`, `uuid()`; otherwise, data inconsistency between the upstream and the downstream might occur.
