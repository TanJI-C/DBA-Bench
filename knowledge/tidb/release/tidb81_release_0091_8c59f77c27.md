# TiDB 3.0.0-rc.1 overview and TiDB changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.0-rc.1.md`
- Source Title: `TiDB 3.0.0-rc.1 Release Notes`
- Source Heading Path: `TiDB 3.0.0-rc.1 Release Notes | TiDB 3.0.0-rc.1 Release Notes > Overview | TiDB 3.0.0-rc.1 Release Notes > TiDB`
- Source Line Ranges: `5-61`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `release-notes`, `sql-optimizer`, `statistics`, `execution-engine`, `slow-log`, `rbac`, `ddl`, `configuration`, `plan-management`, `fast-analyze`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0091_8c59f77c27`
- Source ID: `tidb-docs-8.1:releases/release-3.0.0-rc.1.md#tidb-3-0-0-rc-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `db0b822197ae0756429126bdcde355ec62565d02b408baeeec303df0833bbdab`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.0-rc.1#tidb-3-0-0-rc-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.0-rc.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 3.0.0-rc.1 release-note details about optimizer, execution engine, slow log, RBAC, DDL, or new variables and options.
- Retrieval Keywords: TiDB 3.0.0-rc.1, tidb_opt_correlation_exp_factor, tidb_opt_join_reorder_threshold, FAST ANALYZE, tidb_enable_fast_analyze, SQL Plan Management, bound execution plans for SELECT statements, TableReader, IndexReader, IndexLookupReader, slow log coprocessor tasks, tidb_skip_isolation_level_check, SERIALIZABLE, SHOW GRANT, SET DEFAULT ROLE, GRANT ROLE, config-check, pre_split_regions, CREATE TABLE, FULLTEXT KEY, SHOW FULL COLUMNS, SHOW COLLATIONS
- Follow-up Guidance: The chunk also lists DDL compatibility fixes and server changes such as `kill` statement improvements, prepared DDL statements with no placeholders, and the `whitelist` plugin `ConnectionEvent` error fix.
- Classification Note: This is a TiDB release-notes chunk because the official content summarizes TiDB 3.0.0-rc.1 changes across SQL Optimizer, Execution Engine, Server, and DDL.

## Official Source Content

# TiDB 3.0.0-rc.1 Release Notes

Release Date: May 10, 2019

TiDB version: 3.0.0-rc.1

TiDB Ansible version: 3.0.0-rc.1
## Overview

On May 10, 2019, TiDB 3.0.0-rc.1 is released. The corresponding TiDB Ansible version is 3.0.0-rc.1. Compared with TiDB 3.0.0-beta.1, this release has greatly improved the stability, usability, features, the SQL optimizer, statistics, and the execution engine.
## TiDB

+ SQL Optimizer
    - Improve the accuracy of cost estimates by using order correlation between columns; introduce a heuristic parameter `tidb_opt_correlation_exp_factor` to control the preference for index scans for scenarios when correlation cannot be directly used for estimation. [#9839](https://github.com/pingcap/tidb/pull/9839)
    - Match more prefix columns of the indexes when extracting access conditions of composite indexes if there are relevant columns in the filter [#10053](https://github.com/pingcap/tidb/pull/10053)
    - Use the dynamic programming algorithm to specify the execution order of join operations when the number of tables participating in the join is less than the value of `tidb_opt_join_reorder_threshold`. [#8816](https://github.com/pingcap/tidb/pull/8816)
    - Match more prefix columns of the indexes in the inner tables that build the index join when using composite indexes as the access conditions [#8471](https://github.com/pingcap/tidb/pull/8471)
    - Improve the accuracy of row count estimation for single-column indexes with NULL values [#9474](https://github.com/pingcap/tidb/pull/9474)
    - Specially handle `GROUP_CONCAT` when eliminating aggregate functions during the logical optimization phase to prevent incorrect executions [#9967](https://github.com/pingcap/tidb/pull/9967)
    - Properly push the filter down to child nodes of the join operator if the filter is a constant [#9848](https://github.com/pingcap/tidb/pull/9848)
    - Specially handle some functions such as `RAND()` when pruning columns during the logical optimization phase to prevent incompatibilities with MySQL [#10064](https://github.com/pingcap/tidb/pull/10064)
    - Support `FAST ANALYZE`, which speeds up statistics collection by sampling the region instead of scanning the entire region. This feature is controlled by the variable `tidb_enable_fast_analyze`. [#10258](https://github.com/pingcap/tidb/pull/10258)
    - Support SQL Plan Management, which ensures execution stability by performing execution plan binding for SQL statements. This feature is currently in beta and only supports bound execution plans for SELECT statements. It is not recommended to use it in the production environment. [#10284](https://github.com/pingcap/tidb/pull/10284)

+ Execution Engine
    - Support tracking and controlling memory usage in three operators - `TableReader`, `IndexReader` and `IndexLookupReader` [#10003](https://github.com/pingcap/tidb/pull/10003)
    - Support showing more information about coprocessor tasks in the slow log such as the number of tasks in coprocessor, the average/longest/90% of execution/waiting time and the addresses of the TiKVs which take the longest execution time or waiting time [#10165](https://github.com/pingcap/tidb/pull/10165)
    - Support the prepared DDL statements with no placeholders [#10144](https://github.com/pingcap/tidb/pull/10144)

+ Server
    - Only allow the DDL owner to execute bootstrap when TiDB is started [#10029](https://github.com/pingcap/tidb/pull/10029)
    - Add the variable `tidb_skip_isolation_level_check` to prevent TiDB from reporting errors when setting the transaction isolation level to SERIALIZABLE [#10065](https://github.com/pingcap/tidb/pull/10065)
    - Merge the implicit commit time and the SQL execution time in the slow log [#10294](https://github.com/pingcap/tidb/pull/10294)
        - Support for SQL Roles (RBAC Privilege Management)
        - Support `SHOW GRANT` [#10016](https://github.com/pingcap/tidb/pull/10016)
        - Support `SET DEFAULT ROLE` [#9949](https://github.com/pingcap/tidb/pull/9949)
    - Support `GRANT ROLE` [#9721](https://github.com/pingcap/tidb/pull/9721)
    - Fix the `ConnectionEvent` error from the `whitelist` plugin that makes TiDB exit [#9889](https://github.com/pingcap/tidb/pull/9889)
    - Fix the issue of mistakenly adding read-only statements to the transaction history [#9723](https://github.com/pingcap/tidb/pull/9723)
    - Improve `kill` statements to stop SQL execution and release resources more quickly [#9844](https://github.com/pingcap/tidb/pull/9844)
    - Add a startup option `config-check` to check the validity of the configuration file [#9855](https://github.com/pingcap/tidb/pull/9855)
    - Fix the validity check of inserting NULL fields when the strict SQL mode is disabled [#10161](https://github.com/pingcap/tidb/pull/10161)

+ DDL
    - Add the `pre_split_regions` option for `CREATE TABLE` statements; this option supports pre-splitting the Table Region when creating a table to avoid write hot spots caused by lots of writes after the table creation [#10138](https://github.com/pingcap/tidb/pull/10138)
    - Optimize the execution performance of some DDL statements [#10170](https://github.com/pingcap/tidb/pull/10170)
    - Add the warning that full-text indexes are not supported for `FULLTEXT KEY` [#9821](https://github.com/pingcap/tidb/pull/9821)
    - Fix the compatibility issue for the UTF8 and UTF8MB4 charsets in the old versions of TiDB [#9820](https://github.com/pingcap/tidb/pull/9820)
    - Fix the potential bug in `shard_row_id_bits` of a table [#9868](https://github.com/pingcap/tidb/pull/9868)
    - Fix the bug that the column charset is not changed after the table charset is changed [#9790](https://github.com/pingcap/tidb/pull/9790)
    - Fix a potential bug in `SHOW COLUMN` when using `BINARY`/`BIT` as the column default value [#9897](https://github.com/pingcap/tidb/pull/9897)
    - Fix the compatibility issue in displaying `CHARSET`/`COLLATION` descriptions in the `SHOW FULL COLUMNS` statement [#10007](https://github.com/pingcap/tidb/pull/10007)
    - Fix the issue that the `SHOW COLLATIONS` statement only lists collations supported by TiDB [#10186](https://github.com/pingcap/tidb/pull/10186)
