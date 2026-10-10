# Bug fixes for TiDB in 6.3.0 release notes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.3.0.md`
- Source Title: `TiDB 6.3.0 Release Notes`
- Source Heading Path: `TiDB 6.3.0 Release Notes > Bug fixes`
- Source Line Ranges: `333-370`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `dashboard`, `sql`, `tiflash`
- Topic Tags: `bug-fixes`, `privileges`, `system-variables`, `information-schema`, `json`, `ddl`, `flashback`, `mysql-compatibility`, `transactions`, `optimizer`, `promql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0344_22fa0cf7c5`
- Source ID: `tidb-docs-8.1:releases/release-6.3.0.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66e0febefe2febd58c16a0e171930c7cbfbf06fa6333538dafffc03d7700a08d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.3.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.3.0 bug fixes related to privileges, system variables, INFORMATION_SCHEMA, JSON and MySQL compatibility, DDL and FLASHBACK TABLE behavior, transactions, optimizer errors such as `Can't find column`, or incorrect `PromQL` in the release notes.
- Retrieval Keywords: TiDB 6.3.0 Bug fixes, release-6.3.0 TiDB bug fixes, PREPARE statements privilege check skipped, #35784, tidb_enable_noop_variable WARN, #36647, INFORMATION_SCHEMA.COLUMNS ORDINAL_POSITION expression index, #31200, timestamp larger than MAXINT32, #31585, enterprise plugin TiDB server cannot be started, #37319, SHOW CREATE PLACEMENT POLICY incorrect output, #37526, EXCHANGE PARTITION temporary tables, #37201, INFORMATION_SCHEMA.TIKV_REGION_STATUS incorrect result, EXPLAIN query on views does not check privileges, #34326, JSON null cannot be updated to NULL, #37852, row_count of DDL jobs inaccurate, #25968, FLASHBACK TABLE does not work properly, #37386, prepared statement flags typical MySQL protocol, #36731, INFORMATION_SCHEMA.VARIABLES_INFO security enhanced mode SEM, #37586, string to string cast UNION, #31678, dynamic mode partitioned tables TiFlash wrong result, #37254, binary strings and JSON incompatible with MySQL, #31918, #25053, JSON_OBJECTAGG JSON_ARRAYAGG binary values, #25053, JSON opaque values panic, #37315, single precision float JSON aggregation functions, #37287, UNION unexpected empty result, #36903, castRealAsTime inconsistent with MySQL, #37462, pessimistic DML lock non-unique index keys, #36235, auto-commit change affects transaction commit behaviours, #36581, EXPLAIN ANALYZE DML executors transaction commit finishes, #37373, UPDATE statements projection eliminated Can't find column, #37568, Join Reorder Outer Join condition push down, #37238, IN and NOT IN subqueries Can't find column, #37032, UPDATE statement CTE Can't find column, #35758, incorrect PromQL, #35856
- Follow-up Guidance: The source groups these items under the TiDB subsection of the 6.3.0 release notes bug fixes.
- Classification Note: This chunk is classified as a self-managed TiDB release-note bug-fix section because the official content is a list of TiDB issues fixed in version 6.3.0.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that the privilege check is skipped for `PREPARE` statements [#35784](https://github.com/pingcap/tidb/issues/35784) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the system variable `tidb_enable_noop_variable` can be set to `WARN` [#36647](https://github.com/pingcap/tidb/issues/36647) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that when an expression index is defined, the `ORDINAL_POSITION` column of the `INFORMATION_SCHEMA.COLUMNS` table might be incorrect [#31200](https://github.com/pingcap/tidb/issues/31200) @[bb7133](https://github.com/bb7133)
    - Fix the issue that TiDB does not report an error when the timestamp is larger than `MAXINT32` [#31585](https://github.com/pingcap/tidb/issues/31585) @[bb7133](https://github.com/bb7133)
    - Fix the issue that TiDB server cannot be started when the enterprise plugin is used [#37319](https://github.com/pingcap/tidb/issues/37319) @[xhebox](https://github.com/xhebox)
    - Fix the incorrect output of `SHOW CREATE PLACEMENT POLICY` [#37526](https://github.com/pingcap/tidb/issues/37526) @[xhebox](https://github.com/xhebox)
    - Fix the unexpected `EXCHANGE PARTITION` behaviors with temporary tables [#37201](https://github.com/pingcap/tidb/issues/37201) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that querying `INFORMATION_SCHEMA.TIKV_REGION_STATUS` returns an incorrect result @[zimulala](https://github.com/zimulala)
    - Fix the issue that the `EXPLAIN` query on views does not check privileges [#34326](https://github.com/pingcap/tidb/issues/34326) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that JSON `null` cannot be updated to `NULL` [#37852](https://github.com/pingcap/tidb/issues/37852) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that `row_count` of DDL jobs is inaccurate [#25968](https://github.com/pingcap/tidb/issues/25968) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that `FLASHBACK TABLE` does not work properly [#37386](https://github.com/pingcap/tidb/issues/37386) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue of failing to handle `prepared` statement flags in the typical MySQL protocol [#36731](https://github.com/pingcap/tidb/issues/36731) @[dveeden](https://github.com/dveeden)
    - Fix the issue of incorrect TiDB status that might appear on startup in some extreme cases [#36791](https://github.com/pingcap/tidb/issues/36791) @[xhebox](https://github.com/xhebox)
    - Fix the issue that `INFORMATION_SCHEMA.VARIABLES_INFO` does not comply with security enhanced mode (SEM) [#37586](https://github.com/pingcap/tidb/issues/37586) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Fix the issue that casting string to string goes wrong in queries with `UNION` [#31678](https://github.com/pingcap/tidb/issues/31678) @[cbcwestwolf](https://github.com/cbcwestwolf)
    - Fix the wrong result that occurs when enabling dynamic mode in partitioned tables for TiFlash [#37254](https://github.com/pingcap/tidb/issues/37254) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the cast and comparison between binary strings and JSON in TiDB are incompatible with MySQL [#31918](https://github.com/pingcap/tidb/issues/31918) [#25053](https://github.com/pingcap/tidb/issues/25053) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that `JSON_OBJECTAGG` and `JSON_ARRAYAGG` in TiDB are not compatible with MySQL on binary values [#25053](https://github.com/pingcap/tidb/issues/25053) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the comparison between JSON opaque values causes panic [#37315](https://github.com/pingcap/tidb/issues/37315) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the single precision float cannot be used in JSON aggregation functions [#37287](https://github.com/pingcap/tidb/issues/37287) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the `UNION` operator might return unexpected empty result [#36903](https://github.com/pingcap/tidb/issues/36903) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the result of the `castRealAsTime` expression is inconsistent with MySQL [#37462](https://github.com/pingcap/tidb/issues/37462) @[mengxin9014](https://github.com/mengxin9014)
    - Fix the issue that pessimistic DML operations lock non-unique index keys [#36235](https://github.com/pingcap/tidb/issues/36235) @[ekexium](https://github.com/ekexium)
    - Fix the issue that `auto-commit` change affects transaction commit behaviours [#36581](https://github.com/pingcap/tidb/issues/36581) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the issue that the `EXPLAIN ANALYZE` statement with DML executors might return result before the transaction commit finishes [#37373](https://github.com/pingcap/tidb/issues/37373) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the issue that the UPDATE statements incorrectly eliminate the projection in some cases, which causes the `Can't find column` error  [#37568](https://github.com/pingcap/tidb/issues/37568) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that the Join Reorder operation will mistakenly push down its Outer Join condition [#37238](https://github.com/pingcap/tidb/issues/37238) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that the `IN` and `NOT IN` subqueries in some patterns report the `Can't find column` error [#37032](https://github.com/pingcap/tidb/issues/37032) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that `Can't find column` is reported if an `UPDATE` statement contains common table expressions (CTE) [#35758](https://github.com/pingcap/tidb/issues/35758) @[AilinKid](https://github.com/AilinKid)
    - Fix incorrect `PromQL` [#35856](https://github.com/pingcap/tidb/issues/35856) @[Defined2014](https://github.com/Defined2014)

+ TiKV
