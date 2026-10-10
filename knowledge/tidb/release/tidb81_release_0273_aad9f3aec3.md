# Stability and backup-related release features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.4.0.md`
- Source Title: `TiDB 5.4 Release Notes`
- Source Heading Path: `TiDB 5.4 Release Notes > New features > Stability | TiDB 5.4 Release Notes > New features > High availability and disaster recovery`
- Source Line Ranges: `247-272`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `br`
- Topic Tags: `stability`, `analyze`, `statistics`, `backup`, `auto-tune`, `azure-blob-storage`, `high-availability`, `disaster-recovery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0273_aad9f3aec3`
- Source ID: `tidb-docs-8.1:releases/release-5.4.0.md#stability`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f0f9c4b7d382f15c06c4c342bb75689b73a7836b2937a7dc084b65e37ba5323e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.4.0#stability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 5.4.0 release-note information about persisted ANALYZE configurations, BR auto-tune for backup impact reduction, or Azure Blob Storage backup support.
- Retrieval Keywords: TiDB 5.4.0 Stability, persisting ANALYZE configurations, tidb_analyze_version, tidb_persist_analyze_options, ANALYZE statement, persist analyze configurations, High availability and disaster recovery, Backup & Restore, BR auto-tune, backup tasks on the cluster, adjusting the number of threads, Azure Blob Storage, remote backup storage, backup and restore storages
- Follow-up Guidance: The source links to user documents for persist-analyze-configurations, BR auto-tune, and backup and restore storages.
- Classification Note: This is classified as a release chunk because it summarizes new stability and disaster recovery capabilities introduced in TiDB 5.4.0 for statistics configuration persistence and BR backup features.

## Official Source Content

### Stability

- **Support persisting ANALYZE configurations**

    Statistics are one type of the basic information that the optimizer refers to when generating execution plans. The accuracy of the statistics directly affects whether the generated execution plans are reasonable. To ensure the accuracy of the statistics, sometimes it is necessary to set different collection configurations for different tables, partitions, and indexes.

    Since v5.4.0, TiDB supports persisting some `ANALYZE` configurations. With this feature, the existing configurations can be easily reused for future statistics collection.

    The `ANALYZE` configuration persistence feature is enabled by default (the system variable `tidb_analyze_version` is `2` and [`tidb_persist_analyze_options`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_persist_analyze_options-new-in-v540) is `ON` by default). You can use this feature to record the persistence configurations specified in the `ANALYZE` statement when executing the statement manually. Once recorded, the next time TiDB automatically updates statistics or you manually collect statistics without specifying these configurations, TiDB will collect statistics according to the recorded configurations.

    [User document](https://docs.pingcap.com/tidb/stable/statistics#persist-analyze-configurations)
### High availability and disaster recovery

- **Reduce the impact of backup tasks on the cluster**

    Backup & Restore (BR) introduces the auto-tune feature (enabled by default). This feature can reduce the impact of backup tasks on the cluster by monitoring the cluster resource usage and adjusting the number of threads used by the backup tasks. In some cases, if you increase the cluster hardware resource for backup and enable the auto-tune feature, it can limit the impact of backup tasks on the cluster to 10% or less.

   [User document](https://docs.pingcap.com/tidb/stable/br/br-auto-tune)

- **Support Azure Blob Storage as a target storage for backup**

   Backup & Restore (BR) supports Azure Blob Storage as a remote backup storage. If you deploy TiDB in Azure Cloud, now you can back up the cluster data to the Azure Blob Storage service.

    [User document](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages)
