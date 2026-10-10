# Load statistics behavior and initialization options

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > Load statistics`
- Source Line Ranges: `471-510`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `statistics`, `loading`, `optimizer`, `memory`, `startup`, `configuration`, `histogram`, `topn`, `cmsketch`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0187_5d5b8ffcb4`
- Source ID: `tidb-docs-8.1:statistics.md#load-statistics`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b52cd6c6870ef30f2760503a015835c5fba4e9a90e3fbc569e9c2adacbbb6335`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#load-statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving information about how TiDB loads column statistics into memory, synchronous statistics loading, startup statistics initialization, or related configuration variables and options.
- Retrieval Keywords: Load statistics, tidb_stats_load_sync_wait, tidb_stats_load_pseudo_timeout, stats-load-concurrency, stats-load-queue-size, force-init-stats, lite-init-stats, histograms, TopN, Count-Min Sketch, CMSketch, asynchronously on demand, synchronously loading statistics, statistics initialization, startup, optimizer uses the histogram statistics
- Follow-up Guidance: It also provides the timeout behavior controlled by tidb_stats_load_pseudo_timeout and the startup initialization options force-init-stats and lite-init-stats.
- Classification Note: This is classified as performance for TiDB because the content explains how statistics loading and initialization affect SQL optimization completeness, execution plans, memory usage, and startup behavior.

## Official Source Content

## Load statistics

> **Note:**
>
> Loading statistics is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

By default, depending on the size of column statistics, TiDB loads statistics differently as follows:

- For statistics that consume small amounts of memory (such as count, distinctCount, and nullCount), as long as the column data is updated, TiDB automatically loads the corresponding statistics into memory for use in the SQL optimization stage.
- For statistics that consume large amounts of memory (such as histograms, TopN, and Count-Min Sketch), to ensure the performance of SQL execution, TiDB loads the statistics asynchronously on demand. Take histograms as an example. TiDB loads histogram statistics on a column into memory only when the optimizer uses the histogram statistics on that column. On-demand asynchronous statistics loading does not affect the performance of SQL execution but might provide incomplete statistics for SQL optimization.

Since v5.4.0, TiDB introduces the synchronously loading statistics feature. This feature allows TiDB to synchronously load large-sized statistics (such as histograms, TopN, and Count-Min Sketch statistics) into memory when you execute SQL statements, which improves the completeness of statistics for SQL optimization.

To enable this feature, set the value of the [`tidb_stats_load_sync_wait`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_stats_load_sync_wait-new-in-v540) system variable to a timeout (in milliseconds) that SQL optimization can wait for at most to synchronously load complete column statistics. The default value of this variable is `100`, indicating that the feature is enabled.

After enabling the synchronously loading statistics feature, you can further configure the feature as follows:

- To control how TiDB behaves when the waiting time of SQL optimization reaches the timeout, modify the value of the [`tidb_stats_load_pseudo_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_stats_load_pseudo_timeout-new-in-v540) system variable. The default value of this variable is `ON`, indicating that after the timeout, the SQL optimization process does not use any histogram, TopN, or CMSketch statistics on any columns. If this variable is set to `OFF`, after the timeout, SQL execution fails.
- To specify the maximum number of columns that the synchronously loading statistics feature can process concurrently, modify the value of the [`stats-load-concurrency`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#stats-load-concurrency-new-in-v540) option in the TiDB configuration file. The default value is `5`.
- To specify the maximum number of column requests that the synchronously loading statistics feature can cache, modify the value of the [`stats-load-queue-size`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#stats-load-queue-size-new-in-v540) option in the TiDB configuration file. The default value is `1000`.

During TiDB startup, SQL statements executed before the initial statistics are fully loaded might have suboptimal execution plans, thus causing performance issues. To avoid such issues, TiDB v7.1.0 introduces the configuration parameter [`force-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#force-init-stats-new-in-v657-and-v710). With this option, you can control whether TiDB provides services only after statistics initialization has been finished during startup. Starting from v7.2.0, this parameter is enabled by default.

Starting from v7.1.0, TiDB introduces [`lite-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#lite-init-stats-new-in-v710) for lightweight statistics initialization.

- When the value of `lite-init-stats` is `true`, statistics initialization does not load any histogram, TopN, or Count-Min Sketch of indexes or columns into memory.
- When the value of `lite-init-stats` is `false`, statistics initialization loads histograms, TopN, and Count-Min Sketch of indexes and primary keys into memory but does not load any histogram, TopN, or Count-Min Sketch of non-primary key columns into memory. When the optimizer needs the histogram, TopN, and Count-Min Sketch of a specific index or column, the necessary statistics are loaded into memory synchronously or asynchronously.

The default value of `lite-init-stats` is `true`, which means to enable lightweight statistics initialization. Setting `lite-init-stats` to `true` speeds up statistics initialization and reduces TiDB memory usage by avoiding unnecessary statistics loading.

After enabling the synchronously loading statistics feature, you can control how TiDB behaves when the waiting time of SQL optimization reaches the timeout by modifying the value of the [`tidb_stats_load_pseudo_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_stats_load_pseudo_timeout-new-in-v540) system variable. The default value of this variable is `ON`, indicating that after the timeout, the SQL optimization process does not use any histogram, TopN, or CMSketch statistics on any columns. If this variable is set to `OFF`, after the timeout, SQL execution fails.
