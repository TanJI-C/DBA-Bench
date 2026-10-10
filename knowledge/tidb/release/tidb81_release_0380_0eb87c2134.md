# Bug fixes across TiDB, TiKV, PD, TiFlash, BR, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.10.md`
- Source Title: `TiDB 6.5.10 Release Notes`
- Source Heading Path: `TiDB 6.5.10 Release Notes > Bug fixes`
- Source Line Ranges: `83-134`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `lightning`
- Topic Tags: `bug-fixes`, `sql-execution`, `statistics`, `metadata-lock`, `resolved-ts`, `leader-transfer`, `placement-rules`, `schema-sync`, `log-backup`, `restore`, `changefeed`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0380_0eb87c2134`
- Source ID: `tidb-docs-8.1:releases/release-6.5.10.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `873ec0f831c96ed9966158cd7b9bd5b45a1b3fb5d01e2b7042d2833ac0e8aa27`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.10#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.10.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.10 bug fixes across TiDB, TiKV, PD, TiFlash, BR, and TiCDC for specific errors, SQL functions, replication behavior, restore behavior, metadata lock behavior, or resolved-ts and leader transfer issues.
- Retrieval Keywords: TiDB 6.5.10 bug fixes, FLOAT to UNSIGNED incorrect results, VAR_SAMP() window function, wrong TableDual plan empty query results, fail to get stats version for this histogram, empty projection causes TiDB to panic, TopN operator pushed down incorrectly, SHOW ERRORS statement always true panic, metadata lock plan cache DDL, resolved-ts fail to advance normally, check-leader operations, CONV() overflow TiKV panic, DECIMAL type decimal part incorrect, resolve-ts is blocked, Leader fails to transfer, Placement Rules down peers might not recover, Filter target monitoring metric, ALTER TABLE ... EXCHANGE PARTITION, empty key range read tasks on TiFlash, SUBSTRING_INDEX() TiFlash crash, TiFlash metadata corrupted upgrade, transiently incorrect results in high-concurrency read scenarios, BR restore no Leader, log backup advancer owner panic, checkpoint does not advance, global checkpoint advanced ahead of actual backup file write point, PD leaders cause BR to panic, resume paused log backup unstable network connections to PD, log backup paused after advancer owner migration, BR nested retries restore process, TiCDC Syncpoint Base64 encoded password, DROP PRIMARY KEY not replicated correctly, DROP UNIQUE KEY not replicated correctly, TIMEZONE type default value correct time zone
- Follow-up Guidance: 
- Classification Note: The official content is a release-notes bug-fix list covering multiple components and naming concrete issues, statements, functions, metrics, and operational conditions fixed in TiDB 6.5.10.

## Official Source Content

- Fix the issue that data conversion from the `FLOAT` type to the `UNSIGNED` type returns incorrect results [#41736](https://github.com/pingcap/tidb/issues/41736) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that `VAR_SAMP()` cannot be used as a window function [#52933](https://github.com/pingcap/tidb/issues/52933) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that a wrong TableDual plan causes empty query results [#50051](https://github.com/pingcap/tidb/issues/50051) @[onlyacat](https://github.com/onlyacat)
    - Fix the issue that the TiDB synchronously loading statistics mechanism retries to load empty statistics indefinitely and prints the `fail to get stats version for this histogram` log [#52657](https://github.com/pingcap/tidb/issues/52657) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that an empty projection causes TiDB to panic [#49109](https://github.com/pingcap/tidb/issues/49109) @[winoros](https://github.com/winoros)
    - Fix the issue that the TopN operator might be pushed down incorrectly [#37986](https://github.com/pingcap/tidb/issues/37986) @[qw4990](https://github.com/qw4990)
    - Fix the issue that TiDB panics when executing the `SHOW ERRORS` statement with a predicate that is always `true` [#46962](https://github.com/pingcap/tidb/issues/46962) @[elsa0520](https://github.com/elsa0520)
    - Fix the issue that the metadata lock fails to prevent DDL operations from executing in the plan cache scenario [#51407](https://github.com/pingcap/tidb/issues/51407) @[wjhuang2016](https://github.com/wjhuang2016)

+ TiKV

    - Fix the issue that slow `check-leader` operations on one TiKV node cause `resolved-ts` on other TiKV nodes to fail to advance normally [#15999](https://github.com/tikv/tikv/issues/15999) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that the `CONV()` function in queries might overflow during numeric system conversion, leading to TiKV panic [#16969](https://github.com/tikv/tikv/issues/16969) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue of unstable test cases, ensuring that each test uses an independent temporary directory to avoid online configuration changes affecting other test cases [#16871](https://github.com/tikv/tikv/issues/16871) @[glorv](https://github.com/glorv)
    - Fix the issue that the decimal part of the `DECIMAL` type is incorrect in some cases [#16913](https://github.com/tikv/tikv/issues/16913) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that resolve-ts is blocked when a stale Region peer ignores the GC message [#16504](https://github.com/tikv/tikv/issues/16504) @[crazycs520](https://github.com/crazycs520)

+ PD

    - Fix the issue that the Leader fails to transfer when you switch it between two deployed data centers [#7992](https://github.com/tikv/pd/issues/7992) @[TonsnakeLin](https://github.com/TonsnakeLin)
    - Fix the issue that down peers might not recover when using Placement Rules [#7808](https://github.com/tikv/pd/issues/7808) @[rleungx](https://github.com/rleungx)
    - Fix the issue that the `Filter target` monitoring metric for PD does not provide scatter range information [#8125](https://github.com/tikv/pd/issues/8125) @[HuSharp](https://github.com/HuSharp)

+ TiFlash

    - Fix the issue that TiFlash might fail to synchronize schemas after executing `ALTER TABLE ... EXCHANGE PARTITION` across databases [#7296](https://github.com/pingcap/tiflash/issues/7296) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that a query with an empty key range fails to correctly generate read tasks on TiFlash, which might block TiFlash queries [#9108](https://github.com/pingcap/tiflash/issues/9108) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that the `SUBSTRING_INDEX()` function might cause TiFlash to crash in some corner cases [#9116](https://github.com/pingcap/tiflash/issues/9116) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that TiFlash metadata might become corrupted and cause the process to panic when upgrading a cluster from a version earlier than v6.5.0 to v6.5.0 or later [#9039](https://github.com/pingcap/tiflash/issues/9039) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash might return transiently incorrect results in high-concurrency read scenarios [#8845](https://github.com/pingcap/tiflash/issues/8845) @[JinheLin](https://github.com/JinheLin)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that the test case `TestGetTSWithRetry` takes too long to execute [#52547](https://github.com/pingcap/tidb/issues/52547) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that the Region fetched from PD does not have a Leader when restoring data using BR or importing data using TiDB Lightning in physical import mode [#51124](https://github.com/pingcap/tidb/issues/51124) [#50501](https://github.com/pingcap/tidb/issues/50501) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that a PD connection failure could cause the TiDB instance where the log backup advancer owner is located to panic [#52597](https://github.com/pingcap/tidb/issues/52597) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that after pausing, stopping, and rebuilding the log backup task, the task status is normal, but the checkpoint does not advance [#53047](https://github.com/pingcap/tidb/issues/53047) @[RidRisR](https://github.com/RidRisR)
        - Fix the issue that data restore is slowed down due to the absence of a leader on a TiKV node [#50566](https://github.com/pingcap/tidb/issues/50566) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that the global checkpoint of log backup is advanced ahead of the actual backup file write point due to TiKV restart, which might cause a small amount of backup data loss [#16809](https://github.com/tikv/tikv/issues/16809) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that the transfer of PD leaders might cause BR to panic when restoring data [#53724](https://github.com/pingcap/tidb/issues/53724) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that TiKV might panic when resuming a paused log backup task with unstable network connections to PD [#17020](https://github.com/tikv/tikv/issues/17020) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that log backup might be paused after the advancer owner migration [#53561](https://github.com/pingcap/tidb/issues/53561) @[RidRisR](https://github.com/RidRisR)
        - Fix the issue that BR fails to correctly identify errors due to multiple nested retries during the restore process [#54053](https://github.com/pingcap/tidb/issues/54053) @[RidRisR](https://github.com/RidRisR)

    + TiCDC

        - Fix the issue that TiCDC fails to create a changefeed with Syncpoint enabled when the downstream database password is Base64 encoded [#10516](https://github.com/pingcap/tiflow/issues/10516) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that `DROP PRIMARY KEY` and `DROP UNIQUE KEY` statements are not replicated correctly [#10890](https://github.com/pingcap/tiflow/issues/10890) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that the default value of `TIMEZONE` type is not set according to the correct time zone [#10931](https://github.com/pingcap/tiflow/issues/10931) @[3AceShowHand](https://github.com/3AceShowHand)
