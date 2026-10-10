# TiKV client RPC, coprocessor cache, and transaction latches

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > tikv-client | TiDB Configuration File > tikv-client > `grpc-connection-count` | TiDB Configuration File > tikv-client > `grpc-keepalive-time` | TiDB Configuration File > tikv-client > `grpc-keepalive-timeout` | TiDB Configuration File > tikv-client > `grpc-compression-type` | TiDB Configuration File > tikv-client > `commit-timeout` | TiDB Configuration File > tikv-client > `max-batch-size` | TiDB Configuration File > tikv-client > `max-batch-wait-time` | TiDB Configuration File > tikv-client > `batch-wait-size` | TiDB Configuration File > tikv-client > `overload-threshold` | TiDB Configuration File > tikv-client > `copr-req-timeout` <span class="version-mark">New in v7.5.0</span> | TiDB Configuration File > tikv-client > `enable-replica-selector-v2` <span class="version-mark">New in v8.0.0</span> | TiDB Configuration File > tikv-client.copr-cache <span class="version-mark">New in v4.0.0</span> | TiDB Configuration File > tikv-client.copr-cache <span class="version-mark">New in v4.0.0</span> > `capacity-mb` | TiDB Configuration File > txn-local-latches | TiDB Configuration File > txn-local-latches > `enabled` | TiDB Configuration File > txn-local-latches > `capacity``
- Source Line Ranges: `712-812`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `grpc`, `keepalive`, `compression`, `commit-timeout`, `batching`, `coprocessor-cache`, `replica-selector`, `transaction-latches`, `deprecated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0323_1a9edc0aaf`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#tikv-client`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `724191f800995f2648360cb5e6e6de30b6816022a400199a7c39b61427e5cc00`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tikv-client
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB tikv-client RPC settings, Coprocessor Cache capacity, or txn-local-latches configuration and deprecation notes.
- Retrieval Keywords: tikv-client, grpc-connection-count, grpc-keepalive-time, grpc-keepalive-timeout, grpc-compression-type, commit-timeout, max-batch-size, max-batch-wait-time, batch-wait-size, overload-threshold, copr-req-timeout, enable-replica-selector-v2, tikv-client.copr-cache, capacity-mb, Coprocessor Cache, txn-local-latches, enabled, capacity, BatchCommands API, Raft election timeout
- Follow-up Guidance: It also notes that copr-req-timeout and enable-replica-selector-v2 might be deprecated in future versions, and that txn-local-latches configuration items might be deprecated and are not recommended to use.
- Classification Note: The content is classified as configuration because it lists TiDB-side tikv-client, coprocessor cache, and transaction latch parameters with defaults, constraints, and warnings.

## Official Source Content

## tikv-client
### `grpc-connection-count`

- The maximum number of connections established with each TiKV.
- Default value: `4`
### `grpc-keepalive-time`

- The `keepalive` time interval of the RPC connection between TiDB and TiKV nodes. If there is no network packet within the specified time interval, the gRPC client executes `ping` command to TiKV to see if it is alive.
- Default: `10`
- Unit: second
### `grpc-keepalive-timeout`

- The timeout of the RPC `keepalive` check between TiDB and TiKV nodes.
- Default value: `3`
- Unit: second
### `grpc-compression-type`

- Specifies the compression type used for data transfer from TiDB nodes to TiKV nodes. The default value is `"none"`, which means no compression. To enable the gzip compression, set this value to `"gzip"`.
- Default value: `"none"`
- Value options: `"none"`, `"gzip"`

> **Note:**
>
> The compression algorithm for response messages returned from TiKV nodes to TiDB nodes is controlled by the TiKV configuration item [`grpc-compression-type`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#grpc-compression-type).
### `commit-timeout`

- The maximum timeout when executing a transaction commit.
- Default value: `41s`
- It is required to set this value larger than twice of the Raft election timeout.
### `max-batch-size`

- The maximum number of RPC packets sent in batch. If the value is not `0`, the `BatchCommands` API is used to send requests to TiKV, and the RPC latency can be reduced in the case of high concurrency. It is recommended that you do not modify this value.
- Default value: `128`
### `max-batch-wait-time`

- Waits for `max-batch-wait-time` to encapsulate the data packets into a large packet in batch and send it to the TiKV node. It is valid only when the value of `tikv-client.max-batch-size` is greater than `0`. It is recommended not to modify this value.
- Default value: `0`
- Unit: nanoseconds
### `batch-wait-size`

- The maximum number of packets sent to TiKV in batch. It is recommended not to modify this value.
- Default value: `8`
- If the value is `0`, this feature is disabled.
### `overload-threshold`

- The threshold of the TiKV load. If the TiKV load exceeds this threshold, more `batch` packets are collected to relieve the pressure of TiKV. This configuration item takes effect only when both [`tikv-client.max-batch-size`](#max-batch-size) and [`tikv-client.max-batch-wait-time`](#max-batch-wait-time) are set to values greater than `0`. It is recommended not to modify this value.
- Default value: `200`
### `copr-req-timeout` New in v7.5.0

> **Warning:**
>
> This configuration parameter might be deprecated in future versions. **DO NOT** change the value of it.

+ The timeout of a single Coprocessor request.
+ Default value: `60`
+ Unit: second
### `enable-replica-selector-v2` New in v8.0.0

> **Warning:**
>
> This configuration parameter might be deprecated in future versions. **DO NOT** change the value of it.

+ Whether to use the new version of the Region replica selector when sending RPC requests to TiKV.
+ Default value: `true`
## tikv-client.copr-cache New in v4.0.0

This section introduces configuration items related to the [Coprocessor Cache](https://docs.pingcap.com/tidb/stable/coprocessor-cache) feature.
### `capacity-mb`

- The total size of the cached data. When the cache space is full, old cache entries are evicted. When the value is `0.0`, the Coprocessor Cache feature is disabled.
- Default value: `1000.0`
- Unit: MB
- Type: Float
## txn-local-latches

Configuration items related to the transaction latch. These configuration items might be deprecated in the future. It is not recommended to use them.
### `enabled`

- Determines whether to enable the memory lock of transactions.
- Default value: `false`
### `capacity`

- The number of slots corresponding to Hash, which automatically adjusts upward to an exponential multiple of 2. Each slot occupies 32 Bytes of memory. If set too small, it might result in slower running speed and poor performance in the scenario where data writing covers a relatively large range (such as importing data).
- Default value: `2048000`
