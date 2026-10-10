# Prepared plan cache memory management and limits

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-prepared-plan-cache.md`
- Source Title: `SQL Prepared Execution Plan Cache`
- Source Heading Path: `SQL Prepared Execution Plan Cache > Memory management of Prepared Plan Cache`
- Source Line Ranges: `171-221`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `prepared-plan-cache`, `memory-management`, `grafana`, `memory-usage`, `eviction`, `system-variables`, `session-cache`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0169_94d5ff841f`
- Source ID: `tidb-docs-8.1:sql-prepared-plan-cache.md#memory-management-of-prepared-plan-cache`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ebf95f143c9e1779cfb990e87b2f5e0e2e706f93ab0f88ce4cfbcfb17c3451f4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache#memory-management-of-prepared-plan-cache
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-prepared-plan-cache.md

## Retrieval Guidance

- Use When: Use this when looking up prepared plan cache memory usage, cache size limits, eviction thresholds, and related Grafana metrics for each TiDB instance or session.
- Retrieval Keywords: Plan Cache Memory Usage, Plan Cache Plan Num, Plan Cache Miss OPS, tidb_session_plan_cache_size, tidb_plan_cache_max_plan_size, tidb_prepared_plan_cache_memory_guard_ratio, SESSION level, memory protection mechanism
- Follow-up Guidance: The content points to Grafana panels and system variables that show total cached plan memory, plan count, miss status, per-session cache size, max plan size, and the memory guard threshold.
- Classification Note: This is classified as performance because the official content focuses on memory overhead, cache capacity, eviction, and monitoring metrics for prepared plan cache.

## Official Source Content

## Memory management of Prepared Plan Cache

Using Prepared Plan Cache incurs memory overhead. To view the total memory consumption by the cached execution plans of all sessions in each TiDB instance, you can use the [**Plan Cache Memory Usage** monitoring panel](https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard) in Grafana.

> **Note:**
>
> Because of the memory reclaim mechanism of Golang and some uncounted memory structures, the memory displayed in Grafana is not equal to the actual heap memory usage. It is tested that there is a deviation of about ±20% between the memory displayed in Grafana and the actual heap memory usage.

To view the total number of execution plans cached in each TiDB instance, you can use the [**Plan Cache Plan Num** panel](https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard) in Grafana.

The following is an example of the **Plan Cache Memory Usage** and **Plan Cache Plan Num** panels in Grafana:

![grafana_panels](/media/planCache-memoryUsage-planNum-panels.png)

Starting from v7.1.0, you can control the maximum number of plans that can be cached in each session by configuring the system variable [`tidb_session_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_session_plan_cache_size-new-in-v710). For different environments, the recommended value is as follows and you can adjust it according to the monitoring panels:

Using Prepared Plan Cache has some memory overhead. In internal tests, each cached plan consumes an average of 100 KiB of memory. Because Plan Cache is currently at the `SESSION` level, the total memory consumption is approximately `the number of sessions * the average number of cached plans in a session * 100 KiB`.

For example, the current TiDB instance has 50 sessions in concurrency and each session has approximately 100 cached plans. The total memory consumption is approximately `50 * 100 * 100 KiB` = `512 MB`.

You can control the maximum number of plans that can be cached in each session by configuring the system variable [`tidb_session_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_session_plan_cache_size-new-in-v710). For different environments, the recommended value is as follows:

- When the memory threshold of the TiDB server instance is <= 64 GiB, set `tidb_session_plan_cache_size` to `50`.
- When the memory threshold of the TiDB server instance is > 64 GiB, set `tidb_session_plan_cache_size` to `100`.

Starting from v7.1.0, you can control the maximum size of a plan that can be cached using the system variable [`tidb_plan_cache_max_plan_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_plan_cache_max_plan_size-new-in-v710). The default value is 2 MB. If the size of a plan exceeds this value, the plan will not be cached.

When the unused memory of the TiDB server is less than a certain threshold, the memory protection mechanism of plan cache is triggered, through which some cached plans will be evicted.

You can control the threshold by configuring the system variable `tidb_prepared_plan_cache_memory_guard_ratio`. The threshold is 0.1 by default, which means when the unused memory of the TiDB server is less than 10% of the total memory (90% of the memory is used), the memory protection mechanism is triggered.

Due to memory limit, plan cache might be missed sometimes. You can check the status by viewing the [`Plan Cache Miss OPS` metric](https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard) in the Grafana dashboard.

Due to memory limit, plan cache might be missed sometimes.
