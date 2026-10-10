# Bug fixes for TiFlash, TiCDC, and TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.6.md`
- Source Title: `TiDB 6.1.6 Release Notes`
- Source Heading Path: `TiDB 6.1.6 Release Notes > Bug fixes`
- Source Line Ranges: `74-98`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiflash`, `ticdc`, `lightning`, `pd`, `tidb`
- Topic Tags: `bug-fixes`, `memory-usage`, `log-search`, `collation`, `decimal`, `generated-columns`, `data-replication`, `network-isolation`, `data-consistency`, `error-messages`, `redo-log`, `changefeed`, `checksum`, `split-region`, `auto-random`, `duplicate-resolution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0319_19a6dea7ff`
- Source ID: `tidb-docs-8.1:releases/release-6.1.6.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fff6327b5a73281582756e829253c211e283103faf2c80eb1228734ef5afe8e8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.1.6 bug fixes affecting TiFlash, TiCDC, or TiDB Lightning around memory usage, log search, collation, Decimal behavior, generated columns, replication errors, PD network isolation, redo log, changefeed status, checksum consistency, split-region panics, auto_random imports, or duplicate-resolution.
- Retrieval Keywords: TiDB 6.1.6 bug fixes, TiFlash semi-joins excessive memory Cartesian products, TiFlash log search too slow, TopN Sort incorrect results new collation, Decimal cast rounds up incorrectly, TiFlash cannot recognize generated columns, Decimal division does not round up the last digit, TiCDC UPDATE INSERT disorder Duplicate entry, network isolation between PD and TiCDC abnormal exit, CHARACTER SET non-null unique index without a primary key data inconsistency, db sorter cgroup memory limit, cdc cli invalid input error message, redo log S3 storage failure, pausing a changefeed when PD is abnormal incorrect status, TiDB Lightning duplicate-resolution inconsistent checksums, TiDB Lightning panics in the split-region phase, Local Backend auto_random compound primary key, parallel import local duplicate record skip conflict resolution
- Follow-up Guidance: 
- Classification Note: This is a self-managed release-notes bug-fix chunk that summarizes fixes across shared components including TiFlash, TiCDC, TiDB Lightning, PD, and TiDB in TiDB 6.1.6.

## Official Source Content

- Fix the issue that semi-joins use excessive memory when calculating Cartesian products [#6730](https://github.com/pingcap/tiflash/issues/6730) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that TiFlash log search is too slow [#6829](https://github.com/pingcap/tiflash/issues/6829) @[hehechen](https://github.com/hehechen)
    - Fix the issue that TopN/Sort operators produce incorrect results after enabling the new collation [#6807](https://github.com/pingcap/tiflash/issues/6807) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that Decimal cast rounds up incorrectly in certain cases [#6994](https://github.com/pingcap/tiflash/issues/6994) @[windtalker](https://github.com/windtalker)
    - Fix the issue that TiFlash cannot recognize generated columns [#6801](https://github.com/pingcap/tiflash/issues/6801) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that Decimal division does not round up the last digit in certain cases [#7022](https://github.com/pingcap/tiflash/issues/7022) @[LittleFall](https://github.com/LittleFall)

+ Tools

    + TiCDC

        - Fix the issue that the disorder of `UPDATE` and `INSERT` statements during data replication might cause the `Duplicate entry` error [#8597](https://github.com/pingcap/tiflow/issues/8597) @[sdojjy](https://github.com/sdojjy)
        - Fix the abnormal exit issue of the TiCDC service caused by network isolation between PD and TiCDC [#8562](https://github.com/pingcap/tiflow/issues/8562) @[overvenus](https://github.com/overvenus)
        - Fix the data inconsistency that occurs when replicating data to a TiDB or MySQL sink and when `CHARACTER SET` is specified on the column that has the non-null unique index without a primary key [#8420](https://github.com/pingcap/tiflow/issues/8420) @[zhaoxinyu](https://github.com/zhaoxinyu)
        - Fix the issue that the memory usage of `db sorter` is not controlled by `cgroup memory limit` [#8588](https://github.com/pingcap/tiflow/issues/8588) @[amyangfei](https://github.com/amyangfei)
        - Optimize the error message of `cdc cli` for invalid input [#7903](https://github.com/pingcap/tiflow/issues/7903) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue of insufficient duration that redo log can tolerate for S3 storage failure [#8089](https://github.com/pingcap/tiflow/issues/8089) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that pausing a changefeed when PD is abnormal results in incorrect status [#8330](https://github.com/pingcap/tiflow/issues/8330) @[sdojjy](https://github.com/sdojjy)

    + TiDB Lightning

        - Fix the issue that the conflict resolution logic (`duplicate-resolution`) might lead to inconsistent checksums [#40657](https://github.com/pingcap/tidb/issues/40657) @[sleepymole](https://github.com/sleepymole)
        - Fix the issue that TiDB Lightning panics in the split-region phase [#40934](https://github.com/pingcap/tidb/issues/40934) @[lance6716](https://github.com/lance6716)
        - Fix the issue that when importing data in Local Backend mode, the target columns do not automatically generate data if the compound primary key of the imported target table has an `auto_random` column and no value for the column is specified in the source data [#41454](https://github.com/pingcap/tidb/issues/41454) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that TiDB Lightning might incorrectly skip conflict resolution when all but the last TiDB Lightning instance encounters a local duplicate record during a parallel import [#40923](https://github.com/pingcap/tidb/issues/40923) @[lichunzhu](https://github.com/lichunzhu)
