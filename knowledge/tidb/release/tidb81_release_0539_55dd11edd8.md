# TiDB 7.5.3 bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.3.md`
- Source Title: `TiDB 7.5.3 Release Notes`
- Source Heading Path: `TiDB 7.5.3 Release Notes > Bug fixes`
- Source Line Ranges: `48-83`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `tiproxy`
- Topic Tags: `release-notes`, `bug-fixes`, `memory-usage`, `oom`, `planner`, `cte`, `statistics`, `warnings`, `sql-compatibility`, `grafana`, `resource-groups`, `data-loss`, `authentication`, `stale-read`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0539_55dd11edd8`
- Source ID: `tidb-docs-8.1:releases/release-7.5.3.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1daf6e26bc1235914fdd2809f8307a396d8716733cec18ed4fc941a7d1d00f97`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.3#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.3.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 7.5.3 bug-fix list for specific SQL errors, memory issues, planner problems, monitoring inaccuracies, authentication behavior, and stale read latency.
- Retrieval Keywords: TiDB 7.5.3 bug fixes, loading index statistics memory leaks, UPDATE operation TiDB OOM multi-table scenarios, indirect placeholder ? references GROUP BY, LENGTH() condition utf8_bin utf8mb4_bin, scientific notation warning instead of error, recursive CTE invalid pointers, stats_history duplicate primary keys, non-correlated subqueries LIMIT column pruning, memTracker HashJoin IndexLookUp Apply, recursive CTE memory usage, transactions tracked multiple times, SHOW WARNINGS panic, UNSIGNED field to -1 sql_mode='', TIMESTAMPADD() infinite loop month negative, Connection Count monitoring metric in Grafana, resource group Connection Count TiProxy, CREATE OR REPLACE VIEW table doesn't exist, virtual columns incorrect query results, SELECT DISTINCT CAST(col AS DECIMAL), CAST(col AS SIGNED), Optimizer Hints WARNINGS, DECIMAL(0,0), memory_quota hint subqueries, JSON-related functions inconsistent with MySQL, metadata locks plan cache anomalous data, invalid memory address or nil pointer dereference, Trying to start aggressive locking while it's already started, ALTER TABLE ... REMOVE PARTITIONING data loss, PREPARE EXECUTE CONV expression ? argument, auth_socket authentication plugin, stale reads information schema cache misses, INFORMATION_SCHEMA.TIDB_TRX, STATE field, tidb_enable_async_merge_global_stats, tidb_analyze_partition_concurrency, automatic statistics collection
- Follow-up Guidance: 
- Classification Note: The content is classified as a release bug-fix chunk because it enumerates TiDB 7.5.3 fixes for defects, errors, incorrect results, and monitoring or behavior problems.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that loading index statistics might cause memory leaks [#54022](https://github.com/pingcap/tidb/issues/54022) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that the `UPDATE` operation can cause TiDB OOM in multi-table scenarios [#53742](https://github.com/pingcap/tidb/issues/53742) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that indirect placeholder `?` references in a `GROUP BY` statement cannot find columns [#53872](https://github.com/pingcap/tidb/issues/53872) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the `LENGTH()` condition is unexpectedly removed when the collation is `utf8_bin` or `utf8mb4_bin` [#53730](https://github.com/pingcap/tidb/issues/53730) @[elsa0520](https://github.com/elsa0520)
    - Fix the issue that inserting an overlarge number in scientific notation returns a warning instead of an error, making it consistent with MySQL [#47787](https://github.com/pingcap/tidb/issues/47787) @[qw4990](https://github.com/qw4990)
    - Fix the issue that recursive CTE queries might result in invalid pointers [#54449](https://github.com/pingcap/tidb/issues/54449) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that statistics collection does not update the `stats_history` table when encountering duplicate primary keys [#47539](https://github.com/pingcap/tidb/issues/47539) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that when queries contain non-correlated subqueries and `LIMIT` clauses, column pruning might be incomplete, resulting in a less optimal plan [#54213](https://github.com/pingcap/tidb/issues/54213) @[qw4990](https://github.com/qw4990)
    - Fix the issue of abnormally high memory usage caused by `memTracker` not being detached when the `HashJoin` or `IndexLookUp` operator is the driven side sub-node of the `Apply` operator [#54005](https://github.com/pingcap/tidb/issues/54005) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that the recursive CTE operator incorrectly tracks memory usage [#54181](https://github.com/pingcap/tidb/issues/54181) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that the memory used by transactions might be tracked multiple times [#53984](https://github.com/pingcap/tidb/issues/53984) @[ekexium](https://github.com/ekexium)
    - Fix the issue that using `SHOW WARNINGS;` to obtain warnings might cause a panic [#48756](https://github.com/pingcap/tidb/issues/48756) @[xhebox](https://github.com/xhebox)
    - Fix the issue that updating an `UNSIGNED` type of field to `-1` returns `null` instead of `0` when `sql_mode=''` [#47816](https://github.com/pingcap/tidb/issues/47816) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the `TIMESTAMPADD()` function goes into an infinite loop when the first argument is `month` and the second argument is negative [#54908](https://github.com/pingcap/tidb/issues/54908) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that the Connection Count monitoring metric in Grafana is incorrect when some connections exit before the handshake is complete [#54428](https://github.com/pingcap/tidb/issues/54428) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the Connection Count of each resource group is incorrect when using TiProxy and resource groups [#54545](https://github.com/pingcap/tidb/issues/54545) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that executing `CREATE OR REPLACE VIEW` concurrently might result in the `table doesn't exist` error [#53673](https://github.com/pingcap/tidb/issues/53673) @[tangenta](https://github.com/tangenta)
    - Fix the issue that TiDB might return incorrect query results when you query tables with virtual columns in transactions that involve data modification operations [#53951](https://github.com/pingcap/tidb/issues/53951) @[qw4990](https://github.com/qw4990)
    - Fix the issue that executing the `SELECT DISTINCT CAST(col AS DECIMAL), CAST(col AS SIGNED) FROM ...` query might return incorrect results [#53726](https://github.com/pingcap/tidb/issues/53726) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue of incorrect WARNINGS information when using Optimizer Hints [#53767](https://github.com/pingcap/tidb/issues/53767) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the illegal column type `DECIMAL(0,0)` can be created in some cases [#53779](https://github.com/pingcap/tidb/issues/53779) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the `memory_quota` hint might not work in subqueries [#53834](https://github.com/pingcap/tidb/issues/53834) @[qw4990](https://github.com/qw4990)
    - Fix the issue that JSON-related functions return errors inconsistent with MySQL in some cases [#53799](https://github.com/pingcap/tidb/issues/53799) @[dveeden](https://github.com/dveeden)
    - Fix the issue that improper use of metadata locks might lead to writing anomalous data when using the plan cache under certain circumstances [#53634](https://github.com/pingcap/tidb/issues/53634) @[zimulala](https://github.com/zimulala)
    - Fix the issue that certain filter conditions in queries might cause the planner module to report an `invalid memory address or nil pointer dereference` error [#53582](https://github.com/pingcap/tidb/issues/53582) [#53580](https://github.com/pingcap/tidb/issues/53580) [#53594](https://github.com/pingcap/tidb/issues/53594) [#53603](https://github.com/pingcap/tidb/issues/53603) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that after a statement within a transaction is killed by OOM, if TiDB continues to execute the next statement within the same transaction, you might get an error `Trying to start aggressive locking while it's already started` and a panic occurs [#53540](https://github.com/pingcap/tidb/issues/53540) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that executing `ALTER TABLE ... REMOVE PARTITIONING` might cause data loss [#53385](https://github.com/pingcap/tidb/issues/53385) @[mjonss](https://github.com/mjonss)
    - Fix the issue that `PREPARE`/`EXECUTE` statements with the `CONV` expression containing a `?` argument might result in incorrect query results when executed multiple times [#53505](https://github.com/pingcap/tidb/issues/53505) @[qw4990](https://github.com/qw4990)
    - Fix the issue that TiDB fails to reject unauthenticated user connections in some cases when using the `auth_socket` authentication plugin [#54031](https://github.com/pingcap/tidb/issues/54031) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the query latency of stale reads increases, caused by information schema cache misses [#53428](https://github.com/pingcap/tidb/issues/53428) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that the `STATE` field in the `INFORMATION_SCHEMA.TIDB_TRX` table is empty due to the `size` of the `STATE` field not being defined [#53026](https://github.com/pingcap/tidb/issues/53026) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the issue that the `tidb_enable_async_merge_global_stats` and `tidb_analyze_partition_concurrency` system variables do not take effect during automatic statistics collection [#53972](https://github.com/pingcap/tidb/issues/53972) @[hi-rustin](https://github.com/Rustin170506)
