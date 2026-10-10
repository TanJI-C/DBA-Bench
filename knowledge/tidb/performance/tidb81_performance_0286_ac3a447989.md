# TiKV thread pool performance tuning guidance

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tune-tikv-thread-performance.md`
- Source Title: `Tune TiKV Thread Pool Performance`
- Source Heading Path: `Tune TiKV Thread Pool Performance > Performance tuning for TiKV thread pools`
- Source Line Ranges: `41-106`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `thread-pools`, `performance-tuning`, `cpu-usage`, `grpc`, `scheduler`, `raftstore`, `storewriter`, `unifyreadpool`, `rocksdb`, `grafana`, `write-stall`, `version-dependent`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0286_ac3a447989`
- Source ID: `tidb-docs-8.1:tune-tikv-thread-performance.md#performance-tuning-for-tikv-thread-pools`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `743896ee2b1b3701e17659c64bc06620e63c7fb49547a3b5db11df38b63a123c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance#performance-tuning-for-tikv-thread-pools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tune-tikv-thread-performance.md

## Retrieval Guidance

- Use When: Use this chunk when the need is to find TiKV thread pool performance tuning guidance, CPU usage targets, Grafana metrics, and related configuration items for gRPC, Scheduler, Raftstore, StoreWriter, UnifyReadPool, and RocksDB.
- Retrieval Keywords: server.grpc-concurrency, gRPC poll CPU, storage.scheduler-worker-pool-size, TiKV-Details.Thread CPU.scheduler worker CPU, raftstore.store-pool-size, raftstore.store-io-pool-size, Raft store CPU, readpool.unified.max-thread-count, TiKV-Details.Thread CPU.Unified read pool CPU, readpool.unified.auto-adjust-pool-size, rocksdb.max-background-jobs, raftdb.max-background-jobs, Write Stall Reason, RocksDB-kv, rocksdb.max-sub-compactions, max-write-buffer-number, rocksdb.defaultcf.level0-slowdown-writes-trigger, rocksdb.writecf.level0-slowdown-writes-trigger, rocksdb.lockcf.level0-slowdown-writes-trigger, rocksdb.defaultcf.level0-stop-writes-trigger, rocksdb.writecf.level0-stop-writes-trigger, rocksdb.lockcf.level0-stop-writes-trigger, write stall, StoreWriter thread pool, UnifyReadPool
- Follow-up Guidance: The content includes specific follow-up conditions such as checking `Write Stall Reason` in `RocksDB-kv` on Grafana and using the non-zero metrics to choose among pending compaction bytes, memtable count, or level0 file limit related parameters.
- Classification Note: This chunk is classified as performance because it provides tuning guidance, utilization targets, and configuration parameters for TiKV thread pools and RocksDB background work.

## Official Source Content

## Performance tuning for TiKV thread pools

* The gRPC thread pool.

    The default size (configured by `server.grpc-concurrency`) of the gRPC thread pool is `5`. This thread pool has almost no computing overhead and is mainly responsible for network I/O and deserialization requests, so generally you do not need to adjust the default configuration.

    - If the machine deployed with TiKV has a small number (less than or equal to 8) of CPU cores, consider setting the `server.grpc-concurrency` configuration item to `2`.
    - If the machine deployed with TiKV has very high configuration, TiKV undertakes a large number of read and write requests, and the value of `gRPC poll CPU` that monitors Thread CPU on Grafana exceeds 80% of `server.grpc-concurrency`, then consider increasing the value of `server.grpc-concurrency` to keep the thread pool usage rate below 80% (that is, the metric on Grafana is lower than `80% * server.grpc-concurrency`).

* The Scheduler thread pool.

    When TiKV detects that the number of machine CPU cores is larger than or equal to 16, the default size (configured by `storage.scheduler-worker-pool-size`) of the Scheduler thread pool is `8`; when TiKV detects that the number of machine CPU cores is smaller than 16, the default size is `4`.

    This thread pool is mainly used to convert complex transaction requests into simple key-value read and write requests. However, **the Scheduler thread pool itself does not perform any write operation**.

    - If it detects a transaction conflict, then this thread pool returns the conflict result to the client in advance.
    - If no conflict is detected, then this thread pool merges the key-value requests that perform write operations into a Raft log and sends it to the Raftstore thread for Raft log replication.

    Generally speaking, to avoid excessive thread switching, it is best to ensure that the utilization rate of the Scheduler thread pool is between 50% and 75%. If the thread pool size is `8`, then it is recommended to keep `TiKV-Details.Thread CPU.scheduler worker CPU` on Grafana between 400% and 600%.

* The Raftstore thread pool.

    The Raftstore thread pool is the most complex thread pool in TiKV. The default size (configured by `raftstore.store-pool-size`) of this thread pool is `2`. For the StoreWriter thread pool, the default size (configured by `raftstore.store-io-pool-size`) is `1`.

    - When the size of the StoreWriter thread pool is 0, all write requests are written into RocksDB in the way of `fsync` by the Raftstore thread. In this case, it is recommended to tune the performance as follows:

        - Keep the overall CPU usage of the Raftstore thread below 60%. When the number of Raftstore threads is 2, keep the **TiKV-Details**, **Thread CPU**, **Raft store CPU** on Grafana below 120%. Due to I/O requests, the CPU usage of Raftstore threads in theory is always lower than 100%.
        - Do not increase the size of the Raftstore thread pool to improve write performance without careful consideration, because this might increase the disk burden and degrade performance.

    - When the size of the StoreWriter thread pool is not 0, all write requests are written into RocksDB in the way of `fsync` by the StoreWriter thread. In this case, it is recommended to tune the performance as follows:

        - Enable the StoreWriter thread pool ONLY when the overall CPU resources are sufficient. When the StoreWriter thread pool is enabled, keep the CPU usage of the StoreWriter thread and the Raftstore thread below 80%.

         Compared with the case that the write requests are processed by the Raftstore thread, in theory, when the write requests are processed by the StoreWriter thread, write latency and the tail latency of data read are significantly reduced. However, as the write speed grows faster, the number of Raft logs increases accordingly. This can cause the CPU overhead of the Raftstore threads, the Apply threads, and the gRPC threads to increase. In this case, insufficient CPU resources might offset the tuning effect, and as a result, the write speed might become slower than before. Therefore, if the CPU resources are not sufficient, it is not recommended to enable the StoreWriter thread. Because the Raftstore thread sends most of the I/O requests to the StoreWriter thread, you need to keep the CPU usage of the Raftstore thread below 80%.

    - In most cases, set the size of the StoreWriter thread pool to 1 or 2. This is because the size of the StoreWriter thread pool affects the number of Raft logs, so the value of the thread pool size should not be too large. If the CPU usage is higher than 80%, consider increasing the thread pool size.

    - Pay attention to the impact of increasing Raft logs on the CPU overhead of other thread pools. If necessary, you need to increase the number of Raftstore threads, Apply threads, and gRPC threads accordingly.

* The UnifyReadPool thread pool.

    The UnifyReadPool is responsible for handling all read requests. The default size (configured by `readpool.unified.max-thread-count`) is 80% of the number of the machine's CPU cores. For example, if the machine CPU has 16 cores, the default thread pool size is 12. It is recommended to adjust the CPU usage rate according to the application workloads and keep it between 60% and 90% of the thread pool size.

    If the peak value of the `TiKV-Details.Thread CPU.Unified read pool CPU` on Grafana does not exceed 800%, then it is recommended to set `readpool.unified.max-thread-count` to `10`. Too many threads can cause more frequent thread switching, and take up resources of other thread pools.

    Since v6.3.0, TiKV supports automatically adjusting the UnifyReadPool thread pool size based on the current CPU usage. To enable this feature, you can set the [`readpool.unified.auto-adjust-pool-size = true`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#auto-adjust-pool-size-new-in-v630). It is recommended to automatically adjust the thread pool size for clusters that are reread and whose maximum CPU usage exceeds 80%.

* The RocksDB thread pool.

    The RocksDB thread pool is a thread pool for RocksDB to compact and flush tasks. Usually, you do not need to configure it.

    * If the machine has a small number of CPU cores, set both `rocksdb.max-background-jobs` and `raftdb.max-background-jobs` to `4`.
    * If you encounter write stall, go to Write Stall Reason in **RocksDB-kv** on Grafana and check on the metrics that are not `0`.

        * If it is caused by reasons related to pending compaction bytes, set `rocksdb.max-sub-compactions` to `2` or `3`. This configuration item indicates the number of sub-threads allowed for a single compaction job. Its default value is `3` in TiKV 4.0 and `1` in TiKV 3.0.
        * If the reason is related to memtable count, it is recommended to increase the `max-write-buffer-number` of all columns (`5` by default).
        * If the reason is related to the level0 file limit, it is recommended to increase values of the following parameters to `64` or a larger number:

            ```
            rocksdb.defaultcf.level0-slowdown-writes-trigger
            rocksdb.writecf.level0-slowdown-writes-trigger
            rocksdb.lockcf.level0-slowdown-writes-trigger
            rocksdb.defaultcf.level0-stop-writes-trigger
            rocksdb.writecf.level0-stop-writes-trigger
            rocksdb.lockcf.level0-stop-writes-trigger
            ```
