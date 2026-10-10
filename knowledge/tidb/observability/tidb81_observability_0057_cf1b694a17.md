# TiDB dashboard metrics for KV, PD, schema, DDL, GC, and TTL

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-tidb-dashboard.md`
- Source Title: `TiDB Monitoring Metrics`
- Source Heading Path: `TiDB Monitoring Metrics > Key metrics description > KV Request | TiDB Monitoring Metrics > Key metrics description > PD Client | TiDB Monitoring Metrics > Key metrics description > Schema Load | TiDB Monitoring Metrics > Key metrics description > DDL | TiDB Monitoring Metrics > Key metrics description > Statistics | TiDB Monitoring Metrics > Key metrics description > Owner | TiDB Monitoring Metrics > Key metrics description > Meta | TiDB Monitoring Metrics > Key metrics description > GC | TiDB Monitoring Metrics > Key metrics description > Batch Client | TiDB Monitoring Metrics > Key metrics description > TTL`
- Source Line Ranges: `111-214`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `grafana`, `metrics`, `kv-request`, `pd-client`, `schema-load`, `ddl`, `statistics`, `owner`, `meta`, `gc`, `batch-client`, `ttl`, `latency`, `qps`, `ops`, `errors`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0057_cf1b694a17`
- Source ID: `tidb-docs-8.1:grafana-tidb-dashboard.md#kv-request`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b845ff87212cfe2945faad545fc57aebdeff3116a812d4718ffa97de8a1469b9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard#kv-request
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-tidb-dashboard.md

## Retrieval Guidance

- Use When: Use this chunk when identifying what TiDB Grafana dashboard metrics mean for KV Request, PD Client, Schema Load, DDL, Statistics, Owner, Meta, GC, Batch Client, or TTL panels.
- Retrieval Keywords: KV Request OPS, KV Request Duration 99 by store, KV Request Duration 99 by type, Stale Read Hit/Miss Ops, Stale Read Req Ops, Stale Read Req Traffic, PD Client CMD OPS, PD Client CMD Duration, PD Client CMD Fail OPS, PD TSO OPS, PD TSO Wait Duration, PD TSO RPC duration, Async TSO Duration, Load Schema Duration, Load Schema OPS, Schema Lease Error OPM, change, outdate, Load Privilege OPS, DDL Duration 95, Batch Add Index Duration 100, DDL Waiting Jobs Count, DDL META OPM, DDL Worker Duration 99, Deploy Syncer Duration, Owner Handle Syncer Duration, Update Self Version Duration, DDL OPM, DDL backfill progress in percentage, Auto Analyze Duration 95, Auto Analyze QPS, Stats Inaccuracy Rate, Pseudo Estimation OPS, Dump Feedback OPS, Store Query Feedback QPS, Significant Feedback, Update Stats OPS, New ETCD Session Duration 95, Owner Watcher OPS, AutoID QPS, AutoID Duration, Region Cache Error OPS, Meta Operations Duration 99, Worker Action OPM, run_job, resolve_lock, delete_range, GC Failure OPM, Delete Range Failure OPM, Too Many Locks Error OPM, Action Result OPM, Delete Range Task Status, Push Task Duration 95, Pending Request Count by TiKV, Batch Client Unavailable Duration 95, No Available Connection Counter, TTL QPS By Type, TTL Insert Rows Per Second, TTL Processed Rows Per Second, TTL Insert Rows Per Hour, TTL Delete Rows Per Hour, TTL Scan/Delete Query Duration, TTL Scan/Delete Worker Time By Phase, TTL Job Count By Status, TTL Task Count By Status
- Follow-up Guidance: The source also states that Schema Lease errors include `change` and `outdate`, and that `outdate` is a more serious error that triggers an alert.
- Classification Note: The classification is observability for the dashboard component because the content is a Grafana metric description list for TiDB, TiKV, and PD behavior in a self-managed deployment.

## Official Source Content

### KV Request

The following metrics relate to requests sent to TiKV. Retry requests are counted multiple times.

- KV Request OPS: the execution times of a KV request, displayed according to TiKV
- KV Request Duration 99 by store: the execution time of a KV request, displayed according to TiKV
- KV Request Duration 99 by type: the execution time of a KV request, displayed according to the request type
- Stale Read Hit/Miss Ops
    - **hit**: the number of requests per second that successfully execute a stale read
    - **miss**: the number of requests per second that attempt a stale read but fail
- Stale Read Req Ops:
    - **cross-zone**: the number of requests per second that attempt a stale read in a remote zone
    - **local**: the number of requests per second that attempt a stale read in the local zone
- Stale Read Req Traffic:
    - **cross-zone-in**: the incoming traffic of responses to requests that attempt a stale read in a remote zone
    - **cross-zone-out**: the outgoing traffic of requests that attempt a stale read in a remote zone
    - **local-in**: the incoming traffic of responses to requests that attempt a stale read in the local zone
    - **local-out**: the outgoing traffic of requests that attempt a stale read in the local zone
### PD Client

- PD Client CMD OPS: the statistics of commands executed by PD Client per second
- PD Client CMD Duration: the time it takes for PD Client to execute commands
- PD Client CMD Fail OPS: the statistics of failed commands executed by PD Client per second
- PD TSO OPS: the number of gRPC requests per second that TiDB sends to PD (cmd) and the number of TSO requests (request); each gRPC request contains a batch of TSO requests
- PD TSO Wait Duration: the time that TiDB waits for PD to return TSO
- PD TSO RPC duration: the duration from the time that TiDB sends gRPC requests to PD to get TSO to the time that TiDB receives the gRPC response from PD
- Async TSO Duration: the duration from the time that TiDB prepares to get TSO to the time that TiDB actually starts to wait for PD to return TSO
### Schema Load

- Load Schema Duration: the time it takes TiDB to obtain the schema from TiKV
- Load Schema OPS: the statistics of the schemas that TiDB obtains from TiKV per second
- Schema Lease Error OPM: the Schema Lease errors include two types: `change` and `outdate`. `change` means that the schema has changed, and `outdate` means that the schema cannot be updated, which is a more serious error and triggers an alert.
- Load Privilege OPS: the statistics of the number of privilege information obtained by TiDB from TiKV per second
### DDL

- DDL Duration 95: 95% quantile of DDL statement processing time
- Batch Add Index Duration 100: statistics of the maximum time spent by each Batch on creating an index
- DDL Waiting Jobs Count: the number of DDL tasks that are waiting
- DDL META OPM: the number of times that a DDL obtains META every minute
- DDL Worker Duration 99: 99% quantile of the execution time of each DDL worker
- Deploy Syncer Duration: the time consumed by Schema Version Syncer initialization, restart, and clearing up operations
- Owner Handle Syncer Duration: the time that it takes the DDL Owner to update, obtain, and check the Schema Version
- Update Self Version Duration: the time consumed by updating the version information of Schema Version Syncer
- DDL OPM: the number of DDL executions per second
- DDL backfill progress in percentage: the progress of backfilling DDL tasks
### Statistics

- Auto Analyze Duration 95: the time consumed by automatic `ANALYZE`
- Auto Analyze QPS: the statistics of automatic `ANALYZE`
- Stats Inaccuracy Rate: the information of the statistics inaccuracy rate
- Pseudo Estimation OPS: the number of the SQL statements optimized using pseudo statistics
- Dump Feedback OPS: the number of stored statistical feedbacks
- Store Query Feedback QPS: the number of operations per second to store the feedback information of the union query, which is performed in TiDB memory
- Significant Feedback: the number of significant feedback pieces that update the statistics information
- Update Stats OPS: the number of operations of updating statistics with feedback
### Owner

- New ETCD Session Duration 95: the time it takes to create a new etcd session. TiDB connects to etcd in PD through etcd client to save/read some metadata information. This records the time spent creating the session
- Owner Watcher OPS: the number of Goroutine operations per second of DDL owner watch PD's etcd metadata
### Meta

- AutoID QPS: AutoID related statistics, including three operations (global ID allocation, a single table AutoID allocation, a single table AutoID Rebase)
- AutoID Duration: the time consumed by AutoID related operations
- Region Cache Error OPS: the number of errors encountered per second by the cached Region information in TiDB
- Meta Operations Duration 99: the latency of Meta operations
### GC

- Worker Action OPM: the number of GC related operations, including `run_job`, `resolve_lock`, and `delete_range`
- Duration 99: the time consumed by GC related operations
- Config: the configuration of GC data life time and GC running interval
- GC Failure OPM: the number of failed GC related operations
- Delete Range Failure OPM: the number of times the `Delete Range` has failed
- Too Many Locks Error OPM: the number of the error that GC clears up too many locks
- Action Result OPM: the number of results of GC-related operations
- Delete Range Task Status: the task status of `Delete Range`, including completion and failure
- Push Task Duration 95: the time spent pushing GC subtasks to GC workers
### Batch Client

- Pending Request Count by TiKV: the number of Batch messages that are pending processing
- Batch Client Unavailable Duration 95: the unavailable time of the Batch client
- No Available Connection Counter: the number of times the Batch client cannot find an available link
### TTL

- TiDB CPU Usage: the CPU usage of each TiDB instance.
- TiKV IO MBps: the total bytes of I/O in each TiKV instance.
- TiKV CPU: the CPU usage of each TiKV instance.
- TTL QPS By Type: the QPS information of different types of statements generated by TTL jobs.
- TTL Insert Rows Per Second: the number of rows inserted into TTL tables per second.
- TTL Processed Rows Per Second: the number of expired rows processed by TTL jobs per second.
- TTL Insert Rows Per Hour: the number of rows inserted into TTL tables for every hour.
- TTL Delete Rows Per Hour: the number of expired rows deleted by TTL jobs for every hour.
- TTL Scan/Delete Query Duration: the execution time of TTL scan/delete statements.
- TTL Scan/Delete Worker Time By Phase: the time consumed by different phases of TTL internal worker threads.
- TTL Job Count By Status: the number of TTL jobs currently being executed.
- TTL Task Count By Status: the number of TTL tasks currently being executed.
