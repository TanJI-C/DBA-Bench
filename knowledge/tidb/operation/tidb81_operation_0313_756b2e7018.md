# Configure, rename, test, and deploy a Data Service endpoint

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-manage-endpoint.md`
- Source Title: `Manage an Endpoint`
- Source Heading Path: `Manage an Endpoint > Develop an endpoint > Configure parameters | Manage an Endpoint > Develop an endpoint > Rename | Manage an Endpoint > Test an endpoint | Manage an Endpoint > Deploy an endpoint`
- Source Line Ranges: `266-348`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `endpoint-parameters`, `parameter-types`, `test-values`, `rename`, `endpoint-testing`, `deployment`, `review-draft`, `deployment-history`, `auto-sync`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0313_756b2e7018`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-manage-endpoint.md#configure-parameters`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `30b6a504ba9b3840ff2887776df33da1850bfa8ef329072456e537c4e536e453`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#configure-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-manage-endpoint.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the exact TiDB Cloud Data Service UI behavior for configuring endpoint parameters, renaming an endpoint, testing it with test values, or deploying it and reviewing deployment history.
- Retrieval Keywords: Data Service endpoint Params tab, Definition section, Test Values section, parameter name letters digits underscores, reserved parameter names page page_size, Required, Type, STRING NUMBER INTEGER BOOLEAN ARRAY, Enum Value, ItemType, Default Value, Location, Path Query Body, Rename endpoint, predefined system endpoints do not support renaming, Test endpoint, F5, Deploy endpoint, Review Draft, Endpoint has been deployed, Deployments tab, Auto Sync & Deployment
- Follow-up Guidance: The source also states that if Auto Sync & Deployment is enabled through a GitHub connection, Data App changes made in GitHub are deployed automatically, and the Deployments tab shows deployed history.
- Classification Note: This is classified as an operation chunk because the content gives step-by-step UI procedures and parameter-setting rules for managing a Data Service endpoint in TiDB Cloud.

## Official Source Content

### Configure parameters

On the right pane of the endpoint details page, you can click the **Params** tab to view and manage the parameters used in the endpoint.

In the **Definition** section, you can view and manage the following properties for a parameter:

- The parameter name: the name can only include letters, digits, and underscores (`_`) and must start with a letter or an underscore (`_`). **DO NOT** use `page` and `page_size` as parameter names, which are reserved for pagination of request results.
- **Required**: specifies whether the parameter is required in the request. For path parameters, the configuration is required and cannot be modified. For other parameters, the default configuration is not required.
- **Type**: specifies the data type of the parameter. For path parameters, only `STRING` and `INTEGER` are supported. For other parameters, `STRING`, `NUMBER`, `INTEGER`, `BOOLEAN`, and `ARRAY` are supported.

    When using a `STRING` type parameter, you do not need to add quotation marks (`'` or `"`). For example, `foo` is valid for the `STRING` type and is processed as `"foo"`, whereas `"foo"` is processed as `"\"foo\""`.

- **Enum Value**: (optional) specifies the valid values for the parameter and is available only when the parameter type is `STRING`, `INTEGER`, or `NUMBER`.

    - If you leave this field empty, the parameter can be any value of the specified type.
    - To specify multiple valid values, you can separate them with a comma (`,`). For example, if you set the parameter type to `STRING` and specify this field as `foo, bar`, the parameter value can only be `foo` or `bar`.

- **ItemType**: specifies the item type of an `ARRAY` type parameter.
- **Default Value**: specifies the default value of the parameter.

    - For `ARRAY` type, you need to separate multiple values with a comma (`,`).
    - Make sure that the value can be converted to the type of parameter. Otherwise, the endpoint returns an error.
    - If you do not set a test value for a parameter, the default value is used when testing the endpoint.
- **Location**: indicates the location of the parameter. This property cannot be modified.
    - For path parameters, this property is `Path`.
    - For other parameters, if the request method is `GET` or `DELETE`, this property is `Query`. If the request method is `POST` or `PUT`, this property is `Body`.

In the **Test Values** section, you can view and set test parameters. These values are used as the parameter values when you test the endpoint. Make sure that the value can be converted to the type of parameter. Otherwise, the endpoint returns an error.
### Rename

To rename an endpoint, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its endpoints.
3. Locate the endpoint you want to rename, click **...** > **Rename**., and enter a new name for the endpoint.

> **Note:**
>
> Predefined system endpoints do not support renaming.
## Test an endpoint

To test an endpoint, perform the following steps:

> **Tip:**
>
> If you have imported your Data App to Postman, you can also test endpoints of the Data App in Postman. For more information, see [Run Data App in Postman](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-postman-integration).

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its endpoints.
3. Click the name of the endpoint you want to test to view its details.
4. (Optional) If the endpoint contains parameters, you need to set test values before testing.

    1. On the right pane of the endpoint details page, click the **Params** tab.
    2. Expand the **Test Values** section and set test values for the parameters.

        If you do not set a test value for a parameter, the default value is used.

5. Click **Test** in the upper-right corner.

    > **Tip:**
    >
    > Alternatively, you can also press <kbd>F5</kbd> to test the endpoint.

After testing the endpoint, you can see the response as JSON at the bottom of the page. For more information about the JSON response, refer to [Response of an endpoint](#response).
## Deploy an endpoint

> **Note:**
>
> If you have connected your Data App to GitHub with **Auto Sync & Deployment** enabled, any Data App changes you made in GitHub will be deployed in TiDB Cloud Data Service automatically. For more information, see [Deploy automatically with GitHub](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-github-connection).

To deploy an endpoint, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its endpoints.
3. Locate the endpoint you want to deploy, click the endpoint name to view its details, and then click **Deploy** in the upper-right corner.
4. If **Review Draft** is enabled for your Data App, a dialog is displayed for you to review the changes you made. You can choose whether to discard the changes based on the review.
5. Click **Deploy** to confirm the deployment. You will get the **Endpoint has been deployed** prompt if the endpoint is successfully deployed.

    On the right pane of the endpoint details page, you can click the **Deployments** tab to view the deployed history.
