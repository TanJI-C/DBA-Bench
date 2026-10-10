# Dashboard overview page features and access

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-overview.md`
- Source Title: `Overview Page`
- Source Heading Path: `Overview Page | Overview Page > Access the page | Overview Page > QPS | Overview Page > Latency | Overview Page > Top SQL statements | Overview Page > Recent slow queries | Overview Page > Instances | Overview Page > Monitor and alert`
- Source Line Ranges: `5-94`
- Source Scope: `shared`
- Primary Component: `dashboard`
- Related Components: `shared`, `sql`, `tidb`, `tikv`, `pd`, `tiflash`
- Topic Tags: `overview`, `access`, `qps`, `latency`, `top-sql`, `slow-queries`, `instances`, `monitoring`, `alerts`, `grafana`, `alertmanager`, `diagnostics`, `prometheus`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0031_d672e31f46`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-overview.md#overview-page`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6bd8c0e31fcf3e0d62c5f987a24025fe8cdb28f8b926ab95d07b4e869fa36003`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-overview#overview-page
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about what the TiDB Dashboard Overview page shows, how to access it, or which cluster summary sections and linked monitoring pages are available there.
- Retrieval Keywords: Overview Page, Access the page, Overview, QPS, Latency, Top SQL statements, Recent slow queries, Instances, Monitor and alert, TiDB Dashboard, Prometheus, SQL Statements Page, Slow Queries Page, Cluster Info Page, View Metrics, Grafana dashboard, View Alerts, AlertManager, Run Diagnostics, tidb_slow_log_threshold, instance.tidb_slow_log_threshold
- Follow-up Guidance: The content points to the SQL Statements Page, Slow Queries Page, Cluster Info Page, Grafana dashboard, AlertManager page, and cluster diagnostics page for more detailed information.
- Classification Note: This is classified as observability for the dashboard component because it describes the Overview page sections for cluster QPS, latency, Top SQL, slow queries, instance status, monitoring, alerts, and diagnostics access.

## Official Source Content

# Overview Page

This page shows the overview of the entire TiDB cluster, including the following information:

- Queries per second (QPS) of the entire cluster.
- The query latency of the entire cluster.
- The SQL statements that have accumulated the longest execution time over the recent period.
- The slow queries whose execution time over the recent period exceeds the threshold.
- The node count and status of each instance.
- Monitor and alert messages.
## Access the page

After logging in to TiDB Dashboard, the overview page is entered by default, or you can click **Overview** in the left navigation menu to enter this page:

![Enter overview page](/media/dashboard/dashboard-overview-access-v650.png)
## QPS

This area shows the number of successful and failed queries per second for the entire cluster over the recent hour:

![QPS](/media/dashboard/dashboard-overview-qps.png)

> **Note:**
>
> This feature is available only in the cluster where the Prometheus monitoring component is deployed. If Prometheus is not deployed, an error will be displayed.
## Latency

This area shows the latency of 99.9%, 99%, and 90% of queries in the entire cluster over the recent one hour:

![Latency](/media/dashboard/dashboard-overview-latency.png)

> **Note:**
>
> This feature is available only on the cluster where the Prometheus monitoring component is deployed. If Prometheus is not deployed, an error will be displayed.
## Top SQL statements

This area shows the ten types of SQL statements that have accumulated the longest execution time in the entire cluster over the recent period. SQL statements with different query parameters but of the same structure are classified into the same SQL type and displayed in the same row:

![Top SQL](/media/dashboard/dashboard-overview-top-statements.png)

The information shown in this area is consistent with the more detailed [SQL Statements Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-statement-list). You can click the **Top SQL Statements** heading to view the complete list. For details of the columns in this table, see [SQL Statements Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-statement-list).

> **Note:**
>
> This feature is available only on the cluster where SQL Statements feature is enabled.
## Recent slow queries

By default, this area shows the latest 10 slow queries in the entire cluster over the recent 30 minutes:

![Recent slow queries](/media/dashboard/dashboard-overview-slow-query.png)

By default, the SQL query that is executed longer than 300 milliseconds is counted as a slow query and displayed on the table. You can change this threshold by modifying the [tidb_slow_log_threshold](https://docs.pingcap.com/tidb/stable/system-variables#tidb_slow_log_threshold) variable or the [instance.tidb_slow_log_threshold](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_slow_log_threshold) TiDB parameter.

The content displayed in this area is consistent with the more detailed [Slow Queries Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-slow-query). You can click the **Recent Slow Queries** title to view the complete list. For details of the columns in this table, see this [Slow Queries Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-slow-query).

> **Note:**
>
> This feature is available only in the cluster with slow query logs enabled. By default, slow query logs are enabled in the cluster deployed using TiUP.
## Instances

This area summarizes the total number of instances and abnormal instances of TiDB, TiKV, PD, and TiFlash in the entire cluster:

![Instances](/media/dashboard/dashboard-overview-instances.png)

The statuses in the preceding image are described as follows:

- Up: The instance is running properly (including the offline storage instance).
- Down: The instance is running abnormally, such as network disconnection and process crash.

Click the **Instance** title to enter the [Cluster Info Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-cluster-info) that shows the detailed running status of each instance.
## Monitor and alert

This area provides links for you to view detailed monitor and alert:

![Monitor and alert](/media/dashboard/dashboard-overview-monitor.png)

- **View Metrics**: Click this link to jump to the Grafana dashboard where you can view detailed monitoring information of the cluster. For details of each monitoring metric in the Grafana dashboard, see [monitoring metrics](https://docs.pingcap.com/tidb/stable/grafana-overview-dashboard).
- **View Alerts**: Click this link to jump to the AlertManager page where you can view detailed alert information of the cluster. If alerts exist in the cluster, the number of alerts is directly shown in the link text.
- **Run Diagnostics**: Click this link to jump to the more detailed [cluster diagnostics page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-diagnostics-access).

> **Note:**
>
> The **View Metrics** link is available only in the cluster where the Grafana node is deployed. The **View Alerts** link is available only in the cluster where the AlertManager node is deployed.
