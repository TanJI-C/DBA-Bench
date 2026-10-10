# Chat2Query API overview and prerequisite setup

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/use-chat2query-api.md`
- Source Title: `Get Started with Chat2Query API`
- Source Heading Path: `Get Started with Chat2Query API | Get Started with Chat2Query API > Before you begin | Get Started with Chat2Query API > Before you begin > Create a Chat2Query Data App | Get Started with Chat2Query API > Before you begin > Create an API key`
- Source Line Ranges: `5-63`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `chat2query`, `api`, `data-app`, `api-key`, `authentication`, `roles`, `prerequisites`, `tls`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0433_b81c594a5c`
- Source ID: `tidb-docs-8.1:tidb-cloud/use-chat2query-api.md#get-started-with-chat2query-api`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6dd7ce75b86b109b56892bd1c68c946c16bb39bc1527a7da616316e64c6c2152`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api#get-started-with-chat2query-api
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/use-chat2query-api.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the Chat2Query API prerequisites, access scope, HTTPS/TLS requirement, or the steps to create a Chat2Query Data App and its API key roles in TiDB Cloud.
- Retrieval Keywords: Chat2Query API, RESTful interface, HTTPS, TLS, TiDB Cloud Serverless, TiDB Cloud Dedicated, contact TiDB Cloud support, Data Service, Create DataApp, Chat2Query Data App, Create API Key, Authentication, Chat2Query Admin, Chat2Query Data Summary Management Role, Chat2Query SQL ReadOnly, Chat2Query SQL ReadWrite, data summary, public key, private key, API key never expires, Expires in
- Follow-up Guidance: The source continues with how to call Chat2Query endpoints, including v3, v2, and deprecated v1 endpoints and generating a data summary before using `/v3/chat2data` or `/v2/chat2data`.
- Classification Note: This is classified as an operation chunk because the content describes prerequisite setup steps and role selection for accessing Chat2Query API in TiDB Cloud.

## Official Source Content

# Get Started with Chat2Query API

TiDB Cloud provides the Chat2Query API, a RESTful interface that enables you to generate and execute SQL statements using AI by providing instructions. Then, the API returns the query results for you.

Chat2Query API can only be accessed through HTTPS, ensuring that all data transmitted over the network is encrypted using TLS.

> **Note:**
>
> Chat2Query API is available for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters. To use the Chat2Query API on [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters, contact [TiDB Cloud support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
## Before you begin

Before calling Chat2Query endpoints, you need to create a Chat2Query Data App and create an API key for the Data App.
### Create a Chat2Query Data App

To create a Data App for your project, perform the following steps:

1. On the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project, click <MDSvgIcon name="icon-create-data-app" /> **Create DataApp** in the left pane. The data app creation dialog is displayed.

    > **Tip:**
    >
    > If you are on the **SQL Editor** page of your cluster, you can also open the data app creation dialog by clicking **...** in the upper-right corner, choosing **Access Chat2Query via API**, and clicking **New Chat2Query Data App**.

2. In the dialog, define a name for your Data App, choose the desired clusters as the data sources, and select **Chat2Query Data App** as the **Data App** type. Optionally, you can also write a description for the App.

3. Click **Create**.

   The newly created Chat2Query Data App is displayed in the left pane. Under this Data App, you can find a list of Chat2Query endpoints.
### Create an API key

Before calling an endpoint, you need to create an API key for the Chat2Query Data App, which is used by the endpoint to access data in your TiDB Cloud clusters.

To create an API key, perform the following steps:

1. In the left pane of [**Data Service**](https://tidbcloud.com/project/data-service), click your Chat2Query Data App to view its details on the right side.
2. In the **Authentication** area, click **Create API Key**.
3. In the **Create API Key** dialog, enter a description, and then select one of the following roles for your API key:

   - `Chat2Query Admin`: allows the API key to manage data summaries, generate SQL statements based on provided instructions, and execute any SQL statements.
   - `Chat2Query Data Summary Management Role`: only allows the API key to generate and update data summaries.

        > **Tip:**
        >
        > For Chat2Query API, a data summary is an analysis result of your database by AI, including your database descriptions, table descriptions, and column descriptions. By generating a data summary of your database, you can get a more accurate response when generating SQL statements by providing instructions.

   - `Chat2Query SQL ReadOnly`: only allows the API key to generate SQL statements based on provided instructions and execute `SELECT` SQL statements.
   - `Chat2Query SQL ReadWrite`: allows the API key to generate SQL statements based on provided instructions and execute any SQL statements.

4. By default, an API key never expires. If you prefer to set an expiration time for the key, click **Expires in**, select a time unit (`Minutes`, `Days`, or `Months`), and then fill in a desired number for the time unit.

5. Click **Next**. The public key and private key are displayed.

    Make sure that you have copied and saved the private key in a secure location. After leaving this page, you will not be able to get the full private key again.

6. Click **Done**.
