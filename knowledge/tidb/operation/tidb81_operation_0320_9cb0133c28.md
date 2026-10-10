# Import and run a Data App in Postman

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-postman-integration.md`
- Source Title: `Run Data App in Postman`
- Source Heading Path: `Run Data App in Postman | Run Data App in Postman > Before you begin | Run Data App in Postman > Step 1. Import your Data App to Postman | Run Data App in Postman > Step 2. Configure your Data App API key in Postman | Run Data App in Postman > Step 3. Run Data App in Postman | Run Data App in Postman > Deal with new changes in Data App`
- Source Line Ranges: `5-89`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `data-service`, `data-app`, `postman`, `api-key`, `endpoint`, `import`, `workspace`, `collection`, `request-parameters`, `batch-operation`, `reimport`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0320_9cb0133c28`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-postman-integration.md#run-data-app-in-postman`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `caaaf99fd1a029d523319b78f36b13b37225c4ef32fb9505e9f2e35187d62afd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-postman-integration#run-data-app-in-postman
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-postman-integration.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants to import a TiDB Cloud Data App into Postman, configure the Data App API key, run endpoints, or understand how re-import handles new Data App changes.
- Retrieval Keywords: Run Data App in Postman, TiDB Cloud Data Service, Data App, Run in Postman, Postman workspace, TiDB Data Service - <Your App Name>, Deployed folder, Draft folder, API key, public key, private key, Variables tab, Query Params, Body tab, Batch Operation, items field, Run in Postman for Web, Run in Postman Desktop, collection name is unique, re-import Data App
- Follow-up Guidance: The source also explains that new Data App changes are not synchronized automatically to Postman, so re-importing creates or replaces the collection and requires configuring the API key again for the newly imported app.
- Classification Note: This is classified as an operation because the content provides step-by-step procedures for importing a Data App to Postman, configuring credentials, invoking endpoints, and handling re-import after changes.

## Official Source Content

# Run Data App in Postman

[Postman](https://www.postman.com/) is an API platform that simplifies the API lifecycle and enhances collaboration for faster and better API development.

In TiDB Cloud [Data Service](https://tidbcloud.com/project/data-service), you can easily import your Data App to Postman and leverage Postman's extensive tools to enhance your API development experience.

This document describes how to import your Data App to Postman and how to run your Data App in Postman.
## Before you begin

Before importing a Data App to Postman, make sure that you have the following:

- A [Postman](https://www.postman.com/) account
- A [Postman desktop app](https://www.postman.com/downloads) (optional). Alternatively, you can use the Postman web version without downloading the app.
- A [Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app) with at least one well-defined [endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint). Only endpoints that meet the following requirements can be imported to Postman:

    - The target cluster is selected.
    - The endpoint path and request method are configured.
    - The SQL statements are written.

- An [API key](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-api-key#create-an-api-key) for the Data App.
## Step 1. Import your Data App to Postman

To import your Data App to Postman, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its details.
3. In the upper-right corner of the page, click **Run in Postman**. A dialog with import instructions is displayed.

    > **Note:**
    >
    > - If a Data App lacks a well-defined endpoint (the target cluster, path, request method, and SQL statements are configured), **Run in Postman** remains disabled for the Data App.
    > - For a Chat2Query Data App, **Run in Postman** is not available.

4. Follow the steps provided in the dialog for the Data App import:

    1. Depending on your preference, choose either **Run in Postman for Web** or **Run in Postman Desktop** to open your Postman workspaces, and then select your target workspace.

        - If you have not logged into Postman, follow the on-screen instructions to log into Postman first.
        - If you clicked **Run in Postman Desktop**, follow the on-screen instructions to launch the Postman desktop app.

    2. On the page of your target workspace in Postman, click **Import** in the left navigation menu.
    3. Copy the Data App URL from the TiDB Cloud dialog, and then paste the URL to Postman for the import.

5. After you paste the URL, Postman imports the Data App automatically as a new [collection](https://learning.postman.com/docs/collections/collections-overview). The name of the collection is in the `TiDB Data Service - <Your App Name>` format.

    In the collection, the deployed endpoints are grouped under the **Deployed** folder and the un-deployed endpoints are grouped under the **Draft** folder.
## Step 2. Configure your Data App API key in Postman

Before running the imported Data App in Postman, you need to configure the API key for the Data App in Postman as follows:

1. In the left navigation menu of Postman, click `TiDB Data Service - <Your App Name>` to open a tab for it on the right side.
2. Under the `TiDB Data Service - <Your App Name>` tab, click the **Variables** tab.
3. In the variable table, enter the public key and private key for your Data App in the **Current value** column.
4. In the upper-right corner of the `TiDB Data Service - <Your App Name>` tab, click **Save**.
## Step 3. Run Data App in Postman

To run your Data App in Postman, take the following steps:

1. In the left navigation pane of Postman, expand the **Deployed** or **Draft** folder, and then click your endpoint name to open a tab for it on the right side.
2. Under the `<Your Endpoint Name>` tab, you can call your endpoint as follows:

    - For an endpoint without parameters, you can click **Send** to call it directly.
    - For an endpoint with parameters, you need to fill in the parameter values first, and then click **Send**.

        - For a `GET` or `DELETE` request, fill in the parameter values in the **Query Params** table.
        - For a `POST` or `PUT` request, click the **Body** tab, and then fill in the parameter values as a JSON object. If **Batch Operation** is enabled for the endpoint in TiDB Cloud Data Service, fill in the parameter values to the `items` field as an array of JSON objects.

3. Check the response in the lower pane.

4. If you want to call the endpoint again with different parameter values, you can edit the parameter values accordingly, and then click **Send** again.

To learn more about the Postman usage, see [Postman documentation](https://learning.postman.com/docs).
## Deal with new changes in Data App

After a Data App is imported to Postman, TiDB Cloud Data Service will not automatically synchronize new changes of the Data App to Postman.

If you want any new changes to reflect in Postman, you have to [follow the import process](#step-1-import-your-data-app-to-postman) once again. Because the collection name is unique in a Postman workspace, you can either use the latest Data App to replace the previously imported one or import the latest Data App as a new collection.

Also, after re-importing the Data App, you will have to [configure the API key for the newly imported App](#step-2-configure-your-data-app-api-key-in-postman) in Postman again.
