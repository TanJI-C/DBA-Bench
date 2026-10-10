# Bug fixes across TiFlash and tools in TiDB 7.5.5

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.5.md`
- Source Title: `TiDB 7.5.5 Release Notes`
- Source Heading Path: `TiDB 7.5.5 Release Notes > Bug fixes`
- Source Line Ranges: `125-167`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiflash`, `br`, `ticdc`, `dm`, `lightning`, `dumpling`, `tidb`, `tikv`
- Topic Tags: `bug-fixes`, `release-notes`, `tiflash`, `backup-restore`, `log-backup`, `pitr`, `replication`, `ddl`, `dm`, `import`, `physical-import`, `cloud-storage`, `gcs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0547_d47473ce69`
- Source ID: `tidb-docs-8.1:releases/release-7.5.5.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e4860ccc60d36731274503d7547027d1227a59afc06c32038ce98e4dba4edded`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.5#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.5.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.5 bug fixes affecting TiFlash or tools such as BR, TiCDC, DM, TiDB Lightning, and Dumpling, including specific errors, SQL functions, DDL replication, physical import, PITR, log backup, and GCS retry behavior.
- Retrieval Keywords: TiDB 7.5.5 Release Notes, Bug fixes, TiFlash panic concurrent DDL execution, #8578, LPAD() RPAD() incorrect results, #9465, SUBSTRING() second parameter is negative, #9604, Bit-type columns default value invalid characters table schema parse, #9461, disaggregated storage and compute architecture new columns incorrect results, #9665, BR the target cluster is not fresh checkpoint restore fails, #50232, log backups residual locks checkpoint fail to advance, #57134, logs might print out encrypted information, #57585, PITR Information schema is out of date, #57743, TiCDC TRUNCATE TABLE DDL table without valid index, #11765, Simple Protocol partitioned tables tableID, #11846, redo module fails to properly report errors, #11744, ignore-event add table partition DML changes not replicated, #10524, DDL owner changes schema versions non-incremental discards DDL tasks, #11714, DM physical import mode generated IDs significant jumps, #11768, start-task pre-check TLS shard-mode fails, #11842, MySQL 8.0 password length exceeds 19 characters, #11603, TiDB Lightning oversized messages sent from TiKV, #56114, AUTO_INCREMENT value set too high physical import mode, #56814, Lock wait timeout metadata updates retry, #53042, cloud storage high-concurrency performance degrades, #57413, large number of Parquet files preparation phase stuck, #56104, error report output is truncated, #58085, Dumpling 503 error Google Cloud Storage GCS retry, #56127
- Follow-up Guidance: The chunk groups the fixes by component, including TiFlash, Backup & Restore (BR), TiCDC, TiDB Data Migration (DM), TiDB Lightning, and Dumpling.
- Classification Note: The official content is a release-notes bug-fix summary for TiDB 7.5.5 across shared components and tools in self-managed deployments.

## Official Source Content

- Fix the TiFlash panic issue when TiFlash encounters conflicts during concurrent DDL execution [#8578](https://github.com/pingcap/tiflash/issues/8578) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that `LPAD()` and `RPAD()` functions return incorrect results in some cases [#9465](https://github.com/pingcap/tiflash/issues/9465) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that the `SUBSTRING()` function returns incorrect results when the second parameter is negative [#9604](https://github.com/pingcap/tiflash/issues/9604) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that TiFlash fails to parse the table schema when the table contains Bit-type columns with a default value that contains invalid characters [#9461](https://github.com/pingcap/tiflash/issues/9461) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that querying new columns might return incorrect results under the disaggregated storage and compute architecture [#9665](https://github.com/pingcap/tiflash/issues/9665) @[zimulala](https://github.com/zimulala)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that when resuming from a checkpoint after data restore fails, an error `the target cluster is not fresh` occurs [#50232](https://github.com/pingcap/tidb/issues/50232) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that log backups cannot resolve residual locks promptly, causing the checkpoint to fail to advance [#57134](https://github.com/pingcap/tidb/issues/57134) @[3pointer](https://github.com/3pointer)
        - Fix the issue that logs might print out encrypted information [#57585](https://github.com/pingcap/tidb/issues/57585) @[kennytm](https://github.com/kennytm)
        - Fix the issue that the `TestStoreRemoved` test case is unstable [#52791](https://github.com/pingcap/tidb/issues/52791) @[YuJuncen](https://github.com/YuJuncen)
        - Fix potential security vulnerabilities by upgrading the `k8s.io/api` library version [#57790](https://github.com/pingcap/tidb/issues/57790) @[BornChanger](https://github.com/BornChanger)
        - Fix the issue that PITR tasks might return the `Information schema is out of date` error when there are a large number of tables in the cluster but the actual data size is small [#57743](https://github.com/pingcap/tidb/issues/57743) @[Tristan1900](https://github.com/Tristan1900)

    + TiCDC

        - Fix the issue that TiCDC might report an error when replicating a `TRUNCATE TABLE` DDL on a table without valid index [#11765](https://github.com/pingcap/tiflow/issues/11765) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that the `tableID` for partitioned tables is not correctly set in Simple Protocol messages [#11846](https://github.com/pingcap/tiflow/issues/11846) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that the redo module fails to properly report errors [#11744](https://github.com/pingcap/tiflow/issues/11744) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that after filtering out `add table partition` events is configured in `ignore-event`, TiCDC does not replicate other types of DML changes for related partitions to the downstream [#10524](https://github.com/pingcap/tiflow/issues/10524) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that TiCDC mistakenly discards DDL tasks when the schema versions of DDL tasks become non-incremental during TiDB DDL owner changes [#11714](https://github.com/pingcap/tiflow/issues/11714) @[wlwilliamx](https://github.com/wlwilliamx)

    + TiDB Data Migration (DM)

        - Fix the issue that automatically generated IDs in a table might have significant jumps after data import in physical import mode [#11768](https://github.com/pingcap/tiflow/issues/11768) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that the pre-check of `start-task` fails when both TLS and `shard-mode` are configured [#11842](https://github.com/pingcap/tiflow/issues/11842) @[sunxiaoguang](https://github.com/sunxiaoguang)
        - Fix the issue that connecting to MySQL 8.0 fails when the password length exceeds 19 characters [#11603](https://github.com/pingcap/tiflow/issues/11603) @[fishiu](https://github.com/fishiu)

    + TiDB Lightning

        - Fix the issue that TiDB Lightning fails to receive oversized messages sent from TiKV [#56114](https://github.com/pingcap/tidb/issues/56114) @[fishiu](https://github.com/fishiu)
        - Fix the issue that the `AUTO_INCREMENT` value is set too high after importing data using the physical import mode [#56814](https://github.com/pingcap/tidb/issues/56814) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that TiDB Lightning does not automatically retry when encountering `Lock wait timeout` errors during metadata updates [#53042](https://github.com/pingcap/tidb/issues/53042) @[guoshouyan](https://github.com/guoshouyan)
        - Fix the issue that the performance degrades when importing data from a cloud storage in high-concurrency scenarios [#57413](https://github.com/pingcap/tidb/issues/57413) @[xuanyu66](https://github.com/xuanyu66)
        - Fix the issue that TiDB Lightning might get stuck for a long time during the preparation phase when importing a large number of Parquet files [#56104](https://github.com/pingcap/tidb/issues/56104) @[zeminzhou](https://github.com/zeminzhou)
        - Fix the issue that the error report output is truncated when importing data using TiDB Lightning [#58085](https://github.com/pingcap/tidb/issues/58085) @[lance6716](https://github.com/lance6716)

    + Dumpling

        - Fix the issue that Dumpling fails to retry properly when receiving a 503 error from Google Cloud Storage (GCS) [#56127](https://github.com/pingcap/tidb/issues/56127) @[OliverS929](https://github.com/OliverS929)
