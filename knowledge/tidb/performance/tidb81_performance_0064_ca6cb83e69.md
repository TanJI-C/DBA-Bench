# Three-node hybrid deployment overview and TiKV thread pool tuning

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/three-nodes-hybrid-deployment.md`
- Source Title: `Best Practices for Three-Node Hybrid Deployment`
- Source Heading Path: `Best Practices for Three-Node Hybrid Deployment | Best Practices for Three-Node Hybrid Deployment > Prerequisites for deployment and the test method | Best Practices for Three-Node Hybrid Deployment > Parameter adjustment | Best Practices for Three-Node Hybrid Deployment > Parameter adjustment > Configuration of TiKV thread pool size | Best Practices for Three-Node Hybrid Deployment > Parameter adjustment > Configuration of TiKV thread pool size > `readpool.unified.max-thread-count` | Best Practices for Three-Node Hybrid Deployment > Parameter adjustment > Configuration of TiKV thread pool size > `server.grpc-concurrency` | Best Practices for Three-Node Hybrid Deployment > Parameter adjustment > Configuration of TiKV thread pool size > `storage.scheduler-worker-pool-size``
- Source Line Ranges: `5-77`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`, `pd`, `tiup`, `shared`
- Topic Tags: `hybrid deployment`, `tpcc`, `thread pools`, `resource limits`, `qps jitter`, `grpc concurrency`, `scheduler workers`, `read pool`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0064_ca6cb83e69`
- Source ID: `tidb-docs-8.1:best-practices/three-nodes-hybrid-deployment.md#best-practices-for-three-node-hybrid-deployment`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `01eb7505034a93e592dc75656433705de5e73250eb2849b17103bf6dbf23668e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/three-nodes-hybrid-deployment#best-practices-for-three-node-hybrid-deployment
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/three-nodes-hybrid-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when looking for best practices to reduce QPS jitter in a three-node hybrid deployment by tuning TiKV foreground thread pool parameters under shared resource limits.
- Retrieval Keywords: three-node hybrid deployment, QPS jitter, TPC-C 5000 Warehouse, TiUP bench, readpool.unified.max-thread-count, server.grpc-concurrency, storage.scheduler-worker-pool-size, gRPC poll CPU, Scheduler worker CPU, hybrid deployment scenario, TiKV thread pool size, performance stability
- Follow-up Guidance: The source also provides a final test configuration including `gc.max-write-bytes-per-sec`, `rocksdb.max-background-jobs`, `rocksdb.max-sub-compactions`, `rocksdb.rate-bytes-per-sec`, and TiDB `performance.max-procs`.
- Classification Note: This chunk is classified as performance for TiKV because it explains how TiKV thread pool settings affect resource consumption, performance jitter, and stability in a self-managed hybrid deployment.

## Official Source Content

# Best Practices for Three-Node Hybrid Deployment

For a TiDB cluster, if you have no requirements on high performance but need to control the cost, you can deploy the TiDB, TiKV, and PD components on three machines in a hybrid way.

This document offers an example of three-node hybrid deployment and a TPC-C test against the deployed cluster. Based on this example, this document offers best practices for the deployment scenario and its parameter adjustment.
## Prerequisites for deployment and the test method

In this example, three physical machines are used for deployment, each with 16 CPU cores and 32 GB of memory. On each machine (node), one TiDB instance, one TiKV instance, and one PD instance are deployed in a hybrid way.

Because PD and TiKV both store information on the disk, the read and write latency of disk directly affects the latency of the PD and TiKV services. To avoid the situation that PD and TiKV compete for disk resources and affect each other, it is recommended to use different disks for PD and TiKV.

In this example, the TPC-C 5000 Warehouse data is used in TiUP bench and the test lasts 12 hours with the `terminals` parameter set to `128` (concurrency). Close attention is paid to metrics related to performance stability of the cluster.

The image below shows the QPS monitor of the cluster within 12 hours with the default parameter configuration. From the image, you can see an obvious performance jitter.

![QPS with default config](/media/best-practices/three-nodes-default-config-qps.png)

After the parameter adjustment, the performance is improved.

![QPS with modified config](/media/best-practices/three-nodes-final-config-qps.png)
## Parameter adjustment

Performance jitter occurs in the image above, because the default thread pool configuration and the resource allocation to background tasks are for machines with sufficient resources. In the hybrid deployment scenario, the resources are shared among multiple components, so you need to limit the resource consumption via configuration parameters.

The final cluster configuration for this test is as follows:

```yaml
tikv:
    readpool.unified.max-thread-count: 6
    server.grpc-concurrency: 2
    storage.scheduler-worker-pool-size: 2
    gc.max-write-bytes-per-sec: 300K
    rocksdb.max-background-jobs: 3
    rocksdb.max-sub-compactions: 1
    rocksdb.rate-bytes-per-sec: "200M"

  tidb:
    performance.max-procs: 8
```

The following sections introduce the meanings and the adjustment methods of these parameters.
### Configuration of TiKV thread pool size

This section offers best practices for adjusting parameters that relate to the resource allocation of thread pools for foreground applications. Reducing these thread pool sizes will compromise performance, but in the hybrid deployment scenario with limited resources, the cluster itself is hard to achieve high performance. In this scenario, the overall stability of the cluster is preferred over performance.

If you conduct an actual load test, you can first use the default configuration and observe the actual resource usage of each thread pool. Then you can adjust the corresponding configuration items and reduce the sizes of the thread pools that have lower usage.
#### `readpool.unified.max-thread-count`

The default value of this parameter is 80% of the number of machine threads. In a hybrid deployment scenario, you need to manually calculate and specify this value. You can first set it to 80% of the expected number of CPU threads used by TiKV.
#### `server.grpc-concurrency`

This parameter defaults to `4`. Because in the existing deployment plan, the CPU resources are limited and the actual requests are few. You can observe the monitoring panel, lower the value of this parameter, and keep the usage rate below 80%.

In this test, the value of this parameter is set to `2`. Observe the **gRPC poll CPU** panel and you can see that the usage rate is just around 80%.

![gRPC Pool CPU](/media/best-practices/three-nodes-grpc-pool-usage.png)
#### `storage.scheduler-worker-pool-size`

When TiKV detects that the CPU core number of the machine is greater than or equal to `16`, this parameter value defaults to `8`. When the CPU core number is smaller than `16`, the parameter value defaults to `4`. This parameter is used when TiKV converts complex transaction requests to simple key-value reads or writes, but the scheduler thread pool does not perform any writes.

Ideally, the usage rate of the scheduler thread pool is kept between 50% and 75%. Similar to the gRPC thread pool, the `storage.scheduler-worker-pool-size` parameter defaults to a larger value during the hybrid deployment, which makes resource usage insufficient. In this test, the value of this parameter is set to `2`, which is in line with the best practices, a conclusion drawn by observing the corresponding metrics in the **Scheduler worker CPU** panel.

![Scheduler Worker CPU](/media/best-practices/three-nodes-scheduler-pool-usage.png)
