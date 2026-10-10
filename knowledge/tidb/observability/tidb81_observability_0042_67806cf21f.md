# DM task binlog replication and relay log metrics with instance dashboard entry

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/monitor-a-dm-cluster.md`
- Source Title: `Data Migration Monitoring Metrics`
- Source Heading Path: `Data Migration Monitoring Metrics > Task > Binlog replication | Data Migration Monitoring Metrics > Task > Relay log | Data Migration Monitoring Metrics > Instance`
- Source Line Ranges: `73-131`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `dashboard`
- Topic Tags: `binlog-replication`, `relay-log`, `incremental-replication`, `alerts`, `latency`, `qps`, `queue`, `shard-ddl`, `instance-metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0042_67806cf21f`
- Source ID: `tidb-docs-8.1:dm/monitor-a-dm-cluster.md#binlog-replication`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fee49c26402c854e19e98cc65820f0b04e532714923e322ccb7581a1cd96c2d5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/monitor-a-dm-cluster#binlog-replication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/monitor-a-dm-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs DM-task binlog replication or relay log metrics, alert thresholds, or the DM-instance dashboard name in Grafana.
- Retrieval Keywords: Binlog replication, Relay log, Instance, DM-instance, remaining time to sync, replicate lag gauge, replicate lag histogram, process exist with error, process exits with error, binlog file gap between master and syncer, binlog file gap between relay and syncer, binlog event QPS, skipped binlog event QPS, read binlog event duration, transform binlog event duration, dispatch binlog event duration, transaction execution latency, DML queue remain length, statement execution latency, DML conflict detect duration, unsynced tables, shard lock resolving, ideal QPS, flush checkpoints time interval, storage remain, relay log data corruption, fail to read binlog from master, fail to write relay log, binlog file index, binlog file gap between master and relay, binlog pos
- Follow-up Guidance: The source notes that the binlog replication metrics show only when `task-mode` is `incremental` or `all`, and that currently DM v2.0 does not support enabling the relay log feature.
- Classification Note: The classification is observability for the dm component because the content describes monitoring metrics, dashboard entries, and alert conditions for binlog replication, relay log, and instance views.

## Official Source Content

### Binlog replication

The following metrics show only when `task-mode` is in the `incremental` or `all` mode.

| Metric name | Description | Alert | Severity level |
|:----|:------------|:----|:----|
| remaining time to sync | The predicted remaining time it takes for `syncer` to be completely migrated with the upstream master (in minutes) | N/A | N/A |
| replicate lag gauge | The latency time it takes to replicate the binlog from upstream to downstream (in seconds) | N/A | N/A |
| replicate lag histogram | The histogram of replicating the binlog from upstream to downstream (in seconds). Note that due to different statistical mechanisms, the data might be inaccurate | N/A | N/A |
| process exist with error | The binlog replication unit encounters an error within the DM-worker and exits | Immediate alerts | critical |
| binlog file gap between master and syncer | The number of binlog files by which the `syncer` processing unit is behind the upstream master | An alert occurs when the number of binlog files by which the `syncer` processing unit is behind the upstream master exceeds one (>1) and the condition lasts over 10 minutes | critical |
| binlog file gap between relay and syncer | The number of binlog files by which `syncer` is behind `relay` | An alert occurs when the number of binlog files by which the `syncer` processing unit is behind the `relay` processing unit exceeds one (>1) and the condition lasts over 10 minutes | critical |
| binlog event QPS | The number of binlog events received per unit of time (this number does not include the events that need to be skipped) | N/A | N/A |
| skipped binlog event QPS | The number of binlog events received per unit of time that need to be skipped | N/A | N/A |
| read binlog event duration | The duration that the binlog replication unit reads the binlog from the relay log or the upstream MySQL (in seconds) | N/A | N/A |
| transform binlog event duration | The duration that the binlog replication unit parses and transforms the binlog into SQL statements (in seconds) | N/A | N/A |
| dispatch binlog event duration | The duration that the binlog replication unit dispatches a binlog event (in seconds) | N/A | N/A |
| transaction execution latency | The duration that the binlog replication unit executes the transaction to the downstream (in seconds) | N/A | N/A |
| binlog event size | The size of a binlog event that the binlog replication unit reads from the relay log or the upstream MySQL | N/A | N/A |
| DML queue remain length | The length of the remaining DML job queue | N/A | N/A |
| total sqls jobs | The number of newly added jobs per unit of time | N/A | N/A |
| finished sqls jobs | The number of finished jobs per unit of time | N/A | N/A |
| statement execution latency | The duration that the binlog replication unit executes the statement to the downstream (in seconds) | N/A | N/A |
| add job duration | The duration that the binlog replication unit adds a job to the queue (in seconds) | N/A | N/A |
| DML conflict detect duration | The duration that the binlog replication unit detects the conflict in DML (in seconds) | N/A | N/A |
| skipped event duration | The duration that the binlog replication unit skips a binlog event (in seconds) | N/A | N/A |
| unsynced tables | The number of tables that have not received the shard DDL statement in the current subtask | N/A | N/A |
| shard lock resolving | Whether the current subtask is waiting for the shard DDL lock to be resolved. A value greater than 0 indicates that it is waiting for the shard DDL lock to be resolved | N/A | N/A |
| ideal QPS | The highest QPS that can be achieved when the running time of DM is 0 | N/A | N/A |
| binlog event row | The number of rows in a binlog event | N/A | N/A |
| finished transaction total | The number of finished transactions in total | N/A | N/A |
| replication transaction batch | The number of sql rows in the transaction executed to the downstream | N/A | N/A |
| flush checkpoints time interval | The time interval for flushing the checkpoints (in seconds) | N/A | N/A |
### Relay log

> **Note:**
>
> Currently, DM v2.0 does not support enabling the relay log feature.

| Metric name | Description | Alert | Severity level |
|:----|:------------|:----|:----|
| storage capacity | The storage capacity of the disk occupied by the relay log | N/A | N/A |
| storage remain | The remaining storage capacity of the disk occupied by the relay log | An alert is needed once the value is smaller than 10G | critical |
| process exits with error | The relay log encounters an error within the DM-worker and exits | Immediate alerts | critical |
| relay log data corruption | The number of corrupted relay log files | Immediate alerts | emergency |
| fail to read binlog from master | The number of errors encountered when the relay log reads the binlog from the upstream MySQL | Immediate alerts | critical |
| fail to write relay log | The number of errors encountered when the relay log writes the binlog to disks | Immediate alerts | critical |
| binlog file index | The largest index number of relay log files. For example, "value = 1" indicates "relay-log.000001" | N/A | N/A |
| binlog file gap between master and relay | The number of binlog files in the relay log that are behind the upstream master | An alert occurs when the number of binlog files by which the `relay` processing unit is behind the upstream master exceeds one (>1) and the condition lasts over 10 minutes | critical |
| binlog pos | The write offset of the latest relay log file | N/A | N/A |
| read binlog event duration | The duration that the relay log reads binlog from the upstream MySQL (in seconds) | N/A | N/A |
| write relay log duration | The duration that the relay log writes binlog into the disks each time (in seconds) | N/A | N/A |
| binlog event size | The size of a single binlog event that the relay log writes into the disks | N/A | N/A |
## Instance

In the Grafana dashboard, the default name of an instance is `DM-instance`.
