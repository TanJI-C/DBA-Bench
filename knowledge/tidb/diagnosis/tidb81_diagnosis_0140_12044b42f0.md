# TiDB OOM troubleshooting symptoms, process, causes, and solutions

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-tidb-oom.md`
- Source Title: `Troubleshoot TiDB OOM Issues`
- Source Heading Path: `Troubleshoot TiDB OOM Issues | Troubleshoot TiDB OOM Issues > Typical OOM phenomena | Troubleshoot TiDB OOM Issues > Overall troubleshooting process | Troubleshoot TiDB OOM Issues > Typical causes and solutions | Troubleshoot TiDB OOM Issues > Typical causes and solutions > Deployment issues | Troubleshoot TiDB OOM Issues > Typical causes and solutions > Database issues | Troubleshoot TiDB OOM Issues > Typical causes and solutions > Database issues > Executing SQL statements consumes too much memory | Troubleshoot TiDB OOM Issues > Typical causes and solutions > Database issues > Large transactions or large writes consume too much memory | Troubleshoot TiDB OOM Issues > Typical causes and solutions > Database issues > The process of collecting and loading statistical information consumes too much memory | Troubleshoot TiDB OOM Issues > Typical causes and solutions > Database issues > Prepared statements are overused | Troubleshoot TiDB OOM Issues > Typical causes and solutions > Database issues > `tidb_enable_rate_limit_action` is not configured properly | Troubleshoot TiDB OOM Issues > Typical causes and solutions > Client side issues`
- Source Line Ranges: `5-144`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `tiup`, `sql`, `shared`
- Topic Tags: `oom`, `memory`, `troubleshooting`, `grafana`, `logs`, `deployment`, `sql`, `transactions`, `statistics`, `prepared-statements`, `rate-limit`, `client`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0140_12044b42f0`
- Source ID: `tidb-docs-8.1:troubleshoot-tidb-oom.md#troubleshoot-tidb-oom-issues`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f64b1c7163bbcd65d293afb2e068eb60c11d87bfd54ba0eea3a07338658d1de1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-tidb-oom#troubleshoot-tidb-oom-issues
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-tidb-oom.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing TiDB OOM symptoms, distinguishing deployment issues from database or client-side causes, and locating memory-related logs, metrics, and configuration items.
- Retrieval Keywords: Troubleshoot TiDB OOM Issues, OOM, Out of Memory, SQL error, errno = 2013, state = 'HY000': Lost connection to MySQL server during query, process/heapInUse, estimate-inuse, TiDB > Server > Memory Usage, TiDB > Server > Uptime, TiDB-Runtime > Memory Usage, memory_usage_alarm.go:139, tidb-server has the risk of OOM because of memory usage exceeds alarm ratio, Welcome to TiDB., dmesg -T | grep tidb-server, oom-killer, resource_control, tidb_mem_quota_query, ERROR 1105 (HY000): Out Of Memory Quota![conn_id=54], disk spill, STREAM_AGG(), tidb_distsql_scan_concurrency, tidb_executor_concurrency, ANALYZE, tidb_stats_cache_mem_quota, tidb_mem_quota_analyze, deallocate prepare stmt, wait_timeout, max_execution_time, max_prepared_stmt_count, tidb_enable_rate_limit_action, Client Data Traffic, defaultFetchSize
- Follow-up Guidance: After confirming an OOM issue with operating system logs, the content directs you to investigate whether the cause is deployment, database workload such as large queries or writes and high concurrency, or client-side behavior.
- Classification Note: This chunk is classified as diagnosis because it lists OOM phenomena, gives an overall troubleshooting process, and maps common causes to specific TiDB metrics, logs, SQL behavior, and system variables.

## Official Source Content

# Troubleshoot TiDB OOM Issues

This document describes how to troubleshoot TiDB OOM (Out of Memory) issues, including phenomena, causes, solutions, and diagnostic information.
## Typical OOM phenomena

The following are some typical OOM phenomena:

- The client side reports the following error: `SQL error, errno = 2013, state = 'HY000': Lost connection to MySQL server during query`.

- The Grafana dashboard shows:
    - **TiDB** > **Server** > **Memory Usage** shows that the `process/heapInUse` metric keeps rising, and suddenly drops to zero after reaching the threshold.
    - **TiDB** > **Server** > **Uptime** suddenly drops to zero.
    - **TiDB-Runtime** > **Memory Usage** shows that the `estimate-inuse` metric keeps rising.

- Check `tidb.log`, and you can find the following log entries:
    - An alarm about OOM: `[WARN] [memory_usage_alarm.go:139] ["tidb-server has the risk of OOM because of memory usage exceeds alarm ratio. Running SQLs and heap profile will be recorded in record path"]`. For more information, see [`memory-usage-alarm-ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_memory_usage_alarm_ratio).
    - A log entry about restart: `[INFO] [printer.go:33] ["Welcome to TiDB."]`.
## Overall troubleshooting process

When you troubleshoot OOM issues, follow this process:

1. Confirm whether it is an OOM issue.

    Execute the following command to check the operating system logs. If there is an `oom-killer` log near the time when the problem occurs, you can confirm that it is an OOM issue.

    ```shell
    dmesg -T | grep tidb-server
    ```

    The following is an example of the log that contains `oom-killer`:

    ```shell
    ......
    Mar 14 16:55:03 localhost kernel: tidb-server invoked oom-killer: gfp_mask=0x201da, order=0, oom_score_adj=0
    Mar 14 16:55:03 localhost kernel: tidb-server cpuset=/ mems_allowed=0
    Mar 14 16:55:03 localhost kernel: CPU: 14 PID: 21966 Comm: tidb-server Kdump: loaded Not tainted 3.10.0-1160.el7.x86_64 #1
    Mar 14 16:55:03 localhost kernel: Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS rel-1.14.0-0-g155821a1990b-prebuilt.qemu.org 04/01/2014
    ......
    Mar 14 16:55:03 localhost kernel: Out of memory: Kill process 21945 (tidb-server) score 956 or sacrifice child
    Mar 14 16:55:03 localhost kernel: Killed process 21945 (tidb-server), UID 1000, total-vm:33027492kB, anon-rss:31303276kB, file-rss:0kB, shmem-rss:0kB
    Mar 14 16:55:07 localhost systemd: tidb-4000.service: main process exited, code=killed, status=9/KILL
    ......
    ```

2. After confirming that it is an OOM issue, you can further investigate whether the OOM is caused by deployment or the database.

    - If the OOM is caused by a deployment issue, you need to investigate the resource configuration and impact of hybrid deployment.
    - If the OOM is caused by a database issue, the following are some possible causes:
        - TiDB handles large data traffic, such as large queries, large writes, and data import.
        - TiDB is in a high concurrency scenario, where multiple SQL statements consume resources concurrently or operator concurrency is high.
        - TiDB has a memory leak and resources are not released.

    Refer to the following sections for specific troubleshooting methods.
## Typical causes and solutions

OOM issues are usually caused by the following:

- [Deployment issues](#deployment-issues)
- [Database issues](#database-issues)
- [Client side issues](#client-side-issues)
### Deployment issues

The following are some causes of OOM due to improper deployment:

- The memory capacity of the operating system is too small.
- The TiUP configuration [`resource_control`](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#global) is not appropriate.
- In the case of hybrid deployments (meaning that TiDB and other applications are deployed on the same server), TiDB is killed accidentally by `oom-killer` due to lack of resources.
### Database issues

This section describes the causes and solutions for OOM caused by database issues.

> **Note:**
>
> If you have configured [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query), an error occurs: `ERROR 1105 (HY000): Out Of Memory Quota![conn_id=54]`. It is caused by the memory usage control behavior of the database. It is a normal behavior.
#### Executing SQL statements consumes too much memory

You can take the following measures to reduce the memory usage of SQL statements, depending on the different causes of OOM issues.

- If the execution plan of SQL is not optimal, for example, due to lack of proper indexes, outdated statistics, or optimizer bugs, a wrong execution plan of SQL might be selected. A huge intermediate result set will then be accumulated in the memory. In this case, consider the following measures:
    - Add appropriate indexes.
    - Use the [disk spill](https://docs.pingcap.com/tidb/stable/configure-memory-usage#disk-spill) feature for execution operators.
    - Adjust the JOIN order between tables.
    - Use hints to optimize SQL statements.

- Some operators and functions are not supported to be pushed down to the storage level, resulting in a huge accumulation of intermediate result sets. In this case, you need to refine the SQL statements or use hints to optimize, and use the functions or operators that support pushing down.

- The execution plan contains the operator HashAgg. HashAgg is executed concurrently by multiple threads, which is faster but consumes more memory. Instead, you can use `STREAM_AGG()`.

- Reduce the number of Regions to be read simultaneously or reduce the concurrency of operators to avoid memory problems caused by high concurrency. The corresponding system variables include:
    - [`tidb_distsql_scan_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_distsql_scan_concurrency)
    - [`tidb_executor_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_executor_concurrency-new-in-v50)

- The concurrency of sessions is too high near the time point when the problem occurs. In this case, consider scaling out the TiDB cluster by adding more TiDB nodes.
#### Large transactions or large writes consume too much memory

You need to plan for memory capacity. When a transaction is executed, the memory usage of the TiDB process is scaled up comparing with the transaction size, up to two to three times or more of the transaction size.

You can split a single large transaction to multiple smaller transactions.
#### The process of collecting and loading statistical information consumes too much memory

A TiDB node needs to load statistics into memory after it starts. TiDB consumes memory when collecting statistical information. You can control memory usage in the following ways:

- Specify a sampling rate, only collect statistics for specific columns, and reduce `ANALYZE` concurrency.
- Since TiDB v6.1.0, you can use the system variable [`tidb_stats_cache_mem_quota`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_stats_cache_mem_quota-new-in-v610) to control the memory usage for statistical information.
- Since TiDB v6.1.0, you can use the system variable [`tidb_mem_quota_analyze`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_analyze-new-in-v610) to control the maximum memory usage when TiDB updates statistics.

For more information, see [Introduction to Statistics](https://docs.pingcap.com/tidb/stable/statistics).
#### Prepared statements are overused

The client side keeps creating prepared statements but does not execute [`deallocate prepare stmt`](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache#ignore-the-com_stmt_close-command-and-the-deallocate-prepare-statement), which causes memory consumption to continue to rise and eventually triggers TiDB OOM. The reason is that the memory occupied by a prepared statement is not released until the session is closed. This is especially important for long-time connection sessions.

To solve the problem, consider the following measures:

- Adjust the session lifecycle.
- Adjust [the `wait_timeout` and `max_execution_time` of the connection pool](https://docs.pingcap.com/tidb/stable/develop/dev-guide-connection-parameters#timeout-related-parameters).
- Use the system variable [`max_prepared_stmt_count`](https://docs.pingcap.com/tidb/stable/system-variables#max_prepared_stmt_count) to control the maximum number of prepared statements in a session.
#### `tidb_enable_rate_limit_action` is not configured properly

The system variable [`tidb_enable_rate_limit_action`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_rate_limit_action) controls memory usage effectively when an SQL statement only reads data. When this variable is enabled and computing operations (such as join or aggregation operations) are required, memory usage might not be under the control of [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query), which increases the risk of OOM.

It is recommended that you disable this system variable. Since TiDB v6.3.0, this system variable is disabled by default.
### Client side issues

If OOM occurs on the client side, investigate the following:

- Check the trend and speed on **Grafana TiDB Details** > **Server** > **Client Data Traffic** to see if there is a network blockage.
- Check whether there is an application OOM caused by wrong JDBC configuration parameters. For example, if the `defaultFetchSize` parameter for streaming read is incorrectly configured, it can cause data to be heavily accumulated on the client side.
