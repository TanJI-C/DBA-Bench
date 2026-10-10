# TiDB 7.1.2 bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.2.md`
- Source Title: `TiDB 7.1.2 Release Notes`
- Source Heading Path: `TiDB 7.1.2 Release Notes > Bug fixes`
- Source Line Ranges: `82-118`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `br`, `tiflash`, `tikv`, `shared`
- Topic Tags: `bug-fixes`, `sql-execution`, `ddl`, `partitioning`, `upgrade`, `memory-usage`, `ttl`, `mpp`, `statistics`, `restore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0460_1c7f4ab3ba`
- Source ID: `tidb-docs-8.1:releases/release-7.1.2.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `95efd955e4b9a458ee51166d758bfc9d61b0bb4370d78eb462f1a7a04dbac2c0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.2.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 7.1.2 bug fix coverage for SQL execution, DDL, partitioning, upgrade, memory usage, TTL, MPP, statistics, BR restore, or related errors and incorrect results fixed in this release.
- Retrieval Keywords: TiDB 7.1.2 bug fixes, GROUP_CONCAT ORDER BY column parse, INFORMATION_SCHEMA.TIKV_REGION_STATUS incorrect results, upgrading TiDB gets stuck reading metadata one DDL lease, DML statements with CTE panic, partition exchange detect data does not comply with partition definitions, MERGE_JOIN incorrect results, unsigned types compared with Duration type constants incorrect result, Duplicate entry AUTO_ID_CACHE=1, TTL memory leak, killing a connection go coroutine leaks, Index Join error causes query stuck, BatchPointGet incorrect results hash partitioned tables, EXCHANGE PARTITION fails or is canceled restrictions remain on original table, TIDB_INLJ hint does not take effect joining two sub-queries, DATETIME or TIMESTAMP column compared with number constant inconsistent with MySQL, HashCode repeatedly calculated deeply nested expressions high memory usage OOM, READ_FROM_STORAGE(TIFLASH[...]) hint Can't find a proper physical plan, cast(col)=range FullScan, plan replayer dump explain reports an error, tmp-storage-quota does not take effect, TiDB parser remains in a state causes parsing failure, Aggregation pushed down through Union in MPP incorrect results, TiDB recovers slowly after panic AUTO_ID_CACHE=1, Sort operator crash during spill process, BR restore non-clustered index tables AUTO_ID_CACHE=1 duplicate primary keys, partitioned tables static pruning IndexLookUp query error, partitioned table insert fail after exchanging partitions placement policies, encoding time fields incorrect timezone information, fast add indexes stuck when tmp directory does not exist, upgrading multiple TiDB instances simultaneously blocks upgrade, uneven Region scattering incorrect parameters splitting Regions, DDL operations stuck after TiDB restarted, split table operations non-integer clustered indexes, DDL operations permanently blocked incorrect MDL handling, duplicate rows in information_schema.columns caused by renaming a table, batch-client panic client-go, statistics collection on partitioned tables not killed in time memory usage exceeds memory limits
- Follow-up Guidance: This release note enumerates the fixed issues and affected identifiers for TiDB 7.1.2, including issue numbers such as #41986, #45531, #45176, #46083, #46492, #46580, #45410, #46444, #45510, #46034, #45716, #46779, #45920, #45791, #46160, #38361, #42788, #40146, #45199, #46197, #45161, #45898, #45850, #46454, #47538, #46093, #45757, #46033, #45456, #46228, #46135, #46751, #47350, #46920, #47064, #47691, and #45706.
- Classification Note: The official content is classified as a TiDB 7.1.2 release bug-fix list because it consists of release-note bullets describing fixed issues across TiDB, BR, TiFlash, and related shared components.

## Official Source Content

- Fix the issue that `GROUP_CONCAT` cannot parse the `ORDER BY` column [#41986](https://github.com/pingcap/tidb/issues/41986) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that querying the system table `INFORMATION_SCHEMA.TIKV_REGION_STATUS` returns incorrect results in some cases [#45531](https://github.com/pingcap/tidb/issues/45531) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that upgrading TiDB gets stuck when reading metadata takes longer than one DDL lease [#45176](https://github.com/pingcap/tidb/issues/45176) @[zimulala](https://github.com/zimulala)
    - Fix the issue that executing DML statements with CTE can cause panic [#46083](https://github.com/pingcap/tidb/issues/46083) @[winoros](https://github.com/winoros)
    - Fix the issue of not being able to detect data that does not comply with partition definitions during partition exchange [#46492](https://github.com/pingcap/tidb/issues/46492) @[mjonss](https://github.com/mjonss)
    - Fix the issue that the results of `MERGE_JOIN` are incorrect [#46580](https://github.com/pingcap/tidb/issues/46580) @[qw4990](https://github.com/qw4990)
    - Fix the incorrect result that occurs when comparing unsigned types with `Duration` type constants [#45410](https://github.com/pingcap/tidb/issues/45410) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that `Duplicate entry` might occur when `AUTO_ID_CACHE=1` is set [#46444](https://github.com/pingcap/tidb/issues/46444) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the memory leak issue when TTL is running [#45510](https://github.com/pingcap/tidb/issues/45510) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that killing a connection might cause go coroutine leaks [#46034](https://github.com/pingcap/tidb/issues/46034) @[pingyu](https://github.com/pingyu)
    - Fix the issue that an error in Index Join might cause the query to get stuck [#45716](https://github.com/pingcap/tidb/issues/45716) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the `BatchPointGet` operator returns incorrect results for hash partitioned tables [#46779](https://github.com/pingcap/tidb/issues/46779) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that restrictions on partitioned tables remain on the original table when `EXCHANGE PARTITION` fails or is canceled [#45920](https://github.com/pingcap/tidb/issues/45920) [#45791](https://github.com/pingcap/tidb/issues/45791) @[mjonss](https://github.com/mjonss)
    - Fix the issue that the `TIDB_INLJ` hint does not take effect when joining two sub-queries [#46160](https://github.com/pingcap/tidb/issues/46160) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the behavior is inconsistent with MySQL when comparing a `DATETIME` or `TIMESTAMP` column with a number constant [#38361](https://github.com/pingcap/tidb/issues/38361) @[yibin87](https://github.com/yibin87)
    - Fix the issue that HashCode is repeatedly calculated for deeply nested expressions, which causes high memory usage and OOM [#42788](https://github.com/pingcap/tidb/issues/42788) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that access path pruning logic ignores the `READ_FROM_STORAGE(TIFLASH[...])` hint, which causes the `Can't find a proper physical plan` error [#40146](https://github.com/pingcap/tidb/issues/40146) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that the `cast(col)=range` condition causes FullScan when CAST has no precision loss [#45199](https://github.com/pingcap/tidb/issues/45199) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that `plan replayer dump explain` reports an error [#46197](https://github.com/pingcap/tidb/issues/46197) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that the `tmp-storage-quota` configuration does not take effect [#45161](https://github.com/pingcap/tidb/issues/45161) [#26806](https://github.com/pingcap/tidb/issues/26806) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the TiDB parser remains in a state and causes parsing failure [#45898](https://github.com/pingcap/tidb/issues/45898) @[qw4990](https://github.com/qw4990)
    - Fix the issue that when Aggregation is pushed down through Union in MPP execution plans, the results are incorrect [#45850](https://github.com/pingcap/tidb/issues/45850) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that TiDB recovers slowly after a panic when `AUTO_ID_CACHE=1` is set [#46454](https://github.com/pingcap/tidb/issues/46454) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the Sort operator might cause TiDB to crash during the spill process [#47538](https://github.com/pingcap/tidb/issues/47538) @[windtalker](https://github.com/windtalker)
    - Fix the issue of duplicate primary keys when using BR to restore non-clustered index tables with `AUTO_ID_CACHE=1` [#46093](https://github.com/pingcap/tidb/issues/46093) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the query might report an error when querying partitioned tables in static pruning mode and the execution plan contains `IndexLookUp` [#45757](https://github.com/pingcap/tidb/issues/45757) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that inserting data into a partitioned table might fail after exchanging partitions between the partition table and a table with placement policies  [#45791](https://github.com/pingcap/tidb/issues/45791) @[mjonss](https://github.com/mjonss)
    - Fix the issue of encoding time fields with incorrect timezone information [#46033](https://github.com/pingcap/tidb/issues/46033) @[tangenta](https://github.com/tangenta)
    - Fix the issue that DDL statements that fast add indexes would get stuck when the `tmp` directory does not exist [#45456](https://github.com/pingcap/tidb/issues/45456) @[tangenta](https://github.com/tangenta)
    - Fix the issue that upgrading multiple TiDB instances simultaneously might block the upgrade process [#46228](https://github.com/pingcap/tidb/issues/46228) @[zimulala](https://github.com/zimulala)
    - Fix the issue of uneven Region scattering caused by incorrect parameters used in splitting Regions [#46135](https://github.com/pingcap/tidb/issues/46135) @[zimulala](https://github.com/zimulala)
    - Fix the issue that DDL operations might get stuck after TiDB is restarted [#46751](https://github.com/pingcap/tidb/issues/46751) @[wjhuang2016](https://github.com/wjhuang2016)
    - Prohibit split table operations on non-integer clustered indexes [#47350](https://github.com/pingcap/tidb/issues/47350) @[tangenta](https://github.com/tangenta)
    - Fix the issue that DDL operations might get permanently blocked due to incorrect MDL handling [#46920](https://github.com/pingcap/tidb/issues/46920) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue of duplicate rows in `information_schema.columns` caused by renaming a table [#47064](https://github.com/pingcap/tidb/issues/47064) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the panic issue of `batch-client` in `client-go` [#47691](https://github.com/pingcap/tidb/issues/47691) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that statistics collection on partitioned tables is not killed in time when its memory usage exceeds memory limits [#45706](https://github.com/pingcap/tidb/issues/45706) @[hawkingrei](https://github.com/hawkingrei)
