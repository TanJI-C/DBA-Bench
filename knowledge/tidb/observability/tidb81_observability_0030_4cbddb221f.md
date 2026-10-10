# Latency breakdown metrics across TiDB, PD, and TiKV

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-monitoring.md`
- Source Title: `TiDB Dashboard Monitoring Page`
- Source Heading Path: `TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > Duration | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > Connection Idle Duration | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > Parse Duration, Compile Duration, and Execute Duration | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > Avg TiDB KV Request Duration | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > Avg TiKV GRPC Duration | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > PD TSO Wait/RPC Duration | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > Storage Async Write Duration, Store Duration, and Apply Duration | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > Append Log Duration, Commit Log Duration, and Apply Log Duration`
- Source Line Ranges: `99-158`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `pd`, `tikv`, `sql`
- Topic Tags: `duration`, `idle-duration`, `parse`, `compile`, `execute`, `kv-latency`, `grpc`, `tso-latency`, `async-write`, `raft-log`, `p99`, `latency-breakdown`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0030_4cbddb221f`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-monitoring.md#duration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `38e8f7a9b454f1a30bf33e3ee9dc7cbebc1cca5d5a7e6e6effa853a9b521b403`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-monitoring#duration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-monitoring.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs definitions for latency breakdown metrics on the Performance Overview dashboard across request duration, idle duration, TiDB KV, PD TSO, TiKV async write, or Raft log timings.
- Retrieval Keywords: Duration, Connection Idle Duration, Parse Duration, Compile Duration, Execute Duration, Avg TiDB KV Request Duration, Avg TiKV GRPC Duration, PD TSO Wait/RPC Duration, Storage Async Write Duration, Store Duration, Apply Duration, Append Log Duration, Commit Log Duration, Apply Log Duration, P99 duration, wait - avg, rpc - 99, kv_get, kv_prewrite, kv_commit
- Follow-up Guidance: If the user also needs the workload and throughput metrics that accompany these latency charts, refer to the Performance Overview sections for Database Time, QPS, KV/TSO Request OPS, and resource usage.
- Classification Note: The content is classified as observability for the dashboard component because it explains the latency-oriented monitoring metrics presented for TiDB, PD, and TiKV on the Performance Overview dashboard.

## Official Source Content

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

- wait - avg: Average time in waiting for PD to return TSO in all TiDB instances
- rpc - avg: Average time from sending TSO requests to PD to receiving TSO in all TiDB instances
- wait - 99: P99 time in waiting for PD to return TSO in all TiDB instances
- rpc - 99: P99 time from sending TSO requests to PD to receiving TSO in all TiDB instances
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
