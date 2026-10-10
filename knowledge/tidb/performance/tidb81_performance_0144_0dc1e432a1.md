# OLTP tuning scenario comparison summary

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-tuning-practices.md`
- Source Title: `Performance Tuning Practices for OLTP Scenarios`
- Source Heading Path: `Performance Tuning Practices for OLTP Scenarios > Summary`
- Source Line Ranges: `410-439`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `pd`, `tikv`, `sql`
- Topic Tags: `summary`, `scenario-comparison`, `prepared-statements`, `plan-cache`, `rc-read`, `small-table-cache`, `top-sql`, `continuous-profiling`, `performance-overview`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0144_0dc1e432a1`
- Source ID: `tidb-docs-8.1:performance-tuning-practices.md#summary`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9a749f131eec02212f017b127c28d0cb8a6bc5f380147c60d0399d56c86f7f68`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-tuning-practices#summary
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-tuning-practices.md

## Retrieval Guidance

- Use When: Use this chunk when comparing the seven OLTP tuning scenarios, including Prepared Statement usage, execution plan cache, RC Read, small table cache, and the role of TiDB Dashboard or Performance Overview in performance analysis.
- Retrieval Keywords: Summary, Scenario 2, Scenario 5, Scenario 7, Prepared Statement interface, Query interface, execution plan cache, RC Read, small table cache, useServerPrepStmts=true, cachePrepStmts=true, prepStmtCacheSize=1000, prepStmtCacheSqlLimit=20480, useConfigs=maxPerformance, Top SQL, Continuous Profiling, Performance Overview Dashboard, query duration, QPS
- Follow-up Guidance: The chunk includes JDBC connection parameters for the Prepared Statement interface and names Top SQL, Continuous Profiling, and Performance Overview Dashboard as analysis tools.
- Classification Note: This is classified as performance content because it summarizes scenario-level latency, QPS, CPU utilization, and tuning features used for OLTP performance analysis and comparison.

## Official Source Content

## Summary

The following table lists the performance of seven different scenarios.

| Metrics | Scenario 1 | Scenario 2 | Scenario 3 | Scenario 4 | Scenario 5 | Scenario 6 | Scenario 7 | Comparing Scenario 5 with Scenario 2 (%) | Comparing Scenario 7 with Scenario 3 (%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |  --- |
| query duration  | 479μs | 1120μs | 528μs | 426μs |690μs  | 533μs | 313μs | -38% | -41% |
| QPS            | 56.3k |  24.2k | 19.7k | 22.1k | 30.9k | 34.9k | 40.9k | +28% | +108% |

In these scenarios, Scenario 2 is a common scenario where applications use the Query interface, and Scenario 5 is an ideal scenario where applications use the Prepared Statement interface.

- Comparing Scenario 5 with Scenario 2, you can see that by using best practices for Java application development and caching Prepared Statement objects on the client side, each SQL statement requires only one command and database interaction to hit the execution plan cache, which results in a 38% drop in query latency and a 28% increase in QPS, while the average TiDB CPU utilization drops from 936% to 577%.
- Comparing Scenario 7 with Scenario 3, you can see that with the latest TiDB optimization features such as RC Read and small table cache on top of Scenario 5, latency is reduced by 41% and QPS is increased by 108%, while the average TiDB CPU utilization drops from 936% to 478%.

By comparing the performance of each scenario, we can draw the following conclusions:

- The execution plan cache of TiDB plays a critical role in the OLTP performance tuning. The RC Read and small table cache features introduced from v6.0.0 also play an important role in the further performance tuning of this workload.
- TiDB is compatible with different commands of the MySQL protocol. When using the Prepared Statement interface and setting the following JDBC connection parameters, the application can achieve its best performance:

    ```
    useServerPrepStmts=true&cachePrepStmts=true&prepStmtCacheSize=1000&prepStmtCacheSqlLimit=20480&useConfigs=maxPerformance
    ```

- It is recommended that you use TiDB Dashboard (for example, the Top SQL feature and Continuous Profiling feature) and Performance Overview dashboard for performance analysis and tuning.

    - With the [Top SQL](https://docs.pingcap.com/tidb/stable/dashboard/top-sql) feature, you can visually monitor and explore the CPU consumption of each SQL statement in your database during execution to troubleshoot database performance issues.
    - With [Continuous Profiling](https://docs.pingcap.com/tidb/stable/dashboard/continuous-profiling), you can continuously collect performance data from each instance of TiDB, TiKV, and PD. When applications use different interfaces to interact with TiDB, the difference in the CPU consumption of TiDB is huge.
    - With [Performance Overview Dashboard](https://docs.pingcap.com/tidb/stable/grafana-performance-overview-dashboard), you can get an overview of database time and SQL execution time breakdown information. You can analyze and diagnose performance based on database time to determine whether the performance bottleneck of the entire system is in TiDB or not. If the bottleneck is in TiDB, you can use the database time and latency breakdowns, along with load profile and resource usage, to identify performance bottlenecks within TiDB and tune the performance accordingly.

With a combination usage of these features, you can analyze and tune performance for real-world applications efficiently.
