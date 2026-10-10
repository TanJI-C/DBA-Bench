# TiKV busy errors, leader drops, and slow write troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-troubleshooting-map.md`
- Source Title: `TiDB Troubleshooting Map`
- Source Heading Path: `TiDB Troubleshooting Map > 4. TiKV issues > 4.3 The client reports the `server is busy` error | TiDB Troubleshooting Map > 4. TiKV issues > 4.4 Some TiKV nodes drop Leader frequently | TiDB Troubleshooting Map > 4. TiKV issues > 4.5 TiKV write is slow | TiDB Troubleshooting Map > 5. PD issues`
- Source Line Ranges: `239-335`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `shared`
- Topic Tags: `server-is-busy`, `flow-control`, `write-stall`, `rocksdb`, `scheduler`, `raftstore`, `coprocessor`, `leader-drop`, `re-election`, `network-isolation`, `write-latency`, `grpc`, `append-log`, `apply-log`, `hotspot`, `grafana`, `oom`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0110_e1c726891b`
- Source ID: `tidb-docs-8.1:tidb-troubleshooting-map.md#4-3-the-client-reports-the-server-is-busy-error`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5fce2c5a51c947cddfedb371cafa8e992aaa32bdfe13519d673f0a7b3cc37b52`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-troubleshooting-map#4-3-the-client-reports-the-server-is-busy-error
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-troubleshooting-map.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing TiKV `server is busy` errors, frequent Leader drops, or slow write phases by matching Grafana metrics, RocksDB stalls, scheduler and raftstore backpressure, or network and restart causes.
- Retrieval Keywords: server is busy, Grafana -> TiKV -> errors, write stall, grep "Stalling" RocksDB, LOG, data/raft, data/db, Flow control configuration, soft-pending-compaction-bytes-limit, hard-pending-compaction-bytes-limit, storage.flow-control, max-write-buffer-number, scheduler too busy, latch wait duration, Grafana -> TiKV-details -> scheduler prewrite, scheduler commit, scheduler-pending-write-threshold, MVCC_CONFLICT_COUNTER, raftstore is busy, channel full, append log duration, TiKV Raft messages dashboard, coprocessor threads, readpool.coprocessor.max-tasks-per-worker-normal, readpool.coprocessor.max-tasks-per-worker-low, readpool.coprocessor.max-tasks-per-worker-high, table scan operations, wrong execution plan, drop Leader frequently, re-election, systemd, dmesg, OOM, THP, Transparent Hugepage, network isolation, prewrite/commit/raw-put, TiKV gRPC, RawKV clusters, scheduler command duration, storage async write duration, scheduler-worker-pool-size, Raft IO, WAL Sync Duration max, RocksDB - raft, Raft Propose, propose wait duration, store-pool-size, apply log duration, apply wait duration, apply-pool-size, apply CPU, Region write hot spot, RocksDB kv, max write duration, commit log duration, raft-max-inflight-msgs = 256, performance-map
- Follow-up Guidance: The content points to related sections such as 4.3.1 for RocksDB `write stall`, 4.5 for slow write analysis, 3.3 for wrong execution plan, 4.2 for TiKV OOM, and the performance-map for write path analysis.
- Classification Note: This chunk is classified as diagnosis for the self-managed TiKV and PD troubleshooting map because it describes symptom-based causes, relevant Grafana metrics, logs, configuration identifiers, and linked sections for investigating busy errors, leader re-elections, and slow writes.

## Official Source Content

### 4.3 The client reports the `server is busy` error

Check the specific cause for busy by viewing the monitor **Grafana** -> **TiKV** -> **errors**. `server is busy` is caused by the flow control mechanism of TiKV, which informs `tidb/ti-client` that TiKV is currently under too much pressure and will retry later.

- 4.3.1 TiKV RocksDB encounters `write stall`.

    A TiKV instance has two RocksDB instances, one in `data/raft` to store the Raft log, and the other in `data/db` to store the real data. You can check the specific cause for the stall by running `grep "Stalling" RocksDB` in the log. The RocksDB log is a file starting with `LOG`, and `LOG` is the current log. `write stall` is a performance degradation mechanism natively built in RocksDB. When `write stall` occurs in RocksDB, the system performance drops significantly. In versions before v5.2.0, TiDB tries to block all write requests by returning a `ServerIsBusy` error directly to the client when encountering `write stall`, but this could lead to a sharp decrease in QPS performance. Starting from v5.2.0, TiKV introduces a new flow control mechanism that suppresses writes by delaying write requests dynamically in the scheduling layer, which replaces the previous mechanism of returning `server is busy` to clients when `write stall` occurs. The new flow control mechanism is enabled by default, and TiKV automatically disables the `write stall` mechanism for `KvDB` and `RaftDB` (except for memtables). However, when the number of pending requests exceeds a certain threshold, the flow control mechanism still takes effect, beginning to reject some or all write requests and returning a `server is busy` error to clients. For detailed explanations and thresholds, see [Flow control configuration](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#storageflow-control).

    - If the `server is busy` error is triggered by too many pending compaction bytes, you can alleviate this issue by increasing the values of the  [`soft-pending-compaction-bytes-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#soft-pending-compaction-bytes-limit) and [`hard-pending-compaction-bytes-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#hard-pending-compaction-bytes-limit) parameters.

        - When pending compaction bytes reach the value of the `soft-pending-compaction-bytes-limit` parameter (`192GiB` by default), the flow control mechanism begins to reject some write requests (by returning `ServerIsBusy` to clients). In this case, you can increase the value of this parameter, for example, `[storage.flow-control] soft-pending-compaction-bytes-limit = "384GiB"`.

        - When pending compaction bytes reach the value of the `hard-pending-compaction-bytes-limit` parameter (`1024GiB` by default), the flow control mechanism begins to reject all write requests (by returning `ServerIsBusy` to clients). This scenario is less likely to occur because the flow control mechanism intervenes to slow down write speed after reaching the threshold of `soft-pending-compaction-bytes-limit`. If it occurs, you can increase the value of this parameter, for example, `[storage.flow-control] hard-pending-compaction-bytes-limit = "2048GiB"`.

        - If the disk I/O capacity fails to keep up with the write for a long time, it is recommended to scale up your disk. If the disk throughput reaches the upper limit and causes write stall (for example, the SATA SSD is much lower than NVME SSD), while the CPU resources is sufficient, you may apply a compression algorithm of higher compression ratio. This way, the CPU resources is traded for disk resources, and the pressure on the disk is eased.

        - If the default CF compaction sees a high pressure, change the `[rocksdb.defaultcf] compression-per-level` parameter from `["no", "no", "lz4", "lz4", "lz4", "zstd", "zstd"]` to `["no", "no", "zstd", "zstd", "zstd", "zstd", "zstd"]`.

    - Too many memtables causes stall. This usually occurs when the amount of instant writes is large and the memtables flush to the disk slowly. If the disk write speed cannot be improved, and this issue only occurs during business peaks, you can mitigate it by increasing the `max-write-buffer-number` of the corresponding CF.

        - For example, set `[rocksdb.defaultcf] max-write-buffer-number` to `8` (`5` by default). Note that this might cause more memory usage in the peak, because more memtables might be in the memory.

- 4.3.2 `scheduler too busy`

    - Serious write conflict. `latch wait duration` is high. You can view `latch wait duration` in the monitor **Grafana** -> **TiKV-details** -> **scheduler prewrite**/**scheduler commit**. When the write tasks pile up in the scheduler, the pending write tasks exceed the threshold set in `[storage] scheduler-pending-write-threshold` (100MB). You can verify the cause by viewing the metric corresponding to `MVCC_CONFLICT_COUNTER`.

    - Slow write causes write tasks to pile up. The data being written to TiKV exceeds the threshold set by `[storage] scheduler-pending-write-threshold` (100MB). Refer to [4.5](#45-tikv-write-is-slow).

- 4.3.3 `raftstore is busy`. The processing of messages is slower than the receiving of messages. The short-term `channel full` status does not affect the service, but if the error persists for a long time, it might cause Leader switch.

    - `append log` encounters stall. Refer to [4.3.1](#43-the-client-reports-the-server-is-busy-error).
    - `append log duration` is high, which causes slow processing of messages. You can refer to [4.5](#45-tikv-write-is-slow) to analyze why `append log duration` is high.
    - raftstore receives a large batch of messages in an instant (check in the TiKV Raft messages dashboard), and fails to process them. Usually the short-term `channel full` status does not affect the service.

- 4.3.4 TiKV coprocessor is in a queue. The number of piled up tasks exceeds `coprocessor threads * readpool.coprocessor.max-tasks-per-worker-[normal|low|high]`. Too many large queries leads to the tasks piling up in coprocessor. You need to check whether an execution plan change causes a large number of table scan operations. Refer to [3.3](#33-wrong-execution-plan).
### 4.4 Some TiKV nodes drop Leader frequently

- 4.4.1 Re-election because TiKV is restarted

    - After TiKV panics, it is pulled up by systemd and runs normally. You can check whether panic has occurred by viewing the TiKV log. Because this issue is unexpected, [report a bug](https://github.com/tikv/tikv/issues/new?template=bug-report.md) if it happens.

    - TiKV is stopped or killed by a third party and then pulled up by systemd. Check the cause by viewing `dmesg` and the TiKV log.

    - TiKV is OOM, which causes restart. Refer to [4.2](#42-tikv-oom).

    - TiKV is hung because of dynamically adjusting `THP` (Transparent Hugepage). See case [case-500](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case500.md) in Chinese.

- 4.4.2 TiKV RocksDB encounters write stall and thus results in re-election. You can check if the monitor **Grafana** -> **TiKV-details** -> **errors** shows `server is busy`. Refer to [4.3.1](#43-the-client-reports-the-server-is-busy-error).

- 4.4.3 Re-election because of network isolation.
### 4.5 TiKV write is slow

- 4.5.1 Check whether the TiKV write is slow by viewing the `prewrite/commit/raw-put` duration of TiKV gRPC (only for RawKV clusters). Generally, you can locate the slow phase according to the [performance-map](https://github.com/pingcap/tidb-map/blob/master/maps/performance-map.png). Some common situations are listed as follows.

- 4.5.2 The scheduler CPU is busy (only for transaction kv).

    The `scheduler command duration` of prewrite/commit is longer than the sum of `scheduler latch wait duration` and `storage async write duration`. The scheduler worker has a high CPU demand, such as over 80% of `scheduler-worker-pool-size` * 100%, or the CPU resources of the entire machine are relatively limited. If the write workload is large, check if `[storage] scheduler-worker-pool-size` is set too small.

    For other situations, [report a bug](https://github.com/tikv/tikv/issues/new?template=bug-report.md).

- 4.5.3 Append log is slow.

    The **Raft IO**/`append log duration` in TiKV Grafana is high, usually because the disk write operation is slow. You can verify the cause by checking the `WAL Sync Duration max` value of RocksDB - raft.

    For other situations, [report a bug](https://github.com/tikv/tikv/issues/new?template=bug-report.md).

- 4.5.4 The raftstore thread is busy.

    The **Raft Propose**/`propose wait duration` is significantly larger than the append log duration in TiKV Grafana. Take the following methods:

    - Check whether the `[raftstore] store-pool-size` configuration value is too small. It is recommended to set the value between `1` and `5` and not too large.
    - Check whether the CPU resources on the machine are insufficient.

- 4.5.5 Apply is slow.

    The **Raft IO**/`apply log duration` in TiKV Grafana is high, which usually comes with a high **Raft Propose**/`apply wait duration`. The possible causes are as follows:

    - `[raftstore] apply-pool-size` is too small (it is recommended to set the value between `1` and `5` and not too large), and the **Thread CPU**/`apply CPU` is large.

    - The CPU resources on the machine are insufficient.

    - Region write hot spot. A single apply thread has high CPU usage. Currently, we cannot properly address the hot spot problem on a single Region, which is being improved. To view the CPU usage of each thread, modify the Grafana expression and add `by (instance, name)`.

    - RocksDB write is slow. **RocksDB kv**/`max write duration` is high. A single Raft log might contain multiple KVs. When writing into RocksDB, 128 KVs are written into RocksDB in a write batch. Therefore, an apply log might be associated with multiple writes in RocksDB.

    - For other situations, [report a bug](https://github.com/tikv/tikv/issues/new?template=bug-report.md).

- 4.5.6 Raft commit log is slow.

    The **Raft IO**/`commit log duration` in TiKV Grafana is high (this metric is only supported in Grafana after v4.x). Every Region corresponds to an independent Raft group. Raft has a flow control mechanism, similar to the sliding window mechanism of TCP. You can control the size of the sliding window by configuring the `[raftstore] raft-max-inflight-msgs = 256` parameter. If there is a write hot spot and the `commit log duration` is high, you can adjust the parameter, such as increasing it to `1024`.

- 4.5.7 For other situations, refer to the write path on [performance-map](https://github.com/pingcap/tidb-map/blob/master/maps/performance-map.png) and analyze the cause.
## 5. PD issues
