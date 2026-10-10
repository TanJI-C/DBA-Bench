# Improvements across TiDB, PD, BR, TiCDC, and TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.3.md`
- Source Title: `TiDB 7.1.3 Release Notes`
- Source Heading Path: `TiDB 7.1.3 Release Notes > Improvements`
- Source Line Ranges: `23-53`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `br`, `ticdc`, `lightning`, `tikv`
- Topic Tags: `improvements`, `flashback`, `resource-control`, `snapshot-recovery`, `pitr`, `memory-optimization`, `alarm-rules`, `redo-log`, `s3`, `object-storage`, `incremental-scan`, `canal-json`, `getts`, `leader-change`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0465_b223aa1fda`
- Source ID: `tidb-docs-8.1:releases/release-7.1.3.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `deb18aae36cb23e57f910601d9b06c1287838d592f528afcd594f3e2f55424b1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.3#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.3 improvements across TiDB, PD, BR, TiCDC, and TiDB Lightning.
- Retrieval Keywords: TiDB 7.1.3 improvements, FLASHBACK CLUSTER TO TSO, PD resource control client dynamically fetch latest configurations, BR Region scatter retry, snapshot recovery timeout failures, network errors during snapshot restore, Point-In-Time Recovery PITR delete range scenario, TiCDC memory consumption replicate data to TiDB, TiCDC alarm rules, redo log parallel writing data to S3, lz4 compression algorithm, replicating data to object storage by increasing parallelism, incremental scanning upstream TiKV, Canal-JSON, content-compatible=true, sink-uri, official Canal output, TiDB Lightning GetTS failure caused by PD leader change
- Follow-up Guidance: The source lists improvements separately for TiDB, PD, Backup & Restore (BR), TiCDC, and TiDB Lightning within the TiDB 7.1.3 release notes.
- Classification Note: This is classified as a release improvement summary because the content enumerates enhancement items for multiple components under the Improvements section of the TiDB 7.1.3 release notes.

## Official Source Content

## Improvements

+ TiDB

    - Support the [`FLASHBACK CLUSTER TO TSO`](https://docs.pingcap.com/tidb/v7.1/sql-statement-flashback-cluster) syntax [#48372](https://github.com/pingcap/tidb/issues/48372) @[BornChanger](https://github.com/BornChanger)

+ PD

    - Enhance the configuration retrieval method of the resource control client to dynamically fetch the latest configurations [#7043](https://github.com/tikv/pd/issues/7043) @[nolouch](https://github.com/nolouch)

+ Tools

    + Backup & Restore (BR)

        - Enable automatic retry of Region scatter during snapshot recovery when encountering timeout failures or cancellations of Region scatter [#47236](https://github.com/pingcap/tidb/issues/47236) @[Leavrth](https://github.com/Leavrth)
        - During restoring a snapshot backup, BR retries when it encounters certain network errors [#48528](https://github.com/pingcap/tidb/issues/48528) @[Leavrth](https://github.com/Leavrth)
        - Introduce a new integration test for Point-In-Time Recovery (PITR) in the `delete range` scenario, enhancing PITR stability  [#47738](https://github.com/pingcap/tidb/issues/47738) @[Leavrth](https://github.com/Leavrth)

    + TiCDC

        - Optimize the memory consumption when TiCDC nodes replicate data to TiDB [#9935](https://github.com/pingcap/tiflow/issues/9935) @[3AceShowHand](https://github.com/3AceShowHand)
        - Optimize some alarm rules [#9266](https://github.com/pingcap/tiflow/issues/9266) @[asddongmen](https://github.com/asddongmen)
        - Optimize the performance of redo log, including parallel writing data to S3 and adopting lz4 compression algorithm [#10176](https://github.com/pingcap/tiflow/issues/10176) [#10226](https://github.com/pingcap/tiflow/issues/10226) @[sdojjy](https://github.com/sdojjy)
        - Improve the performance of TiCDC replicating data to object storage by increasing parallelism [#10098](https://github.com/pingcap/tiflow/issues/10098) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Reduce the impact of TiCDC incremental scanning on upstream TiKV [#11390](https://github.com/tikv/tikv/issues/11390) @[hicqu](https://github.com/hicqu)
        - Support making TiCDC Canal-JSON content format [compatible with the content format of the official Canal output](https://docs.pingcap.com/tidb/v6.5/ticdc-canal-json#compatibility-with-the-official-canal) by setting `content-compatible=true` in the `sink-uri` configuration [#10106](https://github.com/pingcap/tiflow/issues/10106) @[3AceShowHand](https://github.com/3AceShowHand)

    + TiDB Lightning

        - Add a retry mechanism for `GetTS` failure caused by PD leader change [#45301](https://github.com/pingcap/tidb/issues/45301) @[lance6716](https://github.com/lance6716)
