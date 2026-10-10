# Bug fixes for TiDB in 7.4.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.4.0.md`
- Source Title: `TiDB 7.4.0 Release Notes`
- Source Heading Path: `TiDB 7.4.0 Release Notes > Bug fixes`
- Source Line Ranges: `391-428`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `tikv`, `sql`, `shared`
- Topic Tags: `bug-fixes`, `sql-execution`, `partitioning`, `planner`, `plan-cache`, `mpp`, `cte`, `parser`, `auto-id-cache`, `configuration`, `collation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0515_2ccdd6aa66`
- Source ID: `tidb-docs-8.1:releases/release-7.4.0.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a09f141784aaeedd3737540dcbd36483085f2f8c441ec7a97cff7a6a64d9bf39`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.4.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.4.0 bug fixes related to incorrect SQL results, parser or CTE panic, partition exchange behavior, plan cache, MPP, TiFlash hints, AUTO_ID_CACHE=1, or specific errors such as `Duplicate entry` and `Can't find a proper physical plan`.
- Retrieval Keywords: TiDB 7.4.0 bug fixes, BatchPointGet incorrect results, hash partitioned tables, non hash partitioned tables, EXCHANGE PARTITION does not check constraints, EXCHANGE PARTITION fails or is canceled, partition exchange, tidb_enforce_mpp, LIKE clause `_`, schemaTs is set to 0, AUTO_ID_CACHE=1, Duplicate entry, next_row_id, SHOW CREATE TABLE, CTE in subqueries, executing DML statements with CTE can cause panic, List partitions, NULL and empty strings, tmp-storage-quota, WEIGHT_STRING(), Index Join query stuck, DATETIME column with a number constant, TIMESTAMP column with a number constant, unsigned types with Duration type constants, READ_FROM_STORAGE(TIFLASH[...]), Can't find a proper physical plan, GROUP_CONCAT parse the ORDER BY column, HashCode repeatedly calculated, high memory usage and OOM, cast(col)=range causes FullScan, Aggregation pushed down through Union in MPP, bindings with `in (?)` cannot match `in (?, ... ?)`, non-prep plan cache, connection collation, plan cache, no warning is reported when an executed plan does not hit the plan cache, plan replayer dump explain, TIDB_INLJ hint, MERGE_JOIN incorrect results
- Follow-up Guidance: 
- Classification Note: This chunk is a release-notes bug-fix summary for the TiDB component in 7.4.0, covering SQL execution, partitioning, planner, plan cache, parser, configuration, and collation related fixes.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that the `BatchPointGet` operator returns incorrect results for tables that are not hash partitioned [#45889](https://github.com/pingcap/tidb/issues/45889) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the `BatchPointGet` operator returns incorrect results for hash partitioned tables [#46779](https://github.com/pingcap/tidb/issues/46779) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that the TiDB parser remains in a state and causes parsing failure [#45898](https://github.com/pingcap/tidb/issues/45898) @[qw4990](https://github.com/qw4990)
    - Fix the issue that `EXCHANGE PARTITION` does not check constraints [#45922](https://github.com/pingcap/tidb/issues/45922) @[mjonss](https://github.com/mjonss)
    - Fix the issue that the `tidb_enforce_mpp` system variable cannot be correctly restored [#46214](https://github.com/pingcap/tidb/issues/46214) @[djshow832](https://github.com/djshow832)
    - Fix the issue that the `_` in the `LIKE` clause is incorrectly handled [#46287](https://github.com/pingcap/tidb/issues/46287) [#46618](https://github.com/pingcap/tidb/issues/46618) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the `schemaTs` is set to 0 when TiDB fails to obtain the schema [#46325](https://github.com/pingcap/tidb/issues/46325) @[hihihuhu](https://github.com/hihihuhu)
    - Fix the issue that `Duplicate entry` might occur when `AUTO_ID_CACHE=1` is set [#46444](https://github.com/pingcap/tidb/issues/46444) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that TiDB recovers slowly after a panic when `AUTO_ID_CACHE=1` is set [#46454](https://github.com/pingcap/tidb/issues/46454) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the `next_row_id` in `SHOW CREATE TABLE` is incorrect when `AUTO_ID_CACHE=1` is set [#46545](https://github.com/pingcap/tidb/issues/46545) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the panic issue that occurs during parsing when using CTE in subqueries [#45838](https://github.com/pingcap/tidb/issues/45838) @[djshow832](https://github.com/djshow832)
    - Fix the issue that restrictions on partitioned tables remain on the original table when `EXCHANGE PARTITION` fails or is canceled [#45920](https://github.com/pingcap/tidb/issues/45920) [#45791](https://github.com/pingcap/tidb/issues/45791) @[mjonss](https://github.com/mjonss)
    - Fix the issue that the definition of List partitions does not support using both `NULL` and empty strings [#45694](https://github.com/pingcap/tidb/issues/45694) @[mjonss](https://github.com/mjonss)
    - Fix the issue of not being able to detect data that does not comply with partition definitions during partition exchange [#46492](https://github.com/pingcap/tidb/issues/46492) @[mjonss](https://github.com/mjonss)
    - Fix the issue that the `tmp-storage-quota` configuration does not take effect [#45161](https://github.com/pingcap/tidb/issues/45161) [#26806](https://github.com/pingcap/tidb/issues/26806) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the `WEIGHT_STRING()` function does not match the collation [#45725](https://github.com/pingcap/tidb/issues/45725) @[dveeden](https://github.com/dveeden)
    - Fix the issue that an error in Index Join might cause the query to get stuck [#45716](https://github.com/pingcap/tidb/issues/45716) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the behavior is inconsistent with MySQL when comparing a `DATETIME` or `TIMESTAMP` column with a number constant [#38361](https://github.com/pingcap/tidb/issues/38361) @[yibin87](https://github.com/yibin87)
    - Fix the incorrect result that occurs when comparing unsigned types with `Duration` type constants [#45410](https://github.com/pingcap/tidb/issues/45410) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that access path pruning logic ignores the `READ_FROM_STORAGE(TIFLASH[...])` hint, which causes the `Can't find a proper physical plan` error [#40146](https://github.com/pingcap/tidb/issues/40146) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that `GROUP_CONCAT` cannot parse the `ORDER BY` column [#41986](https://github.com/pingcap/tidb/issues/41986) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that HashCode is repeatedly calculated for deeply nested expressions, which causes high memory usage and OOM [#42788](https://github.com/pingcap/tidb/issues/42788) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that the `cast(col)=range` condition causes FullScan when CAST has no precision loss [#45199](https://github.com/pingcap/tidb/issues/45199) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that when Aggregation is pushed down through Union in MPP execution plans, the results are incorrect [#45850](https://github.com/pingcap/tidb/issues/45850) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that bindings with `in (?)` cannot match `in (?, ... ?)` [#44298](https://github.com/pingcap/tidb/issues/44298) @[qw4990](https://github.com/qw4990)
    - Fix the error caused by not considering the connection collation when `non-prep plan cache` reuses the execution plan [#47008](https://github.com/pingcap/tidb/issues/47008) @[qw4990](https://github.com/qw4990)
    - Fix the issue that no warning is reported when an executed plan does not hit the plan cache [#46159](https://github.com/pingcap/tidb/issues/46159) @[qw4990](https://github.com/qw4990)
    - Fix the issue that `plan replayer dump explain` reports an error [#46197](https://github.com/pingcap/tidb/issues/46197) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that executing DML statements with CTE can cause panic [#46083](https://github.com/pingcap/tidb/issues/46083) @[winoros](https://github.com/winoros)
    - Fix the issue that the `TIDB_INLJ` hint does not take effect when joining two sub-queries [#46160](https://github.com/pingcap/tidb/issues/46160) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the results of `MERGE_JOIN` are incorrect [#46580](https://github.com/pingcap/tidb/issues/46580) @[qw4990](https://github.com/qw4990)

+ TiKV
