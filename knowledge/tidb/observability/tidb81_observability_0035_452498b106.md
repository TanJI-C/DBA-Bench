# Execution plan and SQL execution detail views

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-statement-details.md`
- Source Title: `Statement Execution Details of TiDB Dashboard`
- Source Heading Path: `Statement Execution Details of TiDB Dashboard > Execution details of plans | Statement Execution Details of TiDB Dashboard > Execution details of plans > SQL sample | Statement Execution Details of TiDB Dashboard > Execution details of plans > Execution plans | Statement Execution Details of TiDB Dashboard > Execution details of plans > Execution plans > Execution plan in table format | Statement Execution Details of TiDB Dashboard > Execution details of plans > Execution plans > Execution plan in graph format | Statement Execution Details of TiDB Dashboard > Execution details of plans > SQL execution details | Statement Execution Details of TiDB Dashboard > Execution details of plans > SQL execution details > Basic tab | Statement Execution Details of TiDB Dashboard > Execution details of plans > SQL execution details > Time tab | Statement Execution Details of TiDB Dashboard > Execution details of plans > SQL execution details > Coprocessor Read tab | Statement Execution Details of TiDB Dashboard > Execution details of plans > SQL execution details > Transaction tab | Statement Execution Details of TiDB Dashboard > Execution details of plans > SQL execution details > Slow Query tab`
- Source Line Ranges: `61-149`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `tikv`, `tiflash`, `sql`
- Topic Tags: `sql-sample`, `execution-plans`, `table-format`, `text-format`, `graph-format`, `operators`, `execution-time`, `coprocessor-read`, `transaction`, `slow-query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0035_452498b106`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-statement-details.md#execution-details-of-plans`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `42387575a55e785be739e8726ff76d71e540f846896f105afcf98e32d73e3cef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-statement-details#execution-details-of-plans
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-statement-details.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants to inspect execution details of a SQL statement plan in TiDB Dashboard, including SQL sample, execution plan formats, operator details, and the Basic, Time, Coprocessor Read, Transaction, or Slow Query tabs.
- Retrieval Keywords: Execution details of plans, SQL sample, Execution plan, execution plan in table format, execution plan in text format, execution plan in graph format, Expand, Copy, column picker, download it as a text file, operator metrics, upper nodes are parent operators, lower nodes are child operators, yellow stands for TiDB, blue stands for TiKV, pink stands for TiFlash, Basic tab, Time tab, Coprocessor Read tab, Transaction tab, Slow Query tab, execution count, total latency, average number of written keys, maximum number of written keys, slow query records
- Follow-up Guidance: The source notes that because some operations might be performed in parallel within a single SQL statement, the cumulative duration of each stage might exceed the actual execution time of the SQL statement.
- Classification Note: This is classified as an observability chunk because the official content focuses on viewing and interpreting SQL execution details, plans, operator information, timing, coprocessor read, transaction metrics, and slow query records in TiDB Dashboard.

## Official Source Content

## Execution details of plans

The execution detail of plans includes the following information:

- SQL sample: The text of a certain SQL statement that is actually executed corresponding to the plan. Any SQL statement that has been executed within the time range might be used as a SQL sample.
- Execution plan: Complete information about execution plans, displayed in table, graph, and text. For details of the execution plan, see [Understand the Query Execution Plan](https://docs.pingcap.com/tidb/stable/explain-overview). If multiple execution plans are selected, only (any) one of them is displayed.
- For basic information, execution time, Coprocessor read, transaction, and slow query of the SQL statement, you can click the corresponding tab titles to switch among different information.

![Execution details of plans](/media/dashboard/dashboard-statement-plans-detail.png)
### SQL sample

To view the detailed information of an item, you can click **Expand**. To copy the detailed information to the clipboard, click **Copy**.
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

![Basic information](/media/dashboard/dashboard-statement-plans-basic.png)
#### Time tab

Click the **Time** tab, and you can see how long each stage of the execution plan lasts.

> **Note:**
>
> Because some operations might be performed in parallel within a single SQL statement, the cumulative duration of each stage might exceed the actual execution time of the SQL statement.

![Execution time](/media/dashboard/dashboard-statement-plans-time.png)
#### Coprocessor Read tab

Click the **Coprocessor Read** tab, and you can see information related to Coprocessor read.

![Coprocessor read](/media/dashboard/dashboard-statement-plans-cop-read.png)
#### Transaction tab

Click the **Transaction** tab, and you can see information related to execution plans and transactions, such as the average number of written keys or the maximum number of written keys.

![Transaction](/media/dashboard/dashboard-statement-plans-transaction.png)
#### Slow Query tab

If an execution plan is executed too slowly, you can see its associated slow query records under the **Slow Query** tab.

![Slow Query](/media/dashboard/dashboard-statement-plans-slow-queries.png)

The information displayed in this area has the same structure with the slow query page. See [TiDB Dashboard Slow Query Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-slow-query) for details.
