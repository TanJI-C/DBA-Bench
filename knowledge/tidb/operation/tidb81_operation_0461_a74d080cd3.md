# TiDB Lightning precheck items and compatibility constraints

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-prechecks.md`
- Source Title: `TiDB Lightning Prechecks`
- Source Heading Path: `TiDB Lightning Prechecks`
- Source Line Ranges: `5-22`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `pd`, `tidb`, `tikv`, `tiflash`, `ticdc`, `cloud`
- Topic Tags: `prechecks`, `migration`, `physical-import`, `disk-space`, `permissions`, `cluster-status`, `region-distribution`, `csv`, `breakpoint-recovery`, `existing-table`, `target-table`, `pitr`, `changefeed`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0461_a74d080cd3`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-prechecks.md#tidb-lightning-prechecks`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `56d137d50830f748b36bfd9fec4f1d27e038f46505f52c38fa4cb33e988857d6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-prechecks#tidb-lightning-prechecks
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-prechecks.md

## Retrieval Guidance

- Use When: Use this chunk when identifying what TiDB Lightning prechecks run before a migration task and the documented compatibility constraints that can stop physical import mode.
- Retrieval Keywords: TiDB Lightning Prechecks, Cluster version and status, Permissions, Disk space, Region distribution status, Exceedingly Large CSV files in the data file, Recovery from breakpoints, Import into an existing table, Whether the target table is empty, Whether PITR is enabled or any changefeed task is running in the cluster, physical import mode, parallel-import = true, sort-kv-dir, StrictFormat=false, empty Regions exceeds max(1000, number of tables * 3), target table is not empty, PITR, changefeed, Amazon S3
- Follow-up Guidance: The source also states that the precheck feature is enabled by default starting from TiDB 5.3.0 and lists the supported version for each check item.
- Classification Note: This is classified as operation content because it describes TiDB Lightning runtime precheck behavior, prerequisites, and error-triggering conditions for migration and physical import tasks.

## Official Source Content

# TiDB Lightning Prechecks

Starting from TiDB 5.3.0, TiDB Lightning provides the ability to check the configuration before running a migration task. It is enabled by default. This feature automatically performs some routine checks for disk space and execution configuration. The main purpose is to ensure that the whole subsequent import process goes smoothly.

The following table describes each check item and detailed explanation.

|  Check Items | Supported Version| Description |
|  ----  | ----  |----  |
| Cluster version and status| >= 5.3.0 | Check whether the cluster can be connected in the configuration, and whether the TiKV/PD/TiFlash version supports the physical import mode. |
| Permissions | >= 5.3.0 | When the data source is cloud storage (Amazon S3), check whether TiDB Lightning has the necessary permissions and make sure that the import will not fail due to lack of permissions. |
| Disk space | >= 5.3.0 | Check whether there is enough space on the local disk and on the TiKV cluster for importing data. TiDB Lightning samples the data sources and estimates the percentage of the index size from the sample result. Because indexes are included in the estimation, there might be cases where the size of the source data is less than the available space on the local disk, but still, the check fails. In the physical import mode, TiDB Lightning also checks whether the local storage is sufficient because external sorting needs to be done locally. For more details about the TiKV cluster space and local storage space (controlled by `sort-kv-dir`), see [Downstream storage space requirements](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-requirements#storage-space-of-the-target-database) and [Resource requirements](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode#environment-requirements). |
| Region distribution status | >= 5.3.0 | Check whether the Regions in the TiKV cluster are distributed evenly and whether there are too many empty Regions. If the number of empty Regions exceeds max(1000, number of tables * 3), i.e. greater than the bigger one of "1000" or "3 times the number of tables", then the import cannot be executed. |
| Exceedingly Large CSV files in the data file | >= 5.3.0 | When there are CSV files larger than 10 GiB in the backup file and auto-slicing is not enabled (StrictFormat=false), it will impact the import performance. The purpose of this check is to remind you to ensure the data is in the right format and to enable auto-slicing. |
| Recovery from breakpoints | >= 5.3.0 | This check ensures that no changes are made to the source file or schema in the database during the breakpoint recovery process that would result in importing the wrong data. |
| Import into an existing table | >= 5.3.0 | When importing into an already created table, it checks, as much as possible, whether the source file matches the existing table. Check if the number of columns matches. If the source file has column names, check if the column names match. When there are default columns in the source file, it checks if the default columns have Default Value, and if they have, the check passes. |
| Whether the target table is empty | >= 5.3.1 | TiDB Lightning automatically exits with an error if the target table is not empty. If parallel import mode is enabled (`parallel-import = true`), this check item will be skipped. |
| Whether PITR is enabled or any changefeed task is running in the cluster | >= 6.5.0 | The TiDB Lightning physical import mode is incompatible with PITR and changefeed. If PITR is enabled or a changefeed task is running, TiDB Lightning automatically exits with an error. If you are certain that the tables to be imported do not require PITR or changefeed for replication, you can skip this check to proceed with the TiDB Lightning physical import mode. |
