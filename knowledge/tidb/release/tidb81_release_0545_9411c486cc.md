# TiDB 7.5.5 bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.5.md`
- Source Title: `TiDB 7.5.5 Release Notes`
- Source Heading Path: `TiDB 7.5.5 Release Notes > Bug fixes`
- Source Line Ranges: `47-83`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `shared`
- Topic Tags: `release-notes`, `bug-fixes`, `ddl`, `ttl`, `stale-read`, `import-into`, `auto-increment`, `plan-replayer`, `cte`, `analyze`, `plan-cache`, `global-sort`, `partitioning`, `collation`, `recover-table`, `index-merge`, `upgrade-failures`, `metadata-locks`, `consistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0545_9411c486cc`
- Source ID: `tidb-docs-8.1:releases/release-7.5.5.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a8d6b0336367b8e16d5f9f2f42cbac4f24791aacfb0f4755c834210d23cdb1fa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.5#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.5.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.5 bug fixes affecting DDL, TTL, stale read, IMPORT INTO, CTE, ANALYZE, plan cache, partitioning, recover table, index merge, and upgrade-related issues.
- Retrieval Keywords: TiDB 7.5.5 bug fixes, Reorg DDL tasks, DDL owner node is switched, sql_mode = '', Stats Healthy Distribution, Common Table Expression, CTE, tidb_ttl_job_enable, stale read, IMPORT INTO, AUTO_INCREMENT, ADD INDEX, ANALYZE, Plan Replayer, Placement Rules, foreign keys, mysql_insert_id, metadata locks, plan cache, Global Sort, RANGE COLUMNS, utf8mb4_0900_ai_ci, RECOVER TABLE BY JOB JOB_ID, read_from_storage hint, Index Merge, INDEX_HASH_JOIN, Distributed eXecution Framework, DXF, GC life time is shorter than transaction duration, EXCHANGE PARTITION, failed to load schema diff, tidb_ddl_enable_fast_reorg, new_collations_enabled_on_first_bootstrap
- Follow-up Guidance: The content includes exact SQL and identifier strings such as `IMPORT INTO`, `ADD INDEX`, `ANALYZE`, `RECOVER TABLE BY JOB JOB_ID;`, `read_from_storage`, `INDEX_HASH_JOIN`, `tidb_ttl_job_enable`, and the error `GC life time is shorter than transaction duration`.
- Classification Note: This is classified as a release bug-fix chunk because the official content is the Bug fixes section of the TiDB 7.5.5 release notes focused on TiDB issues.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that TiDB cannot resume Reorg DDL tasks from the previous progress after the DDL owner node is switched [#56506](https://github.com/pingcap/tidb/issues/56506) @[tangenta](https://github.com/tangenta)
    - Fix the issue that invalid `NULL` values can be inserted in non-strict mode (`sql_mode = ''`) [#56381](https://github.com/pingcap/tidb/issues/56381) @[joechenrh](https://github.com/joechenrh)
    - Fix the issue that the data in the **Stats Healthy Distribution** panel of Grafana might be incorrect [#57176](https://github.com/pingcap/tidb/issues/57176) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue of illegal memory access that might occur when a Common Table Expression (CTE) has multiple data consumers and one consumer exits without reading any data [#55881](https://github.com/pingcap/tidb/issues/55881) @[windtalker](https://github.com/windtalker)
    - Fix the issue that existing TTL tasks are executed unexpectedly frequently in a cluster that is upgraded from v6.5 to v7.5 or later [#56539](https://github.com/pingcap/tidb/issues/56539) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that TTL tasks are not canceled after the `tidb_ttl_job_enable` variable is disabled [#57404](https://github.com/pingcap/tidb/issues/57404) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the query latency of stale reads increases, caused by information schema cache misses [#53428](https://github.com/pingcap/tidb/issues/53428) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that stale read does not strictly verify the timestamp of the read operation, resulting in a small probability of affecting the consistency of the transaction when an offset exists between the TSO and the real physical time [#56809](https://github.com/pingcap/tidb/issues/56809) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that the `AUTO_INCREMENT` field is not correctly set after importing data using the `IMPORT INTO` statement [#56476](https://github.com/pingcap/tidb/issues/56476) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the issue that two DDL Owners might exist at the same time [#54689](https://github.com/pingcap/tidb/issues/54689) @[joccau](https://github.com/joccau)
    - Fix the issue that TTL might fail if TiKV is not selected as the storage engine [#56402](https://github.com/pingcap/tidb/issues/56402) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that TiDB does not check the index length limitation when executing `ADD INDEX` [#56930](https://github.com/pingcap/tidb/issues/56930) @[fzzf678](https://github.com/fzzf678)
    - Fix the issue that when canceling a TTL task, the corresponding SQL is not killed forcibly [#56511](https://github.com/pingcap/tidb/issues/56511) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that execution plan bindings cannot be created for the multi-table `DELETE` statement with aliases [#56726](https://github.com/pingcap/tidb/issues/56726) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that when using `ANALYZE` to collect statistics for a table, if the table contains expression indexes of virtually generated columns, the execution reports an error [#57079](https://github.com/pingcap/tidb/issues/57079) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that Plan Replayer might report an error when importing a table structure containing Placement Rules [#54961](https://github.com/pingcap/tidb/issues/54961) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that when parsing a database name in CTE, it returns a wrong database name [#54582](https://github.com/pingcap/tidb/issues/54582) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the `INSERT ... ON DUPLICATE KEY` statement is not compatible with `mysql_insert_id` [#55965](https://github.com/pingcap/tidb/issues/55965) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that improper use of metadata locks might lead to writing anomalous data when using the plan cache under certain circumstances [#53634](https://github.com/pingcap/tidb/issues/53634) @[zimulala](https://github.com/zimulala)
    - Fix the issue that the performance is unstable when adding indexes using Global Sort [#54147](https://github.com/pingcap/tidb/issues/54147) @[tangenta](https://github.com/tangenta)
    - Fix the issue that Plan Replayer might report an error when importing a table structure containing foreign keys [#56456](https://github.com/pingcap/tidb/issues/56456) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that using the `RANGE COLUMNS` partition function and the `utf8mb4_0900_ai_ci` collation at the same time could result in incorrect query results [#57261](https://github.com/pingcap/tidb/issues/57261) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that using subqueries after the `NATURAL JOIN` or `USING` clause might result in errors [#53766](https://github.com/pingcap/tidb/issues/53766) @[dash12653](https://github.com/dash12653)
    - Fix the issue that TTL tasks cannot be canceled when there is a write conflict [#56422](https://github.com/pingcap/tidb/issues/56422) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that if a CTE contains the `ORDER BY`, `LIMIT`, or `SELECT DISTINCT` clause and is referenced by the recursive part of another CTE, it might be incorrectly inlined and result in an execution error [#56603](https://github.com/pingcap/tidb/issues/56603) @[elsa0520](https://github.com/elsa0520)
    - Fix the issue that the `UPDATE` statement incorrectly updates values of the `ENUM` type [#56832](https://github.com/pingcap/tidb/issues/56832) @[xhebox](https://github.com/xhebox)
    - Fix the issue that executing `RECOVER TABLE BY JOB JOB_ID;` might cause TiDB to panic [#55113](https://github.com/pingcap/tidb/issues/55113) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that the `read_from_storage` hint might not take effect when the query has an available Index Merge execution plan [#56217](https://github.com/pingcap/tidb/issues/56217) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that `INDEX_HASH_JOIN` might hang during an abnormal exit [#54055](https://github.com/pingcap/tidb/issues/54055) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that querying system tables related to the Distributed eXecution Framework (DXF) might lead to upgrade failures [#49263](https://github.com/pingcap/tidb/issues/49263) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the issue that the DDL internal transaction error `GC life time is shorter than transaction duration` causes index addition to fail [#57043](https://github.com/pingcap/tidb/issues/57043) @[tangenta](https://github.com/tangenta)
    - Fix the issue that when executing `EXCHANGE PARTITION` and encountering invalid rows, InfoSchema is fully loaded and the error `failed to load schema diff` is reported [#56685](https://github.com/pingcap/tidb/issues/56685) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the issue that collation is not handled correctly when `tidb_ddl_enable_fast_reorg` and `new_collations_enabled_on_first_bootstrap` are enabled, resulting in inconsistent data indexes [#58036](https://github.com/pingcap/tidb/issues/58036) @[djshow832](https://github.com/djshow832)
