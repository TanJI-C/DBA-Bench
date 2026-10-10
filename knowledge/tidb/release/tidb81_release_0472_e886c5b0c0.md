# TiDB bug fixes in 7.1.4

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.4.md`
- Source Title: `TiDB 7.1.4 Release Notes`
- Source Heading Path: `TiDB 7.1.4 Release Notes > Bug fixes`
- Source Line Ranges: `65-98`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `sql`, `tiup`
- Topic Tags: `bug-fixes`, `queries`, `optimizer`, `cte`, `statistics`, `ddl`, `transactions`, `prepared-statements`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0472_e886c5b0c0`
- Source ID: `tidb-docs-8.1:releases/release-7.1.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8086aa08dc1ba883ff281e73d2e9728f34163f295c263a65a0ec3e6603acaa2d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.4 bug fixes related to query errors, wrong results, optimizer hints, CTEs, statistics, DDL sequencing, prepared statements, transaction timeout handling, or rolling upgrade issues.
- Retrieval Keywords: TiDB 7.1.4 bug fixes, release 7.1.4, tidb_multi_statement_mode, DELETE UPDATE index lookup error, type assertion for CTEStorageMap failed, global statistics for partitioned tables, group by constant elimination wrong query results, BIT type decode failures, LIMIT nested UNION ineffective, AUTO_ID_CACHE=1 auto-increment concurrent conflicts, NATURAL JOIN Column ... in from clause is ambiguous, STREAM_AGG(), IndexMerge, GROUP_CONCAT(ORDER BY), multi-valued index empty JSON array incorrect results, UNIQUE index lookup ORDER BY error, UNION ALL hints do not take effect, LEADING hint, IndexHashJoin tidb_mem_quota_query, WITH RECURSIVE UPDATE DELETE incorrect results, fatal error: concurrent map writes, Can't find column ..., ENUM SET constant propagation wrong query results, DDL tasks with dependencies incorrectly sequenced, EXECUTE PREPARE STMT tidb_enable_prepared_plan_cache, COM_STMT_EXECUTE COMMIT ROLLBACK timed out transactions, SELECT INTO OUTFILE PREPARE success message instead of error, tiup cluster upgrade/start panic with PD
- Follow-up Guidance: The source lists specific fixed issues and error phrases for TiDB 7.1.4, including identifiers such as `tidb_mem_quota_query`, `tidb_enable_prepared_plan_cache`, `AUTO_ID_CACHE=1`, `STREAM_AGG()`, `LEADING`, and `COM_STMT_EXECUTE`.
- Classification Note: This chunk is classified as a TiDB release bug-fix summary because the official content is a list of issues fixed in TiDB 7.1.4 across SQL execution, optimizer behavior, statistics, DDL, transactions, prepared statements, and upgrade interactions.

## Official Source Content

- Fix the issue that the `DELETE` and `UPDATE` statements using index lookup might report an error when `tidb_multi_statement_mode` mode is enabled [#50012](https://github.com/pingcap/tidb/issues/50012) @[tangenta](https://github.com/tangenta)
    - Fix the issue that CTE queries might report an error `type assertion for CTEStorageMap failed` during the retry process [#46522](https://github.com/pingcap/tidb/issues/46522) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue of excessive statistical error in constructing statistics caused by Golang's implicit conversion algorithm [#49801](https://github.com/pingcap/tidb/issues/49801) @[qw4990](https://github.com/qw4990)
    - Fix the issue that errors might be returned during the concurrent merging of global statistics for partitioned tables [#48713](https://github.com/pingcap/tidb/issues/48713) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue of wrong query results due to TiDB incorrectly eliminating constant values in `group by` [#38756](https://github.com/pingcap/tidb/issues/38756) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that `BIT` type columns might cause query errors due to decode failures when they are involved in calculations of some functions [#49566](https://github.com/pingcap/tidb/issues/49566) [#50850](https://github.com/pingcap/tidb/issues/50850) [#50855](https://github.com/pingcap/tidb/issues/50855) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that `LIMIT` in multi-level nested `UNION` queries might become ineffective [#49874](https://github.com/pingcap/tidb/issues/49874) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the auto-increment ID allocation reports an error due to concurrent conflicts when using an auto-increment column with `AUTO_ID_CACHE=1` [#50519](https://github.com/pingcap/tidb/issues/50519) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the `Column ... in from clause is ambiguous` error that might occur when a query uses `NATURAL JOIN` [#32044](https://github.com/pingcap/tidb/issues/32044) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that enforced sorting might become ineffective when a query uses optimizer hints (such as `STREAM_AGG()`) that enforce sorting and its execution plan contains `IndexMerge` [#49605](https://github.com/pingcap/tidb/issues/49605) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that query results are incorrect due to `STREAM_AGG()` incorrectly handling CI [#49902](https://github.com/pingcap/tidb/issues/49902) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the goroutine leak issue that might occur when the `HashJoin` operator fails to spill to disk [#50841](https://github.com/pingcap/tidb/issues/50841) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that hints cannot be used in `REPLACE INTO` statements [#34325](https://github.com/pingcap/tidb/issues/34325) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that executing queries containing the `GROUP_CONCAT(ORDER BY)` syntax might return errors [#49986](https://github.com/pingcap/tidb/issues/49986) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that using a multi-valued index to access an empty JSON array might return incorrect results [#50125](https://github.com/pingcap/tidb/issues/50125) @[YangKeao](https://github.com/YangKeao)
    - Fix the goroutine leak issue that occurs when the memory usage of CTE queries exceeds limits [#50337](https://github.com/pingcap/tidb/issues/50337) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that using old interfaces might cause inconsistent metadata for tables [#49751](https://github.com/pingcap/tidb/issues/49751) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that executing `UNIQUE` index lookup with an `ORDER BY` clause might cause an error [#49920](https://github.com/pingcap/tidb/issues/49920) @[jackysp](https://github.com/jackysp)
    - Fix the issue that common hints do not take effect in `UNION ALL` statements [#50068](https://github.com/pingcap/tidb/issues/50068) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that a query containing the IndexHashJoin operator gets stuck when memory exceeds `tidb_mem_quota_query` [#49033](https://github.com/pingcap/tidb/issues/49033) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that `UPDATE` or `DELETE` statements containing `WITH RECURSIVE` CTEs might produce incorrect results [#48969](https://github.com/pingcap/tidb/issues/48969) @[winoros](https://github.com/winoros)
    - Fix the issue that histogram statistics might not be parsed into readable strings when the histogram boundary contains `NULL` [#49823](https://github.com/pingcap/tidb/issues/49823) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that TiDB might panic when a query contains the Apply operator and the `fatal error: concurrent map writes` error occurs [#50347](https://github.com/pingcap/tidb/issues/50347) @[SeaRise](https://github.com/SeaRise)
    - Fix the `Can't find column ...` error that might occur when aggregate functions are used for group calculations [#50926](https://github.com/pingcap/tidb/issues/50926) @[qw4990](https://github.com/qw4990)
    - Fix the issue that TiDB returns wrong query results when processing `ENUM` or `SET` types by constant propagation [#49440](https://github.com/pingcap/tidb/issues/49440) @[winoros](https://github.com/winoros)
    - Fix the issue that the completion times of two DDL tasks with dependencies are incorrectly sequenced [#49498](https://github.com/pingcap/tidb/issues/49498) @[tangenta](https://github.com/tangenta)
    - Fix the issue that TiDB might panic when using the `EXECUTE` statement to execute `PREPARE STMT` after the `tidb_enable_prepared_plan_cache` system variable is enabled and then disabled [#49344](https://github.com/pingcap/tidb/issues/49344) @[qw4990](https://github.com/qw4990)
    - Fix the issue that `LIMIT` and `OPRDERBY` might be invalid in nested `UNION` queries [#49377](https://github.com/pingcap/tidb/issues/49377) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that the `LEADING` hint does not take effect in `UNION ALL` statements [#50067](https://github.com/pingcap/tidb/issues/50067) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the `COMMIT` or `ROLLBACK` operation executed through `COM_STMT_EXECUTE` fails to terminate transactions that have timed out [#49151](https://github.com/pingcap/tidb/issues/49151) @[zyguan](https://github.com/zyguan)
    - Fix the issue that illegal optimizer hints might cause valid hints to be ineffective [#49308](https://github.com/pingcap/tidb/issues/49308) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that Daylight Saving Time is displayed incorrectly in some time zones [#49586](https://github.com/pingcap/tidb/issues/49586) @[overvenus](https://github.com/overvenus)
    - Fix the issue that executing `SELECT INTO OUTFILE` using the `PREPARE` method incorrectly returns a success message instead of an error [#49166](https://github.com/pingcap/tidb/issues/49166) @[qw4990](https://github.com/qw4990)
    - Fix the issue that TiDB might panic when performing a rolling upgrade using `tiup cluster upgrade/start` due to an interaction issue with PD [#50152](https://github.com/pingcap/tidb/issues/50152) @[zimulala](https://github.com/zimulala)
