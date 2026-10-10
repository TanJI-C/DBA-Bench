# TiKV and TiFlash learner performance configuration settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-performance-tuning-config.md`
- Source Title: `Configure TiDB for Optimal Performance`
- Source Heading Path: `Configure TiDB for Optimal Performance > Key settings for common workloads > TiKV configurations | Configure TiDB for Optimal Performance > Key settings for common workloads > TiKV configurations > Recommended configuration adjustments for write-intensive workloads | Configure TiDB for Optimal Performance > Key settings for common workloads > TiFlash-learner configurations`
- Source Line Ranges: `83-161`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tiflash`
- Topic Tags: `tikv configuration`, `tiflash learner`, `snapshot transfer`, `flow control`, `compaction`, `titan`, `write-intensive workloads`, `disk throughput`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0346_90a13be577`
- Source ID: `tidb-docs-8.1:tidb-performance-tuning-config.md#tikv-configurations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `633613e2755b67a15dba6a442f308def8d70aab073ec852f7f2d1134a7e502bc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-performance-tuning-config#tikv-configurations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-performance-tuning-config.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiKV or TiFlash-learner configuration guidance for write-intensive workloads, snapshot transfer bandwidth, flow control, compaction thresholds, Titan settings, or ServerIsBusy behavior.
- Retrieval Keywords: concurrent-send-snap-limit, concurrent-recv-snap-limit, snap-io-max-bytes-per-sec, rocksdb.max-manifest-file-size, rocksdb.titan, rocksdb.defaultcf.titan, min-blob-size, blob-file-compression, storage.scheduler-pending-write-threshold, Server Is Busy, ServerIsBusy, storage.flow-control.l0-files-threshold, storage.flow-control.soft-pending-compaction-bytes-limit, storage.flow-control.hard-pending-compaction-bytes-limit, rocksdb.writecf.level0-slowdown-writes-trigger, rocksdb.defaultcf.level0-slowdown-writes-trigger, rocksdb.lockcf.level0-slowdown-writes-trigger, rocksdb.writecf.soft-pending-compaction-bytes-limit, rocksdb.defaultcf.soft-pending-compaction-bytes-limit, rocksdb.lockcf.soft-pending-compaction-bytes-limit, rocksdb.rate-bytes-per-sec, TiFlash-learner, snapshot transfer, pending compaction bytes, write flow control, disk throughput 1 GiB/s
- Follow-up Guidance: The chunk also includes hardware-specific notes for TiKV instances with 32 CPU cores, 128 GiB memory, 5 TiB EBS, and 1 GiB/s disk throughput, plus a TiFlash-learner setting for snap-io-max-bytes-per-sec.
- Classification Note: This is classified as configuration because the content is a set of TiKV and TiFlash-learner configuration items, values, descriptions, and notes for performance tuning.

## Official Source Content

### TiKV configurations

Add the following configuration items to the TiKV configuration file:

```toml
[server]
concurrent-send-snap-limit = 64
concurrent-recv-snap-limit = 64
snap-io-max-bytes-per-sec = "400MiB"

[rocksdb]
max-manifest-file-size = "256MiB"
[rocksdb.titan]
enabled = true
[rocksdb.defaultcf.titan]
min-blob-size = "1KB"
blob-file-compression = "zstd"

[storage]
scheduler-pending-write-threshold = "512MiB"
[storage.flow-control]
l0-files-threshold = 50
soft-pending-compaction-bytes-limit = "512GiB"

[rocksdb.writecf]
level0-slowdown-writes-trigger = 20
soft-pending-compaction-bytes-limit = "192GiB"
[rocksdb.defaultcf]
level0-slowdown-writes-trigger = 20
soft-pending-compaction-bytes-limit = "192GiB"
[rocksdb.lockcf]
level0-slowdown-writes-trigger = 20
soft-pending-compaction-bytes-limit = "192GiB"
```

| Configuration item | Description | Note |
| ---------| ---- | ----|
| [`concurrent-send-snap-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#concurrent-send-snap-limit), [`concurrent-recv-snap-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#concurrent-recv-snap-limit), and [`snap-io-max-bytes-per-sec`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#snap-io-max-bytes-per-sec) | Set limits for concurrent snapshot transfer and I/O bandwidth during TiKV scaling operations. Higher limits reduce scaling time by allowing faster data migration. | Adjusting these limits affects the trade-off between scaling speed and online transaction performance. |
| [`rocksdb.max-manifest-file-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#max-manifest-file-size) | Set the maximum size of the RocksDB Manifest file, which logs the metadata about SST files and database state changes. Increasing this size reduces the frequency of Manifest file rewrites, thereby minimizing their impact on foreground write performance. | The default value is `128MiB`. In environments with a large number of SST files (for example, hundreds of thousands), frequent Manifest rewrites can degrade write performance. Adjusting this parameter to a higher value, such as `256MiB` or larger, can help maintain optimal performance. |
| [`rocksdb.titan`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#rocksdbtitan), [`rocksdb.defaultcf.titan`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#rocksdbdefaultcftitan), [`min-blob-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#min-blob-size), and [`blob-file-compression`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#blob-file-compression) | Enable the Titan storage engine to reduce write amplification and alleviate disk I/O bottlenecks. Particularly useful when RocksDB compaction cannot keep up with write workloads, resulting in accumulated pending compaction bytes. | Enable it when write amplification is the primary bottleneck. Trade-offs include: <ul><li>Potential performance impact on primary key range scans. </li><li>Increased space amplification (up to 2x in the worst case). </li><li>Additional memory usage for blob cache. </li></ul>|
| [`storage.scheduler-pending-write-threshold`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#scheduler-pending-write-threshold) | Set the maximum size of the write queue in the TiKV scheduler. When the total size of pending write tasks exceeds this threshold, TiKV returns a `Server Is Busy` error for new write requests. | The default value is `100MiB`. In scenarios with high write concurrency or temporary write spikes, increasing this threshold (for example, to `512MiB`) can help accommodate the load. However, if the write queue continues to accumulate and exceeds this threshold persistently, it might indicate underlying performance issues that require further investigation. |
| [`storage.flow-control.l0-files-threshold`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#l0-files-threshold) | Control when write flow control is triggered based on the number of kvDB L0 files. Increasing the threshold reduces write stalls during high write workloads. | Higher thresholds might lead to more aggressive compactions when many L0 files exist. |
| [`storage.flow-control.soft-pending-compaction-bytes-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#soft-pending-compaction-bytes-limit) | Control the threshold for pending compaction bytes to manage write flow control. The soft limit triggers partial write rejections. | The default soft limit is `192GiB`. In write-intensive scenarios, if compaction processes cannot keep up, pending compaction bytes accumulate, potentially triggering flow control. Adjusting the limit can provide more buffer space, but persistent accumulation indicates underlying issues that require further investigation. |
| [`rocksdb.(defaultcf\|writecf\|lockcf).level0-slowdown-writes-trigger`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#level0-slowdown-writes-trigger) [`rocksdb.(defaultcf\|writecf\|lockcf).soft-pending-compaction-bytes-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#level0-slowdown-writes-trigger) | You need to manually set `level0-slowdown-writes-trigger` and `soft-pending-compaction-bytes-limit` back to their default values. This way they will not be affected by flow control parameters. In addition, set the Rocksdb parameters to maintain the same compaction efficiency as the default parameters. | For more information, see [Issue 18708](https://github.com/tikv/tikv/issues/18708). |

Note that the compaction and flow control configuration adjustments outlined in the preceding table are tailored for TiKV deployments on instances with the following specifications:

- CPU: 32 cores
- Memory: 128 GiB
- Storage: 5 TiB EBS
- Disk Throughput: 1 GiB/s
#### Recommended configuration adjustments for write-intensive workloads

To optimize TiKV performance and stability under write-intensive workloads, it is recommended that you adjust certain compaction and flow control parameters based on the hardware specifications of the instance. For example:

- [`rocksdb.rate-bytes-per-sec`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#rate-bytes-per-sec): usually use the default value. If you notice that compaction I/O is consuming a significant share of the disk bandwidth, consider capping the rate to about 60% of your disk’s maximum throughput. This helps balance compaction work and ensures the disk is not saturated. For example, on a disk rated at **1 GiB/s**, set this to roughly `600MiB`.

- [`storage.flow-control.soft-pending-compaction-bytes-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#soft-pending-compaction-bytes-limit-1) and [`storage.flow-control.hard-pending-compaction-bytes-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#hard-pending-compaction-bytes-limit-1): increase these limits proportionally to the available disk space (for example, 1 TiB and 2 TiB, respectively) to provide more buffer for compaction processes.

These settings help ensure efficient resource utilization and minimize potential bottlenecks during peak write loads.

> **Note:**
>
> TiKV implements flow control at the scheduler layer to ensure system stability. When critical thresholds are breached, including those for pending compaction bytes or write queue sizes, TiKV begins rejecting write requests and returns a ServerIsBusy error. This error indicates that the background compaction processes cannot keep pace with the current rate of foreground write operations. Flow control activation typically results in latency spikes and reduced query throughput (QPS drops). To prevent these performance degradations, comprehensive capacity planning is essential, along with proper configuration of compaction parameters and storage settings.
### TiFlash-learner configurations

Add the following configuration items to the TiFlash-learner configuration file:

```toml
[server]
snap-io-max-bytes-per-sec = "300MiB"
```

| Configuration item | Description | Note |
| ---------| ---- | ----|
| [`snap-io-max-bytes-per-sec`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#snap-io-max-bytes-per-sec) | Control the maximum allowable disk bandwidth for data replication from TiKV to TiFlash. Higher limits accelerate initial data loading and catch-up replication. | Higher bandwidth consumption might impact online transaction performance. Balance between replication speed and system stability. |
