# DM precheck items for incremental and all-mode migration

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-precheck.md`
- Source Title: `Migration Task Precheck`
- Source Heading Path: `Migration Task Precheck > Descriptions of check items > Check items for incremental data migration | Migration Task Precheck > Descriptions of check items > Check items for full and incremental data migration`
- Source Line Ranges: `116-141`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `incremental-migration`, `replication-permissions`, `server-id`, `gtid`, `binlog`, `row-format`, `row-image`, `binlog-filters`, `online-ddl`, `task-mode-all`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0102_de81616bff`
- Source ID: `tidb-docs-8.1:dm/dm-precheck.md#check-items-for-incremental-data-migration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `86355694b5e9db7f25fc3449962a99d956746b768f7c2e8225d870d001f9588d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-precheck#check-items-for-incremental-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-precheck.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks which precheck items apply to incremental migration or `task-mode: all`, especially replication permissions, `server_id`, GTID, binlog settings, and online DDL checks.
- Retrieval Keywords: Check items for incremental data migration, task-mode: incremental, REPLICATION CLIENT permission, REPLICATION SLAVE permission, server_id, GTID, MySQL binlog configuration, binlog is enabled, binlog_format=ROW, binlog_row_image=FULL, binlog_do_db, binlog_ignore_db, Online-DDL, ghost table, rename phase, task-mode: all, full and incremental data migration
- Follow-up Guidance: For `task-mode: all`, the content states that DM includes both the full data migration check items and the incremental data migration check items in addition to the common check items.
- Classification Note: Classified as an operation chunk because it defines the mandatory and recommended prechecks DM performs for incremental replication and combined full-plus-incremental migration modes.

## Official Source Content

### Check items for incremental data migration

For the incremental data migration mode (`task-mode: incremental`), in addition to the [common check items](#common-check-items), the precheck also includes the following check items:

* (Mandatory) Upstream database REPLICATION permission

    - REPLICATION CLIENT permission
    - REPLICATION SLAVE permission

* Database primary-secondary configuration

    - To avoid primary-secondary replication failures, it is recommended that you specify the database ID `server_id` for the upstream database (GTID is recommended for non-AWS Aurora environments).

* (Mandatory) MySQL binlog configuration

    - Check whether binlog is enabled (required by DM).
    - Check whether `binlog_format=ROW` is configured (DM only supports the migration of binlog in the ROW format).
    - Check whether `binlog_row_image=FULL` is configured (DM only supports `binlog_row_image=FULL`).
    - If `binlog_do_db` or `binlog_ignore_db` is configured, check whether the database tables to be migrated meet the conditions of `binlog_do_db` and `binlog_ignore_db`.

* (Mandatory) Check if the upstream database is in an [Online-DDL](https://docs.pingcap.com/tidb/stable/dm/feature-online-ddl) process (in which the `ghost` table is created but the `rename` phase is not executed yet). If the upstream is in the online-DDL process, the precheck returns an error. In this case, wait until the DDL to complete and retry.
### Check items for full and incremental data migration

For the full and incremental data migration mode (`task-mode: all`), in addition to the [common check items](#common-check-items), the precheck also includes the [full data migration check items](#check-items-for-full-data-migration) and the [incremental data migration check items](#check-items-for-incremental-data-migration).
