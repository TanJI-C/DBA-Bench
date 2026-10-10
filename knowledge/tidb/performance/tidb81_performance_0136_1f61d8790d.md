# Performance Overview latency analysis for KV/TSO and TiKV write path

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-tuning-methods.md`
- Source Title: `Performance Analysis and Tuning`
- Source Heading Path: `Performance Analysis and Tuning > Performance analysis and tuning using the Performance Overview dashboard > Query latency breakdown and key latency metrics > KV and TSO Request Duration | Performance Analysis and Tuning > Performance analysis and tuning using the Performance Overview dashboard > Query latency breakdown and key latency metrics > Storage Async Write Duration, Store Duration, and Apply Duration`
- Source Line Ranges: `337-434`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dashboard`
- Topic Tags: `performance-overview`, `latency`, `kv-requests`, `tso`, `pd-client`, `execute-phase`, `write-path`, `raftstore`, `store-duration`, `apply-duration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0136_1f61d8790d`
- Source ID: `tidb-docs-8.1:performance-tuning-methods.md#kv-and-tso-request-duration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d94d2011ee37b6772b4384a744f4ca1dd0ccca20d12c215924ddc58cacb57f73`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-tuning-methods#kv-and-tso-request-duration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-tuning-methods.md

## Retrieval Guidance

- Use When: Use this chunk when analyzing query latency in the Performance Overview dashboard for TSO wait or KV request delays, or when breaking down TiKV write-path latency into Store Duration and Apply Duration.
- Retrieval Keywords: KV and TSO Request Duration, PD TSO Wait/RPC Duration, Avg TiDB KV Request Duration, Avg TiKV GRPC Duration, TSO WAIT, TSO RPC, TSFuture, Wait method, execute phase, Get, BatchGet, Cop, PessimisticLock, Prewrite, Commit, Storage Async Write Duration, Store Duration, Apply Duration, avg Storage Async Write Duration = avg Store Duration + avg Apply Duration, raftstore, scheduler worker
- Follow-up Guidance: The source also provides example comparisons for same data center, different data centers in the same region, and overloaded public cloud cases, plus a write-path example showing when Store Duration is the bottleneck.
- Classification Note: This is classified as performance content because it explains Performance Overview latency metrics for TiDB, PD, and TiKV request paths and shows how to identify write bottlenecks from dashboard durations.

## Official Source Content

#### KV and TSO Request Duration

TiDB interacts with PD and TiKV in the `execute` phase. As shown in the following figure, when processing SQL request, TiDB requests TSOs before entering the `parse` and `compile` phases. The PD Client does not block the caller, but returns a `TSFuture` and asynchronously sends and receives the TSO requests in the background. Once the PD client finishes handling the TSO requests, it returns `TSFuture`. The holder of the `TSFuture` needs to call the Wait method to get the final TSOs. After TiDB finishes the `parse` and `compile` phases, it enters the `execute` phase, where two situations might occur:

- If the TSO request has completed, the Wait method immediately returns an available TSO or an error
- If the TSO request has not yet completed, the Wait method is blocked until a TSO is available or an error appears (the gRPC request has been sent but no result is returned, and the network latency is high)

The TSO wait time is recorded as `TSO WAIT` and the network time of the TSO request is recorded as `TSO RPC`. After the TSO wait is complete, TiDB executor usually sends read or write requests to TiKV.

- Common KV read requests: `Get`, `BatchGet`, and `Cop`
- Common KV write requests: `PessimisticLock`, `Prewrite` and `Commit` for two-phase commits

![Execute](/media/performance/execute_phase.png)

The indicators in this section correspond to the following three panels.

- Avg TiDB KV Request Duration: The average latency of KV requests measured by TiDB
- Avg TiKV GRPC Duration: The average latency in processing gPRC messages in TiKV
- PD TSO Wait/RPC Duration: TiDB executor TSO wait time and network latency for TSO requests (RPC)

The relationship between `Avg TiDB KV Request Duration` and `Avg TiKV GRPC Duration` is as follows:

```
Avg TiDB KV Request Duration = Avg TiKV GRPC Duration + Network latency between TiDB and TiKV + TiKV gRPC processing time + TiDB gRPC processing time and scheduling latency
```

The difference between `Avg TiDB KV Request Duration` and `Avg TiKV GRPC Duration` is closely related to the network traffic, network latency, and resource usage by TiDB and TiKV.

- In the same data center: The difference is generally less than 2 ms.
- In different availability zones in the same region: The difference is generally less than 5 ms.

**Example 1: Low workload of clusters deployed on the same data center**

![Same Data Center](/media/performance/oltp_kv_tso.png)

In this workload, the average `Prewrite` latency on TiDB is 925 us, and the average `kv_prewrite` processing latency inside TiKV is 720 us. The difference is about 200 us, which is normal in the same data center. The average TSO wait latency is 206 us, and the RPC time is 144 us.

**Example 2: Normal workload on public cloud clusters**

![Cloud Env ](/media/performance/cloud_kv_tso.png)

In this example, TiDB clusters are deployed in different data centers in the same region. The average `commit` latency on TiDB is 12.7 ms, and the average `kv_commit` processing latency inside TiKV is 10.2 ms, a difference of about 2.5 ms. The average TSO wait latency is 3.12 ms, and the RPC time is 693 us.

**Example 3: Resource overloaded on public cloud clusters**

![Cloud Env, TiDB Overloaded](/media/performance/cloud_kv_tso_overloaded.png)

In this example, the TiDB clusters are deployed in different data centers in the same region, and TiDB network and CPU resources are severely overloaded. The average `BatchGet` latency on TiDB is 38.6 ms, and the average `kv_batch_get` processing latency inside TiKV is 6.15 ms. The difference is more than 32 ms, which is much higher than the normal value. The average TSO wait latency is 9.45 ms and the RPC time is 14.3 ms.
#### Storage Async Write Duration, Store Duration, and Apply Duration

TiKV processes a write request in the following procedure:

- `scheduler worker` processes the write request, performs a transaction consistency check, and converts the write request into a key-value pair to be sent to the `raftstore` module.
- The TiKV consensus module `raftstore` applies the Raft consensus algorithm to make the storage layer (composed of multiple TiKVs) fault-tolerant.

    Raftstore consists of a `Store` thread and an `Apply` thread:

    - The `Store` thread processes Raft messages and new `proposals`. When a new `proposals` is received, the `Store` thread of the leader node writes to the local Raft DB and copies the message to multiple follower nodes. When this `proposals` is successfully persisted in most instances, the `proposals` is successfully committed.
    - The `Apply` thread writes the committed `proposals` to the KV DB. When the data is successfully written to the KV DB, the `Apply` thread notifies externally that the write request has completed.

![TiKV Write](/media/performance/store_apply.png)

The `Storage Async Write Duration` metric records the latency after a write request enters raftstore. The data is collected on a basis of per request.

The `Storage Async Write Duration` metric contains two parts, `Store Duration` and `Apply Duration`. You can use the following formula to determine whether the bottleneck for write requests is in the `Store` or `Apply` step.

```
avg Storage Async Write Duration = avg Store Duration + avg Apply Duration
```

> **Note:**
>
> `Store Duration` and `Apply Duration` are supported since v5.3.0.

**Example 1: Comparison of the same OLTP workload in v5.3.0 and v5.4.0**

According to the preceding formula, the QPS of a write-heavy OLTP workload in v5.4.0 is 14% higher than that in v5.3.0:

- v5.3.0: 24.4 ms ~= 17.7 ms + 6.59 ms
- v5.4.0: 21.4 ms ~= 14.0 ms + 7.33 ms

In v5.4.0, the gPRC module has been optimized to accelerate Raft log replication, which reduces `Store Duration` compared with v5.3.0.

v5.3.0:

![v5.3.0](/media/performance/v5.3.0_store_apply.png)

v5.4.0:

![v5.4.0](/media/performance/v5.4.0_store_apply.png)

**Example 2: Store Duration is a bottleneck**

Apply the preceding formula: 10.1 ms ~= 9.81 ms + 0.304 ms. The result indicates that the latency bottleneck for write requests is in `Store Duration`.

![Store](/media/performance/cloud_store_apply.png)
