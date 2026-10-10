# Bug fixes for TiFlash, BR, TiCDC, and DM

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.12.md`
- Source Title: `TiDB 6.5.12 Release Notes`
- Source Heading Path: `TiDB 6.5.12 Release Notes > Bug fixes`
- Source Line Ranges: `130-175`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiflash`, `br`, `ticdc`, `dm`, `pd`, `tikv`, `tidb`
- Topic Tags: `bug-fixes`, `tiflash`, `backup-restore`, `log-backup`, `pitr`, `changefeed`, `replication`, `ddl`, `pd-scale-in`, `leader-election`, `data-consistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0388_a5cc6c55ce`
- Source ID: `tidb-docs-8.1:releases/release-6.5.12.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `90847df0d20b0f34559bc5c59df0dae8f397e8da0398342851ab297402875b6a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.12#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.12.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.12 bug fixes related to TiFlash SQL function behavior, BR restore or log backup issues, TiCDC changefeed and DDL replication problems, or DM leader election and connectivity issues.
- Retrieval Keywords: TiDB 6.5.12 bug fixes, TiFlash SUBSTRING() pos len integer types, TiFlash JSON functions unsupported pushed down, TiFlash SUBSTRING() second parameter negative, TiFlash LPAD() RPAD() incorrect results, DROP TABLE large tables TiFlash OOM, TiFlash fails to start division by zero CPU cores, TiFlash high memory usage after importing large amounts of data, BR rpcClient is idle restore TiKV, br log status --json status field missing, PD Leader I/O latency log backup checkpoint latency, tiup br restore target cluster table already exists overwrite existing tables, log backup paused advancer owner switches, log backups residual locks checkpoint fail to advance, logs print out encrypted information, PITR Information schema is out of date, TiCDC RENAME TABLE filtering incorrect table names, TiCDC default NULL Avro protocol, TiCDC PD scale-in connect to PD, Initial Scan not canceled changefeed stopped or deleted, --overwrite-checkpoint-ts changefeed pause stuck, CREATE TABLE IF NOT EXISTS TiCDC panic, TRUNCATE TABLE DDL table without valid index, DDL owner changes schema versions non-incremental, new TiKV nodes added changefeed stuck, Sarama client Kafka message order incorrect, Resolved TS latency Puller incorrect values, redo module fails to properly report errors, DM-master simultaneously become leaders, MySQL 8.0 password length exceeds 19 characters, start-task pre-check TLS shard-mode
- Follow-up Guidance: 
- Classification Note: The official content is a release-notes bug-fix list covering multiple components under TiDB 6.5.12, including TiFlash, BR, TiCDC, and DM.

## Official Source Content

- Fix the issue that the `SUBSTRING()` function does not support the `pos` and `len` arguments for certain integer types, causing query errors [#9473](https://github.com/pingcap/tiflash/issues/9473) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that some JSON functions unsupported by TiFlash are pushed down to TiFlash [#9444](https://github.com/pingcap/tiflash/issues/9444) @[windtalker](https://github.com/windtalker)
    - Fix the issue that the `SUBSTRING()` function returns incorrect results when the second parameter is negative [#9604](https://github.com/pingcap/tiflash/issues/9604) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that `LPAD()` and `RPAD()` functions return incorrect results in some cases [#9465](https://github.com/pingcap/tiflash/issues/9465) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that executing `DROP TABLE` on large tables might cause TiFlash OOM [#9437](https://github.com/pingcap/tiflash/issues/9437) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash fails to start due to a division by zero error when retrieving the number of CPU cores [#9212](https://github.com/pingcap/tiflash/issues/9212) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that TiFlash might maintain high memory usage after importing large amounts of data [#9812](https://github.com/pingcap/tiflash/issues/9812) @[CalvinNeo](https://github.com/CalvinNeo)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that BR fails to restore due to getting the `rpcClient is idle` error when sending requests to TiKV [#58845](https://github.com/pingcap/tidb/issues/58845) @[Tristan1900](https://github.com/Tristan1900)
        - Fix the issue that the `status` field is missing in the result when querying log backup tasks using `br log status --json` [#57959](https://github.com/pingcap/tidb/issues/57959) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that PD Leader I/O latency during log backup might increase checkpoint latency [#58574](https://github.com/pingcap/tidb/issues/58574) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that the `tiup br restore` command omits checking whether the target cluster table already exists during database or table restoration, which might overwrite existing tables [#58168](https://github.com/pingcap/tidb/issues/58168) @[RidRisR](https://github.com/RidRisR)
        - Fix the issue that log backup might unexpectedly enter a paused state when the advancer owner switches [#58031](https://github.com/pingcap/tidb/issues/58031) @[3pointer](https://github.com/3pointer)
        - Fix the issue that log backups cannot resolve residual locks promptly, causing the checkpoint to fail to advance [#57134](https://github.com/pingcap/tidb/issues/57134) @[3pointer](https://github.com/3pointer)
        - Fix the issue that BR integration test cases are unstable, and add a new test case to simulate snapshot or log backup file corruption [#53835](https://github.com/pingcap/tidb/issues/53835) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that logs might print out encrypted information [#57585](https://github.com/pingcap/tidb/issues/57585) @[kennytm](https://github.com/kennytm)
        - Fix the issue that PITR tasks might return the `Information schema is out of date` error when there are a large number of tables in the cluster but the actual data size is small [#57743](https://github.com/pingcap/tidb/issues/57743) @[Tristan1900](https://github.com/Tristan1900)

    + TiCDC
    
        - Fix the issue that TiCDC uses incorrect table names for filtering during `RENAME TABLE` operations [#11946](https://github.com/pingcap/tiflow/issues/11946) @[wk989898](https://github.com/wk989898)
        - Fix the issue that TiCDC reports errors when replicating `default NULL` SQL statements via the Avro protocol [#11994](https://github.com/pingcap/tiflow/issues/11994) @[wk989898](https://github.com/wk989898)
        - Fix the issue that TiCDC fails to properly connect to PD after PD scale-in [#12004](https://github.com/pingcap/tiflow/issues/12004) @[lidezhu](https://github.com/lidezhu)
        - Fix the issue that Initial Scan is not canceled after the changefeed is stopped or deleted [#11638](https://github.com/pingcap/tiflow/issues/11638) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that after the default value of a newly added column in the upstream is changed from `NOT NULL` to `NULL`, the default values of that column in the downstream are incorrect [#12037](https://github.com/pingcap/tiflow/issues/12037) @[wk989898](https://github.com/wk989898)
        - Fix the issue that using the `--overwrite-checkpoint-ts` parameter in the `changefeed pause` command might cause the changefeed to be stuck [#12055](https://github.com/pingcap/tiflow/issues/12055) @[hongyunyan](https://github.com/hongyunyan)
        - Fix the issue that TiCDC might panic when replicating `CREATE TABLE IF NOT EXISTS` or `CREATE DATABASE IF NOT EXISTS` statements [#11839](https://github.com/pingcap/tiflow/issues/11839) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that TiCDC might report an error when replicating a `TRUNCATE TABLE` DDL on a table without valid index [#11765](https://github.com/pingcap/tiflow/issues/11765) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that TiCDC mistakenly discards DDL tasks when the schema versions of DDL tasks become non-incremental during TiDB DDL owner changes [#11714](https://github.com/pingcap/tiflow/issues/11714) @[wlwilliamx](https://github.com/wlwilliamx)
        - Fix the issue that the changefeed might get stuck after new TiKV nodes are added to the cluster [#11766](https://github.com/pingcap/tiflow/issues/11766) @[lidezhu](https://github.com/lidezhu)
        - Fix the issue that out-of-order messages resent by the Sarama client cause Kafka message order to be incorrect [#11935](https://github.com/pingcap/tiflow/issues/11935) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that the Resolved TS latency monitoring in the Puller module displays incorrect values [#11561](https://github.com/pingcap/tiflow/issues/11561) @[wlwilliamx](https://github.com/wlwilliamx)
        - Fix the issue that the redo module fails to properly report errors [#11744](https://github.com/pingcap/tiflow/issues/11744) @[CharlesCheung96](https://github.com/CharlesCheung96)

    + TiDB Data Migration (DM)

        - Fix the issue that multiple DM-master nodes might simultaneously become leaders, leading to data inconsistency [#11602](https://github.com/pingcap/tiflow/issues/11602) @[GMHDBJD](https://github.com/GMHDBJD)
        - Fix the issue that connecting to MySQL 8.0 fails when the password length exceeds 19 characters [#11603](https://github.com/pingcap/tiflow/issues/11603) @[fishiu](https://github.com/fishiu)
        - Fix the issue that the pre-check of `start-task` fails when both TLS and `shard-mode` are configured [#11842](https://github.com/pingcap/tiflow/issues/11842) @[sunxiaoguang](https://github.com/sunxiaoguang)

    + TiDB Lightning
