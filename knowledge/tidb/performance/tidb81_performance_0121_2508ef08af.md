# Index lookup and write-query lock latency formulas

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/latency-breakdown.md`
- Source Title: `Latency Breakdown`
- Source Heading Path: `Latency Breakdown > Read queries > Index look up | Latency Breakdown > Write queries | Latency Breakdown > Write queries > Lock-time point get | Latency Breakdown > Write queries > Lock-time batch point get | Latency Breakdown > Write queries > Lock`
- Source Line Ranges: `254-446`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `shared`
- Topic Tags: `latency`, `read-queries`, `write-queries`, `index-lookup`, `point-get`, `batch-point-get`, `pessimistic-lock`, `2pc`, `rpc`, `metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0121_2508ef08af`
- Source ID: `tidb-docs-8.1:latency-breakdown.md#index-look-up`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ced38aaf30441915ca05d370678427e92999b7bded55cc84e9a17252188f835c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/latency-breakdown#index-look-up
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/latency-breakdown.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving formulas and metric relationships for index lookup latency, write-query phases, SELECT FOR UPDATE lock-time point get or batch point get, and pessimistic lock latency in TiDB.
- Retrieval Keywords: index look up, tidb_session_execute_duration_seconds{type="general"}, pd_client_cmd_handle_cmds_duration_seconds{type="wait"}, tidb_distsql_handle_query_duration_seconds{sql_type="general"}, req_per_copr, rate(tidb_distsql_handle_query_duration_seconds_count) / rate(tidb_distsql_scan_keys_partial_num_count), write queries, execute phase, lock phase, commit phase, two-phase commit protocol (2PC), SELECT FOR UPDATE, lock-time point get, lock-time batch point get, execution(clustered PK), execution(non-clustered PK or UK), tidb_tikvclient_txn_cmd_duration_seconds{type="lock_keys"}, tidb_tikvclient_txn_cmd_duration_seconds{type="batch_get"}, PessimisticLock, tidb_tikvclient_request_seconds{type="PessimisticLock"}, committer-concurrency, tidb_tikvclient_txn_regions_num_sum{type="2pc_pessimistic_lock"}, tidb_tikvclient_txn_regions_num_count{type="2pc_pessimistic_lock"}, tikv_grpc_msg_duration_seconds{type="kv_pessimistic_lock"}, tikv_scheduler_latch_wait_duration_seconds{type="acquire_pessimistic_lock"}, tikv_storage_engine_async_request_duration_seconds{type="snapshot"}, tikv_in_memory_pessimistic_locking{result="success"}, tikv_in_memory_pessimistic_locking{result="full"}, tikv_storage_rocksdb_perf{metric="block_read_time",req="acquire_pessimistic_lock"}, tikv_storage_rocksdb_perf{metric="block_read_count",req="acquire_pessimistic_lock"}, in-memory pessimistic lock
- Follow-up Guidance: The chunk also points to related sections for more detail: Batch point get, Batch client, TiKV Snapshot, and Async write.
- Classification Note: This chunk is classified under performance for the TiDB component because the content breaks down latency formulas and metrics for read-path index lookup and write-path pessimistic locking, with related TiKV and PD metrics in a self-managed deployment scope.

## Official Source Content

### Index look up

The following is the time cost diagram of index look up operations:

```railroad+diagram
Diagram(
    Stack(
        NonTerminal("Resolve TSO"),
        NonTerminal("Load region cache for related index ranges"),
        OneOrMore(
            Sequence(
                NonTerminal("Wait for index scan result"),
                NonTerminal("Wait for table scan result"),
            ),
        Comment("Next loop: drain the result"),
        ),
    ),
)
```

During index look up, the `tidb_session_execute_duration_seconds{type="general"}` duration is calculated as:

```text
tidb_session_execute_duration_seconds{type="general"} =
    pd_client_cmd_handle_cmds_duration_seconds{type="wait"} +
    req_per_copr * (
        tidb_distsql_handle_query_duration_seconds{sql_type="general"}
    ) +
    req_per_copr * (
        tidb_distsql_handle_query_duration_seconds{sql_type="general"}
    )

req_per_copr = rate(tidb_distsql_handle_query_duration_seconds_count) / rate(tidb_distsql_scan_keys_partial_num_count)
```

An index look up combines index scan and table scan, which are processed in a pipeline.
## Write queries

Write queries are much more complex than read queries. There are some variants of write queries. The following is the time cost diagram of write queries operations:

```railroad+diagram
Diagram(
    NonTerminal("Execute write query"),
    Choice(
        0,
        NonTerminal("Pessimistic lock keys"),
        Comment("bypass in optimistic transaction"),
    ),
    Choice(
        0,
        NonTerminal("Auto Commit Transaction"),
        Comment("bypass in non-auto-commit or explicit transaction"),
    ),
)
```

|                 | Pessimistic transaction | Optimistic transaction |
|-----------------|-------------------------|------------------------|
| Auto-commit     | execute + lock + commit | execute + commit       |
| Non-auto-commit | execute + lock          | execute                |

A write query is divided into the following three phases:

- execute phase: execute and write mutation into the memory of TiDB.
- lock phase: acquire pessimistic locks for the execution result.
- commit phase: commit the transaction via the two-phase commit protocol (2PC).

In the execute phase, TiDB manipulates data in memory and the main latency comes from reading the required data. For update and delete queries, TiDB reads data from TiKV first, and then updates or deletes the row in memory.

The exception is lock-time read operations (`SELECT FOR UPDATE`) with point get and batch point get, which perform read and lock in a single Remote Procedure Call (RPC).
### Lock-time point get

The following is the time cost diagram of lock-time point get operations:

```railroad+diagram
Diagram(
    Choice(
        0,
        Sequence(
            NonTerminal("Read handle key by index key"),
            NonTerminal("Lock index key"),
        ),
        Comment("Clustered index"),
    ),
    NonTerminal("Lock handle key"),
    NonTerminal("Read value from pessimistic lock cache"),
)
```

During lock-time point get, the `execution(clustered PK)` and `execution(non-clustered PK or UK)` duration are calculated as:

```text
execution(clustered PK) =
    tidb_tikvclient_txn_cmd_duration_seconds{type="lock_keys"}
execution(non-clustered PK or UK) =
    2 * tidb_tikvclient_txn_cmd_duration_seconds{type="lock_keys"}
```

Lock-time point get locks the key and returns its value. Compared with the lock phase after execution, this saves 1 round trip. The duration of the lock-time point get can be treated the same as [Lock duration](#lock).
### Lock-time batch point get

The following is the time cost diagram of lock-time batch point get operations:

```railroad+diagram
Diagram(
    Choice(
        0,
        NonTerminal("Read handle keys by index keys"),
        Comment("Clustered index"),
    ),
    NonTerminal("Lock index and handle keys"),
    NonTerminal("Read values from pessimistic lock cache"),
)
```

During lock-time batch point get, the `execution(clustered PK)` and `execution(non-clustered PK or UK)` duration are calculated as:

```text
execution(clustered PK) =
    tidb_tikvclient_txn_cmd_duration_seconds{type="lock_keys"}
execution(non-clustered PK or UK) =
    tidb_tikvclient_txn_cmd_duration_seconds{type="batch_get"} +
    tidb_tikvclient_txn_cmd_duration_seconds{type="lock_keys"}
```

The execution of the lock-time batch point get is similar to the [Lock-time point get](#lock-time-point-get) except that the lock-time batch point get reads multiple values in a single RPC. For more details about the `tidb_tikvclient_txn_cmd_duration_seconds{type="batch_get"}` duration, refer to the [Batch point get](#batch-point-get) section.
### Lock

This section describes the lock duration.

```text
round = ceil(
    sum(rate(tidb_tikvclient_txn_regions_num_sum{type="2pc_pessimistic_lock"})) /
    sum(rate(tidb_tikvclient_txn_regions_num_count{type="2pc_pessimistic_lock"})) /
    committer-concurrency
)

lock = tidb_tikvclient_txn_cmd_duration_seconds{type="lock_keys"} =
    round * tidb_tikvclient_request_seconds{type="PessimisticLock"}
```

Locks are acquired through the 2PC structure, which has a flow control mechanism. The flow control limits concurrent on-the-fly requests by `committer-concurrency` (default value is `128`). For simplicity, the flow control can be treated as an amplification of request latency (`round`).

The `tidb_tikvclient_request_seconds{type="PessimisticLock"}` is calculated as:

```text
tidb_tikvclient_request_seconds{type="PessimisticLock"} =
    tidb_tikvclient_batch_wait_duration +
    tidb_tikvclient_batch_send_latency +
    tikv_grpc_msg_duration_seconds{type="kv_pessimistic_lock"} +
    tidb_tikvclient_rpc_net_latency_seconds{store="?"}
```

For more details about the preceding batch client duration, such as `tidb_tikvclient_batch_wait_duration`, `tidb_tikvclient_batch_send_latency`, and `tidb_tikvclient_rpc_net_latency_seconds{store="?"}`, refer to the [Batch client](#batch-client) section.

The `tikv_grpc_msg_duration_seconds{type="kv_pessimistic_lock"}` duration is calculated as:

```text
tikv_grpc_msg_duration_seconds{type="kv_pessimistic_lock"} =
    tikv_scheduler_latch_wait_duration_seconds{type="acquire_pessimistic_lock"} +
    tikv_storage_engine_async_request_duration_seconds{type="snapshot"} +
    (lock in-mem key count + lock on-disk key count) * lock read duration +
    lock on-disk key count / (lock in-mem key count + lock on-disk key count) *
    lock write duration
```

- Since TiDB v6.0, TiKV uses [in-memory pessimistic lock](https://docs.pingcap.com/tidb/stable/pessimistic-transaction#in-memory-pessimistic-lock) by default. In-memory pessimistic lock bypass the async write process.
- `tikv_storage_engine_async_request_duration_seconds{type="snapshot"}` is a snapshot type duration. For more details, refer to the [TiKV Snapshot](#tikv-snapshot) section.
- The `lock in-mem key count` and `lock on-disk key count` are calculated as:

    ```text
    lock in-mem key count =
        sum(rate(tikv_in_memory_pessimistic_locking{result="success"})) /
        sum(rate(tikv_grpc_msg_duration_seconds_count{type="kv_pessimistic_lock"}}))

    lock on-disk key count =
        sum(rate(tikv_in_memory_pessimistic_locking{result="full"})) /
        sum(rate(tikv_grpc_msg_duration_seconds_count{type="kv_pessimistic_lock"}}))
    ```

    The count of in-memory and on-disk locked keys can be calculated by the in-memory lock counter. TiKV reads the keys' values before acquiring locks, and the read duration can be calculated by RocksDB performance context.

    ```text
    lock read duration(from disk) =
        sum(rate(tikv_storage_rocksdb_perf{metric="block_read_time",req="acquire_pessimistic_lock"})) / sum(rate(tikv_storage_rocksdb_perf{metric="block_read_count",req="acquire_pessimistic_lock"}))
    ```

- `lock write duration` is the duration of writing on-disk lock. For more details, refer to the [Async write](#async-write) section.
