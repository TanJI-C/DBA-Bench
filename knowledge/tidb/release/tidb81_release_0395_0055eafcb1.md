# TiDB 6.5.3 bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.3.md`
- Source Title: `TiDB 6.5.3 Release Notes`
- Source Heading Path: `TiDB 6.5.3 Release Notes > Bug fixes`
- Source Line Ranges: `55-91`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `ticdc`, `br`, `tiflash`
- Topic Tags: `release-notes`, `bug-fixes`, `query-correctness`, `cte`, `window-functions`, `partitioned-tables`, `placement-rules`, `ddl`, `stale-read`, `pessimistic-transactions`, `gc`, `ipv6`, `load-data`, `pd-connectivity`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0395_0055eafcb1`
- Source ID: `tidb-docs-8.1:releases/release-6.5.3.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `12feae2b1e5a8b668a502a7c249a64f6982b20e56dd7801745fff7c29663e757`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.3#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.3.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.5.3 bug fixes for query correctness, DDL, placement rules, Stale Read, pessimistic transactions, PD connectivity, IPv6, BR, TiCDC, and LOAD DATA issues.
- Retrieval Keywords: TiDB 6.5.3 bug fixes, min, max query result is incorrect, window functions to TiFlash, query with CTE causes TiDB to hang, runtime error: index out of range, AES_DECRYPT, SHOW PROCESSLIST, TxnStart, PD isolation might block the running DDL, union views and temporary tables with UNION, Placement Rules in partitioned tables, truncating a partition, TiCDC might lose some row changes during table renaming, DDL job history is lost after importing a table using BR, JSON_OBJECT might report an error, system views in IPv6 environment, PD member address changes, AUTO_INCREMENT column will be blocked for a long time, full config reset, SHOW PRIVILEGES returns an incomplete privilege list, ADMIN SHOW DDL JOBS LIMIT returns incorrect results, tidb_auth_token, password complexity check, dynamic pruning mode, Data Truncated warning, MODIFY COLUMN on a partitioned table, incorrect TiDB address in IPv6 environment, CTE results are incorrect when pushing down predicates, non-correlated subqueries, Join Reorder might cause incorrect outer join results, pessimistic transaction is retried, residual pessimistic locks, GC resolves locks, batch cop, Stale Read and PREPARE, assertion failed, LOAD DATA, region data not ready, coprocessor cannot fall back to the leader
- Follow-up Guidance: 
- Classification Note: This is classified as a release bug-fix chunk because it enumerates official TiDB 6.5.3 fixes for previously incorrect behavior, errors, panics, and correctness problems.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that the `min, max` query result is incorrect [#43805](https://github.com/pingcap/tidb/issues/43805) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue of incorrect execution plans when pushing down window functions to TiFlash [#43922](https://github.com/pingcap/tidb/issues/43922) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that the query with CTE causes TiDB to hang [#43749](https://github.com/pingcap/tidb/issues/43749) [#36896](https://github.com/pingcap/tidb/issues/36896) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that the SQL statement reports the `runtime error: index out of range` error when using the `AES_DECRYPT` expression [#43063](https://github.com/pingcap/tidb/issues/43063) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the `SHOW PROCESSLIST` statement cannot display the TxnStart of the transaction of the statement with a long subquery time [#40851](https://github.com/pingcap/tidb/issues/40851) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that PD isolation might block the running DDL [#44014](https://github.com/pingcap/tidb/issues/44014) [#43755](https://github.com/pingcap/tidb/issues/43755) [#44267](https://github.com/pingcap/tidb/issues/44267) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the TiDB panic issue that occurs when querying union views and temporary tables with `UNION` [#42563](https://github.com/pingcap/tidb/issues/42563) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the behavior issue of Placement Rules in partitioned tables, so that the Placement Rules in deleted partitions can be correctly set and recycled [#44116](https://github.com/pingcap/tidb/issues/44116) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that truncating a partition of a partitioned table might cause the Placement Rule of the partition to become invalid [#44031](https://github.com/pingcap/tidb/issues/44031) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that TiCDC might lose some row changes during table renaming [#43338](https://github.com/pingcap/tidb/issues/43338) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the DDL job history is lost after importing a table using BR [#43725](https://github.com/pingcap/tidb/issues/43725) @[tangenta](https://github.com/tangenta)
    - Fix the issue that `JSON_OBJECT` might report an error in some cases [#39806](https://github.com/pingcap/tidb/issues/39806) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the cluster cannot query some system views in IPv6 environment [#43286](https://github.com/pingcap/tidb/issues/43286) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that when the PD member address changes, allocating ID for the `AUTO_INCREMENT` column will be blocked for a long time [#42643](https://github.com/pingcap/tidb/issues/42643) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that TiDB sends duplicate requests to PD during placement rules recycling, causing numerous `full config reset` entries in the PD log [#33069](https://github.com/pingcap/tidb/issues/33069) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the `SHOW PRIVILEGES` statement returns an incomplete privilege list [#40591](https://github.com/pingcap/tidb/issues/40591) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Fix the issue that `ADMIN SHOW DDL JOBS LIMIT` returns incorrect results [#42298](https://github.com/pingcap/tidb/issues/42298) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Fix the issue that the `tidb_auth_token` user fails to be created when the password complexity check is enabled [#44098](https://github.com/pingcap/tidb/issues/44098) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Fix the issue of not finding the partition during inner join in dynamic pruning mode [#43686](https://github.com/pingcap/tidb/issues/43686) @[mjonss](https://github.com/mjonss)
    - Fix the issue that the `Data Truncated` warning occurs when executing `MODIFY COLUMN` on a partitioned table [#41118](https://github.com/pingcap/tidb/issues/41118) @[mjonss](https://github.com/mjonss)
    - Fix the issue of displaying the incorrect TiDB address in IPv6 environment [#43260](https://github.com/pingcap/tidb/issues/43260) @[nexustar](https://github.com/nexustar)
    - Fix the issue that CTE results are incorrect when pushing down predicates [#43645](https://github.com/pingcap/tidb/issues/43645) @[winoros](https://github.com/winoros)
    - Fix the issue that incorrect results might be returned when using a common table expression (CTE) in statements with non-correlated subqueries [#44051](https://github.com/pingcap/tidb/issues/44051) @[winoros](https://github.com/winoros)
    - Fix the issue that Join Reorder might cause incorrect outer join results [#44314](https://github.com/pingcap/tidb/issues/44314) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that in some extreme cases, when the first statement of a pessimistic transaction is retried, resolving locks on this transaction might affect transaction correctness [#42937](https://github.com/pingcap/tidb/issues/42937) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that in some rare cases, residual pessimistic locks of pessimistic transactions might affect data correctness when GC resolves locks [#43243](https://github.com/pingcap/tidb/issues/43243) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that the scan detail information during the execution of `batch cop` might be inaccurate [#41582](https://github.com/pingcap/tidb/issues/41582) @[you06](https://github.com/you06)
    - Fix the issue that TiDB cannot read data updates when Stale Read and `PREPARE` statements are used at the same time [#43044](https://github.com/pingcap/tidb/issues/43044) @[you06](https://github.com/you06)
    - Fix the issue that an `assertion failed` error might be mistakenly reported when executing the `LOAD DATA` statement [#43849](https://github.com/pingcap/tidb/issues/43849) @[you06](https://github.com/you06)
    - Fix the issue that the coprocessor cannot fall back to the leader when a `region data not ready` error occurs during the use of Stale Read [#43365](https://github.com/pingcap/tidb/issues/43365) @[you06](https://github.com/you06)

+ TiKV
