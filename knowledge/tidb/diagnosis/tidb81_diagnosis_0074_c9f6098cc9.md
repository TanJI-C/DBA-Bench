# TiCDC Kafka broken pipe errors

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-faq.md`
- Source Title: `TiCDC FAQs`
- Source Heading Path: `TiCDC FAQs > Why do TiCDC replication tasks to Kafka often fail with `broken pipe` errors?`
- Source Line Ranges: `503-519`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `ecosystem`
- Topic Tags: `kafka`, `broken pipe`, `sarama`, `latency`, `idle timeout`, `restart`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0074_c9f6098cc9`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-faq.md#why-do-ticdc-replication-tasks-to-kafka-often-fail-with-broken-pipe-errors`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `094843204da503d72e2630633dd0e1023f4b81ccd4795b2d5121e63bfa6086c4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#why-do-ticdc-replication-tasks-to-kafka-often-fail-with-broken-pipe-errors
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-faq.md

## Retrieval Guidance

- Use When: Use this chunk when investigating TiCDC changefeeds to Kafka that fail with `write: broken pipe` errors after idle connections are closed.
- Retrieval Keywords: write: broken pipe, TiCDC Kafka, Sarama, retry count to 0, automatic retry mechanism disabled, out-of-order data, connection idle timeout, connections.max.idle.ms, Kafka broker configuration file, changefeed automatically restarts, replication latency lag within 30 seconds, restart Kafka
- Follow-up Guidance: The source states that TiCDC automatically restarts the affected changefeed, and if latency sensitivity matters, the Kafka broker `connections.max.idle.ms` can be increased and Kafka restarted to apply the change.
- Classification Note: This is classified as diagnosis content because the official content describes why `broken pipe` occurs in TiCDC replication to Kafka and what behavior follows when the changefeed fails and restarts.

## Official Source Content

## Why do TiCDC replication tasks to Kafka often fail with `broken pipe` errors?

TiCDC uses the Sarama client to replicate data to Kafka. To avoid out-of-order data, TiCDC disables the automatic retry mechanism of Sarama (by setting the retry count to 0). As a result, if the connection between TiCDC and Kafka is closed by Kafka after being idle for some time, subsequent writes from TiCDC will trigger a `write: broken pipe` error, causing the replication task to fail.

Although the changefeed might fail due to this error, TiCDC automatically restarts the affected changefeed, so the replication task can continue running normally. Note that during the restart process, the replication latency (lag) of the changefeed might temporarily increase by a small amount, typically within 30 seconds, before automatically returning to normal.

If your application is highly sensitive to changefeed latency, it is recommended to do the following:

1. Increase the Kafka connection idle timeout in the Kafka broker configuration file. For example:

    ```properties
    connections.max.idle.ms=86400000  # Set to 1 day
    ```

    It is recommended to adjust the value of `connections.max.idle.ms` according to your actual replication workload. For example, if a TiCDC changefeed always replicates data within several minutes, you can set `connections.max.idle.ms` to several minutes instead of a very large value.

2. Restart Kafka to apply the configuration change. This prevents connections from being closed prematurely and helps reduce `broken pipe` errors.
