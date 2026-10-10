# Restore historical data with tidb_snapshot and GC retention

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/read-historical-data.md`
- Source Title: `Read Historical Data Using the System Variable `tidb_snapshot``
- Source Heading Path: `Read Historical Data Using the System Variable `tidb_snapshot` > How to restore historical data`
- Source Line Ranges: `161-177`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dumpling`, `sql`
- Topic Tags: `historical-restore`, `gc-lifetime`, `data-retention`, `snapshot-export`, `load-data`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0034_db5168c262`
- Source ID: `tidb-docs-8.1:read-historical-data.md#how-to-restore-historical-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0dab0a06b3645060e35e74ed817cd0e20e8b831a0e31ad466d86e9acf260e7c5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/read-historical-data#how-to-restore-historical-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/read-historical-data.md

## Retrieval Guidance

- Use When: Use this chunk when you need guidance on restoring historical data with `tidb_snapshot`, preserving older versions with `tidb_gc_life_time`, or exporting a historical snapshot for later import.
- Retrieval Keywords: How to restore historical data, restore historical data, tidb_snapshot restore, tidb_gc_life_time, SET GLOBAL tidb_gc_life_time="60m", GC life time, history data retention, SELECT ... INTO OUTFILE, LOAD DATA, Dumpling, export historical snapshot, export historical data snapshots of TiDB
- Follow-up Guidance: The content notes that increasing `tidb_gc_life_time` retains additional row versions, which might require more disk space and might affect operations such as scans, and it says to set the variable back to the previous value after the restore.
- Classification Note: The official content is classified as recovery because it describes how to restore data from an older version by retaining historical versions long enough and exporting or reimporting that historical data.

## Official Source Content

## How to restore historical data

Before you restore data from an older version, make sure that Garbage Collection (GC) does not clear the history data while you are working on it. This can be done by setting the `tidb_gc_life_time` variable as the following example shows. Do not forget to set the variable back to the previous value after the restore.

```sql
SET GLOBAL tidb_gc_life_time="60m";
```

> **Note:**
>
> Increasing the GC life time from the default 10 minutes to half an hour or more will result in additional versions of rows being retained, which might require more disk space. This might also affect the performance of certain operations such as scans when TiDB needs to skip these additional versions of the same rows during data reads.

To restore data from an older version, you can use one of the following methods:

- For simple cases, use [`SELECT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select) after setting the `tidb_snapshot` variable and copy-paste the output, or use `SELECT ... INTO OUTFILE` and then use [`LOAD DATA`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-data) to import the data later on.

- Use [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#export-historical-data-snapshots-of-tidb) to export a historical snapshot. Dumpling performs well in exporting larger sets of data.
