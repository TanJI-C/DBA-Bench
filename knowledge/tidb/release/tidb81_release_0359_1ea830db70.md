# 6.4.0 improvements across TiDB, TiKV, PD, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.4.0.md`
- Source Title: `TiDB 6.4.0 Release Notes`
- Source Heading Path: `TiDB 6.4.0 Release Notes > Improvements`
- Source Line Ranges: `333-389`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `dashboard`, `br`, `ticdc`, `dm`, `lightning`
- Topic Tags: `improvements`, `sql`, `transactions`, `configuration`, `raftstore`, `scheduler`, `mpp`, `memory-usage`, `dashboard`, `pitr`, `replication`, `data-migration`, `import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0359_1ea830db70`
- Source ID: `tidb-docs-8.1:releases/release-6.4.0.md#improvements`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f719b3dcbd24529b5df6c3a31a71c21b239306c44cef21c65b1cc2a659d038ba`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.4.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 6.4.0 release improvements across TiDB, TiKV, PD, TiFlash, and related tools, including specific new configuration items, SQL capabilities, scheduler changes, MPP stability, memory usage, PITR, replication, DM, and Lightning updates.
- Retrieval Keywords: TiDB 6.4.0 Improvements, release-6.4.0 improvements, lc_messages, AUTO_RANDOM clustered composite index, pessimistic transactions internal transaction retry, apply-yield-write-size, Raftstore congestion, entry cache leader transfer QPS jitter, json_constrains Coprocessor, CausalTsProvider asynchronous function, hot Region scheduler v2 GA, external timestamp not provided by PD, TiFlash MPP error handling, TiFlash Join performance memory usage, TiDB Dashboard TiFlash metrics, BR PITR metadata memory usage, TiCDC exchange partition DDL, tidb_enable_external_ts_read, Syncpoint, DM operate-source update, DM full import incompatible DDL, TiDB Lightning schema file scan
- Follow-up Guidance: The source further breaks down the improvements by component: TiDB, TiKV, PD, TiFlash, TiDB Dashboard, BR, TiCDC, DM, and TiDB Lightning.
- Classification Note: This chunk is classified as a release note because it lists official 6.4.0 improvements by component and names the exact features, variables, commands, and operational areas updated in this release.

## Official Source Content

## Improvements

+ TiDB

    - Allow modifying the noop variable `lc_messages` [#38231](https://github.com/pingcap/tidb/issues/38231) @[djshow832](https://github.com/djshow832)
    - Support the `AUTO_RANDOM` column as the first column of the clustered composite index [#38572](https://github.com/pingcap/tidb/issues/38572) @[tangenta](https://github.com/tangenta)
    - Use pessimistic transactions in internal transaction retry to avoid retry failure and reduce time consumption [#38136](https://github.com/pingcap/tidb/issues/38136) @[jackysp](https://github.com/jackysp)

+ TiKV

    - Add a new configuration item `apply-yield-write-size` to control the maximum number of bytes that the Apply thread can write for one Finite-state Machine in one round of poll, and relieve Raftstore congestion when the Apply thread writes a large volume of data [#13313](https://github.com/tikv/tikv/issues/13313) @[glorv](https://github.com/glorv)
    - Warm up the entry cache before migrating the leader of Region to avoid QPS jitter during the leader transfer process [#13060](https://github.com/tikv/tikv/issues/13060) @[cosven](https://github.com/cosven)
    - Support pushing down the `json_constrains` operator to Coprocessor [#13592](https://github.com/tikv/tikv/issues/13592) @[lizhenhuan](https://github.com/lizhenhuan)
    - Add the asynchronous function for `CausalTsProvider` to improve the flush performance in some scenarios [#13428](https://github.com/tikv/tikv/issues/13428) @[zeminzhou](https://github.com/zeminzhou)

+ PD

    - The v2 algorithm of the hot Region scheduler becomes GA. In some scenarios, the v2 algorithm can achieve better balancing in both configured dimensions and reduce invalid scheduling [#5021](https://github.com/tikv/pd/issues/5021) @[HundunDM](https://github.com/hundundm)
    - Optimize the timeout mechanism of operator step to avoid premature timeout [#5596](https://github.com/tikv/pd/issues/5596) @[bufferflies](https://github.com/bufferflies)
    - Improve the performance of the scheduler in large clusters [#5473](https://github.com/tikv/pd/issues/5473) @[bufferflies](https://github.com/bufferflies)
    - Support using external timestamp which is not provided by PD [#5637](https://github.com/tikv/pd/issues/5637) @[lhy1024](https://github.com/lhy1024)

+ TiFlash

    - Refactor the TiFlash MPP error handling logic to further improve the stability of MPP [#5095](https://github.com/pingcap/tiflash/issues/5095) @[windtalker](https://github.com/windtalker)
    - Optimize the sorting of the TiFlash computation process, and optimize the key handling for Join and Aggregation [#5294](https://github.com/pingcap/tiflash/issues/5294) @[solotzg](https://github.com/solotzg)
    - Optimize the memory usage for decoding and remove redundant transfer columns to improve Join performance [#6157](https://github.com/pingcap/tiflash/issues/6157) @[yibin87](https://github.com/yibin87)

+ Tools

    + TiDB Dashboard

        - Support displaying TiFlash metrics on the Monitoring page and optimize the presentation of metrics on that page [#1440](https://github.com/pingcap/tidb-dashboard/issues/1440) @[YiniXu9506](https://github.com/YiniXu9506)
        - Show the number of rows for results in the Slow Query list and SQL Statement list [#1443](https://github.com/pingcap/tidb-dashboard/issues/1443) @[baurine](https://github.com/baurine)
        - Optimize the Dashboard to not report the Alertmanager errors when Alertmanager does not exist [#1444](https://github.com/pingcap/tidb-dashboard/issues/1444) @[baurine](https://github.com/baurine)

    + Backup & Restore (BR)

        - Improve the mechanism for loading the metadata. The metadata is loaded into memory only when necessary, which significantly reduces the memory usage during PITR [#38404](https://github.com/pingcap/tidb/issues/38404) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC

        - Support replicating the exchange partition DDL statements [#639](https://github.com/pingcap/tiflow/issues/639) @[asddongmen](https://github.com/asddongmen)
        - Improve non-batch sending performance for the MQ sink module [#7353](https://github.com/pingcap/tiflow/issues/7353) @[hi-rustin](https://github.com/Rustin170506)
        - Improve performance of TiCDC puller when a table has a large number of Regions [#7078](https://github.com/pingcap/tiflow/issues/7078) [#7281](https://github.com/pingcap/tiflow/issues/7281) @[sdojjy](https://github.com/sdojjy)
        - Support reading historical data in the downstream TiDB by using the `tidb_enable_external_ts_read` variable when Syncpoint is enabled [#7419](https://github.com/pingcap/tiflow/issues/7419) @[asddongmen](https://github.com/asddongmen)
        - Enable transaction split and disable safeMode by default to improve the replication stability [#7505](https://github.com/pingcap/tiflow/issues/7505) @[asddongmen](https://github.com/asddongmen)

    + TiDB Data Migration (DM)

        - Remove the useless `operate-source update` command from dmctl [#7246](https://github.com/pingcap/tiflow/issues/7246) @[buchuitoudegou](https://github.com/buchuitoudegou)
        - Fix the issue that DM full import fails if the upstream database uses DDL statements that are incompatible with TiDB. You can create the schema of target tables in TiDB manually in advance using DDL statements supported by TiDB to ensure successful import  [#37984](https://github.com/pingcap/tidb/issues/37984) @[lance6716](https://github.com/lance6716)

    + TiDB Lightning

        - Optimize the file scanning logic to accelerate the scan of schema files [#38598](https://github.com/pingcap/tidb/issues/38598) @[dsdashun](https://github.com/dsdashun)
