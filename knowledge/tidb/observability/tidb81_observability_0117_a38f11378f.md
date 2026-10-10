# TiFlash Raft replication and IO throughput metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash-performance-tuning-methods.md`
- Source Title: `TiFlash Performance Analysis and Tuning Methods`
- Source Heading Path: `TiFlash Performance Analysis and Tuning Methods > Key metrics for TiFlash performance > Raft-related metrics | TiFlash Performance Analysis and Tuning Methods > Key metrics for TiFlash performance > IO throughput metrics`
- Source Line Ranges: `68-113`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tikv`, `dashboard`
- Topic Tags: `raft`, `replication latency`, `read index`, `wait index`, `io throughput`, `write amplification`, `deltatree`, `pagestore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0117_a38f11378f`
- Source ID: `tidb-docs-8.1:tiflash-performance-tuning-methods.md#raft-related-metrics`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `40fc2194e23890c750c3ccbbdf3afcab4a788171125dfef4c6b4c3ec5b2a42b1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash-performance-tuning-methods#raft-related-metrics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash-performance-tuning-methods.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiFlash Raft replication latency and IO throughput metrics, including `wait_index`, `read_index`, stable layer and Pagestore traffic, or the write amplification factor formula.
- Retrieval Keywords: Raft Wait Index Duration, wait_index, read_index, Raft Batch Read Index Duration, Write Throughput By Instance, Write flow, Read flow, File Descriptor, Page, Pagestore, DeltaTree, write amplification factor, (Read flow + Write flow) ÷ total Write Throughput By Instance, network bottleneck between TiKV and TiFlash, TiKV resource is overloaded, TiFlash resource is overloaded
- Follow-up Guidance: The source explains that high `Raft Wait Index Duration` or `Raft Batch Read Index Duration` can indicate overloaded TiKV or TiFlash resources or a network bottleneck between TiKV and TiFlash.
- Classification Note: This is classified as observability because the content provides TiFlash Raft replication and disk IO metrics used to assess replication latency and throughput behavior.

## Official Source Content

### Raft-related metrics

With the following metrics, you can get the Raft replication status of TiFlash:

- Raft Wait Index Duration: the duration of waiting until the local Region index >= `read_index` for all TiFlash instances, which represents the latency of the `wait_index` operation. If this metric is too high, it indicates that data replication from TiKV to TiFlash has a significant latency. Possible reasons include the following:

    - TiKV resource is overloaded.
    - TiFlash resource is overloaded, especially IO resources.
    - There is a network bottleneck between TiKV and TiFlash.

- Raft Batch Read Index Duration: the latency of `read_index` for all TiFlash instances. If this metric is too high, it indicates that the interaction between TiFlash and TiKV is slow. Possible reasons include the following:

    - TiFlash resource is overloaded.
    - TiKV resource is overloaded.
    - There is a network bottleneck between TiFlash and TiKV.
### IO throughput metrics

With the following metrics, you can get the IO throughput of TiFlash:

- Write Throughput By Instance: the throughput of data written by each TiFlash instance. It includes the throughput by applying the Raft data logs and Raft snapshots.
- Write flow: the traffic of disk writes by all TiFlash instances.

    - File Descriptor: the stable layer of the DeltaTree storage engine used by TiFlash.
    - Page: refers to Pagestore, the Delta change layer of the DeltaTree storage engine used by TiFlash.

- Read flow: traffic of disk read operations for all TiFlash instances.

    - File Descriptor: the stable layer of the DeltaTree storage engine used by TiFlash.
    - Page: refers to Pagestore, the Delta change layer of the DeltaTree storage engine used by TiFlash.

You can calculate the write amplification factor of the entire TiFlash cluster using the `(Read flow + Write flow) ÷ total Write Throughput By Instance` formula.

Example 1: Raft and IO metrics of the [CH-benCHmark workload](https://docs.pingcap.com/tidb/stable/benchmark/benchmark-tidb-using-ch) in a self-hosted environment

As shown in the following diagram, the `Raft Wait Index Duration` and the 99th percentile of `Raft Batch Read Index Duration` for this TiFlash cluster are relatively high, at 3.24 seconds and 753 milliseconds respectively. This is because the TiFlash workload in this cluster is high and latency occurs in data replication.

In this cluster, there are two TiFlash nodes. The incremental data replication speed from TiKV to TiFlash is approximately 28 MB per second. The maximum write throughput of the stable layer (File Descriptor) is 939 MB/s, and the maximum read throughput is 1.1 GiB/s. Meanwhile, the maximum write throughput of the Delta layer (Page) is 74 MB/s, and the maximum read throughput is 111 MB/s. In this environment, TiFlash uses dedicated NVME disks, which have strong IO throughput capabilities.

![CH-2TiFlash-OP](/media/performance/tiflash/ch-2tiflash-raft-io-flow.png)

Example 2: Raft and IO metrics of the [CH-benCHmark workload](https://docs.pingcap.com/tidb/stable/benchmark/benchmark-tidb-using-ch) in a public cloud deployment environment

As shown in the following diagram, the 99th percentile of `Raft Wait Index Duration` is up to 438 milliseconds, and 99th percentile of the `Raft Batch Read Index Duration` is up to 125 milliseconds. This cluster has only one TiFlash node. TiKV replicates about 5 MB of incremental data to TiFlash per second. The maximum write traffic of the stable layer (File Descriptor) is 78 MB/s and the maximum read traffic is 221 MB/s. In the meantime, the maximum write traffic of the Delta layer (Page) is 8 MB/s and the maximum read traffic is 18 MB/s. In this environment, TiFlash uses an AWS EBS cloud disk, which has relatively weak IO throughput.

![CH-TiFlash-MPP](/media/performance/tiflash/ch-1tiflash-raft-io-flow-cloud.png)
