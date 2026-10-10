# PD, TiKV, and tools changes in 3.0.0-rc.2

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.0-rc.2.md`
- Source Title: `TiDB 3.0.0-rc.2 Release Notes`
- Source Heading Path: `TiDB 3.0.0-rc.2 Release Notes > PD | TiDB 3.0.0-rc.2 Release Notes > TiKV | TiDB 3.0.0-rc.2 Release Notes > Tools`
- Source Line Ranges: `60-124`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tikv`, `lightning`
- Topic Tags: `release-notes`, `region-metadata`, `scheduling`, `grpc`, `store-limit`, `block-cache`, `pessimistic-locking`, `raftstore`, `hibernate-regions`, `coprocessor`, `rpn-functions`, `binlog-metrics`, `lightning-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0095_b59a90a8b3`
- Source ID: `tidb-docs-8.1:releases/release-3.0.0-rc.2.md#pd`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66b53847a42520f792fcaaf68dae0c8c03c735331a2a035867c94993c0388771`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.0-rc.2#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.0-rc.2.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving PD, TiKV, TiDB Binlog, or TiDB Lightning changes introduced in TiDB 3.0.0-rc.2 release notes.
- Retrieval Keywords: TiDB 3.0.0-rc.2, PD, TiKV, Tools, Region storage by default, Region metadata, ScanRegions, gRPC interface for ScanRegions, store limit mechanism, multiple column families sharing a block cache, pessimistic lock transactions, hibernate Regions, ReadIndex requests for the learner, dirty read issue, snapshot may lose applied data, RPN functions, LogicalOr, IsNull, comparison arithmetic, plus arithmetic, MOD functions, minus arithmetic, TiDB Binlog delay of data replication downstream, TiDB Lightning merging sharded databases and tables, KV write failure retry, table-concurrency 6, tidb.pd-addr, tidb.port
- Follow-up Guidance: The same release-note source also contains a separate TiDB section with SQL optimizer, execution engine, server, and DDL changes.
- Classification Note: This chunk is classified as a shared release-note section because the official content groups release changes for PD, TiKV, and tools rather than a single component.

## Official Source Content

## PD

- Enable the Region storage by default to store the Region metadata [#1524](https://github.com/pingcap/pd/pull/1524)
- Fix the issue that hot Region scheduling is preempted by another scheduler [#1522](https://github.com/pingcap/pd/pull/1522)
- Fix the issue that the priority for the leader does not take effect [#1533](https://github.com/pingcap/pd/pull/1533)
- Add the gRPC interface for `ScanRegions` [#1535](https://github.com/pingcap/pd/pull/1535)
- Push operators actively [#1536](https://github.com/pingcap/pd/pull/1536)
- Add the store limit mechanism for separately controlling the speed of operators for each store [#1474](https://github.com/pingcap/pd/pull/1474)
- Fix the issue of inconsistent `Config` status [#1476](https://github.com/pingcap/pd/pull/1476)
## TiKV

+ Engine
    - Support multiple column families sharing a block cache [#4563](https://github.com/tikv/tikv/pull/4563)

+ Server
    - Remove `TxnScheduler` [#4098](https://github.com/tikv/tikv/pull/4098)
    - Support pessimistic lock transactions [#4698](https://github.com/tikv/tikv/pull/4698)

+ Raftstore
    - Support hibernate Regions to reduce the consumption of the raftstore CPU [#4591](https://github.com/tikv/tikv/pull/4591)
    - Fix the issue that the leader does not reply to the `ReadIndex` requests for the learner [#4653](https://github.com/tikv/tikv/pull/4653)
    - Fix transferring leader failures in some cases [#4684](https://github.com/tikv/tikv/pull/4684)
    - Fix the dirty read issue in some cases [#4688](https://github.com/tikv/tikv/pull/4688)
    - Fix the issue that a snapshot may lose applied data in some cases [#4716](https://github.com/tikv/tikv/pull/4716)

+ Coprocessor
    - Add more RPN functions
        - `LogicalOr` [#4691](https://github.com/tikv/tikv/pull/4601)
        - `LTReal` [#4602](https://github.com/tikv/tikv/pull/4602)
        - `LEReal` [#4602](https://github.com/tikv/tikv/pull/4602)
        - `GTReal` [#4602](https://github.com/tikv/tikv/pull/4602)
        - `GEReal` [#4602](https://github.com/tikv/tikv/pull/4602)
        - `NEReal` [#4602](https://github.com/tikv/tikv/pull/4602)
        - `EQReal` [#4602](https://github.com/tikv/tikv/pull/4602)
        - `IsNull` [#4720](https://github.com/tikv/tikv/pull/4720)
        - `IsTrue` [#4720](https://github.com/tikv/tikv/pull/4720)
        - `IsFalse` [#4720](https://github.com/tikv/tikv/pull/4720)
        - Support comparison arithmetic for `Int` [#4625](https://github.com/tikv/tikv/pull/4625)
        - Support comparison arithmetic for `Decimal` [#4625](https://github.com/tikv/tikv/pull/4625)
        - Support comparison arithmetic for `String` [#4625](https://github.com/tikv/tikv/pull/4625)
        - Support comparison arithmetic for `Time` [#4625](https://github.com/tikv/tikv/pull/4625)
        - Support comparison arithmetic for `Duration` [#4625](https://github.com/tikv/tikv/pull/4625)
        - Support comparison arithmetic for `Json` [#4625](https://github.com/tikv/tikv/pull/4625)
        - Support plus arithmetic for `Int` [#4733](https://github.com/tikv/tikv/pull/4733)
        - Support plus arithmetic for `Real` [#4733](https://github.com/tikv/tikv/pull/4733)
        - Support plus arithmetic for `Decimal` [#4733](https://github.com/tikv/tikv/pull/4733)
        - Support MOD functions for `Int` [#4727](https://github.com/tikv/tikv/pull/4727)
        - Support MOD functions for `Real` [#4727](https://github.com/tikv/tikv/pull/4727)
        - Support MOD functions for `Decimal` [#4727](https://github.com/tikv/tikv/pull/4727)
        - Support minus arithmetic for `Int` [#4746](https://github.com/tikv/tikv/pull/4746)
        - Support minus arithmetic for `Real` [#4746](https://github.com/tikv/tikv/pull/4746)
        - Support minus arithmetic for `Decimal` [#4746](https://github.com/tikv/tikv/pull/4746)
## Tools

+ TiDB Binlog
    - Add a metric to track the delay of data replication downstream [#594](https://github.com/pingcap/tidb-binlog/pull/594)

+ TiDB Lightning

    - Support merging sharded databases and tables [#95](https://github.com/pingcap/tidb-lightning/pull/95)
    - Add the retry mechanism for KV write failure [#176](https://github.com/pingcap/tidb-lightning/pull/176)
    - Update the default value of `table-concurrency` to 6 [#175](https://github.com/pingcap/tidb-lightning/pull/175)
    - Reduce required configuration items by automatically discovering `tidb.pd-addr` and `tidb.port` if they are not provided [#173](https://github.com/pingcap/tidb-lightning/pull/173)
