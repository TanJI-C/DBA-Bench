# PD scheduling policies and core mechanisms

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/pd-scheduling-best-practices.md`
- Source Title: `PD Scheduling Best Practices`
- Source Heading Path: `PD Scheduling Best Practices | PD Scheduling Best Practices > PD scheduling policies | PD Scheduling Best Practices > PD scheduling policies > Scheduling process | PD Scheduling Best Practices > PD scheduling policies > Load balancing | PD Scheduling Best Practices > PD scheduling policies > Hot regions scheduling | PD Scheduling Best Practices > PD scheduling policies > Cluster topology awareness | PD Scheduling Best Practices > PD scheduling policies > Scale-down and failure recovery | PD Scheduling Best Practices > PD scheduling policies > Region merge`
- Source Line Ranges: `5-109`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`, `tidb`
- Topic Tags: `scheduling`, `heartbeats`, `operators`, `load-balancing`, `hot-regions`, `topology-awareness`, `scale-down`, `failure-recovery`, `region-merge`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0006_b15fe20bd6`
- Source ID: `tidb-docs-8.1:best-practices/pd-scheduling-best-practices.md#pd-scheduling-best-practices`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `89b6bfb550c5dbef6ac2835ac303ed527f0794d165ac654097f82313b87ee83b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/pd-scheduling-best-practices#pd-scheduling-best-practices
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/pd-scheduling-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for PD scheduling principles, heartbeat inputs, scheduler behavior, topology-aware replica placement, scale-down or failure recovery, hot region scheduling, or Region merge conditions.
- Retrieval Keywords: StoreHeartbeat, RegionHeartbeat, OperatorController, balance-leader, balance-region, hot-region-scheduler, replicaChecker, mergeChecker, location-labels, leader-weight, region-weight, split-merge-interval, max-merge-region-size, max-merge-region-keys, cluster topology awareness, scale-down and failure recovery, Region merge
- Follow-up Guidance: For checking current scheduling state, the source also points to metrics, pd-ctl, and logs in the query scheduling status section.
- Classification Note: This chunk is classified as architecture because it explains PD scheduling process, internal scheduling components, and the mechanisms used to balance load, place replicas, recover replicas, and merge regions.

## Official Source Content

# PD Scheduling Best Practices

This document details the principles and strategies of PD scheduling through common scenarios to facilitate your application. This document assumes that you have a basic understanding of TiDB, TiKV and PD with the following core concepts:

- [leader/follower/learner](https://docs.pingcap.com/tidb/stable/glossary#leaderfollowerlearner)
- [operator](https://docs.pingcap.com/tidb/stable/glossary#operator)
- [operator step](https://docs.pingcap.com/tidb/stable/glossary#operator-step)
- [pending/down](https://docs.pingcap.com/tidb/stable/glossary#pendingdown)
- [region/peer/Raft group](https://docs.pingcap.com/tidb/stable/glossary#regionpeerraft-group)
- [region split](https://docs.pingcap.com/tidb/stable/glossary#region-split)
- [scheduler](https://docs.pingcap.com/tidb/stable/glossary#scheduler)
- [store](https://docs.pingcap.com/tidb/stable/glossary#store)

> **Note:**
>
> This document initially targets TiDB 3.0. Although some features are not supported in earlier versions (2.x), the underlying mechanisms are similar and this document can still be used as a reference.
## PD scheduling policies

This section introduces the principles and processes involved in the scheduling system.
### Scheduling process

The scheduling process generally has three steps:

1. Collect information

    Each TiKV node periodically reports two types of heartbeats to PD:

    - `StoreHeartbeat`: Contains the overall information of stores, including disk capacity, available storage, and read/write traffic
    - `RegionHeartbeat`: Contains the overall information of regions, including the range of each region, peer distribution, peer status, data volume, and read/write traffic

    PD collects and restores this information for scheduling decisions.

2. Generate operators

    Different schedulers generate the operators based on their own logic and requirements, with the following considerations:

     - Do not add peers to a store in abnormal states (disconnected, down, busy, low space)
     - Do not balance regions in abnormal states
     - Do not transfer a leader to a pending peer
     - Do not remove a leader directly
     - Do not break the physical isolation of various region peers
     - Do not violate constraints such as label property

3. Execute operators

    To execute the operators, the general procedure is:

    1. The generated operator first joins a queue managed by `OperatorController`.

    2. `OperatorController` takes the operator out of the queue and executes it with a certain amount of concurrency based on the configuration. This step is to assign each operator step to the corresponding region leader.

    3. The operator is marked as "finish" or "timeout" and removed from the queue.
### Load balancing

Region primarily relies on `balance-leader` and `balance-region` schedulers to achieve load balance. Both schedulers target distributing regions evenly across all stores in the cluster but with separate focuses: `balance-leader` deals with region leader to balance incoming client requests, whereas `balance-region` concerns itself with each region peer to redistribute the pressure of storage and avoid exceptions like out of storage space.

`balance-leader` and `balance-region` share a similar scheduling process:

1. Rate stores according to their resource availability.
2. `balance-leader` or `balance-region` constantly transfer leaders or peers from stores with high scores to those with low scores.

However, their rating methods are different. `balance-leader` uses the sum of all region sizes corresponding to leaders in a store, whereas the way of `balance-region` is relatively complicated. Depending on the specific storage capacity of each node, the rating method of `balance-region` might:

- based on the amount of data when there is sufficient storage (to balance data distribution among nodes).
- based on the available storage when there is insufficient storage (to balance the storage availability on different nodes).
- based on the weighted sum of the two factors above when neither of the situations applies.

Because different nodes might differ in performance, you can also set the weight of load balancing for different stores. `leader-weight` and `region-weight` are used to control the leader weight and region weight respectively ("1" by default for both). For example, when the `leader-weight` of a store is set to "2", the number of leaders on the node is about twice as many as that of other nodes after the scheduling stabilizes. Similarly, when the `leader-weight` of a store is set to "0.5", the number of leaders on the node is about half as many as that of other nodes.
### Hot regions scheduling

For hot regions scheduling, use `hot-region-scheduler`. Since TiDB v3.0, the process is performed as follows:

1. Count hot regions by determining read/write traffic that exceeds a certain threshold for a certain period based on the information reported by stores.

2. Redistribute these regions in a similar way to load balancing.

For hot write regions, `hot-region-scheduler` attempts to redistribute both region peers and leaders; for hot read regions, `hot-region-scheduler` only redistributes region leaders.
### Cluster topology awareness

Cluster topology awareness enables PD to distribute replicas of a region as much as possible. This is how TiKV ensures high availability and disaster recovery capability. PD continuously scans all regions in the background. When PD finds that the distribution of regions is not optimal, it generates an operator to replace peers and redistribute regions.

The component to check region distribution is `replicaChecker`, which is similar to a scheduler except that it cannot be disabled. `replicaChecker` schedules based on the configuration of `location-labels`. For example, `[zone,rack,host]` defines a three-tier topology for a cluster. PD attempts to schedule region peers to different zones first, or to different racks when zones are insufficient (for example, 2 zones for 3 replicas), or to different hosts when racks are insufficient.
### Scale-down and failure recovery

Scale-down refers to the process when you take a store offline and mark it as "offline" using a command. PD replicates the regions on the offline node to other nodes by scheduling. Failure recovery applies when stores failed and cannot be recovered. In this case, regions with peers distributed on the corresponding store might lose replicas, which requires PD to replenish on other nodes.

The processes of scale-down and failure recovery are basically the same. `replicaChecker` finds a region peer in abnormal states, and then generates an operator to replace the abnormal peer with a new one on a healthy store.
### Region merge

Region merge refers to the process of merging adjacent small regions. It serves to avoid unnecessary resource consumption by a large number of small or even empty regions after data deletion. Region merge is performed by `mergeChecker`, which processes in a similar way to `replicaChecker`: PD continuously scans all regions in the background, and generates an operator when contiguous small regions are found.

Specifically, when a newly split Region exists for more than the value of [`split-merge-interval`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#split-merge-interval) (`1h` by default), if the following conditions occur at the same time, this Region triggers the Region merge scheduling:

- The size of this Region is smaller than the value of the [`max-merge-region-size`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#max-merge-region-size) (20 MiB by default)

- The number of keys in this Region is smaller than the value of [`max-merge-region-keys`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#max-merge-region-keys) (200,000 by default).
