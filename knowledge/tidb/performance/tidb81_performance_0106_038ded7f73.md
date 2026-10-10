# DM performance issue diagnosis across relay, load, and binlog replication units

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-handle-performance-issues.md`
- Source Title: `Handle Performance Issues of TiDB Data Migration`
- Source Heading Path: `Handle Performance Issues of TiDB Data Migration | Handle Performance Issues of TiDB Data Migration > relay log unit | Handle Performance Issues of TiDB Data Migration > relay log unit > Read binlog data | Handle Performance Issues of TiDB Data Migration > relay log unit > binlog data decoding and verification | Handle Performance Issues of TiDB Data Migration > relay log unit > Write relay log files | Handle Performance Issues of TiDB Data Migration > Load unit | Handle Performance Issues of TiDB Data Migration > Binlog replication unit | Handle Performance Issues of TiDB Data Migration > Binlog replication unit > Read binlog data | Handle Performance Issues of TiDB Data Migration > Binlog replication unit > binlog event conversion | Handle Performance Issues of TiDB Data Migration > Binlog replication unit > Write SQL statements to downstream`
- Source Line Ranges: `5-97`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `sql`
- Topic Tags: `performance-diagnosis`, `monitoring-metrics`, `relay-log`, `binlog-replication`, `load-unit`, `latency`, `throughput`, `network`, `disk-io`, `downstream-writes`, `grafana`, `prometheus`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0106_038ded7f73`
- Source ID: `tidb-docs-8.1:dm/dm-handle-performance-issues.md#handle-performance-issues-of-tidb-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `243765e5ceef20e6973dce1bb83ab8fb9a8526a08959d103223722aca171a91a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-handle-performance-issues#handle-performance-issues-of-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-handle-performance-issues.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing DM data migration latency or throughput issues by checking relay log, Load unit, and Binlog replication metrics in Grafana or Prometheus.
- Retrieval Keywords: DM performance issues, TiDB Data Migration, relay log unit, Load unit, Binlog replication unit, binlog file gap between master and relay, binlog file gap between master and syncer, binlog file gap between relay and syncer, binlog pos, read binlog event duration, write relay log duration, dm_relay_read_transform_duration, transform binlog event duration, DML queue remain length, transaction execution latency, statement execution latency, worker-count, q_0, q_7, batch, binlog event size, table router, Grafana, Prometheus
- Follow-up Guidance: If `binlog file gap between master and syncer` stays greater than 1 for a long time, the source says to check `binlog file gap between relay and syncer` to determine whether the latency mainly exists in the relay log unit or continue checking the Binlog replication unit.
- Classification Note: This chunk is classified as performance for the DM component because it describes how to diagnose migration bottlenecks with monitoring metrics across relay log reading and writing, load processing, binlog event conversion, and downstream SQL execution.

## Official Source Content

# Handle Performance Issues of TiDB Data Migration

This document introduces common performance issues that might exist in DM and how to deal with them.

Before diagnosing an issue, you can refer to the [DM Benchmark Report](https://github.com/pingcap/docs-dm/blob/release-5.3/en/dm-benchmark-v5.3.0.md).

When diagnosing and handling performance issues, make sure that:

- The DM monitoring component is correctly configured and installed.
- You can view [monitoring metrics](https://docs.pingcap.com/tidb/stable/dm/monitor-a-dm-cluster#task) on the Grafana monitoring dashboard.
- The component you diagnose works well; otherwise, possible monitoring metrics exceptions might interfere with the diagnosis of performance issues.

In the case of a large latency in the data migration, to quickly figure out whether the bottleneck is inside the DM component or in the TiDB cluster, you can first check `DML queue remain length` in [Write SQL Statements to Downstream](#write-sql-statements-to-downstream).
## relay log unit

To diagnose performance issues in the relay log unit, you can check the `binlog file gap between master and relay` monitoring metric. For more information about this metric, refer to [monitoring metrics of the relay log](https://docs.pingcap.com/tidb/stable/dm/monitor-a-dm-cluster#relay-log). If this metric is greater than 1 for a long time, it usually indicates that there is a performance issue; if this metric is 0, it usually indicates that there is no performance issue.

If the value of `binlog file gap between master and relay` is 0, but you suspect that there is a performance issue, you can check `binlog pos`. If `master` in this metric is much larger than `relay`, a performance issue might exist. In this case, diagnose and handle this issue accordingly.
### Read binlog data

`read binlog event duration` refers to the duration that the relay log reads binlog from the upstream database (MySQL/MariaDB). Ideally, this metric is close to the network latency between DM-worker and MySQL/MariaDB instances.

- For data migration in one data center, reading binlog data is not a performance bottleneck. If the value of `read binlog event duration` is too large, check the network connection between DM-worker and MySQL/MariaDB.

- For data migration in the geo-distributed environment, try to deploy DM-worker and MySQL/MariaDB in one data center, while deploying the TiDB cluster in the target data center.

The process of reading binlog data from the upstream database includes the following sub-processes:

- The upstream MySQL/MariaDB reads the binlog data locally and sends it through the network. When no exception occurs in the MySQL/MariaDB load, this sub-process usually does not become a bottleneck.
- The binlog data is transferred from the machine where MySQL/MariaDB is located to the machine where DM-worker is located via the network. Whether this sub-process becomes a bottleneck mainly depends on the network connection between DM-worker and the upstream MySQL/MariaDB.
- DM-worker reads binlog data from the network data stream and constructs it as a binlog event. When no exception occurs in the DM-worker load, this sub-process usually does not become a bottleneck.

> **Note:**
>
> If the value of `read binlog event duration` is large, another possible reason is that the upstream MySQL/MariaDB has a low load. This means that no binlog event needs to be sent to DM for a period of time, and the relay log unit stays in a wait state, thus this value includes additional waiting time.
### binlog data decoding and verification

After reading the binlog event into the DM memory, DM's relay processing unit decodes and verifies data. This usually does not lead to performance bottleneck; therefore, there is no related performance metric on the monitoring dashboard by default. If you need to view this metric, you can manually add a monitoring item in Grafana. This monitoring item corresponds to `dm_relay_read_transform_duration`, a metric from Prometheus.
### Write relay log files

When writing a binlog event to a relay log file, the relevant performance metric is `write relay log duration`. This value should be microseconds when `binlog event size` is not too large. If `write relay log duration` is too large, check the write performance of the disk. To avoid low write performance, use local SSDs for DM-worker.
## Load unit

The main operations of the Load unit are to read the SQL file data from the local and write it to the downstream. The related performance metric is `transaction execution latency`. If this value is too large, check the downstream performance by checking the monitoring of the downstream database. You can also check whether there is a large network latency between DM and the downstream database.
## Binlog replication unit

To diagnose performance issues in the Binlog replication unit, you can check the `binlog file gap between master and syncer` monitoring metric. For more information about this metric, refer to [monitoring metrics of the Binlog replication](https://docs.pingcap.com/tidb/stable/dm/monitor-a-dm-cluster#binlog-replication).

- If this metric is greater than 1 for a long time, it usually indicates that there is a performance issue.
- If this metric is 0, it usually indicates that there is no performance issue.

When `binlog file gap between master and syncer` is greater than 1 for a long time, check `binlog file gap between relay and syncer` to figure out which unit the latency mainly exists in. If this value is usually 0, the latency might exist in the relay log unit. Then you can refer to [relay log unit](#relay-log-unit) to resolve this issue; otherwise, continue checking the Binlog replication unit.
### Read binlog data

The Binlog replication unit decides whether to read the binlog event from the upstream MySQL/MariaDB or from the relay log file according to the configuration. The related performance metric is `read binlog event duration`, which generally ranges from a few microseconds to tens of microseconds.

- If DM's Binlog replication processing unit reads the binlog event from upstream MySQL/MariaDB, to locate and resolve the issue, refer to [read binlog data](#read-binlog-data) in the "relay log unit" section.

- If DM's Binlog replication processing unit reads the binlog event from the relay log file, when `binlog event size` is not too large, the value of `read binlog event duration` should be microseconds. If `read binlog event duration` is too large, check the read performance of the disk. To avoid low write performance, use local SSDs for DM-worker.
### binlog event conversion

The Binlog replication unit constructs DML, parses DDL, and performs [table router](https://docs.pingcap.com/tidb/stable/dm/dm-table-routing) conversion from binlog event data. The related metric is `transform binlog event duration`.

The duration is mainly affected by the write operations upstream. Take the `INSERT INTO` statement as an example, the time consumed to convert a single `VALUES` greatly differs from that to convert a lot of `VALUES`. The time consumed might range from tens of microseconds to hundreds of microseconds. However, usually this is not a bottleneck of the system.
### Write SQL statements to downstream

When the Binlog replication unit writes the converted SQL statements to the downstream, the related performance metrics are `DML queue remain length` and `transaction execution latency`.

After constructing SQL statements from binlog event, DM uses `worker-count` queues to concurrently write these statements to the downstream. However, to avoid too many monitoring entries, DM performs the modulo `8` operation on the IDs of concurrent queues. This means that all concurrent queues correspond to one item from `q_0` to `q_7`.

`DML queue remain length` indicates in the concurrent processing queue, the number of DML statements that have not been consumed and have not started to be written downstream. Ideally, the curves corresponding to each `q_*` are almost the same. If not, it indicates that the concurrent load is extremely unbalanced.

If the load is not balanced, confirm whether tables need to be migrated have primary keys or unique keys. If these keys do not exist, add the primary keys or the unique keys; if these keys do exist while the load is not balanced, upgrade DM to v1.0.5 or later versions.

- When there is no noticeable latency in the entire data migration link, the corresponding curve of `DML queue remain length` is almost always 0, and the maximum does not exceed the value of `batch` in the task configuration file.

- If you find a noticeable latency in the data migration link, and the curve of `DML queue remain length` corresponding to each `q_*` is almost the same and is almost always 0, it means that DM fails to read, convert, or concurrently write the data from the upstream in time (the bottleneck might be in the relay log unit). For troubleshooting, refer to the previous sections of this document.

If the corresponding curve of `DML queue remain length` is not 0 (usually the maximum is not more than 1024), it indicates that there is a bottleneck when writing SQL statements to the downstream. You can use `transaction execution latency` to view the time consumed to execute a single transaction to the downstream.

`transaction execution latency` is usually tens of milliseconds. If this value is too large, check the downstream performance based on the monitoring of the downstream database. You can also check whether there is a large network latency between DM and the downstream database.

To view the time consumed to write a single statement such as `BEGIN`, `INSERT`, `UPDATE`, `DELETE`, or `COMMIT` to the downstream, you can also check `statement execution latency`.
