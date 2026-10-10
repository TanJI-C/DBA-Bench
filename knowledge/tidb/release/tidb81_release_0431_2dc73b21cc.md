# Performance feature updates across TiDB, TiFlash, and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.0.0.md`
- Source Title: `TiDB 7.0.0 Release Notes`
- Source Heading Path: `TiDB 7.0.0 Release Notes > Feature details > Performance`
- Source Line Ranges: `81-146`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `sql`, `tidb`, `tiflash`, `tikv`
- Topic Tags: `performance`, `fast-online-ddl`, `pitr`, `plan-cache`, `mpp`, `fastscan`, `late-materialization`, `null-aware-semi-join`, `raft-log-recycling`, `window-functions`, `topn`, `limit`, `unique-indexes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0431_2dc73b21cc`
- Source ID: `tidb-docs-8.1:releases/release-7.0.0.md#performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7edc2aff318ad82d0aab3851fc6271fdf0d80c7cf5188de7912e6512b9de3832`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.0.0#performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 7.0.0 performance release-note changes across TiDB, TiFlash, and TiKV such as Fast Online DDL with PITR, TiFlash pushdown and scan optimizations, plan cache expansion, Raft log recycling, window function optimization, and unique indexes.
- Retrieval Keywords: TiDB 7.0.0 Performance, Fast Online DDL PITR compatibility, #38045, null-aware semi join, null-aware anti semi join, IN NOT IN = ANY != ALL, correlated subqueries, TiFlash replicas, MPP mode, #6674, FastScan, tiflash_fastscan, #5252, late materialization, tidb_opt_enable_late_materialization, #5829, non-prepared plan cache, tidb_enable_non_prepared_plan_cache, tidb_non_prepared_plan_cache_size, #36598, execution plan cache subqueries, #40219, SELECT * FROM t WHERE a > (SELECT ...), Raft log recycling, raft-engine.prefill-for-recycle, #14371, derive TopN from window functions, Limit operator, tidb_opt_derive_topn, #13936, unique indexes through Fast Online DDL, #40730
- Follow-up Guidance: The source points to documentation for DDL introduction, TiFlash supported pushdown calculations, FastScan, TiFlash late materialization, non-prepared plan cache restrictions, prepared plan cache, TiKV configuration for prefill-for-recycle, and deriving TopN from window functions.
- Classification Note: This chunk is classified as a self-managed release note for the shared component because it summarizes performance feature updates in TiDB 7.0.0 spanning BR, SQL, TiDB, TiFlash, and TiKV.

## Official Source Content

### Performance

* Achieve compatibility between Fast Online DDL and PITR [#38045](https://github.com/pingcap/tidb/issues/38045) @[Leavrth](https://github.com/Leavrth)

    In TiDB v6.5.0, [Fast Online DDL](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630) is not fully compatible with [PITR](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview). To ensure a full data backup, it is recommended to first stop the PITR background backup task, quickly add indexes using Fast Online DDL, and then resume the PITR backup task.

    Starting from TiDB v7.0.0, Fast Online DDL and PITR are fully compatible. When restoring cluster data through PITR, the index operations added via Fast Online DDL during log backup will be automatically replayed to achieve compatibility.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction).

* TiFlash supports null-aware semi join and null-aware anti semi join operators [#6674](https://github.com/pingcap/tiflash/issues/6674) @[gengliqi](https://github.com/gengliqi)

    When using `IN`, `NOT IN`, `= ANY`, or `!= ALL` operators in correlated subqueries, TiDB optimizes the computing performance by converting them to semi join or anti semi join. If the join key column might be `NULL`, a null-aware join algorithm is required, such as [Null-aware semi join](https://docs.pingcap.com/tidb/stable/explain-subqueries#null-aware-semi-join-in-and--any-subqueries) and [Null-aware anti semi join](https://docs.pingcap.com/tidb/stable/explain-subqueries#null-aware-anti-semi-join-not-in-and--all-subqueries).

    Before v7.0.0, TiFlash does not support null-aware semi join and null-aware anti semi join operators, preventing these subqueries from being directly pushed down to TiFlash. Starting from v7.0.0, TiFlash supports null-aware semi join and null-aware anti semi join operators. If a SQL statement contains these correlated subqueries, the tables in the query have TiFlash replicas, and [MPP mode](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode) is enabled, the optimizer automatically determines whether to push down null-aware semi join and null-aware anti semi join operators to TiFlash to improve overall performance.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations).

* TiFlash supports using FastScan (GA) [#5252](https://github.com/pingcap/tiflash/issues/5252) @[hongyunyan](https://github.com/hongyunyan)

    Starting from v6.3.0, TiFlash introduces FastScan as an experimental feature. In v7.0.0, this feature becomes generally available. You can enable FastScan using the system variable [`tiflash_fastscan`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_fastscan-new-in-v630). By sacrificing strong consistency, this feature significantly improves table scan performance. If the corresponding table only involves `INSERT` operations without any `UPDATE`/`DELETE` operations, FastScan can keep strong consistency and improve the scan performance.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tiflash/use-fastscan).

* TiFlash supports late materialization (experimental) [#5829](https://github.com/pingcap/tiflash/issues/5829) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)

    When processing a `SELECT` statement with filter conditions (`WHERE` clause), TiFlash reads all the data from the columns required by the query by default, and then filters and aggregates the data based on the query conditions. Late materialization is an optimization method that supports pushing down part of the filter conditions to the TableScan operator. That is, TiFlash first scans the column data related to the filter conditions that are pushed down, filters the rows that meet the condition, and then scans the other column data of these rows for further calculation, thereby reducing IO scans and computations of data processing.

    The TiFlash late materialization feature is not enabled by default. You can enable it by setting the `tidb_opt_enable_late_materialization` system variable to `OFF`. When the feature is enabled, the TiDB optimizer will determine which filter conditions to be pushed down based on statistics and filter conditions.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-late-materialization).

* Support caching execution plans for non-prepared statements (experimental) [#36598](https://github.com/pingcap/tidb/issues/36598) @[qw4990](https://github.com/qw4990)

    The execution plan cache is important for improving the load capacity of concurrent OLTP and TiDB already supports [Prepared execution plan cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache). In v7.0.0, TiDB can also cache execution plans for non-Prepare statements, expanding the scope of execution plan cache and improving the concurrent processing capacity of TiDB.

    This feature is disabled by default. You can enable it by setting the system variable [`tidb_enable_non_prepared_plan_cache`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_non_prepared_plan_cache) to `ON`. For stability reasons, TiDB v7.0.0 allocates a new area for caching non-prepared execution plans and you can set the cache size using the system variable [`tidb_non_prepared_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_non_prepared_plan_cache_size). Additionally, this feature has certain restrictions on SQL statements. For more information, see [Restrictions](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache#restrictions).

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache).

* TiDB removes the execution plan cache constraint for subqueries [#40219](https://github.com/pingcap/tidb/issues/40219) @[fzzf678](https://github.com/fzzf678)

    TiDB v7.0.0 removes the execution plan cache constraint for subqueries. This means that the execution plan of SQL statements with subqueries can now be cached, such as `SELECT * FROM t WHERE a > (SELECT ...)`. This feature further expands the application scope of execution plan cache and improves the execution efficiency of SQL queries.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache).

* TiKV supports automatically generating empty log files for log recycling [#14371](https://github.com/tikv/tikv/issues/14371) @[LykxSassinator](https://github.com/LykxSassinator)

    In v6.3.0, TiKV introduced the [Raft log recycling](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-log-recycle-new-in-v630) feature to reduce long-tail latency caused by write load. However, log recycling can only take effect when the number of Raft log files reaches a certain threshold, making it difficult for users to directly experience the throughput improvement brought by this feature.

    In v7.0.0, a new configuration item called `raft-engine.prefill-for-recycle` was introduced to improve user experience. This item controls whether empty log files are generated for recycling when the process starts. When this configuration is enabled, TiKV automatically fills a batch of empty log files during initialization, ensuring that log recycling takes effect immediately after initialization.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#prefill-for-recycle-new-in-v700).

* Support deriving the TopN or Limit operator from [window functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/expressions-pushed-down) to improve window function performance [#13936](https://github.com/tikv/tikv/issues/13936) @[windtalker](https://github.com/windtalker)

    This feature is disabled by default. To enable it, you can set the session variable [tidb_opt_derive_topn](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_derive_topn-new-in-v700) to `ON`.
    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/derive-topn-from-window).

* Support creating unique indexes through Fast Online DDL [#40730](https://github.com/pingcap/tidb/issues/40730) @[tangenta](https://github.com/tangenta)

    TiDB v6.5.0 supports creating ordinary secondary indexes via Fast Online DDL. TiDB v7.0.0 supports creating unique indexes via Fast Online DDL. Compared to v6.1.0, adding unique indexes to large tables is expected to be several times faster with improved performance.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction).
