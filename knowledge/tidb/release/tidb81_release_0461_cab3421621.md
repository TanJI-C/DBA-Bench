# Bug fixes across TiDB, TiKV, PD, and TiFlash

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.2.md`
- Source Title: `TiDB 7.1.2 Release Notes`
- Source Heading Path: `TiDB 7.1.2 Release Notes > Bug fixes`
- Source Line Ranges: `119-167`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `lightning`
- Topic Tags: `bug-fixes`, `query-correctness`, `raftstore`, `replication`, `unsafe-recovery`, `pitr`, `region-merge`, `heartbeat`, `encryption`, `checksum`, `follower-read`, `scheduling`, `tls`, `panic`, `resource-control`, `oom`, `memory-usage`, `mpp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0461_cab3421621`
- Source ID: `tidb-docs-8.1:releases/release-7.1.2.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `44dd7187b8dfc967a189025f1bdb72ac08d1345ee59f6b0676ff31a0e08eb02e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.2 bug fixes related to query correctness, TiKV replication and recovery behavior, PD scheduling and panic issues, or TiFlash memory, consistency, and MPP query problems.
- Retrieval Keywords: TiDB 7.1.2 Release Notes bug fixes, UNHEX inaccurate query results, Can't find column GROUP_CONCAT, ttl-check-poll-interval RawKV API V2, raftstore-applys data error, Data Replication Auto Synchronous sync-recover QPS drops to zero, Online Unsafe Recovery merge abort, Online Unsafe Recovery does not abort on timeout, PITR stuck network interruption between PD and TiKV, Region Merge blocked after FLASHBACK, heartbeat storms store heartbeat retries, encryption partial write data corruption, TiKV panic incorrect metadata of Region, TiDB Lightning checksum coprocessor time out online workload, Follower Read performance deteriorate moving a peer, hot Regions not scheduled v2 scheduler algorithm, TLS handshake high CPU usage empty cluster, PD panic injection errors between PD nodes, Region information is not updated after Flashback, lease timeout error context timeout, evict-leader-scheduler lose configuration, RU consumption less than 0 causes PD to crash, min-resolved-ts might cause PD OOM, MemoryTracker inaccurate memory usage, TiFlash data inconsistent invalid range keys, fsp changed DATETIME TIMESTAMP TIME queries fail, multiple HashAgg operators same MPP task compilation excessively long
- Follow-up Guidance: This release note groups the fixes by component: TiDB, TiKV, PD, TiFlash, and Tools.
- Classification Note: The chunk is classified as a release note because it enumerates bug fixes in TiDB 7.1.2 across multiple components and issue-specific symptoms.

## Official Source Content

- Fix the issue that query results are inaccurate when queries contain `UNHEX` conditions [#45378](https://github.com/pingcap/tidb/issues/45378) @[qw4990](https://github.com/qw4990)
    - Fix the issue that TiDB returns `Can't find column` for queries with `GROUP_CONCAT` [#41957](https://github.com/pingcap/tidb/issues/41957) @[AilinKid](https://github.com/AilinKid)

+ TiKV

    - Fix the issue that the `ttl-check-poll-interval` configuration item does not take effect on RawKV API V2 [#15142](https://github.com/tikv/tikv/issues/15142) @[pingyu](https://github.com/pingyu)
    - Fix the data error of continuously increasing raftstore-applys [#15371](https://github.com/tikv/tikv/issues/15371) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that the QPS drops to zero in the sync-recover phase under the Data Replication Auto Synchronous mode [#14975](https://github.com/tikv/tikv/issues/14975) @[nolouch](https://github.com/nolouch)
    - Fix the data inconsistency issue that might occur when one TiKV node is isolated and another node is restarted [#15035](https://github.com/tikv/tikv/issues/15035) @[overvenus](https://github.com/overvenus)
    - Fix the issue that Online Unsafe Recovery cannot handle merge abort [#15580](https://github.com/tikv/tikv/issues/15580) @[v01dstar](https://github.com/v01dstar)
    - Fix the issue that network interruption between PD and TiKV might cause PITR to get stuck [#15279](https://github.com/tikv/tikv/issues/15279) @[YuJuncen](https://github.com/YuJuncen)
    - Fix the issue that Region Merge might be blocked after executing `FLASHBACK` [#15258](https://github.com/tikv/tikv/issues/15258) @[overvenus](https://github.com/overvenus)
    - Fix the issue of heartbeat storms by reducing the number of store heartbeat retries [#15184](https://github.com/tikv/tikv/issues/15184) @[nolouch](https://github.com/nolouch)
    - Fix the issue that Online Unsafe Recovery does not abort on timeout [#15346](https://github.com/tikv/tikv/issues/15346) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that encryption might cause data corruption during partial write [#15080](https://github.com/tikv/tikv/issues/15080) @[tabokie](https://github.com/tabokie)
    - Fix the TiKV panic issue caused by incorrect metadata of Region [#13311](https://github.com/tikv/tikv/issues/13311) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the issue that requests of the TiDB Lightning checksum coprocessor time out when there is online workload [#15565](https://github.com/tikv/tikv/issues/15565) @[lance6716](https://github.com/lance6716)
    - Fix the issue that moving a peer might cause the performance of the Follower Read to deteriorate [#15468](https://github.com/tikv/tikv/issues/15468) @[YuJuncen](https://github.com/YuJuncen)

+ PD

    - Fix the issue that hot Regions might not be scheduled in the v2 scheduler algorithm [#6645](https://github.com/tikv/pd/issues/6645) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that the TLS handshake might cause high CPU usage in an empty cluster [#6913](https://github.com/tikv/pd/issues/6913) @[nolouch](https://github.com/nolouch)
    - Fix the issue that injection errors between PD nodes might cause PD panic [#6858](https://github.com/tikv/pd/issues/6858) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that store information synchronization might cause the PD leader to exit and get stuck [#6918](https://github.com/tikv/pd/issues/6918) @[rleungx](https://github.com/rleungx)
    - Fix the issue that the Region information is not updated after Flashback [#6912](https://github.com/tikv/pd/issues/6912) @[overvenus](https://github.com/overvenus)
    - Fix the issue that PD might panic during exiting [#7053](https://github.com/tikv/pd/issues/7053) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that the context timeout might cause the `lease timeout` error [#6926](https://github.com/tikv/pd/issues/6926) @[rleungx](https://github.com/rleungx)
    - Fix the issue that peers are not properly scattered by group, which might cause uneven distribution of leaders [#6962](https://github.com/tikv/pd/issues/6962) @[rleungx](https://github.com/rleungx)
    - Fix the issue that the isolation level label is not synchronized when updating using pd-ctl [#7121](https://github.com/tikv/pd/issues/7121) @[rleungx](https://github.com/rleungx)
    - Fix the issue that `evict-leader-scheduler` might lose configuration [#6897](https://github.com/tikv/pd/issues/6897) @[HuSharp](https://github.com/HuSharp)
    - Fix potential security risks of the plugin directory and files [#7094](https://github.com/tikv/pd/issues/7094) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that DDL might not guarantee atomicity after enabling resource control [#45050](https://github.com/pingcap/tidb/issues/45050) @[glorv](https://github.com/glorv)
    - Fix the issue that unhealthy peers cannot be removed when rule checker selects peers [#6559](https://github.com/tikv/pd/issues/6559) @[nolouch](https://github.com/nolouch)
    - Fix the issue that when etcd is already started but the client has not yet connected to it, calling the client might cause PD to panic [#6860](https://github.com/tikv/pd/issues/6860) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that RU consumption less than 0 causes PD to crash [#6973](https://github.com/tikv/pd/issues/6973) @[CabinfeverB](https://github.com/CabinfeverB)
    - Fix the issue that the client-go regularly updating `min-resolved-ts` might cause PD OOM when the cluster is large [#46664](https://github.com/pingcap/tidb/issues/46664) @[HuSharp](https://github.com/HuSharp)

+ TiFlash

    - Fix the issue that the memory usage reported by MemoryTracker is inaccurate [#8128](https://github.com/pingcap/tiflash/issues/8128) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that TiFlash data is inconsistent due to invalid range keys of a region [#7762](https://github.com/pingcap/tiflash/issues/7762) @[lidezhu](https://github.com/lidezhu)
    - Fix the issue that queries fail after `fsp` is changed for `DATETIME`, `TIMESTAMP`, or `TIME` data type [#7809](https://github.com/pingcap/tiflash/issues/7809) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that when there are multiple HashAgg operators within the same MPP task, the compilation of the MPP task might take an excessively long time, severely affecting query performance [#7810](https://github.com/pingcap/tiflash/issues/7810) @[SeaRise](https://github.com/SeaRise)

+ Tools

    + Backup & Restore (BR)
