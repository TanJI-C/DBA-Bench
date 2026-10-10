# New features in performance for TiFlash, TiKV, and TiDB

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.3.0.md`
- Source Title: `TiDB 6.3.0 Release Notes`
- Source Heading Path: `TiDB 6.3.0 Release Notes > New features > Performance`
- Source Line Ranges: `86-123`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiflash`, `tikv`, `tidb`, `sql`, `br`, `lightning`
- Topic Tags: `performance`, `fastscan`, `aggregation`, `log-recycle`, `hash-join`, `cte`, `replication`, `scan-optimization`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0336_483ad0ac3b`
- Source ID: `tidb-docs-8.1:releases/release-6.3.0.md#performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4bba2dd3ab0e8280646afce1633f3d0bfc07a85b2bee144c5448bd9c902a3455`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.3.0#performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.3.0 performance release-note changes for TiFlash, TiKV, or TiDB features such as FastScan, concurrent scan optimization, replication speed, three-stage aggregation, log recycle, null-aware anti join, Hash Join hints, or CTE inline control.
- Retrieval Keywords: TiDB 6.3.0 Performance, TiFlash FastScan, ALTER TABLE ... SET TIFLASH MODE, tiflash_fastscan, multiple concurrency tasks, data scanning performance, TiFlash data replication, BR recover data, TiDB Lightning import data, COUNT(DISTINCT), three-stage aggregation, tidb_opt_three_stage_distinct_agg, TiKV log recycling, enable-log-recycle, Raft Engine, null-aware anti join, NAAJ, IN and = ANY, HASH_JOIN_BUILD(), HASH_JOIN_PROBE(), Hash Join build end, tidb_opt_force_inline_cte, CTE inline, MERGE hint
- Follow-up Guidance: The content notes deprecation of `ALTER TABLE ... SET TIFLASH MODE ...`, states that FastScan settings from v6.2.0 become invalid after upgrade to v6.3.0, and points to the new session control variable `tiflash_fastscan`.
- Classification Note: This is classified as a release chunk because it enumerates new performance features and behavior changes introduced in TiDB 6.3.0 across TiFlash, TiKV, and TiDB.

## Official Source Content

### Performance

* TiFlash changes the way of using FastScan (experimental) [#5252](https://github.com/pingcap/tiflash/issues/5252) @[hongyunyan](https://github.com/hongyunyan)

    In v6.2.0, TiFlash introduces the FastScan feature, which brings expected performance improvements but lacks flexibility in use. Therefore, in v6.3.0, TiFlash changes [the way of using FastScan](https://docs.pingcap.com/tidb/stable/tiflash/use-fastscan): the `ALTER TABLE ... SET TIFLASH MODE ...` syntax to enable or disable FastScan is deprecated. Instead, you can use the system variable [`tiflash_fastscan`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_fastscan-new-in-v630) to easily control whether to enable FastScan.

    When you upgrade from v6.2.0 to v6.3.0, all FastScan settings in v6.2.0 will become invalid, but will not affect the normal reading of data. You need to set the variable `tiflash_fastscan`. When you upgrade from v6.2.0 or an earlier version to v6.3.0, the FastScan feature is not enabled by default for all sessions to keep data consistency.

* TiFlash optimizes data scanning performance in scenarios of multiple concurrency tasks [#5376](https://github.com/pingcap/tiflash/issues/5376) @[JinheLin](https://github.com/JinheLin)

    TiFlash reduces duplicate reads of the same data by combining read operations of the same data. It optimizes the resource overhead and [improves the performance of data scanning in the case of concurrent tasks](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file). For multiple concurrent tasks, it avoids the situation where each task needs to read the same data separately, and avoids the possibility of multiple reads of the same data at the same time.

    This feature is experimental in v6.2.0, and becomes GA in v6.3.0.

* TiFlash improves performance of data replication [#5237](https://github.com/pingcap/tiflash/issues/5237) @[breezewish](https://github.com/breezewish)

    TiFlash uses the Raft protocol for data replication from TiKV. Prior to v6.3.0, it often took a long time to replicate large amounts of replica data. TiDB v6.3.0 optimizes the TiFlash data replication mechanism and significantly improves the replication speed. When you use BR to recover data, use TiDB Lightning to import data, or add new TiFlash replicas, the TiFlash replicas can be replicated more quickly. You can query with TiFlash in a more timely manner. In addition, TiFlash replicas will also reach a secure and balanced state faster when you scale up, scale down, or modify the number of TiFlash replicas.

* TiFlash supports three-stage aggregation of individual `COUNT(DISTINCT)` [#37202](https://github.com/pingcap/tidb/issues/37202) @[fixdb](https://github.com/fixdb)

     TiFlash supports rewriting queries containing only one `COUNT(DISTINCT)` into a [three-stage aggregation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_three_stage_distinct_agg-new-in-v630). This improves concurrency and performance.

* TiKV supports log recycling [#214](https://github.com/tikv/raft-engine/issues/214) @[LykxSassinator](https://github.com/LykxSassinator)

    TiKV supports [recycling log files](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-log-recycle-new-in-v630) in Raft Engine. This reduces the long tail latency in network disks during Raft log appending and improves performance under write workloads.

* TiDB supports null-aware anti join [#37525](https://github.com/pingcap/tidb/issues/37525) @[Arenatlx](https://github.com/Arenatlx)

    TiDB v6.3.0 introduces a new join type [Null-aware anti join (NAAJ)](https://docs.pingcap.com/tidb/stable/explain-subqueries#null-aware-anti-semi-join-not-in-and--all-subqueries). NAAJ can be aware of whether the collection is empty or `NULL` when processing collection operations. This optimizes the execution efficiency of operations such as `IN` and `= ANY` and improves SQL performance.

* Add optimizer hints to control the build end of Hash Join [#35439](https://github.com/pingcap/tidb/issues/35439) @[Reminiscent](https://github.com/Reminiscent)

    In v6.3.0, the TiDB optimizer introduces 2 hints, `HASH_JOIN_BUILD()` and `HASH_JOIN_PROBE()`, to specify the Hash Join, its probe end, and its build end. When the optimizer fails to select the optimal execution plan, you can use these hints to intervene with the plan.

* Support session-level common table expressions (CTE) inline [#36514](https://github.com/pingcap/tidb/issues/36514) @[elsa0520](https://github.com/elsa0520)

    TiDB v6.2.0 introduced the `MERGE` hint in optimizers to allow CTE inline, so that the consumers of a CTE query result can execute it in parallel in TiFlash. In v6.3.0, a session variable [`tidb_opt_force_inline_cte`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_force_inline_cte-new-in-v630) is introduced to allow CTE inline in sessions. This can greatly improve the ease of use.
