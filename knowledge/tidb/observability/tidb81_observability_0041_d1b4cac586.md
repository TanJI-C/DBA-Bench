# DM task dashboard overview, errors, HA, state, and dump/load metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/monitor-a-dm-cluster.md`
- Source Title: `Data Migration Monitoring Metrics`
- Source Heading Path: `Data Migration Monitoring Metrics | Data Migration Monitoring Metrics > Task | Data Migration Monitoring Metrics > Task > `overview` | Data Migration Monitoring Metrics > Task > Operation errors | Data Migration Monitoring Metrics > Task > High availability | Data Migration Monitoring Metrics > Task > Task state | Data Migration Monitoring Metrics > Task > Dump/Load unit`
- Source Line Ranges: `5-72`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `dashboard`, `tiup`
- Topic Tags: `grafana`, `monitoring`, `metrics`, `alerts`, `task-state`, `high-availability`, `operation-errors`, `full-load`, `checksum`, `dump`, `load`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0041_d1b4cac586`
- Source ID: `tidb-docs-8.1:dm/monitor-a-dm-cluster.md#data-migration-monitoring-metrics`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `09987ea3cbfd23674c7f55986bec2a4064e12dc1e71162786bdfc341ae0a807f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/monitor-a-dm-cluster#data-migration-monitoring-metrics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/monitor-a-dm-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when the user is looking for DM-task Grafana metrics or alerts about task overview, operation errors, high availability, task state, or dump/load progress in a DM cluster.
- Retrieval Keywords: DM-task, Overview, Operation errors, High availability, Task state, Dump/Load unit, task state, storage capacity, storage remain, binlog file gap between master and relay, binlog file gap between master and syncer, load progress, dump progress, checksum progress, shard lock resolving, before any operate error, source bound error, start error, pause error, resume error, auto-resume error, update error, stop error, number of workers in different state, workers' state, number of worker event error, shard ddl error per minute, number of pending shard ddl, dump process exits with error, load process exits with error
- Follow-up Guidance: The source also states that these monitoring metrics are provided by DM-worker and that the monitoring system is deployed together when the DM cluster is deployed using TiUP.
- Classification Note: The classification is observability for the dm component because the content enumerates Grafana dashboard metrics, alert conditions, and severity levels for monitoring DM tasks.

## Official Source Content

# Data Migration Monitoring Metrics

If your DM cluster is deployed using TiUP, the [monitoring system](https://docs.pingcap.com/tidb/stable/dm/migrate-data-using-dm#step-8-monitor-the-task-and-check-logs) is also deployed at the same time. This document describes the monitoring metrics provided by DM-worker.
## Task

In the Grafana dashboard, the default name of DM is `DM-task`.
### `overview`

`Overview` contains some monitoring metrics of all the DM-worker and DM-master instances or sources in the currently selected task. The current default alert rule is only for a single DM-worker/DM-master instance/source.

| Metric name | Description | Alert | Severity level |
|:----|:------------|:----|:----|
| task state | The state of subtasks for migration | N/A | N/A |
| storage capacity | The total storage capacity of the disk occupied by relay logs | N/A | N/A |
| storage remain | The remaining storage capacity of the disk occupied by relay logs | N/A | N/A |
| binlog file gap between master and relay | The number of binlog files by which the `relay` processing unit is behind the upstream master | N/A | N/A |
| load progress | The percentage of the completed loading process of the load unit. The value is between 0%~100% | N/A | N/A |
| binlog file gap between master and syncer | The number of binlog files by which the binlog replication unit is behind the upstream master | N/A | N/A |
| shard lock resolving | Whether the current subtask is waiting for sharding DDL migration. A value greater than 0 means that the current subtask is waiting for sharding DDL migration | N/A | N/A |
### Operation errors

| Metric name | Description | Alert | Severity level |
|:----|:------------|:----|:----|
| before any operate error | The number of errors before any operation | N/A | N/A |
| source bound error | The number of errors of data source binding operations | N/A | N/A |
| start error | The number of errors during the start of a subtask | N/A | N/A |
| pause error | The number of errors during the pause of a subtask | N/A | N/A |
| resume error | The number of errors during the resuming of a subtask | N/A | N/A |
| auto-resume error | The number of errors during the auto-resuming of a subtask | N/A | N/A |
| update error | The number of errors during the update of a subtask | N/A | N/A |
| stop error | The number of errors during the stop of a subtask | N/A | N/A |
### High availability

| Metric name | Description | Alert | Severity level |
|:----|:------------|:----|:----|
| number of dm-masters start leader components per minute | The number of DM-master attempts to enable leader related components per minute | N/A | N/A |
| number of workers in different state | The number of DM-workers in different states | Some DM-worker(s) has (have) been offline for more than one hour | critical |
| workers' state | The state of the DM-worker | N/A | N/A |
| number of worker event error | The number of different types of DM-worker errors | N/A | N/A |
| shard ddl error per minute | The number of different types of sharding DDL errors per minute | Any sharding DDL error occurs | critical |
| number of pending shard ddl | The number of pending sharding DDL operations | Any pending sharding DDL operation has existed for more than one hour | critical |
### Task state

| Metric name | Description | Alert | Severity level |
|:----|:------------|:----|:----|
| task state | The state of subtasks | An alert occurs when the subtask has been in the `Paused` state for more than 20 minutes | critical |
### Dump/Load unit

The following metrics show only when `task-mode` is in the `full` or `all` mode.

| Metric name | Description | Alert | Severity level |
|:----|:------------|:----|:----|
| dump progress | The percentage of the completed dumping process of the dump unit. The value range is 0%~100% | N/A | N/A |
| load progress | The percentage of the completed loading process of the load unit. The value range is 0%~100% | N/A | N/A |
| checksum progress | The percentage of the completed checksum process after the load unit finishes dumping. The value range is 0%~100% | N/A | N/A |
| total bytes for load unit | The bytes processed in the parsing, in generating data KV, and in generating index KV stages of the import process by the load unit | N/A | N/A |
| chunk process duration | The duration of the load unit processing the data source file chunk (in seconds) | N/A | N/A |
| data file size | The total size of the data files (includes the `INSERT INTO` statement) in the full data imported by the load unit | N/A | N/A |
| dump process exits with error | The dump unit encounters an error within the DM-worker and exits | Immediate alerts | critical |
| load process exits with error | The load unit encounters an error within the DM-worker and exits | Immediate alerts | critical |
