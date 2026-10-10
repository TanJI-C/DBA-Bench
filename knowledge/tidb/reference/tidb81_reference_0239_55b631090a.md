# TiKV dynamic configuration items table

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dynamic-config.md`
- Source Title: `Modify Configuration Dynamically`
- Source Heading Path: `Modify Configuration Dynamically > Common Operations > Modify TiKV configuration dynamically`
- Source Line Ranges: `126-242`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `ticdc`
- Topic Tags: `dynamic-configuration`, `configuration-items`, `raftstore`, `readpool`, `coprocessor`, `pessimistic-transactions`, `quota`, `gc`, `rocksdb`, `titan`, `grpc`, `snapshots`, `region-split`, `cdc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0239_55b631090a`
- Source ID: `tidb-docs-8.1:dynamic-config.md#modify-tikv-configuration-dynamically`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `45efc57fde935884cd87fbe5e152a913b2544a25743ebd015e937dad5d269438`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tikv-configuration-dynamically
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dynamic-config.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiKV configuration items that can be modified dynamically and their exact meanings across raftstore, readpool, coprocessor, pessimistic-txn, quota, gc, RocksDB, Titan, server, split, backup, import, and cdc settings.
- Retrieval Keywords: TiKV dynamic configuration items, Modify TiKV configuration dynamically, raftstore.raft-max-inflight-msgs, raftstore.store-io-pool-size, readpool.unified.max-tasks-per-worker, Server Is Busy, coprocessor.region-max-size, pessimistic-txn.wait-for-lock-timeout, quota.enable-auto-tune, gc.max-write-bytes-per-sec, server.grpc-memory-pool-quota, server.concurrent-send-snap-limit, storage.block-cache.capacity, import.num-threads, backup.num-threads, split.qps-threshold, cdc.min-ts-interval
- Follow-up Guidance: The content also highlights specific notes such as `raftstore.consistency-check-interval` being not recommended, `raftstore.store-io-pool-size` not being changed between zero and non-zero, and version-support notes embedded on some items.
- Classification Note: This chunk is reference content because it is a table of TiKV dynamic configuration item names with brief descriptions rather than a procedure.

## Official Source Content

| Configuration item | Description |
| :--- | :--- |
| log.level | The log level. |
| `raftstore.raft-max-inflight-msgs` | The number of Raft logs to be confirmed. If this number is exceeded, the Raft state machine slows down log sending. |
| `raftstore.raft-log-gc-tick-interval` | The time interval at which the polling task of deleting Raft logs is scheduled |
| `raftstore.raft-log-gc-threshold` | The soft limit on the maximum allowable number of residual Raft logs |
| `raftstore.raft-log-gc-count-limit` | The hard limit on the allowable number of residual Raft logs |
| `raftstore.raft-log-gc-size-limit` | The hard limit on the allowable size of residual Raft logs |
| `raftstore.raft-max-size-per-msg` | The soft limit on the size of a single message packet that is allowed to be generated |
| `raftstore.raft-entry-max-size` | The hard limit on the maximum size of a single Raft log |
| `raftstore.raft-entry-cache-life-time` | The maximum remaining time allowed for the log cache in memory |
| `raftstore.max-apply-unpersisted-log-limit` | The maximum number of committed but not persisted Raft logs that can be applied |
| `raftstore.split-region-check-tick-interval` | The time interval at which to check whether the Region split is needed |
| `raftstore.region-split-check-diff` | The maximum value by which the Region data is allowed to exceed before Region split |
| `raftstore.pd-heartbeat-tick-interval` | The time interval at which a Region's heartbeat to PD is triggered |
| `raftstore.pd-store-heartbeat-tick-interval` | The time interval at which a store's heartbeat to PD is triggered |
| `raftstore.snap-mgr-gc-tick-interval` | The time interval at which the recycle of expired snapshot files is triggered |
| `raftstore.snap-gc-timeout` | The longest time for which a snapshot file is saved |
| `raftstore.lock-cf-compact-interval` | The time interval at which TiKV triggers a manual compaction for the Lock Column Family |
| `raftstore.lock-cf-compact-bytes-threshold` | The size at which TiKV triggers a manual compaction for the Lock Column Family |
| `raftstore.messages-per-tick` | The maximum number of messages processed per batch |
| `raftstore.max-peer-down-duration` | The longest inactive duration allowed for a peer |
| `raftstore.max-leader-missing-duration` | The longest duration allowed for a peer to be without a leader. If this value is exceeded, the peer verifies with PD whether it has been deleted. |
| `raftstore.abnormal-leader-missing-duration` | The normal duration allowed for a peer to be without a leader. If this value is exceeded, the peer is seen as abnormal and marked in metrics and logs. |
| `raftstore.peer-stale-state-check-interval` | The time interval to check whether a peer is without a leader |
| `raftstore.consistency-check-interval` | The time interval to check consistency (**NOT** recommended because it is not compatible with the garbage collection in TiDB) |
| `raftstore.raft-store-max-leader-lease` | The longest trusted period of a Raft leader |
| `raftstore.merge-check-tick-interval` | The time interval for merge check |
| `raftstore.cleanup-import-sst-interval` | The time interval to check expired SST files |
| `raftstore.local-read-batch-size` | The maximum number of read requests processed in one batch |
| `raftstore.apply-yield-write-size` | The maximum number of bytes that the Apply thread can write for one FSM (Finite-state Machine) in each round |
| `raftstore.hibernate-timeout` | The shortest wait duration before entering hibernation upon start. Within this duration, TiKV does not hibernate (not released). |
| `raftstore.apply-pool-size` | The number of threads in the pool that flushes data to the disk, which is the size of the Apply thread pool |
| `raftstore.store-pool-size` | The number of threads in the pool that processes Raft, which is the size of the Raftstore thread pool |
| `raftstore.apply-max-batch-size` | Raft state machines process data write requests in batches by the BatchSystem. This configuration item specifies the maximum number of Raft state machines that can execute the requests in one batch. |
| `raftstore.store-max-batch-size` | Raft state machines process requests for flushing logs into the disk in batches by the BatchSystem. This configuration item specifies the maximum number of Raft state machines that can process the requests in one batch. |
| `raftstore.store-io-pool-size` | The number of threads that process Raft I/O tasks, which is also the size of the StoreWriter thread pool (**DO NOT** modify this value from a non-zero value to 0 or from 0 to a non-zero value) |
| `raftstore.periodic-full-compact-start-max-cpu` | The CPU usage threshold at which TiKV performs periodic full compaction if full compaction is enabled |
| `readpool.unified.max-thread-count` | The maximum number of threads in the thread pool that uniformly processes read requests, which is the size of the UnifyReadPool thread pool |
| `readpool.unified.max-tasks-per-worker` | The maximum number of tasks allowed for a single thread in the unified read pool. `Server Is Busy` error is returned when the value is exceeded. |
| `readpool.unified.auto-adjust-pool-size` | Determines whether to automatically adjust the UnifyReadPool thread pool size |
| `coprocessor.split-region-on-table` | Enables to split Region by table |
| `coprocessor.batch-split-limit` | The threshold of Region split in batches |
| `coprocessor.region-max-size` | The maximum size of a Region |
| `coprocessor.region-split-size` | The size of the newly split Region |
| `coprocessor.region-max-keys` | The maximum number of keys allowed in a Region |
| `coprocessor.region-split-keys` | The number of keys in the newly split Region |
| `pessimistic-txn.wait-for-lock-timeout` | The longest duration that a pessimistic transaction waits for the lock |
| `pessimistic-txn.wake-up-delay-duration` | The duration after which a pessimistic transaction is woken up |
| `pessimistic-txn.pipelined` | Determines whether to enable the pipelined pessimistic locking process |
| `pessimistic-txn.in-memory` | Determines whether to enable the in-memory pessimistic lock |
| `quota.foreground-cpu-time` | The soft limit on the CPU resources used by TiKV foreground to process read and write requests |
| `quota.foreground-write-bandwidth` | The soft limit on the bandwidth with which foreground transactions write data |
| `quota.foreground-read-bandwidth` | The soft limit on the bandwidth with which foreground transactions and the Coprocessor read data |
| `quota.background-cpu-time` | The soft limit on the CPU resources used by TiKV background to process read and write requests |
| `quota.background-write-bandwidth` | The soft limit on the bandwidth with which background transactions write data |
| `quota.background-read-bandwidth` | The soft limit on the bandwidth with which background transactions and the Coprocessor read data |
| `quota.enable-auto-tune` | Whether to enable the auto-tuning of quota. If this configuration item is enabled, TiKV dynamically adjusts the quota for the background requests based on the load of TiKV instances.  |
| `quota.max-delay-duration` | The maximum time that a single read or write request is forced to wait before it is processed in the foreground |
| `gc.ratio-threshold` | The threshold at which Region GC is skipped (the number of GC versions/the number of keys) |
| `gc.batch-keys` | The number of keys processed in one batch |
| `gc.max-write-bytes-per-sec` | The maximum bytes that can be written into RocksDB per second |
| `gc.enable-compaction-filter` | Whether to enable compaction filter |
| `gc.compaction-filter-skip-version-check` | Whether to skip the cluster version check of compaction filter (not released) |
| `gc.auto-compaction.check-interval` | The interval at which TiKV checks whether to trigger automatic (RocksDB) compaction |
| `gc.auto-compaction.tombstone-num-threshold` | The number of RocksDB tombstones required to trigger TiKV automatic (RocksDB) compaction |
| `gc.auto-compaction.tombstone-percent-threshold` | The percentage of RocksDB tombstones required to trigger TiKV automatic (RocksDB) compaction |
| `gc.auto-compaction.redundant-rows-threshold` | The number of redundant MVCC rows required to trigger TiKV automatic (RocksDB) compaction |
| `gc.auto-compaction.redundant-rows-percent-threshold` | The percentage of redundant MVCC rows required to trigger TiKV automatic (RocksDB) compaction |
| `gc.auto-compaction.bottommost-level-force` | Whether to force compaction on the bottommost level files in RocksDB |
| `{db-name}.max-total-wal-size` | The maximum size of total WAL |
| `{db-name}.max-background-jobs` | The number of background threads in RocksDB |
| `{db-name}.max-background-flushes` | The maximum number of flush threads in RocksDB |
| `{db-name}.max-open-files` | The total number of files that RocksDB can open |
| `{db-name}.compaction-readahead-size` | The size of `readahead` during compaction |
| `{db-name}.bytes-per-sync` | The rate at which OS incrementally synchronizes files to disk while these files are being written asynchronously |
| `{db-name}.wal-bytes-per-sync` | The rate at which OS incrementally synchronizes WAL files to disk while the WAL files are being written |
| `{db-name}.writable-file-max-buffer-size` | The maximum buffer size used in WritableFileWrite |
| `{db-name}.{cf-name}.block-cache-size` | The cache size of a block |
| `{db-name}.{cf-name}.write-buffer-size` | The size of a memtable |
| `{db-name}.{cf-name}.max-write-buffer-number` | The maximum number of memtables |
| `{db-name}.{cf-name}.max-bytes-for-level-base` | The maximum number of bytes at base level (L1) |
| `{db-name}.{cf-name}.target-file-size-base` | The size of the target file at base level |
| `{db-name}.{cf-name}.level0-file-num-compaction-trigger` | The maximum number of files at L0 that trigger compaction |
| `{db-name}.{cf-name}.level0-slowdown-writes-trigger` | The maximum number of files at L0 that trigger write stall |
| `{db-name}.{cf-name}.level0-stop-writes-trigger` | The maximum number of files at L0 that completely block write |
| `{db-name}.{cf-name}.max-compaction-bytes` | The maximum number of bytes written into disk per compaction |
| `{db-name}.{cf-name}.max-bytes-for-level-multiplier` | The default amplification multiple for each layer |
| `{db-name}.{cf-name}.disable-auto-compactions` | Enables or disables automatic compaction |
| `{db-name}.{cf-name}.soft-pending-compaction-bytes-limit` | The soft limit on the pending compaction bytes |
| `{db-name}.{cf-name}.hard-pending-compaction-bytes-limit` | The hard limit on the pending compaction bytes |
| `{db-name}.{cf-name}.titan.blob-run-mode` | The mode of processing blob files |
| `{db-name}.{cf-name}.titan.min-blob-size` | The threshold at which data is stored in Titan. Data is stored in a Titan blob file when its value reaches this threshold. |
| `{db-name}.{cf-name}.titan.blob-file-compression` | The compression algorithm used by Titan blob files |
| `{db-name}.{cf-name}.titan.discardable-ratio` | The threshold of garbage data ratio in Titan data files for GC. When the ratio of useless data in a blob file exceeds the threshold, Titan GC is triggered. |
| `server.grpc-memory-pool-quota` | Limits the memory size that can be used by gRPC |
| `server.max-grpc-send-msg-len` | Sets the maximum length of a gRPC message that can be sent |
| `server.snap-io-max-bytes-per-sec` | Sets the maximum allowable disk bandwidth when processing snapshots |
| `server.concurrent-send-snap-limit` | Sets the maximum number of snapshots sent at the same time |
| `server.concurrent-recv-snap-limit` | Sets the maximum number of snapshots received at the same time |
| `server.raft-msg-max-batch-size` | Sets the maximum number of Raft messages that are contained in a single gRPC message |
| `server.simplify-metrics`        | Controls whether to simplify the sampling monitoring metrics                   |
| `storage.block-cache.capacity` | The size of shared block cache (supported since v4.0.3) |
| `storage.scheduler-worker-pool-size` | The number of threads in the Scheduler thread pool |
| `import.num-threads` | The number of threads to process restore or import RPC requests (dynamic modification is supported starting from v8.1.2) |
| `backup.num-threads` | The number of backup threads (supported since v4.0.3) |
| `split.qps-threshold` | The threshold to execute `load-base-split` on a Region. If the QPS of read requests for a Region exceeds `qps-threshold` for 10 consecutive seconds, this Region should be split.|
| `split.byte-threshold` | The threshold to execute `load-base-split` on a Region. If the traffic of read requests for a Region exceeds the `byte-threshold` for 10 consecutive seconds, this Region should be split. |
| `split.region-cpu-overload-threshold-ratio` | The threshold to execute `load-base-split` on a Region. If the CPU usage in the Unified Read Pool for a Region exceeds the `region-cpu-overload-threshold-ratio` for 10 consecutive seconds, this Region should be split. (supported since v6.2.0) |
| `split.split-balance-score` | The parameter of `load-base-split`, which ensures the load of the two split Regions is as balanced as possible. The smaller the value is, the more balanced the load is. But setting it too small might cause split failure. |
| `split.split-contained-score` | The parameter of `load-base-split`. The smaller the value, the fewer cross-Region visits after Region split. |
| `cdc.min-ts-interval` | The time interval at which Resolved TS is forwarded  |
| `cdc.old-value-cache-memory-quota` | The upper limit of memory occupied by the TiCDC Old Value entries |
| `cdc.sink-memory-quota` | The upper limit of memory occupied by TiCDC data change events |
| `cdc.incremental-scan-speed-limit` | The upper limit on the speed of incremental scanning for historical data |
| `cdc.incremental-scan-concurrency` | The maximum number of concurrent incremental scanning tasks for historical data |
