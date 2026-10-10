# New stability features and operational safeguards

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.0.md`
- Source Title: `TiDB 6.1.0 Release Notes`
- Source Heading Path: `TiDB 6.1.0 Release Notes > New Features > Stability`
- Source Line Ranges: `104-131`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `tidb`
- Topic Tags: `release-notes`, `new-features`, `stability`, `sst-corruption`, `automatic-recovery`, `non-transactional-dml`, `gc`, `statistics`, `mvcc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0297_f43e7f1b58`
- Source ID: `tidb-docs-8.1:releases/release-6.1.0.md#stability`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e0a2ad72c9625c39f3e064abea08f9976de073cff76fefd4b6f6481bdf5a30e9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.0#stability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.1.0 release-note information about stability features such as SST corruption recovery, non-transactional DELETE batching, GC wait time control, or automatic statistics collection time limits.
- Retrieval Keywords: TiDB 6.1.0 Release Notes, Stability, Automatic recovery from SST corruption, background-error-recovery-window, non-transactional DML, DELETE, BATCH, tidb_gc_max_wait_time, GC wait time, MVCC, tidb_max_auto_analyze_time, automatic statistics collection
- Follow-up Guidance: The content links to user documents for background-error-recovery-window, non-transactional DML, tidb_gc_max_wait_time, and system variables including tidb_max_auto_analyze_time.
- Classification Note: This is classified as a release chunk because it describes TiDB 6.1.0 stability-focused features and safeguards affecting TiKV and TiDB operations.

## Official Source Content

### Stability

* Automatic recovery from SST corruption

    When RocksDB detects a damaged SST file in the background, TiKV will try to schedule the affected Peer and recover its data using other replicas. You can set the maximum allowable time for the recovery using the `background-error-recovery-window` parameter. If the recovery operation is not completed within the time window, TiKV will panic. This feature automatically detects and recovers recoverable damaged storage, thus improving the cluster stability.

    [User document](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#background-error-recovery-window-new-in-v610), [#10578](https://github.com/tikv/tikv/issues/10578)

* Support non-transactional DML statement

    In the scenarios of large data processing, a single SQL statement with a large transaction might have a negative impact on the cluster stability and performance. Since v6.1.0, TiDB supports providing a syntax in which a `DELETE` statement is split into multiple statements for batch processing. The split statements compromise transactional atomicity and isolation but greatly improve the cluster stability. For detailed syntax, see [`BATCH`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-batch).

    [User document](https://docs.pingcap.com/tidb/stable/non-transactional-dml)

* TiDB supports configuring the maximum GC wait time

    The transaction of TiDB adopts the Multi-Version Concurrency Control (MVCC) mechanism. When the newly written data overwrites the old data, the old data is not replaced, and both versions of data are stored. The old data is cleaned up by the Garbage Collection (GC) task periodically, which helps reclaim storage space to improve the performance and stability of the cluster. GC is triggered every 10 minutes by default. To ensure that long-running transactions can access the corresponding historical data, when there are transactions in execution, the GC task is delayed. To ensure that the GC task is not delayed indefinitely, TiDB introduces the system variable [`tidb_gc_max_wait_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_max_wait_time-new-in-v610) to control the maximum delay time of the GC task. If the maximum delay time is exceeded, the GC will be forcibly executed. The default value of the variable is 24 hours. This feature enables you to control the relationship between the GC waiting time and the long-running transaction, which improves the stability of the cluster.

    [User document](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_max_wait_time-new-in-v610)

* TiDB supports configuring the maximum execution time for automatic statistics collection tasks

    Databases can effectively understand the distribution of data by collecting statistics, which helps generate reasonable execution plans and improve the efficiency of SQL execution. TiDB regularly collects statistics on frequently changed data objects in the background. However, collecting statistics takes up cluster resources and might affect the stable operation of the business during business peaks.

    Starting from v6.1.0, TiDB introduces [`tidb_max_auto_analyze_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_auto_analyze_time-new-in-v610) to control the maximum execution time for background statistics collection, which is 12 hours by default. When the application does not encounter a resource bottleneck, it is recommended not to modify this variable so that TiDB can timely collect statistics.

    [User document](https://docs.pingcap.com/tidb/stable/system-variables)
