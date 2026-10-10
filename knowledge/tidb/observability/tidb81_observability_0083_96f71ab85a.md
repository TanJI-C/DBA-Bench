# TiCDC alert rules and suggested handling

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-alert-rules.md`
- Source Title: `TiCDC Alert Rules`
- Source Heading Path: `TiCDC Alert Rules | TiCDC Alert Rules > Critical alerts | TiCDC Alert Rules > Critical alerts > `cdc_checkpoint_high_delay` | TiCDC Alert Rules > Critical alerts > `cdc_resolvedts_high_delay` | TiCDC Alert Rules > Critical alerts > `ticdc_changefeed_failed` | TiCDC Alert Rules > Warning alerts | TiCDC Alert Rules > Warning alerts > `cdc_multiple_owners` | TiCDC Alert Rules > Warning alerts > `cdc_no_owner` | TiCDC Alert Rules > Warning alerts > `ticdc_changefeed_meet_error` | TiCDC Alert Rules > Warning alerts > `ticdc_processor_exit_with_error_count` | TiCDC Alert Rules > Warning alerts > `tikv_cdc_min_resolved_ts_no_change_for_1m` | TiCDC Alert Rules > Warning alerts > `tikv_cdc_scan_duration_seconds_more_than_10min` | TiCDC Alert Rules > Warning alerts > `ticdc_sink_execution_error` | TiCDC Alert Rules > Warning alerts > `ticdc_memory_abnormal``
- Source Line Ranges: `5-171`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tikv`
- Topic Tags: `alerting`, `critical-alerts`, `warning-alerts`, `monitoring-metrics`, `replication-delay`, `changefeed-errors`, `owner-election`, `sink-errors`, `memory-usage`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0083_96f71ab85a`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-alert-rules.md#ticdc-alert-rules`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `43aa6517093f5b8878218a5a385cc82b4a75ccf0371cf5a421caf32ab685e717`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-alert-rules#ticdc-alert-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-alert-rules.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving official descriptions, alert rules, severity levels, and suggested handling for TiCDC alerts such as replication delay, changefeed errors, owner election anomalies, sink errors, TiKV CDC resolved-ts or scan issues, and TiCDC memory usage.
- Retrieval Keywords: TiCDC Alert Rules, Critical alerts, Warning alerts, cdc_checkpoint_high_delay, ticdc_owner_checkpoint_ts_lag > 600, replication task is delayed more than 10 minutes, cdc_resolvedts_high_delay, ticdc_owner_resolved_ts_lag > 300, Resolved TS of a replication task is delayed more than 5 minutes, ticdc_changefeed_failed, max_over_time(ticdc_owner_status[1m]) == 2, failed state, cdc_multiple_owners, sum(rate(ticdc_owner_ownership_counter[30s])) >= 2, multiple owners in the TiCDC cluster, cdc_no_owner, sum(rate(ticdc_owner_ownership_counter[240s])) < 0.5, no owner in the TiCDC cluster for more than 10 minutes, ticdc_changefeed_meet_error, max_over_time(ticdc_owner_status[1m]) == 1, max_over_time(ticdc_owner_status[1m]) == 6, ticdc_processor_exit_with_error_count, changes(ticdc_processor_exit_with_error_count[1m]) > 0, tikv_cdc_min_resolved_ts_no_change_for_1m, changes(tikv_cdc_min_resolved_ts[1m]) < 1, tikv_cdc_region_resolve_status{status="resolved"} > 0, tikv_cdc_captured_region_total > 0, tikv_cdc_scan_duration_seconds_more_than_10min, histogram_quantile(0.9, rate(tikv_cdc_scan_duration_seconds_bucket{}[1m])) > 600, ticdc_sink_execution_error, changes(ticdc_sink_execution_error[1m]) > 0, ticdc_memory_abnormal, go_memstats_heap_alloc_bytes{job="ticdc"} > 1e+10, TiCDC Handles Replication Interruption, Troubleshoot TiCDC, Collect TiCDC logs, Collect TiKV logs, Collect TiCDC monitoring metrics
- Follow-up Guidance: For replication interruption style alerts, the source points to TiCDC Handles Replication Interruption, and for sink write errors it points to Troubleshoot TiCDC.
- Classification Note: The official content classifies these TiCDC monitoring rules into Critical and Warning severities and ties each alert name to a specific metric expression, description, and suggested handling.

## Official Source Content

# TiCDC Alert Rules

This document describes the TiCDC alert rules and the corresponding solutions. In descending order, the severity levels are: **Critical**, **Warning**.
## Critical alerts

This section introduces critical alerts and solutions.
### `cdc_checkpoint_high_delay`

For critical alerts, you need to pay close attention to abnormal monitoring metrics.

- Alert rule:

    `ticdc_owner_checkpoint_ts_lag > 600`

- Description:

    A replication task is delayed more than 10 minutes.

- Solution:

    See [TiCDC Handles Replication Interruption](https://docs.pingcap.com/tidb/stable/ticdc/troubleshoot-ticdc#how-do-i-handle-replication-interruptions).
### `cdc_resolvedts_high_delay`

- Alert rule:

    `ticdc_owner_resolved_ts_lag > 300`

- Description:

     The Resolved TS of a replication task is delayed more than 5 minutes.

- Solution:

    See [TiCDC Handles Replication Interruption](https://docs.pingcap.com/tidb/stable/ticdc/troubleshoot-ticdc#how-do-i-handle-replication-interruptions).
### `ticdc_changefeed_failed`

- Alert rule:

    `(max_over_time(ticdc_owner_status[1m]) == 2) > 0`

- Description:

    A replication task encounters an unrecoverable error and enters the failed state.

- Solution:

    This alert is similar to replication interruption. See [TiCDC Handles Replication Interruption](https://docs.pingcap.com/tidb/stable/ticdc/troubleshoot-ticdc#how-do-i-handle-replication-interruptions).
## Warning alerts

Warning alerts are a reminder for an issue or error.
### `cdc_multiple_owners`

- Alert rule:

    `sum(rate(ticdc_owner_ownership_counter[30s])) >= 2`

- Description:

    There are multiple owners in the TiCDC cluster.

- Solution:

    Collect TiCDC logs to locate the root cause.
### `cdc_no_owner`

- Alert rule:

    `sum(rate(ticdc_owner_ownership_counter[240s])) < 0.5`

- Description:

    There is no owner in the TiCDC cluster for more than 10 minutes.

- Solution:

    Collect TiCDC logs to identify the root cause.
### `ticdc_changefeed_meet_error`

- Alert rule:

    `(max_over_time(ticdc_owner_status[1m]) == 1 or max_over_time(ticdc_owner_status[1m]) == 6) > 0`

- Description:

    A replication task encounters an error.

- Solution:

    See [TiCDC Handles Replication Interruption](https://docs.pingcap.com/tidb/stable/ticdc/troubleshoot-ticdc#how-do-i-handle-replication-interruptions).
### `ticdc_processor_exit_with_error_count`

- Alert rule:

    `changes(ticdc_processor_exit_with_error_count[1m]) > 0`

- Description:

    A replication task reports an error and exits.

- Solution:

    See [TiCDC Handles Replication Interruption](https://docs.pingcap.com/tidb/stable/ticdc/troubleshoot-ticdc#how-do-i-handle-replication-interruptions).
### `tikv_cdc_min_resolved_ts_no_change_for_1m`

- Alert rule:

    `changes(tikv_cdc_min_resolved_ts[1m]) < 1 and ON (instance) tikv_cdc_region_resolve_status{status="resolved"} > 0 and ON (instance) tikv_cdc_captured_region_total > 0`

- Description:

    The minimum Resolved TS 1 of TiKV CDC has not advanced for 1 minute.

- Solution:

    Collect TiKV logs to locate the root cause.
### `tikv_cdc_scan_duration_seconds_more_than_10min`

- Alert rule:

    `histogram_quantile(0.9, rate(tikv_cdc_scan_duration_seconds_bucket{}[1m])) > 600`

- Description:

    The TiKV CDC module has scanned for incremental replication for more than 10 minutes.

- Solution:

    Collect TiCDC monitoring metrics and TiKV logs to locate the root cause.
### `ticdc_sink_execution_error`

- Alert rule:

    `changes(ticdc_sink_execution_error[1m]) > 0`

- Description:

    An error occurs when a replication task writes data to the downstream.

- Solution:

    There are many possible root causes. See [Troubleshoot TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/troubleshoot-ticdc).
### `ticdc_memory_abnormal`

- Alert rule:

    `go_memstats_heap_alloc_bytes{job="ticdc"} > 1e+10`

- Description:

    The TiCDC heap memory usage exceeds 10 GiB.

- Solution:

    Collect TiCDC logs to locate the root cause.
