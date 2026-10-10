# TiDB 6.5.9 release notes: compatibility changes and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.9.md`
- Source Title: `TiDB 6.5.9 Release Notes`
- Source Heading Path: `TiDB 6.5.9 Release Notes | TiDB 6.5.9 Release Notes > Compatibility changes | TiDB 6.5.9 Release Notes > Improvements`
- Source Line Ranges: `5-45`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `br`
- Topic Tags: `release-notes`, `compatibility-changes`, `improvements`, `startup`, `statistics`, `analyze`, `memory-usage`, `stability`, `slow-logs`, `log-backup`, `pitr`, `restore`, `gcs`, `dr-auto-sync`, `wal`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0411_ea1f2e70f4`
- Source ID: `tidb-docs-8.1:releases/release-6.5.9.md#tidb-6-5-9-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9c7e70867df65717c8e0cce5990391ff2b2e8514152af2e64723e4605ee9fe37`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.9#tidb-6-5-9-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.9.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.9 release-note items about compatibility changes or improvements in TiDB, TiKV, PD DR Auto-Sync, or BR log backup and restore behavior.
- Retrieval Keywords: TiDB 6.5.9 Release Notes, Compatibility changes, Improvements, track-and-verify-wals-in-manifest, Write Ahead Log (WAL), DR Auto-Sync, wait-recover-timeout, sync-recover, force-init-stats, statistics initialization, HTTP servers, ANALYZE statement blocks the metadata lock, remove unnecessary async blocks, reduce memory usage, snapshot files, raftstore threads, slow logs for peer and store messages, Backup & Restore (BR), log backup, rolling restarts, checkpoint lag, merge operations, error state, abandoning log backup tasks, blocking GC, PITR, Region leadership migration, merging SST files, ingesting SST files in batch, Google Cloud Storage (GCS), slowest Region, global checkpoint advancement, logs and metrics, BR exception handling, unknown errors
- Follow-up Guidance: The chunk groups changes under Compatibility changes and Improvements, with separate items for TiDB, TiKV, and Backup & Restore (BR).
- Classification Note: This is a release-notes chunk because the official content lists version 6.5.9 compatibility changes and implementation improvements across multiple components.

## Official Source Content

# TiDB 6.5.9 Release Notes

Release date: April 12, 2024

TiDB version: 6.5.9

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.5/production-deployment-using-tiup)
## Compatibility changes

- Add a TiKV configuration item [`track-and-verify-wals-in-manifest`](https://docs.pingcap.com/tidb/v6.5/tikv-configuration-file#track-and-verify-wals-in-manifest-new-in-v659) for RocksDB, which helps you investigate possible corruption of Write Ahead Log (WAL) [#16549](https://github.com/tikv/tikv/issues/16549) @[v01dstar](https://github.com/v01dstar)
- DR Auto-Sync supports configuring [`wait-recover-timeout`](https://docs.pingcap.com/tidb/v6.5/two-data-centers-in-one-city-deployment#enable-the-dr-auto-sync-mode), which enables you to control the waiting time for switching back to the `sync-recover` status after the network recovers [#6295](https://github.com/tikv/pd/issues/6295) @[disksing](https://github.com/disksing)
## Improvements

+ TiDB

    - When `force-init-stats` is set to `true`, TiDB waits for statistics initialization to finish before providing services during TiDB startup. This setting no longer blocks the startup of HTTP servers, which enables users to continue monitoring [#50854](https://github.com/pingcap/tidb/issues/50854) @[hawkingrei](https://github.com/hawkingrei)
    - Optimize the issue that the `ANALYZE` statement blocks the metadata lock [#47475](https://github.com/pingcap/tidb/issues/47475) @[wjhuang2016](https://github.com/wjhuang2016)

+ TiKV

    - Remove unnecessary async blocks to reduce memory usage [#16540](https://github.com/tikv/tikv/issues/16540) @[overvenus](https://github.com/overvenus)
    - Avoid performing IO operations on snapshot files in raftstore threads to improve TiKV stability [#16564](https://github.com/tikv/tikv/issues/16564) @[Connor1996](https://github.com/Connor1996)
    - Add slow logs for peer and store messages [#16600](https://github.com/tikv/tikv/issues/16600) @[Connor1996](https://github.com/Connor1996)

+ Tools

    + Backup & Restore (BR)

        - Optimize the Recovery Point Objective (RPO) for log backup during rolling restarts. Now, the checkpoint lag of log backup tasks will be smaller during rolling restarts [#15410](https://github.com/tikv/tikv/issues/15410) @[YuJuncen](https://github.com/YuJuncen)
        - Enhance the tolerance of log backup to merge operations. When encountering a reasonably long merge operation, log backup tasks are less likely to enter the error state [#16554](https://github.com/tikv/tikv/issues/16554) @[YuJuncen](https://github.com/YuJuncen)
        - Support automatically abandoning log backup tasks when encountering a large checkpoint lag, to avoid prolonged blocking GC and potential cluster issues [#50803](https://github.com/pingcap/tidb/issues/50803) @[RidRisR](https://github.com/RidRisR)
        - Alleviate the issue that the latency of the PITR log backup progress increases when Region leadership migration occurs [#13638](https://github.com/tikv/tikv/issues/13638) @[YuJuncen](https://github.com/YuJuncen)
        - Improve the speed of merging SST files during data restore by using a more efficient algorithm [#50613](https://github.com/pingcap/tidb/issues/50613) @[Leavrth](https://github.com/Leavrth)
        - Support ingesting SST files in batch during data restore [#16267](https://github.com/tikv/tikv/issues/16267) @[3pointer](https://github.com/3pointer)
        - Remove an outdated compatibility check when using Google Cloud Storage (GCS) as the external storage [#50533](https://github.com/pingcap/tidb/issues/50533) @[lance6716](https://github.com/lance6716)
        - Print the information of the slowest Region that affects global checkpoint advancement in logs and metrics during log backups [#51046](https://github.com/pingcap/tidb/issues/51046) @[YuJuncen](https://github.com/YuJuncen)
        - Refactor the BR exception handling mechanism to increase tolerance for unknown errors [#47656](https://github.com/pingcap/tidb/issues/47656) @[3pointer](https://github.com/3pointer)
