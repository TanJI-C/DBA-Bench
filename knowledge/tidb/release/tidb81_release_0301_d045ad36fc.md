# Compatibility changes for configuration file parameters

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.0.md`
- Source Title: `TiDB 6.1.0 Release Notes`
- Source Heading Path: `TiDB 6.1.0 Release Notes > Compatibility changes > Configuration file parameters`
- Source Line Ranges: `255-293`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `ticdc`, `dm`
- Topic Tags: `compatibility`, `configuration`, `system-variables`, `defaults`, `deprecation`, `kafka`, `tls`, `sasl`, `avro`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0301_d045ad36fc`
- Source ID: `tidb-docs-8.1:releases/release-6.1.0.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9d6f82d2847fd4db9f8dfb1493645bd29de54a5fc491dfe8e9a2239c05866b3b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.0#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.1.0 compatibility changes for configuration file parameters that were deleted, newly added, or had default values modified across TiDB, TiKV, PD, TiCDC, and DM.
- Retrieval Keywords: TiDB 6.1.0 configuration file parameters, committer-concurrency deleted, tidb_committer_concurrency, lower-case-table-names deleted, lower_case_table_name=2, mem-quota-query deleted, tidb_mem_quota_query, oom-action deleted, tidb_mem_oom_action, prepared-plan-cache.capacity deleted, tidb_prepared_plan_cache_size, prepared-plan-cache.enabled deleted, tidb_enable_prepared_plan_cache, query-log-max-len deleted, tidb_query_log_max_len, require-secure-transport deleted, require_secure_transport, run-auto-analyze deleted, tidb_enable_auto_analyze, enable-global-kill, enable-stats-cache-mem-quota, raft-engine.enable default TRUE, region-max-keys modified, region-max-size modified, coprocessor.enable-region-bucket, coprocessor.region-bucket-size, causal-ts.renew-batch-min-size, causal-ts.renew-interval, max-snapshot-file-raw-size, raft-engine.memory-limit, storage.background-error-recovery-window, storage.api-version, schedule.max-store-preparing-time, enable-tls Kafka, sasl-gssapi-user, sasl-gssapi-password, sasl-gssapi-auth-type, sasl-gssapi-service-name, sasl-gssapi-realm, sasl-gssapi-key-tab-path, sasl-gssapi-kerberos-config-path, avro-decimal-handling-mode, avro-bigint-unsigned-handling-mode, dispatchers.topic, dispatchers.partition, schema-registry, dmctl start-relay worker deleted, relay-dir deleted, is-sharding deleted, shard-mode, auto-fix-gtid deleted, meta-dir deleted, charset deleted
- Follow-up Guidance: The content points to corresponding system variables for deleted TiDB configuration items and notes Kafka, Avro, and dispatcher-related TiCDC configuration names for further lookup.
- Classification Note: This is a release-note compatibility chunk because it catalogs configuration parameter deletions, additions, and modifications in TiDB 6.1.0 for multiple components.

## Official Source Content

### Configuration file parameters

| Configuration file | Configuration | Change type | Description |
|---|---|---|---|
| TiDB | `committer-concurrency` | Deleted | Replaced by the system variable `tidb_committer_concurrency`. This configuration item is no longer valid, if you want to modify the value, you need to modify the corresponding system variable. |
| TiDB | `lower-case-table-names` | Deleted | Currently TiDB only supports `lower_case_table_name=2`. If another value is set, after the cluster is upgraded to v6.1.0, the value is lost.  |
| TiDB | `mem-quota-query` | Deleted | Replaced by the system variable `tidb_mem_quota_query`. This configuration item is no longer valid, if you want to modify the value, you need to modify the corresponding system variable. |
| TiDB | `oom-action` | Deleted | Replaced by the system variable `tidb_mem_oom_action`. This configuration item is no longer valid, if you want to modify the value, you need to modify the corresponding system variable. |
| TiDB | `prepared-plan-cache.capacity` | Deleted | Replaced by the system variable `tidb_prepared_plan_cache_size`. This configuration item is no longer valid, if you want to modify the value, you need to modify the corresponding system variable. |
| TiDB | `prepared-plan-cache.enabled` | Deleted | Replaced by the system variable `tidb_enable_prepared_plan_cache`. This configuration item is no longer valid, if you want to modify the value, you need to modify the corresponding system variable. |
| TiDB | `query-log-max-len` | Deleted | Replaced by the system variable `tidb_query_log_max_len`. This configuration item is no longer valid, if you want to modify the value, you need to modify the corresponding system variable. |
| TiDB | `require-secure-transport` | Deleted | Replaced by the system variable `require_secure_transport`. This configuration item is no longer valid, if you want to modify the value, you need to modify the corresponding system variable. |
| TiDB | `run-auto-analyze` | Deleted | Replaced by the system variable `tidb_enable_auto_analyze`. This configuration item is no longer valid, if you want to modify the value, you need to modify the corresponding system variable. |
| TiDB | [`enable-global-kill`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-global-kill-new-in-v610) | Newly added | Controls whether to enable the Global Kill (terminating queries or connections across instances) feature. When the value is `true`, both `KILL` and `KILL TIDB` statements can terminate queries or connections across instances so you do not need to worry about erroneously terminating queries or connections. |
| TiDB | [`enable-stats-cache-mem-quota`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-stats-cache-mem-quota-new-in-v610) | Newly added | Controls whether to enable the memory quota for the statistics cache. |
| TiKV | [`raft-engine.enable`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-1) | Modified | The default value is changed from `FALSE` to `TRUE`. |
| TiKV | [`region-max-keys`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-max-keys) | Modified | The default value is changed from 1440000 to `region-split-keys / 2 * 3`. |
| TiKV | [`region-max-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-max-size) | Modified | The default value is changed from 144 MB to `region-split-size / 2 * 3`. |
| TiKV | [`coprocessor.enable-region-bucket`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-region-bucket-new-in-v610) | Newly added | Determines whether to divide a Region into smaller ranges called buckets. |
| TiKV | [`coprocessor.region-bucket-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-bucket-size-new-in-v610) | Newly added | The size of a bucket when `enable-region-bucket` is true. |
| TiKV | [`causal-ts.renew-batch-min-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#renew-batch-min-size) | Newly added | The minimum number of locally cached timestamps. |
| TiKV | [`causal-ts.renew-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#renew-interval) | Newly added | The interval at which the locally cached timestamps are refreshed. |
| TiKV | [`max-snapshot-file-raw-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#max-snapshot-file-raw-size-new-in-v610) | Newly added | The snapshot file will split to multiple files when the snapshot file size exceeds this value. |
| TiKV | [`raft-engine.memory-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#memory-limit) | Newly added | Specifies the limit on the memory usage of Raft Engine. |
| TiKV | [`storage.background-error-recovery-window`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#background-error-recovery-window-new-in-v610) | Newly added | The maximum recovery time is allowed after RocksDB detects a recoverable background error. |
| TiKV | [`storage.api-version`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#api-version-new-in-v610) | Newly added | The storage format and interface version used by TiKV when TiKV serves as the raw key-value store. |
| PD | [`schedule.max-store-preparing-time`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#max-store-preparing-time-new-in-v610) | Newly added | Controls the maximum waiting time for the store to go online. |
| TiCDC | [`enable-tls`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#configure-sink-uri-for-kafka) | Newly added | Whether to use TLS to connect to the downstream Kafka instance. |
| TiCDC | `sasl-gssapi-user`<br/>`sasl-gssapi-password`<br/>`sasl-gssapi-auth-type`<br/>`sasl-gssapi-service-name`<br/>`sasl-gssapi-realm`<br/>`sasl-gssapi-key-tab-path`<br/>`sasl-gssapi-kerberos-config-path` | Newly added | Used to support SASL/GSSAPI authentication for Kafka. For details, see [Configure sink URI with `kafka`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#configure-sink-uri-for-kafka). |
| TiCDC | [`avro-decimal-handling-mode`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#configure-sink-uri-for-kafka)<br/>[`avro-bigint-unsigned-handling-mode`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#configure-sink-uri-for-kafka) | Newly added | Determines the output details of Avro format. |
| TiCDC | [`dispatchers.topic`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#customize-the-rules-for-topic-and-partition-dispatchers-of-kafka-sink) | Newly added | Controls how TiCDC dispatches incremental data to different Kafka topics. |
| TiCDC | [`dispatchers.partition`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#customize-the-rules-for-topic-and-partition-dispatchers-of-kafka-sink) | Newly added | `dispatchers.partition` is an alias for `dispatchers.dispatcher`. Controls how TiCDC dispatches incremental data to Kafka partitions. |
| TiCDC | [`schema-registry`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#integrate-ticdc-with-kafka-connect-confluent-platform) | Newly added | Specifies the schema registry endpoint that stores Avro schema. |
| DM | `worker` in the `dmctl start-relay` command | Deleted | This parameter is not recommended for use. Will provide a simpler implementation. |
| DM | `relay-dir` in the source configuration file | Deleted | Replaced by the same configuration item in the worker configuration file. |
| DM | `is-sharding` in the task configuration file | Deleted | Replaced by the `shard-mode` configuration item. |
| DM | `auto-fix-gtid` in the task configuration file | Deleted | Deprecated in v5.x and officially deleted in v6.1.0. |
| DM | `meta-dir` and `charset` in the source configuration file | Deleted | Deprecated in v5.x and officially deleted in v6.1.0. |
