# TiDB 7.1.1 bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.1.md`
- Source Title: `TiDB 7.1.1 Release Notes`
- Source Heading Path: `TiDB 7.1.1 Release Notes > Bug fixes`
- Source Line Ranges: `55-94`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `br`, `tiflash`
- Topic Tags: `release-notes`, `bug-fixes`, `gc`, `locks`, `deadlock`, `memory-leak`, `oom`, `ddl`, `upgrade`, `ttl`, `permissions`, `partitioning`, `flashback`, `follower-read`, `cursor-fetch`, `statistics`, `mpp`, `join-reorder`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0455_0dd9effd1d`
- Source ID: `tidb-docs-8.1:releases/release-7.1.1.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `55637ef7b19b2214dfdd16563f0bce4a4ed00a4805b806db93f3e17527ee7235`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.1#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.1 bug fixes related to query correctness, memory usage, DDL and upgrade issues, locks, GC, permissions, partitioning, follower read, BR restore, or MPP behavior.
- Retrieval Keywords: TiDB 7.1.1 bug fixes, GC Resolve Locks might miss some pessimistic locks, Stats Collector deadlock when a new session is created, memory tracker potential memory leak, batch coprocessor retry incorrect Region information, index scan data race, MPP mode incorrect when tidb_enable_parallel_apply is enabled, indexMerge killed hang-up, statistics SQL execution details causes TiDB OOM, FormatSQL() truncate extremely long SQL statements, DDL operations get stuck during cluster upgrade, TTL tasks not taken over after failures, MySQL Cursor Fetch protocol, tidb_mem_quota_query, INFORMATION_SCHEMA.TIFLASH_REPLICA permissions, ADMIN SHOW DDL JOBS ROW_COUNT inaccurate, Range COLUMNS partitioned table error, FLASHBACK failures and data inconsistency, duplicate entry restoring AUTO_ID_CACHE=1 using BR, DXF task queue memory leak, Header read timeout, PD isolation might block the running DDL, Join Reorder incorrect outer join results, CTEs might cause insufficient disk space, follower read does not handle flashback errors before retrying, SHOW PROCESSLIST TxnStart, LEADING hint does not support querying block aliases, PREPARE stmt FROM "ANALYZE TABLE xxx"
- Follow-up Guidance: 
- Classification Note: This is a release-notes bug-fix chunk listing resolved issues in TiDB 7.1.1, including exact errors, statements, variables, and feature names for retrieval.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that the GC Resolve Locks step might miss some pessimistic locks [#45134](https://github.com/pingcap/tidb/issues/45134) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that Stats Collector might cause deadlock when a new session is created [#44502](https://github.com/pingcap/tidb/issues/44502) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix the potential memory leak issue in memory tracker [#44612](https://github.com/pingcap/tidb/issues/44612) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that batch coprocessor retry might generate incorrect Region information that causes query failure [#44622](https://github.com/pingcap/tidb/issues/44622) @[windtalker](https://github.com/windtalker)
    - Fix the potential data race issue in index scan [#45126](https://github.com/pingcap/tidb/issues/45126) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that query results in MPP mode are incorrect when `tidb_enable_parallel_apply` is enabled [#45299](https://github.com/pingcap/tidb/issues/45299) @[windtalker](https://github.com/windtalker)
    - Fix the hang-up issue that occurs when queries with `indexMerge` are killed [#45279](https://github.com/pingcap/tidb/issues/45279) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that excessive memory consumption of SQL execution details in statistics causes TiDB OOM in extreme cases [#44047](https://github.com/pingcap/tidb/issues/44047) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the `FormatSQL()` method cannot properly truncate extremely long SQL statements in input [#44542](https://github.com/pingcap/tidb/issues/44542) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that DDL operations get stuck during cluster upgrade, which causes upgrade failure [#44158](https://github.com/pingcap/tidb/issues/44158) @[zimulala](https://github.com/zimulala)
    - Fix the issue that other TiDB nodes do not take over TTL tasks after failures in one TiDB node [#45022](https://github.com/pingcap/tidb/issues/45022) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that when the MySQL Cursor Fetch protocol is used, the memory consumption of result sets might exceed the `tidb_mem_quota_query` limit and causes TiDB OOM. After the fix, TiDB will automatically write result sets to the disk to release memory [#43233](https://github.com/pingcap/tidb/issues/43233) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that users can view information in the `INFORMATION_SCHEMA.TIFLASH_REPLICA` table even without permissions [#45320](https://github.com/pingcap/tidb/issues/45320) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that `ROW_COUNT` returned by the `ADMIN SHOW DDL JOBS` statement is inaccurate [#44044](https://github.com/pingcap/tidb/issues/44044) @[tangenta](https://github.com/tangenta)
    - Fix the issue that querying a Range COLUMNS partitioned table might get an error [#43459](https://github.com/pingcap/tidb/issues/43459) @[mjonss](https://github.com/mjonss)
    - Fix the issue that resuming a paused DDL task fails [#44217](https://github.com/pingcap/tidb/issues/44217) @[dhysum](https://github.com/dhysum)
    - Fix the issue that in-memory pessimistic locks cause `FLASHBACK` failures and data inconsistency [#44292](https://github.com/pingcap/tidb/issues/44292) @[JmPotato](https://github.com/JmPotato)
    - Fix the issue that deleted tables can still be read from `INFORMATION_SCHEMA` [#43714](https://github.com/pingcap/tidb/issues/43714) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the cluster upgrade fails when there are paused DDL operations before the upgrade [#44225](https://github.com/pingcap/tidb/issues/44225) @[zimulala](https://github.com/zimulala)
    - Fix the `duplicate entry` error that occurs when restoring a table with `AUTO_ID_CACHE=1` using BR [#44716](https://github.com/pingcap/tidb/issues/44716) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the data index inconsistency issue triggered by multiple switches of DDL owner [#44619](https://github.com/pingcap/tidb/issues/44619) @[tangenta](https://github.com/tangenta)
    - Fix the issue that canceling an `ADD INDEX` DDL task in the `none` status might cause memory leak because this task is not removed from the Distributed eXecution Framework (DXF) task queue [#44205](https://github.com/pingcap/tidb/issues/44205) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the proxy protocol reports the `Header read timeout` error when processing certain erroneous data [#43205](https://github.com/pingcap/tidb/issues/43205) @[blacktear23](https://github.com/blacktear23)
    - Fix the issue that PD isolation might block the running DDL [#44267](https://github.com/pingcap/tidb/issues/44267) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the query result of the `SELECT CAST(n AS CHAR)` statement is incorrect when `n` in the statement is a negative number [#44786](https://github.com/pingcap/tidb/issues/44786) @[xhebox](https://github.com/xhebox)
    - Fix the issue of excessive memory usage after creating a large number of empty partitioned tables [#44308](https://github.com/pingcap/tidb/issues/44308) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that Join Reorder might cause incorrect outer join results [#44314](https://github.com/pingcap/tidb/issues/44314) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that queries containing Common Table Expressions (CTEs) might cause insufficient disk space [#44477](https://github.com/pingcap/tidb/issues/44477) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that dropping a database causes slow GC progress [#33069](https://github.com/pingcap/tidb/issues/33069) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that adding an index fails in the ingest mode [#44137](https://github.com/pingcap/tidb/issues/44137) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the `SELECT` statement returns an error for a partitioned table if the table partition definition uses the `FLOOR()` function to round a partitioned column [#42323](https://github.com/pingcap/tidb/issues/42323) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that follower read does not handle flashback errors before retrying, which causes query errors [#43673](https://github.com/pingcap/tidb/issues/43673) @[you06](https://github.com/you06)
    - Fix the issue that using `memTracker` with cursor fetch causes memory leaks [#44254](https://github.com/pingcap/tidb/issues/44254) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the `SHOW PROCESSLIST` statement cannot display the TxnStart of the transaction of the statement with a long subquery time [#40851](https://github.com/pingcap/tidb/issues/40851) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that the `LEADING` hint does not support querying block aliases [#44645](https://github.com/pingcap/tidb/issues/44645) @[qw4990](https://github.com/qw4990)
    - Fix the issue that `PREPARE stmt FROM "ANALYZE TABLE xxx"` might be killed by `tidb_mem_quota_query` [#44320](https://github.com/pingcap/tidb/issues/44320) @[chrysan](https://github.com/chrysan)
