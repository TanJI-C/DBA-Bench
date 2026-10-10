# Binlog, status service, and pessimistic transaction settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > binlog | TiDB Configuration File > binlog > `enable` | TiDB Configuration File > binlog > `write-timeout` | TiDB Configuration File > binlog > `ignore-error` | TiDB Configuration File > binlog > `binlog-socket` | TiDB Configuration File > binlog > `strategy` | TiDB Configuration File > status | TiDB Configuration File > status > `report-status` | TiDB Configuration File > status > `record-db-qps` | TiDB Configuration File > status > `record-db-label` | TiDB Configuration File > pessimistic-txn | TiDB Configuration File > pessimistic-txn > max-retry-count | TiDB Configuration File > pessimistic-txn > deadlock-history-capacity | TiDB Configuration File > pessimistic-txn > deadlock-history-collect-retryable`
- Source Line Ranges: `813-884`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `binlog`, `pump`, `status-api`, `prometheus`, `pessimistic-transactions`, `retries`, `deadlocks`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0324_9731198253`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#binlog`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `471aae94d360ec0dcdd372f32d5199dc6a9c20f5689439f64517a41ff97d7a49`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#binlog
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB Binlog settings, the status HTTP API and Prometheus metric reporting flags, or pessimistic transaction retry and deadlock history configuration.
- Retrieval Keywords: binlog, binlog.enable, write-timeout, ignore-error, binlog-socket, strategy, Pump, tidb_server_critical_error_total, status, report-status, record-db-qps, record-db-label, Prometheus, pessimistic-txn, max-retry-count, deadlock-history-capacity, deadlock-history-collect-retryable, INFORMATION_SCHEMA.DEADLOCKS, retryable deadlock errors
- Follow-up Guidance: It also explains that deadlock events are recorded in INFORMATION_SCHEMA.DEADLOCKS and that retryable deadlock collection is controlled by deadlock-history-collect-retryable.
- Classification Note: The content is classified as configuration because it describes TiDB configuration items for binlog behavior, service status reporting, and pessimistic transaction retry and deadlock recording.

## Official Source Content

## binlog

Configurations related to TiDB Binlog.
### `enable`

- Enables or disables binlog.
- Default value: `false`
### `write-timeout`

- The timeout of writing binlog into Pump. It is not recommended to modify this value.
- Default: `15s`
- unit: second
### `ignore-error`

- Determines whether to ignore errors occurred in the process of writing binlog into Pump. It is not recommended to modify this value.
- Default value: `false`
- When the value is set to `true` and an error occurs, TiDB stops writing binlog and add `1` to the count of the `tidb_server_critical_error_total` monitoring item. When the value is set to `false`, the binlog writing fails and the entire TiDB service is stopped.
### `binlog-socket`

- The network address to which binlog is exported.
- Default value: ""
### `strategy`

- The strategy of Pump selection when binlog is exported. Currently, only the `hash` and `range` methods are supported.
- Default value: `range`
## status

Configuration related to the status of TiDB service.
### `report-status`

- Enables or disables the HTTP API service.
- Default value: `true`
### `record-db-qps`

- Determines whether to transmit the database-related QPS metrics to Prometheus.
- Default value: `false`
### `record-db-label`

- Determines whether to transmit the database-related QPS metrics to Prometheus.
- Supports more metrics types than `record-db-qps`, for example, duration and statements.
- Default value: `false`
## pessimistic-txn

For pessimistic transaction usage, refer to [TiDB Pessimistic Transaction Mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction).
### max-retry-count

- The maximum number of retries of each statement in pessimistic transactions. If the number of retries exceeds this limit, an error occurs.
- Default value: `256`
### deadlock-history-capacity

+ The maximum number of deadlock events that can be recorded in the [`INFORMATION_SCHEMA.DEADLOCKS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-deadlocks) table of a single TiDB server. If this table is in full volume and an additional deadlock event occurs, the earliest record in the table will be removed to make place for the newest error.
+ Default value: `10`
+ Minimum value: `0`
+ Maximum value: `10000`
### deadlock-history-collect-retryable

+ Controls whether the [`INFORMATION_SCHEMA.DEADLOCKS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-deadlocks) table collects the information of retryable deadlock errors. For the description of retryable deadlock errors, see [Retryable deadlock errors](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-deadlocks#retryable-deadlock-errors).
+ Default value: `false`
