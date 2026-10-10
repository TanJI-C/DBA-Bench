# TiCDC performance overview metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-performance-overview-dashboard.md`
- Source Title: `Key Metrics on Performance Overview`
- Source Heading Path: `Key Metrics on Performance Overview > CDC`
- Source Line Ranges: `191-213`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `dashboard`
- Topic Tags: `cpu`, `memory`, `goroutines`, `changefeed`, `checkpoint-lag`, `resolved-ts`, `status`, `puller`, `sorter`, `mounter`, `sink`, `kafka`, `latency`, `throughput`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0054_c31b9fd58f`
- Source ID: `tidb-docs-8.1:grafana-performance-overview-dashboard.md#cdc`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `604f7342816f300144ca87d1e365466d029ce308821718cb57f8d4f6e0e559e7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-performance-overview-dashboard#cdc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-performance-overview-dashboard.md

## Retrieval Guidance

- Use When: Use this chunk when identifying what TiCDC metrics and status codes are shown on the Performance Overview dashboard for resource usage, replication lag, changefeed state, pipeline event rates, sink latency, and Kafka traffic.
- Retrieval Keywords: TiCDC performance overview metrics, Performance Overview CDC, CPU usage per TiCDC node, Memory usage per TiCDC node, Goroutine count, Changefeed checkpoint lag, Changefeed resolved ts lag, status of changefeeds, 0 Normal, 1 Error, 2 Failed, 3 Stopped, 4 Finished, -1 Unknown, Puller output events/s, Sorter output events/s, Mounter output events/s, Table sink output events/s, SinkV2 - Sink flush rows/s, Transaction Sink Full Flush Duration, MQ Worker Send Message Duration Percentile, Kafka Outgoing Bytes
- Follow-up Guidance: The chunk includes the numeric meanings of changefeed status values and names the TiCDC pipeline stages Puller, Sorter, Mounter, and Sink used by the dashboard metrics.
- Classification Note: This is classified as observability for the TiCDC component because the content lists dashboard metrics, replication lag indicators, status codes, and throughput or latency measurements.

## Official Source Content

## CDC

- CPU usage: The CPU usage per TiCDC node.
- Memory usage: The memory usage per TiCDC node.
- Goroutine count: The number of goroutines per TiCDC node.
- Changefeed checkpoint lag: The progress lag of data replication (the unit is second) between the upstream and the downstream.
- Changefeed resolved ts lag: The progress lag of data replication (the unit is second) between the upstream and TiCDC nodes.
- The status of changefeeds:

    - 0: Normal
    - 1: Error
    - 2: Failed
    - 3: Stopped
    - 4: Finished
    - -1: Unknown
- Puller output events/s: The number of rows that the Puller module of TiCDC nodes sends to the Sorter module per second.
- Sorter output events/s: The number of rows that the Sorter module of TiCDC nodes sends to the Mounter module per second.
- Mounter output events/s: The number of rows that the Mounter module of TiCDC nodes sends to the Sink module per second.
- Table sink output events/s: The number of rows that the Table Sorter module of the TiCDC nodes sends to the Sink module per second.
- SinkV2 - Sink flush rows/s: The number of rows that the Sink module in the TiCDC node sends to the downstream per second.
- Transaction Sink Full Flush Duration: The average latency and p999 latency of writing downstream transactions by the MySQL Sink of TiCDC nodes.
- MQ Worker Send Message Duration Percentile: The latency of sending messages by MQ worker when the downstream is Kafka.
- Kafka Outgoing Bytes: The traffic of writing downstream transactions in MQ Workload.
