# Titan parameters and configuration example

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/storage-engine/titan-configuration.md`
- Source Title: `Titan Configuration`
- Source Heading Path: `Titan Configuration > Parameters | Titan Configuration > Parameters > `min-blob-size` | Titan Configuration > Parameters > `blob-file-compression` and `zstd-dict-size` | Titan Configuration > Parameters > `blob-cache-size` | Titan Configuration > Parameters > `discardable-ratio` and `max-background-gc` | Titan Configuration > Parameters > `rate-bytes-per-sec` | Titan Configuration > Parameters > `shared-blob-cache` (New in v8.0.0) | Titan Configuration > Parameters > Titan configuration example`
- Source Line Ranges: `78-132`
- Source Scope: `all`
- Primary Component: `tikv`
- Related Components: `operator`, `tiup`
- Topic Tags: `titan`, `parameters`, `cache`, `compression`, `garbage-collection`, `compaction-rate`, `version-dependent`, `configuration-example`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0155_738bdd0470`
- Source ID: `tidb-docs-8.1:storage-engine/titan-configuration.md#parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `34b4a777ff10b309f5ce2c477186548198dede55915b0de8b1b519a8b04169ea`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/storage-engine/titan-configuration#parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/storage-engine/titan-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for Titan parameter meanings, tuning-related configuration names, version-specific shared cache behavior, or an example Titan configuration file.
- Retrieval Keywords: Parameters, min-blob-size, blob-file-compression, zstd-dict-size, blob-cache-size, storage.block-cache.capacity, discardable-ratio, max-background-gc, rate-bytes-per-sec, shared-blob-cache, New in v8.0.0, TiKV Details - Thread CPU - RocksDB CPU, [rocksdb.titan], [rocksdb.defaultcf.titan], blob-run-mode, level-merge, enabled = true, blob-file-compression = "zstd"
- Follow-up Guidance: The chunk also includes a complete Titan configuration example and references TiUP configuration changes and Kubernetes cluster configuration.
- Classification Note: This is classified as configuration because the content defines Titan-related TiKV configuration parameters, their effects, and a concrete example configuration.

## Official Source Content

## Parameters

By properly configuring Titan parameters, you can effectively improve database performance and resource utilization. This section introduces some key parameters you can use.
### `min-blob-size`

You can use [`min-blob-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#min-blob-size) to set the threshold for the value size to determine which data is stored in RocksDB and which in Titan's blob files. According to the test, `32KB` is an appropriate threshold. It ensures that Titan's performance does not regress compared with RocksDB. However, in many scenarios, this value is not optimal. It is recommended that you refer to [Impact of `min-blob-size` on performance](https://docs.pingcap.com/tidb/stable/storage-engine/titan-overview#impact-of-min-blob-size-on-performance) to choose an appropriate value. If you want to further improve write performance and can tolerate scan performance regression, you can set it to the minimum value `1KB`.
### `blob-file-compression` and `zstd-dict-size`

You can use [`blob-file-compression`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#blob-file-compression) to specify the compression algorithm used for values in Titan. You can also enable the `zstd` dictionary compression through [`zstd-dict-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#zstd-dict-size) to improve the compression rate.
### `blob-cache-size`

You can use [`blob-cache-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#blob-cache-size) to control the cache size of values in Titan. Larger cache size means higher read performance of Titan. However, too large a cache size causes Out of Memory (OOM) issues.

It is recommended to set the value of `storage.block-cache.capacity` to the store size minus the blob file size, and set `blob-cache-size` to `memory size * 50% - block cache size` according to the monitoring metrics when the database is running stably. This maximizes the blob cache size when the block cache is large enough for the whole RocksDB engine.
### `discardable-ratio` and `max-background-gc`

The [`discardable-ratio`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#discardable-ratio) parameter and [`max-background-gc`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#max-background-gc) parameter significantly impact Titan's read performance and garbage collection process.

When the ratio of obsolete data (the corresponding key has been updated or deleted) in a blob file exceeds the threshold set by [`discardable-ratio`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#discardable-ratio), Titan GC is triggered. Reducing this threshold can reduce space amplification but can cause more frequent Titan GC. Increasing this value can reduce Titan GC, I/O bandwidth, and CPU consumption, but increase disk space usage.

If you observe that the Titan GC thread is in full load for a long time from **TiKV Details** - **Thread CPU** - **RocksDB CPU**, consider adjusting [`max-background-gc`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#max-background-gc) to increase the Titan GC thread pool size.
### `rate-bytes-per-sec`

You can adjust [`rate-bytes-per-sec`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#rate-bytes-per-sec) to limit the I/O rate of RocksDB compaction, reducing its impact on foreground read and write performance during high traffic.
### `shared-blob-cache` (New in v8.0.0)

You can control whether to enable the shared cache for Titan blob files and RocksDB block files through [`shared-blob-cache`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#shared-blob-cache-new-in-v800). The default value is `true`. When the shared cache is enabled, block files have higher priority. This means that TiKV prioritizes meeting the cache needs of block files and then uses the remaining cache for blob files.
### Titan configuration example

The following is an example of the Titan configuration file. You can either [use TiUP to modify the configuration](https://docs.pingcap.com/tidb/stable/maintain-tidb-using-tiup#modify-the-configuration) or [configure a TiDB cluster on Kubernetes](https://docs.pingcap.com/tidb-in-kubernetes/stable/configure-a-tidb-cluster).

```toml
[rocksdb]
rate-bytes-per-sec = 0

[rocksdb.titan]
enabled = true
max-background-gc = 1

[rocksdb.defaultcf.titan]
min-blob-size = "32KB"
blob-file-compression = "zstd"
zstd-dict-size = "16KB"
discardable-ratio = 0.5
blob-run-mode = "normal"
level-merge = false
```
