# OOM diagnostic information collection for TiDB

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-tidb-oom.md`
- Source Title: `Troubleshoot TiDB OOM Issues`
- Source Heading Path: `Troubleshoot TiDB OOM Issues > Diagnostic information to be collected to troubleshoot OOM issues`
- Source Line Ranges: `145-193`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `tiup`, `shared`
- Topic Tags: `oom`, `memory`, `diagnostics`, `configuration`, `grafana`, `slow-query`, `processlist`, `profile`, `logs`, `numa`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0141_246ec909b0`
- Source ID: `tidb-docs-8.1:troubleshoot-tidb-oom.md#diagnostic-information-to-be-collected-to-troubleshoot-oom-issues`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b25b402af879fac2d66445289ebfdad40d16223451eb4187566fa964deb3aa22`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-tidb-oom#diagnostic-information-to-be-collected-to-troubleshoot-oom-issues
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-tidb-oom.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing a TiDB OOM issue and gathering the documented memory, configuration, dashboard, SQL, log, and profile information for root-cause analysis.
- Retrieval Keywords: OOM diagnostic information collection for TiDB, resource_control.memory_limit, cat /proc/meminfo, vm.overcommit_memory, numactl --hardware, numactl --show, tidb_mem_quota_query, memory-usage-alarm-ratio, mem-quota-query, oom-action, tidb_enable_rate_limit_action, tidb_server_memory_limit, oom-use-tmp-storage, tmp-storage-path, tmp-storage-quota, tidb_analyze_version, Grafana TiDB Server Memory Usage, SLOW_QUERY, CLUSTER_SLOW_QUERY, tidb_slow_query.log, grep "expensive_query" tidb.log, EXPLAIN ANALYZE, SELECT * FROM information_schema.processlist;, MEM column, curl -G "http://{TiDBIP}:10080/debug/zip?seconds=10" > profile.zip, grep "tidb-server has the risk of OOM" tidb.log, record path
- Follow-up Guidance: It also points to checking the TiDB Dashboard for SQL statement analysis, slow queries, and memory usage, and to using the alert log entry to find the recorded file path.
- Classification Note: The chunk is classified as diagnosis because the official content lists the exact data, commands, logs, metrics, and configuration items to collect when troubleshooting TiDB OOM issues.

## Official Source Content

## Diagnostic information to be collected to troubleshoot OOM issues

To locate the root cause of an OOM issue, you need to collect the following information:

- Collect the memory-related configurations of the operating system:
    - TiUP configuration: `resource_control.memory_limit`
    - Operating system configurations:
        - Memory information: `cat /proc/meminfo`
        - Kernel parameters: `vm.overcommit_memory`
    - NUMA information:
        - `numactl --hardware`
        - `numactl --show`

- Collect the version information and the memory-related configurations of the database:
    - TiDB version
    - `tidb_mem_quota_query`
    - `memory-usage-alarm-ratio`
    - `mem-quota-query`
    - `oom-action`
    - `tidb_enable_rate_limit_action`
    - `tidb_server_memory_limit`
    - `oom-use-tmp-storage`
    - `tmp-storage-path`
    - `tmp-storage-quota`
    - `tidb_analyze_version`

- Check the daily usage of TiDB memory on the Grafana dashboard: **TiDB** > **Server** > **Memory Usage**.

- Check the SQL statements that consume more memory.

    - View SQL statement analysis, slow queries, and memory usage on the TiDB Dashboard.
    - Check `SLOW_QUERY` and `CLUSTER_SLOW_QUERY` in `INFORMATION_SCHEMA`.
    - Check `tidb_slow_query.log` on each TiDB node.
    - Run `grep "expensive_query" tidb.log` to check the corresponding log entries.
    - Run `EXPLAIN ANALYZE` to check the memory usage of operators.
    - Run `SELECT * FROM information_schema.processlist;` to check the value of the `MEM` column.

- Run the following command to collect the TiDB Profile information when memory usage is high:

    ```shell
    curl -G "http://{TiDBIP}:10080/debug/zip?seconds=10" > profile.zip
    ```

- Run `grep "tidb-server has the risk of OOM" tidb.log` to check the path of the alert file collected by TiDB Server. The following is an example output:

    ```shell
    ["tidb-server has the risk of OOM because of memory usage exceeds alarm ratio. Running SQLs and heap profile will be recorded in record path"] ["is tidb_server_memory_limit set"=false] ["system memory total"=14388137984] ["system memory usage"=11897434112] ["tidb-server memory usage"=11223572312] [memory-usage-alarm-ratio=0.8] ["record path"="/tmp/0_tidb/MC4wLjAuMDo0MDAwLzAuMC4wLjA6MTAwODA=/tmp-storage/record"]
    ```
