# Snapshot backup and restore performance impact

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-snapshot-guide.md`
- Source Title: `Snapshot Backup and Restore Guide`
- Source Heading Path: `Snapshot Backup and Restore Guide > Performance and impact | Snapshot Backup and Restore Guide > Performance and impact > Performance and impact of snapshot backup | Snapshot Backup and Restore Guide > Performance and impact > Performance and impact of snapshot restore`
- Source Line Ranges: `182-224`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`, `tidb`, `pd`, `shared`
- Topic Tags: `backup-performance`, `restore-performance`, `throughput`, `latency`, `qps`, `ratelimit`, `concurrency`, `region-scattering`, `resource-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0071_009c95783d`
- Source ID: `tidb-docs-8.1:br/br-snapshot-guide.md#performance-and-impact`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bbc9178358bb4a61bf839f71cf0195fcc798f26c93708813f999df2d17fc12d2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#performance-and-impact
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-snapshot-guide.md

## Retrieval Guidance

- Use When: Use this when you want the documented performance impact, tuning knobs, or restore concurrency details for BR snapshot backup and restore.
- Retrieval Keywords: Performance and impact, snapshot backup, snapshot restore, backup.num-threads, --ratelimit, concurrency, backup data size(after compressed), --granularity="coarse-grained", --tikv-max-restore-concurrency, TiKV-Details > Backup & Import > Import RPC count, job queue, restore full
- Follow-up Guidance: The guide says snapshot restore performance varies by environment and includes a `tiup br restore full` example with `--granularity "coarse-grained"`.
- Classification Note: This chunk is a performance reference for BR snapshot backup and restore, describing impact, tuning parameters, and restore-side concurrency control.

## Official Source Content

## Performance and impact
### Performance and impact of snapshot backup

The backup feature has some impact on cluster performance (transaction latency and QPS). However, you can mitigate the impact by adjusting the number of backup threads [`backup.num-threads`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#num-threads-1) or by adding more clusters.

To illustrate the impact of backup, this document lists the test conclusions of several snapshot backup tests:

- (5.3.0 and earlier) When the backup threads of BR on a TiKV node take up 75% of the total CPU of the node, the QPS is reduced by 35% of the original QPS.
- (5.4.0 and later) When there are no more than `8` threads of BR on a TiKV node and the cluster's total CPU utilization does not exceed 80%, the impact of BR tasks on the cluster (write and read) is 20% at most.
- (5.4.0 and later) When there are no more than `8` threads of BR on a TiKV node and the cluster's total CPU utilization does not exceed 75%, the impact of BR tasks on the cluster (write and read) is 10% at most.
- (5.4.0 and later) When there are no more than `8` threads of BR on a TiKV node and the cluster's total CPU utilization does not exceed 60%, BR tasks have little impact on the cluster (write and read).

You can use the following methods to manually control the impact of backup tasks on cluster performance. However, these two methods also reduce the speed of backup tasks while reducing the impact of backup tasks on the cluster.

- Use the `--ratelimit` parameter to limit the speed of backup tasks. Note that this parameter limits the speed of **saving backup files to external storage**. When calculating the total size of backup files, use the `backup data size(after compressed)` as a benchmark. When `--ratelimit` is set, to avoid too many tasks causing the speed limit to fail, the `concurrency` parameter of br is automatically adjusted to `1`.
- Adjust the TiKV configuration item [`backup.num-threads`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#num-threads-1) to limit the number of threads used by backup tasks. According to internal tests, when BR uses no more than `8` threads for backup tasks, and the total CPU utilization of the cluster does not exceed 60%, the backup tasks have little impact on the cluster, regardless of the read and write workload.

The impact of backup on cluster performance can be reduced by limiting the backup threads number, but this affects the backup performance. The preceding tests show that the backup speed is proportional to the number of backup threads. When the number of threads is small, the backup speed is about 20 MiB/thread. For example, 5 backup threads on a single TiKV node can reach a backup speed of 100 MiB/s.
### Performance and impact of snapshot restore

- During data restore, TiDB tries to fully utilize the TiKV CPU, disk IO, and network bandwidth resources. Therefore, it is recommended to restore the backup data on an empty cluster to avoid affecting the running applications.
- The speed of restoring backup data is much related with the cluster configuration, deployment, and running applications. The performance and impact of snapshot restore are varied in different user scenarios and should be tested in actual environments.
- BR provides a coarse-grained Region scattering algorithm to accelerate Region restore in large-scale Region scenarios. The algorithm is controlled by the command-line parameter `--granularity="coarse-grained"` and is enabled by default. This algorithm ensures that each TiKV node receives stable and evenly distributed download tasks, thus fully utilizing the resources of each TiKV node and achieving a rapid parallel recovery. In several real-world cases, the snapshot restore speed of the cluster is improved by about 3 times in large-scale Region scenarios. The following is an example:

    ```bash
    tiup br restore full \
    --pd "${PDIP}:2379" \
    --storage "s3://${Bucket}/${Folder}" \
    --s3.region "${region}" \
    --granularity "coarse-grained" \
    --send-credentials-to-tikv=true \
    --log-file restorefull.log
    ```

- Starting from v8.0.0, the `br` command-line tool introduces the `--tikv-max-restore-concurrency` parameter to control the maximum number of files that BR downloads and ingests per TiKV node. By configuring this parameter, you can also control the maximum length of the job queue (the maximum length of the job queue = 32 \* the number of TiKV nodes \* `--tikv-max-restore-concurrency`), thereby controlling the memory consumption of the BR node.

    In normal cases, `--tikv-max-restore-concurrency` is automatically adjusted based on the cluster configuration, so manual configuration is unnecessary. If the **TiKV-Details** > **Backup & Import** > **Import RPC count** monitoring metric in Grafana shows that the number of files BR downloads remains close to 0 for a long time while the number of files that BR ingests consistently reaches the upper limit, it indicates that ingesting file tasks pile up and the job queue has reached its maximum length. In this case, you can take the following measures to alleviate the task pilling-up issue:

    - Set the `--ratelimit` parameter to limit the download speed, ensuring sufficient resources for ingesting file tasks. For example, if the disk throughput of any TiKV node is `x MiB/s` and the network bandwidth for downloading backup files exceeds `x/2 MiB/s`, you can set the parameter as `--ratelimit x/2`. If the disk throughput of any TiKV node is `x MiB/s` and the network bandwidth for downloading backup files is less than or equal to `x/2 MiB/s`, you can leave the parameter `--ratelimit` unset.
    - Increase the `--tikv-max-restore-concurrency` to increase the maximum length of the job queue.
