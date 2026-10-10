# TiDB component alert rules

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/alert-rules.md`
- Source Title: `TiDB Cluster Alert Rules`
- Source Heading Path: `TiDB Cluster Alert Rules > TiDB alert rules | TiDB Cluster Alert Rules > TiDB alert rules > Emergency-level alerts | TiDB Cluster Alert Rules > TiDB alert rules > Emergency-level alerts > `TiDB_schema_error` | TiDB Cluster Alert Rules > TiDB alert rules > Emergency-level alerts > `TiDB_tikvclient_region_err_total` | TiDB Cluster Alert Rules > TiDB alert rules > Emergency-level alerts > `TiDB_domain_load_schema_total` | TiDB Cluster Alert Rules > TiDB alert rules > Critical-level alerts | TiDB Cluster Alert Rules > TiDB alert rules > Critical-level alerts > `TiDB_server_panic_total` | TiDB Cluster Alert Rules > TiDB alert rules > Warning-level alerts | TiDB Cluster Alert Rules > TiDB alert rules > Warning-level alerts > `TiDB_memory_abnormal` | TiDB Cluster Alert Rules > TiDB alert rules > Warning-level alerts > `TiDB_query_duration` | TiDB Cluster Alert Rules > TiDB alert rules > Warning-level alerts > `TiDB_server_event_error` | TiDB Cluster Alert Rules > TiDB alert rules > Warning-level alerts > `TiDB_tikvclient_backoff_seconds_count` | TiDB Cluster Alert Rules > TiDB alert rules > Warning-level alerts > `TiDB_monitor_time_jump_back_error` | TiDB Cluster Alert Rules > TiDB alert rules > Warning-level alerts > `TiDB_ddl_waiting_jobs``
- Source Line Ranges: `20-173`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `alert-rules`, `schema-reload`, `region-cache`, `panic`, `memory-usage`, `query-latency`, `binlog`, `backoff`, `ntp`, `ddl-jobs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0001_90c0aa4e2b`
- Source ID: `tidb-docs-8.1:alert-rules.md#tidb-alert-rules`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `53dce91ff8f8d5627ae23a47bd90d1ebbaa88a560ad4452a293dbab5ea0500c5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/alert-rules#tidb-alert-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/alert-rules.md

## Retrieval Guidance

- Use When: Use this chunk when the user is investigating TiDB alert rules, their Prometheus expressions, descriptions, or listed solutions for schema reload failures, Region cache errors, panic events, memory usage, query latency, binlog hang events, TiKV backoff, time rewind, or DDL waiting jobs.
- Retrieval Keywords: TiDB alert rules, TiDB_schema_error, tidb_session_schema_lease_error_total, TiDB_tikvclient_region_err_total, tidb_tikvclient_region_err_total, TiDB_domain_load_schema_total, tidb_domain_load_schema_total, TiDB_server_panic_total, tidb_server_panic_total, TiDB_memory_abnormal, go_memstats_heap_inuse_bytes, TiDB_query_duration, tidb_server_handle_query_duration_seconds_bucket, SLOW_QUERY, TIME_COP_PROCESS, TiDB_server_event_error, tidb_server_event_total, server_start, server_hang, TiDB_tikvclient_backoff_seconds_count, tidb_tikvclient_backoff_seconds_count, TiDB_monitor_time_jump_back_error, tidb_monitor_time_jump_back_total, TiDB_ddl_waiting_jobs, tidb_ddl_waiting_jobs, admin show ddl, TiKV-Details Cluster dashboard
- Follow-up Guidance: The source points to checking TiKV monitoring items or the TiKV-Details > Cluster dashboard for TiKV-related causes, and to TiDB logs or `admin show ddl` for specific warning alerts.
- Classification Note: This is observability content because it enumerates TiDB alert rules with alert expressions, symptom descriptions, and monitoring-oriented troubleshooting guidance.

## Official Source Content

## TiDB alert rules

This section gives the alert rules for the TiDB component.
### Emergency-level alerts
#### `TiDB_schema_error`

* Alert rule:

    `increase(tidb_session_schema_lease_error_total{type="outdated"}[15m]) > 0`

* Description:

    The latest schema information is not reloaded in TiDB within one lease. When TiDB fails to continue providing services, an alert is triggered.

* Solution:

    It is often caused by an unavailable Region or a TiKV timeout. You need to locate the issue by checking the TiKV monitoring items.
#### `TiDB_tikvclient_region_err_total`

* Alert rule:

    `increase(tidb_tikvclient_region_err_total[10m]) > 6000`

* Description:

    TiDB server accesses the Region leader of TiKV according to its own cache information. If the Region leader has changed or the current TiKV Region information is inconsistent with that in the TiDB cache, a Region cache error occurs. When the error is reported over 6000 times in 10 minutes, an alert is triggered.

* Solution:

    View [**TiKV-Details** > **Cluster** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#cluster) to see if the leader is balanced.
#### `TiDB_domain_load_schema_total`

* Alert rule:

    `increase(tidb_domain_load_schema_total{type="failed"}[10m]) > 10`

* Description:

    The total number of failures to reload the latest schema information in TiDB. If the reloading failure occurs over 10 times in 10 minutes, an alert is triggered.

* Solution:

    Same as [`TiDB_schema_error`](#tidb_schema_error).
### Critical-level alerts
#### `TiDB_server_panic_total`

* Alert rule:

    `increase(tidb_server_panic_total[10m]) > 0`

* Description:

    The number of panicked TiDB threads. When a panic occurs, an alert is triggered. The thread is often recovered, otherwise, TiDB will frequently restart.

* Solution:

    Collect the panic logs to locate the issue.
### Warning-level alerts
#### `TiDB_memory_abnormal`

* Alert rule:

    `go_memstats_heap_inuse_bytes{job="tidb"} > 1e+10`

* Description:

    The monitoring on the TiDB memory usage. If the usage exceeds 10 G, an alert is triggered.

* Solution:

    Use the HTTP API to troubleshoot the goroutine leak issue.
#### `TiDB_query_duration`

* Alert rule:

    `histogram_quantile(0.99, sum(rate(tidb_server_handle_query_duration_seconds_bucket[1m])) BY (le, instance)) > 1`

* Description:

    The latency of handling a request in TiDB. The response time for 99% of requests should be within 1 second; otherwise, an alert is triggered.

* Solution:

    View TiDB logs and search for the `SLOW_QUERY` and `TIME_COP_PROCESS` keywords to locate the slow SQL queries.
#### `TiDB_server_event_error`

* Alert rule:

    `increase(tidb_server_event_total{type=~"server_start|server_hang"}[15m]) > 0`

* Description:

    The number of events that happen in the TiDB service. An alert is triggered when the following events happen:

    1. start: The TiDB service starts.
    2. hang: When a critical-level event (currently there is only one scenario: TiDB cannot write binlog) happens, TiDB enters the `hang` mode and waits to be killed manually.

* Solution:

    * Restart TiDB to recover the service.
    * Check whether the TiDB Binlog service is normal.
#### `TiDB_tikvclient_backoff_seconds_count`

* Alert rule:

    `increase(tidb_tikvclient_backoff_seconds_count[10m]) > 10`

* Description:

    The number of retries when TiDB fails to access TiKV. When the retry times is over 10 in 10 minutes, an alert is triggered.

* Solution:

    View the monitoring status of TiKV.
#### `TiDB_monitor_time_jump_back_error`

* Alert rule:

    `increase(tidb_monitor_time_jump_back_total[10m]) > 0`

* Description:

    When the time of the machine that holds TiDB rewinds, an alert is triggered.

* Solution:

    Troubleshoot the NTP configurations.
#### `TiDB_ddl_waiting_jobs`

* Alert rule:

    `sum(tidb_ddl_waiting_jobs) > 5`

* Description:

    When the number of DDL tasks pending for execution in TiDB exceeds 5, an alert is triggered.

* Solution:

    Check whether there is any time-consuming `add index` operation that is being executed by running `admin show ddl`.
