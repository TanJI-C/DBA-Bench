# Manual profiling overview, supported data, and page access

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-profiling.md`
- Source Title: `TiDB Dashboard Instance Profiling - Manual Profiling`
- Source Heading Path: `TiDB Dashboard Instance Profiling - Manual Profiling | TiDB Dashboard Instance Profiling - Manual Profiling > Supported performance data | TiDB Dashboard Instance Profiling - Manual Profiling > Access the page`
- Source Line Ranges: `5-43`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tidb`, `tikv`, `tiflash`
- Topic Tags: `manual profiling`, `performance data`, `cpu profile`, `heap profile`, `mutex`, `goroutine`, `access`, `advanced debugging`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0032_ee5d82f048`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-profiling.md#tidb-dashboard-instance-profiling-manual-profiling`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b404a73a0b004811f9ecd58d6efebf7edcbb5dc3cafed5d29f31f28974491799`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-profiling#tidb-dashboard-instance-profiling-manual-profiling
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-profiling.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about what Manual Profiling in TiDB Dashboard collects, which instance types and profile types are supported, or how to open the Manual Profiling page.
- Retrieval Keywords: Manual Profiling, TiDB Dashboard Instance Profiling, Supported performance data, CPU, Heap, Mutex, Goroutine, FlameGraph, DAG, Advanced Debugging, Profiling Instances, Manual Profiling page, http://127.0.0.1:2379/dashboard/#/instance_profiling, PD instance address and port, TiDB, TiKV, PD, TiFlash, ongoing performance problems, high CPU overhead, high memory usage, process stalls
- Follow-up Guidance: The source also states that profiling collects current performance data for a period of time, 30 seconds by default, and points to Continuous Profiling for collecting and analyzing performance data at any time.
- Classification Note: This is classified as observability because the content describes collecting and visualizing current performance data to analyze resource consumption and ongoing performance problems.

## Official Source Content

# TiDB Dashboard Instance Profiling - Manual Profiling

> **Note:**
>
> This feature is designed for database experts. For non-expert users, it is recommended to use this feature under the guidance of PingCAP technical supports.

Manual Profiling allows users to collect current performance data **on demand** for each TiDB, TiKV, PD and TiFlash instances with a single click. The collected performance data can be visualized as FlameGraph or DAG.

With these performance data, experts can analyze current resource consumption details like instance's CPU and memory, to help pinpoint sophisticated ongoing performance problems, such as high CPU overhead, high memory usage, and process stalls.

After initiates the profiling, TiDB Dashboard collects current performance data for a period of time (30 seconds by default). Therefore this feature can only be used to analyze ongoing problems that the cluster is facing now and has no significant effect on historical problems. If you want to collect and analyze performance data **at any time**, see [Continuous Profiling](https://docs.pingcap.com/tidb/stable/dashboard/continuous-profiling).
## Supported performance data

The following performance data are currently supported:

- CPU: The CPU overhead of each internal function on TiDB, TiKV, PD and TiFlash instances

  > The CPU overhead of TiKV and TiFlash instances is currently not supported in ARM architecture.

- Heap: The memory consumption of each internal function on TiDB, TiKV, and PD instances

  > Starting from v7.5, TiDB supports the TiKV Heap Profile. The Perl dependency is required in the running environment of TiDB Dashboard. Otherwise an error will occur.

- Mutex: The mutex contention states on TiDB and PD instances

- Goroutine: The running state and call stack of all goroutines on TiDB and PD instances
## Access the page

You can access the instance profiling page using either of the following methods:

* After logging in to TiDB Dashboard, click **Advanced Debugging** > **Profiling Instances** > **Manual Profiling** in the left navigation menu.

  ![Access instance profiling page](/media/dashboard/dashboard-profiling-access.png)

* Visit <http://127.0.0.1:2379/dashboard/#/instance_profiling> in your browser. Replace `127.0.0.1:2379` with the actual PD instance address and port.
