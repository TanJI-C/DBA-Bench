# RocksDB column family format and Titan configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `format-version` <span class="version-mark">New in v6.2.0</span> | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `ttl` <span class="version-mark">New in v7.2.0</span> | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `periodic-compaction-seconds` <span class="version-mark">New in v7.2.0</span> | TiKV Configuration File > rocksdb.defaultcf | rocksdb.writecf | rocksdb.lockcf | rocksdb.raftcf > `max-compactions` <span class="version-mark">New in v6.6.0</span> | TiKV Configuration File > rocksdb.defaultcf.titan | TiKV Configuration File > rocksdb.defaultcf.titan > `min-blob-size` | TiKV Configuration File > rocksdb.defaultcf.titan > `blob-file-compression` | TiKV Configuration File > rocksdb.defaultcf.titan > `zstd-dict-size` | TiKV Configuration File > rocksdb.defaultcf.titan > `blob-cache-size` | TiKV Configuration File > rocksdb.defaultcf.titan > `shared-blob-cache` (New in v8.0.0) | TiKV Configuration File > rocksdb.defaultcf.titan > `min-gc-batch-size` | TiKV Configuration File > rocksdb.defaultcf.titan > `max-gc-batch-size` | TiKV Configuration File > rocksdb.defaultcf.titan > `discardable-ratio` | TiKV Configuration File > rocksdb.defaultcf.titan > `sample-ratio` | TiKV Configuration File > rocksdb.defaultcf.titan > `merge-small-file-threshold` | TiKV Configuration File > rocksdb.defaultcf.titan > `blob-run-mode` | TiKV Configuration File > rocksdb.defaultcf.titan > `level-merge``
- Source Line Ranges: `1720-1858`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `rocksdb`, `titan`, `sst-format`, `compaction`, `ttl`, `blob-cache`, `compression`, `gc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0378_2b80b70f89`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#format-version-span-class-version-mark-new-in-v6-2-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `88aebdfd03b9b9f4599c742fc16ce1d7b3de7d0ec49b6654cbca753d206c7c73`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#format-version-span-class-version-mark-new-in-v6-2-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiKV RocksDB column family SST format options or Titan settings in rocksdb.defaultcf, including compaction, TTL, blob cache, compression, GC, and blob run mode parameters.
- Retrieval Keywords: format-version, rocksdb.defaultcf, rocksdb.writecf, rocksdb.lockcf, rocksdb.raftcf, ttl, periodic-compaction-seconds, max-compactions, rocksdb.defaultcf.titan, Titan, min-blob-size, blob-file-compression, zstd-dict-size, blob-cache-size, shared-blob-cache, min-gc-batch-size, max-gc-batch-size, discardable-ratio, sample-ratio, merge-small-file-threshold, blob-run-mode, level-merge, SST files, Blob file, GC
- Follow-up Guidance: The source also notes that Titan can only be enabled in rocksdb.defaultcf and is not supported in rocksdb.writecf.
- Classification Note: This is classified as configuration because the content defines TiKV configuration items, defaults, optional values, limits, and behavior for RocksDB column families and Titan.

## Official Source Content

### `format-version` New in v6.2.0

+ The format version of SST files. This configuration item only affects newly written tables. For existing tables, the version information is read from the footer.
+ Optional values:
    - `0`: Can be read by all TiKV versions. The default checksum type is CRC32 and this version does not support changing the checksum type.
    - `1`: Can be read by all TiKV versions. Supports non-default checksum types like xxHash. RocksDB only writes data when the checksum type is not CRC32. (version `0` is automatically upgraded)
    - `2`: Can be read by all TiKV versions. Changes the encoding of compressed blocks using LZ4, BZip2 and Zlib compression.
    - `3`: Can be read by TiKV v2.1 and later versions. Changes the encoding of the keys in index blocks.
    - `4`: Can be read by TiKV v3.0 and later versions. Changes the encoding of the values in index blocks.
    - `5`: Can be read by TiKV v6.1 and later versions. Full and partitioned filters use a faster and more accurate Bloom filter implementation with a different schema.
+ Default value:

    + When `storage.engine="raft-kv"`, the default value is `2`.
    + When `storage.engine="partitioned-raft-kv"`, the default value is `5`.
### `ttl` New in v7.2.0

+ SST files with updates older than the TTL will be automatically selected for compaction. These SST files will go through the compaction in a cascading way so that they can be compacted to the bottommost level or file.
+ Default value: `"0s"`, meaning that no SST file is selected by default.
+ Unit: s(second)|h(hour)|d(day)
### `periodic-compaction-seconds` New in v7.2.0

+ The time interval for periodic compaction. SST files with updates older than this value will be selected for compaction and rewritten to the same level where these SST files originally reside.
+ Default value: `"0s"`, meaning that periodic compaction is disabled by default.
+ Unit: s(second)|h(hour)|d(day)
### `max-compactions` New in v6.6.0

+ The maximum number of concurrent compaction tasks. The value `0` means no limit.
+ Default value: `0`
## rocksdb.defaultcf.titan

> **Note:**
>
> Titan can only be enabled in `rocksdb.defaultcf`. It is not supported to enable Titan in `rocksdb.writecf`.

Configuration items related to `rocksdb.defaultcf.titan`.
### `min-blob-size`

> **Note:**
>
> - Starting from TiDB v7.6.0, Titan is enabled by default to enhance the performance of wide table and JSON data writing and point query. The default value of `min-blob-size` changes from `1KiB` to `32KiB`. This means that values exceeding `32KiB` is stored in Titan, while other data continues to be stored in RocksDB.
> - To ensure configuration consistency, for existing clusters upgrading to TiDB v7.6.0 or later versions, if you do not explicitly set `min-blob-size` before the upgrade, TiDB retains the previous default value of `1KiB`.
> - A value smaller than `32KiB` might affect the performance of range scans. However, if the workload primarily involves heavy writes and point queries, you can consider decreasing the value of `min-blob-size` for better performance.

+ The smallest value stored in a Blob file. Values smaller than the specified size are stored in the LSM-Tree.
+ Default value: `"32KiB"`
+ Minimum value: `0`
+ Unit: KiB|MiB|GiB
### `blob-file-compression`

> **Note:**
>
> - Snappy compressed files must be in the [official Snappy format](https://github.com/google/snappy). Other variants of Snappy compression are not supported.
> - Starting from TiDB v7.6.0, the default value of `blob-file-compression` changes from `"lz4"` to `"zstd"`.

+ The compression algorithm used in a Blob file
+ Optional values: `"no"`, `"snappy"`, `"zlib"`, `"bzip2"`, `"lz4"`, `"lz4hc"`, `"zstd"`
+ Default value: `"zstd"`
### `zstd-dict-size`

+ The zstd dictionary compression size. The default value is `"0KiB"`, which means to disable the zstd dictionary compression. In this case, Titan compresses data based on single values, whereas RocksDB compresses data based on blocks (`32KiB` by default). When the average size of Titan values is less than `32KiB`, Titan's compression ratio is lower than that of RocksDB. Taking JSON as an example, the store size in Titan can be 30% to 50% larger than that of RocksDB. The actual compression ratio depends on whether the value content is suitable for compression and the similarity among different values. You can enable the zstd dictionary compression to increase the compression ratio by configuring `zstd-dict-size` (for example, set it to `16KiB`). The actual store size can be lower than that of RocksDB. But the zstd dictionary compression might lead to about 10% performance regression in specific workloads.
+ Default value: `"0KiB"`
+ Unit: KiB|MiB|GiB
### `blob-cache-size`

+ The cache size of a Blob file
+ Default value: `"0GiB"`
+ Minimum value: `0`
+ Recommended value: `0`. Starting from v8.0.0, TiKV introduces the `shared-blob-cache` configuration item and enables it by default, so there is no need to set `blob-cache-size` separately. The configuration of `blob-cache-size` only takes effect when `shared-blob-cache` is set to `false`.
+ Unit: KiB|MiB|GiB
### `shared-blob-cache` (New in v8.0.0)

+ Controls whether to enable the shared cache for Titan blob files and RocksDB block files.
+ Default value: `true`. When the shared cache is enabled, block files have higher priority. This means that TiKV prioritizes meeting the cache needs of block files and then uses the remaining cache for blob files.
### `min-gc-batch-size`

+ The minimum total size of Blob files required to perform GC for one time
+ Default value: `"16MiB"`
+ Minimum value: `0`
+ Unit: KiB|MiB|GiB
### `max-gc-batch-size`

+ The maximum total size of Blob files allowed to perform GC for one time
+ Default value: `"64MiB"`
+ Minimum value: `0`
+ Unit: KiB|MiB|GiB
### `discardable-ratio`

+ When the ratio of obsolete data (the corresponding key has been updated or deleted) in a Blob file exceeds the following threshold, Titan GC is triggered. When Titan writes the valid data of this Blob file to another file, you can use the `discardable-ratio` value to estimate the upper limits of write amplification and space amplification (assuming the compression is disabled).

    Upper limit of write amplification = 1 / `discardable-ratio`

    Upper limit of space amplification = 1 / (1 - `discardable-ratio`)

    From these two equations, you can see that decreasing the value of `discardable_ratio` can reduce space amplification but results in more frequent GC in Titan. Increasing the value reduces the frequency of Titan GC, thereby lowering the corresponding I/O bandwidth and CPU usage, but increases disk usage.

+ Default value: `0.5`
+ Minimum value: `0`
+ Maximum value: `1`
### `sample-ratio`

+ The ratio of (data read from a Blob file/the entire Blob file) when sampling the file during GC
+ Default value: `0.1`
+ Minimum value: `0`
+ Maximum value: `1`
### `merge-small-file-threshold`

+ When the size of a Blob file is smaller than this value, the Blob file might still be selected for GC. In this situation, `discardable-ratio` is ignored.
+ Default value: `"8MiB"`
+ Minimum value: `0`
+ Unit: KiB|MiB|GiB
### `blob-run-mode`

+ Specifies the running mode of Titan.
+ Optional values:
    + `normal`: Writes data to the blob file when the value size exceeds [`min-blob-size`](#min-blob-size).
    + `read-only`: Refuses to write new data to the blob file, but still reads the original data from the blob file.
    + `fallback`: Writes data in the blob file back to LSM.
+ Default value: `normal`
### `level-merge`

+ Determines whether to optimize the read performance. When `level-merge` is enabled, there is more write amplification.
+ Default value: `false`
