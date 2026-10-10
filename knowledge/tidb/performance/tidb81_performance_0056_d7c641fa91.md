# Reduce KV RocksDB compaction I/O on public cloud

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/best-practices-on-public-cloud.md`
- Source Title: `TiDB Best Practices on Public Cloud`
- Source Heading Path: `TiDB Best Practices on Public Cloud | TiDB Best Practices on Public Cloud > Reduce compaction I/O flow in KV RocksDB | TiDB Best Practices on Public Cloud > Reduce compaction I/O flow in KV RocksDB > Enable Titan | TiDB Best Practices on Public Cloud > Reduce compaction I/O flow in KV RocksDB > Increase all the compression levels`
- Source Line Ranges: `5-44`
- Source Scope: `cloud`
- Primary Component: `tikv`
- Related Components: `cloud`
- Topic Tags: `rocksdb`, `compaction`, `io-throughput`, `write-amplification`, `titan`, `compression`, `row-size`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0056_d7c641fa91`
- Source ID: `tidb-docs-8.1:best-practices/best-practices-on-public-cloud.md#tidb-best-practices-on-public-cloud`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `446a37033afbdd0655f858513ff109dbd1b77052282b21e4a91627716574c551`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/best-practices-on-public-cloud#tidb-best-practices-on-public-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/best-practices-on-public-cloud.md

## Retrieval Guidance

- Use When: Use this chunk when looking for public cloud TiKV guidance to reduce RocksDB compaction I/O bottlenecks, pending compaction bytes growth, or flow control caused by limited disk throughput.
- Retrieval Keywords: Reduce compaction I/O flow in KV RocksDB, RocksDB, pending compaction bytes, flow control, write amplification, disk throughput, Titan, rocksdb.titan, rocksdb.defaultcf.titan, min-blob-size, blob-file-compression, zstd, compression-per-level, rocksdb.defaultcf, average row size larger than 512 bytes, average row size smaller than 512 bytes
- Follow-up Guidance: The content also notes that enabling Titan might slightly degrade range scan performance on the primary key and references the impact of `min-blob-size` on performance.
- Classification Note: This is classified as performance because the content focuses on reducing RocksDB compaction I/O, write amplification, and disk throughput bottlenecks in TiKV on public cloud.

## Official Source Content

# TiDB Best Practices on Public Cloud

Public cloud infrastructure has become an increasingly popular choice for deploying and managing TiDB. However, deploying TiDB on public cloud requires careful consideration of several critical factors, including performance tuning, cost optimization, reliability, and scalability.

This document covers various essential best practices for deploying TiDB on public cloud, such as reducing compaction I/O flow in KV RocksDB, using a dedicated disk for Raft Engine, optimizing costs for cross-AZ traffic, mitigating Google Cloud live migration events, and fine-tuning the PD server in large clusters. By following these best practices, you can maximize the performance, cost efficiency, reliability, and scalability of your TiDB deployment on public cloud.
## Reduce compaction I/O flow in KV RocksDB

As the storage engine of TiKV, [RocksDB](https://rocksdb.org/) is used to store user data. Because the provisioned IO throughput on cloud EBS is usually limited due to cost considerations, RocksDB might exhibit high write amplification, and the disk throughput might become the bottleneck for the workload. As a result, the total number of pending compaction bytes grows over time and triggers flow control, which indicates that TiKV lacks sufficient disk bandwidth to keep up with the foreground write flow.

To alleviate the bottleneck caused by limited disk throughput, you can improve performance by [enabling Titan](#enable-titan). If your average row size is smaller than 512 bytes, Titan is not applicable. In this case, you can improve performance by [increasing all the compression levels](#increase-all-the-compression-levels).
### Enable Titan

[Titan](https://docs.pingcap.com/tidb/stable/storage-engine/titan-overview) is a high-performance [RocksDB](https://github.com/facebook/rocksdb) plugin for key-value separation, which can reduce write amplification in RocksDB when large values are used.

If your average row size is larger than 512 bytes, you can enable Titan to reduce the compaction I/O flow as follows, with `min-blob-size` set to `"512B"` or `"1KB"` and `blob-file-compression` set to `"zstd"`:

```toml
[rocksdb.titan]
enabled = true
[rocksdb.defaultcf.titan]
min-blob-size = "1KB"
blob-file-compression = "zstd"
```

> **Note:**
>
> When Titan is enabled, there might be a slight performance degradation for range scans on the primary key. For more information, see [Impact of `min-blob-size` on performance](https://docs.pingcap.com/tidb/stable/storage-engine/titan-overview#impact-of-min-blob-size-on-performance).
### Increase all the compression levels

If your average row size is smaller than 512 bytes, you can increase all the compression levels of the default column family to `"zstd"` as follows:

```toml
[rocksdb.defaultcf]
compression-per-level = ["zstd", "zstd", "zstd", "zstd", "zstd", "zstd", "zstd"]
```
