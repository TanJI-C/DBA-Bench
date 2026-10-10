# TiDB 3.0.0 Beta.1 overview and TiDB changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.0-beta.1.md`
- Source Title: `TiDB 3.0.0 Beta.1 Release Notes`
- Source Heading Path: `TiDB 3.0.0 Beta.1 Release Notes | TiDB 3.0.0 Beta.1 Release Notes > Overview | TiDB 3.0.0 Beta.1 Release Notes > TiDB`
- Source Line Ranges: `5-65`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `release-notes`, `overview`, `sql-optimizer`, `window-functions`, `statistics`, `execution-engine`, `json-functions`, `privilege-management`, `roles`, `server`, `binlog`, `slow-query`, `logging`, `monitoring`, `ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0089_b841ddd26c`
- Source ID: `tidb-docs-8.1:releases/release-3.0.0-beta.1.md#tidb-3-0-0-beta-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d99f9aa7a5c255a71a5d4d99d36563322ca3fd53e2260fc8682175e211602b4e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.0-beta.1#tidb-3-0-0-beta-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.0-beta.1.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 3.0.0 Beta.1 release-note details about new TiDB SQL optimizer, execution engine, privilege management, server, monitoring, binlog, slow query, or DDL features.
- Retrieval Keywords: TiDB 3.0.0 Beta.1, Sort Merge Join, Cartesian product, Skyline Pruning, Window Functions, NTILE, LEAD, LAG, PERCENT_RANK, NTH_VALUE, CUME_DIST, FIRST_VALUE, LAST_VALUE, RANK, DENSE_RANK, RANGE FRAMED, ROW FRAMED, ROW NUMBER, order correlation between columns and the handle column, JSON_QUOTE, JSON_ARRAY_APPEND, JSON_MERGE_PRESERVE, BENCHMARK, COALESCE, NAME_CONST, SET ROLE, CURRENT_ROLE, DROP ROLE, CREATE ROLE, /debug/zip, show pump status, show drainer status, HASH fingerprints, slow SQL statements, log_bin, INFORMATION_SCHEMA.SLOW_QUERY, high_error_rate_feedback_total, QPS monitoring item, ddl_error_count_limit, ALTER ALGORITHM INPLACE, ALTER ALGORITHM INSTANT, SHOW CREATE VIEW, SHOW CREATE USER
- Follow-up Guidance: The release notes also list PD, TiKV, and Tools changes for the same TiDB 3.0.0 Beta.1 release.
- Classification Note: This chunk is classified as a TiDB release-notes section because the official content is the TiDB 3.0.0 Beta.1 overview and a component-organized list of TiDB feature and behavior changes.

## Official Source Content

# TiDB 3.0.0 Beta.1 Release Notes

Release Date: March 26, 2019

TiDB version: 3.0.0-beta.1

TiDB Ansible version: 3.0.0-beta.1
## Overview

On March 26, 2019, TiDB 3.0.0 Beta.1 is released. The corresponding TiDB Ansible version is 3.0.0 Beta.1. Compared with TiDB 3.0.0 Beta, this release has greatly improved the stability, usability, features, the SQL optimizer, statistics, and the execution engine.
## TiDB

+ SQL Optimizer
    - Support calculating the Cartesian product by using `Sort Merge Join` [#9032](https://github.com/pingcap/tidb/pull/9037)
    - Support Skyline Pruning, with some rules to prevent the execution plan from relying too heavily on statistics [#9337](https://github.com/pingcap/tidb/pull/9337)
    + Support Window Functions
        - `NTILE` [#9682](https://github.com/pingcap/tidb/pull/9682)
        - `LEAD` and `LAG` [#9672](https://github.com/pingcap/tidb/pull/9672)
        - `PERCENT_RANK` [#9671](https://github.com/pingcap/tidb/pull/9671)
        - `NTH_VALUE` [#9596](https://github.com/pingcap/tidb/pull/9596)
        - `CUME_DIST` [#9619](https://github.com/pingcap/tidb/pull/9619)
        - `FIRST_VALUE` and `LAST_VALUE` [#9560](https://github.com/pingcap/tidb/pull/9560)
        - `RANK` and `DENSE_RANK` [#9500](https://github.com/pingcap/tidb/pull/9500)
        - `RANGE FRAMED` [#9450](https://github.com/pingcap/tidb/pull/9450)
        - `ROW FRAMED` [#9358](https://github.com/pingcap/tidb/pull/9358)
        - `ROW NUMBER` [#9098](https://github.com/pingcap/tidb/pull/9098)
    - Add a type of statistic that indicates the order correlation between columns and the handle column [#9315](https://github.com/pingcap/tidb/pull/9315)
+ SQL Execution Engine
    + Add built-in functions
        - `JSON_QUOTE` [#7832](https://github.com/pingcap/tidb/pull/7832)
        - `JSON_ARRAY_APPEND` [#9609](https://github.com/pingcap/tidb/pull/9609)
        - `JSON_MERGE_PRESERVE` [#8931](https://github.com/pingcap/tidb/pull/8931)
        - `BENCHMARK` [#9252](https://github.com/pingcap/tidb/pull/9252)
        - `COALESCE` [#9087](https://github.com/pingcap/tidb/pull/9087)
        - `NAME_CONST` [#9261](https://github.com/pingcap/tidb/pull/9261)
    - Optimize the Chunk size based on the query context, to reduce the execution time of SQL statements and resources consumption of the cluster [#6489](https://github.com/pingcap/tidb/issues/6489)
+ Privilege management
    - Support `SET ROLE` and `CURRENT_ROLE` [#9581](https://github.com/pingcap/tidb/pull/9581)
    - Support `DROP ROLE` [#9616](https://github.com/pingcap/tidb/pull/9616)
    - Support `CREATE ROLE` [#9461](https://github.com/pingcap/tidb/pull/9461)
+ Server
    - Add the `/debug/zip` HTTP interface to get information of the current TiDB instance [#9651](https://github.com/pingcap/tidb/pull/9651)
    - Support the `show pump status` and `show drainer status` SQL statements to check the Pump or Drainer status [#9456](https://github.com/pingcap/tidb/pull/9456)
    - Support modifying the Pump or Drainer status by using SQL statements [#9789](https://github.com/pingcap/tidb/pull/9789)
    - Support adding HASH fingerprints to SQL text for easy tracking of slow SQL statements [#9662](https://github.com/pingcap/tidb/pull/9662)
    - Add the `log_bin` system variable ("0" by default) to control the enabling state of binlog; only support checking the state currently [#9343](https://github.com/pingcap/tidb/pull/9343)
    - Support managing the sending binlog strategy by using the configuration file [#9864](https://github.com/pingcap/tidb/pull/9864)
    - Support querying the slow log by using the `INFORMATION_SCHEMA.SLOW_QUERY` memory table [#9290](https://github.com/pingcap/tidb/pull/9290)
    - Change the MySQL version displayed in TiDB from 5.7.10 to 5.7.25 [#9553](https://github.com/pingcap/tidb/pull/9553)
    - Unify the [log format](https://github.com/tikv/rfcs/blob/master/text/0018-unified-log-format.md) for easy collection and analysis by tools
    - Add the `high_error_rate_feedback_total` monitoring item to record the difference between the actual data volume and the estimated data volume based on statistics [#9209](https://github.com/pingcap/tidb/pull/9209)
    - Add the QPS monitoring item in the database dimension, which can be enabled by using a configuration item [#9151](https://github.com/pingcap/tidb/pull/9151)
+ DDL
    - Add the `ddl_error_count_limit` global variable ("512" by default) to limit the number of DDL task retries (If this number exceeds the limit, the DDL task is canceled) [#9295](https://github.com/pingcap/tidb/pull/9295)
    - Support ALTER ALGORITHM `INPLACE`/`INSTANT` [#8811](https://github.com/pingcap/tidb/pull/8811)
    - Support the `SHOW CREATE VIEW` statement [#9309](https://github.com/pingcap/tidb/pull/9309)
    - Support the `SHOW CREATE USER` statement [#9240](https://github.com/pingcap/tidb/pull/9240)
