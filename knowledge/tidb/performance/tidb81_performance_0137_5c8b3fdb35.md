# Raft log latency metrics and dashboard availability for earlier versions

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-tuning-methods.md`
- Source Title: `Performance Analysis and Tuning`
- Source Heading Path: `Performance Analysis and Tuning > Performance analysis and tuning using the Performance Overview dashboard > Query latency breakdown and key latency metrics > Commit Log Duration, Append Log Duration, and Apply Log Duration | Performance Analysis and Tuning > If my TiDB version is earlier than v6.1.0, what should I do to use the Performance Overview dashboard?`
- Source Line Ranges: `435-494`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `dashboard`, `tidb`
- Topic Tags: `performance-overview`, `raftstore`, `commit-log`, `append-log`, `apply-log`, `thread-pools`, `raft-engine`, `version-compatibility`, `grafana`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0137_5c8b3fdb35`
- Source ID: `tidb-docs-8.1:performance-tuning-methods.md#commit-log-duration-append-log-duration-and-apply-log-duration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fa6b21d08ce415e654f16603b3feab9490542e9254574d1862defe63d91cde3b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-tuning-methods#commit-log-duration-append-log-duration-and-apply-log-duration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-tuning-methods.md

## Retrieval Guidance

- Use When: Use this chunk when investigating raftstore latency metrics such as Commit Log Duration, Append Log Duration, and Apply Log Duration, or when checking how to use the Performance Overview dashboard on TiDB versions earlier than v6.1.0.
- Retrieval Keywords: Commit Log Duration, Append Log Duration, Apply Log Duration, raftstore, Store thread, Apply thread, raftstore.store-pool-size, raftstore.apply-pool-size, raft-engine.enable: true, Raft Engine, raftstore.store-io-pool-size: 1, StoreWriter, performance_overview.json, Grafana, Performance Overview dashboard, earlier than v6.1.0
- Follow-up Guidance: The source includes a bottleneck example where Commit Log Duration and Append Log Duration are high, and states that versions earlier than v6.1.0 need manual import of performance_overview.json to use the Performance Overview dashboard.
- Classification Note: This is classified as performance content because it focuses on raftstore log-operation latency metrics, their relationship to Store and Apply processing, and dashboard availability details for earlier TiDB versions.

## Official Source Content

#### Commit Log Duration, Append Log Duration, and Apply Log Duration

`Commit Log Duration`, `Append Log Duration`, and `Apply Log Duration` are latency metrics for key operations within raftstore. These latencies are captured at the batch operation level, with each operation combining multiple write requests. Therefore, the latencies do not directly correspond to the `Store Duration` and `Apply Duration` mentioned above.

- `Commit Log Duration` and `Append Log Duration` record time of operations performed in the `Store` thread. `Commit Log Duration` includes the time of copying Raft logs to other TiKV nodes (to ensure raft-log persistence). `Commit Log Duration` usually contains two `Append Log Duration` operations, one for the leader and the other for the follower. `Commit Log Duration` is usually significantly higher than `Append Log Duration`, because the former includes the time of copying Raft logs to other TiKV nodes through network.
- `Apply Log Duration` records the latency of `apply` Raft logs by the `Apply` thread.

Common scenarios where `Commit Log Duration` is long:

- There is a bottleneck in TiKV CPU resources and the scheduling latency is high
- `raftstore.store-pool-size` is either excessively small or large (an excessively large value might also cause performance degradation)
- The I/O latency is high, resulting in high `Append Log Duration` latency
- The network latency between TiKV nodes is high
- The number of the gRPC threads are too small, CPU usage is uneven among the GRPC threads.

Common scenarios where `Apply Log Duration` is long:

- There is a bottleneck in TiKV CPU resources and the scheduling latency is high
- `raftstore.apply-pool-size` is either excessively small or large (an excessively large value might also cause performance degradation)
- The I/O latency is high

**Example 1: Comparison of the same OLTP workload in v5.3.0 and v5.4.0**

The QPS of a write-heavy OLTP workload in v5.4.0 is improved by 14% compared with that in v5.3.0. The following table compares the three key latencies.

| Avg Duration | v5.3.0 (ms) | v5.4.0 (ms) |
|:----------|:----------|:----------|
| Append Log Duration | 0.27 | 0.303|
| Commit Log Duration | 13 | 8.68 |
| Apply Log Duration | 0.457|0.514 |

In v5.4.0, the gPRC module has been optimized to accelerate Raft log replication, which reduces `Commit Log Duration` and `Store Duration` compared with v5.3.0.

v5.3.0:

![v5.3.0](/media/performance/v5.3.0_commit_append_apply.png)

v5.4.0:

![v5.4.0](/media/performance/v5.4.0_commit_append_apply.png)

**Example 2: Commit Log Duration is a bottleneck**

![Store](/media/performance/cloud_append_commit_apply.png)

- Average `Append Log Duration` = 4.38 ms
- Average `Commit Log Duration` = 7.92 ms
- Average `Apply Log Duration` = 172 us

For the `Store` thread, `Commit Log Duration` is obviously higher than `Apply Log Duration`. Meanwhile, `Append Log Duration` is significantly higher than `Apply Log Duration`, indicating that the `Store` thread might suffer from bottlenecks in both CPU and I/O. Possible ways to reduce `Commit Log Duration` and `Append Log Duration` are as follows:

- If TiKV CPU resources are sufficient, consider adding `Store` threads by increasing the value of `raftstore.store-pool-size`.
- If TiDB is v5.4.0 or later, consider enabling [`Raft Engine`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#raft-engine) by setting `raft-engine.enable: true`. Raft Engine has a light execution path. This helps reduce I/O writes and long-tail latency of writes in some scenarios.
- If TiKV CPU resources are sufficient and TiDB is v5.3.0 or later, consider enabling [`StoreWriter`](https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance#performance-tuning-for-tikv-thread-pools) by setting `raftstore.store-io-pool-size: 1`.
## If my TiDB version is earlier than v6.1.0, what should I do to use the Performance Overview dashboard?

Starting from v6.1.0, Grafana has a built-in Performance Overview dashboard by default. This dashboard is compatible with TiDB v4.x and v5.x versions. If your TiDB is earlier than v6.1.0, you need to manually import [`performance_overview.json`](https://github.com/pingcap/tidb/blob/release-8.1/pkg/metrics/grafana/performance_overview.json), as shown in the following figure:

![Store](/media/performance/import_dashboard.png)
