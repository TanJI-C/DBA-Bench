# TiDB Grafana dashboard key metrics overview and panels

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-tidb-dashboard.md`
- Source Title: `TiDB Monitoring Metrics`
- Source Heading Path: `TiDB Monitoring Metrics | TiDB Monitoring Metrics > Key metrics description | TiDB Monitoring Metrics > Key metrics description > Query Summary | TiDB Monitoring Metrics > Key metrics description > Query Detail | TiDB Monitoring Metrics > Key metrics description > Server | TiDB Monitoring Metrics > Key metrics description > Transaction | TiDB Monitoring Metrics > Key metrics description > Executor | TiDB Monitoring Metrics > Key metrics description > Distsql | TiDB Monitoring Metrics > Key metrics description > KV Errors`
- Source Line Ranges: `5-110`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `tikv`, `pd`, `tiup`
- Topic Tags: `grafana`, `prometheus`, `monitoring`, `dashboard`, `metrics`, `query`, `transactions`, `server`, `executor`, `distsql`, `kv-errors`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0056_b0f37e5dc8`
- Source ID: `tidb-docs-8.1:grafana-tidb-dashboard.md#tidb-monitoring-metrics`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `657dd04aa5a9e08b4ad35f6f7cd0e0165cbc1a9df8c9f7c0070cccb14e22099b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard#tidb-monitoring-metrics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-tidb-dashboard.md

## Retrieval Guidance

- Use When: Use this chunk when locating what the TiDB Grafana dashboard panels mean, especially Query Summary, Query Detail, Server, Transaction, Executor, Distsql, and KV Errors metrics.
- Retrieval Keywords: TiDB Monitoring Metrics, Key metrics description, TiDB dashboard, TiDB Summary panel, Query Summary, Query Detail, Server, Transaction, Executor, Distsql, KV Errors, Duration, Command Per Second, QPS, Failed Query OPM, Slow query, Connection Idle Duration, Duration 80/95/99/999 By Instance, Internal SQL OPS, Uptime, Memory Usage, CPU Usage, Connection Count, Open FD Count, Events OPM, Goroutine Count, Prepare Statement Count, Panic And Critical Error, Time Jump Back OPS, Get Token Duration, Skip Binlog Count, Client Data Traffic, Transaction OPS, Transaction Retry Num, Session Retry Error OPS, Commit Token Wait Duration, tidb_committer_concurrency, KV Transaction OPS, Transaction Regions Num, Statement Lock Keys, TTL Lifetime Reach Counter, max-txn-TTL, Load Safepoint OPS, Pessimistic Statement Retry OPS, Transaction Types Per Seconds, Parse Duration, Compile Duration, Execution Duration, Expensive Executor OPS, Merge Join, Hash Join, Index Look Up Join, Hash Agg, Stream Agg, Sort, TopN, Queries Using Plan Cache OPS, Plan Cache Miss OPS, Plan Cache Memory Usage, Plan Cache Plan Num, Distsql Duration, Distsql QPS, Distsql Partial QPS, Scan Keys Num, Partial Num, KV Backoff Duration, TiClient Region Error OPS, KV Backoff OPS, Lock Resolve OPS, Other Errors OPS
- Follow-up Guidance: The source also notes that if TiUP is used to deploy the TiDB cluster, Prometheus and Grafana are deployed at the same time, and it links to TiDB Monitoring Framework Overview for the monitoring architecture.
- Classification Note: This chunk is classified as observability for the dashboard component because it explains monitoring panels and the meanings of TiDB Grafana metrics across TiDB, TiKV, and PD related views.

## Official Source Content

# TiDB Monitoring Metrics

If you use TiUP to deploy the TiDB cluster, the monitoring system (Prometheus & Grafana) is deployed at the same time. For the monitoring architecture, see [TiDB Monitoring Framework Overview](https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework).

The Grafana dashboard is divided into a series of sub dashboards which include Overview, PD, TiDB, TiKV, Node\_exporter, Disk Performance, and Performance\_overview. The TiDB dashboard consists of the TiDB panel and the TiDB Summary panel. The differences between the two panels are different in the following aspects:

- TiDB panel: provides as comprehensive information as possible for troubleshooting cluster anomalies.
- TiDB Summary Panel: extracts parts of the TiDB panel information with which users are most concerned, with some modifications. It provides data (such as QPS, TPS, response delay) that users care about in the daily database operations, which serves as the monitoring information to be displayed or reported.

This document describes some key monitoring metrics displayed on the TiDB dashboard.
## Key metrics description

To understand the key metrics displayed on the TiDB dashboard, check the following sections:
### Query Summary

- Duration: execution time
    - The duration between the time that the client's network request is sent to TiDB and the time that the request is returned to the client after TiDB has executed it. In general, client requests are sent in the form of SQL statements, but can also include the execution time of commands such as `COM_PING`, `COM_SLEEP`, `COM_STMT_FETCH`, and `COM_SEND_LONG_DATA`
    - Because TiDB supports Multi-Query, it supports sending multiple SQL statements at one time, such as `select 1; select 1; select 1;`. In this case, the total execution time of this query includes the execution time of all SQL statements
- Command Per Second: the number of commands processed by TiDB per second, which is classified according to the success or failure of command execution results
- QPS: the number of SQL statements executed per second on all TiDB instances, which is counted according to `SELECT`, `INSERT`, `UPDATE`, and other types of statements
- CPS By Instance: the command statistics on each TiDB instance, which is classified according to the success or failure of command execution results
- Failed Query OPM: the statistics of error types (such as syntax errors and primary key conflicts) according to the errors occurred when executing SQL statements per minute on each TiDB instance. It contains the module in which the error occurs and the error code
- Slow query: the statistics of the processing time of slow queries (the time cost of the entire slow query, the time cost of Coprocessor, and the waiting time for Coprocessor scheduling). Slow queries are classified into internal and general SQL statements
- Connection Idle Duration: the duration of idle connections
- 999/99/95/80 Duration: the statistics of the execution time for different types of SQL statements (different percentiles)
### Query Detail

- Duration 80/95/99/999 By Instance: the statistics of the execution time for SQL statements on each TiDB instance (different percentiles)
- Failed Query OPM Detail: the statistics of error types (such as syntax errors and primary key conflicts) according to the errors occurred when executing SQL statements per minute on each TiDB instance
- Internal SQL OPS: the internal SQL statements executed per second in the entire TiDB cluster. The internal SQL statements are internally executed and are generally triggered by user SQL statements or internally scheduled tasks.
### Server

- Uptime: the runtime of each TiDB instance
- Memory Usage: the memory usage statistics of each TiDB instance, which is divided into the memory occupied by processes and the memory applied by Golang on the heap
- CPU Usage: the statistics of CPU usage of each TiDB instance
- Connection Count: the number of clients connected to each TiDB instance
- Open FD Count: the statistics of opened file descriptors of each TiDB instance
- Disconnection Count: the number of clients disconnected to each TiDB instance
- Events OPM: the statistics of key events, such as "start", "close", "graceful-shutdown","kill", and "hang"
- Goroutine Count: the number of Goroutines on each TiDB instance
- Prepare Statement Count: the number of `Prepare` statements that are executed on each TiDB instance and the total count of them
- Keep Alive OPM: the number of times that the metrics are refreshed every minute on each TiDB instance. It usually needs no attention.
- Panic And Critical Error: the number of panics and critical errors occurred in TiDB
- Time Jump Back OPS: the number of times that the operating system rewinds every second on each TiDB instance
- Get Token Duration: the time cost of getting Token on each connection
- Skip Binlog Count: the number of binlog write failures in TiDB
- Client Data Traffic: data traffic statistics of TiDB and the client
### Transaction

- Transaction OPS: the number of transactions executed per second
- Duration: the execution duration of a transaction
- Transaction Statement Num: the number of SQL statements in a transaction
- Transaction Retry Num: the number of times that a transaction retries
- Session Retry Error OPS: the number of errors encountered during the transaction retry per second. This metric includes two error types: retry failure and exceeding the maximum number of retries
- Commit Token Wait Duration: the wait duration in the flow control queue during the transaction commit. If the wait duration is long, it means that the transaction to commit is too large and the flow is controlled. If the system still has resources available, you can speed up the commit process by increasing the system variable `tidb_committer_concurrency`.
- KV Transaction OPS: the number of transactions executed per second within each TiDB instance
    - A user transaction might trigger multiple transaction executions in TiDB, including reading internal metadata and atomic retries of the user transaction
    - TiDB's internally scheduled tasks also operate on the database through transactions, which are also included in this panel
- KV Transaction Duration: the time spent on executing transactions within each TiDB
- Transaction Regions Num: the number of Regions operated in the transaction
- Transaction Write KV Num Rate and Sum: the rate at which KVs are written and the sum of these written KVs in the transaction
- Transaction Write KV Num: the number of KVs operated in the transaction
- Statement Lock Keys: the number of locks for a single statement
- Send HeartBeat Duration: the duration for the transaction to send heartbeats
- Transaction Write Size Bytes Rate and sum: the rate at which bytes are written and the sum of these written bytes in the transaction
- Transaction Write Size Bytes: the size of the data written in the transaction
- Acquire Pessimistic Locks Duration: the time consumed by adding locks
- TTL Lifetime Reach Counter: the number of transactions that reach the upper limit of TTL. The default value of the TTL upper limit is 1 hour. It means that 1 hour has passed since the first lock of a pessimistic transaction or the first prewrite of an optimistic transaction. The default value of the upper limit of TTL is 1 hour. The upper limit of TTL life can be changed by modifying `max-txn-TTL` in the TiDB configuration file
- Load Safepoint OPS: the number of times that `Safepoint` is loaded. `Safepoint` is to ensure that the data before `Safepoint` is not read when the transaction reads data, thus ensuring data safety. The data before `Safepoint` might be cleaned up by the GC
- Pessimistic Statement Retry OPS: the number of retry attempts for pessimistic statements. When the statement tries to add lock, it might encounter a write conflict. At this time, the statement will acquire a new snapshot and add lock again
- Transaction Types Per Seconds: the number of transactions committed per second using the two-phase commit (2PC), async commit, and one-phase commit (1PC) mechanisms, including both success and failure transactions
### Executor

- Parse Duration: the statistics of the parsing time of SQL statements
- Compile Duration: the statistics of the time of compiling the parsed SQL AST to the execution plan
- Execution Duration: the statistics of the execution time for SQL statements
- Expensive Executor OPS: the statistics of the operators that consume many system resources per second, including `Merge Join`, `Hash Join`, `Index Look Up Join`, `Hash Agg`, `Stream Agg`, `Sort`, and `TopN`
- Queries Using Plan Cache OPS: the statistics of queries using the Plan Cache per second
- Plan Cache Miss OPS: the statistics of the number of times that the Plan Cache is missed per second
- Plan Cache Memory Usage: the total memory consumed by the execution plan cached in each TiDB instance
- Plan Cache Plan Num: the total number of execution plans cached in each TiDB instance
### Distsql

- Distsql Duration: the processing time of Distsql statements
- Distsql QPS: the statistics of Distsql statements
- Distsql Partial QPS: the number of Partial results every second
- Scan Keys Num: the number of keys that each query scans
- Scan Keys Partial Num: the number of keys that each Partial result scans
- Partial Num: the number of Partial results for each SQL statement
### KV Errors

- KV Backoff Duration: the total duration that a KV retry request lasts. TiDB might encounter an error when sending a request to TiKV. TiDB has a retry mechanism for every request to TiKV. This `KV Backoff Duration` item records the total time of a request retry.
- TiClient Region Error OPS: the number of Region related error messages returned by TiKV
- KV Backoff OPS: the number of error messages returned by TiKV
- Lock Resolve OPS: the number of TiDB operations to resolve locks. When TiDB's read or write request encounters a lock, it tries to resolve the lock
- Other Errors OPS: the number of other types of errors, including clearing locks and updating `SafePoint`
