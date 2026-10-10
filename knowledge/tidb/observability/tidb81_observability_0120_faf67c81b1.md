# TTL observability metrics and system tables

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/time-to-live.md`
- Source Title: `Periodically Delete Data Using TTL (Time to Live)`
- Source Heading Path: `Periodically Delete Expired Data Using TTL (Time to Live) > Observability`
- Source Line Ranges: `156-234`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `ttl`, `grafana`, `metrics`, `job-history`, `runtime-information`, `system-tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0120_faf67c81b1`
- Source ID: `tidb-docs-8.1:time-to-live.md#observability`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6983995ec959073a4f3ffa7ad03b17e0823aba3713dc8fb8f6f655970dc1c467`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/time-to-live#observability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/time-to-live.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB TTL observability details, including Grafana panels and the system tables that expose runtime information, current subtasks, or job history for TTL jobs.
- Retrieval Keywords: TiDB -> TTL panel in Grafana, TTL metrics, mysql.tidb_ttl_table_status, mysql.tidb_ttl_task, mysql.tidb_ttl_job_history, information_schema.tables, last_job_summary, current_job_state, current_job_status, expired_rows, deleted_rows, TTL job history 90 days
- Follow-up Guidance: It also points to the TTL section in TiDB Monitoring Metrics and shows example queries such as `TABLE mysql.tidb_ttl_table_status LIMIT 1\G` and `TABLE mysql.tidb_ttl_job_history LIMIT 1\G`.
- Classification Note: This is classified as observability because the content describes TTL runtime information, Grafana visualization, and system tables used to inspect TTL execution status and history.

## Official Source Content

## Observability

> **Note:**
>
> This section is only applicable to TiDB Self-Managed. Currently, TiDB Cloud does not provide TTL metrics.

TiDB collects runtime information about TTL periodically and provides visualized charts of these metrics in Grafana. You can see these metrics in the TiDB -> TTL panel in Grafana.

For details of the metrics, see the TTL section in [TiDB Monitoring Metrics](https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard).

In addition, TiDB provides three tables to obtain more information about TTL jobs:

+ The `mysql.tidb_ttl_table_status` table contains information about the previously executed TTL job and ongoing TTL job for all TTL tables

    ```sql
    TABLE mysql.tidb_ttl_table_status LIMIT 1\G
    ```

    ```
    *************************** 1. row ***************************
                          table_id: 85
                   parent_table_id: 85
                  table_statistics: NULL
                       last_job_id: 0b4a6d50-3041-4664-9516-5525ee6d9f90
               last_job_start_time: 2023-02-15 20:43:46
              last_job_finish_time: 2023-02-15 20:44:46
               last_job_ttl_expire: 2023-02-15 19:43:46
                  last_job_summary: {"total_rows":4369519,"success_rows":4369519,"error_rows":0,"total_scan_task":64,"scheduled_scan_task":64,"finished_scan_task":64}
                    current_job_id: NULL
              current_job_owner_id: NULL
            current_job_owner_addr: NULL
         current_job_owner_hb_time: NULL
            current_job_start_time: NULL
            current_job_ttl_expire: NULL
                 current_job_state: NULL
                current_job_status: NULL
    current_job_status_update_time: NULL
    1 row in set (0.040 sec)
    ```

    The column `table_id` is the ID of the partitioned table, and the `parent_table_id` is the ID of the table, corresponding with the ID in [`information_schema.tables`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tables). If the table is not a partitioned table, the two IDs are the same.

    The columns `{last, current}_job_{start_time, finish_time, ttl_expire}` describe respectively the start time, finish time, and expiration time used by the TTL job of the last or current execution. The `last_job_summary` column describes the execution status of the last TTL task, including the total number of rows, the number of successful rows, and the number of failed rows.

+ The `mysql.tidb_ttl_task` table contains information about the ongoing TTL subtasks. A TTL job is split into many subtasks, and this table records the subtasks that are currently being executed.
+ The `mysql.tidb_ttl_job_history` table contains information about the TTL jobs that have been executed. The record of TTL job history is kept for 90 days.

    ```sql
    TABLE mysql.tidb_ttl_job_history LIMIT 1\G
    ```

    ```
    *************************** 1. row ***************************
               job_id: f221620c-ab84-4a28-9d24-b47ca2b5a301
             table_id: 85
      parent_table_id: 85
         table_schema: test_schema
           table_name: TestTable
       partition_name: NULL
          create_time: 2023-02-15 17:43:46
          finish_time: 2023-02-15 17:45:46
           ttl_expire: 2023-02-15 16:43:46
         summary_text: {"total_rows":9588419,"success_rows":9588419,"error_rows":0,"total_scan_task":63,"scheduled_scan_task":63,"finished_scan_task":63}
         expired_rows: 9588419
         deleted_rows: 9588419
    error_delete_rows: 0
               status: finished
    ```

    The column `table_id` is the ID of the partitioned table, and the `parent_table_id` is the ID of the table, corresponding with the ID in  `information_schema.tables`. `table_schema`, `table_name`, and `partition_name` correspond to the database, table name, and partition name. `create_time`, `finish_time`, and `ttl_expire` indicate the creation time, end time, and expiration time of the TTL task. `expired_rows` and `deleted_rows` indicate the number of expired rows and the number of rows deleted successfully.
