# In-cluster bottlenecks, hotspot detection, scaling, and summary actions

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-tune-performance-overview.md`
- Source Title: `Overview for Analyzing and Tuning Performance`
- Source Heading Path: `Overview for Analyzing and Tuning Performance > Troubleshoot bottlenecks in user response time > Bottlenecks in the TiDB cluster | Overview for Analyzing and Tuning Performance > Troubleshoot bottlenecks in user response time > Bottlenecks in the TiDB cluster > Optimize slow SQL queries | Overview for Analyzing and Tuning Performance > Troubleshoot bottlenecks in user response time > Bottlenecks in the TiDB cluster > Resolve hotstpot issues | Overview for Analyzing and Tuning Performance > Troubleshoot bottlenecks in user response time > Bottlenecks in the TiDB cluster > Scale out | Overview for Analyzing and Tuning Performance > Troubleshoot bottlenecks in user response time > Bottlenecks in the TiDB cluster > Other issues | Overview for Analyzing and Tuning Performance > Summary`
- Source Line Ranges: `72-128`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`, `sql`, `tidb`, `tikv`
- Topic Tags: `internal-bottlenecks`, `slow-sql`, `hotspot`, `key-visualizer`, `read-hotspot`, `write-hotspot`, `scale-out`, `cpu-utilization`, `storage-space`, `io-rate`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0206_2bc620fe4b`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-tune-performance-overview.md#bottlenecks-in-the-tidb-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8a80a325ac91a83c2d22ec0b8533573c906399c07caa4b1f2bd2e6a27b50fb22`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-tune-performance-overview#bottlenecks-in-the-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-tune-performance-overview.md

## Retrieval Guidance

- Use When: Use this chunk when you have determined the bottleneck is inside the TiDB cluster and need the documented guidance on slow SQL, hotspot patterns in Key Visualizer, scale-out indicators, support information, and the summary optimization table.
- Retrieval Keywords: Bottlenecks in the TiDB cluster, Optimize slow SQL queries, SQL Tuning Overview, Resolve hotspot issues, Key Visualizer tab, write hotspot, read hotspot, bright diagonal line, stepped pattern, self-incrementing primary key, no primary key, time-dependent insert statement, bright horizontal line, hover over the highlighted block, Scale out, storage space, CPU utilization, TiKV IO rate, cluster ID, issue interval, comparable normal interval, problem phenomenon, expected behavior, business workload characteristics, read or write ratios, Prepared plan cache + JDBC, Enable AsyncIO and Raft-engine in TiKV, Clustered Index, Scale out TiDB nodes, Client-side optimization. Split 1 JVM into 3, Limit the network latency between the application and the database
- Follow-up Guidance: It directs you to SQL Tuning Overview, Key Visualizer, the cluster Overview metrics, and the PingCAP support team, and it lists the information to provide if previous methods cannot resolve the issue.
- Classification Note: This is classified as performance for TiDB Cloud because it focuses on diagnosing in-cluster bottlenecks, recognizing hotspot heat map patterns, checking scale-out signals, and summarizing documented optimization actions and effects.

## Official Source Content

### Bottlenecks in the TiDB cluster

If you determine that the performance bottleneck is within a TiDB cluster, it is recommended that you do the following:

- Optimize slow SQL queries.
- Resolve hotspot issues.
- Scale out the cluster to expand the capacity.
#### Optimize slow SQL queries

For more information about SQL performance tuning, see [SQL Tuning Overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sql-tuning-overview).
#### Resolve hotstpot issues

You can view hotspot issues on the [Key Visualizer tab](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#key-visualizer). The following screenshot shows a sample heat map. The horizontal coordinate of the map is the time, and the vertical coordinate is the table and index. Brighter color indicates higher traffic. You can toggle the display of read or write traffic in the toolbar.

![Hotspot issues](/media/tidb-cloud/tidb-cloud-troubleshoot-hotspot.png)

The following screenshot shows an example of a write hotspot. A bright diagonal line (diagonal up or diagonal down) appears in the write flow graph, and the write traffic appears only at the end of the line. It becomes a stepped pattern as the number of table Regions grows. It indicates that there is a write hotspot in the table. When a write hotspot occurs, you need to check whether you are using a self-incrementing primary key, or no primary key, or using a time-dependent insert statement or index.

![Write hotspot](/media/tidb-cloud/tidb-cloud-troubleshoot-write-hotspot.png)

A read hotspot is generally represented in the heat map as a bright horizontal line, usually a small table with a large number of queries, as shown in the following screenshot.

![Read hotspot](/media/tidb-cloud/tidb-cloud-troubleshoot-read-hotspot-new.png)

Hover over the highlighted block to see which table or index has high traffic, as shown in the following screenshot.

![Hotspot index](/media/tidb-cloud/tidb-cloud-troubleshoot-hotspot-index.png)
#### Scale out

On the cluster [Overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-tidb-cluster) page, check the storage space, CPU utilization, and TiKV IO rate metrics. If any of them are reaching the upper limit for a long time, it is possible that the current cluster size cannot meet the business requirements. It is recommended to contact the [PingCAP support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) to confirm if you need to scale out the cluster.
#### Other issues

If the previous methods cannot resolve the performance issue, you can contact the [PingCAP support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for help. It is recommended to provide the following information to speed up the troubleshooting process.

- The cluster ID
- The issue interval and a comparable normal interval
- The problem phenomenon and expected behavior
- The business workload characteristics, such as read or write ratios and primary behavior
## Summary

In general, you can use the following optimization methods to analyze and resolve performance issues.

| Action | Effect |
|:--|:--|
| Prepared plan cache + JDBC | Throughput performance will be greatly improved, latency will be significantly reduced, and the average TiDB CPU utilization will be significantly reduced. |
| Enable AsyncIO and Raft-engine in TiKV | There will be some improvement in throughput performance. You need to contact the [PingCAP support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) to enable it. |
| Clustered Index | Throughput performance will be greatly improved. |
| Scale out TiDB nodes |Throughput performance will be greatly improved.  |
| Client-side optimization. Split 1 JVM into 3 | Throughput performance will improve significantly and may further continue to improve throughput capacity if further split. |
| Limit the network latency between the application and the database | High network latency can lead to decreased throughput and increased latency. |

In the future, TiDB Cloud will introduce more observable metrics and self-diagnostic services. They will provide you with a more comprehensive understanding of performance metrics and operational advice to improve your experience.
