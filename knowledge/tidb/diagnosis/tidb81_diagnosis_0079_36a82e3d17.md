# TiDB Binlog common error handling and cleanup behavior

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/handle-tidb-binlog-errors.md`
- Source Title: `TiDB Binlog Error Handling`
- Source Heading Path: `TiDB Binlog Error Handling | TiDB Binlog Error Handling > `kafka server: Message was too large, server rejected it to avoid allocation error` is returned when Drainer replicates data to Kafka | TiDB Binlog Error Handling > Pump returns `no space left on device` error | TiDB Binlog Error Handling > `fail to notify all living drainer` is returned when Pump is started | TiDB Binlog Error Handling > Data loss occurs during the TiDB Binlog replication | TiDB Binlog Error Handling > When the upstream transaction is large, Pump reports an error `rpc error: code = ResourceExhausted desc = trying to send message larger than max (2191430008 vs. 2147483647)` | TiDB Binlog Error Handling > Is there any cleaning mechanism for the incremental data of the file format output by Drainer? Will the data be deleted?`
- Source Line Ranges: `5-47`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `binlog`, `pump`, `drainer`, `kafka`, `disk-space`, `startup-errors`, `data-loss`, `grpc`, `message-size`, `retention-time`, `file-output`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0079_36a82e3d17`
- Source ID: `tidb-docs-8.1:tidb-binlog/handle-tidb-binlog-errors.md#tidb-binlog-error-handling`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `04a09d7a4e8db7f2c68501fde70ed7a72d0cbe12cbf786378a0fa75a3dff18e2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/handle-tidb-binlog-errors#tidb-binlog-error-handling
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/handle-tidb-binlog-errors.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting TiDB Binlog errors involving Drainer replication to Kafka, Pump startup and disk-space failures, large upstream transaction gRPC size limits, TiDB Binlog data loss checks, or Drainer file output cleanup behavior.
- Retrieval Keywords: TiDB Binlog Error Handling, kafka server: Message was too large, server rejected it to avoid allocation error, message.max.bytes, replica.fetch.max.bytes, fetch.message.max.bytes, Pump returns no space left on device, fail to notify all living drainer, binlogctl, online state, Data loss occurs during the TiDB Binlog replication, curl {TiDB_IP}:{STATUS_PORT}/info/all, rpc error: code = ResourceExhausted desc = trying to send message larger than max, max-message-size, Drainer file format output, retention-time
- Follow-up Guidance: The content also points to using the binlogctl tool to check Drainer node state, the `curl {TiDB_IP}:{STATUS_PORT}/info/all` command to confirm TiDB Binlog status, and Drainer's `retention-time` configuration item for time-based data cleaning in v4.0.x.
- Classification Note: The official content is classified as diagnosis because it lists common TiDB Binlog error messages, their causes, and the corresponding handling details for Pump, Drainer, Kafka, large transactions, and cleanup behavior.

## Official Source Content

# TiDB Binlog Error Handling

This document introduces common errors that you might encounter and solutions to these errors when you use TiDB Binlog.
## `kafka server: Message was too large, server rejected it to avoid allocation error` is returned when Drainer replicates data to Kafka

Cause: Executing a large transaction in TiDB generates binlog data of a large size, which might exceed Kafka's limit on the message size.

Solution: Adjust the configuration parameters of Kafka as shown below:

```
message.max.bytes=1073741824
replica.fetch.max.bytes=1073741824
fetch.message.max.bytes=1073741824
```
## Pump returns `no space left on device` error

Cause: The local disk space is insufficient for Pump to write binlog data normally.

Solution: Clean up the disk space and then restart Pump.
## `fail to notify all living drainer` is returned when Pump is started

Cause: When Pump is started, it notifies all Drainer nodes that are in the `online` state. If it fails to notify Drainer, this error log is printed.

Solution: Use the [binlogctl tool](https://docs.pingcap.com/tidb/stable/tidb-binlog/binlog-control) to check whether each Drainer node is normal or not. This is to ensure that all Drainer nodes that are in the `online` state are working normally. If the state of a Drainer node is not consistent with its actual working status, use the binlogctl tool to change its state and then restart Pump.
## Data loss occurs during the TiDB Binlog replication

You need to confirm that TiDB Binlog is enabled on all TiDB instances and runs normally. If the cluster version is later than v3.0, use the `curl {TiDB_IP}:{STATUS_PORT}/info/all` command to confirm the TiDB Binlog status on all TiDB instances.
## When the upstream transaction is large, Pump reports an error `rpc error: code = ResourceExhausted desc = trying to send message larger than max (2191430008 vs. 2147483647)`

This error occurs because the gRPC message sent by TiDB to Pump exceeds the size limit. You can adjust the maximum size of a gRPC message that Pump allows by specifying `max-message-size` when starting Pump.
## Is there any cleaning mechanism for the incremental data of the file format output by Drainer? Will the data be deleted?

- In Drainer v3.0.x, there is no cleaning mechanism for incremental data of the file format.
- In the v4.0.x version, there is a time-based data cleaning mechanism. For details, refer to [Drainer's `retention-time` configuration item](https://github.com/pingcap/tidb-binlog/blob/v4.0.9/cmd/drainer/drainer.toml#L153).
