# TTL job scheduling and cluster controls

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/time-to-live.md`
- Source Title: `Periodically Delete Data Using TTL (Time to Live)`
- Source Heading Path: `Periodically Delete Expired Data Using TTL (Time to Live) > TTL job`
- Source Line Ranges: `129-155`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `ttl-jobs`, `scheduling`, `task-splitting`, `concurrency`, `global-variables`, `schedule-window`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0484_36d114ec2d`
- Source ID: `tidb-docs-8.1:time-to-live.md#ttl-job`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `de82e515666a101ebd57812929680156707b18ad4620caa3d9b22a28230c60f1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/time-to-live#ttl-job
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/time-to-live.md

## Retrieval Guidance

- Use When: Use this chunk when you need details about how TTL background jobs are scheduled, split into tasks, limited by cluster-wide settings, disabled globally, or restricted to a schedule window.
- Retrieval Keywords: TTL job, TTL_JOB_INTERVAL, ALTER TABLE orders TTL_JOB_INTERVAL = '24h', tidb_ttl_running_tasks, tidb_ttl_job_enable, SET @@global.tidb_ttl_job_enable = OFF, tidb_ttl_job_schedule_window_start_time, tidb_ttl_job_schedule_window_end_time, SET @@global.tidb_ttl_job_schedule_window_start_time = '01:00 +0000', SET @@global.tidb_ttl_job_schedule_window_end_time = '05:00 +0000', split the table into up to 64 tasks, Region being the smallest unit
- Follow-up Guidance: The content notes that not all TTL jobs for all kinds of tables can be split into tasks and refers readers to the Limitations section for details.
- Classification Note: This is classified as an operation chunk because the official content describes operational controls for TTL job execution, concurrency, and scheduling at table and cluster scope.

## Official Source Content

## TTL job

For each table with a TTL attribute, TiDB internally schedules a background job to clean up expired data. You can customize the execution period of these jobs by setting the `TTL_JOB_INTERVAL` attribute for the table. The following example sets the background cleanup jobs for the table `orders` to run once every 24 hours:

```sql
ALTER TABLE orders TTL_JOB_INTERVAL = '24h';
```

`TTL_JOB_INTERVAL` is set to `1h` by default.

When executing a TTL job, TiDB will split the table into up to 64 tasks, with the Region being the smallest unit. These tasks will be executed distributedly. You can limit the number of concurrent TTL tasks across the entire cluster by setting the system variable [`tidb_ttl_running_tasks`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ttl_running_tasks-new-in-v700). However, not all TTL jobs for all kinds of tables can be split into tasks. For more details on which kinds of tables' TTL jobs cannot be split into tasks, refer to the [Limitations](#limitations) section.

To disable the execution of TTL jobs, in addition to setting the `TTL_ENABLE='OFF'` table option, you can also disable the execution of TTL jobs in the entire cluster by setting the [`tidb_ttl_job_enable`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ttl_job_enable-new-in-v650) global variable:

```sql
SET @@global.tidb_ttl_job_enable = OFF;
```

In some scenarios, you might want to allow TTL jobs to run only in a certain time window. In this case, you can set the [`tidb_ttl_job_schedule_window_start_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ttl_job_schedule_window_start_time-new-in-v650) and [`tidb_ttl_job_schedule_window_end_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ttl_job_schedule_window_end_time-new-in-v650) global variables to specify the time window. For example:

```sql
SET @@global.tidb_ttl_job_schedule_window_start_time = '01:00 +0000';
SET @@global.tidb_ttl_job_schedule_window_end_time = '05:00 +0000';
```

The preceding statement allows TTL jobs to be scheduled only between 1:00 and 5:00 UTC. By default, the time window is set to `00:00 +0000` to `23:59 +0000`, which allows the jobs to be scheduled at any time.
