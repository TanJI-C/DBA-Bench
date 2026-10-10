# Import restore and garbage collection settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > import | TiKV Configuration File > import > `num-threads` | TiKV Configuration File > import > `stream-channel-window` | TiKV Configuration File > import > `memory-use-ratio` <span class="version-mark">New in v6.5.0</span> | TiKV Configuration File > gc | TiKV Configuration File > gc > `batch-keys` | TiKV Configuration File > gc > `max-write-bytes-per-sec` | TiKV Configuration File > gc > `enable-compaction-filter` <span class="version-mark">New in v5.0</span> | TiKV Configuration File > gc > `ratio-threshold` | TiKV Configuration File > gc > `num-threads` <span class="version-mark">New in v6.5.8, v7.1.4, v7.5.1, and v7.6.0</span> | TiKV Configuration File > gc.auto-compaction`
- Source Line Ranges: `2186-2242`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `br`, `lightning`
- Topic Tags: `import`, `restore`, `pitr`, `backup-logs`, `gc`, `compaction-filter`, `auto-compaction`, `threads`, `memory-ratio`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0382_c88d7a1fd9`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#import`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `15b8bef563a6a100c26bd3dcfc46960ccd58d6bd5d43a5f114dff6bc3e13f4d1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#import
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiKV import settings for TiDB Lightning, BR restore, or PITR memory usage, or GC and auto-compaction configuration such as batch size, write rate limit, compaction filter, ratio threshold, and GC threads.
- Retrieval Keywords: import, TiDB Lightning import, BR restore, num-threads, stream-channel-window, memory-use-ratio, PITR, backup log files, gc, batch-keys, max-write-bytes-per-sec, enable-compaction-filter, ratio-threshold, gc num-threads, gc.auto-compaction, Compaction Filter
- Follow-up Guidance: The content also states that in versions earlier than v6.5.0, point-in-time recovery (PITR) only supports restoring data by downloading backup files to a local directory.
- Classification Note: This is classified as configuration for the TiKV component because the content documents TiKV configuration items for import, restore, garbage collection, and automatic compaction, including defaults and value ranges.

## Official Source Content

## import

Configuration items related to TiDB Lightning import and BR restore.
### `num-threads`

+ The number of threads to process RPC requests
+ Default value: `8`
+ Minimum value: `1`
### `stream-channel-window`

+ The window size of Stream channel. When the channel is full, the stream is blocked.
+ Default value: `128`
### `memory-use-ratio` New in v6.5.0

+ Starting from v6.5.0, PITR supports directly accessing backup log files in memory and restoring data. This configuration item specifies the ratio of memory available for PITR to the total memory of TiKV.
+ Value range: [0.0, 0.5]
+ Default value: `0.3`, which means that 30% of the system memory is available for PITR. When the value is `0.0`, PITR is performed through downloading log files to a local directory.

> **Note:**
>
> In versions earlier than v6.5.0, point-in-time recovery (PITR) only supports restoring data by downloading backup files to a local directory.
## gc
### `batch-keys`

+ The number of keys to be garbage-collected in one batch
+ Default value: `512`
### `max-write-bytes-per-sec`

+ The maximum bytes that GC worker can write to RocksDB in one second.
+ If the value is set to `0`, there is no limit.
+ Default value: `"0"`
### `enable-compaction-filter` New in v5.0

+ Controls whether to enable the GC in Compaction Filter feature
+ Default value: `true`
### `ratio-threshold`

+ The garbage ratio threshold to trigger GC.
+ Default value: `1.1`
### `num-threads` New in v6.5.8, v7.1.4, v7.5.1, and v7.6.0

+ The number of GC threads when `enable-compaction-filter` is `false`.
+ Default value: `1`
## gc.auto-compaction

Configures the behavior of TiKV automatic compaction.
