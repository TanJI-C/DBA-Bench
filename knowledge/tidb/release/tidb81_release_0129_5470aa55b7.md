# TiKV fixes, defaults, and pessimistic lock improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.8.md`
- Source Title: `TiDB 3.0.8 Release Notes`
- Source Heading Path: `TiDB 3.0.8 Release Notes > TiKV`
- Source Line Ranges: `76-90`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`
- Topic Tags: `coprocessor`, `raftstore`, `engine`, `transaction`, `pessimistic-locking`, `region-splitting`, `defaults`, `gc`, `rocksdb`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0129_5470aa55b7`
- Source ID: `tidb-docs-8.1:releases/release-3.0.8.md#tikv`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3c967478ce45ed4759772e5971ab87fc299bb212dc5e09d783d185a2a0b4521b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.8#tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.8.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiKV 3.0.8 changes about Coprocessor logging, Raftstore defaults, RocksDB iterator handling, GC blocking, or pessimistic lock performance.
- Retrieval Keywords: TiKV 3.0.8, Coprocessor log error to warn, statistics sampling data deleting before inserting, peerfsm destroy panic, split-region-on-table default false, disable splitting Regions by table by default, RocksDB iterator errors empty data, pessimistic locks incorrectly cleaned up, GC is blocked, pessimistic lock waiting mechanism, lock conflict is severe, tikv_alloc jemalloc
- Follow-up Guidance: The source also lists that the default value of `tikv_alloc` is updated from `tikv_alloc/default` to `jemalloc`.
- Classification Note: This is a release-note chunk for the TiKV component covering fixes, default value changes, and transaction behavior improvements in self-managed TiDB 3.0.8.

## Official Source Content

## TiKV

+ Coprocessor
    - Modify the level of the output log from `error` to `warn` when an error occurs in Coprocessor [#6051](https://github.com/tikv/tikv/pull/6051)
    - Modify the update behavior of statistics sampling data from directly updating the row to deleting before inserting, to keep consistency with the update behavior of tidb-server [#6069](https://github.com/tikv/tikv/pull/6096)
+ Raftstore
    - Fix the panic caused by repeatedly sending the `destroy` message to `peerfsm` and `peerfsm` being destroyed multiple times [#6297](https://github.com/tikv/tikv/pull/6297)
    - Update the default value of `split-region-on-table` from `true` to `false` to disable splitting Regions by table by default [#6253](https://github.com/tikv/tikv/pull/6253)
+ Engine
    - Fix the issue that empty data might be returned because RocksDB iterator errors are not correctly processed in extreme conditions [#6326](https://github.com/tikv/tikv/pull/6326)
+ Transaction
    - Fix the issue that TiKV fails to write data into keys and GC is blocked because the pessimistic locks are incorrectly cleaned up [#6354](https://github.com/tikv/tikv/pull/6354)
    - Optimize the pessimistic lock waiting mechanism to improve the performance in scenarios where the lock conflict is severe [#6296](https://github.com/tikv/tikv/pull/6296)
+ Update the default value of `tikv_alloc` from `tikv_alloc/default` to `jemalloc` [#6206](https://github.com/tikv/tikv/pull/6206)
