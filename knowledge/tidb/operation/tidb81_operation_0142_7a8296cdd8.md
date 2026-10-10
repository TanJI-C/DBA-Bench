# Daily management FAQs for TiDB cluster operations

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/manage-cluster-faq.md`
- Source Title: `TiDB Cluster Management FAQs`
- Source Heading Path: `TiDB Cluster Management FAQs | TiDB Cluster Management FAQs > Daily management | TiDB Cluster Management FAQs > Daily management > How to log into TiDB? | TiDB Cluster Management FAQs > Daily management > How to modify the system variables in TiDB? | TiDB Cluster Management FAQs > Daily management > Where and what are the data directories in TiDB (TiKV)? | TiDB Cluster Management FAQs > Daily management > What are the system tables in TiDB? | TiDB Cluster Management FAQs > Daily management > Where are the TiDB/PD/TiKV logs? | TiDB Cluster Management FAQs > Daily management > How to safely stop TiDB? | TiDB Cluster Management FAQs > Daily management > Can `kill` be executed in TiDB? | TiDB Cluster Management FAQs > Daily management > Does TiDB support session timeout? | TiDB Cluster Management FAQs > Daily management > What is the TiDB version management strategy? | TiDB Cluster Management FAQs > Daily management > How about the operating cost of deploying and maintaining a TiDB cluster? | TiDB Cluster Management FAQs > Daily management > What's the difference between various TiDB master versions? | TiDB Cluster Management FAQs > Daily management > Is there a graphical deployment tool for TiDB? | TiDB Cluster Management FAQs > Daily management > How to scale out a TiDB cluster? | TiDB Cluster Management FAQs > Daily management > How to scale TiDB horizontally? | TiDB Cluster Management FAQs > Daily management > If Percolator uses distributed locks and the crash client keeps the lock, will the lock not be released? | TiDB Cluster Management FAQs > Daily management > Why does TiDB use gRPC instead of Thrift? Is it because Google uses it? | TiDB Cluster Management FAQs > Daily management > What does the 92 indicate in `like(bindo.customers.name, jason%, 92)`? | TiDB Cluster Management FAQs > Daily management > Why does the data length shown by `information_schema.tables.data_length` differ from the store size on the TiKV monitoring panel? | TiDB Cluster Management FAQs > Daily management > Why does the transaction not use the Async Commit or the one-phase commit feature?`
- Source Line Ranges: `5-135`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `operator`, `pd`, `sql`, `tidb`, `tikv`, `tiup`
- Topic Tags: `login`, `system-variables`, `data-directory`, `system-tables`, `logs`, `shutdown`, `kill`, `session-timeout`, `versioning`, `monitoring`, `troubleshooting`, `deployment`, `scale-out`, `horizontal-scaling`, `grpc`, `escape-character`, `data-length`, `async-commit`, `one-phase-commit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0142_7a8296cdd8`
- Source ID: `tidb-docs-8.1:faq/manage-cluster-faq.md#tidb-cluster-management-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2b7c4b17225383bfee4d21a0ae282029459956e8e3cbf902ede16db593097792`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/manage-cluster-faq#tidb-cluster-management-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/manage-cluster-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering routine TiDB cluster management questions about login, system variables, data directories, logs, safe shutdown, KILL behavior, session timeout, version viewing, scaling, monitoring, or why Async Commit and one-phase commit are not used.
- Retrieval Keywords: mysql -h 127.0.0.1 -uroot -P4000, SET GLOBAL xxx = n, --data-dir, backup db raft snap, TiDB system table, --log-file, SHUTDOWN, graceful-wait-before-shutdown, information_schema.cluster_processlist, enable-global-kill, kill session_id, kill tidb session_id, admin show ddl jobs, admin cancel ddl jobs, wait_timeout, interactive_timeout, tidb_idle_transaction_timeout, select tidb_version(), tidb-server -V, TiUP, TiDB Operator, Scale a TiDB Cluster Using TiUP, Manually Scale TiDB on Kubernetes, Load Balancer, gRPC instead of Thrift, ASCII 92 escape character, information_schema.tables.data_length, store size on the TiKV monitoring panel, tidb_enable_async_commit, tidb_enable_1pc, TiDB Binlog
- Follow-up Guidance: The content points to related references such as TiDB system table, KILL, ADMIN statement, TiDB versioning, TiDB monitoring framework, TiDB Troubleshooting Map, and scaling guides for TiUP or TiDB Operator.
- Classification Note: This is classified as operation for the shared component scope because the official content is a daily management FAQ spanning TiDB, TiKV, PD, TiUP, SQL behavior, monitoring, shutdown, and scaling.

## Official Source Content

# TiDB Cluster Management FAQs

This document summarizes the FAQs related to TiDB cluster management.
## Daily management

This section describes common problems you might encounter during daily cluster management, their causes, and solutions.
### How to log into TiDB?

You can log into TiDB like logging into MySQL. For example:

```bash
mysql -h 127.0.0.1 -uroot -P4000
```
### How to modify the system variables in TiDB?

Similar to MySQL, TiDB includes static and solid parameters. You can directly modify static parameters using `SET GLOBAL xxx = n`, but the new value of a parameter is only effective within the life cycle in this instance.
### Where and what are the data directories in TiDB (TiKV)?

TiKV data is located in the [`--data-dir`](https://docs.pingcap.com/tidb/stable/command-line-flags-for-tikv-configuration#--data-dir), which include four directories of backup, db, raft, and snap, used to store backup, data, Raft data, and mirror data respectively.
### What are the system tables in TiDB?

Similar to MySQL, TiDB includes system tables as well, used to store the information required by the server when it runs. See [TiDB system table](https://docs.pingcap.com/tidb/stable/mysql-schema/mysql-schema).
### Where are the TiDB/PD/TiKV logs?

By default, TiDB/PD/TiKV outputs standard error in the logs. If a log file is specified by `--log-file` during the startup, the log is output to the specified file and executes rotation daily.
### How to safely stop TiDB?

- If a load balancer is running (recommended): Stop the load balancer and execute the SQL statement `SHUTDOWN`. Then TiDB waits for a period as specified by [`graceful-wait-before-shutdown`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#graceful-wait-before-shutdown-new-in-v50) until all sessions are terminated. Then TiDB stops running.

- If no load balancer is running: Execute the `SHUTDOWN` statement. Then TiDB components are gracefully stopped.
### Can `kill` be executed in TiDB?

- Kill DML statements:

    First use `information_schema.cluster_processlist` to find TiDB instance address and session ID, and then run the kill command.

    TiDB v6.1.0 introduces the Global Kill feature (controlled by the `enable-global-kill` configuration, which is enabled by default). If Global Kill is enabled, just execute `kill session_id`.

    If the TiDB version is earlier than v6.1.0, or the Global Kill feature is not enabled, `kill session_id` does not take effect by default. To terminate a DML statement, you should connect the client directly to the TiDB instance that is executing the DML statement and then execute the `kill tidb session_id` statement. If the client connects to another TiDB instance or there is a proxy between the client and the TiDB cluster, the `kill tidb session_id` statement might be routed to another TiDB instance, which might incorrectly terminate another session. For details, see [`KILL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill).

- Kill DDL statements: First use `admin show ddl jobs` to find the ID of the DDL job you need to terminate, and then run `admin cancel ddl jobs 'job_id' [, 'job_id'] ...`. For more details, see the [`ADMIN` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin).
### Does TiDB support session timeout?

TiDB currently supports the following timeouts: [`wait_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#wait_timeout), [`interactive_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#interactive_timeout), and [`tidb_idle_transaction_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_idle_transaction_timeout-new-in-v760).
### What is the TiDB version management strategy?

For details about TiDB version management, see [TiDB versioning](https://docs.pingcap.com/tidb/stable/releases/versioning).
### How about the operating cost of deploying and maintaining a TiDB cluster?

TiDB provides a few features and [tools](https://docs.pingcap.com/tidb/stable/ecosystem-tool-user-guide), with which you can manage the clusters easily at a low cost:

- For maintenance operations, [TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-documentation-guide) works as the package manager, which simplifies the deployment, scaling, upgrade, and other maintenance tasks.
- For monitoring, the [TiDB monitoring framework](https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework) uses [Prometheus](https://prometheus.io/) to store the monitoring and performance metrics, and uses [Grafana](https://grafana.com/grafana/) to visualize these metrics. Dozens of built-in panels are available with hundreds of metrics.
- For troubleshooting, the [TiDB Troubleshooting Map](https://docs.pingcap.com/tidb/stable/tidb-troubleshooting-map) summarizes common issues of the TiDB server and other components. You can use this map to diagnose and resolve issues when you encounter related problems.
### What's the difference between various TiDB master versions?

The TiDB community is highly active. The engineers have been keeping optimizing features and fixing bugs. Therefore, the TiDB version is updated quite fast. If you want to keep informed of the latest version, see [TiDB Release Timeline](https://docs.pingcap.com/tidb/stable/releases/release-timeline).

It is recommended to deploy TiDB [using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) or [using TiDB Operator](https://docs.pingcap.com/tidb-in-kubernetes/stable). TiDB has a unified management of the version number. You can view the version number using one of the following methods:

- `select tidb_version()`
- `tidb-server -V`
### Is there a graphical deployment tool for TiDB?

Currently no.
### How to scale out a TiDB cluster?

You can scale out your TiDB cluster without interrupting the online services.

- If your cluster is deployed using [TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup), refer to [Scale a TiDB Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup).
- If your cluster is deployed using [TiDB Operator](https://docs.pingcap.com/tidb/stable/tidb-operator-overview) on Kubernetes, refer to [Manually Scale TiDB on Kubernetes](https://docs.pingcap.com/tidb-in-kubernetes/stable/scale-a-tidb-cluster).
### How to scale TiDB horizontally?

As your business grows, your database might face the following three bottlenecks:

- Lack of storage resources which means that the disk space is not enough.

- Lack of computing resources such as high CPU occupancy.

- Not enough write and read capacity.

You can scale TiDB as your business grows.

- If the disk space is not enough, you can increase the capacity simply by adding more TiKV nodes. When the new node is started, PD will migrate the data from other nodes to the new node automatically.

- If the computing resources are not enough, check the CPU consumption situation first before adding more TiDB nodes or TiKV nodes. When a TiDB node is added, you can configure it in the Load Balancer.

- If the capacity is not enough, you can add both TiDB nodes and TiKV nodes.
### If Percolator uses distributed locks and the crash client keeps the lock, will the lock not be released?

For more details, see [Percolator and TiDB Transaction Algorithm](https://pingkai.cn/tidbcommunity/blog/f537be2c) in Chinese.
### Why does TiDB use gRPC instead of Thrift? Is it because Google uses it?

Not really. We need some good features of gRPC, such as flow control, encryption and streaming.
### What does the 92 indicate in `like(bindo.customers.name, jason%, 92)`?

The 92 indicates the escape character, which is ASCII 92 by default.
### Why does the data length shown by `information_schema.tables.data_length` differ from the store size on the TiKV monitoring panel?

Two reasons:

- The two results are calculated in different ways. `information_schema.tables.data_length` is an estimated value by calculating the averaged length of each row, while the store size on the TiKV monitoring panel sums up the length of the data files (the SST files of RocksDB) in a single TiKV instance.
- `information_schema.tables.data_length` is a logical value, while the store size is a physical value. The redundant data generated by multiple versions of the transaction is not included in the logical value, while the redundant data is compressed by TiKV in the physical value.
### Why does the transaction not use the Async Commit or the one-phase commit feature?

In the following situations, even you have enabled the [Async Commit](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_async_commit-new-in-v50) feature and the [one-phase commit](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_1pc-new-in-v50) feature using the system variables, TiDB will not use these features:

- If you have enabled TiDB Binlog, restricted by the implementation of TiDB Binlog, TiDB does not use the Async Commit or one-phase commit feature.
- TiDB uses the Async Commit or one-phase commit features only when no more than 256 key-value pairs are written in the transaction and the total size of keys is no more than 4 KB. This is because, for transactions with a large amount of data to write, using Async Commit cannot greatly improve the performance.
