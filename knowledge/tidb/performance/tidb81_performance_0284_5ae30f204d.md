# TiKV memory tuning overview and parameter specification intro

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tune-tikv-memory-performance.md`
- Source Title: `Tune TiKV Memory Parameter Performance`
- Source Heading Path: `Tune TiKV Memory Parameter Performance | Tune TiKV Memory Parameter Performance > Parameter specification`
- Source Line Ranges: `5-31`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `memory-tuning`, `rocksdb`, `raftdb`, `column-families`, `block-cache`, `write-buffer`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0284_5ae30f204d`
- Source ID: `tidb-docs-8.1:tune-tikv-memory-performance.md#tune-tikv-memory-parameter-performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `405e70e27cd0c57bcef2e195a3b323fab6a1f40408fb0e7b7df028a18e290ba2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tune-tikv-memory-performance#tune-tikv-memory-parameter-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tune-tikv-memory-performance.md

## Retrieval Guidance

- Use When: Use this chunk when identifying which TiKV memory-related RocksDB and RaftDB configuration sections control block cache and write buffer behavior for different column families.
- Retrieval Keywords: Tune TiKV Memory Parameter Performance, Parameter specification, RocksDB, RaftDB, Column Families, default CF, write CF, lock CF, raftdb.defaultcf, rocksdb.defaultcf, rocksdb.writecf, storage.block-cache, capacity, write-buffer-size, shared block cache
- Follow-up Guidance: The source points to etc/config-template.toml, TiKV configuration file, TiUP configuration modification, and dynamic config for the limited set of items that can be modified dynamically.
- Classification Note: This chunk is classified as TiKV performance content because it introduces memory tuning parameters tied to RocksDB, RaftDB, column families, block cache, and write buffers in self-managed deployments.

## Official Source Content

# Tune TiKV Memory Parameter Performance

This document describes how to tune the TiKV parameters for optimal performance. You can find the default configuration file in [etc/config-template.toml](https://github.com/tikv/tikv/blob/release-8.1/etc/config-template.toml). To modify the configuration, you can [use TiUP](https://docs.pingcap.com/tidb/stable/maintain-tidb-using-tiup#modify-the-configuration) or [modify TiKV dynamically](https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tikv-configuration-dynamically) for a limited set of configuration items. For the complete configuration, see [TiKV configuration file](https://docs.pingcap.com/tidb/stable/tikv-configuration-file).

TiKV uses RocksDB for persistent storage at the bottom level of the TiKV architecture. Therefore, many of the performance parameters are related to RocksDB. TiKV uses two RocksDB instances: the default RocksDB instance stores KV data, the Raft RocksDB instance (RaftDB) stores Raft logs.

TiKV implements `Column Families` (CF) from RocksDB.

- The default RocksDB instance stores KV data in the `default`, `write` and `lock` CFs.

    - The `default` CF stores the actual data. The corresponding parameters are in `[rocksdb.defaultcf]`.
    - The `write` CF stores the version information in Multi-Version Concurrency Control (MVCC) and index-related data. The corresponding parameters are in `[rocksdb.writecf]`.
    - The `lock` CF stores the lock information. The system uses the default parameters.

- The Raft RocksDB (RaftDB) instance stores Raft logs.

    - The `default` CF stores the Raft log. The corresponding parameters are in `[raftdb.defaultcf]`.

After TiKV 3.0, by default, all CFs share one block cache instance. You can configure the size of the cache by setting the `capacity` parameter under `[storage.block-cache]`. The bigger the block cache, the more hot data can be cached, and the easier to read data, in the meantime, the more system memory is occupied.

Before TiKV 3.0, shared block cache is not supported, and you need to configure block cache for each CF individually.

Each CF also has a separate `write buffer`. You can configure the size by setting the `write-buffer-size` parameter.
## Parameter specification
