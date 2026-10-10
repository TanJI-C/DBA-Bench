# Release overview, compatibility changes, important fixes, and new features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.14.md`
- Source Title: `TiDB 3.0.14 Release Notes`
- Source Heading Path: `TiDB 3.0.14 Release Notes | TiDB 3.0.14 Release Notes > Compatibility Changes | TiDB 3.0.14 Release Notes > Important Bug Fixes | TiDB 3.0.14 Release Notes > New Features`
- Source Line Ranges: `5-65`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `lightning`
- Topic Tags: `release-notes`, `compatibility`, `bug-fixes`, `new-features`, `privileges`, `index-join`, `fast-analyze`, `binlog`, `transactions`, `recover-table`, `show-grants`, `load-data`, `partition-pruning`, `tls`, `ddl-jobs`, `processlist`, `views`, `auto-id-cache`, `optimistic-transactions`, `pessimistic-transactions`, `lightning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0106_5863a0b85e`
- Source ID: `tidb-docs-8.1:releases/release-3.0.14.md#tidb-3-0-14-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e2c56cdc5ab577010ec2a6ae9cc3ad55db3b74ef4053b23968ece6b5b5b881a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.14#tidb-3-0-14-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.14.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 3.0.14 release overview covering compatibility changes, important bug fixes, and new features across TiDB, TiKV, and TiDB Lightning.
- Retrieval Keywords: TiDB 3.0.14 Release Notes, Compatibility Changes, Important Bug Fixes, New Features, performance_schema read-only, metrics_schema read-only, index join incorrect result, fast analyze panic handle attribute, Binlog data replication DDL job query field, cleanup of lock atomicity of the transaction, admin show ddl jobs schema name column table name column, RECOVER TABLE recovering truncated tables, SHOW GRANTS privilege check, LOAD DATA privilege check, partition pruning time and date partition keys, require-secure-transport, TLS, information_schema.processlist start_ts, ALTER TABLE ... AUTO_ID_CACHE, optimistic transactions BatchRollback, pessimistic lock waiter, tidb-lightning-ctl fetch-mode
- Follow-up Guidance: The chunk points to specific statements and options such as `admin show ddl jobs`, `RECOVER TABLE`, `SHOW GRANTS`, `LOAD DATA`, `require-secure-transport`, `information_schema.processlist`, and `ALTER TABLE ... AUTO_ID_CACHE` for more targeted retrieval.
- Classification Note: The official content is classified as a release overview because it groups TiDB 3.0.14 compatibility changes, important fixes, and newly added features in one release-notes section.

## Official Source Content

# TiDB 3.0.14 Release Notes

Release date: May 9, 2020

TiDB version: 3.0.14
## Compatibility Changes

+ TiDB

    - Adjust the user privilege in `performance_schema` and `metrics_schema` from read-write to read-only [#15417](https://github.com/pingcap/tidb/pull/15417)
## Important Bug Fixes

+ TiDB

    - Fix the issue that the query result of `index join` is incorrect when the `join` condition has multiple equivalent conditions on the column with the `handle` attribute [#15734](https://github.com/pingcap/tidb/pull/15734)
    - Fix the panic that occurs when performing the `fast analyze` operation on the column with the `handle` attribute [#16079](https://github.com/pingcap/tidb/pull/16079)
    - Fix the issue that the `query` field in the DDL job structure is incorrect when the DDL statement is executed in a way of `prepare`. This issue might cause data inconsistency between the upstream and the downstream when Binlog is used for data replication. [#15443](https://github.com/pingcap/tidb/pull/15443)

+ TiKV

    - Fix the issue that repeated requests on the cleanup of lock might destroy the atomicity of the transaction [#7388](https://github.com/tikv/tikv/pull/7388)
## New Features

+ TiDB

    - Add the schema name column and the table name column to the query results of the `admin show ddl jobs` statement [#16428](https://github.com/pingcap/tidb/pull/16428)
    - Enhance the `RECOVER TABLE` syntax to support recovering truncated tables [#15458](https://github.com/pingcap/tidb/pull/15458)
    - Support the privilege check for the `SHOW GRANTS` statement [#16168](https://github.com/pingcap/tidb/pull/16168)
    - Support the privilege check for the `LOAD DATA` statement [#16736](https://github.com/pingcap/tidb/pull/16736)
    - Improve the performance of partition pruning when functions related to time and date are used as partition keys [#15618](https://github.com/pingcap/tidb/pull/15618)
    - Adjust the log level of `dispatch error` from `WARN` to `ERROR` [#16232](https://github.com/pingcap/tidb/pull/16232)
    - Support the `require-secure-transport` startup option to force clients to use TLS [#15415](https://github.com/pingcap/tidb/pull/15415)
    - Support HTTP communication between TiDB components when TLS is configured [#15419](https://github.com/pingcap/tidb/pull/15419)
    - Add the `start_ts` information of the current transaction to the `information_schema.processlist` table [#16160](https://github.com/pingcap/tidb/pull/16160)
    - Support automatically reloading the TLS certificate information used for communication among clusters [#15162](https://github.com/pingcap/tidb/pull/15162)
    - Improve the read performance of the partitioned tables by restructuring the partition pruning [#15628](https://github.com/pingcap/tidb/pull/15628)
    - Support the partition pruning feature when `floor(unix_timestamp(a))` is used as the partition expression of the `range` partition table [#16521](https://github.com/pingcap/tidb/pull/16521)
    - Allow executing the `update` statement that contains a `view` and does not update the `view` [#16787](https://github.com/pingcap/tidb/pull/16787)
    - Prohibit creating nested `view`s [#15424](https://github.com/pingcap/tidb/pull/15424)
    - Prohibit truncating `view` [#16420](https://github.com/pingcap/tidb/pull/16420)
    - Prohibit using the `update` statement to explicitly update the values of a column when this column is not in the `public` state [#15576](https://github.com/pingcap/tidb/pull/15576)
    - Prohibit starting TiDB when the `status` port is occupied [#15466](https://github.com/pingcap/tidb/pull/15466)
    - Change the character set of the `current_role` function from `binary` to `utf8mb4` [#16083](https://github.com/pingcap/tidb/pull/16083)
    - Improve `max-execution-time` usability by checking the interrupt signal when the data of a new Region is read [#15615](https://github.com/pingcap/tidb/pull/15615)
    - Add the `ALTER TABLE ... AUTO_ID_CACHE` syntax for explicitly setting the cache step of `auto_id` [#16287](https://github.com/pingcap/tidb/pull/16287)

+ TiKV

    - Improve the performance when many conflicts and the `BatchRollback` condition exist in optimistic transactions [#7605](https://github.com/tikv/tikv/pull/7605)
    - Fix the issue of decreased performance that occurs because the pessimistic lock `waiter` is frequently awakened when many conflicts exist in pessimistic transactions [#7584](https://github.com/tikv/tikv/pull/7584)

+ Tools

    + TiDB Lightning

        - Support printing the TiKV cluster mode using the `fetch-mode` sub-command of tidb-lightning-ctl [#287](https://github.com/pingcap/tidb-lightning/pull/287)
