# Shard merge task isolation, DDL lock handling, and primary key conflict solutions

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/shard-merge-best-practices.md`
- Source Title: `Best Practices of Data Migration in the Shard Merge Scenario`
- Source Heading Path: `Best Practices of Data Migration in the Shard Merge Scenario | Best Practices of Data Migration in the Shard Merge Scenario > Use a separate data migration task | Best Practices of Data Migration in the Shard Merge Scenario > Handle sharding DDL locks manually | Best Practices of Data Migration in the Shard Merge Scenario > Handle conflicts between primary keys or unique indexes across multiple sharded tables | Best Practices of Data Migration in the Shard Merge Scenario > Handle conflicts of auto-increment primary key | Best Practices of Data Migration in the Shard Merge Scenario > Handle conflicts of auto-increment primary key > Remove the `PRIMARY KEY` attribute from the column | Best Practices of Data Migration in the Shard Merge Scenario > Handle conflicts of auto-increment primary key > Use a composite primary key`
- Source Line Ranges: `5-119`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `sql`, `tidb`
- Topic Tags: `shard-merge`, `migration-tasks`, `ddl-locks`, `manual-handling`, `primary-key-conflicts`, `unique-index-conflicts`, `auto-increment`, `task-configuration`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0016_bd4c0d6444`
- Source ID: `tidb-docs-8.1:dm/shard-merge-best-practices.md#best-practices-of-data-migration-in-the-shard-merge-scenario`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e3cb3409c500ca46d6944f2ddfffb8db3584d68e4ad45a58a7b3664657874c04`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/shard-merge-best-practices#best-practices-of-data-migration-in-the-shard-merge-scenario
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/shard-merge-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when you need DM shard merge guidance about separate migration tasks, sharding DDL lock handling, or resolving `ERROR 1062 (23000): Duplicate entry '***' for key 'PRIMARY'` caused by primary key, unique index, or auto-increment conflicts.
- Retrieval Keywords: sharding group, separate data migration task, pessimistic mode, sharding DDL lock, DM-master, DM-worker, shard-ddl-lock, shard-ddl-lock unlock, query-status, unresolvedGroups, blockingDDLs, manually handling sharding DDL locks, dm_meta, auto_increment_ID, task.yaml, ERROR 1062 (23000): Duplicate entry for key 'PRIMARY', PRIMARY KEY, UNIQUE KEY, auto-increment primary key, composite primary key, CREATE TABLE `tbl_no_pk_2`, CREATE TABLE `tbl_multi_pk_c2`
- Follow-up Guidance: The content also says to run `query-status` to verify whether the data migration task is successfully processed and whether upstream data has been merged and migrated to the downstream database.
- Classification Note: This is classified as data_pipeline because the content focuses on DM shard merge migration task design, lock coordination, and schema strategies for merging sharded data into downstream tables.

## Official Source Content

# Best Practices of Data Migration in the Shard Merge Scenario

This document describes the features and limitations of [TiDB Data Migration (DM)](https://docs.pingcap.com/tidb/stable/dm/dm-overview) in the shard merge scenario and provides a data migration best practice guide for your application (the default "pessimistic" mode is used).
## Use a separate data migration task

In the [Merge and Migrate Data from Sharded Tables](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-pessimistic#principles) document, the definition of "sharding group" is given: A sharding group consists of all upstream tables that need to be merged and migrated into the same downstream table.

The current sharding DDL mechanism has some [usage restrictions](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-pessimistic#restrictions) to coordinate the schema changes brought by DDL operations in different sharded tables. If these restrictions are violated due to unexpected reasons, you need to [handle sharding DDL locks manually in DM](https://docs.pingcap.com/tidb/stable/dm/manually-handling-sharding-ddl-locks), or even redo the entire data migration task.

To mitigate the impact on data migration when an exception occurs, it is recommended to merge and migrate each sharding group as a separate data migration task. **This might enable that only a small number of data migration tasks need to be handled manually while others remain unaffected.**
## Handle sharding DDL locks manually

You can easily conclude from [Merge and Migrate Data from Sharded Tables](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-pessimistic#principles) that DM's sharding DDL lock is a mechanism for coordinating the execution of DDL operations to the downstream from multiple upstream sharded tables.

Therefore, when you find any sharding DDL lock on `DM-master` through `shard-ddl-lock` command, or any `unresolvedGroups` or `blockingDDLs` on some DM-workers through `query-status` command, do not rush to manually release the sharding DDL lock through `shard-ddl-lock unlock` commands.

Instead, you can:

- Follow the corresponding manual solution to handle the scenario if the failure of automatically releasing the sharding DDL lock is one of the [listed abnormal scenarios](https://docs.pingcap.com/tidb/stable/dm/manually-handling-sharding-ddl-locks#supported-scenarios).
- Redo the entire data migration task if it is an unsupported scenario: First, empty the data in the downstream database and the `dm_meta` information associated with the migration task; then, re-execute the full and incremental data replication.
## Handle conflicts between primary keys or unique indexes across multiple sharded tables

Data from multiple sharded tables might cause conflicts between the primary keys or unique indexes. You need to check each primary key or unique index based on the sharding logic of these sharded tables. The following are three cases related to primary keys or unique indexes:

- Shard key: Usually, the same shard key only exists in one sharded table, which means no data conflict is caused on shard key.
- Auto-increment primary key: The auto-increment primary key of each sharded tables counts separately, so their range might overlap. In this case, you need to refer to the next section [Handle conflicts of auto-increment primary key](https://docs.pingcap.com/tidb/stable/dm/shard-merge-best-practices#handle-conflicts-of-auto-increment-primary-key) to solve it.
- Other primary keys or unique indexes: you need to analyze them based on the business logic. If data conflict, you can also refer to the next section [Handle conflicts of auto-increment primary key](https://docs.pingcap.com/tidb/stable/dm/shard-merge-best-practices#handle-conflicts-of-auto-increment-primary-key) to solve it.
## Handle conflicts of auto-increment primary key

This section introduces two recommended solutions to handle conflicts of auto-increment primary key.
### Remove the `PRIMARY KEY` attribute from the column

Assume that the upstream schemas are as follows:

```sql
CREATE TABLE `tbl_no_pk` (
  `auto_pk_c1` bigint(20) NOT NULL,
  `uk_c2` bigint(20) NOT NULL,
  `content_c3` text,
  PRIMARY KEY (`auto_pk_c1`),
  UNIQUE KEY `uk_c2` (`uk_c2`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
```

If the following requirements are satisfied:

- The `auto_pk_c1` column has no impact on the application and does not depend on the column's `PRIMARY KEY` attribute.
- The `uk_c2` column has the `UNIQUE KEY` attribute, and it is globally unique in all upstream sharded tables.

Then you can perform the following steps to fix the `ERROR 1062 (23000): Duplicate entry '***' for key 'PRIMARY'` error that is possibly caused by the `auto_pk_c1` column when you merge sharded tables.

1. Before the full data migration, create a table in the downstream database for merging and migrating data, and modify the `PRIMARY KEY` attribute of the `auto_pk_c1` column to normal index.

    ```sql
    CREATE TABLE `tbl_no_pk_2` (
      `auto_pk_c1` bigint(20) NOT NULL,
      `uk_c2` bigint(20) NOT NULL,
      `content_c3` text,
      INDEX (`auto_pk_c1`),
      UNIQUE KEY `uk_c2` (`uk_c2`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    ```

2. Add the following configuration in `task.yaml` to skip the check of auto-increment primary key conflict:

    ```yaml
    ignore-checking-items: ["auto_increment_ID"]
    ```

3. Start the full and incremental data replication task.

4. Run `query-status` to verify whether the data migration task is successfully processed and whether the data from the upstream has already been merged and migrated to the downstream database.
### Use a composite primary key

Assume that the upstream schemas are as follows:

```sql
CREATE TABLE `tbl_multi_pk` (
  `auto_pk_c1` bigint(20) NOT NULL,
  `uuid_c2` bigint(20) NOT NULL,
  `content_c3` text,
  PRIMARY KEY (`auto_pk_c1`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
```

If the following requirements are satisfied:

* The application does not depend on the `PRIMARY KEY` attribute of the `auto_pk_c1` column.
* The composite primary key that consists of the `auto_pk_c1` and `uuid_c2` columns is globally unique.
* It is acceptable to use a composite primary key in the application.

Then you can perform the following steps to fix the `ERROR 1062 (23000): Duplicate entry '***' for key 'PRIMARY'` error that is possibly caused by the `auto_pk_c1` column when you merge sharded tables.

1. Before the full data migration, create a table in the downstream database for merging and migrating data. Do not specify the `PRIMARY KEY` attribute for the `auto_pk_c1` column, but use the `auto_pk_c1` and `uuid_c2` columns to make up a composite primary key.

    ```sql
    CREATE TABLE `tbl_multi_pk_c2` (
      `auto_pk_c1` bigint(20) NOT NULL,
      `uuid_c2` bigint(20) NOT NULL,
      `content_c3` text,
      PRIMARY KEY (`auto_pk_c1`,`uuid_c2`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    ```

2. Start the full and incremental data migration task.

3. Run `query-status` to verify whether the data migration task is successfully processed and whether the data from upstream has already been merged and migrated to the downstream database.
