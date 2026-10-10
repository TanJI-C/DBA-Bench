# Follower Read overview and tidb_replica_read usage modes

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/follower-read.md`
- Source Title: `Follower Read`
- Source Heading Path: `Follower Read | Follower Read > Overview | Follower Read > Usage`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `operator`
- Topic Tags: `follower-read`, `replica-read`, `session-variables`, `read-routing`, `strong-consistency`, `availability-zones`, `topology-labels`, `learner-replicas`, `version-specific-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0112_de17e4c4d8`
- Source ID: `tidb-docs-8.1:follower-read.md#follower-read`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3dba39e5cf70eebd637489d2df211ae4b8443a9985c95d9a04434dc019cfd3a1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/follower-read#follower-read
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/follower-read.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how `tidb_replica_read` modes route reads among leader, follower, learner, same-availability-zone replicas, or fallbacks in Follower Read.
- Retrieval Keywords: Follower Read, tidb_replica_read, set [session | global] tidb_replica_read, leader, follower, leader-and-follower, prefer-leader, closest-replicas, closest-adaptive, learner, tidb_adaptive_closest_read_threshold, ReadIndex, location-labels, zone label, labels for TiDB and TiKV, Schedule replicas by topology labels
- Follow-up Guidance: The source also notes that `closest-replicas` and `closest-adaptive` depend on PD `location-labels` and TiDB and TiKV `labels`, including the `zone` label, and that TiDB v7.5.0 and earlier return an error in specific no-replica cases for `follower` and `learner`.
- Classification Note: This is classified as configuration because the content centers on setting the `tidb_replica_read` session or global variable and explains the behavior of each allowed value.

## Official Source Content

# Follower Read

When a read hotspot appears in a Region, the Region leader can become a read bottleneck for the entire system. In this situation, enabling the Follower Read feature can significantly reduce the load of the leader, and improve the throughput of the whole system by balancing the load among multiple followers. This document introduces the use and implementation mechanism of Follower Read.
## Overview

The Follower Read feature refers to using any follower replica of a Region to serve a read request under the premise of strongly consistent reads. This feature improves the throughput of the TiDB cluster and reduces the load of the leader. It contains a series of load balancing mechanisms that offload TiKV read loads from the leader replica to the follower replica in a Region. TiKV's Follower Read implementation provides users with strongly consistent reads.

> **Note:**
>
> To achieve strongly consistent reads, the follower node currently needs to request the current execution progress from the leader node (that is `ReadIndex`), which causes an additional network request overhead. Therefore, the main benefits of Follower Read are to isolate read requests from write requests in the cluster and to increase overall read throughput.
## Usage

To enable TiDB's Follower Read feature, modify the value of the `tidb_replica_read` variable as follows:

```sql
set [session | global] tidb_replica_read = '<target value>';
```

Scope: SESSION | GLOBAL

Default: leader

This variable is used to set the expected data read mode.

- When you set the value of `tidb_replica_read` to `leader` or an empty string, TiDB maintains its default behavior and sends all read operations to the leader replica to perform.
- When you set the value of `tidb_replica_read` to `follower`, TiDB selects a follower replica of the Region to perform read operations. If the Region has learner replicas, TiDB also considers them for reads with the same priority. If no available follower or learner replicas exist for the current Region, TiDB reads from the leader replica.
- When the value of `tidb_replica_read` is set to `leader-and-follower`, TiDB can select any replicas to perform read operations. In this mode, read requests are load balanced between the leader, follower, and learner.
- When the value of `tidb_replica_read` is set to `prefer-leader`, TiDB prefers to select the leader replica to perform read operations. If the leader replica is obviously slow in processing read operations (such as caused by disk or network performance jitter), TiDB will select other available follower replicas to perform read operations.
- When the value of `tidb_replica_read` is set to `closest-replicas`, TiDB prefers to select a replica in the same availability zone to perform read operations, which can be a leader, a follower, or a learner. If there is no replica in the same availability zone, TiDB reads from the leader replica.
- When the value of `tidb_replica_read` is set to `closest-adaptive`:

    - If the estimated result of a read request is greater than or equal to the value of [`tidb_adaptive_closest_read_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_adaptive_closest_read_threshold-new-in-v630), TiDB prefers to select a replica in the same availability zone for read operations. To avoid unbalanced distribution of read traffic across availability zones, TiDB dynamically detects the distribution of availability zones for all online TiDB and TiKV nodes. In each availability zone, the number of TiDB nodes whose `closest-adaptive` configuration takes effect is limited, which is always the same as the number of TiDB nodes in the availability zone with the fewest TiDB nodes, and the other TiDB nodes automatically read from the leader replica. For example, if TiDB nodes are distributed across 3 availability zones (A, B, and C), where A and B each contains 3 TiDB nodes and C contains only 2 TiDB nodes, the number of TiDB nodes whose `closest-adaptive` configuration takes effect in each availability zone is 2, and the other TiDB node in each of the A and B availability zones automatically selects the leader replica for read operations.
    - If the estimated result of a read request is less than the value of [`tidb_adaptive_closest_read_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_adaptive_closest_read_threshold-new-in-v630), TiDB can only select the leader replica for read operations.

- When you set the value of `tidb_replica_read` to `learner`, TiDB reads data from the learner replica. If no learner replica is available for the current Region, TiDB reads from an available leader or follower replica.

> **Note:**
>
> When you set `tidb_replica_read` to `closest-replicas` or `closest-adaptive`, to ensure that replicas are distributed across availability zones according to the specified configuration, you need to configure `location-labels` for PD and set the correct `labels` for TiDB and TiKV according to [Schedule replicas by topology labels](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels). TiDB depends on the `zone` label to match TiKV nodes in the same availability zone, so you need to make sure that the `zone` label is included in the `location-labels` of PD and `zone` is included in the configuration of each TiDB and TiKV node. If your cluster is deployed using TiDB Operator, refer to [High availability of data](https://docs.pingcap.com/tidb-in-kubernetes/stable/configure-a-tidb-cluster#high-availability-of-data).
>
> For TiDB v7.5.0 and earlier versions:
>
> - If you set `tidb_replica_read` to `follower` and no follower or learner replicas are available, TiDB returns an error.
> - If you set `tidb_replica_read` to `learner` and no learner replicas are available, TiDB returns an error.
