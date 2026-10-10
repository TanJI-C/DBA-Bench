# TiDB 3.0 Beta Tools PD and TiKV changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0-beta.md`
- Source Title: `TiDB 3.0 Beta Release Notes`
- Source Heading Path: `TiDB 3.0 Beta Release Notes > Tools | TiDB 3.0 Beta Release Notes > PD | TiDB 3.0 Beta Release Notes > TiKV`
- Source Line Ranges: `80-107`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `lightning`, `pd`, `tikv`
- Topic Tags: `release-notes`, `import`, `metadata`, `scheduling`, `metrics`, `gc`, `storage-engine`, `raft`, `monitoring`, `batch-processing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0084_187028ee0f`
- Source ID: `tidb-docs-8.1:releases/release-3.0-beta.md#tools`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cf597fdf4049c076be0c74d843b178ac2e0f2a6cc7857d0101801bed3de2a280`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0-beta#tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0-beta.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 3.0 Beta release-note details about TiDB Lightning import changes, PD metadata and scheduling additions, or TiKV GC, monitoring, storage engine, Raft, and batching updates.
- Retrieval Keywords: TiDB 3.0 Beta Release Notes, TiDB Lightning, batch import for a single table, converting SQL statements to KV pairs, PD, RegionStorage, Region metadata, shuffle hot Region scheduler, scheduling parameter related metrics, cluster label related metrics, importing data simulator, Watch issue about leader election, TiKV, distributed GC, RocksDB Level 0 files, Write Stall, reverse raw_scan, raw_batch_scan, HTTP to obtain monitoring information, DST, Raft messages in batch, Titan, gRPC v1.17.2, client requests and replies in batch, multi-thread Apply, multi-thread Raftstore
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a shared release-notes section because the official content covers multiple components in TiDB 3.0 Beta, specifically Tools, PD, and TiKV.

## Official Source Content

## Tools

+ TiDB Lightning
    - Speed up converting SQL statements to KV pairs remarkably [#110](https://github.com/pingcap/tidb-lightning/pull/110)
    - Support batch import for a single table to improve import performance and stability [#113](https://github.com/pingcap/tidb-lightning/pull/113)
## PD

- Add `RegionStorage` to store Region metadata separately [#1237](https://github.com/pingcap/pd/pull/1237)
- Add shuffle hot Region scheduler [#1361](https://github.com/pingcap/pd/pull/1361)
- Add scheduling parameter related metrics [#1406](https://github.com/pingcap/pd/pull/1406)
- Add cluster label related metrics [#1402](https://github.com/pingcap/pd/pull/1402)
- Add the importing data simulator [#1263](https://github.com/pingcap/pd/pull/1263)
- Fix the `Watch` issue about leader election [#1396](https://github.com/pingcap/pd/pull/1396)
## TiKV

- Support distributed GC [#3179](https://github.com/tikv/tikv/pull/3179)
- Check RocksDB Level 0 files before applying snapshots to avoid Write Stall [#3606](https://github.com/tikv/tikv/pull/3606)
- Support reverse `raw_scan` and `raw_batch_scan` [#3742](https://github.com/tikv/tikv/pull/3724)
- Support using HTTP to obtain monitoring information [#3855](https://github.com/tikv/tikv/pull/3855)
- Support DST better [#3786](https://github.com/tikv/tikv/pull/3786)
- Support receiving and sending Raft messages in batch [#3931](https://github.com/tikv/tikv/pull/3913)
- Introduce a new storage engine Titan [#3985](https://github.com/tikv/tikv/pull/3985)
- Upgrade gRPC to v1.17.2 [#4023](https://github.com/tikv/tikv/pull/4023)
- Support receiving the client requests and sending replies in batch [#4043](https://github.com/tikv/tikv/pull/4043)
- Support multi-thread Apply [#4044](https://github.com/tikv/tikv/pull/4044)
- Support multi-thread Raftstore [#4066](https://github.com/tikv/tikv/pull/4066)
