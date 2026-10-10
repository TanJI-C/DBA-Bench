# Improvements across TiDB, TiKV, PD, BR, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.6.md`
- Source Title: `TiDB 6.5.6 Release Notes`
- Source Heading Path: `TiDB 6.5.6 Release Notes > Improvements`
- Source Line Ranges: `26-56`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `br`, `ticdc`
- Topic Tags: `release-notes`, `improvements`, `flashback`, `memory-usage`, `oom`, `metrics`, `grafana`, `disaster-recovery`, `backup`, `restore`, `pitr`, `region-scatter`, `region-merge`, `canal-json`, `ddl`, `add-index`, `incremental-scan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0404_1eaae187f0`
- Source ID: `tidb-docs-8.1:releases/release-6.5.6.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1c49161a11a3eefcc3f4d9666c624d0eadef190d63a1bb21676ad5366b900040`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.6#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.6.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.5.6 improvements across TiDB, TiKV, PD, BR, and TiCDC, including new syntax, memory and monitoring changes, retry behavior, and replication optimizations.
- Retrieval Keywords: TiDB 6.5.6 Improvements, FLASHBACK CLUSTER TO TSO, TiKV Resolver memory usage prevent OOM, LRUCache in Router objects, apply_router alive leak metrics, raft_router alive leak metrics, PD DR Auto-Sync Grafana Status Sync Progress, BR snapshot restore retries network errors, PITR delete range scenario, Region scatter automatic retry, merge-schedule-limit 0, TiCDC Canal-JSON content-compatible=true, official Canal output compatibility, ADD INDEX DDL avoid blocking subsequent DML, incremental scanning upstream TiKV
- Follow-up Guidance: The chunk groups improvements by component, including TiDB, TiKV, PD, BR, and TiCDC.
- Classification Note: This is an improvements section because it enumerates enhancement items added or optimized in TiDB 6.5.6 across multiple components.

## Official Source Content

## Improvements

+ TiDB

    - Support the [`FLASHBACK CLUSTER TO TSO`](https://docs.pingcap.com/tidb/v6.5/sql-statement-flashback-cluster) syntax [#48372](https://github.com/pingcap/tidb/issues/48372) @[BornChanger](https://github.com/BornChanger)

+ TiKV

    - Optimize memory usage of Resolver to prevent OOM [#15458](https://github.com/tikv/tikv/issues/15458) @[overvenus](https://github.com/overvenus)
    - Eliminate LRUCache in Router objects to reduce memory usage and prevent OOM [#15430](https://github.com/tikv/tikv/issues/15430) @[Connor1996](https://github.com/Connor1996)
    - Add the `alive` and `leak` monitoring dimensions for the `apply_router` and `raft_router` metrics [#15357](https://github.com/tikv/tikv/issues/15357) @[tonyxuqqi](https://github.com/tonyxuqqi)

+ PD

    - Add monitoring metrics such as `Status` and `Sync Progress` for `DR Auto-Sync` on the Grafana dashboard [#6975](https://github.com/tikv/pd/issues/6975) @[disksing](https://github.com/disksing)

+ Tools

    + Backup & Restore (BR)

        - During restoring a snapshot backup, BR retries when it encounters certain network errors [#48528](https://github.com/pingcap/tidb/issues/48528) @[Leavrth](https://github.com/Leavrth)
        - Introduce a new integration test for Point-In-Time Recovery (PITR) in the `delete range` scenario, enhancing PITR stability  [#47738](https://github.com/pingcap/tidb/issues/47738) @[Leavrth](https://github.com/Leavrth)
        - Enable automatic retry of Region scatter during snapshot recovery when encountering timeout failures or cancellations of Region scatter [#47236](https://github.com/pingcap/tidb/issues/47236) @[Leavrth](https://github.com/Leavrth)
        - BR can pause Region merging by setting the `merge-schedule-limit` configuration to `0` [#7148](https://github.com/tikv/pd/issues/7148) @[BornChanger](https://github.com/3pointer)

    + TiCDC

        - Support making TiCDC Canal-JSON content format [compatible with the content format of the official Canal output](https://docs.pingcap.com/tidb/v6.5/ticdc-canal-json#compatibility-with-the-official-canal) by setting `content-compatible=true` in the `sink-uri` configuration [#10106](https://github.com/pingcap/tiflow/issues/10106) @[3AceShowHand](https://github.com/3AceShowHand)
        - Optimize the execution logic of replicating the `ADD INDEX` DDL operations to avoid blocking subsequent DML statements [#9644](https://github.com/pingcap/tiflow/issues/9644) @[sdojjy](https://github.com/sdojjy)
        - Reduce the impact of TiCDC incremental scanning on upstream TiKV [#11390](https://github.com/tikv/tikv/issues/11390) @[hicqu](https://github.com/hicqu)
