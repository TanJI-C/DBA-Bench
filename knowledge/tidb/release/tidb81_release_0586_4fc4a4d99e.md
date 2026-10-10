# Bug fixes for TiDB in 8.0.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes > Bug fixes`
- Source Line Ranges: `450-487`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `shared`
- Topic Tags: `bug-fixes`, `sql`, `statistics`, `auto-analyze`, `ddl`, `plan-cache`, `bindings`, `query-correctness`, `join`, `upgrade`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0586_4fc4a4d99e`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0ad9e0a9e6367ba7b882edda688a785b33725581110e75e83383a305d6730b4c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 8.0.0 bug fixes related to SQL correctness, auto analyze and statistics behavior, DDL and bindings issues, plan cache behavior, upgrade panics, or monitoring metrics.
- Retrieval Keywords: TiDB 8.0.0 Bug fixes, auto analyze triggered multiple times when there is no data change, #51775, auto analyze concurrency set incorrectly, #51749, index inconsistency adding multiple indexes using a single SQL statement, #51746, Column ... in from clause is ambiguous, NATURAL JOIN, #32044, wrong query results incorrectly eliminating constant values in group by, #38756, LEADING hint does not take effect in UNION ALL, #50067, BIT type columns decode failures in calculations of some functions, #49566, #50850, #50855, rolling upgrade tiup cluster upgrade/start panic interaction issue with PD, #50152, UNIQUE index lookup ORDER BY clause might cause an error, #49920, wrong query results ENUM or SET constant propagation, #49440, fatal error: concurrent map writes, Apply operator, #50347, SET_VAR string type control invalid, #50507, SYSDATE() plan cache tidb_sysdate_is_now, #49299, CREATE GLOBAL BINDING uppercase schema name does not take effect, #50646, Index Path selects duplicated indexes, #50496, PLAN REPLAYER fails to load bindings CREATE GLOBAL BINDING contains IN(), #43192, multiple analyze tasks fail failure reasons not recorded correctly, #50481, tidb_stats_load_sync_wait does not take effect, #50872, max_execute_time settings at multiple levels interfere with each other, #50914, concurrent updating of statistics thread safety, #50835, auto analyze on a partition table might cause TiDB to panic, #51187, SQL bindings might not work when IN() contains a different number of values, #51222, cannot correctly convert the type of a system variable in an expression, #43527, force-init-stats configured does not listen to the corresponding port, #51473, tidb_opt_objective='determinate' statistics might not be loaded when query does not contain predicates, #48257, init-stats process might cause TiDB to panic and load stats process to quit, #51581, query result is incorrect when the IN() predicate contains NULL, #51560, blocked DDL statements are not displayed in the MDL View when a DDL task involves multiple tables, #47743, processed_rows of the ANALYZE task might exceed total number of rows, #50632, HashJoin fails to spill to disk goroutine leak, #50841, CTE queries exceed limits goroutine leak, #50337, Can't find column ... aggregate functions used for group calculations, #50926, DDL operations such as renaming tables are stuck CREATE TABLE contains specific partitions or constraints, #50972, tidb_statistics_auto_analyze_total Grafana is not displayed as an integer, #51051
- Follow-up Guidance: The chunk enumerates many specific TiDB 8.0.0 fixes, including issue numbers, exact error texts, SQL statements, variables, and metric names that can be used to refine retrieval.
- Classification Note: This is a release-note bug-fix section for the TiDB component in a self-managed deployment scope, covering fixes across SQL execution, statistics, DDL, bindings, upgrade interaction with PD, and monitoring.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that `auto analyze` is triggered multiple times when there is no data change [#51775](https://github.com/pingcap/tidb/issues/51775) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that the `auto analyze` concurrency is set incorrectly [#51749](https://github.com/pingcap/tidb/issues/51749) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue of index inconsistency caused by adding multiple indexes using a single SQL statement [#51746](https://github.com/pingcap/tidb/issues/51746) @[tangenta](https://github.com/tangenta)
    - Fix the `Column ... in from clause is ambiguous` error that might occur when a query uses `NATURAL JOIN` [#32044](https://github.com/pingcap/tidb/issues/32044) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue of wrong query results due to TiDB incorrectly eliminating constant values in `group by` [#38756](https://github.com/pingcap/tidb/issues/38756) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that the `LEADING` hint does not take effect in `UNION ALL` statements [#50067](https://github.com/pingcap/tidb/issues/50067) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that `BIT` type columns might cause query errors due to decode failures when they are involved in calculations of some functions [#49566](https://github.com/pingcap/tidb/issues/49566) [#50850](https://github.com/pingcap/tidb/issues/50850) [#50855](https://github.com/pingcap/tidb/issues/50855) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that TiDB might panic when performing a rolling upgrade using `tiup cluster upgrade/start` due to an interaction issue with PD [#50152](https://github.com/pingcap/tidb/issues/50152) @[zimulala](https://github.com/zimulala)
    - Fix the issue that executing `UNIQUE` index lookup with an `ORDER BY` clause might cause an error [#49920](https://github.com/pingcap/tidb/issues/49920) @[jackysp](https://github.com/jackysp)
    - Fix the issue that TiDB returns wrong query results when processing `ENUM` or `SET` types by constant propagation [#49440](https://github.com/pingcap/tidb/issues/49440) @[winoros](https://github.com/winoros)
    - Fix the issue that TiDB might panic when a query contains the Apply operator and the `fatal error: concurrent map writes` error occurs [#50347](https://github.com/pingcap/tidb/issues/50347) @[SeaRise](https://github.com/SeaRise)
    - Fix the issue that the control of `SET_VAR` for variables of the string type might become invalid [#50507](https://github.com/pingcap/tidb/issues/50507) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the `SYSDATE()` function incorrectly uses the time in the plan cache when `tidb_sysdate_is_now` is set to `1` [#49299](https://github.com/pingcap/tidb/issues/49299) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that when executing the `CREATE GLOBAL BINDING` statement, if the schema name is in uppercase, the binding does not take effect [#50646](https://github.com/pingcap/tidb/issues/50646) @[qw4990](https://github.com/qw4990)
    - Fix the issue that `Index Path` selects duplicated indexes [#50496](https://github.com/pingcap/tidb/issues/50496) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that `PLAN REPLAYER` fails to load bindings when the `CREATE GLOBAL BINDING` statement contains `IN()` [#43192](https://github.com/pingcap/tidb/issues/43192) @[King-Dylan](https://github.com/King-Dylan)
    - Fix the issue that when multiple `analyze` tasks fail, the failure reasons are not recorded correctly [#50481](https://github.com/pingcap/tidb/issues/50481) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that `tidb_stats_load_sync_wait` does not take effect [#50872](https://github.com/pingcap/tidb/issues/50872) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that `max_execute_time` settings at multiple levels interfere with each other [#50914](https://github.com/pingcap/tidb/issues/50914) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue of thread safety caused by concurrent updating of statistics [#50835](https://github.com/pingcap/tidb/issues/50835) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that executing `auto analyze` on a partition table might cause TiDB to panic [#51187](https://github.com/pingcap/tidb/issues/51187) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that SQL bindings might not work when `IN()` in a SQL statement contains a different number of values [#51222](https://github.com/pingcap/tidb/issues/51222) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that TiDB cannot correctly convert the type of a system variable in an expression [#43527](https://github.com/pingcap/tidb/issues/43527) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that TiDB does not listen to the corresponding port when `force-init-stats` is configured [#51473](https://github.com/pingcap/tidb/issues/51473) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that in `determinate` mode (`tidb_opt_objective='determinate'`), if a query does not contain predicates, statistics might not be loaded [#48257](https://github.com/pingcap/tidb/issues/48257) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that the `init-stats` process might cause TiDB to panic and the `load stats` process to quit [#51581](https://github.com/pingcap/tidb/issues/51581) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the query result is incorrect when the `IN()` predicate contains `NULL` [#51560](https://github.com/pingcap/tidb/issues/51560) @[winoros](https://github.com/winoros)
    - Fix the issue that blocked DDL statements are not displayed in the MDL View when a DDL task involves multiple tables [#47743](https://github.com/pingcap/tidb/issues/47743) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the `processed_rows` of the `ANALYZE` task on a table might exceed the total number of rows in that table [#50632](https://github.com/pingcap/tidb/issues/50632) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the goroutine leak issue that might occur when the `HashJoin` operator fails to spill to disk [#50841](https://github.com/pingcap/tidb/issues/50841) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the goroutine leak issue that occurs when the memory usage of CTE queries exceed limits [#50337](https://github.com/pingcap/tidb/issues/50337) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the `Can't find column ...` error that might occur when aggregate functions are used for group calculations [#50926](https://github.com/pingcap/tidb/issues/50926) @[qw4990](https://github.com/qw4990)
    - Fix the issue that DDL operations such as renaming tables are stuck when the `CREATE TABLE` statement contains specific partitions or constraints [#50972](https://github.com/pingcap/tidb/issues/50972) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the monitoring metric `tidb_statistics_auto_analyze_total` on Grafana is not displayed as an integer [#51051](https://github.com/pingcap/tidb/issues/51051) @[hawkingrei](https://github.com/hawkingrei)
