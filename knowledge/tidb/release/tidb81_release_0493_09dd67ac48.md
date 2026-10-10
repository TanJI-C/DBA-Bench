# 7.2.0 bug fixes across TiDB, TiKV, PD, TiFlash, BR, TiCDC, and Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.2.0.md`
- Source Title: `TiDB 7.2.0 Release Notes`
- Source Heading Path: `TiDB 7.2.0 Release Notes > Bug fixes`
- Source Line Ranges: `257-318`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `lightning`
- Topic Tags: `bug-fixes`, `query-execution`, `sql-functions`, `ddl`, `transactions`, `stale-read`, `follower-read`, `gc`, `replication`, `backup-restore`, `changefeed`, `data-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0493_09dd67ac48`
- Source ID: `tidb-docs-8.1:releases/release-7.2.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `db2ed143905f14e19464a70dcc54eaccb2720f266186119da1e4788df1b8d17a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.2.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.2.0 bug fixes across TiDB, TiKV, PD, TiFlash, BR, TiCDC, or TiDB Lightning for issues involving CTE hangs, stale read, follower read, DDL rollback metadata, checksum mismatch, Resolved TS, or Lightning panic.
- Retrieval Keywords: TiDB 7.2.0 Bug fixes, CTE causes TiDB to hang, min max query result is incorrect, SHOW PROCESSLIST TxnStart long subquery time, stale read global optimization TxnScope Coprocessor tasks, follower read flashback errors before retrying, ON UPDATE primary key data and indexes are inconsistent, permission table case sensitivity, UNIX_TIMESTAMP() upper limit 3001-01-19 03:14:07.999999 UTC, adding an index fails in the ingest mode, canceling a DDL task in the rollback state, memTracker cursor fetch memory leaks, dropping a database causes slow GC progress, partitioned tables probe phase of index join, SUBPARTITION create partitioned tables warning, MAX_EXECUTION_TIME returned error message, LEADING hint block aliases, LAST_INSERT_ID() return type LONGLONG, Join Reorder incorrect outer join results, tidb_mem_quota_query PREPARE stmt FROM "ANALYZE TABLE xxx", stale pessimistic lock conflicts, in-memory pessimistic lock flashback failures, autocommit point get replica read linearizability, redundant replicas cannot be automatically repaired, TiFlash Join build side memory, BR checksum mismatch falsely reported, resolved lock timeout falsely reported, restoring statistics information panic, TiCDC Resolved TS does not advance properly, UPDATE old values Avro CSV protocol, Kafka downstream metadata too frequently, downstream bidirectional replication-related variables, PD node crashing causes the TiCDC node to restart, Kafka-on-Pulsar changefeed, experimental.allow-expression-index UUID, task exits while dividing a data file
- Follow-up Guidance: This chunk also lists related 7.2.0 fixes for PD replica repair, TiFlash join memory usage, BR restore and lock-reporting errors, TiCDC changefeed and downstream issues, and TiDB Lightning panic cases.
- Classification Note: The official content is a release-notes bug-fix summary for TiDB 7.2.0 spanning multiple components and specific issue symptoms.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that the query with CTE causes TiDB to hang [#43749](https://github.com/pingcap/tidb/issues/43749) [#36896](https://github.com/pingcap/tidb/issues/36896) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that the `min, max` query result is incorrect [#43805](https://github.com/pingcap/tidb/issues/43805) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the `SHOW PROCESSLIST` statement cannot display the TxnStart of the transaction of the statement with a long subquery time [#40851](https://github.com/pingcap/tidb/issues/40851) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that the stale read global optimization does not take effect due to the lack of `TxnScope` in Coprocessor tasks [#43365](https://github.com/pingcap/tidb/issues/43365) @[you06](https://github.com/you06)
    - Fix the issue that follower read does not handle flashback errors before retrying, which causes query errors [#43673](https://github.com/pingcap/tidb/issues/43673) @[you06](https://github.com/you06)
    - Fix the issue that data and indexes are inconsistent when the `ON UPDATE` statement does not correctly update the primary key [#44565](https://github.com/pingcap/tidb/issues/44565) @[zyguan](https://github.com/zyguan)
    - Fix the case sensitivity issue in some columns of the permission table [#41048](https://github.com/pingcap/tidb/issues/41048) @[bb7133](https://github.com/bb7133)
    - Modify the upper limit of the `UNIX_TIMESTAMP()` function to `3001-01-19 03:14:07.999999 UTC` to be consistent with that of MySQL 8.0.28 or later versions [#43987](https://github.com/pingcap/tidb/issues/43987) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that adding an index fails in the ingest mode [#44137](https://github.com/pingcap/tidb/issues/44137) @[tangenta](https://github.com/tangenta)
    - Fix the issue that canceling a DDL task in the rollback state causes errors in related metadata [#44143](https://github.com/pingcap/tidb/issues/44143) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that using `memTracker` with cursor fetch causes memory leaks [#44254](https://github.com/pingcap/tidb/issues/44254) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that dropping a database causes slow GC progress [#33069](https://github.com/pingcap/tidb/issues/33069) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that TiDB returns an error when the corresponding rows in partitioned tables cannot be found in the probe phase of index join [#43686](https://github.com/pingcap/tidb/issues/43686) @[AilinKid](https://github.com/AilinKid) @[mjonss](https://github.com/mjonss)
    - Fix the issue that there is no warning when using `SUBPARTITION` to create partitioned tables [#41198](https://github.com/pingcap/tidb/issues/41198) [#41200](https://github.com/pingcap/tidb/issues/41200) @[mjonss](https://github.com/mjonss)
    - Fix the issue that when a query is killed because it exceeds `MAX_EXECUTION_TIME`, the returned error message is inconsistent with that of MySQL [#43031](https://github.com/pingcap/tidb/issues/43031) @[dveeden](https://github.com/dveeden)
    - Fix the issue that the `LEADING` hint does not support querying block aliases [#44645](https://github.com/pingcap/tidb/issues/44645) @[qw4990](https://github.com/qw4990)
    - Modify the return type of the `LAST_INSERT_ID()` function from VARCHAR to LONGLONG to be consistent with that of MySQL [#44574](https://github.com/pingcap/tidb/issues/44574) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that incorrect results might be returned when using a common table expression (CTE) in statements with non-correlated subqueries [#44051](https://github.com/pingcap/tidb/issues/44051) @[winoros](https://github.com/winoros)
    - Fix the issue that Join Reorder might cause incorrect outer join results [#44314](https://github.com/pingcap/tidb/issues/44314) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that `PREPARE stmt FROM "ANALYZE TABLE xxx"` might be killed by `tidb_mem_quota_query` [#44320](https://github.com/pingcap/tidb/issues/44320) @[chrysan](https://github.com/chrysan)

+ TiKV

    - Fix the issue that the transaction returns an incorrect value when TiKV handles stale pessimistic lock conflicts [#13298](https://github.com/tikv/tikv/issues/13298) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the issue that in-memory pessimistic lock might cause flashback failures and data inconsistency [#13303](https://github.com/tikv/tikv/issues/13303) @[JmPotato](https://github.com/JmPotato)
    - Fix the issue that the fair lock might be incorrect when TiKV handles stale requests [#13298](https://github.com/tikv/tikv/issues/13298) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the issue that `autocommit` and `point get replica read` might break linearizability [#14715](https://github.com/tikv/tikv/issues/14715) @[cfzjywxk](https://github.com/cfzjywxk)

+ PD

    - Fix the issue that redundant replicas cannot be automatically repaired in some corner cases [#6573](https://github.com/tikv/pd/issues/6573) @[nolouch](https://github.com/nolouch)

+ TiFlash

    - Fix the issue that queries might consume more memory than needed when the data on the Join build side is very large and contains many small string type columns [#7416](https://github.com/pingcap/tiflash/issues/7416) @[yibin87](https://github.com/yibin87)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that `checksum mismatch` is falsely reported in some cases [#44472](https://github.com/pingcap/tidb/issues/44472) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that `resolved lock timeout` is falsely reported in some cases [#43236](https://github.com/pingcap/tidb/issues/43236) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that TiDB might panic when restoring statistics information [#44490](https://github.com/pingcap/tidb/issues/44490) @[tangenta](https://github.com/tangenta)

    + TiCDC

        - Fix the issue that Resolved TS does not advance properly in some cases [#8963](https://github.com/pingcap/tiflow/issues/8963) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that the `UPDATE` operation cannot output old values when the Avro or CSV protocol is used [#9086](https://github.com/pingcap/tiflow/issues/9086) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue of excessive downstream pressure caused by reading downstream metadata too frequently when replicating data to Kafka [#8959](https://github.com/pingcap/tiflow/issues/8959) @[hi-rustin](https://github.com/Rustin170506)
        - Fix the issue of too many downstream logs caused by frequently setting the downstream bidirectional replication-related variables when replicating data to TiDB or MySQL [#9180](https://github.com/pingcap/tiflow/issues/9180) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that the PD node crashing causes the TiCDC node to restart [#8868](https://github.com/pingcap/tiflow/issues/8868) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that TiCDC cannot create a changefeed with a downstream Kafka-on-Pulsar [#8892](https://github.com/pingcap/tiflow/issues/8892) @[hi-rustin](https://github.com/Rustin170506)

    + TiDB Lightning
        - Fix the TiDB Lightning panic issue when `experimental.allow-expression-index` is enabled and the default value is UUID [#44497](https://github.com/pingcap/tidb/issues/44497) @[lichunzhu](https://github.com/lichunzhu)
        - Fix the TiDB Lightning panic issue when a task exits while dividing a data file [#43195](https://github.com/pingcap/tidb/issues/43195) @[lance6716](https://github.com/lance6716)
