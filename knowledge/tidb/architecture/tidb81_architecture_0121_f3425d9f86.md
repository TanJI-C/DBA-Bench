# TiKV thread pool overview and read-only request model

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tune-tikv-thread-performance.md`
- Source Title: `Tune TiKV Thread Pool Performance`
- Source Heading Path: `Tune TiKV Thread Pool Performance | Tune TiKV Thread Pool Performance > Thread pool introduction | Tune TiKV Thread Pool Performance > TiKV read-only requests`
- Source Line Ranges: `5-40`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `thread-pools`, `grpc`, `scheduler`, `raftstore`, `storewriter`, `apply`, `rocksdb`, `unifyreadpool`, `read-requests`, `unified-pool`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0121_f3425d9f86`
- Source ID: `tidb-docs-8.1:tune-tikv-thread-performance.md#tune-tikv-thread-pool-performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `31b5d310059c47248d76ca23a012f3d6e7160721ad7296d3eb14a5ef38523386`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance#tune-tikv-thread-pool-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tune-tikv-thread-performance.md

## Retrieval Guidance

- Use When: Use this chunk when the need is to identify TiKV internal thread pools and how read-only requests are handled, including the unified read pool behavior after upgrade.
- Retrieval Keywords: gRPC thread pool, Scheduler thread pool, Raftstore thread pool, StoreWriter thread pool, Apply thread pool, RocksDB thread pool, UnifyReadPool thread pool, store-io-pool-size, readpool.storage.use-unified-pool, use-unified-pool, TiKV read-only requests, kv get, kv batch get, raw kv get, coprocessor, Storage Read Pool, Coprocessor Read Pool
- Follow-up Guidance: The content also states that starting from TiKV v5.0 all read requests use the unified thread pool by default, unless an upgraded cluster kept `readpool.storage.use-unified-pool` set to `false`.
- Classification Note: This chunk is classified as architecture because it describes the roles and request flow of TiKV components such as gRPC, Scheduler, Raftstore, StoreWriter, Apply, RocksDB, and UnifyReadPool.

## Official Source Content

# Tune TiKV Thread Pool Performance

This document introduces TiKV internal thread pools and how to tune their performance.
## Thread pool introduction

The TiKV thread pool is mainly composed of gRPC, Scheduler, UnifyReadPool, Raftstore, StoreWriter, Apply, RocksDB, and some scheduled tasks and detection components that do not consume much CPU. This document mainly introduces a few CPU-intensive thread pools that affect the performance of read and write requests.

* The gRPC thread pool: it handles all network requests and forwards requests of different task types to different thread pools.

* The Scheduler thread pool: it detects write transaction conflicts, converts requests like the two-phase commit, pessimistic locking, and transaction rollbacks into key-value pair arrays, and then sends them to the Raftstore thread for Raft log replication.

* The Raftstore thread pool:

    - It processes all Raft messages and the proposal to add a new log.
    - It writes Raft logs to the disk. If the value of  [`store-io-pool-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#store-io-pool-size-new-in-v530) is `0`, the Raftstore thread writes the logs to the disk; if the value is not `0`, the Raftstore thread sends the logs to the StoreWriter thread.
    - When Raft logs in the majority of replicas are consistent, the Raftstore thread sends the logs to the Apply thread.

* The StoreWriter thread pool: it writes all Raft logs to the disk and returns the result to the Raftstore thread.

* The Apply thread pool: it receives the submitted log sent from the Raftstore thread pool, parses it as a key-value request, then writes it to RocksDB, calls the callback function to notify the gRPC thread pool that the write request is complete, and returns the result to the client.

* The RocksDB thread pool: it is a thread pool for RocksDB to compact and flush tasks. For RocksDB's architecture and `Compact` operation, refer to [RocksDB: A Persistent Key-Value Store for Flash and RAM Storage](https://github.com/facebook/rocksdb).

* The UnifyReadPool thread pool: it is a combination of the Coprocessor thread pool and Storage Read Pool. All read requests such as kv get, kv batch get, raw kv get, and coprocessor are executed in this thread pool.
## TiKV read-only requests

TiKV's read requests are divided into the following types:

- Simple queries that specify a certain row or several rows, running in the Storage Read Pool.
- Complex aggregate calculation and range queries, running in the Coprocessor Read Pool.

Starting from TiKV v5.0, all read requests use the unified thread pool for queries by default. If your TiKV cluster is upgraded from TiKV v4.0 and the `use-unified-pool` configuration of `readpool.storage` was set to `false` before the upgrade, all read requests continue using different thread pools after the upgrade. In this scenario, to make all read requests use the unified thread pool for queries, you can set the value of `readpool.storage.use-unified-pool` to `true`.
