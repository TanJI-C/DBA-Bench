# TiDB Binlog alert rules and troubleshooting

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/monitor-tidb-binlog-cluster.md`
- Source Title: `TiDB Binlog Monitoring`
- Source Heading Path: `TiDB Binlog Monitoring > Alert rules | TiDB Binlog Monitoring > Alert rules > Emergency-level alerts | TiDB Binlog Monitoring > Alert rules > Emergency-level alerts > `binlog_pump_storage_error_count` | TiDB Binlog Monitoring > Alert rules > Critical-level alerts | TiDB Binlog Monitoring > Alert rules > Critical-level alerts > `binlog_drainer_checkpoint_high_delay` | TiDB Binlog Monitoring > Alert rules > Warning-level alerts | TiDB Binlog Monitoring > Alert rules > Warning-level alerts > `binlog_pump_write_binlog_rpc_duration_seconds_bucket` | TiDB Binlog Monitoring > Alert rules > Warning-level alerts > `binlog_pump_storage_write_binlog_duration_time_bucket` | TiDB Binlog Monitoring > Alert rules > Warning-level alerts > `binlog_pump_storage_available_size_less_than_20G` | TiDB Binlog Monitoring > Alert rules > Warning-level alerts > `binlog_drainer_checkpoint_tso_no_change_for_1m` | TiDB Binlog Monitoring > Alert rules > Warning-level alerts > `binlog_drainer_execute_duration_time_more_than_10s``
- Source Line Ranges: `47-170`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`
- Topic Tags: `alerts`, `pump`, `drainer`, `checkpoint`, `delay`, `disk`, `latency`, `storage`, `troubleshooting`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0086_e4056c0059`
- Source ID: `tidb-docs-8.1:tidb-binlog/monitor-tidb-binlog-cluster.md#alert-rules`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `22d368171563c298cdf310dd1a3f324a123e909583b2b855a56f450ee7ae64f9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/monitor-tidb-binlog-cluster#alert-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/monitor-tidb-binlog-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB Binlog alert rule names, PromQL expressions, severity levels, descriptions, and the documented troubleshooting checks for Pump or Drainer alerts.
- Retrieval Keywords: Alert rules, Emergency-level alerts, Critical-level alerts, Warning-level alerts, binlog_pump_storage_error_count, changes(binlog_pump_storage_error_count[1m]) > 0, pump_storage_error, binlog_drainer_checkpoint_high_delay, (time() - binlog_drainer_checkpoint_tso / 1000) > 3600, handle tso, Drainer event, execute latency, work count, batch, binlog_pump_write_binlog_rpc_duration_seconds_bucket, histogram_quantile(0.9, rate(binlog_pump_rpc_duration_seconds_bucket{method="WriteBinlog"}[5m])) > 1, node exported, disk latency, util, binlog_pump_storage_write_binlog_duration_time_bucket, histogram_quantile(0.9, rate(binlog_pump_storage_write_binlog_duration_time_bucket{type="batch"}[5m])) > 1, binlog_pump_storage_available_size_less_than_20G, binlog_pump_storage_storage_size_bytes{type="available"} < 20 * 1024 * 1024 * 1024, gc_tso, binlog_drainer_checkpoint_tso_no_change_for_1m, changes(binlog_drainer_checkpoint_tso[1m]) < 1, binlog_drainer_execute_duration_time_more_than_10s, histogram_quantile(0.9, rate(binlog_drainer_execute_duration_time_bucket[1m])) > 10
- Follow-up Guidance: The source provides per-alert solutions such as checking pump_storage_error and Pump logs, comparing handle tso and execute latency, checking disk state or node exported metrics, verifying gc_tso, confirming Pumps are running normally, and checking the TiDB cluster state or Drainer log.
- Classification Note: This is classified as observability because the content defines alert severities, PromQL-based alert conditions, and monitoring-driven troubleshooting guidance for TiDB Binlog.

## Official Source Content

## Alert rules

This section gives the alert rules for TiDB Binlog. According to the severity level, TiDB Binlog alert rules are divided into three categories (from high to low): emergency-level, critical-level and warning-level.
### Emergency-level alerts

Emergency-level alerts are often caused by a service or node failure. Manual intervention is required immediately.
#### `binlog_pump_storage_error_count`

* Alert rule:

    `changes(binlog_pump_storage_error_count[1m]) > 0`

* Description:

    Pump fails to write the binlog data to the local storage.

* Solution:

    Check whether an error exists in the `pump_storage_error` monitoring and check the Pump log to find the causes.
### Critical-level alerts

For the critical-level alerts, a close watch on the abnormal metrics is required.
#### `binlog_drainer_checkpoint_high_delay`

* Alert rule:

    `(time() - binlog_drainer_checkpoint_tso / 1000) > 3600`

* Description:

    The delay of Drainer replication exceeds one hour.

* Solution:

    - Check whether it is too slow to obtain the data from Pump:

        You can check `handle tso` of Pump to get the time for the latest message of each Pump. Check whether a high latency exists for Pump and make sure the corresponding Pump is running normally.

    - Check whether it is too slow to replicate data in the downstream based on Drainer `event` and Drainer `execute latency`:

        - If Drainer `execute time` is too large, check the network bandwidth and latency between the machine with Drainer deployed and the machine with the target database deployed, and the state of the target database.
        - If Drainer `execute time` is not too large and Drainer `event` is too small, add `work count` and `batch` and retry.

    - If the two solutions above cannot work, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.
### Warning-level alerts

Warning-level alerts are a reminder for an issue or error.
#### `binlog_pump_write_binlog_rpc_duration_seconds_bucket`

* Alert rule:

    `histogram_quantile(0.9, rate(binlog_pump_rpc_duration_seconds_bucket{method="WriteBinlog"}[5m])) > 1`

* Description:

    It takes too much time for Pump to handle the TiDB request of writing binlog.

* Solution:

    - Verify the disk performance pressure and check the disk performance monitoring via `node exported`.
    - If both `disk latency` and `util` are low, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.
#### `binlog_pump_storage_write_binlog_duration_time_bucket`

* Alert rule:

    `histogram_quantile(0.9, rate(binlog_pump_storage_write_binlog_duration_time_bucket{type="batch"}[5m])) > 1`

* Description:

    The time it takes for Pump to write the local binlog to the local disk.

* Solution:

    Check the state of the local disk of Pump and fix the problem.
#### `binlog_pump_storage_available_size_less_than_20G`

* Alert rule:

    `binlog_pump_storage_storage_size_bytes{type="available"} < 20 * 1024 * 1024 * 1024`

* Description:

    The available disk space of Pump is less than 20 GB.

* Solution:

    Check whether Pump `gc_tso` is normal. If not, adjust the GC time configuration of Pump or get the corresponding Pump offline.
#### `binlog_drainer_checkpoint_tso_no_change_for_1m`

* Alert rule:

    `changes(binlog_drainer_checkpoint_tso[1m]) < 1`

* Description:

    Drainer `checkpoint` has not been updated for one minute.

* Solution:

    Check whether all the Pumps that are not offline are running normally.
#### `binlog_drainer_execute_duration_time_more_than_10s`

* Alert rule:

    `histogram_quantile(0.9, rate(binlog_drainer_execute_duration_time_bucket[1m])) > 10`

* Description:

    The transaction time it takes Drainer to replicate data to TiDB. If it is too large, the Drainer replication of data is affected.

* Solution:

    - Check the TiDB cluster state.
    - Check the Drainer log or monitor. If a DDL operation causes this problem, you can ignore it.
