# Expensive query and transaction logging with statement priority

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_expensive_query_time_threshold | System Variables > Variable reference > tidb_expensive_txn_time_threshold <span class="version-mark">New in v7.2.0</span> | System Variables > Variable reference > tidb_force_priority`
- Source Line Ranges: `2884-2938`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `system-variables`, `expensive-query-log`, `transaction-logging`, `statement-priority`, `resource-control`, `global-scope`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0081_9fe07b8df6`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-expensive-query-time-threshold`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `23ad954881e0c912ccb557984b83e233bdd2cc196254f1b4f7fc9562337101bb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-expensive-query-time-threshold
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact TiDB variables that control expensive query logging, expensive transaction logging, or forced statement priority on a TiDB server.
- Retrieval Keywords: tidb_expensive_query_time_threshold, tidb_expensive_txn_time_threshold, tidb_force_priority, expensive query logs threshold, expensive transaction logging threshold, slow logs versus expensive query logs, statement priority NO_PRIORITY LOW_PRIORITY HIGH_PRIORITY DELAYED, resource control statement priority, not applicable to TiDB Cloud
- Follow-up Guidance: The content notes that when Resource Control is enabled, statement priority no longer takes effect.
- Classification Note: This is classified as observability because two variables define thresholds for logging expensive queries and transactions, while the same chunk also includes the related server-side statement priority variable.

## Official Source Content

### tidb_expensive_query_time_threshold

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `60`
- Range: `[10, 2147483647]`
- Unit: Seconds
- This variable is used to set the threshold value that determines whether to print expensive query logs. The difference between expensive query logs and slow query logs is:
    - Slow logs are printed after the statement is executed.
    - Expensive query logs print the statements that are being executed, with execution time exceeding the threshold value, and their related information.
### tidb_expensive_txn_time_threshold New in v7.2.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `600`
- Range: `[60, 2147483647]`
- Unit: Seconds
- This variable controls the threshold for logging expensive transactions, which is 600 seconds by default. When the duration of a transaction exceeds the threshold, and the transaction is neither committed nor rolled back, it is considered an expensive transaction and will be logged.
### tidb_force_priority

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `NO_PRIORITY`
- Possible values: `NO_PRIORITY`, `LOW_PRIORITY`, `HIGH_PRIORITY`, `DELAYED`
- This variable is used to change the default priority for statements executed on a TiDB server. A use case is to ensure that a particular user that is performing OLAP queries receives lower priority than users performing OLTP queries.
- The default value `NO_PRIORITY` means that the priority for statements is not forced to change.

> **Note:**
>
> Starting from v6.6.0, TiDB supports [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control). You can use this feature to execute SQL statements with different priorities in different resource groups. By configuring proper quotas and priorities for these resource groups, you can gain better scheduling control for SQL statements with different priorities. When resource control is enabled, statement priority will no longer take effect. It is recommended that you use [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) to manage resource usage for different SQL statements.
