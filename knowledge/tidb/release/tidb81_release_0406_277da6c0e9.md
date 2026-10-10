# Bug fixes for TiKV, PD, TiFlash, and BR

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.6.md`
- Source Title: `TiDB 6.5.6 Release Notes`
- Source Heading Path: `TiDB 6.5.6 Release Notes > Bug fixes`
- Source Line Ranges: `101-152`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `tiflash`, `br`, `tidb`, `cloud`
- Topic Tags: `bug-fixes`, `security`, `follower-read`, `resolved-ts`, `raft`, `dr-auto-sync`, `grafana`, `titan`, `flashback`, `placement-rules`, `log-backup`, `pitr`, `oom`, `external-storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0406_277da6c0e9`
- Source ID: `tidb-docs-8.1:releases/release-6.5.6.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3ac43424eef80b0a502203d43273499aea2a9fc814d320cf6c21e1d351647db5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.6.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.5.6 bug fixes across TiKV, PD, TiFlash, and BR for issues involving follower read, resolved-ts, DR Auto-Sync, placement rules, Grafana metrics, log backup, PITR, OOM, external storage, or related security fixes.
- Retrieval Keywords: TiDB 6.5.6 bug fixes, TiKV Follower Read performance deteriorate moving a peer, #15468, raftstore-applys continuously increasing data error, #15371, TiDB Lightning checksum coprocessor time out online workload, #15565, lz4-sys 1.9.4 security issues, #15621, tokio 6.5 security issues, #15621, remove flatbuffer security issues, #15621, resolved-ts lag increases TiKV stores are partitioned, #15679, TiKV OOM restarting TiKV large number of Raft logs not applied, #15770, stale peers retained block resolved-ts after Regions are merged, #15919, scheduler command variables incorrect in Grafana cloud environment, #15832, blob-run-mode Titan cannot be updated online, #15978, TiKV panics inconsistent metadata between Regions, #13311, leader forced to exit during Online Unsafe Recovery panic, #15629, joint state of DR Auto-Sync might time out when scaling out, #15817, TiKV coprocessor return stale data when removing a Raft peer, #16069, resolved-ts might be blocked for 2 hours, #39130, Flashback stuck notLeader regionNotFound, #15712, PD plugin directory and files security risks, #7094, modified isolation levels not synchronized to the default placement rules, #7121, evict-leader-scheduler might lose configuration, #6897, counting empty Regions might cause Regions to be unbalanced during the recovery process of BR, #7148, canSync hasMajority calculated incorrectly DR Auto-Sync Placement Rules, #7201, available_stores calculated incorrectly DR Auto-Sync, #7221, primary AZ cannot add TiKV nodes when the secondary AZ is down DR Auto-Sync, #7218, adding multiple TiKV nodes to a large cluster heartbeat reporting slow or stuck, #7248, PD might delete normal Peers when TiKV nodes are unavailable, #7249, switch the leader in DR Auto-Sync mode takes a long time, #6988, Gin Web Framework v1.9.1 security issues, #7438, TiFlash max_snapshot_lifetime metric displayed incorrectly on Grafana, #7713, ALTER TABLE EXCHANGE PARTITION causes panic TiFlash, #8372, MemoryTracker memory usage inaccurate TiFlash, #8128, log backup stuck backing up large wide tables, #15714, frequent flushes cause log backup to get stuck, #15602, EC2 metadata connection reset degraded backup and restore performance, #47650, running PITR multiple times within 1 minute might cause data loss, #15483, default values for BR SQL commands and CLI are different OOM issues, #48000, log backup panic when the PD owner is transferred, #47533, BR generates incorrect URIs for external storage files, #48452
- Follow-up Guidance: The source groups the fixes by component as TiKV, PD, TiFlash, and Tools > Backup & Restore (BR), which helps narrow retrieval to a specific subsystem.
- Classification Note: This chunk is classified as a release note because it enumerates bug fixes in TiDB 6.5.6 for multiple components and specific issue identifiers.

## Official Source Content

- Fix the issue that moving a peer might cause the performance of the Follower Read to deteriorate [#15468](https://github.com/tikv/tikv/issues/15468) @[YuJuncen](https://github.com/YuJuncen)
    - Fix the data error of continuously increasing raftstore-applys [#15371](https://github.com/tikv/tikv/issues/15371) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that requests of the TiDB Lightning checksum coprocessor time out when there is online workload [#15565](https://github.com/tikv/tikv/issues/15565) @[lance6716](https://github.com/lance6716)
    - Fix security issues by upgrading the version of `lz4-sys` to 1.9.4  [#15621](https://github.com/tikv/tikv/issues/15621) @[SpadeA-Tang](https://github.com/SpadeA-Tang)
    - Fix security issues by upgrading the version of `tokio` to 6.5 [#15621](https://github.com/tikv/tikv/issues/15621) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix security issues by removing the `flatbuffer` [#15621](https://github.com/tikv/tikv/issues/15621) @[tonyxuqqi](https://github.com/tonyxuqqi)
    - Fix the issue that resolved-ts lag increases when TiKV stores are partitioned [#15679](https://github.com/tikv/tikv/issues/15679) @[hicqu](https://github.com/hicqu)
    - Fix the TiKV OOM issue that occurs when restarting TiKV and there are a large number of Raft logs that are not applied [#15770](https://github.com/tikv/tikv/issues/15770) @[overvenus](https://github.com/overvenus)
    - Fix the issue that stale peers are retained and block resolved-ts after Regions are merged [#15919](https://github.com/tikv/tikv/issues/15919) @[overvenus](https://github.com/overvenus)
    - Fix the issue that the scheduler command variables are incorrect in Grafana on the cloud environment [#15832](https://github.com/tikv/tikv/issues/15832) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that `blob-run-mode` in Titan cannot be updated online [#15978](https://github.com/tikv/tikv/issues/15978) @[tonyxuqqi](https://github.com/tonyxuqqi)
    - Fix the issue that TiKV panics due to inconsistent metadata between Regions [#13311](https://github.com/tikv/tikv/issues/13311) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the issue that TiKV panics when the leader is forced to exit during Online Unsafe Recovery [#15629](https://github.com/tikv/tikv/issues/15629) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that the joint state of DR Auto-Sync might time out when scaling out [#15817](https://github.com/tikv/tikv/issues/15817) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that TiKV coprocessor might return stale data when removing a Raft peer [#16069](https://github.com/tikv/tikv/issues/16069) @[overvenus](https://github.com/overvenus)
    - Fix the issue that resolved-ts might be blocked for 2 hours [#39130](https://github.com/pingcap/tidb/issues/39130) @[overvenus](https://github.com/overvenus)
    - Fix the issue that Flashback might get stuck when encountering `notLeader` or `regionNotFound` [#15712](https://github.com/tikv/tikv/issues/15712) @[HuSharp](https://github.com/HuSharp)

+ PD

    - Fix potential security risks of the plugin directory and files [#7094](https://github.com/tikv/pd/issues/7094) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that modified isolation levels are not synchronized to the default placement rules [#7121](https://github.com/tikv/pd/issues/7121) @[rleungx](https://github.com/rleungx)
    - Fix the issue that `evict-leader-scheduler` might lose configuration [#6897](https://github.com/tikv/pd/issues/6897) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that the method for counting empty Regions might cause Regions to be unbalanced during the recovery process of BR [#7148](https://github.com/tikv/pd/issues/7148) @[Cabinfever](https://github.com/CabinfeverB)
    - Fix the issue that `canSync` and `hasMajority` might be calculated incorrectly for clusters adopting the Data Replication Auto Synchronous (DR Auto-Sync) mode when the configuration of Placement Rules is complex [#7201](https://github.com/tikv/pd/issues/7201) @[disksing](https://github.com/disksing)
    - Fix the issue that `available_stores` is calculated incorrectly for clusters adopting the Data Replication Auto Synchronous (DR Auto-Sync) mode [#7221](https://github.com/tikv/pd/issues/7221) @[disksing](https://github.com/disksing)
    - Fix the issue that the primary AZ cannot add TiKV nodes when the secondary AZ is down for clusters adopting the Data Replication Auto Synchronous (DR Auto-Sync) mode [#7218](https://github.com/tikv/pd/issues/7218) @[disksing](https://github.com/disksing)
    - Fix the issue that adding multiple TiKV nodes to a large cluster might cause TiKV heartbeat reporting to become slow or stuck [#7248](https://github.com/tikv/pd/issues/7248) @[rleungx](https://github.com/rleungx)
    - Fix the issue that PD might delete normal Peers when TiKV nodes are unavailable [#7249](https://github.com/tikv/pd/issues/7249) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that it takes a long time to switch the leader in DR Auto-Sync mode [#6988](https://github.com/tikv/pd/issues/6988) @[HuSharp](https://github.com/HuSharp)
    - Upgrade the version of Gin Web Framework from v1.8.1 to v1.9.1 to fix some security issues [#7438](https://github.com/tikv/pd/issues/7438) @[niubell](https://github.com/niubell)

+ TiFlash

    - Fix the issue that the `max_snapshot_lifetime` metric is displayed incorrectly on Grafana [#7713](https://github.com/pingcap/tiflash/issues/7713) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that executing the `ALTER TABLE ... EXCHANGE PARTITION ...` statement causes panic [#8372](https://github.com/pingcap/tiflash/issues/8372) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that the memory usage reported by MemoryTracker is inaccurate [#8128](https://github.com/pingcap/tiflash/issues/8128) @[JinheLin](https://github.com/JinheLin)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that the log backup might get stuck in some scenarios when backing up large wide tables [#15714](https://github.com/tikv/tikv/issues/15714) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that frequent flushes cause log backup to get stuck [#15602](https://github.com/tikv/tikv/issues/15602) @[3pointer](https://github.com/3pointer)
        - Fix the issue that the retry after an EC2 metadata connection reset cause degraded backup and restore performance [#47650](https://github.com/pingcap/tidb/issues/47650) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that running PITR multiple times within 1 minute might cause data loss [#15483](https://github.com/tikv/tikv/issues/15483) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that the default values for BR SQL commands and CLI are different, which might cause OOM issues [#48000](https://github.com/pingcap/tidb/issues/48000) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that log backup might panic when the PD owner is transferred [#47533](https://github.com/pingcap/tidb/issues/47533) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that BR generates incorrect URIs for external storage files [#48452](https://github.com/pingcap/tidb/issues/48452) @[3AceShowHand](https://github.com/3AceShowHand)

    + TiCDC
