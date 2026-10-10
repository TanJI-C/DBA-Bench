# Data Service overview, prerequisites, and sample Data App

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-get-started.md`
- Source Title: `Get Started with Data Service`
- Source Heading Path: `Get Started with Data Service | Get Started with Data Service > Before you begin | Get Started with Data Service > Get started with a sample Data App`
- Source Line Ranges: `5-41`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `data service`, `data app`, `sample app`, `prerequisites`, `serverless`, `https`, `console`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0305_555d281b53`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-get-started.md#get-started-with-data-service`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c5d5137e95b80e587d28ef853161ce5663b47c94cf906243360458d772c566e5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-get-started#get-started-with-data-service
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-get-started.md

## Retrieval Guidance

- Use When: Use this chunk when looking for a quick start to TiDB Cloud Data Service (beta), including prerequisites, the sample Data App flow, and how to call a sample endpoint with curl from the TiDB Cloud console.
- Retrieval Keywords: Data Service (beta), Data App, sample Data App, TiDB Cloud Serverless, Create Sample Data App, TiDB Cloud console, Data Service page, curl command, HTTPS request, custom API endpoint, Chat2Query, Chat2Data endpoint
- Follow-up Guidance: The source also points to creating a TiDB Cloud Serverless cluster first if none exists in the current project and notes that a Chat2Query system Data App can be created automatically when the Chat2Query API is enabled.
- Classification Note: This is classified as an operation chunk because the content describes the prerequisite and console workflow to create and use a sample Data App and call its endpoint.

## Official Source Content

# Get Started with Data Service

Data Service (beta) enables you to access TiDB Cloud data via an HTTPS request using a custom API endpoint and allows you to seamlessly integrate with any application or service that is compatible with HTTPS.

> **Tip:**
>
> TiDB Cloud provides a Chat2Query API for TiDB clusters. After it is enabled, TiDB Cloud will automatically create a system Data App called **Chat2Query** and a Chat2Data endpoint in Data Service. You can call this endpoint to let AI generate and execute SQL statements by providing instructions.
>
> For more information, see [Get started with Chat2Query API](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api).

This document introduces how to quickly get started with TiDB Cloud Data Service (beta) by creating a Data App, developing, testing, deploying, and calling an endpoint. A Data App is a collection of endpoints that you can use to access data for a specific application.
## Before you begin

Before creating a Data App, make sure that you have created a [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) cluster. If you do not have one, follow the steps in [Create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless) to create one.
## Get started with a sample Data App

Creating a sample Data App is the best way to get started with Data Service. If your project does not have any Data App yet, you can follow the on-screen instructions on the **Data Service** page to create a sample Data App and use this App to explore Data Service features.

1. In the [TiDB Cloud console](https://tidbcloud.com), click <MDSvgIcon name="icon-left-data-service" /> **Data Service** in the left navigation pane.

2. On the **Data Service** page, click **Create Sample Data App**. A dialog is displayed.

3. In the dialog, update the App name if necessary, select clusters that you want the Data App to access, and then click **Create**.

    The creation process takes a few seconds.

    > **Note:**
    >
    > If there is no cluster in your current project, you can click **Create New Cluster** in the **Link Data Sources** drop-down list to create one first.

4. After the sample Data App is automatically created, you can find the App name, a list of endpoints in the left pane, the SQL statements of an endpoint in the middle pane, and instructions about using the sample Data App on the right side.

5. Follow the instructions on the right side to choose an endpoint and use the curl command to call the endpoint.
