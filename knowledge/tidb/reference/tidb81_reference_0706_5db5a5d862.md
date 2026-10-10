# Overview, features, restrictions, and required privileges

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sync-diff-inspector/sync-diff-inspector-overview.md`
- Source Title: `sync-diff-inspector User Guide`
- Source Heading Path: `sync-diff-inspector User Guide | sync-diff-inspector User Guide > Key features | sync-diff-inspector User Guide > Restrictions of sync-diff-inspector | sync-diff-inspector User Guide > Database privileges for sync-diff-inspector`
- Source Line Ranges: `5-50`
- Source Scope: `shared`
- Primary Component: `ecosystem`
- Related Components: `dm`, `ticdc`, `tidb`
- Topic Tags: `overview`, `features`, `restrictions`, `privileges`, `mysql-protocol`, `data-comparison`, `repair-sql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0706_5db5a5d862`
- Source ID: `tidb-docs-8.1:sync-diff-inspector/sync-diff-inspector-overview.md#sync-diff-inspector-user-guide`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `75afa27d459a2fcf9c332d0b34219bf91f4e0f25ff27b314e5620df3b139bd84`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview#sync-diff-inspector-user-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sync-diff-inspector/sync-diff-inspector-overview.md

## Retrieval Guidance

- Use When: Use this when you need the sync-diff-inspector overview, key features, restrictions, or required database privileges for comparing MySQL-protocol databases and generating repair SQL.
- Retrieval Keywords: sync-diff-inspector, Key features, Restrictions of sync-diff-inspector, Database privileges for sync-diff-inspector, compare the table schema and data, repair data, generate the SQL statements used to repair data, data check in the DM replication scenario, data check for TiDB upstream-downstream clusters, range, ignore-columns, FLOAT, DOUBLE, SELECT, RELOAD, PROCESS, INFORMATION_SCHEMA.CLUSTER_INFO, SHOW DATABASES, skip_show_database
- Follow-up Guidance: The content also notes that `SHOW DATABASES` should not be granted on `*.*` and that for MySQL data sources `skip_show_database` should be set to `OFF`.
- Classification Note: This is reference content because it summarizes tool capabilities, limitations, and privilege requirements without providing a step-by-step procedure.

## Official Source Content

# sync-diff-inspector User Guide

[sync-diff-inspector](https://github.com/pingcap/tidb-tools/tree/master/sync_diff_inspector) is a tool used to compare data stored in the databases with the MySQL protocol. For example, it can compare the data in MySQL with that in TiDB, the data in MySQL with that in MySQL, or the data in TiDB with that in TiDB. In addition, you can also use this tool to repair data in the scenario where a small amount of data is inconsistent.

This guide introduces the key features of sync-diff-inspector and describes how to configure and use this tool. To download sync-diff-inspector, use one of the following methods:

+ Binary package. The sync-diff-inspector binary package is included in the TiDB Toolkit. To download the TiDB Toolkit, see [Download TiDB Tools](https://docs.pingcap.com/tidb/stable/download-ecosystem-tools).
+ Docker image. Execute the following command to download:

    ```shell
    docker pull pingcap/tidb-tools:latest
    ```
## Key features

* Compare the table schema and data
* Generate the SQL statements used to repair data if the data inconsistency exists
* Support [data check for tables with different schema or table names](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/route-diff)
* Support [data check in the sharding scenario](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/shard-diff)
* Support [data check for TiDB upstream-downstream clusters](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-upstream-downstream-check)
* Support [data check in the DM replication scenario](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/dm-diff)
## Restrictions of sync-diff-inspector

* Online check is not supported for data migration between MySQL and TiDB. Ensure that no data is written into the upstream-downstream checklist, and that data in a certain range is not changed. You can check data in this range by setting `range`.

* In TiDB and MySQL, `FLOAT`, `DOUBLE` and other floating-point types are implemented differently. `FLOAT` and `DOUBLE` respectively take 6 and 15 significant digits for calculating checksum. If you do not want to use this feature, set `ignore-columns` to skip checking these columns.

* Support checking tables that do not contain the primary key or the unique index. However, if data is inconsistent, the generated SQL statements might not be able to repair the data correctly.
## Database privileges for sync-diff-inspector

To access table schemas and query data, sync-diff-inspector requires specific database privileges. Grant the following privileges on both the upstream and downstream databases:

- `SELECT`: required to compare data.
- `RELOAD`: required to view table schemas.
- `PROCESS`: required when both the upstream and downstream are TiDB clusters. It is used to query the `INFORMATION_SCHEMA.CLUSTER_INFO` table.

> **Note**:
> 
> - **DO NOT** grant the [`SHOW DATABASES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-databases) privilege on all databases (`*.*`). Otherwise, sync-diff-inspector will attempt to access inaccessible databases, which causes errors.
> - For MySQL data sources, ensure that the [`skip_show_database`](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html#sysvar_skip_show_database) system variable is set to `OFF`. If this variable is set to `ON`, the check might fail.
