# 6.5.3 bug fixes across TiKV, TiFlash, BR, TiCDC, Lightning, and Binlog

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.3.md`
- Source Title: `TiDB 6.5.3 Release Notes`
- Source Heading Path: `TiDB 6.5.3 Release Notes > Bug fixes`
- Source Line Ranges: `92-139`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `lightning`, `tidb`
- Topic Tags: `bug-fixes`, `stability`, `oom`, `replication`, `backup-restore`, `import`, `kafka`, `pitr`, `encryption`, `performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0396_bfa79c22ac`
- Source ID: `tidb-docs-8.1:releases/release-6.5.3.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cacb115fa7f290083f0ed7cb8982addf02748523b2b269b8df12e0a3de96cc4a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.3#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.3 bug fixes across TiKV, TiFlash, BR, TiCDC, TiDB Lightning, and TiDB Binlog for issues involving hibernate peers, PITR, encryption keys, linearizability, OOM, Kafka, replication, backup errors, or import failures.
- Retrieval Keywords: TiDB 6.5.3 bug fixes, TiKV peers mistakenly hibernate when a TiKV node fails, Continuous Profiling file handle leakage, PD crash might cause PITR to fail to proceed, encryption key ID conflict might cause deletion of old keys, autocommit and point get replica read might break linearizability, accumulated lock records performance degradation upgraded from previous version to v6.5 or later, TiDB Lightning SST file leakage, potential conflict between the encryption key and raft log file deletion might cause TiKV to fail to start, TiFlash partition TableScan Region transfer performance degradation, GENERATED type field present along with TIMESTAMP or TIME type, large update transactions might cause TiFlash to repeatedly report errors and restart, Truncate error cast decimal as decimal, INSERT SELECT, Join build side very large many small string type columns memory, BR resolve lock timeout misleading error message, TiCDC OOM 50000 tables, TiCDC gets stuck when an OOM occurs in upstream TiDB, TiCDC gets stuck when PD fails network isolation PD Owner node reboot, TiCDC time zone setting, checkpoint lag increases when one of the upstream TiKV nodes crashes, FLASHBACK CLUSTER TO TIMESTAMP replication error downstream MySQL, EXCHANGE PARTITION object storage downstream replication, sorter component excessive memory usage, downstream Kafka queries metadata too frequently, oversized Kafka message body is recorded in the log, downstream Kafka sinks are rolling restarted panic, JSON file corresponding to downstream DDL statements does not record the default values of table fields, TiDB Lightning OOM importing a wide table, write to tikv with no leader returned, unknown RPC error during data import retry mechanism, TiDB Binlog CANCELED DDL statement
- Follow-up Guidance: The source groups the fixes by component, including TiKV, TiFlash, BR, TiCDC, TiDB Lightning, and TiDB Binlog, and names the affected error messages and statements such as `resolve lock timeout`, `FLASHBACK CLUSTER TO TIMESTAMP`, `EXCHANGE PARTITION`, `INSERT SELECT`, `write to tikv with no leader returned`, `unknown RPC`, and `CANCELED` DDL.
- Classification Note: This chunk is classified as a release note because it is the Bug fixes section of the TiDB 6.5.3 Release Notes and enumerates resolved issues across multiple components.

## Official Source Content

- Fix the issue that the peers of the corresponding Region mistakenly hibernate when a TiKV node fails [#14547](https://github.com/tikv/tikv/issues/14547) @[hicqu](https://github.com/hicqu)
    - Fix the issue of file handle leakage in Continuous Profiling [#14224](https://github.com/tikv/tikv/issues/14224) @[tabokie](https://github.com/tabokie)
    - Fix the issue that PD crash might cause PITR to fail to proceed [#14184](https://github.com/tikv/tikv/issues/14184) @[YuJuncen](https://github.com/YuJuncen)
    - Fix the issue that encryption key ID conflict might cause the deletion of the old keys [#14585](https://github.com/tikv/tikv/issues/14585) @[tabokie](https://github.com/tabokie)
    - Fix the issue that autocommit and point get replica read might break linearizability [#14715](https://github.com/tikv/tikv/issues/14715) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the performance degradation issue caused by accumulated lock records when a cluster is upgraded from a previous version to v6.5 or later versions [#14780](https://github.com/tikv/tikv/issues/14780) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that TiDB Lightning might cause SST file leakage [#14745](https://github.com/tikv/tikv/issues/14745) @[YuJuncen](https://github.com/YuJuncen)
    - Fix the potential conflict between the encryption key and raft log file deletion that might cause TiKV to fail to start [#14761](https://github.com/tikv/tikv/issues/14761) @[Connor1996](https://github.com/Connor1996)

+ TiFlash

    - Fix the performance degradation issue of the partition TableScan operator during Region transfer [#7519](https://github.com/pingcap/tiflash/issues/7519) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that a TiFlash query might report an error if the `GENERATED` type field is present along with the `TIMESTAMP` or `TIME` type [#7468](https://github.com/pingcap/tiflash/issues/7468) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that large update transactions might cause TiFlash to repeatedly report errors and restart [#7316](https://github.com/pingcap/tiflash/issues/7316) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that the error "Truncate error cast decimal as decimal" occurs when reading data from TiFlash with the `INSERT SELECT` statement [#7348](https://github.com/pingcap/tiflash/issues/7348) @[windtalker](https://github.com/windtalker)
    - Fix the issue that queries might consume more memory than needed when the data on the Join build side is very large and contains many small string type columns [#7416](https://github.com/pingcap/tiflash/issues/7416) @[yibin87](https://github.com/yibin87)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that the error message "resolve lock timeout" of BR is misleading when a backup fails, which hides the actual error information [#43236](https://github.com/pingcap/tidb/issues/43236) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC

        - Fix an OOM issue that might occur when there are as many as 50,000 tables [#7872](https://github.com/pingcap/tiflow/issues/7872) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that TiCDC gets stuck when an OOM occurs in upstream TiDB [#8561](https://github.com/pingcap/tiflow/issues/8561) @[overvenus](https://github.com/overvenus)
        - Fix the issue that TiCDC gets stuck when PD fails such as network isolation or PD Owner node reboot [#8808](https://github.com/pingcap/tiflow/issues/8808) [#8812](https://github.com/pingcap/tiflow/issues/8812) [#8877](https://github.com/pingcap/tiflow/issues/8877) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue of TiCDC time zone setting [#8798](https://github.com/pingcap/tiflow/issues/8798) @[hi-rustin](https://github.com/Rustin170506)
        - Fix the issue that checkpoint lag increases when one of the upstream TiKV nodes crashes [#8858](https://github.com/pingcap/tiflow/issues/8858) @[hicqu](https://github.com/hicqu)
        - Fix the issue that when replicating data to downstream MySQL, a replication error occurs after the `FLASHBACK CLUSTER TO TIMESTAMP` statement is executed in the upstream TiDB [#8040](https://github.com/pingcap/tiflow/issues/8040) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that when replicating data to object storage, the `EXCHANGE PARTITION` operation in the upstream cannot be properly replicated to the downstream [#8914](https://github.com/pingcap/tiflow/issues/8914) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the OOM issue caused by excessive memory usage of the sorter component in some special scenarios [#8974](https://github.com/pingcap/tiflow/issues/8974) @[hicqu](https://github.com/hicqu)
        - Fix the issue that when the downstream is Kafka, TiCDC queries the downstream metadata too frequently and causes excessive workload in the downstream [#8957](https://github.com/pingcap/tiflow/issues/8957) [#8959](https://github.com/pingcap/tiflow/issues/8959) @[hi-rustin](https://github.com/Rustin170506)
        - Fix the issue that when a replication error occurs due to an oversized Kafka message, the message body is recorded in the log [#9031](https://github.com/pingcap/tiflow/issues/9031) @[darraes](https://github.com/darraes)
        - Fix the TiCDC node panic that occurs when the downstream Kafka sinks are rolling restarted [#9023](https://github.com/pingcap/tiflow/issues/9023) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that when replicating data to storage services, the JSON file corresponding to downstream DDL statements does not record the default values of table fields [#9066](https://github.com/pingcap/tiflow/issues/9066) @[CharlesCheung96](https://github.com/CharlesCheung96)

    + TiDB Lightning

        - Fix the issue that OOM might occur when importing a wide table [#43728](https://github.com/pingcap/tidb/issues/43728) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue of `write to tikv with no leader returned` when importing a large amount of data [#43055](https://github.com/pingcap/tidb/issues/43055) @[lance6716](https://github.com/lance6716)
        - Fix a possible OOM problem when there is an unclosed delimiter in the data file [#40400](https://github.com/pingcap/tidb/issues/40400) @[buchuitoudegou](https://github.com/buchuitoudegou)
        - Add a retry mechanism when encountering an `unknown RPC` error during data import [#43291](https://github.com/pingcap/tidb/issues/43291) @[D3Hunter](https://github.com/D3Hunter)

    + TiDB Binlog

        - Fix the issue that TiDB Binlog reports an error when encountering a `CANCELED` DDL statement [#1228](https://github.com/pingcap/tidb-binlog/issues/1228) @[okJiang](https://github.com/okJiang)
