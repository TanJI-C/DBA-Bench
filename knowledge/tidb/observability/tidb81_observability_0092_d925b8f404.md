# TiDB Cloud built-in alert conditions and recommended actions

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitor-built-in-alerting.md`
- Source Title: `TiDB Cloud Built-in Alerting`
- Source Heading Path: `TiDB Cloud Built-in Alerting > TiDB Cloud built-in alert conditions | TiDB Cloud Built-in Alerting > TiDB Cloud built-in alert conditions > Resource usage alerts | TiDB Cloud Built-in Alerting > TiDB Cloud built-in alert conditions > Data migration alerts`
- Source Line Ranges: `51-87`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`, `dm`
- Topic Tags: `alert-conditions`, `resource-usage`, `memory`, `cpu`, `storage`, `data-migration`, `replication-lag`, `thresholds`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0092_d925b8f404`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitor-built-in-alerting.md#tidb-cloud-built-in-alert-conditions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c67dba8f33e09bf4971ab2e830be05a19fb9420ac65876ab6607a80c341313d4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-built-in-alerting#tidb-cloud-built-in-alert-conditions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitor-built-in-alerting.md

## Retrieval Guidance

- Use When: Use this chunk when the user is looking up TiDB Cloud built-in alert conditions, their thresholds, and the corresponding recommended actions for resource usage or data migration alerts.
- Retrieval Keywords: TiDB Cloud built-in alert conditions, Resource usage alerts, Data migration alerts, Total TiDB node memory utilization across cluster exceeded 70% for 10 minutes, Total TiKV node memory utilization across cluster exceeded 70% for 10 minutes, Total TiFlash node memory utilization across cluster exceeded 70% for 10 minutes, Total TiDB node CPU utilization exceeded 80% for 10 minutes, Total TiKV node CPU utilization exceeded 80% for 10 minutes, Total TiFlash node CPU utilization exceeded 80% for 10 minutes, TiKV storage utilization exceeds 80%, TiFlash storage utilization exceeds 80%, Max memory utilization across TiDB nodes exceeded 70% for 10 minutes, Max memory utilization across TiKV nodes exceeded 70% for 10 minutes, Max CPU utilization across TiDB nodes exceeded 80% for 10 minutes, Max CPU utilization across TiKV nodes exceeded 80% for 10 minutes, hotspot, Data migration job met error during data export, Data migration job met error during data import, Data migration job met error during incremental migration, Data migration job has been paused for more than 6 hours during incremental migration, Replication lag is larger than 10 minutes and still increasing for more than 20 minutes, Troubleshoot data migration
- Follow-up Guidance: The source adds that these conditions are often early warning indicators, thresholds can be edited on the TiDB Cloud console, and some alert rules are disabled by default and can be enabled as needed.
- Classification Note: This is classified under observability for the cloud component because it lists built-in alert conditions and recommended actions covering TiDB, TiKV, TiFlash resource usage and data migration alert scenarios.

## Official Source Content

## TiDB Cloud built-in alert conditions

The following table provides the TiDB Cloud built-in alert conditions and the corresponding recommended actions.

> **Note:**
>
> - While these alert conditions do not necessarily mean there is a problem, they are often early warning indicators of emerging issues. Therefore, taking the recommended action is advised.
> - You can edit the thresholds of the alerts on the TiDB Cloud console. 
> - Some alert rules are disabled by default. You can enable them as needed. 
### Resource usage alerts

| Condition | Recommended Action |
|:--- |:--- |
| Total TiDB node memory utilization across cluster exceeded 70% for 10 minutes | Consider increasing the node number or node size for TiDB to reduce the memory usage percentage of the current workload.|
| Total TiKV node memory utilization across cluster exceeded 70% for 10 minutes | Consider increasing the node number or node size for TiKV to reduce the memory usage percentage of the current workload. |
| Total TiFlash node memory utilization across cluster exceeded 70% for 10 minutes | Consider increasing the node number or node size for TiFlash to reduce the memory usage percentage of the current workload. |
| Total TiDB node CPU utilization exceeded 80% for 10 minutes | Consider increasing the node number or node size for TiDB to reduce the CPU usage percentage of the current workload.|
| Total TiKV node CPU utilization exceeded 80% for 10 minutes | Consider increasing the node number or node size for TiKV to reduce the CPU usage percentage of the current workload. |
| Total TiFlash node CPU utilization exceeded 80% for 10 minutes | Consider increasing the node number or node size for TiFlash to reduce the CPU usage percentage of the current workload. |
| TiKV storage utilization exceeds 80% | Consider increasing the node number or node storage size for TiKV to increase your storage capacity. |
| TiFlash storage utilization exceeds 80% | Consider increasing the node number or node storage size for TiFlash to increase your storage capacity. |
| Max memory utilization across TiDB nodes exceeded 70% for 10 minutes | Consider checking if there is any [hotspot](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sql-tuning-overview#hotspot-issues) in the cluster or increasing the node number or node size for TiDB to reduce the memory usage percentage of the current workload. |
| Max memory utilization across TiKV nodes exceeded 70% for 10 minutes | Consider checking if there is any [hotspot](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sql-tuning-overview#hotspot-issues) in the cluster or increasing the node number or node size for TiKV to reduce the memory usage percentage of the current workload. |
| Max CPU utilization across TiDB nodes exceeded 80% for 10 minutes | Consider checking if there is any [hotspot](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sql-tuning-overview#hotspot-issues) in the cluster or increasing the node number or node size for TiDB to reduce the CPU usage percentage of the current workload. |
| Max CPU utilization across TiKV nodes exceeded 80% for 10 minutes | Consider checking if there is any [hotspot](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sql-tuning-overview#hotspot-issues) in the cluster or increasing the node number or node size for TiKV to reduce the CPU usage percentage of the current workload. |
### Data migration alerts

| Condition | Recommended Action |
|:--- |:--- |
| Data migration job met error during data export | Check the error and see [Troubleshoot data migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting#migration-errors-and-solutions) for help. |
| Data migration job met error during data import | Check the error and see [Troubleshoot data migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting#migration-errors-and-solutions) for help. |
| Data migration job met error during incremental migration | Check the error and see [Troubleshoot data migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting#migration-errors-and-solutions) for help. |
| Data migration job has been paused for more than 6 hours during incremental migration | Data migration job has been paused for more than 6 hours during data incremental migration. The binlog in the upstream database might be purged (depending on your database binlog purge strategy) and might cause incremental migration to fail. See [Troubleshoot data migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting#migration-errors-and-solutions) for help. |
| Replication lag is larger than 10 minutes and still increasing for more than 20 minutes | See [Troubleshoot data migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting#migration-errors-and-solutions) for help. |
