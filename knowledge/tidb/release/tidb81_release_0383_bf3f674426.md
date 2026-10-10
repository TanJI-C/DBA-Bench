# TiDB 6.5.11 bug fixes for TiDB

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.11.md`
- Source Title: `TiDB 6.5.11 Release Notes`
- Source Heading Path: `TiDB 6.5.11 Release Notes > Bug fixes`
- Source Line Ranges: `42-78`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dm`
- Topic Tags: `release-notes`, `bug-fixes`, `memory-tracking`, `cte`, `join`, `plan-cache`, `ddl`, `replication`, `information-schema`, `panic-fix`, `query-correctness`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0383_bf3f674426`
- Source ID: `tidb-docs-8.1:releases/release-6.5.11.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `70526a261f34a9bf4fba2f819ca0640a9e8dbb73f68b2173b10f15729cbe63c5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.11#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.11.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.11 bug fixes affecting memory tracking, recursive CTE, joins, plan cache, DDL, query correctness, INFORMATION_SCHEMA behavior, or panic and cleanup issues.
- Retrieval Keywords: TiDB 6.5.11 Release Notes, Bug fixes, recursive CTE, incorrectly tracks memory usage, PipelinedWindow, Apply, Open method, transactions might be tracked multiple times, memTracker, HashJoin, IndexLookUp, INDEX_HASH_JOIN, DM, max-index-length, GROUP BY, placeholder ?, DECIMAL(0,0), virtual columns, UnionScan, SELECT DISTINCT CAST(col AS DECIMAL), CAST(col AS SIGNED), SELECT ... FOR UPDATE, RANGE partitioned tables, TIMESTAMPADD(), month, negative, auth_socket, Distributed eXecution Framework, DXF, adding indexes, tidb_mem_quota_query, plan cache, metadata locks, mysql.stats_histograms, tot_col_size, information_schema.columns, warning 1356, SELECT ... WHERE ... ORDER BY ..., INFORMATION_SCHEMA.STATISTICS, SUB_PART, INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY, StreamAggExec, groupOffset, Sort operator spills, IndexNestedLoopHashJoin, SHOW COLUMNS, nested generated columns
- Follow-up Guidance: The chunk also identifies a DM-related replication fix where table replication fails when the replicated table index length exceeds `max-index-length`.
- Classification Note: This is a self-managed TiDB release-notes bug-fix chunk focused primarily on TiDB issues, with DM listed as a related component because one fix concerns table replication from DM.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that the recursive CTE operator incorrectly tracks memory usage [#54181](https://github.com/pingcap/tidb/issues/54181) @[guo-shaoge](https://github.com/guo-shaoge)
    - Reset the parameters in the `Open` method of `PipelinedWindow` to fix the unexpected error that occurs when the `PipelinedWindow` is used as a child node of `Apply` due to the reuse of previous parameter values caused by repeated opening and closing operations [#53600](https://github.com/pingcap/tidb/issues/53600) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that the memory used by transactions might be tracked multiple times [#53984](https://github.com/pingcap/tidb/issues/53984) @[ekexium](https://github.com/ekexium)
    - Fix the issue of abnormally high memory usage caused by `memTracker` not being detached when the `HashJoin` or `IndexLookUp` operator is the driven side sub-node of the `Apply` operator [#54005](https://github.com/pingcap/tidb/issues/54005) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that `INDEX_HASH_JOIN` cannot exit properly when SQL is abnormally interrupted [#54688](https://github.com/pingcap/tidb/issues/54688) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that table replication fails when the index length of the table replicated from DM exceeds the maximum length specified by `max-index-length` [#55138](https://github.com/pingcap/tidb/issues/55138) @[lance6716](https://github.com/lance6716)
    - Fix the issue that indirect placeholder `?` references in a `GROUP BY` statement cannot find columns [#53872](https://github.com/pingcap/tidb/issues/53872) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the illegal column type `DECIMAL(0,0)` can be created in some cases [#53779](https://github.com/pingcap/tidb/issues/53779) @[tangenta](https://github.com/tangenta)
    - Fix the issue that predicates cannot be pushed down properly when the filter condition of a SQL query contains virtual columns and the execution condition contains `UnionScan` [#54870](https://github.com/pingcap/tidb/issues/54870) @[qw4990](https://github.com/qw4990)
    - Fix the issue that executing the `SELECT DISTINCT CAST(col AS DECIMAL), CAST(col AS SIGNED) FROM ...` query might return incorrect results [#53726](https://github.com/pingcap/tidb/issues/53726) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue of reusing wrong point get plans for `SELECT ... FOR UPDATE` [#54652](https://github.com/pingcap/tidb/issues/54652) @[qw4990](https://github.com/qw4990)
    - Fix the issue that RANGE partitioned tables that are not strictly self-incrementing can be created [#54829](https://github.com/pingcap/tidb/issues/54829) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the `TIMESTAMPADD()` function goes into an infinite loop when the first argument is `month` and the second argument is negative [#54908](https://github.com/pingcap/tidb/issues/54908) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that TiDB fails to reject unauthenticated user connections in some cases when using the `auth_socket` authentication plugin [#54031](https://github.com/pingcap/tidb/issues/54031) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the network partition during adding indexes using the Distributed eXecution Framework (DXF) might cause inconsistent data indexes [#54897](https://github.com/pingcap/tidb/issues/54897) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the query might get stuck when terminated because the memory usage exceeds the limit set by `tidb_mem_quota_query` [#55042](https://github.com/pingcap/tidb/issues/55042) @[yibin87](https://github.com/yibin87)
    - Fix the issue that improper use of metadata locks might lead to writing anomalous data when using the plan cache under certain circumstances [#53634](https://github.com/pingcap/tidb/issues/53634) @[zimulala](https://github.com/zimulala)
    - Fix the issue that recursive CTE queries might result in invalid pointers [#54449](https://github.com/pingcap/tidb/issues/54449) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the `tot_col_size` column in the `mysql.stats_histograms` table might be a negative number [#55126](https://github.com/pingcap/tidb/issues/55126) @[qw4990](https://github.com/qw4990)
    - Fix the issue that obtaining the column information using `information_schema.columns` returns warning 1356 when a subquery is used as a column definition in a view definition [#54343](https://github.com/pingcap/tidb/issues/54343) @[lance6716](https://github.com/lance6716)
    - Fix the issue that TiDB reports an error in the log when closing the connection in some cases [#53689](https://github.com/pingcap/tidb/issues/53689) @[jackysp](https://github.com/jackysp)
    - Fix the issue that the performance of the `SELECT ... WHERE ... ORDER BY ...` statement execution is poor in some cases [#54969](https://github.com/pingcap/tidb/issues/54969) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the `SUB_PART` value in the `INFORMATION_SCHEMA.STATISTICS` table is `NULL` [#55812](https://github.com/pingcap/tidb/issues/55812) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the query might return incorrect results instead of an error after being killed [#50089](https://github.com/pingcap/tidb/issues/50089) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the issue that querying the `INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY` table might cause TiDB to panic [#54324](https://github.com/pingcap/tidb/issues/54324) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that empty `groupOffset` in `StreamAggExec` might cause TiDB to panic [#53867](https://github.com/pingcap/tidb/issues/53867) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that disk files might not be deleted after the `Sort` operator spills and a query error occurs [#55061](https://github.com/pingcap/tidb/issues/55061) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the data race issue in `IndexNestedLoopHashJoin` [#49692](https://github.com/pingcap/tidb/issues/49692) @[solotzg](https://github.com/solotzg)
    - Fix the issue that an error occurs when using `SHOW COLUMNS` to view columns in a view [#54964](https://github.com/pingcap/tidb/issues/54964) @[lance6716](https://github.com/lance6716)
    - Fix the issue that an error occurs when a DML statement contains nested generated columns [#53967](https://github.com/pingcap/tidb/issues/53967) @[wjhuang2016](https://github.com/wjhuang2016)

+ TiKV
