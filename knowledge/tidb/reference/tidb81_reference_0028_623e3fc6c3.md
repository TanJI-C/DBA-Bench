# Incremental backup overview and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-incremental-guide.md`
- Source Title: `TiDB Incremental Backup and Restore Guide`
- Source Heading Path: `TiDB Incremental Backup and Restore Guide | TiDB Incremental Backup and Restore Guide > Limitations`
- Source Line Ranges: `5-19`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tidb`
- Topic Tags: `incremental-backup`, `mvcc`, `gc`, `limitations`, `ddl`, `deprecated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0028_623e3fc6c3`
- Source ID: `tidb-docs-8.1:br/br-incremental-guide.md#tidb-incremental-backup-and-restore-guide`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c84a43c40544ebecaa84b8e21b06f33ddbea7a6ff1c641be1a4a15b6a5448320`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-incremental-guide#tidb-incremental-backup-and-restore-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-incremental-guide.md

## Retrieval Guidance

- Use When: Use this chunk when answering what TiDB incremental backup contains, what MVCC and GC requirement applies, and what documented limitations or deprecation warning exist.
- Retrieval Keywords: incremental backup overview, differentiated data between starting snapshot and end snapshot, DDLs generated during this period, MVCC data, TiDB GC mechanism, tidb_gc_life_time, Limitations, tables deleted during the incremental backup process might still exist after the data restore, batch renaming of tables, data restore might fail, Development for this feature has stopped, log backup and PITR
- Follow-up Guidance: The source also points to log backup and PITR as an alternative and notes that deleted tables might need to be manually deleted after restore.
- Classification Note: This is reference content because it defines incremental backup, states GC-related prerequisites, and lists official limitations and the warning.

## Official Source Content

# TiDB Incremental Backup and Restore Guide

Incremental data of a TiDB cluster is differentiated data between the starting snapshot and the end snapshot of time period, and the DDLs generated during this period. Compared with full (snapshot) backup data, incremental data is smaller and therefore it is a supplementary to snapshot backup, which reduces the volume of backup data. To perform incremental backup, ensure that MVCC data generated within the specified period is not garbage collected by the [TiDB GC mechanism](https://docs.pingcap.com/tidb/stable/garbage-collection-overview). For example, to perform incremental backup hourly, you must set [`tidb_gc_life_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50) to a value greater than 1 hour.

> **Warning:**
>
> Development for this feature has stopped. It is recommended that you use [log backup and PITR](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) as an alternative.
## Limitations

Because restoring the incremental backup relies on the snapshot of the database table at the backup time point to filter incremental DDL statements, the tables deleted during the incremental backup process might still exist after the data restore and need to be manually deleted.

The incremental backup does not support batch renaming of tables. If batch renaming of tables occurs during the incremental backup process, the data restore might fail. It is recommended to perform a full backup after batch renaming tables, and use the latest full backup to replace the incremental data during restore.
