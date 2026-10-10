# Slow log fields and related system variables

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/identify-slow-queries.md`
- Source Title: `Identify Slow Queries`
- Source Heading Path: `Identify Slow Queries > Fields description | Identify Slow Queries > Related system variables`
- Source Line Ranges: `123-201`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiflash`, `pd`, `sql`
- Topic Tags: `slow-query-log`, `fields`, `coprocessor`, `backoff`, `resource-control`, `system-variables`, `execution-plan`, `plan-decoding`, `performance-testing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0046_b8d1bd971b`
- Source ID: `tidb-docs-8.1:identify-slow-queries.md#fields-description`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `de820999e6074a789360fd82c8eb0dc3cf060ea60c4ca12b4d91bac5f4dc39d9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/identify-slow-queries#fields-description
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/identify-slow-queries.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting TiDB slow query log fields, Coprocessor and backoff metrics, Resource Control fields, or related system variables that affect slow log content and execution plan collection.
- Retrieval Keywords: Request_count, Total_keys, Process_time, Wait_time, Process_keys, Num_cop_tasks, Cop_proc_avg, Cop_proc_p90, Cop_proc_max, Cop_proc_addr, Cop_wait_avg, Cop_wait_p90, Cop_wait_max, Cop_wait_addr, Rocksdb_delete_skipped_count, Rocksdb_key_skipped_count, Rocksdb_block_cache_hit_count, Rocksdb_block_read_count, Rocksdb_block_read_byte, Rocksdb_block_read_time, Cop_backoff_{backoff-type}_total_times, Cop_backoff_{backoff-type}_total_time, Cop_backoff_{backoff-type}_max_time, Cop_backoff_{backoff-type}_max_addr, Cop_backoff_{backoff-type}_avg_time, Cop_backoff_{backoff-type}_p90_time, tikvRPC, tiflashRPC, pdRPC, txnLock, regionMiss, regionScheduling, tikvServerBusy, tiflashServerBusy, tikvDiskFull, txnLockFast, Resource_group, Request_unit_read, Request_unit_write, Time_queued_by_rc, tidb_slow_log_threshold, tidb_query_log_max_len, tidb_redact_log, tidb_enable_collect_execution_info, tidb_decode_plan, Plan field, slow log fields, Related system variables
- Follow-up Guidance: The content also shows how to use `tidb_decode_plan` to view the `Plan` field and notes that its format is roughly the same as `EXPLAIN` or `EXPLAIN ANALYZE`.
- Classification Note: This is classified as diagnosis for TiDB because the content explains slow log field meanings, backoff categories, resource control fields, and system variables used to inspect and understand slow queries.

## Official Source Content

* `Request_count`: The number of Coprocessor requests that a statement sends.
* `Total_keys`: The number of keys that Coprocessor has scanned.
* `Process_time`: The total processing time of a SQL statement in TiKV. Because data is sent to TiKV concurrently, this value might exceed `Query_time`.
* `Wait_time`: The total waiting time of a statement in TiKV. Because the Coprocessor of TiKV runs a limited number of threads, requests might queue up when all threads of Coprocessor are working. When a request in the queue takes a long time to process, the waiting time of the subsequent requests increases.
* `Process_keys`: The number of keys that Coprocessor has processed. Compared with `total_keys`, `processed_keys` does not include the old versions of MVCC. A great difference between `processed_keys` and `total_keys` indicates that many old versions exist.
* `Num_cop_tasks`: The number of Coprocessor tasks sent by this statement.
* `Cop_proc_avg`: The average execution time of cop-tasks, including some waiting time that cannot be counted, such as the mutex in RocksDB.
* `Cop_proc_p90`: The P90 execution time of cop-tasks.
* `Cop_proc_max`: The maximum execution time of cop-tasks.
* `Cop_proc_addr`: The address of the cop-task with the longest execution time.
* `Cop_wait_avg`: The average waiting time of cop-tasks, including the time of request queueing and getting snapshots.
* `Cop_wait_p90`: The P90 waiting time of cop-tasks.
* `Cop_wait_max`: The maximum waiting time of cop-tasks.
* `Cop_wait_addr`: The address of the cop-task whose waiting time is the longest.
* `Rocksdb_delete_skipped_count`: The number of deleted (tombstone) keys that RocksDB encounters when scanning data.
* `Rocksdb_key_skipped_count`: The number of all keys that RocksDB encounters when scanning data.
* `Rocksdb_block_cache_hit_count`: The number of times RocksDB reads data from the block cache.
* `Rocksdb_block_read_count`: The number of times RocksDB reads data from the file system.
* `Rocksdb_block_read_byte`: The amount of data RocksDB reads from the file system.
* `Rocksdb_block_read_time`: The time RocksDB takes to read data from the file system.
* `Cop_backoff_{backoff-type}_total_times`: The total times of backoff caused by an error.
* `Cop_backoff_{backoff-type}_total_time`: The total time of backoff caused by an error.
* `Cop_backoff_{backoff-type}_max_time`: The longest time of backoff caused by an error.
* `Cop_backoff_{backoff-type}_max_addr`: The address of the cop-task that has the longest backoff time caused by an error.
* `Cop_backoff_{backoff-type}_avg_time`: The average time of backoff caused by an error.
* `Cop_backoff_{backoff-type}_p90_time`: The P90 percentile backoff time caused by an error.

`backoff-type` generally includes the following types:

* `tikvRPC`: The backoff caused by failing to send RPC requests to TiKV.
* `tiflashRPC`: The backoff caused by failing to send RPC requests to TiFlash.
* `pdRPC`: The backoff caused by failing to send RPC requests to PD.
* `txnLock`: The backoff caused by lock conflicts.
* `regionMiss`: The backoff caused by that processing requests fails when the TiDB Region cache information is outdated after Regions are split or merged.
* `regionScheduling`: The backoff caused by that TiDB cannot process requests when Regions are being scheduled and the Leader is not selected.
* `tikvServerBusy`: The backoff caused by that the TiKV load is too high to handle new requests.
* `tiflashServerBusy`: The backoff caused by that the TiFlash load is too high to handle new requests.
* `tikvDiskFull`: The backoff caused by that the TiKV disk is full.
* `txnLockFast`: The backoff caused by that locks are encountered during data reads.

Fields related to Resource Control:

* `Resource_group`: the resource group that the statement is bound to.
* `Request_unit_read`: the total read RUs consumed by the statement.
* `Request_unit_write`: the total write RUs consumed by the statement.
* `Time_queued_by_rc`: the total time that the statement waits for available resources.
## Related system variables

* [`tidb_slow_log_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_slow_log_threshold): Sets the threshold for the slow log. The SQL statement whose execution time exceeds this threshold is recorded in the slow log. The default value is 300 (ms).
* [`tidb_query_log_max_len`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_query_log_max_len): Sets the maximum length of the SQL statement recorded in the slow log. The default value is 4096 (byte).
* [tidb_redact_log](https://docs.pingcap.com/tidb/stable/system-variables#tidb_redact_log): Determines whether to desensitize user data using `?` in the SQL statement recorded in the slow log. The default value is `0`, which means to disable the feature.
* [`tidb_enable_collect_execution_info`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_collect_execution_info): Determines whether to record the physical execution information of each operator in the execution plan. The default value is `1`. This feature impacts the performance by approximately 3%. After enabling this feature, you can view the `Plan` information as follows:

    ```sql
    > select tidb_decode_plan('jAOIMAk1XzE3CTAJMQlmdW5jczpjb3VudChDb2x1bW4jNyktPkMJC/BMNQkxCXRpbWU6MTAuOTMxNTA1bXMsIGxvb3BzOjIJMzcyIEJ5dGVzCU4vQQoxCTMyXzE4CTAJMQlpbmRleDpTdHJlYW1BZ2dfOQkxCXQRSAwyNzY4LkgALCwgcnBjIG51bTogMQkMEXMQODg0MzUFK0hwcm9jIGtleXM6MjUwMDcJMjA2HXsIMgk1BWM2zwAAMRnIADcVyAAxHcEQNQlOL0EBBPBbCjMJMTNfMTYJMQkzMTI4MS44NTc4MTk5MDUyMTcJdGFibGU6dCwgaW5kZXg6aWR4KGEpLCByYW5nZTpbLWluZiw1MDAwMCksIGtlZXAgb3JkZXI6ZmFsc2UJMjUBrgnQVnsA');
    +------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | tidb_decode_plan('jAOIMAk1XzE3CTAJMQlmdW5jczpjb3VudChDb2x1bW4jNyktPkMJC/BMNQkxCXRpbWU6MTAuOTMxNTA1bXMsIGxvb3BzOjIJMzcyIEJ5dGVzCU4vQQoxCTMyXzE4CTAJMQlpbmRleDpTdHJlYW1BZ2dfOQkxCXQRSAwyNzY4LkgALCwgcnBjIG51bTogMQkMEXMQODg0MzUFK0hwcm9jIGtleXM6MjUwMDcJMjA2HXsIMg |
    +------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    |     id                    task    estRows               operator info                                                  actRows    execution info                                                                  memory       disk                              |
    |     StreamAgg_17          root    1                     funcs:count(Column#7)->Column#5                                1          time:10.931505ms, loops:2                                                       372 Bytes    N/A                               |
    |     └─IndexReader_18      root    1                     index:StreamAgg_9                                              1          time:10.927685ms, loops:2, rpc num: 1, rpc time:10.884355ms, proc keys:25007    206 Bytes    N/A                               |
    |       └─StreamAgg_9       cop     1                     funcs:count(1)->Column#7                                       1          time:11ms, loops:25                                                             N/A          N/A                               |
    |         └─IndexScan_16    cop     31281.857819905217    table:t, index:idx(a), range:[-inf,50000), keep order:false    25007      time:11ms, loops:25                                                             N/A          N/A                               |
    +------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    ```

If you are conducting a performance test, you can disable the feature of automatically collecting the execution information of operators:

```sql
set @@tidb_enable_collect_execution_info=0;
```

The returned result of the `Plan` field has roughly the same format with that of `EXPLAIN` or `EXPLAIN ANALYZE`. For more details of the execution plan, see [`EXPLAIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain) or [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze).

For more information, see [TiDB specific variables and syntax](https://docs.pingcap.com/tidb/stable/system-variables).
