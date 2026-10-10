# Bug fixes for TiDB, TiKV, and PD

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.1.md`
- Source Title: `TiDB 7.5.1 Release Notes`
- Source Heading Path: `TiDB 7.5.1 Release Notes > Bug fixes`
- Source Line Ranges: `150-181`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `bug-fixes`, `statistics`, `cte`, `panic`, `timezone`, `titan`, `flashback`, `region-merge`, `dr-auto-sync`, `resolved-ts`, `resource-groups`, `systemd`, `leader-election`, `network-partition`, `monitoring`, `security`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0528_e39d0cc7fd`
- Source ID: `tidb-docs-8.1:releases/release-7.5.1.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fdaed3ee96654450d416fac952ff169f127ea2e37d465ab9f09b613f4dafb1ab`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.1#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.1 bug fixes across TiDB, TiKV, and PD involving statistics, CTE errors, panics, timezone conversion, Flashback, Region merge, DR Auto-Sync, Resolved TS, resource groups, systemd startup, leader election, network partition, monitoring, or security.
- Retrieval Keywords: TiDB 7.5.1 Bug fixes, excessive statistical error constructing statistics, Golang implicit conversion algorithm, queries containing CTEs, runtime error: index out of range [32] with length 32, tidb_max_chunk_size, tidb_enable_row_level_checksum, TiKV panic, gRPC threads checking is_shutdown, Brazil and Egypt time zone incorrectly, blob-run-mode Titan cannot be updated online, DECIMAL arithmetic multiplication truncation inconsistent results, Flashback stuck notLeader regionNotFound, damaged SST files spread to other TiKV nodes, panic after Region merge, DR Auto-Sync joint state time out when scaling out, Resolved TS blocked for two hours, cast_duration_as_time incorrect results, TiKV hangs disk I/O operations are blocked, querying resource groups in batch cause PD to panic, started with systemd cannot read resource limitations, PD disk latency fail to select a new leader, network partition in PD scheduling not started immediately, learner-peer-count old value after a leader switch, PD leader transferred PD client fails to update leader information, Gin Web Framework v1.8.1 to v1.9.1, orphan peer is deleted when number of replicas does not meet the requirements, querying a Region without a leader using pd-ctl might cause PD to panic
- Follow-up Guidance: 
- Classification Note: This is a self-managed release-notes bug-fix chunk summarizing fixes in the shared TiDB, TiKV, and PD components for TiDB 7.5.1.

## Official Source Content

- Fix the issue of excessive statistical error in constructing statistics caused by Golang's implicit conversion algorithm [#49801](https://github.com/pingcap/tidb/issues/49801) @[qw4990](https://github.com/qw4990)
    - Fix the issue that queries containing CTEs report `runtime error: index out of range [32] with length 32` when `tidb_max_chunk_size` is set to a small value [#48808](https://github.com/pingcap/tidb/issues/48808) @[guo-shaoge](https://github.com/guo-shaoge)

+ TiKV

    - Fix the issue that enabling `tidb_enable_row_level_checksum` might cause TiKV to panic [#16371](https://github.com/tikv/tikv/issues/16371) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the issue that TiKV might panic when gRPC threads are checking `is_shutdown` [#16236](https://github.com/tikv/tikv/issues/16236) @[pingyu](https://github.com/pingyu)
    - Fix the issue that TiKV converts the time zone incorrectly for Brazil and Egypt [#16220](https://github.com/tikv/tikv/issues/16220) @[overvenus](https://github.com/overvenus)
    - Fix the issue that `blob-run-mode` in Titan cannot be updated online [#15978](https://github.com/tikv/tikv/issues/15978) @[tonyxuqqi](https://github.com/tonyxuqqi)
    - Fix the issue that TiDB and TiKV might produce inconsistent results when processing `DECIMAL` arithmetic multiplication truncation [#16268](https://github.com/tikv/tikv/issues/16268) @[solotzg](https://github.com/solotzg)
    - Fix the issue that Flashback might get stuck when encountering `notLeader` or `regionNotFound` [#15712](https://github.com/tikv/tikv/issues/15712) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that damaged SST files might be spread to other TiKV nodes [#15986](https://github.com/tikv/tikv/issues/15986) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that if TiKV runs extremely slowly, it might panic after Region merge [#16111](https://github.com/tikv/tikv/issues/16111) @[overvenus](https://github.com/overvenus)
    - Fix the issue that the joint state of DR Auto-Sync might time out when scaling out [#15817](https://github.com/tikv/tikv/issues/15817) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that Resolved TS might be blocked for two hours [#11847](https://github.com/tikv/tikv/issues/11847) [#15520](https://github.com/tikv/tikv/issues/15520) [#39130](https://github.com/pingcap/tidb/issues/39130) @[overvenus](https://github.com/overvenus)
    - Fix the issue that `cast_duration_as_time` might return incorrect results [#16211](https://github.com/tikv/tikv/issues/16211) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that TiKV hangs in corner cases (for example, when disk I/O operations are blocked), which affects availability [#16368](https://github.com/tikv/tikv/issues/16368) @[LykxSassinator](https://github.com/LykxSassinator)

+ PD

    - Fix the issue that querying resource groups in batch might cause PD to panic [#7206](https://github.com/tikv/pd/issues/7206) @[nolouch](https://github.com/nolouch)
    - Fix the issue that PD cannot read resource limitations when it is started with `systemd` [#7628](https://github.com/tikv/pd/issues/7628) @[bufferflies](https://github.com/bufferflies)
    - Fix the issue that continuous jitter in PD disk latency might cause PD to fail to select a new leader [#7251](https://github.com/tikv/pd/issues/7251) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that a network partition in PD might cause scheduling not to be started immediately [#7016](https://github.com/tikv/pd/issues/7016) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that the PD monitoring item `learner-peer-count` does not synchronize the old value after a leader switch [#7728](https://github.com/tikv/pd/issues/7728) @[CabinfeverB](https://github.com/CabinfeverB)
    - Fix the issue that when PD leader is transferred and there is a network partition between the new leader and the PD client, the PD client fails to update the information of the leader [#7416](https://github.com/tikv/pd/issues/7416) @[CabinfeverB](https://github.com/CabinfeverB)
    - Fix some security issues by upgrading the version of Gin Web Framework from v1.8.1 to v1.9.1 [#7438](https://github.com/tikv/pd/issues/7438) @[niubell](https://github.com/niubell)
    - Fix the issue that the orphan peer is deleted when the number of replicas does not meet the requirements [#7584](https://github.com/tikv/pd/issues/7584) @[bufferflies](https://github.com/bufferflies)
    - Fix the issue that querying a Region without a leader using `pd-ctl` might cause PD to panic [#7630](https://github.com/tikv/pd/issues/7630) @[rleungx](https://github.com/rleungx)

+ TiFlash
