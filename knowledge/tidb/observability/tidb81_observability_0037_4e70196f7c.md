# Top SQL overview, scenarios, and access

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/top-sql.md`
- Source Title: `TiDB Dashboard Top SQL page`
- Source Heading Path: `TiDB Dashboard Top SQL Page | TiDB Dashboard Top SQL Page > Recommended scenarios | TiDB Dashboard Top SQL Page > Access the page`
- Source Line Ranges: `5-43`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `top sql`, `cpu overhead`, `real-time monitoring`, `performance analysis`, `supported scenarios`, `unsupported scenarios`, `access`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0037_4e70196f7c`
- Source ID: `tidb-docs-8.1:dashboard/top-sql.md#tidb-dashboard-top-sql-page`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1813b15700d5d55b02dc8c754ddca0f1f2396b2c41987bde6db056eb244e00eb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/top-sql#tidb-dashboard-top-sql-page
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/top-sql.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants to know what the Top SQL page shows, which performance-analysis scenarios it supports or does not support, and how to access it in TiDB Dashboard.
- Retrieval Keywords: Top SQL page, CPU overhead, real-time monitoring, top 5 SQL statements, queries per second, average latency, query plan, specific TiDB instance, specific TiKV instance, performance issues, CPU hotspots, high CPU usage, unsupported scenarios, transaction lock conflicts, incorrect data, abnormal crashes, Access the page, Top SQL in the left navigation menu, http://127.0.0.1:2379/dashboard/#/topsql, PD instance address and port
- Follow-up Guidance: If the user needs feature enablement, instance selection, refresh, disabling, or FAQ details, the next relevant content is the Enable Top SQL, Use Top SQL, Disable Top SQL, and Frequently asked questions sections.
- Classification Note: This chunk is classified as observability for the dashboard component because the official content describes monitoring and visual analysis of SQL CPU overhead on the TiDB Dashboard Top SQL page.

## Official Source Content

# TiDB Dashboard Top SQL Page

With Top SQL, you can monitor and visually explore the CPU overhead of each SQL statement in your database in real-time, which helps you optimize and resolve database performance issues. Top SQL continuously collects and stores CPU load data summarized by SQL statements at any seconds from all TiDB and TiKV instances. The collected data can be stored for up to 30 days. Top SQL presents you with visual charts and tables to quickly pinpoint which SQL statements are contributing the high CPU load of a TiDB or TiKV instance over a certain period of time.

Top SQL provides the following features:

* Visualize the top 5 types of SQL statements with the highest CPU overhead through charts and tables.
* Display detailed execution information such as queries per second, average latency, and query plan.
* Collect all SQL statements that are executed, including those that are still running.
* Allow viewing data of a specific TiDB and TiKV instance.
## Recommended scenarios

Top SQL is suitable for analyzing performance issues. The following are some typical Top SQL scenarios:

* You discovered that an individual TiKV instance in the cluster has a very high CPU usage through the Grafana charts. You want to know which SQL statements cause the CPU hotspots so that you can optimize them and better leverage all of your distributed resources.
* You discovered that the cluster has a very high CPU usage overall and queries are slow. You want to quickly figure out which SQL statements are currently consuming the most CPU resources so that you can optimize them.
* The CPU usage of the cluster has drastically changed and you want to know the major cause.
* Analyze the most resource-intensive SQL statements in the cluster and optimize them to reduce hardware costs.

Top SQL cannot be used to pinpoint non-performance issues, such as incorrect data or abnormal crashes.

The Top SQL feature is still in an early stage and is being continuously enhanced. Here are some scenarios that are **not supported** at the moment:

* Analyzing the overhead of SQL statements outside of Top 5 (for example, when multiple business workloads are mixed).
* Analyzing the overhead of Top N SQL statements by various dimensions such as users and databases.
* Analyzing database performance issues that are not caused by high CPU load, such as transaction lock conflicts.
## Access the page

You can access the Top SQL page using either of the following methods:

* After logging in to TiDB Dashboard, click **Top SQL** in the left navigation menu.

  ![Top SQL](/media/dashboard/top-sql-access.png)

* Visit <http://127.0.0.1:2379/dashboard/#/topsql> in your browser. Replace `127.0.0.1:2379` with the actual PD instance address and port.
