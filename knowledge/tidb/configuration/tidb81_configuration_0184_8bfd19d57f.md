# Kafka version support and sink URI parameters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-kafka.md`
- Source Title: `Replicate Data to Kafka`
- Source Heading Path: `Replicate Data to Kafka > Supported Kafka versions | Replicate Data to Kafka > Configure sink URI for Kafka`
- Source Line Ranges: `34-108`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `shared`
- Topic Tags: `kafka`, `version-compatibility`, `sink-uri`, `parameters`, `authentication`, `tls`, `sasl`, `avro`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0184_8bfd19d57f`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-kafka.md#supported-kafka-versions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `98496c9384f2dbc103e1caf39131fcb94ed848816e6f608701a8c5df2eac0e68`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#supported-kafka-versions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-kafka.md

## Retrieval Guidance

- Use When: Use this chunk when looking for supported Kafka versions for TiCDC or the exact Kafka sink URI format and query parameters for a changefeed.
- Retrieval Keywords: Supported Kafka versions, TiCDC >= v8.1.0, Minimum supported Kafka version, Configure sink URI for Kafka, kafka-version, protocol, partition-num, max-message-bytes, replication-factor, required-acks, compression, auto-create-topic, enable-tls, sasl-mechanism, avro-decimal-handling-mode, avro-bigint-unsigned-handling-mode
- Follow-up Guidance: It includes the sink URI pattern `[scheme]://[host]:[port][/path]?[query_parameters]`, a multi-host example, and parameter descriptions for TLS, SASL, timeouts, and Avro-specific options.
- Classification Note: This is classified as a configuration chunk because the content defines version compatibility and lists Kafka sink URI parameters, allowed values, defaults, and constraints.

## Official Source Content

## Supported Kafka versions

The following table shows the minimum supported Kafka versions for each TiCDC version:

| TiCDC version            | Minimum supported Kafka version |
|:-------------------------|:--------------------------------|
| TiCDC >= v8.1.0          | 2.1.0                           |
| v7.6.0 <= TiCDC < v8.1.0 | 2.4.0                           |
| v7.5.2 <= TiCDC < v8.0.0 | 2.1.0                           |
| v7.5.0 <= TiCDC < v7.5.2 | 2.4.0                           |
| v6.5.0 <= TiCDC < v7.5.0 | 2.1.0                           |
| v6.1.0 <= TiCDC < v6.5.0 | 2.0.0                           |
## Configure sink URI for Kafka

Sink URI is used to specify the connection information of the TiCDC target system. The format is as follows:

```shell
[scheme]://[host]:[port][/path]?[query_parameters]
```

> **Tip:**
> 
> If there are multiple hosts or ports for the downstream Kafka, you can configure multiple `[host]:[port]` in the sink URI. For example:
>
> ```shell
> [scheme]://[host]:[port],[host]:[port],[host]:[port][/path]?[query_parameters]
> ```

Sample configuration:

```shell
--sink-uri="kafka://127.0.0.1:9092/topic-name?protocol=canal-json&kafka-version=2.4.0&partition-num=6&max-message-bytes=67108864&replication-factor=1"
```

The following are descriptions of sink URI parameters and values that can be configured for Kafka:

| Parameter/Parameter value               | Description                                                        |
| :------------------ | :------------------------------------------------------------ |
| `host`          | The IP address of the downstream Kafka services.                                 |
| `port`               | The port for the downstream Kafka.                                          |
| `topic-name` | Variable. The name of the Kafka topic. |
| `protocol` | The protocol with which messages are output to Kafka. The value options are [`canal-json`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-canal-json), [`open-protocol`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-protocol), [`avro`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-avro-protocol), [`debezium`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-debezium) and [`simple`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-simple-protocol). |
| `kafka-version`      | The version of the downstream Kafka. This value needs to be consistent with the actual version of the downstream Kafka.                      |
| `kafka-client-id`    | Specifies the Kafka client ID of the replication task (optional. `TiCDC_sarama_producer_replication ID` by default). |
| `partition-num`      | The number of the downstream Kafka partitions (optional. The value must be **no greater than** the actual number of partitions; otherwise, the replication task cannot be created successfully. `3` by default). |
| `max-message-bytes`  | The maximum size of data that is sent to Kafka broker each time (optional, `10MB` by default, and the maximum value is `100MB`). From v5.0.6 and v4.0.6, the default value has changed from `64MB` and `256MB` to `10MB`. |
| `replication-factor` | The number of Kafka message replicas that can be saved (optional, `1` by default). This value must be greater than or equal to the value of [`min.insync.replicas`](https://kafka.apache.org/33/documentation.html#brokerconfigs_min.insync.replicas) in Kafka. |
| `required-acks` | A parameter used in the `Produce` request, which notifies the broker of the number of replica acknowledgements it needs to receive before responding. Value options are `0` (`NoResponse`: no response, only `TCP ACK` is provided), `1` (`WaitForLocal`: responds only after local commits are submitted successfully), and `-1` (`WaitForAll`: responds after all replicated replicas are committed successfully. You can configure the minimum number of replicated replicas using the [`min.insync.replicas`](https://kafka.apache.org/33/documentation.html#brokerconfigs_min.insync.replicas) configuration item of the broker). (Optional, the default value is `-1`).    |
| `compression` | The compression algorithm used when sending messages (value options are `none`, `lz4`, `gzip`, `snappy`, and `zstd`; `none` by default). Note that the Snappy compressed file must be in the [official Snappy format](https://github.com/google/snappy). Other variants of Snappy compression are not supported.|
| `auto-create-topic` | Determines whether TiCDC creates the topic automatically when the `topic-name` passed in does not exist in the Kafka cluster (optional, `true` by default). |
| `enable-tidb-extension` | Optional. `false` by default. When the output protocol is `canal-json`, if the value is `true`, TiCDC sends [WATERMARK events](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-canal-json#watermark-event) and adds the [TiDB extension field](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-canal-json#tidb-extension-field) to Kafka messages. From v6.1.0, this parameter is also applicable to the `avro` protocol. If the value is `true`, TiCDC adds [three TiDB extension fields](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-avro-protocol#tidb-extension-fields) to the Kafka message. |
| `max-batch-size` | New in v4.0.9. If the message protocol supports outputting multiple data changes to one Kafka message, this parameter specifies the maximum number of data changes in one Kafka message. It currently takes effect only when Kafka's `protocol` is `open-protocol` (optional, `16` by default). |
| `enable-tls` | Whether to use TLS to connect to the downstream Kafka instance (optional, `false` by default). |
| `ca` | The path of the CA certificate file needed to connect to the downstream Kafka instance (optional).  |
| `cert` | The path of the certificate file needed to connect to the downstream Kafka instance (optional). |
| `key` | The path of the certificate key file needed to connect to the downstream Kafka instance (optional). |
| `insecure-skip-verify` | Whether to skip certificate verification when connecting to the downstream Kafka instance (optional, `false` by default). |
| `sasl-user` | The identity (authcid) of SASL/PLAIN or SASL/SCRAM authentication needed to connect to the downstream Kafka instance (optional). |
| `sasl-password` | The password of SASL/PLAIN or SASL/SCRAM authentication needed to connect to the downstream Kafka instance (optional). If it contains special characters, they need to be URL encoded. |
| `sasl-mechanism` | The name of SASL authentication needed to connect to the downstream Kafka instance. The value can be `plain`, `scram-sha-256`, `scram-sha-512`, or `gssapi`. |
| `sasl-gssapi-auth-type` | The gssapi authentication type. Values can be `user` or `keytab` (optional). |
| `sasl-gssapi-keytab-path` | The gssapi keytab path (optional).|
| `sasl-gssapi-kerberos-config-path` | The gssapi kerberos configuration path (optional). |
| `sasl-gssapi-service-name` | The gssapi service name (optional). |
| `sasl-gssapi-user` | The user name of gssapi authentication (optional). |
| `sasl-gssapi-password` | The password of gssapi authentication (optional). If it contains special characters, they need to be URL encoded. |
| `sasl-gssapi-realm` | The gssapi realm name (optional). |
| `sasl-gssapi-disable-pafxfast` | Whether to disable the gssapi PA-FX-FAST (optional). |
| `dial-timeout` | The timeout in establishing a connection with the downstream Kafka. The default value is `10s`. |
| `read-timeout` | The timeout in getting a response returned by the downstream Kafka. The default value is `10s`. |
| `write-timeout` | The timeout in sending a request to the downstream Kafka. The default value is `10s`. |
| `avro-decimal-handling-mode` | Only effective with the `avro` protocol. Determines how Avro handles the DECIMAL field. The value can be `string` or `precise`, indicating either mapping the DECIMAL field to a string or a precise floating number.  |
| `avro-bigint-unsigned-handling-mode` | Only effective with the `avro` protocol. Determines how Avro handles the BIGINT UNSIGNED field. The value can be `string` or `long`, indicating either mapping the BIGINT UNSIGNED field to a 64-bit signed number or a string.  |
