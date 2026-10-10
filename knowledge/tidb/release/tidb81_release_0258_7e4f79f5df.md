# Improvements across TiDB, TiKV, PD, TiFlash, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.3.0.md`
- Source Title: `TiDB 5.3 Release Notes`
- Source Heading Path: `TiDB 5.3 Release Notes > Improvements`
- Source Line Ranges: `259-316`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `ticdc`, `dashboard`, `sql`, `br`
- Topic Tags: `improvements`, `statistics`, `analyze`, `disk-space-protection`, `flow-control`, `logging`, `scheduler`, `dashboard`, `mpp`, `functions-pushdown`, `simd`, `kafka`, `memory-usage`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0258_7e4f79f5df`
- Source ID: `tidb-docs-8.1:releases/release-5.3.0.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `97ebf97749a72c129d32e580fcb15074c3cce59b543557eda58cbe25f7599636`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.3.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.3 improvements across TiDB, TiKV, PD, TiFlash, TiCDC, Dashboard, SQL, or BR such as ANALYZE enhancements, disk space protection, scheduler changes, MPP function pushdown, Kafka sink defaults, or monitoring optimizations.
- Retrieval Keywords: TiDB 5.3 Improvements, ANALYZE TABLE table_name COLUMNS col_1, col_2, ... , col_n, tidb_analyze_version 2, coprocessor encounters a lock debug log affected SQL statements, size of the backup and restore data SQL logical layer, TiKV disk space protection, disk fully-written error, disk full error, list of disk full nodes, Drop/Truncate Table, scale out the nodes, L0 flow control, raft client module error log report, logging threads performance bottleneck, write queries statistics types, Raftstore thread pool, PD hotspot scheduler QPS dimensions, Balance Region scheduler retry limit, TiDB Dashboard v2021.10.08.1, evict leader scheduler unhealthy peers, TiFlash TableScan operator, Exchange operator, MPP engine pushdown, LIKE pattern, FORMAT(), LOWER(), LTRIM(), RTRIM(), SUBSTRING_INDEX(), TRIM(), UCASE(), UPPER(), ROUND (decimal, int), HOUR(), MICROSECOND(), MINUTE(), SECOND(), SYSDATE(), CAST(time, real), GROUP_CONCAT(), SUM(enum), 512-bit SIMD, dashboard memory or CPU information non-Linux systems, logger.count, logger.size, TiCDC MaxMessageBytes, Kafka Broker, replication pipeline memory usage, monitoring items and alert rules, historical error messages
- Follow-up Guidance: The source also notes that when the TiKV remaining space threshold is triggered, some write operations fail with a disk full error and a list of disk full nodes, and space can be recovered by executing `Drop/Truncate Table` or scaling out the nodes.
- Classification Note: This chunk is classified as a self-managed release-note summary because it lists TiDB 5.3 improvements across multiple components and operational areas without introducing a single feature procedure.

## Official Source Content

## Improvements

+ TiDB

    - Show the affected SQL statements in the debug log when the coprocessor encounters a lock, which is helpful in diagnosing problems [#27718](https://github.com/pingcap/tidb/issues/27718)
    - Support showing the size of the backup and restore data when backing up and restoring data in the SQL logical layer [#27247](https://github.com/pingcap/tidb/issues/27247)
    - Improve the default collection logic of ANALYZE when `tidb_analyze_version` is `2`, which accelerates collection and reduces resource overhead
    - Introduce the `ANALYZE TABLE table_name COLUMNS col_1, col_2, ... , col_n` syntax. The syntax allows collecting statistics only on a portion of the columns in wide tables, which improves the speed of statistics collection

+ TiKV

    - Enhance disk space protection to improve storage stability

        To solve the issue that TiKV might panic in case of a disk fully-written error, TiKV introduces a two-level threshold defense mechanism to protect the disk remaining space from being exhausted by excess traffic. Additionally, the mechanism provides the ability to reclaim space when the threshold is triggered. When the remaining space threshold is triggered, some write operations will fail and TiKV will return a disk full error as well as a list of disk full nodes. In this case, to recover the space and restore the service, you can execute `Drop/Truncate Table` or scale out the nodes.

    - Simplify the algorithm of L0 flow control [#10879](https://github.com/tikv/tikv/issues/10879)
    - Improve the error log report in the raft client module [#10944](https://github.com/tikv/tikv/pull/10944)
    - Improve logging threads to avoid them becoming a performance bottleneck [#10841](https://github.com/tikv/tikv/issues/10841)
    - Add more statistics types of write queries [#10507](https://github.com/tikv/tikv/issues/10507)
    - Reduce the write latency by separating I/O operations from Raftstore thread pool (disabled by default). For more information about tuning, see [Tune TiKV Thread Pool Performance](https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance) [#10540](https://github.com/tikv/tikv/issues/10540)

+ PD

    - Add more types of write queries to QPS dimensions in the hotspot scheduler [#3869](https://github.com/tikv/pd/issues/3869)
    - Support dynamically adjusting the retry limit of the Balance Region scheduler to improve the performance of the scheduler [#3744](https://github.com/tikv/pd/issues/3744)
    - Update TiDB Dashboard to v2021.10.08.1 [#4070](https://github.com/tikv/pd/pull/4070)
    - Support that the evict leader scheduler can schedule Regions with unhealthy peers [#4093](https://github.com/tikv/pd/issues/4093)
    - Speed up the exit process of schedulers [#4146](https://github.com/tikv/pd/issues/4146)

+ TiFlash

    - Improve the execution efficiency of the TableScan operator greatly
    - Improve the execution efficiency of the Exchange operator
    - Reduce write amplification and memory usage during GC of the storage engine (experimental feature)
    - Improve the stability and availability of TiFlash when TiFlash restarts, which reduces possible query failures following the restart
    - Support pushing down multiple new String and Time functions to the MPP engine

        - String functions: LIKE pattern, FORMAT(), LOWER(), LTRIM(), RTRIM(), SUBSTRING_INDEX(), TRIM(), UCASE(), UPPER()
        - Mathematical functions: ROUND (decimal, int)
        - Date and time functions: HOUR(), MICROSECOND(), MINUTE(), SECOND(), SYSDATE()
        - Type conversion function: CAST(time, real)
        - Aggregation functions: GROUP_CONCAT(), SUM(enum)

    - Support 512-bit SIMD
    - Enhance the cleanup algorithm for outdated data to reduce disk usage and read files more efficiently
    - Fix the issue that dashboard does not display memory or CPU information in some non-Linux systems
    - Unify the naming style of TiFlash log files (keep the naming style consistent with that of TiKV) and support dynamic modification of logger.count and logger.size
    - Improve the data validation capability of column-based files (checksums, experimental feature)

+ Tools

    + TiCDC

        - Reduce the default value of the Kafka sink configuration item `MaxMessageBytes` from 64 MB to 1 MB to fix the issue that large messages are rejected by the Kafka Broker [#3104](https://github.com/pingcap/tiflow/pull/3104)
        - Reduce memory usage in the replication pipeline [#2553](https://github.com/pingcap/tiflow/issues/2553) [#3037](https://github.com/pingcap/tiflow/pull/3037) [#2726](https://github.com/pingcap/tiflow/pull/2726)
        - Optimize monitoring items and alert rules to improve observability of synchronous links, memory GC, and stock data scanning processes [#2735](https://github.com/pingcap/tiflow/pull/2735) [#1606](https://github.com/pingcap/tiflow/issues/1606) [#3000](https://github.com/pingcap/tiflow/pull/3000) [#2985](https://github.com/pingcap/tiflow/issues/2985) [#2156](https://github.com/pingcap/tiflow/issues/2156)
        - When the sync task status is normal, no more historical error messages are displayed to avoid misleading users [#2242](https://github.com/pingcap/tiflow/issues/2242)
