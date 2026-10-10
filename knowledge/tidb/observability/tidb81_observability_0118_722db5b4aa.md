# TiFlash monitoring dashboards and metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/monitor-tiflash.md`
- Source Title: `Monitor the TiFlash Cluster`
- Source Heading Path: `Monitor the TiFlash Cluster | Monitor the TiFlash Cluster > Server | Monitor the TiFlash Cluster > Coprocessor | Monitor the TiFlash Cluster > Task Scheduler | Monitor the TiFlash Cluster > DDL | Monitor the TiFlash Cluster > Storage | Monitor the TiFlash Cluster > Storage Write Stall | Monitor the TiFlash Cluster > Raft`
- Source Line Ranges: `5-106`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`, `pd`, `tiup`, `dashboard`
- Topic Tags: `monitoring`, `grafana`, `metrics`, `server`, `coprocessor`, `task-scheduler`, `ddl`, `storage`, `write-stall`, `raft`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0118_722db5b4aa`
- Source ID: `tidb-docs-8.1:tiflash/monitor-tiflash.md#monitor-the-tiflash-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `037ad5e1f6e34d080ada6c02384e584cfd65283e937500865df3cc53fdfe16ed`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/monitor-tiflash#monitor-the-tiflash-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/monitor-tiflash.md

## Retrieval Guidance

- Use When: Use this chunk when identifying what the TiFlash Grafana dashboards show and what TiFlash-Summary metrics mean across Server, Coprocessor, Task Scheduler, DDL, Storage, Storage Write Stall, and Raft sections.
- Retrieval Keywords: TiFlash-Summary, TiFlash-Proxy-Summary, TiFlash-Proxy-Details, Monitor the TiFlash Cluster, Grafana dashboard, Server, Coprocessor, Task Scheduler, DDL, Storage, Storage Write Stall, Raft, Store size, Available size, Capacity size, Uptime, Memory, CPU Usage, FSync OPS, File Open OPS, Opened File Count, Request QPS, Executor QPS, Request Duration, Error QPS, meet_lock, region_not_found, epoch_not_match, kv_client_error, internal_error, Request Handle Duration, Response Bytes/Seconds, Cop task memory usage, Handling Request Number, Threads of RPC, Max Threads of RPC, Min TSO, Estimated Thread Usage and Limit, Active and Waiting Queries Count, Active and Waiting Tasks Count, Hard Limit Exceeded Count, Task Waiting Duration, Schema Version, Schema Apply OPM, schema diff, diff apply, full apply, failed apply, Schema Internal DDL OPM, Schema Apply Duration, Write Command OPS, Write Amplification, Read Tasks OPS, Rough Set Filter Rate, Internal Tasks OPS, Page GC Tasks OPM, Disk Write OPS, Disk Read OPS, Write flow, Read flow, Write & Delta Management Throughput, throughput_write, throughput_delta-management, Write Stall Duration, Write Throughput By Instance, Write Command OPS By Instance, write block, delete_range, ingest, Read Index OPS, read_index, Read Index Duration, Wait Index Duration, wait_index
- Follow-up Guidance: The source also states that TiFlash-Proxy-Summary and TiFlash-Proxy-Details mainly show Raft layer information, and related metrics are detailed in Key Monitoring Metrics of TiKV.
- Classification Note: This chunk is classified as observability for self-managed TiFlash because it defines dashboard panels and monitoring metrics used to observe TiFlash status and behavior.

## Official Source Content

# Monitor the TiFlash Cluster

This document describes the monitoring items of TiFlash.

If you use TiUP to deploy the TiDB cluster, the monitoring system (Prometheus & Grafana) is deployed at the same time. For more information, see [Overview of the Monitoring Framework](https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework).

The Grafana dashboard is divided into a series of sub dashboards which include Overview, PD, TiDB, TiKV, and Node\_exporter. A lot of metrics are there to help you diagnose.

TiFlash has three dashboard panels: **TiFlash-Summary**, **TiFlash-Proxy-Summary**, and **TiFlash-Proxy-Details**. The metrics on these panels indicate the current status of TiFlash. The **TiFlash-Proxy-Summary** and **TiFlash-Proxy-Details** panels mainly show the information of the Raft layer and the metrics are detailed in [Key Monitoring Metrics of TiKV](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard).

> **Note:**
>
> It is recommended that you use TiDB v4.0.5 or later versions for improved monitor on TiFlash.

The following sections introduce the default monitoring information of **TiFlash-Summary**.
## Server

- Store size: The storage size used by each TiFlash instance.
- Available size: The storage size available for each TiFlash instance.
- Capacity size: The storage capacity for each TiFlash instance.
- Uptime: The runtime of TiFlash since last restart.
- Memory: The memory usage per TiFlash instance.
- CPU Usage: The CPU utilization per TiFlash instance.
- FSync OPS: The number of fsync operations per TiFlash instance per second.
- File Open OPS: The number of `open` operations per TiFlash instance per second.
- Opened File Count: The number of file descriptors currently opened by each TiFlash instance.

> **Note:**
>
> Store size, FSync OPS, File Open OPS, and Opened File Count currently only cover the monitoring information of the TiFlash storage layer and do not cover that in TiFlash-Proxy.
## Coprocessor

- Request QPS: The number of coprocessor requests received by all TiFlash instances. `batch` is the number of batch requests. `batch_cop` is the number of coprocessor requests in the batch requests. `cop` is the number of coprocessor requests that are sent directly via the coprocessor interface. `cop_dag` is the number of dag requests in all coprocessor requests. `super_batch` is the number of requests to enable the Super Batch feature.
- Executor QPS: The number of each type of dag executors in the requests received by all TiFlash instances. `table_scan` is the table scan executor. `selection` is the selection executor. `aggregation` is the aggregation executor. `top_n` is the `TopN` executor. `limit` is the limit executor.
- Request Duration: The total duration of all TiFlash instances processing coprocessor requests. The total duration is from the time that the coprocessor request is received to the time that the response to the request is completed.
- Error QPS: The number of errors of all TiFlash instances processing coprocessor requests. `meet_lock` means that the read data is locked. `region_not_found` means that the Region does not exist. `epoch_not_match` means the read Region epoch is inconsistent with the local epoch. `kv_client_error` means that the communication with TiKV returns an error. `internal_error` is the internal system error of TiFlash. `other` is other types of errors.
- Request Handle Duration: The duration of all TiFlash instances processing coprocessor requests. The processing time is from starting to execute the coprocessor request to completing the execution.
- Response Bytes/Seconds: The total bytes of the response from all TiFlash instances.
- Cop task memory usage: The total memory usage of all TiFlash instances processing coprocessor requests.
- Handling Request Number: The total number of all TiFlash instances processing coprocessor requests. The classification of the requests is the same as that of Request QPS.
- Threads of RPC: The real-time number of RPC threads used in each TiFlash instance.
- Max Threads of RPC: The maximum number of RPC threads recently used in each TiFlash instance.
- Threads: The real-time number of threads used in each TiFlash instance.
- Max Threads: The maximum number of threads recently used in each TiFlash instance.
## Task Scheduler

- Min TSO: The minimum TSO among all queries running on each TiFlash instance. This value ensures that queries with the minimum TSO can be scheduled to run. When no queries are running, this value is the maximum unsigned 64-bit integer.
- Estimated Thread Usage and Limit: The estimated amount of threads used by all queries running on each TiFlash instance, and the soft and hard limits on the amount.
- Active and Waiting Queries Count: The amount of running queries and that of waiting queries on each TiFlash instance.
- Active and Waiting Tasks Count: The amount of running tasks and that of waiting tasks on each TiFlash instance.
- Hard Limit Exceeded Count: Times that the estimated amount of threads used by queries running on each TiFlash instance exceeds the hard limit.
- Task Waiting Duration: The duration from task initialization to task scheduling on each TiFlash instance.
## DDL

- Schema Version: The version of the schema currently cached in each TiFlash instance.
- Schema Apply OPM: The number of TiDB `schema diff` synchronized in `apply` operations by all TiFlash instances per minute. This item includes the count of three types of `apply`: `diff apply`, `full apply`, and `failed apply`. `diff apply` is the normal process of a single apply. If `diff apply` fails, `failed apply` increases by `1`, and TiFlash rolls back to `full apply` and pulls the latest schema information to update the schema version of TiFlash.
- Schema Internal DDL OPM: The number of specific DDL operations executed per minute in all TiFlash instances.
- Schema Apply Duration: The time used for a single `apply schema` operation in all TiFlash instances.
## Storage

- Write Command OPS: The number of write requests received per second by the storage layer of all TiFlash instances.
- Write Amplification: Write amplification of each TiFlash instance (the actual bytes of disk writes divided by the written bytes of logical data). `total` is the write amplification since this start, and `5min` is the write amplification in the last 5 minutes.
- Read Tasks OPS: The number of read tasks in the storage layer per second for each TiFlash instance.
- Rough Set Filter Rate: The proportion of the number of packets read by each TiFlash instance in the last minute that are filtered by the rough set index of the storage layer.
- Internal Tasks OPS: The number of times that all TiFlash instances perform internal data sorting tasks per second.
- Internal Tasks Duration: The time consumed by all TiFlash instances for internal data sorting tasks.
- Page GC Tasks OPM: The number of times that all TiFlash instances perform Delta data sorting tasks per minute.
- Page GC Tasks Duration: The distribution of time consumed by all TiFlash instances to perform Delta data sorting tasks.
- Disk Write OPS: The number of disk writes per second by all TiFlash instances.
- Disk Read OPS: The number of disk reads per second by all TiFlash instances.
- Write flow: The traffic of disk writes by all TiFlash instances.
- Read flow: The traffic of disk reads by all TiFlash instances.

> **Note:**
>
> These metrics only cover the monitoring information of the TiFlash storage layer and do not cover that in TiFlash-Proxy.
## Storage Write Stall

- Write & Delta Management Throughput: The throughput of write and data compaction for all instances.
    - `throughput_write` means the throughput of data synchronization through Raft.
    - `throughput_delta-management` means the throughput of data compaction.
    - `total_write` means the total bytes written since the last start.
    - `total_delta-management` means the total bytes of data compacted since the last start.
- Write Stall Duration: The stall duration of write and removing Region data (deleting ranges) by instance.
- Write Throughput By Instance: The throughput of write by instance. It includes the throughput by applying the Raft write commands and Raft snapshots.
- Write Command OPS By Instance: The total count of different kinds of commands received by instance.
    - `write block` means the data logs synchronized through Raft.
    - `delete_range` means that some Regions are removed from or moved to this instance.
    - `ingest` means some Region snapshots are applied to this instance.
## Raft

- Read Index OPS: The number of times that each TiFlash instance triggers the `read_index` request per second, which equals to the number of Regions triggered.
- Read Index Duration: The time used by `read_index` for all TiFlash instances. Most time is used for interaction with the Region leader and retry.
- Wait Index Duration: The time used by `wait_index` for all TiFlash instances, namely the time used to wait until local index >= read_index after the `read_index` request is received.
