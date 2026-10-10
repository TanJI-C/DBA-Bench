# Release overview and compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.4.md`
- Source Title: `TiDB 6.5.4 Release Notes`
- Source Heading Path: `TiDB 6.5.4 Release Notes | TiDB 6.5.4 Release Notes > Compatibility changes | TiDB 6.5.4 Release Notes > Compatibility changes > Behavior changes`
- Source Line Ranges: `5-22`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `ticdc`
- Topic Tags: `release-date`, `version`, `compatibility-changes`, `behavior-changes`, `memory-usage`, `cursor-fetch`, `disk-spill`, `rocksdb`, `periodic-compaction`, `configuration`, `cdc`, `update-events`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0397_eff4167f32`
- Source ID: `tidb-docs-8.1:releases/release-6.5.4.md#tidb-6-5-4-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f621ea708ed8936ca7b4d4ebdde891c96f944b2c40e5a496cfcf5eda44b8c673`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.4#tidb-6-5-4-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.4 release date, compatibility changes, or behavior changes involving Cursor Fetch memory usage, TiKV RocksDB periodic compaction defaults, or TiCDC update event splitting.
- Retrieval Keywords: TiDB 6.5.4 Release Notes, Release date August 28 2023, TiDB version 6.5.4, Compatibility changes, Behavior changes, Cursor Fetch, writes the result set to the disk, too much memory, RocksDB periodic compaction, Disable periodic compaction of RocksDB by default, rocksdb.[defaultcf|writecf|lockcf].periodic-compaction-seconds, rocksdb.[defaultcf|writecf|lockcf].ttl, TiCDC splits an event into delete and insert events, delete events preceding insert events, primary key or non-null unique index value is modified, transactions containing multiple changes
- Follow-up Guidance: The source points to TiCDC documentation for transactions containing multiple update changes.
- Classification Note: This is a release-notes chunk classified as shared because it summarizes official 6.5.4 compatibility and behavior changes across TiDB, TiKV, and TiCDC.

## Official Source Content

# TiDB 6.5.4 Release Notes

Release date: August 28, 2023

TiDB version: 6.5.4

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.5/production-deployment-using-tiup)
## Compatibility changes

- To fix the issue that TiDB consumes too much memory when using `Cursor Fetch` to fetch a large result set, TiDB automatically writes the result set to the disk to release memory [#43233](https://github.com/pingcap/tidb/issues/43233) @[YangKeao](https://github.com/YangKeao)
- Disable periodic compaction of RocksDB by default, so that the default behavior of TiKV RocksDB is now consistent with that in versions before v6.5.0. This change prevents potential performance impact caused by a significant number of compactions after upgrading. In addition, TiKV introduces two new configuration items [`rocksdb.[defaultcf|writecf|lockcf].periodic-compaction-seconds`](https://docs.pingcap.com/tidb/v6.5/tikv-configuration-file#periodic-compaction-seconds-new-in-v654) and [`rocksdb.[defaultcf|writecf|lockcf].ttl`](https://docs.pingcap.com/tidb/v6.5/tikv-configuration-file#ttl-new-in-v654), enabling you to manually configure periodic compaction of RocksDB [#15355](https://github.com/tikv/tikv/issues/15355) @[LykxSassinator](https://github.com/LykxSassinator)
### Behavior changes

- For transactions containing multiple changes, if the primary key or non-null unique index value is modified in the update event, TiCDC splits an event into delete and insert events and ensures that all events follow the sequence of delete events preceding insert events. For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-split-update-behavior#transactions-containing-multiple-update-changes).
