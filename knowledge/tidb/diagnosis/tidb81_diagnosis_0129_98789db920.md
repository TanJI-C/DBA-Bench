# Other latency causes maintenance replicas indexes and GC

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-cpu-issues.md`
- Source Title: `Troubleshoot Increased Read and Write Latency`
- Source Heading Path: `Troubleshoot Increased Read and Write Latency > Other causes | Troubleshoot Increased Read and Write Latency > Other causes > Cluster maintenance | Troubleshoot Increased Read and Write Latency > Other causes > Minority of replicas are offline | Troubleshoot Increased Read and Write Latency > Other causes > New indexes | Troubleshoot Increased Read and Write Latency > Other causes > High GC pressure`
- Source Line Ranges: `111-139`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tidb`, `tikv`, `sql`
- Topic Tags: `maintenance`, `leadership-switch`, `replicas`, `raft`, `index-creation`, `ddl`, `backfill`, `gc`, `mvcc`, `scan-lock`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0129_98789db920`
- Source ID: `tidb-docs-8.1:troubleshoot-cpu-issues.md#other-causes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a0cd6dad70cf0e8b6ce92036b8ba00f426fc378702777582495c60e0285b457a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-cpu-issues#other-causes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-cpu-issues.md

## Retrieval Guidance

- Use When: Use this chunk when latency or performance jitter is related to cluster maintenance, a minority of replicas being offline, creating new indexes, or high GC pressure phases and their observable requests.
- Retrieval Keywords: Cluster maintenance, switch the leadership, performance jitter of about 3 seconds, Minority of replicas are offline, Raft protocol, New indexes, tidb_ddl_reorg_worker_cnt, tidb_ddl_reorg_batch_size, tidb_ddl_reorg_priority, PRIORITY_HIGH, High GC pressure, MVCC, Resolve Locks, scan_lock, Delete Ranges, unsafe_destroy_range, GC tasks, Do GC
- Follow-up Guidance: The content provides parameter names for adjusting index creation speed and identifies GC phases and request types that can be observed in gRPC-related metrics and the GC tasks panel.
- Classification Note: This is classified as diagnosis content because it summarizes other documented causes of latency or jitter and names the exact operational conditions, parameters, and GC indicators involved.

## Official Source Content

## Other causes
### Cluster maintenance

Most of each online cluster has three or five nodes. If the machine to be maintained has the PD component, you need to determine whether the node is the leader or the follower. Disabling a follower has no impact on the cluster operation. Before disabling a leader, you need to switch the leadership. During the leadership change, performance jitter of about 3 seconds will occur.
### Minority of replicas are offline

By default, each TiDB cluster has three replicas, so each Region has three replicas in the cluster. These Regions elect the leader and replicate data through the Raft protocol. The Raft protocol ensures that TiDB can still provide services without data loss even when the nodes (that are fewer than half of replicas) fail or are isolated. For the cluster with three replicas, the failure of one node might cause performance jitter but the usability and correctness in theory are not affected.
### New indexes

Creating indexes consumes a huge amount of resources when TiDB scans tables and backfills indexes. Index creation might even conflict with the frequently updated fields, which affects the application. Creating indexes on a large table often takes a long time, so you must try to balance the index creation time and the cluster performance (for example, creating indexes at the off-peak time).

**Parameter adjustment:**

Currently, you can use `tidb_ddl_reorg_worker_cnt` and `tidb_ddl_reorg_batch_size` to dynamically adjust the speed of index creation. Usually, the smaller the values, the smaller the impact on the system, with longer execution time though.

In general cases, you can first keep their default values (`4` and `256`), observe the resource usage and response speed of the cluster, and then increase the value of `tidb_ddl_reorg_worker_cnt` to increase the concurrency. If no obvious jitter is observed in the monitor, increase the value of `tidb_ddl_reorg_batch_size`. If the columns involved in the index creation are frequently updated, the many resulting conflicts will cause the index creation to fail and be retried.

In addition, you can also set the value of `tidb_ddl_reorg_priority` to `PRIORITY_HIGH` to prioritize the index creation and speed up the process. But in the general OLTP system, it is recommended to keep its default value.
### High GC pressure

The transaction of TiDB adopts the Multi-Version Concurrency Control (MVCC) mechanism. When the newly written data overwrites the old data, the old data is not replaced, and both versions of data are stored. Timestamps are used to mark different versions. The task of GC is to clear the obsolete data.

* In the phase of Resolve Locks, a large amount of `scan_lock` requests are created in TiKV, which can be observed in the gRPC-related metrics. These `scan_lock` requests call all Regions.
* In the phase of Delete Ranges, a few (or no) `unsafe_destroy_range` requests are sent to TiKV, which can be observed in the gRPC-related metrics and the **GC tasks** panel.
* In the phase of Do GC, each TiKV by default scans the leader Regions on the machine and performs GC to each leader, which can be observed in the **GC tasks** panel.
