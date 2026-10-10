# Bug fixes for TiDB 7.5.2

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.2.md`
- Source Title: `TiDB 7.5.2 Release Notes`
- Source Heading Path: `TiDB 7.5.2 Release Notes > Bug fixes`
- Source Line Ranges: `76-117`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `tikv`
- Topic Tags: `bug-fixes`, `ddl`, `dml`, `indexes`, `statistics`, `query-planner`, `panic`, `mpp`, `stale-read`, `dashboard-monitoring`, `foreign-keys`, `auto-increment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0533_f3a91001a3`
- Source ID: `tidb-docs-8.1:releases/release-7.5.2.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `17b1e1f68fe0bea4425293f2cfaf6d106cdbfbec5631def36e47ce7770e471bd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.2.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.5.2 bug fixes for issues involving DDL or DML index inconsistency, TiDB panics, incorrect query results, statistics initialization, stale read behavior, MPP planning, Dashboard Connection Count, foreign key restore DDL, or auto-increment behavior.
- Retrieval Keywords: TiDB 7.5.2 bug fixes, #52914 concurrent DML adding unique index inconsistent data indexes, #52080 multi-schema changes partitioned tables adding indexes inconsistent data indexes, #51162 multi-valued indexes inconsistent data indexes, #47060 DDL operations get stuck due to network problems, #53592 GC error loading statistics at startup, #50758 requests to unready TiKV nodes, #52193 Stale Read miss after TiKV rolling restart, #51921 data race during KV request retries TiDB panics, #47115 panic when parsing index data, #46556 JOIN implicit type conversion panic, #50235 YEAR type compared with out of range unsigned integer incorrect results, #52687 subqueries in UPDATE list panic, #45783 Longlong type overflow in predicates, #42093 SELECT INTO OUTFILE clustered indexes used as predicates, #37986 TopN operator pushed down incorrectly, #49109 empty projection panic, #52947 Index Merge incorrectly pushes partial limit down ordered index plans, #49721 view does not work in recursive CTE, #53236 unstable unique IDs of columns UPDATE statement errors, #46962 SHOW ERRORS predicate always true panic, #51362 final AggMode non-final AggMode coexist in MPP, #50051 wrong TableDual plan empty query results, #52223 lite-init-stats concurrently-init-stats panic initializing statistics, #52813 NO_JOIN hints CREATE BINDING, #52755 subqueries in ALL function incorrect results, #52933 VAR_SAMP window function, #52768 column pruning shallow copies of slices panic, #52312 adding a unique index panic, #51596 server marked as health before initialization complete, #51765 IFNULL function type inconsistent with MySQL, #51372 parallel Apply clustered index incorrect results, #51107 HAVING clause in subquery correlated columns incorrect results, #50810 TIDB_HOT_REGIONS INFORMATION_SCHEMA tables, #52346 automatic statistics collection before initialization finishes, #52600 AutoID Leader change auto-increment decrease AUTO_ID_CACHE=1, #51873 CTE partitioned tables missing statistics incorrect results, #51889 Dashboard Monitoring Connection Count incorrect calculation and display, #51838 DDL operations get stuck restoring a table with the foreign key
- Follow-up Guidance: This release-note section lists the specific GitHub issue identifiers for each TiDB 7.5.2 fix, including fixes related to Dashboard monitoring and TiKV interaction.
- Classification Note: The chunk is classified as a self-managed TiDB release-note bug-fix summary because the official content enumerates resolved issues in TiDB 7.5.2 across TiDB, Dashboard monitoring, and TiKV-related behavior.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue of inconsistent data indexes caused by concurrent DML operations when adding a unique index [#52914](https://github.com/pingcap/tidb/issues/52914) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue of inconsistent data indexes caused by adding indexes with multi-schema changes on partitioned tables [#52080](https://github.com/pingcap/tidb/issues/52080) @[tangenta](https://github.com/tangenta)
    - Fix the issue of inconsistent data indexes caused by adding multi-valued indexes [#51162](https://github.com/pingcap/tidb/issues/51162) @[ywqzzy](https://github.com/ywqzzy)
    - Fix the issue that DDL operations get stuck due to network problems [#47060](https://github.com/pingcap/tidb/issues/47060) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that TiDB might report an error due to GC when loading statistics at startup [#53592](https://github.com/pingcap/tidb/issues/53592) @[you06](https://github.com/you06)
    - Fix the issue that TiDB might send requests to unready TiKV nodes [#50758](https://github.com/pingcap/tidb/issues/50758) @[zyguan](https://github.com/zyguan)
    - Fix the issue that Stale Read might miss after a TiKV rolling restart [#52193](https://github.com/pingcap/tidb/issues/52193) @[zyguan](https://github.com/zyguan)
    - Fix the issue that data race might occur during KV request retries, leading to TiDB panics [#51921](https://github.com/pingcap/tidb/issues/51921) @[zyguan](https://github.com/zyguan)
    - Fix the issue that TiDB might panic when parsing index data [#47115](https://github.com/pingcap/tidb/issues/47115) @[zyguan](https://github.com/zyguan)
    - Fix the issue that TiDB might panic when the JOIN condition contains an implicit type conversion [#46556](https://github.com/pingcap/tidb/issues/46556) @[qw4990](https://github.com/qw4990)
    - Fix the issue that comparing a column of `YEAR` type with an unsigned integer that is out of range causes incorrect results [#50235](https://github.com/pingcap/tidb/issues/50235) @[qw4990](https://github.com/qw4990)
    - Fix the issue that subqueries in an `UPDATE` list might cause TiDB to panic [#52687](https://github.com/pingcap/tidb/issues/52687) @[winoros](https://github.com/winoros)
    - Fix the overflow issue of the `Longlong` type in predicates [#45783](https://github.com/pingcap/tidb/issues/45783) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that `SELECT INTO OUTFILE` does not work when clustered indexes are used as predicates [#42093](https://github.com/pingcap/tidb/issues/42093) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the TopN operator might be pushed down incorrectly [#37986](https://github.com/pingcap/tidb/issues/37986) @[qw4990](https://github.com/qw4990)
    - Fix the issue that an empty projection causes TiDB to panic [#49109](https://github.com/pingcap/tidb/issues/49109) @[winoros](https://github.com/winoros)
    - Fix the issue that Index Merge incorrectly pushes partial limit down when index plans are kept ordered [#52947](https://github.com/pingcap/tidb/issues/52947) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that using a view does not work in recursive CTE [#49721](https://github.com/pingcap/tidb/issues/49721) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that unstable unique IDs of columns might cause the `UPDATE` statement to return errors [#53236](https://github.com/pingcap/tidb/issues/53236) @[winoros](https://github.com/winoros)
    - Fix the issue that TiDB panics when executing the `SHOW ERRORS` statement with a predicate that is always `true` [#46962](https://github.com/pingcap/tidb/issues/46962) @[elsa0520](https://github.com/elsa0520)
    - Fix the issue that the `final` AggMode and the `non-final` AggMode cannot coexist in Massively Parallel Processing (MPP) [#51362](https://github.com/pingcap/tidb/issues/51362) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that a wrong TableDual plan causes empty query results [#50051](https://github.com/pingcap/tidb/issues/50051) @[onlyacat](https://github.com/onlyacat)
    - Fix the issue that TiDB might panic when initializing statistics after enabling both `lite-init-stats` and `concurrently-init-stats` [#52223](https://github.com/pingcap/tidb/issues/52223) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that `NO_JOIN` hints do not work with `CREATE BINDING` [#52813](https://github.com/pingcap/tidb/issues/52813) @[qw4990](https://github.com/qw4990)
    - Fix the issue that subqueries included in the `ALL` function might cause incorrect results [#52755](https://github.com/pingcap/tidb/issues/52755) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that `VAR_SAMP()` cannot be used as a window function [#52933](https://github.com/pingcap/tidb/issues/52933) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that column pruning without using shallow copies of slices might cause TiDB to panic [#52768](https://github.com/pingcap/tidb/issues/52768) @[winoros](https://github.com/winoros)
    - Fix the issue that adding a unique index might cause TiDB to panic [#52312](https://github.com/pingcap/tidb/issues/52312) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the TiDB server is marked as health before the initialization is complete [#51596](https://github.com/pingcap/tidb/issues/51596) @[shenqidebaozi](https://github.com/shenqidebaozi)
    - Fix the issue that the type returned by the `IFNULL` function is inconsistent with MySQL [#51765](https://github.com/pingcap/tidb/issues/51765) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that parallel `Apply` might generate incorrect results when the table has a clustered index [#51372](https://github.com/pingcap/tidb/issues/51372) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that query results might be incorrect when the `HAVING` clause in a subquery contains correlated columns [#51107](https://github.com/pingcap/tidb/issues/51107) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that querying the `TIDB_HOT_REGIONS` table might incorrectly return `INFORMATION_SCHEMA` tables [#50810](https://github.com/pingcap/tidb/issues/50810) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that automatic statistics collection is triggered before the initialization of statistics finishes [#52346](https://github.com/pingcap/tidb/issues/52346) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that AutoID Leader change might cause the value of the auto-increment column to decrease in the case of `AUTO_ID_CACHE=1` [#52600](https://github.com/pingcap/tidb/issues/52600) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that query results might be incorrect when you use Common Table Expressions (CTE) to access partitioned tables with missing statistics [#51873](https://github.com/pingcap/tidb/issues/51873) @[qw4990](https://github.com/qw4990)
    - Fix the incorrect calculation and display of the number of connections (Connection Count) on the TiDB Dashboard Monitoring page [#51889](https://github.com/pingcap/tidb/issues/51889) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that DDL operations get stuck when restoring a table with the foreign key [#51838](https://github.com/pingcap/tidb/issues/51838) @[YangKeao](https://github.com/YangKeao)
