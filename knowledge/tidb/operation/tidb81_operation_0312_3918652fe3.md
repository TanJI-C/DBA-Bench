# Write and run endpoint SQL

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-manage-endpoint.md`
- Source Title: `Manage an Endpoint`
- Source Heading Path: `Manage an Endpoint > Develop an endpoint > Write SQL statements`
- Source Line Ranges: `200-265`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `cloud`
- Topic Tags: `sql editor`, `parameters`, `query execution`, `ai generation`, `result tab`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0312_3918652fe3`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-manage-endpoint.md#write-sql-statements`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f3edb66c5b1778b5d45ec43b0cf5c0c0af2fc35d31c697d6b2c01f8a95befae7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#write-sql-statements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-manage-endpoint.md

## Retrieval Guidance

- Use When: Use this chunk when writing or running SQL statements for a Data Service endpoint, selecting a linked cluster, specifying a database, defining parameters, or using keyboard shortcuts in the SQL editor.
- Retrieval Keywords: Write SQL statements, SQL editor, linked clusters, Schema tab, USE database_name;, Params tab, Result tab, -- followed by your instructions, AI generate SQL statements, ${ID}, SELECT * FROM table_name WHERE id = ${ID}, array parameter, SELECT * FROM table_name WHERE id IN (${ID}), parameter name is case-sensitive, parameter cannot be used as a table name or column name, ⌘ + Enter, Ctrl + Enter, Shift + Ctrl + Enter, 8 MiB
- Follow-up Guidance: If parameters are inserted in SQL statements, the source says to set test values or default values in the Params tab, otherwise an error is returned.
- Classification Note: This is classified as operation because the content describes how to execute endpoint SQL in the editor, including cluster and database selection, parameter handling, and statement execution behavior.

## Official Source Content

### Write SQL statements

On the SQL editor of the endpoint details page, you can write and run the SQL statements for an endpoint. You can also simply type `--` followed by your instructions to let AI generate SQL statements automatically.

1. Select a cluster.

    > **Note:**
    >
    > Only clusters that are linked to the Data App are displayed in the drop-down list. To manage the linked clusters, see [Manage linked clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app#manage-linked-data-sources).

    On the upper part of the SQL editor, select a cluster on which you want to execute SQL statements from the drop-down list. Then, you can view all databases of this cluster in the **Schema** tab on the right pane.

2. Depending on your endpoint type, do one of the following to select a database:

    - Predefined system endpoints: on the upper part of the SQL editor, select the target database from the drop-down list.
    - Other endpoints: write a SQL statement to specify the target database in the SQL editor. For example, `USE database_name;`.

3. Write SQL statements.

    In the SQL editor, you can write statements such as table join queries, complex queries, and aggregate functions. You can also simply type `--` followed by your instructions to let AI generate SQL statements automatically.

    To define a parameter, you can insert it as a variable placeholder like `${ID}` in the SQL statement. For example, `SELECT * FROM table_name WHERE id = ${ID}`. Then, you can click the **Params** tab on the right pane to change the parameter definition and test values. For more information, see [Parameters](#configure-parameters).

    When defining an array parameter, the parameter is automatically converted to multiple comma-separated values in the SQL statement. To make sure that the SQL statement is valid, you need to add parentheses (`()`) around the parameter in some SQL statements (such as `IN`). For example, if you define an array parameter `ID` with test value `1,2,3`, use `SELECT * FROM table_name WHERE id IN (${ID})` to query the data.

    > **Note:**
    >
    > - The parameter name is case-sensitive.
    > - The parameter cannot be used as a table name or column name.

4. Run SQL statements.

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

    > **Note:**
    >
    > The returned result has a size limit of 8 MiB.
