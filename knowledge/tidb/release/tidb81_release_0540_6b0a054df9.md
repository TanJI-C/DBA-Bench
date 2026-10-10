# 7.5.3 bug fixes across TiDB, TiKV, PD, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.3.md`
- Source Title: `TiDB 7.5.3 Release Notes`
- Source Heading Path: `TiDB 7.5.3 Release Notes > Bug fixes`
- Source Line Ranges: `84-134`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dumpling`
- Topic Tags: `bug-fixes`, `sql`, `coprocessor`, `oom`, `cdc`, `log-backup`, `resource-groups`, `quota`, `etcd-client`, `redaction`, `fastscan`, `late-materialization`, `tls`, `restore`, `incremental-backup`, `incremental-restore`, `kafka`, `export`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0540_6b0a054df9`
- Source ID: `tidb-docs-8.1:releases/release-7.5.3.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7e499fa03c75f80c877a51f490aed49a48864c74a21117b55a4226a01c966a5d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.3#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 7.5.3 bug fix list across TiDB, TiKV, PD, TiFlash, BR, TiCDC, and Dumpling for issues involving specific functions, configuration items, errors, or component behaviors.
- Retrieval Keywords: TiDB 7.5.3 bug fixes, CURRENT_DATE() default value incorrect query results, SELECT ... FOR UPDATE wrong point get plans, grpc-compression-type TiKV to TiDB, highly concurrent Coprocessor requests TiKV OOM, CDC log-backup check_leader advance-ts-interval resolved_ts lag, corrupted Raft data snapshot repeatedly panic, resource group allocated tokens less than specified value, resource group quota limits requesting tokens for more than 500 ms, deleted nodes candidate connection list etcd client, coprocessor.region-split-size less than 1 MiB causes PD panic, security.redact-info-log PD logs not fully redacted, binding a role to a resource group no error reported, FastScan duplicate rows after BR or TiDB Lightning, SUBSTRING_INDEX() TiFlash crash, empty string SSL certificate incorrectly enables TLS, late materialization column type mismatch, virtual generated columns incorrect results after late materialization, RENAME TABLE ... TO ... partitioned table empty partitions panic, database deleted shortly after creation TiFlash panic, log backup paused after advancer owner migration, multiple nested retries restore process identify errors, incremental backups scanning DDL jobs inefficiency, checkpoint backups interruptions in seeking Region leaders, log backup task status normal but checkpoint does not advance, ADD INDEX MODIFY COLUMN incremental restore not correctly recovered, checksum set to 0 after splitting UPDATE events, Processor module stuck downstream Kafka inaccessible, Dumpling exporting tables and views at the same time error
- Follow-up Guidance: The chunk can also help when matching a known issue to its exact component and identifier, such as `security.redact-info-log`, `coprocessor.region-split-size`, `advance-ts-interval`, `CURRENT_DATE()`, `SUBSTRING_INDEX()`, `SELECT ... FOR UPDATE`, `RENAME TABLE ... TO ...`, `ADD INDEX`, or `MODIFY COLUMN`.
- Classification Note: The official content is a release-notes bug-fix summary for self-managed TiDB 7.5.3, grouped by component and listing corrected issues, affected SQL statements, configuration items, and operational behaviors.

## Official Source Content

- Fix the issue that using `CURRENT_DATE()` as the default value for a column results in incorrect query results [#53746](https://github.com/pingcap/tidb/issues/53746) @[tangenta](https://github.com/tangenta)
    - Fix the issue of reusing wrong point get plans for `SELECT ... FOR UPDATE` [#54652](https://github.com/pingcap/tidb/issues/54652) @[qw4990](https://github.com/qw4990)

+ TiKV

    - Fix the issue that setting the gRPC message compression method via `grpc-compression-type` does not take effect on messages sent from TiKV to TiDB [#17176](https://github.com/tikv/tikv/issues/17176) @[ekexium](https://github.com/ekexium)
    - Fix the issue that highly concurrent Coprocessor requests might cause TiKV OOM [#16653](https://github.com/tikv/tikv/issues/16653) @[overvenus](https://github.com/overvenus)
    - Fix the issue that CDC and log-backup do not limit the timeout of `check_leader` using the `advance-ts-interval` configuration, causing the `resolved_ts` lag to be too large when TiKV restarts normally in some cases [#17107](https://github.com/tikv/tikv/issues/17107) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that TiKV might repeatedly panic when applying a corrupted Raft data snapshot [#15292](https://github.com/tikv/tikv/issues/15292) @[LykxSassinator](https://github.com/LykxSassinator)

+ PD

    - Fix the issue that slots are not fully deleted in a resource group client, which causes the number of the allocated tokens to be less than the specified value [#7346](https://github.com/tikv/pd/issues/7346) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that a resource group encounters quota limits when requesting tokens for more than 500 ms [#8349](https://github.com/tikv/pd/issues/8349) @[nolouch](https://github.com/nolouch)
    - Fix the data race issue of resource groups [#8267](https://github.com/tikv/pd/issues/8267) @[HuSharp](https://github.com/HuSharp)
    - Fix the data race issue that PD encounters during operator checks [#8263](https://github.com/tikv/pd/issues/8263) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that deleted nodes still appear in the candidate connection list in etcd client [#8286](https://github.com/tikv/pd/issues/8286) @[JmPotato](https://github.com/JmPotato)
    - Fix the issue that setting the TiKV configuration item [`coprocessor.region-split-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-split-size) to a value less than 1 MiB causes PD panic [#8323](https://github.com/tikv/pd/issues/8323) @[JmPotato](https://github.com/JmPotato)
    - Fix the issue that the encryption manager is not initialized before use [#8384](https://github.com/tikv/pd/issues/8384) @[releungx](https://github.com/releungx)
    - Fix the issue that PD logs are not fully redacted when the PD configuration item [`security.redact-info-log`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#redact-info-log-new-in-v50) is enabled [#8419](https://github.com/tikv/pd/issues/8419) @[releungx](https://github.com/releungx)
    - Fix the issue that no error is reported when binding a role to a resource group [#54417](https://github.com/pingcap/tidb/issues/54417) @[JmPotato](https://github.com/JmPotato)

+ TiFlash

    - Fix the issue that a large number of duplicate rows might be read in FastScan mode after importing data via BR or TiDB Lightning [#9118](https://github.com/pingcap/tiflash/issues/9118) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that the `SUBSTRING_INDEX()` function might cause TiFlash to crash in some corner cases [#9116](https://github.com/pingcap/tiflash/issues/9116) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that setting the SSL certificate configuration to an empty string in TiFlash incorrectly enables TLS and causes TiFlash to fail to start [#9235](https://github.com/pingcap/tiflash/issues/9235) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that some queries might report a column type mismatch error after late materialization is enabled [#9175](https://github.com/pingcap/tiflash/issues/9175) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that queries with virtual generated columns might return incorrect results after late materialization is enabled [#9188](https://github.com/pingcap/tiflash/issues/9188) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that TiFlash might panic after executing `RENAME TABLE ... TO ...` on a partitioned table with empty partitions across databases [#9132](https://github.com/pingcap/tiflash/issues/9132) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash might panic when a database is deleted shortly after creation [#9266](https://github.com/pingcap/tiflash/issues/9266) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that log backup might be paused after the advancer owner migration [#53561](https://github.com/pingcap/tidb/issues/53561) @[RidRisR](https://github.com/RidRisR)
        - Fix the issue that BR fails to correctly identify errors due to multiple nested retries during the restore process [#54053](https://github.com/pingcap/tidb/issues/54053) @[RidRisR](https://github.com/RidRisR)
        - Fix the inefficiency issue in scanning DDL jobs during incremental backups [#54139](https://github.com/pingcap/tidb/issues/54139) @[3pointer](https://github.com/3pointer)
        - Fix the issue that the backup performance during checkpoint backups is affected due to interruptions in seeking Region leaders [#17168](https://github.com/tikv/tikv/issues/17168) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that after pausing, stopping, and rebuilding the log backup task, the task status is normal, but the checkpoint does not advance [#53047](https://github.com/pingcap/tidb/issues/53047) @[RidRisR](https://github.com/RidRisR)
        - Fix the issue that DDLs requiring backfilling, such as `ADD INDEX` and `MODIFY COLUMN`, might not be correctly recovered during incremental restore [#54426](https://github.com/pingcap/tidb/issues/54426) @[3pointer](https://github.com/3pointer)

    + TiCDC

        - Fix the issue that the checksum is not correctly set to `0` after splitting `UPDATE` events [#11402](https://github.com/pingcap/tiflow/issues/11402) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that the Processor module might get stuck when the downstream Kafka is inaccessible [#11340](https://github.com/pingcap/tiflow/issues/11340) @[asddongmen](https://github.com/asddongmen)

    + Dumpling

        - Fix the issue that Dumpling reports an error when exporting tables and views at the same time [#53682](https://github.com/pingcap/tidb/issues/53682) @[tangenta](https://github.com/tangenta)
