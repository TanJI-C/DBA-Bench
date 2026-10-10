# Bug fixes for TiDB in 6.5.6 release notes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.6.md`
- Source Title: `TiDB 6.5.6 Release Notes`
- Source Heading Path: `TiDB 6.5.6 Release Notes > Bug fixes`
- Source Line Ranges: `57-100`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `shared`
- Topic Tags: `bug-fixes`, `ddl`, `optimizer`, `mpp`, `join`, `plan-cache`, `memory-usage`, `panic`, `ingest`, `partitioning`, `cte`, `load-data`, `import-into`, `admin-check`, `tablesample`, `schema-cache`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0405_1e0f7101e1`
- Source ID: `tidb-docs-8.1:releases/release-6.5.6.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `93a67e7769fa4ac6c7f3b83c140ee8ae8153665cb3a885363d1a37a67f392b03`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.6.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.5.6 bug fixes related to DDL blocking, optimizer and join correctness, MPP result issues, plan cache behavior, memory usage or panic problems, ingest and partitioning issues, CTE behavior, LOAD DATA or IMPORT INTO failures, ADMIN CHECK, TABLESAMPLE, or schema cache problems.
- Retrieval Keywords: TiDB 6.5.6 Bug fixes, 6.5.6 release notes TiDB bug fixes, HashJoin chunk cannot be reused when probe, Duplicate entry AUTO_ID_CACHE=1, TIDB_INLJ hint does not take effect joining two sub-queries, DDL operations might get stuck after TiDB is restarted, DDL operations permanently blocked incorrect MDL handling, MERGE_JOIN results are incorrect, Sort operator crash during spill process, cast(col)=range causes FullScan, batch-client panic client-go, split table operations non-integer clustered indexes, prepared plan cache non-prepared plan cache time conversion, empty table create index ingest mode, partition exchange data does not comply with partition definitions, GROUP_CONCAT ORDER BY column parse, HashCode repeatedly calculated deeply nested expressions high memory usage OOM, Aggregation pushed down through Union in MPP incorrect results, INDEX_LOOKUP_HASH_JOIN incorrect memory usage estimation, plan replayer zip file cannot be imported back into TiDB, LIMIT N excessively large N incorrect cost estimation, constructing TopN structure for statistics panic, COUNT(INT) calculated by MPP incorrect, tidb_enable_ordered_result_mode panic, optimizer selects IndexFullScan reduce sort introduced by window functions, predicates pushed down to common table expressions incorrect result, UNION ALL with DUAL table as the first subnode error, column pruning cause panic, CTE aggregate or window functions referenced by other recursive CTEs syntax error, QB_NAME hint in a prepared statement exception, Goroutine leak AUTO_ID_CACHE=1, TiDB might panic when shutting down, MVCC interface reading schema diff commit versions from TiDB schema cache not handling locks, duplicate rows in information_schema.columns caused by renaming a table, LOAD DATA REPLACE INTO bugs, IMPORT INTO task failure caused by PD leader malfunction for 1 minute, ADMIN CHECK failure creating an index on a date type field, TABLESAMPLE unsorted row data, DDL jobID restored to 0 panic
- Follow-up Guidance: The source also points to related TiKV bug fixes in the same TiDB 6.5.6 release notes.
- Classification Note: This chunk is classified as a TiDB release-note bug-fix summary because it is the TiDB subsection under the 6.5.6 Bug fixes heading and enumerates fixed issues across TiDB features and operations.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that the chunk cannot be reused when the HashJoin operator performs probe [#48082](https://github.com/pingcap/tidb/issues/48082) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that `Duplicate entry` might occur when `AUTO_ID_CACHE=1` is set [#46444](https://github.com/pingcap/tidb/issues/46444) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the `TIDB_INLJ` hint does not take effect when joining two sub-queries [#46160](https://github.com/pingcap/tidb/issues/46160) @[qw4990](https://github.com/qw4990)
    - Fix the issue that DDL operations might get stuck after TiDB is restarted [#46751](https://github.com/pingcap/tidb/issues/46751) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that DDL operations might get permanently blocked due to incorrect MDL handling [#46920](https://github.com/pingcap/tidb/issues/46920) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the results of `MERGE_JOIN` are incorrect [#46580](https://github.com/pingcap/tidb/issues/46580) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the Sort operator might cause TiDB to crash during the spill process [#47538](https://github.com/pingcap/tidb/issues/47538) @[windtalker](https://github.com/windtalker)
    - Fix the issue that the `cast(col)=range` condition causes FullScan when CAST has no precision loss [#45199](https://github.com/pingcap/tidb/issues/45199) @[AilinKid](https://github.com/AilinKid)
    - Fix the panic issue of `batch-client` in `client-go` [#47691](https://github.com/pingcap/tidb/issues/47691) @[crazycs520](https://github.com/crazycs520)
    - Prohibit split table operations on non-integer clustered indexes [#47350](https://github.com/pingcap/tidb/issues/47350) @[tangenta](https://github.com/tangenta)
    - Fix the incompatibility issue between the behavior of prepared plan cache and non-prepared plan cache during time conversion [#42439](https://github.com/pingcap/tidb/issues/42439) @[qw4990](https://github.com/qw4990)
    - Fix the issue that sometimes an index cannot be created for an empty table using ingest mode [#39641](https://github.com/pingcap/tidb/issues/39641) @[tangenta](https://github.com/tangenta)
    - Fix the issue of not being able to detect data that does not comply with partition definitions during partition exchange [#46492](https://github.com/pingcap/tidb/issues/46492) @[mjonss](https://github.com/mjonss)
    - Fix the issue that `GROUP_CONCAT` cannot parse the `ORDER BY` column [#41986](https://github.com/pingcap/tidb/issues/41986) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that HashCode is repeatedly calculated for deeply nested expressions, which causes high memory usage and OOM [#42788](https://github.com/pingcap/tidb/issues/42788) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that when Aggregation is pushed down through Union in MPP execution plans, the results are incorrect [#45850](https://github.com/pingcap/tidb/issues/45850) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue of incorrect memory usage estimation in `INDEX_LOOKUP_HASH_JOIN` [#47788](https://github.com/pingcap/tidb/issues/47788) @[SeaRise](https://github.com/SeaRise)
    - Fix the issue that the zip file generated by `plan replayer` cannot be imported back into TiDB [#46474](https://github.com/pingcap/tidb/issues/46474) @[YangKeao](https://github.com/YangKeao)
    - Fix the incorrect cost estimation caused by an excessively large `N` in `LIMIT N` [#43285](https://github.com/pingcap/tidb/issues/43285) @[qw4990](https://github.com/qw4990)
    - Fix the panic issue that might occur when constructing TopN structure for statistics [#35948](https://github.com/pingcap/tidb/issues/35948) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that the result of `COUNT(INT)` calculated by MPP might be incorrect [#48643](https://github.com/pingcap/tidb/issues/48643) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that panic might occur when `tidb_enable_ordered_result_mode` is enabled [#45044](https://github.com/pingcap/tidb/issues/45044) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the optimizer mistakenly selects IndexFullScan to reduce sort introduced by window functions [#46177](https://github.com/pingcap/tidb/issues/46177) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the result might be incorrect when predicates are pushed down to common table expressions [#47881](https://github.com/pingcap/tidb/issues/47881) @[winoros](https://github.com/winoros)
    - Fix the issue that executing `UNION ALL` with the DUAL table as the first subnode might cause an error [#48755](https://github.com/pingcap/tidb/issues/48755) @[winoros](https://github.com/winoros)
    - Fix the issue that column pruning can cause panic in specific situations [#47331](https://github.com/pingcap/tidb/issues/47331) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue of possible syntax error when a common table expression (CTE) containing aggregate or window functions is referenced by other recursive CTEs [#47603](https://github.com/pingcap/tidb/issues/47603) [#47711](https://github.com/pingcap/tidb/issues/47711)  @[elsa0520](https://github.com/elsa0520)
    - Fix the issue that an exception might occur when using the `QB_NAME` hint in a prepared statement [#46817](https://github.com/pingcap/tidb/issues/46817) @[jackysp](https://github.com/jackysp)
    - Fix the issue of Goroutine leak when using `AUTO_ID_CACHE=1` [#46324](https://github.com/pingcap/tidb/issues/46324) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that TiDB might panic when shutting down [#32110](https://github.com/pingcap/tidb/issues/32110) @[july2993](https://github.com/july2993)
    - Fix the issue of not handling locks in the MVCC interface when reading schema diff commit versions from the TiDB schema cache [#48281](https://github.com/pingcap/tidb/issues/48281) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the issue of duplicate rows in `information_schema.columns` caused by renaming a table [#47064](https://github.com/pingcap/tidb/issues/47064) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the bugs in the `LOAD DATA REPLACE INTO` statement [#47995](https://github.com/pingcap/tidb/issues/47995)) @[lance6716](https://github.com/lance6716)
    - Fix the issue of `IMPORT INTO` task failure caused by PD leader malfunction for 1 minute [#48307](https://github.com/pingcap/tidb/issues/48307) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the issue of `ADMIN CHECK` failure caused by creating an index on a date type field [#47426](https://github.com/pingcap/tidb/issues/47426) @[tangenta](https://github.com/tangenta)
    - Fix the issue of unsorted row data returned by `TABLESAMPLE` [#48253](https://github.com/pingcap/tidb/issues/48253) @[tangenta](https://github.com/tangenta)
    - Fix the TiDB node panic issue that occurs when DDL `jobID` is restored to 0 [#46296](https://github.com/pingcap/tidb/issues/46296) @[jiyfhust](https://github.com/jiyfhust)

+ TiKV
