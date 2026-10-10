# Performance Overview workload, KV request, and resource analysis

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-tuning-methods.md`
- Source Title: `Performance Analysis and Tuning`
- Source Heading Path: `Performance Analysis and Tuning > Performance analysis and tuning using the Performance Overview dashboard > TiDB key metrics and cluster resource utilization > Query Per Second, Command Per Second, and Prepared-Plan-Cache | Performance Analysis and Tuning > Performance analysis and tuning using the Performance Overview dashboard > TiDB key metrics and cluster resource utilization > KV/TSO Request OPS and KV Request Time By Source | Performance Analysis and Tuning > Performance analysis and tuning using the Performance Overview dashboard > TiDB key metrics and cluster resource utilization > TiDB CPU, TiKV CPU, and IO usage | Performance Analysis and Tuning > Performance analysis and tuning using the Performance Overview dashboard > Query latency breakdown and key latency metrics`
- Source Line Ranges: `138-251`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `tikv`, `pd`, `sql`, `tiflash`
- Topic Tags: `performance-overview`, `qps`, `cps`, `prepared-plan-cache`, `kv-requests`, `tso-requests`, `cpu-usage`, `io-throughput`, `latency-breakdown`, `workload-analysis`, `resource-bottlenecks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0134_b9c2bc0c39`
- Source ID: `tidb-docs-8.1:performance-tuning-methods.md#query-per-second-command-per-second-and-prepared-plan-cache`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6ca9dbeee55192d6c98172d9a4851a5db35935821bb0e65a8f9c1327e602daef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-tuning-methods#query-per-second-command-per-second-and-prepared-plan-cache
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-tuning-methods.md

## Retrieval Guidance

- Use When: Use this chunk when analyzing the Performance Overview dashboard to interpret QPS, CPS By Type, Queries Using Plan Cache OPS, KV/TSO Request OPS, KV Request Time By Source, TiDB CPU, TiKV CPU/IO MBps, and latency percentile panels for workload profile and resource bottlenecks.
- Retrieval Keywords: Performance Overview, QPS, CPS By Type, Queries Using Plan Cache OPS, prepared plan cache, avg-hit, avg-miss, StmtExecute, StmtPrepare, StmtClose, StmtFetch, KV/TSO Request OPS, KV Request Time By Source, kv request total, external, internal, Commit-external_Commit, Prewrite-external_Commit, Cop-internal_stats, TiDB CPU, TiKV CPU/IO MBps, delta, Query latency breakdown, 99th percentile, 999th percentile, tidb_ignore_prepared_cache_close_stmt
- Follow-up Guidance: The content includes example interpretations for TPC-C workload, read-only OLTP workload, prepared statement loops, prepared statement leaks, analyze workload, and high TiDB or TiKV resource usage.
- Classification Note: This is classified as performance content because it explains how dashboard metrics and request patterns reveal workload characteristics, plan cache behavior, latency behavior, and TiDB or TiKV resource bottlenecks.

## Official Source Content

#### Query Per Second, Command Per Second, and Prepared-Plan-Cache

By checking the following three panels in Performance Overview, you can learn the application workload type, how the application interacts with TiDB, and whether the application fully utilizes TiDB [prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache).

- QPS: Short for Query Per Second. It shows the count of SQL statements executed by the application.
- CPS By Type: Short for Command Per Second. Command indicates MySQL protocol-specific commands. A query statement can be sent to TiDB either by a query command or a prepared statement.
- Queries Using Plan Cache OPS: `avg-hit` is the number of queries using the execution plan cache per second in a TiDB cluster, and `avg-miss` is the number of queries not using the execution plan cache per second in a TiDB cluster.

    `avg-hit + avg-miss` is equal to `StmtExecute`, which is the number of all queries executed per second. When prepared plan cache is enabled in TiDB, the following three scenarios will occur:

    - No prepared plan cache is hit: `avg-hit` (the number of hits per second) is 0, and `avg-miss` is equal to the number of `StmtExecute` commands per second. The possible reasons include:
        - The application is using the query interface.
        - The cached plans are cleaned up because the application calls the `StmtClose` command after each `StmtExecute` execution.
        - All statements executed by `StmtExecute` do not meet the [cache conditions](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache) so the execution plan cache cannot be hit.
    - All prepared plan cache is hit: `avg-hit` (the number of hits per second) is equal to the number of `StmtExecute` commands per second, and `avg-miss` (the number without hits per second) is 0.
    - Some prepared plan cache is hit: `avg-hit` (the number of hits per second) is fewer than the number of `StmtExecute` commands per second. Prepared plan cache has known limitations. For example, it does not support subqueries, so SQL statements with subqueries cannot use prepared plan cache.

**Example 1: TPC-C workload**

The TPC-C workload are mainly `UPDATE`, `SELECT`, and `INSERT` statements. The total QPS is equal to the number of `StmtExecute` commands per second and the latter is almost equal to `avg-hit` on the Queries Using Plan Cache OPS panel. Ideally, the client caches the object of the prepared statement. In this way, the cached statement is called directly when a SQL statement is executed. All SQL executions hit the prepared plan cache, and there is no need to recompile to generate execution plans.

![TPC-C](/media/performance/tpcc_qps.png)

**Example 2: Prepared plan cache unavailable for query commands in read-only OLTP workload**

In this workload, `Commit QPS` = `Rollback QPS` = `Select QPS`. The application has enabled auto-commit concurrency, and rollback is performed every time a connection is fetched from the connection pool. As a result, these three statements are executed the same number of times.

![OLTP-Query](/media/performance/oltp_long_compile_qps.png)

- The red bold line in the QPS panel stands for failed queries, and the Y-axis on the right shows the number of failed queries. A value other than 0 means the presence of failed queries.
- The total QPS is equal to the number of queries in the CPS By Type panel, the query command has been used by the application.
- The Queries Using Plan Cache OPS panel has no data, because prepared plan cache is unavailable for query command. This means that TiDB needs to parse and generate an execution plan for every query execution. As a result, the compile time is longer with increasing CPU consumption by TiDB.

**Example 3: Prepared plan cache unavailable with prepared statement enabled for OLTP workload**

`StmtPrepare` times = `StmtExecute` times = `StmtClose` times ~= `StmtFetch` times. The application uses the prepare > execute > fetch > close loop. To prevent prepared statement object leak, many application frameworks call `close` after the `execute` phase. This creates two problems.

- A SQL execution requires four commands and four network round trips.
- Queries Using Plan Cache OPS is 0, indicating zero hit of prepared plan cache. The `StmtClose` command clears cached execution plans by default and the next `StmtPrepare` command needs to generate the execution plan again.

> **Note:**
>
> Starting from TiDB v6.0.0, you can prevent the `StmtClose` command from clearing cached execution plans via the global variable (`set global tidb_ignore_prepared_cache_close_stmt=on;`). In this way, subsequent executions can hit the prepared plan cache.

![OLTP-Prepared](/media/performance/oltp_prepared_statement_no_plan_cache.png)

**Example 4: Prepared statements have a resource leak**

The number of `StmtPrepare` commands per second is much greater than that of `StmtClose` per second, which indicates that the application has an object leak for prepared statements.

![OLTP-Query](/media/performance/prepared_statement_leaking.png)

- In the QPS panel, the red bold line indicates the number of failed queries, and the Y axis on the right indicates the coordinate value of the number. In this example, the number of failed queries per second is 74.6.
- In the CPS By Type panel, the number of `StmtPrepare` commands per second is much greater than that of `StmtClose` per second, which indicates that an object leak occurs in the application for prepared statements.
- In the Queries Using Plan Cache OPS panel, `avg-miss` is almost equal to `StmtExecute` in the CPS By Type panel, which indicates that almost all SQL executions miss the execution plan cache.
#### KV/TSO Request OPS and KV Request Time By Source

- In the KV/TSO Request OPS panel, you can view the statistics of KV and TSO requests per second. Among the statistics, `kv request total` represents the sum of all requests from TiDB to TiKV. By observing the types of requests from TiDB to PD and TiKV, you can get an idea of the workload profile within the cluster.
- In the KV Request Time By Source panel, you can view the time ratio of each KV request type and all request sources.
    - kv request total time: The total time of processing KV and TiFlash requests per second.
    - Each KV request and the corresponding request source form a stacked bar chart, in which `external` identifies normal business requests and `internal` identifies internal activity requests (such as DDL and auto analyze requests).

**Example 1: Busy workload**

![TPC-C](/media/performance/tpcc_source_sql.png)

In this TPC-C workload:

- The total number of KV requests per second is 79,700. The top request types are `Prewrite`, `Commit`, `PessimisticLock`, and `BatchGet` in order of number of requests.
- Most of the KV processing time is spent on `Commit-external_Commit` and `Prewrite-external_Commit`, which indicates that the most time-consuming KV requests are `Commit` and `Prewrite` from external commit statements.

**Example 2: Analyze workload**

![OLTP](/media/performance/internal_stats.png)

In this workload, only `ANALYZE` statements are running in the cluster:

- The total number of KV requests per second is 35.5 and the number of Cop requests per second is 9.3.
- Most of the KV processing time is spent on `Cop-internal_stats`, which indicates that the most time-consuming KV request is `Cop` from internal `ANALYZE` operations.
#### TiDB CPU, TiKV CPU, and IO usage

In the TiDB CPU and TiKV CPU/IO MBps panels, you can observe the logical CPU usage and IO throughput of TiDB and TiKV, including average, maximum, and delta (maximum CPU usage minus minimum CPU usage), based on which you can determine the overall CPU usage of TiDB and TiKV.

- Based on the `delta` value, you can determine if CPU usage in TiDB is unbalanced (usually accompanied by unbalanced application connections) and if there are read/write hot spots among the cluster.
- With an overview of TiDB and TiKV resource usage, you can quickly determine if there are resource bottlenecks in your cluster and whether TiKV or TiDB needs scale-out.

**Example 1: High TiDB resource usage**

In this workload, each TiDB and TiKV is configured with 8 CPUs.

![TPC-C](/media/performance/tidb_high_cpu.png)

- The average, maximum, and delta CPU usage of TiDB are 575%, 643%, and 136%, respectively.
- The average, maximum, and delta CPU usage of TiKV are 146%, 215%, and 118%, respectively. The average, maximum, and delta I/O throughput of TiKV are 9.06 MB/s, 19.7 MB/s, and 17.1 MB/s, respectively.

Obviously, TiDB consumes more CPU, which is near the bottleneck threshold of 8 CPUs. It is recommended that you scale out the TiDB.

**Example 2: High TiKV resource usage**

In the TPC-C workload below, each TiDB and TiKV is configured with 16 CPUs.

![TPC-C](/media/performance/tpcc_cpu_io.png)

- The average, maximum, and delta CPU usage of TiDB are 883%, 962%, and 153%, respectively.
- The average, maximum, and delta CPU usage of TiKV are 1288%, 1360%, and 126%, respectively. The average, maximum, and delta I/O throughput of TiKV are 130 MB/s, 153 MB/s, and 53.7 MB/s, respectively.

Obviously, TiKV consumes more CPU, which is expected because TPC-C is a write-heavy scenario. It is recommended that you scale out the TiKV to improve performance.
### Query latency breakdown and key latency metrics

The latency panel provides average values and 99th percentile. The average values help identify the overall bottleneck, while the 99th or 999th percentile or 999th helps determine whether there is a significant latency jitter.
