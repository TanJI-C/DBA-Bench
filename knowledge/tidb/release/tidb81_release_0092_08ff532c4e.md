# PD and TiKV changes in TiDB 3.0.0-rc.1

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.0-rc.1.md`
- Source Title: `TiDB 3.0.0-rc.1 Release Notes`
- Source Heading Path: `TiDB 3.0.0-rc.1 Release Notes > PD | TiDB 3.0.0-rc.1 Release Notes > TiKV`
- Source Line Ranges: `62-109`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tikv`
- Topic Tags: `release-notes`, `etcd`, `leader-election`, `hot-region-scheduling`, `metrics`, `engine`, `raftstore`, `coprocessor`, `memory-allocator`, `batch-execution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0092_08ff532c4e`
- Source ID: `tidb-docs-8.1:releases/release-3.0.0-rc.1.md#pd`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `df487a800280b7cbf8e6b55204adbe529291c74a44db85bd298f3c16309037dc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.0-rc.1#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.0-rc.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for PD or TiKV 3.0.0-rc.1 release-note items about ETCD, leader election, hot region scheduling, metrics, engine fixes, raftstore, coprocessor batch execution, or memory allocator changes.
- Retrieval Keywords: PD 3.0.0-rc.1, TiKV 3.0.0-rc.1, Upgrade ETCD, PreVote, Lease deadlock, hot region scheduling, TSO requests metrics, Store ID and Address metrics, GetOperator service, Heartbeat stream, regionScatterer, MergeRegion operator, incorrect statistics of keys, incorrect statistics on read traffic, prefix extractor panic when deleting a range, Iterator Key Bound Option, block cache sharing among different column families, batch commands, properties index distance, batch index scan executor, vectorized evaluation framework, execution summary framework for batch executors, BatchLimitExecutor, tokio-threadpool, batch aggregation framework, BatchSelectionExecutor, AVG, LogicalAnd, tcmalloc
- Follow-up Guidance: The chunk also includes PD fixes for rebuilding a cluster from a single PD node and TiKV server and coprocessor changes that reduce context switch overhead.
- Classification Note: This is a shared PD and TiKV release-notes chunk because the official content groups 3.0.0-rc.1 changes for both components, including PD scheduling and metrics updates and TiKV engine, raftstore, and coprocessor updates.

## Official Source Content

## PD

+ Upgrade ETCD [#1452](https://github.com/pingcap/pd/pull/1452)
    - Unify the log format of etcd and PD server
    - Fix the issue of failing to elect Leader by PreVote
    - Support fast dropping the "propose" and "read" requests that are to fail to avoid blocking the subsequent requests
    - Fix the deadlock issue of Lease
+ Fix the issue that a hot store makes incorrect statistics of keys [#1487](https://github.com/pingcap/pd/pull/1487)
+ Support forcibly rebuilding a PD cluster from a single PD node [#1485](https://github.com/pingcap/pd/pull/1485)
+ Fix the issue that `regionScatterer` might generate an invalid `OperatorStep` [#1482](https://github.com/pingcap/pd/pull/1482)
+ Fix the too short timeout issue of the `MergeRegion` operator [#1495](https://github.com/pingcap/pd/pull/1495)
+ Support giving high priority to hot region scheduling [#1492](https://github.com/pingcap/pd/pull/1492)
+ Add the metrics for recording the time of handling TSO requests on the PD server side [#1502](https://github.com/pingcap/pd/pull/1502)
+ Add the corresponding Store ID and Address to the metrics related to the store [#1506](https://github.com/pingcap/pd/pull/1506)
+ Support the `GetOperator` service [#1477](https://github.com/pingcap/pd/pull/1477)
+ Fix the issue that the error cannot be sent in the Heartbeat stream because the store cannot be found [#1521](https://github.com/pingcap/pd/pull/1521)
## TiKV

+ Engine
    - FIx the issue that may cause incorrect statistics on read traffic [#4436](https://github.com/tikv/tikv/pull/4436)
    - Fix the issue that may cause prefix extractor panic when deleting a range [#4503](https://github.com/tikv/tikv/pull/4503)
    - Optimize memory management to reduce memory allocation and copying for `Iterator Key Bound Option` [#4537](https://github.com/tikv/tikv/pull/4537)
    - Fix the issue that failing to consider learner log gap may in some cases cause panic [#4559](https://github.com/tikv/tikv/pull/4559)
    - Support `block cache` sharing among different `column families` [#4612](https://github.com/tikv/tikv/pull/4612)

+ Server
    - Reduce context switch overhead of `batch commands` [#4473](https://github.com/tikv/tikv/pull/4473)
    - Check the validity of seek iterator status [#4470](https://github.com/tikv/tikv/pull/4470)

+ RaftStore
    - Support configurable `properties index distance` [#4517](https://github.com/tikv/tikv/pull/4517)

+ Coprocessor
    - Add batch index scan executor [#4419](https://github.com/tikv/tikv/pull/4419)
    - Add vectorized evaluation framework [#4322](https://github.com/tikv/tikv/pull/4322)
    - Add execution summary framework for batch executors [#4433](https://github.com/tikv/tikv/pull/4433)
    - Check the maximum column when constructing the RPN expression to avoid invalid column offset that may cause evaluation panic [#4481](https://github.com/tikv/tikv/pull/4481)
    - Add `BatchLimitExecutor` [#4469](https://github.com/tikv/tikv/pull/4469)
    - Replace the original `futures-cpupool` with `tokio-threadpool` in ReadPool to reduce context switch [#4486](https://github.com/tikv/tikv/pull/4486)
    - Add batch aggregation framework [#4533](https://github.com/tikv/tikv/pull/4533)
    - Add `BatchSelectionExecutor` [#4562](https://github.com/tikv/tikv/pull/4562)
    - Add batch aggression function `AVG` [#4570](https://github.com/tikv/tikv/pull/4570)
    - Add RPN function `LogicalAnd`[#4575](https://github.com/tikv/tikv/pull/4575)

+ Misc
    - Support `tcmalloc` as a memory allocator [#4370](https://github.com/tikv/tikv/pull/4370)
