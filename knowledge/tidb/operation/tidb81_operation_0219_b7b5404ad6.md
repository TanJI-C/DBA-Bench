# Smooth upgrade limitations for operations, tools, and plugins

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/smooth-upgrade-tidb.md`
- Source Title: `TiDB Smooth Upgrade`
- Source Heading Path: `TiDB Smooth Upgrade > Limitations | TiDB Smooth Upgrade > Limitations > Limitations on user operations | TiDB Smooth Upgrade > Limitations > Limitations on tools | TiDB Smooth Upgrade > Limitations > Limitation on plugins`
- Source Line Ranges: `72-105`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiup`, `br`, `dm`, `ticdc`
- Topic Tags: `limitations`, `ddl`, `dxf`, `dist-task`, `add-index`, `import-into`, `tool-compatibility`, `plugins`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0219_b7b5404ad6`
- Source ID: `tidb-docs-8.1:smooth-upgrade-tidb.md#limitations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `588b6e1da9136258127ed5ac4fa82721d58d5850764f02977da47e711cdb2301`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/smooth-upgrade-tidb#limitations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/smooth-upgrade-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when identifying smooth upgrade limitations that affect DDL jobs, DXF distributed tasks, TiUP timeout behavior, external tools, or plugins during a TiDB upgrade.
- Retrieval Keywords: Limitations, canceling DDL job, error is reported and the upgrade is exited, TiDB Distributed eXecution Framework, DXF, tidb_enable_dist_task, OFF, ADD INDEX, IMPORT INTO, more than 300, DDL jobs waiting in queues, system tables, mysql.*, information_schema.*, performance_schema.*, metrics_schema.*, ADMIN CANCEL DDL JOBS, BR, DM, TiCDC, plugins
- Follow-up Guidance: The content also states that these limitations apply not only to scenarios using the smooth upgrade feature, but also to upgrading TiDB using TiUP.
- Classification Note: This is classified as an operation chunk because it documents upgrade-time restrictions on user operations, compatibility limits for TiUP, BR, DM, and TiCDC, and plugin-related DDL behavior.

## Official Source Content

## Limitations

When using the smooth upgrade feature, note the following limitations.

> **Note:**
>
> The limitations in this section apply not only to scenarios using the smooth upgrade feature, but also to [upgrading TiDB using TiUP](https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup#upgrade-tidb-using-tiup).
### Limitations on user operations

* Before the upgrade, consider the following restrictions:

    * If there is a canceling DDL job in the cluster, that is, an ongoing DDL job is being canceled by a user, because the job in the canceling state cannot be paused, TiDB will retry canceling the job. If the retry fails, an error is reported and the upgrade is exited.
    * If your current TiDB version is earlier than v8.1.0 and the TiDB Distributed eXecution Framework (DXF) is enabled, disable it by setting [`tidb_enable_dist_task`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_dist_task-new-in-v710) to `OFF`. Make sure that all ongoing distributed `ADD INDEX` and `IMPORT INTO` tasks are completed. Alternatively, you can cancel these tasks and wait until the upgrade is complete to restart them. Otherwise, the `ADD INDEX` operations during the upgrade might cause data index inconsistency. If your current TiDB version is v8.1.0 or later, you do not need to disable the DXF, and you can just ignore this limitation.

* In scenarios of using TiUP to upgrade TiDB, because TiUP upgrade has a timeout period, if the cluster has a large number of DDL jobs (more than 300) waiting in queues before the upgrade, the upgrade might fail.

* During the upgrade, the following operations are not allowed:

    * Run DDL operations on system tables (`mysql.*`, `information_schema.*`, `performance_schema.*`, and `metrics_schema.*`).
    * Manually cancel DDL jobs: `ADMIN CANCEL DDL JOBS job_id [, job_id] ...;`.
    * Import data.
### Limitations on tools

* During the upgrade, use of the following tools is not supported:

    * BR: BR might replicate the paused DDL jobs to TiDB. The paused DDL jobs cannot be automatically resumed, which might cause the DDL jobs to be stuck later.

    * DM and TiCDC: If you use DM or TiCDC to import SQL statements to TiDB during the upgrade process, and if one of the SQL statements contains DDL operations, the import operation is blocked and undefined errors might occur.
### Limitation on plugins

The plugins installed in TiDB might contain DDL operations. However, during the upgrade, if the DDL operations in the plugins are performed on non-system tables, the upgrade might fail.
