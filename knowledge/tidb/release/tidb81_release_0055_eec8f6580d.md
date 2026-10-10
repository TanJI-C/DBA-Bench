# TiDB 2.1.1 overview and TiDB changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.1.md`
- Source Title: `TiDB 2.1.1 Release Notes`
- Source Heading Path: `TiDB 2.1.1 Release Notes | TiDB 2.1.1 Release Notes > TiDB`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `pd`
- Topic Tags: `release-notes`, `sql-optimizer`, `executor`, `statistics`, `server`, `transactions`, `ddl`, `character-set`, `collation`, `indexing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0055_eec8f6580d`
- Source ID: `tidb-docs-8.1:releases/release-2.1.1.md#tidb-2-1-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2acf69001999479f715eac609da9dc4f74b34e4250bc5afc8e0581f6da1fd2cd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.1#tidb-2-1-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 2.1.1 release-note changes in the SQL optimizer, executor, server, transactions, DDL, character set, collation, statistics, or index addition behavior.
- Retrieval Keywords: TiDB 2.1.1 Release Notes, TiDB, SQL Optimizer/Executor, Server, DDL, negative date round error, uncompress function does not check the data length, prepare statement reset bind arguments after execute, automatically collecting the statistics information of a partition table, abs function pushdown integer type, data race on the JSON column, transaction obtained TSO is incorrect when PD breaks down, bootstrap failure ANSI standards, incorrect parameters are used in transaction retries, default character set and collation utf8mb4, ddl_reorg_batch_size, character set and collation options case-insensitive, adding indexes for generated columns
- Follow-up Guidance: The same release notes file also contains separate sections for PD, TiKV, Lightning, and TiDB Binlog changes in 2.1.1.
- Classification Note: This is classified as a TiDB release chunk because the official content lists TiDB 2.1.1 fixes and changes across optimizer/executor, server, and DDL behavior.

## Official Source Content

# TiDB 2.1.1 Release Notes

On December 12, 2018, TiDB 2.1.1 is released. Compared with TiDB 2.1.0, this release has great improvement in stability, SQL optimizer, statistics information, and execution engine.
## TiDB

+ SQL Optimizer/Executor
    - Fix the round error of the negative date [#8574](https://github.com/pingcap/tidb/pull/8574)
    - Fix the issue that the `uncompress` function does not check the data length [#8606](https://github.com/pingcap/tidb/pull/8606)
    - Reset bind arguments of the `prepare` statement after the `execute` command is executed [#8652](https://github.com/pingcap/tidb/pull/8652)
    - Support automatically collecting the statistics information of a partition table [#8649](https://github.com/pingcap/tidb/pull/8649)
    - Fix the wrongly configured integer type when pushing down the `abs` function [#8628](https://github.com/pingcap/tidb/pull/8628)
    - Fix the data race on the JSON column [#8660](https://github.com/pingcap/tidb/pull/8660)
+ Server
    - Fix the issue that the transaction obtained TSO is incorrect when PD breaks down [#8567](https://github.com/pingcap/tidb/pull/8567)
    - Fix the bootstrap failure caused by the statement that does not conform to ANSI standards [#8576](https://github.com/pingcap/tidb/pull/8576)
    - Fix the issue that incorrect parameters are used in transaction retries [#8638](https://github.com/pingcap/tidb/pull/8638)
+ DDL
    - Change the default character set and collation of tables into `utf8mb4` [#8590](https://github.com/pingcap/tidb/pull/8590)
    - Add the `ddl_reorg_batch_size` variable to control the speed of adding indexes [#8614](https://github.com/pingcap/tidb/pull/8614)
    - Make the character set and collation options content in DDL case-insensitive [#8611](https://github.com/pingcap/tidb/pull/8611)
    - Fix the issue of adding indexes for generated columns [#8655](https://github.com/pingcap/tidb/pull/8655)
