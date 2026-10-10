# TiDB 8.1.2 release notes: compatibility changes and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.2.md`
- Source Title: `TiDB 8.1.2 Release Notes`
- Source Heading Path: `TiDB 8.1.2 Release Notes | TiDB 8.1.2 Release Notes > Compatibility changes | TiDB 8.1.2 Release Notes > Improvements`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `br`, `ticdc`, `pd`
- Topic Tags: `release-notes`, `compatibility-changes`, `configuration`, `snapshot-ingest`, `metrics`, `region-merge`, `diskfull`, `compaction`, `dynamic-configuration`, `external-storage`, `s3`, `tls`, `clustered-index`, `join-cancellation`, `backup`, `checksum`, `ddl`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0606_61630bec0c`
- Source ID: `tidb-docs-8.1:releases/release-8.1.2.md#tidb-8-1-2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a9e57b5455e201cbc293e86f7ad8467defa28da4ddfc72d6c1cc4436d0ee0393`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.2#tidb-8-1-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 8.1.2 release-note details about compatibility changes or component improvements across TiDB, TiKV, TiFlash, BR, and TiCDC.
- Retrieval Keywords: TiDB 8.1.2 Release Notes, Compatibility changes, Improvements, server.snap-min-ingest-size, snap-min-ingest-size, 2MiB, ingest method, direct write method, Request Unit (RU) settings metrics, Region Merge empty tables small Regions, DiskFull, RaftEngine spill-dir, RocksDB compaction DELETE versions, import.num-threads, dynamic configuration, AWS Rust SDK, Rusoto, Amazon S3, IMDSv2, EKS Pod Identity, clustered indexes, TLS enabled certificates, disaggregated storage and compute, JOIN operator cancel requests, LENGTH(), ASCII(), TiFlash compute nodes, BR --checksum=false, table-level checksum calculation, full backups, TiCDC SUPER privilege, asynchronously executed DDL tasks, ADD INDEX DDL
- Follow-up Guidance: The source also states the release date is December 26, 2024 and includes quick access links for Quick start and Production deployment.
- Classification Note: This is a self-managed release-notes chunk covering one compatibility change and multiple improvements in shared and component-specific areas for TiDB 8.1.2.

## Official Source Content

# TiDB 8.1.2 Release Notes

Release date: December 26, 2024

TiDB version: 8.1.2

Quick access: [Quick start](https://docs.pingcap.com/tidb/v8.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v8.1/production-deployment-using-tiup)
## Compatibility changes

- Add the TiKV configuration item [`server.snap-min-ingest-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#snap-min-ingest-size-new-in-v812), which specifies the minimum threshold for whether TiKV adopts the ingest method when processing snapshots. The default value is `2MiB`.

    - When the snapshot size exceeds this threshold, TiKV adopts the ingest method, which imports SST files from the snapshot into RocksDB. This method is faster for large files.
    - When the snapshot size does not exceed this threshold, TiKV adopts the direct write method, which writes each piece of data into RocksDB individually. This method is more efficient for small files.
## Improvements

+ TiDB

    - Add metrics about Request Unit (RU) settings [#8444](https://github.com/tikv/pd/issues/8444) @[nolouch](https://github.com/nolouch)

+ TiKV

    - Improve the speed of Region Merge in scenarios with empty tables and small Regions [#17376](https://github.com/tikv/tikv/issues/17376) @[LykxSassinator](https://github.com/LykxSassinator)
    - Optimize TiKV's `DiskFull` detection to make it compatible with RaftEngine's `spill-dir` configuration, ensuring that this feature works consistently [#17356](https://github.com/tikv/tikv/issues/17356) @[LykxSassinator](https://github.com/LykxSassinator)
    - Optimize the trigger mechanism of RocksDB compaction to accelerate disk space reclamation when handling a large number of DELETE versions [#17269](https://github.com/tikv/tikv/issues/17269) @[AndreMouche](https://github.com/AndreMouche)
    - Support modifying the `import.num-threads` configuration item dynamically [#17807](https://github.com/tikv/tikv/issues/17807) @[RidRisR](https://github.com/RidRisR)
    - Replace the Rusoto library with AWS Rust SDK to access external storage (such as Amazon S3) for backup and restore, which enhances compatibility with AWS features such as IMDSv2 and EKS Pod Identity [#12371](https://github.com/tikv/tikv/issues/12371) @[akoshchiy](https://github.com/akoshchiy)

+ TiFlash

    - Improve the garbage collection speed of outdated data in the background for tables with clustered indexes [#9529](https://github.com/pingcap/tiflash/issues/9529) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Mitigate the issue that TiFlash might panic due to updating certificates after TLS is enabled [#8535](https://github.com/pingcap/tiflash/issues/8535) @[windtalker](https://github.com/windtalker)
    - Reduce the number of threads that TiFlash needs to create when processing disaggregated storage and compute requests, helping avoid crashes of TiFlash compute nodes when processing a large number of such requests [#9334](https://github.com/pingcap/tiflash/issues/9334) @[JinheLin](https://github.com/JinheLin)
    - Improve the cancel mechanism of the JOIN operator, so that the JOIN operator can respond to cancel requests in a timely manner [#9430](https://github.com/pingcap/tiflash/issues/9430) @[windtalker](https://github.com/windtalker)
    - Optimize the execution efficiency of `LENGTH()` and `ASCII()` functions [#9344](https://github.com/pingcap/tiflash/issues/9344) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Optimize the retry strategy for TiFlash compute nodes in the disaggregated storage and compute architecture to handle exceptions when downloading files from Amazon S3 [#9695](https://github.com/pingcap/tiflash/issues/9695) @[JinheLin](https://github.com/JinheLin)

+ Tools

    + Backup & Restore (BR)

        - Reduce unnecessary log printing during backup [#55902](https://github.com/pingcap/tidb/issues/55902) @[Leavrth](https://github.com/Leavrth)
        - Disable the table-level checksum calculation (`--checksum=false`) during full backups by default to improve backup performance [#56373](https://github.com/pingcap/tidb/issues/56373) @[Tristan1900](https://github.com/Tristan1900)

    + TiCDC

        - TiCDC supports querying the status of asynchronously executed DDL tasks after being granted the `SUPER` privilege, preventing execution errors caused by repeatedly executing DDL tasks on the same table [#11521](https://github.com/pingcap/tiflow/issues/11521) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - When the downstream is TiDB with the `SUPER` permission granted, TiCDC supports querying the execution status of `ADD INDEX DDL` from the downstream database to avoid data replication failure due to timeout in retrying executing the DDL statement in some cases [#10682](https://github.com/pingcap/tiflow/issues/10682) @[CharlesCheung96](https://github.com/CharlesCheung96)
