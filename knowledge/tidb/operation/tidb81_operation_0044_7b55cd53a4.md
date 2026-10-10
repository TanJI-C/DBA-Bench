# Statement details overview and fast plan binding

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-statement-details.md`
- Source Title: `Statement Execution Details of TiDB Dashboard`
- Source Heading Path: `Statement Execution Details of TiDB Dashboard | Statement Execution Details of TiDB Dashboard > Fast plan binding | Statement Execution Details of TiDB Dashboard > Fast plan binding > Usage | Statement Execution Details of TiDB Dashboard > Fast plan binding > Usage > Bind an execution plan | Statement Execution Details of TiDB Dashboard > Fast plan binding > Usage > Drop an existing binding | Statement Execution Details of TiDB Dashboard > Fast plan binding > Limitation`
- Source Line Ranges: `5-60`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `tiflash`
- Topic Tags: `statement-details`, `sql-statements`, `execution-plans`, `plan-binding`, `bind-plan`, `drop-binding`, `privileges`, `limitations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0044_7b55cd53a4`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-statement-details.md#statement-execution-details-of-tidb-dashboard`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fa54f982ae14fc147e5bf0af8550cf4da7028292df74d8071209b8fd7b2a3a6a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-statement-details#statement-execution-details-of-tidb-dashboard
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-statement-details.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants to view SQL statement details in TiDB Dashboard or use fast plan binding to bind or drop a statement execution plan and needs the stated limitations or privilege requirement.
- Retrieval Keywords: Statement Execution Details of TiDB Dashboard, Fast plan binding, Plan Binding, Bind, Drop, Bound, Not bound, SQL template, SQL template ID, execution plan list, visual execution plans, Bind an execution plan, Drop an existing binding, SUPER privilege, statements that are not SELECT DELETE UPDATE INSERT or REPLACE, queries with subqueries, queries that access TiFlash, queries that join three or more tables
- Follow-up Guidance: If the user encounters permission issues while using fast plan binding, the source says to refer to TiDB Dashboard User Management to add the necessary privileges.
- Classification Note: This is classified as an operation chunk because the official content describes dashboard interactions for opening statement details and performing fast plan binding, including bind, drop, limitations, and required privilege.

## Official Source Content

# Statement Execution Details of TiDB Dashboard

Click any item in the list to enter the detail page of the SQL statement to view more detailed information. This information includes the following parts:

- The overview of SQL statements, which includes the SQL template, the SQL template ID, the current time range of displayed SQL executions, the number of execution plans, the database in which the SQL statement is executed, and the fast plan binding feature (area 1 in the following figure).
- The execution plan list: If a SQL statement has multiple execution plans, this list is displayed. Besides text information of execution plans, TiDB v6.2.0 introduces visual execution plans, through which you can learn each operator of a statement and detailed information more intuitively. You can select different execution plans, and the details of the selected plans are displayed below the list (area 2 in the following figure).
- Execution detail of plans, which displays the detailed information of the selected execution plans. See [Execution plan in details](#execution-details-of-plans) (area 3 in the following figure).

![Details](/media/dashboard/dashboard-statement-detail-v660.png)
## Fast plan binding

Starting from v6.6.0, TiDB introduces the fast plan binding feature. You can quickly bind a SQL statement to a specific execution plan in TiDB Dashboard.
### Usage
#### Bind an execution plan

1. Click **Plan Binding**. The **Plan Binding** dialog box is displayed.

    ![Fast plan binding - not bound - entry](/media/dashboard/dashboard-quick-binding-entry-notbound.png)

2. Select a plan that you want to bind and click **Bind**.

    ![Fast plan binding - popup](/media/dashboard/dashboard-quick-binding-popup-notbound.png)

3. After the binding is completed, you can see the **Bound** label.

    ![Fast plan binding - popup - binding completed](/media/dashboard/dashboard-quick-binding-popup-bound.png)
#### Drop an existing binding

1. On the page of a SQL statement that has an existing binding, click **Plan Binding**. The **Plan Binding** dialog box is displayed.

    ![Fast plan binding - bound - entry](/media/dashboard/dashboard-quick-binding-entry-bound.png)

2. Click **Drop**.

    ![Fast plan binding - popup - bound](/media/dashboard/dashboard-quick-binding-popup-bound.png)

3. After the binding is dropped, you can see the **Not bound** label.

    ![Fast plan binding - popup](/media/dashboard/dashboard-quick-binding-popup-notbound.png)
### Limitation

Currently, the fast plan binding feature does not support the following types of SQL statements:

- Statements that are not `SELECT`, `DELETE`, `UPDATE`, `INSERT`, or `REPLACE`
- Queries with subqueries
- Queries that access TiFlash
- Queries that join three or more tables

To use this feature, you must have the SUPER privilege. If you encounter permission issues while using it, refer to [TiDB Dashboard User Management](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-user) to add the necessary privileges.
