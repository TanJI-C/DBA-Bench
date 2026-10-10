# Performance features and experimental execution improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.0.md`
- Source Title: `TiDB 7.1.0 Release Notes`
- Source Heading Path: `TiDB 7.1.0 Release Notes > Feature details > Performance`
- Source Line Ranges: `85-142`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `lightning`, `br`, `ticdc`, `sql`
- Topic Tags: `performance`, `experimental-features`, `partitioned-raft-kv`, `late-materialization`, `mpp-join`, `replica-read`, `plan-cache`, `distributed-execution`, `ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0443_13f9a0ff4f`
- Source ID: `tidb-docs-8.1:releases/release-7.1.0.md#performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1c5f4fd11e424be77689e79345e30c785ba2ed71f556164a1b6739e2ac16b178`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.0#performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 7.1.0 performance release notes about experimental and GA execution features, storage engine changes, replica read behavior, plan cache updates, or DDL distributed execution.
- Retrieval Keywords: TiDB 7.1.0 Performance, Partitioned Raft KV storage engine, experimental, TiDB Lightning, BR, TiCDC, late materialization, tidb_opt_enable_late_materialization, MPP Join algorithm, tidb_prefer_broadcast_join_by_exchange_data_size, tidb_broadcast_join_threshold_count, tidb_broadcast_join_threshold_size, load-based replica read, tidb_load_based_replica_read_threshold, non-prepared plan cache, tidb_session_plan_cache_size, tidb_prepared_plan_cache_size, tidb_non_prepared_plan_cache_size, tidb_enable_non_prepared_plan_cache, tidb_enable_non_prepared_plan_cache_for_dml, TiDB Distributed eXecution Framework, DXF, tidb_enable_dist_task, SET GLOBAL tidb_enable_dist_task = ON, ADD INDEX
- Follow-up Guidance: The source also points to related documentation for Partitioned Raft KV, TiFlash late materialization, MPP mode join algorithm support, scatter read hotspots, SQL non-prepared plan cache, and the TiDB Distributed eXecution Framework.
- Classification Note: This is a self-managed TiDB 7.1.0 release-note chunk classified under shared performance features because it summarizes performance-related changes across TiDB, TiKV, TiFlash, Lightning, BR, TiCDC, SQL, and DDL execution.

## Official Source Content

### Performance

* Enhance the Partitioned Raft KV storage engine (experimental) [#11515](https://github.com/tikv/tikv/issues/11515) [#12842](https://github.com/tikv/tikv/issues/12842) @[busyjay](https://github.com/busyjay) @[tonyxuqqi](https://github.com/tonyxuqqi) @[tabokie](https://github.com/tabokie) @[bufferflies](https://github.com/bufferflies) @[5kbpers](https://github.com/5kbpers) @[SpadeA-Tang](https://github.com/SpadeA-Tang) @[nolouch](https://github.com/nolouch)

    TiDB v6.6.0 introduces the Partitioned Raft KV storage engine as an experimental feature, which uses multiple RocksDB instances to store TiKV Region data, and the data of each Region is independently stored in a separate RocksDB instance. The new storage engine can better control the number and level of files in the RocksDB instance, achieve physical isolation of data operations between Regions, and support stably managing more data. Compared with the original TiKV storage engine, using the Partitioned Raft KV storage engine can achieve about twice the write throughput and reduce the elastic scaling time by about 4/5 under the same hardware conditions and mixed read and write scenarios.

    In TiDB v7.1.0, the Partitioned Raft KV storage engine supports tools such as TiDB Lightning, BR, and TiCDC.

    Currently, this feature is experimental and not recommended for use in production environments. You can only use this engine in a newly created cluster and you cannot directly upgrade from the original TiKV storage engine.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/partitioned-raft-kv).

* TiFlash supports late materialization (GA) [#5829](https://github.com/pingcap/tiflash/issues/5829) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)

    In v7.0.0, late materialization was introduced in TiFlash as an experimental feature for optimizing query performance. This feature is disabled by default (the [`tidb_opt_enable_late_materialization`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_late_materialization-new-in-v700) system variable defaults to `OFF`). When processing a `SELECT` statement with filter conditions (`WHERE` clause), TiFlash reads all the data from the columns required by the query, and then filters and aggregates the data based on the query conditions. When Late materialization is enabled, TiDB supports pushing down part of the filter conditions to the TableScan operator. That is, TiFlash first scans the column data related to the filter conditions that are pushed down to the TableScan operator, filters the rows that meet the condition, and then scans the other column data of these rows for further calculation, thereby reducing IO scans and computations of data processing.

    Starting from v7.1.0, the TiFlash late materialization feature is generally available and enabled by default (the [`tidb_opt_enable_late_materialization`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_late_materialization-new-in-v700) system variable defaults to `ON`). The TiDB optimizer decides which filters to be pushed down to the TableScan operator based on the statistics and the filter conditions of the query.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-late-materialization).

* TiFlash supports automatically choosing an MPP Join algorithm according to the overhead of network transmission [#7084](https://github.com/pingcap/tiflash/issues/7084) @[solotzg](https://github.com/solotzg)

    The TiFlash MPP mode supports multiple Join algorithms. Before v7.1.0, TiDB determines whether the MPP mode uses the Broadcast Hash Join algorithm based on the [`tidb_broadcast_join_threshold_count`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_count-new-in-v50) and [`tidb_broadcast_join_threshold_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_size-new-in-v50) variables and the actual data volume.

    In v7.1.0, TiDB introduces the [`tidb_prefer_broadcast_join_by_exchange_data_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_prefer_broadcast_join_by_exchange_data_size-new-in-v710) variable, which controls whether to choose the MPP Join algorithm based on the minimum overhead of network transmission. This variable is disabled by default, indicating that the default algorithm selection method remains the same as that before v7.1.0. You can set the variable to `ON` to enable it. When it is enabled, you no longer need to manually adjust the [`tidb_broadcast_join_threshold_count`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_count-new-in-v50) and [`tidb_broadcast_join_threshold_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_size-new-in-v50) variables (both variables does not take effect at this time), TiDB automatically estimates the threshold of network transmission by different Join algorithms, and then chooses the algorithm with the smallest overhead overall, thus reducing network traffic and improving MPP query performance.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode#algorithm-support-for-the-mpp-mode).

* Support load-based replica read to mitigate read hotspots [#14151](https://github.com/tikv/tikv/issues/14151) @[sticnarf](https://github.com/sticnarf) @[you06](https://github.com/you06)

    In a read hotspot scenario, the hotspot TiKV node cannot process read requests in time, resulting in the read requests queuing. However, not all TiKV resources are exhausted at this time. To reduce latency, TiDB v7.1.0 introduces the load-based replica read feature, which allows TiDB to read data from other TiKV nodes without queuing on the hotspot TiKV node. You can control the queue length of read requests using the [`tidb_load_based_replica_read_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_load_based_replica_read_threshold-new-in-v700) system variable. When the estimated queue time of the leader node exceeds this threshold, TiDB prioritizes reading data from follower nodes. This feature can improve read throughput by 70% to 200% in a read hotspot scenario compared to not scattering read hotspots.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#scatter-read-hotspots).

* Enhance the capability of caching execution plans for non-prepared statements (experimental) [#36598](https://github.com/pingcap/tidb/issues/36598) @[qw4990](https://github.com/qw4990)

    TiDB v7.0.0 introduces non-prepared plan cache as an experimental feature to improve the load capacity of concurrent OLTP. In v7.1.0, TiDB enhances this feature and supports caching more SQL statements.

    To improve memory utilization, TiDB v7.1.0 merges the cache pools of non-prepared and prepared plan caches. You can control the cache size using the system variable [`tidb_session_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_session_plan_cache_size-new-in-v710). The [`tidb_prepared_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_prepared_plan_cache_size-new-in-v610) and [`tidb_non_prepared_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_non_prepared_plan_cache_size) system variables are deprecated.
    To maintain forward compatibility, when you upgrade from an earlier version to v7.1.0 or later versions, the cache size `tidb_session_plan_cache_size` remains the same value as `tidb_prepared_plan_cache_size`, and [`tidb_enable_non_prepared_plan_cache`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_non_prepared_plan_cache) remains the setting before the upgrade. After sufficient performance testing, you can enable non-prepared plan cache using `tidb_enable_non_prepared_plan_cache`. For a newly created cluster, non-prepared plan cache is enabled by default.

    Non-prepared plan cache does not support DML statements by default. To remove this restriction, you can set the [`tidb_enable_non_prepared_plan_cache_for_dml`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_non_prepared_plan_cache_for_dml-new-in-v710) system variable to `ON`.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache).

* Support the TiDB Distributed eXecution Framework (DXF) (experimental) [#41495](https://github.com/pingcap/tidb/issues/41495) @[benjamin2037](https://github.com/benjamin2037)

    Before TiDB v7.1.0, only one TiDB node can serve as the DDL owner and execute DDL tasks at the same time. Starting from TiDB v7.1.0, in the new DXF, multiple TiDB nodes can execute the same DDL task in parallel, thus better utilizing the resources of the TiDB cluster and significantly improving the performance of DDL. In addition, you can linearly improve the performance of DDL by adding more TiDB nodes. Note that this feature is currently experimental and only supports `ADD INDEX` operations.

    To use the DXF, set the value of [`tidb_enable_dist_task`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_dist_task-new-in-v710) to `ON`:

    ```sql
    SET GLOBAL tidb_enable_dist_task = ON;
    ```

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework).
