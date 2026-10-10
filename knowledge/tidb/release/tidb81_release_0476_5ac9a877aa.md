# TiDB 7.1.5 overview, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.5.md`
- Source Title: `TiDB 7.1.5 Release Notes`
- Source Heading Path: `TiDB 7.1.5 Release Notes | TiDB 7.1.5 Release Notes > Compatibility changes | TiDB 7.1.5 Release Notes > Improvements`
- Source Line Ranges: `5-42`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `br`
- Topic Tags: `release-notes`, `compatibility-changes`, `improvements`, `wal`, `rocksdb`, `region-loading`, `analyze`, `ldap`, `slow-logs`, `etcd`, `log-backup`, `pitr`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0476_5ac9a877aa`
- Source ID: `tidb-docs-8.1:releases/release-7.1.5.md#tidb-7-1-5-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a22929ec5e08a526fbe12b438d80170428b91afe3fb27a0a3dcdbc7a699271cf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.5#tidb-7-1-5-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.5.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 7.1.5 release overview, compatibility changes, or listed improvements across TiDB, TiKV, PD, and BR.
- Retrieval Keywords: TiDB 7.1.5 Release Notes, Compatibility changes, Improvements, track-and-verify-wals-in-manifest, RocksDB, Write Ahead Log, WAL, loading Regions in batch from PD, ANALYZE statement blocks the metadata lock, LDAP authentication timeout mechanism, slow logs for peer and store messages, snapshot files in raftstore threads, etcd v3.4.30, log backup tasks, checkpoint lag, blocking GC, PITR, active DDL jobs
- Follow-up Guidance: The chunk also points to Quick start and Production deployment links for TiDB v7.1.
- Classification Note: This is a release-notes summary chunk because the official content lists one compatibility change and multiple improvements for TiDB 7.1.5 components and tools.

## Official Source Content

# TiDB 7.1.5 Release Notes

Release date: April 26, 2024

TiDB version: 7.1.5

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.1/production-deployment-using-tiup)
## Compatibility changes

- Add a TiKV configuration item [`track-and-verify-wals-in-manifest`](https://docs.pingcap.com/tidb/v7.1/tikv-configuration-file#track-and-verify-wals-in-manifest-new-in-v659-and-v715) for RocksDB, which helps you investigate possible corruption of Write Ahead Log (WAL) [#16549](https://github.com/tikv/tikv/issues/16549) @[v01dstar](https://github.com/v01dstar)
## Improvements

+ TiDB

    - Support loading Regions in batch from PD to speed up the conversion process from the KV range to Regions when querying large tables [#51326](https://github.com/pingcap/tidb/issues/51326) @[SeaRise](https://github.com/SeaRise)
    - Optimize the issue that the `ANALYZE` statement blocks the metadata lock [#47475](https://github.com/pingcap/tidb/issues/47475) @[wjhuang2016](https://github.com/wjhuang2016)
    - Add a timeout mechanism for LDAP authentication to avoid the issue of resource lock (RLock) not being released in time [#51883](https://github.com/pingcap/tidb/issues/51883) @[YangKeao](https://github.com/YangKeao)

+ TiKV

    - Add slow logs for peer and store messages [#16600](https://github.com/tikv/tikv/issues/16600) @[Connor1996](https://github.com/Connor1996)
    - Avoid performing IO operations on snapshot files in raftstore threads to improve TiKV stability [#16564](https://github.com/tikv/tikv/issues/16564) @[Connor1996](https://github.com/Connor1996)

+ PD

    - Upgrade the etcd version to v3.4.30 [#7904](https://github.com/tikv/pd/issues/7904) @[JmPotato](https://github.com/JmPotato)

+ Tools

    + Backup & Restore (BR)

        - Support automatically abandoning log backup tasks when encountering a large checkpoint lag, to avoid prolonged blocking GC and potential cluster issues [#50803](https://github.com/pingcap/tidb/issues/50803) @[RidRisR](https://github.com/RidRisR)
        - Add PITR integration test cases to cover compatibility testing for log backup and adding index acceleration [#51987](https://github.com/pingcap/tidb/issues/51987) @[Leavrth](https://github.com/Leavrth)
        - Remove the invalid verification for active DDL jobs when log backup starts [#52733](https://github.com/pingcap/tidb/issues/52733) @[Leavrth](https://github.com/Leavrth)
