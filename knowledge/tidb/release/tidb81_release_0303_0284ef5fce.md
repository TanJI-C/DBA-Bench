# 6.1.0 improvements across TiDB, TiKV, PD, TiFlash, BR, Lightning, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.0.md`
- Source Title: `TiDB 6.1.0 Release Notes`
- Source Heading Path: `TiDB 6.1.0 Release Notes > Improvements`
- Source Line Ranges: `326-370`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `lightning`, `ticdc`
- Topic Tags: `improvements`, `sql`, `cdc`, `raft`, `snapshots`, `memory`, `region-labels`, `region-buckets`, `backup`, `restore`, `data-import`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0303_0284ef5fce`
- Source ID: `tidb-docs-8.1:releases/release-6.1.0.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b6b77f6a934723b04103cadf27af0270e548972a2500b2191aba39c4f5b552a6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 6.1.0 Improvements section that lists new capabilities and performance or stability improvements across TiDB, TiKV, PD, TiFlash, BR, TiDB Lightning, and TiCDC.
- Retrieval Keywords: TiDB 6.1.0 Improvements, UnionScanRead operator, EXPLAIN add the MPP task type, rand() as the default value of a column, uuid() as the default value of a column, modify the character set of columns from latin1 to utf8 utf8mb4, old value hit rate of CDC, in-memory pessimistic lock, health check to detect unavailable Raftstore, Region Cache, Raft Engine memory limit, damaged SST files, CDC supports RawKV, splitting a large snapshot file into multiple files, snapshot garbage collection background thread, max-grpc-send-msg-len, raft-msg-max-batch-size, online unsafe recovery plan through Raft, time-to-live TTL for region labels, Region Buckets, swagger server by default, Optimize memory calculation for an aggregate operator, backing up and restoring empty databases, Scatter Region to batch mode, splitting large transactions during replication
- Follow-up Guidance: The chunk groups the improvements by component: TiDB, TiKV, PD, TiFlash, Backup & Restore (BR), TiDB Lightning, and TiCDC.
- Classification Note: This is classified as a release chunk because it is the Improvements section of the TiDB 6.1.0 release notes and enumerates component-specific enhancements.

## Official Source Content

## Improvements

+ TiDB

    - Improve the performance of the `UnionScanRead` operator [#32433](https://github.com/pingcap/tidb/issues/32433)
    - Improve the display of task types in the output of `EXPLAIN` (add the MPP task type) [#33332](https://github.com/pingcap/tidb/issues/33332)
    - Support using `rand()` as the default value of a column [#10377](https://github.com/pingcap/tidb/issues/10377)
    - Support using `uuid()` as the default value of a column [#33870](https://github.com/pingcap/tidb/issues/33870)
    - Support modifying the character set of columns from `latin1` to `utf8`/`utf8mb4` [#34008](https://github.com/pingcap/tidb/issues/34008)

+ TiKV

    - Improve the old value hit rate of CDC when using in-memory pessimistic lock [#12279](https://github.com/tikv/tikv/issues/12279)
    - Improve the health check to detect unavailable Raftstore, so that the TiKV client can update Region Cache in time [#12398](https://github.com/tikv/tikv/issues/12398)
    - Support setting memory limit on Raft Engine [#12255](https://github.com/tikv/tikv/issues/12255)
    - TiKV automatically detects and deletes the damaged SST files to improve the product availability [#10578](https://github.com/tikv/tikv/issues/10578)
    - CDC supports RawKV [#11965](https://github.com/tikv/tikv/issues/11965)
    - Support splitting a large snapshot file into multiple files [#11595](https://github.com/tikv/tikv/issues/11595)
    - Move the snapshot garbage collection from Raftstore to background thread to prevent snapshot GC from blocking Raftstore message loops [#11966](https://github.com/tikv/tikv/issues/11966)
    - Support dynamic setting of the maximum message length (`max-grpc-send-msg-len`) and the maximum batch size of gPRC messages (`raft-msg-max-batch-size`) [#12334](https://github.com/tikv/tikv/issues/12334)
    - Support executing online unsafe recovery plan through Raft [#10483](https://github.com/tikv/tikv/issues/10483)

+ PD
    - Support time-to-live (TTL) for region labels [#4694](https://github.com/tikv/pd/issues/4694)
    - Support Region Buckets [#4668](https://github.com/tikv/pd/issues/4668)
    - Disable compiling swagger server by default [#4932](https://github.com/tikv/pd/issues/4932)

+ TiFlash

    - Optimize memory calculation for an aggregate operator so that a more efficient algorithm is used in the merge phase [#4451](https://github.com/pingcap/tiflash/issues/4451)

+ Tools

    + Backup & Restore (BR)

        - Support backing up and restoring empty databases [#33866](https://github.com/pingcap/tidb/issues/33866)

    + TiDB Lightning

        - Optimize Scatter Region to batch mode to improve the stability of the Scatter Region process [#33618](https://github.com/pingcap/tidb/issues/33618)

    + TiCDC

        - TiCDC supports splitting large transactions during replication, which significantly reduces replication latency caused by large transactions [#5280](https://github.com/pingcap/tiflow/issues/5280)
