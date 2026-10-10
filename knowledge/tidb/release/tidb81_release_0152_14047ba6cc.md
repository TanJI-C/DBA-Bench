# RC.1 bug fixes across TiDB, TiKV, PD, and TiFlash

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.0-rc.1.md`
- Source Title: `TiDB 4.0 RC.1 Release Notes`
- Source Heading Path: `TiDB 4.0 RC.1 Release Notes > Bug Fixes`
- Source Line Ranges: `101-148`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`
- Topic Tags: `release-notes`, `bug-fixes`, `security`, `tls`, `plan-cache`, `index-merge`, `partition-pruning`, `follower-read`, `region-merge`, `grpc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0152_14047ba6cc`
- Source ID: `tidb-docs-8.1:releases/release-4.0.0-rc.1.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7a6a88754959fc0173dfdf7748f6703ea67e07ba93a4df69aa3e8d13d902eca6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.0-rc.1#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.0-rc.1.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 4.0 RC.1 bug fixes for specific SQL errors, plan cache and Index Merge problems, TLS and API issues, follower read and region merge bugs, or TiFlash gRPC and Region handling fixes.
- Retrieval Keywords: Bug Fixes, use_index_merge, explain for connection, plan cache, tidb_capture_plan_baselines, group by, prepare statement, analyze primary key, cluster_info, Index Merge, show create table, sequence default values, StaleCommand, COLLATE, SHOW CREATE DATABASE, partition pruning, PointGet, slow_query, CVE-2020-1967, BatchRollback, write conflicts, multi-time merging, learner is not deleted, follower read, group by constant, optimistic lock, TLS validation, configuration API, scheduler not found, balance-hot-region-scheduler list, coarse-grained index optimization, resolving locks for Regions, Coprocessor statistics, Region Split, Region Merge, gRPC, Coprocessor response, AdminCmdType::Split
- Follow-up Guidance: The chunk is organized by component and enumerates bug fixes for TiDB, TiKV, PD, and TiFlash in RC.1.
- Classification Note: This is a bug-fix release chunk because the official content is a component-by-component list of resolved issues and errors in TiDB 4.0 RC.1.

## Official Source Content

## Bug Fixes

+ TiDB

- Fix the issue that negative numbers cannot be correctly displayed in the system table because the columns are defined as unsigned [#16004](https://github.com/pingcap/tidb/pull/16004)
- Add a warning when the `use_index_merge` hint contains the invalid index name [#15960](https://github.com/pingcap/tidb/pull/15960)
- Forbid multiple instances of a TiDB server sharing the same temporary directory [#16026](https://github.com/pingcap/tidb/pull/16026)
- Fix the panic that occurs during the execution of `explain for connection` when the plan cache is enabled [#16285](https://github.com/pingcap/tidb/pull/16285)
- Fix the issue that the result of the `tidb_capture_plan_baselines` system variable is incorrectly displayed [#16048](https://github.com/pingcap/tidb/pull/16048)
- Fix the issue that the `group by` clause in the `prepare` statement is incorrectly parsed [#16377](https://github.com/pingcap/tidb/pull/16377)
- Fix the panic that might occur during the execution of the `analyze primary key` statement [#16081](https://github.com/pingcap/tidb/pull/16081)
- Fix the issue that the TiFlash store information in the `cluster_info` system table is wrong [#16024](https://github.com/pingcap/tidb/pull/16024)
- Fix the panic that might occur during the Index Merge process [#16360](https://github.com/pingcap/tidb/pull/16360)
- Fix the issue that an incorrect result might occur when the Index Merge reader reads the generated columns [#16359](https://github.com/pingcap/tidb/pull/16359)
- Fix the incorrect display of the default sequence value in the `show create table` statement [#16526](https://github.com/pingcap/tidb/pull/16526)
- Fix the issue that the `not-null` error is returned because the sequence is used as the default values of the primary key [#16510](https://github.com/pingcap/tidb/pull/16510)
- Fix the issue that no error is reported for a blocked SQL execution when TiKV continues to return the `StaleCommand` error [#16530](https://github.com/pingcap/tidb/pull/16530)
- Fix the issue that an error is reported if you only specify `COLLATE` when creating a database; add the missing `COLLATE` part in the result of `SHOW CREATE DATABASE` [#16540](https://github.com/pingcap/tidb/pull/16540)
- Fix the partition pruning failure when the plan cache is enabled [#16723](https://github.com/pingcap/tidb/pull/16723)
- Fix the bug that `PointGet` returns wrong results when handling the overflow [#16755](https://github.com/pingcap/tidb/pull/16755)
- Fix the issue that a wrong result is returned when querying the `slow_query` system table with equal time values [#16806](https://github.com/pingcap/tidb/pull/16806)

+ TiKV

    - Address the OpenSSL security issue: CVE-2020-1967 [#7622](https://github.com/tikv/tikv/pull/7622)
    - Avoid protecting rollback records written by `BatchRollback` to improve performance when many write conflicts exist in optimistic transactions [#7604](https://github.com/tikv/tikv/pull/7604)
    - Fix the issue that the needless wake-up of transactions results in useless retry and performance reduction in heavy lock-race workloads [#7551](https://github.com/tikv/tikv/pull/7551)
    - Fix the issue that the Region might be stuck in the multi-time merging [#7518](https://github.com/tikv/tikv/pull/7518)
    - Fix the issue that the learner is not deleted when deleting the learner [#7518](https://github.com/tikv/tikv/pull/7518)
    - Fix the issue that follower read might cause panic in raft-rs [#7408](https://github.com/tikv/tikv/pull/7408)
    - Fix the bug that a SQL operation might fail because of the `group by constant` error [#7383](https://github.com/tikv/tikv/pull/7383)
    - Fix the issue that an optimistic lock might block reads if the corresponding primary lock is a pessimistic lock [#7328](https://github.com/tikv/tikv/pull/7328)

+ PD

    - Fix the issue that some APIs might fail in the TLS validation [#2363](https://github.com/pingcap/pd/pull/2363)
    - Fix the issue that the configuration API cannot accept a configuration item with a prefix [#2354](https://github.com/pingcap/pd/pull/2354)
    - Fix the issue that the `500` error is returned when the scheduler is not found [#2328](https://github.com/pingcap/pd/pull/2328)
    - Fix the issue that the `404` error is returned for the `scheduler config balance-hot-region-scheduler list` command [#2321](https://github.com/pingcap/pd/pull/2321)

+ TiFlash

    - Disable the coarse-grained index optimization for the storage engine
    - Fix the bug that an exception is thrown when resolving locks for Regions and some locks need to be skipped
    - Fix the null pointer exception (NPE) when collecting the Coprocessor statistics
    - Fix the check for Region meta to ensure that the process of Region Split/Region Merge is correct
    - Fix the issue that the message size exceeds the limit for gRPC because the size of Coprocessor response is not estimated
    - Fix the handling of the `AdminCmdType::Split` command in TiFlash
