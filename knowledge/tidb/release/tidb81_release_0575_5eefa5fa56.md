# Performance features in TiDB 8.0.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes > Feature details > Performance`
- Source Line Ranges: `83-143`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `br`, `pd`, `tiflash`, `tikv`, `sql`
- Topic Tags: `performance`, `restore`, `snapshot`, `pushdown`, `hashagg`, `disk-spill`, `statistics`, `plan-cache`, `multi-valued-indexes`, `tso`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0575_5eefa5fa56`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4bbccf26868e2e63d0c4d4354a50bc062fc4cd1583728d6103bd8059e6f1d299`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 8.0.0 performance release details about BR snapshot restore speed, TiFlash function pushdown, parallel HashAgg disk spill, automatic statistics collection priority queue, plan cache limitations removed, multi-valued index optimizer support, or low-precision TSO update interval.
- Retrieval Keywords: TiDB 8.0.0 Performance, BR snapshot restore speed GA, snapshot restore enabled by default, coarse-grained Region scattering algorithm, finer-grained Region scattering algorithm, 1.2 GiB/s, 100 TiB within one hour, TiFlash pushdown CAST(DECIMAL AS DOUBLE), TiFlash pushdown POWER(), parallel HashAgg disk spill experimental, tidb_enable_parallel_hashagg_spill, automatic statistics collection priority queue, tidb_enable_auto_analyze_priority_queue, plan cache partitioned tables, plan cache generated columns, multi-valued indexes and plan cache, optimizer multi-valued indexes, OR member of Index Merge, low-precision TSO, tidb_low_resolution_tso_update_interval, tidb_low_resolution_tso
- Follow-up Guidance: The chunk also points to documentation for BR snapshot restore, TiFlash supported pushdown calculations, the `tidb_enable_parallel_hashagg_spill` variable, the `tidb_enable_auto_analyze_priority_queue` variable, prepared plan cache, multi-valued indexes, and the `tidb_low_resolution_tso_update_interval` variable.
- Classification Note: This is classified as a release feature summary because the content lists new TiDB 8.0.0 performance enhancements and related system variables across BR, TiFlash, optimizer, and SQL execution.

## Official Source Content

### Performance

* BR improves snapshot restore speed (GA) [#50701](https://github.com/pingcap/tidb/issues/50701) @[3pointer](https://github.com/3pointer) @[Leavrth](https://github.com/Leavrth)

  Starting from TiDB v8.0.0, the acceleration of snapshot restore speed is now generally available (GA) and enabled by default. BR improves the snapshot restore speed significantly by implementing various optimizations such as adopting the coarse-grained Region scattering algorithm, creating databases and tables in batches, reducing the mutual impact between SST file downloads and ingest operations, and accelerating the restore of table statistics. According to test results from real-world cases, the data restore speed of a single TiKV node stabilizes at 1.2 GiB/s, and 100 TiB of data can be restored within one hour.

  This means that even in high-load environments, BR can fully utilize the resources of each TiKV node, significantly reducing database restore time, enhancing the availability and reliability of databases, and reducing downtime and business losses caused by data loss or system failures. Note that the increase in restore speed is attributed to the parallel execution of a large number of goroutines, which can result in significant memory consumption, especially when there are many tables or Regions. It is recommended to use machines with higher memory capacity to run the BR client. If the memory capacity of the machine is limited, it is recommended to use a finer-grained Region scattering algorithm. In addition, because the coarse-grained Region scattering algorithm might consume a significant amount of external storage bandwidth, you need to avoid any impact on other applications due to insufficient external bandwidth.

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#restore-cluster-snapshots).

* Support pushing down the following functions to TiFlash [#50975](https://github.com/pingcap/tidb/issues/50975) [#50485](https://github.com/pingcap/tidb/issues/50485) @[yibin87](https://github.com/yibin87) @[windtalker](https://github.com/windtalker)

    * `CAST(DECIMAL AS DOUBLE)`
    * `POWER()`

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations).

* The parallel HashAgg algorithm of TiDB supports disk spill (experimental) [#35637](https://github.com/pingcap/tidb/issues/35637) @[xzhangxian1008](https://github.com/xzhangxian1008)

    In earlier versions of TiDB, the concurrency algorithm of the HashAgg operator does not support disk spill. If the execution plan of a SQL statement contains the parallel HashAgg operator, all the data for that SQL statement can only be processed in memory. Consequently, TiDB has to process a large amount of data in memory. When the data size exceeds the memory limit, TiDB can only choose the non-parallel algorithm, which does not leverage concurrency for performance improvement.

     In v8.0.0, the parallel HashAgg algorithm of TiDB supports disk spill. Under any parallel conditions, the HashAgg operator can automatically trigger data spill based on memory usage, thus balancing performance and data throughput. Currently, as an experimental feature, TiDB introduces the `tidb_enable_parallel_hashagg_spill` variable to control whether to enable the parallel HashAgg algorithm that supports disk spill. When this variable is `ON`, it means enabled. This variable will be deprecated after the feature is generally available in a future release.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_parallel_hashagg_spill-new-in-v800).

* Introduce the priority queue for automatic statistics collection [#50132](https://github.com/pingcap/tidb/issues/50132) @[hi-rustin](https://github.com/Rustin170506)

    Maintaining optimizer statistics up-to-date is the key to stabilizing database performance. Most users rely on the [automatic statistics collection](https://docs.pingcap.com/tidb/stable/statistics#automatic-update) provided by TiDB to collect the latest statistics. Automatic statistics collection checks the status of statistics for all objects, and adds unhealthy objects to a queue for sequential collections. In previous versions, the order is random, which could result in excessive waits for more worthy candidates to be updated, causing potential performance regressions.

    Starting from v8.0.0, automatic statistics collection dynamically sets priorities for objects in combination with a variety of conditions to ensure that more deserving candidates are processed in priority, such as newly created indexes and partitioned tables with definition changes. Additionally, TiDB prioritizes tables with lower health scores, placing them at the top of the queue. This enhancement makes the order of collection more reasonable, and reduces performance problems caused by outdated statistics, therefore improving database stability.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_auto_analyze_priority_queue-new-in-v800).

* Remove some limitations on execution plan cache [#49161](https://github.com/pingcap/tidb/pull/49161) @[mjonss](https://github.com/mjonss) @[qw4990](https://github.com/qw4990)

    TiDB supports [plan cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache), which can effectively reduce the latency of OLTP systems and is important for performance. In v8.0.0, TiDB removes several limitations on plan cache. Execution plans with the following items can be cached now:

    - [Partitioned tables](https://docs.pingcap.com/tidb/stable/partitioned-table)
    - [Generated columns](https://docs.pingcap.com/tidb/stable/generated-columns), including objects that depend on generated columns (such as [multi-valued indexes](https://docs.pingcap.com/tidb/stable/choose-index#multi-valued-indexes-and-plan-cache))

  This enhancement extends the use cases of plan cache and improves the overall database performance in complex scenarios.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache).

* Optimizer enhances support for multi-valued indexes [#47759](https://github.com/pingcap/tidb/issues/47759) [#46539](https://github.com/pingcap/tidb/issues/46539) @[Arenatlx](https://github.com/Arenatlx) @[time-and-fate](https://github.com/time-and-fate)

    TiDB v6.6.0 introduces [multi-value indexes](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#multi-valued-indexes) to improve query performance for JSON data types. In v8.0.0, the optimizer enhances its support for multi-valued indexes and can correctly identify and utilize them to optimize queries in complex scenarios.

    * The optimizer collects statistics on multi-valued indexes and decides execution plans with the statistics. If several multi-value indexes can be selected by a SQL statement, the optimizer can identify the one with lower cost.
    * When using `OR` to connect multiple `member of` conditions, the optimizer can match an effective index partial path for each DNF item (a `member of` condition) and combine these paths using Union to form an `Index Merge`. This achieves more efficient condition filtering and data fetch.

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#multi-valued-indexes).

* Support configuring the update interval for low-precision TSO [#51081](https://github.com/pingcap/tidb/issues/51081) @[Tema](https://github.com/Tema)
    The [low-precision TSO feature](https://docs.pingcap.com/tidb/stable/system-variables#tidb_low_resolution_tso) in TiDB uses regularly updated TSO as the transaction timestamp. In scenarios where reading outdated data is acceptable, this feature reduces the overhead of obtaining TSO for small read-only transactions by sacrificing real-time performance and improves the ability of high-concurrency reads.

    Before v8.0.0, the TSO update interval of low-precision TSO feature is fixed and cannot be adjusted according to actual application requirements. In v8.0.0, TiDB introduces the system variable `tidb_low_resolution_tso_update_interval` to control the TSO update interval. This feature takes effect only when the low-precision TSO feature is enabled.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_low_resolution_tso_update_interval-new-in-v800).
