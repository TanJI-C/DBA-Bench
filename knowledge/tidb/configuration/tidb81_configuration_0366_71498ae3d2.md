# TiKV server networking and request handling settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > server | TiKV Configuration File > server > `addr` | TiKV Configuration File > server > `advertise-addr` | TiKV Configuration File > server > `status-addr` | TiKV Configuration File > server > `status-thread-pool-size` | TiKV Configuration File > server > `grpc-compression-type` | TiKV Configuration File > server > `grpc-concurrency` | TiKV Configuration File > server > `grpc-concurrent-stream` | TiKV Configuration File > server > `grpc-memory-pool-quota` | TiKV Configuration File > server > `grpc-raft-conn-num` | TiKV Configuration File > server > `max-grpc-send-msg-len` | TiKV Configuration File > server > `grpc-stream-initial-window-size` | TiKV Configuration File > server > `grpc-keepalive-time` | TiKV Configuration File > server > `grpc-keepalive-timeout` | TiKV Configuration File > server > `concurrent-send-snap-limit` | TiKV Configuration File > server > `concurrent-recv-snap-limit` | TiKV Configuration File > server > `end-point-recursion-limit` | TiKV Configuration File > server > `end-point-request-max-handle-duration` | TiKV Configuration File > server > `snap-io-max-bytes-per-sec` | TiKV Configuration File > server > `snap-min-ingest-size` <span class="version-mark">New in v8.1.2</span> | TiKV Configuration File > server > `enable-request-batch` | TiKV Configuration File > server > `labels` | TiKV Configuration File > server > `background-thread-count` | TiKV Configuration File > server > `end-point-slow-log-threshold` | TiKV Configuration File > server > `raft-client-queue-size` | TiKV Configuration File > server > `simplify-metrics` <span class="version-mark">New in v6.2.0</span> | TiKV Configuration File > server > `forward-max-connections-per-address` <span class="version-mark">New in v5.0.0</span>`
- Source Line Ranges: `107-277`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`, `br`
- Topic Tags: `server`, `networking`, `grpc`, `snapshots`, `status-endpoint`, `request-batching`, `thread-pools`, `metrics`, `labels`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0366_71498ae3d2`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#server`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c715fd7f13ac207189969c8e5b4a55f2e505a7c950c2227b70e571fd0ed2c8e7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#server
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiKV server configuration for listening and advertised addresses, HTTP status endpoint, gRPC behavior, snapshot transfer limits, request batching, labels, background threads, or metrics simplification.
- Retrieval Keywords: server, addr, advertise-addr, status-addr, status-thread-pool-size, grpc-compression-type, grpc-concurrency, grpc-concurrent-stream, grpc-memory-pool-quota, grpc-raft-conn-num, max-grpc-send-msg-len, grpc-stream-initial-window-size, grpc-keepalive-time, grpc-keepalive-timeout, concurrent-send-snap-limit, concurrent-recv-snap-limit, end-point-recursion-limit, end-point-request-max-handle-duration, snap-io-max-bytes-per-sec, snap-min-ingest-size, enable-request-batch, labels, background-thread-count, end-point-slow-log-threshold, raft-client-queue-size, simplify-metrics, forward-max-connections-per-address, HTTP API service, TiDB push down request, gRPC response messages, gzip, deflate
- Follow-up Guidance: The content includes a warning that exposing `status-addr` publicly might leak TiKV server status information and references performance tuning for TiKV thread pools for `grpc-concurrency`.
- Classification Note: This chunk is classified as TiKV configuration because it documents server-side network, request handling, snapshot, thread pool, and metrics-related configuration items with defaults and constraints.

## Official Source Content

## server

+ Configuration items related to the server.
### `addr`

+ The listening IP address and the listening port
+ Default value: `"127.0.0.1:20160"`
### `advertise-addr`

+ Advertise the listening address for client communication
+ If this configuration item is not set, the value of `addr` is used.
+ Default value: `""`
### `status-addr`

+ The configuration item reports TiKV status directly through the `HTTP` address

    > **Warning:**
    >
    > If this value is exposed to the public, the status information of the TiKV server might be leaked.

+ To disable the status address, set the value to `""`.
+ Default value: `"127.0.0.1:20180"`
### `status-thread-pool-size`

+ The number of worker threads for the `HTTP` API service
+ Default value: `1`
+ Minimum value: `1`
### `grpc-compression-type`

+ The compression algorithm for gRPC messages. It affects gRPC messages between TiKV nodes. Starting from v6.5.11, v7.1.6, v7.5.3, and v8.1.1, it also affects gRPC response messages sent from TiKV to TiDB.
+ Optional values: `"none"`, `"deflate"`, `"gzip"`

    > **Note:**
    >
    > TiDB does not support `"deflate"`. Therefore, if you want to compress gRPC response messages sent from TiKV to TiDB, set this configuration item to `"gzip"`.

+ Default value: `"none"`
### `grpc-concurrency`

+ The number of gRPC worker threads. When you modify the size of the gRPC thread pool, refer to [Performance tuning for TiKV thread pools](https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance#performance-tuning-for-tikv-thread-pools).
+ Default value: `5`
+ Minimum value: `1`
### `grpc-concurrent-stream`

+ The maximum number of concurrent requests allowed in a gRPC stream
+ Default value: `1024`
+ Minimum value: `1`
### `grpc-memory-pool-quota`

+ Limits the memory size that can be used by gRPC
+ Default value: No limit
+ Limit the memory in case OOM is observed. Note that limit the usage can lead to potential stall
### `grpc-raft-conn-num`

+ The maximum number of connections between TiKV nodes for Raft communication
+ Default value: `1`
+ Minimum value: `1`
### `max-grpc-send-msg-len`

+ Sets the maximum length of a gRPC message that can be sent
+ Default value: `10485760`
+ Unit: Bytes
+ Maximum value: `2147483647`
### `grpc-stream-initial-window-size`

+ The window size of the gRPC stream
+ Default value: `2MiB`
+ Unit: KiB|MiB|GiB
+ Minimum value: `"1KiB"`
### `grpc-keepalive-time`

+ The time interval at which that gRPC sends `keepalive` Ping messages
+ Default value: `"10s"`
+ Minimum value: `"1s"`
### `grpc-keepalive-timeout`

+ Disables the timeout for gRPC streams
+ Default value: `"3s"`
+ Minimum value: `"1s"`
### `concurrent-send-snap-limit`

+ The maximum number of snapshots sent at the same time
+ Default value: `32`
+ Minimum value: `1`
### `concurrent-recv-snap-limit`

+ The maximum number of snapshots received at the same time
+ Default value: `32`
+ Minimum value: `1`
### `end-point-recursion-limit`

+ The maximum number of recursive levels allowed when TiKV decodes the Coprocessor DAG expression
+ Default value: `1000`
+ Minimum value: `1`
### `end-point-request-max-handle-duration`

+ The longest duration allowed for a TiDB's push down request to TiKV for processing tasks
+ Default value: `"60s"`
+ Minimum value: `"1s"`
### `snap-io-max-bytes-per-sec`

+ The maximum allowable disk bandwidth when processing snapshots
+ Default value: `"100MiB"`
+ Unit: KiB|MiB|GiB
+ Minimum value: `"1KiB"`
### `snap-min-ingest-size` New in v8.1.2

+ Specifies the minimum threshold for whether TiKV adopts the ingest method when processing snapshots.

    + When the snapshot size exceeds this threshold, TiKV adopts the ingest method, which imports SST files from the snapshot into RocksDB. This method is faster for large files.
    + When the snapshot size does not exceed this threshold, TiKV adopts the direct write method, which writes each piece of data into RocksDB individually. This method is more efficient for small files.

+ Default value: `"2MiB"`
+ Unit: KiB|MiB|GiB
+ Minimum value: `0`
### `enable-request-batch`

+ Determines whether to process requests in batches
+ Default value: `true`
### `labels`

+ Specifies server attributes, such as `{ zone = "us-west-1", disk = "ssd" }`.
+ Default value: `{}`
### `background-thread-count`

+ The working thread count of the background pool, including endpoint threads, BR threads, split-check threads, Region threads, and other threads of delay-insensitive tasks.
+ Default value: when the number of CPU cores is less than 16, the default value is `2`; otherwise, the default value is `3`.
### `end-point-slow-log-threshold`

+ The time threshold for a TiDB's push-down request to output slow log. If the processing time is longer than this threshold, the slow logs are output.
+ Default value: `"1s"`
+ Minimum value: `0`
### `raft-client-queue-size`

+ Specifies the queue size of the Raft messages in TiKV. If too many messages not sent in time result in a full buffer, or messages discarded, you can specify a greater value to improve system stability.
+ Default value: `8192`
### `simplify-metrics` New in v6.2.0

+ Specifies whether to simplify the returned monitoring metrics. After you set the value to `true`, TiKV reduces the amount of data returned for each request by filtering out some metrics.
+ Default value: `false`
### `forward-max-connections-per-address` New in v5.0.0

+ Sets the size of the connection pool for service and forwarding requests to the server. Setting it to too small a value affects the request latency and load balancing.
+ Default value: `4`
