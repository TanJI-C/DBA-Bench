# TiKV GC, snapshot, coprocessor, task, and thread metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-tikv-dashboard.md`
- Source Title: `Key Monitoring Metrics of TiKV`
- Source Heading Path: `Key Monitoring Metrics of TiKV > TiKV-Details dashboard > GC | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Snapshot | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Task | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Coprocessor Overview | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Coprocessor Detail | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Threads`
- Source Line Ranges: `261-320`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `dashboard`, `tidb`
- Topic Tags: `grafana`, `metrics`, `gc`, `snapshot`, `tasks`, `coprocessor`, `threads`, `latency`, `workers`, `dag`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0060_43aaaab32c`
- Source ID: `tidb-docs-8.1:grafana-tikv-dashboard.md#gc`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5cab768b8e4ac0e279f1609d73ddcdc40d0eb18a9cbb8149773db05d3647d5ff`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#gc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-tikv-dashboard.md

## Retrieval Guidance

- Use When: Use this chunk when locating TiKV-Details dashboard metrics for GC progress, snapshot handling, worker or future pool tasks, coprocessor request behavior, DAG activity, or TiKV thread state and I/O.
- Retrieval Keywords: TiKV-Details dashboard, GC, GC tasks, GC tasks Duration, TiDB GC seconds, TiDB GC worker actions, ResolveLocks Progress, TiKV Auto GC Progress, GC speed, TiKV Auto GC SafePoint, GC lifetime, GC interval, GC in Compaction Filter, Snapshot, Rate snapshot message, 99% Handle snapshot duration, Snapshot state count, 99.99% Snapshot size, 99.99% Snapshot KV count, Task, Worker handled tasks, Worker pending tasks, FuturePool handled tasks, FuturePool pending tasks, Coprocessor Overview, Request duration, Total Requests, Handle duration, Total Request Errors, Total KV Cursor Operations, KV Cursor Operations, Total RocksDB Perf Statistics, Total Response Size, Coprocessor Detail, 95% Handle duration by store, Wait duration, 95% Wait duration by store, Total DAG Requests, Total DAG Executors, Total Ops Details (Table Scan), Total Ops Details (Index Scan), Total Ops Details by CF (Table Scan), Total Ops Details by CF (Index Scan), Threads, Threads state, Threads IO, Thread Voluntary Context Switches, Thread Nonvoluntary Context Switches
- Follow-up Guidance: The source also gives several normal-case interpretations, including Worker pending tasks being less than 1000, Coprocessor Wait duration being less than 10s at P99.99, and not having many Total Request Errors in a short time.
- Classification Note: This is classified as observability for TiKV because the content describes Grafana TiKV-Details dashboard metrics for GC, snapshots, task pools, coprocessor processing, and thread-level runtime behavior.

## Official Source Content

### GC

- GC tasks: The count of GC tasks processed by gc_worker
- GC tasks Duration: The time consumed when executing GC tasks
- TiDB GC seconds: The GC duration
- TiDB GC worker actions: The count of TiDB GC worker actions
- ResolveLocks Progress: The progress of the first phase of GC (Resolve Locks)
- TiKV Auto GC Progress: The progress of the second phase of GC
- GC speed: The number of keys deleted by GC per second
- TiKV Auto GC SafePoint: The value of TiKV GC safe point. The safe point is the current GC timestamp
- GC lifetime: The lifetime of TiDB GC
- GC interval: The interval of TiDB GC
- GC in Compaction Filter: The count of filtered versions in the compaction filter of write CF.
### Snapshot

- Rate snapshot message: The rate at which Raft snapshot messages are sent
- 99% Handle snapshot duration: The time consumed to handle snapshots (P99)
- Snapshot state count: The number of snapshots per state
- 99.99% Snapshot size: The snapshot size (P99.99)
- 99.99% Snapshot KV count: The number of KV within a snapshot (P99.99)
### Task

- Worker handled tasks: The number of tasks handled by worker per second
- Worker pending tasks: Current number of pending and running tasks of worker per second. It should be less than `1000` in normal case.
- FuturePool handled tasks: The number of tasks handled by future pool per second
- FuturePool pending tasks: Current number of pending and running tasks of future pool per second
### Coprocessor Overview

- Request duration: The total duration from the time of receiving the coprocessor request to the time of finishing processing the request
- Total Requests: The number of requests by type per second
- Handle duration: The histogram of time spent actually processing coprocessor requests per minute
- Total Request Errors: The number of request errors of Coprocessor per second. There should not be a lot of errors in a short time.
- Total KV Cursor Operations: The total number of the KV cursor operations by type per second, such as `select`, `index`, `analyze_table`, `analyze_index`, `checksum_table`, and `checksum_index`.
- KV Cursor Operations: The histogram of KV cursor operations by type per second
- Total RocksDB Perf Statistics: The statistics of RocksDB performance
- Total Response Size: The total size of coprocessor response
### Coprocessor Detail

- Handle duration: The histogram of time spent actually processing coprocessor requests per minute
- 95% Handle duration by store: The time consumed to handle coprocessor requests per TiKV instance per second (P95)
- Wait duration: The time consumed when coprocessor requests are waiting to be handled. It should be less than `10s` (P99.99).
- 95% Wait duration by store: The time consumed when coprocessor requests are waiting to be handled per TiKV instance per second (P95)
- Total DAG Requests: The total number of DAG requests per second
- Total DAG Executors: The total number of DAG executors per second
- Total Ops Details (Table Scan): The number of RocksDB internal operations per second when executing select scan in coprocessor
- Total Ops Details (Index Scan): The number of RocksDB internal operations per second when executing index scan in coprocessor
- Total Ops Details by CF (Table Scan): The number of RocksDB internal operations for each CF per second when executing select scan in coprocessor
- Total Ops Details by CF (Index Scan): The number of RocksDB internal operations for each CF per second when executing index scan in coprocessor
### Threads

- Threads state: The state of TiKV threads
- Threads IO: The I/O traffic of each TiKV thread
- Thread Voluntary Context Switches: The number of TiKV threads voluntary context switches
- Thread Nonvoluntary Context Switches: The number of TiKV threads nonvoluntary context switches
