# Release overview and compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.1.md`
- Source Title: `TiDB 7.5.1 Release Notes`
- Source Heading Path: `TiDB 7.5.1 Release Notes | TiDB 7.5.1 Release Notes > Compatibility changes`
- Source Line Ranges: `5-23`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `tikv`, `ticdc`
- Topic Tags: `release-date`, `version`, `compatibility-changes`, `security-enhanced-mode`, `secure-transport`, `logging`, `gc-threads`, `changefeed-config`, `redo-log`, `object-storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0524_ef30ab0ccd`
- Source ID: `tidb-docs-8.1:releases/release-7.5.1.md#tidb-7-5-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c8768e690ed29bdf04aa80d424b2f9ccdd98be8717c91d8285e26797b68a9424`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.1#tidb-7-5-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.1.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.5.1 release overview details or compatibility changes involving Security Enhanced Mode, TiFlash logging, TiKV GC threads, or new TiCDC changefeed configuration items.
- Retrieval Keywords: TiDB 7.5.1 Release Notes, Release date February 29, 2024, TiDB version 7.5.1, Compatibility changes, require_secure_transport, Security Enhanced Mode, SEM, logger.level, TiFlash default debug to info, gc.num-threads, enable-compaction-filter, TiCDC Changefeed, compression, redo log files, sink.cloud-storage-config, object storage, consistent.flush-concurrency, uploading a single redo file
- Follow-up Guidance: The chunk also points to Quick start and Production deployment links for TiDB v7.5.
- Classification Note: This is classified as a release chunk because it states the TiDB 7.5.1 release date and version and lists official compatibility changes across TiDB, TiFlash, TiKV, and TiCDC.

## Official Source Content

# TiDB 7.5.1 Release Notes

Release date: February 29, 2024

TiDB version: 7.5.1

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.5/production-deployment-using-tiup)
## Compatibility changes

- Prohibit setting [`require_secure_transport`](https://docs.pingcap.com/tidb/v7.5/system-variables#require_secure_transport-new-in-v610) to `ON` in Security Enhanced Mode (SEM) to prevent potential connectivity issues for users [#47665](https://github.com/pingcap/tidb/issues/47665) @[tiancaiamao](https://github.com/tiancaiamao)
- To reduce the overhead of log printing, TiFlash changes the default value of `logger.level` from `"debug"` to `"info"` [#8641](https://github.com/pingcap/tiflash/issues/8641) @[JaySon-Huang](https://github.com/JaySon-Huang)
- Introduce the TiKV configuration item [`gc.num-threads`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#num-threads-new-in-v658-and-v751) to set the number of GC threads when `enable-compaction-filter` is `false`  [#16101](https://github.com/tikv/tikv/issues/16101) @[tonyxuqqi](https://github.com/tonyxuqqi)
- TiCDC Changefeed introduces the following new configuration items:
    - [`compression`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config): enables you to configure the compression behavior of redo log files [#10176](https://github.com/pingcap/tiflow/issues/10176) @[sdojjy](https://github.com/sdojjy)
    - [`sink.cloud-storage-config`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config): enables you to set the automatic cleanup of historical data when replicating data to object storage [#10109](https://github.com/pingcap/tiflow/issues/10109) @[CharlesCheung96](https://github.com/CharlesCheung96)
    - [`consistent.flush-concurrency`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config): enables you to set the concurrency for uploading a single redo file [#10226](https://github.com/pingcap/tiflow/issues/10226) @[sdojjy](https://github.com/sdojjy)
