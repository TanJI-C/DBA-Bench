# TiKV RocksDB Titan and column family storage configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > rocksdb.titan > `disable-gc` | TiKV Configuration File > rocksdb.titan > `max-background-gc` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `block-size` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `block-cache-size` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `disable-block-cache` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `cache-index-and-filter-blocks` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `pin-l0-filter-and-index-blocks` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `use-bloom-filter` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `optimize-filters-for-hits` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `optimize-filters-for-memory` <span class="version-mark">New in v7.2.0</span> | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `whole-key-filtering` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `bloom-filter-bits-per-key` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `block-based-bloom-filter` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `ribbon-filter-above-level` <span class="version-mark">New in v7.2.0</span> | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `read-amp-bytes-per-bit` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `compression-per-level` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `bottommost-level-compression` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `write-buffer-size` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `max-write-buffer-number` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `min-write-buffer-number-to-merge` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `max-bytes-for-level-base` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `target-file-size-base` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `level0-file-num-compaction-trigger` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `level0-slowdown-writes-trigger` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `level0-stop-writes-trigger` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `max-compaction-bytes` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `compaction-pri` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `dynamic-level-bytes` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `num-levels` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `max-bytes-for-level-multiplier` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `compaction-style` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `disable-auto-compactions` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `soft-pending-compaction-bytes-limit` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `hard-pending-compaction-bytes-limit` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `enable-compaction-guard` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `compaction-guard-min-output-file-size` | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `compaction-guard-max-output-file-size``
- Source Line Ranges: `1477-1719`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `rocksdb`, `titan`, `column-family`, `block-cache`, `bloom-filter`, `compression`, `memtable`, `compaction`, `write-stall`, `storage-engine`, `version-specific`, `deprecated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0377_00e3810c7f`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#disable-gc`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c0fce6f8317d1032f0bfbfdab9c814f9aff180b2dc0e17337dfd807242f3a649`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#disable-gc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiKV RocksDB Titan and column family configuration items for default values, deprecations, version-specific behavior, overrides, and compaction or cache settings in rocksdb.defaultcf, rocksdb.writecf, rocksdb.lockcf, or rocksdb.raftcf.
- Retrieval Keywords: rocksdb.titan disable-gc, rocksdb.titan max-background-gc, TiKV Details Thread CPU RocksDB CPU, rocksdb.defaultcf, rocksdb.writecf, rocksdb.lockcf, rocksdb.raftcf, block-size, block-cache-size deprecated v6.6.0, disable-block-cache, cache-index-and-filter-blocks, pin-l0-filter-and-index-blocks, use-bloom-filter, optimize-filters-for-hits, optimize-filters-for-memory, format-version >= 5, whole-key-filtering, bloom-filter-bits-per-key, block-based-bloom-filter, ribbon-filter-above-level, read-amp-bytes-per-bit, compression-per-level, bottommost-level-compression, write-buffer-size, storage.engine raft-kv, storage.engine partitioned-raft-kv, max-write-buffer-number, storage.flow-control.enable, storage.flow-control.memtables-threshold, max-bytes-for-level-base, target-file-size-base, level0-file-num-compaction-trigger, level0-slowdown-writes-trigger, storage.flow-control.l0-files-threshold, level0-stop-writes-trigger, max-compaction-bytes, compaction-pri, min-overlapping-ratio, oldest-largest-seq-first, oldest-smallest-seq-first, by-compensated-size, dynamic-level-bytes, num-levels, max-bytes-for-level-multiplier, compaction-style, disable-auto-compactions, soft-pending-compaction-bytes-limit, hard-pending-compaction-bytes-limit, enable-compaction-guard, compaction-guard-min-output-file-size, compaction-guard-max-output-file-size
- Follow-up Guidance: The source notes several interactions and overrides, including format-version requirements for optimize-filters-for-memory and ribbon-filter-above-level, storage.flow-control overrides for multiple write-stall and pending-compaction settings, and compaction-guard-max-output-file-size overriding target-file-size-base.
- Classification Note: This chunk is classified as configuration because it lists TiKV RocksDB Titan and column family configuration parameters, including defaults, allowed values, deprecation status, and related behavior.

## Official Source Content

### `disable-gc`

+ Determines whether to disable Garbage Collection (GC) that Titan performs to Blob files
+ Default value: `false`
### `max-background-gc`

+ The maximum number of GC threads in Titan. From the **TiKV Details** > **Thread CPU** > **RocksDB CPU** panel, if you observe that the Titan GC threads are at full capacity for a long time, consider increasing the size of the Titan GC thread pool.
+ Default value: `1`. Before v8.0.0, the default value is `4`.
+ Minimum value: `1`
## rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf

Configuration items related to `rocksdb.defaultcf`, `rocksdb.writecf`, and `rocksdb.lockcf`.
### `block-size`

+ The default size of a RocksDB block
+ Default value for `defaultcf` and `writecf`: `"32KiB"`
+ Default value for `lockcf`: `"16KiB"`
+ Minimum value: `"1KiB"`
+ Unit: KiB|MiB|GiB
### `block-cache-size`

> **Warning:**
>
> Starting from v6.6.0, this configuration is deprecated.

+ The cache size of a RocksDB block.
+ Default value for `defaultcf`: `Total machine memory * 25%`
+ Default value for `writecf`: `Total machine memory * 15%`
+ Default value for `lockcf`: `Total machine memory * 2%`
+ Minimum value: `0`
+ Unit: KiB|MiB|GiB
### `disable-block-cache`

+ Enables or disables block cache
+ Default value: `false`
### `cache-index-and-filter-blocks`

+ Enables or disables caching index and filter
+ Default value: `true`
### `pin-l0-filter-and-index-blocks`

+ Determines whether to pin the index and filter blocks of the level 0 SST files in memory.
+ Default value: `true`
### `use-bloom-filter`

+ Enables or disables bloom filter
+ Default value: `true`
### `optimize-filters-for-hits`

+ Determines whether to optimize the hit ratio of filters
+ Default value for `defaultcf`: `true`
+ Default value for `writecf` and `lockcf`: `false`
### `optimize-filters-for-memory` New in v7.2.0

+ Determines whether to generate Bloom/Ribbon filters that minimize memory internal fragmentation.
+ Note that this configuration item takes effect only when [`format-version`](#format-version-new-in-v620) >= 5.
+ Default value: `false`
### `whole-key-filtering`

+ Determines whether to put the entire key to bloom filter
+ Default value for `defaultcf` and `lockcf`: `true`
+ Default value for `writecf`: `false`
### `bloom-filter-bits-per-key`

+ The length that bloom filter reserves for each key
+ Default value: `10`
+ Unit: byte
### `block-based-bloom-filter`

+ Determines whether each block creates a bloom filter
+ Default value: `false`
### `ribbon-filter-above-level` New in v7.2.0

+ Determines whether to use Ribbon filters for levels greater than or equal to this value and use non-block-based bloom filters for levels less than this value. When this configuration item is set, [`block-based-bloom-filter`](#block-based-bloom-filter) will be ignored.
+ Note that this configuration item takes effect only when [`format-version`](#format-version-new-in-v620) >= 5.
+ Default value: `false`
### `read-amp-bytes-per-bit`

+ Enables or disables statistics of read amplification.
+ Optional values: `0` (disabled), > `0` (enabled).
+ Default value: `0`
+ Minimum value: `0`
### `compression-per-level`

+ The default compression algorithm for each level
+ Default value for `defaultcf`: ["no", "no", "lz4", "lz4", "lz4", "zstd", "zstd"]
+ Default value for `writecf`: ["no", "no", "lz4", "lz4", "lz4", "zstd", "zstd"]
+ Default value for `lockcf`: ["no", "no", "no", "no", "no", "no", "no"]
### `bottommost-level-compression`

+ Sets the compression algorithm of the bottommost layer. This configuration item overrides the `compression-per-level` setting.
+ Ever since data is written to LSM-tree, RocksDB does not directly adopt the last compression algorithm specified in the `compression-per-level` array for the bottommost layer. `bottommost-level-compression` enables the bottommost layer to use the compression algorithm of the best compression effect from the beginning.
+ If you do not want to set the compression algorithm for the bottommost layer, set the value of this configuration item to `disable`.
+ Default value: `"zstd"`
### `write-buffer-size`

+ Memtable size
+ Default value for `defaultcf` and `writecf`: `"128MiB"`
+ Default value for `lockcf`:
    + When `storage.engine="raft-kv"`, the default value is `"32MiB"`.
    + When `storage.engine="partitioned-raft-kv"`, the default value is `"4MiB"`.
+ Minimum value: `0`
+ Unit: KiB|MiB|GiB
### `max-write-buffer-number`

+ The maximum number of memtables. When `storage.flow-control.enable` is set to `true`, `storage.flow-control.memtables-threshold` overrides this configuration item.
+ Default value: `5`
+ Minimum value: `0`
### `min-write-buffer-number-to-merge`

+ The minimum number of memtables required to trigger flush
+ Default value: `1`
+ Minimum value: `0`
### `max-bytes-for-level-base`

+ The maximum number of bytes at base level (level-1). Generally, it is set to 4 times the size of a memtable. When the level-1 data size reaches the limit value of `max-bytes-for-level-base`, the SST files of level-1 and their overlapping SST files of level-2 will be compacted.
+ Default value for `defaultcf` and `writecf`: `"512MiB"`
+ Default value for `lockcf`: `"128MiB"`
+ Minimum value: `0`
+ Unit: KiB|MiB|GiB
+ It is recommended that the value of `max-bytes-for-level-base` is set approximately equal to the data volume in L0 to reduce unnecessary compaction. For example, if the compression method is "no:no:lz4:lz4:lz4:lz4:lz4", the value of `max-bytes-for-level-base` should be `write-buffer-size * 4`, because there is no compression of L0 and L1 and the trigger condition of compaction for L0 is that the number of the SST files reaches 4 (the default value). When L0 and L1 both adopt compaction, you need to analyze RocksDB logs to understand the size of an SST file compressed from a memtable. For example, if the file size is 32 MiB, it is recommended to set the value of `max-bytes-for-level-base` to 128 MiB (`32 MiB * 4`).
### `target-file-size-base`

+ The size of the target file at base level. This value is overridden by `compaction-guard-max-output-file-size` when the `enable-compaction-guard` value is `true`.
+ Default value: `"8MiB"`
+ Minimum value: `0`
+ Unit: KiB|MiB|GiB
### `level0-file-num-compaction-trigger`

+ The maximum number of files at L0 that trigger compaction
+ Default value for `defaultcf` and `writecf`: `4`
+ Default value for `lockcf`: `1`
+ Minimum value: `0`
### `level0-slowdown-writes-trigger`

+ The maximum number of files at L0 that trigger write stall. When `storage.flow-control.enable` is set to `true`, `storage.flow-control.l0-files-threshold` overrides this configuration item.
+ Default value: `20`
+ Minimum value: `0`
### `level0-stop-writes-trigger`

+ The maximum number of files at L0 required to completely block write
+ Default value: `36`
+ Minimum value: `0`
### `max-compaction-bytes`

+ The maximum number of bytes written into disk per compaction
+ Default value: `"2GiB"`
+ Minimum value: `0`
+ Unit: KiB|MiB|GiB
### `compaction-pri`

+ The priority type of compaction
+ Optional values:
    - `"by-compensated-size"`: compact files in order of file size and large files are compacted with higher priority.
    - `"oldest-largest-seq-first"`: prioritize compaction on files with the oldest update time. Use this value **only** when updating hot keys in small ranges.
    - `"oldest-smallest-seq-first"`: prioritize compaction on files with ranges that are not compacted to the next level for a long time. If you randomly update hot keys across the key space, this value can slightly reduce write amplification.
    - `"min-overlapping-ratio"`: prioritize compaction on files with a high overlap ratio. When a file is small in different levels (the result of `the file size in the next level` ÷ `the file size in this level` is small), TiKV compacts this file first. In many cases, this value can effectively reduce write amplification.
+ Default value for `defaultcf` and `writecf`: `"min-overlapping-ratio"`
+ Default value for `lockcf`: `"by-compensated-size"`
### `dynamic-level-bytes`

+ Determines whether to optimize dynamic level bytes
+ Default value: `true`
### `num-levels`

+ The maximum number of levels in a RocksDB file
+ Default value: `7`
### `max-bytes-for-level-multiplier`

+ The default amplification multiple for each layer
+ Default value: `10`
### `compaction-style`

+ Compaction method
+ Optional values: `"level"`, `"universal"`, `"fifo"`
+ Default value: `"level"`
### `disable-auto-compactions`

+ Determines whether to disable auto compaction.
+ Default value: `false`
### `soft-pending-compaction-bytes-limit`

+ The soft limit on the pending compaction bytes. When `storage.flow-control.enable` is set to `true`, `storage.flow-control.soft-pending-compaction-bytes-limit` overrides this configuration item.
+ Default value: `"192GiB"`
+ Unit: KiB|MiB|GiB
### `hard-pending-compaction-bytes-limit`

+ The hard limit on the pending compaction bytes. When `storage.flow-control.enable` is set to `true`, `storage.flow-control.hard-pending-compaction-bytes-limit` overrides this configuration item.
+ Default value: `"256GiB"`
+ Unit: KiB|MiB|GiB
### `enable-compaction-guard`

+ Enables or disables the compaction guard, which is an optimization to split SST files at TiKV Region boundaries. This optimization can help reduce compaction I/O and allows TiKV to use larger SST file size (thus less SST files overall) and at the time efficiently clean up stale data when migrating Regions.
+ Default value for `defaultcf` and `writecf`: `true`
+ Default value for `lockcf`: `false`
### `compaction-guard-min-output-file-size`

+ The minimum SST file size when the compaction guard is enabled. This configuration prevents SST files from being too small when the compaction guard is enabled.
+ Default value: `"8MiB"`
+ Unit: KiB|MiB|GiB
### `compaction-guard-max-output-file-size`

+ The maximum SST file size when the compaction guard is enabled. The configuration prevents SST files from being too large when the compaction guard is enabled. This configuration overrides `target-file-size-base` for the same column family.
+ Default value: `"128MiB"`
+ Unit: KiB|MiB|GiB
