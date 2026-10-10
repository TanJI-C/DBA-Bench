# TiDB Cloud system table limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/limited-sql-features.md`
- Source Title: `Limited SQL Features on TiDB Cloud`
- Source Heading Path: `Limited SQL features on TiDB Cloud > System tables`
- Source Line Ranges: `71-121`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`, `pd`, `tikv`
- Topic Tags: `system-tables`, `information-schema`, `performance-schema`, `mysql-schema`, `cluster-metadata`, `slow-query`, `statement-summary`, `placement-policies`, `resource-groups`, `serverless`, `dedicated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0812_c9b9d85257`
- Source ID: `tidb-docs-8.1:tidb-cloud/limited-sql-features.md#system-tables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `024f0af4f3ebc2a97ddedc4ea24a2688b810c386860015e96bc55037d0397e71`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/limited-sql-features#system-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/limited-sql-features.md

## Retrieval Guidance

- Use When: Use this chunk when verifying whether a system table in information_schema, performance_schema, or mysql is supported in TiDB Cloud Dedicated or TiDB Cloud Serverless.
- Retrieval Keywords: TiDB Cloud system table limitations, System tables TiDB Cloud, information_schema support TiDB Cloud, performance_schema support TiDB Cloud, mysql schema support TiDB Cloud, information_schema ATTRIBUTES, information_schema CLUSTER_INFO, information_schema CLUSTER_SLOW_QUERY, information_schema CLUSTER_STATEMENTS_SUMMARY, information_schema PLACEMENT_POLICIES, information_schema RESOURCE_GROUPS, information_schema SLOW_QUERY, information_schema STATEMENTS_SUMMARY, information_schema TIDB_HOT_REGIONS_HISTORY, information_schema TIDB_SERVERS_INFO, information_schema TIKV_REGION_PEERS, information_schema TIKV_REGION_STATUS, information_schema TIKV_STORE_STATUS, information_schema CLUSTER_CONFIG, information_schema CLUSTER_HARDWARE, information_schema METRICS_TABLES, performance_schema pd_profile_cpu, performance_schema tidb_profile_cpu, performance_schema tikv_profile_cpu, mysql expr_pushdown_blacklist, mysql gc_delete_range, mysql opt_rule_blacklist, mysql tidb
- Follow-up Guidance: 
- Classification Note: This is a reference chunk because it is a support matrix listing which system tables are supported or not supported on TiDB Cloud Dedicated and Serverless.

## Official Source Content

## System tables

| Database | Table | TiDB Cloud Dedicated | TiDB Cloud Serverless |
|:-|:-|:-|:-|
| `information_schema` | `ATTRIBUTES` | Supported | Not supported [^1] |
| `information_schema` | `CLUSTER_CONFIG` | Not supported [^4] | Not supported [^4] |
| `information_schema` | `CLUSTER_HARDWARE` | Not supported [^4] | Not supported [^4] |
| `information_schema` | `CLUSTER_INFO` | Supported | Not supported [^1] |
| `information_schema` | `CLUSTER_LOAD` | Not supported [^4] | Not supported [^4] |
| `information_schema` | `CLUSTER_LOG` | Not supported [^4] | Not supported [^4] |
| `information_schema` | `CLUSTER_SLOW_QUERY` | Supported | Not supported [^5] |
| `information_schema` | `CLUSTER_STATEMENTS_SUMMARY` | Supported | Not supported [^6] |
| `information_schema` | `CLUSTER_STATEMENTS_SUMMARY_EVICTED` | Supported | Not supported [^6] |
| `information_schema` | `CLUSTER_STATEMENTS_SUMMARY_HISTORY` | Supported | Not supported [^6] |
| `information_schema` | `CLUSTER_SYSTEMINFO` | Not supported [^4] | Not supported [^4] |
| `information_schema` | `INSPECTION_RESULT` | Not supported [^4] | Not supported [^4] |
| `information_schema` | `INSPECTION_RULES` | Not supported [^4] | Not supported [^4] |
| `information_schema` | `INSPECTION_SUMMARY` | Not supported [^4] | Not supported [^4] |
| `information_schema` | `METRICS_SUMMARY` | Not supported [^4] | Not supported [^4] |
| `information_schema` | `METRICS_SUMMARY_BY_LABEL` | Not supported [^4] | Not supported [^4] |
| `information_schema` | `METRICS_TABLES` | Not supported [^4] | Not supported [^4] |
| `information_schema` | `PLACEMENT_POLICIES` | Supported | Not supported [^1] |
| `information_schema` | `RESOURCE_GROUPS` | Supported | Not supported [^2] |
| `information_schema` | `SLOW_QUERY` | Supported | Not supported [^5] |
| `information_schema` | `STATEMENTS_SUMMARY` | Supported | Not supported [^6] |
| `information_schema` | `STATEMENTS_SUMMARY_EVICTED` | Supported | Not supported [^6] |
| `information_schema` | `TIDB_HOT_REGIONS` | Not supported [^4] | Not supported [^4] |
| `information_schema` | `TIDB_HOT_REGIONS_HISTORY` | Supported | Not supported [^1] |
| `information_schema` | `TIDB_SERVERS_INFO` | Supported | Not supported [^1] |
| `information_schema` | `TIKV_REGION_PEERS` | Supported | Not supported [^1] |
| `information_schema` | `TIKV_REGION_STATUS` | Supported | Not supported [^1] |
| `information_schema` | `TIKV_STORE_STATUS` | Supported | Not supported [^1] |
| `performance_schema` | `pd_profile_allocs` | Not supported [^4] | Not supported [^4] |
| `performance_schema` | `pd_profile_block` | Not supported [^4] | Not supported [^4] |
| `performance_schema` | `pd_profile_cpu` | Not supported [^4] | Not supported [^4] |
| `performance_schema` | `pd_profile_goroutines` | Not supported [^4] | Not supported [^4] |
| `performance_schema` | `pd_profile_memory` | Not supported [^4] | Not supported [^4] |
| `performance_schema` | `pd_profile_mutex` | Not supported [^4] | Not supported [^4] |
| `performance_schema` | `tidb_profile_allocs` | Not supported [^4] | Not supported [^4] |
| `performance_schema` | `tidb_profile_block` | Not supported [^4] | Not supported [^4] |
| `performance_schema` | `tidb_profile_cpu` | Not supported [^4] | Not supported [^4] |
| `performance_schema` | `tidb_profile_goroutines` | Not supported [^4] | Not supported [^4] |
| `performance_schema` | `tidb_profile_memory` | Not supported [^4] | Not supported [^4] |
| `performance_schema` | `tidb_profile_mutex` | Not supported [^4] | Not supported [^4] |
| `performance_schema` | `tikv_profile_cpu` | Not supported [^4] | Not supported [^4] |
| `mysql` | `expr_pushdown_blacklist` | Not supported [^4] | Not supported [^4] |
| `mysql` | `gc_delete_range` | Not supported [^4] | Not supported [^4] |
| `mysql` | `gc_delete_range_done` | Not supported [^4] | Not supported [^4] |
| `mysql` | `opt_rule_blacklist` | Not supported [^4] | Not supported [^4] |
| `mysql` | `tidb` | Not supported [^4] | Not supported [^4] |
