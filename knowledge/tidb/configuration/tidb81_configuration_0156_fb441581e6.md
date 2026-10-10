# Enable experimental Titan Level Merge

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/storage-engine/titan-configuration.md`
- Source Title: `Titan Configuration`
- Source Heading Path: `Titan Configuration > Level Merge (experimental)`
- Source Line Ranges: `174-189`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `titan`, `level-merge`, `experimental`, `range-query`, `gc`, `write-performance`, `space-amplification`, `write-amplification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0156_fb441581e6`
- Source ID: `tidb-docs-8.1:storage-engine/titan-configuration.md#level-merge-experimental`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0cdd5d4e3dd01dcbf5cb27ef115fe111b5082987e776a3b0cdf28bbf5a821773`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/storage-engine/titan-configuration#level-merge-experimental
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/storage-engine/titan-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when asking about the experimental Titan Level Merge option, its configuration name, or its stated effects on range query, GC impact, disk usage, and write amplification.
- Retrieval Keywords: Level Merge (experimental), rocksdb.defaultcf.titan.level-merge, level-merge = true, Titan range query, Titan GC, foreground write operations, write performance, space amplification, disk usage, write amplification, native RocksDB
- Follow-up Guidance: 
- Classification Note: This is classified as a configuration topic because the content introduces the level-merge option and summarizes the documented effects of enabling it.

## Official Source Content

## Level Merge (experimental)

In TiKV 4.0, [Level Merge](https://docs.pingcap.com/tidb/stable/storage-engine/titan-overview#level-merge), a new algorithm, is introduced to improve the performance of range query and to reduce the impact of Titan GC on the foreground write operations. You can enable Level Merge using the following option:

```toml
[rocksdb.defaultcf.titan]
level-merge = true
```

Enabling Level Merge has the following benefits:

- Greatly improve the performance of Titan range query.
- Reduce the impact of Titan GC on the foreground write operations and improve write performance.
- Reduce space amplification of Titan and the disk usage (compared to the disk usage with the default configuration).

Accordingly, the write amplification with Level Merge enabled is slightly higher than that of Titan but is still lower than that of the native RocksDB.
