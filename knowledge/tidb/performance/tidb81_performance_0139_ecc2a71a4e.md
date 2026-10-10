# Performance tuning process and iterative workflow

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-tuning-overview.md`
- Source Title: `Performance Tuning Overview`
- Source Heading Path: `TiDB Performance Tuning Overview > Performance tuning process | TiDB Performance Tuning Overview > Performance tuning process > Step 1. Define a tuning objective | TiDB Performance Tuning Overview > Performance tuning process > Step 2. Establish a performance baseline | TiDB Performance Tuning Overview > Performance tuning process > Step 3. Identify bottlenecks in user response time | TiDB Performance Tuning Overview > Performance tuning process > Step 4. Propose tuning solutions, and evaluate the benefits, risks, and costs of each solution | TiDB Performance Tuning Overview > Performance tuning process > Step 5. Implement tuning solutions | TiDB Performance Tuning Overview > Performance tuning process > Step 6. Evaluate tuning results`
- Source Line Ranges: `55-128`
- Source Scope: `all`
- Primary Component: `shared`
- Related Components: `dashboard`, `tidb`
- Topic Tags: `tuning-objective`, `performance-baseline`, `bottleneck-analysis`, `slow-query`, `top-sql`, `continuous-profiling`, `traffic-visualizer`, `prometheus`, `capacity-planning`, `regression-validation`, `risk-evaluation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0139_ecc2a71a4e`
- Source ID: `tidb-docs-8.1:performance-tuning-overview.md#performance-tuning-process`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b9bc458b9db0989d3a8dbca3bda4f08fce8e56c4018ad9b8a6341f41fdd8e759`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-tuning-overview#performance-tuning-process
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-tuning-overview.md

## Retrieval Guidance

- Use When: Use this chunk when describing the overall TiDB performance tuning workflow, including setting objectives, building a baseline, identifying bottlenecks, evaluating solutions, implementing changes, and reviewing results iteratively.
- Retrieval Keywords: performance tuning process, Define a tuning objective, Establish a performance baseline, Identify bottlenecks in user response time, Propose tuning solutions, Implement tuning solutions, Evaluate tuning results, slow query logs, Top SQL, Continuous Performance Profiling, traffic visualizer, Prometheus, Amdahl's Law, regression, test and staging environments, capacity planning
- Follow-up Guidance: It states that you usually repeat Step 2 to Step 6 multiple times and can use tools such as slow query logs, Top SQL, Continuous Performance Profiling, traffic visualizer, and Prometheus data when establishing and comparing the baseline.
- Classification Note: This is classified as performance because the content presents the official end-to-end tuning methodology and the related diagnostic data and tools for performance analysis.

## Official Source Content

## Performance tuning process

The performance tuning process consists of the following 6 steps:

1. Define a tuning objective.
2. Establish a performance baseline.
3. Identify bottlenecks in user response time.
4. Propose tuning solutions, and evaluate the benefits, risks, and costs of each solution.
5. Implement tuning solutions.
6. Evaluate tuning results.

To achieve the tuning objective of a performance tuning project, you usually need to repeat Step 2 to Step 6 multiple times.
### Step 1. Define a tuning objective

For different types of systems, tuning objectives are different too. For example, for a financial core OLTP system, the tuning objective might be to reduce the long-tail latency of transactions; for a financial settlement system, the tuning objective might be to make better use of hardware resources and reduce the time of batch settlement tasks.

A good tuning objective should be easily quantifiable. For example:

- Good tuning objective: The p99 latency for transfer transactions needs to be less than 200 ms during peak business hours of 9 am to 10 am.
- Poor tuning objective: The system is too slow to respond so it needs to be optimized.

Defining a clear tuning objective helps guide the subsequent performance tuning steps.
### Step 2. Establish a performance baseline

To tune performance efficiently, you need to capture the current performance data to establish a performance baseline. The performance data to be captured typically includes the following:

- Mean and long-tail values of user response time, and throughput of your application
- Database performance data such as database time, query latency, and QPS

    TiDB measures and stores performance data thoroughly in different dimensions, such as [slow query logs](https://docs.pingcap.com/tidb/stable/identify-slow-queries), [Top SQL](https://docs.pingcap.com/tidb/stable/dashboard/top-sql), [Continuous Performance Profiling](https://docs.pingcap.com/tidb/stable/dashboard/continuous-profiling), and [traffic visualizer](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-key-visualizer). In addition, you can perform historical backtracking and comparison of the timing metrics data stored in Prometheus.

- Resource utilization, including resources such as CPU, IO, and network
- Configuration information, such as application configurations, database configurations, and operating system configurations
### Step 3. Identify bottlenecks in user response time

Identify or speculate on bottlenecks in user response times based on data from the performance baseline.

Applications usually do not measure and record the full chain of user requests, so you cannot effectively break down user response time from top to bottom through the application.

In contrast, databases have a complete record of performance metrics such as query latency and throughput. Based on database time, you can determine if the bottleneck in user response time is in a database.

- If the bottleneck is not in databases, you need to rely on the resource utilization collected outside databases or profile the application to identify the bottleneck outside databases. Common scenarios include insufficient resources of an application or proxy server, and insufficient usage of hardware resources caused by serial points in an application.
- If bottlenecks are in databases, you can analyze and diagnose the database performances using comprehensive tuning tools. Common scenarios include the presence of slow SQL, unreasonable usage of a database by an application, and the presence of read and write hotspots in databases.

For more information about the analysis and diagnostic methods and tools, see [Performance Analysis and Tuning](https://docs.pingcap.com/tidb/stable/performance-tuning-methods).
### Step 4. Propose tuning solutions, and evaluate the benefits, risks, and costs of each solution

After identifying the bottleneck of a system through performance analysis, you can propose a tuning solution that is cost-effective, has low risks, and provides the maximum benefit based on the actual situation.

According to [Amdahl's Law](https://en.wikipedia.org/wiki/Amdahl%27s_law), the maximum gain from performance tuning depends on the percentage of the optimized part in the overall system. Therefore, you need to identify the system bottlenecks and the corresponding percentage based on the performance data, and then predict the gains after the bottleneck is resolved or optimized.

Note that even if a solution can bring the greatest potential benefits by tuning the largest bottleneck, you still need to evaluate the risks and costs of this solution. For example:

- The most straightforward tuning objective solution for a resource-overloaded system is to expand its capacity, but in practice, the expansion solution might be too costly to be adopted.
- When a slow query in a business module causes a slow response of the entire module, upgrading to a new version of the database can solve the slow query issue, but it might also affect modules that did not have this issue. Therefore, this solution might have a potentially high risk. A low-risk solution is to skip the database version upgrade and rewrite the existing slow queries for the current database version.
### Step 5. Implement tuning solutions

Considering the benefits, risks, and costs, choose one or more tuning solutions for implementation. In the implementation process, you need to make thorough preparation for changes to the production system and record the changes in detail.

To mitigate risks and validate the benefits of a tuning solution, it is recommended that you perform validation and complete regression of changes in both test and staging environments. For example, if the selected tuning solution of a slow query is to create a new index to optimize the query access path, you need to ensure that the new index does not introduce any obvious write hotspots to the existing data insertion workload and slows down other modules.
### Step 6. Evaluate tuning results

After applying the tuning solution, you need to evaluate the results:

- If the tuning objective is reached, the entire tuning project is completed successfully.
- If the tuning objective is not reached, you need to repeat Step 2 to Step 6 in this document until the tuning objective is reached.

After reaching your tuning objectives, you might need to further plan your system capacity to meet your business growth.
