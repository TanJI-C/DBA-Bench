# Call a Data Service endpoint with API key authentication

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-manage-endpoint.md`
- Source Title: `Manage an Endpoint`
- Source Heading Path: `Manage an Endpoint > Call an endpoint | Manage an Endpoint > Call an endpoint > Prerequisites | Manage an Endpoint > Call an endpoint > Request | Manage an Endpoint > Call an endpoint > Response`
- Source Line Ranges: `349-453`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `api-key`, `https-request`, `code-example`, `curl`, `basic-authentication`, `digest-authentication`, `draft-endpoint`, `online-endpoint`, `regional-domain`, `global-domain`, `pagination`, `batch-operation`, `json-response`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0314_f2d9fe113d`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-manage-endpoint.md#call-an-endpoint`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9e326e1ca967811019eed89300f9a74e29f0130524dedb7632d4f809e9e04ad7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#call-an-endpoint
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-manage-endpoint.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the official way to call a TiDB Cloud Data Service endpoint with an API key, choose test or online environment, or understand the generated curl example and request format.
- Retrieval Keywords: Call an endpoint, API key, Create an API key, Code Example, curl code example, Test Environment, Online Environment, Basic Authentication, Digest Authentication, --digest, endpoint-type: draft, HTTPS request, regional domain <region>.data.tidbcloud.com, global domain data.tidbcloud.com, --location-trusted, <Public Key>, <Private Key>, GET pagination page page_size, POST PUT --data-raw, Batch Operation, items field, draft version, online version, JSON response
- Follow-up Guidance: The source also explains response handling at a high level by saying that endpoint responses are returned in JSON format and refers to Response and Status Codes of Data Service for more details.
- Classification Note: This is classified as an operation chunk because it describes the prerequisites, generated request examples, authentication choices, environments, request options, and response format for invoking a Data Service endpoint.

## Official Source Content

## Call an endpoint

To call an endpoint, you can send an HTTPS request to either an undeployed draft version or a deployed online version of the endpoint.

> **Tip:**
>
> If you have imported your Data App to Postman, you can also call endpoints of the Data App in Postman. For more information, see [Run Data App in Postman](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-postman-integration).
### Prerequisites

Before calling an endpoint, you need to create an API key. For more information, refer to [Create an API key](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-api-key#create-an-api-key).
### Request

TiDB Cloud Data Service generates code examples to help you call an endpoint. To get the code example, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its endpoints.
3. Locate the endpoint you want to call and click **...** > **Code Example**. The **Code Example** dialog box is displayed.

    > **Tip:**
    >
    > Alternatively, you can also click the endpoint name to view its details and click **...** > **Code Example** in the upper-right corner.

4. In the dialog box, select the environment and authentication method that you want to use to call the endpoint, and then copy the code example.

    > **Note:**
    >
    > - The code examples are generated based on the properties and parameters of the endpoint.
    > - Currently, TiDB Cloud Data Service only provides the curl code example.

    - Environment: choose **Test Environment** or **Online Environment** depending on your need. **Online Environment** is available only after you deploy the endpoint.
    - Authentication method: choose **Basic Authentication** or **Digest Authentication**.
        - **Basic Authentication** transmits your API key as based64 encoded text.
        - **Digest Authentication** transmits your API key in an encrypted form, which is more secure.

      Compared with **Basic Authentication**, the curl code of **Digest Authentication** includes an additional `--digest` option.

    Here is an example of a curl code snippet for a `POST` request that enables **Batch Operation** and uses **Digest Authentication**:

    <div label="Test Environment">

    To call a draft version of the endpoint, you need to add the `endpoint-type: draft` header:

    ```bash
    curl --digest --user '<Public Key>:<Private Key>' \
     --request POST 'https://<region>.data.tidbcloud.com/api/v1beta/app/<App ID>/endpoint/<Endpoint Path>' \
     --header 'content-type: application/json'\
     --header 'endpoint-type: draft'
     --data-raw '{
      "items": [
        {
          "age": "${age}",
          "career": "${career}"
        }
      ]
    }'
    ```

    </div>

    <div label="Online Environment">

    You must deploy your endpoint first before checking the code example in the online environment.

    To call the current online version of the endpoint, use the following command:

    ```bash
    curl --digest --user '<Public Key>:<Private Key>' \
     --request POST 'https://<region>.data.tidbcloud.com/api/v1beta/app/<App ID>/endpoint/<Endpoint Path>' \
     --header 'content-type: application/json'\
     --data-raw '{
      "items": [
        {
          "age": "${age}",
          "career": "${career}"
        }
      ]
    }'
    ```

    </div>

    > **Note:**
    >
    > - By requesting the regional domain `<region>.data.tidbcloud.com`, you can directly access the endpoint in the region where the TiDB cluster is located.
    > - Alternatively, you can also request the global domain `data.tidbcloud.com` without specifying a region. In this way, TiDB Cloud Data Service will internally redirect the request to the target region, but this might result in additional latency. If you choose this way, make sure to add the `--location-trusted` option to your curl command when calling an endpoint.

5. Paste the code example in your application, edit the example according to your need, and then run it.

    - You need to replace the `<Public Key>` and `<Private Key>` placeholders with your API key. For more information, refer to [Manage an API key](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-api-key).
    - If the request method of your endpoint is `GET` and **Pagination** is enabled for the endpoint, you can paginate the results by updating the values of `page=<Page Number>` and `page_size=<Page Size>` with your desired values. For example, to get the second page with 10 items per page, use `page=2` and `page_size=10`.
    - If the request method of your endpoint is `POST` or `PUT`, fill in the `--data-raw` option according to the rows of data that you want to operate on.

        - For endpoints with **Batch Operation** enabled, the `--data-raw` option accepts an object with an `items` field containing an array of data objects so you can operate on multiple rows of data using one endpoint.
        - For endpoints with **Batch Operation** not enabled, the `--data-raw` option only accepts one data object.

    - If the endpoint contains parameters, specify the parameter values when calling the endpoint.
### Response

After calling an endpoint, you can see the response in JSON format. For more information, see [Response and Status Codes of Data Service](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-response-and-status-code).
