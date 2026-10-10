# TiDB 2.1 RC5 release notes across TiDB, PD, TiKV, and Tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1-rc.5.md`
- Source Title: `TiDB 2.1 RC5 Release Notes`
- Source Heading Path: `TiDB 2.1 RC5 Release Notes | TiDB 2.1 RC5 Release Notes > TiDB | TiDB 2.1 RC5 Release Notes > PD | TiDB 2.1 RC5 Release Notes > TiKV | TiDB 2.1 RC5 Release Notes > Tools`
- Source Line Ranges: `5-63`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `ecosystem`
- Topic Tags: `release-notes`, `stability`, `sql-optimizer`, `execution-engine`, `statistics`, `server`, `ddl`, `pd-ctl`, `region`, `api`, `restart`, `leader-watch`, `write-conflict`, `grpc`, `kv-scan`, `binlog-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0054_08d1bb9039`
- Source ID: `tidb-docs-8.1:releases/release-2.1-rc.5.md#tidb-2-1-rc5-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8938cc0e9abf1dce9f03081437efebbaf51d719bb8aa02ad14f32bc22f0d81a3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1-rc.5#tidb-2-1-rc5-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1-rc.5.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 2.1 RC5 release-note summary and the specific fixes or additions across TiDB, PD, TiKV, and Tools.
- Retrieval Keywords: TiDB 2.1 RC5 Release Notes, TiDB 2.1 RC5, IndexReader reads the wrong handle, IndexScan Prepared, Plan Cache, Union statement is unstable, wide tables, Truncate built-in function, JSON data to the decimal type, Update the float type, incorrect statistics during point queries, selectivity estimation of statistics for primary key, statistics of deleted tables are not cleared up, infoschema.profiling, pumps client to write binlogs, tidb_slow_log_threshold, tidb_query_log_max_len, tidb_opt_write_row_id, _tidb_rowid, Scan command of ticlient, truncate table in partition tables, admin show next_row_id, pd-ctl reading the Region key, regions/check API returns the wrong result, PD cannot restart join after a PD join failure, watch leader might lose events, WriteConflict, panic mark file, grpcio, segment fault, kv_scan interface, TiDB-Binlog cluster, not compatible with the older version of binlog
- Follow-up Guidance: The source groups the changes by TiDB, PD, TiKV, and Tools and names exact items such as `tidb_slow_log_threshold`, `tidb_query_log_max_len`, `tidb_opt_write_row_id`, `admin show next_row_id`, `regions/check`, `WriteConflict`, and `kv_scan` for more targeted lookup.
- Classification Note: This is a self-managed release-notes chunk for TiDB 2.1 RC5 that catalogs stability, optimizer, statistics, execution engine, server, DDL, PD, TiKV, and Tools changes from the official release content.

## Official Source Content

# TiDB 2.1 RC5 Release Notes

On November 12, 2018, TiDB 2.1 RC5 is released. Compared with TiDB 2.1 RC4, this release has great improvement in stability, SQL optimizer, statistics information, and execution engine.
## TiDB

+ SQL Optimizer
    - Fix the issue that `IndexReader` reads the wrong handle in some cases [#8132](https://github.com/pingcap/tidb/pull/8132)
    - Fix the issue occurred while the `IndexScan Prepared` statement uses `Plan Cache` [#8055](https://github.com/pingcap/tidb/pull/8055)
    - Fix the issue that the result of the `Union` statement is unstable [#8165](https://github.com/pingcap/tidb/pull/8165)
+ SQL Execution Engine
    - Improve the performance of TiDB on inserting or updating wide tables [#8024](https://github.com/pingcap/tidb/pull/8024)
    - Support the unsigned `int` flag in the `Truncate` built-in function [#8068](https://github.com/pingcap/tidb/pull/8068)
    - Fix the error occurred while converting JSON data to the decimal type [#8109](https://github.com/pingcap/tidb/pull/8109)
    - Fix the error occurred when you `Update` the float type [#8170](https://github.com/pingcap/tidb/pull/8170)
+ Statistics
    - Fix the incorrect statistics issue during point queries in some cases [#8035](https://github.com/pingcap/tidb/pull/8035)
    - Fix the selectivity estimation of statistics for primary key in some cases [#8149](https://github.com/pingcap/tidb/pull/8149)
    - Fix the issue that the statistics of deleted tables are not cleared up for a long period of time [#8182](https://github.com/pingcap/tidb/pull/8182)
+ Server
    + Improve the readability of logs and make logs better
        - [#8063](https://github.com/pingcap/tidb/pull/8063)
        - [#8053](https://github.com/pingcap/tidb/pull/8053)
        - [#8224](https://github.com/pingcap/tidb/pull/8224)
    - Fix the error occurred when obtaining the table data of `infoschema.profiling` [#8096](https://github.com/pingcap/tidb/pull/8096)
    - Replace the unix socket with the pumps client to write binlogs [#8098](https://github.com/pingcap/tidb/pull/8098)
    - Add the threshold value for the `tidb_slow_log_threshold` environment variable, which dynamically sets the slow log [#8094](https://github.com/pingcap/tidb/pull/8094)
    - Add the original length of a SQL statement truncated while the `tidb_query_log_max_len` environment variable dynamically sets logs [#8200](https://github.com/pingcap/tidb/pull/8200)
    - Add the `tidb_opt_write_row_id` environment variable to control whether to allow writing `_tidb_rowid` [#8218](https://github.com/pingcap/tidb/pull/8218)
    - Add an upper bound to the `Scan` command of ticlient, to avoid overbound scan [#8081](https://github.com/pingcap/tidb/pull/8081), [#8247](https://github.com/pingcap/tidb/pull/8247)
+ DDL
    - Fix the issue that executing DDL statements in transactions encounters an error in some cases [#8056](https://github.com/pingcap/tidb/pull/8056)
    - Fix the issue that executing `truncate table` in partition tables does not take effect [#8103](https://github.com/pingcap/tidb/pull/8103)
    - Fix the issue that the DDL operation does not roll back correctly after being cancelled in some cases [#8057](https://github.com/pingcap/tidb/pull/8057)
    - Add the `admin show next_row_id` command to return the next available row ID [#8268](https://github.com/pingcap/tidb/pull/8268)
## PD

+ Fix the issues related to `pd-ctl` reading the Region key
    - [#1298](https://github.com/pingcap/pd/pull/1298)
    - [#1299](https://github.com/pingcap/pd/pull/1299)
    - [#1308](https://github.com/pingcap/pd/pull/1308)
+ Fix the issue that the `regions/check` API returns the wrong result [#1311](https://github.com/pingcap/pd/pull/1311)
+ Fix the issue that PD cannot restart join after a PD join failure [#1279](https://github.com/pingcap/pd/pull/1279)
+ Fix the issue that `watch leader` might lose events in some cases [#1317](https://github.com/pingcap/pd/pull/1317)
## TiKV

+ Improve the error message of `WriteConflict` [#3750](https://github.com/tikv/tikv/pull/3750)
+ Add the panic mark file [#3746](https://github.com/tikv/tikv/pull/3746)
+ Downgrade grpcio to avoid the segment fault issue caused by the new version of gRPC [#3650](https://github.com/tikv/tikv/pull/3650)
+ Add an upper limit to the `kv_scan` interface [#3749](https://github.com/tikv/tikv/pull/3749)
## Tools

- Support the TiDB-Binlog cluster, which is not compatible with the older version of binlog [#8093](https://github.com/pingcap/tidb/pull/8093), [documentation](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview)
