# TiDB 3.0.0-rc.3 overview and TiDB changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.0-rc.3.md`
- Source Title: `TiDB 3.0.0-rc.3 Release Notes`
- Source Heading Path: `TiDB 3.0.0-rc.3 Release Notes | TiDB 3.0.0-rc.3 Release Notes > Overview | TiDB 3.0.0-rc.3 Release Notes > TiDB`
- Source Line Ranges: `5-59`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `release-notes`, `sql-optimizer`, `execution-engine`, `server`, `ddl`, `statistics`, `region-splitting`, `hotspot`, `pessimistic-transactions`, `bindings`, `expensive-query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0096_6a7ef7a472`
- Source ID: `tidb-docs-8.1:releases/release-3.0.0-rc.3.md#tidb-3-0-0-rc-3-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3cceb815e37ff1e00f0ebfa98ed19618a67185b54d7ec66fbd2f9476bf960dc9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.0-rc.3#tidb-3-0-0-rc-3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.0-rc.3.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 3.0.0-rc.3 release-note details about TiDB SQL optimizer, execution engine, server, and DDL changes such as hotspot alleviation, bindings, expensive query logging, or pessimistic transaction fixes.
- Retrieval Keywords: TiDB 3.0.0-rc.3, SQL Optimizer, Execution Engine, Server, DDL, split table region, split index region, SHARD_ROW_ID_BITS, bind-info-lease, expensive query, stats-lease, fast analyze, create view prepare panic, show create table partitioned tables, admin show ddl jobs, show grants current_user, show view privilege explain, pessimistic-txn, skip-grant-table, slow queries host
- Follow-up Guidance: This chunk is followed by release-note sections for PD, TiKV, Tools, and TiDB Ansible changes in the same 3.0.0-rc.3 release.
- Classification Note: The content is classified as a TiDB release-note chunk because it summarizes version 3.0.0-rc.3 changes across TiDB optimizer, execution engine, server, and DDL areas.

## Official Source Content

# TiDB 3.0.0-rc.3 Release Notes

Release date: June 21, 2019

TiDB version: 3.0.0-rc.3

TiDB Ansible version: 3.0.0-rc.3
## Overview

On June 21, 2019, TiDB 3.0.0-rc.3 is released. The corresponding TiDB Ansible version is 3.0.0-rc.3. Compared with TiDB 3.0.0-rc.2, this release has greatly improved the stability, usability, features, the SQL optimizer, statistics, and the execution engine.
## TiDB

+ SQL Optimizer
    - Remove the feature of collecting virtual generated column statistics [#10629](https://github.com/pingcap/tidb/pull/10629)
    - Fix the issue that the primary key constant overflows during point queries [#10699](https://github.com/pingcap/tidb/pull/10699)
    - Fix the issue that using uninitialized information in `fast analyze` causes panic [#10691](https://github.com/pingcap/tidb/pull/10691)
    - Fix the issue that executing the `create view` statement using `prepare` causes panic because of wrong column information [#10713](https://github.com/pingcap/tidb/pull/10713)
    - Fix the issue that the column information is not cloned when handling window functions [#10720](https://github.com/pingcap/tidb/pull/10720)
    - Fix the wrong estimation for the selectivity rate of the inner table selection in index join [#10854](https://github.com/pingcap/tidb/pull/10854)
    - Support automatic loading statistics when the `stats-lease` variable value is 0 [#10811](https://github.com/pingcap/tidb/pull/10811)

+ Execution Engine
    - Fix the issue that resources are not correctly released when calling the `Close` function in `StreamAggExec` [#10636](https://github.com/pingcap/tidb/pull/10636)
    - Fix the issue that the order of `table_option` and `partition_options` is incorrect in the result of executing the `show create table` statement for partitioned tables [#10689](https://github.com/pingcap/tidb/pull/10689)
    - Improve the performance of `admin show ddl jobs` by supporting scanning data in reverse order [#10687](https://github.com/pingcap/tidb/pull/10687)
    - Fix the issue that the result of the `show grants` statement in RBAC is incompatible with that of MySQL when this statement has the `current_user` field [#10684](https://github.com/pingcap/tidb/pull/10684)
    - Fix the issue that UUIDs might generate duplicate values on multiple nodes [#10712](https://github.com/pingcap/tidb/pull/10712)
    - Fix the issue that the `show view` privilege is not considered in `explain` [#10635](https://github.com/pingcap/tidb/pull/10635)
    - Add the `split table region` statement to manually split the table Region to alleviate the hotspot issue [#10765](https://github.com/pingcap/tidb/pull/10765)
    - Add the `split index region` statement to manually split the index Region to alleviate the hotspot issue [#10764](https://github.com/pingcap/tidb/pull/10764)
    - Fix the incorrect execution issue when you execute multiple statements such as `create user`, `grant`, or `revoke` consecutively [#10737](https://github.com/pingcap/tidb/pull/10737)
    - Add a blocklist to prohibit pushing down expressions to Coprocessor [#10791](https://github.com/pingcap/tidb/pull/10791)
    - Add the feature of printing the `expensive query` log when a query exceeds the memory configuration limit [#10849](https://github.com/pingcap/tidb/pull/10849)
    - Add the `bind-info-lease` configuration item to control the update time of the modified binding execution plan [#10727](https://github.com/pingcap/tidb/pull/10727)
    - Fix the OOM issue in high concurrent scenarios caused by the failure to quickly release Coprocessor resources, resulted from the `execdetails.ExecDetails` pointer [#10832](https://github.com/pingcap/tidb/pull/10832)
    - Fix the panic issue caused by the `kill` statement in some cases [#10876](https://github.com/pingcap/tidb/pull/10876)

+ Server
    - Fix the issue that goroutine might leak when repairing GC [#10683](https://github.com/pingcap/tidb/pull/10683)
    - Support displaying the `host` information in slow queries [#10693](https://github.com/pingcap/tidb/pull/10693)
    - Support reusing idle links that interact with TiKV [#10632](https://github.com/pingcap/tidb/pull/10632)
    - Fix the support for enabling the `skip-grant-table` option in RBAC [#10738](https://github.com/pingcap/tidb/pull/10738)
    - Fix the issue that `pessimistic-txn` configuration goes invalid [#10825](https://github.com/pingcap/tidb/pull/10825)
    - Fix the issue that the actively canceled ticlient requests are still retried [#10850](https://github.com/pingcap/tidb/pull/10850)
    - Improve performance in the case where pessimistic transactions conflict with optimistic transactions [#10881](https://github.com/pingcap/tidb/pull/10881)

+ DDL
    - Fix the issue that modifying charset using `alter table` causes the `blob` type change [#10698](https://github.com/pingcap/tidb/pull/10698)
    - Add a feature to use `SHARD_ROW_ID_BITS` to scatter row IDs when the column contains an `AUTO_INCREMENT` attribute to alleviate the hotspot issue [#10794](https://github.com/pingcap/tidb/pull/10794)
    - Prohibit adding stored generated columns by using the `alter table` statement [#10808](https://github.com/pingcap/tidb/pull/10808)
    - Optimize the invalid survival time of DDL metadata to shorten the period during which the DDL operation is slower after cluster upgrade [#10795](https://github.com/pingcap/tidb/pull/10795)
