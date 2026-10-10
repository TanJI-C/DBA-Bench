# TiDB RC1 release highlights across TiKV, PD, TiDB, and new tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-rc.1.md`
- Source Title: `TiDB RC1 Release Notes`
- Source Heading Path: `TiDB RC1 Release Notes | TiDB RC1 Release Notes > TiKV | TiDB RC1 Release Notes > Placement Driver (PD) | TiDB RC1 Release Notes > TiDB | TiDB RC1 Release Notes > New tools`
- Source Line Ranges: `5-47`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `tidb`, `ecosystem`
- Topic Tags: `release-notes`, `optimizer`, `scheduling`, `raw-kv`, `mysql-compatibility`, `add-index`, `deployment-tools`, `data-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0614_ab2235248b`
- Source ID: `tidb-docs-8.1:releases/release-rc.1.md#tidb-rc1-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `00e689d11375322d131ecaa3f579259eafeaf90841ac7e499a1c0cade8ecfaf2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-rc.1#tidb-rc1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-rc.1.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB RC1 release highlights spanning TiKV, PD, TiDB optimizer and MySQL compatibility changes, or newly added tools.
- Retrieval Keywords: TiDB RC1 Release Notes, TiKV write speed improved, disk space usage is reduced, support a cluster with 200 nodes, Raw KV API, Golang client, Placement Driver PD, scheduling strategy framework, label, Cross Data Center scheduling, PD Control, SQL query optimizer, Eager aggregation, more detailed EXPLAIN information, parallelization of the UNION operator, subquery performance, conditional push-down, Cost Based Optimizer CBO, time related data types, compatibility with MySQL, built-in functions in MySQL, add index statement, CHANGE COLUMN, MODIFY COLUMN, ALTER TABLE, Loader, mydumper data format, Multi-thread import, Retry if error occurs, Breakpoint resume, one-click deployment
- Follow-up Guidance: The source also lists exact RC1 additions such as `CHANGE COLUMN`, `MODIFY COLUMN`, `EXPLAIN` improvements, `Loader`, and PD `label` support for Cross Data Center scheduling.
- Classification Note: This is a self-managed release-notes chunk summarizing RC1 updates across shared components including TiKV, PD, TiDB, and ecosystem tools.

## Official Source Content

# TiDB RC1 Release Notes

On December 23, 2016, TiDB RC1 is released. See the following updates in this release:
## TiKV

+ The write speed has been improved.
+ The disk space usage is reduced.
+ Hundreds of TBs of data can be supported.
+ The stability is improved and TiKV can support a cluster with 200 nodes.
+ Supports the Raw KV API and the Golang client.
## Placement Driver (PD)

+ The scheduling strategy framework is optimized and now the strategy is more flexible and reasonable.
+ The support for `label` is added to support Cross Data Center scheduling.
+ PD Control is provided to operate the PD cluster more easily.
## TiDB

+ The following features are added or improved in the SQL query optimizer:
    - Eager aggregation
    - More detailed `EXPLAIN` information
    - Parallelization of the `UNION` operator
    - Optimization of the subquery performance
    - Optimization of the conditional push-down
    - Optimization of the Cost Based Optimizer (CBO) framework
+ The implementation of the time related data types are refactored to improve the compatibility with MySQL.
+ More built-in functions in MySQL are supported.
+ The speed of the `add index` statement is enhanced.
+ The following statements are supported:
    - Use the `CHANGE COLUMN` statement to change the name of a column.
    - Use `MODIFY COLUMN` and `CHANGE COLUMN` of the `ALTER TABLE` statement for some of the column type transfer.
## New tools

+ `Loader` is added to be compatible with the `mydumper` data format in Percona and provides the following functions:
    - Multi-thread import
    - Retry if error occurs
    - Breakpoint resume
    - Targeted optimization for TiDB
+ The tool for one-click deployment is added.
