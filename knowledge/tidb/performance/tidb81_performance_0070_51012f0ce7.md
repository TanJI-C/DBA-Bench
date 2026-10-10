# PITR performance and monitoring

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-pitr-guide.md`
- Source Title: `TiDB Log Backup and PITR Guide`
- Source Heading Path: `TiDB Log Backup and PITR Guide > Performance capabilities of PITR | TiDB Log Backup and PITR Guide > Monitoring and alert | TiDB Log Backup and PITR Guide > See also`
- Source Line Ranges: `105-156`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`, `tidb`
- Topic Tags: `throughput`, `restore speed`, `batching`, `monitoring`, `alerts`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0070_51012f0ce7`
- Source ID: `tidb-docs-8.1:br/br-pitr-guide.md#performance-capabilities-of-pitr`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9e56244430100aef5a94d2e1f5c650f5223823d983fd5fb93328eb4d1f2514c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-pitr-guide#performance-capabilities-of-pitr
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-pitr-guide.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs PITR restore throughput figures, log truncate performance, batching parameter names, or where to monitor log backup activity and alerts.
- Retrieval Keywords: Performance capabilities of PITR, 2 TiB/h, 30 GiB/h, 600 GB/h, import.num-threads, pitr-concurrency, pitr-batch-size, pitr-batch-count, many Regions, short flush interval, TiKV-Details > Backup Log, Log backup alerts, Monitoring and alert
- Follow-up Guidance: It also states that restore speed figures are based on testing scenarios and that batching overhead can increase when the upstream cluster has many Regions and a short flush interval.
- Classification Note: The content is classified as performance because it provides PITR restore and truncate speed metrics, tuning parameters, and monitoring references.

## Official Source Content

## Performance capabilities of PITR

- On each TiKV node, PITR can restore snapshot data (full restore) at a speed of 2 TiB/h and log data (including meta files and KV files) at a speed of 30 GiB/h.
- BR deletes outdated log backup data (`tiup br log truncate`) at a speed of 600 GB/h.

> **Note:**
>
> The preceding specifications are based on test results from the following two testing scenarios. The actual data might be different.
>
> - Snapshot data restore speed = Total size of restored snapshot data on all TiKV nodes in the cluster / (duration * the number of TiKV nodes)
> - Log data restore speed = Total size of restored log data on all TiKV nodes in the cluster / (duration * the number of TiKV nodes)
>
> External storage only contains KV data of a single replica. Therefore, the data size in external storage does not represent the actual data size restored in the cluster. BR restores all replicas according to the number of replicas configured for the cluster. The more replicas there are, the more data can be actually restored.
> The default replica number for all clusters in the test is 3.
> To improve the overall restore performance, you can modify the [`import.num-threads`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#import) item in the TiKV configuration file and the [`pitr-concurrency`](https://docs.pingcap.com/tidb/stable/br/br-pitr-manual#restore-to-a-specified-point-in-time-pitr) option in the BR command.
> When the upstream cluster has **many Regions** and a **short flush interval**, PITR generates a large number of small files. This increases batching and dispatching overhead during restore. To raise the number of files processed per batch, you can **moderately** increase the values of the following parameters:
>
> - `pitr-batch-size`: cumulative **bytes per batch** (default **16 MiB**).
> - `pitr-batch-count`: **number of files per batch** (default **8**).
>
> When determining whether to start the next batch, these two thresholds are evaluated independently: whichever threshold is reached first closes the current batch and starts the next, while the other threshold is ignored for that batch.

Testing scenario 1 (on [TiDB Cloud](https://tidbcloud.com)) is as follows:

- The number of TiKV nodes (8 core, 16 GB memory): 21
- TiKV configuration item `import.num-threads`: 8
- BR command option `concurrency`: 128
- The number of Regions: 183,000
- New log data created in the cluster: 10 GB/h
- Write (INSERT/UPDATE/DELETE) QPS: 10,000

Testing scenario 2 (on TiDB Self-Managed) is as follows:

- The number of TiKV nodes (8 core, 64 GB memory): 6
- TiKV configuration item `import.num-threads`: 8
- BR command option `concurrency`: 128
- The number of Regions: 50,000
- New log data created in the cluster: 10 GB/h
- Write (INSERT/UPDATE/DELETE) QPS: 10,000
## Monitoring and alert

After log backup tasks are distributed, each TiKV node continuously writes data to external storage. You can view the monitoring data for this process in the **TiKV-Details > Backup Log** dashboard.

To receive notifications metrics deviate from normal ranges, see [Log backup alerts](https://docs.pingcap.com/tidb/stable/br/br-monitoring-and-alert#log-backup-alerts) to configure alert rules.
## See also

* [TiDB Backup and Restore Use Cases](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-use-cases)
* [br Command-line Manual](https://docs.pingcap.com/tidb/stable/br/use-br-command-line-tool)
* [Log Backup and PITR Architecture](https://docs.pingcap.com/tidb/stable/br/br-log-architecture)
* [Monitoring and Alert for Backup and Restore](https://docs.pingcap.com/tidb/stable/br/br-monitoring-and-alert)
