# Endpoint properties configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-manage-endpoint.md`
- Source Title: `Manage an Endpoint`
- Source Heading Path: `Manage an Endpoint > Develop an endpoint > Configure properties > Basic properties | Manage an Endpoint > Develop an endpoint > Configure properties > Advanced properties`
- Source Line Ranges: `134-199`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `endpoint`, `path`, `request method`, `timeout`, `pagination`, `cache`, `batch operation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0227_ab0542724f`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-manage-endpoint.md#basic-properties`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `758e726e08283f71c2f0d99f35a9e389cf91671dd4ef56cb7a5fe4f662e00478`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#basic-properties
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-manage-endpoint.md

## Retrieval Guidance

- Use When: Use this chunk when configuring a TiDB Cloud Data Service endpoint path, request method, endpoint URL behavior, timeout, max rows, pagination, cache response TTL, or batch operation rules.
- Retrieval Keywords: Path, Endpoint URL, Request Method, GET, POST, PUT, DELETE, Timeout(ms), Max Rows, Tag, Pagination, page, page_size, Cache Response, Time-to-live(s), TTL, Batch Operation, Data App, https://<region>.data.tidbcloud.com/api/v1beta/app/<App ID>/endpoint/, GET /var/{var1}, GET /var/123, {items: [{dataObject1}, {dataObject2}]}
- Follow-up Guidance: The content also points to Configure parameters for using path parameters directly in SQL and to Call an endpoint for pagination and batch request examples.
- Classification Note: This is classified as configuration because the content defines endpoint property settings, validation rules, availability conditions, and generated URL structure in TiDB Cloud Data Service.

## Official Source Content

#### Basic properties

- **Path**: the path that users use to access the endpoint.

    - The length of the path must be less than 64 characters.
    - The combination of the request method and the path must be unique within a Data App.
    - Only letters, numbers, underscores (`_`), slashes (`/`), and parameters enclosed in curly braces (such as `{var}`) are allowed in a path. Each path must start with a slash (`/`) and end with a letter, number, or underscore (`_`). For example, `/my_endpoint/get_id`.
    - For parameters enclosed in `{ }`, only letters, numbers, and underscores (`_`) are allowed. Each parameter enclosed in `{ }` must start with a letter or underscore (`_`).

    > **Note:**
    >
    > - In a path, each parameter must be at a separate level and does not support prefixes or suffixes.
    >
    >    Valid path: ```/var/{var}``` and  ```/{var}```
    >
    >    Invalid path: ```/var{var}``` and ```/{var}var```
    >
    > - Paths with the same method and prefix might conflict, as in the following example:
    >
    >    ```GET /var/{var1}```
    >
    >    ```GET /var/{var2}```
    >
    >   These two paths will conflict with each other because `GET /var/123` matches both.
    >
    > - Paths with parameters have lower priority than paths without parameters. For example:
    >
    >    ```GET /var/{var1}```
    >
    >    ```GET /var/123```
    >
    >   These two paths will not conflict because `GET /var/123` takes precedence.
    >
    > - Path parameters can be used directly in SQL. For more information, see [Configure parameters](#configure-parameters).

- **Endpoint URL**: (read-only) the default URL is automatically generated based on the region where the corresponding cluster is located, the service URL of the Data App, and the path of the endpoint. For example, if the path of the endpoint is `/my_endpoint/get_id`, the endpoint URL is `https://<region>.data.tidbcloud.com/api/v1beta/app/<App ID>/endpoint/my_endpoint/get_id`. To configure a custom domain for the Data App, see [Custom Domain in Data Service](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-custom-domain).

- **Request Method**: the HTTP method of the endpoint. The following methods are supported:

    - `GET`: use this method to query or retrieve data, such as a `SELECT` statement.
    - `POST`: use this method to insert or create data, such as an `INSERT` statement.
    - `PUT`: use this method to update or modify data, such as an `UPDATE` statement.
    - `DELETE`: use this method to delete data, such as a `DELETE` statement.

- **Description** (Optional): the description of the endpoint.
#### Advanced properties

- **Timeout(ms)**: the timeout for the endpoint, in milliseconds.
- **Max Rows**: the maximum number of rows that the endpoint can operate or return.
- **Tag**: the tag used for identifying a group of endpoints.
- **Pagination**: this property is available only when the request method is `GET` and the last SQL statement of the endpoint is a `SELECT` operation. When **Pagination** is enabled, you can paginate the results by specifying `page` and `page_size` as query parameters when calling the endpoint, such as `https://<region>.data.tidbcloud.com/api/v1beta/app/<App ID>/endpoint/my_endpoint/get_id?page=<Page Number>&page_size=<Page Size>`. For more information, see [Call an endpoint](#call-an-endpoint).

    > **Note:**
    >
    > - If you do not include the `page` and `page_size` parameters in the request, the default behavior is to return the maximum number of rows specified in the **Max Rows** property on a single page.
    > - The `page_size` must be less than or equal to the **Max Rows** property. Otherwise, an error is returned.

- **Cache Response**: this property is available only when the request method is `GET`. When **Cache Response** is enabled, TiDB Cloud Data Service can cache the response returned by your `GET` requests within a specified time-to-live (TTL) period.
- **Time-to-live(s)**: this property is available only when **Cache Response** is enabled. You can use it to specify the time-to-live (TTL) period in seconds for cached response. During the TTL period, if you make the same `GET` requests again, Data Service returns the cached response directly instead of fetching data from the target database again, which improves your query performance.
- **Batch Operation**: this property is visible only when the request method is `POST` or `PUT`. When **Batch Operation** is enabled, you can operate on multiple rows in a single request. For example, you can insert multiple rows of data in a single `POST` request by putting an array of data objects to the `items` field of an object in the `--data-raw` option of your curl command when [calling the endpoint](#call-an-endpoint).

    > **Note:**
    >
    > The endpoint with **Batch Operation** enabled supports both array and object formats for the request body: `[{dataObject1}, {dataObject2}]` and `{items: [{dataObject1}, {dataObject2}]}`. For better compatibility with other systems, it is recommended that you use the object format `{items: [{dataObject1}, {dataObject2}]}`.
