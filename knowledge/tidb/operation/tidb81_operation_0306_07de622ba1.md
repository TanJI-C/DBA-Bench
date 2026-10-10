# Develop, test, and deploy a Data Service endpoint

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-get-started.md`
- Source Title: `Get Started with Data Service`
- Source Heading Path: `Get Started with Data Service > Get started with your own Data App > Step 2. Develop an endpoint > Write SQL statements | Get Started with Data Service > Get started with your own Data App > Step 3. Test the endpoint (optional) | Get Started with Data Service > Get started with your own Data App > Step 4. Deploy the endpoint`
- Source Line Ranges: `99-181`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `data service`, `endpoint development`, `sql editor`, `parameters`, `query execution`, `endpoint testing`, `deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0306_07de622ba1`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-get-started.md#write-sql-statements`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `49fe239bbee411faa84a248aebc14c889f601fb4749eb32fe39964f65368588f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-get-started#write-sql-statements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-get-started.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented workflow for developing a Data Service endpoint in the SQL editor, defining `${ID}` style parameters, running SQL, testing the endpoint, and deploying it.
- Retrieval Keywords: Data Service page, SQL editor, select a cluster, Schema tab, USE database_name;, -- followed by your instructions, Params tab, parameter name is case-sensitive, parameter cannot be used as a table name or column name, Definition section, Test Values section, Run, ⌘ + Enter, Ctrl + Enter, ⇧ + ⌘ + Enter, Shift + Ctrl + Enter, Result tab, Test, F5, HTTP Response tab, Deploy, Endpoint has been deployed, Deployments tab
- Follow-up Guidance: The source also points to Manage linked clusters, Configure parameters, and Response of an endpoint for related details.
- Classification Note: This is classified as an operation chunk because it describes procedural steps on TiDB Cloud Data Service to write SQL statements, run them, test an endpoint, and deploy it.

## Official Source Content

#### Write SQL statements

You can customize SQL statements for the endpoint in the SQL editor, which is the middle pane on the **Data Service** page.

1. Select a cluster.

    > **Note:**
    >
    > Only clusters that are linked to the Data App are displayed in the drop-down list. To manage the linked clusters, see [Manage linked clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app#manage-linked-data-sources).

    On the upper part of the SQL editor, select a cluster on which you want to execute SQL statements from the drop-down list. Then, you can view all databases of this cluster in the **Schema** tab on the right pane.

2. Write SQL statements.

    Before querying or modifying data, you need to first specify the database in the SQL statements. For example, `USE database_name;`.

    In the SQL editor, you can write statements such as table join queries, complex queries, and aggregate functions. You can also simply type `--` followed by your instructions to let AI generate SQL statements automatically.

    > **Note:**
    >
    > To try the AI capacity of TiDB Cloud, you need to allow PingCAP and Amazon Bedrock to use your code snippets for research and service improvement. For more information, see [Enable or disable AI to generate SQL queries](https://docs.pingcap.com/tidb/stable/tidb-cloud/explore-data-with-chat2query#enable-or-disable-ai-to-generate-sql-queries).

    To define a parameter, you can insert it as a variable placeholder like `${ID}` in the SQL statement. For example, `SELECT * FROM table_name WHERE id = ${ID}`. Then, you can click the **Params** tab on the right pane to change the parameter definition and test values.

    > **Note:**
    >
    > - The parameter name is case-sensitive.
    > - The parameter cannot be used as a table name or column name.

    - In the **Definition** section, you can specify whether the parameter is required when a client calls the endpoint, the data type, and the default value of the parameter.
    - In the **Test Values** section, you can set the test value for a parameter. The test values are used when you run the SQL statements or test the endpoint. If you do not set the test values, the default values are used.
    - For more information, see [Configure parameters](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#configure-parameters).

3. Run SQL statements.

    If you have inserted parameters in the SQL statements, make sure that you have set test values or default values for the parameters in the **Params** tab on the right pane. Otherwise, an error is returned.

    <div label="macOS">

    For macOS:

    - If you have only one statement in the editor, to run it, press **⌘ + Enter** or click <svg width="1rem" height="1rem" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6.70001 20.7756C6.01949 20.3926 6.00029 19.5259 6.00034 19.0422L6.00034 12.1205L6 5.33028C6 4.75247 6.00052 3.92317 6.38613 3.44138C6.83044 2.88625 7.62614 2.98501 7.95335 3.05489C8.05144 3.07584 8.14194 3.12086 8.22438 3.17798L19.2865 10.8426C19.2955 10.8489 19.304 10.8549 19.3126 10.8617C19.4069 10.9362 20 11.4314 20 12.1205C20 12.7913 19.438 13.2784 19.3212 13.3725C19.307 13.3839 19.2983 13.3902 19.2831 13.4002C18.8096 13.7133 8.57995 20.4771 8.10002 20.7756C7.60871 21.0812 7.22013 21.0683 6.70001 20.7756Z" fill="currentColor"></path></svg>**Run**.

    - If you have multiple statements in the editor, to run one or several of them sequentially, place your cursor on your target statement or select the lines of the target statements with your cursor, and then press **⌘ + Enter** or click **Run**.

    - To run all statements in the editor sequentially, press **⇧ + ⌘ + Enter**, or select the lines of all statements with your cursor and click **Run**.

    </div>

    <div label="Windows/Linux">

    For Windows or Linux:

    - If you have only one statement in the editor, to run it, press **Ctrl + Enter** or click <svg width="1rem" height="1rem" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6.70001 20.7756C6.01949 20.3926 6.00029 19.5259 6.00034 19.0422L6.00034 12.1205L6 5.33028C6 4.75247 6.00052 3.92317 6.38613 3.44138C6.83044 2.88625 7.62614 2.98501 7.95335 3.05489C8.05144 3.07584 8.14194 3.12086 8.22438 3.17798L19.2865 10.8426C19.2955 10.8489 19.304 10.8549 19.3126 10.8617C19.4069 10.9362 20 11.4314 20 12.1205C20 12.7913 19.438 13.2784 19.3212 13.3725C19.307 13.3839 19.2983 13.3902 19.2831 13.4002C18.8096 13.7133 8.57995 20.4771 8.10002 20.7756C7.60871 21.0812 7.22013 21.0683 6.70001 20.7756Z" fill="currentColor"></path></svg>**Run**.

    - If you have multiple statements in the editor, to run one or several of them sequentially, place your cursor on your target statement or select the lines of the target statements with your cursor, and then press **Ctrl + Enter** or click **Run**.

    - To run all statements in the editor sequentially, press **Shift + Ctrl + Enter**, or select the lines of all statements with your cursor and click **Run**.

    </div>

    After running the statements, you can see the query results immediately in the **Result** tab at the bottom of the page.
### Step 3. Test the endpoint (optional)

After configuring an endpoint, you can test the endpoint to verify whether it works as expected before deploying.

To test the endpoint, click **Test** in the upper-right corner or press **F5**.

Then, you can see the response in the **HTTP Response** tab at the bottom of the page. For more information about the response, see [Response of an endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#response).
### Step 4. Deploy the endpoint

To deploy the endpoint, perform the following steps:

1. On the endpoint details page, click **Deploy** in the upper-right corner.

2. Click **Deploy** to confirm the deployment. You will get the **Endpoint has been deployed** prompt if the endpoint is successfully deployed.

    To view the deployment history, you can click the name of your Data App in the left pane, and then click the **Deployments** tab in the right pane.
