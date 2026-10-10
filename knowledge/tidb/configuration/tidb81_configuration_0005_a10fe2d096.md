# TiKV tuning methods for clusters with massive Regions

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/massive-regions-best-practices.md`
- Source Title: `Best Practices for TiKV Performance Tuning with Massive Regions`
- Source Heading Path: `Best Practices for TiKV Performance Tuning with Massive Regions > Performance tuning methods > Method 1: Increase Raftstore concurrency | Best Practices for TiKV Performance Tuning with Massive Regions > Performance tuning methods > Method 2: Enable Hibernate Region | Best Practices for TiKV Performance Tuning with Massive Regions > Performance tuning methods > Method 3: Enable `Region Merge` | Best Practices for TiKV Performance Tuning with Massive Regions > Performance tuning methods > Method 4: Increase the number of TiKV instances | Best Practices for TiKV Performance Tuning with Massive Regions > Performance tuning methods > Method 5: Adjust `raft-base-tick-interval` | Best Practices for TiKV Performance Tuning with Massive Regions > Performance tuning methods > Method 6: Adjust Region size | Best Practices for TiKV Performance Tuning with Massive Regions > Performance tuning methods > Method 7: Increase the maximum number of connections for Raft communication`
- Source Line Ranges: `72-153`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`
- Topic Tags: `raftstore`, `concurrency`, `hibernate-region`, `region-merge`, `tick-interval`, `region-size`, `raft-communication`, `connections`, `instances`, `scheduling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0005_a10fe2d096`
- Source ID: `tidb-docs-8.1:best-practices/massive-regions-best-practices.md#method-1-increase-raftstore-concurrency`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2cb9db061876b13681a908a09bad0f61e8ccd22af2e37782b685324e299d1011`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/massive-regions-best-practices#method-1-increase-raftstore-concurrency
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/massive-regions-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when looking for documented TiKV and PD tuning methods for clusters with massive Regions, including concurrency, Hibernate Region, Region Merge, tick interval, Region size, and Raft communication connections.
- Retrieval Keywords: raftstore.store-pool-size, Increase Raftstore concurrency, Hibernate Region, Configure Hibernate Region, Region Merge, config set max-merge-region-size 20, config set max-merge-region-keys 200000, config set merge-schedule-limit 8, max-merge-region-size, max-merge-region-keys, merge-schedule-limit, Increase the number of TiKV instances, raft-base-tick-interval, raft-election-timeout, raft-heartbeat-interval, Adjust Region size, grpc-raft-conn-num, maximum number of connections for Raft communication
- Follow-up Guidance: The source notes related defaults and effects, such as Region Merge enabled by default since TiDB v3.0, Hibernate Region enabled by default in TiKV master, and that increasing raft-base-tick-interval also lengthens leader failure detection.
- Classification Note: This chunk is classified as configuration because it centers on specific tunable parameters, default settings, and deployment adjustments for reducing Raftstore pressure with massive Regions.

## Official Source Content

### Method 1: Increase Raftstore concurrency

Raftstore has been upgraded to a multi-threaded module since TiDB v3.0, which greatly reduces the possibility that a Raftstore thread becomes the bottleneck.

By default, `raftstore.store-pool-size` is configured to `2` in TiKV. If a bottleneck occurs in Raftstore, you can properly increase the value of this configuration item according to the actual situation. But to avoid introducing unnecessary thread switching overhead, it is recommended that you do not set this value too high.
### Method 2: Enable Hibernate Region

In the actual situation, read and write requests are not evenly distributed on every Region. Instead, they are concentrated on a few Regions. Then you can minimize the number of messages between the Raft leader and the followers for the temporarily idle Regions, which is the feature of Hibernate Region. In this feature, Raftstore doesn't send tick messages to the Raft state machines of idle Regions if not necessary. Then these Raft state machines will not be triggered to generate heartbeat messages, which can greatly reduce the workload of Raftstore.

Hibernate Region is enabled by default in [TiKV master](https://github.com/tikv/tikv/tree/master). You can configure this feature according to your needs. For details, refer to [Configure Hibernate Region](https://docs.pingcap.com/tidb/stable/tikv-configuration-file).
### Method 3: Enable `Region Merge`

> **Note:**
>
> `Region Merge` is enabled by default since TiDB v3.0.

You can also reduce the number of Regions by enabling `Region Merge`. Contrary to `Region Split`, `Region Merge` is the process of merging adjacent small Regions through scheduling. After dropping data or executing the `Drop Table` or `Truncate Table` statement, you can merge small Regions or even empty Regions to reduce resource consumption.

Enable `Region Merge` by configuring the following parameters:

```
config set max-merge-region-size 20
config set max-merge-region-keys 200000
config set merge-schedule-limit 8
```

Refer to [Region Merge](https://tikv.org/docs/4.0/tasks/configure/region-merge/) and the following three configuration parameters in the [PD configuration file](https://docs.pingcap.com/tidb/stable/pd-configuration-file#schedule) for more details:

- [`max-merge-region-size`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#max-merge-region-size)
- [`max-merge-region-keys`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#max-merge-region-keys)
- [`merge-schedule-limit`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#merge-schedule-limit)

The default configuration of the `Region Merge` parameters is rather conservative. You can speed up the `Region Merge` process by referring to the method provided in [PD Scheduling Best Practices](https://docs.pingcap.com/tidb/stable/best-practices/pd-scheduling-best-practices#region-merge-is-slow).
### Method 4: Increase the number of TiKV instances

If I/O resources and CPU resources are sufficient, you can deploy multiple TiKV instances on a single machine to reduce the number of Regions on a single TiKV instance; or you can increase the number of machines in the TiKV cluster.
### Method 5: Adjust `raft-base-tick-interval`

In addition to reducing the number of Regions, you can also reduce pressure on Raftstore by reducing the number of messages for each Region within a unit of time. For example, you can properly increase the value of the `raft-base-tick-interval` configuration item:

```
[raftstore]
raft-base-tick-interval = "2s"
```

In the above configuration, `raft-base-tick-interval` is the time interval at which Raftstore drives the Raft state machine of each Region, which means at this time interval, Raftstore sends a tick message to the Raft state machine. Increasing this interval can effectively reduce the number of messages from Raftstore.

Note that this interval between tick messages also determines the intervals between `election timeout` and `heartbeat`. See the following example:

```
raft-election-timeout = raft-base-tick-interval * raft-election-timeout-ticks
raft-heartbeat-interval = raft-base-tick-interval * raft-heartbeat-ticks
```

If Region followers have not received the heartbeat from the leader within the `raft-election-timeout` interval, these followers determine that the leader has failed and start a new election. `raft-heartbeat-interval` is the interval at which a leader sends a heartbeat to followers. Therefore, increasing the value of `raft-base-tick-interval` can reduce the number of network messages sent from Raft state machines but also makes it longer for Raft state machines to detect the leader failure.
### Method 6: Adjust Region size

The default size of a Region is 96 MiB, and you can reduce the number of Regions by setting Regions to a larger size. For more information, see [Tune Region Performance](https://docs.pingcap.com/tidb/stable/tune-region-performance).

> **Note:**
>
> Customized Region size is an experimental feature before TiDB v6.5.0. If you need to resize the Region size, it is recommended that you upgrade to v6.5.0 or a later version.
### Method 7: Increase the maximum number of connections for Raft communication

By default, the maximum number of connections used for Raft communication between TiKV nodes is 1. Increasing this number can help alleviate blockage issues caused by heavy communication workloads of a large number of Regions. For detailed instructions, see [`grpc-raft-conn-num`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#grpc-raft-conn-num).

> **Note:**
>
> To reduce unnecessary thread switching overhead and mitigate potential negative impacts from batch processing, it is recommended to set the number within the range of `[1, 4]`.
