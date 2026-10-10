# TiDB Cloud metrics available to Datadog

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitor-datadog-integration.md`
- Source Title: `Integrate TiDB Cloud with Datadog (Beta)`
- Source Heading Path: `Integrate TiDB Cloud with Datadog (Beta) > Metrics available to Datadog`
- Source Line Ranges: `49-70`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `metrics`, `datadog`, `labels`, `gauges`, `counts`, `cluster-monitoring`, `dashboard`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0094_55ddcea314`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitor-datadog-integration.md#metrics-available-to-datadog`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c2ebd57d600a16dc2b9f77fbea93a5431b72b1cd19ca92e96f9344d969c9e16e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-datadog-integration#metrics-available-to-datadog
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitor-datadog-integration.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact Datadog metric names, metric types, labels, and descriptions that TiDB Cloud exposes for cluster monitoring.
- Retrieval Keywords: Metrics available to Datadog, tidb_cloud.db_database_time, tidb_cloud.db_query_per_second, tidb_cloud.db_average_query_duration, tidb_cloud.db_failed_queries, tidb_cloud.db_total_connection, tidb_cloud.db_active_connections, tidb_cloud.db_disconnections, tidb_cloud.db_command_per_second, tidb_cloud.db_queries_using_plan_cache_ops, tidb_cloud.db_transaction_per_second, tidb_cloud.node_storage_used_bytes, tidb_cloud.node_storage_capacity_bytes, tidb_cloud.node_cpu_seconds_total, tidb_cloud.node_cpu_capacity_cores, tidb_cloud.node_memory_used_bytes, tidb_cloud.node_memory_capacity_bytes, cluster_name, instance, component, sql_type, txn_mode, type, result
- Follow-up Guidance: The metric labels shown here include dimensions such as cluster_name, instance, component, sql_type, txn_mode, type, and result for filtering TiDB, TiKV, and TiFlash metrics in Datadog.
- Classification Note: This is classified as observability because the content is a metrics catalog for Datadog, listing monitoring identifiers, label dimensions, metric types, and what each metric measures.

## Official Source Content

## Metrics available to Datadog

Datadog tracks the following metric data for your TiDB clusters.

| Metric name  | Metric type | Labels | Description                                   |
| :------------| :---------- | :------| :----------------------------------------------------- |
| tidb_cloud.db_database_time| gauge | sql_type: Select\|Insert\|...<br/>cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…<br/>component: `tidb` | The total time consumed by all SQL statements running in TiDB per second, including the CPU time of all processes and the non-idle waiting time. |
| tidb_cloud.db_query_per_second| gauge | type: Select\|Insert\|...<br/>cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…<br/>component: `tidb` | The number of SQL statements executed per second on all TiDB instances, which is counted according to SELECT, INSERT, UPDATE, and other types of statements. |
| tidb_cloud.db_average_query_duration| gauge | sql_type: Select\|Insert\|...<br/>cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…<br/>component: `tidb` | The duration between the time that the client's network request is sent to TiDB and the time that the request is returned to the client after TiDB has executed it. |
| tidb_cloud.db_failed_queries| gauge | type: executor:xxxx\|parser:xxxx\|...<br/>cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…<br/>component: `tidb` | The statistics of error types (such as syntax errors and primary key conflicts) according to the SQL execution errors that occur per second on each TiDB instance. |
| tidb_cloud.db_total_connection| gauge | cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…<br/>component: `tidb` | The number of current connections in your TiDB server. |
| tidb_cloud.db_active_connections| gauge | cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…<br/>component: `tidb` | The number of active connections. |
| tidb_cloud.db_disconnections| gauge | result: ok\|error\|undetermined<br/>cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…<br/>component: `tidb` | The number of disconnected clients. |
| tidb_cloud.db_command_per_second| gauge | type: Query\|StmtPrepare\|...<br/>cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…<br/>component: `tidb` | The number of commands processed by TiDB per second, which is classified according to the success or failure of command execution results. |
| tidb_cloud.db_queries_using_plan_cache_ops| gauge | cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…<br/>component: `tidb` | The statistics of queries using [Plan Cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache) per second. The execution plan cache only supports the prepared statement command. |
| tidb_cloud.db_transaction_per_second| gauge | txn_mode: pessimistic\|optimistic<br/>type: abort\|commit\|...<br/>cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…<br/>component: `tidb` | The number of transactions executed per second. |
| tidb_cloud.node_storage_used_bytes | gauge | cluster_name: `<cluster name>`<br/>instance: tikv-0\|tikv-1…\|tiflash-0\|tiflash-1…<br/>component: tikv\|tiflash | The disk usage of TiKV/TiFlash nodes, in bytes. |
| tidb_cloud.node_storage_capacity_bytes | gauge | cluster_name: `<cluster name>`<br/>instance: tikv-0\|tikv-1…\|tiflash-0\|tiflash-1…<br/>component: tikv\|tiflash | The disk capacity of TiKV/TiFlash nodes, in bytes. |
| tidb_cloud.node_cpu_seconds_total | count | cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…\|tikv-0…\|tiflash-0…<br/>component: tidb\|tikv\|tiflash | The CPU usage of TiDB/TiKV/TiFlash nodes. |
| tidb_cloud.node_cpu_capacity_cores | gauge | cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…\|tikv-0…\|tiflash-0…<br/>component: tidb\|tikv\|tiflash | The limit on CPU cores of TiDB/TiKV/TiFlash nodes. |
| tidb_cloud.node_memory_used_bytes | gauge | cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…\|tikv-0…\|tiflash-0…<br/>component: tidb\|tikv\|tiflash | The used memory of TiDB/TiKV/TiFlash nodes, in bytes. |
| tidb_cloud.node_memory_capacity_bytes | gauge | cluster_name: `<cluster name>`<br/>instance: tidb-0\|tidb-1…\|tikv-0…\|tiflash-0…<br/>component: tidb\|tikv\|tiflash | The memory capacity of TiDB/TiKV/TiFlash nodes, in bytes. |
