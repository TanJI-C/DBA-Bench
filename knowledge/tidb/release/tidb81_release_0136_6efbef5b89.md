# TiDB 3.1.0 GA release notes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.1.0-ga.md`
- Source Title: `TiDB 3.1.0 GA Release Notes`
- Source Heading Path: `TiDB 3.1.0 GA Release Notes | TiDB 3.1.0 GA Release Notes > Compatibility Changes | TiDB 3.1.0 GA Release Notes > New Features | TiDB 3.1.0 GA Release Notes > Bug Fixes`
- Source Line Ranges: `5-93`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tiflash`, `tikv`, `br`
- Topic Tags: `release-notes`, `compatibility`, `new-features`, `bug-fixes`, `ansible`, `coprocessor`, `hot-region-scheduling`, `monitoring`, `panic-fix`, `data-loss`, `restore`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0136_6efbef5b89`
- Source ID: `tidb-docs-8.1:releases/release-3.1.0-ga.md#tidb-3-1-0-ga-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1b3da73cc3c65a06bf9a683875940a870d2eff8096781d3d21105ef6f68f70bb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.1.0-ga#tidb-3-1-0-ga-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.1.0-ga.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 3.1.0 GA release notes covering compatibility changes, new features, and bug fixes across TiDB, PD, TiFlash, TiKV, TiDB Ansible, TiDB Binlog, and BR.
- Retrieval Keywords: TiDB 3.1.0 GA Release Notes, release date April 16, 2020, TiDB Ansible 3.1.0 GA, report-status, HTTP listening port is unavailable, BR does not support restoring data from the TiKV cluster earlier than 3.1 GA, explain format = "dot", Coprocessor tasks, disable-error-stack, hot Region scheduling, DeltaTree engine metrics, fromUnixTime, dateFormat, Disable the rough set filter by default, Add TiFlash monitor, merge join panic, fast analyze panic, current_role, monitoring session retry errors, ALLOW_INVALID_DATES, weekday, Garbage Collection (GC) might not work normally when the cluster has TiFlash nodes, hash partitioned table OOM, UNION statement, TopN pushed down to mocktikv, replica read panic, restoration process creates empty Regions, resolve lock requests, pessimistic transactions, rename table data loss, TiFlash-related DDL jobs might interrupt the replication of Drainer, checksum operation is still executed when it is disabled, incremental backup fails when TiDB enables auto-random or alter-pk
- Follow-up Guidance: The source also lists exact affected components and issue areas under Compatibility Changes, New Features, and Bug Fixes for TiDB 3.1.0 GA.
- Classification Note: This chunk is classified as a release note because the official content announces TiDB 3.1.0 GA and enumerates compatibility changes, new features, and bug fixes for multiple components.

## Official Source Content

# TiDB 3.1.0 GA Release Notes

Release date: April 16, 2020

TiDB version: 3.1.0 GA

TiDB Ansible version: 3.1.0 GA
## Compatibility Changes

+ TiDB

    - Support directly stopping starting TiDB if the HTTP listening port is unavailable when the `report-status` configuration item is enabled [#16291](https://github.com/pingcap/tidb/pull/16291)

+ Tools

    - Backup & Restore (BR)

        * BR does not support restoring data from the TiKV cluster earlier than 3.1 GA [#233](https://github.com/pingcap/br/pull/233)
## New Features

+ TiDB

    - Support displaying the information of Coprocessor tasks in `explain format = "dot"` [#16125](https://github.com/pingcap/tidb/pull/16125)
    - Reduce the redundant stack information of log using the `disable-error-stack` configuration item [#16182](https://github.com/pingcap/tidb/pull/16182)

+ Placement Driver (PD)

    - Optimize the hot Region scheduling [#2342](https://github.com/pingcap/pd/pull/2342)

+ TiFlash

    - Add the metrics report related to the read and write workloads of DeltaTree engine
    - Support pushing down the `fromUnixTime` and `dateFormat` functions
    - Disable the rough set filter by default

+ TiDB Ansible

    - Add TiFlash monitor [#1253](https://github.com/pingcap/tidb-ansible/pull/1253) [#1257](https://github.com/pingcap/tidb-ansible/pull/1257)
    - Optimize the configuration parameters of TiFlash [#1262](https://github.com/pingcap/tidb-ansible/pull/1262) [#1265](https://github.com/pingcap/tidb-ansible/pull/1265) [#1271](https://github.com/pingcap/tidb-ansible/pull/1271)
    - Optimize the TiDB starting script [#1268](https://github.com/pingcap/tidb-ansible/pull/1268)
## Bug Fixes

+ TiDB

    - Fix the panic issue caused by the merge join operation in some scenarios [#15920](https://github.com/pingcap/tidb/pull/15920)
    - Fix the issue that some expressions are repeatedly counted in selectivity calculation [#16052](https://github.com/pingcap/tidb/pull/16052)
    - Fix the panic issue occurred when loading the statistics information in extreme cases [#15710](https://github.com/pingcap/tidb/pull/15710)
    - Fix the issue that an error is returned in some cases when equivalent expressions cannot be recognized in SQL query [#16015](https://github.com/pingcap/tidb/pull/16015)
    - Fix the issue that an error is returned when querying the `view` of one database from another database [#15867](https://github.com/pingcap/tidb/pull/15867)
    - Fix the panic issue that occurs when the column is handled using `fast analyze` [#16080](https://github.com/pingcap/tidb/pull/16080)
    - Fix the incorrect character set of the `current_role` print result [#16084](https://github.com/pingcap/tidb/pull/16084)
    - Refine the log of MySQL connection handshake error [#15799](https://github.com/pingcap/tidb/pull/15799)
    - Fix the panic issue caused by port probing after the audit plugin is loaded [#16065](https://github.com/pingcap/tidb/pull/16065)
    - Fix the panic issue of the `sort` operator on left join because the `TypeNull` class is mistaken as a variable-length type [#15739](https://github.com/pingcap/tidb/pull/15739)
    - Fix the issue of inaccurate count of monitoring session retry errors [#16120](https://github.com/pingcap/tidb/pull/16120)
    - Fix the issue of wrong results of `weekday` in the `ALLOW_INVALID_DATES` mode [#16171](https://github.com/pingcap/tidb/pull/16171)
    - Fix the issue that Garbage Collection (GC) might not work normally when the cluster has TiFlash nodes [#15761](https://github.com/pingcap/tidb/pull/15761)
    - Fix the issue that TiDB goes out of memory (OOM) when users set a large partition count when creating the hash partitioned table [#16219](https://github.com/pingcap/tidb/pull/16219)
    - Fix the issue that warnings are mistaken as errors, and make the `UNION` statement have the same behavior as the `SELECT` statement [#16138](https://github.com/pingcap/tidb/pull/16138)
    - Fix the execution error when `TopN` is pushed down to mocktikv [#16200](https://github.com/pingcap/tidb/pull/16200)
    - Increase the initial length of `chunk.column.nullBitMap` to avoid unnecessary overhead of `runtime.growslice` [#16142](https://github.com/pingcap/tidb/pull/16142)

+ TiKV

    - Fix the panic issue caused by replica read [#7418](https://github.com/tikv/tikv/pull/7418) [#7369](https://github.com/tikv/tikv/pull/7369)
    - Fix the issue that the restoration process creates empty Regions [#7419](https://github.com/tikv/tikv/pull/7419)
    - Fix the issue that repeated resolve lock requests might harm the atomicity of pessimistic transactions [#7389](https://github.com/tikv/tikv/pull/7389)

+ TiFlash

    - Fix the potential issue of the `rename table` operation when replicating the schema from TiDB
    - Fix the issue of data loss caused by the `rename table` operation under multiple data path configurations
    - Fix the issue that TiFlash reports incorrect storage space in some scenarios
    - Fix the potential issue caused by reading from TiFlash when Region Merge is enabled

+ Tools

    - TiDB Binlog

        * Fix the issue that TiFlash-related DDL jobs might interrupt the replication of Drainer [#948](https://github.com/pingcap/tidb-binlog/pull/948) [#942](https://github.com/pingcap/tidb-binlog/pull/942)

    - Backup & Restore (BR)

        * Fix the issue that the `checksum` operation is still executed when it is disabled [#223](https://github.com/pingcap/br/pull/223)
        * Fix the issue that incremental backup fails when TiDB enables `auto-random` or `alter-pk` [#230](https://github.com/pingcap/br/pull/230) [#231](https://github.com/pingcap/br/pull/231)
