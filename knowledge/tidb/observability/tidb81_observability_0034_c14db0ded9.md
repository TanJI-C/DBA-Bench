# Access and use the Slow Queries list

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-slow-query.md`
- Source Title: `Slow Queries Page of TiDB Dashboard`
- Source Heading Path: `Slow Queries Page of TiDB Dashboard | Slow Queries Page of TiDB Dashboard > Access the page | Slow Queries Page of TiDB Dashboard > Access the page > Change filters | Slow Queries Page of TiDB Dashboard > Access the page > Display more columns | Slow Queries Page of TiDB Dashboard > Access the page > Export slow queries locally | Slow Queries Page of TiDB Dashboard > Access the page > Sort by column`
- Source Line Ranges: `5-49`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tidb`, `shared`
- Topic Tags: `slow-queries`, `access`, `filters`, `columns`, `export`, `sorting`, `slow-query-log`, `threshold`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0034_c14db0ded9`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-slow-query.md#slow-queries-page-of-tidb-dashboard`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `17a44a67c5f892b3e7a674ec3b0fcec1dc67191fa8f078bf1f62dee84b62abea`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-slow-query#slow-queries-page-of-tidb-dashboard
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-slow-query.md

## Retrieval Guidance

- Use When: Use this when you need TiDB Dashboard slow query page access details, filter options, available columns, CSV export behavior, default sorting, or the slow query threshold and log prerequisites.
- Retrieval Keywords: Slow Queries page, TiDB Dashboard, slow query logs, tidb_slow_log_threshold, instance.tidb_slow_log_threshold, tidb_enable_slow_log, Slow Queries left navigation menu, /dashboard/#/slow_query, time range filter, related database filter, SQL keywords, SQL types, number of slow queries to be displayed, Columns, Export CSV, Finish Time descending
- Follow-up Guidance: The page data comes from TiDB slow query system tables and slow query logs, and the feature is unavailable if the slow query log is disabled.
- Classification Note: This is classified as observability because the content describes using the Dashboard Slow Queries page to search, view, filter, sort, and export slow query records in a cluster.

## Official Source Content

# Slow Queries Page of TiDB Dashboard

On the Slow Queries page of TiDB Dashboard, you can search and view all slow queries in the cluster.

By default, SQL queries with an execution time of more than 300 milliseconds are considered as slow queries. These queries are recorded in the [slow query logs](https://docs.pingcap.com/tidb/stable/identify-slow-queries) and can be searched via TiDB Dashboard. You can adjust the threshold of slow queries through the [`tidb_slow_log_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_slow_log_threshold) session variable or the [`instance.tidb_slow_log_threshold`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_slow_log_threshold) TiDB parameter.

> **Note:**
>
> If the slow query log is disabled, this feature will be unavailable. The slow query log is enabled by default, and you can enable or disable it through the system variable [`tidb_enable_slow_log`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_slow_log).
## Access the page

You can use one of the following two methods to access the slow query page:

* After logging in to TiDB Dashboard, click **Slow Queries** in the left navigation menu.

* Visit <http://127.0.0.1:2379/dashboard/#/slow_query> in your browser. Replace `127.0.0.1:2379` with the actual PD address and port.

All data displayed on the slow query page comes from TiDB slow query system tables and slow query logs. See [slow query logs](https://docs.pingcap.com/tidb/stable/identify-slow-queries) for details.
### Change filters

You can filter slow queries based on the time range, the related database, SQL keywords, SQL types, the number of slow queries to be displayed. In the image below, 100 slow queries over the recent 30 minutes are displayed by default.

![Modify list filters](/media/dashboard/dashboard-slow-queries-list1-v620.png)
### Display more columns

Click **Columns** on the page and you can choose to see more columns. You can move your mouse to the **(i)** icon at the right side of a column name to view the description of this column:

![Show more columns](/media/dashboard/dashboard-slow-queries-list2-v620.png)
### Export slow queries locally

Click ☰ (**More**) in the upper-right corner of the page to display the **Export** option. After you click **Export**, TiDB Dashboard exports slow queries in the current list as a CSV file.

![Export slow queries locally](/media/dashboard/dashboard-slow-queries-export-v651.png)
### Sort by column

By default, the list is sorted by **Finish Time** in the descending order. Click column headings to sort by the column or switch the sorting order:

![Modify sorting basis](/media/dashboard/dashboard-slow-queries-list3-v620.png)
