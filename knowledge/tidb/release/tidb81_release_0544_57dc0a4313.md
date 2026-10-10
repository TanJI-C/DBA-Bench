# TiDB 7.5.5 overview, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.5.md`
- Source Title: `TiDB 7.5.5 Release Notes`
- Source Heading Path: `TiDB 7.5.5 Release Notes | TiDB 7.5.5 Release Notes > Compatibility changes | TiDB 7.5.5 Release Notes > Improvements`
- Source Line Ranges: `5-46`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `br`, `dm`
- Topic Tags: `release-notes`, `compatibility`, `system-variables`, `configuration-defaults`, `optimizer`, `slow-logs`, `disk-detection`, `restart-stability`, `tls`, `garbage-collection`, `s3-retry`, `backup-logging`, `binlog-events`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0544_57dc0a4313`
- Source ID: `tidb-docs-8.1:releases/release-7.5.5.md#tidb-7-5-5-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ea5e0261f0ba6bd7b1b170e6f43976b4e106765827b7e7d7165d984ef6041133`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.5#tidb-7-5-5-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.5.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 7.5.5 release summary covering compatibility changes and component improvements across TiDB, TiKV, TiFlash, BR, and DM.
- Retrieval Keywords: TiDB 7.5.5 Release Notes, Compatibility changes, Improvements, tidb_ddl_reorg_max_write_speed, raft-client-queue-size, slow disk detection, slow logs for peer and store messages, restarting TiKV, TLS enabled, garbage collection speed of outdated data, Amazon S3 retry strategy, Reduce unnecessary log printing during backup, unrecognized MariaDB binlog events
- Follow-up Guidance: The content points to the system variable `tidb_ddl_reorg_max_write_speed` and the TiKV configuration item `raft-client-queue-size` as exact identifiers mentioned in the compatibility changes.
- Classification Note: This is classified as a release chunk because the official content is the TiDB 7.5.5 release notes overview with listed compatibility changes and improvements.

## Official Source Content

# TiDB 7.5.5 Release Notes

Release date: December 31, 2024

TiDB version: 7.5.5

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.5/production-deployment-using-tiup)
## Compatibility changes

- Add a new system variable [`tidb_ddl_reorg_max_write_speed`](https://docs.pingcap.com/tidb/v7.5/system-variables#tidb_ddl_reorg_max_write_speed-new-in-v6512-and-v755) to limit the maximum speed of the ingest phase when adding indexes [#57156](https://github.com/pingcap/tidb/issues/57156) @[CbcWestwolf](https://github.com/CbcWestwolf)
- Change the default value of the TiKV configuration item [`raft-client-queue-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#raft-client-queue-size) from `8192` to `16384` [#17101](https://github.com/tikv/tikv/issues/17101) @[Connor1996](https://github.com/Connor1996)
## Improvements

+ TiDB

    - Adjust estimation results from 0 to 1 for equality conditions that do not hit TopN when statistics are entirely composed of TopN and the modified row count in the corresponding table statistics is non-zero [#47400](https://github.com/pingcap/tidb/issues/47400) @[terry1purcell](https://github.com/terry1purcell)

+ TiKV

    - Fix the issue that when Raft and RocksDB are deployed on different disks, the slow disk detection does not work for the disk where RocksDB is located [#17884](https://github.com/tikv/tikv/issues/17884) @[LykxSassinator](https://github.com/LykxSassinator)
    - Add slow logs for peer and store messages [#16600](https://github.com/tikv/tikv/issues/16600) @[Connor1996](https://github.com/Connor1996)
    - Optimize the jittery access delay when restarting TiKV due to waiting for the log to be applied, improving the stability of TiKV [#15874](https://github.com/tikv/tikv/issues/15874) @[LykxSassinator](https://github.com/LykxSassinator)

+ TiFlash

    - Mitigate the issue that TiFlash might panic due to updating certificates after TLS is enabled [#8535](https://github.com/pingcap/tiflash/issues/8535) @[windtalker](https://github.com/windtalker)
    - Improve the garbage collection speed of outdated data in the background for tables with clustered indexes [#9529](https://github.com/pingcap/tiflash/issues/9529) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Optimize the retry strategy for TiFlash compute nodes in the disaggregated storage and compute architecture to handle exceptions when downloading files from Amazon S3 [#9695](https://github.com/pingcap/tiflash/issues/9695) @[JinheLin](https://github.com/JinheLin)

+ Tools

    + Backup & Restore (BR)

        - Reduce unnecessary log printing during backup [#55902](https://github.com/pingcap/tidb/issues/55902) @[Leavrth](https://github.com/Leavrth)

    + TiDB Data Migration (DM)

        - Lower the log level for unrecognized MariaDB binlog events [#10204](https://github.com/pingcap/tiflow/issues/10204) @[dveeden](https://github.com/dveeden)
