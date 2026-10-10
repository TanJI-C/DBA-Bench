# System variable changes in 7.4.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.4.0.md`
- Source Title: `TiDB 7.4.0 Release Notes`
- Source Heading Path: `TiDB 7.4.0 Release Notes > Compatibility changes > System variables`
- Source Line Ranges: `299-316`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `sql`, `tidb`, `tiflash`, `tikv`
- Topic Tags: `system-variables`, `defaults`, `new-variables`, `deleted-variables`, `optimizer`, `resource-control`, `global-sort`, `memory-limit`, `spill`, `rpc-timeout`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0512_3402fcf389`
- Source ID: `tidb-docs-8.1:releases/release-7.4.0.md#system-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1cbb189e64a75e6bbacc7f20267a0d5387e60670f106e8e7a26ec618f86151fc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.4.0#system-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks which system variables were added, modified, or deleted in TiDB 7.4.0 and what defaults or controls they introduce.
- Retrieval Keywords: TiDB 7.4.0 system variables, tidb_enable_tiflash_pipeline_model deleted, tidb_enable_non_prepared_plan_cache default OFF, default_collation_for_utf8mb4 utf8mb4_bin, tidb_cloud_storage_uri, Global Sort system variable, tidb_opt_enable_hash_join, tidb_opt_objective moderate determinate, tidb_request_source_type, Resource Control, tidb_schema_version_cache_limit, tidb_service_scope, DXF, ADD INDEX, IMPORT INTO, tidb_session_alias, tiflash_mem_quota_query_per_node, tiflash_query_spill_ratio, query-level spilling, tikv_client_read_timeout
- Follow-up Guidance: The source provides per-variable descriptions, including example syntax for SET @@tidb_request_source_type = "background" and default values where stated.
- Classification Note: This chunk is a system-variable change list in the TiDB 7.4.0 release notes, identifying deleted, modified, and newly added variables and their documented purposes.

## Official Source Content

### System variables

| Variable name | Change type | Description |
|--------|------------------------------|------|
| `tidb_enable_tiflash_pipeline_model` | Deleted | This variable was used to control whether to enable the TiFlash pipeline execution model. Starting from v7.4.0, the TiFlash pipeline execution model is automatically enabled when the TiFlash resource control feature is enabled. |
| [`tidb_enable_non_prepared_plan_cache`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_non_prepared_plan_cache) | Modified |  Changes the default value from `ON` to `OFF` after further tests, meaning that non-prepared execution plan cache is disabled. |
| [`default_collation_for_utf8mb4`](https://docs.pingcap.com/tidb/stable/system-variables#default_collation_for_utf8mb4-new-in-v740) | Newly added | Controls the default collation for the `utf8mb4` character set. The default value is `utf8mb4_bin`. |
| [`tidb_cloud_storage_uri`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_cloud_storage_uri-new-in-v740) | Newly added | Specifies the cloud storage URI to enable [Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort). |
| [`tidb_opt_enable_hash_join`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_hash_join-new-in-v656-v712-and-v740) | Newly added | Controls whether the optimizer will select hash joins for tables. The value is `ON` by default. If set to `OFF`, the optimizer avoids selecting a hash join of a table unless there is no other execution plan available. |
| [`tidb_opt_objective`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_objective-new-in-v740) | Newly added | This variable controls the objective of the optimizer. `moderate` maintains the default behavior in versions prior to TiDB v7.4.0, where the optimizer tries to use more information to generate better execution plans. `determinate` mode tends to be more conservative and makes the execution plan more stable. |
| [`tidb_request_source_type`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_request_source_type-new-in-v740) | Newly added | Explicitly specifies the task type for the current session, which is identified and controlled by [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control). For example: `SET @@tidb_request_source_type = "background"`. |
| [`tidb_schema_version_cache_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_schema_version_cache_limit-new-in-v740) | Newly added | This variable limits how many historical schema versions can be cached in a TiDB instance. The default value is `16`, which means that TiDB caches 16 historical schema versions by default. |
| [`tidb_service_scope`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_service_scope-new-in-v740) | Newly added | This variable is an instance-level system variable. You can use it to control the service scope of TiDB nodes under the [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework). When you set `tidb_service_scope` of a TiDB node to `background`, the DXF schedules that TiDB node to execute DXF tasks, such as [`ADD INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index) and [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into). |
| [`tidb_session_alias`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_session_alias-new-in-v740) |  Newly added | Controls the value of the `session_alias` column in the logs related to the current session. |
| [`tiflash_mem_quota_query_per_node`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_mem_quota_query_per_node-new-in-v740) | Newly added | Limits the maximum memory usage for a query on a TiFlash node. When the memory usage of a query exceeds this limit, TiFlash returns an error and terminates the query. The default value is `0`, which means no limit.|
| [`tiflash_query_spill_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_query_spill_ratio-new-in-v740) | Newly added | Controls the threshold for TiFlash [query-level spilling](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-spill-disk#query-level-spilling). The default value is `0.7`. |
| [`tikv_client_read_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#tikv_client_read_timeout-new-in-v740) | Newly added | Controls the timeout for TiDB to send a TiKV RPC read request in a query. The default value `0` indicates that the default timeout (usually 40 seconds) is used. |
