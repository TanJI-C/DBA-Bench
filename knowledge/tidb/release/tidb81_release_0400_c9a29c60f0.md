# 6.5.4 bug fixes across TiDB, TiKV, PD, TiFlash, and BR

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.4.md`
- Source Title: `TiDB 6.5.4 Release Notes`
- Source Heading Path: `TiDB 6.5.4 Release Notes > Bug fixes`
- Source Line Ranges: `112-161`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`
- Topic Tags: `bug-fixes`, `stability`, `configuration`, `memory`, `oom`, `data-consistency`, `unsafe-recovery`, `flashback`, `pitr`, `backup`, `restore`, `replication`, `query-performance`, `heartbeat`, `traffic-control`, `encryption`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0400_c9a29c60f0`
- Source ID: `tidb-docs-8.1:releases/release-6.5.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `41dfd144713b33f69648a06096df12d0b9d032d296e355b9bb61112d1f9c53e8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.4 bug fixes across TiDB, TiKV, PD, TiFlash, and BR for issues involving specific configuration items, stability problems, data consistency, PITR, backup and restore, unsafe recovery, or query performance.
- Retrieval Keywords: TiDB 6.5.4 bug fixes, tmp-storage-quota does not take effect, killing a connection go coroutine leaks, Config.Labels data race, TiFlash replicas unavailable when a TiFlash node is down, min-resolved-ts PD OOM, ttl-check-poll-interval RawKV API V2, Online Unsafe Recovery does not abort on timeout, Region Merge blocked after FLASHBACK, data inconsistency isolated TiKV node restarted, QPS drops to zero sync-recover Data Replication Auto Synchronous, encryption data corruption partial write, heartbeat storms store heartbeat retries, traffic control pending compaction bytes, network interruption PD TiKV PITR stuck, Old Value TiCDC enabled more memory, PD panic etcd already started client not yet connected, leader cannot exit for a long time, LOCATION_LABELS SQL and Rule Checker not compatible, PD unexpectedly add multiple Learners, unhealthy peers cannot be removed rule checker selects peers, unsafe recovery auto-detect failed learner peers ignored, TiFlash queries fail after fsp is changed, TiFlash invalid range keys region data inconsistent, multiple HashAgg operators same MPP task compilation excessively long, TiFlash restart too long after Online Unsafe Recovery, TiFlash DECIMAL division rounding incorrectly, BR restore failures TableColumnCountLimit IndexLimit, PITR rewrite failures DDL meta information, PITR panic not checking function returns, invalid region ID S3-compatible storage other than Amazon S3, fine-grained backup phase RawKV mode, resolve lock frequency too high when there is no PITR backup task, PITR log backup progress latency leadership migration
- Follow-up Guidance: The source groups these fixes under TiDB, TiKV, PD, TiFlash, and Tools > Backup & Restore (BR).
- Classification Note: This is a release-note bug-fix summary for TiDB 6.5.4 covering multiple shared components and issue-specific fixes listed in the official content.

## Official Source Content

- Fix the issue that killing a connection might cause go coroutine leaks [#46034](https://github.com/pingcap/tidb/issues/46034) @[pingyu](https://github.com/pingyu)
    - Fix the issue that the `tmp-storage-quota` configuration does not take effect [#45161](https://github.com/pingcap/tidb/issues/45161) [#26806](https://github.com/pingcap/tidb/issues/26806) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that TiFlash replicas might be unavailable when a TiFlash node is down in the cluster [#38484](https://github.com/pingcap/tidb/issues/38484) @[hehechen](https://github.com/hehechen)
    - Fix the issue that TiDB crashes due to possible data race when reading and writing `Config.Labels` concurrently [#45561](https://github.com/pingcap/tidb/issues/45561) @[genliqi](https://github.com/gengliqi)
    - Fix the issue that the client-go regularly updating `min-resolved-ts` might cause PD OOM when the cluster is large [#46664](https://github.com/pingcap/tidb/issues/46664) @[HuSharp](https://github.com/HuSharp)

+ TiKV

    - Fix the issue that the `ttl-check-poll-interval` configuration item does not take effect on RawKV API V2 [#15142](https://github.com/tikv/tikv/issues/15142) @[pingyu](https://github.com/pingyu)
    - Fix the issue that Online Unsafe Recovery does not abort on timeout [#15346](https://github.com/tikv/tikv/issues/15346) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that Region Merge might be blocked after executing `FLASHBACK` [#15258](https://github.com/tikv/tikv/issues/15258) @[overvenus](https://github.com/overvenus)
    - Fix the data inconsistency issue that might occur when one TiKV node is isolated and another node is restarted [#15035](https://github.com/tikv/tikv/issues/15035) @[overvenus](https://github.com/overvenus)
    - Fix the issue that the QPS drops to zero in the sync-recover phase under the Data Replication Auto Synchronous mode [#14975](https://github.com/tikv/tikv/issues/14975) @[nolouch](https://github.com/nolouch)
    - Fix the issue that encryption might cause data corruption during partial write [#15080](https://github.com/tikv/tikv/issues/15080) @[tabokie](https://github.com/tabokie)
    - Fix the issue of heartbeat storms by reducing the number of store heartbeat retries [#15184](https://github.com/tikv/tikv/issues/15184) @[nolouch](https://github.com/nolouch)
    - Fix the issue that traffic control might not work when there is a high amount of pending compaction bytes [#14392](https://github.com/tikv/tikv/issues/14392) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that network interruption between PD and TiKV might cause PITR to get stuck [#15279](https://github.com/tikv/tikv/issues/15279) @[YuJuncen](https://github.com/YuJuncen)
    - Fix the issue that TiKV might consume more memory when the Old Value feature in TiCDC is enabled [#14815](https://github.com/tikv/tikv/issues/14815) @[YuJuncen](https://github.com/YuJuncen)

+ PD

    - Fix the issue that when etcd is already started but the client has not yet connected to it, calling the client might cause PD to panic [#6860](https://github.com/tikv/pd/issues/6860) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that a leader cannot exit for a long time [#6918](https://github.com/tikv/pd/issues/6918) @[bufferflies](https://github.com/bufferflies)
    - Fix the issue that when the placement rule uses `LOCATION_LABELS`, SQL and the Rule Checker are not compatible [#38605](https://github.com/pingcap/tidb/issues/38605) @[nolouch](https://github.com/nolouch)
    - Fix the issue that PD might unexpectedly add multiple Learners to a Region [#5786](https://github.com/tikv/pd/issues/5786) @[HunDunDM](https://github.com/HunDunDM)
    - Fix the issue that unhealthy peers cannot be removed when rule checker selects peers [#6559](https://github.com/tikv/pd/issues/6559) @[nolouch](https://github.com/nolouch)
    - Fix the issue that failed learner peers in `unsafe recovery` are ignored in `auto-detect` mode [#6690](https://github.com/tikv/pd/issues/6690) @[v01dstar](https://github.com/v01dstar)

+ TiFlash 

    - Fix the issue that queries fail after `fsp` is changed for `DATETIME`, `TIMESTAMP`, or `TIME` data type [#7809](https://github.com/pingcap/tiflash/issues/7809) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash data is inconsistent due to invalid range keys of a region [#7762](https://github.com/pingcap/tiflash/issues/7762) @[lidezhu](https://github.com/lidezhu)
    - Fix the issue that when there are multiple HashAgg operators within the same MPP task, the compilation of the MPP task might take an excessively long time, severely affecting query performance [#7810](https://github.com/pingcap/tiflash/issues/7810) @[SeaRise](https://github.com/SeaRise)
    - Fix the issue that TiFlash takes too long to restart after using Online Unsafe Recovery [#7671](https://github.com/pingcap/tiflash/issues/7671) @[hongyunyan](https://github.com/hongyunyan)
    - Fix the issue that TiFlash rounds the `DECIMAL` result incorrectly when doing division [#6462](https://github.com/pingcap/tiflash/issues/6462) @[LittleFall](https://github.com/LittleFall)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue of restore failures by increasing the default values of the global parameters `TableColumnCountLimit` and `IndexLimit` used by BR to their maximum values [#45793](https://github.com/pingcap/tidb/issues/45793) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue of rewrite failures when processing DDL meta information in PITR [#43184](https://github.com/pingcap/tidb/issues/43184) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue of panic caused by not checking function returns during PITR execution [#45853](https://github.com/pingcap/tidb/issues/45853) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue of obtaining invalid region ID when using S3-compatible storage other than Amazon S3 [#41916](https://github.com/pingcap/tidb/issues/41916) [#42033](https://github.com/pingcap/tidb/issues/42033) @[3pointer](https://github.com/3pointer)
        - Fix the potential error in fine-grained backup phase in RawKV mode [#37085](https://github.com/pingcap/tidb/issues/37085) @[pingyu](https://github.com/pingyu)
        - Fix the issue that the frequency of `resolve lock` is too high when there is no PITR backup task in the TiDB cluster [#40759](https://github.com/pingcap/tidb/issues/40759) @[joccau](https://github.com/joccau)
        - Alleviate the issue that the latency of the PITR log backup progress increases when Region leadership migration occurs [#13638](https://github.com/tikv/tikv/issues/13638) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC
