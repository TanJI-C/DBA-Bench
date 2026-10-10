# TiDB 8.1.1 bug fixes for SQL execution, optimizer, statistics, DDL, and observability

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.1.md`
- Source Title: `TiDB 8.1.1 Release Notes`
- Source Heading Path: `TiDB 8.1.1 Release Notes > Bug fixes`
- Source Line Ranges: `61-97`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`, `tiproxy`, `dashboard`
- Topic Tags: `bug-fixes`, `sql-execution`, `optimizer`, `query-results`, `memory-usage`, `oom`, `statistics`, `ddl`, `partitioning`, `cte`, `mpp`, `slow-log`, `grafana`, `resource-groups`, `plan-cache`, `metadata-locks`, `json-functions`, `foreign-keys`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0602_1a904f5baa`
- Source ID: `tidb-docs-8.1:releases/release-8.1.1.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2875b28280d1679ab80a0e9b918258250ae821ce9449e21b7df2d7fd18a885c8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.1#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 8.1.1 bug fixes affecting SQL execution, optimizer behavior, statistics, DDL, slow log and Grafana observability, resource groups, plan cache, memory usage, or specific statements and functions named in the release notes.
- Retrieval Keywords: TiDB 8.1.1 bug fixes, #55290 HashAgg disk spill incorrect query results parallel calculation, #54688 INDEX_HASH_JOIN cannot exit properly abnormally interrupted SQL, #54829 RANGE partitioned tables not strictly self-incrementing created, #54583 PointGet execution plans for _tidb_rowid, #54190 slow log internal SQL redacted to null by default, #53742 UPDATE operation TiDB OOM multi-table scenarios, #42734 Window function panic related subquery, #53730 LENGTH() condition removed utf8_bin utf8mb4_bin, #53540 Trying to start aggressive locking while it's already started, #53505 PREPARE EXECUTE CONV expression ? incorrect query results, #54181 recursive CTE operator incorrectly tracks memory usage, #48756 SHOW WARNINGS panic, #37986 TopN operator pushed down incorrectly, #46962 SHOW ERRORS predicate always true panic, #53026 INFORMATION_SCHEMA.TIDB_TRX STATE field empty, #53726 SELECT DISTINCT CAST(col AS DECIMAL), CAST(col AS SIGNED) incorrect results, #52335 DDL statements incorrectly use etcd tasks queue up, #53752 Distinct_count GlobalStats incorrect, #53972 tidb_enable_async_merge_global_stats tidb_analyze_partition_concurrency automatic statistics collection, #54908 TIMESTAMPADD() infinite loop month negative, #54428 Connection Count monitoring metric in Grafana incorrect, #54545 Connection Count of each resource group incorrect TiProxy resource groups, #49721 view does not work in recursive CTE, #51362 final AggMode non-final AggMode coexist in MPP, #53767 incorrect WARNINGS information using Optimizer Hints, #54005 memTracker not detached HashJoin IndexLookUp driven side Apply high memory usage, #53779 DECIMAL(0,0) can be created, #49803 PointGetPlan StatsInfo potential data races, #53634 metadata locks anomalous data using the plan cache, #53799 JSON-related functions errors inconsistent with MySQL, #53652 stats_meta foreign keys create table, #53834 memory_quota hint might not work in subqueries, #53592 GC error when loading statistics at startup
- Follow-up Guidance: The release notes list the affected operators, statements, system variables, table names, functions, metrics, and error text for each fixed issue.
- Classification Note: This chunk is classified as a release-note bug-fix summary for TiDB 8.1.1 because it enumerates resolved issues across SQL execution, optimizer, statistics, DDL, and observability in TiDB and related components.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that the disk spill for the HashAgg operator causes incorrect query results during parallel calculation [#55290](https://github.com/pingcap/tidb/issues/55290) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that `INDEX_HASH_JOIN` cannot exit properly when SQL is abnormally interrupted [#54688](https://github.com/pingcap/tidb/issues/54688) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that RANGE partitioned tables that are not strictly self-incrementing can be created [#54829](https://github.com/pingcap/tidb/issues/54829) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that `PointGet` execution plans for `_tidb_rowid` can be generated [#54583](https://github.com/pingcap/tidb/issues/54583) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that internal SQL statements in the slow log are redacted to null by default [#54190](https://github.com/pingcap/tidb/issues/54190) [#52743](https://github.com/pingcap/tidb/issues/52743) [#53264](https://github.com/pingcap/tidb/issues/53264) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the `UPDATE` operation can cause TiDB OOM in multi-table scenarios [#53742](https://github.com/pingcap/tidb/issues/53742) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the Window function might panic when there is a related subquery in it [#42734](https://github.com/pingcap/tidb/issues/42734) @[hi-rustin](https://github.com/hi-rustin)
    - Fix the issue that the `LENGTH()` condition is unexpectedly removed when the collation is `utf8_bin` or `utf8mb4_bin` [#53730](https://github.com/pingcap/tidb/issues/53730) @[elsa0520](https://github.com/elsa0520)
    - Fix the issue that after a statement within a transaction is killed by OOM, if TiDB continues to execute the next statement within the same transaction, you might get an error `Trying to start aggressive locking while it's already started` and a panic occurs [#53540](https://github.com/pingcap/tidb/issues/53540) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that `PREPARE`/`EXECUTE` statements with the `CONV` expression containing a `?` argument might result in incorrect query results when executed multiple times [#53505](https://github.com/pingcap/tidb/issues/53505) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the recursive CTE operator incorrectly tracks memory usage [#54181](https://github.com/pingcap/tidb/issues/54181) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that using `SHOW WARNINGS;` to obtain warnings might cause a panic [#48756](https://github.com/pingcap/tidb/issues/48756) @[xhebox](https://github.com/xhebox)
    - Fix the issue that the TopN operator might be pushed down incorrectly [#37986](https://github.com/pingcap/tidb/issues/37986) @[qw4990](https://github.com/qw4990)
    - Fix the issue that TiDB panics when executing the `SHOW ERRORS` statement with a predicate that is always `true` [#46962](https://github.com/pingcap/tidb/issues/46962) @[elsa0520](https://github.com/elsa0520)
    - Fix the issue that the `STATE` field in the `INFORMATION_SCHEMA.TIDB_TRX` table is empty due to the `size` of the `STATE` field not being defined [#53026](https://github.com/pingcap/tidb/issues/53026) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the issue that executing the `SELECT DISTINCT CAST(col AS DECIMAL), CAST(col AS SIGNED) FROM ...` query might return incorrect results [#53726](https://github.com/pingcap/tidb/issues/53726) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that DDL statements incorrectly use etcd and cause tasks to queue up [#52335](https://github.com/pingcap/tidb/issues/52335) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the `Distinct_count` information in GlobalStats might be incorrect [#53752](https://github.com/pingcap/tidb/issues/53752) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the `tidb_enable_async_merge_global_stats` and `tidb_analyze_partition_concurrency` system variables do not take effect during automatic statistics collection [#53972](https://github.com/pingcap/tidb/issues/53972) @[hi-rustin](https://github.com/hi-rustin)
    - Fix the issue that the `TIMESTAMPADD()` function goes into an infinite loop when the first argument is `month` and the second argument is negative [#54908](https://github.com/pingcap/tidb/issues/54908) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that the Connection Count monitoring metric in Grafana is incorrect when some connections exit before the handshake is complete [#54428](https://github.com/pingcap/tidb/issues/54428) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the Connection Count of each resource group is incorrect when using TiProxy and resource groups [#54545](https://github.com/pingcap/tidb/issues/54545) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that using a view does not work in recursive CTE [#49721](https://github.com/pingcap/tidb/issues/49721) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the `final` AggMode and the `non-final` AggMode cannot coexist in Massively Parallel Processing (MPP) [#51362](https://github.com/pingcap/tidb/issues/51362) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue of incorrect WARNINGS information when using Optimizer Hints [#53767](https://github.com/pingcap/tidb/issues/53767) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue of abnormally high memory usage caused by `memTracker` not being detached when the `HashJoin` or `IndexLookUp` operator is the driven side sub-node of the `Apply` operator [#54005](https://github.com/pingcap/tidb/issues/54005) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that the illegal column type `DECIMAL(0,0)` can be created in some cases [#53779](https://github.com/pingcap/tidb/issues/53779) @[tangenta](https://github.com/tangenta)
    - Fix the issue of potential data races during the execution of `(*PointGetPlan).StatsInfo()` [#49803](https://github.com/pingcap/tidb/issues/49803) [#43339](https://github.com/pingcap/tidb/issues/43339) @[qw4990](https://github.com/qw4990)
    - Fix the issue that improper use of metadata locks might lead to writing anomalous data when using the plan cache under certain circumstances [#53634](https://github.com/pingcap/tidb/issues/53634) @[zimulala](https://github.com/zimulala)
    - Fix the issue that JSON-related functions return errors inconsistent with MySQL in some cases [#53799](https://github.com/pingcap/tidb/issues/53799) @[dveeden](https://github.com/dveeden)
    - Fix the issue that TiDB does not create corresponding statistics metadata (`stats_meta`) when creating a table with foreign keys [#53652](https://github.com/pingcap/tidb/issues/53652) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the `memory_quota` hint might not work in subqueries [#53834](https://github.com/pingcap/tidb/issues/53834) @[qw4990](https://github.com/qw4990)
    - Fix the issue that TiDB might report an error due to GC when loading statistics at startup [#53592](https://github.com/pingcap/tidb/issues/53592) @[you06](https://github.com/you06)
