# TiDB 7.5.7 overview and compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.7.md`
- Source Title: `TiDB 7.5.7 Release Notes`
- Source Heading Path: `TiDB 7.5.7 Release Notes | TiDB 7.5.7 Release Notes > Compatibility changes`
- Source Line Ranges: `5-21`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `release-notes`, `compatibility-changes`, `system-variables`, `historical-statistics`, `configuration-deprecation`, `auto-compaction`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0552_8c2cafa58b`
- Source ID: `tidb-docs-8.1:releases/release-7.5.7.md#tidb-7-5-7-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `abbb5b1305fd2ee7012244906b206bc0af07be030f07e60165e43a2cde2cb152`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.7#tidb-7-5-7-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.7.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB 7.5.7 compatibility changes, especially the default change for tidb_enable_historical_stats or the TiKV auto-compaction configuration deprecations and replacements.
- Retrieval Keywords: TiDB 7.5.7 Release Notes, Compatibility changes, tidb_enable_historical_stats, default value ON to OFF, historical statistics, gc.auto-compaction, region-compact-check-interval, region-compact-check-step, region-compact-min-tombstones, region-compact-tombstones-percent, region-compact-min-redundant-rows, region-compact-redundant-rows-percent, gc.auto-compaction.check-interval, gc.auto-compaction.tombstone-num-threshold, gc.auto-compaction.tombstone-percent-threshold, gc.auto-compaction.redundant-rows-threshold, gc.auto-compaction.redundant-rows-percent-threshold, gc.auto-compaction.bottommost-level-force
- Follow-up Guidance: The chunk also lists the exact deprecated TiKV configuration items and the corresponding new gc.auto-compaction configuration items.
- Classification Note: This is classified as a release chunk because it summarizes TiDB 7.5.7 compatibility changes affecting a TiDB system variable and TiKV configuration names.

## Official Source Content

# TiDB 7.5.7 Release Notes

Release date: September 4, 2025

TiDB version: 7.5.7

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.5/production-deployment-using-tiup)
## Compatibility changes

- Change the default value of [`tidb_enable_historical_stats`](https://docs.pingcap.com/tidb/v7.5/system-variables/#tidb_enable_historical_stats) from `ON` to `OFF`, which turns off historical statistics to avoid potential stability issues [#53048](https://github.com/pingcap/tidb/issues/53048) @[hawkingrei](https://github.com/hawkingrei)
- TiKV deprecates the following configuration items and replaces them with the new [`gc.auto-compaction`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file/#gcauto-compaction) configuration group, which controls automatic compaction behavior [#18727](https://github.com/tikv/tikv/issues/18727) @[v01dstar](https://github.com/v01dstar)

    - Deprecated configuration items: [`region-compact-check-interval`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#region-compact-check-interval), [`region-compact-check-step`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#region-compact-check-step), [`region-compact-min-tombstones`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#region-compact-min-tombstones), [`region-compact-tombstones-percent`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#region-compact-tombstones-percent), [`region-compact-min-redundant-rows`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#region-compact-min-redundant-rows-new-in-v710), and [`region-compact-redundant-rows-percent`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#region-compact-redundant-rows-percent-new-in-v710).
    - New configuration items: [`gc.auto-compaction.check-interval`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#check-interval-new-in-v757), [`gc.auto-compaction.tombstone-num-threshold`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#tombstone-num-threshold-new-in-v757), [`gc.auto-compaction.tombstone-percent-threshold`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#tombstone-percent-threshold-new-in-v757), [`gc.auto-compaction.redundant-rows-threshold`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#redundant-rows-threshold-new-in-v757), [`gc.auto-compaction.redundant-rows-percent-threshold`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#redundant-rows-percent-threshold-new-in-v757), and [`gc.auto-compaction.bottommost-level-force`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#bottommost-level-force-new-in-v757).
