# PD and TiKV 3.0 GA changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0-ga.md`
- Source Title: `TiDB 3.0 GA Release Notes`
- Source Heading Path: `TiDB 3.0 GA Release Notes > PD | TiDB 3.0 GA Release Notes > TiKV`
- Source Line Ranges: `119-176`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tikv`
- Topic Tags: `release-notes`, `api`, `configuration`, `scheduler`, `region-merge`, `hot-region`, `raftstore`, `gc`, `monitoring`, `experimental-features`, `performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0087_d60392d96c`
- Source ID: `tidb-docs-8.1:releases/release-3.0-ga.md#pd`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0ac5b0cbd81345c144bf46135ef339f518b7d931a6dfddd5fabe4fdf40a28545`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0-ga#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0-ga.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 3.0 GA release-note details about PD or TiKV new APIs, configuration items, scheduler behavior, monitoring, GC, Raftstore, or experimental features.
- Retrieval Keywords: TiDB 3.0 GA Release Notes, PD and TiKV 3.0 GA changes, remove-tombstone API, ScanRegions API, GetOperator API, GetStores API, enable-two-way-merge, hot-region-schedule-limit, hot-region-cache-hits-threshold, store-balance-rate, waitingOperator queue, shuffle-hot-region scheduler, Region Scatter, distributed GC, concurrent lock resolving, raw_scan, raw_batch_scan, Multi-thread Raftstore, Multi-thread Apply, Titan, pessimistic transaction mode, getting monitoring information via HTTP, Insert semantics, block cache, batch commands, read index, GC worker, Hibernate Regions, EXPLAIN ANALYZE, work-stealing thread pool
- Follow-up Guidance: The source also states that PD adds monitoring metrics for scheduling parameters, cluster label information, and TSO request processing time, while TiKV adds performance and monitoring items related to configuration information, key bound crossing, read index, and GC worker.
- Classification Note: This is a self-managed release-notes chunk for shared PD and TiKV changes in TiDB 3.0 GA, covering APIs, configurations, scheduler optimizations, engine and server changes, monitoring, and experimental capabilities.

## Official Source Content

## PD

+ Support re-creating a cluster from a single node
+ Migrate Region metadata from etcd to the go-leveldb storage engine to solve the storage bottleneck in etcd for large-scale clusters
+ API
    - Add the `remove-tombstone` API to clear Tombstone stores
    - Add the `ScanRegions` API to batch query Region information
    - Add the `GetOperator` API to query running operators
    - Optimize the performance of the `GetStores` API
+ Configurations
    - Optimize configuration check logic to avoid configuration item errors
    - Add `enable-two-way-merge` to control the direction of Region merge
    - Add `hot-region-schedule-limit` to control the scheduling rate for hot Regions
    - Add `hot-region-cache-hits-threshold` to identify hotspot when hitting multiple thresholds consecutively
    - Add the `store-balance-rate` configuration item to control the maximum numbers of balance Region operators allowed per minute
+ Scheduler Optimizations
    - Add the store limit mechanism for separately controlling the speed of operators for each store
    - Support the `waitingOperator` queue to optimize the resource race among different schedulers
    - Support scheduling rate limit to actively send scheduling operations to TiKV. This improves the scheduling rate by limiting the number of concurrent scheduling tasks on a single node.
    - Optimize the `Region Scatter` scheduling to be not restrained by the limit mechanism
    - Add the `shuffle-hot-region` scheduler to facilitate TiKV stability test in scenarios of poor hotspot scheduling
+ Simulator
    - Add simulator for data import scenarios
    - Support setting different heartbeats intervals for the Store
+ Others
    - Upgrade etcd to solve the issues of inconsistent log output formats, Leader selection failure in prevote, and lease deadlocking
    - Develop a unified log format specification with restructured log system to facilitate collection and analysis by tools
    - Add monitoring metrics including scheduling parameters, cluster label information, and time consumed by PD to process TSO requests, Store ID, and address information.
## TiKV

+ Support distributed GC and concurrent lock resolving for improved GC performance
+ Support reversed `raw_scan` and `raw_batch_scan`
+ Support Multi-thread Raftstore and Multi-thread Apply to improve scalabilities, concurrency capacity, and resource usage within a single node. Performance improves by 70% under the same level of pressure
+ Support batch receiving and sending Raft messages, improving TPS by 7% for write intensive scenarios
+ Support checking RocksDB Level 0 files before applying snapshots to avoid write stall
+ Introduce Titan, a key-value plugin that improves write performance for scenarios with value sizes greater than 1KiB, and relieves write amplification in certain degrees
+ Support the pessimistic transaction mode (**Experimental**)
+ Support getting monitoring information via HTTP
+ Modify the semantics of `Insert` to allow Prewrite to succeed only when there is no Key
+ Develop a unified log format specification with restructured log system to facilitate collection and analysis by tools
+ Add performance metrics related to configuration information and key bound crossing
+ Support Local Reader in RawKV to improve performance
+ Engine
    - Optimize memory management to reduce memory allocation and copying for `Iterator Key Bound Option`
    - Support `block cache` sharing among different column families
+ Server
    - Reduce context switch overhead from `batch commands`
    - Remove `txn scheduler`
    - Add monitoring items related to `read index` and `GC worker`
+ RaftStore
    - Support Hibernate Regions to optimize CPU consumption from RaftStore (**Experimental**)
    - Remove the local reader thread
+ Coprocessor
    - Refactor the computation framework to implement vector operators, computation using vector expressions, and vector aggregations to improve performance
    - Support providing operator execution status for the `EXPLAIN ANALYZE` statement in TiDB
    - Switch to the `work-stealing` thread pool model to reduce context switch cost
