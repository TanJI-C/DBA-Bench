# Dedicated cluster built-in metrics reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/built-in-monitoring.md`
- Source Title: `TiDB Cloud Built-in Metrics`
- Source Heading Path: `TiDB Cloud Built-in Metrics > Metrics for TiDB Cloud Dedicated clusters > Overview | TiDB Cloud Built-in Metrics > Metrics for TiDB Cloud Dedicated clusters > Advanced | TiDB Cloud Built-in Metrics > Metrics for TiDB Cloud Dedicated clusters > Server`
- Source Line Ranges: `30-81`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`
- Topic Tags: `metrics`, `dedicated-clusters`, `sql`, `transactions`, `connections`, `latency`, `grpc`, `tso`, `raft`, `cpu`, `memory`, `storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0785_e40dfba43c`
- Source ID: `tidb-docs-8.1:tidb-cloud/built-in-monitoring.md#overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9235873cb5f394afbcb1e6627db91a3f0490f259f443d0c9339cc9709a40628e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring#overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/built-in-monitoring.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the built-in metrics reference for TiDB Cloud Dedicated clusters, including metric names, labels, and descriptions across Overview, Advanced, and Server sections.
- Retrieval Keywords: Metrics for TiDB Cloud Dedicated clusters, Overview, Advanced, Server, Database Time by SQL types, Query Per Second, Query Duration, Failed Queries, Command Per Second, Queries Using Plan Cache OPS, Transaction Per Second, Transaction Duration, Connection Count, Disconnection Count, Average Idle Connection Duration, Get Token Duration, Parse Duration, Compile Duration, Execute Duration, Average TiDB KV Request Duration, Average TiKV gRPC Duration, Average / P99 PD TSO Wait/RPC Duration, Average / P99 Storage Async Write Duration, Average / P99 Store Duration, Average / P99 Apply Duration, Average / P99 Append Log Duration, Average / P99 Commit Log Duration, Average / P99 Apply Log Duration, TiDB Uptime, TiDB CPU Usage, TiDB Memory Usage, TiKV Uptime, TiKV CPU Usage, TiKV Memory Usage, TiKV IO Bps, TiKV Storage Usage, TiFlash Uptime, TiFlash CPU Usage, TiFlash Memory Usage, TiFlash IO MBps, TiFlash Storage Usage, SELECT, INSERT, UPDATE, kv_get, kv_prewrite, kv_commit
- Follow-up Guidance: The metric descriptions include exact labels such as avg, 99, hit, miss, node, limit, node-write, node-read, and request-type examples like Get, Prewrite, Commit, kv_get, kv_prewrite, and kv_commit.
- Classification Note: This is reference content because it is a tabular catalog of TiDB Cloud Dedicated cluster metrics with exact metric names, labels, and definitions.

## Official Source Content

### Overview

| Metric name  | Labels | Description                                   |
| :------------| :------| :-------------------------------------------- |
| Database Time by SQL types | database time, {SQL type} | database time: total database time per second. <br/> {SQL type}: database time consumed by SQL statements per second, which are collected by SQL types, such as `SELECT`, `INSERT`, and `UPDATE`. |
| Query Per Second | {SQL type} | The number of SQL statements executed per second in all TiDB instances, which are collected by SQL types, such as `SELECT`, `INSERT`, and `UPDATE`. |
| Query Duration | avg-{SQL type}, 99-{SQL type} | The duration from receiving a request from the client to TiDB until TiDB executes the request and returns the result to the client. In general, client requests are sent in the form of SQL statements; however, this duration can include the execution time of commands such as `COM_PING`, `COM_SLEEP`, `COM_STMT_FETCH`, and `COM_SEND_LONG_DATA`. TiDB supports Multi-Query, which means the client can send multiple SQL statements at one time, such as `select 1; select 1; select 1;`. In this case, the total execution time of this query includes the execution time of all SQL statements. |
| Failed Queries | All, {Error type} @ {instance} | The statistics of error types (such as syntax errors and primary key conflicts) according to the SQL statement execution errors per minute on each TiDB instance. It contains the module in which an error occurs and the error code. |
| Command Per Second | Query, StmtExecute, and StmtPrepare | The number of commands processed by all TiDB instances per second based on command types. |
| Queries Using Plan Cache OPS | hit, miss | hit: the number of queries using plan cache per second in all TiDB instances. <br/> miss: the number of queries missing plan cache per second in all TiDB instances. |
| Transaction Per Second | {types}-{transaction model} | The number of transactions executed per second. |
| Transaction Duration | avg-{transaction model}, 99-{transaction model} | The average or the 99th percentile duration of transactions. |
| Connection Count | All, active connection | All: the number of connections to all TiDB instances. <br/> Active connections: the number of active connections to all TiDB instances. |
| Disconnection Count | {instance}-{result} | The number of clients disconnected to each TiDB instance. |
### Advanced

| Metric name  | Labels | Description                                   |
| :------------| :------| :-------------------------------------------- |
| Average Idle Connection Duration | avg-in-txn, avg-not-in-txn | The connection idle duration indicates the duration of a connection being idle.<br/> avg-in-txn: The average connection idle duration when a connection is within a transaction. <br/>avg-not-in-txn: The average connection idle duration when a connection is not within a transaction. |
| Get Token Duration | avg, 99 | The average or the 99th percentile duration consumed in getting tokens of SQL statements. |
| Parse Duration | avg, 99 | The average or the 99th percentile duration consumed in parsing SQL statements. |
| Compile Duration | avg, 99 | The average or the 99th percentile duration consumed in compiling the parsed SQL AST to execution plans. |
| Execute Duration | avg, 99 | The average or the 99th percentile duration consumed in executing execution plans of SQL statements. |
| Average TiDB KV Request Duration | {Request Type} | The average time consumed in executing KV requests in all TiDB instances based on request types, such as `Get`, `Prewrite`, and `Commit`. |
| Average TiKV gRPC Duration | {Request Type} | The average time consumed in executing gRPC requests in all TiKV instances based on request types, such as `kv_get`, `kv_prewrite`, and `kv_commit`. |
| Average / P99 PD TSO Wait/RPC Duration | wait-avg/99, rpc-avg/99 | Wait: the average or the 99th percentile duration in waiting for PD to return TSO in all TiDB instances. <br/> RPC: the average time or the 99th percentile of duration from sending TSO requests to PD to receiving TSO in all TiDB instances. |
| Average / P99 Storage Async Write Duration | avg, 99 | The average or the 99th percentile duration consumed in asynchronous writing. Average storage async write duration = Average store duration + Average apply duration. |
| Average / P99 Store Duration | avg, 99 | The average or the 99th percentile duration consumed in storing loop during asynchronous writing. |
| Average / P99 Apply Duration | avg, 99 | The average or the 99th percentile duration consumed in applying loop during asynchronous writing. |
| Average / P99 Append Log Duration | avg, 99 | The average or the 99th percentile duration consumed by Raft to append logs. |
| Average / P99 Commit Log Duration | avg, 99 | The average or the 99th percentile duration consumed by Raft to commit logs. |
| Average / P99 Apply Log Duration | avg, 99 | The average or the 99th percentile duration consumed by Raft to apply logs. |
### Server

| Metric name  | Labels | Description                                   |
| :------------| :------| :-------------------------------------------- |
| TiDB Uptime | node | The runtime of each TiDB node since last restart. |
| TiDB CPU Usage | node, limit | The CPU usage statistics or upper limit of each TiDB node. |
| TiDB Memory Usage | node, limit | The memory usage statistics or upper limit of each TiDB node. |
| TiKV Uptime | node | The runtime of each TiKV node since last restart. |
| TiKV CPU Usage | node, limit | The CPU usage statistics or upper limit of each TiKV node. |
| TiKV Memory Usage | node, limit | The memory usage statistics or upper limit of each TiKV node. |
| TiKV IO Bps | node-write, node-read | The total input/output bytes per second of read and write in each TiKV node. |
| TiKV Storage Usage | node, limit | The storage usage statistics or upper limit of each TiKV node. |
| TiFlash Uptime | node | The runtime of each TiFlash node since last restart. |
| TiFlash CPU Usage | node, limit | The CPU usage statistics or upper limit of each TiFlash node. |
| TiFlash Memory Usage | node, limit | The memory usage statistics or upper limit of each TiFlash node. |
| TiFlash IO MBps | node-write, node-read | The total bytes of read and write in each TiFlash node. |
| TiFlash Storage Usage | node, limit | The storage usage statistics or upper limit of each TiFlash node. |
