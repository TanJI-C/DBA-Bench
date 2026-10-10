# Improvements across TiDB ecosystem in v6.5.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.0.md`
- Source Title: `TiDB 6.5.0 Release Notes`
- Source Heading Path: `TiDB 6.5.0 Release Notes > Improvements`
- Source Line Ranges: `376-436`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `dashboard`, `br`, `ticdc`, `dm`
- Topic Tags: `improvements`, `performance`, `stability`, `observability`, `backup`, `restore`, `replication`, `scheduling`, `memory-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0370_6cc5c51e9b`
- Source ID: `tidb-docs-8.1:releases/release-6.5.0.md#improvements`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f6a4df4bb31a292fe3f3ea6e4a62b56e79c9e5c2ce4b2066298d4fd52ebfb501`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB 6.5.0 improvements across TiDB, TiKV, PD, TiFlash, BR, TiCDC, Dashboard, and DM, especially performance, stability, observability, backup, replication, and memory-usage improvements.
- Retrieval Keywords: TiDB 6.5.0 improvements, INFORMATION_SCHEMA.COLUMNS BIT CHAR MySQL consistency, TiFlash MPP probing mechanism abnormal nodes, Raft Engine insufficient space, json_valid pushdown to TiKV, backup multiple ranges single backup request, ap-southeast-3 AWS backup, reduce pessimistic transaction conflicts, recovery performance caching external storage objects, CheckLeader dedicated thread TiCDC replication latency, pull model for Checkpoints, crossbeam-channel spinning issues sender side, batch Coprocessor tasks processing, wake up Regions failure recovery, reduce requested size of memory usage, Raft extension code extensibility, tikv-ctl query Regions in key range, locked continuously read and write performance, PD lock contention heartbeats high concurrency, scheduler performance large-scale clusters, speed of loading Regions, optimized handling of Region heartbeats, garbage collecting tombstone stores, TiFlash TableFullScan explain analyze details, Dashboard slow query Is Prepared, Is Plan from Cache, Is Plan from Binding, BR memory usage cleaning backup log data, restoration failure PD leader switch, OpenSSL protocol log backup, TiCDC Kafka protocol encoder performance, DM block list not parsing data, DM relay asynchronous write batch write, DM precheck error messages, SHOW SLAVE HOSTS old MySQL versions
- Follow-up Guidance: 
- Classification Note: This is an improvements chunk because it enumerates release-note enhancements across multiple TiDB ecosystem components without introducing compatibility-change or deprecation sections.

## Official Source Content

## Improvements

+ TiDB

    - For `BIT` and `CHAR` columns, make the result of `INFORMATION_SCHEMA.COLUMNS` consistent with MySQL [#25472](https://github.com/pingcap/tidb/issues/25472) @[hawkingrei](https://github.com/hawkingrei)
    - Optimize the TiDB probing mechanism for TiFlash nodes in the TiFlash MPP mode to mitigate the performance impact when nodes are abnormal [#39686](https://github.com/pingcap/tidb/issues/39686) @[hackersean](https://github.com/hackersean)

+ TiKV

    - Stop writing to Raft Engine when there is insufficient space to avoid exhausting disk space [#13642](https://github.com/tikv/tikv/issues/13642) @[jiayang-zheng](https://github.com/jiayang-zheng)
    - Support pushing down the `json_valid` function to TiKV [#13571](https://github.com/tikv/tikv/issues/13571) @[lizhenhuan](https://github.com/lizhenhuan)
    - Support backing up multiple ranges of data in a single backup request [#13701](https://github.com/tikv/tikv/issues/13701) @[Leavrth](https://github.com/Leavrth)
    - Support backing up data to the Asia Pacific region (ap-southeast-3) of AWS by updating the rusoto library [#13751](https://github.com/tikv/tikv/issues/13751) @[3pointer](https://github.com/3pointer)
    - Reduce pessimistic transaction conflicts [#13298](https://github.com/tikv/tikv/issues/13298) @[MyonKeminta](https://github.com/MyonKeminta)
    - Improve recovery performance by caching external storage objects [#13798](https://github.com/tikv/tikv/issues/13798) @[YuJuncen](https://github.com/YuJuncen)
    - Run the CheckLeader in a dedicated thread to reduce TiCDC replication latency [#13774](https://github.com/tikv/tikv/issues/13774) @[overvenus](https://github.com/overvenus)
    - Support pull model for Checkpoints [#13824](https://github.com/tikv/tikv/issues/13824) @[YuJuncen](https://github.com/YuJuncen)
    - Avoid spinning issues on the sender side by updating crossbeam-channel [#13815](https://github.com/tikv/tikv/issues/13815) @[sticnarf](https://github.com/sticnarf)
    - Support batch Coprocessor tasks processing in TiKV [#13849](https://github.com/tikv/tikv/issues/13849) @[cfzjywxk](https://github.com/cfzjywxk)
    - Reduce waiting time on failure recovery by notifying TiKV to wake up Regions [#13648](https://github.com/tikv/tikv/issues/13648) @[LykxSassinator](https://github.com/LykxSassinator)
    - Reduce the requested size of memory usage by code optimization [#13827](https://github.com/tikv/tikv/issues/13827) @[BusyJay](https://github.com/BusyJay)
    - Introduce the Raft extension to improve code extensibility [#13827](https://github.com/tikv/tikv/issues/13827) @[BusyJay](https://github.com/BusyJay)
    - Support using tikv-ctl to query which Regions are included in a certain key range [#13760](https://github.com/tikv/tikv/issues/13760) @[HuSharp](https://github.com/HuSharp)
    - Improve read and write performance for rows that are not updated but locked continuously [#13694](https://github.com/tikv/tikv/issues/13694) @[sticnarf](https://github.com/sticnarf)

+ PD

    - Optimize the granularity of locks to reduce lock contention and improve the handling capability of heartbeats under high concurrency [#5586](https://github.com/tikv/pd/issues/5586) @[rleungx](https://github.com/rleungx)
    - Optimize scheduler performance for large-scale clusters and accelerate the production of scheduling policies [#5473](https://github.com/tikv/pd/issues/5473) @[bufferflies](https://github.com/bufferflies)
    - Improve the speed of loading Regions [#5606](https://github.com/tikv/pd/issues/5606) @[rleungx](https://github.com/rleungx)
    - Reduce unnecessary overhead by optimized handling of Region heartbeats [#5648](https://github.com/tikv/pd/issues/5648) @[rleungx](https://github.com/rleungx)
    - Add the feature of automatically garbage collecting tombstone stores [#5348](https://github.com/tikv/pd/issues/5348) @[nolouch](https://github.com/nolouch)

+ TiFlash

    - Improve write performance in scenarios where there is no batch processing on the SQL side [#6404](https://github.com/pingcap/tiflash/issues/6404) @[lidezhu](https://github.com/lidezhu)
    - Add more details for TableFullScan in the `explain analyze` output [#5926](https://github.com/pingcap/tiflash/issues/5926) @[hongyunyan](https://github.com/hongyunyan)

+ Tools

    + TiDB Dashboard

        - Add three new fields to the slow query page: "Is Prepared?", "Is Plan from Cache?", "Is Plan from Binding?" [#1451](https://github.com/pingcap/tidb-dashboard/issues/1451) @[shhdgit](https://github.com/shhdgit)

    + Backup & Restore (BR)

        - Optimize BR memory usage during the process of cleaning backup log data [#38869](https://github.com/pingcap/tidb/issues/38869) @[Leavrth](https://github.com/Leavrth)
        - Fix the restoration failure issue caused by PD leader switch during the restoration process [#36910](https://github.com/pingcap/tidb/issues/36910) @[MoCuishle28](https://github.com/MoCuishle28)
        - Improve TLS compatibility by using the OpenSSL protocol in log backup [#13867](https://github.com/tikv/tikv/issues/13867) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC

        - Improve the performance of Kafka protocol encoder [#7540](https://github.com/pingcap/tiflow/issues/7540) [#7532](https://github.com/pingcap/tiflow/issues/7532) [#7543](https://github.com/pingcap/tiflow/issues/7543) @[3AceShowHand](https://github.com/3AceShowHand) @[sdojjy](https://github.com/sdojjy)

    + TiDB Data Migration (DM)

        - Improve the data replication performance for DM by not parsing the data of tables in the block list [#7622](https://github.com/pingcap/tiflow/pull/7622) @[GMHDBJD](https://github.com/GMHDBJD)
        - Improve the write efficiency of DM relay by using asynchronous write and batch write [#7580](https://github.com/pingcap/tiflow/pull/7580) @[GMHDBJD](https://github.com/GMHDBJD)
        - Optimize the error messages in DM precheck [#7621](https://github.com/pingcap/tiflow/issues/7621) @[buchuitoudegou](https://github.com/buchuitoudegou)
        - Improve the compatibility of `SHOW SLAVE HOSTS` for old MySQL versions [#5017](https://github.com/pingcap/tiflow/issues/5017) @[lyzx2001](https://github.com/lyzx2001)
