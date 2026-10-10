# Bug fixes across TiKV, PD, TiFlash, BR, TiCDC, Binlog, DM, and Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.3.0.md`
- Source Title: `TiDB 6.3.0 Release Notes`
- Source Heading Path: `TiDB 6.3.0 Release Notes > Bug fixes`
- Source Line Ranges: `371-428`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dm`, `lightning`
- Topic Tags: `bug-fixes`, `raftstore`, `region-heartbeat`, `deadlock`, `encryption`, `json`, `mysql-compatibility`, `panic`, `pitr`, `checkpoint`, `changefeed`, `replication`, `backup-restore`, `log-backup`, `binlog`, `parquet`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0345_bfea4de5c6`
- Source ID: `tidb-docs-8.1:releases/release-6.3.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b9ae084fee5eef5fe8abd2cf132c362b933596af3b2e25bb2fbf733963f83809`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.3.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.3.0 bug fixes across TiKV, PD, TiFlash, BR, TiCDC, TiDB Binlog, DM, or TiDB Lightning for specific errors, panics, compatibility issues, replication problems, or backup and restore issues.
- Retrieval Keywords: TiDB 6.3.0 bug fixes, PD does not reconnect to TiKV after the Region heartbeat is interrupted, Regions might be overlapped if Raftstore is busy, PD client might cause deadlocks, TiKV might panic when encryption is disabled, Unified Read Pool CPU, TiKV service is unavailable for several minutes when a TiKV instance is in an isolated network environment, PessimisticLockNotFound, PITR might cause data loss, checkpoint not advanced, long pessimistic transactions, TiKV does not distinguish the datetime type and STRING type in JSON, incompatibility with MySQL of comparison between JSON bool and other JSON value, enable-forwarding, PD panic, unhealthy Region might cause PD panic, TiFlash learner replica might not be created, window function might cause TiFlash to crash when the query is canceled, CAST(value AS DATETIME), CAST(Real/Decimal AS time), page GC might block creating tables, checkpoint being stale, log backup checkpoint TS stuck, TiCDC exists in the cluster, wrong PD address with a grpc service, cdc cause cli changefeed list, failed changefeeds, Drainer cannot send requests correctly to Pump when compressor is set to gzip, Specified key was too long, collation_compatible, found error when get timezone from binlog status_vars, latin1 data might be corrupted during replication, columns starting with slash, number, or non-ascii characters in Parquet files
- Follow-up Guidance: The chunk groups fixes by component, including TiKV, PD, TiFlash, BR, TiCDC, TiDB Binlog, DM, and TiDB Lightning, and names the exact issue text for each fix.
- Classification Note: This is a release-note bug-fix summary for TiDB 6.3.0 covering multiple components and issue-specific fixes listed in the official content.

## Official Source Content

- Fix the issue that PD does not reconnect to TiKV after the Region heartbeat is interrupted [#12934](https://github.com/tikv/tikv/issues/12934) @[bufferflies](https://github.com/bufferflies)
    - Fix the issue that Regions might be overlapped if Raftstore is busy [#13160](https://github.com/tikv/tikv/issues/13160) @[5kbpers](https://github.com/5kbpers)
    - Fix the issue that the PD client might cause deadlocks [#13191](https://github.com/tikv/tikv/issues/13191) @[bufferflies](https://github.com/bufferflies) [#12933](https://github.com/tikv/tikv/issues/12933) @[BurtonQin](https://github.com/BurtonQin)
    - Fix the issue that TiKV might panic when encryption is disabled [#13081](https://github.com/tikv/tikv/issues/13081) @[jiayang-zheng](https://github.com/jiayang-zheng)
    - Fix the wrong expression of `Unified Read Pool CPU` in Dashboard [#13086](https://github.com/tikv/tikv/issues/13086) @[glorv](https://github.com/glorv)
    - Fix the issue that the TiKV service is unavailable for several minutes when a TiKV instance is in an isolated network environment [#12966](https://github.com/tikv/tikv/issues/12966) @[cosven](https://github.com/cosven)
    - Fix the issue that TiKV mistakenly reports a `PessimisticLockNotFound` error [#13425](https://github.com/tikv/tikv/issues/13425) @[sticnarf](https://github.com/sticnarf)
    - Fix the issue that PITR might cause data loss in some situations [#13281](https://github.com/tikv/tikv/issues/13281) @[YuJuncen](https://github.com/YuJuncen)
    - Fix the issue that causes checkpoint not advanced when there are some long pessimistic transactions [#13304](https://github.com/tikv/tikv/issues/13304) @[YuJuncen](https://github.com/YuJuncen)
    - Fix the issue that TiKV does not distinguish the datetime type (`DATETIME`, `DATE`, `TIMESTAMP` and `TIME`) and `STRING` type in JSON [#13417](https://github.com/tikv/tikv/issues/13417) @[YangKeao](https://github.com/YangKeao)
    - Fix incompatibility with MySQL of comparison between JSON bool and other JSON value [#13386](https://github.com/tikv/tikv/issues/13386) [#37481](https://github.com/pingcap/tidb/issues/37481) @[YangKeao](https://github.com/YangKeao)

+ PD

    - Fix PD panics caused by the issue that gRPC handles errors inappropriately when `enable-forwarding` is enabled [#5373](https://github.com/tikv/pd/issues/5373) @[bufferflies](https://github.com/bufferflies)
    - Fix the issue that unhealthy Region might cause PD panic [#5491](https://github.com/tikv/pd/issues/5491) @[nolouch](https://github.com/nolouch)
    - Fix the issue that the TiFlash learner replica might not be created [#5401](https://github.com/tikv/pd/issues/5401) @[HunDunDM](https://github.com/HunDunDM)

+ TiFlash

    - Fix the issue that a window function might cause TiFlash to crash when the query is canceled [#5814](https://github.com/pingcap/tiflash/issues/5814) @[SeaRise](https://github.com/SeaRise)
    - Fix the issue that wrong data input for `CAST(value AS DATETIME)` causing high TiFlash sys CPU [#5097](https://github.com/pingcap/tiflash/issues/5097) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that the result of `CAST(Real/Decimal AS time)` is inconsistent with MySQL [#3779](https://github.com/pingcap/tiflash/issues/3779) @[mengxin9014](https://github.com/mengxin9014)
    - Fix the issue that some obsolete data in storage cannot be deleted [#5570](https://github.com/pingcap/tiflash/issues/5570) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that page GC might block creating tables [#5697](https://github.com/pingcap/tiflash/issues/5697) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the panic that occurs after creating the primary index with a column containing the `NULL` value [#5859](https://github.com/pingcap/tiflash/issues/5859) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that might cause the information of the checkpoint being stale [#36423](https://github.com/pingcap/tidb/issues/36423) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that the regions are not balanced because the concurrency is set too large during the restoration [#37549](https://github.com/pingcap/tidb/issues/37549) @[3pointer](https://github.com/3pointer)
        - Fix the issue that might cause log backup checkpoint TS stuck when TiCDC exists in the cluster [#37822](https://github.com/pingcap/tidb/issues/37822) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that might lead to backup and restoration failure if special characters exist in the authorization key of external storage [#37469](https://github.com/pingcap/tidb/issues/37469) @[MoCuishle28](https://github.com/MoCuishle28)

    + TiCDC

        - Fix the issue that TiCDC returns an inaccurate error for a wrong PD address with a grpc service [#6458](https://github.com/pingcap/tiflow/issues/6458) @[crelax](https://github.com/crelax)
        - Fix the issue that the `cdc cause cli changefeed list` command does not return failed changefeeds [#6334](https://github.com/pingcap/tiflow/issues/6334) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that TiCDC is unavailable when changefeed initialization fails [#6859](https://github.com/pingcap/tiflow/issues/6859) @[asddongmen](https://github.com/asddongmen)

    + TiDB Binlog

        - Fix the issue that Drainer cannot send requests correctly to Pump when compressor is set to gzip [#1152](https://github.com/pingcap/tidb-binlog/issues/1152) @[lichunzhu](https://github.com/lichunzhu)

    + TiDB Data Migration (DM)

        - Fix the issue that DM reports the `Specified key was too long` error [#5315](https://github.com/pingcap/tiflow/issues/5315) @[lance6716](https://github.com/lance6716)
        - Fix goroutine leak when relay meets an error [#6193](https://github.com/pingcap/tiflow/issues/6193) @[lance6716](https://github.com/lance6716)
        - Fix the issue that when `collation_compatible` is set to `"strict"`, DM might generate SQL with duplicated collations [#6832](https://github.com/pingcap/tiflow/issues/6832) @[lance6716](https://github.com/lance6716)
        - Reduce the appearance of the warning message "found error when get timezone from binlog status_vars" in DM-worker log [#6628](https://github.com/pingcap/tiflow/issues/6628) @[lyzx2001](https://github.com/lyzx2001)
        - Fix the issue that latin1 data might be corrupted during replication [#7028](https://github.com/pingcap/tiflow/issues/7028) @[lance6716](https://github.com/lance6716)

    + TiDB Lightning

        - Fix the issue that TiDB Lightning does not support columns starting with slash, number, or non-ascii characters in Parquet files [#36980](https://github.com/pingcap/tidb/issues/36980) @[D3Hunter](https://github.com/D3Hunter)
