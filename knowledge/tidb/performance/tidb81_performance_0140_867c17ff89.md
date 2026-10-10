# OLTP performance tuning scenarios 1-3 with JDBC, dashboard analysis, and plan cache behavior

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-tuning-practices.md`
- Source Title: `Performance Tuning Practices for OLTP Scenarios`
- Source Heading Path: `Performance Tuning Practices for OLTP Scenarios | Performance Tuning Practices for OLTP Scenarios > Environment description | Performance Tuning Practices for OLTP Scenarios > Scenario 1. Use the Query interface | Performance Tuning Practices for OLTP Scenarios > Scenario 1. Use the Query interface > Application configuration | Performance Tuning Practices for OLTP Scenarios > Scenario 1. Use the Query interface > Performance analysis | Performance Tuning Practices for OLTP Scenarios > Scenario 1. Use the Query interface > Performance analysis > TiDB Dashboard | Performance Tuning Practices for OLTP Scenarios > Scenario 1. Use the Query interface > Performance analysis > Performance Overview dashboard | Performance Tuning Practices for OLTP Scenarios > Scenario 1. Use the Query interface > Analysis conclusion | Performance Tuning Practices for OLTP Scenarios > Scenario 2. Use the maxPerformance configuration | Performance Tuning Practices for OLTP Scenarios > Scenario 2. Use the maxPerformance configuration > Application configuration | Performance Tuning Practices for OLTP Scenarios > Scenario 2. Use the maxPerformance configuration > Performance analysis | Performance Tuning Practices for OLTP Scenarios > Scenario 2. Use the maxPerformance configuration > Performance analysis > TiDB Dashboard | Performance Tuning Practices for OLTP Scenarios > Scenario 2. Use the maxPerformance configuration > Performance analysis > Performance Overview dashboard | Performance Tuning Practices for OLTP Scenarios > Scenario 2. Use the maxPerformance configuration > Analysis conclusion | Performance Tuning Practices for OLTP Scenarios > Scenario 3. Use the Prepared Statement interface with execution plan caching not enabled | Performance Tuning Practices for OLTP Scenarios > Scenario 3. Use the Prepared Statement interface with execution plan caching not enabled > Application configuration | Performance Tuning Practices for OLTP Scenarios > Scenario 3. Use the Prepared Statement interface with execution plan caching not enabled > Performance analysis | Performance Tuning Practices for OLTP Scenarios > Scenario 3. Use the Prepared Statement interface with execution plan caching not enabled > Performance analysis > TiDB Dashboard | Performance Tuning Practices for OLTP Scenarios > Scenario 3. Use the Prepared Statement interface with execution plan caching not enabled > Performance analysis > Performance Overview dashboard`
- Source Line Ranges: `5-186`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `sql`, `tikv`
- Topic Tags: `oltp`, `jdbc`, `query-interface`, `prepared-statements`, `plan-cache`, `top-sql`, `continuous-profiling`, `performance-overview`, `cpu-usage`, `qps`, `compile`, `optimize`, `latency`, `read-committed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0140_867c17ff89`
- Source ID: `tidb-docs-8.1:performance-tuning-practices.md#performance-tuning-practices-for-oltp-scenarios`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4031528ec29e5201a62eac4f30e17dce42b86bb36c58f0a8ec5294eb525be7c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-tuning-practices#performance-tuning-practices-for-oltp-scenarios
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-tuning-practices.md

## Retrieval Guidance

- Use When: Use this chunk when analyzing OLTP performance differences across JDBC Query and Prepared Statement interfaces with TiDB Dashboard, Performance Overview, CPU usage, QPS, and execution plan cache behavior.
- Retrieval Keywords: useServerPrepStmts=false, useConfigs=maxPerformance, useServerPrepStmts=true, SELECT @@session.tx_isolation, select @@session.transaction_read_only, Top SQL, Continuous Profiling, Performance Overview dashboard, Query interface, Prepared Statement interface, execution plan cache, Queries Using Plan Cache OPS, Compile, Optimize, CompileExecutePreparedStmt, StmtPrepare, StmtExecute, StmtClose, read committed, avg QPS, TiDB CPU utilization, TiKV CPU utilization
- Follow-up Guidance: The source continues by comparing these scenarios and explaining that using the Prepared Statement interface can use the execution plan cache of TiDB to reduce CPU consumption caused by execution plan compiling and decrease latency, while Scenario 3 shows the cache is not hit because `StmtClose` clears the execution plan cache in internal processing.
- Classification Note: This chunk is classified as performance content for TiDB because it compares OLTP runtime scenarios using JDBC settings and dashboard evidence such as QPS, latency, CPU utilization, SQL phases, and plan cache hit behavior.

## Official Source Content

# Performance Tuning Practices for OLTP Scenarios

TiDB provides comprehensive performance diagnostics and analysis features, such as [Top SQL](https://docs.pingcap.com/tidb/stable/dashboard/top-sql) and [Continuous Profiling](https://docs.pingcap.com/tidb/stable/dashboard/continuous-profiling) features on the TiDB Dashboard, and TiDB [Performance Overview Dashboard](https://docs.pingcap.com/tidb/stable/grafana-performance-overview-dashboard).

This document describes how to use these features together to analyze and compare the performance of the same OLTP workload in seven different runtime scenarios, which demonstrates a performance tuning process to help you analyze and tune TiDB performance efficiently.

> **Note:**
>
> [Top SQL](https://docs.pingcap.com/tidb/stable/dashboard/top-sql) and [Continuous Profiling](https://docs.pingcap.com/tidb/stable/dashboard/continuous-profiling) are not enabled by default. You need to enable them in advance.

By running the same application with different JDBC configurations in these scenarios, this document shows you how the overall system performance is affected by different interactions between applications and databases, so that you can apply [Best Practices for Developing Java Applications with TiDB](https://docs.pingcap.com/tidb/stable/develop/java-app-best-practices) for better performance.
## Environment description

This document takes a core banking OLTP workload for demonstration. The configurations of the simulation environment are as follows:

- Application development language for the workload: JAVA
- SQL statements used in business: 200 statements in total, 90% of which are SELECT statements. It is a typical read-heavy OLTP workload.
- Tables used in transactions: 60 tables in total. 12 tables involve update operations, and the rest 48 tables are read-only.
- Isolation level used by the application: `read committed`.
- TiDB cluster configuration: 3 TiDB nodes and 3 TiKV nodes, with 16 CPUs allocated to each node.
- Client server configuration: 36 CPUs.
## Scenario 1. Use the Query interface
### Application configuration

The application uses the following JDBC configuration to connect to the database through the Query interface.

```
useServerPrepStmts=false
```
### Performance analysis
#### TiDB Dashboard

From the Top SQL page in the TiDB Dashboard below, you can see that the non-business SQL type `SELECT @@session.tx_isolation` consumes the most resources. Although TiDB processes these types of SQL statements quickly, these types of SQL statements have the highest number of executions that result in the highest overall CPU time consumption.

![dashboard-for-query-interface](/media/performance/case1.png)

From the following flame chart of TiDB, you can see that the CPU consumption of functions such as `Compile` and `Optimize` is significant during the SQL execution. Because the application uses the Query interface, TiDB cannot use the execution plan cache. TiDB needs to compile and generate an execution plan for each SQL statement.

![flame-graph-for-query-interface](/media/performance/7.1.png)

- ExecuteStmt cpu = 38% cpu time = 23.84s
- Compile cpu = 27%  cpu time = 17.17s
- Optimize cpu = 26% cpu time = 16.41s
#### Performance Overview dashboard

Check the database time overview and QPS in the following Performance Overview dashboard.

![performance-overview-1-for-query-interface](/media/performance/j-1.png)

- Database Time by SQL Type: the `Select` statement type takes most of the time.
- Database Time by SQL Phase: the `execute` and `compile` phases take most of the time.
- SQL Execute Time Overview: `Get`, `Cop`, and `tso wait` take most of the time.
- CPS By Type: only the `Query` command is used.
- Queries Using Plan Cache OPS: no data indicates that the execution plan cache is not hit.
- In the query duration, the latency of `execute` and `compile` takes the highest percentage.
- avg QPS = 56.8k

Check the resource consumption of the cluster: the average utilization of TiDB CPU is 925%, the average utilization of TiKV CPU is 201%, and the average throughput of TiKV IO is 18.7 MB/s. The resource consumption of TiDB is significantly higher.

![performance-overview-2-for-query-interface](/media/performance/5.png)
### Analysis conclusion

We need to eliminate these useless non-business SQL statements, which have a large number of executions and contribute to the high TiDB CPU usage.
## Scenario 2. Use the maxPerformance configuration
### Application configuration

The application adds a new parameter `useConfigs=maxPerformance` to the JDBC connection string in Scenario 1. This parameter can be used to eliminate the SQL statements sent from JDBC to the database (for example, `select @@session.transaction_read_only`). The full configuration is as follows:

```
useServerPrepStmts=false&useConfigs=maxPerformance
```
### Performance analysis
#### TiDB Dashboard

From the Top SQL page in the TiDB Dashboard below, you can see that `SELECT @@session.tx_isolation`, which consumed the most resources, has disappeared.

![dashboard-for-maxPerformance](/media/performance/case2.png)

From the following flame chart of TiDB, you can see that the CPU consumption of functions such as `Compile` and `Optimize` is still significant during the SQL execution.

![flame-graph-for-maxPerformance](/media/performance/20220507-145257.jpg)

- ExecuteStmt cpu = 43% cpu time =35.84s
- Compile cpu = 31% cpu time =25.61s
- Optimize cpu = 30% cpu time = 24.74s
#### Performance Overview dashboard

The data of the database time overview and QPS is as follows:

![performance-overview-1-for-maxPerformance](/media/performance/j-2.png)

- Database Time by SQL Type: the `Select` statement type takes most of the time.
- Database Time by SQL Phase: the `execute` and `compile` phases take most of the time.
- SQL Execute Time Overview: `Get`, `Cop`, `Prewrite`, and `tso wait` take most of the time.
- In the database time, the latency of `execute` and `compile` takes the highest percentage.
- CPS By Type: only the `Query` command is used.
- avg QPS = 24.2k (from 56.3k to 24.2k)
- The execution plan cache is not hit.

From Scenario 1 to Scenario 2, the average TiDB CPU utilization drops from 925% to 874%, and the average TiKV CPU utilization increases from 201% to about 250%.

![performance-overview-2-for-maxPerformance](/media/performance/9.1.1.png)

The changes in key latency metrics are as follows:

![performance-overview-3-for-maxPerformance](/media/performance/9.2.2.png)

- avg query duration = 1.12ms (from 479μs to 1.12ms)
- avg parse duration = 84.7μs (from 37.2μs to 84.7μs)
- avg compile duration = 370μs (from 166μs to 370μs)
- avg execution duration = 626μs (from 251μs to 626μs)
### Analysis conclusion

Compared with Scenario 1, the QPS of Scenario 2 has significantly decreased. The average query duration and average `parse`, `compile`, and `execute` durations have significantly increased. This is because SQL statements such as `select @@session.transaction_read_only` in Scenario 1, which are executed many times and have fast processing time, lower the average performance data. After Scenario 2 blocks such statements, only business-related SQL statements remain, so the average duration increases.

When the application uses the Query interface, TiDB cannot use the execution plan cache, which results in TiDB consuming high resources to compile execution plans. In this case, it is recommended that you use the Prepared Statement interface, which uses the execution plan cache of TiDB to reduce the TiDB CPU consumption caused by execution plan compiling and decrease the latency.
## Scenario 3. Use the Prepared Statement interface with execution plan caching not enabled
### Application configuration

The application uses the following connection configuration. Compared with Scenario 2, the value of the JDBC parameter `useServerPrepStmts` is modified to `true`, indicating that the Prepared Statement interface is enabled.

```
useServerPrepStmts=true&useConfigs=maxPerformance"
```
### Performance analysis
#### TiDB Dashboard

From the following flame chart of TiDB, you can see that the CPU consumption of `CompileExecutePreparedStmt` and `Optimize` is still significant after the Prepared Statement interface is enabled.

![flame-graph-for-PrepStmts](/media/performance/3.1.1.png)

- ExecutePreparedStmt cpu = 31%  cpu time = 23.10s
- preparedStmtExec cpu = 30% cpu time = 22.92s
- CompileExecutePreparedStmt cpu = 24% cpu time = 17.83s
- Optimize cpu = 23%  cpu time = 17.29s
#### Performance Overview dashboard

After the Prepared Statement interface is used, the data of database time overview and QPS is as follows:

![performance-overview-1-for-PrepStmts](/media/performance/j-3.png)

The QPS drops from 24.4k to 19.7k. From the Database Time Overview, you can see that the application uses three types of Prepared commands, and the `general` statement type (which includes the execution time of commands such as `StmtPrepare` and `StmtClose`) takes the second place in Database Time by SQL Type. This indicates that even when the Prepared Statement interface is used, the execution plan cache is not hit. The reason is that, when the `StmtClose` command is executed, TiDB clears the execution plan cache of SQL statements in the internal processing.

- Database Time by SQL Type: the `Select` statement type takes most of the time, followed by `general` statements.
- Database Time by SQL Phase: the `execute` and `compile` phases take most of the time.
- SQL Execute Time Overview: `Get`, `Cop`, `Prewrite`, and `tso wait` take most of the time.
- CPS By Type: 3 types of commands (`StmtPrepare`, `StmtExecute`, `StmtClose`) are used.
- avg QPS = 19.7k (from 24.4k to 19.7k)
- The execution plan cache is not hit.

The TiDB average CPU utilization increases from 874% to 936%.

![performance-overview-1-for-PrepStmts](/media/performance/3-2.png)

The key latency metrics are as follows:

![performance-overview-2-for-PrepStmts](/media/performance/3.4.png)

- avg query duration = 528μs (from 1.12ms to 528μs)
- avg parse duration = 14.9μs (from 84.7μs to 14.9μs)
- avg compile duration = 374μs (from 370μs to 374μs)
- avg execution duration = 649μs (from 626μs to 649μs)
