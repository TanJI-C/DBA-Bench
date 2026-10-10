# TiKV-Details dashboard key monitoring metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-tikv-dashboard.md`
- Source Title: `Key Monitoring Metrics of TiKV`
- Source Heading Path: `Key Monitoring Metrics of TiKV | Key Monitoring Metrics of TiKV > TiKV-Details dashboard | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Cluster | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Errors | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Server | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > gRPC | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Thread CPU | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > PD | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Raft IO | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Raft process | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Raft message | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Raft propose | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Raft admin | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Local reader | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Unified Read Pool | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Storage`
- Source Line Ranges: `5-186`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `dashboard`, `pd`, `tidb`
- Topic Tags: `grafana`, `monitoring`, `metrics`, `tikv-details`, `cluster-health`, `errors`, `grpc`, `thread-cpu`, `pd-requests`, `raft`, `storage`, `read-pool`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0058_846a7e6f7f`
- Source ID: `tidb-docs-8.1:grafana-tikv-dashboard.md#key-monitoring-metrics-of-tikv`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `60b1896682ea2a24141361e8c6cff717157d1fbf151cf5512ac8ad08032f90dc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#key-monitoring-metrics-of-tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-tikv-dashboard.md

## Retrieval Guidance

- Use When: Use this chunk when identifying what the TiKV-Details Grafana dashboard shows for TiKV health, errors, gRPC, thread CPU, PD interaction, Raft activity, local reader, unified read pool, and storage metrics.
- Retrieval Keywords: TiKV-Details dashboard, Key Monitoring Metrics of TiKV, Cluster, Errors, Server, gRPC, Thread CPU, PD requests, PD heartbeats, Raft IO, Raft process, Raft message, Raft propose, Raft admin, Local reader requests, Unified Read Pool, Storage command total, Server is busy, Channel full, gRPC message failed, Process ready duration per server, Storage async snapshot duration, Storage async write duration
- Follow-up Guidance: The source lists normal-case expectations for several metrics, including Server is busy and Server report failures being 0, Channel full being 0, Process ready duration per server being less than 2 seconds (P99.99), and storage async snapshot and write duration being less than 1s in .99.
- Classification Note: This chunk is classified as observability for the TiKV component because it documents Grafana monitoring metrics and dashboard panels used to inspect TiKV status and behavior.

## Official Source Content

# Key Monitoring Metrics of TiKV

If you use TiUP to deploy the TiDB cluster, the monitoring system (Prometheus/Grafana) is deployed at the same time. For more information, see [Overview of the Monitoring Framework](https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework).

The Grafana dashboard is divided into a series of sub dashboards which include Overview, PD, TiDB, TiKV, Node\_exporter, and Performance\_overview. A lot of metrics are there to help you diagnose.
## TiKV-Details dashboard

You can get an overview of the component TiKV status from the **TiKV-Details** dashboard, where the key metrics are displayed. According to the [Performance Map](https://asktug.com/_/tidb-performance-map/#/), you can check whether the status of the cluster is as expected.

This section provides a detailed description of these key metrics on the **TiKV-Details** dashboard.
### Cluster

- Store size: The storage size per TiKV instance
- Available size: The available capacity per TiKV instance
- Capacity size: The capacity size per TiKV instance
- CPU: The CPU utilization per TiKV instance
- Memory: The memory usage per TiKV instance
- IO utilization: The I/O utilization per TiKV instance
- MBps: The total bytes of read and write in each TiKV instance
- QPS: The QPS per command in each TiKV instance
- Errps: The rate of gRPC message failures
- leader: The number of leaders per TiKV instance
- Region: The number of Regions per TiKV instance
- Uptime: The runtime of TiKV since last restart

![TiKV Dashboard - Cluster metrics](/media/tikv-dashboard-cluster.png)
### Errors

- Critical error: The number of critical errors
- Server is busy: Indicates occurrences of events that make the TiKV instance unavailable temporarily, such as Write Stall, and Channel Full. It should be `0` in normal case.
- Server report failures: The number of error messages reported by server. It should be `0` in normal case.
- Raftstore error: The number of Raftstore errors per type on each TiKV instance
- Scheduler error: The number of scheduler errors per type on each TiKV instance
- Coprocessor error: The number of coprocessor errors per type on each TiKV instance
- gRPC message error: The number of gRPC message errors per type on each TiKV instance
- Leader drop: The count of dropped leaders per TiKV instance
- Leader missing: The count of missing leaders per TiKV instance
- Log Replication Reject: The number of logappend messages rejected due to insufficient memory on each TiKV instance

![TiKV Dashboard - Errors metrics](/media/tikv-dashboard-errors-v610.png)
### Server

- CF size: The size of each column family
- Store size: The storage size per TiKV instance
- Channel full: The number of Channel Full errors per TiKV instance. It should be `0` in normal case.
- Active written leaders: The number of leaders being written on each TiKV instance
- Approximate Region size: The approximate Region size
- Approximate Region size Histogram: The histogram of each approximate Region size
- Region average written keys: The average number of written keys to Regions per TiKV instance
- Region average written bytes: The average written bytes to Regions per TiKV instance

![TiKV Dashboard - Server metrics](/media/tikv-dashboard-server.png)
### gRPC

- gRPC message count: The rate of gRPC messages per type
- gRPC message failed: The rate of failed gRPC messages
- 99% gRPC message duration: The gRPC message duration per message type (P99)
- Average gRPC message duration: The average execution time of gRPC messages
- gRPC batch size: The batch size of gRPC messages between TiDB and TiKV
- Raft message batch size: The batch size of Raft messages between TiKV instances
- gRPC request sources QPS: The QPS of gRPC request sources
- gRPC request sources duration: The execution time of gRPC request sources
- gRPC resource group QPS: The QPS of gRPC request sources by resource groups
### Thread CPU

- Raft store CPU: The CPU utilization of the `raftstore` thread. The CPU utilization should be less than 80% * `raftstore.store-pool-size` in normal case.
- Async apply CPU: The CPU utilization of the `async apply` thread. The CPU utilization should be less than 90% * `raftstore.apply-pool-size` in normal cases.
- Store writer CPU: The CPU utilization of the async IO thread. The CPU utilization should be less than 90% * `raftstore.store-io-pool-size` in normal cases.
- gRPC poll CPU: The CPU utilization of the `gRPC` thread. The CPU utilization should be less than 80% * `server.grpc-concurrency` in normal cases.
- Scheduler worker CPU: The CPU utilization of the `scheduler worker` thread. The CPU utilization should be less than 90% * `storage.scheduler-worker-pool-size` in normal cases.
- Storage ReadPool CPU: The CPU utilization of the `storage read pool` thread
- Unified read pool CPU: The CPU utilization of the `unified read pool` thread
- RocksDB CPU: The CPU utilization of the RocksDB thread
- Coprocessor CPU: The CPU utilization of the `coprocessor` thread
- GC worker CPU: The CPU utilization of the `GC worker` thread
- BackGround worker CPU: The CPU utilization of the `background worker` thread
- Import CPU: The CPU utilization of the `import` thread
- Backup Worker CPU: The CPU utilization of the `backup` thread
- CDC Worker CPU: The CPU utilization of the `CDC worker` thread
- CDC endpoint CPU: The CPU utilization of the `CDC endpoint` thread
- Raftlog fetch worker CPU: The CPU utilization of the async raft log fetcher worker
- TSO Worker CPU: The CPU utilization of the `TSO worker` thread
### PD

- PD requests: The rate at which TiKV sends to PD
- PD request duration (average): The average duration of processing requests that TiKV sends to PD
- PD heartbeats: The rate at which heartbeat messages are sent from TiKV to PD
- PD validate peers: The rate at which messages are sent from TiKV to PD to validate TiKV peers
### Raft IO

- Apply log duration: The time consumed for Raft to apply logs
- Apply log duration per server: The time consumed for Raft to apply logs per TiKV instance
- Append log duration: The time consumed for Raft to append logs
- Append log duration per server: The time consumed for Raft to append logs per TiKV instance
- Commit log duration: The time consumed by Raft to commit logs
- Commit log duration per server: The time consumed by Raft to commit logs per TiKV instance

![TiKV Dashboard - Raft IO metrics](/media/tikv-dashboard-raftio.png)
### Raft process

- Ready handled: The number of handled ready operations per type per second
    - count: The number of handled ready operations per second
    - has_ready_region: The number of Regions that have ready per second
    - pending_region: The operations per second of the Regions being checked for whether it has ready. This metric is deprecated since v3.0.0
    - message: The number of messages that the ready operations per second contain
    - append: The number of Raft log entries that the ready operations per second contain
    - commit: The number of committed Raft log entries that the ready operations per second contain
    - snapshot: The number of snapshots that the ready operations per second contains
- 0.99 Duration of Raft store events: The time consumed by Raftstore events (P99)
- Process ready duration: The time consumed for processes to be ready in Raft
- Process ready duration per server: The time consumed for peer processes to be ready in Raft per TiKV instance. It should be less than 2 seconds (P99.99).
- Max Duration of Raft store events: The time consumed by the slowest Raftstore event.
- Replica read lock checking duration: The time consumed for checking locks when processing Replica Read.
- Peer msg length distribution: The number of messages processed by each Region in each TiKV instance at a time. The more messages, the busier the peer is.

![TiKV Dashboard - Raft process metrics](/media/tikv-dashboard-raft-process.png)
### Raft message

- Sent messages per server: The number of Raft messages sent by each TiKV instance per second
- Flush messages per server: The number of Raft messages flushed by the Raft client in each TiKV instance per second
- Receive messages per server: The number of Raft messages received by each TiKV instance per second
- Messages: The number of Raft messages sent per type per second
- Vote: The number of Vote messages sent in Raft per second
- Raft dropped messages: The number of dropped Raft messages per type per second

![TiKV Dashboard - Raft message metrics](/media/tikv-dashboard-raft-message.png)
### Raft propose

- Raft apply proposals per ready: The histogram of the number of proposals that each ready operation contains in a batch while applying proposal.
- Raft read/write proposals: The number of proposals per type per second
- Raft read proposals per server: The number of read proposals made by each TiKV instance per second
- Raft write proposals per server: The number of write proposals made by each TiKV instance per second
- Propose wait duration: The histogram of waiting time of each proposal
- Propose wait duration per server: The histogram of waiting time of each proposal per TiKV instance
- Apply wait duration: The histogram of apply time of each proposal
- Apply wait duration per server: The histogram of apply time of each proposal per TiKV instance
- Raft log speed: The average rate at which peers propose logs

![TiKV Dashboard - Raft propose metrics](/media/tikv-dashboard-raft-propose.png)
### Raft admin

- Admin proposals: The number of admin proposals per second
- Admin apply: The number of processed apply commands per second
- Check split: The number of Raftstore split check commands per second
- 99.99% Check split duration: The time consumed when running split check commands (P99.99)

![TiKV Dashboard - Raft admin metrics](/media/tikv-dashboard-raft-admin.png)
### Local reader

- Local reader requests: The number of total requests and the number of rejections from the local read thread

![TiKV Dashboard - Local reader metrics](/media/tikv-dashboard-local-reader.png)
### Unified Read Pool

- Time used by level: The time consumed for each level in the unified read pool. Level 0 means small queries.
- Level 0 chance: The proportion of level 0 tasks in unified read pool
- Running tasks: The number of tasks running concurrently in the unified read pool
### Storage

- Storage command total: The number of received command by type per second
- Storage async request error: The number of engine asynchronous request errors per second
- Storage async snapshot duration: The time consumed by processing asynchronous snapshot requests. It should be less than `1s` in `.99`.
- Storage async write duration: The time consumed by processing asynchronous write requests. It should be less than `1s` in `.99`.

![TiKV Dashboard - Storage metrics](/media/tikv-dashboard-storage.png)
