# Performance Overview dashboard metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-performance-overview-dashboard.md`
- Source Title: `Key Metrics on Performance Overview`
- Source Heading Path: `Key Metrics on Performance Overview | Key Metrics on Performance Overview > Performance Overview | Key Metrics on Performance Overview > Performance Overview > Database Time by SQL Type | Key Metrics on Performance Overview > Performance Overview > Database Time by SQL Phase | Key Metrics on Performance Overview > Performance Overview > SQL Execute Time Overview | Key Metrics on Performance Overview > Performance Overview > QPS | Key Metrics on Performance Overview > Performance Overview > CPS By Type | Key Metrics on Performance Overview > Performance Overview > Queries Using Plan Cache OPS | Key Metrics on Performance Overview > Performance Overview > KV/TSO Request OPS | Key Metrics on Performance Overview > Performance Overview > KV Request Time By Source | Key Metrics on Performance Overview > Performance Overview > TiDB CPU | Key Metrics on Performance Overview > Performance Overview > TiKV CPU/IO MBps | Key Metrics on Performance Overview > Performance Overview > Duration | Key Metrics on Performance Overview > Performance Overview > Connection Idle Duration | Key Metrics on Performance Overview > Performance Overview > Connection Count | Key Metrics on Performance Overview > Performance Overview > Parse Duration, Compile Duration, and Execute Duration | Key Metrics on Performance Overview > Performance Overview > Avg TiDB KV Request Duration | Key Metrics on Performance Overview > Performance Overview > Avg TiKV GRPC Duration | Key Metrics on Performance Overview > Performance Overview > PD TSO Wait/RPC Duration | Key Metrics on Performance Overview > Performance Overview > Storage Async Write Duration, Store Duration, and Apply Duration | Key Metrics on Performance Overview > Performance Overview > Append Log Duration, Commit Log Duration, and Apply Log Duration | Key Metrics on Performance Overview > Performance Overview > Interface of the Performance Overview panels`
- Source Line Ranges: `5-167`
- Source Scope: `shared`
- Primary Component: `dashboard`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `grafana`, `dashboard`, `metrics`, `qps`, `cps`, `plan cache`, `tso`, `kv requests`, `cpu`, `io`, `latency`, `connections`, `duration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0052_f63474db37`
- Source ID: `tidb-docs-8.1:grafana-performance-overview-dashboard.md#key-metrics-on-performance-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ebf4afb82f0894265a6ee14d7a186b92cc432985b8355f5cbe1447a0134c9194`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-performance-overview-dashboard#key-metrics-on-performance-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-performance-overview-dashboard.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving what the Grafana Performance Overview dashboard shows for TiDB, PD, and TiKV performance, including workload profile, latency breakdown, and key panel metric meanings.
- Retrieval Keywords: Performance Overview dashboard, Database Time by SQL Type, Database Time by SQL Phase, SQL Execute Time Overview, QPS, CPS By Type, Queries Using Plan Cache OPS, avg-hit, avg-miss, StmtExecute, KV/TSO Request OPS, tso - cmd, tso - request, KV Request Time By Source, external, internal, TiDB CPU, TiKV CPU/IO MBps, Duration, Connection Idle Duration, Connection Count, Parse Duration, Compile Duration, Execute Duration, Avg TiDB KV Request Duration, Avg TiKV GRPC Duration, PD TSO Wait/RPC Duration, Storage Async Write Duration, Store Duration, Apply Duration, Append Log Duration, Commit Log Duration, Apply Log Duration, database time, sql_type, get token, parse, compile, execute, tso_wait, tiflash_mpp, kv_get, kv_prewrite, kv_commit
- Follow-up Guidance: The source also states that the dashboard helps confirm whether the bottleneck of user response time is in the database and points to Performance Analysis and Tuning for details.
- Classification Note: This chunk is classified as observability for the dashboard component because it defines Grafana Performance Overview panels and explains the metrics used to diagnose TiDB, PD, and TiKV performance.

## Official Source Content

# Key Metrics on Performance Overview

If you use TiUP to deploy the TiDB cluster, the monitoring system (Prometheus & Grafana) is deployed at the same time. For more information, see [TiDB Monitoring Framework Overview](https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework).

The Grafana dashboard is divided into a series of sub dashboards which include PD, TiDB, TiKV, Node_exporter, Overview, and Performance Overview. A lot of metrics are there to help you diagnose.

The Performance Overview dashboard orchestrates the metrics of TiDB, PD, and TiKV, and presents each of them in the following sections:

- Overview: Database time and SQL execution time summary. By checking different colors in the overview, you can quickly identify the database workload profile and the performance bottleneck.

- Load profile: Key metrics and resource usage, including database QPS, connection information, the MySQL command types the application interacts with TiDB, database internal TSO and KV request OPS, and resource usage of the TiKV and TiDB.

- Top-down latency breakdown: Query latency versus connection idle time ratio, query latency breakdown, TSO/KV request latency during execution, breakdown of write latency within TiKV.

With the Performance Overview Dashboard, you can analyze performance efficiently, and confirm whether the bottleneck of user response time is in the database. If the bottleneck is in the database, you can identify the bottleneck inside the database, with database time overview, workload profile and SQL latency breakdown. For details, see [Performance Analysis and Tuning](https://docs.pingcap.com/tidb/stable/performance-tuning-methods).

The following sections illustrate the metrics on the Performance Overview dashboard.
## Performance Overview
### Database Time by SQL Type

- database time: Total database time per second
- sql_type: Database time consumed by each type of SQL statements per second
### Database Time by SQL Phase

- database time: Total database time per second
- get token/parse/compile/execute: Database time consumed in four SQL processing phases

The SQL execution phase is in green and other phases are in red on general. If non-green areas are large, it means much database time is consumed in other phases than the execution phase and further cause analysis is required.
### SQL Execute Time Overview

- execute time: Database time consumed during SQL execution per second
- tso_wait: Concurrent TSO waiting time per second during SQL execution
- kv request type: Time waiting for each KV request type per second during SQL execution. The total KV request wait time might exceed SQL execution time, because KV requests are concurrent.
- tiflash_mpp: Time of processing TiFlash requests per second during SQL execution.

Green metrics stand for common KV write requests (such as prewrite and commit), blue metrics stand for common read requests, purple metrics stand for TiFlash MPP requests, and metrics in other colors stand for unexpected situations which you need to pay attention to. For example, pessimistic lock KV requests are marked red and TSO waiting is marked dark brown.

If non-blue or non-green areas are large, it means there is a bottleneck during SQL execution. For example:

- If serious lock conflicts occur, the red area will take a large proportion.
- If excessive time is consumed in waiting TSO, the dark brown area will take a large proportion.
### QPS

Number of SQL statements executed per second in all TiDB instances, collected by type: such as `SELECT`, `INSERT`, and `UPDATE`
### CPS By Type

Number of commands processed by all TiDB instances per second based on type
### Queries Using Plan Cache OPS

- avg-hit: The number of queries using the execution plan cache per second for all TiDB instances
- avg-miss: The number of queries not using the execution plan cache per second for all TiDB instances

`avg-hit + avg-miss` is equal to `StmtExecute`, which is the number of all queries executed per second.
### KV/TSO Request OPS

- kv request total: Total number of KV requests per second in all TiDB instances
- kv request by type: Number of KV requests per second in all TiDB instances based on such types as `Get`, `Prewrite`, and `Commit`
- tso - cmd: Number of gRPC requests per second that TiDB sends to PD in all TiDB instances; each gRPC request contains a batch of TSO requests
- tso - request: Number of TSO requests per second in all TiDB instances

Generally, `tso - request` divided by `tso - cmd` is the average size of TSO request batches per second.
### KV Request Time By Source

- kv request total time: Total time of processing KV and TiFlash requests per second in all TiDB instances
- Each KV request and the corresponding request source form a stacked bar chart, in which `external` identifies normal business requests and `internal` identifies internal activity requests (such as DDL and auto analyze requests)
### TiDB CPU

- avg: Average CPU utilization across all TiDB instances
- delta: Maximum CPU utilization of all TiDB instances minus minimum CPU utilization of all TiDB instances
- max: Maximum CPU utilization across all TiDB instances
### TiKV CPU/IO MBps

- CPU-Avg: Average CPU utilization of all TiKV instances
- CPU-Delta: Maximum CPU utilization of all TiKV instances minus minimum CPU utilization of all TiKV instances
- CPU-MAX: Maximum CPU utilization among all TiKV instances
- IO-Avg: Average MBps of all TiKV instances
- IO-Delt: Maximum MBps of all TiKV instances minus minimum MBps of all TiKV instances
- IO-MAX: Maximum MBps of all TiKV instances
### Duration

- Duration: Execution time

    - The duration from receiving a request from the client to TiDB till TiDB executing the request and returning the result to the client. In general, client requests are sent in the form of SQL statements; however, this duration can include the execution time of commands such as `COM_PING`, `COM_SLEEP`, `COM_STMT_FETCH`, and `COM_SEND_LONG_DATA`.
    - TiDB supports Multi-Query, which means the client can send multiple SQL statements at one time, such as `select 1; select 1; select 1;`. In this case, the total execution time of this query includes the execution time of all SQL statements.

- avg: Average time to execute all requests
- 99: P99 duration to execute all requests
- avg by type: Average time to execute all requests in all TiDB instances, collected by type: `SELECT`, `INSERT`, and `UPDATE`
### Connection Idle Duration

Connection Idle Duration indicates the duration of a connection being idle.

- avg-in-txn: Average connection idle duration when the connection is within a transaction
- avg-not-in-txn: Average connection idle duration when the connection is not within a transaction
- 99-in-txn: P99 connection idle duration when the connection is within a transaction
### Connection Count

- total: Number of connections to all TiDB instances
- active connections: Number of active connections to all TiDB instances
- tidb-{node-number}-peer: Number of connections to each TiDB instance
- disconnection/s: Number of disconnections in a TiDB cluster
- 99-not-in-txn: P99 connection idle duration when the connection is not within a transaction
### Parse Duration, Compile Duration, and Execute Duration

- Parse Duration: Time consumed in parsing SQL statements
- Compile Duration: Time consumed in compiling the parsed SQL AST to execution plans
- Execution Duration: Time consumed in executing execution plans of SQL statements

All these three metrics include the average duration and the 99th percentile duration in all TiDB instances.
### Avg TiDB KV Request Duration

Average time consumed in executing KV requests in all TiDB instances based on the type, including `Get`, `Prewrite`, and `Commit`.
### Avg TiKV GRPC Duration

Average time consumed in executing gRPC requests in all TiKV instances based on the type, including `kv_get`, `kv_prewrite`, and `kv_commit`.
### PD TSO Wait/RPC Duration

- wait - avg: Average duration of waiting for PD to return TSO in all TiDB instances
- rpc - avg: Average duration from the time that TiDB sends gRPC requests to PD to get TSO to the time that TiDB receives TSO in all TiDB instances
- wait - 99: P99 duration of waiting for PD to return TSO in all TiDB instances
- rpc - 99: P99 duration from the time that TiDB sends gRPC requests to PD to get TSO to the time that TiDB receives TSO in all TiDB instances
### Storage Async Write Duration, Store Duration, and Apply Duration

- Storage Async Write Duration: Time consumed in asynchronous write
- Store Duration: Time consumed in store loop during asynchronously write
- Apply Duration: Time consumed in apply loop during asynchronously write

All these three metrics include the average duration and P99 duration in all TiKV instances.

Average storage async write duration = Average store duration + Average apply duration
### Append Log Duration, Commit Log Duration, and Apply Log Duration

- Append Log Duration: Time consumed by Raft to append logs
- Commit Log Duration: Time consumed by Raft to commit logs
- Apply Log Duration: Time consumed by Raft to apply logs

All these three metrics include the average duration and P99 duration in all TiKV instances.
### Interface of the Performance Overview panels

![performance overview](/media/performance/grafana_performance_overview.png)
