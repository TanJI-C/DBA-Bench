# TiDB 2.1.15 release notes across TiDB, TiKV, PD, tools, and TiDB Ansible

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.15.md`
- Source Title: `TiDB 2.1.15 Release Notes`
- Source Heading Path: `TiDB 2.1.15 Release Notes | TiDB 2.1.15 Release Notes > TiDB | TiDB 2.1.15 Release Notes > TiKV | TiDB 2.1.15 Release Notes > PD | TiDB 2.1.15 Release Notes > Tools | TiDB 2.1.15 Release Notes > TiDB Ansible`
- Source Line Ranges: `5-52`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `lightning`
- Topic Tags: `release-notes`, `bug-fixes`, `sql-statements`, `plugins`, `region-distribution`, `logging`, `scheduling`, `binlog`, `import`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0063_dd57a04590`
- Source ID: `tidb-docs-8.1:releases/release-2.1.15.md#tidb-2-1-15-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9e3f77e979601943d661df14c29ca8e0d9ecb0fbd6cdf5308364985877944fb1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.15#tidb-2-1-15-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.15.md

## Retrieval Guidance

- Use When: Use this chunk when looking for what changed in TiDB 2.1.15 across TiDB, TiKV, PD, TiDB Binlog, TiDB Lightning, and TiDB Ansible, including new SQL statements, configuration items, and bug fixes.
- Retrieval Keywords: TiDB 2.1.15 Release Notes, 2.1.15, SHOW TABLE REGIONS, ADMIN PLUGINS ENABLE, ADMIN PLUGINS DISABLE, tidb_scatter_region, DATE_ADD microseconds, UPDATE SELECT projection elimination, SHOW CREATE TABLE CURRENT_TIMESTAMP precision, modify collation UTF-8 utf8mb4, Audit plugin session connection information, TiKV unify the log format, PD unify the log format, Region approximate size or keys, TiDB Binlog Pump GC strategy, TiDB Lightning column names not in lowercase, parse duration, compile duration, TiDB Dashboard monitoring
- Follow-up Guidance: The source groups the changes by TiDB, TiKV, PD, Tools, and TiDB Ansible and names the specific statements, configuration item, plugin behavior, monitoring items, and fixes added in 2.1.15.
- Classification Note: This is a self-managed release-notes chunk because the official content is the TiDB 2.1.15 release notes covering multiple components and operational fixes or features for that release.

## Official Source Content

# TiDB 2.1.15 Release Notes

Release date: July 16, 2019

TiDB version: 2.1.15

TiDB Ansible version: 2.1.15
## TiDB

+ Fix the issue that the `DATE_ADD` function returns wrong results due to incorrect alignment when dealing with microseconds [#11289](https://github.com/pingcap/tidb/pull/11289)
+ Fix the issue that an error is reported when the empty value in the string column is compared with `FLOAT` or `INT` [#11279](https://github.com/pingcap/tidb/pull/11279)
+ Fix the issue that the `INSERT` function fails to correctly return the `NULL` value when a parameter is `NULL` [#11249](https://github.com/pingcap/tidb/pull/11249)
+ Fix the issue that an error occurs when indexing the column of the non-string type and `0` length [#11215](https://github.com/pingcap/tidb/pull/11215)
+ Add the `SHOW TABLE REGIONS` statement to query the Region distribution of a table through SQL statements [#11238](https://github.com/pingcap/tidb/pull/11238)
+ Fix the issue that an error is reported when using the `UPDATE … SELECT` statement because the projection elimination is used to optimize rules in the `SELECT` subqueries [#11254](https://github.com/pingcap/tidb/pull/11254)
+ Add the `ADMIN PLUGINS ENABLE`/`ADMIN PLUGINS DISABLE` SQL statement to dynamically enable or disable plugins [#11189](https://github.com/pingcap/tidb/pull/11189)
+ Add the session connection information in the Audit plugin [#11189](https://github.com/pingcap/tidb/pull/11189)
+ Fix the panic issue that happens when a column is queried on multiple times and the returned result is `NULL` during point queries [#11227](https://github.com/pingcap/tidb/pull/11227)
+ Add the `tidb_scatter_region` configuration item to scatter table Regions when creating a table [#11213](https://github.com/pingcap/tidb/pull/11213)
+ Fix the data race issue caused by non-thread safe `rand.Rand` when using the `RAND` function [#11170](https://github.com/pingcap/tidb/pull/11170)
+ Fix the issue that the comparison result of integers and non-integers is incorrect in some cases [#11191](https://github.com/pingcap/tidb/pull/11191)
+ Support modifying the collation of a database or a table, but the character set of the database/table has to be UTF-8 or utf8mb4 [#11085](https://github.com/pingcap/tidb/pull/11085)
+ Fix the issue that the precision shown by the `SHOW CREATE TABLE` statement is incomplete when `CURRENT_TIMESTAMP` is used as the default value of the column and the float precision is specified [#11087](https://github.com/pingcap/tidb/pull/11087)
## TiKV

+ Unify the log format [#5083](https://github.com/tikv/tikv/pull/5083)
+ Improve the accuracy of Region's approximate size or keys in extreme cases to improve the accuracy of scheduling [#5085](https://github.com/tikv/tikv/pull/5085)
## PD

+ Unify the log format [#1625](https://github.com/pingcap/pd/pull/1625)
## Tools

TiDB Binlog

+ Optimize the Pump GC strategy and remove the restriction that the unconsumed binlog cannot be cleaned to make sure that the resources are not occupied for a long time [#663](https://github.com/pingcap/tidb-binlog/pull/663)

TiDB Lightning

+ Fix the import error that happens when the column names specified by the SQL dump are not in lowercase [#210](https://github.com/pingcap/tidb-lightning/pull/210)
## TiDB Ansible

+ Add the `parse duration` and `compile duration` monitoring items in TiDB Dashboard to monitor the time that it takes to parse SQL statements and execute compilation [#815](https://github.com/pingcap/tidb-ansible/pull/815)
