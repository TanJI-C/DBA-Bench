# Performance analysis concepts and troubleshooting entry points

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-tune-performance-overview.md`
- Source Title: `Overview for Analyzing and Tuning Performance`
- Source Heading Path: `Overview for Analyzing and Tuning Performance | Overview for Analyzing and Tuning Performance > User response time | Overview for Analyzing and Tuning Performance > Relationship between user response time and system throughput | Overview for Analyzing and Tuning Performance > Troubleshoot bottlenecks in user response time`
- Source Line Ranges: `5-57`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`, `sql`, `tidb`
- Topic Tags: `user-response-time`, `throughput`, `service-time`, `queueing-delay`, `coherency-delay`, `diagnosis`, `metrics`, `sql-tuning`, `key-visualizer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0204_9fb58e4bb1`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-tune-performance-overview.md#overview-for-analyzing-and-tuning-performance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `821d13b62e6a493f78c29eb970f6bf1f67fc2b43101408f86438c720efb9ae34`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-tune-performance-overview#overview-for-analyzing-and-tuning-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-tune-performance-overview.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB Cloud overview of user response time, throughput, service time, queuing delay, coherency delay, and the main console entry points for performance troubleshooting.
- Retrieval Keywords: user response time, system throughput, service time, queuing delay, coherency delay, Total user response time in ΔT, Average TPS, Diagnosis, SQL Statement, execution plan, SQL Tuning Overview, Key Visualizer, Metrics, request units, used storage size, query per second, average query duration, TiDB Cloud Support
- Follow-up Guidance: It points to Diagnosis, SQL Statement, Key Visualizer, Metrics, and SQL Tuning Overview for further analysis, and notes that additional metrics can be requested from TiDB Cloud Support.
- Classification Note: This is classified as performance for TiDB Cloud because the content defines latency and throughput concepts and identifies built-in troubleshooting pages and metrics for analyzing SQL performance.

## Official Source Content

# Overview for Analyzing and Tuning Performance

This document describes steps to help you analyze and tune SQL performance in TiDB Cloud.
## User response time

User response time indicates how long an application takes to return the results of a request to users. As you can see from the following sequential timing diagram, the time of a typical user request contains the following:

- The network latency between the user and the application
- The processing time of the application
- The network latency during the interaction between the application and the database
- The service time of the database

The user response time is affected by various subsystems on the request chain, such as network latency and bandwidth, number and request types of concurrent users, and resource usage of server CPU and I/O. To optimize the entire system effectively, you need to first identify the bottlenecks in user response time.

To get a total user response time within a specified time range (`ΔT`), you can use the following formula:

Total user response time in `ΔT` = Average TPS (Transactions Per Second) x Average user response time x `ΔT`.

![user_response_time](/media/performance/user_response_time_en.png)
## Relationship between user response time and system throughput

User response time consists of service time, queuing time, and concurrent waiting time to complete a user request.

```
User Response time = Service time + Queuing delay + Coherency delay
```

- Service time: the time a system consumes on certain resources when processing a request, for example, the CPU time that a database consumes to complete a SQL request.
- Queuing delay: the time a system waits in a queue for service of certain resources when processing a request.
- Coherency delay: the time a system communicates and collaborates with other concurrent tasks, so that it can access shared resources when processing a request.

System throughput indicates the number of requests that can be completed by a system per second. User response time and throughput are usually inverse of each other. When the throughput increases, the system resource utilization and the queuing latency for a requested service increase accordingly. Once resource utilization exceeds a certain inflection point, the queuing latency will increase dramatically.

For example, for a database system running OLTP loads, after its CPU utilization exceeds 65%, the CPU queueing scheduling latency increases significantly. This is because concurrent requests of a system are not completely independent, which means that these requests can collaborate and compete for shared resources. For example, requests from different users might perform mutually exclusive locking operations on the same data. When the resource utilization increases, the queuing and scheduling latency increases too, which causes that the shared resources cannot be released in time and in turn prolongs the waiting time for shared resources by other tasks.
## Troubleshoot bottlenecks in user response time

There are several pages in the TiDB Cloud console that help you troubleshoot user response time.

- [**Diagnosis**](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#view-the-diagnosis-page):

    - **SQL Statement** enables you to directly observe SQL execution on the page, and easily locate performance problems without querying the system tables. You can click a SQL statement to further view the execution plan of the query for troubleshooting and analysis. For more information about SQL performance tuning, see [SQL Tuning Overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sql-tuning-overview).
    - **Key Visualizer** helps you observe TiDB's data access patterns and data hotspots.

- [**Metrics**](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring#view-the-metrics-page): on this page, you can view metrics such as request units, used storage size, query per second, and average query duration.

To request additional metrics, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).

If you experience latency and performance issues, refer to the steps in the following sections for analysis and troubleshooting.
