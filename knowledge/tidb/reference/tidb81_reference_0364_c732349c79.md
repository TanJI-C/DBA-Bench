# TiKV common parameter reference for gRPC message types

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-tikv-dashboard.md`
- Source Title: `Key Monitoring Metrics of TiKV`
- Source Heading Path: `Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Explanation of Common Parameters | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Explanation of Common Parameters > gRPC Message Type`
- Source Line Ranges: `534-567`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `grpc`, `message-types`, `transactional-api`, `raw-api`, `2pc`, `locks`, `gc`, `delete-range`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0364_c732349c79`
- Source ID: `tidb-docs-8.1:grafana-tikv-dashboard.md#explanation-of-common-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `00fc365018b41f23039a94609de3f8b51cb219896ac20e11a6a9a7d4ee95bc99`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#explanation-of-common-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-tikv-dashboard.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiKV-Details common parameter reference that explains gRPC message type names for Transactional API or Raw API operations.
- Retrieval Keywords: TiKV-Details dashboard, Explanation of Common Parameters, gRPC Message Type, Transactional API, Raw API, kv_get, kv_scan, kv_prewrite, kv_pessimistic_lock, kv_pessimistic_rollback, kv_txn_heart_beat, kv_check_txn_status, kv_commit, kv_cleanup, kv_batch_get, kv_batch_rollback, kv_scan_lock, kv_resolve_lock, kv_gc, kv_delete_range, raw_get, raw_batch_get, raw_scan, raw_batch_scan, raw_put, raw_batch_put, raw_delete, raw_batch_delete, raw_delete_range, 2PC, lock_ttl, GC
- Follow-up Guidance: The source states that `kv_cleanup` is deprecated in v4.0.
- Classification Note: This is classified as reference content because it defines the meanings of TiKV gRPC message type identifiers used in the dashboard.

## Official Source Content

### Explanation of Common Parameters
#### gRPC Message Type

1. Transactional API:

    - kv_get: The command of getting the latest version of data specified by `ts`
    - kv_scan: The command of scanning a range of data
    - kv_prewrite: The command of prewriting the data to be committed at first phase of 2PC
    - kv_pessimistic_lock: The command of adding a pessimistic lock to the key to prevent other transaction from modifying this key
    - kv_pessimistic_rollback: The command of deleting the pessimistic lock on the key
    - kv_txn_heart_beat: The command of updating `lock_ttl` for pessimistic transactions or large transactions to prevent them from rolling back
    - kv_check_txn_status: The command of checking the status of the transaction
    - kv_commit: The command of committing the data written by the prewrite command
    - kv_cleanup: The command of rolling back a transaction, which is deprecated in v4.0
    - kv_batch_get: The command of getting the value of batch key at once, similar to `kv_get`
    - kv_batch_rollback: The command of batch rollback of multiple prewrite transactions
    - kv_scan_lock: The command of scanning all locks with a version number before `max_version` to clean up expired transactions
    - kv_resolve_lock: The command of committing or rollback the transaction lock, according to the transaction status.
    - kv_gc: The command of GC
    - kv_delete_range: The command of deleting a range of data from TiKV

2. Raw API:

    - raw_get: The command of getting the value of key
    - raw_batch_get: The command of getting the value of batch keys
    - raw_scan: The command of scanning a range of data
    - raw_batch_scan: The command of scanning multiple consecutive data range
    - raw_put: The command of writing a key/value pair
    - raw_batch_put: The command of writing a batch of key/value pairs
    - raw_delete: The command of deleting a key/value pair
    - raw_batch_delete: The command of a batch of key/value pairs
    - raw_delete_range: The command of deleting a range of data
