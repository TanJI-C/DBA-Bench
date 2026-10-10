# TiDB 2.1.12 release overview and TiDB fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.12.md`
- Source Title: `TiDB 2.1.12 Release Notes`
- Source Heading Path: `TiDB 2.1.12 Release Notes | TiDB 2.1.12 Release Notes > TiDB`
- Source Line Ranges: `5-35`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`, `tikv`
- Topic Tags: `release-notes`, `bug-fixes`, `mysql-compatibility`, `charset`, `grant`, `functions`, `type-conversion`, `statistics`, `grpc`, `slow-query`, `partitioned-tables`, `uuid`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0059_2e74ce523a`
- Source ID: `tidb-docs-8.1:releases/release-2.1.12.md#tidb-2-1-12-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `975a6837ffa15791025d63c91184891aebe10aed5a3a56f35052dd0fe5ad09ca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.12#tidb-2-1-12-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.12.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 2.1.12 bug fixes or compatibility changes related to SQL functions, charset changes, GRANT, type conversion, statistics feedback, gRPC message size errors, slow query parsing, partitioned tables, or UUID behavior.
- Retrieval Keywords: TiDB 2.1.12 Release Notes, TiDB 2.1.12, index query feedback, unmatched data types, blob column is changed to the text column, charset altering, GRANT, Duplicate Entry, DAYNAME, MONTHNAME, EXTRACT MONTH 0 value, DECIMAL converted to TIMESTAMP, DECIMAL converted to DATETIME, change the table charset, column charset, decimal to float overflow, grpc: received message larger than max, TiDB and TiKV gRPC, ORDER BY not filtering NULL, UUID duplicate when multiple nodes exist, CAST(-num as datetime), unsigned histogram meets signed ranges, statistics feedback, bigint unsigned primary key, Show Create Table, partitioned tables, GROUP_CONCAT, correlated subqueries, memory table of slow queries, slow query log
- Follow-up Guidance: The source groups these fixes under the TiDB section of the TiDB 2.1.12 release notes.
- Classification Note: This is classified as a TiDB release chunk because the official content lists TiDB 2.1.12 fixes and MySQL compatibility improvements for SQL behavior, statistics, charset handling, gRPC, and query result correctness.

## Official Source Content

# TiDB 2.1.12 Release Notes

Release date: June 13, 2019

TiDB version: 2.1.12

TiDB Ansible version: 2.1.12
## TiDB

- Fix the issue caused by unmatched data types when using the index query feedback [#10755](https://github.com/pingcap/tidb/pull/10755)
- Fix the issue that the blob column is changed to the text column caused by charset altering in some cases [#10745](https://github.com/pingcap/tidb/pull/10745)
- Fix the issue that the `GRANT` operation in the transaction mistakenly reports "Duplicate Entry" in some cases [#10739](https://github.com/pingcap/tidb/pull/10739)
- Improve the compatibility with MySQL of the following features
    - The `DAYNAME` function [#10732](https://github.com/pingcap/tidb/pull/10732)
    - The `MONTHNAME` function [#10733](https://github.com/pingcap/tidb/pull/10733)
    - Support the 0 value for the `EXTRACT` function when processing `MONTH` [#10702](https://github.com/pingcap/tidb/pull/10702)
    - The `DECIMAL` type can be converted to `TIMESTAMP` or `DATETIME` [#10734](https://github.com/pingcap/tidb/pull/10734)
- Change the column charset while changing the table charset [#10714](https://github.com/pingcap/tidb/pull/10714)
- Fix the overflow issue when converting a decimal to a float in some cases [#10730](https://github.com/pingcap/tidb/pull/10730)
- Fix the issue that some extremely large messages report the "grpc: received message larger than max" error caused by inconsistent maximum sizes of messages sent/received by gRPC of TiDB and TiKV [#10710](https://github.com/pingcap/tidb/pull/10710)
- Fix the panic issue caused by `ORDER BY` not filtering NULL in some cases [#10488](https://github.com/pingcap/tidb/pull/10488)
- Fix the issue that values returned by the `UUID` function might be duplicate when multiple nodes exist [#10711](https://github.com/pingcap/tidb/pull/10711)
- Change the value returned by `CAST(-num as datetime)` from `error` to NULL [#10703](https://github.com/pingcap/tidb/pull/10703)
- Fix the issue that an unsigned histogram meets signed ranges in some cases [#10695](https://github.com/pingcap/tidb/pull/10695)
- Fix the issue that an error is reported mistakenly for reading data when the statistics feedback meets the bigint unsigned primary key [#10307](https://github.com/pingcap/tidb/pull/10307)
- Fix the issue that the result of `Show Create Table` for partitioned tables is not correctly displayed in some cases [#10690](https://github.com/pingcap/tidb/pull/10690)
- Fix the issue that the calculation result of the `GROUP_CONCAT` aggregate function is not correct for some correlated subqueries [#10670](https://github.com/pingcap/tidb/pull/10670)
- Fix the issue that the result is wrongly displayed when the memory table of slow queries parses the slow query log in some cases [#10776](https://github.com/pingcap/tidb/pull/10776)
