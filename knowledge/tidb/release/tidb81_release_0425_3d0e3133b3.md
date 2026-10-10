# TiDB 6.6.0 bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes > Bug fixes`
- Source Line Ranges: `503-542`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`
- Topic Tags: `bug-fixes`, `ddl`, `statistics`, `ttl`, `indexes`, `transactions`, `mysql-compatibility`, `resource-management`, `slow-query-log`, `metadata-locks`, `auto-increment`, `json`, `authentication`, `virtual-tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0425_3d0e3133b3`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `31e3db4de06438b02e15df6fe39382cb33e274c1703cff87a136e9a2fdbe5bfd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.6.0 bug fix notes for issues involving DDL, statistics, TTL, indexes, transactions, MDL, authentication, JSON, auto-increment, slow query log, or virtual table queries.
- Retrieval Keywords: TiDB 6.6.0 bug fixes, #39336 incorrect datetime statistics collection task fails, #38189 stats_meta is not created following table creation, #24427 frequent write conflicts transactions DDL data backfill, #39641 index cannot be created for an empty table using ingest mode, #39713 wait_ts in the slow query log same for different SQL statements within the same transaction, #39570 Assertion Failed adding a column during deleting a row record, #39643 not a DDL owner modifying a column type, #38950 AUTO_INCREMENT exhaustion no error when inserting a row, #39784 Unknown column creating an expression index, #39826 data cannot be inserted into a renamed table generated expression includes table name, #40192 INSERT ignore default values column is write-only, #40546 resources are not released when disabling the resource management module, #40109 TTL tasks cannot trigger statistics updates in time, #40158 NULL values constructing key ranges unexpected data is read, #40164 MODIFY COLUMN also changes the default value illegal values are written, #38436 adding index operation inefficient invalid Region cache many Regions, #40584 data race allocating auto-increment IDs, #40683 not operator in JSON incompatible with MySQL, #40352 concurrent view DDL operations to be blocked, #40620 data inconsistency concurrently executing DDL statements modify columns of partitioned tables, #40831 Malformed packet caching_sha2_password without specifying a password, #40456 TTL task fails primary key contains an ENUM column, #40838 mysql.tidb_mdl_view DDL operations blocked by MDL cannot be queried, #40970 data race during DDL ingestion, #41043 TTL tasks might delete some data incorrectly after the time zone changes, #39806 JSON_OBJECT might report an error, #40408 TiDB might deadlock during initialization, #40979 system variables incorrectly modified due to memory reuse, #40464 unique index created in the ingest mode data might be inconsistent with the index, #40484 truncate operations cannot be blocked by MDL truncating the same table concurrently, #40591 SHOW PRIVILEGES returns an incomplete privilege list, #40592 TiDB panics when adding a unique index, #40430 ADMIN RECOVER might cause the index data to be corrupted, #40130 CAST expression in the expression index query might fail, #40217 unique index might still produce duplicate data, #39605 PD OOM large number of Regions virtual tables Prepare Execute table ID cannot be pushed down
- Follow-up Guidance: The source lists specific TiDB 6.6.0 fixes including exact errors, statements, tables, and features such as `mysql.tidb_mdl_view`, `AUTO_INCREMENT`, `JSON_OBJECT`, `SHOW PRIVILEGES`, `ADMIN RECOVER`, `Prepare`, and `Execute`.
- Classification Note: This chunk is classified as a TiDB release bug-fix summary because the official content enumerates resolved defects in TiDB 6.6.0, including one fix that references PD behavior during virtual table queries.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that a statistics collection task fails due to an incorrect `datetime` value [#39336](https://github.com/pingcap/tidb/issues/39336) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix the issue that `stats_meta` is not created following table creation [#38189](https://github.com/pingcap/tidb/issues/38189) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix frequent write conflicts in transactions when performing DDL data backfill [#24427](https://github.com/pingcap/tidb/issues/24427) @[mjonss](https://github.com/mjonss)
    - Fix the issue that sometimes an index cannot be created for an empty table using ingest mode [#39641](https://github.com/pingcap/tidb/issues/39641) @[tangenta](https://github.com/tangenta)
    - Fix the issue that `wait_ts` in the slow query log is the same for different SQL statements within the same transaction [#39713](https://github.com/pingcap/tidb/issues/39713) @[TonsnakeLin](https://github.com/TonsnakeLin)
    - Fix the issue that the `Assertion Failed` error is reported when adding a column during the process of deleting a row record [#39570](https://github.com/pingcap/tidb/issues/39570) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the `not a DDL owner` error is reported when modifying a column type [#39643](https://github.com/pingcap/tidb/issues/39643) @[zimulala](https://github.com/zimulala)
    - Fix the issue that no error is reported when inserting a row after exhaustion of the auto-increment values of the `AUTO_INCREMENT` column [#38950](https://github.com/pingcap/tidb/issues/38950) @[Dousir9](https://github.com/Dousir9)
    - Fix the issue that the `Unknown column` error is reported when creating an expression index [#39784](https://github.com/pingcap/tidb/issues/39784) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that data cannot be inserted into a renamed table when the generated expression includes the name of this table [#39826](https://github.com/pingcap/tidb/issues/39826) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the `INSERT ignore` statement cannot fill in default values when the column is write-only [#40192](https://github.com/pingcap/tidb/issues/40192) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that resources are not released when disabling the resource management module [#40546](https://github.com/pingcap/tidb/issues/40546) @[zimulala](https://github.com/zimulala)
    - Fix the issue that TTL tasks cannot trigger statistics updates in time [#40109](https://github.com/pingcap/tidb/issues/40109) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that unexpected data is read because TiDB improperly handles `NULL` values when constructing key ranges [#40158](https://github.com/pingcap/tidb/issues/40158) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that illegal values are written to a table when the `MODIFY COLUMN` statement also changes the default value of a column [#40164](https://github.com/pingcap/tidb/issues/40164) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the adding index operation is inefficient due to invalid Region cache when there are many Regions in a table [#38436](https://github.com/pingcap/tidb/issues/38436) @[tangenta](https://github.com/tangenta)
    - Fix data race occurred in allocating auto-increment IDs [#40584](https://github.com/pingcap/tidb/issues/40584) @[Dousir9](https://github.com/Dousir9)
    - Fix the issue that the implementation of the not operator in JSON is incompatible with the implementation in MySQL [#40683](https://github.com/pingcap/tidb/issues/40683) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that concurrent view might cause DDL operations to be blocked [#40352](https://github.com/pingcap/tidb/issues/40352) @[zeminzhou](https://github.com/zeminzhou)
    - Fix data inconsistency caused by concurrently executing DDL statements to modify columns of partitioned tables [#40620](https://github.com/pingcap/tidb/issues/40620) @[mjonss](https://github.com/mjonss) @[mjonss](https://github.com/mjonss)
    - Fix the issue that "Malformed packet" is reported when using `caching_sha2_password` for authentication without specifying a password [#40831](https://github.com/pingcap/tidb/issues/40831) @[dveeden](https://github.com/dveeden)
    - Fix the issue that a TTL task fails if the primary key of the table contains an `ENUM` column [#40456](https://github.com/pingcap/tidb/issues/40456) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that some DDL operations blocked by MDL cannot be queried in `mysql.tidb_mdl_view` [#40838](https://github.com/pingcap/tidb/issues/40838) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that data race might occur during DDL ingestion [#40970](https://github.com/pingcap/tidb/issues/40970) @[tangenta](https://github.com/tangenta)
    - Fix the issue that TTL tasks might delete some data incorrectly after the time zone changes [#41043](https://github.com/pingcap/tidb/issues/41043) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that `JSON_OBJECT` might report an error in some cases [#39806](https://github.com/pingcap/tidb/issues/39806) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that TiDB might deadlock during initialization [#40408](https://github.com/pingcap/tidb/issues/40408) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the value of system variables might be incorrectly modified in some cases due to memory reuse [#40979](https://github.com/pingcap/tidb/issues/40979) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that data might be inconsistent with the index when a unique index is created in the ingest mode [#40464](https://github.com/pingcap/tidb/issues/40464) @[tangenta](https://github.com/tangenta)
    - Fix the issue that some truncate operations cannot be blocked by MDL when truncating the same table concurrently [#40484](https://github.com/pingcap/tidb/issues/40484) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the `SHOW PRIVILEGES` statement returns an incomplete privilege list [#40591](https://github.com/pingcap/tidb/issues/40591) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Fix the issue that TiDB panics when adding a unique index [#40592](https://github.com/pingcap/tidb/issues/40592) @[tangenta](https://github.com/tangenta)
    - Fix the issue that executing the `ADMIN RECOVER` statement might cause the index data to be corrupted [#40430](https://github.com/pingcap/tidb/issues/40430) @[xiongjiwei](https://github.com/xiongjiwei)
    - Fix the issue that a query might fail when the queried table contains a `CAST` expression in the expression index [#40130](https://github.com/pingcap/tidb/issues/40130) @[xiongjiwei](https://github.com/xiongjiwei)
    - Fix the issue that a unique index might still produce duplicate data in some cases [#40217](https://github.com/pingcap/tidb/issues/40217) @[tangenta](https://github.com/tangenta)
    - Fix the PD OOM issue when there is a large number of Regions but the table ID cannot be pushed down when querying some virtual tables using `Prepare` or `Execute` [#39605](https://github.com/pingcap/tidb/issues/39605) @[djshow832](https://github.com/djshow832)
