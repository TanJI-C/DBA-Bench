# Binlog consumer overview and Drainer Kafka output configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/binlog-consumer-client.md`
- Source Title: `Binlog Consumer Client User Guide`
- Source Heading Path: `Binlog Consumer Client User Guide | Binlog Consumer Client User Guide > Configure Drainer`
- Source Line Ranges: `5-24`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `binlog`, `drainer`, `kafka`, `downstream`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0197_1f54e5bffd`
- Source ID: `tidb-docs-8.1:tidb-binlog/binlog-consumer-client.md#binlog-consumer-client-user-guide`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `134f61378fcf06fde769bae6587579e1184ba0b8014b9ae7f6498d18a2c47717`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/binlog-consumer-client#binlog-consumer-client-user-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/binlog-consumer-client.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to configure Drainer to output TiDB secondary binlog data to Kafka for Binlog Consumer Client consumption.
- Retrieval Keywords: Configure Drainer, Binlog Consumer Client, Drainer, secondary binlog data, Kafka output, [syncer], db-type = "kafka", [syncer.to], kafka-addrs, kafka-version, down streaming, MySQL, TiDB, file, Kafka
- Follow-up Guidance: The same guide also provides the Kafka output data format and Driver information for reading binlog data from Kafka.
- Classification Note: This is classified as configuration because the content consists of Drainer configuration settings for enabling Kafka as the downstream output.

## Official Source Content

# Binlog Consumer Client User Guide

Binlog Consumer Client is used to consume TiDB secondary binlog data from Kafka and output the data in a specific format. Currently, Drainer supports multiple kinds of down streaming, including MySQL, TiDB, file and Kafka. But sometimes users have customized requirements for outputting data to other formats, for example, Elasticsearch and Hive, so this feature is introduced.
## Configure Drainer

Modify the configuration file of Drainer and set it to output the data to Kafka:

```
[syncer]
db-type = "kafka"

[syncer.to]
# the Kafka address
kafka-addrs = "127.0.0.1:9092"
# the Kafka version
kafka-version = "2.4.0"
```
