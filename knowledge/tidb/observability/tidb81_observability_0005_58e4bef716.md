# TiKV alert rules: raft, scheduler, coprocessor, capacity, and task alerts

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/alert-rules.md`
- Source Title: `TiDB Cluster Alert Rules`
- Source Heading Path: `TiDB Cluster Alert Rules > TiKV alert rules > Critical-level alerts > `TiKV_raft_append_log_duration_secs` | TiDB Cluster Alert Rules > TiKV alert rules > Critical-level alerts > `TiKV_raft_apply_log_duration_secs` | TiDB Cluster Alert Rules > TiKV alert rules > Critical-level alerts > `TiKV_scheduler_latch_wait_duration_seconds` | TiDB Cluster Alert Rules > TiKV alert rules > Critical-level alerts > `TiKV_thread_apply_worker_cpu_seconds` | TiDB Cluster Alert Rules > TiKV alert rules > Warning-level alerts | TiDB Cluster Alert Rules > TiKV alert rules > Warning-level alerts > `TiKV_leader_drops` | TiDB Cluster Alert Rules > TiKV alert rules > Warning-level alerts > `TiKV_raft_process_ready_duration_secs` | TiDB Cluster Alert Rules > TiKV alert rules > Warning-level alerts > `TiKV_raft_process_tick_duration_secs` | TiDB Cluster Alert Rules > TiKV alert rules > Warning-level alerts > `TiKV_scheduler_context_total` | TiDB Cluster Alert Rules > TiKV alert rules > Warning-level alerts > `TiKV_scheduler_command_duration_seconds` | TiDB Cluster Alert Rules > TiKV alert rules > Warning-level alerts > `TiKV_coprocessor_outdated_request_wait_seconds` | TiDB Cluster Alert Rules > TiKV alert rules > Warning-level alerts > `TiKV_coprocessor_pending_request` | TiDB Cluster Alert Rules > TiKV alert rules > Warning-level alerts > `TiKV_batch_request_snapshot_nums` | TiDB Cluster Alert Rules > TiKV alert rules > Warning-level alerts > `TiKV_pending_task` | TiDB Cluster Alert Rules > TiKV alert rules > Warning-level alerts > `TiKV_low_space` | TiDB Cluster Alert Rules > TiKV alert rules > Warning-level alerts > `TiKV_approximate_region_size``
- Source Line Ranges: `577-773`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `tidb`
- Topic Tags: `alert-rules`, `monitoring`, `raft`, `scheduler`, `coprocessor`, `cpu`, `io`, `latency`, `disk-space`, `region-split`, `tasks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0005_58e4bef716`
- Source ID: `tidb-docs-8.1:alert-rules.md#tikv-raft-append-log-duration-secs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `76c288d8c2a33d54b015275f5f0ad6706f6fc56649a1359946f9971e3b3535d3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/alert-rules#tikv-raft-append-log-duration-secs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/alert-rules.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiKV alert rule descriptions, Prometheus expressions, and listed solutions for raft, scheduler, coprocessor, pending task, low space, or approximate Region size alerts in a self-managed TiDB cluster.
- Retrieval Keywords: TiKV_raft_append_log_duration_secs, tikv_raftstore_append_log_duration_seconds_bucket, TiKV_raft_apply_log_duration_secs, tikv_raftstore_apply_log_duration_seconds_bucket, TiKV_scheduler_latch_wait_duration_seconds, tikv_scheduler_latch_wait_duration_seconds_bucket, Scheduler-${cmd}, TiKV_thread_apply_worker_cpu_seconds, tikv_thread_cpu_seconds_total{name=~"apply_.*"}, TiKV_leader_drops, tikv_pd_heartbeat_tick_total{type="leader"}, TiKV_raft_process_ready_duration_secs, TiKV_raft_process_tick_duration_secs, raft-base-tick-interval = "2s", TiKV_scheduler_context_total, tikv_scheduler_context_total, TiKV_scheduler_command_duration_seconds, tikv_scheduler_command_duration_seconds_bucket, TiKV_coprocessor_outdated_request_wait_seconds, tikv_coprocessor_outdated_request_wait_seconds_count, TiKV_coprocessor_pending_request, tikv_coprocessor_pending_request, TiKV_batch_request_snapshot_nums, name=~"cop_.*", TiKV_pending_task, tikv_worker_pending_task_total, Worker pending tasks, TiKV_low_space, tikv_store_size_bytes{type="available"}, TiKV_approximate_region_size, tikv_raftstore_region_size_bucket, pd-ctl operator add split-region <region_id> --policy=approximate
- Follow-up Guidance: Several alert entries refer to related items such as `TiKV_channel_full_total`, `TiKV_scheduler_latch_wait_duration_seconds`, and `TiKV_coprocessor_request_wait_seconds`, and some solutions point to Grafana monitors or the `TiKV-Details` > `Task` dashboard.
- Classification Note: The supplied content is observability documentation because it defines TiKV alert rules with alert expressions, descriptions, severity levels, and troubleshooting-oriented solutions.

## Official Source Content

#### `TiKV_raft_append_log_duration_secs`

* Alert rule:

    `histogram_quantile(0.99, sum(rate(tikv_raftstore_append_log_duration_seconds_bucket[1m])) by (le, instance)) > 1`

* Description:

    Indicates the time cost of appending Raft log. If it is high, it usually means I/O is too busy.
#### `TiKV_raft_apply_log_duration_secs`

* Alert rule:

    `histogram_quantile(0.99, sum(rate(tikv_raftstore_apply_log_duration_seconds_bucket[1m])) by (le, instance)) > 1`

* Description:

    Indicates the time cost of applying Raft log. If it is high, it usually means I/O is too busy.
#### `TiKV_scheduler_latch_wait_duration_seconds`

* Alert rule:

    `histogram_quantile(0.99, sum(rate(tikv_scheduler_latch_wait_duration_seconds_bucket[1m])) by (le, instance, type)) > 1`

* Description:

    The waiting time for the write operations to obtain the memory lock in Scheduler. If it is high, there might be many write conflicts, or that some operations that lead to conflicts take a long time to finish and block other operations that wait for the same lock.

* Solution:

    1. Identify the most time-consuming command by viewing the scheduler command duration in the `Scheduler` and `Scheduler-${cmd}` (`${cmd}` is the write command to query) monitors;
    2. Check the `total` and `process` values in the scheduler scan details of the `Scheduler` and `Scheduler-${cmd}` monitors and see whether `total` and `process` match.
    3. View the storage async snapshot/write duration in the Storage monitor and see whether the Raft operation is performed in time.
#### `TiKV_thread_apply_worker_cpu_seconds`

* Alert rule:

    `max(rate(tikv_thread_cpu_seconds_total{name=~"apply_.*"}[1m])) by (instance) > 0.9`

* Description:

    The apply Raft log thread is under great pressure and is approaching or has exceeded its limit. This is often caused by a burst of writes.
### Warning-level alerts
#### `TiKV_leader_drops`

* Alert rule:

    `delta(tikv_pd_heartbeat_tick_total{type="leader"}[30s]) < -10`

* Description:

    It is often caused by a stuck Raftstore thread.

* Solution:

    1. Refer to [`TiKV_channel_full_total`](#tikv_channel_full_total).
    2. It there is low pressure on TiKV, consider whether the PD scheduling is too frequent. You can view the Operator Create panel on the PD page, and check the types and number of the PD scheduling.
#### `TiKV_raft_process_ready_duration_secs`

* Alert rule:

    `histogram_quantile(0.999, sum(rate(tikv_raftstore_raft_process_duration_secs_bucket{type='ready'}[1m])) by (le, instance, type)) > 2`

* Description:

    Indicates the time cost of handling Raft ready. If this value is large, it is often caused by the stuck appending log task.
#### `TiKV_raft_process_tick_duration_secs`

* Alert rule:

    `histogram_quantile(0.999, sum(rate(tikv_raftstore_raft_process_duration_secs_bucket{type='tick'}[1m])) by (le, instance, type)) > 2`

* Description:

    Indicates the time cost of handling Raft tick. If this value is large, it is often caused by too many Regions.

* Solution:

    1. Consider using a higher-level log such as `warn` or `error`.
    2. Add `raft-base-tick-interval = "2s"` under the `[raftstore]` configuration.
#### `TiKV_scheduler_context_total`

* Alert rule:

    `abs(delta( tikv_scheduler_context_total[5m])) > 1000`

* Description:

    The number of write commands that are being executed by Scheduler. If this value is large, it means the task is not finished timely.

* Solution:

    Refer to [`TiKV_scheduler_latch_wait_duration_seconds`](#tikv_scheduler_latch_wait_duration_seconds).
#### `TiKV_scheduler_command_duration_seconds`

* Alert rule:

    `histogram_quantile(0.99, sum(rate(tikv_scheduler_command_duration_seconds_bucket[1m])) by (le, instance, type)) > 1`

* Description:

    Indicates the time cost of executing the Scheduler command.

* Solution:

    Refer to [`TiKV_scheduler_latch_wait_duration_seconds`](#tikv_scheduler_latch_wait_duration_seconds).
#### `TiKV_coprocessor_outdated_request_wait_seconds`

* Alert rule:

    `delta(tikv_coprocessor_outdated_request_wait_seconds_count[10m]) > 0`

* Description:

    The waiting time of the expired requests by Coprocessor. If this value is large, it means there is high pressure on Coprocessor.

* Solution:

    Refer to [`TiKV_coprocessor_request_wait_seconds`](#tikv_coprocessor_request_wait_seconds).
#### `TiKV_coprocessor_pending_request`

* Alert rule:

    `delta(tikv_coprocessor_pending_request[10m]) > 5000`

* Description:

    The queuing requests of Coprocessor.

* Solution:

    Refer to [`TiKV_coprocessor_request_wait_seconds`](#tikv_coprocessor_request_wait_seconds).
#### `TiKV_batch_request_snapshot_nums`

* Alert rule:

    `sum(rate(tikv_thread_cpu_seconds_total{name=~"cop_.*"}[1m])) by (instance) / (count(tikv_thread_cpu_seconds_total{name=~"cop_.*"}) * 0.9) / count(count(tikv_thread_cpu_seconds_total) by (instance)) > 0`

* Description:

    The Coprocessor CPU usage of a TiKV machine exceeds 90%.
#### `TiKV_pending_task`

* Alert rule:

    `sum(tikv_worker_pending_task_total) BY (instance,name)  > 1000`

* Description:

    The number of pending tasks of TiKV.

* Solution:

    Check which kind of tasks has a higher value from the `Worker pending tasks` metric in the [**TiKV-Details** > **Task** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#task).
#### `TiKV_low_space`

* Alert rule:

    `sum(tikv_store_size_bytes{type="available"}) by (instance) / sum(tikv_store_size_bytes{type="capacity"}) by (instance) < 0.2`

* Description:

    The data volume of TiKV exceeds 80% of the configured node capacity or the disk capacity of the machine.

* Solution:

    * Check the balance condition of node space.
    * Make a plan to increase the disk capacity or delete some data or increase cluster node depending on different situations.
#### `TiKV_approximate_region_size`

* Alert rule:

    `histogram_quantile(0.99, sum(rate(tikv_raftstore_region_size_bucket[1m])) by (le)) > 1073741824`

* Description:

    The maximum Region approximate size that is scanned by the TiKV split checker is continually larger than 1 GB within one minute.

* Solution:

    The speed of splitting Regions is slower than the write speed. To alleviate this issue, you'd better update TiDB to a version that supports batch-split (>= 2.1.0-rc1). If it is not possible to update temporarily, you can use `pd-ctl operator add split-region <region_id> --policy=approximate` to manually split Regions.
