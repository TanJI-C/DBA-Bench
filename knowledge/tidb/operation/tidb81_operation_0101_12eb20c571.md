# DM precheck items for common, full migration, and physical import

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-precheck.md`
- Source Title: `Migration Task Precheck`
- Source Heading Path: `Migration Task Precheck > Descriptions of check items > Common check items | Migration Task Precheck > Descriptions of check items > Check items for full data migration | Migration Task Precheck > Descriptions of check items > Check items for full data migration > Check items for physical import`
- Source Line Ranges: `38-115`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `lightning`, `pd`, `tikv`, `tidb`, `ticdc`, `br`
- Topic Tags: `database-version`, `schema-compatibility`, `foreign-keys`, `character-sets`, `primary-keys`, `dump-permissions`, `sharding`, `optimistic-ddl`, `pessimistic-ddl`, `auto-increment`, `physical-import`, `empty-regions`, `region-balance`, `version-compatibility`, `free-space`, `task-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0101_12eb20c571`
- Source ID: `tidb-docs-8.1:dm/dm-precheck.md#common-check-items`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e0d0f66773aa4711c3c18d16c4a5ccdb89d67524961530f3d6ce8b70cc528517`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-precheck#common-check-items
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-precheck.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks which DM precheck items apply to common checks, full migration, or physical import, including schema compatibility, permissions, sharding consistency, and downstream physical import requirements.
- Retrieval Keywords: Common check items, Database version, MySQL version > 5.5, MariaDB version >= 10.1.2, Compatibility of the upstream MySQL table schema, foreign keys, character sets, primary key constraints, unique key constraints, task-mode: full, dump permission of the upstream database, SELECT permission on INFORMATION_SCHEMA, RELOAD permission if consistency=flush, LOCK TABLES permission if consistency=flush/lock, Consistency of upstream MySQL multi-instance sharding tables, pessimistic mode, optimistic mode, optimistic compatibility, start-task, Auto-increment primary key in sharded tables, import-mode: "physical", Empty Regions in the downstream database, Region distribution in the downstream database, The versions of TiDB, PD, and TiKV in the downstream database, The free space of the downstream database, TiCDC, PITR, physical import
- Follow-up Guidance: For `import-mode: "physical"`, the content also lists warning and error conditions for empty Regions, Region distribution, downstream TiDB/PD/TiKV version compatibility, free space, and incompatible running tasks such as TiCDC and PITR.
- Classification Note: Classified as an operation chunk because it enumerates DM precheck items and result conditions for common checks, `task-mode: full`, and `import-mode: "physical"` task validation.

## Official Source Content

### Common check items

Regardless of the migration mode you choose, the precheck always includes the following common check items:

- Database version

    - MySQL version > 5.5
    - MariaDB version >= 10.1.2

    > **Warning:**
    >
    > - Migrating data from MySQL 8.0 to TiDB using DM is an experimental feature (introduced since DM v2.0). It is NOT recommended that you use it in a production environment.
    > - Migrating data from MariaDB to TiDB using DM is an experimental feature. It is NOT recommended that you use it in a production environment.

- Compatibility of the upstream MySQL table schema

    - Check whether the upstream tables have foreign keys, which are not supported by TiDB. A warning is returned if a foreign key is found in the precheck.
    - Check whether the upstream tables use character sets that are incompatible with TiDB. For more information, see [TiDB Supported Character Sets](https://docs.pingcap.com/tidb/stable/character-set-and-collation).
    - Check whether the upstream tables have primary key constraints or unique key constraints (introduced from v1.0.7).

    > **Warning:**
    >
    > - When the upstream uses incompatible character sets, you can still continue the replication by creating tables with the utf8mb4 character set in the downstream. However, this practice is not recommended. You are advised to replace the incompatible character set used by the upstream with another character set that is supported in downstream.
    > - When the upstream tables have no primary key constraints or unique key constraints, the same row of data might be replicated multiple times to the downstream, which might also affect the performance of replication. In a production environment, it is recommended that you specify primary key constraints or unique key constraints for the upstream table.
### Check items for full data migration

For the full data migration mode (`task-mode: full`), in addition to the [common check items](#common-check-items), the precheck also includes the following check items:

* (Mandatory) dump permission of the upstream database

    - SELECT permission on INFORMATION_SCHEMA and dump tables
    - RELOAD permission if `consistency=flush`
    - LOCK TABLES permission on the dump tables if `consistency=flush/lock`

* (Mandatory) Consistency of upstream MySQL multi-instance sharding tables

    - In the pessimistic mode, check whether the table schemas of all sharded tables are consistent in the following items:

        - Number of columns
        - Column name
        - Column order
        - Column type
        - Primary key
        - Unique index

    - In the optimistic mode, check whether the schemas of all sharded tables meet the [optimistic compatibility](https://github.com/pingcap/tiflow/blob/release-8.1/dm/docs/RFCS/20191209_optimistic_ddl.md#modifying-column-types).

    - If a migration task was started successfully by the `start-task` command, the precheck of this task skips the consistency check.

* Auto-increment primary key in sharded tables

    - If sharded tables have auto-increment primary keys, the precheck returns a warning. If there are conflicts in auto-increment primary keys, see [Handle conflicts of auto-increment primary key](https://docs.pingcap.com/tidb/stable/dm/shard-merge-best-practices#handle-conflicts-of-auto-increment-primary-key) for solutions.
#### Check items for physical import

If you set `import-mode: "physical"` in the task configuration, the following check items are added to ensure that [Physical Import](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode) runs normally. After following the prompts, if you find it difficult to meet the requirements of these check items, you can try to use the [logical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode) to import data.

* Empty Regions in the downstream database

    - If the number of empty Regions is greater than `max(1000, 3 * the number of tables)` (the larger of "1000" and "3 times the number of tables"), the precheck returns a warning. You can adjust related PD parameters to speed up the merging of empty Regions and wait for the number of empty Regions to decrease. See [PD Scheduling Best Practices - Slow Region Merge](https://docs.pingcap.com/tidb/stable/best-practices/pd-scheduling-best-practices#region-merge-is-slow).

* Region distribution in the downstream database

    - Checks the number of Regions on different TiKV nodes. Assuming that the TiKV node with the lowest Region count has `a` Regions and the TiKV node with the highest Region count has `b` Regions, if `a / b` is less than 0.75, the precheck returns a warning. You can adjust related PD parameters to speed up the scheduling of Regions and wait for the number of Regions to change. See [PD Scheduling Best Practices - Leader/Region distribution is not balanced](https://docs.pingcap.com/tidb/stable/best-practices/pd-scheduling-best-practices#leadersregions-are-not-evenly-distributed).

* The versions of TiDB, PD, and TiKV in the downstream database

    - Physical import must call the interfaces of TiDB, PD, and TiKV. If the versions are not compatible, the precheck returns an error.

* The free space of the downstream database

    - Estimates the total sizes of all tables in the allow list in the upstream database (`source_size`). If the free space of the downstream database is less than `source_size`, the precheck returns an error. If the free space of the downstream database is less than the number of TiKV replicas \* `source_size` \* 2, the precheck returns a warning.

* Whether the downstream database is running tasks that are incompatible with physical import

    - Currently, physical import is incompatible with [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) and [PITR](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) tasks. If these tasks are running in the downstream database, the precheck returns an error.
