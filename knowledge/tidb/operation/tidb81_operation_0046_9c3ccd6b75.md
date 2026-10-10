# Enable, use, disable, and troubleshoot Top SQL

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/top-sql.md`
- Source Title: `TiDB Dashboard Top SQL page`
- Source Heading Path: `TiDB Dashboard Top SQL Page > Enable Top SQL | TiDB Dashboard Top SQL Page > Use Top SQL | TiDB Dashboard Top SQL Page > Disable Top SQL | TiDB Dashboard Top SQL Page > Frequently asked questions`
- Source Line Ranges: `44-145`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `tikv`, `pd`, `tiup`, `operator`
- Topic Tags: `feature enablement`, `system variable`, `instance selection`, `cpu hotspot analysis`, `time range`, `refresh`, `feature disablement`, `faq`, `performance impact`, `ga status`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0046_9c3ccd6b75`
- Source ID: `tidb-docs-8.1:dashboard/top-sql.md#enable-top-sql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1987b10b9ee08b08677df6906fe99c27fd926ab8bfca918ff86e336cc53d91c0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/top-sql#enable-top-sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/top-sql.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the documented ways to enable, use, refresh, disable, or troubleshoot Top SQL, including the tidb_enable_top_sql system variable and the NgMonitoring error.
- Retrieval Keywords: Enable Top SQL, Use Top SQL, Disable Top SQL, Frequently asked questions, tidb_enable_top_sql, SET GLOBAL tidb_enable_top_sql = 1;, SET GLOBAL tidb_enable_top_sql = 0;, Open Settings, Enable Feature, Save, gear icon, Disable, wait up to 1 minute, select a particular TiDB or TiKV instance, Grafana charts, Call/sec, Scan Indexes/sec, SQL Statement page, Slow Queries page, time picker, precision of up to 1 second, Refresh button, Auto Refresh, required component NgMonitoring is not started, performance impact less than 3%, generally available (GA) feature, Other Statements, Y-axis of the Top SQL chart, running unfinished SQL statements, TiUP v1.9.0 or above, TiDB Operator v1.3.0 or above
- Follow-up Guidance: If the user asks what Top SQL is for, its supported and unsupported scenarios, or how to open the page, the overview and access sections are the related next content.
- Classification Note: This chunk is classified as operation for the dashboard component because the official content focuses on feature enablement, configuration, usage flow, disabling, and FAQ troubleshooting for Top SQL.

## Official Source Content

## Enable Top SQL

> **Note:**
>
> To use Top SQL, your cluster should be deployed or upgraded with a recent version of TiUP (v1.9.0 or above) or TiDB Operator (v1.3.0 or above). If your cluster was upgraded using an earlier version of TiUP or TiDB Operator, see [FAQ](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-faq#a-required-component-ngmonitoring-is-not-started-error-is-shown) for instructions.

Top SQL is not enabled by default as it has a slight impact on cluster performance (within 3% on average) when enabled. You can enable Top SQL by the following steps:

1. Visit the [Top SQL page](#access-the-page).
2. Click **Open Settings**. On the right side of the **Settings** area, switch on **Enable Feature**.
3. Click **Save**.

After enabling the feature, wait up to 1 minute for Top SQL to load the data. Then you can see the CPU load details.

In addition to the UI, you can also enable the Top SQL feature by setting the TiDB system variable [`tidb_enable_top_sql`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_top_sql-new-in-v540):

```sql
SET GLOBAL tidb_enable_top_sql = 1;
```
## Use Top SQL

The following are the common steps to use Top SQL.

1. Visit the [Top SQL page](#access-the-page).

2. Select a particular TiDB or TiKV instance that you want to observe the load.

   ![Select Instance](/media/dashboard/top-sql-usage-select-instance.png)

   If you are unsure of which TiDB or TiKV instance to observe, you can select an arbitrary instance. Also, when the cluster CPU load is extremely unbalanced, you can first use Grafana charts to determine the specific instance you want to observe.

3. Observe the charts and tables presented by Top SQL.

   ![Chart and Table](/media/dashboard/top-sql-usage-chart.png)

   The size of the bars in the bar chart represents the size of CPU resources consumed by the SQL statement at that moment. Different colors distinguish different types of SQL statements. In most cases, you only need to focus on the SQL statements that have a higher CPU resource overhead in the corresponding time range in the chart.

4. Click a SQL statement in the table to show more information. You can see detailed execution metrics of different plans of that statement, such as Call/sec (average queries per second) and Scan Indexes/sec (average number of index rows scanned per second).

   ![Details](/media/dashboard/top-sql-details.png)

5. Based on these initial clues, you can further explore the [SQL Statement](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-statement-list) or [Slow Queries](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-slow-query) page to find the root cause of high CPU consumption or large data scans of the SQL statement.

Additionally, you can configure Top SQL as follows:

* You can adjust the time range in the time picker or select a time range in the chart to get a more precise and detailed look at the problem. A smaller time range can provide more detailed data, with precision of up to 1 second.

  ![Change time range](/media/dashboard/top-sql-usage-change-timerange.png)

* If the chart is out of date, you can click the **Refresh** button or select Auto Refresh options from the **Refresh** drop-down list.

  ![Refresh](/media/dashboard/top-sql-usage-refresh.png)
## Disable Top SQL

You can disable this feature by following these steps:

1. Visit [Top SQL page](#access-the-page).
2. Click the gear icon in the upper right corner to open the settings screen and switch off **Enable Feature**.
3. Click **Save**.
4. In the popped-up dialog box, click **Disable**.

In addition to the UI, you can also disable the Top SQL feature by setting the TiDB system variable [`tidb_enable_top_sql`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_top_sql-new-in-v540):

```sql
SET GLOBAL tidb_enable_top_sql = 0;
```
## Frequently asked questions

**1. Top SQL cannot be enabled and the UI displays "required component NgMonitoring is not started"**.

See [TiDB Dashboard FAQ](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-faq#a-required-component-ngmonitoring-is-not-started-error-is-shown).

**2. Will performance be affected after enabling Top SQL?**

This feature has a slight impact on cluster performance. According to our benchmark, the average performance impact is usually less than 3% when the feature is enabled.

**3. What is the status of this feature?**

It is now a generally available (GA) feature and can be used in production environments.

**4. What is the meaning of "Other Statements"?**

"Other Statement" counts the total CPU overhead of all non-Top 5 statements. With this information, you can learn the CPU overhead contributed by the Top 5 statements compared with the overall.

**5. What is the relationship between the CPU overhead displayed by Top SQL and the actual CPU usage of the process?**

Their correlation is strong but they are not exactly the same thing. For example, the cost of writing multiple replicas is not counted in the TiKV CPU overhead displayed by Top SQL. In general, SQL statements with higher CPU usage result in higher CPU overhead displayed in Top SQL.

**6. What is the meaning of the Y-axis of the Top SQL chart?**

It represents the size of CPU resources consumed. The more resources consumed by a SQL statement, the higher the value is. In most cases, you do not need to care about the meaning or unit of the specific value.

**7. Does Top SQL collect running (unfinished) SQL statements?**

Yes. The bars displayed in the Top SQL chart at each moment indicate the CPU overhead of all running SQL statements at that moment.
