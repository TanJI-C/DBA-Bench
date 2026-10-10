# 6.3.0 improvements across TiDB, TiKV, PD, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.3.0.md`
- Source Title: `TiDB 6.3.0 Release Notes`
- Source Heading Path: `TiDB 6.3.0 Release Notes > Improvements`
- Source Line Ranges: `271-332`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dashboard`, `tiflash`, `br`, `ticdc`, `dm`, `lightning`
- Topic Tags: `release-notes`, `improvements`, `sql`, `mysql-compatibility`, `logging`, `ddl`, `json`, `join-performance`, `plan-replayer`, `raftstore`, `tso`, `rocksdb`, `region-merge`, `regex-functions`, `thread-pool`, `dashboard-metrics`, `function-pushdown`, `memory-tracker`, `collation-performance`, `read-limiter`, `pitr`, `log-backup`, `tiflash-replica`, `changefeed`, `mysql-sink`, `health-api`, `sink-throughput`, `deprecated-features`, `data-migration`, `s3-external-storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0343_af519f2c0f`
- Source ID: `tidb-docs-8.1:releases/release-6.3.0.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8f433651b5420c4a48e838ee1d33c6304031d61a748104b41e1782c9d34e3fa9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.3.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 6.3.0 release-note improvements across TiDB, TiKV, PD, TiFlash, BR, TiCDC, DM, and TiDB Lightning, including exact feature names, parameters, APIs, and deprecated items.
- Retrieval Keywords: TiDB 6.3.0 Improvements, release notes improvements, init_connect parsing check, start_job_id parameter, DDL history jobs HTTP API, JSON path wrong syntax, PLAN REPLAYER multiple SQL statements, unreachable_backoff, rocksdb.max-sub-compactions, TSO service fault tolerance, empty Regions merge, regular expression functions, thread pool size based on CPU usage, TiDB Dashboard monitoring URL, metrics to monitoring, TiKV IO MBps metric, TiFlash elt pushdown, leftShift pushdown, castTimeAsDuration pushdown, HexIntArg HexStrArg pushdown, new interpreter Planner, memory tracker, UTF8_BIN ASCII_BIN LATIN1_BIN UTF8MB4_BIN, ReadLimiter, PITR merge small files, TiFlash replicas based on upstream cluster configuration, MySQL sink start ts, api/v1/health, asynchronous mode sink throughput, deprecated pulsar sink, discarding DDL statements irrelevant to a changefeed, MySQL 8.0 as data source, invalid connection, S3 external storage URL assuming a given role
- Follow-up Guidance: The source also lists component-specific improvements such as TiDB case-insensitive target table existence checks, TiCDC asynchronous MQ and MySQL sinks, and TiDB Lightning S3 external storage URL query parameters.
- Classification Note: This chunk is classified as a self-managed release-notes improvements summary because the official content enumerates product improvements introduced in TiDB 6.3.0 across multiple components and tools.

## Official Source Content

## Improvements

+ TiDB

    - TiDB is now case-insensitive to the target table name when checking the table existence [#34610](https://github.com/pingcap/tidb/issues/34610) @[tiancaiamao](https://github.com/tiancaiamao)
    - Improve MySQL compatibility by adding a parsing check when setting the value of `init_connect` [#35324](https://github.com/pingcap/tidb/issues/35324) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Improve the log warning generated for new connections [#34964](https://github.com/pingcap/tidb/issues/34964) @[xiongjiwei](https://github.com/xiongjiwei)
    - Optimize the HTTP API for querying DDL history jobs, and add support for the `start_job_id` parameter [#35838](https://github.com/pingcap/tidb/issues/35838) @[tiancaiamao](https://github.com/tiancaiamao)
    - Report errors when the JSON path has wrong syntax [#22525](https://github.com/pingcap/tidb/issues/22525) [#34959](https://github.com/pingcap/tidb/issues/34959) @[xiongjiwei](https://github.com/xiongjiwei)
    - Improve the performance of Join operations by fixing a false sharing issue [#37641](https://github.com/pingcap/tidb/issues/37641) @[gengliqi](https://github.com/gengliqi)
    - Support exporting the execution plan information of multiple SQL statements at a time using [`PLAN REPLAYER`](https://docs.pingcap.com/tidb/stable/sql-plan-replayer), which makes troubleshooting more efficient [#37798](https://github.com/pingcap/tidb/issues/37798) @[Yisaer](https://github.com/Yisaer)

+ TiKV

    - Support configuring the `unreachable_backoff` item to avoid Raftstore broadcasting too many messages after one peer becomes unreachable [#13054](https://github.com/tikv/tikv/issues/13054) @[5kbpers](https://github.com/5kbpers)
    - Improve the fault tolerance of TSO service [#12794](https://github.com/tikv/tikv/issues/12794) @[pingyu](https://github.com/pingyu)
    - Support dynamically modifying the number of sub-compaction operations performed concurrently in RocksDB (`rocksdb.max-sub-compactions`) [#13145](https://github.com/tikv/tikv/issues/13145) @[ethercflow](https://github.com/ethercflow)
    - Optimize the performance of merging empty Regions [#12421](https://github.com/tikv/tikv/issues/12421) @[tabokie](https://github.com/tabokie)
    - Support more regular expression functions [#13483](https://github.com/tikv/tikv/issues/13483) @[gengliqi](https://github.com/gengliqi)
    - Support automatically adjusting the thread pool size based on the CPU usage [#13313](https://github.com/tikv/tikv/issues/13313) @[glorv](https://github.com/glorv)

+ PD

    - Improve the query of the TiKV IO MBps metric in TiDB Dashboard [#5366](https://github.com/tikv/pd/issues/5366) @[YiniXu9506](https://github.com/YiniXu9506)
    - Modify the URL in TiDB Dashboard from `metrics` to `monitoring` [#5366](https://github.com/tikv/pd/issues/5366) @[YiniXu9506](https://github.com/YiniXu9506)

+ TiFlash

    - Support pushing down the `elt` function to TiFlash [#5104](https://github.com/pingcap/tiflash/issues/5104) @[Willendless](https://github.com/Willendless)
    - Support pushing down the `leftShift` function to TiFlash [#5099](https://github.com/pingcap/tiflash/issues/5099) @[AnnieoftheStars](https://github.com/AnnieoftheStars)
    - Support pushing down the `castTimeAsDuration` function to TiFlash [#5306](https://github.com/pingcap/tiflash/issues/5306) @[AntiTopQuark](https://github.com/AntiTopQuark)
    - Support pushing down the `HexIntArg/HexStrArg` function to TiFlash [#5107](https://github.com/pingcap/tiflash/issues/5107) @[YangKeao](https://github.com/YangKeao)
    - Refactor TiFlash's interpreter, and support the new interpreter Planner [#4739](https://github.com/pingcap/tiflash/issues/4739) @[SeaRise](https://github.com/SeaRise)
    - Improve the accuracy of memory tracker in TiFlash [#5609](https://github.com/pingcap/tiflash/issues/5609) @[bestwoody](https://github.com/bestwoody)
    - Improve the performance of string columns with the `UTF8_BIN/ASCII_BIN/LATIN1_BIN/UTF8MB4_BIN` collations [#5294](https://github.com/pingcap/tiflash/issues/5294) @[solotzg](https://github.com/solotzg)
    - Calculate the I/O throughput in background in ReadLimiter [#5401](https://github.com/pingcap/tiflash/issues/5401), [#5091](https://github.com/pingcap/tiflash/issues/5091) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)

+ Tools

    + Backup & Restore (BR)

        - PITR can merge small files generated in log backup, which greatly reduces the number of backup files [#13232](https://github.com/tikv/tikv/issues/13232) @[Leavrth](https://github.com/Leavrth)
        - PITR supports automatically configuring the number of TiFlash replicas based on the upstream cluster configuration after the restoration [#37208](https://github.com/pingcap/tidb/issues/37208) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC

        - Improve TiCDC's compatibility with the concurrent DDL framework introduced in the upstream TiDB [#6506](https://github.com/pingcap/tiflow/issues/6506) @[lance6716](https://github.com/lance6716)
        - Support logging `start ts` of DML statements when MySQL sink gets an error [#6460](https://github.com/pingcap/tiflow/issues/6460) @[overvenus](https://github.com/overvenus)
        - Enhance the `api/v1/health` API to return a more accurate health state of a TiCDC cluster [#4757](https://github.com/pingcap/tiflow/issues/4757) @[overvenus](https://github.com/overvenus)
        - Implement MQ sink and MySQL sink in the asynchronous mode to improve the sink throughput [#5928](https://github.com/pingcap/tiflow/issues/5928) @[hicqu](https://github.com/hicqu) @[hi-rustin](https://github.com/Rustin170506)
        - Delete the deprecated pulsar sink [#7087](https://github.com/pingcap/tiflow/issues/7087) @[hi-rustin](https://github.com/Rustin170506)
        - Improve replication performance by discarding DDL statements that are irrelevant to a changefeed [#6447](https://github.com/pingcap/tiflow/issues/6447) @[asddongmen](https://github.com/asddongmen)

    + TiDB Data Migration (DM)

        - Improve compatibility with MySQL 8.0 as data source [#6448](https://github.com/pingcap/tiflow/issues/6448) @[lance6716](https://github.com/lance6716)
        - Optimize DDL by executing DDL asynchronously when encounter "invalid connection" [#4689](https://github.com/pingcap/tiflow/issues/4689) @[lyzx2001](https://github.com/lyzx2001)

    + TiDB Lightning

        - Add query parameters for S3 external storage URL to support accessing the S3 data in another account by assuming a given role [#36891](https://github.com/pingcap/tidb/issues/36891) @[dsdashun](https://github.com/dsdashun)
