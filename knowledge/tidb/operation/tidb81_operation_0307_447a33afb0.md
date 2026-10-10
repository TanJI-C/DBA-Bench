# Call a Data Service endpoint with API keys and code examples

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-get-started.md`
- Source Title: `Get Started with Data Service`
- Source Heading Path: `Get Started with Data Service > Get started with your own Data App > Step 5. Call the endpoint | Get Started with Data Service > Get started with your own Data App > Step 5. Call the endpoint > 1. Create an API key | Get Started with Data Service > Get started with your own Data App > Step 5. Call the endpoint > 2. Get the code example | Get Started with Data Service > Get started with your own Data App > Step 5. Call the endpoint > 3. Use the code example | Get Started with Data Service > Learn more`
- Source Line Ranges: `182-304`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `data service`, `endpoint invocation`, `https request`, `api key`, `authentication`, `curl`, `json response`, `draft endpoint`, `online endpoint`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0307_447a33afb0`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-get-started.md#step-5-call-the-endpoint`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `97cdc170b990bc724a14251c8b6914b662d1807470fc94a775f89ab4ed35b6d3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-get-started#step-5-call-the-endpoint
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-get-started.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented steps and generated code example for calling a TiDB Cloud Data Service endpoint with an API key over HTTPS.
- Retrieval Keywords: Call the endpoint, HTTPS request, Create API Key, Authentication, ReadOnly, ReadAndWrite, SELECT, SHOW, USE, DESC, EXPLAIN, DML, DDL, rate limit, public key, private key, Code Example, curl --digest, --user '<Public Key>:<Private Key>', endpoint-type: draft, https://<region>.data.tidbcloud.com/api/v1beta/app/<App ID>/endpoint/<Endpoint Path>, data.tidbcloud.com, --location-trusted, JSON format, type sql_endpoint, Query OK!, row_count, row_affect
- Follow-up Guidance: The source also links to API Keys in Data Service, Response of an endpoint, Data Service Overview, Get Started with Chat2Query API, Manage a Data App, and Manage an Endpoint.
- Classification Note: This is classified as an operation chunk because it provides the procedure to create an API key, obtain a code example, and invoke a Data Service endpoint with the documented request format and response example.

## Official Source Content

### Step 5. Call the endpoint

You can call the endpoint by sending an HTTPS request. Before calling an endpoint, you need to first obtain an API key for the Data App.
#### 1. Create an API key

1. In the left pane of the [**Data Service**](https://tidbcloud.com/project/data-service) page, click the name of your Data App to view its details.
2. In the **Authentication** area, click **Create API Key**.
3. In the **Create API Key** dialog box, do the following:

    1. (Optional) Enter a description for your API key.
    2. Select a role for your API key.

        The role is used to control whether the API key can read or write data to the clusters linked to the Data App. You can select the `ReadOnly` or `ReadAndWrite` role:

        - `ReadOnly`: only allows the API key to read data, such as `SELECT`, `SHOW`, `USE`, `DESC`, and `EXPLAIN` statements.
        - `ReadAndWrite`: allows the API key to read and write data. You can use this API key to execute all SQL statements, such as DML and DDL statements.

    3. (Optional) Set a desired rate limit for your API key.

4. Click **Next**. The public key and private key are displayed.

    Make sure that you have copied and saved the private key in a secure location. After leaving this page, you will not be able to get the full private key again.

5. Click **Done**.

For more information about API keys, see [API Keys in Data Service](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-api-key).
#### 2. Get the code example

TiDB Cloud generates code examples to help you call an endpoint. To get the code example, perform the following steps:

1. In the left pane of the [**Data Service**](https://tidbcloud.com/project/data-service) page, click the name of your endpoint, and then click **...** > **Code Example** in the upper-right corner. The **Code Example** dialog box is displayed.

2. In the dialog box, select the cluster and database that you want to use to call the endpoint, and then copy the code example.

    An example of the curl code example is as follows:

    <div label="Test Environment">

    To call a draft version of the endpoint, you need to add the `endpoint-type: draft` header:

    ```bash
    curl --digest --user '<Public Key>:<Private Key>' \
      --request GET 'https://<region>.data.tidbcloud.com/api/v1beta/app/<App ID>/endpoint/<Endpoint Path>' \
      --header 'endpoint-type: draft'
    ```

    </div>

    <div label="Online Environment">

    You must deploy your endpoint first before checking the code example in the online environment.

    To call the current online version of the endpoint, use the following command:

    ```bash
    curl --digest --user '<Public Key>:<Private Key>' \
      --request GET 'https://<region>.data.tidbcloud.com/api/v1beta/app/<App ID>/endpoint/<Endpoint Path>'
    ```

    </div>

    > **Note:**
    >
    > - By requesting the regional domain `<region>.data.tidbcloud.com`, you can directly access the endpoint in the region where the TiDB cluster is located.
    > - Alternatively, you can also request the global domain `data.tidbcloud.com` without specifying a region. In this way, TiDB Cloud will internally redirect the request to the target region, but this might result in additional latency. If you choose this way, make sure to add the `--location-trusted` option to your curl command when calling an endpoint.
#### 3. Use the code example

Paste the code example in your application and run it. Then, you can get the response of the endpoint.

- You need to replace the `<Public Key>` and `<Private Key>` placeholders with your API key.
- If the endpoint contains parameters, specify the parameter values when calling the endpoint.

After calling an endpoint, you can see the response in JSON format. The following is an example:

```json
{
  "type": "sql_endpoint",
  "data": {
    "columns": [
      {
        "col": "id",
        "data_type": "BIGINT",
        "nullable": false
      },
      {
        "col": "type",
        "data_type": "VARCHAR",
        "nullable": false
      }
    ],
    "rows": [
      {
        "id": "20008295419",
        "type": "CreateEvent"
      }
    ],
    "result": {
      "code": 200,
      "message": "Query OK!",
      "start_ms": 1678965476709,
      "end_ms": 1678965476839,
      "latency": "130ms",
      "row_count": 1,
      "row_affect": 0,
      "limit": 50
    }
  }
}
```

For more information about the response, see [Response of an endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#response).
## Learn more

- [Data Service Overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-overview)
- [Get Started with Chat2Query API](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api)
- [Manage a Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app)
- [Manage an Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint)
