# Add and manage the predefined system endpoint

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-manage-endpoint.md`
- Source Title: `Manage an Endpoint`
- Source Heading Path: `Manage an Endpoint > Create an endpoint > Add a predefined system endpoint`
- Source Line Ranges: `84-121`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `data-service`, `system-endpoint`, `endpoint-library`, `system-query`, `immediate-deployment`, `sql-execution`, `warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0311_6b85d789a4`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-manage-endpoint.md#add-a-predefined-system-endpoint`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `70c00e7f28a8fc4fb178fcdc531494a9dad9b9849a456e752f8820b902a8353e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#add-a-predefined-system-endpoint
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-manage-endpoint.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the predefined system endpoint library in Data Service, especially how to add or remove the `/system/query` endpoint and what behavior it has.
- Retrieval Keywords: Add a predefined system endpoint, endpoint library, Manage Endpoint Library, /system/query, Execute Query, sql parameter, POST /system/query, deployed to production immediately, same path and method already exists, timeout, max rows, system endpoint
- Follow-up Guidance: The chunk notes that `/system/query` is deployed immediately after saving, supports only customizable `timeout` and `max rows` properties, and has automatically configured parameters that cannot be modified.
- Classification Note: This is classified as an operation chunk because the content gives the procedure and constraints for adding or removing the predefined `/system/query` system endpoint.

## Official Source Content

### Add a predefined system endpoint

Data Service provides an endpoint library with predefined system endpoints that you can directly add to your Data App, reducing the effort in your endpoint development. Currently, the library only includes the `/system/query` endpoint, which enables you to execute any SQL statement by simply passing the statement in the predefined `sql` parameter.

To add a predefined system endpoint to your Data App, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.

2. In the left pane, locate your target Data App, click **+** to the right of the App name, and then click **Manage Endpoint Library**.

    A dialog for endpoint library management is displayed. Currently, only **Execute Query** (that is, the `/system/query` endpoint) is provided in the dialog.

3. To add the `/system/query` endpoint to your Data App, toggle the **Execute Query** switch to **Added**.

    > **Tip:**
    >
    > To remove an added predefined endpoint from your Data App, toggle the **Execute Query** switch to **Removed**.

4. Click **Save**.

    > **Note:**
    >
    > - After you click **Save**, the added or removed endpoint is deployed to production immediately, which makes the added endpoint accessible and the removed endpoint inaccessible immediately.
    > - If a non-predefined endpoint with the same path and method already exists in the current App, the creation of the system endpoint will fail.

    The added system-provided endpoint is displayed at the top of the endpoint list.

5. Check the endpoint name, SQL statements, properties, and parameters of the new endpoint.

    > **Note:**
    >
    > The `/system/query` endpoint is powerful and versatile but can be potentially destructive. Use it with discretion and ensure the queries are secure and well-considered to prevent unintended consequences.

    - Endpoint name: the endpoint name and path is `/system/query`, and the request method `POST`.
    - SQL statements: the `/system/query` endpoint does not come with any SQL statement. You can find the SQL editor in the middle section of the page and write your desired SQL statements in the SQL editor. Note that the SQL statements written in the SQL editor for the `/system/query` endpoint will be saved in the SQL editor so you can further develop and test them next time but they will not be saved in the endpoint configuration.
    - Endpoint properties: in the right pane of the page, you can find the endpoint properties on the **Properties** tab. Unlike other custom endpoints, only the `timeout` and `max rows` properties can be customized for system endpoints.
    - Endpoint parameters: in the right pane of the page, you can find the endpoint parameters on the **Params** tab. The parameters of the `/system/query` endpoint are configured automatically and cannot be modified.
