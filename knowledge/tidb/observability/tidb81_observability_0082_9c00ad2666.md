# TiCDC dashboard monitoring metrics by panel

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/monitor-ticdc.md`
- Source Title: `TiCDC Monitoring Metrics Details`
- Source Heading Path: `TiCDC Monitoring Metrics Details | TiCDC Monitoring Metrics Details > Server | TiCDC Monitoring Metrics Details > Changefeed | TiCDC Monitoring Metrics Details > Events | TiCDC Monitoring Metrics Details > TiKV`
- Source Line Ranges: `5-123`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `dashboard`, `pd`, `tikv`, `tiup`
- Topic Tags: `monitoring`, `grafana`, `metrics`, `dashboard`, `changefeed`, `replication`, `events`, `latency`, `throughput`, `resource-usage`, `tikv`, `pd`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0082_9c00ad2666`
- Source ID: `tidb-docs-8.1:ticdc/monitor-ticdc.md#ticdc-monitoring-metrics-details`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `224329f4d91ed5c8fd82b78eda8dc4bb7a75b2cc73265ea645740d43cd0a8a19`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/monitor-ticdc#ticdc-monitoring-metrics-details
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/monitor-ticdc.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiCDC dashboard panel layout or the meaning of TiCDC monitoring metrics in the Server, Changefeed, Events, or TiKV panels for a replication task.
- Retrieval Keywords: TiCDC Monitoring Metrics Details, TiCDC dashboard, Server panel, Changefeed panel, Events panel, TiKV panel, Uptime, Goroutine count, Open FD count, Ownership, Ownership history, CPU usage, Memory usage, Changefeed table count, Processor resolved ts, Table resolved ts, Changefeed checkpoint, PD etcd requests/s, Exit error count/m, Changefeed checkpoint lag, Processor resolved ts lag, Sink write duration, Sink write duration percentile, Flush sink duration, Flush sink duration percentile, MySQL sink conflict detect duration, MySQL sink conflict detect duration percentile, MySQL sink worker load, Changefeed catch-up ETA, Eventfeed count, Event size percentile, Eventfeed error/m, KV client receive events/s, Puller receive events/s, Puller output events/s, Sink flush rows/s, Puller buffer size, Entry sorter buffer size, Processor/Mounter buffer size, Sink row buffer size, Entry sorter sort duration, Entry sorter sort duration percentile, Entry sorter merge duration, Entry sorter merge duration percentile, Mounter unmarshal duration, Mounter unmarshal duration percentile, KV client dispatch events/s, KV client batch resolved size, CDC endpoint CPU, CDC worker CPU, Min resolved ts, Min resolved region, Resolved ts lag duration percentile, Initial scan duration, Initial scan duration percentile, Memory without block cache, CDC pending bytes in memory, Captured region count, cdc cli changefeed create, simple-replication-task
- Follow-up Guidance: The source also gives an example changefeed creation command and notes that a TiCDC sub-dashboard is available when the TiDB cluster is deployed using TiUP.
- Classification Note: This chunk is classified as observability for the TiCDC component because it describes Grafana dashboard panels and metric meanings for monitoring TiCDC, TiKV, and replication progress.

## Official Source Content

# TiCDC Monitoring Metrics Details

If you use TiUP to deploy the TiDB cluster, you can see a sub-dashboard for TiCDC in the monitoring system which is deployed at the same time. You can get an overview of TiCDC's current status from the TiCDC dashboard, where the key metrics are displayed. This document provides a detailed description of these key metrics.

The metric description in this document is based on the following replication task example, which replicates data to MySQL using the default configuration.

```shell
cdc cli changefeed create --server=http://10.0.10.25:8300 --sink-uri="mysql://root:123456@127.0.0.1:3306/" --changefeed-id="simple-replication-task"
```

The TiCDC dashboard contains four monitoring panels. See the following screenshot:

![TiCDC Dashboard - Overview](/media/ticdc/ticdc-dashboard-overview.png)

The description of each panel is as follows:

- [**Server**](#server): The summary information of TiKV nodes and TiCDC nodes in the TiDB cluster
- [**Changefeed**](#changefeed): The detailed information of TiCDC replication tasks
- [**Events**](#events): The detail information about the data flow within the TiCDC cluster
- [**TiKV**](#tikv): TiKV information related to TiCDC
## Server

The following is an example of the **Server** panel:

![TiCDC Dashboard - Server metrics](/media/ticdc/ticdc-dashboard-server.png)

The description of each metric in the **Server** panel is as follows:

- Uptime: The time for which TiKV nodes and TiCDC nodes have been running
- Goroutine count: The number of goroutines of a TiCDC node
- Open FD count: The number of file handles opened by TiCDC nodes
- Ownership: The current status of nodes in the TiCDC cluster
- Ownership history: The ownership history of the TiCDC cluster
- CPU usage: The CPU usage of TiCDC nodes
- Memory usage: The memory usage of TiCDC nodes
## Changefeed

The following is an example of the **Changefeed** panel:

![TiCDC Dashboard - Changefeed metrics 1](/media/ticdc/ticdc-dashboard-changefeed-1.png)

- Changefeed table count: The number of tables that each TiCDC node needs to replicate in the replication task
- Processor resolved ts: The timestamps that have been resolved in the TiCDC cluster
- Table resolved ts: The replication progress of each table in the replication task
- Changefeed checkpoint: The progress of replicating data to the downstream. Normally, the green bars are connected to the yellow line
- PD etcd requests/s: The number of requests that a TiCDC node sends to PD per second
- Exit error count/m: The number of errors that interrupt the replication task per minute
- Changefeed checkpoint lag: The progress lag of data replication (the unit is second) between the upstream and the downstream
- Processor resolved ts lag: The progress lag of data replication (the unit is second) between the upstream and TiCDC nodes

![TiCDC Dashboard - Changefeed metrics 2](/media/ticdc/ticdc-dashboard-changefeed-2.png)

- Sink write duration: The histogram of the time spent by TiCDC writing a transaction change to the downstream
- Sink write duration percentile: The time (P95, P99, and P999) spent by TiCDC writing a transaction change to the downstream within one second
- Flush sink duration: The histogram of the time spent by TiCDC asynchronously flushing data to the downstream
- Flush sink duration percentile: The time (P95, P99, and P999) spent by TiCDC asynchronously flushing data to the downstream within one second

![TiCDC Dashboard - Changefeed metrics 3](/media/ticdc/ticdc-dashboard-changefeed-3.png)

- MySQL sink conflict detect duration: The histogram of the time spent on detecting MySQL sink conflicts
- MySQL sink conflict detect duration percentile: The time (P95, P99, and P999) spent on detecting MySQL sink conflicts within one second
- MySQL sink worker load: The workload of MySQL sink workers of TiCDC nodes

![TiCDC Dashboard - Changefeed metrics 4](/media/ticdc/ticdc-dashboard-changefeed-4.png)

- Changefeed catch-up ETA: The estimated time needed for the replication task to catch up with the upstream cluster data. When the upstream write speed is faster than the TiCDC replication speed, the metric might be extremely large. Because TiCDC replication speed is subject to many factors, this metric is for reference only and might not be the actual replication time.
## Events

The following is an example of the **Events** panel:

![TiCDC Dashboard - Events metrics 2](/media/ticdc/ticdc-dashboard-events-1.png)
![TiCDC Dashboard - Events metrics 2](/media/ticdc/ticdc-dashboard-events-2.png)
![TiCDC Dashboard - Events metrics 2](/media/ticdc/ticdc-dashboard-events-3.png)

The description of each metric in the **Events** panel is as follows:

- Eventfeed count: The number of Eventfeed RPC requests of TiCDC nodes
- Event size percentile: The event size (P95, P99, and P999) which TiCDC receives from TiKV within one second
- Eventfeed error/m: The number of errors reported by Eventfeed RPC requests of TiCDC nodes per minute
- KV client receive events/s: The number of events that the KV client module of TiCDC nodes receives from TiKV per second
- Puller receive events/s: The number of events that the Puller module of TiCDC nodes receives from the KV client per second
- Puller output events/s: The number of events that the Puller module of TiCDC nodes sends to the Sorter module per second
- Sink flush rows/s: The number of events that TiCDC nodes write to the downstream per second
- Puller buffer size: The number of events that TiCDC nodes cache in the Puller module
- Entry sorter buffer size: The number of events that TiCDC nodes cache in the Sorter module
- Processor/Mounter buffer size: The number of events that TiCDC nodes cache in the Processor module and the Mounter module
- Sink row buffer size: The number of events that TiCDC nodes cache in the Sink module
- Entry sorter sort duration: The histogram of the time spent by TiCDC nodes sorting events
- Entry sorter sort duration percentile: The time (P95, P99, and P999) spent by TiCDC sorting events within one second
- Entry sorter merge duration: The histogram of the time spent by TiCDC nodes merging sorted events
- Entry sorter merge duration percentile: The time (P95, P99, and P999) spent by TiCDC merging sorted events within one second
- Mounter unmarshal duration: The histogram of the time spent by TiCDC nodes unmarshalling events
- Mounter unmarshal duration percentile: The time (P95, P99, and P999) spent by TiCDC unmarshalling events within one second
- KV client dispatch events/s: The number of events that the KV client module dispatches among the TiCDC nodes
- KV client batch resolved size: The batch size of resolved timestamp messages that TiKV sends to TiCDC
## TiKV

The following is an example of the **TiKV** panel:

![TiCDC Dashboard - TiKV metrics 1](/media/ticdc/ticdc-dashboard-tikv-1.png)
![TiCDC Dashboard - TiKV metrics 2](/media/ticdc/ticdc-dashboard-tikv-2.png)

The description of each metric in the **TiKV** panel is as follows:

- CDC endpoint CPU: The CPU usage of the CDC endpoint threads on TiKV nodes
- CDC worker CPU: The CPU usage of the CDC worker threads on TiKV nodes
- Min resolved ts: The minimum resolved timestamp on TiKV nodes
- Min resolved region: The Region ID of the minimum resolved timestamp on TiKV nodes
- Resolved ts lag duration percentile: The lag between the minimum resolved timestamp on TiKV nodes and the current time
- Initial scan duration: The histogram of the time spent on incremental scan when TiKV nodes connect to TiCDC nodes
- Initial scan duration percentile: The time (P95, P99, and P999) spent on the incremental scan of TiKV nodes within one second
- Memory without block cache: The memory usage of TiKV nodes excluding the RocksDB block cache
- CDC pending bytes in memory: The memory usage of CDC module on TiKV nodes
- Captured region count: The number of event-capturing Regions on TiKV nodes
