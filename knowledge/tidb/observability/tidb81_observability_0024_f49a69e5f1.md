# TiDB Dashboard introduction and feature overview

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-intro.md`
- Source Title: `TiDB Dashboard Introduction`
- Source Heading Path: `TiDB Dashboard Introduction | TiDB Dashboard Introduction > Show the overall running status of the TiDB cluster | TiDB Dashboard Introduction > Show the running status of components and hosts | TiDB Dashboard Introduction > Show distribution and trends of read and write traffic | TiDB Dashboard Introduction > Show a list of execution information of all SQL statements | TiDB Dashboard Introduction > Learn the detailed execution information of slow queries | TiDB Dashboard Introduction > Diagnose common cluster problems and generate reports | TiDB Dashboard Introduction > Query logs of all components | TiDB Dashboard Introduction > Estimate cluster capacity for resource control | TiDB Dashboard Introduction > Collect profiling data for each instance`
- Source Line Ranges: `5-72`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tidb`, `tikv`, `tiflash`, `operator`, `sql`
- Topic Tags: `dashboard`, `overview`, `cluster-status`, `component-status`, `host-status`, `traffic-heatmap`, `sql-statements`, `slow-queries`, `diagnostics`, `log-search`, `resource-control`, `profiling`, `kubernetes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0024_f49a69e5f1`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-intro.md#tidb-dashboard-introduction`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1edc96757f75674fa0a93851e6031ba0a9965a4781300ea15121cfe6070c8f12`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro#tidb-dashboard-introduction
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-intro.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for what TiDB Dashboard is, where it runs, or which built-in monitoring, diagnosing, and management features it provides for a TiDB cluster.
- Retrieval Keywords: TiDB Dashboard Introduction, TiDB Dashboard, Web UI, built into the PD component, does not require an independent deployment, available since v4.0, deploying TiDB Dashboard as an independent Pod on Kubernetes, TiDB Operator v1.4.0, cluster overview, QPS, execution time, types of SQL statements that consume the most resources, cluster information page, TiDB TiKV PD TiFlash components, host status, Key Visualizer, heatmap, read and write traffic, hotspot issues, SQL Statements page, execution information of all SQL statements, Slow Queries page, diagnostic feature, common risks, inconsistent configurations, generate reports, Search Logs page, search logs of all running instances, Resource Manager page, resource control, resource groups, quotas, Profile Instances Page, collect profiling data
- Follow-up Guidance: The source points to related pages for details, including TiDB Dashboard Overview, Cluster Information Page, Key Visualizer Page, SQL Statements Page, Slow Queries Page, Cluster Diagnostics Page, Search Logs Page, Resource Manager page, and Profile Instances Page.
- Classification Note: This chunk is classified as observability for the dashboard component because it introduces TiDB Dashboard as the built-in Web UI for cluster monitoring and diagnostics and summarizes status, traffic, SQL, slow query, diagnostics, log search, capacity, and profiling features.

## Official Source Content

# TiDB Dashboard Introduction

TiDB Dashboard is a Web UI for monitoring, diagnosing, and managing the TiDB cluster, which is available since v4.0. It is built into the PD component and does not require an independent deployment.

> **Note:**
>
> TiDB v6.5.0 (and later) and TiDB Operator v1.4.0 (and later) support deploying TiDB Dashboard as an independent Pod on Kubernetes. For details, see [Deploy TiDB Dashboard independently in TiDB Operator](https://docs.pingcap.com/tidb-in-kubernetes/v1.6/get-started#deploy-tidb-dashboard-independently).

![TiDB Dashboard interface](/media/dashboard/dashboard-intro.gif)

TiDB Dashboard is open-sourced on [GitHub](https://github.com/pingcap-incubator/tidb-dashboard).

This document introduces the main features of TiDB Dashboard. You can click links in the following sections to learn more details.
## Show the overall running status of the TiDB cluster

You can use TiDB Dashboard to learn the TiDB cluster's queries per second (QPS), execution time, the types of SQL statements that consume the most resources, and other overview information.

See [TiDB Dashboard Overview](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-overview) for details.
## Show the running status of components and hosts

You can use TiDB Dashboard to view the running status of TiDB, TiKV, PD, TiFlash components in the entire cluster and the running status of the host on which these components are located.

See [TiDB Dashboard Cluster Information Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-cluster-info) for details.
## Show distribution and trends of read and write traffic

The Key Visualizer feature of TiDB Dashboard visually shows the change of read and write traffic over time in the entire cluster in the form of heatmap. You can use this feature to timely discover changes of application modes or locate hotspot issues with uneven performance.

See [Key Visualizer Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-key-visualizer) for details.
## Show a list of execution information of all SQL statements

The execution information of all SQL statements is listed on the SQL Statements page. You can use this page to learn the execution time and total executions at all stages, which helps you analyze and locate the SQL queries that consume the most resources and improve the overall cluster performance.

See [SQL Statements Page of TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-statement-list) for details.
## Learn the detailed execution information of slow queries

The Slow Queries page of TiDB Dashboard shows a list of all SQL statements that take a long time to execute, including the SQL texts and execution information. This page helps you locate the cause of slow queries or performance jitter.

See [Slow Queries Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-slow-query) for details.
## Diagnose common cluster problems and generate reports

The diagnostic feature of TiDB Dashboard automatically determines whether some common risks (such as inconsistent configurations) or problems exist in the cluster, generates reports, and gives operation suggestions, or compares the status of each cluster metric in different time ranges for you to analyze possible problems.

See [TiDB Dashboard Cluster Diagnostics Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-diagnostics-access) for details.
## Query logs of all components

On the Search Logs page of TiDB Dashboard, you can quickly search logs of all running instances in the cluster by keywords, time range, and other conditions, package these logs, and download them to your local machine.

See [Search Logs Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-log-search) for details.
## Estimate cluster capacity for resource control

To implement resource isolation using the [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) feature, cluster administrators can create resource groups and set quotas for each group.

Before resource planning, you need to know the overall capacity of the cluster. For more details, see [Resource Manager page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-resource-manager).
## Collect profiling data for each instance

This is an advanced debugging feature that lets you profile each instance online and analyze various internal operations an instance performed during the profiling data collection period and the proportion of the operation execution time in this period without third-party tools.

See [Profile Instances Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-profiling) for details.
