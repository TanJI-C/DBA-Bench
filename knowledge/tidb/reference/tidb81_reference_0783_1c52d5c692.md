# Backup and restore overview and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/backup-and-restore.md`
- Source Title: `Back Up and Restore TiDB Cloud Dedicated Data`
- Source Heading Path: `Back Up and Restore TiDB Cloud Dedicated Data | Back Up and Restore TiDB Cloud Dedicated Data > Limitations`
- Source Line Ranges: `6-22`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `br`, `tidb`
- Topic Tags: `backup`, `restore`, `limitations`, `pitr`, `snapshot-backup`, `recycle-bin`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0783_1c52d5c692`
- Source ID: `tidb-docs-8.1:tidb-cloud/backup-and-restore.md#back-up-and-restore-tidb-cloud-dedicated-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `110d7b9b41372af0796b0e3f20fc13ab148b63f729fb30f563741251c53de0ce`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#back-up-and-restore-tidb-cloud-dedicated-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/backup-and-restore.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for TiDB Cloud Dedicated backup and restore capabilities or documented limitations around snapshot backup, Point-in-time Restore, recycle bin restore, imported data, or restore contents.
- Retrieval Keywords: TiDB Cloud Dedicated, automatic backup, manual backup, restore to a new cluster, restore a deleted cluster from the recycle bin, Limitations, Point-in-time Restore, snapshot backup, recycle bin, mysql schema, system variables, user accounts, SQL bindings, v6.2.0 or later, imported data does not generate change logs, recoverable range, Dual Region Backup
- Follow-up Guidance: The content points to Back Up and Restore TiDB Cloud Serverless Data for Serverless clusters and to Import CSV Files from Cloud Storage into TiDB Cloud Dedicated for more information about imported data and change logs.
- Classification Note: This is reference content because it summarizes supported backup and restore behaviors and explicit limitations for TiDB Cloud Dedicated.

## Official Source Content

# Back Up and Restore TiDB Cloud Dedicated Data

This document describes how to back up and restore your TiDB Cloud Dedicated cluster data on TiDB Cloud. TiDB Cloud Dedicated supports automatic backup and manual backup. You can also restore backup data to a new cluster or restore a deleted cluster from the recycle bin.

> **Tip**
>
> To learn how to back up and restore TiDB Cloud Serverless cluster data, see [Back Up and Restore TiDB Cloud Serverless Data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore-serverless).
## Limitations

- For clusters of v6.2.0 or later versions, TiDB Cloud Dedicated supports restoring user accounts and SQL bindings from backups by default.
- TiDB Cloud Dedicated does not support restoring system variables stored in the `mysql` schema. 
- It is recommended that you import data first, then perform a **manual** snapshot backup, and finally enable Point-in-time Restore. Because the data imported through the TiDB Cloud console **does not** generate change logs, it cannot be automatically detected and backed up. For more information, see [Import CSV Files from Cloud Storage into TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files). 
- If you turn on and off Point-in-time Restore multiple times, you can only choose a time point within the recoverable range after the most recent Point-in-time Restore is enabled. The earlier recoverable range is not accessible.
- DO NOT modify the switches of **Point-in-time Restore** and **Dual Region Backup** at the same time.
