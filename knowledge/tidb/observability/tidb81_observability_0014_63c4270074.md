# BR backup monitoring setup and metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-monitoring-and-alert.md`
- Source Title: `Monitoring and Alert for Backup and Restore`
- Source Heading Path: `Monitoring and Alert for Backup and Restore | Monitoring and Alert for Backup and Restore > Snapshot backup and restore monitoring | Monitoring and Alert for Backup and Restore > Log backup monitoring | Monitoring and Alert for Backup and Restore > Log backup monitoring > Monitoring configuration | Monitoring and Alert for Backup and Restore > Log backup monitoring > Grafana configuration | Monitoring and Alert for Backup and Restore > Log backup monitoring > Monitoring metrics`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`, `dashboard`, `tiup`, `shared`
- Topic Tags: `monitoring`, `grafana`, `prometheus`, `snapshot-backup`, `log-backup`, `pitr`, `metrics`, `dashboard`, `manual-deployment`, `tiup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0014_63c4270074`
- Source ID: `tidb-docs-8.1:br/br-monitoring-and-alert.md#monitoring-and-alert-for-backup-and-restore`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c64eb1dcacfc53a5b6a6a7f15f928b05143bc8570a6619d09f9970a99c077c09`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-monitoring-and-alert#monitoring-and-alert-for-backup-and-restore
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-monitoring-and-alert.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs where to view BR snapshot backup or PITR log backup monitoring and the exact TiKV log backup metrics, dashboards, or Prometheus collection setup.
- Retrieval Keywords: TiKV-Details, Backup & Import, Backup Log, PITR panel, Prometheus, Grafana, scrape_configs, tikv_details.json, tikv_log_backup_internal_actor_acting_duration_sec, tikv_log_backup_initial_scan_reason, tikv_log_backup_event_handle_duration_sec, tikv_log_backup_handle_kv_batch, tikv_log_backup_initial_scan_disk_read, tikv_log_backup_incremental_scan_bytes, tikv_log_backup_skip_kv_count, tikv_log_backup_errors, tikv_log_backup_fatal_errors, tikv_log_backup_heap_memory, tikv_log_backup_on_event_duration_seconds, tikv_log_backup_store_checkpoint_ts, tidb_log_backup_last_checkpoint, tikv_log_backup_flush_duration_sec, tikv_log_backup_flush_file_size, tikv_log_backup_initial_scan_duration_sec, tikv_log_backup_skip_retry_observe, tikv_log_backup_initial_scan_operations, tikv_log_backup_enabled, tikv_log_backup_observed_region, tikv_log_backup_task_status, tikv_log_backup_pending_initial_scan, snapshot backup and restore monitoring, log backup monitoring
- Follow-up Guidance: For TiUP deployments, Prometheus automatically collects the metrics and Grafana already contains the PITR panel, while manual deployments use TiKV-related jobs in `scrape_configs` and import `tikv_details.json` to find the **Backup Log** panel.
- Classification Note: This is observability content because it describes monitoring deployment, Grafana dashboard locations, Prometheus collection, and the official BR log backup metrics exposed by TiKV.

## Official Source Content

# Monitoring and Alert for Backup and Restore

This document describes the monitoring and alert of the backup and restore feature, including how to deploy monitoring components, monitoring metrics, and common alerts.
## Snapshot backup and restore monitoring

To view the snapshot backup and restore metrics, go to the [**TiKV-Details** > **Backup & Import** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#backup--import) in Grafana.
## Log backup monitoring

Log backup supports using [Prometheus](https://prometheus.io/) to collect monitoring metrics. Currently all monitoring metrics are built into TiKV.
### Monitoring configuration

- For clusters deployed using TiUP, Prometheus automatically collects monitoring metrics.
- For clusters deployed manually, follow the instructions in [TiDB Cluster Monitoring Deployment](https://docs.pingcap.com/tidb/stable/deploy-monitoring-services) to add TiKV-related jobs to the `scrape_configs` section of the Prometheus configuration file.
### Grafana configuration

- For clusters deployed using TiUP, the [Grafana](https://grafana.com/) dashboard contains the point-in-time recovery (PITR) panel. The **Backup Log** panel in the TiKV-Details dashboard is the PITR panel.
- For clusters deployed manually, refer to [Import a Grafana dashboard](https://docs.pingcap.com/tidb/stable/deploy-monitoring-services#step-2-import-a-grafana-dashboard) and upload the [tikv_details](https://github.com/tikv/tikv/blob/release-8.1/metrics/grafana/tikv_details.json) JSON file to Grafana. Then find the **Backup Log** panel in the TiKV-Details dashboard.
### Monitoring metrics

| Metrics                                                | Type    |  Description                                                                                                                                                 |
|-------------------------------------------------------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| **tikv_log_backup_internal_actor_acting_duration_sec** | Histogram | The duration of handling all internal messages and events. <br/>`message :: TaskType`                                                                                                            |
| **tikv_log_backup_initial_scan_reason**               | Counter   | Statistics of the reasons why initial scan is triggered. The main reason is leader transfer or Region version change. <br/> `reason :: {"leader-changed", "region-changed", "retry"}`                                           |
| **tikv_log_backup_event_handle_duration_sec**         | Histogram | The duration of handling KV events. Compared with `tikv_log_backup_on_event_duration_seconds`, this metric also includes the duration of internal conversion. <br/>`stage :: {"to_stream_event", "save_to_temp_file"}` |
| **tikv_log_backup_handle_kv_batch**                   | Histogram |  Region-level statistics of the sizes of KV pair batches sent by Raftstore.                                                                                                    |
| **tikv_log_backup_initial_scan_disk_read**            | Counter   | The size of data read from the disk during initial scan. In Linux, this information is from procfs, which is the size of data actually read from the block device. The configuration item `initial-scan-rate-limit` applies to this metric.                                   |
| **tikv_log_backup_incremental_scan_bytes**            | Histogram | The size of KV pairs actually generated during initial scan. Because of compression and read amplification, this value might be different from that of `tikv_log_backup_initial_scan_disk_read`.                                                                  |
| **tikv_log_backup_skip_kv_count**                     | Counter   |  The number of Raft events being skipped during the log backup because they are not helpful to the backup.                                                                                                                   |
| **tikv_log_backup_errors**                            | Counter   | The errors that can be retried or ignored during the log backup. <br/>`type :: ErrorType`                                                                                                       |
| **tikv_log_backup_fatal_errors**                      | Counter   | The errors that cannot be retried or ignored during the log backup. When an error of this type occurs, the log backup is paused. <br/>`type :: ErrorType`                                                                                   |
| **tikv_log_backup_heap_memory**                       | Gauge     |  The memory occupied by events that are unconsumed and found by initial scan during log backup.                                                                                                                         |
| **tikv_log_backup_on_event_duration_seconds**         | Histogram |  The duration of storing KV events to temporary files. <br/>`stage :: {"write_to_tempfile", "syscall_write"}`                                                                        |
| **tikv_log_backup_store_checkpoint_ts**               | Gauge     | The store-level checkpoint TS, which is deprecated. It is close to the GC safepoint registered by the current store. <br/>`task :: string`                                                                    |
| **tidb_log_backup_last_checkpoint** | Gauge | The global checkpoint TS. It is a time point till which log data has been backed up. <br/>`task :: string` |
| **tikv_log_backup_flush_duration_sec**                | Histogram |  The duration of moving local temporary files to the external storage. <br/>`stage :: {"generate_metadata", "save_files", "clear_temp_files"}`                                                                |
| **tikv_log_backup_flush_file_size**                   | Histogram |  Statistics of the sizes of files generated during the backup.                                                                                                                                          |
| **tikv_log_backup_initial_scan_duration_sec**         | Histogram | The statistics of the overall duration of initial scan.                                                                                                                                           |
| **tikv_log_backup_skip_retry_observe**                | Counter   | Statistics of the errors that can be ignored during log backup, or the reasons why retry is skipped.  <br/>`reason :: {"region-absent", "not-leader", "stale-command"}`                                                   |
| **tikv_log_backup_initial_scan_operations**           | Counter   | Statistics of RocksDB-related operations during initial scan. <br/>`cf :: {"default", "write", "lock"}, op :: RocksDBOP`                                                                       |
| **tikv_log_backup_enabled**                           | Counter   |  Whether to enable log backup. If the value is greater than `0`, log backup is enabled.                                                                                                                                |
| **tikv_log_backup_observed_region**                   | Gauge     | The number of Regions being listened to.                                                                                                                                        |
| **tikv_log_backup_task_status**                       | Gauge     | The status of the log backup task. `0` means running. `1` means paused. `2` means error.  <br/>`task :: string`                                                                                                |
| **tikv_log_backup_pending_initial_scan**              | Gauge     | Statistics of pending initial scans. <br/>`stage :: {"queuing", "executing"}`                                                                                                     |
