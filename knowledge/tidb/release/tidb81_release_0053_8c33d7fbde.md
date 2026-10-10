# TiDB 2.1 RC4 release notes across TiDB, PD, and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1-rc.4.md`
- Source Title: `TiDB 2.1 RC4 Release Notes`
- Source Heading Path: `TiDB 2.1 RC4 Release Notes | TiDB 2.1 RC4 Release Notes > TiDB | TiDB 2.1 RC4 Release Notes > PD | TiDB 2.1 RC4 Release Notes > TiKV`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `release-notes`, `stability`, `sql-optimizer`, `execution-engine`, `statistics`, `server`, `compatibility`, `expressions`, `ddl`, `grafana`, `etcd`, `leader-switching`, `rocksdb`, `raftstore`, `grpcio`, `metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0053_8c33d7fbde`
- Source ID: `tidb-docs-8.1:releases/release-2.1-rc.4.md#tidb-2-1-rc4-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0a3bba341d8d926fb151c6ca6f5ce0bad9d26732dbd97e1ac2b9ef7689853d29`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1-rc.4#tidb-2-1-rc4-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1-rc.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 2.1 RC4 release notes and the specific fixes and improvements across TiDB, PD, and TiKV.
- Retrieval Keywords: TiDB 2.1 RC4 Release Notes, TiDB 2.1 RC4, EXPLAIN ANALYZE, UnionAll column pruning, UnionAll result incorrect, AVG precision issue, PointGet panic, Limit subclause panic, AddDate SubDate panic, histogram low-bound combined index, statistics collecting memory leak, histogram empty panic, statistics sampling maximum length, Latch transaction conflicts, slow queries panic, LOAD DATA ESCAPED BY empty string, coprocessor error log information, SHOW PROCESSLIST Command Sleep, SYSDATE constant folding, SUBSTRING_INDEX panics, invalid ddl job type, ADMIN CHECK TABLE incorrect, tombstone TiKV Grafana, etcd startup failure, leader switching data race, RocksDB Write stall applying snapshots, raftstore tick metrics, IngestExternalFile, grpcio too many pings
- Follow-up Guidance: The source groups the changes by TiDB, PD, and TiKV and names the affected statements, functions, metrics, errors, and subsystems in each section.
- Classification Note: This is a self-managed release-notes chunk summarizing stability, SQL optimizer, statistics, execution engine, compatibility, DDL, PD, and TiKV changes in TiDB 2.1 RC4.

## Official Source Content

# TiDB 2.1 RC4 Release Notes

On October 23, 2018, TiDB 2.1 RC4 is released. Compared with TiDB 2.1 RC3, this release has great improvement in stability, SQL optimizer, statistics information, and execution engine.
## TiDB

+ SQL Optimizer
    - Fix the issue that column pruning of `UnionAll` is incorrect in some cases [#7941](https://github.com/pingcap/tidb/pull/7941)
    - Fix the issue that the result of the `UnionAll` operator is incorrect in some cases [#8007](https://github.com/pingcap/tidb/pull/8007)
+ SQL Execution Engine
    - Fix the precision issue of the `AVG` function [#7874](https://github.com/pingcap/tidb/pull/7874)
    - Support using the `EXPLAIN ANALYZE` statement to check the runtime statistics including the execution time and the number of returned rows of each operator during the query execution process [#7925](https://github.com/pingcap/tidb/pull/7925)
    - Fix the panic issue of the `PointGet` operator when a column of a table appears multiple times in the result set [#7943](https://github.com/pingcap/tidb/pull/7943)
    - Fix the panic issue caused by too large values in the `Limit` subclause [#8002](https://github.com/pingcap/tidb/pull/8002)
    - Fix the panic issue during the execution process of the `AddDate`/`SubDate` statement in some cases [#8009](https://github.com/pingcap/tidb/pull/8009)
+ Statistics
    - Fix the issue of judging the prefix of the histogram low-bound of the combined index as out of range [#7856](https://github.com/pingcap/tidb/pull/7856)
    - Fix the memory leak issue caused by statistics collecting [#7873](https://github.com/pingcap/tidb/pull/7873)
    - Fix the panic issue when the histogram is empty [#7928](https://github.com/pingcap/tidb/pull/7928)
    - Fix the issue that the histogram bound is out of range when the statistics is being uploaded [#7944](https://github.com/pingcap/tidb/pull/7944)
    - Limit the maximum length of values in the statistics sampling process [#7982](https://github.com/pingcap/tidb/pull/7982)
+ Server
    - Refactor Latch to avoid misjudgment of transaction conflicts and improve the execution performance of concurrent transactions [#7711](https://github.com/pingcap/tidb/pull/7711)
    - Fix the panic issue caused by collecting slow queries in some cases [#7874](https://github.com/pingcap/tidb/pull/7847)
    - Fix the panic issue when `ESCAPED BY` is an empty string in the `LOAD DATA` statement [#8005](https://github.com/pingcap/tidb/pull/8005)
    - Complete the "coprocessor error" log information [#8006](https://github.com/pingcap/tidb/pull/8006)
+ Compatibility
    - Set the `Command` field of the `SHOW PROCESSLIST` result to `Sleep` when the query is empty [#7839](https://github.com/pingcap/tidb/pull/7839)
+ Expressions
    - Fix the constant folding issue of the `SYSDATE` function [#7895](https://github.com/pingcap/tidb/pull/7895)
    - Fix the issue that `SUBSTRING_INDEX` panics in some cases [#7897](https://github.com/pingcap/tidb/pull/7897)
+ DDL
    - Fix the stack overflow issue caused by throwing the `invalid ddl job type` error [#7958](https://github.com/pingcap/tidb/pull/7958)
    - Fix the issue that the result of `ADMIN CHECK TABLE` is incorrect in some cases [#7975](https://github.com/pingcap/tidb/pull/7975)
## PD

- Fix the issue that the tombstone TiKV is not removed from Grafana [#1261](https://github.com/pingcap/pd/pull/1261)
- Fix the data race issue when grpc-go configures the status [#1265](https://github.com/pingcap/pd/pull/1265)
- Fix the issue that the PD server gets stuck caused by etcd startup failure [#1267](https://github.com/pingcap/pd/pull/1267)
- Fix the issue that data race might occur during leader switching [#1273](https://github.com/pingcap/pd/pull/1273)
- Fix the issue that extra warning logs might be output when TiKV becomes tombstone [#1280](https://github.com/pingcap/pd/pull/1273)
## TiKV

- Optimize the RocksDB Write stall issue caused by applying snapshots [#3606](https://github.com/tikv/tikv/pull/3606)
- Add raftstore `tick` metrics [#3657](https://github.com/tikv/tikv/pull/3657)
- Upgrade RocksDB and fix the Write block issue and that the source file might be damaged by the Write operation when performing `IngestExternalFile` [#3661](https://github.com/tikv/tikv/pull/3661)
- Upgrade grpcio and fix the issue that "too many pings" is wrongly reported [#3650](https://github.com/tikv/tikv/pull/3650)
