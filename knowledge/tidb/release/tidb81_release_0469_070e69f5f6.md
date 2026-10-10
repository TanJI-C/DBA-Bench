# Release overview and compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.4.md`
- Source Title: `TiDB 7.1.4 Release Notes`
- Source Heading Path: `TiDB 7.1.4 Release Notes | TiDB 7.1.4 Release Notes > Compatibility changes`
- Source Line Ranges: `5-18`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiflash`, `tikv`
- Topic Tags: `release-notes`, `compatibility`, `default-values`, `logging`, `gc`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0469_070e69f5f6`
- Source ID: `tidb-docs-8.1:releases/release-7.1.4.md#tidb-7-1-4-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `29d8bc115bcb0789de14d4d758982e79f1f6ddae5c5c6c9eca96925a62ae5954`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.4#tidb-7-1-4-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.4.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.1.4 compatibility changes involving default logging behavior in TiFlash or the new TiKV GC thread configuration.
- Retrieval Keywords: TiDB 7.1.4 Release Notes, Compatibility changes, TiFlash logger.level default value debug to info, logger.level, TiKV gc.num-threads, enable-compaction-filter false, number of GC threads
- Follow-up Guidance: This chunk points to the TiKV configuration item `gc.num-threads` and states it is used when `enable-compaction-filter` is `false`.
- Classification Note: This is a release-note compatibility section because the official content describes changed defaults and a newly introduced configuration item.

## Official Source Content

# TiDB 7.1.4 Release Notes

Release date: March 11, 2024

TiDB version: 7.1.4

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.1/production-deployment-using-tiup)
## Compatibility changes

- To reduce the overhead of log printing, TiFlash changes the default value of `logger.level` from `"debug"` to `"info"` [#8641](https://github.com/pingcap/tiflash/issues/8641) @[JaySon-Huang](https://github.com/JaySon-Huang)
- Introduce the TiKV configuration item [`gc.num-threads`](https://docs.pingcap.com/tidb/v6.5/tikv-configuration-file#num-threads-new-in-v658) to set the number of GC threads when `enable-compaction-filter` is `false`  [#16101](https://github.com/tikv/tikv/issues/16101) @[tonyxuqqi](https://github.com/tonyxuqqi)
