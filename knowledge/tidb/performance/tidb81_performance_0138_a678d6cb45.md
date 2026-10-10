# Performance concepts: user response time, database time, and throughput

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-tuning-overview.md`
- Source Title: `Performance Tuning Overview`
- Source Heading Path: `TiDB Performance Tuning Overview | TiDB Performance Tuning Overview > User response time and database time | TiDB Performance Tuning Overview > User response time and database time > User response time | TiDB Performance Tuning Overview > User response time and database time > Database time | TiDB Performance Tuning Overview > Relationship between user response time and system throughput`
- Source Line Ranges: `5-54`
- Source Scope: `all`
- Primary Component: `shared`
- Related Components: `tidb`
- Topic Tags: `user-response-time`, `database-time`, `throughput`, `latency`, `qps`, `tps`, `active-sessions`, `resource-utilization`, `queueing-delay`, `coherency-delay`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0138_a678d6cb45`
- Source ID: `tidb-docs-8.1:performance-tuning-overview.md#tidb-performance-tuning-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ed10acc51e79c73c53071ca8789c7de6b4560b93c411f75888aec119f562b72d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-tuning-overview#tidb-performance-tuning-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-tuning-overview.md

## Retrieval Guidance

- Use When: Use this chunk when explaining TiDB performance concepts such as user response time, database time, throughput, and how latency changes as resource utilization and queueing increase.
- Retrieval Keywords: user response time, database time, throughput, TPS, QPS, avg latency, avg active connections, active sessions, tidb_server_tokens, Service time + Queuing delay + Coherency delay, queuing delay, coherency delay, resource utilization, CPU utilization 65%, OLTP loads
- Follow-up Guidance: It also gives formulas for total user response time in ΔT and for database time using QPS × avg latency × ΔT, avg active connections × ΔT, or rate(tidb_server_tokens) × ΔT.
- Classification Note: This is classified as performance because the content defines latency, throughput, database time, active sessions, and queueing behavior used in performance tuning.

## Official Source Content

# TiDB Performance Tuning Overview

This document introduces the basic concepts of performance tuning, such as user response time, throughput, and database time, and also provides a general process for performance tuning.
## User response time and database time
### User response time

User response time indicates how long an application takes to return the results of a request to users. As you can see from the following sequential timing diagram, the time of a typical user request contains the following:

- The network latency between the user and the application
- The processing time of the application
- The network latency during the interaction between the application and the database
- The service time of the database

The user response time is affected by various subsystems on the request chain, such as network latency and bandwidth, number and request types of concurrent users, and resource usage of server CPU and I/O. To optimize the entire system effectively, you need to first identify the bottlenecks in user response time.

To get a total user response time within a specified time range (`ΔT`), you can use the following formula:

Total user response time in `ΔT` = Average TPS (Transactions Per Second) x Average user response time x `ΔT`.

![user_response_time](/media/performance/user_response_time_en.png)
### Database time

Database time indicates the total service time provided by a database. The database time in `ΔT` is the sum of the time that a database takes to process all application requests concurrently.

To get the database time, you can use any of the following methods:

- Method 1: Multiply the average query latency by QPS and by ΔT, that is, `DB Time in ΔT = QPS × avg latency × ΔT`
- Method 2: Multiply the average number of active sessions by ΔT, that is, `DB Time in ΔT  = avg active connections × ΔT`
- Method 3: Calculate the time based on the TiDB internal Prometheus metric `tidb_server_tokens`, that is. `ΔT DB Time = rate(tidb_server_tokens) × ΔT`
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
