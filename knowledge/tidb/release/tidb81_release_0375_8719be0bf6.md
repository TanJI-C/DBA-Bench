# TiDB bug fixes in 6.5.1

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.1.md`
- Source Title: `TiDB 6.5.1 Release Notes`
- Source Heading Path: `TiDB 6.5.1 Release Notes > Bug fixes`
- Source Line Ranges: `73-111`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `bug-fixes`, `pessimistic-transactions`, `point-get`, `insert`, `replace`, `auto-analyze`, `ddl`, `indexing`, `region-cache`, `deadlock`, `null-handling`, `system-variables`, `ttl`, `mdl`, `global-bindings`, `partition-tables`, `cursor-read`, `gc`, `show-processlist`, `memory-control`, `kill`, `indexmerge`, `analyze`, `goroutine-leak`, `wrong-results`, `memory-leak`, `timezone`, `data-index-consistency`, `batch-cop`, `cop-concurrency`, `plan-cache`, `statistics`, `predicate-pushdown`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0375_8719be0bf6`
- Source ID: `tidb-docs-8.1:releases/release-6.5.1.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7e9c04e02e2548b196afc2691e1b5f5fd13bf7e418fea974fda0cdb87d2958ec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.1#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.1.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.5.1 bug fixes related to SQL execution, DDL and indexing, plan cache, Region cache, cursor read, GC, memory control, statistics, or wrong-result and panic issues.
- Retrieval Keywords: TiDB 6.5.1 bug fixes, pessimistic-auto-commit point-get, INSERT REPLACE long session connections panic, auto analyze graceful shutdown, DDL ingestion data race, adding index data race, invalid Region cache many Regions, TiDB deadlock during initialization, NULL values constructing key ranges, system variables memory reuse, TTL task ENUM primary key, adding unique index panic, MDL truncating the same table concurrently, global bindings partition tables dynamic trimming mode, cursor read error because of GC, SHOW PROCESSLIST EXECUTE information is null, globalMemoryControl KILL operation might not end, indexMerge panic after error, ANALYZE statement terminated by KILL, goroutine leak in indexMerge, wrong results unsigned TINYINT SMALLINT INT with DECIMAL FLOAT DOUBLE smaller than 0, tidb_enable_reuse_chunk memory leak, time zone data-index inconsistency, batch cop scan detail inaccurate, cop upper concurrency is not limited, statement context in cursor read is mistakenly cached, stale Region cache memory leak and performance degradation, plan cache year cmp const wrong result, large estimation errors large range data modification, conditions cannot be pushed down through Join operators when using Plan Cache, IndexMerge incorrect ranges SET type columns, Plan Cache FullScan int_col cmp decimal, Plan Cache FullScan int_col in decimal, ignore_plan_cache hint INSERT statements, Unsigned Primary Keys in partitioned tables incorrect access intervals
- Follow-up Guidance: The source lists specific fixed issues in TiDB 6.5.1 with issue identifiers such as #39928, #40351, #40038, #40970, #40879, #38436, #40408, and #41626.
- Classification Note: This chunk is classified as a TiDB release bug-fix summary because the official content is a release-notes list of issues fixed in TiDB 6.5.1 across SQL, DDL, plan cache, statistics, GC, and memory-related areas.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that the [`pessimistic-auto-commit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#pessimistic-auto-commit-new-in-v600) configuration item does not take effect for point-get queries [#39928](https://github.com/pingcap/tidb/issues/39928) @[zyguan](https://github.com/zyguan)
    - Fix the issue that the `INSERT` or `REPLACE` statements might panic in long session connections [#40351](https://github.com/pingcap/tidb/issues/40351) @[winoros](https://github.com/winoros)
    - Fix the issue that `auto analyze` causes graceful shutdown to take a long time [#40038](https://github.com/pingcap/tidb/issues/40038) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix the issue that data race might occur during DDL ingestion [#40970](https://github.com/pingcap/tidb/issues/40970) @[tangenta](https://github.com/tangenta)
    - Fix the issue that data race might occur when an index is added [#40879](https://github.com/pingcap/tidb/issues/40879) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the adding index operation is inefficient due to invalid Region cache when there are many Regions in a table [#38436](https://github.com/pingcap/tidb/issues/38436) @[tangenta](https://github.com/tangenta)
    - Fix the issue that TiDB might deadlock during initialization [#40408](https://github.com/pingcap/tidb/issues/40408) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that unexpected data is read because TiDB improperly handles `NULL` values when constructing key ranges [#40158](https://github.com/pingcap/tidb/issues/40158) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the value of system variables might be incorrectly modified in some cases due to memory reuse [#40979](https://github.com/pingcap/tidb/issues/40979) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that a TTL task fails if the primary key of the table contains an `ENUM` column [#40456](https://github.com/pingcap/tidb/issues/40456) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that TiDB panics when adding a unique index [#40592](https://github.com/pingcap/tidb/issues/40592) @[tangenta](https://github.com/tangenta)
    - Fix the issue that some truncate operations cannot be blocked by MDL when truncating the same table concurrently [#40484](https://github.com/pingcap/tidb/issues/40484) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that TiDB cannot restart after global bindings are created for partition tables in dynamic trimming mode [#40368](https://github.com/pingcap/tidb/issues/40368) @[Yisaer](https://github.com/Yisaer)
    - Fix the issue that reading data using the "cursor read" method might return an error because of GC [#39447](https://github.com/pingcap/tidb/issues/39447) @[zyguan](https://github.com/zyguan)
    - Fix the issue that the `EXECUTE` information is null in the result of `SHOW PROCESSLIST` [#41156](https://github.com/pingcap/tidb/issues/41156) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that when `globalMemoryControl` is killing a query, the `KILL` operation might not end [#41057](https://github.com/pingcap/tidb/issues/41057) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that TiDB might panic after `indexMerge` encounters an error [#41047](https://github.com/pingcap/tidb/issues/41047) [#40877](https://github.com/pingcap/tidb/issues/40877) @[guo-shaoge](https://github.com/guo-shaoge) @[windtalker](https://github.com/windtalker)
    - Fix the issue that the `ANALYZE` statement might be terminated by `KILL` [#41825](https://github.com/pingcap/tidb/issues/41825) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that goroutine leak might occur in `indexMerge` [#41545](https://github.com/pingcap/tidb/issues/41545) [#41605](https://github.com/pingcap/tidb/issues/41605) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue of potential wrong results when comparing unsigned `TINYINT`/`SMALLINT`/`INT` values with `DECIMAL`/`FLOAT`/`DOUBLE` values smaller than `0` [#41736](https://github.com/pingcap/tidb/issues/41736) @[LittleFall](https://github.com/LittleFall)
    - Fix the issue that enabling `tidb_enable_reuse_chunk` might lead to memory leak [#40987](https://github.com/pingcap/tidb/issues/40987) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that data race in time zone might cause data-index inconsistency [#40710](https://github.com/pingcap/tidb/issues/40710) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the scan detail information during the execution of `batch cop` might be inaccurate [#41582](https://github.com/pingcap/tidb/issues/41582) @[you06](https://github.com/you06)
    - Fix the issue that the upper concurrency of `cop` is not limited [#41134](https://github.com/pingcap/tidb/issues/41134) @[you06](https://github.com/you06)
    - Fix the issue that the `statement context` in `cursor read` is mistakenly cached [#39998](https://github.com/pingcap/tidb/issues/39998) @[zyguan](https://github.com/zyguan)
    - Periodically clean up stale Region cache to avoid memory leak and performance degradation [#40355](https://github.com/pingcap/tidb/issues/40355) @[sticnarf](https://github.com/sticnarf)
    - Fix the issue that using plan cache on queries that contain `year <cmp> const` might get a wrong result [#41626](https://github.com/pingcap/tidb/issues/41626) @[qw4990](https://github.com/qw4990)
    - Fix the issue of large estimation errors when querying with a large range and a large amount of data modification [#39593](https://github.com/pingcap/tidb/issues/39593) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that some conditions cannot be pushed down through Join operators when using Plan Cache [#40093](https://github.com/pingcap/tidb/issues/40093) [#38205](https://github.com/pingcap/tidb/issues/38205) @[qw4990](https://github.com/qw4990)
    - Fix the issue that IndexMerge plans might generate incorrect ranges on the SET type columns [#41273](https://github.com/pingcap/tidb/issues/41273) [#41293](https://github.com/pingcap/tidb/issues/41293) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that Plan Cache might cache FullScan plans when processing `int_col <cmp> decimal` conditions [#40679](https://github.com/pingcap/tidb/issues/40679) [#41032](https://github.com/pingcap/tidb/issues/41032) @[qw4990](https://github.com/qw4990)
    - Fix the issue that Plan Cache might cache FullScan plans when processing `int_col in (decimal...)` conditions [#40224](https://github.com/pingcap/tidb/issues/40224) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the `ignore_plan_cache` hint might not work for `INSERT` statements [#40079](https://github.com/pingcap/tidb/issues/40079) [#39717](https://github.com/pingcap/tidb/issues/39717) @[qw4990](https://github.com/qw4990)
    - Fix the issue that Auto Analyze might hinder TiDB from exiting [#40038](https://github.com/pingcap/tidb/issues/40038) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix the issue that incorrect access intervals might be constructed on Unsigned Primary Keys in partitioned tables [#40309](https://github.com/pingcap/tidb/issues/40309) @[winoros](https://github.com/winoros)
