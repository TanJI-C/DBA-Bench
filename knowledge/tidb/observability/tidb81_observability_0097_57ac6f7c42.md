# Cluster and node status in TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitor-tidb-cluster.md`
- Source Title: `Monitor a TiDB Cluster`
- Source Heading Path: `Monitor a TiDB Cluster | Monitor a TiDB Cluster > Cluster status and node status | Monitor a TiDB Cluster > Cluster status and node status > Cluster status | Monitor a TiDB Cluster > Cluster status and node status > TiDB node status | Monitor a TiDB Cluster > Cluster status and node status > TiKV node status`
- Source Line Ranges: `5-54`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`
- Topic Tags: `cluster status`, `node status`, `health`, `availability`, `dedicated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0097_57ac6f7c42`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitor-tidb-cluster.md#monitor-a-tidb-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e163c2177e8e19bd2dc098c1b79ecec12ec96a3da1e39e7f4107607637ad58c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-tidb-cluster#monitor-a-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitor-tidb-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when identifying TiDB Cloud cluster status meanings or TiDB and TiKV node status meanings shown on the cluster page.
- Retrieval Keywords: Cluster status, Available, Creating, Importing, Maintaining, Modifying, Unavailable, Pausing, Paused, Resuming, Restoring, TiDB node status, TiKV node status, TiDB Cloud Dedicated clusters, cluster page, node status
- Follow-up Guidance: The content notes that TiDB node status and TiKV node status are only available for TiDB Cloud Dedicated clusters.
- Classification Note: This is classified as observability for TiDB Cloud because it defines health and availability status values for clusters and nodes shown in the monitoring view.

## Official Source Content

# Monitor a TiDB Cluster

This document describes how to monitor a TiDB cluster on TiDB Cloud.
## Cluster status and node status

You can see the current status of each running cluster on the cluster page.
### Cluster status

| Cluster status | Description |
|:--|:--|
| **Available** | The cluster is healthy and available. |
| **Creating** | The cluster is being created. The cluster is inaccessible while it is being created. |
| **Importing** | Importing data into the cluster. |
| **Maintaining** | The cluster is in maintenance. |
| **Modifying** | The cluster is being modified. |
| **Unavailable** | The cluster has failed and TiDB cannot recover it. |
| **Pausing** | The cluster is being paused. |
| **Paused** | The cluster is paused. |
| **Resuming** | The cluster is being resumed from a pause. |
| **Restoring** | The cluster is currently being restored from a backup. |
### TiDB node status

> **Note:**
>
> The TiDB node status is only available for TiDB Cloud Dedicated clusters.

| TiDB node status | Description |
|:--|:--|
| **Available** | The TiDB node is healthy and available. |
| **Creating** | The TiDB node is being created. |
| **Unavailable** | The TiDB node is not available. |
| **Deleting** | The TiDB node is being deleted. |
### TiKV node status

> **Note:**
>
> The TiKV node status is only available for TiDB Cloud Dedicated clusters.

| TiKV node status | Description |
|:--|:--|
| **Available** | The TiKV node is healthy and available. |
| **Creating** | The TiKV node is being created. |
| **Unavailable** | The TiKV node is not available. |
| **Deleting** | The TiKV node is being deleted. |
