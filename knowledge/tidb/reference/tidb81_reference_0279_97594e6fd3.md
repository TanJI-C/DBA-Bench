# BR backup size, restore behavior, statistics, and parallel restore FAQs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/backup-and-restore-faq.md`
- Source Title: `Backup & Restore FAQs`
- Source Heading Path: `Backup & Restore FAQs > Other things you may want to know about backup and restore > What is the size of the backup data? Are there replicas of the backup? | Backup & Restore FAQs > Other things you may want to know about backup and restore > Why is the disk usage shown on the monitoring node inconsistent after backup or restore using BR? | Backup & Restore FAQs > Other things you may want to know about backup and restore > After BR restores the backup data, do I need to execute the `ANALYZE` statement on the table to update the statistics of TiDB on the tables and indexes? | Backup & Restore FAQs > Other things you may want to know about backup and restore > Can I start multiple restore tasks at the same time to restore the data of a single cluster? | Backup & Restore FAQs > Other things you may want to know about backup and restore > Does BR back up the `SHARD_ROW_ID_BITS` and `PRE_SPLIT_REGIONS` information of a table? Does the restored table have multiple Regions?`
- Source Line Ranges: `286-315`
- Source Scope: `shared`
- Primary Component: `br`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `backup-size`, `local-storage`, `compression`, `checksum`, `analyze-table`, `statistics`, `parallel-restore`, `pd-configuration`, `resource-usage`, `region-splitting`, `table-options`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0279_97594e6fd3`
- Source ID: `tidb-docs-8.1:faq/backup-and-restore-faq.md#what-is-the-size-of-the-backup-data-are-there-replicas-of-the-backup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8e3647ff7e0a64ea535784323ea1e3955be7588fb531793bff7655256e704c44`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq#what-is-the-size-of-the-backup-data-are-there-replicas-of-the-backup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/backup-and-restore-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about BR backup size, local storage replica requirements, monitoring disk usage differences after backup or restore, post-restore ANALYZE behavior, parallel restore tasks, or whether restored tables keep SHARD_ROW_ID_BITS and PRE_SPLIT_REGIONS Region splitting.
- Retrieval Keywords: BR backup size, backup files generated on the Leader nodes of each Region, no redundant replicas, total data size divided by the number of replicas, restore data from local storage, each TiKV must have access to all backup files, disk usage shown on the monitoring node inconsistent, data compression rate used in backup is different from the default rate used in restore, If the checksum succeeds, you can ignore this issue, ANALYZE TABLE, BR does not back up statistics, v4.0.9, v4.0.10, TiDB automatically execute ANALYZE, multiple restore tasks at the same time, modifies some global configurations of PD, abnormal cluster status, running restore tasks in parallel, SHARD_ROW_ID_BITS, PRE_SPLIT_REGIONS, restored table is also split into multiple Regions
- Follow-up Guidance: If statistics are not restored, the content states that you need to manually execute `ANALYZE TABLE` or wait for TiDB to automatically execute `ANALYZE`.
- Classification Note: This is reference content because it directly answers operational FAQ items about BR backup size, restore effects, statistics handling, parallel restore limits, and preserved table options.

## Official Source Content

### What is the size of the backup data? Are there replicas of the backup?

During data backup, backup files are generated on the Leader nodes of each Region. The size of the backup is equal to the data size, with no redundant replicas. Therefore, the total data size is approximately the total number of TiKV data divided by the number of replicas.

However, if you want to restore data from local storage, the number of replicas is equal to that of the TiKV nodes, because each TiKV must have access to all backup files.
### Why is the disk usage shown on the monitoring node inconsistent after backup or restore using BR?

This inconsistency is caused by the fact that the data compression rate used in backup is different from the default rate used in restore. If the checksum succeeds, you can ignore this issue.
### After BR restores the backup data, do I need to execute the `ANALYZE` statement on the table to update the statistics of TiDB on the tables and indexes?

BR does not back up statistics (except in v4.0.9). Therefore, after restoring the backup data, you need to manually execute `ANALYZE TABLE` or wait for TiDB to automatically execute `ANALYZE`.

In v4.0.9, BR backs up statistics by default, which consumes too much memory. To ensure that the backup process goes well, the backup for statistics is disabled by default starting from v4.0.10.

If you do not execute `ANALYZE` on the table, TiDB will fail to select the optimal execution plan due to inaccurate statistics. If query performance is not a key concern, you can ignore `ANALYZE`.
### Can I start multiple restore tasks at the same time to restore the data of a single cluster?

**It is strongly not recommended** to start multiple restore tasks at the same time to restore the data of a single cluster for the following reasons:

- When BR restores data, it modifies some global configurations of PD. Therefore, if you start multiple restore tasks for data restore at the same time, these configurations might be mistakenly overwritten and cause abnormal cluster status.
- BR consumes a lot of cluster resources to restore data, so in fact, running restore tasks in parallel improves the restore speed only to a limited extent.
- There has been no test for running multiple restore tasks in parallel for data restore, so it is not guaranteed to succeed.
### Does BR back up the `SHARD_ROW_ID_BITS` and `PRE_SPLIT_REGIONS` information of a table? Does the restored table have multiple Regions?

Yes. BR backs up the [`SHARD_ROW_ID_BITS` and `PRE_SPLIT_REGIONS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region#pre_split_regions) information of a table. The data of the restored table is also split into multiple Regions.
