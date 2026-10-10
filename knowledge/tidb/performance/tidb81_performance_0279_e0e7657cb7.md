# Optimize and scatter read hotspots

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-hot-spot-issues.md`
- Source Title: `Troubleshoot Hotspot Issues`
- Source Heading Path: `Troubleshoot Hotspot Issues > Optimization of small table hotspots | Troubleshoot Hotspot Issues > Scatter read hotspots`
- Source Line Ranges: `173-186`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `small-table-hotspots`, `coprocessor-cache`, `read-hotspots`, `replica-read`, `follower-read`, `queue-threshold`, `latency`, `throughput`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0279_e0e7657cb7`
- Source ID: `tidb-docs-8.1:troubleshoot-hot-spot-issues.md#optimization-of-small-table-hotspots`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ddce63c4c429659cc3a1aaf22b31a43973749a60c111596e9725e832591eb2c1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#optimization-of-small-table-hotspots
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-hot-spot-issues.md

## Retrieval Guidance

- Use When: Use this chunk when you need options for small-table read hotspots or for reducing read queuing on a hotspot TiKV node.
- Retrieval Keywords: Optimization of small table hotspots, Coprocessor Cache, read hotspots of small tables, Scatter read hotspots, load-based replica read, tidb_load_based_replica_read_threshold, queue time, follower nodes, read throughput
- Follow-up Guidance: See the linked Coprocessor Cache and split-region references if you need the related feature pages.
- Classification Note: This chunk describes read-hotspot optimization with Coprocessor Cache and load-based replica read for scattering reads.

## Official Source Content

## Optimization of small table hotspots

The Coprocessor Cache feature of TiDB supports pushing down computing result caches. After this feature is enabled, TiDB caches the computing results that will be pushed down to TiKV. This feature works well for read hotspots of small tables.

For more details, see [Coprocessor Cache](https://docs.pingcap.com/tidb/stable/coprocessor-cache).

**See also:**

- [Highly Concurrent Write Best Practices](https://docs.pingcap.com/tidb/stable/best-practices/high-concurrency-best-practices)
- [Split Region](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region)
## Scatter read hotspots

In a read hotspot scenario, the hotspot TiKV node cannot process read requests in time, resulting in the read requests queuing. However, not all TiKV resources are exhausted at this time. To reduce latency, TiDB v7.1.0 introduces the load-based replica read feature, which allows TiDB to read data from other TiKV nodes without queuing on the hotspot TiKV node. You can control the queue length of read requests using the [`tidb_load_based_replica_read_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_load_based_replica_read_threshold-new-in-v700) system variable. When the estimated queue time of the leader node exceeds this threshold, TiDB prioritizes reading data from follower nodes. This feature can improve read throughput by 70% to 200% in a read hotspot scenario compared to not scattering read hotspots.
