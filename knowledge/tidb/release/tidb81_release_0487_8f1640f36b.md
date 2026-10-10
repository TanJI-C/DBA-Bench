# Bug fixes for BR, TiCDC, DM, Lightning, Dumpling, and TiDB Binlog

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.6.md`
- Source Title: `TiDB 7.1.6 Release Notes`
- Source Heading Path: `TiDB 7.1.6 Release Notes > Bug fixes`
- Source Line Ranges: `255-303`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `ticdc`, `dm`, `lightning`, `dumpling`, `tidb`, `pd`, `tikv`
- Topic Tags: `bug-fixes`, `backup`, `restore`, `log-backup`, `pitr`, `cdc`, `replication`, `import`, `export`, `binlog`, `leader-election`, `checkpoint`, `data-consistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0487_8f1640f36b`
- Source ID: `tidb-docs-8.1:releases/release-7.1.6.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e1e58df7b27fa5791bf30898c40af112cd216ba58d43b2dad340e41fb8d7ba89`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.6.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 7.1.6 bug fixes across BR, TiCDC, DM, TiDB Lightning, Dumpling, or TiDB Binlog for backup, PITR, CDC, replication, import, export, leader election, checkpoint, or data consistency issues.
- Retrieval Keywords: TiDB 7.1.6 Release Notes bug fixes, BR incremental restore ADD INDEX MODIFY COLUMN backfilling, log backup PITR safepoints PD not properly cleared, log backup advancer owner migration paused, incremental backups scanning DDL jobs inefficiency, checkpoint backups Region leaders interruptions, BR logs sensitive credential information log backup, restore process multiple nested retries errors, TiKV panic resuming paused log backup unstable network PD, backup tasks stuck TiKV unresponsive, checkpoint path backup restore incompatible external storage, Region fetched from PD does not have a Leader BR TiDB Lightning physical import mode, transfer of PD leaders cause BR panic restoring data, log backup checkpoint does not advance after pausing stopping rebuilding task, log backups residual locks checkpoint fail to advance, TiCDC TIMEZONE default value correct time zone, TiCDC Sorter module reads disk data panic, TiCDC data inconsistency restarting Changefeed repeatedly UPDATE multi-node, ignore-event add table partition DML changes related partitions downstream, DROP PRIMARY KEY DROP UNIQUE KEY not replicated correctly, Processor module stuck downstream Kafka inaccessible, DM ALTER DATABASE default database replication error, multiple DM-master nodes simultaneously become leaders, go-mysql connection blocking issue, max-index-length data replication interrupted, ALTER TABLE DROP PARTITION LIST partitioned tables DM error, TiDB Lightning oversized messages sent from TiKV, TiKV data corrupted after disabling import mode of TiDB Lightning, transaction conflicts during data import using TiDB Lightning, TiDB Lightning fail to import data when EBS BR is running, verify allocator base failed same task ID parallel import tasks, invalid store ID 0 killing PD Leader TiDB Lightning, Dumpling exporting tables and views at the same time error, TiDB Binlog ADD COLUMN data and columnID count not match
- Follow-up Guidance: The source lists issue-specific fixes for BR, TiCDC, DM, TiDB Lightning, Dumpling, and TiDB Binlog in TiDB 7.1.6.
- Classification Note: This is a release-note bug-fix summary covering multiple data movement, backup and restore, CDC, import/export, and binlog components for self-managed TiDB 7.1.6.

## Official Source Content

- Fix the issue that BR integration test cases are unstable, and add a new test case to simulate snapshot or log backup file corruption [#53835](https://github.com/pingcap/tidb/issues/53835) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that DDLs requiring backfilling, such as `ADD INDEX` and `MODIFY COLUMN`, might not be correctly recovered during incremental restore [#54426](https://github.com/pingcap/tidb/issues/54426) @[3pointer](https://github.com/3pointer)
        - Fix the issue that after a log backup PITR task fails and you stop it, the safepoints related to that task are not properly cleared in PD [#17316](https://github.com/tikv/tikv/issues/17316) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that log backup might be paused after the advancer owner migration [#53561](https://github.com/pingcap/tidb/issues/53561) @[RidRisR](https://github.com/RidRisR)
        - Fix the inefficiency issue in scanning DDL jobs during incremental backups [#54139](https://github.com/pingcap/tidb/issues/54139) @[3pointer](https://github.com/3pointer)
        - Fix the issue that the backup performance during checkpoint backups is affected due to interruptions in seeking Region leaders [#17168](https://github.com/tikv/tikv/issues/17168) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that BR logs might print sensitive credential information when log backup is enabled [#55273](https://github.com/pingcap/tidb/issues/55273) @[RidRisR](https://github.com/RidRisR)
        - Fix the issue that BR fails to correctly identify errors due to multiple nested retries during the restore process [#54053](https://github.com/pingcap/tidb/issues/54053) @[RidRisR](https://github.com/RidRisR)
        - Fix the issue that TiKV might panic when resuming a paused log backup task with unstable network connections to PD [#17020](https://github.com/tikv/tikv/issues/17020) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that backup tasks might get stuck if TiKV becomes unresponsive during the backup process [#53480](https://github.com/pingcap/tidb/issues/53480) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that the checkpoint path of backup and restore is incompatible with some external storage [#55265](https://github.com/pingcap/tidb/issues/55265) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that the Region fetched from PD does not have a Leader when restoring data using BR or importing data using TiDB Lightning in physical import mode [#51124](https://github.com/pingcap/tidb/issues/51124) [#50501](https://github.com/pingcap/tidb/issues/50501) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that the transfer of PD leaders might cause BR to panic when restoring data [#53724](https://github.com/pingcap/tidb/issues/53724) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that after pausing, stopping, and rebuilding the log backup task, the task status is normal, but the checkpoint does not advance [#53047](https://github.com/pingcap/tidb/issues/53047) @[RidRisR](https://github.com/RidRisR)
        - Fix the issue that log backups cannot resolve residual locks promptly, causing the checkpoint to fail to advance [#57134](https://github.com/pingcap/tidb/issues/57134) @[3pointer](https://github.com/3pointer)

    + TiCDC

        - Fix the issue that the default value of `TIMEZONE` type is not set according to the correct time zone [#10931](https://github.com/pingcap/tiflow/issues/10931) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that TiCDC might panic when the Sorter module reads disk data [#10853](https://github.com/pingcap/tiflow/issues/10853) @[hicqu](https://github.com/hicqu)
        - Fix the issue that data inconsistency might occur when restarting Changefeed repeatedly when performing a large number of `UPDATE` operations in a multi-node environment [#11219](https://github.com/pingcap/tiflow/issues/11219) @[lidezhu](https://github.com/lidezhu)
        - Fix the issue that after filtering out `add table partition` events is configured in `ignore-event`, TiCDC does not replicate other types of DML changes for related partitions to the downstream [#10524](https://github.com/pingcap/tiflow/issues/10524) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that `DROP PRIMARY KEY` and `DROP UNIQUE KEY` statements are not replicated correctly [#10890](https://github.com/pingcap/tiflow/issues/10890) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that the Processor module might get stuck when the downstream Kafka is inaccessible [#11340](https://github.com/pingcap/tiflow/issues/11340) @[asddongmen](https://github.com/asddongmen)

    + TiDB Data Migration (DM)

        - Fix the issue that DM does not set the default database when processing the `ALTER DATABASE` statement, which causes a replication error [#11503](https://github.com/pingcap/tiflow/issues/11503) @[lance6716](https://github.com/lance6716)
        - Fix the issue that multiple DM-master nodes might simultaneously become leaders, leading to data inconsistency [#11602](https://github.com/pingcap/tiflow/issues/11602) @[GMHDBJD](https://github.com/GMHDBJD)
        - Fix the connection blocking issue by upgrading `go-mysql` [#11041](https://github.com/pingcap/tiflow/issues/11041) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that data replication is interrupted when the index length exceeds the default value of `max-index-length` [#11459](https://github.com/pingcap/tiflow/issues/11459) @[michaelmdeng](https://github.com/michaelmdeng)
        - Fix the issue that DM returns an error when replicating the `ALTER TABLE ... DROP PARTITION` statement for LIST partitioned tables [#54760](https://github.com/pingcap/tidb/issues/54760) @[lance6716](https://github.com/lance6716)

    + TiDB Lightning

        - Fix the issue that TiDB Lightning fails to receive oversized messages sent from TiKV [#56114](https://github.com/pingcap/tidb/issues/56114) @[fishiu](https://github.com/fishiu)
        - Fix the issue that TiKV data might be corrupted when importing data after disabling the import mode of TiDB Lightning [#15003](https://github.com/tikv/tikv/issues/15003) [#47694](https://github.com/pingcap/tidb/issues/47694) @[lance6716](https://github.com/lance6716)
        - Fix the issue that transaction conflicts occur during data import using TiDB Lightning [#49826](https://github.com/pingcap/tidb/issues/49826) @[lance6716](https://github.com/lance6716)
        - Fix the issue that TiDB Lightning might fail to import data when EBS BR is running [#49517](https://github.com/pingcap/tidb/issues/49517) @[mittalrishabh](https://github.com/mittalrishabh)
        - Fix the issue that TiDB Lightning reports a `verify allocator base failed` error when two instances simultaneously start parallel import tasks and are assigned the same task ID [#55384](https://github.com/pingcap/tidb/issues/55384) @[ei-sugimoto](https://github.com/ei-sugimoto)
        - Fix the issue that killing the PD Leader causes TiDB Lightning to report the `invalid store ID 0` error during data import [#50501](https://github.com/pingcap/tidb/issues/50501) @[Leavrth](https://github.com/Leavrth)

    + Dumpling
        - Fix the issue that Dumpling reports an error when exporting tables and views at the same time [#53682](https://github.com/pingcap/tidb/issues/53682) @[tangenta](https://github.com/tangenta)

    + TiDB Binlog
    
        - Fix the issue that deleting rows during the execution of `ADD COLUMN` might report an error `data and columnID count not match` when TiDB Binlog is enabled [#53133](https://github.com/pingcap/tidb/issues/53133) @[tangenta](https://github.com/tangenta)
