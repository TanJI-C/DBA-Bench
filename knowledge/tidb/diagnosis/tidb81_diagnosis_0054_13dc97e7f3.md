# Commit latency, batch client, and TiKV snapshot breakdown

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/latency-breakdown.md`
- Source Title: `Latency Breakdown`
- Source Heading Path: `Latency Breakdown > Write queries > Commit | Latency Breakdown > Batch client | Latency Breakdown > TiKV snapshot`
- Source Line Ranges: `447-661`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `latency`, `commit`, `2pc`, `async-commit`, `1pc`, `prewrite`, `batch-client`, `rpc`, `network-latency`, `snapshot`, `metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0054_13dc97e7f3`
- Source ID: `tidb-docs-8.1:latency-breakdown.md#commit`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2b352e3ccf750e673d35b8845e3ca59a2d1bffe43b2e613a1f8f123f6623f480`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/latency-breakdown#commit
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/latency-breakdown.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing write or read latency by breaking down commit duration, batch client request time, or TiKV snapshot time into TiDB, TiKV, PD, RPC, and network-related metrics.
- Retrieval Keywords: Commit latency breakdown, Get_latest_ts_time, Prewrite_time, Get_commit_ts_time, Commit_time, pd_client_cmd_handle_cmds_duration_seconds{type="wait"}, tidb_tikvclient_txn_regions_num_sum{type="2pc_prewrite"}, tidb_tikvclient_txn_regions_num_count{type="2pc_prewrite"}, tidb_tikvclient_txn_regions_num_sum{type="2pc_commit"}, tidb_tikvclient_txn_regions_num_count{type="2pc_commit"}, committer-concurrency, tidb_tikvclient_request_seconds{type="Prewrite"}, tidb_tikvclient_request_seconds{type="Commit"}, tidb_tikvclient_batch_wait_duration, tidb_tikvclient_batch_send_latency, tidb_tikvclient_rpc_net_latency_seconds, tikv_grpc_msg_duration_seconds{type="kv_prewrite"}, tikv_grpc_msg_duration_seconds{type="kv_commit"}, tikv_scheduler_kv_command_key_write_sum{type="prewrite"}, tikv_scheduler_kv_command_key_write_count{type="prewrite"}, tikv_scheduler_kv_command_key_write_sum{type="commit"}, tikv_scheduler_kv_command_key_write_count{type="commit"}, tikv_storage_rocksdb_perf{metric="block_read_time",req="prewrite"}, tikv_storage_rocksdb_perf{metric="block_read_count",req="prewrite"}, tikv_storage_rocksdb_perf{metric="block_read_time",req="commit"}, tikv_storage_rocksdb_perf{metric="block_read_count",req="commit"}, Batch client, ConnArray, BatchConn, tikv-client.max-batch-size, CmdBatchCop, CmdCopStream, CmdMPPConn, TiKV snapshot, tikv_storage_engine_async_request_duration_seconds{type="snapshot"}, tikv_coprocessor_request_wait_seconds{type="snapshot"}, tikv_raftstore_request_wait_time_duration_secs, tikv_raftstore_commit_log_duration_seconds, 2pc, async-commit, 1pc, read index, snapshot
- Follow-up Guidance: For prewrite and commit request timing, this chunk points to the Batch client section for `tidb_tikvclient_batch_wait_duration`, `tidb_tikvclient_batch_send_latency`, and `tidb_tikvclient_rpc_net_latency_seconds{store="?"}`, and it points to the Async write section for write duration details.
- Classification Note: The official content is classified as diagnosis because it explains how to decompose commit, batch client, and snapshot latency using formulas and specific metrics across TiDB, TiKV, and PD.

## Official Source Content

### Commit

This section describes the commit duration. The following is the time cost diagram of commit operations:

```railroad+diagram
Diagram(
    Stack(
        Sequence(
            Choice(
                0,
                Comment("use 2pc or causal consistency"),
                NonTerminal("Get min-commit-ts"),
            ),
            Optional("Async prewrite binlog"),
            NonTerminal("Prewrite mutations"),
            Optional("Wait prewrite binlog result"),
        ),
        Sequence(
            Choice(
                1,
                Comment("1pc"),
                Sequence(
                    Comment("2pc"),
                    NonTerminal("Get commit-ts"),
                    NonTerminal("Check schema"),
                    NonTerminal("Commit PK mutation"),
                ),
                Sequence(
                    Comment("async-commit"),
                    NonTerminal("Commit mutations asynchronously"),
                ),
            ),
            Choice(
                0,
                Comment("committed"),
                NonTerminal("Async cleanup"),
            ),
            Optional("Commit binlog"),
        ),
    ),
)
```

The duration of the commit phase is calculated as:

```text
commit =
    Get_latest_ts_time +
    Prewrite_time +
    Get_commit_ts_time +
    Commit_time

Get_latest_ts_time = Get_commit_ts_time =
    pd_client_cmd_handle_cmds_duration_seconds{type="wait"}

prewrite_round = ceil(
    sum(rate(tidb_tikvclient_txn_regions_num_sum{type="2pc_prewrite"})) /
    sum(rate(tidb_tikvclient_txn_regions_num_count{type="2pc_prewrite"})) /
    committer-concurrency
)

commit_round = ceil(
    sum(rate(tidb_tikvclient_txn_regions_num_sum{type="2pc_commit"})) /
    sum(rate(tidb_tikvclient_txn_regions_num_count{type="2pc_commit"})) /
    committer-concurrency
)

Prewrite_time =
    prewrite_round * tidb_tikvclient_request_seconds{type="Prewrite"}

Commit_time =
    commit_round * tidb_tikvclient_request_seconds{type="Commit"}
```

The commit duration can be broken down into four metrics:

- `Get_latest_ts_time` records the duration of getting latest TSO in async-commit or single-phase commit (1PC) transaction.
- `Prewrite_time` records the duration of the prewrite phase.
- `Get_commit_ts_time` records the duration of common 2PC transaction.
- `Commit_time` records the duration of the commit phase. Note that an async-commit or 1PC transaction does not have this phase.

Like pessimistic lock, flow control acts as an amplification of latency (`prewrite_round` and `commit_round` in the preceding formula).

The `tidb_tikvclient_request_seconds{type="Prewrite"}` and `tidb_tikvclient_request_seconds{type="Commit"}` duration are calculated as:

```text
tidb_tikvclient_request_seconds{type="Prewrite"} =
    tidb_tikvclient_batch_wait_duration +
    tidb_tikvclient_batch_send_latency +
    tikv_grpc_msg_duration_seconds{type="kv_prewrite"} +
    tidb_tikvclient_rpc_net_latency_seconds{store="?"}

tidb_tikvclient_request_seconds{type="Commit"} =
    tidb_tikvclient_batch_wait_duration +
    tidb_tikvclient_batch_send_latency +
    tikv_grpc_msg_duration_seconds{type="kv_commit"} +
    tidb_tikvclient_rpc_net_latency_seconds{store="?"}
```

For more details about the preceding batch client duration, such as `tidb_tikvclient_batch_wait_duration`, `tidb_tikvclient_batch_send_latency`, and `tidb_tikvclient_rpc_net_latency_seconds{store="?"}`, refer to the [Batch client](#batch-client) section.

The `tikv_grpc_msg_duration_seconds{type="kv_prewrite"}` is calculated as:

```text
tikv_grpc_msg_duration_seconds{type="kv_prewrite"} =
    prewrite key count * prewrite read duration +
    prewrite write duration

prewrite key count =
    sum(rate(tikv_scheduler_kv_command_key_write_sum{type="prewrite"})) /
    sum(rate(tikv_scheduler_kv_command_key_write_count{type="prewrite"}))

prewrite read duration(from disk) =
    sum(rate(tikv_storage_rocksdb_perf{metric="block_read_time",req="prewrite"})) / sum(rate(tikv_storage_rocksdb_perf{metric="block_read_count",req="prewrite"}))
```

Like locks in TiKV, prewrite is processed in read and write phases. The read duration can be calculated from the RocksDB performance context. For more details about the write duration, refer to the [Async write](#async-write) section.

The `tikv_grpc_msg_duration_seconds{type="kv_commit"}` is calculated as:

```text
tikv_grpc_msg_duration_seconds{type="kv_commit"} =
    commit key count * commit read duration +
    commit write duration

commit key count =
    sum(rate(tikv_scheduler_kv_command_key_write_sum{type="commit"})) /
    sum(rate(tikv_scheduler_kv_command_key_write_count{type="commit"}))

commit read duration(from disk) =
    sum(rate(tikv_storage_rocksdb_perf{metric="block_read_time",req="commit"})) / sum(rate(tikv_storage_rocksdb_perf{metric="block_read_count",req="commit"})) (storage)
```

The duration of `kv_commit` is almost the same as `kv_prewrite`. For more details about the write duration, refer to the [Async write](#async-write) section.
## Batch client

The following is the time cost diagram of the batch client:

```railroad+diagram
Diagram(
    NonTerminal("Get conn pool to the target store"),
    Choice(
        0,
        Sequence(
            Comment("Batch enabled"),
                NonTerminal("Push request to channel"),
                NonTerminal("Wait response"),
            ),
            Sequence(
            NonTerminal("Get conn from pool"),
            NonTerminal("Call RPC"),
            Choice(
                0,
                Comment("Unary call"),
                NonTerminal("Recv first"),
            ),
        ),
    ),
)
```

- The overall duration of sending a request is observed as `tidb_tikvclient_request_seconds`.
- RPC client maintains connection pools (named ConnArray) to each store, and each pool has a BatchConn with a batch request (send) channel.
- Batch is enabled when the store is TiKV and batch size is positive, which is true in most cases.
- The size of batch request channel is [`tikv-client.max-batch-size`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#max-batch-size) (default is `128`), the duration of enqueue is observed as `tidb_tikvclient_batch_wait_duration`.
- There are three kinds of stream requests: `CmdBatchCop`, `CmdCopStream`, and `CmdMPPConn`, which involve an additional `recv()` call to fetch the first response from the stream.

Though there is still some latency missed observed, the `tidb_tikvclient_request_seconds` can be calculated approximately as:

```text
tidb_tikvclient_request_seconds{type="?"} =
    tidb_tikvclient_batch_wait_duration +
    tidb_tikvclient_batch_send_latency +
    tikv_grpc_msg_duration_seconds{type="kv_?"} +
    tidb_tikvclient_rpc_net_latency_seconds{store="?"}
```

- `tidb_tikvclient_batch_wait_duration` records the waiting duration in the batch system.
- `tidb_tikvclient_batch_send_latency` records the encode duration in the batch system.
- `tikv_grpc_msg_duration_seconds{type="kv_?"}` is the TiKV processing duration.
- `tidb_tikvclient_rpc_net_latency_seconds` records the network latency.
## TiKV snapshot

The following is the time cost diagram of TiKV snapshot operations:

```railroad+diagram
Diagram(
    Choice(
        0,
        Comment("Local Read"),
        Sequence(
            NonTerminal("Propose Wait"),
            NonTerminal("Read index Read Wait"),
        ),
    ),
    NonTerminal("Fetch A Snapshot From KV Engine"),
)
```

The overall duration of a TiKV snapshot is observed as `tikv_storage_engine_async_request_duration_seconds{type="snapshot"}` and is calculated as:

```text
tikv_storage_engine_async_request_duration_seconds{type="snapshot"} =
    tikv_coprocessor_request_wait_seconds{type="snapshot"} =
    tikv_raftstore_request_wait_time_duration_secs +
    tikv_raftstore_commit_log_duration_seconds +
    get snapshot from rocksdb duration
```

When leader lease is expired, TiKV proposes a read index command before getting a snapshot from RocksDB. `tikv_raftstore_request_wait_time_duration_secs` and `tikv_raftstore_commit_log_duration_seconds` are the duration of committing read index command.

Since getting a snapshot from RocksDB is usually a fast operation, the `get snapshot from rocksdb duration` is ignored.
