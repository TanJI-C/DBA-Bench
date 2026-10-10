# Bug fixes for TiKV, PD, TiFlash, and BR

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.6.md`
- Source Title: `TiDB 7.5.6 Release Notes`
- Source Heading Path: `TiDB 7.5.6 Release Notes > Bug fixes`
- Source Line Ranges: `81-125`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `tiflash`, `br`, `tidb`
- Topic Tags: `bug-fixes`, `region-split`, `leader-election`, `flow-control`, `1pc`, `async-commit`, `gc`, `cdc`, `region-merge`, `resolved-ts`, `upgrade`, `tso`, `memory-leak`, `network-stability`, `partitioned-table`, `raft`, `log-backup`, `pitr`, `restore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0550_7e157d8bb1`
- Source ID: `tidb-docs-8.1:releases/release-7.5.6.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6cd2d8189fafc0c32f209e8e3dd02080cb361e55ed10084d0316d831e1aa3e1b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.6 bug fixes across TiKV, PD, TiFlash, or BR for issues such as Region split leader election, RocksDB flow control, 1PC and Async Commit read visibility, GC Worker deadlock, Titan upgrade failure, `tidb_enable_tso_follower_proxy`, TSO allocation, TiFlash memory or Raft message handling, and BR log backup or restore errors.
- Retrieval Keywords: TiDB 7.5.6 bug fixes, TiKV leader could not be quickly elected after Region split, time rollback abnormal RocksDB flow control performance jitter, one-phase commit 1PC Async Commit latest written data might not be readable, GC Worker under heavy load deadlock, Region merge TiKV abnormal exit Raft index mismatch, Resolved-TS monitoring and logs abnormal, Titan component upgrade failure incompatibility, PD `max-size` single log file default value, PD `flow-round-by-digit` overwritten after a restart, unstable PD network data import adding index fail, `tidb_enable_tso_follower_proxy` PD panic, `tidb_enable_tso_follower_proxy` might not take effect, allocating TSOs memory leaks, PD Leader switch Region syncer might not exit in time, PD node still generate TSOs when not the Leader, TiFlash reject processing Raft messages when memory usage is low, TiFlash high memory usage after importing large amounts of data, partitioned table `ALTER TABLE ... RENAME COLUMN` query errors, `profiles.default.init_thread_count_scale` set to `0` startup blocked, `Not found column` virtual columns remote reads, disaggregated storage and compute architecture TiFlash compute nodes selected for adding Region peers, BR `rpcClient is idle` restore error, PITR restore indexes larger than 3072 bytes, `br log status --json` missing `status` field, log backup paused state advancer owner switches
- Follow-up Guidance: This chunk also includes BR fixes for log backup fatal errors when PD is inaccessible, `rpcClient is idle` during restore, PITR index restore limits, and `br log status --json` output.
- Classification Note: The official content is a TiDB 7.5.6 release-note bug-fix section covering multiple self-managed components: TiKV, PD, TiFlash, and Backup & Restore (BR).

## Official Source Content

- Fix the issue that the leader could not be quickly elected after Region split [#17602](https://github.com/tikv/tikv/issues/17602) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the issue that time rollback might cause abnormal RocksDB flow control, leading to performance jitter [#17995](https://github.com/tikv/tikv/issues/17995) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the issue that the latest written data might not be readable when only one-phase commit (1PC) is enabled and Async Commit is not enabled [#18117](https://github.com/tikv/tikv/issues/18117) @[zyguan](https://github.com/zyguan)
    - Fix the issue that TiKV converts the time zone incorrectly for Brazil and Egypt [#16220](https://github.com/tikv/tikv/issues/16220) @[overvenus](https://github.com/overvenus)
    - Fix the issue that a deadlock might occur when GC Worker is under heavy load [#18214](https://github.com/tikv/tikv/issues/18214) @[zyguan](https://github.com/zyguan)
    - Fix the issue that disk stalls might prevent leader migration, leading to performance jitter [#17363](https://github.com/tikv/tikv/issues/17363) @[hhwyt](https://github.com/hhwyt)
    - Fix the issue that encoding might fail when processing GBK/GB18030 encoded data [#17618](https://github.com/tikv/tikv/issues/17618) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Fix the issue that CDC connections might cause resource leakage when encountering exceptions [#18245](https://github.com/tikv/tikv/issues/18245) @[wlwilliamx](https://github.com/wlwilliamx)
    - Fix the issue that Region merge might lead to TiKV abnormal exit due to Raft index mismatch [#18129](https://github.com/tikv/tikv/issues/18129) @[glorv](https://github.com/glorv)
    - Fix the issue that Resolved-TS monitoring and logs might be abnormal [#17989](https://github.com/tikv/tikv/issues/17989) @[ekexium](https://github.com/ekexium)
    - Fix the issue that an incompatibility with the Titan component causes upgrade failure [#18263](https://github.com/tikv/tikv/issues/18263) @[v01dstar](https://github.com/v01dstar) @[LykxSassinator](https://github.com/LykxSassinator)
  
+ PD

    - Fix the issue that the default value of `max-size` for a single log file is not correctly set [#9037](https://github.com/tikv/pd/issues/9037) @[rleungx](https://github.com/rleungx)
    - Fix the issue that the value of the `flow-round-by-digit` configuration item might be overwritten after a restart [#8980](https://github.com/tikv/pd/issues/8980) @[nolouch](https://github.com/nolouch)
    - Fix the issue that operations in data import or adding index scenarios might fail due to unstable PD network [#8962](https://github.com/tikv/pd/issues/8962) @[okJiang](https://github.com/okJiang)
    - Fix the issue that PD might panic when the `tidb_enable_tso_follower_proxy` system variable is enabled [#8950](https://github.com/tikv/pd/issues/8950) @[okJiang](https://github.com/okJiang)
    - Fix the issue that the `tidb_enable_tso_follower_proxy` system variable might not take effect [#8947](https://github.com/tikv/pd/issues/8947) @[JmPotato](https://github.com/JmPotato)
    - Fix the issue that memory leaks might occur when allocating TSOs [#9004](https://github.com/tikv/pd/issues/9004) @[rleungx](https://github.com/rleungx)
    - Fix the issue that Region syncer might not exit in time during the PD Leader switch [#9017](https://github.com/tikv/pd/issues/9017) @[rleungx](https://github.com/rleungx)
    - Fix the issue that a PD node might still generate TSOs even when it is not the Leader [#9051](https://github.com/tikv/pd/issues/9051) @[rleungx](https://github.com/rleungx)

+ TiFlash

    - Fix the issue that TiFlash might unexpectedly reject processing Raft messages when memory usage is low [#9745](https://github.com/pingcap/tiflash/issues/9745) @[CalvinNeo](https://github.com/CalvinNeo)
    - Fix the issue that TiFlash might maintain high memory usage after importing large amounts of data [#9812](https://github.com/pingcap/tiflash/issues/9812) @[CalvinNeo](https://github.com/CalvinNeo)
    - Fix the issue that queries on a partitioned table might return errors after executing `ALTER TABLE ... RENAME COLUMN` on that partitioned table [#9787](https://github.com/pingcap/tiflash/issues/9787) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that TiFlash might fail to print error stack traces when it unexpectedly exits in certain situations [#9902](https://github.com/pingcap/tiflash/issues/9902) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash startup might be blocked when `profiles.default.init_thread_count_scale` is set to `0` [#9906](https://github.com/pingcap/tiflash/issues/9906) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that a `Not found column` error might occur when a query involves virtual columns and triggers remote reads [#9561](https://github.com/pingcap/tiflash/issues/9561) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that in the disaggregated storage and compute architecture, TiFlash compute nodes might be incorrectly selected as target nodes for adding Region peers [#9750](https://github.com/pingcap/tiflash/issues/9750) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that log backup fails to exit properly when encountering a fatal error due to not being able to access PD [#18087](https://github.com/tikv/tikv/issues/18087) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that BR fails to restore due to getting the `rpcClient is idle` error when sending requests to TiKV [#58845](https://github.com/pingcap/tidb/issues/58845) @[Tristan1900](https://github.com/Tristan1900)
        - Fix the issue that PITR fails to restore indexes larger than 3072 bytes [#58430](https://github.com/pingcap/tidb/issues/58430) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that the `status` field is missing in the result when querying log backup tasks using `br log status --json` [#57959](https://github.com/pingcap/tidb/issues/57959) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that log backup might unexpectedly enter a paused state when the advancer owner switches [#58031](https://github.com/pingcap/tidb/issues/58031) @[3pointer](https://github.com/3pointer)

    + TiCDC
