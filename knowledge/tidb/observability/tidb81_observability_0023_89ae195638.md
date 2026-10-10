# Overview monitoring sections in diagnostic report

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-diagnostics-report.md`
- Source Title: `TiDB Dashboard Diagnostic Report`
- Source Heading Path: `TiDB Dashboard Diagnostic Report > View report > Overview information > Time Consumed by Each Component | TiDB Dashboard Diagnostic Report > View report > Overview information > Errors Occurred in Each Component | TiDB Dashboard Diagnostic Report > View report > Overview information > Specific TiDB/PD/TiKV monitoring information | TiDB Dashboard Diagnostic Report > View report > Overview information > TiDB-related monitoring information | TiDB Dashboard Diagnostic Report > View report > Overview information > TiDB-related monitoring information > Time Consumed by TiDB Component | TiDB Dashboard Diagnostic Report > View report > Overview information > TiDB-related monitoring information > TiDB Server Connections | TiDB Dashboard Diagnostic Report > View report > Overview information > TiDB-related monitoring information > TiDB Transaction | TiDB Dashboard Diagnostic Report > View report > Overview information > TiDB-related monitoring information > DDL Owner | TiDB Dashboard Diagnostic Report > View report > Overview information > PD related monitoring information | TiDB Dashboard Diagnostic Report > View report > Overview information > TiKV related monitoring information`
- Source Line Ranges: `137-286`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `diagnostic-report`, `overview`, `monitoring-metrics`, `time-consumption`, `errors`, `transactions`, `ddl-owner`, `pd-monitoring`, `tikv-monitoring`, `connections`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0023_89ae195638`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-diagnostics-report.md#time-consumed-by-each-component`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `05cb15d633c6329f6dda500f6518303eaf34f354d57bb934f64b76caa5d2a195`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-diagnostics-report#time-consumed-by-each-component
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-diagnostics-report.md

## Retrieval Guidance

- Use When: Use this chunk when locating or interpreting TiDB Dashboard diagnostic report overview and component monitoring tables such as time consumption, errors, TiDB transactions, DDL owner, PD monitoring, and TiKV monitoring.
- Retrieval Keywords: Time Consumed by Each Component, Errors Occurred in Each Component, Specific TiDB/PD/TiKV monitoring information, Time Consumed by TiDB Component, TiDB Server Connections, TiDB Transaction, DDL Owner, Time Consumed by PD Component, Time Consumed by TiKV Component, TOTAL_TIME, TIME_RATIO, TOTAL_COUNT, P999, P99, tidb_query, kv_request, tikv_grpc_message, tikv_cop_wait, tikv_scheduler_command, tikv_storage_async_request, tikv_raft_process, tikv_raft_append_log, tikv_raft_commit_log, tikv_raft_apply_wait, tikv_raft_apply_log, tikv server is busy, TiKV channel full, tikv write stall, ddl_worker, Top 10 Slow Query, Slow Query With Diff Plan, Blance Leader/Region, Cluster Status, Store Status, Etcd Status, Time Consumed by RocksDB, TiKV Error, TiKV Engine Size, Coprocessor Info, Raft Info, Snapshot Info, GC Info, Cache Hit
- Follow-up Guidance: The content also points to related tables under TiDB, PD, and TiKV monitoring information, including slow query, cluster status, RocksDB, Raft, snapshot, GC, and cache hit tables.
- Classification Note: This is classified as observability for the dashboard component because it describes diagnostic report monitoring tables, metrics, error summaries, and how to read time-consumption relationships across TiDB, PD, and TiKV.

## Official Source Content

#### Time Consumed by Each Component

The `Time Consumed by Each Component` table shows the monitored consumed time and the time ratio of TiDB, PD, TiKV modules in the cluster. The default time unit is seconds. You can use this table to quickly locate which modules consume more time.

![Time Consume report](/media/dashboard/dashboard-diagnostics-total-time-consume.png)

The fields in columns of the table above are described as follows:

* `METRIC_NAME`: The name of the monitoring metric.
* `Label`: The label information for the monitoring metric. Click **expand** to view more detailed monitoring information of each label for a metric.
* `TIME_RATIO`: The ratio of the total time consumed by this monitoring metric to the total time of the monitoring row where `TIME_RATIO` is `1`. For example, the total consumed time by `kv_request` is `1.65` (namely, `38325.58`/`23223.86`) times that of `tidb_query`. Because KV requests are executed concurrently, the total time of all KV requests might exceed the total query (`tidb_query`) execution time.
* `TOTAL_TIME`: The total time consumed by this monitoring metric.
* `TOTAL_COUNT`: The total number of times this monitoring metric is executed.
* `P999`: The maximum P999 time of this monitoring metric.
* `P99`: The maximum P99 time of this monitoring metric.
* `P90`: The maximum P90 time of this monitoring metric.
* `P80`: The maximum P80 time of this monitoring metric.

The following image shows the relationship of time consumption of the related modules in the monitoring metrics above.

![Time-consumption relationship of each module](/media/dashboard/dashboard-diagnostics-time-relation.png)

In the image above, yellow boxes are the TiDB-related monitoring metrics.Blue boxes are TiKV-related monitoring metrics, and gray boxes temporarily do not correspond to specific monitoring metrics.

In the image above, the time consumption of `tidb_query` includes the following four parts:

* `get_token`
* `parse`
* `compile`
* `execute`

The `execute` time includes the following parts:

* `wait_start_tso`
* The execution time at the TiDB layer, which is currently not monitored
* KV request time
* `KV_backoff` time, which is the time for backoff after the KV request fails

Among the parts above, the KV request time includes the following parts:

* The time consumed by the network sending and receiving of requests. Currently, there is no monitoring metric for this item. You can subtract the time of `tikv_grpc_message` from the KV request time to roughly estimate this item.
* `tikv_grpc_message` time consumption.

Among the parts above, `tikv_grpc_message` time consumption includes the following parts:

* Coprocessor request time consumption, which refers to processing the COP type requests. This time consumption includes the following parts:
    * `tikv_cop_wait`: The time consumed by request queue.
    * `Coprocessor handle`: The time consumed to process Coprocessor requests.

* `tikv_scheduler_command` time consumption, which includes the following parts:
    * `tikv_scheduler_processing_read`: The time consumed to process read requests.
    * The time consumed to get snapshot in `tikv_storage_async_request` (snapshot is the label for this monitoring metric).
    * Time consumed to process write requests. This time consumption includes the following parts:
        * `tikv_scheduler_latch_wait`: The time consumed to wait for latch.
        * The time consumption of writes in `tikv_storage_async_request` (write is the label for this monitoring metric).

Among the above metrics, The time consumption of writes in `tikv_storage_async_request` refers to the time consumption of writing Raft KVs, including the following parts:

* `tikv_raft_propose_wait`
* `tikv_raft_process`, which mainly includes `tikv_raft_append_log`
* `tikv_raft_commit_log`
* `tikv_raft_apply_wait`
* `tikv_raft_apply_log`

You can use `TOTAL_TIME`, the P999 time, and the P99 time to determine which modules consume longer time according to the relationship between the time consumptions described above, and then look at the related monitoring metrics.

> **Note:**
>
> Because the Raft KVs writes might be processed in one batch, using `TOTAL_TIME` to measure the time consumed by each module is inapplicable to monitoring metrics related to Raft KV writes, specifically, `tikv_raft_process`, `tikv_raft_append_log`, `tikv_raft_commit_log`, `tikv_raft_apply_wait`, and `tikv_raft_apply_log`. In this situation, it is more reasonable to compare the time consumption of each module with the time of P999 and P99.
>
> The reason is that if there are 10 asynchronous write requests, Raft KVs internally pack 10 requests into a batch execution, and the execution time is 1 second. Therefore, the execution time of each request is 1 second, and the total time of 10 requests is 10 seconds, but the total time for Raft KV processing is 1 second. If you use `TOTAL_TIME` to measure the consumed time, you might not understand where the remaining 9 seconds are spent. You can also see the difference between the monitoring metric of Raft KV and other previous monitoring metrics from the total number of requests (`TOTAL_COUNT`).
#### Errors Occurred in Each Component

The `Errors Occurred in Each Component` table shows the total number of errors in TiDB and TiKV, such as the failure to write binlog, `tikv server is busy`, `TiKV channel full`, `tikv write stall`. You can see the row comments for the specific meaning of each error.

![Errors Occurred in Each Component report](/media/dashboard/dashboard-diagnostics-error.png)
#### Specific TiDB/PD/TiKV monitoring information

This part includes more specific monitoring information of TiDB, PD, or TiKV.
#### TiDB-related monitoring information
##### Time Consumed by TiDB Component

This table shows the time consumed by each TiDB module and the ratio of each time consumption, which is similar to the `time consume` table in the overview, but the label information of this table are more detailed.
##### TiDB Server Connections

This table shows the number of client connections for each TiDB instance.
##### TiDB Transaction

This table shows transaction-related monitoring metrics.

![Transaction report](/media/dashboard/dashboard-diagnostics-tidb-txn.png)

* `TOTAL_VALUE`: The sum of all values ​​(SUM) during the report time range.
* `TOTAL_COUNT`: The total number of occurrences of this monitoring metric.
* `P999`: The maximum P999 value of this monitoring metric.
* `P99`: The maximum P99 value of this monitoring metric.
* `P90`: The maximum P90 value of this monitoring metric.
* `P80`: The maximum P80 value of this monitoring metric.

Example:

In the table above, within the report time range, `tidb_txn_kv_write_size`: a total of about 181,296 transactions of KV writes, and the total KV write size is 266.772 MB, of which the maximum P999, P99, P90, P80 values for a single transaction of KV writes ​​are 116.913 KB, 1.996 KB, 1.905 KB, and 1.805 KB.
##### DDL Owner

![TiDB DDL Owner Report](/media/dashboard/dashboard-diagnostics-tidb-ddl.png)

The table above shows that from `2020-05-21 14:40:00`, the cluster's `DDL OWNER` is at the `10.0.1.13:10080` node. If the owner changes, multiple rows of data exist in the table above, where the `Min_Time` column indicates the minimum time of the corresponding known owner.

> **Note:**
>
> If the owner information is empty, it does not mean that no owner exists in this period of time. Because in this situation, the DDL owner is determined based on the monitoring information of `ddl_worker`, it might be that `ddl_worker` has not done any DDL job in this period of time, causing the owner information to be empty.

Other monitoring tables in TiDB are as follows:

* Statistics Info: Shows related monitoring metrics of TiDB statistical information.
* Top 10 Slow Query: Shows the Top 10 slow query information in the report time range.
* Top 10 Slow Query Group By Digest: Shows the Top 10 slow query information in the report time range, which is aggregated according to the SQL fingerprint.
* Slow Query With Diff Plan: The SQL statement whose execution plan changes within the report time range.
#### PD related monitoring information

The tables related to the monitoring information of PD modules are as follows:

* `Time Consumed by PD Component`: The time consumed by the monitoring metrics of related modules in PD.
* `Blance Leader/Region`: The monitoring information of `balance-region` and `balance leader` occurred in the cluster within the report time range, such as the number of leaders that are scheduled out from `tikv_note_1` or the number of leaders that are scheduled in.
* `Cluster Status`: The cluster status information, including total number of TiKV nodes, total cluster storage capacity, the number of Regions, and the number of offline TiKV nodes.
* `Store Status`: Record the status information of each TiKV node, including Region score, leader score, and the number of Regions/leaders.
* `Etcd Status`: etcd related information in PD.
#### TiKV related monitoring information

The tables related to the monitoring information of TiKV modules are as follows:

* `Time Consumed by TiKV Component`: The time consumed by related modules in TiKV.
* `Time Consumed by RocksDB`: The time consumed by RocksDB in TiKV.
* `TiKV Error`: The error information related to each module in TiKV.
* `TiKV Engine Size`: The size of stored data of column families on each node in TiKV.
* `Coprocessor Info`: Monitoring information related to the Coprocessor module in TiKV.
* `Raft Info`: Monitoring information of the Raft module in TiKV.
* `Snapshot Info`: Snapshot related monitoring information in TiKV.
* `GC Info`: Garbage Collection (GC) related monitoring information in TiKV.
* `Cache Hit`: The hit rate information of each cache of RocksDB in TiKV.
