# Bug fixes across TiDB, TiKV, PD, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.0.md`
- Source Title: `TiDB 7.1.0 Release Notes`
- Source Heading Path: `TiDB 7.1.0 Release Notes > Bug fixes`
- Source Line Ranges: `458-533`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dm`, `dumpling`, `lightning`
- Topic Tags: `bug-fixes`, `transactions`, `plan-cache`, `ddl`, `pitr`, `replication`, `monitoring`, `backup`, `restore`, `data-import`, `cdc`, `migration`, `timezone`, `oom`, `panic`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0452_80fd8d173f`
- Source ID: `tidb-docs-8.1:releases/release-7.1.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4da8adfba488f27cf55889c485db26b7ad37ad0e3bc1ac9140eabdf575923ad1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.0 bug fixes across TiDB, TiKV, PD, TiFlash, BR, TiCDC, DM, Dumpling, Binlog, or Lightning for issues involving transactions, plan cache, DDL, PITR, replication, monitoring, backup and restore, or data import.
- Retrieval Keywords: TiDB 7.1.0 bug fixes, TiCDC lose some row changes during table renaming, TiDB server crashes when the client uses cursor reads, ADMIN SHOW DDL JOBS LIMIT returns incorrect results, union views and temporary tables with UNION panic, renaming tables does not take effect when committing multiple statements in a transaction, prepared plan cache and non-prepared plan cache during time conversion, wrong results caused by plan cache for Decimal type, null-aware anti join NAAJ panic, pessimistic transactions at the RC isolation level might cause inconsistency between data and indexes, residual pessimistic locks, LOCK to PUT optimization duplicate data, tidb_pessimistic_txn_fair_locking, raft entry is too large during the PITR recovery process, log_batch exceeding 2 GB, low space store, Region Health monitoring data is deleted after PD leader switch, schedule=deny label, TIMESTAMP or TIME returns errors after enabling late materialization, backup slowdown when a TiKV node crashes, TiCDC time zone setting, checkpoint lag increases when one of the upstream TiKV nodes crashes, EXCHANGE PARTITION operation, sorter component OOM, downstream Kafka sinks are rolling restarted, latin1 data might be corrupted during replication, UNSIGNED INTEGER type primary key cannot be used for splitting chunks, write to tikv with no leader returned, keys within region is empty, skip doIngest, keyspace-name
- Follow-up Guidance: The chunk groups the fixes by component, including TiDB, TiKV, PD, TiFlash, and tools such as BR, TiCDC, DM, Dumpling, Binlog, and Lightning.
- Classification Note: This is a release-note bug-fix summary for TiDB 7.1.0 covering multiple components and issue-specific fixes listed in the official content.

## Official Source Content

- Fix the issue that TiCDC might lose some row changes during table renaming [#43338](https://github.com/pingcap/tidb/issues/43338) @[tangenta](https://github.com/tangenta)
    - Fix the issue that TiDB server crashes when the client uses cursor reads [#38116](https://github.com/pingcap/tidb/issues/38116) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that `ADMIN SHOW DDL JOBS LIMIT` returns incorrect results [#42298](https://github.com/pingcap/tidb/issues/42298) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Fix the TiDB panic issue that occurs when querying union views and temporary tables with `UNION` [#42563](https://github.com/pingcap/tidb/issues/42563) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that renaming tables does not take effect when committing multiple statements in a transaction [#39664](https://github.com/pingcap/tidb/issues/39664) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the incompatibility issue between the behavior of prepared plan cache and non-prepared plan cache during time conversion [#42439](https://github.com/pingcap/tidb/issues/42439) @[qw4990](https://github.com/qw4990)
    - Fix the wrong results caused by plan cache for Decimal type [#43311](https://github.com/pingcap/tidb/issues/43311) @[qw4990](https://github.com/qw4990)
    - Fix the TiDB panic issue in null-aware anti join (NAAJ) due to the wrong field type check [#42459](https://github.com/pingcap/tidb/issues/42459) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that DML execution failures in pessimistic transactions at the RC isolation level might cause inconsistency between data and indexes [#43294](https://github.com/pingcap/tidb/issues/43294) @[ekexium](https://github.com/ekexium)
    - Fix the issue that in some extreme cases, when the first statement of a pessimistic transaction is retried, resolving locks on this transaction might affect transaction correctness [#42937](https://github.com/pingcap/tidb/issues/42937) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that in some rare cases, residual pessimistic locks of pessimistic transactions might affect data correctness when GC resolves locks [#43243](https://github.com/pingcap/tidb/issues/43243) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that the `LOCK` to `PUT` optimization leads to duplicate data being returned in specific queries [#28011](https://github.com/pingcap/tidb/issues/28011) @[zyguan](https://github.com/zyguan)
    - Fix the issue that when data is changed, the locking behavior of the unique index is not consistent with that when the data is unchanged [#36438](https://github.com/pingcap/tidb/issues/36438) @[zyguan](https://github.com/zyguan)

+ TiKV

    - Fix the issue that when you enable `tidb_pessimistic_txn_fair_locking`, in some extreme cases, expired requests caused by failed RPC retries might affect data correctness during the resolve lock operation [#14551](https://github.com/tikv/tikv/issues/14551) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that when you enable `tidb_pessimistic_txn_fair_locking`, in some extreme cases, expired requests caused by failed RPC retries might cause transaction conflicts to be ignored, thus affecting transaction consistency [#14311](https://github.com/tikv/tikv/issues/14311) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that encryption key ID conflict might cause the deletion of the old keys [#14585](https://github.com/tikv/tikv/issues/14585) @[tabokie](https://github.com/tabokie)
    - Fix the performance degradation issue caused by accumulated lock records when a cluster is upgraded from a previous version to v6.5 or later versions [#14780](https://github.com/tikv/tikv/issues/14780) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that the `raft entry is too large` error occurs during the PITR recovery process [#14313](https://github.com/tikv/tikv/issues/14313) @[YuJuncen](https://github.com/YuJuncen)
    - Fix the issue that TiKV panics during the PITR recovery process due to `log_batch` exceeding 2 GB [#13848](https://github.com/tikv/tikv/issues/13848) @[YuJuncen](https://github.com/YuJuncen)

+ PD

    - Fix the issue that the number of `low space store` in the PD monitoring panel is abnormal after TiKV panics [#6252](https://github.com/tikv/pd/issues/6252) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that Region Health monitoring data is deleted after PD leader switch [#6366](https://github.com/tikv/pd/issues/6366) @[iosmanthus](https://github.com/iosmanthus)
    - Fix the issue that the rule checker cannot repair unhealthy Regions with the `schedule=deny` label [#6426](https://github.com/tikv/pd/issues/6426) @[nolouch](https://github.com/nolouch)
    - Fix the issue that some existing labels are lost after TiKV or TiFlash restarts [#6467](https://github.com/tikv/pd/issues/6467) @[JmPotato](https://github.com/JmPotato)
    - Fix the issue that the replication status cannot be switched when there are learner nodes in the replication mode [#14704](https://github.com/tikv/tikv/issues/14704) @[nolouch](https://github.com/nolouch)

+ TiFlash

    - Fix the issue that querying data in the `TIMESTAMP` or `TIME` type returns errors after enabling late materialization [#7455](https://github.com/pingcap/tiflash/issues/7455) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that large update transactions might cause TiFlash to repeatedly report errors and restart [#7316](https://github.com/pingcap/tiflash/issues/7316) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue of backup slowdown when a TiKV node crashes in a cluster [#42973](https://github.com/pingcap/tidb/issues/42973) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue of inaccurate error messages caused by a backup failure in some cases [#43236](https://github.com/pingcap/tidb/issues/43236) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC

        - Fix the issue of TiCDC time zone setting [#8798](https://github.com/pingcap/tiflow/issues/8798) @[hi-rustin](https://github.com/Rustin170506)
        - Fix the issue that TiCDC cannot automatically recover when PD address or leader fails [#8812](https://github.com/pingcap/tiflow/issues/8812) [#8877](https://github.com/pingcap/tiflow/issues/8877) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that checkpoint lag increases when one of the upstream TiKV nodes crashes [#8858](https://github.com/pingcap/tiflow/issues/8858) @[hicqu](https://github.com/hicqu)
        - Fix the issue that when replicating data to object storage, the `EXCHANGE PARTITION` operation in the upstream cannot be properly replicated to the downstream [#8914](https://github.com/pingcap/tiflow/issues/8914) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the OOM issue caused by excessive memory usage of the sorter component in some special scenarios [#8974](https://github.com/pingcap/tiflow/issues/8974) @[hicqu](https://github.com/hicqu)
        - Fix the TiCDC node panic that occurs when the downstream Kafka sinks are rolling restarted [#9023](https://github.com/pingcap/tiflow/issues/9023) @[asddongmen](https://github.com/asddongmen)

    + TiDB Data Migration (DM)
        - Fix the issue that latin1 data might be corrupted during replication [#7028](https://github.com/pingcap/tiflow/issues/7028) @[lance6716](https://github.com/lance6716)

    + TiDB Dumpling

        - Fix the issue that the `UNSIGNED INTEGER` type primary key cannot be used for splitting chunks [#42620](https://github.com/pingcap/tidb/issues/42620) @[lichunzhu](https://github.com/lichunzhu)
        - Fix the issue that TiDB Dumpling might panic when `--output-file-template` is incorrectly set [#42391](https://github.com/pingcap/tidb/issues/42391) @[lichunzhu](https://github.com/lichunzhu)

    + TiDB Binlog

        - Fix the issue that an error might occur when encountering a failed DDL statement [#1228](https://github.com/pingcap/tidb-binlog/issues/1228) @[okJiang](https://github.com/okJiang)

    + TiDB Lightning

        - Fix the performance degradation issue during data import [#42456](https://github.com/pingcap/tidb/issues/42456) @[lance6716](https://github.com/lance6716)
        - Fix the issue of `write to tikv with no leader returned` when importing a large amount of data [#43055](https://github.com/pingcap/tidb/issues/43055) @[lance6716](https://github.com/lance6716)
        - Fix the issue of excessive `keys within region is empty, skip doIngest` logs during data import [#43197](https://github.com/pingcap/tidb/issues/43197) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that panic might occur during partial write [#43363](https://github.com/pingcap/tidb/issues/43363) @[lance6716](https://github.com/lance6716)
        - Fix the issue that OOM might occur when importing a wide table [#43728](https://github.com/pingcap/tidb/issues/43728) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue of missing data in the TiDB Lightning Grafana dashboard [#43357](https://github.com/pingcap/tidb/issues/43357) @[lichunzhu](https://github.com/lichunzhu)
        - Fix the import failure due to incorrect setting of `keyspace-name` [#43684](https://github.com/pingcap/tidb/issues/43684) @[zeminzhou](https://github.com/zeminzhou)
        - Fix the issue that data import might be skipped during range partial write in some cases [#43768](https://github.com/pingcap/tidb/issues/43768) @[lance6716](https://github.com/lance6716)
