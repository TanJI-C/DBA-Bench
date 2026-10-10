# Async write latency breakdown in TiKV

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/latency-breakdown.md`
- Source Title: `Latency Breakdown`
- Source Heading Path: `Latency Breakdown > Async write | Latency Breakdown > Async write > Raft DB | Latency Breakdown > Async write > KV DB`
- Source Line Ranges: `662-857`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`
- Topic Tags: `latency`, `async-write`, `raft`, `raft-engine`, `rocksdb`, `commit`, `apply`, `metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0122_6493df6631`
- Source ID: `tidb-docs-8.1:latency-breakdown.md#async-write`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bd2ab2657aa12382a0706b46a8de84748e242038d96eb05a48bdf066edc7a6f1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/latency-breakdown#async-write
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/latency-breakdown.md

## Retrieval Guidance

- Use When: Use this chunk when breaking down TiKV async write latency into propose, commit, apply, Raft DB, or KV DB phases using waterfall and performance context metrics.
- Retrieval Keywords: Async write latency breakdown in TiKV, async write duration, Propose Wait, Process Command, Apply Wait, Apply Log, tikv_raftstore_apply_wait_time_duration_secs, tikv_raftstore_apply_log_duration_seconds, tikv_raftstore_store_wf_batch_wait_duration_seconds, tikv_raftstore_store_wf_send_to_queue_duration_seconds, tikv_raftstore_store_wf_before_write_duration_seconds, tikv_raftstore_store_wf_write_end_duration_seconds, tikv_raftstore_store_wf_persist_duration_seconds, tikv_raftstore_store_wf_send_proposal_duration_seconds, tikv_raftstore_store_wf_commit_log_duration, persist log locally duration, wait by write worker duration, replicate log duration, commit log wait duration, Raft DB, KV DB, raft_engine_write_preprocess_duration_seconds, raft_engine_write_leader_duration_seconds, raft_engine_write_apply_duration_seconds, tikv_raftstore_store_perf_context_time_duration_secs{type="write_thread_wait"}, tikv_raftstore_store_perf_context_time_duration_secs{type="write_scheduling_flushes_compactions_time"}, tikv_raftstore_store_perf_context_time_duration_secs{type="write_wal_time"}, tikv_raftstore_store_perf_context_time_duration_secs{type="write_memtable_time"}, tikv_raftstore_apply_perf_context_time_duration_secs{type="write_thread_wait"}, tikv_raftstore_apply_perf_context_time_duration_secs{type="write_scheduling_flushes_compactions_time"}, tikv_raftstore_apply_perf_context_time_duration_secs{type="write_wal_time"}, tikv_raftstore_apply_perf_context_time_duration_secs{type="write_memtable_time"}, store-io-pool-size, Async IO Raft, Raft Engine
- Follow-up Guidance: The chunk also states that Async IO Raft is enabled only when `store-io-pool-size` is set to a positive value, and that Raft Engine changes the log-writing process.
- Classification Note: This chunk is classified as performance for TiKV because it defines formulas and metrics to attribute async write latency across propose, commit, apply, Raft DB, and KV DB stages.

## Official Source Content

## Async write

Async write is the process that TiKV writes data into the Raft-based replicated state machine asynchronously with a callback.

- The following is the time cost diagram of async write operations when the asynchronous IO is disabled:

    ```railroad+diagram
    Diagram(
        NonTerminal("Propose Wait"),
        NonTerminal("Process Command"),
        Choice(
            0,
            Sequence(
                NonTerminal("Wait Current Batch"),
                NonTerminal("Write to Log Engine"),
            ),
            Sequence(
                NonTerminal("RaftMsg Send Wait"),
                NonTerminal("Commit Log Wait"),
            ),
        ),
        NonTerminal("Apply Wait"),
        NonTerminal("Apply Log"),
    )
    ```

- The following is the time cost diagram of async write operations when the asynchronous IO is enabled:

    ```railroad+diagram
    Diagram(
        NonTerminal("Propose Wait"),
        NonTerminal("Process Command"),
        Choice(
            0,
            NonTerminal("Wait Until Persisted by Write Worker"),
            Sequence(
                NonTerminal("RaftMsg Send Wait"),
                NonTerminal("Commit Log Wait"),
            ),
        ),
        NonTerminal("Apply Wait"),
        NonTerminal("Apply Log"),
    )
    ```

The async write duration is calculated as:

```text
async write duration(async io disabled) =
    propose +
    async io disabled commit +
    tikv_raftstore_apply_wait_time_duration_secs +
    tikv_raftstore_apply_log_duration_seconds

async write duration(async io enabled) =
    propose +
    async io enabled commit +
    tikv_raftstore_apply_wait_time_duration_secs +
    tikv_raftstore_apply_log_duration_seconds
```

Async write can be broken down into the following three phases:

- Propose
- Commit
- Apply: `tikv_raftstore_apply_wait_time_duration_secs + tikv_raftstore_apply_log_duration_seconds` in the preceding formula

The duration of the propose phase is calculated as:

```text
propose =
    propose wait duration +
    propose duration

propose wait duration =
    tikv_raftstore_store_wf_batch_wait_duration_seconds

propose duration =
    tikv_raftstore_store_wf_send_to_queue_duration_seconds -
    tikv_raftstore_store_wf_batch_wait_duration_seconds
```

The Raft process is recorded in a waterfall manner. So the propose duration is calculated from the difference between the two metrics.

The duration of the commit phase is calculated as:

```text
async io disabled commit = max(
    persist log locally duration,
    replicate log duration
)

async io enabled commit = max(
    wait by write worker duration,
    replicate log duration
)
```

Since v5.3.0, TiKV supports Async IO Raft (write Raft log by a StoreWriter thread pool). The Async IO Raft is only enabled when the [`store-io-pool-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#store-io-pool-size-new-in-v530) is set to a positive value, which changes the process of commit. The `persist log locally duration` and `wait by write worker duration` are calculated as:

```text
persist log locally duration =
    batch wait duration +
    write to raft db duration

batch wait duration =
    tikv_raftstore_store_wf_before_write_duration_seconds -
    tikv_raftstore_store_wf_send_to_queue_duration_seconds

write to raft db duration =
    tikv_raftstore_store_wf_write_end_duration_seconds -
    tikv_raftstore_store_wf_before_write_duration_seconds

wait by write worker duration =
    tikv_raftstore_store_wf_persist_duration_seconds -
    tikv_raftstore_store_wf_send_to_queue_duration_seconds
```

The difference between with and without Async IO is the duration of persisting logs locally. With Async IO, the duration of persisting log locally can be calculated from the waterfall metrics directly (skip the batch wait duration).

The replicate log duration records the duration of log persisted in quorum peers, which contains an RPC duration and the duration of log persisting in the majority. The `replicate log duration` is calculated as:

```text
replicate log duration =
    raftmsg send wait duration +
    commit log wait duration

raftmsg send wait duration =
    tikv_raftstore_store_wf_send_proposal_duration_seconds -
    tikv_raftstore_store_wf_send_to_queue_duration_seconds

commit log wait duration =
    tikv_raftstore_store_wf_commit_log_duration -
    tikv_raftstore_store_wf_send_proposal_duration_seconds
```
### Raft DB

The following is the time cost diagram of Raft DB operations:

```railroad+diagram
Diagram(
    NonTerminal("Wait for Writer Leader"),
    NonTerminal("Write and Sync Log"),
    NonTerminal("Apply Log to Memtable"),
)
```

```text
write to raft db duration = raft db write duration
commit log wait duration >= raft db write duration

raft db write duration(raft engine enabled) =
    raft_engine_write_preprocess_duration_seconds +
    raft_engine_write_leader_duration_seconds +
    raft_engine_write_apply_duration_seconds

raft db write duration(raft engine disabled) =
    tikv_raftstore_store_perf_context_time_duration_secs{type="write_thread_wait"} +
    tikv_raftstore_store_perf_context_time_duration_secs{type="write_scheduling_flushes_compactions_time"} +
    tikv_raftstore_store_perf_context_time_duration_secs{type="write_wal_time"} +
    tikv_raftstore_store_perf_context_time_duration_secs{type="write_memtable_time"}
```

Because `commit log wait duration` is the longest duration of quorum peers, it might be larger than `raft db write duration`.

Since v6.1.0, TiKV uses [Raft Engine](https://docs.pingcap.com/tidb/stable/glossary#raft-engine) as its default log storage engine, which changes the process of writing log.
### KV DB

The following is the time cost diagram of KV DB operations:

```railroad+diagram
Diagram(
    NonTerminal("Wait for Writer Leader"),
    NonTerminal("Preprocess"),
    Choice(
        0,
        Comment("No Need to Switch"),
        NonTerminal("Switch WAL or Memtable"),
    ),
    NonTerminal("Write and Sync WAL"),
    NonTerminal("Apply to Memtable"),
)
```

```text
tikv_raftstore_apply_log_duration_seconds =
    tikv_raftstore_apply_perf_context_time_duration_secs{type="write_thread_wait"} +
    tikv_raftstore_apply_perf_context_time_duration_secs{type="write_scheduling_flushes_compactions_time"} +
    tikv_raftstore_apply_perf_context_time_duration_secs{type="write_wal_time"} +
    tikv_raftstore_apply_perf_context_time_duration_secs{type="write_memtable_time"}
```

In the async write process, committed logs need to be applied to the KV DB. The applying duration can be calculated from the RocksDB performance context.
