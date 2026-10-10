# Expensive query log overview, example, and field descriptions

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/identify-expensive-queries.md`
- Source Title: `Identify Expensive Queries`
- Source Heading Path: `Identify Expensive Queries | Identify Expensive Queries > Expensive query log example | Identify Expensive Queries > Fields description`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `expensive-query-log`, `thresholds`, `execution-time`, `memory-usage`, `tidb-server-log`, `slow-query-log`, `log-fields`, `coprocessor-tasks`, `statistics`, `session-identification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0065_fd91038460`
- Source ID: `tidb-docs-8.1:identify-expensive-queries.md#identify-expensive-queries`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c2d690b989fa854040e59f7adbb0db7826058084de50e3994ecbd02717225fd3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/identify-expensive-queries#identify-expensive-queries
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/identify-expensive-queries.md

## Retrieval Guidance

- Use When: Use this chunk when looking for what the expensive query log records, how it differs from the slow query log, or what fields in an [expensive_query] tidb-server log entry mean.
- Retrieval Keywords: expensive query log, [expensive_query], tidb-server log, tidb.log, tidb_expensive_query_time_threshold, tidb_mem_quota_query, slow query log difference, cost_time, mem_max, stats=t:pseudo, table_ids, txn_start_ts, conn_id, database, user, sql, wait_time, request_count, total_keys, processed_keys, num_cop_tasks, process_avg_time, process_p90_time, process_max_time, process_max_addr, wait_avg_time, wait_p90_time, wait_max_time, wait_max_addr, con:60026
- Follow-up Guidance: The source notes that if `stats` is `pseudo`, there are no available statistics and in that case you need to analyze the tables or indexes.
- Classification Note: This is observability content for TiDB because it explains how TiDB emits expensive query information to the tidb-server log and how to interpret the logged fields, including TiKV Coprocessor task metrics.

## Official Source Content

# Identify Expensive Queries

TiDB allows you to identify expensive queries during SQL execution, so you can diagnose and improve the performance of SQL execution. Specifically, TiDB prints the information about statements whose execution time exceeds [`tidb_expensive_query_time_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_expensive_query_time_threshold) (60 seconds by default) or memory usage exceeds [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query) (1 GB by default) to the [tidb-server log file](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#logfile) ("tidb.log" by default).

> **Note:**
>
> The expensive query log differs from the [slow query log](https://docs.pingcap.com/tidb/stable/identify-slow-queries) in this way: TiDB prints statement information to the expensive query log **as soon as** the statement exceeds the threshold of resource usage (execution time or memory usage); while TiDB prints statement information to the slow query log **after** the statement execution.
## Expensive query log example

```sql
[2020/02/05 15:32:25.096 +08:00] [WARN] [expensivequery.go:167] [expensive_query] [cost_time=60.008338935s] [wait_time=0s] [request_count=1] [total_keys=70] [process_keys=65] [num_cop_tasks=1] [process_avg_time=0s] [process_p90_time=0s] [process_max_time=0s] [process_max_addr=10.0.1.9:20160] [wait_avg_time=0.002s] [wait_p90_time=0.002s] [wait_max_time=0.002s] [wait_max_addr=10.0.1.9:20160] [stats=t:pseudo] [conn_id=60026] [user=root] [database=test] [table_ids="[122]"] [txn_start_ts=414420273735139329] [mem_max="1035 Bytes (1.0107421875 KB)"] [sql="insert into t select sleep(1) from t"]
```
## Fields description

Basic fields:

* `cost_time`: The execution time of a statement when the log is printed.
* `stats`: The version of statistics used by the tables or indexes involved in a statement. If the value is `pseudo`, it means that there are no available statistics. In this case, you need to analyze the tables or indexes.
* `table_ids`: The IDs of the tables involved in a statement.
* `txn_start_ts`: The start timestamp and the unique ID of a transaction. You can use this value to search for the transaction-related logs.
* `sql`: The sql statement.

Memory usage related fields:

* `mem_max`: Memory usage of a statement when the log is printed. This field has two kinds of units to measure memory usage: byte and other readable and adaptable units (such as MB and GB).

User related fields:

* `user`: The name of the user who executes the statement.
* `conn_id`: The connection ID (session ID). For example, you can use the keyword `con:60026` to search for the log whose session ID is `60026`.
* `database`: The database where the statement is executed.

TiKV Coprocessor task related fields:

* `wait_time`: The total waiting time of all Coprocessor requests of a statement in TiKV. Because the Coprocessor of TiKV runs a limited number of threads, requests might queue up when all threads of Coprocessor are working. When a request in the queue takes a long time to process, the waiting time of the subsequent requests increases.
* `request_count`: The number of Coprocessor requests that a statement sends.
* `total_keys`: The number of keys that Coprocessor has scanned.
* `processed_keys`: The number of keys that Coprocessor has processed. Compared with `total_keys`, `processed_keys` does not include the old versions of MVCC. A great difference between `processed_keys` and `total_keys` indicates that many old versions exist.
* `num_cop_tasks`: The number of Coprocessor requests that a statement sends.
* `process_avg_time`: The average execution time of Coprocessor tasks.
* `process_p90_time`: The P90 execution time of Coprocessor tasks.
* `process_max_time`: The maximum execution time of Coprocessor tasks.
* `process_max_addr`: The address of the Coprocessor task with the longest execution time.
* `wait_avg_time`: The average waiting time of Coprocessor tasks.
* `wait_p90_time`: The P90 waiting time of Coprocessor tasks.
* `wait_max_time`: The maximum waiting time of Coprocessor tasks.
* `wait_max_addr`: The address of the Coprocessor task with the longest waiting time.
