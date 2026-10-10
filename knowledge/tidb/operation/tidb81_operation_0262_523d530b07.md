# TiCDC Kafka changefeed creation

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-kafka.md`
- Source Title: `Replicate Data to Kafka`
- Source Heading Path: `Replicate Data to Kafka | Replicate Data to Kafka > Create a replication task`
- Source Line Ranges: `5-33`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `changefeed`, `kafka`, `sink-uri`, `creation`, `cli`, `replication-task`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0262_523d530b07`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-kafka.md#replicate-data-to-kafka`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `51383f8bf95a8e309dfcb033d1d7a73afcf71fccf3fe1c7cb2ecbc9471e0658b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#replicate-data-to-kafka
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-kafka.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiCDC CLI command and arguments to create a Kafka changefeed replication task, including example --server, --sink-uri, and --changefeed-id usage.
- Retrieval Keywords: cdc cli changefeed create, --server, --sink-uri, --changefeed-id, simple-replication-task, Create changefeed successfully!, start-ts, target-ts, TiCDC Kafka changefeed creation
- Follow-up Guidance: It also states the changefeed ID format regex `^[a-zA-Z0-9]+(\-[a-zA-Z0-9]+)*$` and that `--sink-uri` details are in the Kafka sink URI configuration section.
- Classification Note: This is classified as an operation chunk because the content shows the command to create a replication task and explains the creation-time CLI parameters and result output.

## Official Source Content

# Replicate Data to Kafka

This document describes how to create a changefeed that replicates incremental data to Apache Kafka using TiCDC.
## Create a replication task

Create a replication task by running the following command:

```shell
cdc cli changefeed create \
    --server=http://10.0.10.25:8300 \
    --sink-uri="kafka://127.0.0.1:9092,127.0.0.1:9093,127.0.0.1:9094/topic-name?protocol=canal-json&kafka-version=2.4.0&partition-num=6&max-message-bytes=67108864&replication-factor=1" \
    --changefeed-id="simple-replication-task"
```

```shell
Create changefeed successfully!
ID: simple-replication-task
Info: {"sink-uri":"kafka://127.0.0.1:9092,127.0.0.1:9093,127.0.0.1:9094/topic-name?protocol=canal-json&kafka-version=2.4.0&partition-num=6&max-message-bytes=67108864&replication-factor=1","opts":{},"create-time":"2023-11-28T22:04:08.103600025+08:00","start-ts":415241823337054209,"target-ts":0,"admin-job-type":0,"sort-engine":"unified","sort-dir":".","config":{"case-sensitive":false,"filter":{"rules":["*.*"],"ignore-txn-start-ts":null,"ddl-allow-list":null},"mounter":{"worker-num":16},"sink":{"dispatchers":null},"scheduler":{"type":"table-number","polling-time":-1}},"state":"normal","history":null,"error":null}
```

- `--server`: The address of any TiCDC server in the TiCDC cluster.
- `--changefeed-id`: The ID of the replication task. The format must match the `^[a-zA-Z0-9]+(\-[a-zA-Z0-9]+)*$` regular expression. If this ID is not specified, TiCDC automatically generates a UUID (the version 4 format) as the ID.
- `--sink-uri`: The downstream address of the replication task. For details, see [Configure sink URI with `kafka`](#configure-sink-uri-for-kafka).
- `--start-ts`: Specifies the starting TSO of the changefeed. From this TSO, the TiCDC cluster starts pulling data. The default value is the current time.
- `--target-ts`: Specifies the ending TSO of the changefeed. To this TSO, the TiCDC cluster stops pulling data. The default value is empty, which means that TiCDC does not automatically stop pulling data.
- `--config`: Specifies the changefeed configuration file. For details, see [TiCDC Changefeed Configuration Parameters](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config).
