# Query and instance memory limits and memory usage views

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/configure-memory-usage.md`
- Source Title: `TiDB Memory Control`
- Source Heading Path: `TiDB Memory Control | TiDB Memory Control > Configure the memory quota of a query | TiDB Memory Control > Configure the memory usage threshold of a tidb-server instance | TiDB Memory Control > View the memory usage of the current tidb-server instance using the INFORMATION_SCHEMA system table`
- Source Line Ranges: `5-72`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`, `sql`
- Topic Tags: `memory-control`, `query-memory-quota`, `instance-memory-limit`, `oom-action`, `information-schema`, `gc-trigger`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0023_c612b02aa7`
- Source ID: `tidb-docs-8.1:configure-memory-usage.md#tidb-memory-control`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8570494103b81eaa2df7f820fad732059e3800f0c0e5ecb91a05399da6a2dc2b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/configure-memory-usage#tidb-memory-control
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/configure-memory-usage.md

## Retrieval Guidance

- Use When: Use this chunk when the need is to find TiDB query memory limits, tidb-server instance memory thresholds, OOM handling behavior, GC trigger behavior, or INFORMATION_SCHEMA memory usage views.
- Retrieval Keywords: tidb_mem_oom_action, LOG, CANCEL, tidb_mem_quota_query, SET tidb_mem_quota_query = 8 << 30, tidb_server_memory_limit, SET GLOBAL tidb_server_memory_limit = "32GB", Out Of Memory Quota!, tidb_server_memory_limit_gc_trigger, INFORMATION_SCHEMA.MEMORY_USAGE, INFORMATION_SCHEMA.CLUSTER_MEMORY_USAGE, INFORMATION_SCHEMA.MEMORY_USAGE_OPS_HISTORY, INFORMATION_SCHEMA.CLUSTER_MEMORY_USAGE_OPS_HISTORY, server-memory-quota
- Follow-up Guidance: The source also points to INFORMATION_SCHEMA.(CLUSTER_)MEMORY_USAGE for current memory usage and INFORMATION_SCHEMA.(CLUSTER_)MEMORY_USAGE_OPS_HISTORY for memory-related operations, with the latest 50 records retained for each instance.
- Classification Note: This is classified as configuration because it defines memory-related system variables, their effects when limits are reached, and the system tables used to inspect memory usage.

## Official Source Content

# TiDB Memory Control

Currently, TiDB can track the memory quota of a single SQL query and take actions to prevent OOM (out of memory) or troubleshoot OOM when the memory usage exceeds a specific threshold value. The system variable [`tidb_mem_oom_action`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_oom_action-new-in-v610) specifies the action to take when a query reaches the memory limit:

- A value of `LOG` means that queries will continue to execute when the [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query) limit is reached, but TiDB will print an entry to the log.
- A value of `CANCEL` means TiDB stops executing the SQL query immediately after the [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query) limit is reached, and returns an error to the client. The error information clearly shows the memory usage of each physical execution operator that consumes memory in the SQL execution process.
## Configure the memory quota of a query

The system variable [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query) sets the limit for a query in bytes. Some usage examples:

```sql
-- Set the threshold value of memory quota for a single SQL query to 8GB:
SET tidb_mem_quota_query = 8 << 30;
```

```sql
-- Set the threshold value of memory quota for a single SQL query to 8MB:
SET tidb_mem_quota_query = 8 << 20;
```

```sql
-- Set the threshold value of memory quota for a single SQL query to 8KB:
SET tidb_mem_quota_query = 8 << 10;
```
## Configure the memory usage threshold of a tidb-server instance

Since v6.5.0, you can use the system variable [`tidb_server_memory_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit-new-in-v640) to set the threshold for the memory usage of a tidb-server instance.

For example, set the total memory usage of a tidb-server instance to 32 GB:

```sql
SET GLOBAL tidb_server_memory_limit = "32GB";
```

After you set this variable, when the memory usage of a tidb-server instance reaches 32 GB, TiDB will terminate the SQL operation with the largest memory usage among all running SQL operations in order, until the memory usage of the instance drops below 32 GB. The forcibly terminated SQL operation will return the `Out Of Memory Quota!` error to the client.

Currently, the memory limit set by `tidb_server_memory_limit` **DOES NOT** terminate the following SQL operations:

- DDL operations
- SQL operations that contain window functions and common table expressions

> **Warning:**
>
> + During the startup process, TiDB does not guarantee that the [`tidb_server_memory_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit-new-in-v640) limit is enforced. If the free memory of the operating system is insufficient, TiDB might still encounter OOM. You need to ensure that the TiDB instance has enough available memory.
> + In the process of memory control, the total memory usage of TiDB might slightly exceed the limit set by `tidb_server_memory_limit`.
> + Since v6.5.0, the configuration item `server-memory-quota` is deprecated. To ensure compatibility, after you upgrade your cluster to v6.5.0 or a later version, `tidb_server_memory_limit` will inherit the value of `server-memory-quota`. If you have not configured `server-memory-quota` before the upgrade, the default value of `tidb_server_memory_limit` is used, which is `80%`.

When the memory usage of a tidb-server instance reaches a certain proportion of the total memory (the proportion is controlled by the system variable [`tidb_server_memory_limit_gc_trigger`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit_gc_trigger-new-in-v640)), tidb-server will try to trigger a Golang GC to relieve memory stress. To avoid frequent GCs that cause performance issues due to the instance memory fluctuating around the threshold, this GC method will trigger GC at most once every minute.

> **Note:**
>
> In a hybrid deployment scenario, `tidb_server_memory_limit` is the memory usage threshold for a single tidb-server instance, instead of the total memory threshold for the whole physical machine.
## View the memory usage of the current tidb-server instance using the INFORMATION_SCHEMA system table

To view the memory usage of the current instance or cluster, you can query the system table [`INFORMATION_SCHEMA.(CLUSTER_)MEMORY_USAGE`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-memory-usage).

To view the memory-related operations and execution basis of the current instance or cluster, you can query the system table [`INFORMATION_SCHEMA.(CLUSTER_)MEMORY_USAGE_OPS_HISTORY`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-memory-usage-ops-history). For each instance, this table retains the latest 50 records.
