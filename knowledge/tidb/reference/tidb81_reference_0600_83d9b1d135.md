# IMPORT INTO overview, restrictions, prerequisites, and privileges

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-import-into.md`
- Source Title: `IMPORT INTO`
- Source Heading Path: `IMPORT INTO | IMPORT INTO > Restrictions | IMPORT INTO > Restrictions > `IMPORT INTO ... FROM FILE` restrictions | IMPORT INTO > Restrictions > `IMPORT INTO ... FROM SELECT` restrictions | IMPORT INTO > Prerequisites for import | IMPORT INTO > Required privileges`
- Source Line Ranges: `5-66`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `lightning`, `tidb`, `pd`, `tikv`, `ticdc`, `br`, `cloud`
- Topic Tags: `import`, `physical-import-mode`, `restrictions`, `prerequisites`, `privileges`, `global-sort`, `dxf`, `temporary-directory`, `s3`, `gcs`, `detached`, `empty-table`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0600_83d9b1d135`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-import-into.md#import-into`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2cea13c1917ab40505137ea0e9707b36cde21d5aea4e646b605ad3185989f831`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#import-into
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-import-into.md

## Retrieval Guidance

- Use When: Use this chunk when determining whether an `IMPORT INTO` job is allowed and what restrictions, prerequisites, privileges, concurrency limits, temporary directory requirements, or `FROM FILE` versus `FROM SELECT` constraints apply.
- Retrieval Keywords: IMPORT INTO, Physical Import Mode, IMPORT INTO ... FROM FILE, IMPORT INTO ... FROM SELECT, existing empty tables, temporary table, cached table, BEGIN/END, FLASHBACK CLUSTER, TiCDC, Point-in-Time Recovery (PITR), FLASHBACK DATABASE, temporary directory, temp-dir, 90 GiB, Global Sort, DETACHED, up to 16 IMPORT INTO tasks, DXF, tidb_enable_dist_task, S3, GCS, THREAD must be at least 8, 32 MiB, SHOW IMPORT JOB, CANCEL IMPORT JOB, tidb_snapshot, required privileges, SELECT UPDATE INSERT DELETE ALTER, FILE privilege
- Follow-up Guidance: If the user needs the statement form or field-to-column mapping syntax, the source also provides a separate synopsis and parameter description for `ColumnNameOrUserVarList` and `SetClause`.
- Classification Note: This is reference content because it enumerates official `IMPORT INTO` restrictions, prerequisites, privilege requirements, and operational limits for `FROM FILE` and `FROM SELECT`.

## Official Source Content

# IMPORT INTO

The `IMPORT INTO` statement lets you import data to TiDB via the [Physical Import Mode](https://docs.pingcap.com/tidb/stable/tidb-lightning-physical-import-mode) of TiDB Lightning. You can use `IMPORT INTO` in the following two ways:

- `IMPORT INTO ... FROM FILE`: imports data files in formats such as `CSV`, `SQL`, and `PARQUET` into an empty table in TiDB.
- `IMPORT INTO ... FROM SELECT`: imports the query result of a `SELECT` statement into an empty table in TiDB. You can also use it to import historical data queried with [`AS OF TIMESTAMP`](https://docs.pingcap.com/tidb/stable/as-of-timestamp).

> **Note:**
>
> Compared with [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview), `IMPORT INTO` can be directly executed on TiDB nodes, supports automated distributed task scheduling and [TiDB Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort), and offers significant improvements in deployment, resource utilization, task configuration convenience, ease of invocation and integration, high availability, and scalability. It is recommended that you consider using `IMPORT INTO` instead of TiDB Lightning in appropriate scenarios.
## Restrictions

- `IMPORT INTO` only supports importing data into existing empty tables in the database.
- `IMPORT INTO` does not support importing data into an empty partition if other partitions of the same table already contain data. The target table must be completely empty for import operations.
- `IMPORT INTO` does not support importing data into a [temporary table](https://docs.pingcap.com/tidb/stable/temporary-tables) or a [cached table](https://docs.pingcap.com/tidb/stable/cached-tables).
- `IMPORT INTO` does not support transactions or rollback. Executing `IMPORT INTO` within an explicit transaction (`BEGIN`/`END`) will return an error.
- `IMPORT INTO` does not support working simultaneously with features such as [Backup & Restore](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview), [`FLASHBACK CLUSTER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster), [acceleration of adding indexes](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630), data import using TiDB Lightning, data replication using TiCDC, or [Point-in-Time Recovery (PITR)](https://docs.pingcap.com/tidb/stable/br-log-architecture). For more compatibility information, see [Compatibility of TiDB Lightning and `IMPORT INTO` with TiCDC and Log Backup](https://docs.pingcap.com/tidb/stable/tidb-lightning-compatibility-and-scenarios).
- During the data import process, do not perform DDL or DML operations on the target table, and do not execute [`FLASHBACK DATABASE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-database) for the target database. These operations can lead to import failures or data inconsistencies. In addition, it is **NOT** recommended to perform read operations during the import process, as the data being read might be inconsistent. Perform read and write operations only after the import is completed.
- The import process consumes system resources significantly. For TiDB Self-Managed, to get better performance, it is recommended to use TiDB nodes with at least 32 cores and 64 GiB of memory. TiDB writes sorted data to the TiDB [temporary directory](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#temp-dir-new-in-v630) during import, so it is recommended to configure high-performance storage media for TiDB Self-Managed, such as flash memory. For more information, see [Physical Import Mode limitations](https://docs.pingcap.com/tidb/stable/tidb-lightning-physical-import-mode#requirements-and-restrictions).
- For TiDB Self-Managed, the TiDB [temporary directory](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#temp-dir-new-in-v630) is expected to have at least 90 GiB of available space. It is recommended to allocate storage space that is equal to or greater than the volume of data to be imported.
- One import job supports importing data into one target table only.
- `IMPORT INTO` is not supported during TiDB cluster upgrades.
- Ensure that the data to be imported does not contain any records with primary key or non-null unique index conflicts. Otherwise, the conflicts can result in import task failures.
- Known issue: the `IMPORT INTO` task might fail if the PD address in the TiDB node configuration file is inconsistent with the current PD topology of the cluster. This inconsistency can arise in situations such as that PD was scaled in previously, but the TiDB configuration file was not updated accordingly or the TiDB node was not restarted after the configuration file update.
### `IMPORT INTO ... FROM FILE` restrictions

- For TiDB Self-Managed, each `IMPORT INTO` task supports importing data within 10 TiB. If you enable the [Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort) feature, each `IMPORT INTO` task supports importing data within 40 TiB.
- For [TiDB Cloud Dedicated](https://docs.pingcap.com/tidbcloud/select-cluster-tier#tidb-cloud-dedicated), if your data to be imported exceeds 500 GiB, it is recommended to use TiDB nodes with at least 16 cores and enable the [Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort) feature, then each `IMPORT INTO` task supports importing data within 40 TiB. If your data to be imported is within 500 GiB or if the cores of your TiDB nodes are less than 16, it is not recommended to enable the [Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort) feature.
- The execution of `IMPORT INTO ... FROM FILE` blocks the current connection until the import is completed. To execute the statement asynchronously, you can add the `DETACHED` option.
- Up to 16 `IMPORT INTO` tasks can run simultaneously on each cluster (see [TiDB Distributed eXecution Framework (DXF) usage limitations](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework#limitation)). When a cluster lacks sufficient resources or reaches the maximum number of tasks, newly submitted import tasks are queued for execution.
- When the [Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort) feature is used for data import, the value of the `THREAD` option must be at least `8`.
- When the [Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort) feature is used for data import, the data size of a single row after encoding must not exceed 32 MiB.
- All `IMPORT INTO` tasks that are created when [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework) is not enabled run directly on the nodes where the tasks are submitted, and these tasks will not be scheduled for execution on other TiDB nodes even after DXF is enabled later. After DXF is enabled, only newly created `IMPORT INTO` tasks that import data from S3 or GCS are automatically scheduled or failed over to other TiDB nodes for execution.
### `IMPORT INTO ... FROM SELECT` restrictions

- `IMPORT INTO ... FROM SELECT` can only be executed on the TiDB node that the current user is connected to, and it blocks the current connection until the import is complete.
- `IMPORT INTO ... FROM SELECT` only supports two [import options](#withoptions): `THREAD` and `DISABLE_PRECHECK`.
- `IMPORT INTO ... FROM SELECT` does not support the task management statements such as `SHOW IMPORT JOB(s)` and `CANCEL IMPORT JOB <job-id>`.
- The [temporary directory](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#temp-dir-new-in-v630) of TiDB requires sufficient space to store the entire query result of the `SELECT` statement (configuring the `DISK_QUOTA` option is not supported currently).
- Importing historical data using [`tidb_snapshot`](https://docs.pingcap.com/tidb/stable/read-historical-data) is not supported.
- Because the syntax of the `SELECT` clause is complex, the `WITH` parameter in `IMPORT INTO` might conflict with it and cause parsing errors, such as `GROUP BY ... [WITH ROLLUP]`. It is recommended to create a view for complex `SELECT` statements and then use `IMPORT INTO ... FROM SELECT * FROM view_name` for importing. Alternatively, you can clarify the scope of the `SELECT` clause with parentheses, such as `IMPORT INTO ... FROM (SELECT ...) WITH ...`.
## Prerequisites for import

Before using `IMPORT INTO` to import data, make sure the following requirements are met:

- The target table to be imported is already created in TiDB and it is empty.
- The target cluster has sufficient space to store the data to be imported.
- For TiDB Self-Managed, the [temporary directory](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#temp-dir-new-in-v630) of the TiDB node connected to the current session has at least 90 GiB of available space. If [`tidb_enable_dist_task`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_dist_task-new-in-v710) is enabled and the data for import is from S3 or GCS, also make sure that the temporary directory of each TiDB node in the cluster has sufficient disk space.
## Required privileges

Executing `IMPORT INTO` requires the `SELECT`, `UPDATE`, `INSERT`, `DELETE`, and `ALTER` privileges on the target table. To import files in TiDB local storage, the `FILE` privilege is also required.
