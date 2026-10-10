# TiDB bug fixes in 7.5.1

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.1.md`
- Source Title: `TiDB 7.5.1 Release Notes`
- Source Heading Path: `TiDB 7.5.1 Release Notes > Bug fixes`
- Source Line Ranges: `115-149`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tiflash`, `shared`
- Topic Tags: `bug-fixes`, `sql-execution`, `query-optimizer`, `union`, `order-by`, `limit`, `mpp`, `ddl`, `transactions`, `memory-management`, `panic`, `statistics`, `auto-increment`, `hints`, `partitioning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0527_dd64e8133d`
- Source ID: `tidb-docs-8.1:releases/release-7.5.1.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `85f5c68095efd6130790f77711d4216c75a78ee7c7e8b8853dbda75278683ece`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.1#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.1.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.5.1 bug-fix notes for SQL execution, optimizer, MPP, DDL, transaction, panic, memory, statistics, auto-increment, hints, or partition-related issues.
- Retrieval Keywords: TiDB 7.5.1 Release Notes, Bug fixes, UNIQUE index lookup ORDER BY error, #49920, LIMIT multi-level nested UNION ineffective, #49874, COUNT(INT) MPP incorrect, #48643, ENUM SET parsing invalid values SQL statement errors, #49487, invalid memory address or nil pointer dereference, #42739, UNION ALL DUAL first subnode error, #48755, common hints do not take effect in UNION ALL, #50068, graceful shutdown panic, #36793, Daylight Saving Time displayed incorrectly, #49586, CALIBRATE RESOURCE relies on Prometheus data, #49174, hints cannot be used in REPLACE INTO, #34325, GROUP_CONCAT(ORDER BY) returns errors, #49986, audit logging enterprise plugin consumes significant resources, #49273, inconsistent metadata for tables old interfaces, #49751, tidb_enable_collect_execution_info coprocessor cache panic, #48212, ALTER TABLE ... LAST PARTITION DATETIME fails, #48814, COM_STMT_EXECUTE COMMIT ROLLBACK timed out transactions, #49151, histogram boundary contains NULL readable strings, #49823, CTEs get stuck when memory limit is exceeded, #49096, Distributed eXecution Framework DXF ADD INDEX DDL Owner network isolated inconsistent data, #49773, AUTO_ID_CACHE=1 auto-increment concurrent conflicts, #50519, fatal error: concurrent map writes Apply operator, #50347, DDL jobID restored to 0 panic, #46296, STREAM_AGG incorrectly handling CI wrong query results, #49902, OOM large number of tables or partitions, #50077, LEADING hint does not take effect in UNION ALL, #50067, LIMIT and OPRDERBY invalid in nested UNION queries, #49377, IndexHashJoin stuck tidb_mem_quota_query, #49033, ENUM SET constant propagation wrong query results, #49440, SELECT INTO OUTFILE PREPARE success instead of error, #49166, IndexMerge enforced sorting optimizer hints ineffective, #49605, AUTO_ID_CACHE=1 gRPC client leaks, #48869, sql_mode = '' truncation INSERT still reports an error, #49369, LIKE _ wildcard trailing spaces incorrect query results, #48983, ADMIN CHECK tidb_mem_quota_query ERROR 8175, #49258
- Follow-up Guidance: 
- Classification Note: The official content is a TiDB 7.5.1 release-note bug-fix list covering TiDB issues in SQL execution, optimizer behavior, MPP, DDL, transactions, memory management, statistics, auto-increment, hints, and partitioning.

## Official Source Content

- Fix the issue that executing `UNIQUE` index lookup with an `ORDER BY` clause might cause an error [#49920](https://github.com/pingcap/tidb/issues/49920) @[jackysp](https://github.com/jackysp)
    - Fix the issue that `LIMIT` in multi-level nested `UNION` queries might become ineffective [#49874](https://github.com/pingcap/tidb/issues/49874) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the result of `COUNT(INT)` calculated by MPP might be incorrect [#48643](https://github.com/pingcap/tidb/issues/48643) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that parsing invalid values of `ENUM` or `SET` types would directly cause SQL statement errors [#49487](https://github.com/pingcap/tidb/issues/49487) @[winoros](https://github.com/winoros)
    - Fix the issue that TiDB panics and reports an error `invalid memory address or nil pointer dereference` [#42739](https://github.com/pingcap/tidb/issues/42739) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Fix the issue that executing `UNION ALL` with the DUAL table as the first subnode might cause an error [#48755](https://github.com/pingcap/tidb/issues/48755) @[winoros](https://github.com/winoros)
    - Fix the issue that common hints do not take effect in `UNION ALL` statements [#50068](https://github.com/pingcap/tidb/issues/50068) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that TiDB server might panic during graceful shutdown [#36793](https://github.com/pingcap/tidb/issues/36793) @[bb7133](https://github.com/bb7133)
    - Fix the issue that Daylight Saving Time is displayed incorrectly in some time zones [#49586](https://github.com/pingcap/tidb/issues/49586) @[overvenus](https://github.com/overvenus)
    - Fix the issue that static `CALIBRATE RESOURCE` relies on the Prometheus data [#49174](https://github.com/pingcap/tidb/issues/49174) @[glorv](https://github.com/glorv)
    - Fix the issue that hints cannot be used in `REPLACE INTO` statements [#34325](https://github.com/pingcap/tidb/issues/34325) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that executing queries containing the `GROUP_CONCAT(ORDER BY)` syntax might return errors [#49986](https://github.com/pingcap/tidb/issues/49986) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that TiDB server might consume a significant amount of resources when the enterprise plugin for audit logging is used [#49273](https://github.com/pingcap/tidb/issues/49273) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that using old interfaces might cause inconsistent metadata for tables [#49751](https://github.com/pingcap/tidb/issues/49751) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that disabling `tidb_enable_collect_execution_info` causes the coprocessor cache to panic [#48212](https://github.com/pingcap/tidb/issues/48212) @[you06](https://github.com/you06)
    - Fix the issue that executing `ALTER TABLE ... LAST PARTITION` fails when the partition column type is `DATETIME` [#48814](https://github.com/pingcap/tidb/issues/48814) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that the `COMMIT` or `ROLLBACK` operation executed through `COM_STMT_EXECUTE` fails to terminate transactions that have timed out [#49151](https://github.com/pingcap/tidb/issues/49151) @[zyguan](https://github.com/zyguan)
    - Fix the issue that histogram statistics might not be parsed into readable strings when the histogram boundary contains `NULL` [#49823](https://github.com/pingcap/tidb/issues/49823) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that queries containing common table expressions (CTEs) unexpectedly get stuck when the memory limit is exceeded [#49096](https://github.com/pingcap/tidb/issues/49096) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that data is inconsistent under the TiDB Distributed eXecution Framework (DXF) when executing `ADD INDEX` after the DDL Owner is network isolated [#49773](https://github.com/pingcap/tidb/issues/49773) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the auto-increment ID allocation reports an error due to concurrent conflicts when using an auto-increment column with `AUTO_ID_CACHE=1` [#50519](https://github.com/pingcap/tidb/issues/50519) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that TiDB might panic when a query contains the Apply operator and the `fatal error: concurrent map writes` error occurs [#50347](https://github.com/pingcap/tidb/issues/50347) @[SeaRise](https://github.com/SeaRise)
    - Fix the TiDB node panic issue that occurs when DDL `jobID` is restored to 0 [#46296](https://github.com/pingcap/tidb/issues/46296) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that query results are incorrect due to `STREAM_AGG()` incorrectly handling CI [#49902](https://github.com/pingcap/tidb/issues/49902) @[wshwsh12](https://github.com/wshwsh12)
    - Mitigate the issue that TiDB nodes might encounter OOM errors when dealing with a large number of tables or partitions [#50077](https://github.com/pingcap/tidb/issues/50077) @[zimulala](https://github.com/zimulala)
    - Fix the issue that the `LEADING` hint does not take effect in `UNION ALL` statements [#50067](https://github.com/pingcap/tidb/issues/50067) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that `LIMIT` and `OPRDERBY` might be invalid in nested `UNION` queries [#49377](https://github.com/pingcap/tidb/issues/49377) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that a query containing the IndexHashJoin operator gets stuck when memory exceeds `tidb_mem_quota_query` [#49033](https://github.com/pingcap/tidb/issues/49033) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that TiDB returns wrong query results when processing `ENUM` or `SET` types by constant propagation [#49440](https://github.com/pingcap/tidb/issues/49440) @[winoros](https://github.com/winoros)
    - Fix the issue that executing `SELECT INTO OUTFILE` using the `PREPARE` method incorrectly returns a success message instead of an error [#49166](https://github.com/pingcap/tidb/issues/49166) @[qw4990](https://github.com/qw4990)
    - Fix the issue that enforced sorting might become ineffective when a query uses optimizer hints (such as `STREAM_AGG()`) that enforce sorting and its execution plan contains `IndexMerge` [#49605](https://github.com/pingcap/tidb/issues/49605) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that tables with `AUTO_ID_CACHE=1` might lead to gRPC client leaks when there are a large number of tables [#48869](https://github.com/pingcap/tidb/issues/48869) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that in non-strict mode (`sql_mode = ''`), truncation during executing `INSERT` still reports an error [#49369](https://github.com/pingcap/tidb/issues/49369) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that using the `_` wildcard in `LIKE` when the data contains trailing spaces can result in incorrect query results [#48983](https://github.com/pingcap/tidb/issues/48983) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that executing `ADMIN CHECK` after updating the `tidb_mem_quota_query` system variable returns `ERROR 8175` [#49258](https://github.com/pingcap/tidb/issues/49258) @[tangenta](https://github.com/tangenta)
