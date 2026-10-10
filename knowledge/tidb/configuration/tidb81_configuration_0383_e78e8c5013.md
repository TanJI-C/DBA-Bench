# GC auto-compaction thresholds and timing

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > gc.auto-compaction > `check-interval` <span class="version-mark">New in v7.5.7</span> | TiKV Configuration File > gc.auto-compaction > `tombstone-num-threshold` <span class="version-mark">New in v7.5.7</span> | TiKV Configuration File > gc.auto-compaction > `tombstone-percent-threshold` <span class="version-mark">New in v7.5.7</span> | TiKV Configuration File > gc.auto-compaction > `redundant-rows-threshold` <span class="version-mark">New in v7.5.7</span> | TiKV Configuration File > gc.auto-compaction > `redundant-rows-percent-threshold` <span class="version-mark">New in v7.5.7</span> | TiKV Configuration File > gc.auto-compaction > `bottommost-level-force` <span class="version-mark">New in v7.5.7</span>`
- Source Line Ranges: `2243-2282`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `gc`, `auto-compaction`, `rocksdb`, `tombstones`, `mvcc`, `thresholds`, `compaction-filter`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0383_e78e8c5013`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#check-interval-span-class-version-mark-new-in-v7-5-7-span`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6659027c58d0c9fde6c5b4c40d3fdfab4b516edf583a4d0102fc8b83a500c2e3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#check-interval-span-class-version-mark-new-in-v7-5-7-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiKV gc.auto-compaction trigger thresholds, check timing, or whether tombstone and redundant MVCC row thresholds apply with Compaction Filter enabled or disabled.
- Retrieval Keywords: gc.auto-compaction, check-interval, tombstone-num-threshold, tombstone-percent-threshold, redundant-rows-threshold, redundant-rows-percent-threshold, bottommost-level-force, Compaction Filter, automatic compaction, RocksDB tombstones, redundant MVCC rows, TiKV stale versions, TiKV deletion tombstones
- Follow-up Guidance: The content distinguishes thresholds that take effect only when Compaction Filter is disabled from thresholds that take effect only when Compaction Filter is enabled.
- Classification Note: This is classified as configuration because the content defines TiKV gc.auto-compaction configuration items, their meanings, defaults, and validity constraints.

## Official Source Content

### `check-interval` New in v7.5.7

+ The interval at which TiKV checks whether to trigger automatic compaction. Within this interval, Regions that meet the automatic compaction conditions are processed based on priority. When the interval elapses, TiKV rescans Region information and recalculates priorities.
+ Default value: `"300s"`
### `tombstone-num-threshold` New in v7.5.7

+ The number of RocksDB tombstones required to trigger TiKV automatic compaction. When the number of tombstones reaches this threshold, or when the percentage of tombstones reaches [`tombstone-percent-threshold`](#tombstone-percent-threshold-new-in-v757), TiKV triggers automatic compaction.
+ This configuration item takes effect only when [Compaction Filter](https://docs.pingcap.com/tidb/stable/garbage-collection-configuration) is disabled.
+ Default value: `10000`
+ Minimum value: `0`
### `tombstone-percent-threshold` New in v7.5.7

+ The percentage of RocksDB tombstones required to trigger TiKV automatic compaction. When the percentage of tombstones reaches this threshold, or when the number of tombstones reaches [`tombstone-num-threshold`](#tombstone-num-threshold-new-in-v757), TiKV triggers automatic compaction.
+ This configuration item takes effect only when [Compaction Filter](https://docs.pingcap.com/tidb/stable/garbage-collection-configuration) is disabled.
+ Default value: `30`
+ Minimum value: `0`
+ Maximum value: `100`
### `redundant-rows-threshold` New in v7.5.7

+ The number of redundant MVCC rows required to trigger TiKV automatic compaction. Redundant rows include RocksDB tombstones, TiKV stale versions, and TiKV deletion tombstones. When the number of redundant MVCC rows reaches this threshold, or when the percentage of these rows reaches [`redundant-rows-percent-threshold`](#redundant-rows-percent-threshold-new-in-v757), TiKV triggers automatic compaction.
+ This configuration item takes effect only when [Compaction Filter](https://docs.pingcap.com/tidb/stable/garbage-collection-configuration) is enabled.
+ Default value: `50000`
+ Minimum value: `0`
### `redundant-rows-percent-threshold` New in v7.5.7

+ The percentage of redundant MVCC rows required to trigger TiKV automatic compaction. Redundant rows include RocksDB tombstones, TiKV stale versions, and TiKV deletion tombstones. When the number of redundant MVCC rows reaches [`redundant-rows-threshold`](#redundant-rows-threshold-new-in-v757), or when the percentage of these rows reaches `redundant-rows-percent-threshold`, TiKV triggers automatic compaction.
+ This configuration item takes effect only when [Compaction Filter](https://docs.pingcap.com/tidb/stable/garbage-collection-configuration) is enabled.
+ Default value: `20`
+ Minimum value: `0`
+ Maximum value: `100`
### `bottommost-level-force` New in v7.5.7

+ Controls whether to force compaction on the bottommost files in RocksDB.
+ Default value: `true`
