# Excessive memory usage alarm behavior and example

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/configure-memory-usage.md`
- Source Title: `TiDB Memory Control`
- Source Heading Path: `TiDB Memory Control > Trigger the alarm of excessive memory usage`
- Source Line Ranges: `73-131`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`, `sql`
- Topic Tags: `memory-alarm`, `oom-risk`, `status-files`, `logs`, `thresholds`, `ops-history`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0017_027c997c00`
- Source ID: `tidb-docs-8.1:configure-memory-usage.md#trigger-the-alarm-of-excessive-memory-usage`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ff8b88322aebf99acba6c58bd87b771f5643591253b43d70c6e01ddab3527155`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/configure-memory-usage#trigger-the-alarm-of-excessive-memory-usage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/configure-memory-usage.md

## Retrieval Guidance

- Use When: Use this chunk when the need is to retrieve how TiDB triggers and records an excessive memory usage alarm, what log keyword appears, which status files are generated, and which variables control alarm thresholds and retention.
- Retrieval Keywords: Trigger the alarm of excessive memory usage, tidb_memory_usage_alarm_ratio, tidb_memory_usage_alarm_keep_record_num, tidb-server has the risk of OOM, filename, top 10 SQL statements with the highest memory usage, top 10 SQL statements with the longest running time, goroutine stack information, heap memory, oom_record, goroutinue, heap, running_sql, SET GLOBAL tidb_memory_usage_alarm_ratio = 0.85
- Follow-up Guidance: The source includes an example that checks tidb.log for fields such as system memory total, system memory usage, tidb-server memory usage, memory-usage-alarm-ratio, and record path, then inspects the generated status files in the record directory.
- Classification Note: This is classified as observability because it describes alarm trigger conditions, emitted logs, recorded diagnostic files, and the observable fields captured during high memory usage.

## Official Source Content

## Trigger the alarm of excessive memory usage

When the memory usage of a tidb-server instance exceeds its memory threshold (70% of its total memory by default) and any of the following conditions is met, TiDB records the related status files and prints an alarm log.

- It is the first time the memory usage exceeds the memory threshold.
- The memory usage exceeds the memory threshold and it has been more than 60 seconds since the last alarm.
- The memory usage exceeds the memory threshold and `(Current memory usage - Memory usage at the last alarm) / Total memory > 10%`.

You can control the memory threshold that triggers the alarm by modifying the memory usage ratio via the system variable [`tidb_memory_usage_alarm_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_memory_usage_alarm_ratio).

When the alarm of excessive memory usage is triggered, TiDB takes the following actions:

- TiDB records the following information in the directory where the TiDB log file [`filename`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#filename) is located.

    - The information about the top 10 SQL statements with the highest memory usage and the top 10 SQL statements with the longest running time among all SQL statements currently being executed
    - The goroutine stack information
    - The usage status of heap memory

- TiDB prints an alarm log containing the keyword `tidb-server has the risk of OOM` and the values of the following memory-related system variables.

    - [`tidb_mem_oom_action`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_oom_action-new-in-v610)
    - [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query)
    - [`tidb_server_memory_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit-new-in-v640)
    - [`tidb_analyze_version`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_analyze_version-new-in-v510)
    - [`tidb_enable_rate_limit_action`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_rate_limit_action)

To avoid accumulating too many status files for alarms, TiDB only retains the status files generated during the recent five alarms by default. You can adjust this number by configuring the system variable [`tidb_memory_usage_alarm_keep_record_num`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_memory_usage_alarm_keep_record_num-new-in-v640).

The following example constructs a memory-intensive SQL statement that triggers the alarm:

1. Set `tidb_memory_usage_alarm_ratio` to `0.85`:

    ```sql
    SET GLOBAL tidb_memory_usage_alarm_ratio = 0.85;
    ```

2. Execute `CREATE TABLE t(a int);` and insert 1000 rows of data.

3. Execute `select * from t t1 join t t2 join t t3 order by t1.a`. This SQL statement outputs one billion records, which consumes a large amount of memory and therefore triggers the alarm.

4. Check the `tidb.log` file which records the total system memory, current system memory usage, memory usage of the tidb-server instance, and the directory of status files.

    ```
    [2022/10/11 16:39:02.281 +08:00] [WARN] [memoryusagealarm.go:212] ["tidb-server has the risk of OOM because of memory usage exceeds alarm ratio. Running SQLs and heap profile will be recorded in record path"] ["is tidb_server_memory_limit set"=false] ["system memory total"=33682427904] ["system memory usage"=22120655360] ["tidb-server memory usage"=21468556992] [memory-usage-alarm-ratio=0.85] ["record path"=/tiup/deploy/tidb-4000/log/oom_record]
    ```

    The fields of the example log file above are described as follows:

    * `is tidb_server_memory_limit set` indicates whether [`tidb_server_memory_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit-new-in-v640) is set.
    * `system memory total` indicates the total memory of the current system.
    * `system memory usage` indicates the current system memory usage.
    * `tidb-server memory usage` indicates the memory usage of the tidb-server instance.
    * `memory-usage-alarm-ratio` indicates the value of the system variable [`tidb_memory_usage_alarm_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_memory_usage_alarm_ratio).
    * `record path` indicates the directory of status files.

5. By checking the directory of status files (In the preceding example, the directory is `/tiup/deploy/tidb-4000/log/oom_record`), you can see a record directory with the corresponding timestamp (for example, `record2022-10-09T17:18:38+08:00`). The record directory includes three files: `goroutinue`, `heap`, and `running_sql`. These three files are suffixed with the time when status files are logged. They respectively record goroutine stack information, the usage status of heap memory, and the running SQL information when the alarm is triggered. For the content in `running_sql`, refer to [`expensive-queries`](https://docs.pingcap.com/tidb/stable/identify-expensive-queries).
