# Kafka sink column filtering, table scaling, and large message handling

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-kafka.md`
- Source Title: `Replicate Data to Kafka`
- Source Heading Path: `Replicate Data to Kafka > Column selectors | Replicate Data to Kafka > Scale out the load of a single large table to multiple TiCDC nodes | Replicate Data to Kafka > Handle messages that exceed the Kafka topic limit | Replicate Data to Kafka > Handle messages that exceed the Kafka topic limit > TiCDC data compression`
- Source Line Ranges: `327-418`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`, `tikv`, `ecosystem`, `sql`
- Topic Tags: `kafka`, `column-selectors`, `filtering`, `large-table`, `scheduler`, `scaling`, `message-size`, `compression`, `canal-json`, `open-protocol`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0188_b12659d548`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-kafka.md#column-selectors`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bfe1f5f908e3a5ed55cf52736c3a2035d1b91503245b9bdd4c9e425135cef28f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#column-selectors
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-kafka.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiCDC Kafka sink settings for `column-selectors`, scaling a single large table across TiCDC nodes, or handling Kafka messages that exceed `max.message.bytes` with large message compression.
- Retrieval Keywords: column-selectors, columns = ['a', 'b'], columns = ["*", "!b"], columns = ['column*', '!column1'], columns = ["column?", "!column1"], primary key or unique key to be replicated, enable-table-across-nodes = true, region-threshold, write-key-threshold, Scale out the load of a single large table to multiple TiCDC nodes, INFORMATION_SCHEMA.TIKV_REGION_STATUS, SELECT COUNT(*) FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS, max.message.bytes, large-message-handle-option, Canal-JSON, Open Protocol, enable-tidb-extension=true, large-message-handle-compression, lz4, snappy, compression parameter in sink-uri
- Follow-up Guidance: The content includes the SQL `SELECT COUNT(*) FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS WHERE DB_NAME="database1" AND TABLE_NAME="table1" AND IS_INDEX=0;` to query how many Regions a table contains.
- Classification Note: This is classified as configuration because it documents sink and scheduler parameters, matching rules, thresholds, protocol requirements, and compression settings for Kafka changefeeds.

## Official Source Content

## Column selectors

The column selector feature supports selecting columns from events and sending only the data changes related to those columns to the downstream.

Take the following configuration of `column-selectors` as an example:

```toml
[sink]
column-selectors = [
    {matcher = ['test.t1'], columns = ['a', 'b']},
    {matcher = ['test.*'], columns = ["*", "!b"]},
    {matcher = ['test1.t1'], columns = ['column*', '!column1']},
    {matcher = ['test3.t'], columns = ["column?", "!column1"]},
]
```

- For table `test.t1`, only columns `a` and `b` are sent.
- For tables in the `test` database (excluding the `t1` table), all columns except `b` are sent.
- For table `test1.t1`, any column starting with `column` is sent, except for `column1`.
- For table `test3.t`, any 7-character column starting with `column` is sent, except for `column1`.
- For tables that do not match any rule, all columns are sent.

> **Note:**
>
> After being filtered by the `column-selectors` rules, the data in the table must have a primary key or unique key to be replicated. Otherwise, the changefeed reports an error when it is created or running.
## Scale out the load of a single large table to multiple TiCDC nodes

This feature splits the data replication range of a single large table into multiple ranges, according to the data volume and the number of modified rows per minute, and it makes the data volume and the number of modified rows replicated in each range approximately the same. This feature distributes these ranges to multiple TiCDC nodes for replication, so that multiple TiCDC nodes can replicate a large single table at the same time. This feature can solve the following two problems:

- A single TiCDC node cannot replicate a large single table in time.
- The resources (such as CPU and memory) consumed by TiCDC nodes are not evenly distributed.

> **Warning:**
>
> TiCDC v7.0.0 only supports scaling out the load of a large single table on Kafka changefeeds.

Sample configuration:

```toml
[scheduler]
# The default value is "false". You can set it to "true" to enable this feature.
enable-table-across-nodes = true
# When you enable this feature, it only takes effect for tables with the number of regions greater than the `region-threshold` value.
region-threshold = 100000
# When you enable this feature, it takes effect for tables with the number of rows modified per minute greater than the `write-key-threshold` value.
# Note:
# * The default value of `write-key-threshold` is 0, which means that the feature does not split the table replication range according to the number of rows modified in a table by default.
# * You can configure this parameter according to your cluster workload. For example, if it is configured as 30000, it means that the feature will split the replication range of a table when the number of modified rows per minute in the table exceeds 30000.
# * When `region-threshold` and `write-key-threshold` are configured at the same time:
#   TiCDC will check whether the number of modified rows is greater than `write-key-threshold` first.
#   If not, next check whether the number of Regions is greater than `region-threshold`.
write-key-threshold = 30000
```

You can query the number of Regions a table contains by the following SQL statement:

```sql
SELECT COUNT(*) FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS WHERE DB_NAME="database1" AND TABLE_NAME="table1" AND IS_INDEX=0;
```
## Handle messages that exceed the Kafka topic limit

Kafka topic sets a limit on the size of messages it can receive. This limit is controlled by the [`max.message.bytes`](https://kafka.apache.org/documentation/#topicconfigs_max.message.bytes) parameter. If TiCDC Kafka sink sends data that exceeds this limit, the changefeed reports an error and cannot proceed to replicate data. To solve this problem, TiCDC adds a new configuration `large-message-handle-option` and provides the following solution.

Currently, this feature supports two encoding protocols: Canal-JSON and Open Protocol. When using the Canal-JSON protocol, you must specify `enable-tidb-extension=true` in `sink-uri`.
### TiCDC data compression

Starting from v7.4.0, TiCDC Kafka sink supports compressing data immediately after encoding and comparing the compressed data size with the message size limit. This feature can effectively reduce the occurrence of messages exceeding the size limit.

An example configuration is as follows:

```toml
[sink.kafka-config.large-message-handle]
# This configuration is introduced in v7.4.0.
# "none" by default, which means that the compression feature is disabled.
# Possible values are "none", "lz4", and "snappy". The default value is "none".
large-message-handle-compression = "none"
```

When `large-message-handle-compression` is enabled, the message received by the consumer is encoded using a specific compression protocol, and the consumer application needs to use the specified compression protocol to decode the data.

This feature is different from the compression feature of the Kafka producer:

* The compression algorithm specified in `large-message-handle-compression` compresses a single Kafka message. The compression is performed before comparing with the message size limit.
* At the same time, you can also configure the compression algorithm by using the `compression` parameter in [`sink-uri`](#configure-sink-uri-for-kafka). This compression algorithm is applied to the entire data sending request, which contains multiple Kafka messages.

If you set `large-message-handle-compression`, when TiCDC receives a message, it first compares it to the value of the message size limit parameter, and messages larger than the size limit are compressed. If you also set `compression` in [`sink-uri`](#configure-sink-uri-for-kafka), TiCDC compresses the entire sending data request again at the sink level based on the `sink-uri` setting.

The compression ratio for the two preceding compression methods is calculated as follows: `compression ratio = size before compression / size after compression * 100`.
