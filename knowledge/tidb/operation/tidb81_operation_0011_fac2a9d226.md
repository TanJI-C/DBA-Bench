# Scheduling parameters and slow or uneven balancing scenarios

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/pd-scheduling-best-practices.md`
- Source Title: `PD Scheduling Best Practices`
- Source Heading Path: `PD Scheduling Best Practices > Control scheduling strategy > Adjust scheduling parameter | PD Scheduling Best Practices > PD scheduling in common scenarios | PD Scheduling Best Practices > PD scheduling in common scenarios > Leaders/regions are not evenly distributed | PD Scheduling Best Practices > PD scheduling in common scenarios > Taking nodes offline is slow | PD Scheduling Best Practices > PD scheduling in common scenarios > Bringing nodes online is slow`
- Source Line Ranges: `184-243`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `scheduling-parameters`, `load-balancing`, `leader-distribution`, `region-distribution`, `offline-nodes`, `online-nodes`, `operator-generation`, `operator-execution`, `scheduler-limits`, `snapshots`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0011_fac2a9d226`
- Source ID: `tidb-docs-8.1:best-practices/pd-scheduling-best-practices.md#adjust-scheduling-parameter`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9b53096802ac260ab1b3a3064464e7474fc13a214d972d57ab62f407bc47003a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/pd-scheduling-best-practices#adjust-scheduling-parameter
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/pd-scheduling-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting slow PD scheduling, uneven leader or region distribution, slow node offline handling, or slow node online balancing in a self-managed TiDB cluster.
- Retrieval Keywords: config show, config set {key} {value}, leader-schedule-limit, region-schedule-limit, replica-schedule-limit, enable-replace-offline-replica, enable-location-replacement, max-snapshot-count, max-pending-peer-count, leader-weight, region-weight, Operator step duration, TransferLeader, RemovePeer, PromoteLearner, AddLearner, AddPeer, evict-leader-scheduler, label property, scheduler limit set to 0, taking nodes offline is slow, bringing nodes online is slow, leaders/regions are not evenly distributed
- Follow-up Guidance: The content points to related troubleshooting for hot regions scheduling and region merge when hot regions, empty regions, or small regions affect balancing.
- Classification Note: This is classified as operation because the content focuses on checking PD scheduling configuration, examining operator generation and execution metrics, and adjusting scheduler parameters during cluster balancing scenarios.

## Official Source Content

### Adjust scheduling parameter

You can check the scheduling configuration using the `config show` command in pd-ctl, and adjust the values using `config set {key} {value}`. Common adjustments include:

- `leader-schedule-limit`: Controls the concurrency of transferring leader scheduling
- `region-schedule-limit`: Controls the concurrency of adding/deleting peer scheduling
- `enable-replace-offline-replica`: Determines whether to enable the scheduling to take nodes offline
- `enable-location-replacement`: Determines whether to enable the scheduling that handles the isolation level of regions
- `max-snapshot-count`: Controls the maximum concurrency of sending/receiving snapshots for each store
## PD scheduling in common scenarios

This section illustrates the best practices of PD scheduling strategies through several typical scenarios.
### Leaders/regions are not evenly distributed

The rating mechanism of PD determines that leader count and region count of different stores cannot fully reflect the load balancing status. Therefore, it is necessary to confirm whether there is load imbalancing from the actual load of TiKV or storage usage.

Once you have confirmed that leaders/region are not evenly distributed, you need to check the rating of different stores.

If the scores of different stores are close, it means PD mistakenly believes that leaders/regions are evenly distributed. Possible reasons are:

- There are hot regions that cause load imbalancing. In this case, you need to analyze further based on [hot regions scheduling](#hot-regions-are-not-evenly-distributed).
- There are a large number of empty regions or small regions, which leads to a great difference in the number of leaders in different stores and high pressure on Raft store. This is the time for a [region merge](#region-merge-is-slow) scheduling.
- Hardware and software environment varies among stores. To control the distribution of leader/region, you can refer to [Load balancing](#load-balancing) and adjust the values of `leader-weight` and `region-weight`.
- Other unknown reasons. Still you can adjust the values of `leader-weight` and `region-weight` to control the distribution of leader/region.

If there is a big difference in the rating of different stores, you need to examine the operator-related metrics, with special focus on the generation and execution of operators. There are two main situations:

- When operators are generated normally but the scheduling process is slow, it is possible that:

    - The scheduling speed is limited by default for load balancing purpose. You can adjust `leader-schedule-limit` or `region-schedule-limit` to larger values without significantly impacting regular services. In addition, you can also properly ease the restrictions specified by `max-pending-peer-count` and `max-snapshot-count`.
    - Other scheduling tasks are running concurrently, which slows down the balancing. In this case, if the balancing takes precedence over other scheduling tasks, you can stop other tasks or limit their speeds. For example, if you take some nodes offline when balancing is in progress, both operations consume the quota of `region-schedule-limit`. In this case, you can limit the speed of scheduler to remove nodes, or simply set `enable-replace-offline-replica = false` to temporarily disable it.
    - The scheduling process is too slow. You can check the **Operator step duration** metric to confirm the cause. Generally, steps that do not involve sending and receiving snapshots (such as `TransferLeader`, `RemovePeer`, `PromoteLearner`) should be completed in milliseconds, while steps that involve snapshots (such as `AddLearner` and `AddPeer`) are expected to be completed in tens of seconds. If the duration is obviously too long, it could be caused by high pressure on TiKV or bottleneck in network, which needs specific analysis.

- PD fails to generate the corresponding balancing scheduler. Possible reasons include:

    - The scheduler is not activated. For example, the corresponding scheduler is deleted, or its limit it set to "0".
    - Other constraints. For example, `evict-leader-scheduler` in the system prevents leaders from being migrating to the corresponding store. Or label property is set, which makes some stores reject leaders.
    - Restrictions from the cluster topology. For example, in a cluster of 3 replicas across 3 data centers, 3 replicas of each region are distributed in different data centers due to replica isolation. If the number of stores is different among these data centers, the scheduling can only reach a balanced state within each data center, but not balanced globally.
### Taking nodes offline is slow

This scenario requires examining the generation and execution of operators through related metrics.

If operators are successfully generated but the scheduling process is slow, possible reasons are:

- The scheduling speed is limited by default. You can adjust `leader-schedule-limit` or `replica-schedule-limit` to larger values. Similarly, you can consider loosening the limits on `max-pending-peer-count` and `max-snapshot-count`.
- Other scheduling tasks are running concurrently and racing for resources in the system. You can refer to the solution in [Leaders/regions are not evenly distributed](#leadersregions-are-not-evenly-distributed).
- When you take a single node offline, a number of region leaders to be processed (around 1/3 under the configuration of 3 replicas) are distributed on the node to remove. Therefore, the speed is limited by the speed at which snapshots are generated by this single node. You can speed it up by manually adding an `evict-leader-scheduler` to migrate leaders.

If the corresponding operator fails to generate, possible reasons are:

- The operator is stopped, or `replica-schedule-limit` is set to "0".
- There is no proper node for region migration. For example, if the available capacity size of the replacing node (of the same label) is less than 20%, PD will stop scheduling to avoid running out of storage on that node. In such case, you need to add more nodes or delete some data to free the space.
### Bringing nodes online is slow

Currently, bringing nodes online is scheduled through the balance region mechanism. You can refer to [Leaders/regions are not evenly distributed](#leadersregions-are-not-evenly-distributed) for troubleshooting.
