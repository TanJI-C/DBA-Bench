# TiCDC Summary Dashboard panels and monitoring metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-summary-monitor.md`
- Source Title: `TiCDC Monitoring Metrics Summary`
- Source Heading Path: `TiCDC Monitoring Metrics Summary | TiCDC Monitoring Metrics Summary > Server panel | TiCDC Monitoring Metrics Summary > Changefeed panel | TiCDC Monitoring Metrics Summary > Dataflow panel | TiCDC Monitoring Metrics Summary > Transaction Sink panel | TiCDC Monitoring Metrics Summary > MQ Sink panel | TiCDC Monitoring Metrics Summary > Cloud Storage Sink panel | TiCDC Monitoring Metrics Summary > Redo panel`
- Source Line Ranges: `5-105`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`, `sql`, `shared`
- Topic Tags: `grafana`, `dashboard`, `monitoring`, `metrics`, `changefeed`, `latency`, `dataflow`, `sink`, `kafka`, `cloud-storage`, `redo-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0084_b4f54bc8d3`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-summary-monitor.md#ticdc-monitoring-metrics-summary`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `af4837b54fe9bf981c0663abadcf3a0aa89d8cf1bfc1c0d724b90ac64f88f38a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-summary-monitor#ticdc-monitoring-metrics-summary
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-summary-monitor.md

## Retrieval Guidance

- Use When: Use this chunk when identifying what the TiCDC Summary Dashboard panels show and which TiCDC monitoring metrics indicate server status, changefeed latency, internal dataflow, and sink or redo performance.
- Retrieval Keywords: TiCDC Summary Dashboard, TiCDC Monitoring Metrics Summary, Server panel, Changefeed panel, Dataflow panel, Transaction Sink panel, MQ Sink panel, Cloud Storage Sink panel, Redo panel, Uptime, CPU usage, Memory usage, Changefeed checkpoint lag, Changefeed resolved ts lag, Puller output events/s, Puller output events, Sorter output events/s, Sorter output event, Mounter output events/s, Mounter output event, Sink flush rows/s, Sink flush rows, Backend Flush Duration, Full Flush Duration, Worker Send Message Duration Percentile, Kafka Ongoing Bytes, Write Bytes/s, File Count, Redo Write rows/s, Redo Write byte/s, Redo flush log duration, Redo flushall duration, downstream MySQL or TiDB, downstream is Kafka, downstream is Cloud Storage, Redo Log feature is enabled
- Follow-up Guidance: The source also states panel-specific display conditions and explains how lag or throughput metrics relate to upstream pulling, downstream flushing, queueing time, and redo write capacity.
- Classification Note: This is classified as observability for the TiCDC component because the content describes Grafana dashboard panels and monitoring metrics for TiCDC servers, changefeeds, internal modules, sinks, and redo behavior.

## Official Source Content

# TiCDC Monitoring Metrics Summary

Starting from v7.0.0, when you deploy Grafana using TiUP, the TiCDC Summary Dashboard is automatically added to the Grafana monitoring page. Through this dashboard, you can quickly understand the status of TiCDC servers and changefeeds.

The following image shows the monitoring panels of the TiCDC Summary Dashboard:

![TiCDC Summary Dashboard - Overview](/media/ticdc/ticdc-summary-monitor.png)

Each monitoring panel is described as follows:

- Server: summary of TiCDC nodes in the cluster.
- Changefeed: the latency and status information of TiCDC changefeeds.
- Dataflow: statistics of data changes processed by TiCDC internal modules.
- Transaction Sink: the write latency of the downstream MySQL or TiDB.
- MQ Sink: the write latency of the downstream MQ system.
- Cloud Storage Sink: the write speed of the downstream cloud storage.
- Redo: the write latency when the redo feature is enabled.
## Server panel

The **Server** panel is as follows:

![TiCDC Summary Dashboard - Server metrics](/media/ticdc/ticdc-summary-monitor-server.png)

- **Uptime**: the time that TiCDC nodes have been running.
- **CPU usage**: the CPU usage of TiCDC nodes.
- **Memory usage**: the memory usage of TiCDC nodes.
## Changefeed panel

The **Changefeed** panel is as follows:

![TiCDC Summary Dashboard - Changefeed metrics](/media/ticdc/ticdc-summary-monitor-changefeed.png)

- **Changefeed checkpoint lag**: indicates the data replication latency between the upstream TiDB cluster and the downstream system, measured in time. In general, this metric reflects the overall health of the data replication task. Usually, the smaller the lag, the better the status of the replication task. When the lag increases, it usually indicates that the replication ability of the changefeed or the consumption ability of the downstream system cannot keep up with the write speed of the upstream.
- **Changefeed resolved ts lag**: indicates the data latency between the upstream TiDB cluster and the TiCDC node, measured in time. This metric reflects the ability of the changefeed to pull the data changes from the upstream. When the lag increases, it means that the changefeed cannot pull the data changes generated by the upstream in time.
## Dataflow panel

![TiCDC Summary Dashboard - Puller metrics](/media/ticdc/ticdc-summary-monitor-dataflow-puller.png)

- **Puller output events/s**: the number of data changes output by the Puller module to the Sorter module per second in the TiCDC node. This metric reflects the speed at which TiCDC pulls the data changes from the upstream.
- **Puller output events**: the total number of data changes output by the Puller module to the Sorter module in the TiCDC node.

![TiCDC Summary Dashboard - Sorter metrics](/media/ticdc/ticdc-summary-monitor-dataflow-sorter.png)

- **Sorter output events/s**: the number of data changes output by the Sorter module per second to the Sink module in the TiCDC node. Note that the data output rate of Sorter is affected by the Sink module. Therefore, when you find that the output rate of the Sorter module is lower than that of the Puller module, it does not necessarily mean that the sorting speed of the Sorter module is too slow. You need to first observe the metrics related to the Sink module to confirm whether the Sink module takes a long time to flush data, resulting in a decrease in Sorter module output.

- **Sorter output event**: the total number of data changes output by the Sorter module to the Sink module in the TiCDC node.

![TiCDC Summary Dashboard - Mounter metrics](/media/ticdc/ticdc-summary-monitor-dataflow-mounter.png)

- **Mounter output events/s**: the number of data changes decoded by the Mounter module per second in the TiCDC node. When the upstream data changes involve a large number of fields, the decoding speed of the Mounter module might be affected.

- **Mounter output event**: the total number of data changes decoded by the Mounter module in the TiCDC node.

![TiCDC Summary Dashboard - Sink metrics](/media/ticdc/ticdc-summary-monitor-dataflow-sink.png)

- **Sink flush rows/s**: the number of data changes output by the Sink module to the downstream per second in the TiCDC node. This metric reflects the speed at which the data changes are replicated to the downstream. When **Sink flush rows/s** is lower than **Puller output events/s**, the replication latency might increase.

- **Sink flush rows**: the total number of data changes output by the Sink module to the downstream in the TiCDC node.
## Transaction Sink panel

The **Transaction Sink** panel displays data only when the downstream is MySQL or TiDB.

![TiCDC Summary Dashboard - Transaction Sink metrics](/media/ticdc/ticdc-summary-monitor-transaction-sink.png)

- **Backend Flush Duration**: the duration that the TiCDC Transaction Sink module takes to execute a SQL statement on the downstream. By observing this metric, you can determine whether the performance of the downstream is the bottleneck of the replication speed. Generally, the p999 value should be below 500 ms. When the value exceeds this limit, the replication speed might be affected, resulting in an increase in the Changefeed checkpoint lag.

- **Full Flush Duration**: the total duration consumed by each transaction in TiCDC from sorting by Sorter to sending downstream. By subtracting the **Backend Flush Duration** value from this value, you can get the total queueing time of a transaction before it is executed on the downstream. If the queueing time is too long, you can consider allocating more memory quota to the replication task.
## MQ Sink panel

The **MQ Sink** panel displays data only when the downstream is Kafka.

![TiCDC Summary Dashboard - Transaction Sink metrics](/media/ticdc/ticdc-summary-monitor-mq-sink.png)

- **Worker Send Message Duration Percentile**: The latency of TiCDC MQ Sink worker sending data to the downstream.
- **Kafka Ongoing Bytes**: The speed at which TiCDC MQ Sink sends data to the downstream.
## Cloud Storage Sink panel

The **Cloud Storage Sink** panel displays data only when the downstream is Cloud Storage.

![TiCDC Summary Dashboard - Transaction Sink metrics](/media/ticdc/ticdc-summary-monitor-cloud-storage.png)

- **Write Bytes/s**: The speed at which the Cloud Storage Sink module writes data to the downstream.
- **File Count**: the total number of files written by the Cloud Storage Sink module.
## Redo panel

The **Redo** panel displays data only when the Redo Log feature is enabled.

![TiCDC Summary Dashboard - Transaction Sink metrics](/media/ticdc/ticdc-summary-monitor-redo.png)

- **Redo Write rows/s**: the number of rows written per second by the Redo module. When the Redo feature is enabled, if the latency of a replication task increases, you can observe whether there is a significant difference between this metric and the value of Puller Output event/s. If so, the increase in latency might be due to the insufficient writing capacity of the Redo module.
- **Redo Write byte/s**: the speed at which data is written per second by the Redo module.
- **Redo flush log duration**: the time taken for the Redo module to flush data to the downstream. If this metric value is high, this operation might affect the replication speed.
- **Redo flushall duration**: the total time that data changes stay in the Redo module.
