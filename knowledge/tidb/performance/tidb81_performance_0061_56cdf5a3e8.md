# Raftstore workflow, bottlenecks, and monitoring for massive Regions

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/massive-regions-best-practices.md`
- Source Title: `Best Practices for TiKV Performance Tuning with Massive Regions`
- Source Heading Path: `Best Practices for TiKV Performance Tuning with Massive Regions | Best Practices for TiKV Performance Tuning with Massive Regions > Raftstore workflow | Best Practices for TiKV Performance Tuning with Massive Regions > Performance problem | Best Practices for TiKV Performance Tuning with Massive Regions > Performance problem > Performance monitoring | Best Practices for TiKV Performance Tuning with Massive Regions > Performance tuning methods`
- Source Line Ranges: `5-71`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`, `dashboard`
- Topic Tags: `raftstore`, `regions`, `cpu`, `latency`, `monitoring`, `grafana`, `propose-wait`, `commit-log`, `workload`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0061_56cdf5a3e8`
- Source ID: `tidb-docs-8.1:best-practices/massive-regions-best-practices.md#best-practices-for-tikv-performance-tuning-with-massive-regions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `85ad0b9cadcd31b730a249821d8af4c8379a1474f843df28582122a0b66414f8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/massive-regions-best-practices#best-practices-for-tikv-performance-tuning-with-massive-regions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/massive-regions-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing TiKV performance bottlenecks caused by massive Regions and checking Raftstore workflow, CPU saturation, request delay, and related Grafana metrics.
- Retrieval Keywords: Raftstore workflow, massive Regions, Raft store CPU, Thread-CPU, Propose wait duration, Raft Propose, Commit log duration, Raft IO, raftstore.store-pool-size, propose wait duration hundreds of milliseconds, single-threaded Raftstore, reduce the number of Regions on a single TiKV instance, reduce the number of messages for a single Region
- Follow-up Guidance: The source follows this diagnosis section with tuning directions to reduce the number of Regions on a single TiKV instance and reduce the number of messages for a single Region.
- Classification Note: This chunk is classified as performance because it explains how massive Regions make Raftstore a bottleneck and maps the issue to CPU, latency, and monitoring indicators in TiKV Dashboard.

## Official Source Content

# Best Practices for TiKV Performance Tuning with Massive Regions

In TiDB, data is split into Regions, each storing data for a specific key range. These Regions are distributed among multiple TiKV instances. As data is written into a cluster, millions of Regions might be created. Too many Regions on a single TiKV instance can bring a heavy burden to the cluster and affect its performance.

This document introduces the workflow of Raftstore (a core module of TiKV), explains why a massive amount of Regions affect the performance, and offers methods for tuning TiKV performance.
## Raftstore workflow

A TiKV instance has multiple Regions on it. The Raftstore module drives the Raft state machine to process Region messages. These messages include processing read or write requests on Regions, persisting or replicating Raft logs, and processing Raft heartbeats. However, an increasing number of Regions can affect performance of the whole cluster. To understand this, it is necessary to learn the workflow of Raftstore shown as follows:

![Raftstore Workflow](/media/best-practices/raft-process.png)

> **Note:**
>
> This diagram only illustrates the workflow of Raftstore and does not represent the actual code structure.

From the above diagram, you can see that requests from the TiDB servers, after passing through the gRPC and storage modules, become read and write messages of KV (key-value), and are sent to the corresponding Regions. These messages are not immediately processed but are temporarily stored. Raftstore polls to check whether each Region has messages to process. If a Region has messages to process, Raftstore drives the Raft state machine of this Region to process these messages and perform subsequent operations according to the state changes of these messages. For example, when write requests come in, the Raft state machine stores logs into disk and sends logs to other Region replicas; when the heartbeat interval is reached, the Raft state machine sends heartbeat information to other Region replicas.
## Performance problem

From the Raftstore workflow diagram, messages in each Region are processed one by one. When a large number of Regions exist, it takes Raftstore some time to process the heartbeats of these Regions, which can cause some delay. As a result, some read and write requests are not processed in time. If read and write pressure is high, the CPU usage of the Raftstore thread might easily become the bottleneck, which further increases the delay and affects the performance.

Generally, if the CPU usage of the loaded Raftstore reaches 85% or higher, Raftstore goes into a busy state and becomes the bottleneck. At the same time, `propose wait duration` can be as high as hundreds of milliseconds.

> **Note:**
>
> + For the CPU usage of Raftstore as mentioned above, Raftstore is single-threaded. If Raftstore is multi-threaded, you can increase the CPU usage threshold (85%) proportionally.
> + Because I/O operations exist in the Raftstore thread, CPU usage cannot reach 100%.
### Performance monitoring

You can check the following monitoring metrics in Grafana's **TiKV Dashboard**:

+ `Raft store CPU` in the **Thread-CPU** panel

    Reference value: lower than `raftstore.store-pool-size * 85%`.

    ![Check Raftstore CPU](/media/best-practices/raft-store-cpu.png)

+ `Propose wait duration` in the **Raft Propose** panel

    `Propose wait duration` is the delay between the time a request is sent to Raftstore and the time Raftstore actually starts processing the request. Long delay means that Raftstore is busy, or that processing the append log is time-consuming, making Raftstore unable to process the request in time.

    Reference value: lower than 50~100 ms according to the cluster size

    ![Check Propose wait duration](/media/best-practices/propose-wait-duration.png)

+ `Commit log duration` in the **Raft IO** panel

    `Commit log duration` is the time Raftstore takes to commit Raft logs to the majority of members in the respective Region. The possible reasons for a high value of this metric with significant fluctuations include the following:

    - The workload on Raftstore is heavy.
    - The append log operation is slow.
    - Raft logs cannot be committed timely due to network congestion.

  Reference value: lower than 200-500 ms.

    ![Check Commit log duration](/media/best-practices/commit-log-duration.png)
## Performance tuning methods

After finding out the cause of a performance problem, try to solve it from the following two aspects:

+ Reduce the number of Regions on a single TiKV instance
+ Reduce the number of messages for a single Region
