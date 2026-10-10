# TiDB 6.5.11 overview, compatibility change, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.11.md`
- Source Title: `TiDB 6.5.11 Release Notes`
- Source Heading Path: `TiDB 6.5.11 Release Notes | TiDB 6.5.11 Release Notes > Compatibility changes | TiDB 6.5.11 Release Notes > Improvements`
- Source Line Ranges: `5-41`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `ticdc`
- Topic Tags: `release-notes`, `compatibility-changes`, `grpc-compression`, `performance-improvements`, `gc`, `compaction`, `query-performance`, `ddl-replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0382_c0f1f7af33`
- Source ID: `tidb-docs-8.1:releases/release-6.5.11.md#tidb-6-5-11-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2312cf3cd9e8069de45fe458a55372d2b44f1f0227f08a37667e0c03ab478bf2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.11#tidb-6-5-11-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.11.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.11 release-note details about compatibility changes to TiKV gRPC compression behavior or component-specific improvements in TiDB, TiKV, TiFlash, and TiCDC.
- Retrieval Keywords: TiDB 6.5.11 Release Notes, v6.5.11, Compatibility changes, server.grpc-compression-type, gRPC response messages sent from TiKV to TiDB, compression algorithm, CPU resources, TRUNCATE, DROP, partitioned tables, data GC, TiFlash placement rules, RocksDB compaction trigger mechanism, DELETE versions, disk space reclamation, highly concurrent data read operations, short query performance, LENGTH(), ASCII(), TiCDC, SUPER, ADD INDEX DDL, downstream TiDB, data replication failure, timeout retrying executing the DDL statement
- Follow-up Guidance: The chunk notes that starting from v6.5.11, enabling `server.grpc-compression-type` for TiKV-to-TiDB gRPC response messages might consume more CPU resources.
- Classification Note: This is a self-managed release-notes chunk covering a compatibility change and improvements across shared components including TiDB, TiKV, TiFlash, and TiCDC.

## Official Source Content

# TiDB 6.5.11 Release Notes

Release date: September 20, 2024

TiDB version: 6.5.11

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.5/production-deployment-using-tiup)
## Compatibility changes

- Change the scope of the TiKV configuration item [`server.grpc-compression-type`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#grpc-compression-type):

    - In v6.5.x versions earlier than v6.5.11, this configuration item only affects the compression algorithm of gRPC messages between TiKV nodes.
    - Starting from v6.5.11, this configuration item also affects the compression algorithm of gRPC response messages sent from TiKV to TiDB. Enabling compression might consume more CPU resources. [#17176](https://github.com/tikv/tikv/issues/17176) @[ekexium](https://github.com/ekexium)
## Improvements

+ TiDB

    - By batch deleting TiFlash placement rules, improve the processing speed of data GC after performing the `TRUNCATE` or `DROP` operation on partitioned tables [#54068](https://github.com/pingcap/tidb/issues/54068) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)

+ TiKV

    - Optimize the compaction trigger mechanism of RocksDB to accelerate disk space reclamation when handling a large number of DELETE versions [#17269](https://github.com/tikv/tikv/issues/17269) @[AndreMouche](https://github.com/AndreMouche)

+ TiFlash

    - Reduce lock conflicts under highly concurrent data read operations and optimize short query performance [#9125](https://github.com/pingcap/tiflash/issues/9125) @[JinheLin](https://github.com/JinheLin)
    - Optimize the execution efficiency of `LENGTH()` and `ASCII()` functions [#9344](https://github.com/pingcap/tiflash/issues/9344) @[xzhangxian1008](https://github.com/xzhangxian1008)

+ Tools

    + TiCDC

        - When the downstream is TiDB with the `SUPER` permission granted, TiCDC supports querying the execution status of `ADD INDEX DDL` from the downstream database to avoid data replication failure due to timeout in retrying executing the DDL statement in some cases [#10682](https://github.com/pingcap/tiflow/issues/10682) @[CharlesCheung96](https://github.com/CharlesCheung96)
