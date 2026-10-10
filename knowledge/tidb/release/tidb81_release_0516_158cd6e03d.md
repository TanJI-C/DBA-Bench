# Bug fixes across TiKV, PD, TiFlash, BR, TiCDC, DM, and Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.4.0.md`
- Source Title: `TiDB 7.4.0 Release Notes`
- Source Heading Path: `TiDB 7.4.0 Release Notes > Bug fixes`
- Source Line Ranges: `429-488`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dm`, `lightning`, `tidb`
- Topic Tags: `bug-fixes`, `stability`, `reliability`, `backup-restore`, `point-in-time-recovery`, `replication`, `changefeed`, `data-migration`, `data-import`, `monitoring`, `flashback`, `placement-rules`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0516_158cd6e03d`
- Source ID: `tidb-docs-8.1:releases/release-7.4.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fd861ac34fde839945cf0f6addc500c762662df4af8bf8518180b155bb703e3e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.4.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.4.0 bug fixes across TiKV, PD, TiFlash, BR, TiCDC, DM, and TiDB Lightning, especially for specific errors, monitoring issues, PITR, changefeed, replication, or import problems.
- Retrieval Keywords: TiDB 7.4.0 bug fixes, Blob file deleted twice, Titan enabled, Thread Voluntary, Thread Nonvoluntary, raftstore-applys, incorrect metadata of Region, sync_recovery, sync, Online Unsafe Recovery, CpuRecord, Error 9002: TiKV server timeout, Flashback, Scatter Peers, RU consumption less than 0, default placement rules, min-resolved-ts, PD OOM, max_snapshot_lifetime, MPP task has failed, resolve lock timeout, PITR, implicit primary keys, meta-kv, TiCDC changefeed fails, replication write conflicts, multiple tables are renamed in the same DDL statement, Chinese characters are not validated in CSV files, upstream TiDB GC is blocked, scale-out, DM validator deadlock, case-insensitive collations, optimistic mode, NONCLUSTERED auto_increment, AUTO_ID_CACHE=1, checksum = "optional", PD cluster address changes
- Follow-up Guidance: This chunk can also help when matching a reported issue to the exact component section such as TiKV, PD, TiFlash, BR, TiCDC, DM, or TiDB Lightning in the TiDB 7.4.0 release notes.
- Classification Note: The official content is a release-notes bug-fix summary for TiDB 7.4.0 covering multiple components and specific fixed issues.

## Official Source Content

- Fix the issue that TiKV fails to start when Titan is enabled and the `Blob file deleted twice` error occurs [#15454](https://github.com/tikv/tikv/issues/15454) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue of no data in the Thread Voluntary and Thread Nonvoluntary monitoring panels [#15413](https://github.com/tikv/tikv/issues/15413) @[SpadeA-Tang](https://github.com/SpadeA-Tang)
    - Fix the data error of continuously increasing raftstore-applys [#15371](https://github.com/tikv/tikv/issues/15371) @[Connor1996](https://github.com/Connor1996)
    - Fix the TiKV panic issue caused by incorrect metadata of Region [#13311](https://github.com/tikv/tikv/issues/13311) @[zyguan](https://github.com/zyguan)
    - Fix the issue of QPS dropping to 0 after switching from `sync_recovery` to `sync` [#15366](https://github.com/tikv/tikv/issues/15366) @[nolouch](https://github.com/nolouch)
    - Fix the issue that Online Unsafe Recovery does not abort on timeout [#15346](https://github.com/tikv/tikv/issues/15346) @[Connor1996](https://github.com/Connor1996)
    - Fix the potential memory leak issue caused by CpuRecord [#15304](https://github.com/tikv/tikv/issues/15304) @[overvenus](https://github.com/overvenus)
    - Fix the issue that `"Error 9002: TiKV server timeout"` occurs when the backup cluster is down and the primary cluster is queried [#12914](https://github.com/tikv/tikv/issues/12914) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that the backup TiKV gets stuck when TiKV restarts after the primary cluster recovers [#12320](https://github.com/tikv/tikv/issues/12320) @[disksing](https://github.com/disksing)

+ PD

    - Fix the issue that the Region information is not updated and saved during Flashback [#6912](https://github.com/tikv/pd/issues/6912) @[overvenus](https://github.com/overvenus)
    - Fix the issue of slow switching of PD Leaders due to slow synchronization of store config [#6918](https://github.com/tikv/pd/issues/6918) @[bufferflies](https://github.com/bufferflies)
    - Fix the issue that the groups are not considered in Scatter Peers [#6962](https://github.com/tikv/pd/issues/6962) @[bufferflies](https://github.com/bufferflies)
    - Fix the issue that RU consumption less than 0 causes PD to crash [#6973](https://github.com/tikv/pd/issues/6973) @[CabinfeverB](https://github.com/CabinfeverB)
    - Fix the issue that modified isolation levels are not synchronized to the default placement rules [#7121](https://github.com/tikv/pd/issues/7121) @[rleungx](https://github.com/rleungx)
    - Fix the issue that the client-go regularly updating `min-resolved-ts` might cause PD OOM when the cluster is large [#46664](https://github.com/pingcap/tidb/issues/46664) @[HuSharp](https://github.com/HuSharp)

+ TiFlash

    - Fix the issue that the `max_snapshot_lifetime` metric is displayed incorrectly on Grafana [#7713](https://github.com/pingcap/tiflash/issues/7713) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that some metrics about the maximum duration are not correct [#8076](https://github.com/pingcap/tiflash/issues/8076) @[CalvinNeo](https://github.com/CalvinNeo)
    - Fix the issue that TiDB incorrectly reports that an MPP task has failed [#7177](https://github.com/pingcap/tiflash/issues/7177) @[yibin87](https://github.com/yibin87)

+ Tools

    + Backup & Restore (BR)

        - Fix an issue that the misleading error message `resolve lock timeout` covers up the actual error when backup fails [#43236](https://github.com/pingcap/tidb/issues/43236) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that recovering implicit primary keys using PITR might cause conflicts [#46520](https://github.com/pingcap/tidb/issues/46520) @[3pointer](https://github.com/3pointer)
        - Fix the issue that recovering meta-kv using PITR might cause errors [#46578](https://github.com/pingcap/tidb/issues/46578) @[Leavrth](https://github.com/Leavrth)
        - Fix the errors in BR integration test cases [#46561](https://github.com/pingcap/tidb/issues/46561) @[purelind](https://github.com/purelind)

    + TiCDC

        - Fix the issue that TiCDC accesses the invalid old address during PD scaling up and down [#9584](https://github.com/pingcap/tiflow/issues/9584) @[fubinzh](https://github.com/fubinzh) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that changefeed fails in some scenarios [#9309](https://github.com/pingcap/tiflow/issues/9309) [#9450](https://github.com/pingcap/tiflow/issues/9450) [#9542](https://github.com/pingcap/tiflow/issues/9542) [#9685](https://github.com/pingcap/tiflow/issues/9685) @[hicqu](https://github.com/hicqu) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that replication write conflicts might occur when the unique keys for multiple rows are modified in one transaction on the upstream [#9430](https://github.com/pingcap/tiflow/issues/9430) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that a replication error occurs when multiple tables are renamed in the same DDL statement on the upstream [#9476](https://github.com/pingcap/tiflow/issues/9476) [#9488](https://github.com/pingcap/tiflow/issues/9488) @[CharlesCheung96](https://github.com/CharlesCheung96) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that Chinese characters are not validated in CSV files [#9609](https://github.com/pingcap/tiflow/issues/9609) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that upstream TiDB GC is blocked after all changefeeds are removed [#9633](https://github.com/pingcap/tiflow/issues/9633) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue of uneven distribution of write keys among nodes when `scale-out` is enabled [#9665](https://github.com/pingcap/tiflow/issues/9665) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that sensitive user information is recorded in the logs [#9690](https://github.com/pingcap/tiflow/issues/9690) @[sdojjy](https://github.com/sdojjy)

    + TiDB Data Migration (DM)

        - Fix the issue that DM cannot handle conflicts correctly with case-insensitive collations [#9489](https://github.com/pingcap/tiflow/issues/9489) @[hihihuhu](https://github.com/hihihuhu)
        - Fix the DM validator deadlock issue and enhance retries [#9257](https://github.com/pingcap/tiflow/issues/9257) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that replication lag returned by DM keeps growing when a failed DDL is skipped and no subsequent DDLs are executed [#9605](https://github.com/pingcap/tiflow/issues/9605) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that DM cannot properly track upstream table schemas when skipping online DDLs [#9587](https://github.com/pingcap/tiflow/issues/9587) @[GMHDBJD](https://github.com/GMHDBJD)
        - Fix the issue that DM skips all DMLs when resuming a task in optimistic mode [#9588](https://github.com/pingcap/tiflow/issues/9588) @[GMHDBJD](https://github.com/GMHDBJD)
        - Fix the issue that DM skips partition DDLs in optimistic mode [#9788](https://github.com/pingcap/tiflow/issues/9788) @[GMHDBJD](https://github.com/GMHDBJD)

    + TiDB Lightning
        - Fix the issue that inserting data returns an error after TiDB Lightning imports the `NONCLUSTERED auto_increment` and `AUTO_ID_CACHE=1` tables [#46100](https://github.com/pingcap/tidb/issues/46100) @[tiancaiamao](https://github.com/tiancaiamao)
        - Fix the issue that checksum still reports errors when `checksum = "optional"` [#45382](https://github.com/pingcap/tidb/issues/45382) @[lyzx2001](https://github.com/lyzx2001)
        - Fix the issue that data import fails when the PD cluster address changes [#43436](https://github.com/pingcap/tidb/issues/43436) @[lichunzhu](https://github.com/lichunzhu)
