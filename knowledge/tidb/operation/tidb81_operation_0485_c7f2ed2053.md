# TTL limitations and operational FAQ guidance

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/time-to-live.md`
- Source Title: `Periodically Delete Data Using TTL (Time to Live)`
- Source Heading Path: `Periodically Delete Expired Data Using TTL (Time to Live) > Limitations | Periodically Delete Expired Data Using TTL (Time to Live) > FAQs`
- Source Line Ranges: `253-302`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `shared`
- Topic Tags: `ttl`, `limitations`, `foreign-keys`, `temporary-tables`, `clustered-indexes`, `worker-count`, `scanning`, `deleting`, `performance-tuning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0485_c7f2ed2053`
- Source ID: `tidb-docs-8.1:time-to-live.md#limitations`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bdff141481c5045e4e81d36b08d8a55a6728db03ac1af277450710123f8b3217`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/time-to-live#limitations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/time-to-live.md

## Retrieval Guidance

- Use When: Use this chunk when you need TTL limitations or FAQ guidance about deletion timing, foreign key and temporary table restrictions, clustered index behavior, Grafana bottleneck analysis, or tuning `tidb_ttl_scan_worker_count` and `tidb_ttl_delete_worker_count`.
- Retrieval Keywords: TTL limitations, temporary tables, global temporary tables, local temporary tables, foreign key constraint, clustered indexes, executed sequentially on a single TiDB node, TTL Insert Rows Per Hour, TTL Delete Rows Per Hour, TTL Scan Worker Time By Phase, TTL Delete Worker Time By Phase, dispatch phase, idle phase, tidb_ttl_scan_worker_count, tidb_ttl_delete_worker_count, mysql.tidb_ttl_job_history
- Follow-up Guidance: It explains how to compare `TTL Insert Rows Per Hour` and `TTL Delete Rows Per Hour`, how to read scan and delete worker phases, and how `mysql.tidb_ttl_job_history` helps identify which TTL job was running at a certain moment.
- Classification Note: This is classified as operation because the content combines operational limitations with practical troubleshooting and worker-count tuning guidance for TTL tasks.

## Official Source Content

## Limitations

Currently, the TTL feature has the following limitations:

* The TTL attribute cannot be set on temporary tables, including local temporary tables and global temporary tables.
* A table with the TTL attribute does not support being referenced by other tables as the primary table in a foreign key constraint.
* It is not guaranteed that all expired data is deleted immediately. The time when expired data is deleted depends on the scheduling interval and scheduling window of the background cleanup job.
* For tables that use [clustered indexes](https://docs.pingcap.com/tidb/stable/clustered-indexes), if the primary key is neither an integer nor a binary string type, the TTL job cannot be split into multiple tasks. This will cause the TTL job to be executed sequentially on a single TiDB node. If the table contains a large amount of data, the execution of the TTL job might become slow.
## FAQs

- How can I determine whether the deletion is fast enough to keep the data size relatively stable?

    In the [Grafana `TiDB` dashboard](https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard), the panel `TTL Insert Rows Per Hour` records the total number of rows inserted in the previous hour. The corresponding `TTL Delete Rows Per Hour` records the total number of rows deleted by the TTL task in the previous hour. If `TTL Insert Rows Per Hour` is higher than `TTL Delete Rows Per Hour` for a long time, it means that the rate of insertion is higher than the rate of deletion and the total amount of data will increase. For example:

    ![insert fast example](/media/ttl/insert-fast.png)

    It is worth noting that since TTL does not guarantee that the expired rows will be deleted immediately, and the rows currently inserted will be deleted in a future TTL task, even if the speed of TTL deletion is lower than the speed of insertion in a short period of time, it does not necessarily mean that the speed of TTL is too slow. You need to consider the situation in its context.

- How can I determine whether the bottleneck of a TTL task is in scanning or deleting?

    Look at the `TTL Scan Worker Time By Phase` and `TTL Delete Worker Time By Phase` panels. If the scan worker is in the `dispatch` phase for a large percentage of time and the delete worker is rarely in the `idle` phase, then the scan worker is waiting for the delete worker to finish the deletion. If the cluster resources are still free at this point, you can consider increasing `tidb_ttl_ delete_worker_count` to increase the number of delete workers. For example:

    ![scan fast example](/media/ttl/scan-fast.png)

    In contrast, if the scan worker is rarely in the `dispatch` phase and the delete worker is in the `idle` phase for a long time, then the scan worker is relatively busy. For example:

    ![delete fast example](/media/ttl/delete-fast.png)

    The percentage of scan and delete in TTL jobs is related to the machine configuration and data distribution, so the monitoring data at each moment is only representative of the TTL Jobs being executed. You can read the table `mysql.tidb_ttl_job_history` to determine which TTL job is running at a certain moment and the corresponding table of the job.

- How to configure `tidb_ttl_scan_worker_count` and `tidb_ttl_delete_worker_count` properly?

    1. Refer to the question "How to determine whether the bottleneck of TTL tasks is in scanning or deleting?" to consider whether to increase the value of `tidb_ttl_scan_worker_count` or `tidb_ttl_delete_worker_count`.
    2. If the number of TiKV nodes is high, increase the value of `tidb_ttl_scan_worker_count` can make the TTL task workload more balanced.

   Since too many TTL workers will cause a lot of pressure, you need to evaluate the CPU level of TiDB and the disk and CPU usage of TiKV together. Depending on different scenarios and needs (whether you need to speed up TTL as much as possible, or to reduce the impact of TTL on other queries), you can adjust the value of `tidb_ttl_scan_worker_count` and `tidb_ttl_delete_worker_count` to improve the speed of TTL scanning and deleting or reduce the performance impact brought by TTL tasks.

- How to configure `tidb_ttl_scan_worker_count` and `tidb_ttl_delete_worker_count` properly?

   If the number of TiKV nodes is high, increase the value of `tidb_ttl_scan_worker_count` can make the TTL task workload more balanced.

   But too many TTL workers will cause a lot of pressure, you need to evaluate the CPU level of TiDB and the disk and CPU usage of TiKV together. Depending on different scenarios and needs (whether you need to speed up TTL as much as possible, or to reduce the impact of TTL on other queries), you can adjust the value of `tidb_ttl_scan_worker_count` and `tidb_ttl_delete_worker_count` to improve the speed of TTL scanning and deleting or reduce the performance impact brought by TTL tasks.
