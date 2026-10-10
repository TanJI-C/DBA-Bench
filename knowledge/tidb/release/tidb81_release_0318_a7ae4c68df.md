# Bug fixes across TiDB, TiKV, and PD

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.6.md`
- Source Title: `TiDB 6.1.6 Release Notes`
- Source Heading Path: `TiDB 6.1.6 Release Notes > Bug fixes`
- Source Line Ranges: `31-73`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`
- Topic Tags: `release-notes`, `bug-fixes`, `plan-cache`, `indexmerge`, `wrong-results`, `panic`, `memory`, `ddl`, `partition`, `region-cache`, `unsafe-recovery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0318_a7ae4c68df`
- Source ID: `tidb-docs-8.1:releases/release-6.1.6.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3daa4e314d29f28aa5d169b9cf5ffc316fa2e6b9f2c94141eeef3edf4a15e479`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.1.6 bug-fix entries involving plan cache, indexMerge, wrong results, panic, memory, partition behavior, region cache, TiKV fixes, or PD recovery and scatter issues.
- Retrieval Keywords: TiDB 6.1.6 bug fixes, ignore_plan_cache, INSERT statements, indexMerge, TopN virtual columns, TiKV or TiFlash, Prepare or Execute, virtual tables, Plan Cache, FullScan plans, int_col in (decimal...), SET type columns, wrong results, CLUSTER_SLOW_QUERY, Grafana dashboard, multiple MAXVALUE partitions, Shuffle operators, data-index inconsistency, Cursor Fetch, Fetch and Close, floating-point type DDL, information_schema.columns, inconsistent InfoSchema, generated columns, different partitioned tables, full index scans, prepared plan cache, PointGet, PointUpdate, region cache, INSERT IGNORE, REPLACE, const Enum, CPU quota limitation, incorrect snapshot last index, Region Scatter, uneven distribution of leader, Online Unsafe Recovery timeout
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release note bug-fix section because it lists specific fixes in TiDB, TiKV, and PD for errors, incorrect results, panics, memory issues, and recovery behavior.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that the `ignore_plan_cache` hint might not work for `INSERT` statements [#40079](https://github.com/pingcap/tidb/issues/40079) [#39717](https://github.com/pingcap/tidb/issues/39717) @[qw4990](https://github.com/qw4990)
    - Fix the issue that TiDB might panic after `indexMerge` encounters an error [#41047](https://github.com/pingcap/tidb/issues/41047) [#40877](https://github.com/pingcap/tidb/issues/40877) @[guo-shaoge](https://github.com/guo-shaoge) @[windtalker](https://github.com/windtalker)
    - Fix the issue that incorrect results might be returned when TopN operators with virtual columns are mistakenly pushing down to TiKV or TiFlash [#41355](https://github.com/pingcap/tidb/issues/41355) @[Dousir9](https://github.com/Dousir9)
    - Fix the PD OOM issue when there is a large number of Regions but the table ID cannot be pushed down when querying some virtual tables using `Prepare` or `Execute` [#39605](https://github.com/pingcap/tidb/issues/39605) @[djshow832](https://github.com/djshow832)
    - Fix the issue that Plan Cache might cache FullScan plans when processing `int_col in (decimal...)` conditions [#40224](https://github.com/pingcap/tidb/issues/40224) @[qw4990](https://github.com/qw4990)
    - Fix the issue that IndexMerge plans might generate incorrect ranges on the SET type columns [#41273](https://github.com/pingcap/tidb/issues/41273) [#41293](https://github.com/pingcap/tidb/issues/41293) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue of potential wrong results when comparing unsigned `TINYINT`/`SMALLINT`/`INT` values with `DECIMAL`/`FLOAT`/`DOUBLE` values smaller than `0` [#41736](https://github.com/pingcap/tidb/issues/41736) @[LittleFall](https://github.com/LittleFall)
    - Fix the issue that the TiDB server might run out of memory when the `INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY` table is queried. This issue can be triggered when you check slow queries on the Grafana dashboard [#33893](https://github.com/pingcap/tidb/issues/33893) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that range partitions allow multiple `MAXVALUE` partitions [#36329](https://github.com/pingcap/tidb/issues/36329) @[u5surf](https://github.com/u5surf)
    - Fix the issue that Plan Cache might cache Shuffle operators and return incorrect results [#38335](https://github.com/pingcap/tidb/issues/38335) @[qw4990](https://github.com/qw4990)
    - Fix the issue that data race in time zone might cause data-index inconsistency [#40710](https://github.com/pingcap/tidb/issues/40710) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that goroutine leak might occur in `indexMerge` [#41545](https://github.com/pingcap/tidb/issues/41545) [#41605](https://github.com/pingcap/tidb/issues/41605) @[guo-shaoge](https://github.com/guo-shaoge) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that, when using Cursor Fetch and running other statements among Execute, Fetch, and Close, the Fetch and Close commands might return incorrect results or cause TiDB to panic [#40094](https://github.com/pingcap/tidb/issues/40094) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that when modifying the floating-point type using DDL to keep the length unchanged and reduce the decimal places, the old data still remains the same [#41281](https://github.com/pingcap/tidb/issues/41281) @[zimulala](https://github.com/zimulala)
    - Fix the issue that joining the `information_schema.columns` table causes TiDB to panic [#32459](https://github.com/pingcap/tidb/issues/32459) @[tangenta](https://github.com/tangenta)
    - Fix the issue that TiDB panic occurs due to inconsistent InfoSchema being obtained when generating the execution plan [#41622](https://github.com/pingcap/tidb/issues/41622) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that TiFlash reports an error for generated columns during execution [#40663](https://github.com/pingcap/tidb/issues/40663) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that TiDB might produce incorrect results when different partitioned tables appear in a single SQL statement [#42135](https://github.com/pingcap/tidb/issues/42135) @[mjonss](https://github.com/mjonss)
    - Fix the issue that Plan Cache might cache Shuffle operators and return incorrect results [#38335](https://github.com/pingcap/tidb/issues/38335) @[qw4990](https://github.com/qw4990) @[fzzf678](https://github.com/fzzf678)
    - Fix the issue that using Index Merge to read a table containing the `SET` type column might lead to incorrect results [#41293](https://github.com/pingcap/tidb/issues/41293) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that full index scans might cause errors when prepared plan cache is enabled [#42150](https://github.com/pingcap/tidb/issues/42150) @[fzzf678](https://github.com/fzzf678)
    - Fix the issue that SQL statements using `PointGet` to read a table during the execution of a DDL statement might throw a panic [#41622](https://github.com/pingcap/tidb/issues/41622) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that after executing `PointUpdate` within a transaction, TiDB returns incorrect results for the `SELECT` statement [#28011](https://github.com/pingcap/tidb/issues/28011) @[zyguan](https://github.com/zyguan)
    - Clear expired region cache regularly to avoid memory leak and performance degradation [#40461](https://github.com/pingcap/tidb/issues/40461) @[sticnarf](https://github.com/sticnarf) @[zyguan](https://github.com/zyguan)
    - Fix the issue that `INSERT IGNORE` and `REPLACE` statements do not lock keys that do not modify values [#42121](https://github.com/pingcap/tidb/issues/42121) @[zyguan](https://github.com/zyguan)

+ TiKV

    - Fix an error that occurs when casting the `const Enum` type to other types [#14156](https://github.com/tikv/tikv/issues/14156) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue of CPU quota limitation [#13084](https://github.com/tikv/tikv/issues/13084) @[BornChanger](https://github.com/BornChanger)
    - Fix the issue of incorrect snapshot last index [#12618](https://github.com/tikv/tikv/issues/12618) @[LintianShi](https://github.com/LintianShi)

+ PD

    - Fix the issue that the Region Scatter might cause uneven distribution of leader [#6017](https://github.com/tikv/pd/issues/6017) @[HunDunDM](https://github.com/HunDunDM)
    - Fix the issue that the timeout mechanism of Online Unsafe Recovery does not work [#6107](https://github.com/tikv/pd/issues/6107) @[v01dstar](https://github.com/v01dstar)

+ TiFlash
