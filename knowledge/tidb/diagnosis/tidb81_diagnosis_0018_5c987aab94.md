# Inspect slow query execution details and plans

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-slow-query.md`
- Source Title: `Slow Queries Page of TiDB Dashboard`
- Source Heading Path: `Slow Queries Page of TiDB Dashboard > View execution details | Slow Queries Page of TiDB Dashboard > View execution details > SQL | Slow Queries Page of TiDB Dashboard > View execution details > Execution plans | Slow Queries Page of TiDB Dashboard > View execution details > Execution plans > Execution plan in table format | Slow Queries Page of TiDB Dashboard > View execution details > Execution plans > Execution plan in graph format | Slow Queries Page of TiDB Dashboard > View execution details > SQL execution details | Slow Queries Page of TiDB Dashboard > View execution details > SQL execution details > Basic tab | Slow Queries Page of TiDB Dashboard > View execution details > SQL execution details > Time tab | Slow Queries Page of TiDB Dashboard > View execution details > SQL execution details > Coprocessor tab | Slow Queries Page of TiDB Dashboard > View execution details > SQL execution details > Transaction tab`
- Source Line Ranges: `50-134`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `tikv`, `tiflash`, `shared`
- Topic Tags: `slow-queries`, `execution-details`, `sql-text`, `execution-plans`, `table-plan`, `graph-plan`, `operator-metrics`, `timing`, `coprocessor`, `transactions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0018_5c987aab94`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-slow-query.md#view-execution-details`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8afb2f963576a88d4eefae6632bcb9dbe9c671d2eb4f8efe51342898fce9f4d1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-slow-query#view-execution-details
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-slow-query.md

## Retrieval Guidance

- Use When: Use this when you need TiDB Dashboard details for a selected slow query, including SQL text, execution plans in table, text, or graph format, and the Basic, Time, Coprocessor, and Transaction tabs.
- Retrieval Keywords: View execution details, Query column, tidb_stmt_summary_max_sql_length, Expand, Copy, execution plan in table format, execution plan in text format, execution plan in graph format, column picker, download as a text file, operator metrics, TiDB yellow TiKV blue TiFlash pink, right sidebar, Basic tab, Time tab, Coprocessor tab, Transaction tab, execution count, total latency, average number of written keys, maximum number of written keys
- Follow-up Guidance: The Time tab notes that parallel operations in a single SQL statement can make the cumulative duration of stages exceed the actual execution time.
- Classification Note: This is classified as diagnosis because the content focuses on inspecting slow query execution details and plans to understand operators, timing, coprocessor reads, and transaction-related information.

## Official Source Content

## View execution details

Click any item in the list to display detailed execution information of the slow query, including:

- Query: The text of the SQL statement (area 1 in the following figure)
- Plan: The execution plan of the slow query (area 2 in the following figure)
- Other sorted SQL execution information (area 3 in the following figure)

![View execution details](/media/dashboard/dashboard-slow-queries-detail1-v620.png)
### SQL

> **Note:**
>
> The maximum length of the query recorded in the `Query` column is limited by the [`tidb_stmt_summary_max_sql_length`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_stmt_summary_max_sql_length-new-in-v40) system variable.

Click the **Expand** button to view the detailed information of an item. Click the **Copy** button to copy the detailed information to the clipboard.
### Execution plans

On TiDB Dashboard, you can view execution plans in three ways: table, text, and graph. To learn how to read an execution plan, see [Understand the query execution plan](https://docs.pingcap.com/tidb/stable/explain-overview).
#### Execution plan in table format

The table format provides detailed information about the execution plan, which helps you quickly identify abnormal operator metrics and compare the status of different operators. The following figure shows an execution plan in table format:

![Execution plan in table format](/media/dashboard/dashboard-table-plan.png)

The table format displays similar information to the text format but provides more user-friendly interactions:

- You can adjust the column width freely.
- When content exceeds the column width, it is automatically truncated and a tooltip is shown for the full information.
- If the execution plan is large, you can download it as a text file for local analysis.
- You can hide and manage columns using the column picker.

![Execution plan in table format - column picker](/media/dashboard/dashboard-table-plan-columnpicker.png)
#### Execution plan in graph format

The graph format is more suitable for viewing the execution plan tree of a complex SQL statement and understanding each operator and its corresponding content in detail. The following figure shows an execution plan in graph format:

![Execution plan in graph format](/media/dashboard/dashboard-visual-plan-2.png)

- The graph shows the execution from left to right, and from top to bottom.
- Upper nodes are parent operators and lower nodes are child operators.
- The color of the title bar indicates the component where the operator is executed: yellow stands for TiDB, blue stands for TiKV, and pink stands for TiFlash.
- The title bar shows the operator name and the text shown below is the basic information of the operator.

Click the node area, and the detailed operator information is displayed on the right sidebar.

![Execution plan in graph format - sidebar](/media/dashboard/dashboard-visual-plan-popup.png)
### SQL execution details

For basic information, execution time, Coprocessor read, transaction, and slow query of the SQL statement, you can click the corresponding tab titles to switch among different information.

![Show different execution information](/media/dashboard/dashboard-slow-queries-detail2-v620.png)
#### Basic tab

The basic information of a SQL execution includes the table names, index name, execution count, and total latency. The **Description** column provides detailed description of each field.

![Basic information](/media/dashboard/dashboard-slow-queries-detail-plans-basic.png)
#### Time tab

Click the **Time** tab, and you can see how long each stage of the execution plan lasts.

> **Note:**
>
> Because some operations might be performed in parallel within a single SQL statement, the cumulative duration of each stage might exceed the actual execution time of the SQL statement.

![Execution time](/media/dashboard/dashboard-slow-queries-detail-plans-time.png)
#### Coprocessor tab

Click the **Coprocessor** tab, and you can see information related to Coprocessor read.

![Coprocessor read](/media/dashboard/dashboard-slow-queries-detail-plans-cop-read.png)
#### Transaction tab

Click the **Transaction** tab, and you can see information related to execution plans and transactions, such as the average number of written keys or the maximum number of written keys.

![Transaction](/media/dashboard/dashboard-slow-queries-detail-plans-transaction.png)
