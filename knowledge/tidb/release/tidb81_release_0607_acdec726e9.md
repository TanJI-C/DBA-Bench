# TiDB 8.1.2 bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.2.md`
- Source Title: `TiDB 8.1.2 Release Notes`
- Source Heading Path: `TiDB 8.1.2 Release Notes > Bug fixes`
- Source Line Ranges: `56-93`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`
- Topic Tags: `bug-fixes`, `ttl`, `plan-cache`, `import-into`, `statistics`, `plan-replayer`, `memory`, `query-execution`, `partition-pruning`, `cte`, `indexing`, `stale-read`, `collation`, `ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0607_acdec726e9`
- Source ID: `tidb-docs-8.1:releases/release-8.1.2.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a5b08f10cd69524267ccb2e96dd678c8f397f755c25d83955295aa054580a8c6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.2.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 8.1.2 bug-fix notes for issues involving TTL, plan cache, IMPORT INTO, statistics, Plan Replayer, memory limits, query cancellation, partition pruning, CTE, indexing, stale reads, collation, DDL, or TiFlash system table queries.
- Retrieval Keywords: TiDB 8.1.2 bug fixes, TTL tasks executed unexpectedly frequently upgrade from v6.5 to v7.5 or later, #56539, metadata locks plan cache anomalous data, #53634, IMPORT INTO stuck Global Sort Region size exceeds 96 MiB, #55374, DUMP STATS histogram upper bound lower bound corrupted JSON, #56083, execution plan bindings multi-table DELETE statement with aliases, #56726, memory leaks in TTL tables, #56934, partition pruning EXTRACT(YEAR FROM col), #54210, Plan Replayer Placement Rules, #54961, tidb_mem_quota_query query terminated stuck, #55042, queries cannot be canceled during cop task construction, #55957, tidb_ttl_delete_worker_count TTL job fail to complete, #55561, CAST explicitly setting the character set, #55677, TTL tasks cannot be canceled write conflict, #56422, IndexNestedLoopHashJoin data race, #49692, groupOffset StreamAggExec panic, #53867, correlated subquery and CTE hang or incorrect results, #55551, index addition retries data index inconsistency, #55808, out of range small display width integer column, #55837, LOAD DATA ... REPLACE INTO data inconsistency, #56408, columnEvaluator runtime error: index out of range, #53713, CTE multiple data consumers illegal memory access, #55881, canceling a TTL task SQL is not killed forcibly, #56511, IMPORT INTO temporary tables panic, #55970, unique index column IS NULL row estimate as 1, #56116, stale reads information schema cache misses query latency, #53428, UPDATE ENUM incorrectly updates values, #56832, Plan Replayer foreign keys, #56456, tidb_ttl_job_enable TTL tasks are not canceled, #57404, UPDATE or DELETE recursive CTE error or not take effect, #55666, INFORMATION_SCHEMA.STATISTICS SUB_PART NULL, #55812, TiFlash system table default timeout too short, #57816, default_collation_for_utf8mb4 SET NAMES, #56439, mysql.tidb_timer manually delete a timer TTL internal coroutine panic, #57112, tidb_ddl_enable_fast_reorg Duplicate entry, #49233
- Follow-up Guidance: The chunk lists the affected statements, variables, tables, and components such as `IMPORT INTO`, `DUMP STATS`, `tidb_mem_quota_query`, `tidb_ttl_delete_worker_count`, `tidb_ttl_job_enable`, `INFORMATION_SCHEMA.STATISTICS`, `mysql.tidb_timer`, and `tidb_ddl_enable_fast_reorg` for more targeted retrieval.
- Classification Note: This is a release-note bug-fix summary for TiDB 8.1.2 focused on the TiDB component, with one item explicitly mentioning TiFlash system table query timeout.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that existing TTL tasks are executed unexpectedly frequently in a cluster that is upgraded from v6.5 to v7.5 or later [#56539](https://github.com/pingcap/tidb/issues/56539) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that improper use of metadata locks might lead to writing anomalous data when using the plan cache under certain circumstances [#53634](https://github.com/pingcap/tidb/issues/53634) @[zimulala](https://github.com/zimulala)
    - Fix the issue that executing `IMPORT INTO` is stuck when Global Sort is enabled and the Region size exceeds 96 MiB [#55374](https://github.com/pingcap/tidb/issues/55374) @[lance6716](https://github.com/lance6716)
    - Fix the issue that the upper bound and lower bound of the histogram are corrupted when `DUMP STATS` is transforming statistics into JSON [#56083](https://github.com/pingcap/tidb/issues/56083) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that execution plan bindings cannot be created for the multi-table `DELETE` statement with aliases [#56726](https://github.com/pingcap/tidb/issues/56726) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue of memory leaks in TTL tables [#56934](https://github.com/pingcap/tidb/issues/56934) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that partition pruning does not work when the partition expression is `EXTRACT(YEAR FROM col)` [#54210](https://github.com/pingcap/tidb/issues/54210) @[mjonss](https://github.com/mjonss)
    - Fix the issue that Plan Replayer might report an error when importing a table structure containing Placement Rules [#54961](https://github.com/pingcap/tidb/issues/54961) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the query might get stuck when terminated because the memory usage exceeds the limit set by `tidb_mem_quota_query` [#55042](https://github.com/pingcap/tidb/issues/55042) @[yibin87](https://github.com/yibin87)
    - Fix the issue that TiDB queries cannot be canceled during cop task construction [#55957](https://github.com/pingcap/tidb/issues/55957) @[yibin87](https://github.com/yibin87)
    - Fix the issue that reducing the value of `tidb_ttl_delete_worker_count` during TTL job execution makes the job fail to complete [#55561](https://github.com/pingcap/tidb/issues/55561) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the `CAST` function does not support explicitly setting the character set [#55677](https://github.com/pingcap/tidb/issues/55677) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that TTL tasks cannot be canceled when there is a write conflict [#56422](https://github.com/pingcap/tidb/issues/56422) @[YangKeao](https://github.com/YangKeao)
    - Fix the data race issue in `IndexNestedLoopHashJoin` [#49692](https://github.com/pingcap/tidb/issues/49692) @[solotzg](https://github.com/solotzg)
    - Fix the issue that empty `groupOffset` in `StreamAggExec` might cause TiDB to panic [#53867](https://github.com/pingcap/tidb/issues/53867) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that TiDB might hang or return incorrect results when executing a query containing a correlated subquery and CTE [#55551](https://github.com/pingcap/tidb/issues/55551) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue of data index inconsistency caused by retries during index addition [#55808](https://github.com/pingcap/tidb/issues/55808) @[lance6716](https://github.com/lance6716)
    - Fix the issue that an `out of range` error might occur when a small display width is specified for a column of the integer type [#55837](https://github.com/pingcap/tidb/issues/55837) @[windtalker](https://github.com/windtalker)
    - Fix the issue that the `LOAD DATA ... REPLACE INTO` operation causes data inconsistency [#56408](https://github.com/pingcap/tidb/issues/56408) @[fzzf678](https://github.com/fzzf678)
    - Fix the issue that `columnEvaluator` cannot identify the column references in the input chunk, which leads to `runtime error: index out of range` when executing SQL statements [#53713](https://github.com/pingcap/tidb/issues/53713) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue of illegal memory access that might occur when a Common Table Expression (CTE) has multiple data consumers and one consumer exits without reading any data [#55881](https://github.com/pingcap/tidb/issues/55881) @[windtalker](https://github.com/windtalker)
    - Fix the issue that when canceling a TTL task, the corresponding SQL is not killed forcibly [#56511](https://github.com/pingcap/tidb/issues/56511) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that TiDB panics when importing temporary tables using the `IMPORT INTO` statement [#55970](https://github.com/pingcap/tidb/issues/55970) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the issue that the optimizer incorrectly estimates the number of rows as 1 when accessing a unique index with the query condition `column IS NULL` [#56116](https://github.com/pingcap/tidb/issues/56116) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the query latency of stale reads increases, caused by information schema cache misses [#53428](https://github.com/pingcap/tidb/issues/53428) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that the `UPDATE` statement incorrectly updates values of the `ENUM` type [#56832](https://github.com/pingcap/tidb/issues/56832) @[xhebox](https://github.com/xhebox)
    - Fix the issue that Plan Replayer might report an error when importing a table structure containing foreign keys [#56456](https://github.com/pingcap/tidb/issues/56456) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that TTL tasks are not canceled after the `tidb_ttl_job_enable` variable is disabled [#57404](https://github.com/pingcap/tidb/issues/57404) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that when an `UPDATE` or `DELETE` statement contains a recursive CTE, the statement might report an error or not take effect [#55666](https://github.com/pingcap/tidb/issues/55666) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that the `SUB_PART` value in the `INFORMATION_SCHEMA.STATISTICS` table is `NULL` [#55812](https://github.com/pingcap/tidb/issues/55812) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the default timeout for querying the TiFlash system table is too short [#57816](https://github.com/pingcap/tidb/issues/57816) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that the value of the `default_collation_for_utf8mb4` variable does not work for the `SET NAMES` statement [#56439](https://github.com/pingcap/tidb/issues/56439) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that TTL internal coroutine might panic when you manually delete a timer in the `mysql.tidb_timer` table [#57112](https://github.com/pingcap/tidb/issues/57112) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that enabling acceleration of `ADD INDEX` and `CREATE INDEX` via `tidb_ddl_enable_fast_reorg` might lead to the `Duplicate entry` error [#49233](https://github.com/pingcap/tidb/issues/49233) @[lance6716](https://github.com/lance6716)
