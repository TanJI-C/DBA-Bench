# TiDB 4.0 RC release notes: compatibility, features, and fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.0-rc.md`
- Source Title: `TiDB 4.0 RC Release Notes`
- Source Heading Path: `TiDB 4.0 RC Release Notes | TiDB 4.0 RC Release Notes > Compatibility Changes | TiDB 4.0 RC Release Notes > Important Bug Fixes | TiDB 4.0 RC Release Notes > New Features | TiDB 4.0 RC Release Notes > Bug Fixes`
- Source Line Ranges: `5-104`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `lightning`, `ticdc`
- Topic Tags: `release-notes`, `compatibility-changes`, `new-features`, `bug-fixes`, `performance`, `tls`, `collation`, `recover-table`, `ddl`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0157_7cdd7adeaa`
- Source ID: `tidb-docs-8.1:releases/release-4.0.0-rc.md#tidb-4-0-rc-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b75d1f63b6134783758d4d970d2cbd88fd7613171fb1442d42c132591ecaa4bd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.0-rc#tidb-4-0-rc-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.0-rc.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.0-rc release-note details about compatibility changes, new features, performance improvements, and bug fixes across TiDB, TiKV, PD, TiDB Lightning, TiDB Binlog, and TiCDC.
- Retrieval Keywords: TiDB 4.0 RC Release Notes, 4.0.0-rc, TiUP 0.0.3, Compatibility Changes, Important Bug Fixes, New Features, Bug Fixes, tidb-server status port is occupied, pipelined feature in pessimistic transactions, unify-read-pool, verifying Common Name, PREPARE statement DDL job replication, Read Committed isolation level, Inline Projection optimization, INL_MERGE_JOIN, AutoRandom, utf8mb4_general_ci, utf8_general_ci, RECOVER TABLE, recovering truncated tables, DDLJobs system table, EXPLAIN output, TLS in the HTTP port, default PD configuration information through the HTTP API, TiDB Lightning performance, Follower Read leader transfer panic, BIT(N), ErrorCount, Garbage Collection TiFlash, test schema does not exist in the downstream, CDC cli real-time interactive mode, checking whether the table in the upstream can be replicated, asynchronous write to Kafka
- Follow-up Guidance: The source also includes a warning that some known issues were found in this version and recommends using the latest 4.0.x version.
- Classification Note: This is a self-managed release-notes chunk summarizing official TiDB 4.0.0-rc compatibility changes, features, fixes, and tool/component updates from the release notes.

## Official Source Content

# TiDB 4.0 RC Release Notes

Release date: April 8, 2020

TiDB version: 4.0.0-rc

TiUP version: 0.0.3

> **Warning:**
>
> Some known issues are found in this version, and these issues are fixed in new versions. It is recommended that you use the latest 4.0.x version.
## Compatibility Changes

+ TiDB

    - Refuse to get started instead of returning an alert log when the tidb-server status port is occupied [#15177](https://github.com/pingcap/tidb/pull/15177)

+ TiKV

    - Support the `pipelined` feature in pessimistic transactions, which improves the TPC-C performance by 20%. The risk is that the transaction commit might fail because of lock failure during the execution [#6984](https://github.com/tikv/tikv/pull/6984)
    - Enable the `unify-read-pool` configuration item in new clusters by default and use the previous setting of this item in old clusters [#7059](https://github.com/tikv/tikv/pull/7059)

+ Tools

    - TiDB Binlog

        * Add the configuration item for verifying Common Name [#934](https://github.com/pingcap/tidb-binlog/pull/934)
## Important Bug Fixes

+ TiDB

    - Fix the issue that replication between the upstream and downstream might go wrong when the DDL job is executed using the `PREPARE` statement because of the incorrect job query in the internal records [#15435](https://github.com/pingcap/tidb/pull/15435)
    - Fix the issue of incorrect subquery result in the `Read Committed` isolation level [#15471](https://github.com/pingcap/tidb/pull/15471)
    - Fix the issue of incorrect results caused by the Inline Projection optimization [#15411](https://github.com/pingcap/tidb/pull/15411)
    - Fix the issue that the SQL Hint `INL_MERGE_JOIN` is executed incorrectly in some cases [#15515](https://github.com/pingcap/tidb/pull/15515)
    - Fix the issue that columns with the `AutoRandom` attribute are rebased when the negative number is explicitly written to these columns [#15397](https://github.com/pingcap/tidb/pull/15397)
## New Features

+ TiDB

    - Add the case-insensitive collation so that users can enable `utf8mb4_general_ci` and `utf8_general_ci` in a new cluster [#33](https://github.com/pingcap/tidb/projects/33)
    - Enhance the `RECOVER TABLE` syntax to support recovering truncated tables [#15398](https://github.com/pingcap/tidb/pull/15398)
    - Refuse to get started instead of returning an alert log when the tidb-server status port is occupied [#15177](https://github.com/pingcap/tidb/pull/15177)
    - Optimize the write performance of using a sequence as the default column values [#15216](https://github.com/pingcap/tidb/pull/15216)
    - Add the `DDLJobs` system table to query the details of DDL jobs [#14837](https://github.com/pingcap/tidb/pull/14837)
    - Optimize the `aggFuncSum` performance [#14887](https://github.com/pingcap/tidb/pull/14887)
    - Optimize the output of `EXPLAIN` [#15507](https://github.com/pingcap/tidb/pull/15507)

+ TiKV

    - Support the `pipelined` feature in pessimistic transactions, which improves the TPC-C performance by 20%. The risk is that the transaction commit might fail because of lock failure during the execution [#6984](https://github.com/tikv/tikv/pull/6984)
    - Support TLS in the HTTP port [#5393](https://github.com/tikv/tikv/pull/5393)
    - Enable the `unify-read-pool` configuration item in new clusters by default and use the previous setting of this item in old clusters [#7059](https://github.com/tikv/tikv/pull/7059)

+ PD

    - Support getting the default PD configuration information through the HTTP API [#2258](https://github.com/pingcap/pd/pull/2258)

+ Tools

    - TiDB Binlog

        * Add the configuration item for verifying Common Name [#934](https://github.com/pingcap/tidb-binlog/pull/934)

    - TiDB Lightning

        * Optimize the performance of TiDB Lightning [#281](https://github.com/pingcap/tidb-lightning/pull/281) [#275](https://github.com/pingcap/tidb-lightning/pull/275)
## Bug Fixes

+ TiDB

    - Fix the issue that replication between the upstream and downstream might go wrong when the DDL job is executed using the `PREPARE` statement because of the incorrect job query in the internal records [#15435](https://github.com/pingcap/tidb/pull/15435)
    - Fix the issue of incorrect subquery result in the `Read Committed` isolation level [#15471](https://github.com/pingcap/tidb/pull/15471)
    - Fix the issue of possible wrong behavior when using `INSERT ... VALUES` to specify the `BIT(N)` data type [#15350](https://github.com/pingcap/tidb/pull/15350)
    - Fix the issue that the DDL Job internal retry does not fully achieve the expected outcomes because the values of `ErrorCount` fail to be summed correctly [#15373](https://github.com/pingcap/tidb/pull/15373)
    - Fix the issue that Garbage Collection might work abnormally when TiDB connects to TiFlash [#15505](https://github.com/pingcap/tidb/pull/15505)
    - Fix the issue of incorrect result caused by the Inline Projection optimization [#15411](https://github.com/pingcap/tidb/pull/15411)
    - Fix the issue that the SQL Hint `INL_MERGE_JOIN` is executed incorrectly in some cases [#15515](https://github.com/pingcap/tidb/pull/15515)
    - Fix the issue that columns with the `AutoRandom` attribute are rebased when the negative number is explicitly written to these columns [#15397](https://github.com/pingcap/tidb/pull/15397)

+ TiKV
    - Fix the possible panic caused by transferring the leader when the Follower Read feature is enabled [#7101](https://github.com/tikv/tikv/pull/7101)

+ Tools

    - TiDB Lightning

        * Fix the issue of data error caused by the error of character conversion when the backend is TiDB [#283](https://github.com/pingcap/tidb-lightning/pull/283)

    - TiCDC

        * Fix the issue that an error is returned if the `test` schema does not exist in the downstream when MySQL sink is executing the DDL statement [#353](https://github.com/pingcap/tiflow/pull/353)
        * Support the real-time interactive mode in CDC cli [#351](https://github.com/pingcap/tiflow/pull/351)
        * Support checking whether the table in the upstream can be replicated during data replication [#368](https://github.com/pingcap/tiflow/pull/368)
        * Support asynchronous write to Kafka [#344](https://github.com/pingcap/tiflow/pull/344)
