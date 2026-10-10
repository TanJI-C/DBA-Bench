# TiKV background task limits and TiDB CPU usage tuning

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/three-nodes-hybrid-deployment.md`
- Source Title: `Best Practices for Three-Node Hybrid Deployment`
- Source Heading Path: `Best Practices for Three-Node Hybrid Deployment > Parameter adjustment > Resource configuration for TiKV background tasks | Best Practices for Three-Node Hybrid Deployment > Parameter adjustment > Resource configuration for TiKV background tasks > `rocksdb.max-background-jobs` and `rocksdb.max-sub-compactions` | Best Practices for Three-Node Hybrid Deployment > Parameter adjustment > Resource configuration for TiKV background tasks > `rocksdb.rate-bytes-per-sec` | Best Practices for Three-Node Hybrid Deployment > Parameter adjustment > Resource configuration for TiKV background tasks > `gc.max_write_bytes_per_sec` | Best Practices for Three-Node Hybrid Deployment > Parameter adjustment > TiDB parameter adjustment | Best Practices for Three-Node Hybrid Deployment > Parameter adjustment > TiDB parameter adjustment > `performance.max-procs``
- Source Line Ranges: `78-129`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`, `shared`, `tiup`
- Topic Tags: `background tasks`, `rocksdb compaction`, `write stall`, `disk bandwidth`, `gc traffic`, `mvcc`, `operator concurrency`, `max procs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0065_1968c90e5c`
- Source ID: `tidb-docs-8.1:best-practices/three-nodes-hybrid-deployment.md#resource-configuration-for-tikv-background-tasks`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `89ebd26efa4dc39a61d73a87eb39098e7762b921526d8f3779dba30b1458d9e0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/three-nodes-hybrid-deployment#resource-configuration-for-tikv-background-tasks
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/three-nodes-hybrid-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when looking for guidance on limiting TiKV background task resource usage and understanding TiDB `performance.max-procs` in a three-node hybrid deployment.
- Retrieval Keywords: rocksdb.max-background-jobs, rocksdb.max-sub-compactions, rocksdb.rate-bytes-per-sec, gc.max_write_bytes_per_sec, performance.max-procs, write stall, background compaction jobs, MVCC, tikv-ctl, modify-tikv-config, tidb_hash_join_concurrency, tidb_index_lookup_join_concurrency, GC Impact
- Follow-up Guidance: The source includes a `tiup ctl:v<CLUSTER_VERSION> tikv --host=${ip:port} modify-tikv-config -n gc.max_write_bytes_per_sec -v ${limit}` example and notes that limiting GC traffic can cause MVCC versions to pile up and affect read performance in application scenarios with frequent updates.
- Classification Note: This chunk is classified as performance for TiKV because it covers resource limits for TiKV background jobs and GC traffic, while also noting TiDB CPU usage control through `performance.max-procs`.

## Official Source Content

### Resource configuration for TiKV background tasks

In addition to foreground tasks, TiKV regularly sorts data and cleans outdated data in background tasks. The default configuration allocates sufficient resources to these tasks for the scenario of high-traffic writes.

However, in the hybrid deployment scenario, this default configuration is not in line with the best practices. You need to limit the resource usage of background tasks by adjusting the following parameters.
#### `rocksdb.max-background-jobs` and `rocksdb.max-sub-compactions`

The RocksDB thread pool is used to perform compaction and flush jobs. The default value of `rocksdb.max-background-jobs` is `8`, which obviously exceeds the resource that is in need. Therefore, the value should be adjusted to limit the resource usage.

`rocksdb.max-sub-compactions` indicates the number of concurrent sub-tasks allowed for a single compaction job, which defaults to `3`. You can lower this value when the write traffic is not high.

In the test, the `rocksdb.max-background-jobs` value is set to `3` and the `rocksdb.max-sub-compactions` value is set to `1`. No write stall occurs during the 12-hour test with the TPC-C load. When optimizing the two parameter values according to the actual load, you can lower the values gradually based on monitoring metrics:

* If write stall occurs, increase the value of `rocksdb.max-background-jobs`.
* If the write stall persists, set the value of `rocksdb.max-sub-compactions` to `2` or `3`.
#### `rocksdb.rate-bytes-per-sec`

This parameter is used to limit the disk traffic for the background compaction jobs. The default configuration has no limit for this parameter. To avoid the situation that compaction jobs occupy the resources of foreground services, you can adjust this parameter value according to the sequential read and write speed of the disk, which reserves enough disk bandwidth for foreground services.

The method of optimizing the RocksDB thread pool is similar to that of optimizing the compaction thread pool. You can determine whether the value you have adjusted is suitable according to whether write stall occurs.
#### `gc.max_write_bytes_per_sec`

Because TiDB uses the multi-version concurrency control (MVCC) model, TiKV periodically cleans old version data in the background. When the available resources are limited, this operation causes periodical performance jitter. You can use the `gc.max_write_bytes_per_sec` parameter to limit the resource usage of such an operation.

![GC Impact](/media/best-practices/three-nodes-gc-impact.png)

In addition to setting this parameter value in the configuration file, you can also dynamically adjust this value in tikv-ctl.

```shell
tiup ctl:v<CLUSTER_VERSION> tikv --host=${ip:port} modify-tikv-config -n gc.max_write_bytes_per_sec -v ${limit}
```

> **Note:**
>
> In application scenarios with frequent updates, limiting GC traffic might cause the MVCC versions to pile up and affect read performance. Currently, to achieve a balance between performance jitter and performance decrease, you might need to try multiple times to adjust the value of this parameter.
### TiDB parameter adjustment

Generally, you can adjust the TiDB parameters of execution operators using system variables such as `tidb_hash_join_concurrency` and `tidb_index_lookup_join_concurrency`.

In this test, these parameters are not adjusted. In the load test of your actual application, if the execution operators consume an excessive amount of CPU resources, you can limit the resource usage of specific operators according to your application scenario. For more details, see [TiDB system variables](https://docs.pingcap.com/tidb/stable/system-variables).
#### `performance.max-procs`

This parameter is used to control how many CPU cores an entire Go process can use. By default, the value is equal to the number of CPU cores of the current machine or cgroups.

When Go is running, a proportion of threads is used for background tasks such as GC. If you do not limit the value of the `performance.max-procs` parameter, these background tasks will consume too much CPU.
