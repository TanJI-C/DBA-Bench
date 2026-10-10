# Overview and load profile metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-monitoring.md`
- Source Title: `TiDB Dashboard Monitoring Page`
- Source Heading Path: `TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > Database Time by SQL Type | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > Database Time by SQL Phase | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > SQL Execute Time Overview | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > QPS | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > CPS By Type | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > Queries Using Plan Cache OPS | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > KV/TSO Request OPS | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > Connection Count | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > TiDB CPU | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview > TiKV CPU/IO MBps`
- Source Line Ranges: `32-98`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `database-time`, `sql-phase`, `execution-time`, `qps`, `cps`, `plan-cache`, `kv-requests`, `tso`, `connections`, `cpu`, `io`, `load-profile`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0029_668d7bf696`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-monitoring.md#database-time-by-sql-type`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1be8a50a99fbb52c0d27b07f139d41654813d88240756b3c2516a702d6ac019b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-monitoring#database-time-by-sql-type
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-monitoring.md

## Retrieval Guidance

- Use When: Use this chunk when the user is interpreting Performance Overview metrics for database time, SQL phases, QPS, connections, plan cache, KV or TSO request rates, or TiDB and TiKV resource usage.
- Retrieval Keywords: Database Time by SQL Type, Database Time by SQL Phase, SQL Execute Time Overview, QPS, CPS By Type, Queries Using Plan Cache OPS, KV/TSO Request OPS, Connection Count, TiDB CPU, TiKV CPU/IO MBps, database time, sql_type, get token, parse, compile, execute, tso_wait, kv request total, kv request by type, tso - cmd, tso - request, active connections, CPU-Avg, IO-MAX
- Follow-up Guidance: If the user is investigating latency rather than request counts or resource usage, the next relevant section is the latency breakdown metrics such as Duration, PD TSO Wait/RPC Duration, and TiKV write or Raft log durations.
- Classification Note: The content is classified as observability for the dashboard component because it defines the Performance Overview metrics used to inspect workload profile, SQL processing phases, request rates, and CPU or IO utilization.

## Official Source Content

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

Green metrics stand for common KV write requests (such as prewrite and commit), blue metrics stand for common read requests, and metrics in other colors stand for unexpected situations which you need to pay attention to. For example, pessimistic lock KV requests are marked red and TSO waiting is marked dark brown.

If non-blue or non-green areas are large, it means there is a bottleneck during SQL execution. For example:

- If serious lock conflicts occur, the red area will take a large proportion.
- If excessive time is consumed in waiting TSO, the dark brown area will take a large proportion.
### QPS

Number of SQL statements executed per second in all TiDB instances, collected by type: such as `SELECT`, `INSERT`, and `UPDATE`
### CPS By Type

Number of commands processed by all TiDB instances per second based on type
### Queries Using Plan Cache OPS

Number of queries using plan cache per second in all TiDB instances
### KV/TSO Request OPS

- kv request total: Total number of KV requests per second in all TiDB instances
- kv request by type: Number of KV requests per second in all TiDB instances based on such types as `Get`, `Prewrite`, and `Commit`
- tso - cmd: Number of gRPC requests per second that TiDB sends to PD in all TiDB instances; each gRPC request contains a batch of TSO requests
- tso - request: Number of TSO requests per second in all TiDB instances

Generally, `tso - request` divided by `tso - cmd` is the average size of TSO request batches per second.
### Connection Count

- total: Number of connections to all TiDB instances
- active connections: Number of active connections to all TiDB instances
- Number of connections to each TiDB instance
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
