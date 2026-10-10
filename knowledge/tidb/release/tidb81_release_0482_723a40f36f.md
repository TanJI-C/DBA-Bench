# TiDB bug fixes in 7.1.6

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.6.md`
- Source Title: `TiDB 7.1.6 Release Notes`
- Source Heading Path: `TiDB 7.1.6 Release Notes > Bug fixes`
- Source Line Ranges: `110-142`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `bug-fixes`, `query-execution`, `cte`, `statistics`, `planner`, `ddl`, `authentication`, `ttl`, `stale-read`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0482_723a40f36f`
- Source ID: `tidb-docs-8.1:releases/release-7.1.6.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f702323a9dfd1d093373771448ea96907f3ac20b3161a1082127e5e5cc895940`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.6 bug fixes related to SQL execution, CTE, statistics, planner, DDL, authentication, TTL, stale read, or specific fixed errors and incorrect results.
- Retrieval Keywords: TiDB 7.1.6 bug fixes, recursive CTE UPDATE DELETE error not take effect, #55666, correlated subquery and CTE hang incorrect results, #55551, statistics for string columns with non-binary collations fail to load, #55684, IndexJoin duplicate rows Left Outer Anti Semi, #52902, UNION incorrect results, #52985, StreamAggExec empty groupOffset panic, #53867, RANGE partitioned tables not strictly self-incrementing created, #54829, tidb_mem_quota_query query stuck when terminated, #55042, INFORMATION_SCHEMA.TIDB_TRX STATE field empty, #53026, IndexNestedLoopHashJoin data race, #49692, wrong TableDual plan empty query results, #50051, mysql.stats_histograms tot_col_size negative, #55126, FLOAT to UNSIGNED incorrect results, #41736, auth_socket unauthenticated user connections, #54031, memory_quota hint not work in subqueries, #53834, metadata lock DDL plan cache scenario, #51407, CURRENT_DATE() default value incorrect query results, #53746, COALESCE() DATE type incorrect result type, #46475, PipelinedWindow Apply unexpected error repeated opening and closing, #53600, TopN correlated subqueries incorrect result, #52777, recursive CTE operator incorrectly tracks memory usage, #54181, SHOW COLUMNS view error, #54964, tidb_ttl_delete_worker_count TTL job fail to complete, #55561, view does not work in recursive CTE, #49721, stats_meta foreign keys create table, #53652, query incorrect results after being killed, #50089, statistics synchronous loading high query concurrency fail unexpectedly, #52294, invalid memory address or nil pointer dereference planner filter conditions, #53582, #53580, #53594, #53603, fail to get stats version for this histogram, #52657, TIMESTAMPADD() month negative infinite loop, #54908, tidb_mem_quota_analyze crash updating statistics exceeds limit, #52601, duplicate entry adding unique indexes, #56161, stale reads latency increases information schema cache misses, #53428
- Follow-up Guidance: The source lists the fixed issue descriptions together with the related GitHub issue numbers for each bug fix in TiDB 7.1.6.
- Classification Note: This chunk is classified as a TiDB release bug-fix summary because the official content is a release-notes list of resolved TiDB issues across SQL, planner, statistics, DDL, authentication, TTL, and stale read behavior.

## Official Source Content

- Fix the issue that when an `UPDATE` or `DELETE` statement contains a recursive CTE, the statement might report an error or not take effect [#55666](https://github.com/pingcap/tidb/issues/55666) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that TiDB might hang or return incorrect results when executing a query containing a correlated subquery and CTE [#55551](https://github.com/pingcap/tidb/issues/55551) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that statistics for string columns with non-binary collations might fail to load when initializing statistics [#55684](https://github.com/pingcap/tidb/issues/55684) @[winoros](https://github.com/winoros)
    - Fix the issue that IndexJoin produces duplicate rows when calculating hash values in the Left Outer Anti Semi type [#52902](https://github.com/pingcap/tidb/issues/52902) @[yibin87](https://github.com/yibin87)
    - Fix the issue that a query statement that contains `UNION` might return incorrect results [#52985](https://github.com/pingcap/tidb/issues/52985) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that empty `groupOffset` in `StreamAggExec` might cause TiDB to panic [#53867](https://github.com/pingcap/tidb/issues/53867) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that RANGE partitioned tables that are not strictly self-incrementing can be created [#54829](https://github.com/pingcap/tidb/issues/54829) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the query might get stuck when terminated because the memory usage exceeds the limit set by `tidb_mem_quota_query` [#55042](https://github.com/pingcap/tidb/issues/55042) @[yibin87](https://github.com/yibin87)
    - Fix the issue that the `STATE` field in the `INFORMATION_SCHEMA.TIDB_TRX` table is empty due to the `size` of the `STATE` field not being defined [#53026](https://github.com/pingcap/tidb/issues/53026) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the data race issue in `IndexNestedLoopHashJoin` [#49692](https://github.com/pingcap/tidb/issues/49692) @[solotzg](https://github.com/solotzg)
    - Fix the issue that a wrong TableDual plan causes empty query results [#50051](https://github.com/pingcap/tidb/issues/50051) @[onlyacat](https://github.com/onlyacat)
    - Fix the issue that the `tot_col_size` column in the `mysql.stats_histograms` table might be a negative number [#55126](https://github.com/pingcap/tidb/issues/55126) @[qw4990](https://github.com/qw4990)
    - Fix the issue that data conversion from the `FLOAT` type to the `UNSIGNED` type returns incorrect results [#41736](https://github.com/pingcap/tidb/issues/41736) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that TiDB fails to reject unauthenticated user connections in some cases when using the `auth_socket` authentication plugin [#54031](https://github.com/pingcap/tidb/issues/54031) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the `memory_quota` hint might not work in subqueries [#53834](https://github.com/pingcap/tidb/issues/53834) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the metadata lock fails to prevent DDL operations from executing in the plan cache scenario [#51407](https://github.com/pingcap/tidb/issues/51407) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that using `CURRENT_DATE()` as the default value for a column results in incorrect query results [#53746](https://github.com/pingcap/tidb/issues/53746) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the `COALESCE()` function returns incorrect result type for `DATE` type parameters [#46475](https://github.com/pingcap/tidb/issues/46475) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Reset the parameters in the `Open` method of `PipelinedWindow` to fix the unexpected error that occurs when the `PipelinedWindow` is used as a child node of `Apply` due to the reuse of previous parameter values caused by repeated opening and closing operations [#53600](https://github.com/pingcap/tidb/issues/53600) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the incorrect result of the TopN operator in correlated subqueries [#52777](https://github.com/pingcap/tidb/issues/52777) @[yibin87](https://github.com/yibin87)
    - Fix the issue that the recursive CTE operator incorrectly tracks memory usage [#54181](https://github.com/pingcap/tidb/issues/54181) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that an error occurs when using `SHOW COLUMNS` to view columns in a view [#54964](https://github.com/pingcap/tidb/issues/54964) @[lance6716](https://github.com/lance6716)
    - Fix the issue that reducing the value of `tidb_ttl_delete_worker_count` during TTL job execution makes the job fail to complete [#55561](https://github.com/pingcap/tidb/issues/55561) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that using a view does not work in recursive CTE [#49721](https://github.com/pingcap/tidb/issues/49721) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that TiDB does not create corresponding statistics metadata (`stats_meta`) when creating a table with foreign keys [#53652](https://github.com/pingcap/tidb/issues/53652) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the query might return incorrect results instead of an error after being killed [#50089](https://github.com/pingcap/tidb/issues/50089) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the issue that the statistics synchronous loading mechanism might fail unexpectedly under high query concurrency [#52294](https://github.com/pingcap/tidb/issues/52294) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that certain filter conditions in queries might cause the planner module to report an `invalid memory address or nil pointer dereference` error [#53582](https://github.com/pingcap/tidb/issues/53582) [#53580](https://github.com/pingcap/tidb/issues/53580) [#53594](https://github.com/pingcap/tidb/issues/53594) [#53603](https://github.com/pingcap/tidb/issues/53603) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the TiDB synchronously loading statistics mechanism retries to load empty statistics indefinitely and prints the `fail to get stats version for this histogram` log [#52657](https://github.com/pingcap/tidb/issues/52657) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the `TIMESTAMPADD()` function goes into an infinite loop when the first argument is `month` and the second argument is negative [#54908](https://github.com/pingcap/tidb/issues/54908) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that TiDB might crash when `tidb_mem_quota_analyze` is enabled and the memory used by updating statistics exceeds the limit [#52601](https://github.com/pingcap/tidb/issues/52601) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that `duplicate entry` might occur when adding unique indexes [#56161](https://github.com/pingcap/tidb/issues/56161) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the query latency of stale reads increases, caused by information schema cache misses [#53428](https://github.com/pingcap/tidb/issues/53428) @[crazycs520](https://github.com/crazycs520)
