# Data Service endpoint overview and endpoint creation methods

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-manage-endpoint.md`
- Source Title: `Manage an Endpoint`
- Source Heading Path: `Manage an Endpoint | Manage an Endpoint > Before you begin | Manage an Endpoint > Create an endpoint | Manage an Endpoint > Create an endpoint > Generate an endpoint automatically | Manage an Endpoint > Create an endpoint > Create an endpoint manually`
- Source Line Ranges: `5-83`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `data-service`, `endpoint`, `api`, `prerequisites`, `create-endpoint`, `autogenerate`, `manual-creation`, `http-methods`, `vector-search`, `deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0310_8a8894b1c1`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-manage-endpoint.md#manage-an-endpoint`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4e5eaf7f47f7906a03a20ffde3e8bb70fa077aae2357a8b63e2e891138cd5575`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#manage-an-endpoint
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-manage-endpoint.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiDB Cloud Data Service endpoints work, what prerequisites are required, and how to create endpoints automatically or manually in a Data App.
- Retrieval Keywords: Manage an Endpoint, Data Service, endpoint, Data App, Create an endpoint, Autogenerate Endpoint, Create Endpoint, Before you begin, API key, Generate an endpoint automatically, Create an endpoint manually, GET (Retrieve), POST (Create), PUT (Update), POST (Batch Create), Vector Search Operations, VEC_L2_DISTANCE, VEC_COSINE_DISTANCE, VEC_NEGATIVE_INNER_PRODUCT, VEC_L1_DISTANCE, Auto-Deploy Endpoint, POST /sample_table, /bulk, /vector_search
- Follow-up Guidance: The chunk also points to developing an endpoint for modifying the generated endpoint name, SQL statements, properties, or parameters.
- Classification Note: This is classified as an operation chunk because the content describes prerequisites and step-by-step procedures to create and review Data Service endpoints in the TiDB Cloud console.

## Official Source Content

# Manage an Endpoint

An endpoint in Data Service (beta) is a web API that you can customize to execute SQL statements. You can specify parameters for the SQL statements, such as the value used in the `WHERE` clause. When a client calls an endpoint and provides values for the parameters in a request URL, the endpoint executes the SQL statement with the provided parameters and returns the results as part of the HTTP response.

This document describes how to manage your endpoints in a Data App in the TiDB Cloud console.
## Before you begin

- Before you create an endpoint, make sure the following:

    - You have created a cluster and a Data App. For more information, see [Create a Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app#create-a-data-app).
    - The databases, tables, and columns that the endpoint will operate on already exist in the target cluster.

- Before you call an endpoint, make sure that you have created an API key in the Data App. For more information, see [Create an API key](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-api-key#create-an-api-key).
## Create an endpoint

In Data Service, you can automatically generate endpoints, manually create endpoints, or add predefined system endpoints.

> **Tip:**
>
> You can also create an endpoint from a SQL file in SQL Editor. For more information, see [Generate an endpoint from a SQL file](https://docs.pingcap.com/tidb/stable/tidb-cloud/explore-data-with-chat2query#generate-an-endpoint-from-a-sql-file).
### Generate an endpoint automatically

In TiDB Cloud Data Service, you can generate one or multiple endpoints automatically in one go as follows:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, locate your target Data App, click **+** to the right of the App name, and then click **Autogenerate Endpoint**. The dialog for endpoint generation is displayed.
3. In the dialog, do the following:

    1. Select the target cluster, database, and table for the endpoint to be generated.

        > **Note:**
        >
        > The **Table** drop-down list includes only user-defined tables with at least one column, excluding system tables and any tables without a column definition.

    2. Select at least one HTTP operation (such as `GET (Retrieve)`, `POST (Create)`, and `PUT (Update)`) for the endpoint to be generated.

        For each operation you select, TiDB Cloud Data Service will generate a corresponding endpoint. If you select a batch operation (such as `POST (Batch Create)`), the generated endpoint lets you operate on multiple rows in a single request.

        If the table you selected contains [vector data types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types), you can enable the **Vector Search Operations** option and select a vector distance function to generate a vector search endpoint that automatically calculates vector distances based on your selected distance function. The supported [vector distance functions](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-functions-and-operators) include the following:

        - `VEC_L2_DISTANCE` (default): calculates the L2 distance (Euclidean distance) between two vectors.
        - `VEC_COSINE_DISTANCE`: calculates the cosine distance between two vectors.
        - `VEC_NEGATIVE_INNER_PRODUCT`: calculates the distance by using the negative of the inner product between two vectors.
        - `VEC_L1_DISTANCE`: calculates the L1 distance (Manhattan distance) between two vectors.
       
    3. (Optional) Configure a timeout and tag for the operations. All the generated endpoints will automatically inherit the configured properties, which can be modified later as needed.
    4. (Optional) The **Auto-Deploy Endpoint** option (disabled by default) controls whether to enable the direct deployment of the generated endpoints. When it is enabled, the draft review process is skipped, and the generated endpoints are deployed immediately without further manual review or approval.

4. Click **Generate**.

    The generated endpoint is displayed at the top of the endpoint list.

5. Check the generated endpoint name, SQL statements, properties, and parameters of the new endpoint.

    - Endpoint name: the generated endpoint name is in the `/<name of the selected table>` format, and the request method (such as `GET`, `POST`, and `PUT`) is displayed before the endpoint name. For example, if the selected table name is `sample_table` and the selected operation is `POST (Create)`, the generated endpoint is displayed as `POST /sample_table`.

        - If a batch operation is selected, TiDB Cloud Data Service appends `/bulk` to the name of the generated endpoint. For example, if the selected table name is `/sample_table` and the selected operation is `POST (Batch Create)`, the generated endpoint is displayed as `POST /sample_table/bulk`.
        - If `POST (Vector Similarity Search)` is selected, TiDB Cloud Data Service appends `/vector_search` to the name of the generated endpoint. For example, if the selected table name is `/sample_table` and the selected operation is `POST (Vector Similarity Search)`, the generated endpoint is displayed as `POST /sample_table/vector_search`.
        - If there has been already an endpoint with the same request method and endpoint name, TiDB Cloud Data Service appends `_dump_<random letters>` to the name of the generated endpoint. For example, `/sample_table_dump_EUKRfl`.

    - SQL statements: TiDB Cloud Data Service automatically writes SQL statements for the generated endpoints according to the table column specifications and the selected endpoint operations. You can click the endpoint name to view its SQL statements in the middle section of the page.
    - Endpoint properties: TiDB Cloud Data Service automatically configures the endpoint path, request method, timeout, and tag according to your selection. You can find the properties in the right pane of the page.
    - Endpoint parameters: TiDB Cloud Data Service automatically configures parameters for the generated endpoints. You can find the parameters in the right pane of the page.

6. If you want to modify the details of the generated endpoint, such as its name, SQL statements, properties, or parameters, refer to the instructions provided in [Develop an endpoint](#deploy-an-endpoint).
### Create an endpoint manually

To create an endpoint manually, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, locate your target Data App, click **+** to the right of the App name, and then click **Create Endpoint**.
3. Update the default name if necessary. The newly created endpoint is added to the top of the endpoint list.
4. Configure the new endpoint according to the instructions in [Develop an endpoint](#develop-an-endpoint).
