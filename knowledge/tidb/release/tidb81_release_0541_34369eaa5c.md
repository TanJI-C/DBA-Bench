# TiDB 7.5.4 overview, compatibility change, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.4.md`
- Source Title: `TiDB 7.5.4 Release Notes`
- Source Heading Path: `TiDB 7.5.4 Release Notes | TiDB 7.5.4 Release Notes > Compatibility changes | TiDB 7.5.4 Release Notes > Improvements`
- Source Line Ranges: `5-47`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `br`, `ticdc`
- Topic Tags: `release-notes`, `compatibility`, `improvements`, `ddl-history`, `http-api`, `log-redaction`, `explain`, `slow-query`, `compaction`, `disk-space-reclamation`, `memory-usage`, `restart-stability`, `diskfull-detection`, `raft-engine`, `string-functions`, `tls`, `join-cancel`, `restore-precheck`, `disk-space-check`, `replication`, `add-index-ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0541_34369eaa5c`
- Source ID: `tidb-docs-8.1:releases/release-7.5.4.md#tidb-7-5-4-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `44fd58047b743ac582cfb1658f33f87b713a51deaa7864418895be75840046dd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.4#tidb-7-5-4-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.4 release-note items about compatibility changes or improvements in TiDB, TiKV, TiFlash, BR, or TiCDC.
- Retrieval Keywords: TiDB 7.5.4 Release Notes, Compatibility changes, Improvements, DDL historical tasks, TiDB HTTP API, default limit of 2048, OOM issues, tidb_redact_log, EXPLAIN, slow queries, RocksDB compaction, disk space reclamation, DELETE versions, peer message channel, DiskFull, RaftEngine, spill-dir, TiFlash LENGTH(), TiFlash ASCII(), TLS, JOIN operator cancel requests, BR restore, disk space in TiKV, SST file, TiCDC, SUPER, ADD INDEX DDL
- Follow-up Guidance: The chunk also lists component-specific improvements for TiDB, TiKV, TiFlash, Backup & Restore (BR), and TiCDC in TiDB 7.5.4.
- Classification Note: This is classified as a release chunk because the official content is the TiDB 7.5.4 release notes covering one compatibility change and multiple improvements.

## Official Source Content

# TiDB 7.5.4 Release Notes

Release date: October 15, 2024

TiDB version: 7.5.4

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.5/production-deployment-using-tiup)
## Compatibility changes

- Set a default limit of 2048 for DDL historical tasks retrieved through the [TiDB HTTP API](https://github.com/pingcap/tidb/blob/release-7.5/docs/tidb_http_api.md) to prevent OOM issues caused by excessive historical tasks [#55711](https://github.com/pingcap/tidb/issues/55711) @[joccau](https://github.com/joccau)
## Improvements

+ TiDB 

    - Support applying the `tidb_redact_log` setting to the output of `EXPLAIN` statements and further optimize the logic in processing logs [#54565](https://github.com/pingcap/tidb/issues/54565) @[hawkingrei](https://github.com/hawkingrei)
    - Optimize the query speed of TiDB slow queries [#54630](https://github.com/pingcap/tidb/pull/54630) @[yibin87](https://github.com/yibin87)

+ TiKV

    - Optimize the trigger mechanism of RocksDB compaction to accelerate disk space reclamation when handling a large number of DELETE versions [#17269](https://github.com/tikv/tikv/issues/17269) @[AndreMouche](https://github.com/AndreMouche)
    - Reduce the memory usage of the peer message channel [#16229](https://github.com/tikv/tikv/issues/16229) @[Connor1996](https://github.com/Connor1996)
    - Optimize the jittery access delay when restarting TiKV due to waiting for the log to be applied, improving the stability of TiKV [#15874](https://github.com/tikv/tikv/issues/15874) @[LykxSassinator](https://github.com/LykxSassinator)
    - Optimize TiKV's `DiskFull` detection to make it compatible with RaftEngine's `spill-dir` configuration, ensuring that this feature works consistently [#17356](https://github.com/tikv/tikv/issues/17356) @[LykxSassinator](https://github.com/LykxSassinator)

+ TiFlash

    - Optimize the execution efficiency of `LENGTH()` and `ASCII()` functions [#9344](https://github.com/pingcap/tiflash/issues/9344) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Mitigate the issue that TiFlash might panic due to updating certificates after TLS is enabled [#8535](https://github.com/pingcap/tiflash/issues/8535) @[windtalker](https://github.com/windtalker)
    - Improve the cancel mechanism of the JOIN operator, so that the JOIN operator can respond to cancel requests in a timely manner [#9430](https://github.com/pingcap/tiflash/issues/9430) @[windtalker](https://github.com/windtalker)

+ Tools

    + Backup & Restore (BR)

        - Support checking whether the disk space in TiKV is sufficient before TiKV downloads each SST file. If the space is insufficient, BR terminates the restore and returns an error [#17224](https://github.com/tikv/tikv/issues/17224) @[RidRisR](https://github.com/RidRisR)

    + TiCDC

        - When the downstream is TiDB with the `SUPER` permission granted, TiCDC supports querying the execution status of `ADD INDEX DDL` from the downstream database to avoid data replication failure due to timeout in retrying executing the DDL statement in some cases [#10682](https://github.com/pingcap/tiflow/issues/10682) @[CharlesCheung96](https://github.com/CharlesCheung96)
