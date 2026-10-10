# TiKV 2.1 GA improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1-ga.md`
- Source Title: `TiDB 2.1 GA Release Notes`
- Source Heading Path: `TiDB 2.1 GA Release Notes > TiKV`
- Source Line Ranges: `205-258`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `lightning`
- Topic Tags: `coprocessor`, `transaction`, `mvcc`, `gc`, `raftstore`, `region-split`, `rocksdb`, `tikv-ctl`, `performance`, `diagnostics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0042_f8aac2e53a`
- Source ID: `tidb-docs-8.1:releases/release-2.1-ga.md#tikv`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `42be7fd8d0fb969b702b766ba97598593d53c6d10429ee4485a6a173e9780987`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1-ga#tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1-ga.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiKV 2.1 GA release-note changes for coprocessor, transaction, Raftstore, RocksDB storage engine, or tikv-ctl diagnostic improvements.
- Retrieval Keywords: TiKV 2.1 GA, Coprocessor ReadPool, LocalReader, BatchSplit, Region Split according to statistics, Region Split according to the number of keys, PreVote, UnsafeDestroyRange, kv_scan upper bound, MVCC scan operation, full table scan, CompactFiles, RocksDB v5.15, IngestExternalFile, tikv-ctl ldb, compact bottommost level, Lightning
- Follow-up Guidance: The chunk also points to linked RFC or tool references for ReadPool, UnsafeDestroyRange, LocalReader, BatchSplit, and the tikv-ctl ldb command.
- Classification Note: This is a self-managed TiKV release-notes chunk because it lists TiKV 2.1 GA improvements across coprocessor, transaction, raftstore, storage engine, and tikv-ctl.

## Official Source Content

## TiKV

+ Coprocessor

    - Add more built-in functions

    - [Add Coprocessor `ReadPool` to improve the concurrency in processing the requests](https://github.com/tikv/rfcs/blob/master/text/0010-read-pool.md)

    - Fix the time function parsing issue and the time zone related issues

    - Optimize the memory usage for pushdown aggregation computing

+ Transaction

    - Optimize the read logic and memory usage of MVCC to improve the performance of the scan operation and the performance of full table scan is 1 time better than that in TiDB 2.0

    - Fold the continuous Rollback records to ensure the read performance

    - [Add the `UnsafeDestroyRange` API to support to collecting space for the dropping table/index](https://github.com/tikv/rfcs/blob/master/text/0002-unsafe-destroy-range.md)

    - Separate the GC module to reduce the impact on write

    - Add the `upper bound` support in the `kv_scan` command

+ Raftstore

    - Improve the snapshot writing process to avoid RocksDB stall

    - [Add the `LocalReader` thread to process read requests and reduce the delay for read requests](https://github.com/tikv/rfcs/pull/17)

    - [Support `BatchSplit` to avoid large Region brought by large amounts of write](https://github.com/tikv/rfcs/pull/6)

    - Support `Region Split` according to statistics to reduce the I/O overhead

    - Support `Region Split` according to the number of keys to improve the concurrency of index scan

    - Improve the Raft message process to avoid unnecessary delay brought by `Region Split`

    - Enable the `PreVote` feature by default to reduce the impact of network isolation on services

+ Storage Engine

    - Fix the `CompactFiles`bug in RocksDB and reduce the impact on importing data using Lightning

    - Upgrade RocksDB to v5.15 to fix the possible issue of snapshot file corruption

    - Improve `IngestExternalFile` to avoid the issue that flush could block write

+ tikv-ctl

    - [Add the `ldb` command to diagnose RocksDB related issues](https://tikv.org/docs/3.0/reference/tools/tikv-ctl/#ldb-command)

    - The `compact` command supports specifying whether to compact data in the bottommost level
