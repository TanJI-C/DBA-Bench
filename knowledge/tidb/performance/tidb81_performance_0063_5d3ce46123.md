# Three-data-center local read with Stale Read and zone labels

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/three-dc-local-read.md`
- Source Title: `Local Read under Three Data Centers Deployment`
- Source Heading Path: `Local Read under Three Data Centers Deployment | Local Read under Three Data Centers Deployment > Deploy a TiDB cluster of three data centers | Local Read under Three Data Centers Deployment > Perform local read using Stale Read`
- Source Line Ranges: `5-29`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `shared`
- Topic Tags: `three-data-center`, `local-read`, `stale-read`, `zone-labels`, `closest-replicas`, `cross-center-latency`, `geo-distributed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0063_5d3ce46123`
- Source ID: `tidb-docs-8.1:best-practices/three-dc-local-read.md#local-read-under-three-data-centers-deployment`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b29b622167385ea80a45a8732704587b491f7c380149da023e993586aa811122`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/three-dc-local-read#local-read-under-three-data-centers-deployment
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/three-dc-local-read.md

## Retrieval Guidance

- Use When: Use this chunk when asking how to reduce cross-center read latency in a three-data-center TiDB deployment by using Stale Read together with matching `zone` labels and `tidb_replica_read=closest-replicas`.
- Retrieval Keywords: three data centers, Local Read under Three Data Centers Deployment, Stale Read, zone label, labels, zone=dc-1, tidb_replica_read, closest-replicas, cross-center access, cross-center latency, geo-distributed deployment, Leader replica, historical data, AS OF TIMESTAMP
- Follow-up Guidance: The source points to the Stale Read documentation and to performing Stale Read using the `AS OF TIMESTAMP` clause, and notes the three-data-center deployment method in Multiple Data Centers in One City Deployment.
- Classification Note: This is classified as a TiDB performance topic because the content explains lowering read access latency in a geo-distributed three-data-center setup by reading local replicas through Stale Read instead of always accessing the Leader replica across data centers.

## Official Source Content

# Local Read under Three Data Centers Deployment

In the model of three data centers, a Region has three replicas which are isolated in each data center. However, due to the requirement of strongly consistent read, TiDB must access the Leader replica of the corresponding data for every query. If the query is generated in a data center different from that of the Leader replica, TiDB needs to read data from another data center, thus causing the access latency to increase.

This document describes how to use the [Stale Read](https://docs.pingcap.com/tidb/stable/stale-read) feature to avoid cross-center access and reduce the access latency at the expense of real-time data availability.
## Deploy a TiDB cluster of three data centers

For the three-data-center deployment method, refer to [Multiple Data Centers in One City Deployment](https://docs.pingcap.com/tidb/stable/multi-data-centers-in-one-city-deployment).

Note that if both the TiKV and TiDB nodes have the configuration item `labels` configured, the TiKV and TiDB nodes in the same data center must have the same value for the `zone` label. For example, if a TiKV node and a TiDB node are both in the data center `dc-1`, then the two nodes need to be configured with the following label:

```
[labels]
zone=dc-1
```
## Perform local read using Stale Read

[Stale Read](https://docs.pingcap.com/tidb/stable/stale-read) is a mechanism that TiDB provides for the users to read historical data. Using this mechanism, you can read the corresponding historical data of a specific point in time or within a specified time range, and thus save the latency brought by data replication between storage nodes. When using Stale Read in some scenarios of geo-distributed deployment, TiDB accesses the replica in the current data center to read the corresponding data at the expense of some real-time performance, which avoids network latency brought by cross-center connection and reduces the access latency for the entire query process.

When TiDB receives a Stale Read query, if the `zone` label of that TiDB node is configured, and [`tidb_replica_read`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_replica_read-new-in-v40) is set to `closest-replicas`, then TiDB sends the request to the TiKV node with the same `zone` label where the corresponding data replica resides.

For how to perform Stale Read, see [Perform Stale Read using the `AS OF TIMESTAMP` clause](https://docs.pingcap.com/tidb/stable/as-of-timestamp).
