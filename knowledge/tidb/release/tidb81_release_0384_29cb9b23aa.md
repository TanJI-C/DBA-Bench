# Bug fixes across TiKV, PD, TiFlash, BR, TiCDC, DM, and Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.11.md`
- Source Title: `TiDB 6.5.11 Release Notes`
- Source Heading Path: `TiDB 6.5.11 Release Notes > Bug fixes`
- Source Line Ranges: `79-132`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dm`, `lightning`, `tidb`
- Topic Tags: `bug fixes`, `kms`, `master key rotation`, `traffic control`, `panic`, `raft snapshots`, `grpc compression`, `cdc`, `log backup`, `resolved ts`, `log redaction`, `region split size`, `tiflash startup`, `cast`, `datetime`, `tls`, `network partition`, `query performance`, `checkpoint backup`, `incremental restore`, `pitr`, `safepoints`, `sensitive credentials`, `sorter`, `kafka`, `data replication`, `list partition`, `alter database`, `data import`, `transaction conflicts`, `data corruption`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0384_29cb9b23aa`
- Source ID: `tidb-docs-8.1:releases/release-6.5.11.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `507ba7f2f727019a05e8abbec0f0812f58f1b28f40ff2be9123f8495ac7096c8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.11#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.11.md

## Retrieval Guidance

- Use When: Use this chunk when searching the TiDB 6.5.11 release notes for fixed issues across TiKV, PD, TiFlash, BR, TiCDC, DM, or TiDB Lightning involving panic, replication, backup, CDC, TLS, Kafka, KMS, or data import problems.
- Retrieval Keywords: TiDB 6.5.11 bug fixes, master key rotation KMS, traffic control after deleting large tables or partitions, sst_importer SST files panic, stale replica processes Raft snapshots, corrupted Raft data snapshot panic, grpc-compression-type TiKV to TiDB, check_leader advance-ts-interval resolved_ts lag, PD logs not redacted, coprocessor.region-split-size less than 1 MiB PD panic, replication.strictly-match-label true TiFlash fail to start, PD operator checks data race, TiFlash CAST() string to datetime time zone invalid characters, SSL certificate configuration empty string incorrectly enables TLS, network partition between TiFlash and PD read request timeout, outer join TiFlash crash, DECIMAL incorrect query results corner cases, EXCHANGE PARTITION DROP TABLE TiFlash metadata replication query performance, BR checkpoint path incompatible with some external storage, incremental backups scanning DDL jobs inefficiency, checkpoint backups interruptions in seeking Region leaders, ADD INDEX MODIFY COLUMN incremental restore backfilling, log backup PITR safepoints not properly cleared in PD, backup tasks stuck if TiKV becomes unresponsive, BR logs sensitive credential information, TiCDC Sorter reads disk data panic, Processor module downstream Kafka inaccessible stuck, DM max-index-length data replication interrupted, schema tracker LIST partition tables DM errors, ALTER TABLE ... DROP PARTITION LIST partitioned tables, ALTER DATABASE replication error default database, TiDB Lightning transaction conflicts during data import, TiKV data corrupted after disabling import mode of TiDB Lightning, restarting TiKV during importing data using TiDB Lightning
- Follow-up Guidance: 
- Classification Note: The official content is a release-note bug-fix summary for TiDB 6.5.11 covering multiple components including TiKV, PD, TiFlash, BR, TiCDC, DM, and TiDB Lightning.

## Official Source Content

- Fix the issue that prevents master key rotation when the master key is stored in a Key Management Service (KMS) [#17410](https://github.com/tikv/tikv/issues/17410) @[hhwyt](https://github.com/hhwyt)
    - Fix a traffic control issue that might occur after deleting large tables or partitions [#17304](https://github.com/tikv/tikv/issues/17304) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that TiKV might panic due to ingesting deleted `sst_importer` SST files [#15053](https://github.com/tikv/tikv/issues/15053) @[lance6716](https://github.com/lance6716)
    - Fix the issue that TiKV might panic when a stale replica processes Raft snapshots, triggered by a slow split operation and immediate removal of the new replica [#17469](https://github.com/tikv/tikv/issues/17469) @[hbisheng](https://github.com/hbisheng)
    - Fix the issue that TiKV might repeatedly panic when applying a corrupted Raft data snapshot [#15292](https://github.com/tikv/tikv/issues/15292) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the issue that setting the gRPC message compression method via `grpc-compression-type` does not take effect on messages sent from TiKV to TiDB [#17176](https://github.com/tikv/tikv/issues/17176) @[ekexium](https://github.com/ekexium)
    - Fix the issue that CDC and log-backup do not limit the timeout of `check_leader` using the `advance-ts-interval` configuration, causing the `resolved_ts` lag to be too large when TiKV restarts normally in some cases [#17107](https://github.com/tikv/tikv/issues/17107) @[MyonKeminta](https://github.com/MyonKeminta)

+ PD

    - Fix the issue that some logs are not redacted [#8419](https://github.com/tikv/pd/issues/8419) @[rleungx](https://github.com/rleungx)
    - Fix the issue that setting the TiKV configuration item [`coprocessor.region-split-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-split-size) to a value less than 1 MiB causes PD panic [#8323](https://github.com/tikv/pd/issues/8323) @[JmPotato](https://github.com/JmPotato)
    - Fix the issue that setting `replication.strictly-match-label` to `true` causes TiFlash to fail to start [#8480](https://github.com/tikv/pd/issues/8480) @[rleungx](https://github.com/rleungx)
    - Fix the data race issue that PD encounters during operator checks [#8263](https://github.com/tikv/pd/issues/8263) @[lhy1024](https://github.com/lhy1024)

+ TiFlash

    - Fix the issue that when using the `CAST()` function to convert a string to a datetime with a time zone or invalid characters, the result is incorrect [#8754](https://github.com/pingcap/tiflash/issues/8754) @[solotzg](https://github.com/solotzg)
    - Fix the issue that TiFlash might panic when a database is deleted shortly after creation [#9266](https://github.com/pingcap/tiflash/issues/9266) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that setting the SSL certificate configuration to an empty string in TiFlash incorrectly enables TLS and causes TiFlash to fail to start [#9235](https://github.com/pingcap/tiflash/issues/9235) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that a network partition (network disconnection) between TiFlash and any PD might cause read request timeout errors [#9243](https://github.com/pingcap/tiflash/issues/9243) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that TiFlash might crash if an error occurs during the execution of a query containing outer join [#9190](https://github.com/pingcap/tiflash/issues/9190) @[windtalker](https://github.com/windtalker)
    - Fix the issue that converting data types to `DECIMAL` might cause incorrect query results in some corner cases [#53892](https://github.com/pingcap/tidb/issues/53892) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that frequent `EXCHANGE PARTITION` and `DROP TABLE` operations over a long period in a cluster might slow down the replication of TiFlash table metadata and degrade the query performance [#9227](https://github.com/pingcap/tiflash/issues/9227) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that the checkpoint path of backup and restore is incompatible with some external storage [#55265](https://github.com/pingcap/tidb/issues/55265) @[Leavrth](https://github.com/Leavrth)
        - Fix the inefficiency issue in scanning DDL jobs during incremental backups [#54139](https://github.com/pingcap/tidb/issues/54139) @[3pointer](https://github.com/3pointer)
        - Fix the issue that the backup performance during checkpoint backups is affected due to interruptions in seeking Region leaders [#17168](https://github.com/tikv/tikv/issues/17168) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that DDLs requiring backfilling, such as `ADD INDEX` and `MODIFY COLUMN`, might not be correctly recovered during incremental restore [#54426](https://github.com/pingcap/tidb/issues/54426) @[3pointer](https://github.com/3pointer)
        - Fix the issue that after a log backup PITR task fails and you stop it, the safepoints related to that task are not properly cleared in PD [#17316](https://github.com/tikv/tikv/issues/17316) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that backup tasks might get stuck if TiKV becomes unresponsive during the backup process [#53480](https://github.com/pingcap/tidb/issues/53480) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that BR logs might print sensitive credential information when log backup is enabled [#55273](https://github.com/pingcap/tidb/issues/55273) @[RidRisR](https://github.com/RidRisR)

    + TiCDC

        - Fix the issue that TiCDC might panic when the Sorter module reads disk data [#10853](https://github.com/pingcap/tiflow/issues/10853) @[hicqu](https://github.com/hicqu)
        - Fix the issue that the Processor module might get stuck when the downstream Kafka is inaccessible [#11340](https://github.com/pingcap/tiflow/issues/11340) @[asddongmen](https://github.com/asddongmen)

    + TiDB Data Migration (DM)

        - Fix the issue that data replication is interrupted when the index length exceeds the default value of `max-index-length` [#11459](https://github.com/pingcap/tiflow/issues/11459) @[michaelmdeng](https://github.com/michaelmdeng)
        - Fix the issue that schema tracker incorrectly handles LIST partition tables, causing DM errors [#11408](https://github.com/pingcap/tiflow/issues/11408) @[lance6716](https://github.com/lance6716)
        - Fix the issue that DM returns an error when replicating the `ALTER TABLE ... DROP PARTITION` statement for LIST partitioned tables [#54760](https://github.com/pingcap/tidb/issues/54760) @[lance6716](https://github.com/lance6716)
        - Fix the issue that DM does not set the default database when processing the `ALTER DATABASE` statement, which causes a replication error [#11503](https://github.com/pingcap/tiflow/issues/11503) @[lance6716](https://github.com/lance6716)

    + TiDB Lightning
        - Fix the issue that transaction conflicts occur during data import using TiDB Lightning [#49826](https://github.com/pingcap/tidb/issues/49826) @[lance6716](https://github.com/lance6716)
        - Fix the issue that TiKV data might be corrupted when importing data after disabling the import mode of TiDB Lightning [#15003](https://github.com/tikv/tikv/issues/15003) [#47694](https://github.com/pingcap/tidb/issues/47694) @[lance6716](https://github.com/lance6716)
        - Fix the issue that during importing data using TiDB Lightning, an error occurs when restarting TiKV [#15912](https://github.com/tikv/tikv/issues/15912) @[lance6716](https://github.com/lance6716)
