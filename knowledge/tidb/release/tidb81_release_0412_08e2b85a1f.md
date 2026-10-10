# TiDB bug fixes in 6.5.9

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.9.md`
- Source Title: `TiDB 6.5.9 Release Notes`
- Source Heading Path: `TiDB 6.5.9 Release Notes > Bug fixes`
- Source Line Ranges: `46-82`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `tiflash`
- Topic Tags: `bugfix`, `query correctness`, `statistics`, `ddl`, `memory`, `panic`, `health`, `hot regions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0412_08e2b85a1f`
- Source ID: `tidb-docs-8.1:releases/release-6.5.9.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `33da36eb1b4e1b8ab043839468d66fb9419e7561070b7774a684e5177fce6200`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.9#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.9.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.9 bug fixes related to query correctness, statistics, DDL, memory leaks or panic, health status, Grafana metrics, TiFlash compaction, or hot region metadata.
- Retrieval Keywords: TiDB 6.5.9 Release Notes, Bug fixes, Stats Healthy Distribution, tidb_statistics_auto_analyze_total, MemTableScan, HAVING clause correlated columns, Common Table Expressions CTE partitioned tables missing statistics, MPP JOIN SELECT only constants incorrect query results, AUTO_INCREMENT non-consecutive IDs, global statistics for partitioned tables, INSERT IGNORE write-only default values, shuffleExec quits unexpectedly, HashJoin spill to disk goroutine leak, IN() predicate contains NULL, JSON of BINARY type error, parallel Apply clustered index, init-stats panic load stats quit, tidb_merge_partition_stats_concurrency, auto analyze partitioned tables, automatic statistics updates time window, approx_percentile panic, BIT type decode failures, force-init-stats, ALTER TABLE ... COMPACT TIFLASH REPLICA, tidb_gogc_tuner_threshold, tidb_server_memory_limit, Can't find column ..., REVERSE function BIT type, HTTP interface add label returns success but does not take effect, IFNULL inconsistent with MySQL, server marked as health before initialization is complete, TIDB_HOT_REGIONS, EXCHANGE PARTITION foreign keys
- Follow-up Guidance: The chunk lists individual fixed issues with exact identifiers, SQL constructs, metrics, system variables, and component behaviors corrected in TiDB 6.5.9.
- Classification Note: This is a release-note bug-fix section for the TiDB component in a self-managed deployment, covering fixes across dashboard, TiFlash, SQL execution, statistics, DDL, memory, and health-related topics.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that dropped tables are still counted by the Grafana `Stats Healthy Distribution` panel [#39349](https://github.com/pingcap/tidb/issues/39349) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix the issue that TiDB does not handle the `WHERE <column_name>` filtering condition in a SQL statement when the query of that statement involves the `MemTableScan` operator [#40937](https://github.com/pingcap/tidb/issues/40937) @[zhongzc](https://github.com/zhongzc)
    - Fix the issue that query results might be incorrect when the `HAVING` clause in a subquery contains correlated columns [#51107](https://github.com/pingcap/tidb/issues/51107) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that query results might be incorrect when you use Common Table Expressions (CTE) to access partitioned tables with missing statistics [#51873](https://github.com/pingcap/tidb/issues/51873) @[qw4990](https://github.com/qw4990)
    - Fix the issue that query execution using MPP might lead to incorrect query results when a SQL statement contains `JOIN` and the `SELECT` list in the statement contains only constants [#50358](https://github.com/pingcap/tidb/issues/50358) @[yibin87](https://github.com/yibin87)
    - Fix the issue that the `AUTO_INCREMENT` attribute causes non-consecutive IDs due to unnecessary transaction conflicts when assigning auto-increment IDs [#50819](https://github.com/pingcap/tidb/issues/50819) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the monitoring metric `tidb_statistics_auto_analyze_total` on Grafana is not displayed as an integer [#51051](https://github.com/pingcap/tidb/issues/51051) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that errors might be returned during the concurrent merging of global statistics for partitioned tables [#48713](https://github.com/pingcap/tidb/issues/48713) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that getting the default value of a column returns an error if the column default value is dropped [#50043](https://github.com/pingcap/tidb/issues/50043) [#51324](https://github.com/pingcap/tidb/issues/51324) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that the `INSERT ignore` statement cannot fill in default values when the column is write-only [#40192](https://github.com/pingcap/tidb/issues/40192) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that TiDB crashes when `shuffleExec` quits unexpectedly [#48230](https://github.com/pingcap/tidb/issues/48230) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the goroutine leak issue that might occur when the `HashJoin` operator fails to spill to disk [#50841](https://github.com/pingcap/tidb/issues/50841) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that renaming tables does not take effect when committing multiple statements in a transaction [#39664](https://github.com/pingcap/tidb/issues/39664) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the query result is incorrect when the `IN()` predicate contains `NULL` [#51560](https://github.com/pingcap/tidb/issues/51560) @[winoros](https://github.com/winoros)
    - Fix the issue that querying JSON of `BINARY` type might cause an error in some cases [#51547](https://github.com/pingcap/tidb/issues/51547) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that parallel `Apply` might generate incorrect results when the table has a clustered index [#51372](https://github.com/pingcap/tidb/issues/51372) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that the `init-stats` process might cause TiDB to panic and the `load stats` process to quit [#51581](https://github.com/pingcap/tidb/issues/51581) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the `tidb_merge_partition_stats_concurrency` variable does not take effect when `auto analyze` is processing partitioned tables [#47594](https://github.com/pingcap/tidb/issues/47594) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that after the time window for automatic statistics updates is configured, statistics might still be updated outside that time window [#49552](https://github.com/pingcap/tidb/issues/49552) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the `approx_percentile` function might cause TiDB panic [#40463](https://github.com/pingcap/tidb/issues/40463) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that `BIT` type columns might cause query errors due to decode failures when they are involved in calculations of some functions [#49566](https://github.com/pingcap/tidb/issues/49566) [#50850](https://github.com/pingcap/tidb/issues/50850) [#50855](https://github.com/pingcap/tidb/issues/50855) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the goroutine leak issue that occurs when the memory usage of CTE queries exceed limits [#50337](https://github.com/pingcap/tidb/issues/50337) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that TiDB does not listen to the corresponding port when `force-init-stats` is configured [#51473](https://github.com/pingcap/tidb/issues/51473) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that `ALTER TABLE ... COMPACT TIFLASH REPLICA` might incorrectly end when the primary key type is `VARCHAR` [#51810](https://github.com/pingcap/tidb/issues/51810) @[breezewish](https://github.com/breezewish)
    - Fix the issue that the `tidb_gogc_tuner_threshold` system variable is not adjusted accordingly after the `tidb_server_memory_limit` variable is modified [#48180](https://github.com/pingcap/tidb/issues/48180) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the `Can't find column ...` error that might occur when aggregate functions are used for group calculations [#50926](https://github.com/pingcap/tidb/issues/50926) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the `REVERSE` function reports an error when processing columns of the `BIT` type [#50850](https://github.com/pingcap/tidb/issues/50850) [#50855](https://github.com/pingcap/tidb/issues/50855) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that `INSERT IGNORE` reports an error when inserting data in bulk into a table undergoing a DDL operation [#50993](https://github.com/pingcap/tidb/issues/50993) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the TiDB server adds a label via the HTTP interface and returns success, but does not take effect [#51427](https://github.com/pingcap/tidb/issues/51427) @[you06](https://github.com/you06)
    - Fix the issue that the type returned by the `IFNULL` function is inconsistent with MySQL [#51765](https://github.com/pingcap/tidb/issues/51765) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the TiDB server is marked as health before the initialization is complete [#51596](https://github.com/pingcap/tidb/issues/51596) @[shenqidebaozi](https://github.com/shenqidebaozi)
    - Fix the issue that querying the `TIDB_HOT_REGIONS` table might incorrectly return `INFORMATION_SCHEMA` tables [#50810](https://github.com/pingcap/tidb/issues/50810) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that `EXCHANGE PARTITION` incorrectly processes foreign keys [#51807](https://github.com/pingcap/tidb/issues/51807) @[YangKeao](https://github.com/YangKeao)
