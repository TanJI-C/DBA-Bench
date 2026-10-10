# Fix Kafka EOF broker connection error in TiCDC

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/troubleshoot-ticdc.md`
- Source Title: `Troubleshoot TiCDC`
- Source Heading Path: `Troubleshoot TiCDC > The `Kafka: client has run out of available brokers to talk to: EOF` error is reported when I use TiCDC to replicate messages to Kafka. What should I do?`
- Source Line Ranges: `148-154`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `ecosystem`
- Topic Tags: `kafka`, `sink-uri`, `kafka-version`, `connection-failure`, `network`, `changefeed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0078_1e4ae27b47`
- Source ID: `tidb-docs-8.1:ticdc/troubleshoot-ticdc.md#the-kafka-client-has-run-out-of-available-brokers-to-talk-to-eof-error-is-reported-when-i-use-ticdc-to-replicate-messages-to-kafka-what-should-i-do`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a03ab023396b41e72cd0fab2e795f8644125199fed6cb17f26708d8d4fbbb71f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/troubleshoot-ticdc#the-kafka-client-has-run-out-of-available-brokers-to-talk-to-eof-error-is-reported-when-i-use-ticdc-to-replicate-messages-to-kafka-what-should-i-do
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/troubleshoot-ticdc.md

## Retrieval Guidance

- Use When: Use this when troubleshooting a TiCDC changefeed to Kafka that reports `Kafka: client has run out of available brokers to talk to: EOF` during message replication.
- Retrieval Keywords: Kafka: client has run out of available brokers to talk to: EOF, TiCDC Kafka EOF broker connection error, kafka-version, --sink-uri, cdc cli changefeed create, connection failure between TiCDC and the Kafka cluster, Kafka logs, network status, wrong Kafka API version, kafka://127.0.0.1:9092/test?topic=test&protocol=open-protocol&kafka-version=2.4.0
- Follow-up Guidance: The content says to check the Kafka logs and network status, and notes that specifying the correct `kafka-version` parameter in the `--sink-uri` can resolve the issue when the Kafka client uses the wrong API version.
- Classification Note: This is classified as diagnosis because the official content explains the likely causes of the EOF broker error and identifies the relevant TiCDC and Kafka configuration and connection context for troubleshooting.

## Official Source Content

## The `Kafka: client has run out of available brokers to talk to: EOF` error is reported when I use TiCDC to replicate messages to Kafka. What should I do?

This error is typically caused by the connection failure between TiCDC and the Kafka cluster. To troubleshoot, you can check the Kafka logs and network status. One possible reason is that you did not specify the correct `kafka-version` parameter when creating the replication task, causing the Kafka client inside TiCDC to use the wrong Kafka API version when accessing the Kafka server. You can fix this issue by specifying the correct `kafka-version` parameter in the [`--sink-uri`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#configure-sink-uri-for-kafka) configuration. For example:

```shell
cdc cli changefeed create --server=http://127.0.0.1:8300 --sink-uri "kafka://127.0.0.1:9092/test?topic=test&protocol=open-protocol&kafka-version=2.4.0" 
```
