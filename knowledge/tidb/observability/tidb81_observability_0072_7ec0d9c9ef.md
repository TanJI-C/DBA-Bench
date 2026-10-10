# Performance Overview dashboard interpretation and color-based tuning

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-tuning-methods.md`
- Source Title: `Performance Analysis and Tuning`
- Source Heading Path: `Performance Analysis and Tuning > Performance analysis and tuning using the Performance Overview dashboard | Performance Analysis and Tuning > Performance analysis and tuning using the Performance Overview dashboard > Database time and SQL execution time overview | Performance Analysis and Tuning > Performance analysis and tuning using the Performance Overview dashboard > Database time and SQL execution time overview > Tune by color | Performance Analysis and Tuning > Performance analysis and tuning using the Performance Overview dashboard > TiDB key metrics and cluster resource utilization`
- Source Line Ranges: `47-137`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `pd`, `tikv`, `tiflash`
- Topic Tags: `grafana`, `performance overview`, `database time`, `sql execution`, `color coding`, `workload profile`, `lock contention`, `prepared plan cache`, `mpp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0072_7ec0d9c9ef`
- Source ID: `tidb-docs-8.1:performance-tuning-methods.md#performance-analysis-and-tuning-using-the-performance-overview-dashboard`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5ca52fde4a95fc08a2bba1cb21cbd1a6f0d83bdf7f71b44fb12af4b119fd7d1b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-tuning-methods#performance-analysis-and-tuning-using-the-performance-overview-dashboard
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-tuning-methods.md

## Retrieval Guidance

- Use When: Use this chunk when you need to interpret the Grafana Performance Overview dashboard, especially color-coded database time graphs, SQL execution phases, KV or PD request types, and resource or latency sections.
- Retrieval Keywords: Performance Overview dashboard, Grafana, Database Time By SQL Type, Database Time By SQL Phase, SQL Execute Time Overview, Tune by color, StmtPrepare, StmtReset, StmtFetch, StmtClose, prepared plan cache, compile phase, Prewrite, Commit, Cop, Get, BatchGet, PessimisticLock, tso_wait, TiFlash MPP, tiflash_mpp, Top-down latency breakdown, query latency and connection idle time
- Follow-up Guidance: If non-green or non-blue areas occupy a significant proportion in the database time breakdown or execution time overview, further cause analysis is required based on the subsequent performance data.
- Classification Note: This chunk is classified as observability for the dashboard because it describes how the Performance Overview dashboard organizes TiDB, PD, TiKV, and TiFlash metrics and how colors and sections reveal workload characteristics and bottlenecks.

## Official Source Content

## Performance analysis and tuning using the Performance Overview dashboard

This section describes how to perform performance analysis and tuning based on database time using the Performance Overview dashboard in Grafana.

The Performance Overview dashboard orchestrates the metrics of TiDB, PD, and TiKV, and presents each of them in the following sections:

- Database time and SQL execution time overview: Color-coded SQL types, database time by SQL execution phase, and database time of different requests help you quickly identify database workload characteristics and performance bottlenecks.
- Key metrics and resource utilization: Contains database QPS, connection information, request command types between the applications and the database, database internal TSO and KV request OPS, and TiDB/TiKV resource usage.
- Top-down latency breakdown: Contains a comparison of query latency and connection idle time, breakdown of query latency, latency of TSO requests and KV requests in SQL execution, and breakdown of TiKV internal write latency.
### Database time and SQL execution time overview

The database time metric is the sum of the latency that TiDB processes SQL per second, which is also the total time that TiDB concurrently processes application SQL requests per second (equal to the number of active connections).

The Performance Overview dashboard provides the following three stacked area graphs. They help you understand database workload profile and quickly identify the bottleneck causes in terms of statements, sql phase, and TiKV or PD request type during SQL execution.

- Database Time By SQL Type
- Database Time By SQL Phase
- SQL Execute Time Overview
#### Tune by color

The diagrams of database time breakdown and execution time overview present both expected and unexpected time consumption intuitively. Therefore, you can quickly identify performance bottleneck and learn the workload profile. Green and blue areas stand for normal time consumption and requests. If non-green or non-blue areas occupy a significant proportion in these two diagrams, the database time distribution is inappropriate.

- Database Time By SQL Type:

    - Blue: `Select` statement
    - Green: `Update`, `Insert`, `Commit` and other DML statements
    - Red: General SQL types, including `StmtPrepare`, `StmtReset`, `StmtFetch`, and `StmtClose`

- Database Time By SQL Phase: The SQL execution phase is in green and other phases are in red on general. If non-green areas are large, it means much database time is consumed in other phases than the execution phase and further cause analysis is required. A common scenario is that the compile phase shown in orange takes a large area due to unavailability of prepared plan cache.
- SQL Execute Time Overview: Green metrics stand for common KV write requests (such as `Prewrite` and `Commit`), blue metrics stand for common KV read requests (such as Cop and Get), purple metrics stand for TiFlash MPP requests, and metrics in other colors stand for unexpected situations which you need to pay attention. For example, pessimistic lock KV requests are marked red and TSO waiting is marked dark brown. If non-blue or non-green areas are large, it means there is bottleneck during SQL execution. For example:

    - If serious lock conflicts occur, the red area will take a large proportion.
    - If excessive time is consumed in waiting TSO, the dark brown area will take a large proportion.

**Example 1: TPC-C workload**

![TPC-C](/media/performance/tpcc_db_time.png)

- Database Time by SQL Type: Most time-consuming statements are `commit`, `update`, `select`, and `insert` statements.
- Database Time by SQL Phase: The most time-consuming phase is SQL execution in green.
- SQL Execute Time Overview: The most time-consuming KV requests in SQL execution are `Prewrite` and `Commit` in green.

    > **Note:**
    >
    > It is normal that the total KV request time is greater than the execute time. Because the TiDB executor may send KV requests to multiple TiKVs concurrently, causing the total KV request wait time to be greater than the execute time. In the preceding TPC-C workload, TiDB sends `Prewrite` and `Commit` requests concurrently to multiple TiKVs when a transaction is committed. Therefore, the total time for `Prewrite`, `Commit`, and `PessimisticLock` requests in this example is obviously longer than the execute time.
    >
    > - The `execute` time may also be significantly greater than the total time of the KV request plus the `tso_wait` time. This means that the SQL execution time is spent mostly inside the TiDB executor. Here are two common examples:
    >
        > - Example 1: After TiDB executor reads a large amount of data from TiKV, it needs to do complex join and aggregation inside TiDB, which consumes a lot of time.
        > - Example 2: The application experiences serious write statement lock conflicts. Frequent lock retries result in long `Retried execution time`.

**Example 2: OLTP read-heavy workload**

![OLTP](/media/performance/oltp_normal_db_time.png)

- Database Time by SQL Type: Major time-consuming statements are `SELECT`, `COMMIT`, `UPDATE`, and `INSERT`, among which `SELECT` consumes most database time.
- Database Time by SQL Phase: Most time is consumed in the `execute` phase in green.
- SQL Execute Time Overview: In SQL execution phase, `pd tso_wait` in dark brown, `KV Get` in blue, and `Prewrite` and `Commit` in green are time-consuming.

**Example 3: Read-only OLTP workload**

![OLTP](/media/performance/oltp_long_compile_db_time.png)

- Database Time by SQL Type: Mainly are `SELECT` statements.
- Database Time by SQL Phase: Major time-consuming phases are `compile` in orange and `execute` in green. Latency in the `compile` phase is the highest, indicating that TiDB is taking too long to generate execution plans and the root cause needs to be further determined based on the subsequent performance data.
- SQL Execute Time Overview: The KV BatchGet requests in blue consume the most time during SQL execution.

> **Note:**
>
> In example 3, `SELECT` statements need to read thousands of rows concurrently from multiple TiKVs. Therefore, the total time of the `BatchGet` request is much longer than the execution time.

**Example 4: Lock contention workload**

![OLTP](/media/performance/oltp_lock_contention_db_time.png)

- Database Time by SQL Type: Mainly are `UPDATE` statements.
- Database Time by SQL Phase: Most time is consumed in the execute phase in green.
- SQL Execute Time Overview: The KV request PessimisticLock shown in red consumes the most time during SQL execution, and the execution time is obviously longer than the total time of KV requests. This is caused by serious lock conflicts in write statements and frequent lock retries prolong `Retried execution time`. Currently, TiDB does not measure `Retried execution time`.

**Example 5: HTAP CH-Benchmark workload**

![HTAP](/media/performance/htap_tiflash_mpp.png)

- Database Time by SQL Type: Mainly are `SELECT` statements.
- Database Time by SQL Phase: Most time is consumed in the execute phase in green.
- SQL Execute Time Overview: The `tiflash_mpp` requests shown in purple consume the most time during SQL execution, followed by the KV requests, including the `Cop` requests in blue, and the `Prewrite` and `Commit` requests in green.
### TiDB key metrics and cluster resource utilization
