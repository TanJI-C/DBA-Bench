# TiKV emergency and critical alert rules for memory, GC, connectivity, raft, storage, and coprocessor pressure

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/alert-rules.md`
- Source Title: `TiDB Cluster Alert Rules`
- Source Heading Path: `TiDB Cluster Alert Rules > TiKV alert rules | TiDB Cluster Alert Rules > TiKV alert rules > Emergency-level alerts | TiDB Cluster Alert Rules > TiKV alert rules > Emergency-level alerts > `TiKV_memory_used_too_fast` | TiDB Cluster Alert Rules > TiKV alert rules > Emergency-level alerts > `TiKV_GC_can_not_work` | TiDB Cluster Alert Rules > TiKV alert rules > Critical-level alerts | TiDB Cluster Alert Rules > TiKV alert rules > Critical-level alerts > `TiKV_server_report_failure_msg_total` | TiDB Cluster Alert Rules > TiKV alert rules > Critical-level alerts > `TiKV_channel_full_total` | TiDB Cluster Alert Rules > TiKV alert rules > Critical-level alerts > `TiKV_write_stall` | TiDB Cluster Alert Rules > TiKV alert rules > Critical-level alerts > `TiKV_raft_log_lag` | TiDB Cluster Alert Rules > TiKV alert rules > Critical-level alerts > `TiKV_async_request_snapshot_duration_seconds` | TiDB Cluster Alert Rules > TiKV alert rules > Critical-level alerts > `TiKV_async_request_write_duration_seconds` | TiDB Cluster Alert Rules > TiKV alert rules > Critical-level alerts > `TiKV_coprocessor_request_wait_seconds` | TiDB Cluster Alert Rules > TiKV alert rules > Critical-level alerts > `TiKV_raftstore_thread_cpu_seconds_total``
- Source Line Ranges: `419-576`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`, `shared`
- Topic Tags: `alert-rules`, `tikv`, `emergency-alerts`, `critical-alerts`, `memory-usage`, `gc`, `network-connectivity`, `raftstore`, `write-stall`, `raft-log`, `snapshot-latency`, `write-latency`, `coprocessor`, `cpu-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0004_34bd9d9060`
- Source ID: `tidb-docs-8.1:alert-rules.md#tikv-alert-rules`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `849ae36cd77dda42f867cab170a8bffad177da2b7e85419382843f8a688d499d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/alert-rules#tikv-alert-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/alert-rules.md

## Retrieval Guidance

- Use When: Use this chunk when investigating TiKV emergency-level or critical-level alerts involving fast memory growth, GC not working, unreachable TiKV peers, channel full events, write stalls, raft log lag, snapshot or write latency, coprocessor wait time, or Raftstore CPU pressure.
- Retrieval Keywords: TiKV_memory_used_too_fast, process_resident_memory_bytes, block-cache-size, rocksdb.defaultcf, rocksdb.writecf, TiKV_GC_can_not_work, tikv_gcworker_gc_tasks_vec{task="gc"}, tikv_gc_compaction_filter_perform, tikv_engine_event_total{db="kv", cf="write", type="compaction"}, SELECT VARIABLE_VALUE FROM mysql.tidb WHERE VARIABLE_NAME = "tikv_gc_leader_desc", gc_worker tidb.log, TiKV_server_report_failure_msg_total, tikv_server_report_failure_msg_total{type="unreachable"}, TiKV_channel_full_total, tikv_channel_full_total, raftstore.raft-base-tick-interval, TiKV_write_stall, tikv_engine_write_stall, max-sub-compactions, TiKV_raft_log_lag, tikv_raftstore_log_lag_bucket, TiKV_async_request_snapshot_duration_seconds, tikv_storage_engine_async_request_duration_seconds_bucket{type="snapshot"}, TiKV_async_request_write_duration_seconds, tikv_storage_engine_async_request_duration_seconds_bucket{type="write"}, TiKV_coprocessor_request_wait_seconds, tikv_coprocessor_request_wait_seconds_bucket, over seek bound, TiKV_raftstore_thread_cpu_seconds_total, tikv_thread_cpu_seconds_total{name=~"raftstore_.*"}, raftstore.store-pool-size, Raft Propose dashboard, Raft IO dashboard, Raft process dashboard
- Follow-up Guidance: The content includes follow-up checks in TiDB logs, Grafana dashboards, SQL for locating the GC leader, network and disk inspection, hotspot checks, and specific configuration items such as `raftstore.raft-base-tick-interval`, `max-sub-compactions`, and `block-cache-size`.
- Classification Note: The official content classifies these as TiKV alert rules spanning emergency-level alerts for memory and GC and critical-level alerts for connectivity, Raftstore pressure, storage stalls, latency, coprocessor pressure, and CPU usage.

## Official Source Content

## TiKV alert rules

This section gives the alert rules for the TiKV component.
### Emergency-level alerts
#### `TiKV_memory_used_too_fast`

* Alert rule:

    `process_resident_memory_bytes{job=~"tikv",instance=~".*"} - (process_resident_memory_bytes{job=~"tikv",instance=~".*"} offset 5m) > 5*1024*1024*1024`

* Description:

    Currently, there are no TiKV monitoring items about memory. You can monitor the memory usage of the machines in the cluster by Node_exporter. The above rule indicates that when the memory usage exceeds 5 GB within 5 minutes (the memory is occupied too fast in TiKV), an alert is triggered.

* Solution:

    Adjust the `block-cache-size` value of both `rocksdb.defaultcf` and `rocksdb.writecf`.
#### `TiKV_GC_can_not_work`

* Alert rule:

    `sum(increase(tikv_gcworker_gc_tasks_vec{task="gc"}[1d])) < 1 and (sum(increase(tikv_gc_compaction_filter_perform[1d])) < 1 and sum(increase(tikv_engine_event_total{db="kv", cf="write", type="compaction"}[1d])) >= 1)`

* Description:

    GC is not performed successfully on a TiKV instance within 24 hours, which indicates that GC is not working properly. If GC does not run in a short term, it will not cause much trouble; but if GC keeps down, more and more versions are retained, which slows down the query.

* Solution:

    1. Perform `SELECT VARIABLE_VALUE FROM mysql.tidb WHERE VARIABLE_NAME = "tikv_gc_leader_desc"` to locate the `tidb-server` corresponding to the GC leader;
    2. View the log of the `tidb-server`, and grep gc_worker tidb.log;
    3. If you find that the GC worker has been resolving locks (the last log is "start resolve locks") or deleting ranges (the last log is "start delete {number} ranges") during this time, it means the GC process is running normally. Otherwise, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.
### Critical-level alerts
#### `TiKV_server_report_failure_msg_total`

* Alert rule:

    `sum(rate(tikv_server_report_failure_msg_total{type="unreachable"}[10m])) BY (store_id) > 10`

* Description:

    Indicates that the remote TiKV cannot be connected.

* Solution:

    1. Check whether the network is clear.
    2. Check whether the remote TiKV is down.
    3. If the remote TiKV is not down, check whether the pressure is too high. Refer to the solution in [`TiKV_channel_full_total`](#tikv_channel_full_total).
#### `TiKV_channel_full_total`

* Alert rule:

    `sum(rate(tikv_channel_full_total[10m])) BY (type, instance) > 0`

* Description:

    This issue is often caused by the stuck Raftstore thread and high pressure on TiKV.

* Solution:

    1. Watch the [**TiKV-Details** > **Raft Propose** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#raft-propose), and see whether the alerted TiKV node has a much higher Raft propose than other TiKV nodes. If so, it means that there are one or more hot spots on this TiKV. You need to check whether the hot spot scheduling can work properly.
    2. Watch the [**TiKV-Details** > **Raft IO** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#raft-io), and see whether the latency increases. If the latency is high, it means a bottleneck might exist in the disk.
    3. Watch the [**TiKV-Details** > **Raft process** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#raft-process), and see whether the `tick duration` is high. If so, you need to set [`raftstore.raft-base-tick-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#raft-base-tick-interval) to `"2s"`.
#### `TiKV_write_stall`

* Alert rule:

    `delta(tikv_engine_write_stall[10m]) > 0`

* Description:

    The write pressure on RocksDB is too high, and a stall occurs.

* Solution:

    1. View the disk monitor, and troubleshoot the disk issues;
    2. Check whether there is any write hot spot on the TiKV;
    3. Set `max-sub-compactions` to a larger value under the `[rocksdb]` and `[raftdb]` configurations.
#### `TiKV_raft_log_lag`

* Alert rule:

    `histogram_quantile(0.99, sum(rate(tikv_raftstore_log_lag_bucket[1m])) by (le, instance)) > 5000`

* Description:

    If this value is relatively large, it means Follower has lagged far behind Leader, and Raft cannot be replicated normally. It is possibly because the TiKV machine where Follower is located is stuck or down.
#### `TiKV_async_request_snapshot_duration_seconds`

* Alert rule:

    `histogram_quantile(0.99, sum(rate(tikv_storage_engine_async_request_duration_seconds_bucket{type="snapshot"}[1m])) by (le, instance, type)) > 1`

* Description:

    If this value is relatively large, it means the load pressure on Raftstore is too high, and it might be stuck already.

* Solution:

    Refer to the solution in [`TiKV_channel_full_total`](#tikv_channel_full_total).
#### `TiKV_async_request_write_duration_seconds`

* Alert rule:

    `histogram_quantile(0.99, sum(rate(tikv_storage_engine_async_request_duration_seconds_bucket{type="write"}[1m])) by (le, instance, type)) > 1`

* Description:

    If this value is relatively large, it means the Raft write takes a long time.

* Solution:

    1. Watch the [**TiKV-Details** > **Raft propose** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#raft-propose) and see whether the **99% Propose wait duration per server** metric of the alerted TiKV node is significantly higher than that of other TiKV nodes. If so, it indicates that hotspots exist on this TiKV node, and you need to check whether the hotspot scheduling works properly.
    2. Watch the [**TiKV-Details** > **Raft IO** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#raft-io) and see whether the latency increases. If the latency is high, it means a bottleneck might exist in the disk.
    3. For further analysis of performance issues of the alerted TiKV node and tuning methods, see [Performance analysis and tuning](https://docs.pingcap.com/tidb/stable/performance-tuning-methods#storage-async-write-duration-store-duration-and-apply-duration).
#### `TiKV_coprocessor_request_wait_seconds`

* Alert rule:

    `histogram_quantile(0.9999, sum(rate(tikv_coprocessor_request_wait_seconds_bucket[1m])) by (le, instance, req)) > 10`

* Description:

    If this value is relatively large, it means the pressure on the Coprocessor worker is high. There might be a slow task that makes the Coprocessor thread stuck.

* Solution:

    1. View the slow query log from the TiDB log to see whether the index or full table scan is used in a query, or see whether it is needed to analyze;
    2. Check whether there is a hot spot;
    3. View the Coprocessor monitor and see whether `total` and `process` in `coprocessor table/index scan` match. If they differ a lot, it indicates too many invalid queries are performed. You can see whether there is `over seek bound`. If so, there are too many versions that GC does not handle in time. Then you need to increase the number of parallel GC threads.
#### `TiKV_raftstore_thread_cpu_seconds_total`

* Alert rule:

    `sum(rate(tikv_thread_cpu_seconds_total{name=~"raftstore_.*"}[1m])) by (instance) > 1.6`

* Description:

    This rule monitors CPU usage by Raftstore. If the value is high, it indicates pressure on Raftstore threads is heavy.

    The alert threshold is 80% of the [`raftstore.store-pool-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#store-pool-size) value. `raftstore.store-pool-size` is 2 by default, so the alert threshold is 1.6.

* Solution:

    Refer to the solution in [`TiKV_channel_full_total`](#tikv_channel_full_total).
