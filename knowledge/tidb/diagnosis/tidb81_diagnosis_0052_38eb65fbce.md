# threshold-check diagnostic rule metrics and thread CPU checks

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-inspection-result.md`
- Source Title: `INSPECTION_RESULT`
- Source Heading Path: `INSPECTION_RESULT > Diagnostic rules > `threshold-check` diagnostic rule`
- Source Line Ranges: `274-314`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `inspection_result`, `diagnostic-rules`, `threshold-check`, `metrics-schema`, `monitoring`, `latency`, `cache-hit-rate`, `region-health`, `cpu-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0052_38eb65fbce`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-inspection-result.md#threshold-check-diagnostic-rule`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2c53940f5569b10878407305cf3aa2d420eebff2a95312b3cbce6fb7dcb525f7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-inspection-result#threshold-check-diagnostic-rule
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-inspection-result.md

## Retrieval Guidance

- Use When: Use this chunk when looking up what the `threshold-check` diagnostic rule in `INSPECTION_RESULT` evaluates, including metric thresholds, metrics schema tables, and TiKV thread CPU usage checks.
- Retrieval Keywords: threshold-check diagnostic rule, INSPECTION_RESULT, metrics schema, pd_tso_wait_duration, tidb_get_token_duration, token-limit, tidb_load_schema_duration, tikv_scheduler_command_duration, tikv_handle_snapshot_duration, tikv_storage_async_request_duration, tikv_engine_write_duration, tikv_engine_max_get_duration, tikv_engine_max_seek_duration, tikv_scheduler_pending_commands, tikv_block_index_cache_hit, tikv_block_filter_cache_hit, tikv_block_data_cache_hit, pd_scheduler_store_status, pd_region_health, region-health, leader-score-balance, region-score-balance, store-available-balance, region-count, scheduler-worker-cpu, coprocessor-normal-cpu, coprocessor-high-cpu, coprocessor-low-cpu, grpc-cpu, raftstore-cpu, apply-cpu, storage-readpool-normal-cpu, storage-readpool-high-cpu, storage-readpool-low-cpu, split-check-cpu
- Follow-up Guidance: The source also notes that built-in diagnostic rules are constantly being improved and mentions creating a PR or an issue in the `tidb` repository for additional diagnostic rules.
- Classification Note: This is classified as diagnosis content because it defines the `threshold-check` diagnostic rule by listing monitored metrics, expected threshold values, related monitoring tables, and TiKV thread CPU checks used to detect cluster health issues.

## Official Source Content

### `threshold-check` diagnostic rule

The `threshold-check` diagnostic rule checks whether the following metrics in the cluster exceed the threshold by querying the related monitoring system tables in the metrics schema:

|  Component  | Monitoring metric | Monitoring table | Expected value |  Description  |
|  :----  | :----  |  :----  |  :----  |  :----  |
| TiDB | tso-duration              | pd_tso_wait_duration                | < 50ms  |   The wait duration of getting the TSO of transaction. |
| TiDB | get-token-duration        | tidb_get_token_duration             | < 1ms   |  Queries the time it takes to get the token. The related TiDB configuration item is [`token-limit`](https://docs.pingcap.com/tidb/stable/command-line-flags-for-tidb-configuration#--token-limit).  |
| TiDB | load-schema-duration      | tidb_load_schema_duration           | < 1s    |   The time it takes for TiDB to update the schema metadata.|
| TiKV | scheduler-cmd-duration    | tikv_scheduler_command_duration     | < 0.1s  |  The time it takes for TiKV to execute the KV `cmd` request. |
| TiKV | handle-snapshot-duration  | tikv_handle_snapshot_duration       | < 30s   |  The time it takes for TiKV to handle the snapshot. |
| TiKV | storage-write-duration    | tikv_storage_async_request_duration | < 0.1s  |  The write latency of TiKV. |
| TiKV | storage-snapshot-duration | tikv_storage_async_request_duration | < 50ms  |  The time it takes for TiKV to get the snapshot. |
| TiKV | rocksdb-write-duration    | tikv_engine_write_duration          | < 100ms |  The write latency of TiKV RocksDB. |
| TiKV | rocksdb-get-duration | tikv_engine_max_get_duration | < 50ms |   The read latency of TiKV RocksDB. |
| TiKV | rocksdb-seek-duration | tikv_engine_max_seek_duration | < 50ms |  The latency of TiKV RocksDB to execute `seek`.   |
| TiKV | scheduler-pending-cmd-coun | tikv_scheduler_pending_commands  | < 1000 |  The number of commands stalled in TiKV.  |
| TiKV | index-block-cache-hit | tikv_block_index_cache_hit | > 0.95 |  The hit rate of index block cache in TiKV. |
| TiKV | filter-block-cache-hit | tikv_block_filter_cache_hit | > 0.95 |  The hit rate of filter block cache in TiKV. |
| TiKV | data-block-cache-hit | tikv_block_data_cache_hit | > 0.80 |  The hit rate of data block cache in TiKV. |
| TiKV | leader-score-balance | pd_scheduler_store_status  | < 0.05 |  Checks whether the leader score of each TiKV instance is balanced. The expected difference between instances is less than 5%. |
| TiKV | region-score-balance | pd_scheduler_store_status  | < 0.05 |  Checks whether the Region score of each TiKV instance is balanced. The expected difference between instances is less than 5%. |
| TiKV | store-available-balance | pd_scheduler_store_status  | < 0.2 | Checks whether the available storage of each TiKV instance is balanced. The expected difference between instances is less than 20%. |
| TiKV | region-count | pd_scheduler_store_status  | < 20000 |  Checks the number of Regions on each TiKV instance. The expected number of Regions in a single instance is less than 20,000. |
| PD | region-health | pd_region_health | < 100  |  Detects the number of Regions that are in the process of scheduling in the cluster. The expected number is less than 100 in total. |

In addition, this rule also checks whether the CPU usage of the following threads in a TiKV instance is too high:

* scheduler-worker-cpu
* coprocessor-normal-cpu
* coprocessor-high-cpu
* coprocessor-low-cpu
* grpc-cpu
* raftstore-cpu
* apply-cpu
* storage-readpool-normal-cpu
* storage-readpool-high-cpu
* storage-readpool-low-cpu
* split-check-cpu

The built-in diagnostic rules are constantly being improved. If you have more diagnostic rules, welcome to create a PR or an issue in the [`tidb` repository](https://github.com/pingcap/tidb).
