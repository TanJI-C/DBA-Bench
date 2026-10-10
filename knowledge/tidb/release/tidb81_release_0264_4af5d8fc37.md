# TiDB 5.3.2 release notes: warning, compatibility changes, improvements, and bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.3.2.md`
- Source Title: `TiDB 5.3.2 Release Notes`
- Source Heading Path: `TiDB 5.3.2 Release Notes | TiDB 5.3.2 Release Notes > Compatibility Changes | TiDB 5.3.2 Release Notes > Improvements | TiDB 5.3.2 Release Notes > Bug Fixes`
- Source Line Ranges: `5-94`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `tiflash`, `dm`, `lightning`, `ticdc`
- Topic Tags: `release-notes`, `version-warning`, `compatibility-changes`, `improvements`, `bug-fixes`, `known-bug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0264_4af5d8fc37`
- Source ID: `tidb-docs-8.1:releases/release-5.3.2.md#tidb-5-3-2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `37681434123fc4f7131c12e53635ede8a3764762516f1a7a358c856c4f468f41`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.3.2#tidb-5-3-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.3.2.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 5.3.2 release notes for the version warning, compatibility changes, improvements, and bug fixes across TiDB, PD, TiKV, DM, and TiDB Lightning.
- Retrieval Keywords: TiDB 5.3.2 Release Notes, v5.3.2 known bug, #12934, v5.3.3, Compatibility Changes, Improvements, Bug Fixes, REPLACE statement auto ID out of range, #29483, Disable compiling swagger server by default, #4932, Raft client CPU efficiency, #11309, health check unavailable Raftstore Region Cache, #12398, CDC observer latency jitter, #12111, Raft logs garbage collection metrics, #11374, DM-worker working directory Syncer /tmp, #4107, TiDB Lightning Scatter Region batch mode, #33618, Amazon S3 compressed data size, #30534, data and columnID count not match, #33608, INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY OOM, #33893, fatal error: concurrent map read and map write, #35340, invalid store ID 0 Follower Read, #12478, Write Conflict poor network optimistic transactions, #34066, PD leader transfer scheduling, #4769, SchedulerMaxWaitingOperator set to 1, #4946
- Follow-up Guidance: The source also states that v5.3.2 has a known bug referenced by #12934 and that this bug is fixed in v5.3.3.
- Classification Note: This is a self-managed release-notes chunk for TiDB 5.3.2 that summarizes warning information, compatibility changes, improvements, and bug fixes for multiple components.

## Official Source Content

# TiDB 5.3.2 Release Notes

Release Date: June 29, 2022

TiDB version: 5.3.2

> **Warning:**
>
> It is not recommended to use v5.3.2, because this version has a known bug. For details, see [#12934](https://github.com/tikv/tikv/issues/12934). This bug has been fixed in v5.3.3. It is recommended to use [v5.3.3](https://docs.pingcap.com/tidb/stable/releases/release-5.3.3).
## Compatibility Changes

+ TiDB

    - Fix the issue that the `REPLACE` statement incorrectly changes other rows when the auto ID is out of range [#29483](https://github.com/pingcap/tidb/issues/29483)

+ PD

    - Disable compiling swagger server by default [#4932](https://github.com/tikv/pd/issues/4932)
## Improvements

+ TiKV

    - Reduce the system call by the Raft client and increase CPU efficiency [#11309](https://github.com/tikv/tikv/issues/11309)
    - Improve the health check to detect unavailable Raftstore, so that the TiKV client can update Region Cache in time [#12398](https://github.com/tikv/tikv/issues/12398)
    - Transfer the leadership to CDC observer to reduce latency jitter [#12111](https://github.com/tikv/tikv/issues/12111)
    - Add more metrics for the garbage collection module of Raft logs to locate performance problems in the module [#11374](https://github.com/tikv/tikv/issues/11374)

+ Tools

    + TiDB Data Migration (DM)

        - Support Syncer using the working directory of the DM-worker rather than `/tmp` to write internal files, and cleaning the directory after the task is stopped [#4107](https://github.com/pingcap/tiflow/issues/4107)

    + TiDB Lightning

        - Optimize Scatter Region to batch mode to improve the stability of the Scatter Region process [#33618](https://github.com/pingcap/tidb/issues/33618)
## Bug Fixes

+ TiDB

    - Fix the issue that Amazon S3 cannot correctly calculate the size of compressed data [#30534](https://github.com/pingcap/tidb/issues/30534)
    - Fix the issue of potential data index inconsistency in optimistic transaction mode [#30410](https://github.com/pingcap/tidb/issues/30410)
    - Fix the issue that a SQL operation is canceled when its JSON type column joins its `CHAR` type column [#29401](https://github.com/pingcap/tidb/issues/29401)
    - Previously, when a network connectivity issue occurred, TiDB did not always correctly free the resources held by the disconnected session. This issue has been fixed so that open transactions can be rolled back and other associated resources can be released. [#34722](https://github.com/pingcap/tidb/issues/34722)
    - Fix the issue of the `data and columnID count not match` error that occurs when inserting duplicated values with TiDB Binlog enabled [#33608](https://github.com/pingcap/tidb/issues/33608)
    - Fix the issue that query result might be wrong when Plan Cache is started in the RC isolation level [#34447](https://github.com/pingcap/tidb/issues/34447)
    - Fix the session panic that occurs when executing the prepared statement after table schema change with the MySQL binary protocol [#33509](https://github.com/pingcap/tidb/issues/33509)
    - Fix the issue that the table attributes are not indexed when a new partition is added and the issue that the table range information is not updated when the partition changes [#33929](https://github.com/pingcap/tidb/issues/33929)
    - Fix the issue that the TiDB server might run out of memory when the `INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY` table is queried. This issue can be triggered when you check slow queries on the Grafana dashboard [#33893](https://github.com/pingcap/tidb/issues/33893)
    - Fix the issue that some DDL statements might be stuck for a period after the PD node of a cluster is replaced [#33908](https://github.com/pingcap/tidb/issues/33908)
    - Fix the issue that granting the `all` privilege might fail in clusters that are upgraded from v4.0 [#33588](https://github.com/pingcap/tidb/issues/33588)
    - Fix wrong results of deleting data of multiple tables using `left join` [#31321](https://github.com/pingcap/tidb/issues/31321)
    - Fix a bug that TiDB may dispatch duplicate tasks to TiFlash [#32814](https://github.com/pingcap/tidb/issues/32814)
    - Fix the issue that the background HTTP service of TiDB might not exit successfully and makes the cluster in an abnormal state [#30571](https://github.com/pingcap/tidb/issues/30571)
    - Fix the panic issue caused by the `fatal error: concurrent map read and map write` error [#35340](https://github.com/pingcap/tidb/issues/35340)

+ TiKV

    - Fix the issue of frequent PD client reconnection that occurs when the PD client meets an error [#12345](https://github.com/tikv/tikv/issues/12345)
    - Fix the issue of time parsing error that occurs when the `DATETIME` values contain a fraction and `Z` [#12739](https://github.com/tikv/tikv/issues/12739)
    - Fix the issue that TiKV panics when performing type conversion for an empty string [#12673](https://github.com/tikv/tikv/issues/12673)
    - Fix the possible duplicate commit records in pessimistic transactions when async commit is enabled [#12615](https://github.com/tikv/tikv/issues/12615)
    - Fix the bug that TiKV reports the `invalid store ID 0` error when using Follower Read [#12478](https://github.com/tikv/tikv/issues/12478)
    - Fix the issue of TiKV panic caused by the race between destroying peers and batch splitting Regions [#12368](https://github.com/tikv/tikv/issues/12368)
    - Fix the issue that successfully committed optimistic transactions may report the `Write Conflict` error when the network is poor [#34066](https://github.com/pingcap/tidb/issues/34066)
    - Fix the issue that TiKV panics and destroys peers unexpectedly when the target Region to be merged is invalid [#12232](https://github.com/tikv/tikv/issues/12232)
    - Fix a bug that stale messages cause TiKV to panic [#12023](https://github.com/tikv/tikv/issues/12023)
    - Fix the issue of intermittent packet loss and out of memory (OOM) caused by the overflow of memory metrics [#12160](https://github.com/tikv/tikv/issues/12160)
    - Fix the potential panic issue that occurs when TiKV performs profiling on Ubuntu 18.04 [#9765](https://github.com/tikv/tikv/issues/9765)
    - Fix the issue that tikv-ctl returns an incorrect result due to its wrong string match [#12329](https://github.com/tikv/tikv/issues/12329)
    - Fix a bug that replica reads might violate the linearizability [#12109](https://github.com/tikv/tikv/issues/12109)
    - Fix the TiKV panic issue that occurs when the target peer is replaced with the peer that is destroyed without being initialized when merging a Region [#12048](https://github.com/tikv/tikv/issues/12048)
    - Fix a bug that TiKV might panic if it has been running for 2 years or more [#11940](https://github.com/tikv/tikv/issues/11940)

+ PD

    - Fix the PD panic that occurs when a hot region has no leader [#5005](https://github.com/tikv/pd/issues/5005)
    - Fix the issue that scheduling cannot start immediately after the PD leader transfer [#4769](https://github.com/tikv/pd/issues/4769)
    - Fix the issue that a removed tombstone store appears again after the PD leader transfer ​​[#4941](https://github.com/tikv/pd/issues/4941)
    - Fix a bug of TSO fallback in some corner cases [#4884](https://github.com/tikv/pd/issues/4884)
    - Fix the issue that when there exists a Store with large capacity (2T for example), fully allocated small Stores cannot be detected, which results in no balance operator being generated [#4805](https://github.com/tikv/pd/issues/4805)
    - Fix the issue that schedulers do not work when `SchedulerMaxWaitingOperator` is set to `1` [#4946](https://github.com/tikv/pd/issues/4946)
    - Fix the issue that the label distribution has residual labels in the metrics [#4825](https://github.com/tikv/pd/issues/4825)

+ TiFlash
